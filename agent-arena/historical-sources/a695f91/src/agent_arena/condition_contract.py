"""Condition-aware, registered execution specifications for Study Forensics.

This module is deliberately narrow.  It supports the immutable Phase-7 prompt,
the prospective taxonomy-aligned prompt under the paired Phase-5A plan, and the
separately registered one-shot Phase-5B Haiku replication.  A caller may select a
registered plan/arm/model identifier, but may not supply prompt text, units,
repetitions, runtime values, fingerprints, QA scope, or approval state.

Specification identity is independent of authorization and progress.  Actual
source/environment/QA identity is intentionally captured later by the guarded
preflight and checkpoint layers, avoiding self-referential committed artifacts.
"""

from __future__ import annotations

import copy
import json
import subprocess
from pathlib import Path

from agent_arena import condition_analysis as ca
from agent_arena import condition_retry as cr
from agent_arena import phase7a_execution as p7
from agent_arena import preflight_integrity as pi
from agent_arena import runtime_contract as rc
from agent_arena.runner import (
    STUDY_FORENSICS_PROMPT_VERSION_HISTORICAL,
    STUDY_FORENSICS_PROMPT_VERSION_PROSPECTIVE,
    resolve_study_forensics_prompt,
    study_forensics_prompt_identity,
)


PLAN_DOCUMENT_SCHEMA_VERSION = "agent_arena.condition_plan_document/v1"
SPECIFICATION_SCHEMA_VERSION = "agent_arena.condition_execution_specification/v1"
ARM_SCHEMA_VERSION = "agent_arena.condition_arm/v1"
RUNTIME_SCHEMA_VERSION = "agent_arena.condition_runtime/v1"
EXECUTION_MANIFEST_SCHEMA_VERSION = "agent_arena.condition_execution_manifest/v1"
CALL_PLAN_SCHEMA_VERSION = "agent_arena.condition_call_plan/v1"
PACKET_DESCRIPTOR_VERSION = "study_forensics_packet/v2-condition-aware"
OUTPUT_CONTRACT_ID = "study_forensics_output_contract/v1"

AUTH_NOT_AUTHORIZED = "NOT_AUTHORIZED_FOR_REAL_EXECUTION"
AUTH_REAL = "AUTHORIZED_FOR_REAL_EXECUTION"
AUTH_SYNTHETIC_TEST = "AUTHORIZED_SYNTHETIC_TEST_ONLY"
AUTH_CONSUMED = "CONSUMED_AFTER_SINGLE_GUARDED_INVOCATION"
PROGRESS_NOT_EXECUTED = "NOT_EXECUTED"
PROGRESS_PARTIAL = "PARTIAL"
PROGRESS_PARTIAL_INCOMPLETE = "PARTIAL_INCOMPLETE"
PROGRESS_COMPLETE = "COMPLETE"

PAIRED_PLAN_ID = "AA-P5A-MEOV-PAIRED-001"
PAIRED_COMPARISON_ID = "AA-P5A-MEOV-COMPARISON-001"
HISTORICAL_ARM_ID = "contemporary_historical_prompt_control"
PROSPECTIVE_ARM_ID = "prospective_taxonomy_aligned_prompt"

_REGISTERED_PLAN_PATHS = {
    "AA-HARNESS-VALUE-20260913-001-CONTINUATION-001": Path(
        "analysis/harness_value_20260913/continuation/execution_plan.json"
    ),
    "AA-HARNESS-VALUE-20260913-001": Path(
        "analysis/harness_value_20260913/execution_plan.json"
    ),
    PAIRED_PLAN_ID: Path(
        "analysis/phase5a_scientific_contract/paired_prompt_validation_plan.json"
    ),
    "AA-P5B-HAIKU-FULL-REPLICATION-001": Path(
        "analysis/phase5b_haiku_full_replication/execution_plan.json"
    ),
    "AA-P5B-SONNET-FULL-REPLICATION-001": Path(
        "analysis/phase5b_sonnet_full_replication/execution_plan.json"
    ),
}


