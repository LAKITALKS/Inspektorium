"""Write the blind coding sheet and read it back after the coding.

Stage 2 of the hit rule is a human judgment. The sheet has one row per run. A row
shows all error reports of the run and the target description of the text. It
shows neither the model nor the version nor the repetition, and the rows are in
random order. A separate key leads each row back to its run. Keep the key out of
sight until the coding is done.

The coder answers one question per run: does a report describe the target error?
The answer is ``ja`` with the number of the report, ``nein`` or ``unklar``.

Report text is not edited, so a chatbot that names itself stays recognizable.
Text that a spreadsheet would run as a formula is neutralized with a leading
apostrophe, because report text is untrusted.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import secrets
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from genius_loader import dump_json
from import_runs import USABLE

COLUMNS = (
    "lauf",
    "text_id",
    "zielbeschreibung",
    "meldungen",
    "antwort",
    "meldung_nr",
    "notiz",
)
ANSWER_YES = "ja"
ANSWER_NO = "nein"
ANSWER_UNCLEAR = "unklar"
ANSWERS = (ANSWER_YES, ANSWER_NO, ANSWER_UNCLEAR)
NO_REPORT = "(keine Meldung)"
RUN_FIELDS = ("model", "text_id", "version", "repetition")
_FORMULA_STARTS = ("=", "+", "-", "@", "\t", "\r")

Run = Mapping[str, Any]
RunKey = tuple[str, str, str, str]


class ExportError(RuntimeError):
    """The export cannot be made, or would replace an earlier sheet or key."""


class CodingError(ValueError):
    """The filled sheet cannot be used; each problem names the row."""

    def __init__(self, problems: list[str]) -> None:
        super().__init__("; ".join(problems))
        self.problems = problems


@dataclass(frozen=True)
class Code:
    """The coder's answer for one run."""

    answer: str
    report: int | None = None


def run_key(run: Run) -> RunKey:
    model, text_id, version, repetition = (run[field] for field in RUN_FIELDS)
    return model, text_id, version, repetition


def _neutralized(value: str) -> str:
    return f"'{value}" if value.startswith(_FORMULA_STARTS) else value


def _report_lines(run: Run) -> str:
    """List the reports of a usable run, numbered from 1."""

    if run["status"] != USABLE or not run["errors"]:
        return NO_REPORT
    lines = []
    for number, error in enumerate(run["errors"], start=1):
        place = error["sid"] or "ohne Satznummer"
        lines.append(
            f"{number}: [{place}, {error['category']}] "
            f"„{error['quote']}“ – {error['explanation']}"
        )
    return "\n".join(lines)


def _rank(run: Run, salt: str) -> str:
    return hashlib.sha256(f"{salt}:{run_key(run)}".encode()).hexdigest()


def build_sheet(
    records: Sequence[Run], targets: Mapping[str, Mapping[str, Any]], salt: str
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    """Return the blind rows and the key that leads back to the runs."""

    rows: list[dict[str, str]] = []
    runs: dict[str, dict[str, str]] = {}
    for number, run in enumerate(
        sorted(records, key=lambda item: _rank(item, salt)), start=1
    ):
        if run["text_id"] not in targets:
            raise ExportError(f"no target for text {run['text_id']}")
        name = f"L{number:03d}"
        runs[name] = {field: run[field] for field in RUN_FIELDS}
        reports = _report_lines(run)
        rows.append(
            {
                "lauf": name,
                "text_id": run["text_id"],
                "zielbeschreibung": _neutralized(
                    targets[run["text_id"]]["description"]
                ),
                "meldungen": _neutralized(reports),
                "antwort": ANSWER_NO if reports == NO_REPORT else "",
                "meldung_nr": "",
                "notiz": "",
            }
        )
    return rows, {"salt": salt, "runs": runs}


def sheet_bytes(rows: list[dict[str, str]]) -> bytes:
    """Serialize as CSV; the byte order mark lets spreadsheets read the umlauts."""

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8-sig")


def _parse_row(row: Mapping[str, str | None], reports: int) -> Code | str:
    """Return the code of a filled row, or the reason it cannot be used."""

    answer = (row.get("antwort") or "").strip().casefold()
    number = (row.get("meldung_nr") or "").strip()
    if answer not in ANSWERS:
        return f"answer must be one of {', '.join(ANSWERS)}"
    if answer != ANSWER_YES:
        return "a number belongs to ja only" if number else Code(answer)
    if not number.isascii() or not number.isdigit():
        return "ja needs the number of a report"
    if not 1 <= int(number) <= reports:
        return f"report {number} does not exist"
    return Code(answer, int(number))


def read_codes(
    raw: bytes, key: Mapping[str, Any], records: Sequence[Run]
) -> dict[RunKey, Code]:
    """Read the filled sheet; every problem is named before anything is used.

    Spreadsheets on German systems save with semicolons, so both separators are
    read.
    """

    text = raw.decode("utf-8-sig")
    header = text.split("\n", maxsplit=1)[0]
    delimiter = ";" if header.count(";") > header.count(",") else ","
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    known: dict[str, dict[str, str]] = key["runs"]
    by_key = {run_key(run): run for run in records}
    codes: dict[RunKey, Code] = {}
    problems: list[str] = []
    seen: set[str] = set()
    for row in reader:
        name = (row.get("lauf") or "").strip()
        if name not in known:
            problems.append(f"{name or 'empty row'}: unknown run")
            continue
        if name in seen:
            problems.append(f"{name}: appears twice")
            continue
        seen.add(name)
        origin = known[name]
        identity = (
            origin["model"],
            origin["text_id"],
            origin["version"],
            origin["repetition"],
        )
        run = by_key.get(identity)
        if run is None:
            problems.append(f"{name}: run is not in the import")
        elif run["status"] == USABLE:
            parsed = _parse_row(row, len(run["errors"]))
            if isinstance(parsed, Code):
                codes[identity] = parsed
            else:
                problems.append(f"{name}: {parsed}")
    problems += [f"{name}: row is missing" for name in sorted(set(known) - seen)]
    if problems:
        raise CodingError(problems)
    return codes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--imported", type=Path, required=True)
    parser.add_argument("--targets", type=Path, required=True)
    parser.add_argument("--sheet", type=Path, required=True)
    parser.add_argument("--key", type=Path, required=True)
    args = parser.parse_args(argv)
    for target in (args.sheet, args.key):
        if target.exists():
            raise ExportError(f"{target.name} already exists and is not replaced")
    records = json.loads(args.imported.read_text(encoding="utf-8"))
    targets = json.loads(args.targets.read_text(encoding="utf-8"))
    rows, key = build_sheet(records, targets, secrets.token_hex(16))
    args.sheet.write_bytes(sheet_bytes(rows))
    args.key.write_bytes(dump_json(key))
    print(f"wrote {len(rows)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
