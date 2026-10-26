"""Strict public data contracts for Inspektorium v0.1."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictInt,
    StrictStr,
    StringConstraints,
    field_validator,
    model_validator,
)

from inspektorium.core.normalization import normalize_text
from inspektorium.core.relations import (
    DeterministicValidationStatus,
    EvaluatorCertainty,
    EvidenceRelation,
    EvidenceSufficiency,
    ValidationIssueCode,
)

Identifier = Annotated[
    StrictStr,
    StringConstraints(
        pattern=r"^[a-z][a-z0-9]*(?:[-_][a-z0-9]+)*$",
        min_length=1,
        max_length=80,
    ),
]
Sha256Hex = Annotated[StrictStr, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
NonEmptyText = Annotated[StrictStr, StringConstraints(min_length=1)]


class StrictModel(BaseModel):
    """Immutable model that rejects fields outside its public contract."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class AnswerInput(StrictModel):
    """The single answer inspected by one invocation."""

    answer_id: Identifier = "answer"
    text: NonEmptyText

    @field_validator("text")
    @classmethod
    def canonicalize_text(cls, value: str) -> str:
        return normalize_text(value)


class SourceDocument(StrictModel):
    """A source document explicitly supplied by the user."""

    source_id: Identifier
    title: NonEmptyText | None = None
    text: NonEmptyText

    @field_validator("text")
    @classmethod
    def canonicalize_text(cls, value: str) -> str:
        return normalize_text(value)


class InspectionInput(StrictModel):
    """Canonical source-bounded input bundle."""

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
    """Evaluator-generated semantic judgment and proposed citation.

    Evidence fields are required keys but may be null. Keeping them independent
    lets deterministic validation expose incomplete references rather than
    repairing them or silently discarding the proposal.
    """

    claim_id: Identifier
    claim_text: NonEmptyText
    claim_start: StrictInt = Field(ge=0)
    claim_end: StrictInt = Field(ge=0)
    proposed_relation: EvidenceRelation
    source_id: Identifier | None
    evidence_quote: NonEmptyText | None
    evidence_start: StrictInt | None = Field(ge=0)
    evidence_end: StrictInt | None = Field(ge=0)
    rationale: NonEmptyText
    evidence_sufficiency: EvidenceSufficiency
    evaluator_certainty: EvaluatorCertainty

    @property
    def evidence_field_count(self) -> int:
        """Return how many evidence-reference fields are non-null."""

        return sum(
            value is not None
            for value in (
                self.source_id,
                self.evidence_quote,
                self.evidence_start,
                self.evidence_end,
            )
        )

    @property
    def has_complete_evidence_reference(self) -> bool:
        return self.evidence_field_count == 4


class ProposalBatch(StrictModel):
    """Strict output contract for precomputed or provider proposals."""

    schema_version: Literal["0.1"] = "0.1"
    findings: tuple[ProposedFinding, ...]

    @model_validator(mode="after")
    def claim_ids_are_unique(self) -> ProposalBatch:
        claim_ids = [finding.claim_id for finding in self.findings]
        if len(claim_ids) != len(set(claim_ids)):
            raise ValueError("claim_id values must be unique")
        return self


class ValidationIssue(StrictModel):
    """One deterministic failure with a stable machine-readable code."""

    code: ValidationIssueCode
    message: NonEmptyText


class ValidatedFinding(ProposedFinding):
    """A semantic proposal annotated by deterministic mechanical checks."""

    claim_span_verified: StrictBool
    evidence_span_verified: StrictBool | None
    deterministic_validation_status: DeterministicValidationStatus
    reportable_relation: EvidenceRelation | None
    validation_issues: tuple[ValidationIssue, ...]

    @model_validator(mode="after")
    def reportability_is_gated_without_claiming_semantic_proof(
        self,
    ) -> ValidatedFinding:
        if self.evidence_field_count == 0:
            missing_required_citation = (
                self.proposed_relation.requires_citation
                and self.evidence_span_verified is False
            )
            if (
                self.evidence_span_verified is not None
                and not missing_required_citation
            ):
                raise ValueError(
                    "evidence span status must be null when no citation is proposed"
                )
        if self.evidence_field_count > 0 and self.evidence_span_verified is None:
            raise ValueError("a proposed citation requires an evidence span result")
        if (
            self.evidence_span_verified is True
            and not self.has_complete_evidence_reference
        ):
            raise ValueError(
                "a verified citation requires a complete evidence reference"
            )

        if self.deterministic_validation_status is DeterministicValidationStatus.PASSED:
            if not self.claim_span_verified:
                raise ValueError("a passed guard requires an exact claim span")
            if (
                self.proposed_relation.requires_citation
                and not self.evidence_span_verified
            ):
                raise ValueError(
                    "this proposed relation requires an exact citation span"
                )
            if self.evidence_field_count > 0 and not self.evidence_span_verified:
                raise ValueError("a supplied optional citation must validate exactly")
            if self.reportable_relation is not self.proposed_relation:
                raise ValueError(
                    "a passed guard exposes the unchanged proposed relation"
                )
            if self.validation_issues:
                raise ValueError("a passed guard cannot contain validation failures")
        else:
            if self.reportable_relation is not None:
                raise ValueError("a failed guard cannot expose a reportable relation")
            if not self.validation_issues:
                raise ValueError(
                    "a failed guard requires at least one validation issue"
                )
        return self


