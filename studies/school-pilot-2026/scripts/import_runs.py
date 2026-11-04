"""Import chatbot outputs without assigning anything afterwards.

Layout: ``runs/<model>/<text_id>/<version>/<repetition>.json`` holds the answer
exactly as received. ``<repetition>.meta.json`` next to it holds ``date``,
``time``, ``model_name`` (the name the chat interface shows) and ``chat_mode``.

A run that cannot be read counts as a failure. Two things are tolerated and
counted: one code block around the whole answer is removed, and an error entry
with an unknown category is marked while the run stays usable. Nothing else is
repaired. The importer sets no pointers: a comment that lists no quote stays
without one, whatever its text says.

Metadata belongs to the operator, not to the tool. A run file with a missing
field is rejected and the field is named, so that it can be added from the chat
history. If that is impossible, the metadata file holds ``protocol_error`` with
a reason instead. Such a run enters no measure and is not replaced.
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
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
PROTOCOL_ERROR = "protocol_error"

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
_CODE_FENCE = re.compile(
    r"\s*```(?:json)?[ \t]*\r?\n(.*)\r?\n```\s*", re.DOTALL | re.IGNORECASE
)
_CATEGORY_PROBLEM = re.compile(r"\$\.errors\[(\d+)\]\.category: outside the vocabulary")


class RunSetupError(RuntimeError):
    """The study setup is incomplete; this is not a failure of the model."""


class MetadataRejected(RuntimeError):
    """Run files have unusable metadata; each problem names the file and field."""

    def __init__(self, problems: list[str]) -> None:
        super().__init__("; ".join(problems))
        self.problems = problems


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
class Metadata:
    """What is recorded for every attempted run."""

    date: str
    time: str
    model_name: str
    chat_mode: str


@dataclass(frozen=True)
class ProtocolNote:
    """The operator's statement that a field cannot be reconstructed."""

    reason: str


@dataclass(frozen=True)
class ParsedOutput:
    """A readable output and what was tolerated to read it."""

    value: dict[str, Any]
    code_fence_removed: bool
    invalid_categories: frozenset[int]


@dataclass(frozen=True)
class RunRecord:
    model: str
    text_id: str
    version: str
    repetition: str
    status: str
    date: str | None = None
    time: str | None = None
    model_name: str | None = None
    chat_mode: str | None = None
    failure_reason: str | None = None
    protocol_note: str | None = None
    code_fence_removed: bool = False
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


def remove_code_fence(raw: bytes) -> tuple[bytes, bool]:
    """Remove one code block around the whole answer; change nothing else.

    The fences must stand on their own lines, and nothing but whitespace may
    stand outside them. Text around the block, or a second block, stays in the
    answer, and the strict JSON decoder then rejects it.
    """

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw, False
    match = _CODE_FENCE.fullmatch(text)
    if match is None:
        return raw, False
    return match.group(1).encode("utf-8"), True


def read_output(raw: bytes, schema: dict[str, Any]) -> ParsedOutput | None:
    """Return the decoded output, or None if it is not readable as agreed.

    An unknown category of an error entry is the only schema violation that a
    run survives. Every other violation, in any entry, makes the run a failure.
    """

    content, fenced = remove_code_fence(raw)
    try:
        value = load_strict_json(content)
    except StrictJSONError:
        return None
    invalid: set[int] = set()
    for problem in schema_problems(value, schema):
        match = _CATEGORY_PROBLEM.fullmatch(problem)
        if match is None:
            return None
        invalid.add(int(match.group(1)))
    assert isinstance(value, dict)
    return ParsedOutput(value, fenced, frozenset(invalid))


def _field_problem(name: str, value: object) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return f"missing field {name}"
    parsers: dict[str, Callable[[str], object]] = {
        "date": datetime.date.fromisoformat,
        "time": datetime.time.fromisoformat,
    }
    if name in parsers:
        try:
            parsers[name](value)
        except ValueError:
            return f"field {name} cannot be read"
    return None


