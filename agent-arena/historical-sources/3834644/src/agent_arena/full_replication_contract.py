"""Registered one-shot contract for the Phase-5B full Haiku replication.

This is deliberately separate from the 19-unit paired Phase-5A design.  It
binds the complete historical Phase-7A universe to the prospective prompt and
one exact Haiku snapshot.  Historical responses are reference-only.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median

from agent_arena import condition_contract as cc
from agent_arena import phase7a_execution as p7
from agent_arena import preflight_integrity as pi
from agent_arena import runtime_contract as rc
from agent_arena.runner import STUDY_FORENSICS_PROMPT_VERSION_PROSPECTIVE


PLAN_ID = "AA-P5B-HAIKU-FULL-REPLICATION-001"
COMPARISON_ID = "AA-P5B-HAIKU-HISTORICAL-REFERENCE-001"
ARM_ID = "prospective_taxonomy_aligned_full_haiku"
ANALYTICAL_CONDITION_ID = "AA-P5B-COND-HAIKU-TAXONOMY-ALIGNED-FULL-001"
ANALYSIS_CONTRACT_ID = "AA-P5B-FULL-REPLICATION-ANALYSIS-001"
PLAN_PATH = Path("analysis/phase5b_haiku_full_replication/execution_plan.json")
COST_GATE_PATH = Path("analysis/phase5b_haiku_full_replication/pre_execution_cost_estimate.json")
ARTIFACT_NAMESPACE = "analysis/phase5b_haiku_full_replication/run"
LEASE_FILENAME = "execution_authorization_lease.json"
EXPECTED_MODEL_KEY = "haiku"
EXPECTED_MODEL_ID = "claude-haiku-4-5-20251001"
EXPECTED_PROMPT_CONDITION = "study_forensics.taxonomy_aligned.v2"
EXPECTED_PROMPT_SHA256 = "37d91b813bee2b4febb9dba5da66fa8e2bda1e091989785adf6ca5acc132b7ef"
EXPECTED_UNITS = 84
EXPECTED_REPETITIONS = 5
EXPECTED_SLOTS = 420
OPERATIONAL_BUDGET_USD = 6.0


class FullReplicationContractError(cc.ConditionContractError):
    """The registered full-replication contract failed closed."""


def _sha256(path: Path) -> str:
    return rc._sha256_hex(path.read_bytes())


def _required_definition_fields() -> set[str]:
    return {
        "plan_id",
        "comparison_id",
        "scientific_design",
        "research_question",
        "model_keys",
        "n_replications",
        "execution_mode",
        "qa_profile",
        "unit_selection_rule",
        "ordered_unit_ids",
        "arm",
        "retry_policy",
        "historical_reference",
        "governance_constraints",
        "pricing_contract",
    }


def _historical_reference_errors(reference: dict, root: Path) -> list[str]:
    errors: list[str] = []
    required = {
        "role",
        "model_id",
        "prompt_version",
        "expected_units",
        "expected_responses",
        "raw_records_path",
        "raw_records_sha256",
        "raw_freeze_path",
        "raw_freeze_sha256",
        "analysis_path",
        "analysis_sha256",
        "execution_manifest_path",
        "execution_manifest_sha256",
        "call_plan_path",
        "call_plan_sha256",
        "aggregate_result_set_fingerprint",
        "reported_unit_accuracy",
        "reported_brier",
    }
    if not isinstance(reference, dict) or set(reference) != required:
        return ["historical-reference definition is partial or has unknown fields"]
    if reference["role"] != "reference_only_not_reused_as_prospective_response":
        errors.append("historical records are not declared reference-only")
    if reference["model_id"] != EXPECTED_MODEL_ID:
        errors.append("historical reference model differs from exact Haiku snapshot")
    if reference["prompt_version"] != "study_forensics_prompt/v1-historical-phase7":
        errors.append("historical reference prompt identity mismatch")
    if reference["expected_units"] != EXPECTED_UNITS or reference["expected_responses"] != EXPECTED_SLOTS:
        errors.append("historical reference does not bind 84 units and 420 responses")
    for path_field, hash_field in (
        ("raw_records_path", "raw_records_sha256"),
        ("raw_freeze_path", "raw_freeze_sha256"),
        ("analysis_path", "analysis_sha256"),
        ("execution_manifest_path", "execution_manifest_sha256"),
        ("call_plan_path", "call_plan_sha256"),
    ):
        path = root / reference[path_field]
        try:
            actual = _sha256(path)
        except OSError as exc:
            errors.append(f"historical reference unavailable: {reference[path_field]}: {exc}")
            continue
        if actual != reference[hash_field]:
            errors.append(f"historical reference hash mismatch: {reference[path_field]}")
    try:
        freeze = json.loads((root / reference["raw_freeze_path"]).read_text())
        if freeze.get("aggregate_result_set_fingerprint") != reference[
            "aggregate_result_set_fingerprint"
        ]:
            errors.append("historical aggregate result-set fingerprint mismatch")
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"historical raw freeze cannot be verified: {exc}")
    return errors


def _retry_contract() -> dict:
    """One guarded pass; only the SDK's two transport retries may reissue HTTP."""
    http_attempts = 1 + rc.SHARED_RUNTIME["max_transport_retries_after_initial_request"]
    return {
        "retry_contract_schema_version": "agent_arena.full_replication_retry_contract/v1",
        "retry_contract_id": "AA-P5B-HAIKU-FULL-RETRY-001",
        "semantic_or_quality_retries": "PROHIBITED",
        "outer_provider_error_passes_per_guarded_invocation": 1,
        "sdk_transport_retries_after_initial_per_provider_invocation": 2,
        "guarded_batch_invocations_authorized": 1,
        "manual_restarts_authorized": 0,
        "provider_method_invocations_schedule_max": EXPECTED_SLOTS,
        "http_attempts_schedule_max": EXPECTED_SLOTS * http_attempts,
        "nonterminal_provider_failures_after_guarded_pass": "PRESERVE_AND_STOP",
        "persistent_provider_account_spending_cap": "NOT_IMPLEMENTED",
    }


