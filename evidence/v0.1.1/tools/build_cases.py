"""Materialize catalog cases into input/proposal files with SHA-256 digests.

Deterministic: the same catalog always yields byte-identical files. Answer and
source texts are composed from the fixture; offsets are computed on the
product's documented canonical text (LF newlines, NFC). A fixture whose
intended placement cannot be found raises an error instead of guessing.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from common import (
    CATALOG_PATH,
    canonical_text,
    read_json,
    sha256_bytes,
    sha256_file,
    write_json,
)

ANSWER_FILLER = "Unrelated filler text for offsets. "
SOURCE_FILLER = "Unrelated source filler for offsets. "
DEFAULT_SOURCE_ID = "guide"
DEFAULT_TITLE = "Library guide"


class FixtureError(ValueError):
    """The fixture cannot be built as specified."""


def _filler(unit: str, minimum: int) -> str:
    text = unit
    while len(text) < minimum + len(unit):
        text += unit
    return text.strip()


def _compose(
    pieces: list[str], explicit: str | None, filler_unit: str, need: int
) -> tuple[str, int]:
    """Return (text, filler_start) with filler long enough for mismatch spans."""

    body = explicit if explicit is not None else " ".join(pieces)
    filler = _filler(filler_unit, max(need, 1))
    text = f"{body} {filler}" if body else filler
    filler_start = len(canonical_text(text)) - len(filler)
    return text, filler_start


def build_fixture(case: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    fixture = case["fixture"]
    findings = fixture["findings"]
    source_id = fixture.get("source_id", DEFAULT_SOURCE_ID)
    title = fixture.get("source_title", DEFAULT_TITLE)

    claim_pieces = [
        f["claim_text"] for f in findings if f["claim_placement"] == "answer"
    ]
    quote_pieces = [
        f["quote"]
        for f in findings
        if f.get("quote") is not None and f.get("quote_placement") == "source"
    ]
    mismatch_claim = max(
        [len(f["claim_text"]) for f in findings if f["claim_placement"] != "answer"]
        or [0]
    )
    mismatch_quote = max(
        [
            len(f["quote"])
            for f in findings
            if f.get("quote") is not None and f.get("quote_placement") != "source"
        ]
        or [0]
    )
    answer, answer_filler = _compose(
        claim_pieces, fixture.get("answer_text"), ANSWER_FILLER, mismatch_claim
    )
    source, source_filler = _compose(
        quote_pieces, fixture.get("source_text"), SOURCE_FILLER, mismatch_quote
    )
    canonical_answer = canonical_text(answer)
    canonical_source = canonical_text(source)

    proposals = []
    answer_cursor = 0
    source_cursor = 0
    for spec in findings:
        claim = spec["claim_text"]
        if spec["claim_placement"] == "answer":
            position = canonical_answer.find(canonical_text(claim), answer_cursor)
            if position < 0:
                raise FixtureError(f"{case['id']}: claim not found in answer")
            claim_start = position
            answer_cursor = position + len(canonical_text(claim))
        else:
            claim_start = answer_filler
        claim_end = claim_start + len(claim)

        quote = spec.get("quote")
        evidence: dict[str, Any]
        if quote is None:
            evidence = {
                "source_id": spec.get("source_id"),
                "evidence_quote": None,
                "evidence_start": None,
                "evidence_end": None,
            }
        else:
            if spec["quote_placement"] == "source":
                position = canonical_source.find(canonical_text(quote), source_cursor)
                if position < 0:
                    raise FixtureError(f"{case['id']}: quote not found in source")
                start = position
                source_cursor = position + len(canonical_text(quote))
            else:
                start = source_filler
            evidence = {
                "source_id": spec.get("source_id", source_id),
                "evidence_quote": quote,
                "evidence_start": start,
                "evidence_end": start + len(quote),
            }
        proposals.append(
            {
                "claim_id": spec["claim_id"],
                "claim_text": claim,
                "claim_start": claim_start,
                "claim_end": claim_end,
                "proposed_relation": spec["relation"],
                **evidence,
                "rationale": spec["rationale"],
                "evidence_sufficiency": spec["sufficiency"],
                "evaluator_certainty": spec["certainty"],
            }
        )
    inspection_input = {
        "schema_version": "0.1",
        "answer": {"answer_id": "answer", "text": answer},
        "sources": [{"source_id": source_id, "title": title, "text": source}],
    }
    batch = {"schema_version": "0.1", "findings": proposals}
    return inspection_input, batch


def _json_bytes(payload: Any) -> bytes:
    return (json.dumps(payload, indent=2, ensure_ascii=True) + "\n").encode("ascii")


def build_case(case: dict[str, Any], directory: Path) -> dict[str, Any]:
    inspection_input, batch = build_fixture(case)
    if "input_raw" in case:
        input_bytes = case["input_raw"].encode("utf-8", errors="strict")
    else:
        input_bytes = _json_bytes(inspection_input)
    if "proposals_raw" in case:
        proposal_bytes = case["proposals_raw"].encode("utf-8", errors="strict")
    else:
        proposal_bytes = _json_bytes(batch)
    if case["kind"] == "input_acceptance":
        decoded = json.loads(input_bytes)
        if decoded["answer"]["text"] != case["fixture"]["answer_text"]:
            raise FixtureError(f"{case['id']}: raw input answer differs from fixture")
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "input.json").write_bytes(input_bytes)
    (directory / "proposals.json").write_bytes(proposal_bytes)
    return {
        "id": case["id"],
        "input_sha256": sha256_bytes(input_bytes),
        "proposals_sha256": sha256_bytes(proposal_bytes),
        "input_bytes": len(input_bytes),
        "proposals_bytes": len(proposal_bytes),
    }


def build_all(catalog_path: Path, out: Path) -> dict[str, Any]:
    catalog = read_json(catalog_path)
    rows = [build_case(case, out / case["id"]) for case in catalog["cases"]]
    manifest = {
        "catalog_id": catalog["catalog_id"],
        "catalog_version": catalog["catalog_version"],
        "catalog_sha256": sha256_file(catalog_path),
        "case_count": len(rows),
        "cases": rows,
    }
    write_json(out / "cases_manifest.json", manifest)
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--catalog", default=str(CATALOG_PATH))
    parser.add_argument("--out", required=True, help="directory for case files")
    args = parser.parse_args(argv)
    manifest = build_all(Path(args.catalog), Path(args.out))
    print(f"built {manifest['case_count']} cases, catalog {manifest['catalog_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