class ConditionContractError(ValueError):
    """A registered condition, plan, or immutable binding failed validation."""


def _canon(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _fp(value: object) -> str:
    return rc._sha256_hex(_canon(value).encode("utf-8"))


def _without_fingerprint(value: dict, field: str) -> dict:
    return {key: item for key, item in value.items() if key != field}


def packet_descriptor(prompt_version: str) -> str:
    identity = study_forensics_prompt_identity(prompt_version)
    return (
        f"{PACKET_DESCRIPTOR_VERSION}|prompt_version={prompt_version}|"
        f"prompt_condition_id={identity['prompt_condition_id']}|"
        "system=resolved_registered_prompt(verbatim)|user=task.prompt(verbatim)|"
        "messages=[{role:user,content:user}]"
    )


def package_contract(prompt_version: str) -> dict:
    prompt = resolve_study_forensics_prompt(prompt_version)
    identity = study_forensics_prompt_identity(prompt_version)
    payload = {
        "package_schema_version": "agent_arena.study_forensics_package/v1",
        **identity,
        "system_prompt_sha256": rc._sha256_hex(prompt.encode("utf-8")),
        "packet_descriptor_version": PACKET_DESCRIPTOR_VERSION,
        "packet_descriptor_sha256": rc._sha256_hex(
            packet_descriptor(prompt_version).encode("utf-8")
        ),
        "output_contract_id": OUTPUT_CONTRACT_ID,
        "output_contract_sha256": rc.parser_contract_sha256(),
    }
    payload["package_fingerprint"] = _fp(payload)
    return payload


def registered_identity_contract() -> dict:
    """Expose exact registry-derived identities without creating a second source of truth."""
    return {
        "identity_contract_schema_version": "agent_arena.condition_registry_bindings/v1",
        "model_registry_source": "agent_arena.runtime_contract.MODELS",
        "models": [
            {
                "model_key": key,
                "exact_model_id": rc.MODELS[key]["exact_model_id"],
                "model_revision": rc.MODELS[key]["model_revision"],
                "agent_config_path": rc.MODELS[key]["agent_config_path"],
            }
            for key in ("haiku", "sonnet")
        ],
        "prompt_registry_source": "agent_arena.runner._STUDY_FORENSICS_PROMPT_REGISTRY",
        "prompts": [
            {
                "prompt_version": version,
                "prompt_condition_id": package_contract(version)["prompt_condition_id"],
                "system_prompt_sha256": package_contract(version)["system_prompt_sha256"],
            }
            for version in (
                STUDY_FORENSICS_PROMPT_VERSION_HISTORICAL,
                STUDY_FORENSICS_PROMPT_VERSION_PROSPECTIVE,
            )
        ],
        "unit_registry_source": "agent_arena.phase7a_execution.resolve_evaluated_units",
        "runtime_contract_builder": "agent_arena.condition_contract.condition_runtime_contract",
        "analysis_contract_implementation": "agent_arena.condition_analysis",
        "retry_contract_source": "agent_arena.condition_retry.build_retry_contract",
    }


def registered_provider_state() -> dict:
    """Preserve unknown external state without performing an unauthorized check."""
    return {
        "model_availability": "UNKNOWN_PENDING_SEPARATELY_AUTHORIZED_PROVIDER_CHECK",
        "pricing": "UNKNOWN_PENDING_SEPARATELY_AUTHORIZED_CURRENT_PRICE_CHECK",
        "verification_authorized": False,
    }


def build_call_accounting(
    *,
    n_units: int,
    n_replications: int,
    primary_units: int,
    control_units: int,
) -> dict:
    """Separate analytical slots from provider invocations and HTTP attempts."""
    for name, value in (
        ("n_units", n_units),
        ("n_replications", n_replications),
        ("primary_units", primary_units),
        ("control_units", control_units),
    ):
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ConditionContractError(f"{name} must be a nonnegative integer")
    if n_units <= 0 or n_replications <= 0:
        raise ConditionContractError("units and repetitions must be positive")
    if primary_units + control_units != n_units:
        raise ConditionContractError("primary and control populations must partition units")
    model_count = 2
    arm_count = 2
    slots_per_model_arm = n_units * n_replications
    return {
        "model_count": model_count,
        "prompt_arm_count": arm_count,
        "independent_units": n_units,
        "repetitions": n_replications,
        "formula": (
            f"{model_count} models × {arm_count} prompt arms × {n_units} units × "
            f"{n_replications} repetitions"
        ),
        "analytical_slots_total": model_count * arm_count * slots_per_model_arm,
        "analytical_slots_per_model_arm_batch": slots_per_model_arm,
        "analytical_slots_per_model_across_arms": arm_count * slots_per_model_arm,
        "analytical_slots_per_arm_across_models": model_count * slots_per_model_arm,
        "guarded_batch_invocations_in_schedule": model_count * arm_count,
        "primary_units_per_model_arm": primary_units,
        "control_units_per_model_arm": control_units,
        "provider_invocations_are_not_analytical_slots": True,
        "http_attempts_are_not_provider_invocations": True,
    }


def condition_runtime_contract(
    model_key: str,
    prompt_version: str,
    repo_root: str | Path | None = None,
) -> dict:
    if model_key not in rc.MODELS:
        raise ConditionContractError(f"unknown registered model key: {model_key}")
    model = rc.MODELS[model_key]
    package = package_contract(prompt_version)
    payload = {
        "runtime_schema_version": RUNTIME_SCHEMA_VERSION,
        "runtime_contract_id": (
            f"AA-P5A-RTC-{model_key.upper()}-"
            f"{package['prompt_condition_id'].rsplit('.', 1)[-1].upper()}-001"
        ),
        "model_key": model_key,
        "model_family": model["model_family"],
        "exact_model_id": model["exact_model_id"],
        "model_revision": model["model_revision"],
        "agent_config_path": model["agent_config_path"],
        "agent_config_model": rc.agent_config_model(model["agent_config_path"], repo_root),
        "agent_config_sha256": rc.agent_config_sha256(model["agent_config_path"], repo_root),
        "prompt_condition_id": package["prompt_condition_id"],
        "prompt_version": prompt_version,
        "system_prompt_sha256": package["system_prompt_sha256"],
        "package_fingerprint": package["package_fingerprint"],
        "runtime": copy.deepcopy(rc.SHARED_RUNTIME),
    }
    payload["runtime_contract_fingerprint"] = _fp(payload)
    return payload


def _unit_bindings(definition: dict, repo_root: str | Path | None) -> list[dict]:
    available = {unit.unit_id: unit for unit in p7.resolve_evaluated_units(repo_root)}
    ordered_ids: list[str] = []
    for stratum in definition["unit_strata"]:
        ordered_ids.extend(stratum["unit_ids"])
    if len(set(ordered_ids)) != len(ordered_ids):
        raise ConditionContractError("registered plan contains duplicate unit identities")
    missing = [unit_id for unit_id in ordered_ids if unit_id not in available]
    if missing:
        raise ConditionContractError(f"registered plan units unavailable: {missing}")
    bindings = []
    for unit_id in ordered_ids:
        unit = available[unit_id]
        if unit.unit_type == "perturbation_variant":
            raise ConditionContractError(
                "paired Phase-5A plan must use independent base units, not nested variants"
            )
        bindings.append(unit.meta())
    return bindings


def _selected_unit_manifest_fingerprint(unit_bindings: list[dict]) -> str:
    """Match the Phase-7 scientific-manifest material over the selected subset."""
    rows = sorted(
        (
            unit["unit_id"],
            unit["unit_type"],
            unit["gold_label"],
            unit["unit_fingerprint"],
            unit["cluster_root_id"] or "",
            unit["family_id"] or "",
        )
        for unit in unit_bindings
    )
    return _fp(rows)


def _build_arm(
    definition: dict,
    arm_definition: dict,
    unit_bindings: list[dict],
    repo_root: str | Path | None,
) -> dict:
    prompt_version = arm_definition["prompt_version"]
    package = package_contract(prompt_version)
    runtime_contracts = {
        key: condition_runtime_contract(key, prompt_version, repo_root)
        for key in definition["model_keys"]
    }
    runtime_fingerprints = {
        contract["exact_model_id"]: contract["runtime_contract_fingerprint"]
        for contract in runtime_contracts.values()
    }
    execution_manifest = {
        "execution_manifest_schema_version": EXECUTION_MANIFEST_SCHEMA_VERSION,
        "plan_id": definition["plan_id"],
        "arm_id": arm_definition["arm_id"],
        "analytical_condition_id": arm_definition["analytical_condition_id"],
        "prompt_condition_id": package["prompt_condition_id"],
        "prompt_version": prompt_version,
        "package_fingerprint": package["package_fingerprint"],
        "ordered_unit_bindings": unit_bindings,
        "n_independent_units": len(unit_bindings),
        "data_role": "historically_exposed_phase7_class_b_validation",
        "holdout_claim": False,
        "execution_mode": definition["execution_mode"],
        "artifact_namespace": arm_definition["artifact_namespace"],
    }
    execution_manifest["execution_manifest_fingerprint"] = _fp(execution_manifest)
    slots = [
        [rc.MODELS[model_key]["exact_model_id"], unit["unit_id"], run_index]
        for model_key in definition["model_keys"]
        for unit in unit_bindings
        for run_index in range(definition["n_replications"])
    ]
    call_plan = {
        "call_plan_schema_version": CALL_PLAN_SCHEMA_VERSION,
        "plan_id": definition["plan_id"],
        "arm_id": arm_definition["arm_id"],
        "analytical_condition_id": arm_definition["analytical_condition_id"],
        "prompt_condition_id": package["prompt_condition_id"],
        "model_ids": [rc.MODELS[key]["exact_model_id"] for key in definition["model_keys"]],
        "n_replications": definition["n_replications"],
        "n_independent_units": len(unit_bindings),
        "expected_calls": len(slots),
        "expected_slots_fingerprint": _fp(slots),
        "sdk_transport_retries_after_initial_per_provider_invocation": (
            rc.SHARED_RUNTIME["max_transport_retries_after_initial_request"]
        ),
        "outer_provider_error_passes_per_guarded_invocation": (
            cr.PROVIDER_ERROR_PASSES_PER_GUARDED_INVOCATION
        ),
        "provider_method_invocations_for_arm_schedule_max": (
            len(slots) * cr.PROVIDER_ERROR_PASSES_PER_GUARDED_INVOCATION
        ),
        "http_attempts_for_arm_schedule_max": (
            len(slots)
            * cr.PROVIDER_ERROR_PASSES_PER_GUARDED_INVOCATION
            * (1 + rc.SHARED_RUNTIME["max_transport_retries_after_initial_request"])
        ),
        "retry_contract_fingerprint": _fp(definition["retry_contract"]),
        "package_fingerprint": package["package_fingerprint"],
        "runtime_contract_fingerprints": runtime_fingerprints,
        "execution_manifest_fingerprint": execution_manifest[
            "execution_manifest_fingerprint"
        ],
    }
    call_plan["call_plan_fingerprint"] = _fp(call_plan)
    arm = {
        "arm_schema_version": ARM_SCHEMA_VERSION,
        **arm_definition,
        "prompt_condition_id": package["prompt_condition_id"],
        "system_prompt_sha256": package["system_prompt_sha256"],
        "packet_descriptor_version": package["packet_descriptor_version"],
        "packet_descriptor_sha256": package["packet_descriptor_sha256"],
        "output_contract_id": package["output_contract_id"],
        "output_contract_sha256": package["output_contract_sha256"],
        "package_fingerprint": package["package_fingerprint"],
        "runtime_contracts": runtime_contracts,
        "runtime_contract_fingerprints": runtime_fingerprints,
        "execution_manifest": execution_manifest,
        "call_plan": call_plan,
    }
    arm["arm_specification_fingerprint"] = _fp(arm)
    return arm


def build_specification(definition: dict, repo_root: str | Path | None = None) -> dict:
    """Build the immutable scientific/execution specification from tracked definition."""
    if isinstance(definition, dict):
        if definition.get("plan_id") == "AA-HARNESS-VALUE-20260913-001-CONTINUATION-001":
            from agent_arena import bounded_harness_continuation

            return bounded_harness_continuation.build_specification(definition, repo_root)
        if definition.get("plan_id") == "AA-HARNESS-VALUE-20260913-001":
            from agent_arena import bounded_harness_mission

            return bounded_harness_mission.build_specification(definition, repo_root)
        from agent_arena import full_replication_contract as frc

        if definition.get("plan_id") in frc.FULL_REPLICATION_PLAN_IDS:
            return frc.build_specification(definition, repo_root)
    required = {
        "plan_id",
        "comparison_id",
        "research_question",
        "hypothesis",
        "model_keys",
        "n_replications",
        "execution_mode",
        "qa_profile",
        "unit_selection_rule",
        "unit_strata",
        "arms",
        "analysis_contract",
        "registered_identity_contract",
        "provider_state",
        "call_accounting",
        "retry_contract",
    }
    if set(definition) != required:
        raise ConditionContractError("registered plan definition is partial or has unknown fields")
    if definition["plan_id"] != PAIRED_PLAN_ID:
        raise ConditionContractError("registered definition carries the wrong plan identity")
    if definition["model_keys"] != ["haiku", "sonnet"]:
        raise ConditionContractError("paired Phase-5A model set must remain fixed")
    n = definition["n_replications"]
    if n != 3:
        raise ConditionContractError("paired Phase-5A replication count must remain exactly three")
    if definition["qa_profile"] != pi.CONDITION_CONTRACT_QA_VERSION:
        raise ConditionContractError("registered plan QA profile is not the internal condition scope")
    arm_ids = [arm["arm_id"] for arm in definition["arms"]]
    if arm_ids != [HISTORICAL_ARM_ID, PROSPECTIVE_ARM_ID]:
        raise ConditionContractError("paired plan must contain the fixed old/new arm order")
    prompt_versions = [arm["prompt_version"] for arm in definition["arms"]]
    if prompt_versions != [
        STUDY_FORENSICS_PROMPT_VERSION_HISTORICAL,
        STUDY_FORENSICS_PROMPT_VERSION_PROSPECTIVE,
    ]:
        raise ConditionContractError("paired plan prompt versions are not the registered pair")

    if definition["registered_identity_contract"] != registered_identity_contract():
        raise ConditionContractError("registered model/prompt identity contract does not reproduce")
    if definition["provider_state"] != registered_provider_state():
        raise ConditionContractError("registered provider availability/pricing state changed")

    units = _unit_bindings(definition, repo_root)
    populations = definition["analysis_contract"].get("populations") or {}
    primary_units = (populations.get("primary") or {}).get("expected_units_per_model_arm")
    control_units = (populations.get("controls") or {}).get("expected_units_per_model_arm")
    call_accounting = build_call_accounting(
        n_units=len(units),
        n_replications=n,
        primary_units=primary_units,
        control_units=control_units,
    )
    if definition["call_accounting"] != call_accounting:
        raise ConditionContractError("registered call accounting does not reproduce")
    retry_contract = cr.build_retry_contract(
        analytical_slots=call_accounting["analytical_slots_total"],
        guarded_batch_invocations=call_accounting["guarded_batch_invocations_in_schedule"],
        slots_per_batch=call_accounting["analytical_slots_per_model_arm_batch"],
    )
    if definition["retry_contract"] != retry_contract:
        raise ConditionContractError("registered retry accounting does not reproduce")
    analysis_errors = ca.validate_analysis_contract(
        definition["analysis_contract"], definition["unit_strata"], n
    )
    if analysis_errors:
        raise ConditionContractError("; ".join(analysis_errors))
    arms = [_build_arm(definition, arm, units, repo_root) for arm in definition["arms"]]
    calls_per_arm = call_accounting["analytical_slots_per_arm_across_models"]
    specification = {
        "specification_schema_version": SPECIFICATION_SCHEMA_VERSION,
        "plan_id": definition["plan_id"],
        "comparison_id": definition["comparison_id"],
        "research_question": definition["research_question"],
        "hypothesis": definition["hypothesis"],
        "model_keys": definition["model_keys"],
        "model_ids": [rc.MODELS[key]["exact_model_id"] for key in definition["model_keys"]],
        "registered_identity_contract": definition["registered_identity_contract"],
        "provider_state": definition["provider_state"],
        "n_replications": n,
        "execution_mode": definition["execution_mode"],
        "qa_specification": pi.condition_contract_qa_specification(),
        "qa_specification_fingerprint": pi.condition_contract_qa_specification_fingerprint(),
        "unit_selection_rule": definition["unit_selection_rule"],
        "unit_strata": definition["unit_strata"],
        "ordered_unit_bindings": units,
        "ordered_unit_universe_fingerprint": _fp(units),
        "selected_unit_manifest_fingerprint": _selected_unit_manifest_fingerprint(units),
        "n_independent_units": len(units),
        "arms": arms,
        "analysis_contract": definition["analysis_contract"],
        "analysis_contract_fingerprint": _fp(definition["analysis_contract"]),
        "call_accounting": call_accounting,
        "retry_contract": retry_contract,
        "retry_contract_fingerprint": _fp(retry_contract),
        "expected_calls_per_arm": calls_per_arm,
        "expected_calls_total": call_accounting["analytical_slots_total"],
        "provider_method_invocations_schedule_max": retry_contract["schedule"][
            "provider_method_invocations_schedule_max"
        ],
        "http_attempts_schedule_max": retry_contract["schedule"][
            "http_attempts_schedule_max"
        ],
    }
    specification["specification_fingerprint"] = _fp(specification)
    return specification


def build_plan_document(definition: dict, repo_root: str | Path | None = None) -> dict:
    specification = build_specification(definition, repo_root)
    return {
        "plan_document_schema_version": PLAN_DOCUMENT_SCHEMA_VERSION,
        "definition": copy.deepcopy(definition),
        "specification": specification,
        "authorization": {
            "status": AUTH_NOT_AUTHORIZED,
            "specification_fingerprint": specification["specification_fingerprint"],
            "authorization_source": "NO_PRODUCTION_APPROVAL_COMMITTED",
            "authorized_budget_calls": 0,
        },
        "progress": {
            "status": PROGRESS_NOT_EXECUTED,
            "completed_calls": 0,
            "arm_progress": {
                arm["arm_id"]: PROGRESS_NOT_EXECUTED for arm in specification["arms"]
            },
        },
    }


def specification_fingerprint(document: dict) -> str:
    """Reproduce immutable identity; authorization/progress are deliberately excluded."""
    specification = copy.deepcopy(document["specification"])
    stored = specification.pop("specification_fingerprint", None)
    reproduced = _fp(specification)
    if stored != reproduced:
        raise ConditionContractError("plan specification fingerprint does not reproduce")
    return reproduced


def validate_plan_document(
    document: dict,
    repo_root: str | Path | None = None,
    *,
    _allow_synthetic_test: bool = False,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict) or set(document) != {
        "plan_document_schema_version", "definition", "specification", "authorization", "progress"
    }:
        return ["plan document is partial or has unknown fields"]
    if document.get("plan_document_schema_version") != PLAN_DOCUMENT_SCHEMA_VERSION:
        errors.append("plan document schema version mismatch")
    try:
        expected = build_specification(document["definition"], repo_root)
    except (ConditionContractError, KeyError, TypeError, OSError) as exc:
        errors.append(f"plan definition cannot reproduce specification: {exc}")
        return errors
    if document.get("specification") != expected:
        errors.append("stored immutable specification differs from tracked definition")
    try:
        spec_fp = specification_fingerprint(document)
    except (ConditionContractError, KeyError, TypeError) as exc:
        errors.append(str(exc))
        spec_fp = None
    authorization = document.get("authorization")
    if not isinstance(authorization, dict):
        errors.append("plan authorization state is malformed")
    else:
        if authorization.get("specification_fingerprint") != spec_fp:
            errors.append("authorization refers to another specification")
        allowed_states = {AUTH_NOT_AUTHORIZED, AUTH_REAL, AUTH_CONSUMED}
        if _allow_synthetic_test:
            allowed_states.add(AUTH_SYNTHETIC_TEST)
        if authorization.get("status") not in allowed_states:
            errors.append("unsupported production authorization state")
        if authorization.get("status") == AUTH_REAL:
            if authorization.get("authorization_source") != "tracked_governance_approval":
                errors.append("real authorization lacks tracked governance approval")
            if authorization.get("authorized_budget_calls") != expected["expected_calls_total"]:
                errors.append("real authorization budget differs from immutable call plan")
        elif authorization.get("status") == AUTH_SYNTHETIC_TEST:
            if authorization.get("authorization_source") != "private_test_seam":
                errors.append("synthetic authorization is not from the private test seam")
            if authorization.get("authorized_budget_calls") != expected["expected_calls_total"]:
                errors.append("synthetic authorization budget differs from immutable call plan")
        elif authorization.get("status") == AUTH_CONSUMED:
            if authorization.get("authorized_budget_calls") != 0:
                errors.append("consumed one-shot plan carries a nonzero authorized budget")
        elif authorization.get("authorized_budget_calls") != 0:
            errors.append("unapproved plan carries a nonzero authorized budget")
    progress = document.get("progress")
    if not isinstance(progress, dict) or progress.get("status") not in {
        PROGRESS_NOT_EXECUTED, PROGRESS_PARTIAL, PROGRESS_PARTIAL_INCOMPLETE,
        PROGRESS_COMPLETE
    }:
        errors.append("plan progress state is malformed")
    from agent_arena import full_replication_contract as frc

    if document.get("specification", {}).get("plan_id") in frc.FULL_REPLICATION_PLAN_IDS:
        errors.extend(
            frc.validate_document_state(
                document,
                allow_synthetic_test=_allow_synthetic_test,
            )
        )
    return errors


def _repo_root(repo_root: str | Path | None) -> Path:
    return Path(repo_root).resolve() if repo_root else Path(__file__).resolve().parents[2]


def _read_authenticated_plan_artifact(root: Path, relative: Path) -> bytes:
    """Read a plan only when its working-tree bytes equal the authenticated HEAD bytes."""
    relative_text = relative.as_posix()
    tracked = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--error-unmatch", "--", relative_text],
        capture_output=True,
        check=False,
    )
    if tracked.returncode != 0:
        raise ConditionContractError("registered plan artifact is not tracked at HEAD")
    frozen = subprocess.run(
        ["git", "-C", str(root), "show", f"HEAD:{relative_text}"],
        capture_output=True,
        check=False,
    )
    if frozen.returncode != 0:
        raise ConditionContractError("registered plan artifact is unavailable from HEAD")
    try:
        working = (root / relative).read_bytes()
    except OSError as exc:
        raise ConditionContractError(f"registered plan artifact unreadable: {exc}") from exc
    if working != frozen.stdout:
        raise ConditionContractError("registered plan artifact differs from authenticated HEAD")
    return working


