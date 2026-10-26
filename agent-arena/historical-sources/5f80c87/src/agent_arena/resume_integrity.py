"""Prospective Phase-7A resume/checkpoint integrity.

Historical Phase-7 JSONL remains readable through the historical reader in
``phase7a_real_run``.  This module defines the stricter, versioned contract that
new checkpoints must satisfy before they can participate in a future resume.

The SHA-256 values here are deterministic integrity comparisons.  They do not
authenticate against an actor able to rewrite content and every accompanying
hash.  Production authorization still comes from the guarded Phase-2 source,
artifact, QA, credential, and provider boundary.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from agent_arena import phase7a_execution as p7
from agent_arena import preflight_integrity as pi
from agent_arena import runtime_contract as rc


CHECKPOINT_SCHEMA_VERSION = "agent_arena.phase7a_checkpoint/v1"
RESUME_RECORD_SCHEMA_VERSION = "agent_arena.phase7a_resume_record/v1"
CONDITION_CHECKPOINT_SCHEMA_VERSION = "agent_arena.condition_checkpoint/v2"
CONDITION_RESUME_RECORD_SCHEMA_VERSION = "agent_arena.condition_resume_record/v2"

_HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
_SOURCE_BINDING_FIELDS = (
    "repository_identity",
    "commit",
    "tree",
    "tracked_source_fingerprint",
    "tracked_config_fingerprint",
    "python_environment_fingerprint",
    "source_state_fingerprint",
)
_RECORD_CONTRACT_FIELDS = (
    "checkpoint_id",
    "checkpoint_namespace",
    "checkpoint_storage_identity",
    "checkpoint_contract_fingerprint",
    "scientific_manifest_fingerprint",
    "execution_manifest_fingerprint",
    "call_plan_fingerprint",
    "package_fingerprint",
    "runtime_contract_fingerprint",
    "source_state_fingerprint",
    "execution_source_fingerprint",
    "provider_runtime_identity_fingerprint",
)
_REQUIRED_RECORD_FIELDS = (
    "resume_record_schema_version",
    "resume_record_fingerprint",
    "checkpoint_id",
    "checkpoint_namespace",
    "checkpoint_storage_identity",
    "checkpoint_contract_fingerprint",
    "library_run_id",
    "model",
    "unit_id",
    "run_index",
    "unit_binding_fingerprint",
    "unit_fingerprint",
    "gold_label",
    "runtime_contract_fingerprint",
    "package_fingerprint",
    "scientific_manifest_fingerprint",
    "execution_manifest_fingerprint",
    "call_plan_fingerprint",
    "source_state_fingerprint",
    "execution_source_fingerprint",
    "provider_runtime_identity_fingerprint",
    "execution_type",
    "dry_run",
    "raw_response",
    "raw_response_sha256",
    "raw_result_ref",
    "confidence_state",
    "terminal_attempt",
    "classification_valid",
    "calibration_valid",
    "model_call_again_allowed",
)
_CONDITION_RECORD_FIELDS = (
    "plan_id",
    "specification_fingerprint",
    "arm_id",
    "arm_specification_fingerprint",
    "analytical_condition_id",
    "prompt_condition_id",
    "prompt_version",
    "system_prompt_sha256",
)


class ResumeIntegrityError(RuntimeError):
    """Raised when prospective checkpoint material cannot be safely produced."""


def _git_text(root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, check=False
    )
    if proc.returncode != 0:
        raise ResumeIntegrityError(
            (proc.stderr or proc.stdout or "git checkpoint binding failed").strip()
        )
    return proc.stdout.strip()


def _execution_source_fingerprint(root: Path) -> str:
    """Bind the material execution/parser/provider modules used by this run."""
    relative_paths = (
        "src/agent_arena/resume_integrity.py",
        "src/agent_arena/phase7a_real_run.py",
        "src/agent_arena/phase7a_execution.py",
        "src/agent_arena/run_library.py",
        "src/agent_arena/runtime_contract.py",
        "src/agent_arena/condition_analysis.py",
        "src/agent_arena/condition_contract.py",
        "src/agent_arena/condition_retry.py",
        "src/agent_arena/full_replication_contract.py",
        "src/agent_arena/full_replication_analysis.py",
        "src/agent_arena/runner.py",
        "src/agent_arena/output_contract.py",
        "src/agent_arena/providers/anthropic.py",
    )
    rows = []
    for relative in relative_paths:
        path = root / relative
        try:
            content_hash = rc._sha256_hex(path.read_bytes())
        except OSError as exc:
            raise ResumeIntegrityError(
                f"material execution source unavailable: {relative}: {type(exc).__name__}: {exc}"
            ) from exc
        rows.append((relative, content_hash))
    return p7._fp(rows)


def unit_binding_fingerprint(unit) -> str:
    """Bind the complete evaluated-unit metadata, including source/gold identity."""
    return p7._fp(unit.meta())


def _provider_runtime_identity(model_id: str, dry_run: bool) -> dict:
    if dry_run:
        return {
            "condition": "offline_injected_diagnostic",
            "model": model_id,
            "analytical": False,
        }
    return {
        "condition": "anthropic_capture_provider",
        "provider": "anthropic",
        "model": model_id,
        "request_timeout_seconds": rc.SHARED_RUNTIME["request_timeout_seconds"],
        "max_transport_retries_after_initial_request": rc.SHARED_RUNTIME[
            "max_transport_retries_after_initial_request"
        ],
        "semantic_or_quality_retries": rc.SHARED_RUNTIME["semantic_or_quality_retries"],
    }


def build_resume_contract(
    model_key: str,
    units: list,
    repo_root: str | Path,
    *,
    execution_type: str,
    dry_run: bool,
    source_binding: dict | None = None,
    checkpoint_root: str | Path | None = None,
) -> dict:
    """Reconstruct the exact prospective contract a checkpoint must match."""
    root = Path(repo_root).resolve()
    model_id = rc.MODELS[model_key]["exact_model_id"]
    manifest = p7.build_execution_manifest(root)
    plan = p7.build_call_plan(root)
    source = source_binding or pi.inspect_source_state(root)
    if any(source.get(field) is None for field in _SOURCE_BINDING_FIELDS):
        source = pi.inspect_source_state(root)
    missing_source = [field for field in _SOURCE_BINDING_FIELDS if source.get(field) is None]
    if missing_source:
        raise ResumeIntegrityError(
            f"checkpoint source binding unavailable: {', '.join(missing_source)}"
        )

    slots = sorted(
        (model_id, unit.unit_id, run_index)
        for unit in units
        for run_index in range(p7.N_REPLICATIONS)
    )
    unit_bindings = sorted(
        (unit.unit_id, unit_binding_fingerprint(unit)) for unit in units
    )
    provider_identity = _provider_runtime_identity(model_id, dry_run)
    storage_root = Path(checkpoint_root).resolve() if checkpoint_root else (
        root / f"analysis/phase7a_execution/{model_key}"
    ).resolve()
    storage_identity = p7._fp(
        {"checkpoint_root": str(storage_root), "model": model_id, "execution_type": execution_type}
    )
    contract = {
        "checkpoint_schema_version": CHECKPOINT_SCHEMA_VERSION,
        "resume_record_schema_version": RESUME_RECORD_SCHEMA_VERSION,
        "checkpoint_namespace": f"phase7a_run_{model_key}:{storage_identity[:20]}",
        "checkpoint_storage_identity": storage_identity,
        "library_run_id": f"phase7a_run_{model_key}",
        "model_key": model_key,
        "model": model_id,
        "model_set": [model_id],
        "execution_type": execution_type,
        "dry_run": bool(dry_run),
        "n_replications": p7.N_REPLICATIONS,
        "expected_units": len(units),
        "expected_slots": len(slots),
        "expected_unit_ids": [unit.unit_id for unit in units],
        "expected_slots_fingerprint": p7._fp(slots),
        "unit_bindings_fingerprint": p7._fp(unit_bindings),
        "scientific_manifest_fingerprint": manifest["scientific_manifest_fingerprint"],
        "execution_manifest_fingerprint": manifest["execution_manifest_fingerprint"],
        "call_plan_fingerprint": plan["call_plan_fingerprint"],
        "package_fingerprint": plan["package_fingerprint"],
        "runtime_contract_fingerprint": plan["runtime_contract_fingerprints"][model_id],
        "repository_identity": source["repository_identity"],
        "repository_commit": source["commit"],
        "repository_tree": source["tree"],
        "tracked_source_fingerprint": source["tracked_source_fingerprint"],
        "tracked_config_fingerprint": source["tracked_config_fingerprint"],
        "python_environment_fingerprint": source["python_environment_fingerprint"],
        "source_state_fingerprint": source["source_state_fingerprint"],
        "execution_source_fingerprint": _execution_source_fingerprint(root),
        "provider_runtime_identity": provider_identity,
        "provider_runtime_identity_fingerprint": p7._fp(provider_identity),
    }
    contract_fingerprint = p7._fp(contract)
    contract["checkpoint_contract_fingerprint"] = contract_fingerprint
    contract["checkpoint_id"] = f"p7a-{model_key}-{contract_fingerprint[:20]}"
    return contract


def build_condition_resume_contract(
    document: dict,
    arm: dict,
    model_key: str,
    units: list,
    repo_root: str | Path,
    *,
    execution_type: str,
    dry_run: bool,
    source_binding: dict | None = None,
    checkpoint_root: str | Path | None = None,
) -> dict:
    """Bind a new-schema checkpoint to one authenticated registered condition."""
    root = Path(repo_root).resolve()
    specification = document["specification"]
    if model_key not in specification["model_keys"]:
        raise ResumeIntegrityError("checkpoint model is outside registered specification")
    model_id = rc.MODELS[model_key]["exact_model_id"]
    source = source_binding or pi.inspect_source_state(root)
    if any(source.get(field) is None for field in _SOURCE_BINDING_FIELDS):
        source = pi.inspect_source_state(root)
    missing_source = [field for field in _SOURCE_BINDING_FIELDS if source.get(field) is None]
    if missing_source:
        raise ResumeIntegrityError(
            f"checkpoint source binding unavailable: {', '.join(missing_source)}"
        )

    n_replications = specification["n_replications"]
    slots = sorted(
        (model_id, unit.unit_id, run_index)
        for unit in units
        for run_index in range(n_replications)
    )
    unit_bindings = sorted(
        (unit.unit_id, unit_binding_fingerprint(unit)) for unit in units
    )
    provider_identity = _provider_runtime_identity(model_id, dry_run)
    storage_root = Path(checkpoint_root).resolve() if checkpoint_root else (
        root / arm["artifact_namespace"] / model_key
    ).resolve()
    storage_identity = p7._fp(
        {
            "checkpoint_root": str(storage_root),
            "model": model_id,
            "execution_type": execution_type,
            "specification_fingerprint": specification["specification_fingerprint"],
            "arm_specification_fingerprint": arm["arm_specification_fingerprint"],
        }
    )
    runtime_fp = arm["runtime_contract_fingerprints"][model_id]
    contract = {
        "checkpoint_schema_version": CONDITION_CHECKPOINT_SCHEMA_VERSION,
        "resume_record_schema_version": CONDITION_RESUME_RECORD_SCHEMA_VERSION,
        "plan_id": specification["plan_id"],
        "specification_fingerprint": specification["specification_fingerprint"],
        "arm_id": arm["arm_id"],
        "arm_specification_fingerprint": arm["arm_specification_fingerprint"],
        "analytical_condition_id": arm["analytical_condition_id"],
        "prompt_condition_id": arm["prompt_condition_id"],
        "prompt_version": arm["prompt_version"],
        "system_prompt_sha256": arm["system_prompt_sha256"],
        "checkpoint_namespace": (
            f"{specification['plan_id']}:{arm['arm_id']}:{model_key}:{storage_identity[:20]}"
        ),
        "checkpoint_storage_identity": storage_identity,
        "library_run_id": f"{specification['plan_id']}:{arm['arm_id']}:{model_key}",
        "model_key": model_key,
        "model": model_id,
        "model_set": [model_id],
        "execution_type": execution_type,
        "dry_run": bool(dry_run),
        "n_replications": n_replications,
        "expected_units": len(units),
        "expected_slots": len(slots),
        "expected_unit_ids": [unit.unit_id for unit in units],
        "expected_slots_fingerprint": p7._fp(slots),
        "unit_bindings_fingerprint": p7._fp(unit_bindings),
        "scientific_manifest_fingerprint": arm["execution_manifest"][
            "execution_manifest_fingerprint"
        ],
        "execution_manifest_fingerprint": arm["execution_manifest"][
            "execution_manifest_fingerprint"
        ],
        "call_plan_fingerprint": arm["call_plan"]["call_plan_fingerprint"],
        "package_fingerprint": arm["package_fingerprint"],
        "runtime_contract_fingerprint": runtime_fp,
        "repository_identity": source["repository_identity"],
        "repository_commit": source["commit"],
        "repository_tree": source["tree"],
        "tracked_source_fingerprint": source["tracked_source_fingerprint"],
        "tracked_config_fingerprint": source["tracked_config_fingerprint"],
        "python_environment_fingerprint": source["python_environment_fingerprint"],
        "source_state_fingerprint": source["source_state_fingerprint"],
        "execution_source_fingerprint": _execution_source_fingerprint(root),
        "provider_runtime_identity": provider_identity,
        "provider_runtime_identity_fingerprint": p7._fp(provider_identity),
    }
    contract_fingerprint = p7._fp(contract)
    contract["checkpoint_contract_fingerprint"] = contract_fingerprint
    contract["checkpoint_id"] = f"p5a-{arm['arm_id']}-{model_key}-{contract_fingerprint[:20]}"
    return contract


def resume_record_fingerprint(record: dict) -> str:
    """Fingerprint every stored field except the fingerprint's self-reference."""
    return p7._fp(
        {key: value for key, value in record.items() if key != "resume_record_fingerprint"}
    )


