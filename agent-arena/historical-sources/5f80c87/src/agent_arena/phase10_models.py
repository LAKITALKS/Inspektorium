"""Strict local artifact envelope for AA-P10/1.0. Hashes are not authentication."""
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field

CONTRACT_VERSION = "AA-P10/1.0"
SCHEMA_VERSION = "1.0"
Status = Literal["PREFLIGHT_BLOCKED", "RUN_FAILED", "ANALYSIS_INCOMPLETE", "REVIEW_REQUIRED",
                 "RELEASE_BLOCKED", "READY_FOR_RELEASE", "RELEASED"]
FILES = ("record.json", "decision.json", "report.md", "report.html", "manifest.json")


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Control(StrictModel):
    control_id: str
    version: str
    subject: str
    execution: Literal["executed", "error", "not_executed"]
    outcome: Literal["pass", "fail", "not_applicable"]
    eligible: int = Field(ge=0)
    evaluated: int = Field(ge=0)
    findings: list[dict[str, Any]] = Field(default_factory=list)
    reason: str = Field(min_length=1)


class Parent(StrictModel):
    revision_id: str
    manifest_fingerprint: str


class ReleaseIntent(StrictModel):
    reviewer: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    scope: Literal["local_artifact_only"] = "local_artifact_only"


class AuditRecord(StrictModel):
    schema_version: Literal["1.0"] = SCHEMA_VERSION
    contract_version: Literal["AA-P10/1.0"] = CONTRACT_VERSION
    revision_id: str
    parent: Parent | None = None
    created_at: str
    execution_mode: Literal["recorded_offline"] = "recorded_offline"
    status: Status
    release_intent: ReleaseIntent | None
    run_record: dict[str, Any]
    selected_position_id: str | None
    provenance: dict[str, Any]


class Decision(StrictModel):
    schema_version: Literal["1.0"] = SCHEMA_VERSION
    status: Status
    subject: str
    registry_fingerprint: str
    controls: list[Control]
    report_hashes: dict[str, str]
    release_intent: ReleaseIntent | None = None


class Manifest(StrictModel):
    schema_version: Literal["1.0"] = SCHEMA_VERSION
    contract_version: Literal["AA-P10/1.0"] = CONTRACT_VERSION
    revision_id: str
    status: Status
    release_intent: ReleaseIntent | None
    created_at: str
    execution_mode: Literal["recorded_offline"] = "recorded_offline"
    provenance: dict[str, Any]
    files: dict[str, str]
    fingerprint: str


class OperationResult(StrictModel):
    status: Status
    path: str | None = None
    errors: list[str] = Field(default_factory=list)


class Verification(StrictModel):
    valid: bool
    status: Status = "RELEASE_BLOCKED"
    errors: list[str] = Field(default_factory=list)
