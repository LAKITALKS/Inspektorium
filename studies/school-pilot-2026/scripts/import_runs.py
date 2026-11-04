"""Import chatbot outputs without repairing or assigning anything.

Layout: ``runs/<model>/<text_id>/<version>/<repetition>.json`` holds the answer
exactly as received. ``<repetition>.meta.json`` next to it holds ``date`` and
``model_name``, the model's name as the chat interface shows it.

A run that cannot be read counts as a failure. The importer sets no pointers:
a comment that lists no quote stays without one, whatever its text says.
Nothing is extracted from surrounding prose, so an answer in a code fence or
with a sentence around the JSON is a failure too.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from check_quotes import check_quote
from genius_loader import SentenceBank, dump_json, read_bank

from inspektorium.core.strict_json import StrictJSONError, load_strict_json

STUDY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = STUDY_ROOT / "schemas" / "output.schema.json"
DEFAULT_RUNS = STUDY_ROOT / "runs"
DEFAULT_BANKS = STUDY_ROOT / "data" / "selected"
ORIGINAL = "original"

USABLE = "usable"
FAILED = "failed"

DELIVERED_VALID = "delivered_valid"
DELIVERED_INVALID = "delivered_invalid"
MISSING = "missing"
GLOBAL_COMMENT = "global_comment"

_SCHEMA_KEYWORDS = frozenset(
    {
        "$schema",
        "title",
        "type",
        "additionalProperties",
        "required",
        "properties",
        "items",
        "enum",
        "pattern",
        "minimum",
        "maximum",
    }
)
_META_NAME = re.compile(r"\.meta\.json$")


class RunSetupError(RuntimeError):
    """The study setup is incomplete; this is not a failure of the model."""


@dataclass(frozen=True)
class Reference:
    """One evidence reference with its origin in both comparison modes."""

    owner: str
    owner_index: int
    sid: str | None
    quote: str | None
    origin_strict: str
    origin_normalized: str
    text_valid_strict: bool | None
    text_valid_normalized: bool | None


@dataclass(frozen=True)
class RunRecord:
    model: str
    text_id: str
    version: str
    repetition: str
    date: str | None
    model_name: str | None
    status: str
    failure_reason: str | None = None
    grade: int | None = None
    comments: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)
    references: list[Reference] = field(default_factory=list)


def schema_problems(
    value: object, schema: dict[str, Any], path: str = "$"
) -> list[str]:
    """Check ``value`` against the subset of JSON Schema the study uses.

    The schema file stays the only definition of the format. A keyword outside
    this subset is an error, so a schema change cannot be ignored silently.
    """

    unknown = set(schema) - _SCHEMA_KEYWORDS
    if unknown:
        raise RunSetupError(f"unsupported schema keywords: {sorted(unknown)}")
    kind = schema["type"]
    problems: list[str] = []
    if kind == "object":
        if not isinstance(value, dict):
            return [f"{path}: not an object"]
        properties = schema.get("properties", {})
        problems += [
            f"{path}.{key}: missing"
            for key in schema.get("required", [])
            if key not in value
        ]
        if schema.get("additionalProperties", True) is False:
            problems += [f"{path}: extra key" for key in value if key not in properties]
        for key, item in value.items():
            if key in properties:
                problems += schema_problems(item, properties[key], f"{path}.{key}")
    elif kind == "array":
        if not isinstance(value, list):
            return [f"{path}: not an array"]
        for index, item in enumerate(value):
            problems += schema_problems(item, schema["items"], f"{path}[{index}]")
    elif kind == "string":
        if not isinstance(value, str):
            return [f"{path}: not a string"]
        if "enum" in schema and value not in schema["enum"]:
            problems.append(f"{path}: outside the vocabulary")
        if "pattern" in schema and re.fullmatch(schema["pattern"], value) is None:
            problems.append(f"{path}: wrong form")
    elif kind == "integer":
        if not isinstance(value, int) or isinstance(value, bool):
            return [f"{path}: not an integer"]
        if value < schema.get("minimum", value) or value > schema.get("maximum", value):
            problems.append(f"{path}: out of range")
    else:
        raise RunSetupError(f"unsupported schema type: {kind}")
    return problems


def read_output(raw: bytes, schema: dict[str, Any]) -> dict[str, Any] | None:
    """Return the decoded output, or None if it is not readable as agreed."""

    try:
        value = load_strict_json(raw)
    except StrictJSONError:
        return None
    if schema_problems(value, schema):
        return None
    assert isinstance(value, dict)
    return value


def read_metadata(path: Path) -> tuple[str, str] | None:
    """Return date and model name, or None if the metadata cannot be used."""

    if not path.is_file():
        return None
    try:
        value = load_strict_json(path.read_bytes())
    except StrictJSONError:
        return None
    if not isinstance(value, dict):
        return None
    day, name = value.get("date"), value.get("model_name")
    if not isinstance(day, str) or not isinstance(name, str) or not name.strip():
        return None
    try:
        date.fromisoformat(day)
    except ValueError:
        return None
    return day, name


def _delivered(
    bank: SentenceBank, owner: str, index: int, sid: str, quote: str
) -> Reference:
    strict = check_quote(bank, sid, quote, "strict")
    normalized = check_quote(bank, sid, quote, "normalized")
    return Reference(
        owner=owner,
        owner_index=index,
        sid=sid,
        quote=quote,
        origin_strict=DELIVERED_VALID if strict.location_valid else DELIVERED_INVALID,
        origin_normalized=(
            DELIVERED_VALID if normalized.location_valid else DELIVERED_INVALID
        ),
        text_valid_strict=strict.text_valid,
        text_valid_normalized=normalized.text_valid,
    )


def _no_quote(index: int, scope: str) -> Reference:
    origin = GLOBAL_COMMENT if scope == "global" else MISSING
    return Reference("comment", index, None, None, origin, origin, None, None)


def build_references(output: dict[str, Any], bank: SentenceBank) -> list[Reference]:
    """Record what the output delivered, one entry per reference."""

    references: list[Reference] = []
    for index, comment in enumerate(output["comments"]):
        if not comment["quotes"]:
            references.append(_no_quote(index, comment["scope"]))
        for item in comment["quotes"]:
            references.append(
                _delivered(bank, "comment", index, item["sid"], item["quote"])
            )
    for index, error in enumerate(output["errors"]):
        references.append(
            _delivered(bank, "error", index, error["sid"], error["quote"])
        )
    return references


def bank_path(banks: Path, text_id: str, version: str) -> Path:
    """Locate the bank a version was graded on."""

    name = text_id if version == ORIGINAL else f"{text_id}.{version}"
    return banks / f"{name}.json"


def import_run(
    runs: Path,
    model: str,
    text_id: str,
    version: str,
    repetition: str,
    banks: Path,
    schema: dict[str, Any],
) -> RunRecord:
    """Import one attempted run."""

    folder = runs / model / text_id / version
    identity = (model, text_id, version, repetition)
    metadata = read_metadata(folder / f"{repetition}.meta.json")
    day, name = metadata if metadata is not None else (None, None)

    def failed(reason: str) -> RunRecord:
        return RunRecord(*identity, day, name, FAILED, failure_reason=reason)

    answer = folder / f"{repetition}.json"
    if metadata is None:
        return failed("metadata_unusable")
    if not answer.is_file():
        return failed("no_output")
    output = read_output(answer.read_bytes(), schema)
    if output is None:
        return failed("unreadable_output")

    path = bank_path(banks, text_id, version)
    if not path.is_file():
        raise RunSetupError(f"no sentence bank for {text_id} / {version}")
    return RunRecord(
        *identity,
        day,
        name,
        USABLE,
        grade=output["grade"],
        comments=[
            {
                "index": index,
                "scope": comment["scope"],
                "criteria": comment["criteria"],
            }
            for index, comment in enumerate(output["comments"])
        ],
        errors=[
            {"index": index, "sid": error["sid"], "category": error["category"]}
            for index, error in enumerate(output["errors"])
        ],
        references=build_references(output, read_bank(path)),
    )


def discover(runs: Path) -> list[tuple[str, str, str, str]]:
    """List attempted runs; a metadata file alone also marks an attempt."""

    found: set[tuple[str, str, str, str]] = set()
    for path in runs.glob("*/*/*/*.json"):
        version = path.parent
        text = version.parent
        repetition = _META_NAME.sub("", path.name).removesuffix(".json")
        found.add((text.parent.name, text.name, version.name, repetition))
    return sorted(found)


def import_all(runs: Path, banks: Path, schema: dict[str, Any]) -> list[RunRecord]:
    return [
        import_run(runs, model, text_id, version, repetition, banks, schema)
        for model, text_id, version, repetition in discover(runs)
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, default=DEFAULT_RUNS)
    parser.add_argument("--banks", type=Path, default=DEFAULT_BANKS)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    records = import_all(args.runs, args.banks, schema)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(dump_json([asdict(record) for record in records]))
    failures = sum(record.status == FAILED for record in records)
    print(f"imported {len(records)} attempted runs, {failures} failures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
