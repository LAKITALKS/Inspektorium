"""Strict data contracts for Inspektorium v0.1.

This module defines structure and cross-field invariants only. It deliberately
does not inspect answer or source content; exact source-bound validation belongs
to the deterministic kernel planned for the next phase.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictInt,
    StrictStr,
    StringConstraints,
    model_validator,
)


Identifier = Annotated[
    StrictStr,
    StringConstraints(pattern=r"^[a-z][a-z0-9]*(?:[-_][a-z0-9]+)*$", min_length=1, max_length=80),
]
Sha256Hex = Annotated[
    StrictStr,
    StringConstraints(pattern=r"^[0-9a-f]{64}$"),
]
NonEmptyText = Annotated[StrictStr, StringConstraints(min_length=1)]


class StrictModel(BaseModel):
    """Base model that rejects unrecognized fields."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class EvidenceRelation(str, Enum):
    """The complete public evidence-relationship vocabulary."""

    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    NOT_ESTABLISHED = "not_established"
    ATTRIBUTION_MISMATCH = "attribution_mismatch"

    @property
    def requires_evidence(self) -> bool:
        """Whether v0.1 requires a source quotation for this relationship."""

        return self is not EvidenceRelation.NOT_ESTABLISHED


class EvidenceSufficiency(str, Enum):
    """Qualitative description of evidence coverage, not a probability."""

    SUFFICIENT = "sufficient"
    PARTIAL = "partial"
    INSUFFICIENT = "insufficient"


class EvaluatorCertainty(str, Enum):
    """Qualitative description of evaluator confidence, not calibration."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ValidationStatus(str, Enum):
    """Outcome of deterministic span and reference validation."""

    PASSED = "passed"
    FAILED = "failed"


class ValidationIssueCode(str, Enum):
    """Public, mechanical reasons a proposal can fail validation."""

    CLAIM_SPAN_MISMATCH = "claim_span_mismatch"
    UNKNOWN_SOURCE_ID = "unknown_source_id"
    EVIDENCE_SPAN_MISMATCH = "evidence_span_mismatch"
    EVIDENCE_QUOTE_MISMATCH = "evidence_quote_mismatch"
    MISSING_REQUIRED_EVIDENCE = "missing_required_evidence"


class AnswerInput(StrictModel):
    """The single answer inspected by one v0.1 invocation."""

    answer_id: Identifier = "answer"
    text: NonEmptyText


class SourceDocument(StrictModel):
    """A user-supplied source document."""

    source_id: Identifier
    title: NonEmptyText | None = None
    text: NonEmptyText


class InspectionInput(StrictModel):
    """The complete source-bounded input bundle."""

    schema_version: Literal["0.1"] = "0.1"
    answer: AnswerInput
    sources: tuple[SourceDocument, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def source_ids_are_unique(self) -> InspectionInput:
        source_ids = [source.source_id for source in self.sources]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("source_id values must be unique")
        return self


class ProposedFinding(StrictModel):
    """A model-proposed claim and evidence binding.

    A complete evidence reference is required for every relation except
    ``not_established``. These fields are not proof that the spans are valid.
    """

    claim_id: Identifier
    claim_text: NonEmptyText
    claim_start: StrictInt = Field(ge=0)
    claim_end: StrictInt = Field(gt=0)
    relation: EvidenceRelation
    source_id: Identifier | None = None
    evidence_quote: NonEmptyText | None = None
    evidence_start: StrictInt | None = Field(default=None, ge=0)
    evidence_end: StrictInt | None = Field(default=None, gt=0)
    rationale: NonEmptyText
    evidence_sufficiency: EvidenceSufficiency
    evaluator_certainty: EvaluatorCertainty

    @property
    def has_evidence_reference(self) -> bool:
        return self.source_id is not None

    @model_validator(mode="after")
    def spans_and_evidence_are_structurally_complete(self) -> ProposedFinding:
        if self.claim_end <= self.claim_start:
            raise ValueError("claim_end must be greater than claim_start")
        if self.claim_end - self.claim_start != len(self.claim_text):
            raise ValueError("claim offsets must have the same length as claim_text")

        evidence_fields = (
            self.source_id,
            self.evidence_quote,
            self.evidence_start,
            self.evidence_end,
        )
        supplied_count = sum(value is not None for value in evidence_fields)
        if supplied_count not in (0, len(evidence_fields)):
            raise ValueError("evidence reference fields must be supplied together")

        if self.relation.requires_evidence and supplied_count == 0:
            raise ValueError(f"{self.relation.value} requires an evidence reference")

        if supplied_count:
            assert self.evidence_quote is not None
            assert self.evidence_start is not None
            assert self.evidence_end is not None
            if self.evidence_end <= self.evidence_start:
                raise ValueError("evidence_end must be greater than evidence_start")
            if self.evidence_end - self.evidence_start != len(self.evidence_quote):
                raise ValueError(
                    "evidence offsets must have the same length as evidence_quote"
                )
        return self


class ValidatedFinding(ProposedFinding):
    """A proposal annotated with deterministic validation results."""

    claim_span_verified: StrictBool
    evidence_span_verified: StrictBool | None
    validation_status: ValidationStatus
    verified_relation: EvidenceRelation | None

    @model_validator(mode="after")
    def verified_relation_is_gated_by_validation(self) -> ValidatedFinding:
        if self.has_evidence_reference and self.evidence_span_verified is None:
            raise ValueError("an evidence reference requires an evidence verification result")
        if not self.has_evidence_reference and self.evidence_span_verified is not None:
            raise ValueError("evidence verification must be null when no evidence was proposed")

        if self.validation_status is ValidationStatus.PASSED:
            if not self.claim_span_verified:
                raise ValueError("a passed finding requires a verified claim span")
            if self.has_evidence_reference and not self.evidence_span_verified:
                raise ValueError("a passed evidence binding requires a verified evidence span")
            if self.verified_relation is not self.relation:
                raise ValueError("a passed finding must expose its relation as verified")
        else:
            if self.verified_relation is not None:
                raise ValueError("a failed finding cannot expose a verified relation")
            mechanical_failure = (
                not self.claim_span_verified
                or self.evidence_span_verified is False
            )
            if not mechanical_failure:
                raise ValueError("a failed finding requires a failed mechanical check")
        return self


class SourceFingerprint(StrictModel):
    """SHA-256 fingerprint for one named source."""

    source_id: Identifier
    sha256: Sha256Hex


class InputFingerprints(StrictModel):
    """Simple deterministic provenance for a report's textual inputs."""

    algorithm: Literal["sha256"] = "sha256"
    answer_sha256: Sha256Hex
    sources: tuple[SourceFingerprint, ...] = Field(min_length=1)
    normalized_bundle_sha256: Sha256Hex

    @model_validator(mode="after")
    def source_ids_are_unique(self) -> InputFingerprints:
        source_ids = [source.source_id for source in self.sources]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("fingerprinted source_id values must be unique")
        return self


