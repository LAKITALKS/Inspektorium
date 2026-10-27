"""Prospective authoritative Inspektorium official-release boundary.

The Phase-7B primitives remain deterministic checks over ``ForensicRecord``.  This module is
the one supported boundary that may create an artifact carrying the official release role.  It
validates a source-bound release object, selects and executes the mandatory gates internally,
stages and verifies the complete package, revalidates all material state, and atomically promotes
one directory.  Legacy renderers remain diagnostic and cannot create a package accepted here.

SHA-256 values are deterministic integrity comparisons.  They are not authentication against an
actor able to rewrite content and every accompanying hash.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Literal

from inspektorium.audit.integrity.artifact_binding import (
    MANDATORY_PHASE7B_GATE_SET_ID,
    MANDATORY_PHASE7B_GATE_SET_VERSION,
    PHASE7B_ASSURANCE_SCOPE,
    PHASE7B_RELEASE_REPORT_SCHEMA_VERSION,
    ReleaseReport,
    evaluate_artifact_release,
    mandatory_gate_set_fingerprint,
    record_fingerprint,
    validate_release_report,
    validate_release_report_contract,
)
from inspektorium.audit.forensics.forensic_report import canonical_report_bytes, leakage_findings
from inspektorium.audit.schemas import FORENSIC_RECORD_SCHEMA_VERSION, ForensicRecord
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator


RELEASE_SOURCE_SCHEMA_VERSION = "inspektorium.audit.release_source/v1"
CONDITION_RELEASE_SOURCE_SCHEMA_VERSION = "inspektorium.audit.release_source/v2-condition-aware"
RELEASE_OBJECT_SCHEMA_VERSION = "inspektorium.audit.release_object/v1"
OFFICIAL_RELEASE_SCHEMA_VERSION = "inspektorium.audit.official_release/v1"
CONDITION_OFFICIAL_RELEASE_SCHEMA_VERSION = "inspektorium.audit.official_release/v2-condition-aware"
OFFICIAL_RELEASE_MANIFEST_SCHEMA_VERSION = "inspektorium.audit.official_release_manifest/v1"
CONDITION_OFFICIAL_RELEASE_MANIFEST_SCHEMA_VERSION = (
    "inspektorium.audit.official_release_manifest/v2-condition-aware"
)
OFFICIAL_ARTIFACT_ROLE = "official_inspektorium_release"
DIAGNOSTIC_ARTIFACT_ROLE = "diagnostic_non_release"
OFFICIAL_RELEASE_NAMESPACE = "official-inspektorium-releases"

_HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_SOURCE_MANIFEST_FIELDS = {
    "release_source_schema_version",
    "data_role",
    "execution_id",
    "analysis_id",
    "package_fingerprint",
    "runtime_contract_fingerprint",
    "forensic_record_fingerprint",
}
_CONDITION_SOURCE_FIELDS = {
    "plan_id", "specification_fingerprint", "arm_id", "arm_specification_fingerprint",
    "analytical_condition_id", "prompt_condition_id",
}
_OFFICIAL_ARTIFACT_FIELDS = {
    "official_release_schema_version", "artifact_role", "official_release_authorized",
    "release_id", "release_object_id", "release_object_fingerprint",
    "forensic_record_id", "forensic_record_fingerprint", "source_execution_id",
    "source_analysis_id", "source_artifact_sha256", "source_state_fingerprint",
    "package_fingerprint", "runtime_contract_fingerprint", "mandatory_gate_set_id",
    "mandatory_gate_set_version", "mandatory_gate_set_fingerprint",
    "release_report_fingerprint", "consolidated_decision", "releasable",
    "assurance_scope", "synthetic_fixture", "client_findings",
}
_CONDITION_OFFICIAL_ARTIFACT_FIELDS = _OFFICIAL_ARTIFACT_FIELDS | _CONDITION_SOURCE_FIELDS
_OFFICIAL_MANIFEST_FIELDS = {
    "release_manifest_schema_version", "artifact_role", "official_release_authorized",
    "release_id", "release_object_id", "release_object_fingerprint",
    "forensic_record_id", "forensic_record_fingerprint", "mandatory_gate_set_id",
    "mandatory_gate_set_version", "mandatory_gate_set_fingerprint",
    "release_report_schema_version", "release_report_fingerprint",
    "consolidated_decision", "source_binding", "files", "manifest_fingerprint",
}


class ReleaseBoundaryError(ValueError):
    """Controlled validation failure at the prospective release boundary."""


class SourceExecutionBinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    release_source_schema_version: Literal[
        "inspektorium.audit.release_source/v1",
        "inspektorium.audit.release_source/v2-condition-aware",
    ]
    data_role: Literal["prospective_release_source", "synthetic_release_qa"]
    source_artifact_path: str
    source_artifact_sha256: str
    source_manifest_fingerprint: str
    execution_id: str
    analysis_id: str
    package_fingerprint: str
    runtime_contract_fingerprint: str
    forensic_record_fingerprint: str
    repository_commit: str
    repository_tree: str
    tracked_source_fingerprint: str
    source_state_fingerprint: str
    plan_id: str | None = None
    specification_fingerprint: str | None = None
    arm_id: str | None = None
    arm_specification_fingerprint: str | None = None
    analytical_condition_id: str | None = None
    prompt_condition_id: str | None = None

    @model_validator(mode="after")
    def condition_fields_match_schema(self):
        values = [getattr(self, field) for field in _CONDITION_SOURCE_FIELDS]
        if self.release_source_schema_version == CONDITION_RELEASE_SOURCE_SCHEMA_VERSION:
            if any(not isinstance(value, str) or not value.strip() for value in values):
                raise ValueError("condition-aware release source lacks condition identity")
            for field in ("specification_fingerprint", "arm_specification_fingerprint"):
                if not _HEX64_RE.fullmatch(str(getattr(self, field))):
                    raise ValueError(f"condition-aware release source {field} is malformed")
        elif any(value is not None for value in values):
            raise ValueError("legacy release source cannot carry partial condition identity")
        return self


class CanonicalReleaseObject(BaseModel):
    """Small release envelope around the existing structured Phase-7B record."""

    model_config = ConfigDict(extra="forbid")

    release_object_schema_version: Literal["inspektorium.audit.release_object/v1"]
    release_object_id: str
    object_role: Literal["official_release_candidate"]
    record: ForensicRecord
    source_binding: SourceExecutionBinding
    object_fingerprint: str


class ReleaseResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    released: bool = False
    official_release_write_count: int = 0
    release_id: str | None = None
    package_path: str | None = None
    decision_status: str | None = None
    errors: list[str] = Field(default_factory=list)


class ReleaseVerification(BaseModel):
    model_config = ConfigDict(extra="forbid")

    valid: bool
    artifact_role: str = ""
    release_id: str | None = None
    errors: list[str] = Field(default_factory=list)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _fingerprint(value: object) -> str:
    return _sha256(canonical_report_bytes(value))


def _git(root: Path, *args: str, binary: bool = False) -> str | bytes:
    proc = subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=not binary, check=False,
    )
    if proc.returncode != 0:
        stderr = proc.stderr if isinstance(proc.stderr, str) else proc.stderr.decode(errors="replace")
        raise ReleaseBoundaryError((stderr or "git source-binding operation failed").strip())
    return proc.stdout


def _source_path(root: Path, relative: str) -> Path:
    if not relative or Path(relative).is_absolute():
        raise ReleaseBoundaryError("source artifact path must be repository-relative")
    path = (root / relative).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ReleaseBoundaryError("source artifact escapes repository root") from exc
    if not path.is_file() or path.is_symlink():
        raise ReleaseBoundaryError("source artifact must be a regular non-symlink file")
    return path


def _inspect_source_state(repo_root: str | Path, source_artifact_path: str) -> dict:
    root = Path(repo_root).resolve()
    authenticated = Path(str(_git(root, "rev-parse", "--show-toplevel")).strip()).resolve()
    if authenticated != root:
        raise ReleaseBoundaryError("requested repository root is not the authenticated Git root")
    if str(_git(root, "status", "--porcelain=v1", "--untracked-files=no")).strip():
        raise ReleaseBoundaryError("tracked source tree is dirty")
    path = _source_path(root, source_artifact_path)
    relative = str(path.relative_to(root))
    _git(root, "ls-files", "--error-unmatch", "--", relative)
    if str(_git(root, "diff", "--name-only", "HEAD", "--", relative)).strip():
        raise ReleaseBoundaryError("source artifact differs from authenticated HEAD")
    index = _git(root, "ls-files", "-s", "-z", binary=True)
    assert isinstance(index, bytes)
    state = {
        "repository_commit": str(_git(root, "rev-parse", "HEAD")).strip(),
        "repository_tree": str(_git(root, "rev-parse", "HEAD^{tree}")).strip(),
        "tracked_source_fingerprint": _sha256(index),
    }
    state["source_state_fingerprint"] = _fingerprint(state)
    state["source_artifact_sha256"] = _sha256(path.read_bytes())
    return state


def _read_source_manifest(path: Path) -> dict:
    try:
        value = json.loads(path.read_text())
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReleaseBoundaryError(f"release source manifest unreadable: {type(exc).__name__}: {exc}") from exc
    if not isinstance(value, dict):
        raise ReleaseBoundaryError("release source manifest is not an object")
    schema = value.get("release_source_schema_version")
    expected_fields = (
        _SOURCE_MANIFEST_FIELDS | _CONDITION_SOURCE_FIELDS
        if schema == CONDITION_RELEASE_SOURCE_SCHEMA_VERSION else _SOURCE_MANIFEST_FIELDS
    )
    if set(value) != expected_fields:
        raise ReleaseBoundaryError("release source manifest is partial or has unknown fields")
    if schema not in {RELEASE_SOURCE_SCHEMA_VERSION, CONDITION_RELEASE_SOURCE_SCHEMA_VERSION}:
        raise ReleaseBoundaryError("release source manifest schema version is unsupported")
    for field in (
        "package_fingerprint", "runtime_contract_fingerprint", "forensic_record_fingerprint",
    ):
        if not isinstance(value.get(field), str) or not _HEX64_RE.fullmatch(value[field]):
            raise ReleaseBoundaryError(f"release source manifest {field} is malformed")
    if value.get("data_role") not in {"prospective_release_source", "synthetic_release_qa"}:
        raise ReleaseBoundaryError("release source manifest data role is unsupported")
    for field in ("execution_id", "analysis_id"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            raise ReleaseBoundaryError(f"release source manifest {field} is missing")
    if schema == CONDITION_RELEASE_SOURCE_SCHEMA_VERSION:
        for field in _CONDITION_SOURCE_FIELDS:
            item = value.get(field)
            if not isinstance(item, str) or not item.strip():
                raise ReleaseBoundaryError(f"release source manifest {field} is missing")
        for field in ("specification_fingerprint", "arm_specification_fingerprint"):
            if not _HEX64_RE.fullmatch(value[field]):
                raise ReleaseBoundaryError(f"release source manifest {field} is malformed")
    return value


def canonical_release_object_fingerprint(value: CanonicalReleaseObject | dict) -> str:
    payload = value.model_dump(mode="json") if isinstance(value, CanonicalReleaseObject) else dict(value)
    payload["object_fingerprint"] = ""
    return _fingerprint(payload)


def build_release_object(
    record: ForensicRecord,
    *,
    release_object_id: str,
    source_artifact_path: str,
    repo_root: str | Path,
) -> CanonicalReleaseObject:
    """Construct a source-bound candidate; this does not authorize or write a release."""
    root = Path(repo_root).resolve()
    state = _inspect_source_state(root, source_artifact_path)
    manifest = _read_source_manifest(_source_path(root, source_artifact_path))
    expected_record_fp = record_fingerprint(record)
    if manifest["forensic_record_fingerprint"] != expected_record_fp:
        raise ReleaseBoundaryError("source manifest is not bound to this ForensicRecord")
    binding = SourceExecutionBinding(
        **manifest,
        source_artifact_path=source_artifact_path,
        source_artifact_sha256=state["source_artifact_sha256"],
        source_manifest_fingerprint=_fingerprint(manifest),
        repository_commit=state["repository_commit"],
        repository_tree=state["repository_tree"],
        tracked_source_fingerprint=state["tracked_source_fingerprint"],
        source_state_fingerprint=state["source_state_fingerprint"],
    )
    candidate = CanonicalReleaseObject(
        release_object_schema_version=RELEASE_OBJECT_SCHEMA_VERSION,
        release_object_id=release_object_id,
        object_role="official_release_candidate",
        record=record,
        source_binding=binding,
        object_fingerprint="",
    )
    candidate.object_fingerprint = canonical_release_object_fingerprint(candidate)
    errors = _validate_release_object(candidate, root)
    if errors:
        raise ReleaseBoundaryError("; ".join(errors))
    return candidate


def load_release_object(path: str | Path) -> CanonicalReleaseObject:
    try:
        raw = json.loads(Path(path).read_text())
        return CanonicalReleaseObject.model_validate(raw)
    except (OSError, UnicodeError, json.JSONDecodeError, ValidationError) as exc:
        raise ReleaseBoundaryError(f"release object is malformed: {type(exc).__name__}: {exc}") from exc


def _validate_release_object(candidate: CanonicalReleaseObject, root: Path) -> list[str]:
    errors: list[str] = []
    record = candidate.record
    binding = candidate.source_binding
    if not _SAFE_ID_RE.fullmatch(candidate.release_object_id):
        errors.append("release object ID is empty or unsafe")
    if record.record_schema_version != FORENSIC_RECORD_SCHEMA_VERSION:
        errors.append("ForensicRecord schema version is unsupported")
    if not record.record_id.strip():
        errors.append("ForensicRecord ID is empty")
    if leakage_findings(record.model_dump(mode="json")):
        errors.append("ForensicRecord contains private identity/path leakage")
    for field in ("provenance", "evidence", "findings", "client_findings"):
        if not getattr(record, field):
            errors.append(f"ForensicRecord is empty/vacuous: {field} is empty")
    id_groups = {
        "provenance": [item.provenance_id for item in record.provenance],
        "evidence": [item.evidence_id for item in record.evidence],
        "findings": [item.finding_id for item in record.findings],
        "client_findings": [item.client_finding_id for item in record.client_findings],
        "search_scopes": [item.search_scope_id for item in record.search_scopes],
        "negative_assertions": [item.assertion_id for item in record.negative_assertions],
    }
    for name, identifiers in id_groups.items():
        if any(not identifier.strip() for identifier in identifiers):
            errors.append(f"ForensicRecord {name} contains an empty identity")
        if len(set(identifiers)) != len(identifiers):
            errors.append(f"ForensicRecord {name} contains duplicate identities")
    from inspektorium.audit.integrity.artifact_binding import compute_content_fingerprint

    for provenance in record.provenance:
        expected = compute_content_fingerprint(
            provenance.exact_claim_text, provenance.provenance_state
        )
        if provenance.content_fingerprint != expected:
            errors.append(f"claim provenance fingerprint mismatch: {provenance.provenance_id}")
    expected_record_fp = record_fingerprint(record)
    if binding.forensic_record_fingerprint != expected_record_fp:
        errors.append("source binding ForensicRecord fingerprint mismatch")
    for field in (
        "source_artifact_sha256", "source_manifest_fingerprint", "package_fingerprint",
        "runtime_contract_fingerprint", "forensic_record_fingerprint",
        "tracked_source_fingerprint", "source_state_fingerprint",
    ):
        value = getattr(binding, field)
        if not _HEX64_RE.fullmatch(value):
            errors.append(f"source binding {field} is malformed")
    if binding.data_role == "prospective_release_source":
        if record.synthetic_fixture or record.fixture_class != "release_candidate":
            errors.append("prospective source requires a non-synthetic release_candidate record")
    elif not record.synthetic_fixture or record.fixture_class != "release_boundary_qa":
        errors.append("synthetic release QA requires an explicit release_boundary_qa record")
    if candidate.object_fingerprint != canonical_release_object_fingerprint(candidate):
        errors.append("canonical release-object fingerprint mismatch")
    try:
        state = _inspect_source_state(root, binding.source_artifact_path)
        manifest = _read_source_manifest(_source_path(root, binding.source_artifact_path))
        comparisons = {
            "source_artifact_sha256": state["source_artifact_sha256"],
            "source_manifest_fingerprint": _fingerprint(manifest),
            "repository_commit": state["repository_commit"],
            "repository_tree": state["repository_tree"],
            "tracked_source_fingerprint": state["tracked_source_fingerprint"],
            "source_state_fingerprint": state["source_state_fingerprint"],
        }
        for field, expected in comparisons.items():
            if getattr(binding, field) != expected:
                errors.append(f"source binding mismatch: {field}")
        manifest_fields = set(_SOURCE_MANIFEST_FIELDS)
        if binding.release_source_schema_version == CONDITION_RELEASE_SOURCE_SCHEMA_VERSION:
            manifest_fields.update(_CONDITION_SOURCE_FIELDS)
        for field in manifest_fields:
            if field in {"release_source_schema_version", "data_role"}:
                expected = getattr(binding, field)
            else:
                expected = getattr(binding, field)
            if manifest.get(field) != expected:
                errors.append(f"source manifest/binding mismatch: {field}")
    except ReleaseBoundaryError as exc:
        errors.append(str(exc))
    return errors


def _release_id(candidate: CanonicalReleaseObject, report: ReleaseReport) -> str:
    return (
        f"AR-{candidate.release_object_id}-{candidate.object_fingerprint[:12]}-"
        f"{report.release_report_fingerprint[:12]}"
    )


def _render_official_artifact(
    candidate: CanonicalReleaseObject, report: ReleaseReport, release_id: str
) -> dict:
    condition_aware = (
        candidate.source_binding.release_source_schema_version
        == CONDITION_RELEASE_SOURCE_SCHEMA_VERSION
    )
    artifact = {
        "official_release_schema_version": (
            CONDITION_OFFICIAL_RELEASE_SCHEMA_VERSION
            if condition_aware else OFFICIAL_RELEASE_SCHEMA_VERSION
        ),
        "artifact_role": OFFICIAL_ARTIFACT_ROLE,
        "official_release_authorized": True,
        "release_id": release_id,
        "release_object_id": candidate.release_object_id,
        "release_object_fingerprint": candidate.object_fingerprint,
        "forensic_record_id": candidate.record.record_id,
        "forensic_record_fingerprint": report.record_fingerprint,
        "source_execution_id": candidate.source_binding.execution_id,
        "source_analysis_id": candidate.source_binding.analysis_id,
        "source_artifact_sha256": candidate.source_binding.source_artifact_sha256,
        "source_state_fingerprint": candidate.source_binding.source_state_fingerprint,
        "package_fingerprint": candidate.source_binding.package_fingerprint,
        "runtime_contract_fingerprint": candidate.source_binding.runtime_contract_fingerprint,
        "mandatory_gate_set_id": report.mandatory_gate_set_id,
        "mandatory_gate_set_version": report.mandatory_gate_set_version,
        "mandatory_gate_set_fingerprint": report.mandatory_gate_set_fingerprint,
        "release_report_fingerprint": report.release_report_fingerprint,
        "consolidated_decision": report.decision_status,
        "releasable": report.releasable,
        "assurance_scope": PHASE7B_ASSURANCE_SCOPE,
        "synthetic_fixture": candidate.record.synthetic_fixture,
        "client_findings": [
            finding.model_dump(mode="json") for finding in candidate.record.client_findings
        ],
    }
    if condition_aware:
        artifact.update({
            field: getattr(candidate.source_binding, field) for field in _CONDITION_SOURCE_FIELDS
        })
    return artifact


def _manifest_fingerprint(manifest: dict) -> str:
    payload = dict(manifest)
    payload["manifest_fingerprint"] = ""
    return _fingerprint(payload)


def _write_staged_package(
    staging: Path,
    candidate: CanonicalReleaseObject,
    report: ReleaseReport,
    release_id: str,
) -> None:
    artifact_bytes = canonical_report_bytes(_render_official_artifact(candidate, report, release_id))
    report_bytes = canonical_report_bytes(report.model_dump(mode="json"))
    condition_aware = (
        candidate.source_binding.release_source_schema_version
        == CONDITION_RELEASE_SOURCE_SCHEMA_VERSION
    )
    manifest = {
        "release_manifest_schema_version": (
            CONDITION_OFFICIAL_RELEASE_MANIFEST_SCHEMA_VERSION
            if condition_aware else OFFICIAL_RELEASE_MANIFEST_SCHEMA_VERSION
        ),
        "artifact_role": OFFICIAL_ARTIFACT_ROLE,
        "official_release_authorized": True,
        "release_id": release_id,
        "release_object_id": candidate.release_object_id,
        "release_object_fingerprint": candidate.object_fingerprint,
        "forensic_record_id": candidate.record.record_id,
        "forensic_record_fingerprint": report.record_fingerprint,
        "mandatory_gate_set_id": MANDATORY_PHASE7B_GATE_SET_ID,
        "mandatory_gate_set_version": MANDATORY_PHASE7B_GATE_SET_VERSION,
        "mandatory_gate_set_fingerprint": mandatory_gate_set_fingerprint(),
        "release_report_schema_version": PHASE7B_RELEASE_REPORT_SCHEMA_VERSION,
        "release_report_fingerprint": report.release_report_fingerprint,
        "consolidated_decision": report.decision_status,
        "source_binding": candidate.source_binding.model_dump(mode="json"),
        "files": {
            "artifact.json": _sha256(artifact_bytes),
            "release_report.json": _sha256(report_bytes),
        },
        "manifest_fingerprint": "",
    }
    manifest["manifest_fingerprint"] = _manifest_fingerprint(manifest)
    (staging / "artifact.json").write_bytes(artifact_bytes)
    (staging / "release_report.json").write_bytes(report_bytes)
    (staging / "manifest.json").write_bytes(canonical_report_bytes(manifest))


def _before_promotion(
    candidate: CanonicalReleaseObject, report: ReleaseReport, staging: Path
) -> None:
    """Private no-op seam used only by deterministic adversarial tests."""


def _promote_release_package(staging: Path, target: Path) -> None:
    staging.rename(target)


def _path_occupied(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def verify_official_release(
    package_path: str | Path,
    *,
    release_object: CanonicalReleaseObject | None = None,
) -> ReleaseVerification:
    package = Path(package_path)
    errors: list[str] = []
    values: dict[str, dict] = {}
    for name in ("artifact.json", "release_report.json", "manifest.json"):
        path = package / name
        try:
            value = json.loads(path.read_text())
            if not isinstance(value, dict):
                raise ValueError("not an object")
            values[name] = value
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"{name} unreadable or malformed: {type(exc).__name__}: {exc}")
    if errors:
        return ReleaseVerification(valid=False, errors=errors)
    artifact = values["artifact.json"]
    manifest = values["manifest.json"]
    try:
        report = ReleaseReport.model_validate(values["release_report.json"])
    except ValidationError as exc:
        return ReleaseVerification(valid=False, errors=[f"release report malformed: {exc}"])
    condition_aware = (
        isinstance(manifest.get("source_binding"), dict)
        and manifest["source_binding"].get("release_source_schema_version")
        == CONDITION_RELEASE_SOURCE_SCHEMA_VERSION
    )
    expected_artifact_fields = (
        _CONDITION_OFFICIAL_ARTIFACT_FIELDS if condition_aware else _OFFICIAL_ARTIFACT_FIELDS
    )
    if set(artifact) != expected_artifact_fields:
        errors.append("official artifact is partial or has unknown fields")
    if set(manifest) != _OFFICIAL_MANIFEST_FIELDS:
        errors.append("release manifest is partial or has unknown fields")
    expected_artifact_schema = (
        CONDITION_OFFICIAL_RELEASE_SCHEMA_VERSION if condition_aware
        else OFFICIAL_RELEASE_SCHEMA_VERSION
    )
    if artifact.get("official_release_schema_version") != expected_artifact_schema:
        errors.append("official artifact schema version mismatch")
    for value, label in ((artifact, "artifact"), (manifest, "manifest")):
        if value.get("artifact_role") != OFFICIAL_ARTIFACT_ROLE:
            errors.append(f"{label} does not carry the official artifact role")
        if value.get("official_release_authorized") is not True:
            errors.append(f"{label} lacks official release authorization marker")
    expected_manifest_schema = (
        CONDITION_OFFICIAL_RELEASE_MANIFEST_SCHEMA_VERSION if condition_aware
        else OFFICIAL_RELEASE_MANIFEST_SCHEMA_VERSION
    )
    if manifest.get("release_manifest_schema_version") != expected_manifest_schema:
        errors.append("release manifest schema version mismatch")
    if manifest.get("release_report_schema_version") != PHASE7B_RELEASE_REPORT_SCHEMA_VERSION:
        errors.append("manifest release-report schema version mismatch")
    if manifest.get("manifest_fingerprint") != _manifest_fingerprint(manifest):
        errors.append("release manifest fingerprint mismatch")
    files = manifest.get("files")
    file_inventory = files if isinstance(files, dict) else {}
    if set(file_inventory) != {"artifact.json", "release_report.json"}:
        errors.append("release manifest file inventory mismatch")
    for name in ("artifact.json", "release_report.json"):
        expected = file_inventory.get(name)
        try:
            observed = _sha256((package / name).read_bytes())
        except OSError as exc:
            errors.append(f"release package hash unavailable: {name}: {type(exc).__name__}: {exc}")
        else:
            if expected != observed:
                errors.append(f"release package hash mismatch: {name}")
    errors.extend(validate_release_report_contract(report))
    if not report.releasable or report.decision_status != "releasable":
        errors.append("release report is not releasable")
    if artifact.get("releasable") is not True:
        errors.append("official artifact does not carry a releasable decision")
    if artifact.get("assurance_scope") != PHASE7B_ASSURANCE_SCOPE:
        errors.append("official artifact assurance scope mismatch")
    cross_fields = (
        "release_id", "release_object_id", "release_object_fingerprint",
        "forensic_record_id", "forensic_record_fingerprint", "mandatory_gate_set_id",
        "mandatory_gate_set_version", "mandatory_gate_set_fingerprint",
        "release_report_fingerprint", "consolidated_decision",
    )
    for field in cross_fields:
        if artifact.get(field) != manifest.get(field):
            errors.append(f"artifact/manifest mismatch: {field}")
    if report.release_report_fingerprint != manifest.get("release_report_fingerprint"):
        errors.append("manifest/report fingerprint mismatch")
    if report.record_fingerprint != manifest.get("forensic_record_fingerprint"):
        errors.append("manifest/report object mismatch")
    if report.mandatory_gate_set_fingerprint != manifest.get("mandatory_gate_set_fingerprint"):
        errors.append("manifest/report gate-set mismatch")
    try:
        source_binding = SourceExecutionBinding.model_validate(manifest.get("source_binding"))
    except ValidationError as exc:
        errors.append(f"manifest source binding malformed: {exc}")
    else:
        source_cross_fields = {
            "source_execution_id": source_binding.execution_id,
            "source_analysis_id": source_binding.analysis_id,
            "source_artifact_sha256": source_binding.source_artifact_sha256,
            "source_state_fingerprint": source_binding.source_state_fingerprint,
            "package_fingerprint": source_binding.package_fingerprint,
            "runtime_contract_fingerprint": source_binding.runtime_contract_fingerprint,
        }
        if condition_aware:
            source_cross_fields.update({
                field: getattr(source_binding, field) for field in _CONDITION_SOURCE_FIELDS
            })
        for field, expected in source_cross_fields.items():
            if artifact.get(field) != expected:
                errors.append(f"artifact/manifest source-binding mismatch: {field}")
    if release_object is not None:
        if canonical_release_object_fingerprint(release_object) != release_object.object_fingerprint:
            errors.append("supplied release object fingerprint is invalid")
        if manifest.get("release_object_fingerprint") != release_object.object_fingerprint:
            errors.append("package belongs to a different release object")
        if report.record_fingerprint != record_fingerprint(release_object.record):
            errors.append("package report belongs to a different ForensicRecord")
        report_ok, report_errors = validate_release_report(report, release_object.record)
        if not report_ok:
            errors.extend(report_errors)
    return ReleaseVerification(
        valid=not errors,
        artifact_role=artifact.get("artifact_role", ""),
        release_id=manifest.get("release_id"),
        errors=errors,
    )


def is_authoritative_release_path(path: str | Path) -> bool:
    candidate = Path(path)
    return (
        OFFICIAL_RELEASE_NAMESPACE in candidate.parts
        or OFFICIAL_RELEASE_NAMESPACE in candidate.resolve(strict=False).parts
    )


def release_official_artifact(
    release_object: CanonicalReleaseObject,
    *,
    output_root: str | Path,
    repo_root: str | Path,
) -> ReleaseResult:
    """The only supported production API that may write an official release package."""
    root = Path(repo_root).resolve()
    errors = _validate_release_object(release_object, root)
    if errors:
        return ReleaseResult(status="INVALID_OBJECT", errors=errors)
    initial_object_fp = release_object.object_fingerprint
    initial_source_state = release_object.source_binding.source_state_fingerprint

    report = evaluate_artifact_release(release_object.record)
    report_ok, report_errors = validate_release_report(report, release_object.record)
    if not report_ok:
        return ReleaseResult(status="MALFORMED_GATE_EVIDENCE", errors=report_errors)
    if not report.releasable:
        return ReleaseResult(
            status=report.decision_status.upper(),
            decision_status=report.decision_status,
            errors=[report.decision_reason],
        )

    release_id = _release_id(release_object, report)
    output = Path(output_root).resolve()
    namespace = output / OFFICIAL_RELEASE_NAMESPACE
    target = namespace / release_id
    if namespace.is_symlink() or (namespace.exists() and not namespace.is_dir()):
        return ReleaseResult(
            status="INVALID_OUTPUT_NAMESPACE",
            release_id=release_id,
            errors=["official release namespace is not a real directory"],
        )
    if _path_occupied(target):
        return ReleaseResult(
            status="TARGET_COLLISION", release_id=release_id,
            errors=["official release target already exists; no new artifact was written"],
        )

    staging: Path | None = None
    try:
        output.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=".inspektorium-release-staging-", dir=output))
        _write_staged_package(staging, release_object, report, release_id)
        _before_promotion(release_object, report, staging)

        revalidation_errors = _validate_release_object(release_object, root)
        if release_object.object_fingerprint != initial_object_fp:
            revalidation_errors.append("release object changed after gate execution")
        if release_object.source_binding.source_state_fingerprint != initial_source_state:
            revalidation_errors.append("source binding changed after gate execution")
        report_ok, report_errors = validate_release_report(report, release_object.record)
        revalidation_errors.extend(report_errors)
        staged = verify_official_release(staging, release_object=release_object)
        revalidation_errors.extend(staged.errors)
        if revalidation_errors:
            return ReleaseResult(
                status="REVALIDATION_FAILED", release_id=release_id,
                decision_status=report.decision_status, errors=revalidation_errors,
            )
        namespace.mkdir(parents=True, exist_ok=True)
        if _path_occupied(target):
            return ReleaseResult(
                status="TARGET_COLLISION", release_id=release_id,
                errors=["official release target appeared before promotion"],
            )
        _promote_release_package(staging, target)
        staging = None
        return ReleaseResult(
            status="RELEASED",
            released=True,
            official_release_write_count=1,
            release_id=release_id,
            package_path=str(target),
            decision_status=report.decision_status,
        )
    except (OSError, ReleaseBoundaryError, ValidationError, ValueError) as exc:
        return ReleaseResult(
            status="WRITE_FAILED", release_id=release_id,
            decision_status=report.decision_status,
            errors=[f"{type(exc).__name__}: {exc}"],
        )
    finally:
        if staging is not None and staging.exists():
            shutil.rmtree(staging)
