"""AA-P9/1.0 records for bound disagreement and review, not release decisions."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

CONTRACT_VERSION = "AA-P9/1.0"
Origin = Literal["original", "model_review", "stability", "human_correction"]
Route = Literal["AUTO_RESOLVABLE", "REVIEW_RECOMMENDED", "HUMAN_REVIEW_REQUIRED", "UNRESOLVED"]
Dimension = Literal[
    "label", "evidence", "proposition", "causal_strength", "product_transfer",
    "search_scope", "composite", "unknown",
]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class ReviewPosition(StrictModel):
    position_id: str
    case_id: str
    run_id: str
    claim_id: str
    origin: Origin
    provider: str
    model: str
    raw_sha256: str
    agent_result: dict[str, Any]
    forensic_record: dict[str, Any] | None = None
    phase8: dict[str, Any]


class ConflictPosition(StrictModel):
    position_id: str
    value: Any
    evidence_ids: list[str] = Field(default_factory=list)


class Disagreement(StrictModel):
    disagreement_id: str
    case_id: str
    claim_id: str
    proposition_ids: list[str] = Field(default_factory=list)
    dimension: Dimension
    field: str
    positions: list[ConflictPosition]
    material: bool
    reason: str
    resolution: Literal["unresolved", "adjudicated"] = "unresolved"
    provenance: list[str] = Field(default_factory=list)


class ReviewTrigger(StrictModel):
    trigger_id: str
    code: str
    case_id: str
    claim_id: str
    position_ids: list[str] = Field(default_factory=list)
    proposition_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    field: str
    reason: str
    material: bool = True
    mandatory: bool = True


class Phase9Assessment(StrictModel):
    contract_version: str = CONTRACT_VERSION
    case_id: str
    technical_status: Literal["completed", "not_executed", "incomplete"]
    route: Route
    mandatory: bool = False
    execution_status: Literal["not_executed", "completed", "failed"] = "not_executed"
    review_state: Literal["not_required", "pending", "unresolved", "adjudicated"] = "not_required"
    positions: list[ReviewPosition] = Field(default_factory=list)
    conflicts: list[Disagreement] = Field(default_factory=list)
    triggers: list[ReviewTrigger] = Field(default_factory=list)
    uncertainty: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)
    assurance_scope: str = (
        "Checks represented positions, identity, materiality and routing. No majority vote, "
        "scientific truth, reviewer independence or release authorization is inferred."
    )
