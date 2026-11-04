"""The quote checker, tested on invented sentences only."""

from __future__ import annotations

import json
from pathlib import Path

import check_quotes as cq
import genius_loader as loader
import pytest

from inspektorium.core import validation

BANK = loader.build_bank(
    "toy",
    [
        "Das Auto fährt 300 km weit.",
        'Er sagte: "Das reicht nicht" und ging.',
        "Laden dauert lange",
        "Das Auto ist teuer und laut.",
        "Zeile eins\nZeile zwei",
    ],
)


def _both(sid: str, quote: str) -> tuple[bool, bool]:
    return (
        cq.check_quote(BANK, sid, quote, "strict").location_valid,
        cq.check_quote(BANK, sid, quote, "normalized").location_valid,
    )


@pytest.mark.parametrize(
    ("sid", "quote", "strict", "normalized"),
    [
        pytest.param("S1", "fährt 300 km", True, True, id="exact-part"),
        pytest.param("S1", "Das Auto fährt 300 km weit.", True, True, id="sentence"),
        pytest.param("S4", "fährt 300 km", False, False, id="wrong-sentence"),
        pytest.param("S1", "fährt 301 km", False, False, id="changed-number"),
        pytest.param("S1", "fährt 300 Kilometer", False, False, id="changed-word"),
        pytest.param("S1", "Fährt 300 km", False, False, id="changed-case"),
        pytest.param("S1", "Niemand schrieb das", False, False, id="fabricated"),
        pytest.param("S1", "fährt 300 km", False, True, id="thin-space"),
        pytest.param("S1", "fährt 300 km", False, True, id="no-break-space"),
        pytest.param("S3", "Laden dauert", False, True, id="thin-space-in-source"),
        pytest.param("S2", "„Das reicht nicht“", False, True, id="german-quotes"),
        pytest.param("S2", "«Das reicht nicht»", False, True, id="guillemets"),
        pytest.param("S5", "eins Zeile", False, True, id="line-break-as-space"),
        pytest.param("S1", "fährt  300 km", False, False, id="spaces-are-not-merged"),
    ],
)
def test_the_two_modes(sid: str, quote: str, strict: bool, normalized: bool) -> None:
    assert _both(sid, quote) == (strict, normalized)


def test_strict_mode_applies_the_kernel_normalization() -> None:
    assert _both("S1", "fährt 300 km".replace("ä", "ä")) == (
        True,
        True,
    )
    assert _both("S5", "eins\r\nZeile") == (True, True)


def test_text_and_location_are_reported_apart() -> None:
    result = cq.check_quote(BANK, "S4", "fährt 300 km", "strict")
    assert (result.text_valid, result.location_valid) == (True, False)
    assert result.reason == "wrong_location"


def test_a_quote_may_not_run_across_two_sentences() -> None:
    result = cq.check_quote(BANK, "S1", "weit. Er sagte", "strict")
    assert (result.text_valid, result.location_valid) == (True, False)


def test_an_unknown_sentence_number_fails_closed() -> None:
    result = cq.check_quote(BANK, "S99", "fährt 300 km", "strict")
    assert (result.text_valid, result.location_valid) == (True, False)
    assert result.reason == "unknown_sid"


@pytest.mark.parametrize("mark", [".", "!", "?"])
def test_one_added_final_mark_is_ignored_only_in_normalized_mode(mark: str) -> None:
    quote = f"fährt 300 km{mark}"
    strict = cq.check_quote(BANK, "S1", quote, "strict")
    normalized = cq.check_quote(BANK, "S1", quote, "normalized")
    assert strict.location_valid is False
    assert strict.final_mark_ignored is False
    assert normalized.location_valid is True
    assert normalized.final_mark_ignored is True
    assert BANK.full_text[normalized.start : normalized.end] == "fährt 300 km"


def test_a_literal_final_mark_needs_no_rule() -> None:
    result = cq.check_quote(BANK, "S1", "300 km weit.", "normalized")
    assert (result.location_valid, result.final_mark_ignored) == (True, False)


def test_an_omitted_final_mark_is_a_literal_part_and_valid_in_both_modes() -> None:
    assert _both("S1", "Das Auto fährt 300 km weit") == (True, True)


