"""Write a blind sheet for coding the reports of usable runs.

The sheet has one row per error report and comment. It holds no model name, no
date, time or chat mode and no repetition number, and its rows are in random
order. A separate key file leads each item back to its run. Keep the key out of
sight until the coding is done.

The text of the reports is not edited, so a chatbot that names itself stays
recognizable there. Text that a spreadsheet would run as a formula is neutralized
with a leading apostrophe, because report text is untrusted.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import secrets
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from genius_loader import dump_json
from import_runs import USABLE

COLUMNS = (
    "item",
    "text_id",
    "version",
    "kind",
    "scope",
    "quotes",
    "category",
    "text",
    "code",
    "note",
)
ORIGIN_FIELDS = ("model", "text_id", "version", "repetition")
_FORMULA_STARTS = ("=", "+", "-", "@", "\t", "\r")

Run = Mapping[str, Any]


class ExportError(RuntimeError):
    """The export would replace an earlier sheet or key."""


def _neutralized(value: str) -> str:
    return f"'{value}" if value.startswith(_FORMULA_STARTS) else value


def _quotes(run: Run, owner: str, index: int) -> str:
    return " | ".join(
        f"{item['sid']}: {item['quote']}"
        for item in run["references"]
        if item["owner"] == owner
        and item["owner_index"] == index
        and item["sid"] is not None
    )


def coding_items(records: Sequence[Run]) -> list[dict[str, Any]]:
    """List every report of every usable run, with its origin."""

    items: list[dict[str, Any]] = []
    for run in records:
        if run["status"] != USABLE:
            continue
        origin = {key: run[key] for key in ORIGIN_FIELDS}
        for error in run["errors"]:
            items.append(
                {
                    "origin": {**origin, "kind": "error", "index": error["index"]},
                    "scope": "",
                    "quotes": _quotes(run, "error", error["index"]),
                    "category": error["category"],
                    "text": error["explanation"],
                }
            )
        for comment in run["comments"]:
            items.append(
                {
                    "origin": {**origin, "kind": "comment", "index": comment["index"]},
                    "scope": comment["scope"],
                    "quotes": _quotes(run, "comment", comment["index"]),
                    "category": "",
                    "text": comment["text"],
                }
            )
    return items


def shuffled(items: list[dict[str, Any]], salt: str) -> list[dict[str, Any]]:
    """Order the items by a salted hash of their origin."""

    def rank(item: dict[str, Any]) -> str:
        origin = json.dumps(item["origin"], sort_keys=True)
        return hashlib.sha256(f"{salt}:{origin}".encode()).hexdigest()

    return sorted(items, key=rank)


def build_export(
    records: Sequence[Run], salt: str
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    """Return the blind rows and the key that leads back to the runs."""

    rows: list[dict[str, str]] = []
    key: dict[str, Any] = {}
    for number, item in enumerate(shuffled(coding_items(records), salt), start=1):
        name = f"P{number:04d}"
        origin = item["origin"]
        key[name] = origin
        rows.append(
            {
                "item": name,
                "text_id": origin["text_id"],
                "version": origin["version"],
                "kind": origin["kind"],
                "scope": item["scope"],
                "quotes": _neutralized(item["quotes"]),
                "category": _neutralized(item["category"]),
                "text": _neutralized(item["text"]),
                "code": "",
                "note": "",
            }
        )
    return rows, {"salt": salt, "items": key}


def sheet_bytes(rows: list[dict[str, str]]) -> bytes:
    """Serialize as CSV; the byte order mark lets spreadsheets read the umlauts."""

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8-sig")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--imported", type=Path, required=True)
    parser.add_argument("--sheet", type=Path, required=True)
    parser.add_argument("--key", type=Path, required=True)
    args = parser.parse_args(argv)
    for target in (args.sheet, args.key):
        if target.exists():
            raise ExportError(f"{target.name} already exists and is not replaced")
    records = json.loads(args.imported.read_text(encoding="utf-8"))
    rows, key = build_export(records, secrets.token_hex(16))
    args.sheet.write_bytes(sheet_bytes(rows))
    args.key.write_bytes(dump_json(key))
    print(f"wrote {len(rows)} items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