def build_specification(definition: dict, repo_root: str | Path | None = None) -> dict:
    root = Path(repo_root).resolve() if repo_root else Path(__file__).resolve().parents[2]
    if not isinstance(definition, dict) or set(definition) != _required_definition_fields():
        raise FullReplicationContractError(
            "full-replication definition is partial or has unknown fields"
        )
    if definition["plan_id"] != PLAN_ID or definition["comparison_id"] != COMPARISON_ID:
        raise FullReplicationContractError("full-replication plan/comparison identity mismatch")
    if definition["scientific_design"] != "historical_reference_replication_not_randomized_ab":
        raise FullReplicationContractError("scientific design is not the registered replication")
    if definition["model_keys"] != [EXPECTED_MODEL_KEY]:
        raise FullReplicationContractError("full replication must contain Haiku only")
    if definition["n_replications"] != EXPECTED_REPETITIONS:
        raise FullReplicationContractError("full replication must use five repetitions")
    if definition["execution_mode"] != "independent_model_adjudication":
        raise FullReplicationContractError("full replication execution mode mismatch")
    if definition["qa_profile"] != pi.FULL_REPLICATION_QA_VERSION:
        raise FullReplicationContractError("full replication QA profile mismatch")
    if definition["retry_policy"] != _retry_contract():
        raise FullReplicationContractError("full replication retry contract mismatch")
    governance = definition["governance_constraints"]
    if governance != {
        "historical_responses_reused_as_prospective": False,
        "prompt_only_causal_attribution_permitted": False,
        "sonnet_authorized": False,
        "historical_prompt_arm_authorized": False,
        "official_release_writes_authorized": 0,
        "manual_restarts_authorized": 0,
        "one_shot_authorization_required": True,
    }:
        raise FullReplicationContractError("full replication governance constraints mismatch")
    if definition["pricing_contract"] != {
        "currency": "USD",
        "retrieval_date": "2026-08-29",
        "input_usd_per_million_tokens": 1.0,
        "output_usd_per_million_tokens": 5.0,
        "cache_enabled": False,
        "batch_api_enabled": False,
        "operational_authorization_limit_usd": OPERATIONAL_BUDGET_USD,
    }:
        raise FullReplicationContractError("full replication pricing contract mismatch")

    units = p7.resolve_evaluated_units(root)
    ordered_ids = [unit.unit_id for unit in units]
    if len(units) != EXPECTED_UNITS or len(set(ordered_ids)) != EXPECTED_UNITS:
        raise FullReplicationContractError("canonical Phase-7A unit universe is not 84 unique units")
    if definition["ordered_unit_ids"] != ordered_ids:
        raise FullReplicationContractError("ordered 84-unit universe differs from Phase-7A truth")
    historical_errors = _historical_reference_errors(definition["historical_reference"], root)
    if historical_errors:
        raise FullReplicationContractError("; ".join(historical_errors))

    arm_definition = definition["arm"]
    if arm_definition != {
        "arm_id": ARM_ID,
        "analytical_condition_id": ANALYTICAL_CONDITION_ID,
        "prompt_version": STUDY_FORENSICS_PROMPT_VERSION_PROSPECTIVE,
        "prompt_condition_id": EXPECTED_PROMPT_CONDITION,
        "system_prompt_sha256": EXPECTED_PROMPT_SHA256,
        "artifact_namespace": ARTIFACT_NAMESPACE,
    }:
        raise FullReplicationContractError("full replication arm identity mismatch")

    package = cc.package_contract(STUDY_FORENSICS_PROMPT_VERSION_PROSPECTIVE)
    if package["prompt_condition_id"] != EXPECTED_PROMPT_CONDITION:
        raise FullReplicationContractError("prospective prompt condition drift")
    if package["system_prompt_sha256"] != EXPECTED_PROMPT_SHA256:
        raise FullReplicationContractError("prospective prompt bytes drift")
    runtime = cc.condition_runtime_contract(
        EXPECTED_MODEL_KEY, STUDY_FORENSICS_PROMPT_VERSION_PROSPECTIVE, root
    )
    if runtime["exact_model_id"] != EXPECTED_MODEL_ID:
        raise FullReplicationContractError("exact Haiku runtime identity drift")
    unit_bindings = [unit.meta() for unit in units]
    execution_manifest = {
        "execution_manifest_schema_version": "agent_arena.full_replication_manifest/v1",
        "plan_id": PLAN_ID,
        "arm_id": ARM_ID,
        "model_id": EXPECTED_MODEL_ID,
        "prompt_condition_id": EXPECTED_PROMPT_CONDITION,
        "ordered_unit_bindings": unit_bindings,
        "n_evaluated_units": EXPECTED_UNITS,
        "n_replications": EXPECTED_REPETITIONS,
        "data_role": "historically_exposed_phase7_class_b_full_replication",
        "holdout_claim": False,
        "historical_responses_are_reference_only": True,
        "execution_mode": definition["execution_mode"],
        "artifact_namespace": ARTIFACT_NAMESPACE,
    }
    execution_manifest["execution_manifest_fingerprint"] = cc._fp(execution_manifest)
    slots = [
        [EXPECTED_MODEL_ID, unit.unit_id, run_index]
        for unit in units
        for run_index in range(EXPECTED_REPETITIONS)
    ]
    call_plan = {
        "call_plan_schema_version": "agent_arena.full_replication_call_plan/v1",
        "plan_id": PLAN_ID,
        "arm_id": ARM_ID,
        "model_ids": [EXPECTED_MODEL_ID],
        "prompt_condition_id": EXPECTED_PROMPT_CONDITION,
        "n_replications": EXPECTED_REPETITIONS,
        "n_evaluated_units": EXPECTED_UNITS,
        "expected_calls": EXPECTED_SLOTS,
        "expected_slots_fingerprint": cc._fp(slots),
        "guarded_batch_invocations": 1,
        "provider_method_invocations_schedule_max": EXPECTED_SLOTS,
        "http_attempts_schedule_max": EXPECTED_SLOTS * 3,
        "manual_restarts": 0,
        "package_fingerprint": package["package_fingerprint"],
        "runtime_contract_fingerprints": {
            EXPECTED_MODEL_ID: runtime["runtime_contract_fingerprint"]
        },
        "execution_manifest_fingerprint": execution_manifest[
            "execution_manifest_fingerprint"
        ],
    }
    call_plan["call_plan_fingerprint"] = cc._fp(call_plan)
    arm = {
        "arm_schema_version": "agent_arena.full_replication_arm/v1",
        **arm_definition,
        "packet_descriptor_version": package["packet_descriptor_version"],
        "packet_descriptor_sha256": package["packet_descriptor_sha256"],
        "output_contract_id": package["output_contract_id"],
        "output_contract_sha256": package["output_contract_sha256"],
        "package_fingerprint": package["package_fingerprint"],
        "runtime_contracts": {EXPECTED_MODEL_KEY: runtime},
        "runtime_contract_fingerprints": {
            EXPECTED_MODEL_ID: runtime["runtime_contract_fingerprint"]
        },
        "execution_manifest": execution_manifest,
        "call_plan": call_plan,
    }
    arm["arm_specification_fingerprint"] = cc._fp(arm)
    specification = {
        "specification_schema_version": "agent_arena.full_replication_specification/v1",
        "plan_id": PLAN_ID,
        "comparison_id": COMPARISON_ID,
        "scientific_design": definition["scientific_design"],
        "research_question": definition["research_question"],
        "model_keys": [EXPECTED_MODEL_KEY],
        "model_ids": [EXPECTED_MODEL_ID],
        "n_replications": EXPECTED_REPETITIONS,
        "execution_mode": definition["execution_mode"],
        "qa_specification": pi.full_replication_qa_specification(),
        "qa_specification_fingerprint": pi.full_replication_qa_specification_fingerprint(),
        "unit_selection_rule": definition["unit_selection_rule"],
        "ordered_unit_bindings": unit_bindings,
        "ordered_unit_universe_fingerprint": cc._fp(unit_bindings),
        "selected_unit_manifest_fingerprint": p7.scientific_manifest_fingerprint(units),
        "n_independent_units": EXPECTED_UNITS,
        "arms": [arm],
        "historical_reference": definition["historical_reference"],
        "historical_reference_fingerprint": cc._fp(definition["historical_reference"]),
        "analysis_contract": {
            "analysis_contract_id": ANALYSIS_CONTRACT_ID,
            "implementation": "agent_arena.full_replication_analysis",
            "expected_units": EXPECTED_UNITS,
            "expected_response_slots": EXPECTED_SLOTS,
            "targeted_19_denominator": 19,
            "remaining_65_denominator": 65,
            "historical_reference_not_randomized_control": True,
            "causal_prompt_attribution_prohibited": True,
        },
        "analysis_mode": "full_historical_reference_replication",
        "retry_contract": definition["retry_policy"],
        "governance_constraints": governance,
        "pricing_contract": definition["pricing_contract"],
        "expected_calls_per_arm": EXPECTED_SLOTS,
        "expected_calls_total": EXPECTED_SLOTS,
        "provider_method_invocations_schedule_max": EXPECTED_SLOTS,
        "http_attempts_schedule_max": EXPECTED_SLOTS * 3,
        "one_shot_execution": True,
        "execution_lease_filename": LEASE_FILENAME,
        "outer_provider_error_passes_per_guarded_invocation": 1,
        "cost_gate_path": COST_GATE_PATH.as_posix(),
    }
    specification["analysis_contract_fingerprint"] = cc._fp(
        specification["analysis_contract"]
    )
    specification["specification_fingerprint"] = cc._fp(specification)
    return specification