def seal_new_record(record: dict, unit, contract: dict) -> dict:
    """Attach prospective provenance to a newly executed, never-stored record."""
    sealed = dict(record)
    if "raw_response" not in sealed:
        if p7.is_terminal_attempt(sealed):
            raise ResumeIntegrityError("new terminal record lacks captured raw response")
        sealed["raw_response"] = ""
    if not isinstance(sealed["raw_response"], str):
        raise ResumeIntegrityError("new raw response is not text")
    raw_hash = rc._sha256_hex(sealed["raw_response"].encode("utf-8"))
    if sealed.get("raw_response_sha256") not in (None, raw_hash):
        raise ResumeIntegrityError("new raw-response content/hash mismatch")

    sealed.update(
        {
            "resume_record_schema_version": contract["resume_record_schema_version"],
            "checkpoint_id": contract["checkpoint_id"],
            "checkpoint_namespace": contract["checkpoint_namespace"],
            "checkpoint_storage_identity": contract["checkpoint_storage_identity"],
            "checkpoint_contract_fingerprint": contract[
                "checkpoint_contract_fingerprint"
            ],
            "library_run_id": contract["library_run_id"],
            "model": contract["model"],
            "unit_id": unit.unit_id,
            "case_id": unit.unit_id,
            "case_file": f"{unit.unit_id}.yaml",
            "unit_type": unit.unit_type,
            "base_case_id": unit.base_case_id,
            "cluster_root_id": unit.cluster_root_id,
            "perturbation_family": unit.perturbation_family,
            "family_id": unit.family_id,
            "gold_label": unit.gold_label,
            "unit_fingerprint": unit.unit_fingerprint,
            "unit_binding_fingerprint": unit_binding_fingerprint(unit),
            "runtime_contract_fingerprint": contract["runtime_contract_fingerprint"],
            "package_fingerprint": contract["package_fingerprint"],
            "scientific_manifest_fingerprint": contract[
                "scientific_manifest_fingerprint"
            ],
            "execution_manifest_fingerprint": contract[
                "execution_manifest_fingerprint"
            ],
            "call_plan_fingerprint": contract["call_plan_fingerprint"],
            "source_state_fingerprint": contract["source_state_fingerprint"],
            "execution_source_fingerprint": contract["execution_source_fingerprint"],
            "provider_runtime_identity_fingerprint": contract[
                "provider_runtime_identity_fingerprint"
            ],
            "execution_type": contract["execution_type"],
            "dry_run": contract["dry_run"],
            "raw_response_sha256": raw_hash,
            "raw_result_ref": "inline:raw_response",
        }
    )
    if contract.get("checkpoint_schema_version") == CONDITION_CHECKPOINT_SCHEMA_VERSION:
        sealed.update({field: contract[field] for field in _CONDITION_RECORD_FIELDS})
    sealed.update(p7.analytical_state(sealed))
    sealed["resume_record_fingerprint"] = resume_record_fingerprint(sealed)
    return sealed


