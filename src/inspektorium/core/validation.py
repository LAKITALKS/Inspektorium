"""Pure deterministic validation of evaluator-proposed spans."""

from __future__ import annotations

from inspektorium.core.models import (
    InspectionInput,
    ProposedFinding,
    ValidatedFinding,
    ValidationIssue,
)
from inspektorium.core.relations import (
    DeterministicValidationStatus,
    ValidationIssueCode,
)


def _issue(code: ValidationIssueCode, message: str) -> ValidationIssue:
    return ValidationIssue(code=code, message=message)


def _claim_span_matches(answer: str, finding: ProposedFinding) -> bool:
    start = finding.claim_start
    end = finding.claim_end
    return 0 <= start <= end <= len(answer) and answer[start:end] == finding.claim_text


def validate_finding(
    inspection_input: InspectionInput,
    finding: ProposedFinding,
) -> ValidatedFinding:
    """Apply exact claim/citation guards without semantic reinterpretation."""

    issues: list[ValidationIssue] = []
    claim_span_verified = _claim_span_matches(
        inspection_input.answer.text,
        finding,
    )
    if not claim_span_verified:
        issues.append(
            _issue(
                ValidationIssueCode.CLAIM_SPAN_MISMATCH,
                "The claim text does not equal the canonical answer span at the "
                "proposed offsets.",
            )
        )

    evidence_span_verified: bool | None
    evidence_count = finding.evidence_field_count
    if evidence_count == 0:
        evidence_span_verified = None
        if finding.proposed_relation.requires_citation:
            evidence_span_verified = False
            issues.append(
                _issue(
                    ValidationIssueCode.INCOMPLETE_EVIDENCE_REFERENCE,
                    "This proposed relation requires source_id, quote, start, and end.",
                )
            )
    elif evidence_count != 4:
        evidence_span_verified = False
        issues.append(
            _issue(
                ValidationIssueCode.INCOMPLETE_EVIDENCE_REFERENCE,
                "Evidence reference fields must be either all present or all null.",
            )
        )
    else:
        assert finding.source_id is not None
        assert finding.evidence_quote is not None
        assert finding.evidence_start is not None
        assert finding.evidence_end is not None
        source_by_id = {source.source_id: source for source in inspection_input.sources}
        source = source_by_id.get(finding.source_id)
        if source is None:
            evidence_span_verified = False
            issues.append(
                _issue(
                    ValidationIssueCode.UNKNOWN_SOURCE,
                    "The proposed source_id does not name a supplied source.",
                )
            )
        else:
            start = finding.evidence_start
            end = finding.evidence_end
            offsets_valid = 0 <= start <= end <= len(
                source.text
            ) and end - start == len(finding.evidence_quote)
            if not offsets_valid:
                evidence_span_verified = False
                issues.append(
                    _issue(
                        ValidationIssueCode.INVALID_EVIDENCE_OFFSETS,
                        "The proposed evidence offsets are outside the source or do "
                        "not match the quote length.",
                    )
                )
            elif source.text[start:end] != finding.evidence_quote:
                evidence_span_verified = False
                issues.append(
                    _issue(
                        ValidationIssueCode.EVIDENCE_SPAN_MISMATCH,
                        "The proposed quote does not equal the canonical source span "
                        "at the proposed offsets.",
                    )
                )
            else:
                evidence_span_verified = True

    mandatory_citation_passed = (
        evidence_span_verified is True
        if finding.proposed_relation.requires_citation
        else evidence_count == 0 or evidence_span_verified is True
    )
    guard_passed = claim_span_verified and mandatory_citation_passed
    status = (
        DeterministicValidationStatus.PASSED
        if guard_passed
        else DeterministicValidationStatus.FAILED
    )
    return ValidatedFinding(
        **finding.model_dump(),
        claim_span_verified=claim_span_verified,
        evidence_span_verified=evidence_span_verified,
        deterministic_validation_status=status,
        reportable_relation=finding.proposed_relation if guard_passed else None,
        validation_issues=tuple(issues),
    )


__all__ = ["validate_finding"]
