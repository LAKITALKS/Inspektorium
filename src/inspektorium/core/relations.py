"""Finite public vocabularies used by Inspektorium v0.1."""

from __future__ import annotations

from enum import StrEnum


class EvidenceRelation(StrEnum):
    """Evaluator-proposed relationships to user-supplied sources."""

    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    NOT_ESTABLISHED = "not_established"
    ATTRIBUTION_MISMATCH = "attribution_mismatch"

    @property
    def requires_citation(self) -> bool:
        """Whether the relation needs an exact citation to be reportable."""

        return self is not EvidenceRelation.NOT_ESTABLISHED


class EvidenceSufficiency(StrEnum):
    """Qualitative evaluator judgment about evidence coverage."""

    SUFFICIENT = "sufficient"
    PARTIAL = "partial"
    INSUFFICIENT = "insufficient"


class EvaluatorCertainty(StrEnum):
    """Qualitative evaluator confidence, without empirical calibration."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DeterministicValidationStatus(StrEnum):
    """Outcome of mechanical claim and citation guards."""

    PASSED = "passed"
    FAILED = "failed"


class ValidationIssueCode(StrEnum):
    """Small public vocabulary for deterministic validation failures."""

    CLAIM_SPAN_MISMATCH = "claim_span_mismatch"
    UNKNOWN_SOURCE = "unknown_source"
    INVALID_EVIDENCE_OFFSETS = "invalid_evidence_offsets"
    EVIDENCE_SPAN_MISMATCH = "evidence_span_mismatch"
    INCOMPLETE_EVIDENCE_REFERENCE = "incomplete_evidence_reference"
    MALFORMED_PROPOSAL = "malformed_proposal"


__all__ = [
    "DeterministicValidationStatus",
    "EvidenceRelation",
    "EvidenceSufficiency",
    "EvaluatorCertainty",
    "ValidationIssueCode",
]