def validate_document_state(
    document: dict,
    *,
    allow_synthetic_test: bool = False,
) -> list[str]:
    errors: list[str] = []
    specification = document.get("specification") or {}
    authorization = document.get("authorization") or {}
    progress = document.get("progress") or {}
    if authorization.get("specification_fingerprint") != specification.get(
        "specification_fingerprint"
    ):
        errors.append("full replication authorization fingerprint mismatch")
    status = authorization.get("status")
    if status == cc.AUTH_REAL:
        expected = {
            "status": cc.AUTH_REAL,
            "specification_fingerprint": specification.get("specification_fingerprint"),
            "authorization_source": "tracked_governance_approval",
            "authorized_budget_calls": EXPECTED_SLOTS,
            "authorized_model_keys": [EXPECTED_MODEL_KEY],
            "authorized_prompt_condition_ids": [EXPECTED_PROMPT_CONDITION],
            "guarded_batch_invocations_authorized": 1,
            "manual_restarts_authorized": 0,
            "operational_budget_usd": OPERATIONAL_BUDGET_USD,
            "authorization_mode": "ONE_SHOT_LEASE_BEFORE_PROVIDER_CONSTRUCTION",
        }
        if authorization != expected:
            errors.append("full replication real authorization scope mismatch")
        if progress != {
            "status": cc.PROGRESS_NOT_EXECUTED,
            "completed_calls": 0,
            "arm_progress": {ARM_ID: cc.PROGRESS_NOT_EXECUTED},
        }:
            errors.append("authorized full replication must begin NOT_EXECUTED")
    elif status == cc.AUTH_SYNTHETIC_TEST and allow_synthetic_test:
        expected = {
            "status": cc.AUTH_SYNTHETIC_TEST,
            "specification_fingerprint": specification.get("specification_fingerprint"),
            "authorization_source": "private_test_seam",
            "authorized_budget_calls": EXPECTED_SLOTS,
        }
        if authorization != expected:
            errors.append("full replication synthetic authorization scope mismatch")
        if progress != {
            "status": cc.PROGRESS_NOT_EXECUTED,
            "completed_calls": 0,
            "arm_progress": {ARM_ID: cc.PROGRESS_NOT_EXECUTED},
        }:
            errors.append("synthetic full replication must begin NOT_EXECUTED")
    elif status == cc.AUTH_CONSUMED:
        expected = {
            "status": cc.AUTH_CONSUMED,
            "specification_fingerprint": specification.get("specification_fingerprint"),
            "authorization_source": "one_shot_execution_consumed",
            "authorized_budget_calls": 0,
            "authorized_model_keys": [],
            "authorized_prompt_condition_ids": [],
            "guarded_batch_invocations_authorized": 0,
            "manual_restarts_authorized": 0,
            "operational_budget_usd_remaining": 0,
            "authorization_mode": "REVOKED_AFTER_PRE_PROVIDER_QA_BLOCK",
            "consumption_reason": (
                "FRESH_CANONICAL_QA_COULD_NOT_EXECUTE_BEFORE_PROVIDER_CONSTRUCTION"
            ),
            "lease_fingerprint": None,
            "consumed_invocation_specification_fingerprint": (
                "a00c4eda7b90bd715a0f172c2401fcd47fcc2aacb513dbfd355e60ab2719729c"
            ),
            "consumed_invocation_qa_profile": "phase5b-full-replication-production-qa/v1",
        }
        if authorization != expected:
            errors.append("consumed full replication audit state mismatch")
        if progress.get("status") not in {cc.PROGRESS_COMPLETE, cc.PROGRESS_PARTIAL_INCOMPLETE}:
            errors.append("consumed full replication progress is not terminal")
    else:
        errors.append("full replication authorization state is unsupported")
    return errors


