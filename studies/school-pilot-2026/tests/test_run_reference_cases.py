"""The component test runner, tested on invented cases only.

The committed and the held-out reference cases are not used here: running the
checker on them is the measurement itself.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pytest
import run_reference_cases as runner
from genius_loader import build_bank
from make_reference_cases import EXPECTED

BANK = build_bank("toy", ["Das Auto fährt 400 km weit.", "Wasserstoff ist teuer."])
QUOTES = {
    "valid_exact": ("S1", "Auto fährt 400 km"),
    "wrong_location": ("S2", "Auto fährt 400 km"),
    "altered_number": ("S1", "Auto fährt 401 km"),
    "altered_word": ("S1", "Das Fahrrad fährt"),
    "fabricated": ("S1", "Ein fremder Satz steht hier"),
    "case_change": ("S1", "das Auto fährt"),
    "format_variant": ("S1", "Auto fährt 400 km"),
    "punctuation_added": ("S2", "Wasserstoff ist!"),
}
COUNTS = dict.fromkeys(EXPECTED, 1)
STATE = {"commit": "c", "src_tree": "t", "check_quotes_blob": "b"}


def _case(case_type: str, **changes: Any) -> dict[str, Any]:
    sid, quote = QUOTES[case_type]
    strict, normalized = EXPECTED[case_type]
    return {
        "case_id": f"toy.{case_type}.1",
        "text_id": "toy",
        "claimed_sid": sid,
        "quote": quote,
        "type": case_type,
        "expected_strict": strict,
        "expected_normalized": normalized,
        **changes,
    }


CASES = [_case(case_type) for case_type in EXPECTED]


@pytest.fixture
def folder(tmp_path: Path) -> Path:
    (tmp_path / "banks").mkdir()
    (tmp_path / "banks/toy.json").write_text(json.dumps(asdict(BANK)), "utf-8")
    (tmp_path / "cases.json").write_text(json.dumps(CASES), "utf-8")
    counts = {name: {"development": 1, "held_out": 1} for name in EXPECTED}
    (tmp_path / "summary.json").write_text(json.dumps({"by_type": counts}), "utf-8")
    return tmp_path


@pytest.fixture
def frozen(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(runner, "frozen_state", lambda: dict(STATE))


def _arguments(folder: Path, part: str, *more: str) -> list[str]:
    return [
        *("--part", part, "--cases", str(folder / "cases.json")),
        *("--banks", str(folder / "banks"), "--summary", str(folder / "summary.json")),
        *("--out", str(folder / "result.json"), *more),
    ]


def _digest(folder: Path) -> str:
    return hashlib.sha256((folder / "cases.json").read_bytes()).hexdigest()


def test_correct_verdicts_give_no_deviation() -> None:
    result = runner.evaluate(CASES, {"toy": BANK})
    assert result["deviations"] == []
    nothing = {"cases": 8, "false_accept": 0, "false_reject": 0}
    assert result["total"] == {"strict": nothing, "normalized": nothing}
    assert set(result["by_type"]) == set(EXPECTED)
    one = {"cases": 1, "false_accept": 0, "false_reject": 0}
    for cells in result["by_type"].values():
        assert cells == {"strict": one, "normalized": one}


def test_a_wrongly_accepted_case_is_a_false_accept() -> None:
    case = _case("altered_word", quote="Das Auto fährt")
    result = runner.evaluate([case], {"toy": BANK})
    assert result["total"]["strict"] == {
        "cases": 1,
        "false_accept": 1,
        "false_reject": 0,
    }
    assert result["deviations"] == [
        {
            "case_id": "toy.altered_word.1",
            "mode": mode,
            "kind": "false_accept",
            "reason": "ok",
        }
        for mode in ("strict", "normalized")
    ]


def test_a_wrongly_rejected_case_is_a_false_reject() -> None:
    case = _case("valid_exact", quote="Auto fliegt 400 km")
    result = runner.evaluate([case], {"toy": BANK})
    assert result["total"]["normalized"]["false_reject"] == 1
    assert result["total"]["normalized"]["false_accept"] == 0
    assert {item["reason"] for item in result["deviations"]} == {"not_in_text"}


def test_the_location_decides_not_the_text() -> None:
    case = _case("wrong_location", expected_strict=True, expected_normalized=True)
    result = runner.evaluate([case], {"toy": BANK})
    assert result["total"]["strict"]["false_reject"] == 1
    assert result["deviations"][0]["reason"] == "wrong_location"


def test_the_two_modes_are_counted_apart() -> None:
    result = runner.evaluate(
        [_case("format_variant", expected_strict=True)], {"toy": BANK}
    )
    assert result["total"]["strict"]["false_reject"] == 1
    assert result["total"]["normalized"]["false_reject"] == 0


@pytest.mark.parametrize(
    ("cases", "message"),
    [
        ([*CASES, CASES[0]], "twice"),
        ([_case("valid_exact", expected_strict=False), *CASES[1:]], "label"),
        ([_case("valid_exact", type="unknown"), *CASES[1:]], "label"),
        (CASES[1:], "number of cases"),
        ([*CASES, _case("fabricated", case_id="toy.2")], "number of cases"),
    ],
)
def test_unexpected_cases_are_refused(
    cases: list[dict[str, Any]], message: str
) -> None:
    with pytest.raises(runner.RunError, match=message):
        runner.read_cases(json.dumps(cases).encode(), COUNTS)


def test_expected_cases_are_read() -> None:
    assert runner.read_cases(json.dumps(CASES).encode(), COUNTS) == CASES


@pytest.mark.usefixtures("frozen")
def test_the_held_out_part_needs_its_hash(folder: Path) -> None:
    with pytest.raises(runner.RunError, match="needs its SHA-256"):
        runner.main(_arguments(folder, "held_out"))
    assert not (folder / "result.json").exists()


@pytest.mark.usefixtures("frozen")
def test_a_wrong_hash_stops_before_the_cases_are_read(
    folder: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def refuse(*_: object) -> None:
        raise AssertionError("the cases were read")

    monkeypatch.setattr(runner, "read_cases", refuse)
    with pytest.raises(runner.RunError, match="not the given one"):
        runner.main(_arguments(folder, "held_out", "--sha256", "0" * 64))
    assert not (folder / "result.json").exists()


@pytest.mark.usefixtures("frozen")
@pytest.mark.parametrize("part", runner.PARTS)
def test_a_run_writes_counts_and_no_case_text(
    folder: Path, part: str, capsys: pytest.CaptureFixture[str]
) -> None:
    digest = _digest(folder)
    assert runner.main(_arguments(folder, part, "--sha256", digest)) == 0
    written = (folder / "result.json").read_text("utf-8")
    result = json.loads(written)
    assert result["part"] == part
    assert result["cases_sha256"] == digest
    assert result["frozen"] == STATE
    assert capsys.readouterr().out == (
        f"{part}, cases {digest}\n"
        "strict: false accepts 0 of 7, false rejects 0 of 1\n"
        "normalized: false accepts 0 of 5, false rejects 0 of 3\n"
    )
    for _, quote in QUOTES.values():
        assert quote not in written


@pytest.mark.usefixtures("frozen")
def test_an_existing_result_is_not_replaced(folder: Path) -> None:
    (folder / "result.json").write_bytes(b"earlier")
    with pytest.raises(runner.RunError, match="already exists"):
        runner.main(_arguments(folder, "development"))
    assert (folder / "result.json").read_bytes() == b"earlier"


def _fake_git(**answers: str) -> Any:
    known = {
        "hash-object": runner.FROZEN_CHECKER_BLOB,
        "rev-parse HEAD:src": runner.FROZEN_SRC_TREE,
        "rev-parse HEAD": "commit",
        "status": "",
    }
    known.update({name.replace("_", "-"): value for name, value in answers.items()})

    def answer(*arguments: str) -> str:
        joined = " ".join(arguments)
        return known.get(joined, known.get(arguments[0], ""))

    return answer


def test_the_agreed_state_passes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(runner, "git", _fake_git())
    monkeypatch.setattr(
        runner.inspektorium, "__file__", str(runner.REPO_ROOT / "src/x.py")
    )
    assert runner.frozen_state() == {
        "commit": "commit",
        "src_tree": runner.FROZEN_SRC_TREE,
        "check_quotes_blob": runner.FROZEN_CHECKER_BLOB,
    }


@pytest.mark.parametrize(
    ("answers", "message"),
    [
        ({"hash_object": "0" * 40}, "frozen tool differs"),
        ({"rev-parse HEAD:src": "0" * 40}, "frozen tool differs"),
        ({"status": " M src/inspektorium/x.py"}, "uncommitted"),
    ],
)
def test_a_changed_tool_stops_the_run(
    monkeypatch: pytest.MonkeyPatch, answers: dict[str, str], message: str
) -> None:
    monkeypatch.setattr(runner, "git", _fake_git(**answers))
    monkeypatch.setattr(
        runner.inspektorium, "__file__", str(runner.REPO_ROOT / "src/x.py")
    )
    with pytest.raises(runner.RunError, match=message):
        runner.frozen_state()


def test_a_foreign_kernel_stops_the_run(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(runner, "git", _fake_git())
    monkeypatch.setattr(runner.inspektorium, "__file__", str(tmp_path / "x.py"))
    with pytest.raises(runner.RunError, match="kernel"):
        runner.frozen_state()


def test_the_frozen_ids_are_those_of_the_frozen_tool_test() -> None:
    import test_frozen_tools as frozen_tools

    assert runner.FROZEN_SRC_TREE == frozen_tools.FROZEN_SRC_TREE
    assert runner.FROZEN_CHECKER_BLOB == frozen_tools.FROZEN_CHECKER_BLOB