class SourceFingerprint(StrictModel):
    """SHA-256 fingerprint for one canonical source."""

    source_id: Identifier
    sha256: Sha256Hex


class InputFingerprints(StrictModel):
    """Simple deterministic provenance for canonical inspection inputs."""

    algorithm: Literal["sha256"] = "sha256"
    answer_sha256: Sha256Hex
    sources: tuple[SourceFingerprint, ...] = Field(min_length=1)
    canonical_bundle_sha256: Sha256Hex

    @model_validator(mode="after")
    def source_ids_are_unique_and_sorted(self) -> InputFingerprints:
        source_ids = [source.source_id for source in self.sources]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("fingerprinted source_id values must be unique")
        if source_ids != sorted(source_ids):
            raise ValueError("fingerprinted sources must be ordered by source_id")
        return self


class ReportSummary(StrictModel):
    """Mechanical counts only; never a score or aggregate semantic verdict."""

    claims_inspected: StrictInt = Field(ge=0)
    reportable_findings: StrictInt = Field(ge=0)
    citation_spans_verified: StrictInt = Field(ge=0)
    validation_failures: StrictInt = Field(ge=0)


class ScopeNotice(StrictModel):
    """Required source-bounded limitation notice."""

    basis: Literal["user_supplied_sources_only"] = "user_supplied_sources_only"
    statement: NonEmptyText
    limitations: tuple[NonEmptyText, ...] = Field(min_length=1)


class InspectionReport(StrictModel):
    """Deterministic, source-bounded inspection report."""

    schema_version: Literal["0.1"] = "0.1"
    generated_at: datetime | None = None
    fingerprints: InputFingerprints
    summary: ReportSummary
    findings: tuple[ValidatedFinding, ...]
    scope: ScopeNotice

    @model_validator(mode="after")
    def report_is_internally_consistent(self) -> InspectionReport:
        if self.generated_at is not None:
            if (
                self.generated_at.tzinfo is None
                or self.generated_at.utcoffset() is None
            ):
                raise ValueError("generated_at must include a timezone offset")

        claim_ids = [finding.claim_id for finding in self.findings]
        if len(claim_ids) != len(set(claim_ids)):
            raise ValueError("finding claim_id values must be unique")

        expected = (
            len(self.findings),
            sum(finding.reportable_relation is not None for finding in self.findings),
            sum(finding.evidence_span_verified is True for finding in self.findings),
            sum(
                finding.deterministic_validation_status
                is DeterministicValidationStatus.FAILED
                for finding in self.findings
            ),
        )
        actual = (
            self.summary.claims_inspected,
            self.summary.reportable_findings,
            self.summary.citation_spans_verified,
            self.summary.validation_failures,
        )
        if actual != expected:
            raise ValueError("summary counts must match report findings")

        fingerprinted_ids = {item.source_id for item in self.fingerprints.sources}
        for finding in self.findings:
            if (
                finding.reportable_relation is not None
                and finding.source_id is not None
                and finding.source_id not in fingerprinted_ids
            ):
                raise ValueError(
                    "a reportable citation must name a fingerprinted source"
                )
        return self


__all__ = [
    "AnswerInput",
    "InputFingerprints",
    "InspectionInput",
    "InspectionReport",
    "ProposalBatch",
    "ProposedFinding",
    "ReportSummary",
    "ScopeNotice",
    "SourceDocument",
    "SourceFingerprint",
    "StrictModel",
    "ValidatedFinding",
    "ValidationIssue",
]