def validate_cost_gate(document: dict, repo_root: str | Path) -> dict:
    root = Path(repo_root).resolve()
    try:
        raw = cc._read_authenticated_plan_artifact(root, COST_GATE_PATH)
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError, cc.ConditionContractError) as exc:
        raise FullReplicationContractError(f"pre-execution cost gate unavailable: {exc}") from exc
    expected_keys = {
        "cost_gate_schema_version",
        "plan_id",
        "specification_fingerprint",
        "model_id",
        "prompt_condition_id",
        "unique_contexts_measured",
        "repetitions",
        "planned_slots",
        "input_tokens_first_attempt",
        "historical_output_distribution",
        "estimated_output_tokens",
        "pricing",
        "estimated_first_attempt_cost_usd",
        "operational_budget_usd",
        "within_authorized_budget",
        "token_count_endpoint",
        "model_generations",
        "cost_gate_fingerprint",
    }
    if not isinstance(value, dict) or set(value) != expected_keys:
        raise FullReplicationContractError("pre-execution cost gate is partial or malformed")
    stored = value.get("cost_gate_fingerprint")
    reproduced = cc._fp({k: v for k, v in value.items() if k != "cost_gate_fingerprint"})
    if stored != reproduced:
        raise FullReplicationContractError("pre-execution cost-gate fingerprint mismatch")
    if value["plan_id"] != PLAN_ID:
        raise FullReplicationContractError("cost gate refers to another plan")
    if value["specification_fingerprint"] != document["specification"][
        "specification_fingerprint"
    ]:
        raise FullReplicationContractError("cost gate refers to another specification")
    if value["model_id"] != EXPECTED_MODEL_ID or value["prompt_condition_id"] != EXPECTED_PROMPT_CONDITION:
        raise FullReplicationContractError("cost gate model/prompt identity mismatch")
    if (
        value["unique_contexts_measured"] != EXPECTED_UNITS
        or value["repetitions"] != EXPECTED_REPETITIONS
        or value["planned_slots"] != EXPECTED_SLOTS
    ):
        raise FullReplicationContractError("cost gate does not cover the 84x5 schedule")
    input_measurement = value["input_tokens_first_attempt"]
    expected_input_keys = {
        "per_unique_context",
        "sum_unique_contexts",
        "schedule_formula",
        "estimated_schedule_input_tokens",
    }
    if not isinstance(input_measurement, dict) or set(input_measurement) != expected_input_keys:
        raise FullReplicationContractError("input-token measurement is partial or malformed")
    rows = input_measurement["per_unique_context"]
    expected_ids = [
        binding["unit_id"] for binding in document["specification"]["ordered_unit_bindings"]
    ]
    if (
        not isinstance(rows, list)
        or [row.get("unit_id") for row in rows if isinstance(row, dict)] != expected_ids
        or any(not isinstance(row, dict) or set(row) != {"unit_id", "input_tokens"} for row in rows)
        or any(
            not isinstance(row["input_tokens"], int)
            or isinstance(row["input_tokens"], bool)
            or row["input_tokens"] <= 0
            for row in rows
        )
    ):
        raise FullReplicationContractError("input-token contexts do not bind the ordered universe")
    unique_input_total = sum(row["input_tokens"] for row in rows)
    scheduled_input_total = unique_input_total * EXPECTED_REPETITIONS
    if (
        input_measurement["sum_unique_contexts"] != unique_input_total
        or input_measurement["schedule_formula"] != "sum_unique_contexts * repetitions"
        or input_measurement["estimated_schedule_input_tokens"] != scheduled_input_total
    ):
        raise FullReplicationContractError("input-token schedule does not reproduce")

    output_distribution = value["historical_output_distribution"]
    expected_output_keys = {
        "source_path",
        "source_sha256",
        "response_records",
        "records_with_output_tokens",
        "sum_output_tokens",
        "mean_output_tokens",
        "median_output_tokens",
        "minimum_output_tokens",
        "maximum_output_tokens",
    }
    if not isinstance(output_distribution, dict) or set(output_distribution) != expected_output_keys:
        raise FullReplicationContractError("historical output distribution is partial or malformed")
    reference = document["specification"]["historical_reference"]
    if (
        output_distribution["source_path"] != reference["raw_records_path"]
        or output_distribution["source_sha256"] != reference["raw_records_sha256"]
    ):
        raise FullReplicationContractError("historical output distribution source mismatch")
    historical_records = [
        json.loads(line)
        for line in (root / reference["raw_records_path"]).read_text().splitlines()
        if line.strip()
    ]
    output_tokens = [
        record.get("usage", {}).get("output_tokens")
        for record in historical_records
        if isinstance(record.get("usage", {}).get("output_tokens"), int)
        and not isinstance(record.get("usage", {}).get("output_tokens"), bool)
    ]
    reproduced_distribution = {
        "source_path": reference["raw_records_path"],
        "source_sha256": reference["raw_records_sha256"],
        "response_records": len(historical_records),
        "records_with_output_tokens": len(output_tokens),
        "sum_output_tokens": sum(output_tokens),
        "mean_output_tokens": mean(output_tokens),
        "median_output_tokens": median(output_tokens),
        "minimum_output_tokens": min(output_tokens),
        "maximum_output_tokens": max(output_tokens),
    }
    if output_distribution != reproduced_distribution or len(output_tokens) != EXPECTED_SLOTS:
        raise FullReplicationContractError("historical output distribution does not reproduce")

    estimated_output = value["estimated_output_tokens"]
    expected_estimated_output = {
        "method": "historical_mean_output_tokens * planned_slots",
        "historical_mean_output_tokens": mean(output_tokens),
        "planned_slots": EXPECTED_SLOTS,
        "value": mean(output_tokens) * EXPECTED_SLOTS,
    }
    if estimated_output != expected_estimated_output:
        raise FullReplicationContractError("estimated output-token exposure does not reproduce")
    pricing = value["pricing"]
    expected_pricing = {
        "currency": "USD",
        "input_usd_per_million_tokens": 1.0,
        "output_usd_per_million_tokens": 5.0,
        "cache_enabled": False,
        "batch_api_enabled": False,
    }
    if pricing != expected_pricing:
        raise FullReplicationContractError("cost-gate pricing differs from the registered contract")
    endpoint = value["token_count_endpoint"]
    if endpoint != {
        "provider": "anthropic",
        "operation": "messages.count_tokens",
        "request_count": EXPECTED_UNITS,
        "max_transport_retries_after_initial_request": 0,
        "model_id": EXPECTED_MODEL_ID,
        "model_generations": 0,
        "request_contract": "registered prospective system prompt plus exact unit user prompt",
    }:
        raise FullReplicationContractError("token-count endpoint accounting mismatch")
    if value["model_generations"] != 0:
        raise FullReplicationContractError("pre-execution cost measurement generated model output")
    expected_cost = (
        scheduled_input_total * pricing["input_usd_per_million_tokens"]
        + estimated_output["value"] * pricing["output_usd_per_million_tokens"]
    ) / 1_000_000
    estimate = value.get("estimated_first_attempt_cost_usd")
    if not isinstance(estimate, (int, float)) or isinstance(estimate, bool):
        raise FullReplicationContractError("cost estimate is not numeric")
    if abs(estimate - expected_cost) > 1e-12:
        raise FullReplicationContractError("first-attempt cost estimate does not reproduce")
    if (
        value["operational_budget_usd"] != OPERATIONAL_BUDGET_USD
        or estimate > OPERATIONAL_BUDGET_USD
        or value.get("within_authorized_budget") is not True
    ):
        raise FullReplicationContractError("first-attempt estimate exceeds operational budget")
    return value


