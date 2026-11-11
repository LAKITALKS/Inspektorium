"""The replacement rule: invented ids, plus the agreed count on the corpus."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import fetch_genius
import genius_loader as loader
import make_run_plan as plan_module
import pytest
import replace_pilot_texts as rp
import reserve as rs
import select_texts as select

SEED = 7
OLD_A = "11_Verk_T1"
OLD_B = "12_Verk_T1-rev"
KEPT = "13_Verk_T1-Rev"
GOOD = rp.Profile(100, 5, True, True)
PLAIN = rp.Profile(100, 5, True, False)


def _sorted_reserve(text_ids: list[str]) -> list[str]:
    return select.draw_order(text_ids, SEED)


def _selection(reserve: list[str], *, used: tuple[str, ...] = ()) -> dict[str, Any]:
    return {
        "seed": SEED,
        "corpus_sha256": "unused",
        "annotation_files": 0,
        "groups": {
            "pilot": [OLD_A, OLD_B, KEPT],
            "component": ["21_Verk_T1"],
            "validation_holdout": ["22_Verk_T1-rev"],
            "reserve": reserve,
        },
        rs.USED_FOR_FABRICATED: list(used),
    }


def _profiles(reserve: list[str]) -> dict[str, rp.Profile]:
    profiles = {OLD_A: PLAIN, OLD_B: PLAIN, KEPT: GOOD}
    profiles.update(dict.fromkeys(reserve, GOOD))
    return profiles


RESERVE = ["31_Verk_T1", "32_Verk_T1-rev", "33_Verk_T1-Rev", "34_Verk_T1", "35_Verk_T1"]


def _build(
    selection: dict[str, Any],
    profiles: dict[str, rp.Profile],
    *,
    skips: dict[str, str] | None = None,
    cleared: list[str] | None = None,
) -> dict[str, Any]:
    return rp.build_marking(
        selection,
        profiles,
        (OLD_A, OLD_B),
        KEPT,
        skips or {},
        RESERVE[:2] if cleared is None else cleared,
    )


# --- the conclusion zone ---------------------------------------------------------

HEADER = (
    "#FORMAT=WebAnno TSV 3.3\n"
    "#T_SP=webanno.custom.Argument|Clarity\n"
    "#T_SP=webanno.custom.Struktur|Struktur\n\n\n"
)


def _lines(argument: str, structure: str, word: str = "Satz") -> list[str]:
    body = f"#Text={word}.\n1-1\t0-5\t{word}\t{argument}\t{structure}\t\n"
    return (HEADER + body).split("\n")


def test_a_label_in_the_structure_column_is_a_conclusion_zone() -> None:
    assert rp.has_conclusion_zone(_lines("_", "Schluss[6]"))
    assert rp.has_conclusion_zone(_lines("_", "Schluss"))
    assert rp.has_conclusion_zone(_lines("_", "Hauptteil[2]|Schluss[6]"))


def test_the_word_in_the_essay_is_no_conclusion_zone() -> None:
    assert not rp.has_conclusion_zone(_lines("_", "_", word="Schluss"))
    assert not rp.has_conclusion_zone(
        _lines("_", "Hauptteil[2]", word="schlussendlich")
    )


def test_the_label_in_another_column_is_no_conclusion_zone() -> None:
    assert not rp.has_conclusion_zone(_lines("Schluss[6]", "_"))


def test_a_file_without_the_column_has_no_conclusion_zone() -> None:
    lines = ("#T_SP=webanno.custom.Argument|Clarity\n\n\n#Text=Satz.\n").split("\n")
    assert not rp.has_conclusion_zone([*lines, "1-1\t0-5\tSatz\tSchluss[6]\t"])


def test_a_similar_label_is_no_conclusion_zone() -> None:
    assert not rp.has_conclusion_zone(_lines("_", "Schlussteil[6]"))


# --- the rule ---------------------------------------------------------------------


def test_the_first_candidates_are_taken_in_the_stored_order() -> None:
    selection = _selection(RESERVE)
    assert rp.find_candidates(selection, _profiles(RESERVE), KEPT) == RESERVE
    marking = _build(selection, _profiles(RESERVE))
    assert [item["text_id"] for item in marking["replacements"]] == RESERVE[:2]
    assert [item["replaces"] for item in marking["replacements"]] == [OLD_A, OLD_B]
    assert [item["reserve_place"] for item in marking["replacements"]] == [1, 2]


@pytest.mark.parametrize(
    ("first", "profile"),
    [
        pytest.param("31_Verk_T1", rp.Profile(79, 5, True, True), id="too-short"),
        pytest.param("31_Verk_T1", rp.Profile(100, 5, False, True), id="no-argument"),
        pytest.param("31_Verk_T1", PLAIN, id="no-conclusion"),
        pytest.param("31_Rad_T1", GOOD, id="other-task"),
        pytest.param("21_Verk_T1-rev", GOOD, id="version-in-component"),
        pytest.param("22_Verk_T1", GOOD, id="version-in-holdout"),
        pytest.param("13_Verk_T1", GOOD, id="version-of-the-kept-text"),
        pytest.param("11_Verk_T1-rev", GOOD, id="version-of-a-replaced-text"),
    ],
)
def test_a_text_outside_the_rule_is_passed_over(
    first: str, profile: rp.Profile
) -> None:
    reserve = [first, *RESERVE[1:]]
    profiles = _profiles(reserve)
    profiles[first] = profile
    assert rp.find_candidates(_selection(reserve), profiles, KEPT) == RESERVE[1:]


def test_exactly_80_words_meet_the_rule() -> None:
    profiles = _profiles(RESERVE)
    profiles[RESERVE[0]] = rp.Profile(80, 5, True, True)
    assert rp.find_candidates(_selection(RESERVE), profiles, KEPT) == RESERVE


def test_a_text_used_for_fabricated_cases_is_passed_over() -> None:
    selection = _selection(RESERVE, used=(RESERVE[0],))
    assert rp.find_candidates(selection, _profiles(RESERVE), KEPT) == RESERVE[1:]


def test_a_reserve_text_without_annotation_is_refused() -> None:
    profiles = _profiles(RESERVE)
    del profiles[RESERVE[2]]
    with pytest.raises(rp.ReplacementError, match="no annotation file"):
        rp.find_candidates(_selection(RESERVE), profiles, KEPT)


def test_a_selection_without_the_used_list_is_refused() -> None:
    selection = _selection(RESERVE)
    del selection[rs.USED_FOR_FABRICATED]
    with pytest.raises(rs.ReserveError, match="no used_for_fabricated"):
        rp.find_candidates(selection, _profiles(RESERVE), KEPT)


@pytest.mark.parametrize("text_id", ["31-Verk_T1", "Verk_T1", "31_Verk_T1-v2", ""])
def test_an_unreadable_text_id_is_refused(text_id: str) -> None:
    with pytest.raises(rp.ReplacementError, match="cannot read the text id"):
        rp.split_text_id(text_id)


@pytest.mark.parametrize(
    ("text_id", "number"),
    [("31_Verk_T1", "31"), ("31_Verk_T1-rev", "31"), ("31_Verk_T1-Rev", "31")],
)
def test_all_three_id_forms_give_the_number_and_the_task(
    text_id: str, number: str
) -> None:
    assert rp.split_text_id(text_id) == (number, "Verk_T1")


def test_two_versions_of_one_text_never_both_enter_the_pilot() -> None:
    candidates = ["31_Verk_T1", "31_Verk_T1-rev", "32_Verk_T1"]
    assert rp.take_first(candidates, 2, []) == ["31_Verk_T1", "32_Verk_T1"]


def test_too_few_candidates_are_refused() -> None:
    with pytest.raises(rp.ReplacementError, match="the rule leaves 1"):
        rp.take_first(RESERVE[:1], 2, [])


# --- the privacy check ------------------------------------------------------------


def test_a_skipped_text_gives_way_to_the_next() -> None:
    selection = _selection(RESERVE)
    marking = _build(
        selection,
        _profiles(RESERVE),
        skips={RESERVE[1]: "person"},
        cleared=[RESERVE[0], RESERVE[2]],
    )
    assert [item["text_id"] for item in marking["replacements"]] == [
        RESERVE[0],
        RESERVE[2],
    ]
    assert marking["privacy_skips"] == [
        {"text_id": RESERVE[1], "reason": "person", "reserve_place": 2}
    ]


def test_a_skip_past_the_last_text_taken_is_refused() -> None:
    with pytest.raises(rp.ReplacementError, match="skips never reached"):
        rp.take_first(RESERVE, 2, [RESERVE[3]])


def test_a_skip_outside_the_candidates_is_refused() -> None:
    with pytest.raises(rp.ReplacementError, match="skips never reached"):
        rp.take_first(RESERVE, 2, ["99_Verk_T1"])


@pytest.mark.parametrize(
    "cleared",
    [
        pytest.param([RESERVE[0], RESERVE[2]], id="hand-picked"),
        pytest.param([RESERVE[1], RESERVE[0]], id="other-order"),
        pytest.param([RESERVE[0]], id="too-few"),
        pytest.param([], id="none"),
    ],
)
def test_only_the_texts_the_rule_takes_can_be_cleared(cleared: list[str]) -> None:
    with pytest.raises(rp.ReplacementError, match="the rule takes"):
        _build(_selection(RESERVE), _profiles(RESERVE), cleared=cleared)


@pytest.mark.parametrize("reason", ["person", "school", "place"])
def test_a_skip_names_a_kind(reason: str) -> None:
    assert rp.read_skip(f"31_Verk_T1={reason}") == ("31_Verk_T1", reason)


@pytest.mark.parametrize(
    "entry", ["31_Verk_T1", "31_Verk_T1=", "31_Verk_T1=Musterstadt"]
)
def test_a_skip_cannot_carry_a_name(entry: str) -> None:
    with pytest.raises(rp.ReplacementError, match="a skip needs the form"):
        rp.read_skip(entry)


# --- the checks around the rule ---------------------------------------------------


def test_the_stored_order_must_be_the_order_of_the_draw() -> None:
    drawn = _sorted_reserve(RESERVE)
    rp.check_stored_order(_selection(drawn), SEED)
    with pytest.raises(rp.ReplacementError, match="not stored in the order"):
        rp.check_stored_order(_selection(drawn[::-1]), SEED)


def test_a_different_seed_is_refused() -> None:
    drawn = _sorted_reserve(RESERVE)
    with pytest.raises(rp.ReplacementError, match="differs from the seed"):
        rp.check_stored_order(_selection(drawn), SEED + 1)


def _corpus(zones: int, files: int) -> dict[str, rp.Profile]:
    return {
        f"{number}_Verk_T1": GOOD if number < zones else PLAIN
        for number in range(files)
    }


def test_the_agreed_count_passes_and_a_different_count_stops() -> None:
    selection = {"annotation_files": 262}
    rp.check_corpus(selection, _corpus(33, 262))
    for zones in (32, 34, 36, 0):
        with pytest.raises(rp.ReplacementError, match="expected 33 files"):
            rp.check_corpus(selection, _corpus(zones, 262))


def test_a_different_corpus_size_stops() -> None:
    with pytest.raises(rp.ReplacementError, match="expected 262 annotation"):
        rp.check_corpus({"annotation_files": 262}, _corpus(33, 261))


def test_the_named_texts_must_be_the_drawn_pilot() -> None:
    selection = _selection(RESERVE)
    with pytest.raises(rp.ReplacementError, match="not the drawn pilot"):
        rp.next_texts(selection, _profiles(RESERVE), (OLD_A,), KEPT, {})


def test_a_text_with_a_zone_is_not_replaced() -> None:
    profiles = _profiles(RESERVE)
    profiles[OLD_A] = GOOD
    with pytest.raises(rp.ReplacementError, match="to be replaced has a conclusion"):
        rp.next_texts(_selection(RESERVE), profiles, (OLD_A, OLD_B), KEPT, {})


def test_the_kept_text_must_have_a_zone() -> None:
    profiles = _profiles(RESERVE)
    profiles[KEPT] = PLAIN
    with pytest.raises(rp.ReplacementError, match="kept text has no conclusion"):
        rp.next_texts(_selection(RESERVE), profiles, (OLD_A, OLD_B), KEPT, {})


def test_a_second_replacement_is_refused() -> None:
    selection = _selection(RESERVE)
    selection[rs.PILOT_REPLACEMENT] = _build(selection, _profiles(RESERVE))
    with pytest.raises(rp.ReplacementError, match="already holds a replacement"):
        rp.next_texts(selection, _profiles(RESERVE), (OLD_A, OLD_B), KEPT, {})


# --- the marking ------------------------------------------------------------------


def _marked(skips: dict[str, str] | None = None) -> dict[str, Any]:
    selection = _selection(RESERVE, used=(RESERVE[4],))
    cleared = [RESERVE[0], RESERVE[2]] if skips else RESERVE[:2]
    marking = _build(selection, _profiles(RESERVE), skips=skips, cleared=cleared)
    return {**selection, rs.PILOT_REPLACEMENT: marking}


def test_the_replacements_stand_where_the_replaced_texts_stood() -> None:
    assert rs.current_pilot(_marked()) == [RESERVE[0], RESERVE[1], KEPT]


def test_an_unmarked_selection_has_the_drawn_pilot() -> None:
    assert rs.current_pilot(_selection(RESERVE)) == [OLD_A, OLD_B, KEPT]


def test_the_groups_of_the_draw_stay_unchanged() -> None:
    marked = _marked()
    assert marked["groups"] == _selection(RESERVE, used=(RESERVE[4],))["groups"]


def test_a_replacement_of_an_unknown_text_is_refused() -> None:
    marked = _marked()
    marked[rs.PILOT_REPLACEMENT]["replacements"][0]["replaces"] = "99_Verk_T1"
    with pytest.raises(rs.ReserveError, match="not in the pilot"):
        rs.current_pilot(marked)


def test_replacements_and_skips_are_out_of_later_samples() -> None:
    assert rs.available_reserve(_marked()) == RESERVE[2:4]
    marked = _marked({RESERVE[1]: "place"})
    assert rs.available_reserve(marked) == [RESERVE[3]]


def test_a_replacement_from_outside_the_reserve_is_refused() -> None:
    marked = _marked()
    marked[rs.PILOT_REPLACEMENT]["replacements"][0]["text_id"] = "99_Verk_T1"
    with pytest.raises(rs.ReserveError, match="not in the reserve"):
        rs.available_reserve(marked)


def test_the_marking_names_the_rule() -> None:
    marking = _build(_selection(RESERVE), _profiles(RESERVE))
    assert marking["rule"]["conclusion_column"] == "webanno.custom.Struktur|Struktur"
    assert marking["rule"]["conclusion_label"] == "Schluss"
    assert marking["rule"]["pool"] == "available_reserve"
    assert marking["kept"] == [KEPT]


# --- the command line -------------------------------------------------------------


def _toy_file(folder: Path, text_id: str, label: str) -> None:
    words = " ".join(f"Wort{number}" for number in range(90))
    body = f"#Text={words}\n1-1\t0-5\tWort0\t_\t{label}\t\n"
    (folder / f"{text_id}.tsv").write_text(HEADER + body, "utf-8")


class Toy:
    """A small corpus on disk; 33 files carry a zone, as the agreed count says."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.selection = root / "selection.json"
        self.selected = root / "selected"
        annotations = root / "annotations"
        annotations.mkdir()
        reserve = _sorted_reserve(RESERVE)
        self.reserve = reserve
        for text_id in (OLD_A, OLD_B, "21_Verk_T1", "22_Verk_T1-rev"):
            _toy_file(annotations, text_id, "_")
        _toy_file(annotations, KEPT, "Schluss[1]")
        for text_id in reserve:
            _toy_file(annotations, text_id, "Schluss[1]")
        for number in range(27):
            _toy_file(annotations, f"{900 + number}_Verk_T1", "Schluss[1]")
        corpus = loader.load_corpus(annotations)
        banks = root / "banks"
        by_sentence = root / "sentence_criteria.json"
        criteria = root / "criteria.json"
        banks.mkdir()
        for item in corpus:
            (banks / f"{item.bank.text_id}.json").write_bytes(
                loader.dump_json(item.bank.as_dict())
            )
        by_sentence.write_bytes(
            loader.dump_json({i.bank.text_id: i.sentence_criteria for i in corpus})
        )
        criteria.write_text("{}", "utf-8")
        self.archive = root / "toy.zip"
        self.archive.write_bytes(b"toy")
        digest = hashlib.sha256(b"toy").hexdigest()
        selection = {
            **_selection(reserve),
            "corpus_sha256": digest,
            "annotation_files": len(corpus),
        }
        self.selection.write_bytes(loader.dump_json(selection))
        (root / "seed.txt").write_text(str(SEED), "utf-8")

    def run(self, *extra: str) -> int:
        return rp.main(
            [
                "--annotations",
                str(self.root / "annotations"),
                "--archive",
                str(self.archive),
                "--banks",
                str(self.root / "banks"),
                "--sentence-criteria",
                str(self.root / "sentence_criteria.json"),
                "--seed-file",
                str(self.root / "seed.txt"),
                "--selection",
                str(self.selection),
                "--selected",
                str(self.selected),
                *extra,
            ]
        )

    def replacements(self) -> list[str]:
        loaded = json.loads(self.selection.read_text("utf-8"))
        marking = loaded[rs.PILOT_REPLACEMENT]
        return [item["text_id"] for item in marking["replacements"]]