@pytest.mark.parametrize(
    "quote",
    [
        pytest.param("fährt 300 km..", id="two-marks"),
        pytest.param("fährt 300 km!?", id="mixed-marks"),
        pytest.param("fährt 300 km,", id="comma"),
        pytest.param("fährt 300 km;", id="semicolon"),
        pytest.param("fährt 300 km:", id="colon"),
        pytest.param("fährt 300 km…", id="ellipsis"),
        pytest.param("fährt 300 km. ", id="mark-then-space"),
        pytest.param("fährt. 300 km", id="inner-mark"),
        pytest.param(".fährt 300 km", id="leading-mark"),
    ],
)
def test_only_a_single_final_mark_is_ignored(quote: str) -> None:
    assert _both("S1", quote) == (False, False)


@pytest.mark.parametrize(
    ("sid", "quote"),
    [
        pytest.param("S1", "fährt 301 km.", id="changed-number"),
        pytest.param("S1", "Fährt 300 km.", id="changed-case"),
        pytest.param("S1", "fährt 300 Kilometer.", id="changed-word"),
        pytest.param("S1", "Niemand schrieb das.", id="fabricated"),
        pytest.param("S1", "teuer und laut.", id="wrong-sentence"),
    ],
)
def test_the_final_mark_rule_rescues_no_other_defect(sid: str, quote: str) -> None:
    assert _both(sid, quote) == (False, False)


def test_the_final_mark_rule_cooperates_with_the_comparison_form() -> None:
    assert _both("S1", "fährt 300 km!") == (False, True)


@pytest.mark.parametrize("quote", ["", " ", " ", ".", "?", "!", "...", '"'])
def test_a_quote_without_content_fails_in_both_modes(quote: str) -> None:
    for mode in cq.MODES:
        result = cq.check_quote(BANK, "S1", quote, mode)
        assert result.location_valid is False
        assert result.reason == "no_content"


def test_the_comparison_form_keeps_every_offset() -> None:
    text = "a b c　d „e“ ‚f‘ «g» ‹h›\tj\nk"
    compared = cq.normalize_for_comparison(text)
    assert len(compared) == len(text)
    assert compared == "a b c d \"e\" 'f' \"g\" 'h' j k"


def test_the_comparison_form_leaves_other_characters_alone() -> None:
    text = "Größe: 5 % – ein Wort´s ​"
    assert cq.normalize_for_comparison(text) == text


def test_the_kernel_receives_the_located_span(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[tuple[str | None, int | None, int | None]] = []
    original = validation.validate_finding

    def spy(inspection, finding):  # type: ignore[no-untyped-def]
        seen.append(
            (finding.evidence_quote, finding.evidence_start, finding.evidence_end)
        )
        return original(inspection, finding)

    monkeypatch.setattr(cq, "validate_finding", spy)
    cq.check_quote(BANK, "S1", "fährt 300 km", "strict")
    assert ("fährt 300 km", 9, 21) in seen


def test_a_kernel_rejection_is_final(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cq, "_kernel_confirms", lambda *_: False)
    assert _both("S1", "fährt 300 km") == (False, False)


def test_a_clean_span_passes_the_kernel_and_a_moved_one_does_not() -> None:
    assert cq._kernel_confirms(BANK.full_text, "fährt", 9) is True
    assert cq._kernel_confirms(BANK.full_text, "fährt", 10) is False


def test_a_bank_with_wrong_offsets_is_refused() -> None:
    broken = loader.SentenceBank(
        "toy", 2, (loader.Sentence("S1", "Hallo", 1, 6),), "Hallo Welt"
    )
    with pytest.raises(cq.BankError, match="offsets"):
        cq.check_quote(broken, "S1", "Hallo", "strict")


def test_a_bank_outside_the_canonical_form_is_refused() -> None:
    text = "ä Welt"
    broken = loader.SentenceBank("toy", 2, (loader.Sentence("S1", text, 0, 7),), text)
    with pytest.raises(cq.BankError, match="canonical"):
        cq.check_quote(broken, "S1", "Welt", "strict")


def test_the_command_line_reports_through_its_exit_code(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "toy.json"
    path.write_bytes(loader.dump_json(BANK.as_dict()))
    common = ["--bank", str(path), "--sid", "S1", "--mode", "normalized"]
    assert cq.main([*common, "--quote", "fährt 300 km."]) == 0
    assert json.loads(capsys.readouterr().out)["final_mark_ignored"] is True
    assert cq.main([*common, "--quote", "fährt 999 km."]) == 1
