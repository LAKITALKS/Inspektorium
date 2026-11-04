"""The case generator, tested on invented sentences only."""

from __future__ import annotations

import ast
import hashlib
import json
import unicodedata
from pathlib import Path

import genius_loader as loader
import make_reference_cases as make
import pytest

POOL = (
    "Fremde Sätze stammen aus einem ganz anderen Aufsatz der Reserve.",
    "Auch dieser Satz wurde von niemandem in diesem Spieltext geschrieben.",
)
TOY = loader.build_bank(
    "toy",
    [
        "Elektroautos kosten heute rund 40000 Euro und halten etwa 15 Jahre lang.",
        'Der Spielbericht nennt das Wort "Reichweite" als wichtigsten Grund dafür.',
        "Wasserstoff braucht viel Energie bei der Herstellung und beim Transport.",
        "Das ist gut.",
        "Das ist gut, weil neue Tankstellen sehr viele Menschen erreichen können.",
    ],
)


@pytest.fixture(scope="module")
def cases() -> list[make.Case]:
    return make.cases_for_text(TOY, 1, POOL)


def _sentence(sid: str) -> str:
    return next(item.text for item in TOY.sentences if item.sid == sid)


def test_every_type_is_built_on_the_toy_text(cases: list[make.Case]) -> None:
    assert {case.type for case in cases} == set(make.EXPECTED)


def test_the_type_table_is_the_agreed_one() -> None:
    assert make.EXPECTED == {
        "valid_exact": (True, True),
        "wrong_location": (False, False),
        "altered_number": (False, False),
        "altered_word": (False, False),
        "fabricated": (False, False),
        "case_change": (False, False),
        "format_variant": (False, True),
        "punctuation_added": (False, True),
    }


def test_labels_are_the_table_values(cases: list[make.Case]) -> None:
    for case in cases:
        assert (case.expected_strict, case.expected_normalized) == (
            make.EXPECTED[case.type]
        )


def test_every_label_holds_for_its_claimed_sentence(cases: list[make.Case]) -> None:
    for case in cases:
        assert make.label_holds(case.type, case.quote, _sentence(case.claimed_sid))


def test_a_text_without_digits_gets_no_number_case() -> None:
    bank = loader.build_bank("plain", ["Hier steht kein Wert in dem langen Satz drin."])
    built = make.cases_for_text(bank, 1, POOL)
    assert "altered_number" not in {case.type for case in built}
    assert "valid_exact" in {case.type for case in built}


def test_a_number_inside_a_word_is_not_a_number() -> None:
    assert not make._NUMBER.search("CO2 und H2O")
    assert make._NUMBER.search("rund 3,5 Liter").group() == "3,5"  # type: ignore[union-attr]


def test_format_variants_keep_their_changed_space_through_nfc(
    cases: list[make.Case],
) -> None:
    for space in make._VARIANT_SPACES:
        assert unicodedata.normalize("NFC", space) == space
    variants = [case for case in cases if case.type == "format_variant"]
    assert variants
    for case in variants:
        assert case.quote not in _sentence(case.claimed_sid)
        assert case.quote.replace(" ", " ").replace(" ", " ").replace(" ", " ").replace(
            "“", '"'
        ) in _sentence(case.claimed_sid)


def test_added_punctuation_is_really_added(cases: list[make.Case]) -> None:
    added = [case for case in cases if case.type == "punctuation_added"]
    assert added
    for case in added:
        sentence = _sentence(case.claimed_sid)
        assert case.quote[-1] in ".!?"
        assert case.quote not in sentence
        assert case.quote[:-1] in sentence


def test_an_omitted_mark_cannot_carry_the_punctuation_label() -> None:
    """Without its final mark, a sentence is still a literal part of itself."""

    sentence = "Das ist gut."
    assert not make.label_holds("punctuation_added", "Das ist gut", sentence)
    assert make.label_holds("valid_exact", "Das ist gut", sentence)


def test_the_final_mark_rule_cannot_mislabel_a_wrong_location() -> None:
    """S4 ends where S5 goes on: the normalized view would accept the quote."""

    assert not make.label_holds("wrong_location", "Das ist gut.", _sentence("S5"))
    assert make.label_holds("wrong_location", "Das ist gut.", _sentence("S1"))


