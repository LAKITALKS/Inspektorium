"""The blind coding sheet and its reading, tested on invented outputs only."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any

import export_for_coding as export
import pytest

TRAPS = {"toy": {"description": "Die Ladezeit im Satz ist falsch."}}


def _run(
    model: str = "chatbot-a",
    repetition: str = "1",
    status: str = "usable",
    version: str = "original",
    errors: int = 2,
) -> dict[str, Any]:
    return {
        "model": model,
        "text_id": "toy",
        "version": version,
        "repetition": repetition,
        "status": status,
        "model_name": f"{model} Version 9",
        "errors": [
            {
                "index": index,
                "sid": "S2" if index else None,
                "quote": f"Zitat {index}",
                "category": "Zahl",
                "explanation": f"Begründung {index}",
            }
            for index in range(errors)
        ],
    }


RECORDS = [
    _run(model, number, version=version)
    for model in ("a-bot", "z-bot")
    for version in ("original", "geheim")
    for number in "123"
]


def _filled(
    answers: dict[str, tuple[str, str]],
    records: list[dict[str, Any]],
    delimiter: str = ",",
) -> tuple[bytes, dict[str, Any]]:
    rows, key = export.build_sheet(records, TRAPS, "salz")
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=export.COLUMNS, delimiter=delimiter)
    writer.writeheader()
    for row in rows:
        answer, number = answers.get(row["lauf"], (row["antwort"] or "nein", ""))
        writer.writerow({**row, "antwort": answer, "meldung_nr": number})
    return buffer.getvalue().encode("utf-8-sig"), key


def test_every_run_gets_one_row() -> None:
    rows, _ = export.build_sheet(RECORDS, TRAPS, "salz")
    assert len(rows) == len(RECORDS)
    assert [row["lauf"] for row in rows] == [
        f"L{number:03d}" for number in range(1, 13)
    ]


def test_a_row_shows_every_report_and_the_target_description() -> None:
    rows, _ = export.build_sheet(RECORDS[:1], TRAPS, "salz")
    row = rows[0]
    assert row["zielbeschreibung"] == "Die Ladezeit im Satz ist falsch."
    assert row["meldungen"].split("\n") == [
        "1: [ohne Satznummer, Zahl] „Zitat 0“ – Begründung 0",
        "2: [S2, Zahl] „Zitat 1“ – Begründung 1",
    ]


def test_the_sheet_hides_model_version_and_repetition() -> None:
    rows, _ = export.build_sheet(RECORDS, TRAPS, "salz")
    sheet = export.sheet_bytes(rows).decode("utf-8-sig")
    for hidden in ("a-bot", "z-bot", "Version 9", "geheim", "original"):
        assert hidden not in sheet
    hidden_columns = {"model", "model_name", "version", "repetition"}
    assert not hidden_columns & set(export.COLUMNS)


def test_a_failed_run_looks_like_a_run_without_reports() -> None:
    failed = _run(status="failed")
    empty = _run(repetition="2", errors=0)
    rows, _ = export.build_sheet([failed, empty], TRAPS, "salz")
    assert {row["meldungen"] for row in rows} == {export.NO_REPORT}
    assert {row["antwort"] for row in rows} == {"nein"}


def test_a_row_with_reports_starts_without_an_answer() -> None:
    rows, _ = export.build_sheet(RECORDS[:1], TRAPS, "salz")
    assert rows[0]["antwort"] == ""


def test_the_rows_are_not_grouped_by_model() -> None:
    _, key = export.build_sheet(RECORDS, TRAPS, "salz")
    order = [origin["model"] for origin in key["runs"].values()]
    assert order != sorted(order)
    assert order != sorted(order, reverse=True)


def test_the_order_follows_the_salt() -> None:
    _, first = export.build_sheet(RECORDS, TRAPS, "salz")
    _, second = export.build_sheet(RECORDS, TRAPS, "pfeffer")
    assert first["runs"] != second["runs"]


def test_a_text_without_a_trap_stops_the_export() -> None:
    with pytest.raises(export.ExportError, match="no target"):
        export.build_sheet(RECORDS, {}, "salz")


def test_text_that_looks_like_a_formula_is_neutralized() -> None:
    rows, _ = export.build_sheet(RECORDS[:1], {"toy": {"description": "=1+1"}}, "salz")
    assert rows[0]["zielbeschreibung"] == "'=1+1"


def test_the_sheet_keeps_its_line_breaks_when_read_back() -> None:
    rows, _ = export.build_sheet(RECORDS[:1], TRAPS, "salz")
    read = list(
        csv.DictReader(io.StringIO(export.sheet_bytes(rows).decode("utf-8-sig")))
    )
    assert read[0]["meldungen"] == rows[0]["meldungen"]


def test_answers_are_read_back_to_their_runs() -> None:
    records = [_run(repetition="1"), _run(repetition="2"), _run(repetition="3")]
    _, key = export.build_sheet(records, TRAPS, "salz")
    names = sorted(key["runs"], key=lambda name: key["runs"][name]["repetition"])
    answers = {
        names[0]: ("ja", "2"),
        names[1]: ("nein", ""),
        names[2]: (" UNKLAR ", ""),
    }
    raw, key = _filled(answers, records)
    codes = export.read_codes(raw, key, records)
    prefix = ("chatbot-a", "toy", "original")
    assert codes[(*prefix, "1")] == export.Code("ja", 2)
    assert codes[(*prefix, "2")] == export.Code("nein")
    assert codes[(*prefix, "3")] == export.Code("unklar")


def test_a_sheet_saved_with_semicolons_is_read() -> None:
    records = [_run()]
    raw, key = _filled({"L001": ("ja", "1")}, records, delimiter=";")
    assert export.read_codes(raw, key, records) == {
        ("chatbot-a", "toy", "original", "1"): export.Code("ja", 1)
    }


@pytest.mark.parametrize(
    ("answer", "number", "message"),
    [
        pytest.param("", "", "answer must be", id="blank"),
        pytest.param("vielleicht", "", "answer must be", id="other-word"),
        pytest.param("ja", "", "needs the number", id="ja-without-number"),
        pytest.param("ja", "x", "needs the number", id="ja-with-text"),
        pytest.param("ja", "3", "does not exist", id="report-too-high"),
        pytest.param("ja", "0", "does not exist", id="report-zero"),
        pytest.param("nein", "1", "belongs to ja", id="nein-with-number"),
        pytest.param("unklar", "1", "belongs to ja", id="unklar-with-number"),
    ],
)
def test_a_wrong_answer_is_refused_by_row(
    answer: str, number: str, message: str
) -> None:
    records = [_run()]
    raw, key = _filled({"L001": (answer, number)}, records)
    with pytest.raises(export.CodingError, match=message) as caught:
        export.read_codes(raw, key, records)
    assert caught.value.problems[0].startswith("L001:")


def test_all_problems_are_named_at_once() -> None:
    records = [_run(repetition="1"), _run(repetition="2")]
    raw, key = _filled({"L001": ("", ""), "L002": ("ja", "")}, records)
    with pytest.raises(export.CodingError) as caught:
        export.read_codes(raw, key, records)
    assert len(caught.value.problems) == 2


def test_a_missing_row_is_refused() -> None:
    records = [_run(repetition="1"), _run(repetition="2")]
    raw, key = _filled({}, records)
    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    kept = [row for row in rows if row["lauf"] != "L002"]
    with pytest.raises(export.CodingError, match="L002: row is missing"):
        export.read_codes(export.sheet_bytes(kept), key, records)


def test_an_unknown_or_repeated_row_is_refused() -> None:
    records = [_run()]
    raw, key = _filled({"L001": ("nein", "")}, records)
    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    rows += [rows[0], {**rows[0], "lauf": "L099"}]
    with pytest.raises(export.CodingError) as caught:
        export.read_codes(export.sheet_bytes(rows), key, records)
    assert "L001: appears twice" in caught.value.problems
    assert "L099: unknown run" in caught.value.problems


def test_the_answer_of_a_failed_run_is_ignored() -> None:
    records = [_run(status="failed")]
    raw, key = _filled({"L001": ("ja", "9")}, records)
    assert export.read_codes(raw, key, records) == {}


def test_the_command_line_writes_sheet_and_key_apart(tmp_path: Path) -> None:
    imported = tmp_path / "imported.json"
    imported.write_text(json.dumps(RECORDS), "utf-8")
    targets = tmp_path / "targets.json"
    targets.write_text(json.dumps(TRAPS), "utf-8")
    sheet, key = tmp_path / "sheet.csv", tmp_path / "key.json"
    arguments = ["--imported", str(imported), "--targets", str(targets)]
    assert export.main([*arguments, "--sheet", str(sheet), "--key", str(key)]) == 0
    assert "a-bot" not in sheet.read_text("utf-8-sig")
    assert "a-bot" in key.read_text("utf-8")


@pytest.mark.parametrize("existing", ["sheet.csv", "key.json"])
def test_an_earlier_export_is_never_replaced(tmp_path: Path, existing: str) -> None:
    imported = tmp_path / "imported.json"
    imported.write_text(json.dumps(RECORDS), "utf-8")
    targets = tmp_path / "targets.json"
    targets.write_text(json.dumps(TRAPS), "utf-8")
    (tmp_path / existing).write_text("kodiert", "utf-8")
    arguments = ["--imported", str(imported), "--targets", str(targets)]
    arguments += ["--sheet", str(tmp_path / "sheet.csv")]
    arguments += ["--key", str(tmp_path / "key.json")]
    with pytest.raises(export.ExportError, match="not replaced"):
        export.main(arguments)
    assert (tmp_path / existing).read_text("utf-8") == "kodiert"