def _slot_key(record: dict) -> tuple[str, str, int] | None:
    model = record.get("model")
    unit_id = record.get("unit_id")
    run_index = record.get("run_index")
    if not isinstance(model, str) or not isinstance(unit_id, str):
        return None
    if not isinstance(run_index, int) or isinstance(run_index, bool):
        return None
    return model, unit_id, run_index


def _expected_slot_map(contract: dict, units: list) -> dict[tuple[str, str, int], object]:
    return {
        (contract["model"], unit.unit_id, run_index): unit
        for unit in units
        for run_index in range(contract["n_replications"])
    }


def _record_errors(record: dict, unit, contract: dict) -> list[str]:
    errors: list[str] = []
    required_fields = list(_REQUIRED_RECORD_FIELDS)
    if contract.get("checkpoint_schema_version") == CONDITION_CHECKPOINT_SCHEMA_VERSION:
        required_fields.extend(_CONDITION_RECORD_FIELDS)
    for field in required_fields:
        if field not in record:
            errors.append(f"missing required record provenance: {field}")
    if errors:
        return errors

    if record.get("resume_record_schema_version") != contract["resume_record_schema_version"]:
        errors.append("unknown resume record schema version")
    if record.get("library_run_id") != contract["library_run_id"]:
        errors.append("record run namespace mismatch")
    for field in _RECORD_CONTRACT_FIELDS:
        if record.get(field) != contract.get(field):
            errors.append(f"record contract mismatch: {field}")
    for field in ("model", "execution_type", "dry_run"):
        if record.get(field) != contract.get(field):
            errors.append(f"record execution binding mismatch: {field}")
    if contract.get("checkpoint_schema_version") == CONDITION_CHECKPOINT_SCHEMA_VERSION:
        for field in _CONDITION_RECORD_FIELDS:
            if record.get(field) != contract.get(field):
                errors.append(f"record condition binding mismatch: {field}")

    expected_unit = {
        "unit_id": unit.unit_id,
        "case_id": unit.unit_id,
        "case_file": f"{unit.unit_id}.yaml",
        "unit_type": unit.unit_type,
        "base_case_id": unit.base_case_id,
        "cluster_root_id": unit.cluster_root_id,
        "perturbation_family": unit.perturbation_family,
        "family_id": unit.family_id,
        "gold_label": unit.gold_label,
        "unit_fingerprint": unit.unit_fingerprint,
        "unit_binding_fingerprint": unit_binding_fingerprint(unit),
    }
    for field, expected in expected_unit.items():
        if record.get(field) != expected:
            errors.append(f"record unit/gold binding mismatch: {field}")

    raw_response = record.get("raw_response")
    raw_hash = record.get("raw_response_sha256")
    if not isinstance(raw_response, str):
        errors.append("raw response missing or not text")
    elif not isinstance(raw_hash, str) or not _HEX64_RE.fullmatch(raw_hash):
        errors.append("raw-response fingerprint malformed or missing")
    elif rc._sha256_hex(raw_response.encode("utf-8")) != raw_hash:
        errors.append("raw-response content/hash mismatch")
    if record.get("raw_result_ref") != "inline:raw_response":
        errors.append("raw response is not inline-bound")

    stored_fp = record.get("resume_record_fingerprint")
    if not isinstance(stored_fp, str) or not _HEX64_RE.fullmatch(stored_fp):
        errors.append("resume-record fingerprint malformed or missing")
    elif stored_fp != resume_record_fingerprint(record):
        errors.append("resume-record fingerprint mismatch")

    state = p7.analytical_state(record)
    for field, expected in state.items():
        if record.get(field) is not expected:
            errors.append(f"stored analytical state mismatch: {field}")
    if record.get("confidence_state") != p7.record_confidence_state(record):
        errors.append("stored confidence state contradicts its raw value")
    if p7.is_classification_valid(record):
        expected_correct = record.get("label") == unit.gold_label
        if record.get("label_correct") is not expected_correct:
            errors.append("stored label correctness contradicts current gold binding")
    return errors


