"""Small offline inspection workflow over precomputed proposals."""

from __future__ import annotations

from datetime import datetime

from inspektorium.core.fingerprints import fingerprint_input
from inspektorium.core.models import (
    InspectionInput,
    InspectionReport,
    ProposalBatch,
    ReportSummary,
    ScopeNotice,
)
from inspektorium.core.relations import DeterministicValidationStatus
from inspektorium.core.validation import validate_finding

SCOPE_NOTICE = ScopeNotice(
    statement=(
        "This report compares evaluator proposals with the answer and sources "
        "supplied for this inspection."
    ),
    limitations=(
        "Citation validation confirms exact text and offsets, not semantic truth.",
        "Evaluator-proposed relationships remain qualitative judgments.",
        "The report does not assess source quality, completeness, or authority.",
        "The report does not determine whether relevant evidence exists elsewhere.",
        "The report does not provide domain-specific medical, legal, or safety "
        "conclusions.",
        "The report does not assign a global score or answer-level label.",
    ),
)


def inspect_proposals(
    inspection_input: InspectionInput,
    proposals: ProposalBatch,
    *,
    generated_at: datetime | None = None,
) -> InspectionReport:
    """Validate proposals and assemble a deterministic report object."""

    findings = tuple(
        validate_finding(inspection_input, proposal) for proposal in proposals.findings
    )
    summary = ReportSummary(
        claims_inspected=len(findings),
        reportable_findings=sum(
            finding.reportable_relation is not None for finding in findings
        ),
        citation_spans_verified=sum(
            finding.evidence_span_verified is True for finding in findings
        ),
        validation_failures=sum(
            finding.deterministic_validation_status
            is DeterministicValidationStatus.FAILED
            for finding in findings
        ),
    )
    return InspectionReport(
        generated_at=generated_at,
        fingerprints=fingerprint_input(inspection_input),
        summary=summary,
        findings=findings,
        scope=SCOPE_NOTICE,
    )


__all__ = ["SCOPE_NOTICE", "inspect_proposals"]
