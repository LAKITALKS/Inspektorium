"""Build the inspect input and proposals for each judge and for the controls.

build_proposals.py --inputs DIR --out DIR

Canonical texts come from inspektorium.core.normalization.normalize_text of
the installed release, the same function the kernel applies to its inputs.
Each piece becomes one proposal: the claim is its first exact occurrence in
the canonical answer, and the evidence quote is located in the canonical
source by locator.py. Piece IDs are lowercased to fit the kernel's
identifier pattern; both forms are recorded.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from locator import exact_occurrences, locate  # noqa: E402

from inspektorium.core.normalization import normalize_text  # noqa: E402

JUDGES = ("grok", "astra", "gemini")
SOURCE_ID = "early-body"
RELATION = "supported"
# These fields are required by the proposal schema; validation does not read them.
FIXED = {
    "rationale": "Replay of a judge quotation; see PREREGISTRATION.md.",
    "evidence_sufficiency": "sufficient",
    "evaluator_certainty": "medium",
}
CONTROL_PHRASES = (
    "Of the 509 participants screened",
    "Two patients in the empagliflozin group experienced serious adverse events",
)
CONTROL_CHANGES = (("509", "508"), ("severe rash", "severe rush"))


def sentence_from(text: str, phrase: str) -> str:
    """The sentence that starts with phrase, up to the first full stop before space."""

    if text.count(phrase) != 1:
        raise SystemExit(f"control phrase must occur once: {phrase!r}")
    start = text.index(phrase)
    end = start
    while True:
        end = text.index(".", end + 1)
        if end + 1 == len(text) or text[end + 1].isspace():
            return text[start : end + 1]


def finding(core_id: str, answer: str, quote: str, source: str) -> tuple[dict, dict]:
    claim_start = answer.find(quote)
    if claim_start < 0:
        raise SystemExit(f"{core_id}: piece is not in the canonical answer")
    location = locate(source, quote)
    proposal = {
        "claim_id": core_id,
        "claim_text": quote,
        "claim_start": claim_start,
        "claim_end": claim_start + len(quote),
        "proposed_relation": RELATION,
        "source_id": SOURCE_ID,
        "evidence_quote": quote,
        "evidence_start": location.start,
        "evidence_end": location.end,
        **FIXED,
    }
    locator = {
        "method": location.method,
        "evidence_start": location.start,
        "evidence_end": location.end,
        "l2_ratio": None if location.method == "L1" else location.ratio,
        "exact_occurrences_in_canonical_source": exact_occurrences(source, quote),
    }
    return proposal, locator


def write_case(
    out: Path,
    answer_id: str,
    answer_raw: str,
    source_raw: str,
    findings: list[dict],
    locators: dict,
) -> None:
    out.mkdir(parents=True, exist_ok=False)
    inspection_input = {
        "schema_version": "0.1",
        "answer": {"answer_id": answer_id, "text": answer_raw},
        "sources": [
            {
                "source_id": SOURCE_ID,
                "title": "EARLY randomized clinical trial, body text",
                "text": source_raw,
            }
        ],
    }
    proposals = {"schema_version": "0.1", "findings": findings}
    for name, data in (
        ("input.json", inspection_input),
        ("proposals.json", proposals),
        ("locator.json", locators),
    ):
        (out / name).write_text(
            json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
        )


def build(inputs: Path, out: Path) -> None:
    source_raw = (inputs / "source/early_body.txt").read_text(encoding="utf-8")
    source = normalize_text(source_raw)
    pieces = json.loads((inputs / "extraction/pieces.json").read_text(encoding="utf-8"))
    for judge in JUDGES:
        answer_raw = (inputs / f"judges/{judge}_lauf3.txt").read_text(encoding="utf-8")
        answer = normalize_text(answer_raw)
        findings, locators = [], {}
        for piece in (p for p in pieces if p["judge"] == judge):
            quote = normalize_text(piece["quote"])
            core_id = piece["id"].lower()
            proposal, locator = finding(core_id, answer, quote, source)
            locator["piece_id"] = piece["id"]
            locator["quote_changed_by_normalize_text"] = quote != piece["quote"]
            findings.append(proposal)
            locators[core_id] = locator
        write_case(
            out / judge, f"{judge}-run3", answer_raw, source_raw, findings, locators
        )
    positives = [sentence_from(source, phrase) for phrase in CONTROL_PHRASES]
    negatives = []
    for sentence, (old, new) in zip(positives, CONTROL_CHANGES, strict=True):
        if sentence.count(old) != 1:
            raise SystemExit(f"control change must apply once: {old!r}")
        negatives.append(sentence.replace(old, new))
    controls = [
        ("control-pos-1", positives[0]),
        ("control-pos-2", positives[1]),
        ("control-neg-1", negatives[0]),
        ("control-neg-2", negatives[1]),
    ]
    answer_raw = "\n".join(text for _, text in controls) + "\n"
    answer = normalize_text(answer_raw)
    findings, locators = [], {}
    for core_id, text in controls:
        proposal, locator = finding(core_id, answer, text, source)
        locator["piece_id"] = core_id
        findings.append(proposal)
        locators[core_id] = locator
    write_case(out / "controls", "controls", answer_raw, source_raw, findings, locators)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    build(args.inputs, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