class ReportSummary(StrictModel):
    """Counts only; never a quality score or aggregate verdict."""

    claims_inspected: StrictInt = Field(ge=0)
    evidence_bindings_verified: StrictInt = Field(ge=0)
    validation_failures: StrictInt = Field(ge=0)


class ValidationWarning(StrictModel):
    """Visible explanation of one deterministic validation failure."""

    claim_id: Identifier
    code: ValidationIssueCode
    message: NonEmptyText


class ScopeNotice(StrictModel):
    """Required source-bounded limitation notice."""

    basis: Literal["user_supplied_sources_only"] = "user_supplied_sources_only"
    statement: NonEmptyText
    limitations: tuple[NonEmptyText, ...] = Field(min_length=1)


class InspectionReport(StrictModel):
    """Machine-readable v0.1 inspection report."""

    schema_version: Literal["0.1"] = "0.1"
    generated_at: datetime
    fingerprints: InputFingerprints
    summary: ReportSummary
    findings: tuple[ValidatedFinding, ...]
    validation_warnings: tuple[ValidationWarning, ...]
    scope: ScopeNotice

    @model_validator(mode="after")
    def report_is_internally_consistent(self) -> InspectionReport:
        if self.generated_at.tzinfo is None or self.generated_at.utcoffset() is None:
            raise ValueError("generated_at must include a timezone offset")

        claim_ids = [finding.claim_id for finding in self.findings]
        if len(claim_ids) != len(set(claim_ids)):
            raise ValueError("finding claim_id values must be unique")

        claims_inspected = len(self.findings)
        bindings_verified = sum(
            finding.validation_status is ValidationStatus.PASSED
            and finding.evidence_span_verified is True
            for finding in self.findings
        )
        failures = sum(
            finding.validation_status is ValidationStatus.FAILED
            for finding in self.findings
        )
        expected = (claims_inspected, bindings_verified, failures)
        actual = (
            self.summary.claims_inspected,
            self.summary.evidence_bindings_verified,
            self.summary.validation_failures,
        )
        if actual != expected:
            raise ValueError("summary counts must match report findings")

        fingerprinted_source_ids = {
            source.source_id for source in self.fingerprints.sources
        }
        for finding in self.findings:
            if (
                finding.validation_status is ValidationStatus.PASSED
                and finding.source_id is not None
                and finding.source_id not in fingerprinted_source_ids
            ):
                raise ValueError(
                    "a passed evidence binding must name a fingerprinted source"
                )

        failed_ids = {
            finding.claim_id
            for finding in self.findings
            if finding.validation_status is ValidationStatus.FAILED
        }
        warning_ids = {warning.claim_id for warning in self.validation_warnings}
        unknown_warning_ids = warning_ids - failed_ids
        if unknown_warning_ids:
            raise ValueError("validation warnings may reference only failed findings")
        if not failed_ids.issubset(warning_ids):
            raise ValueError("every failed finding requires a validation warning")
        return self


__all__ = [
    "AnswerInput",
    "EvidenceRelation",
    "EvidenceSufficiency",
    "EvaluatorCertainty",
    "InputFingerprints",
    "InspectionInput",
    "InspectionReport",
    "ProposedFinding",
    "ReportSummary",
    "ScopeNotice",
    "SourceDocument",
    "SourceFingerprint",
    "ValidatedFinding",
    "ValidationIssueCode",
    "ValidationStatus",
    "ValidationWarning",
]