def checkpoint_record_accounting(records: list[dict], expected_slots: int) -> dict:
    terminal = sum(1 for record in records if p7.is_terminal_attempt(record))
    classification = sum(1 for record in records if p7.is_classification_valid(record))
    calibration = sum(1 for record in records if p7.is_calibration_valid(record))
    nonterminal = len(records) - terminal
    absent = expected_slots - len(records)
    return {
        "expected_slots": expected_slots,
        "records_loaded": len(records),
        "resume_eligible_terminal_records": terminal,
        "authenticated_nonterminal_records": nonterminal,
        "legitimately_absent_slots": absent,
        "provider_calls_required": absent + nonterminal,
        "classification_valid_records": classification,
        "calibration_valid_records": calibration,
        "terminal_coverage_complete": terminal == expected_slots,
        "analytical_complete": classification == calibration == expected_slots,
    }


def _records_fingerprint(records: list[dict]) -> str:
    rows = sorted(
        (list(_slot_key(record) or ("INVALID", "INVALID", -1)),
         record.get("resume_record_fingerprint"))
        for record in records
    )
    return p7._fp(rows)


def _checkpoint_fingerprint(manifest: dict) -> str:
    return p7._fp(
        {key: value for key, value in manifest.items() if key != "checkpoint_fingerprint"}
    )