def read_metadata(path: Path, label: str) -> Metadata | ProtocolNote:
    """Return the metadata or a protocol note; reject anything else by name."""

    names = list(Metadata.__dataclass_fields__)
    if not path.is_file():
        raise MetadataRejected([f"{label}: no metadata file, needs {', '.join(names)}"])
    try:
        value = load_strict_json(path.read_bytes())
    except StrictJSONError as error:
        raise MetadataRejected([f"{label}: not valid JSON"]) from error
    if not isinstance(value, dict):
        raise MetadataRejected([f"{label}: not a JSON object"])
    if PROTOCOL_ERROR in value:
        reason = value[PROTOCOL_ERROR]
        if not isinstance(reason, str) or not reason.strip():
            raise MetadataRejected([f"{label}: {PROTOCOL_ERROR} needs a reason"])
        return ProtocolNote(reason)
    problems = [_field_problem(name, value.get(name)) for name in names]
    found = [f"{label}: {problem}" for problem in problems if problem is not None]
    if found:
        raise MetadataRejected(found)
    return Metadata(**{name: value[name] for name in names})


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
    meta_path = folder / f"{repetition}.meta.json"
    metadata = read_metadata(meta_path, meta_path.relative_to(runs).as_posix())
    if isinstance(metadata, ProtocolNote):
        return RunRecord(*identity, PROTOCOL_ERROR, protocol_note=metadata.reason)
    stamp = asdict(metadata)

    def failed(reason: str) -> RunRecord:
        return RunRecord(*identity, FAILED, **stamp, failure_reason=reason)

    answer = folder / f"{repetition}.json"
    if not answer.is_file():
        return failed("no_output")
    parsed = read_output(answer.read_bytes(), schema)
    if parsed is None:
        return failed("unreadable_output")
    output = parsed.value

    path = bank_path(banks, text_id, version)
    if not path.is_file():
        raise RunSetupError(f"no sentence bank for {text_id} / {version}")
    return RunRecord(
        *identity,
        USABLE,
        **stamp,
        code_fence_removed=parsed.code_fence_removed,
        grade=output["grade"],
        comments=[
            {
                "index": index,
                "text": comment["text"],
                "scope": comment["scope"],
                "criteria": comment["criteria"],
            }
            for index, comment in enumerate(output["comments"])
        ],
        errors=[
            {
                "index": index,
                "sid": error["sid"],
                "quote": error["quote"],
                "category": error["category"],
                "explanation": error["explanation"],
                "invalid_category": index in parsed.invalid_categories,
            }
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
    """Import every attempted run; all metadata problems are named at once."""

    records: list[RunRecord] = []
    problems: list[str] = []
    for model, text_id, version, repetition in discover(runs):
        try:
            records.append(
                import_run(runs, model, text_id, version, repetition, banks, schema)
            )
        except MetadataRejected as rejected:
            problems.extend(rejected.problems)
    if problems:
        raise MetadataRejected(problems)
    return records


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, default=DEFAULT_RUNS)
    parser.add_argument("--banks", type=Path, default=DEFAULT_BANKS)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    try:
        records = import_all(args.runs, args.banks, schema)
    except MetadataRejected as rejected:
        print("REJECTED, nothing written:", file=sys.stderr)
        for problem in rejected.problems:
            print(f"  {problem}", file=sys.stderr)
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(dump_json([asdict(record) for record in records]))
    failures = sum(record.status == FAILED for record in records)
    protocol = sum(record.status == PROTOCOL_ERROR for record in records)
    fences = sum(record.code_fence_removed for record in records)
    invalid = sum(
        error["invalid_category"] for record in records for error in record.errors
    )
    print(
        f"imported {len(records)} attempted runs, {failures} failures, "
        f"{protocol} protocol errors, "
        f"{fences} code fences removed, {invalid} invalid categories"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