def test_the_final_mark_rule_cannot_mislabel_a_fabricated_sentence() -> None:
    pool = ("Das ist gut.",)
    built = make.cases_for_text(TOY, 1, pool)
    assert "fabricated" not in {case.type for case in built}


def test_a_changed_case_stays_invalid_in_both_modes() -> None:
    assert make.label_holds("case_change", "das ist gut", "Das ist gut.")
    assert not make.label_holds("case_change", "Das ist gut", "Das ist gut.")


def test_ids_are_unique(cases: list[make.Case]) -> None:
    assert len({case.case_id for case in cases}) == len(cases)


def test_generation_is_reproducible(cases: list[make.Case]) -> None:
    assert make.cases_for_text(TOY, 1, POOL) == cases


def test_the_seed_changes_the_cases(cases: list[make.Case]) -> None:
    assert make.cases_for_text(TOY, 2, POOL) != cases


def _invented_cases(count: int) -> list[make.Case]:
    return [
        make.Case(f"c{n}", "t", "S1", "q", "valid_exact", True, True)
        for n in range(count)
    ]


def test_the_split_is_seventy_thirty_and_loses_nothing() -> None:
    development, held_out = make.split_cases(_invented_cases(100), 3)
    assert (len(development), len(held_out)) == (70, 30)
    assert {case.case_id for case in development}.isdisjoint(
        case.case_id for case in held_out
    )


def test_the_split_depends_on_the_seed() -> None:
    assert make.split_cases(_invented_cases(100), 3) != make.split_cases(
        _invented_cases(100), 4
    )


def test_the_hash_file_names_the_sealed_payload(tmp_path: Path) -> None:
    development, held_out = make.split_cases(_invented_cases(10), 3)
    sealed = tmp_path / "sealed/holdout_cases.json"
    digest = make.write_cases(
        development, held_out, tmp_path / "dev.json", sealed, tmp_path / "hash.txt"
    )
    assert hashlib.sha256(sealed.read_bytes()).hexdigest() == digest
    assert (tmp_path / "hash.txt").read_text() == (
        f"{digest}  sealed/holdout_cases.json\n"
    )


def test_the_summary_holds_only_counts() -> None:
    development, held_out = make.split_cases(_invented_cases(10), 3)
    summary = make.summarize(development, held_out, ["r1"])
    assert "q" not in json.dumps(summary)
    assert summary["held_out"] == 3


def test_the_generator_never_imports_a_checker(study_root: Path) -> None:
    source = (study_root / "scripts/make_reference_cases.py").read_text("utf-8")
    imported: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert imported.isdisjoint({"inspektorium", "check_quotes"})


def test_committed_development_cases_keep_their_labels(study_root: Path) -> None:
    cases = json.loads(
        (study_root / "data/reference_cases_dev.json").read_text("utf-8")
    )
    assert cases
    for case in cases:
        bank = loader.read_bank(study_root / f"data/selected/{case['text_id']}.json")
        sentence = next(s.text for s in bank.sentences if s.sid == case["claimed_sid"])
        assert make.label_holds(case["type"], case["quote"], sentence)
        assert (case["expected_strict"], case["expected_normalized"]) == (
            make.EXPECTED[case["type"]]
        )


def test_committed_summary_covers_every_type(study_root: Path) -> None:
    summary = json.loads(
        (study_root / "prereg/reference_cases_summary.json").read_text("utf-8")
    )
    assert set(summary["by_type"]) == set(make.EXPECTED)
    assert all(
        counts["development"] and counts["held_out"]
        for counts in summary["by_type"].values()
    )


def test_the_sealed_file_is_ignored_by_git(study_root: Path) -> None:
    assert "sealed/" in (study_root / ".gitignore").read_text("utf-8").split()


def test_the_sealed_file_matches_its_committed_hash(study_root: Path) -> None:
    sealed = study_root / "sealed/holdout_cases.json"
    if not sealed.exists():
        pytest.skip("the sealed file is kept outside Git")
    committed = (study_root / "prereg/holdout_sha256.txt").read_text("utf-8")
    assert committed.split()[0] == hashlib.sha256(sealed.read_bytes()).hexdigest()
