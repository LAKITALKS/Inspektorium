"""The blind coding export, tested on invented outputs only."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any

import export_for_coding as export
import pytest


def _run(
    model: str = "chatbot-a",
    repetition: str = "1",
    status: str = "usable",
    explanation: str = "Die Zahl stimmt nicht.",
) -> dict[str, Any]:
    return {
        "model": model,
        "text_id": "toy",
        "version": "original",
        "repetition": repetition,
        "status": status,
        "date": "2026-11-20",
        "time": "14:30",
        "model_name": f"{model} Version 9",
        "chat_mode": "Temporärer Chat",
        "errors": [
            {
                "index": 0,
                "sid": "S1",
                "quote": "300 km",
                "category": "Zahl",
                "explanation": explanation,
            }
        ],
        "comments": [
            {"index": 0, "text": "Gut gegliedert.", "scope": "global", "criteria": []},
            {"index": 1, "text": "Klare These.", "scope": "local", "criteria": ["K1"]},
        ],
        "references": [
            {"owner": "comment", "owner_index": 0, "sid": None, "quote": None},
            {"owner": "comment", "owner_index": 1, "sid": "S1", "quote": "Das Auto"},
            {"owner": "comment", "owner_index": 1, "sid": "S2", "quote": "Der Akku"},
            {"owner": "error", "owner_index": 0, "sid": "S1", "quote": "300 km"},
        ],
    }


RECORDS = [_run(model, number) for model in ("a-bot", "z-bot") for number in "12"]


def _sheet(rows: list[dict[str, str]]) -> str:
    return export.sheet_bytes(rows).decode("utf-8-sig")


def test_every_report_of_a_usable_run_gets_a_row() -> None:
    rows, _ = export.build_export(RECORDS, "salz")
    assert len(rows) == 4 * 3
    assert {row["kind"] for row in rows} == {"error", "comment"}


def test_a_comment_row_lists_all_its_quotes() -> None:
    rows, _ = export.build_export(RECORDS[:1], "salz")
    row = next(row for row in rows if row["text"] == "Klare These.")
    assert row["quotes"] == "S1: Das Auto | S2: Der Akku"


def test_the_sheet_hides_who_wrote_what_and_when() -> None:
    rows, _ = export.build_export(RECORDS, "salz")
    sheet = _sheet(rows)
    for hidden in ("a-bot", "z-bot", "Version 9", "2026-11-20", "14:30", "Temporär"):
        assert hidden not in sheet
    hidden_columns = {"model", "model_name", "date", "time", "chat_mode", "repetition"}
    assert not hidden_columns & set(export.COLUMNS)


def test_item_names_do_not_reveal_the_model() -> None:
    rows, key = export.build_export(RECORDS, "salz")
    assert [row["item"] for row in rows] == [f"P{n:04d}" for n in range(1, 13)]
    assert set(key["items"]) == {row["item"] for row in rows}


def test_the_rows_are_not_grouped_by_model() -> None:
    _, key = export.build_export(RECORDS, "salz")
    order = [origin["model"] for origin in key["items"].values()]
    assert order != sorted(order)
    assert order != sorted(order, reverse=True)


def test_the_order_follows_the_salt() -> None:
    first, _ = export.build_export(RECORDS, "salz")
    second, _ = export.build_export(RECORDS, "pfeffer")
    assert [row["text"] for row in first] != [row["text"] for row in second]


def test_the_same_salt_gives_the_same_sheet() -> None:
    assert export.build_export(RECORDS, "salz") == export.build_export(RECORDS, "salz")


def test_the_key_leads_every_item_back_to_its_run() -> None:
    rows, key = export.build_export(RECORDS, "salz")
    assert key["salt"] == "salz"
    for row in rows:
        origin = key["items"][row["item"]]
        assert origin["model"] in ("a-bot", "z-bot")
        assert origin["kind"] == row["kind"]


def test_failed_runs_and_protocol_errors_are_left_out() -> None:
    records = [_run(status="failed"), _run(status="protocol_error")]
    assert export.build_export(records, "salz")[0] == []


@pytest.mark.parametrize("text", ["=1+1", "+49", "-3", "@SUM(A1)", "\tx", "\rx"])
def test_text_that_looks_like_a_formula_is_neutralized(text: str) -> None:
    rows, _ = export.build_export([_run(explanation=text)], "salz")
    row = next(row for row in rows if row["kind"] == "error")
    assert row["text"] == f"'{text}"


def test_plain_text_stays_as_it_is() -> None:
    rows, _ = export.build_export([_run(explanation="Größe, 5 %")], "salz")
    row = next(row for row in rows if row["kind"] == "error")
    assert row["text"] == "Größe, 5 %"


def test_the_sheet_can_be_read_back_with_empty_coding_columns() -> None:
    rows, _ = export.build_export([_run(explanation='Sagt "nein", dann\nja')], "salz")
    read = list(csv.DictReader(io.StringIO(_sheet(rows))))
    assert len(read) == 3
    assert all(row["code"] == "" and row["note"] == "" for row in read)
    assert 'Sagt "nein", dann\nja' in {row["text"] for row in read}


def test_the_command_line_writes_sheet_and_key_apart(tmp_path: Path) -> None:
    imported = tmp_path / "imported.json"
    imported.write_text(json.dumps(RECORDS), "utf-8")
    sheet, key = tmp_path / "sheet.csv", tmp_path / "key.json"
    arguments = ["--imported", str(imported), "--sheet", str(sheet), "--key", str(key)]
    assert export.main(arguments) == 0
    assert "a-bot" not in sheet.read_text("utf-8-sig")
    assert "a-bot" in key.read_text("utf-8")


@pytest.mark.parametrize("existing", ["sheet.csv", "key.json"])
def test_an_earlier_export_is_never_replaced(tmp_path: Path, existing: str) -> None:
    imported = tmp_path / "imported.json"
    imported.write_text(json.dumps(RECORDS), "utf-8")
    (tmp_path / existing).write_text("kodiert", "utf-8")
    arguments = ["--imported", str(imported)]
    arguments += ["--sheet", str(tmp_path / "sheet.csv")]
    arguments += ["--key", str(tmp_path / "key.json")]
    with pytest.raises(export.ExportError, match="not replaced"):
        export.main(arguments)
    assert (tmp_path / existing).read_text("utf-8") == "kodiert"
