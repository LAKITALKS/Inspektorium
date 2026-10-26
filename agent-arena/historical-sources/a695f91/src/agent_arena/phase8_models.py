"""Small, strict Phase-8 extraction and derived-result contracts (AA-P8/1.0).

These objects deliberately do not import schemas: the existing record remains
the owner of source evidence and capture provenance. Extraction is untrusted.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ScientificState = Literal["supported", "unsupported", "contradicted", "unknown"]
TechnicalStatus = Literal["completed", "not_executed", "incomplete"]
Directness = Literal["direct", "partial", "indirect", "remote", "unknown"]
Observation = Literal[
    "support", "no_evidence_found", "search_incomplete", "no_effect_observed",
    "contradiction", "inconclusive", "unknown",
]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class OriginalSpan(StrictModel):
    start: int = Field(ge=0)
    end: int = Field(gt=0)
    text: str = Field(min_length=1)


class SemanticAttributes(StrictModel):
    population: str | None = None
    species: str | None = None
    intervention: str | None = None
    dose: str | None = None
    formulation: str | None = None
    route: str | None = None
    comparator: str | None = None
    endpoint: str | None = None
    endpoint_type: str | None = None
    relation: str | None = None
    effect_direction: str | None = None
    effect_magnitude: str | None = None
    effect_basis: str | None = None
    follow_up: str | None = None
    certainty: str | None = None
    comparison: str | None = None


class EvidenceBinding(StrictModel):
    binding_id: str = Field(min_length=1)
    proposition_id: str = Field(min_length=1)
    evidence_id: str = Field(min_length=1)
    directness: Directness = "unknown"
    observation: Observation = "unknown"
    search_scope_id: str | None = None
    reason: str = Field(min_length=1)


class EvidenceDescription(StrictModel):
    evidence_id: str = Field(min_length=1)
    evidence_type: Literal[
        "descriptive", "observational", "mechanistic", "in_vitro", "animal",
        "controlled_intervention", "review", "unknown",
    ] = "unknown"
    source_role: str = Field(min_length=1)
    attributes: SemanticAttributes
    randomized: bool | None = None
    identification_evidence_ids: list[str] = Field(default_factory=list)
    identification_argument: str | None = None
    design_limitations: list[str] = Field(default_factory=list)
    underlying_evidence_ids: list[str] = Field(default_factory=list)
    study_id: str | None = None
    cohort_id: str | None = None
    dataset_id: str | None = None
    quality: str | None = None


class InferenceBridge(StrictModel):
    bridge_id: str = Field(min_length=1)
    kind: Literal["mechanism_to_outcome", "causal_identification", "semantic_transfer"]
    premise_proposition_ids: list[str] = Field(default_factory=list)
    conclusion_proposition_id: str = Field(min_length=1)
    evidence_ids: list[str] = Field(default_factory=list)
    dimensions: list[str] = Field(default_factory=list)
    state: Literal["supported", "partial", "unsupported", "unknown"]
    reason: str = Field(min_length=1)


class ProductTransfer(StrictModel):
    transfer_id: str = Field(min_length=1)
    binding_id: str = Field(min_length=1)
    state: Literal[
        "direct_match", "supported_transfer", "unsupported_transfer", "unknown_transfer",
    ]
    dimensions: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    reason: str = Field(min_length=1)


class Proposition(StrictModel):
    proposition_id: str = Field(min_length=1)
    parent_claim_id: str = Field(min_length=1)
    proposition_text: str = Field(min_length=1)
    original_span: OriginalSpan
    materiality: Literal["required", "optional"]
    attributes: SemanticAttributes
    material_dimensions: list[str] = Field(default_factory=list)
    not_applicable: dict[str, str] = Field(default_factory=dict)
    evidence_bindings: list[EvidenceBinding] = Field(default_factory=list)
    reported_verdict: ScientificState
    uncertainty: list[str] = Field(default_factory=list)
    reason: str = Field(min_length=1)
    provenance_id: str = Field(min_length=1)
    search_question: str = Field(min_length=1)
    search_scope_ids: list[str] = Field(default_factory=list)
    required_bridge_ids: list[str] = Field(default_factory=list)
    premise_proposition_ids: list[str] = Field(default_factory=list)
    observation_target: Observation | None = None


class ClaimLogic(StrictModel):
    operator: Literal["leaf", "and", "or"]
    proposition_id: str | None = None
    children: list[ClaimLogic] = Field(default_factory=list)


class SemanticTransformation(StrictModel):
    transformation_id: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    stage: Literal["extraction", "search_question", "internal", "summary"]
    from_proposition_ids: list[str] = Field(default_factory=list)
    from_text: str = Field(min_length=1)
    to_text: str = Field(min_length=1)
    from_attributes: SemanticAttributes
    to_attributes: SemanticAttributes
    asserted_state: ScientificState | None = None
    asserts_whole_claim: bool = False
    reason: str = Field(min_length=1)


class PropositionLedger(StrictModel):
    contract_version: Literal["AA-P8/1.0"] = "AA-P8/1.0"
    claim_id: str = Field(min_length=1)
    provenance_id: str = Field(min_length=1)
    original_claim: str = Field(min_length=1)
    required_proposition_ids: list[str]
    propositions: list[Proposition]
    logic: ClaimLogic
    extraction_provenance: str = Field(min_length=1)
    evidence_descriptions: list[EvidenceDescription] = Field(default_factory=list)
    bridges: list[InferenceBridge] = Field(default_factory=list)
    product_transfers: list[ProductTransfer] = Field(default_factory=list)
    transformations: list[SemanticTransformation] = Field(default_factory=list)


class PropositionAssessment(StrictModel):
    proposition_id: str
    reported_verdict: ScientificState
    derived_state: ScientificState
    reasons: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    dependency_status: str = "unknown"


class Phase8Assessment(StrictModel):
    contract_version: str = "AA-P8/1.0"
    technical_status: TechnicalStatus
    composite_state: ScientificState = "unknown"
    assessed_composite_state: ScientificState = "unknown"
    propositions: list[PropositionAssessment] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)
    transformation_findings: list[str] = Field(default_factory=list)
    assurance_scope: str = (
        "Validates represented structure and semantic constraints; does not prove "
        "complete or correct model extraction, scientific truth or efficacy."
    )


def proposition_id(claim_id: str, local_id: str) -> str:
    """Host-known claim identity + local extraction identity, stable without model hashes."""
    return f"{claim_id}:{local_id}"
