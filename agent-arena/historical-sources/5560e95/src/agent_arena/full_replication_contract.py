"""Registered one-shot contract for the Phase-5B full replications.

This is deliberately separate from the 19-unit paired Phase-5A design.  It binds
the complete historical Phase-7A universe to the repaired prospective prompt and
one exact model snapshot per registered profile.  Two profiles are registered:
``HAIKU`` (claude-haiku-4-5-20251001, historical reference H0) and ``SONNET``
(claude-sonnet-4-5-20250929, historical reference S0).  Both share every
generatively relevant input — the 84-unit universe, gold, the v2 prompt bytes,
the runtime contract, N=5, and the 420-slot schedule — so the same fail-closed
machinery serves both; only the model/plan identity differs.  Historical
responses are reference-only and each profile can only ever validate against its
own historical reference.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median

from agent_arena import condition_contract as cc
from agent_arena import phase7a_execution as p7
from agent_arena import preflight_integrity as pi
from agent_arena import runtime_contract as rc
from agent_arena.runner import STUDY_FORENSICS_PROMPT_VERSION_PROSPECTIVE


# ---------------------------------------------------------------------------
# Shared, model-independent identity (byte-identical across every registered
# full-replication plan: the 84-unit universe, gold, v2 prompt bytes, N, slots,
# the transport-retry ceiling, and the one-shot lease filename).
# ---------------------------------------------------------------------------
LEASE_FILENAME = "execution_authorization_lease.json"
EXPECTED_PROMPT_CONDITION = "study_forensics.taxonomy_aligned.v2"
EXPECTED_PROMPT_SHA256 = "37d91b813bee2b4febb9dba5da66fa8e2bda1e091989785adf6ca5acc132b7ef"
HISTORICAL_PROMPT_VERSION = "study_forensics_prompt/v1-historical-phase7"
EXPECTED_UNITS = 84
EXPECTED_REPETITIONS = 5
EXPECTED_SLOTS = 420


class FullReplicationContractError(cc.ConditionContractError):
    """The registered full-replication contract failed closed."""


@dataclass(frozen=True)
class FullReplicationProfile:
    """Per-plan / per-model identity for one registered full-replication plan.

    Two profiles are registered (``HAIKU``, ``SONNET``).  Everything generatively
    relevant is *shared* between them (unit universe, gold, v2 prompt bytes,
    runtime, retry ceiling, N=5, 420 slots); a profile carries only the
    legitimately model/plan-specific identity so the same fail-closed machinery
    serves both without scientific divergence.  A Sonnet plan therefore can never
    validate against the Haiku historical reference, and vice versa.
    """

    plan_id: str
    comparison_id: str
    arm_id: str
    analytical_condition_id: str
    analysis_contract_id: str
    plan_path: Path
    cost_gate_path: Path
    artifact_namespace: str
    model_key: str
    model_id: str
    model_display_name: str
    retry_contract_id: str
    operational_budget_usd: float
    pricing_retrieval_date: str
    pricing_input_usd_per_million_tokens: float
    pricing_output_usd_per_million_tokens: float
    cross_model_guard_key: str
    consumed_invocation_qa_profile: str
    # None => a consumed plan references its own current specification (no
    # pre-repair invocation exists); a fixed value pins a historical anchor.
    consumed_invocation_specification_fingerprint: str | None

    def governance_constraints(self) -> dict:
        return {
            "historical_responses_reused_as_prospective": False,
            "prompt_only_causal_attribution_permitted": False,
            self.cross_model_guard_key: False,
            "historical_prompt_arm_authorized": False,
            "official_release_writes_authorized": 0,
            "manual_restarts_authorized": 0,
            "one_shot_authorization_required": True,
        }

    def pricing_contract(self) -> dict:
        return {
            "currency": "USD",
            "retrieval_date": self.pricing_retrieval_date,
            "input_usd_per_million_tokens": self.pricing_input_usd_per_million_tokens,
            "output_usd_per_million_tokens": self.pricing_output_usd_per_million_tokens,
            "cache_enabled": False,
            "batch_api_enabled": False,
            "operational_authorization_limit_usd": self.operational_budget_usd,
        }

    def cost_gate_pricing(self) -> dict:
        return {
            "currency": "USD",
            "input_usd_per_million_tokens": self.pricing_input_usd_per_million_tokens,
            "output_usd_per_million_tokens": self.pricing_output_usd_per_million_tokens,
            "cache_enabled": False,
            "batch_api_enabled": False,
        }


HAIKU = FullReplicationProfile(
    plan_id="AA-P5B-HAIKU-FULL-REPLICATION-001",
    comparison_id="AA-P5B-HAIKU-HISTORICAL-REFERENCE-001",
    arm_id="prospective_taxonomy_aligned_full_haiku",
    analytical_condition_id="AA-P5B-COND-HAIKU-TAXONOMY-ALIGNED-FULL-001",
    analysis_contract_id="AA-P5B-FULL-REPLICATION-ANALYSIS-001",
    plan_path=Path("analysis/phase5b_haiku_full_replication/execution_plan.json"),
    cost_gate_path=Path(
        "analysis/phase5b_haiku_full_replication/pre_execution_cost_estimate.json"
    ),
    artifact_namespace="analysis/phase5b_haiku_full_replication/run",
    model_key="haiku",
    model_id="claude-haiku-4-5-20251001",
    model_display_name="Haiku",
    retry_contract_id="AA-P5B-HAIKU-FULL-RETRY-001",
    operational_budget_usd=6.0,
    pricing_retrieval_date="2026-08-29",
    pricing_input_usd_per_million_tokens=1.0,
    pricing_output_usd_per_million_tokens=5.0,
    cross_model_guard_key="sonnet_authorized",
    consumed_invocation_qa_profile="phase5b-full-replication-production-qa/v1",
    consumed_invocation_specification_fingerprint=(
        "a00c4eda7b90bd715a0f172c2401fcd47fcc2aacb513dbfd355e60ab2719729c"
    ),
)

SONNET = FullReplicationProfile(
    plan_id="AA-P5B-SONNET-FULL-REPLICATION-001",
    comparison_id="AA-P5B-SONNET-HISTORICAL-REFERENCE-001",
    arm_id="prospective_taxonomy_aligned_full_sonnet",
    analytical_condition_id="AA-P5B-COND-SONNET-TAXONOMY-ALIGNED-FULL-001",
    analysis_contract_id="AA-P5B-SONNET-FULL-REPLICATION-ANALYSIS-001",
    plan_path=Path("analysis/phase5b_sonnet_full_replication/execution_plan.json"),
    cost_gate_path=Path(
        "analysis/phase5b_sonnet_full_replication/pre_execution_cost_estimate.json"
    ),
    artifact_namespace="analysis/phase5b_sonnet_full_replication/run",
    model_key="sonnet",
    model_id="claude-sonnet-4-5-20250929",
    model_display_name="Sonnet",
    retry_contract_id="AA-P5B-SONNET-FULL-RETRY-001",
    operational_budget_usd=18.0,
    pricing_retrieval_date="2026-09-12",
    pricing_input_usd_per_million_tokens=3.0,
    pricing_output_usd_per_million_tokens=15.0,
    cross_model_guard_key="haiku_authorized",
    consumed_invocation_qa_profile="phase5b-full-replication-production-qa/v2",
    consumed_invocation_specification_fingerprint=None,
)

_PROFILES = {HAIKU.plan_id: HAIKU, SONNET.plan_id: SONNET}
FULL_REPLICATION_PLAN_IDS = frozenset(_PROFILES)


def profile_for_plan_id(plan_id) -> FullReplicationProfile:
    """Resolve the registered full-replication profile for a plan identifier."""
    try:
        return _PROFILES[plan_id]
    except KeyError as exc:
        raise FullReplicationContractError(
            f"unknown full-replication plan identity: {plan_id!r}"
        ) from exc


def _profile_for_document(document: dict) -> FullReplicationProfile:
    return profile_for_plan_id((document.get("specification") or {}).get("plan_id"))


# Backward-compatible module-level aliases. The Haiku profile is the historical
# default so existing callers and tests that read ``frc.PLAN_ID`` etc. are
# unchanged; new callers pass a profile-bearing plan/document instead.
PLAN_ID = HAIKU.plan_id
COMPARISON_ID = HAIKU.comparison_id
ARM_ID = HAIKU.arm_id
ANALYTICAL_CONDITION_ID = HAIKU.analytical_condition_id
ANALYSIS_CONTRACT_ID = HAIKU.analysis_contract_id
PLAN_PATH = HAIKU.plan_path
COST_GATE_PATH = HAIKU.cost_gate_path
ARTIFACT_NAMESPACE = HAIKU.artifact_namespace
EXPECTED_MODEL_KEY = HAIKU.model_key
EXPECTED_MODEL_ID = HAIKU.model_id
OPERATIONAL_BUDGET_USD = HAIKU.operational_budget_usd


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


def _historical_reference_errors(
    reference: dict, root: Path, profile: FullReplicationProfile
) -> list[str]:
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
    if reference["model_id"] != profile.model_id:
        errors.append(
            f"historical reference model differs from exact {profile.model_display_name} snapshot"
        )
    if reference["prompt_version"] != HISTORICAL_PROMPT_VERSION:
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


def _retry_contract(profile: FullReplicationProfile) -> dict:
    """One guarded pass; only the SDK's two transport retries may reissue HTTP."""
    http_attempts = 1 + rc.SHARED_RUNTIME["max_transport_retries_after_initial_request"]
    return {
        "retry_contract_schema_version": "agent_arena.full_replication_retry_contract/v1",
        "retry_contract_id": profile.retry_contract_id,
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
    profile = profile_for_plan_id(definition["plan_id"])
    if definition["comparison_id"] != profile.comparison_id:
        raise FullReplicationContractError("full-replication plan/comparison identity mismatch")
    if definition["scientific_design"] != "historical_reference_replication_not_randomized_ab":
        raise FullReplicationContractError("scientific design is not the registered replication")
    if definition["model_keys"] != [profile.model_key]:
        raise FullReplicationContractError(
            f"full replication must contain {profile.model_display_name} only"
        )
    if definition["n_replications"] != EXPECTED_REPETITIONS:
        raise FullReplicationContractError("full replication must use five repetitions")
    if definition["execution_mode"] != "independent_model_adjudication":
        raise FullReplicationContractError("full replication execution mode mismatch")
    if definition["qa_profile"] != pi.FULL_REPLICATION_QA_VERSION:
        raise FullReplicationContractError("full replication QA profile mismatch")
    if definition["retry_policy"] != _retry_contract(profile):
        raise FullReplicationContractError("full replication retry contract mismatch")
    governance = definition["governance_constraints"]
    if governance != profile.governance_constraints():
        raise FullReplicationContractError("full replication governance constraints mismatch")
    if definition["pricing_contract"] != profile.pricing_contract():
        raise FullReplicationContractError("full replication pricing contract mismatch")

    units = p7.resolve_evaluated_units(root)
    ordered_ids = [unit.unit_id for unit in units]
    if len(units) != EXPECTED_UNITS or len(set(ordered_ids)) != EXPECTED_UNITS:
        raise FullReplicationContractError("canonical Phase-7A unit universe is not 84 unique units")
    if definition["ordered_unit_ids"] != ordered_ids:
        raise FullReplicationContractError("ordered 84-unit universe differs from Phase-7A truth")
    historical_errors = _historical_reference_errors(
        definition["historical_reference"], root, profile
    )
    if historical_errors:
        raise FullReplicationContractError("; ".join(historical_errors))

    arm_definition = definition["arm"]
    if arm_definition != {
        "arm_id": profile.arm_id,
        "analytical_condition_id": profile.analytical_condition_id,
        "prompt_version": STUDY_FORENSICS_PROMPT_VERSION_PROSPECTIVE,
        "prompt_condition_id": EXPECTED_PROMPT_CONDITION,
        "system_prompt_sha256": EXPECTED_PROMPT_SHA256,
        "artifact_namespace": profile.artifact_namespace,
    }:
        raise FullReplicationContractError("full replication arm identity mismatch")

    package = cc.package_contract(STUDY_FORENSICS_PROMPT_VERSION_PROSPECTIVE)
    if package["prompt_condition_id"] != EXPECTED_PROMPT_CONDITION:
        raise FullReplicationContractError("prospective prompt condition drift")
    if package["system_prompt_sha256"] != EXPECTED_PROMPT_SHA256:
        raise FullReplicationContractError("prospective prompt bytes drift")
    runtime = cc.condition_runtime_contract(
        profile.model_key, STUDY_FORENSICS_PROMPT_VERSION_PROSPECTIVE, root
    )
    if runtime["exact_model_id"] != profile.model_id:
        raise FullReplicationContractError(
            f"exact {profile.model_display_name} runtime identity drift"
        )
    unit_bindings = [unit.meta() for unit in units]
    execution_manifest = {
        "execution_manifest_schema_version": "agent_arena.full_replication_manifest/v1",
        "plan_id": profile.plan_id,
        "arm_id": profile.arm_id,
        "model_id": profile.model_id,
        "prompt_condition_id": EXPECTED_PROMPT_CONDITION,
        "ordered_unit_bindings": unit_bindings,
        "n_evaluated_units": EXPECTED_UNITS,
        "n_replications": EXPECTED_REPETITIONS,
        "data_role": "historically_exposed_phase7_class_b_full_replication",
        "holdout_claim": False,
        "historical_responses_are_reference_only": True,
        "execution_mode": definition["execution_mode"],
        "artifact_namespace": profile.artifact_namespace,
    }
    execution_manifest["execution_manifest_fingerprint"] = cc._fp(execution_manifest)
    slots = [
        [profile.model_id, unit.unit_id, run_index]
        for unit in units
        for run_index in range(EXPECTED_REPETITIONS)
    ]
    call_plan = {
        "call_plan_schema_version": "agent_arena.full_replication_call_plan/v1",
        "plan_id": profile.plan_id,
        "arm_id": profile.arm_id,
        "model_ids": [profile.model_id],
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
            profile.model_id: runtime["runtime_contract_fingerprint"]
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
        "runtime_contracts": {profile.model_key: runtime},
        "runtime_contract_fingerprints": {
            profile.model_id: runtime["runtime_contract_fingerprint"]
        },
        "execution_manifest": execution_manifest,
        "call_plan": call_plan,
    }
    arm["arm_specification_fingerprint"] = cc._fp(arm)
    specification = {
        "specification_schema_version": "agent_arena.full_replication_specification/v1",
        "plan_id": profile.plan_id,
        "comparison_id": profile.comparison_id,
        "scientific_design": definition["scientific_design"],
        "research_question": definition["research_question"],
        "model_keys": [profile.model_key],
        "model_ids": [profile.model_id],
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
            "analysis_contract_id": profile.analysis_contract_id,
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
        "cost_gate_path": profile.cost_gate_path.as_posix(),
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
    try:
        profile = _profile_for_document(document)
    except FullReplicationContractError as exc:
        return [str(exc)]
    spec_fp = specification.get("specification_fingerprint")
    not_executed_progress = {
        "status": cc.PROGRESS_NOT_EXECUTED,
        "completed_calls": 0,
        "arm_progress": {profile.arm_id: cc.PROGRESS_NOT_EXECUTED},
    }
    if authorization.get("specification_fingerprint") != spec_fp:
        errors.append("full replication authorization fingerprint mismatch")
    status = authorization.get("status")
    if status == cc.AUTH_REAL:
        expected = {
            "status": cc.AUTH_REAL,
            "specification_fingerprint": spec_fp,
            "authorization_source": "tracked_governance_approval",
            "authorized_budget_calls": EXPECTED_SLOTS,
            "authorized_model_keys": [profile.model_key],
            "authorized_prompt_condition_ids": [EXPECTED_PROMPT_CONDITION],
            "guarded_batch_invocations_authorized": 1,
            "manual_restarts_authorized": 0,
            "operational_budget_usd": profile.operational_budget_usd,
            "authorization_mode": "ONE_SHOT_LEASE_BEFORE_PROVIDER_CONSTRUCTION",
        }
        if authorization != expected:
            errors.append("full replication real authorization scope mismatch")
        if progress != not_executed_progress:
            errors.append("authorized full replication must begin NOT_EXECUTED")
    elif status == cc.AUTH_NOT_AUTHORIZED:
        expected = {
            "status": cc.AUTH_NOT_AUTHORIZED,
            "specification_fingerprint": spec_fp,
            "authorization_source": "NO_PRODUCTION_APPROVAL_COMMITTED",
            "authorized_budget_calls": 0,
        }
        if authorization != expected:
            errors.append("full replication unauthorized audit state mismatch")
        if progress != not_executed_progress:
            errors.append("unauthorized full replication must begin NOT_EXECUTED")
    elif status == cc.AUTH_SYNTHETIC_TEST and allow_synthetic_test:
        expected = {
            "status": cc.AUTH_SYNTHETIC_TEST,
            "specification_fingerprint": spec_fp,
            "authorization_source": "private_test_seam",
            "authorized_budget_calls": EXPECTED_SLOTS,
        }
        if authorization != expected:
            errors.append("full replication synthetic authorization scope mismatch")
        if progress != not_executed_progress:
            errors.append("synthetic full replication must begin NOT_EXECUTED")
    elif status == cc.AUTH_CONSUMED:
        consumed_spec_fp = profile.consumed_invocation_specification_fingerprint
        if consumed_spec_fp is None:
            # No pre-repair invocation exists; a consumed plan references its own spec.
            consumed_spec_fp = spec_fp
        expected = {
            "status": cc.AUTH_CONSUMED,
            "specification_fingerprint": spec_fp,
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
            "consumed_invocation_specification_fingerprint": consumed_spec_fp,
            "consumed_invocation_qa_profile": profile.consumed_invocation_qa_profile,
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
    profile = _profile_for_document(document)
    try:
        raw = cc._read_authenticated_plan_artifact(root, profile.cost_gate_path)
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
    if value["plan_id"] != profile.plan_id:
        raise FullReplicationContractError("cost gate refers to another plan")
    if value["specification_fingerprint"] != document["specification"][
        "specification_fingerprint"
    ]:
        raise FullReplicationContractError("cost gate refers to another specification")
    if value["model_id"] != profile.model_id or value["prompt_condition_id"] != EXPECTED_PROMPT_CONDITION:
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
    if pricing != profile.cost_gate_pricing():
        raise FullReplicationContractError("cost-gate pricing differs from the registered contract")
    endpoint = value["token_count_endpoint"]
    if endpoint != {
        "provider": "anthropic",
        "operation": "messages.count_tokens",
        "request_count": EXPECTED_UNITS,
        "max_transport_retries_after_initial_request": 0,
        "model_id": profile.model_id,
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
        value["operational_budget_usd"] != profile.operational_budget_usd
        or estimate > profile.operational_budget_usd
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
    profile = _profile_for_document(document)
    if model_key != profile.model_key:
        raise FullReplicationContractError(
            f"one-shot lease refuses a non-{profile.model_display_name} model"
        )
    path = Path(target).resolve() / LEASE_FILENAME
    if path.exists():
        raise FullReplicationContractError(
            "one-shot execution authorization already consumed; second invocation prohibited"
        )
    payload = {
        "lease_schema_version": "agent_arena.one_shot_execution_lease/v1",
        "status": "CONSUMED_FOR_SINGLE_GUARDED_INVOCATION",
        "plan_id": profile.plan_id,
        "specification_fingerprint": document["specification"]["specification_fingerprint"],
        "arm_id": arm["arm_id"],
        "model_key": model_key,
        "model_id": profile.model_id,
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