def build_checkpoint_manifest(contract: dict, records: list[dict]) -> dict:
    manifest = {
        **contract,
        "checkpoint_record_count": len(records),
        "checkpoint_records_fingerprint": _records_fingerprint(records),
        "checkpoint_accounting": checkpoint_record_accounting(
            records, contract["expected_slots"]
        ),
    }
    manifest["checkpoint_fingerprint"] = _checkpoint_fingerprint(manifest)
    return manifest


def validate_checkpoint_records(
    records: list[dict], contract: dict, units: list
) -> dict:
    expected = _expected_slot_map(contract, units)
    errors: list[str] = []
    by_key: dict[tuple[str, str, int], list[dict]] = {}
    invalid_records = 0
    unexpected_slots = 0
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"record {index} is not a JSON object")
            invalid_records += 1
            continue
        key = _slot_key(record)
        if key is None:
            errors.append(f"record {index} has malformed slot identity")
            invalid_records += 1
            continue
        by_key.setdefault(key, []).append(record)
        unit = expected.get(key)
        if unit is None:
            errors.append(f"unexpected checkpoint slot: {key}")
            unexpected_slots += 1
            invalid_records += 1
            continue
        record_errors = _record_errors(record, unit, contract)
        if record_errors:
            invalid_records += 1
            errors.extend(f"slot {key}: {error}" for error in record_errors)

    duplicate_slots = sum(1 for group in by_key.values() if len(group) > 1)
    conflicting_slots = sum(
        1
        for group in by_key.values()
        if len(group) > 1 and len({pi._fingerprint(record) for record in group}) > 1
    )
    if duplicate_slots:
        errors.append(f"duplicate checkpoint slots: {duplicate_slots}")
    if conflicting_slots:
        errors.append(f"conflicting checkpoint slots: {conflicting_slots}")

    unique_records = [group[0] for group in by_key.values() if len(group) == 1]
    return {
        "valid": not errors,
        "errors": errors,
        "records": sorted(unique_records, key=lambda record: _slot_key(record)),
        "invalid_records": invalid_records,
        "duplicate_slots": duplicate_slots,
        "conflicting_slots": conflicting_slots,
        "unexpected_slots": unexpected_slots,
    }


