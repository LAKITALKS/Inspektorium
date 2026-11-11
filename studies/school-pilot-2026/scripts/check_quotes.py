"""Check one quote with a sentence number against a sentence bank.

The sentence number selects a character range through ``start`` and ``end``.
Inside that range this script looks for the quote, and the Inspektorium kernel
then decides: ``validate_finding`` confirms exact text and offsets. Nothing here
judges meaning.

Two modes exist. Strict mode applies only the kernel's normalization. Normalized
mode also compares every Unicode whitespace character as one ASCII space, every
typographic quotation mark as a straight one, and ignores one final ``.``, ``!``
or ``?`` of the quote. The README states these rules.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from genius_loader import Sentence, SentenceBank, read_bank

from inspektorium.core.models import (
    AnswerInput,
    InspectionInput,
    ProposedFinding,
    SourceDocument,
)
from inspektorium.core.normalization import normalize_text
from inspektorium.core.relations import (
    DeterministicValidationStatus,
    EvaluatorCertainty,
    EvidenceRelation,
    EvidenceSufficiency,
)
from inspektorium.core.validation import validate_finding

Mode = Literal["strict", "normalized"]
MODES: tuple[Mode, ...] = ("strict", "normalized")

FINAL_MARKS = ".!?"
_QUOTE_MAP = str.maketrans(
    {
        **dict.fromkeys("„“”‟«»", '"'),
        **dict.fromkeys("‚‘’‛‹›", "'"),
    }
)
_SOURCE_ID = "essay"


class BankError(ValueError):
    """The sentence bank is inconsistent, so no quote can be checked against it."""


@dataclass(frozen=True)
class QuoteResult:
    """The outcome for one quote in one mode."""

    mode: Mode
    sid: str
    quote: str
    text_valid: bool
    """The text occurs somewhere in the essay."""
    location_valid: bool
    """The text occurs inside the claimed sentence."""
    final_mark_ignored: bool
    start: int | None
    end: int | None
    reason: str


def normalize_for_comparison(text: str) -> str:
    """Map whitespace and quotation marks one to one; the length stays the same."""

    spaced = "".join(" " if character.isspace() else character for character in text)
    return spaced.translate(_QUOTE_MAP)


def _view(text: str, mode: Mode) -> str:
    canonical = normalize_text(text)
    return canonical if mode == "strict" else normalize_for_comparison(canonical)


def _candidates(quote: str, mode: Mode) -> list[tuple[str, bool]]:
    """Return the forms to compare, each with its ``final_mark_ignored`` flag."""

    forms = [(quote, False)]
    if mode == "normalized" and quote[-1:] in FINAL_MARKS:
        forms.append((quote[:-1], True))
    return forms


def _kernel_confirms(source: str, quote: str, start: int) -> bool:
    """Let the kernel confirm exact text and offsets of one span.

    The kernel needs a claim. The quote itself stands in for it, so the claim
    check always holds and the evidence check alone decides. The relation is
    only the kernel's way to require a citation; it says nothing about meaning.
    """

    inspection = InspectionInput(
        answer=AnswerInput(text=quote),
        sources=(SourceDocument(source_id=_SOURCE_ID, text=source),),
    )
    claim = inspection.answer.text
    finding = ProposedFinding(
        claim_id="quote",
        claim_text=claim,
        claim_start=0,
        claim_end=len(claim),
        proposed_relation=EvidenceRelation.SUPPORTED,
        source_id=_SOURCE_ID,
        evidence_quote=quote,
        evidence_start=start,
        evidence_end=start + len(quote),
        rationale="Mechanical quote check; no statement about meaning.",
        evidence_sufficiency=EvidenceSufficiency.PARTIAL,
        evaluator_certainty=EvaluatorCertainty.LOW,
    )
    outcome = validate_finding(inspection, finding)
    return (
        outcome.deterministic_validation_status is DeterministicValidationStatus.PASSED
    )


def _sentence_for(bank: SentenceBank, sid: str) -> Sentence | None:
    return next((item for item in bank.sentences if item.sid == sid), None)


def _verify_bank(bank: SentenceBank) -> None:
    if not bank.full_text:
        raise BankError("the bank has no text")
    if normalize_text(bank.full_text) != bank.full_text:
        raise BankError("full_text is not in the kernel's canonical form")
    for sentence in bank.sentences:
        if bank.full_text[sentence.start : sentence.end] != sentence.text:
            raise BankError(f"{sentence.sid} does not match its offsets")


def _locate(
    source: str, forms: list[tuple[str, bool]], low: int, high: int
) -> tuple[str, int, bool] | None:
    """Find the first form inside ``source[low:high]`` that the kernel confirms."""

    for form, ignored in forms:
        start = source.find(form, low, high)
        if start >= 0 and _kernel_confirms(source, form, start):
            return form, start, ignored
    return None


def check_quote(bank: SentenceBank, sid: str, quote: str, mode: Mode) -> QuoteResult:
    """Check ``quote`` against the sentence ``sid`` of ``bank``."""

    _verify_bank(bank)
    source = _view(bank.full_text, mode)
    if normalize_text(source) != source or len(source) != len(bank.full_text):
        raise BankError("the comparison form moved the offsets")
    compared = _view(quote, mode)
    if not any(character.isalnum() for character in compared):
        return QuoteResult(
            mode, sid, quote, False, False, False, None, None, "no_content"
        )

    forms = _candidates(compared, mode)
    anywhere = _locate(source, forms, 0, len(source))
    sentence = _sentence_for(bank, sid)
    found = (
        None
        if sentence is None
        else _locate(source, forms, sentence.start, sentence.end)
    )
    if found is not None:
        form, start, ignored = found
        return QuoteResult(
            mode, sid, quote, True, True, ignored, start, start + len(form), "ok"
        )
    if sentence is None:
        reason = "unknown_sid"
    else:
        reason = "not_in_text" if anywhere is None else "wrong_location"
    return QuoteResult(
        mode, sid, quote, anywhere is not None, False, False, None, None, reason
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bank", type=Path, required=True)
    parser.add_argument("--sid", required=True)
    parser.add_argument("--quote", required=True)
    parser.add_argument("--mode", choices=MODES, default="strict")
    args = parser.parse_args(argv)
    result = check_quote(read_bank(args.bank), args.sid, args.quote, args.mode)
    json.dump(asdict(result), sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0 if result.location_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