@pytest.fixture
def toy(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Toy:
    built = Toy(tmp_path)
    monkeypatch.setattr(rp, "REPLACED", (OLD_A, OLD_B))
    monkeypatch.setattr(rp, "KEPT", KEPT)
    return built


def test_a_run_without_cleared_texts_writes_nothing(
    toy: Toy, capsys: pytest.CaptureFixture[str]
) -> None:
    before = toy.selection.read_bytes()
    assert toy.run() == 0
    assert toy.selection.read_bytes() == before
    assert not toy.selected.exists()
    assert " ".join(toy.reserve[:2]) in capsys.readouterr().out


def test_the_cleared_texts_are_marked_and_copied(toy: Toy) -> None:
    assert toy.run("--cleared", *toy.reserve[:2]) == 0
    assert toy.replacements() == toy.reserve[:2]
    names = sorted(path.stem for path in toy.selected.glob("*_T1*.json"))
    expected = [OLD_A, OLD_B, KEPT, "21_Verk_T1", *toy.reserve[:2]]
    assert names == sorted(expected)
    subset = json.loads((toy.selected / "sentence_criteria.json").read_text("utf-8"))
    assert sorted(subset) == sorted(expected)


def test_the_groups_keep_their_bytes_after_the_run(toy: Toy) -> None:
    before = json.loads(toy.selection.read_text("utf-8"))
    assert toy.run("--cleared", *toy.reserve[:2]) == 0
    after = json.loads(toy.selection.read_text("utf-8"))
    del after[rs.PILOT_REPLACEMENT]
    assert after == before


def test_hand_picked_texts_write_nothing(
    toy: Toy, capsys: pytest.CaptureFixture[str]
) -> None:
    before = toy.selection.read_bytes()
    assert toy.run("--cleared", toy.reserve[0], toy.reserve[2]) == 1
    assert toy.selection.read_bytes() == before
    assert not toy.selected.exists()
    assert "REFUSED, nothing written" in capsys.readouterr().err


def test_a_skip_moves_the_rule_on(toy: Toy) -> None:
    taken = [toy.reserve[0], toy.reserve[2]]
    assert toy.run("--skip", f"{toy.reserve[1]}=place", "--cleared", *taken) == 0
    assert toy.replacements() == taken


def test_a_second_run_is_refused(toy: Toy) -> None:
    assert toy.run("--cleared", *toy.reserve[:2]) == 0
    before = toy.selection.read_bytes()
    assert toy.run("--cleared", *toy.reserve[2:4]) == 1
    assert toy.selection.read_bytes() == before


def test_a_reordered_reserve_stops_the_run(toy: Toy) -> None:
    loaded = json.loads(toy.selection.read_text("utf-8"))
    loaded["groups"]["reserve"].reverse()
    toy.selection.write_bytes(loader.dump_json(loaded))
    assert toy.run() == 1


def test_a_wrong_count_stops_the_run(toy: Toy) -> None:
    _toy_file(toy.root / "annotations", "11_Verk_T1", "Schluss[1]")
    assert toy.run("--cleared", *toy.reserve[:2]) == 1


def test_an_unpinned_archive_stops_the_run(toy: Toy) -> None:
    toy.archive.write_bytes(b"not the pinned archive")
    assert toy.run("--cleared", *toy.reserve[:2]) == 1
    assert not toy.selected.exists()


def test_the_run_plan_follows_the_replacement(toy: Toy) -> None:
    assert toy.run("--cleared", *toy.reserve[:2]) == 0
    plan = toy.root / "plan.csv"
    code = plan_module.main(
        [
            "--seed-file",
            str(toy.root / "seed.txt"),
            "--selection",
            str(toy.selection),
            "--plan",
            str(plan),
            "--root",
            str(toy.root),
        ]
    )
    assert code == 0
    written = plan.read_text("utf-8")
    assert toy.reserve[0] in written
    assert toy.reserve[1] in written
    assert KEPT in written
    assert OLD_A not in written
    assert OLD_B not in written


# --- the agreed count on the corpus ------------------------------------------------


def test_the_agreed_count_holds_on_the_corpus(annotations_dir: Path) -> None:
    """33 of 262 by label; the 36 of a word search is not the same thing."""

    profiles = rp.read_profiles(annotations_dir)
    assert len(profiles) == 262
    assert sum(item.has_conclusion for item in profiles.values()) == 33


def test_the_word_search_finds_three_files_without_a_zone(
    annotations_dir: Path,
) -> None:
    profiles = rp.read_profiles(annotations_dir)
    word_only = {
        path.stem
        for path in annotations_dir.glob("*.tsv")
        if "schluss" in path.read_text("utf-8").casefold()
        and not profiles[path.stem].has_conclusion
    }
    assert word_only == {"315_Verk_T1", "897_Verk_T1-rev", "937_Verk_T1-rev"}


def test_the_archive_is_pinned_by_the_selection(study_root: Path) -> None:
    selection = json.loads((study_root / "prereg/selection.json").read_text("utf-8"))
    assert selection["corpus_sha256"] == fetch_genius.EXPECTED_SHA256


def test_the_committed_reserve_is_stored_in_the_order_of_the_draw(
    study_root: Path,
) -> None:
    selection = json.loads((study_root / "prereg/selection.json").read_text("utf-8"))
    rp.check_stored_order(selection, select.read_seed(study_root / "prereg/seed.txt"))


def test_two_conditions_exclude_nothing_on_this_corpus(annotations_dir: Path) -> None:
    """All files have one task, and no text number occurs twice."""

    parts = [rp.split_text_id(path.stem) for path in annotations_dir.glob("*.tsv")]
    assert len(parts) == 262
    assert {task for _, task in parts} == {"Verk_T1"}
    assert len({number for number, _ in parts}) == 262