def _read_json_object(path: Path, label: str, errors: list[str]) -> dict | None:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        errors.append(f"{label} unreadable: {type(exc).__name__}: {exc}")
        return None
    if not raw.strip():
        errors.append(f"{label} empty")
        return None
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"{label} malformed: {type(exc).__name__}: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{label} structurally partial: expected JSON object")
        return None
    return value


def _read_jsonl_strict(path: Path, errors: list[str]) -> list[dict] | None:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        errors.append(f"checkpoint records unreadable: {type(exc).__name__}: {exc}")
        return None
    if not raw.strip():
        errors.append("checkpoint records empty")
        return None
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        errors.append(f"checkpoint records malformed: UnicodeDecodeError: {exc}")
        return None
    records: list[dict] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            errors.append(f"checkpoint records malformed: blank line {line_number}")
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(
                f"checkpoint records malformed/truncated at line {line_number}: {exc}"
            )
            continue
        if not isinstance(value, dict):
            errors.append(f"checkpoint record {line_number} is not a JSON object")
            continue
        records.append(value)
    return records


def validate_resume_checkpoint(
    records_path: str | Path,
    manifest_path: str | Path,
    contract: dict,
    units: list,
) -> dict:
    """Load and authenticate the entire prospective checkpoint without mutation."""
    records_path = Path(records_path)
    manifest_path = Path(manifest_path)
    records_exists = records_path.exists()
    manifest_exists = manifest_path.exists()
    base = {
        "records_path": str(records_path),
        "manifest_path": str(manifest_path),
        "expected_slots": contract["expected_slots"],
    }
    if not records_exists and not manifest_exists:
        accounting = checkpoint_record_accounting([], contract["expected_slots"])
        return {
            **base,
            "status": "NO_CHECKPOINT",
            "valid": True,
            "resumable": True,
            "legacy_checkpoint": False,
            "errors": [],
            "records": [],
            "invalid_records": 0,
            "duplicate_slots": 0,
            "conflicting_slots": 0,
            "unexpected_slots": 0,
            "accounting": accounting,
        }

    errors: list[str] = []
    legacy = records_exists and not manifest_exists
    if not records_exists:
        errors.append("checkpoint manifest exists without checkpoint records")
    if legacy:
        errors.append("legacy checkpoint lacks prospective provenance manifest")
    records = _read_jsonl_strict(records_path, errors) if records_exists else None
    manifest = _read_json_object(manifest_path, "checkpoint manifest", errors) \
        if manifest_exists else None

    record_report = validate_checkpoint_records(records or [], contract, units) \
        if records is not None and manifest is not None else {
            "valid": False,
            "errors": [],
            "records": [],
            "invalid_records": 0,
            "duplicate_slots": 0,
            "conflicting_slots": 0,
            "unexpected_slots": 0,
        }
    errors.extend(record_report["errors"])

    if manifest is not None:
        if manifest.get("checkpoint_schema_version") != contract["checkpoint_schema_version"]:
            errors.append("unknown checkpoint schema version")
        for field, expected_value in contract.items():
            if manifest.get(field) != expected_value:
                errors.append(f"checkpoint contract mismatch: {field}")
        if manifest.get("checkpoint_record_count") != len(records or []):
            errors.append("checkpoint record count mismatch")
        if manifest.get("checkpoint_records_fingerprint") != _records_fingerprint(records or []):
            errors.append("checkpoint record-set fingerprint mismatch")
        expected_accounting = checkpoint_record_accounting(
            records or [], contract["expected_slots"]
        )
        if manifest.get("checkpoint_accounting") != expected_accounting:
            errors.append("checkpoint accounting mismatch")
        stored_checkpoint_fp = manifest.get("checkpoint_fingerprint")
        if not isinstance(stored_checkpoint_fp, str) or not _HEX64_RE.fullmatch(
            stored_checkpoint_fp
        ):
            errors.append("checkpoint fingerprint malformed or missing")
        elif stored_checkpoint_fp != _checkpoint_fingerprint(manifest):
            errors.append("checkpoint fingerprint mismatch")

    valid_records = record_report["records"] if not errors else []
    accounting = checkpoint_record_accounting(
        valid_records if not errors else [], contract["expected_slots"]
    )
    accounting["records_loaded"] = len(records or [])
    accounting.update(
        {
            "invalid_records": record_report["invalid_records"],
            "duplicate_slots": record_report["duplicate_slots"],
            "conflicting_slots": record_report["conflicting_slots"],
            "unexpected_slots": record_report["unexpected_slots"],
        }
    )
    return {
        **base,
        "status": "VALID_CHECKPOINT" if not errors else (
            "LEGACY_CHECKPOINT_NON_RESUMABLE" if legacy else "INVALID_CHECKPOINT"
        ),
        "valid": not errors,
        "resumable": not errors,
        "legacy_checkpoint": legacy,
        "errors": errors,
        "records": valid_records,
        "invalid_records": record_report["invalid_records"],
        "duplicate_slots": record_report["duplicate_slots"],
        "conflicting_slots": record_report["conflicting_slots"],
        "unexpected_slots": record_report["unexpected_slots"],
        "accounting": accounting,
    }


def _write_json_atomic(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")
    temporary.replace(path)


def write_resume_checkpoint(
    records_path: str | Path,
    manifest_path: str | Path,
    records: list[dict],
    contract: dict,
    units: list,
) -> dict:
    """Atomically replace both prospective checkpoint components.

    The two files cannot be replaced as one filesystem transaction.  Any crash
    between replacements leaves a detectable record-set/manifest mismatch and
    therefore fails closed on the next resume.
    """
    report = validate_checkpoint_records(records, contract, units)
    if not report["valid"]:
        raise ResumeIntegrityError(
            "refusing to persist invalid checkpoint records: " + "; ".join(report["errors"])
        )
    records_path = Path(records_path)
    records_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = records_path.with_suffix(records_path.suffix + ".tmp")
    with temporary.open("w") as handle:
        for record in sorted(records, key=lambda value: _slot_key(value)):
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    temporary.replace(records_path)
    manifest = build_checkpoint_manifest(contract, records)
    _write_json_atomic(Path(manifest_path), manifest)
    return manifest