def resolve_registered_plan(plan_id: str, repo_root: str | Path | None = None) -> dict:
    """Load only an internally registered tracked plan; arbitrary paths are impossible."""
    try:
        relative = _REGISTERED_PLAN_PATHS[plan_id]
    except KeyError as exc:
        raise ConditionContractError(f"unknown registered plan identifier: {plan_id}") from exc
    root = _repo_root(repo_root)
    path = (root / relative).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:  # pragma: no cover - registry constant defense
        raise ConditionContractError("registered plan path escapes repository root") from exc
    try:
        artifact = json.loads(_read_authenticated_plan_artifact(root, relative).decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ConditionContractError(f"registered plan artifact unreadable: {exc}") from exc
    if not isinstance(artifact, dict) or set(artifact) != {
        "plan_document_schema_version", "definition", "authorization", "progress"
    }:
        raise ConditionContractError("registered plan artifact is partial or has unknown fields")
    document = {
        "plan_document_schema_version": artifact["plan_document_schema_version"],
        "definition": artifact["definition"],
        "specification": build_specification(artifact["definition"], root),
        "authorization": artifact["authorization"],
        "progress": artifact["progress"],
    }
    errors = validate_plan_document(document, root)
    if errors:
        raise ConditionContractError("; ".join(errors))
    if document["specification"]["plan_id"] != plan_id:
        raise ConditionContractError("registered path resolved a different plan identity")
    return copy.deepcopy(document)


def resolve_arm(document: dict, arm_id: str) -> dict:
    matches = [arm for arm in document["specification"]["arms"] if arm["arm_id"] == arm_id]
    if len(matches) != 1:
        raise ConditionContractError(f"unknown or duplicate registered arm: {arm_id}")
    return copy.deepcopy(matches[0])


def production_authorization_errors(
    document: dict,
    repo_root: str | Path | None = None,
) -> list[str]:
    """A hash identifies content; only tracked governance state can authorize it."""
    errors = validate_plan_document(document, repo_root)
    authorization = document.get("authorization") or {}
    if authorization.get("status") != AUTH_REAL:
        errors.append("registered plan is not authorized for real execution")
    if authorization.get("authorization_source") != "tracked_governance_approval":
        errors.append("registered plan lacks tracked governance approval")
    return errors


def units_for_plan(document: dict, repo_root: str | Path | None = None) -> list:
    available = {unit.unit_id: unit for unit in p7.resolve_evaluated_units(repo_root)}
    ordered = [item["unit_id"] for item in document["specification"]["ordered_unit_bindings"]]
    try:
        return [available[unit_id] for unit_id in ordered]
    except KeyError as exc:
        raise ConditionContractError(f"specified unit unavailable: {exc.args[0]}") from exc


def verify_arm_bindings(
    document: dict,
    arm: dict,
    model_key: str,
    repo_root: str | Path | None = None,
    *,
    _allow_synthetic_test: bool = False,
) -> list[str]:
    """Recompute prompt/package/runtime/manifest/call-plan identities fail closed."""
    errors = validate_plan_document(
        document, repo_root, _allow_synthetic_test=_allow_synthetic_test
    )
    try:
        expected_arm = resolve_arm(
            {"specification": build_specification(document["definition"], repo_root)},
            arm["arm_id"],
        )
    except (ConditionContractError, KeyError, TypeError, OSError) as exc:
        errors.append(f"arm bindings cannot reproduce: {exc}")
        return errors
    if arm != expected_arm:
        errors.append("prompt/package/runtime/manifest/call-plan arm bindings mismatch")
    if model_key not in document["specification"]["model_keys"]:
        errors.append("model is outside the registered specification")
    return errors


def synthetic_authorized_copy(document: dict, *, expected_calls: int) -> dict:
    """Private deterministic-test helper; never accepted by the public production resolver."""
    copied = copy.deepcopy(document)
    copied["authorization"] = {
        "status": AUTH_SYNTHETIC_TEST,
        "specification_fingerprint": copied["specification"]["specification_fingerprint"],
        "authorization_source": "private_test_seam",
        "authorized_budget_calls": expected_calls,
    }
    return copied