def claim_one_shot_lease(
    target: str | Path,
    document: dict,
    arm: dict,
    model_key: str,
    source_binding: dict,
    *,
    synthetic: bool = False,
) -> dict:
    """Atomically consume the only guarded invocation before provider construction."""
    if model_key != EXPECTED_MODEL_KEY:
        raise FullReplicationContractError("one-shot lease refuses a non-Haiku model")
    path = Path(target).resolve() / LEASE_FILENAME
    if path.exists():
        raise FullReplicationContractError(
            "one-shot execution authorization already consumed; second invocation prohibited"
        )
    payload = {
        "lease_schema_version": "agent_arena.one_shot_execution_lease/v1",
        "status": "CONSUMED_FOR_SINGLE_GUARDED_INVOCATION",
        "plan_id": PLAN_ID,
        "specification_fingerprint": document["specification"]["specification_fingerprint"],
        "arm_id": arm["arm_id"],
        "model_key": model_key,
        "model_id": EXPECTED_MODEL_ID,
        "prompt_condition_id": EXPECTED_PROMPT_CONDITION,
        "expected_slots": EXPECTED_SLOTS,
        "guarded_invocations_consumed": 1,
        "manual_restarts_remaining": 0,
        "repository_commit": source_binding.get("commit"),
        "source_state_fingerprint": source_binding.get("source_state_fingerprint"),
        "synthetic_test_only": bool(synthetic),
        "consumed_at": datetime.now(timezone.utc).isoformat(),
    }
    payload["lease_fingerprint"] = cc._fp(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    try:
        descriptor = os.open(path, flags, 0o600)
    except FileExistsError as exc:
        raise FullReplicationContractError(
            "one-shot execution authorization already consumed; second invocation prohibited"
        ) from exc
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
    return {"path": str(path), "record": payload}


def validate_one_shot_lease(path: str | Path, specification_fingerprint: str) -> dict:
    value = json.loads(Path(path).read_text())
    stored = value.get("lease_fingerprint")
    reproduced = cc._fp({k: v for k, v in value.items() if k != "lease_fingerprint"})
    if stored != reproduced:
        raise FullReplicationContractError("one-shot lease fingerprint mismatch")
    if value.get("specification_fingerprint") != specification_fingerprint:
        raise FullReplicationContractError("one-shot lease specification mismatch")
    if value.get("status") != "CONSUMED_FOR_SINGLE_GUARDED_INVOCATION":
        raise FullReplicationContractError("one-shot lease status mismatch")
    return value
