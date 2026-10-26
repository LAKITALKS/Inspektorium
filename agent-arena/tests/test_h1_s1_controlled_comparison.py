"""H1 (Haiku) <-> S1 (Sonnet) controlled-comparison guarantees, plus S0->S1
historical comparability.

Proves that the registered H1 and S1 plans differ *generatively* only in the
foundation-model snapshot: every non-model scientific input and every runtime
request parameter is byte-identical, and S1 reuses the same S0 universe and gold
under the repaired v2 contract (not a verbatim S0 v1 replay).  Read-only over the
resolved specifications; nothing is executed.
"""

from __future__ import annotations

from pathlib import Path

from agent_arena import condition_contract as cc
from agent_arena import full_replication_contract as frc
from agent_arena import phase7a_execution as p7
from agent_arena import runtime_contract as rc

REPO_ROOT = Path(__file__).resolve().parents[1]

HAIKU_MODEL_ID = "claude-haiku-4-5-20251001"
SONNET_MODEL_ID = "claude-sonnet-4-5-20250929"


def _h1() -> dict:
    return cc.resolve_registered_plan(frc.HAIKU.plan_id, REPO_ROOT)["specification"]


def _s1() -> dict:
    return cc.resolve_registered_plan(frc.SONNET.plan_id, REPO_ROOT)["specification"]


# ---------------------------------------------------------------------------
# Exactly one intended generative difference: the model snapshot
# ---------------------------------------------------------------------------

def test_h1_and_s1_share_every_non_model_scientific_input():
    h1, s1 = _h1(), _s1()
    # Identical evaluated universe and gold.
    assert s1["ordered_unit_bindings"] == h1["ordered_unit_bindings"]
    assert s1["ordered_unit_universe_fingerprint"] == h1["ordered_unit_universe_fingerprint"]
    assert s1["selected_unit_manifest_fingerprint"] == h1["selected_unit_manifest_fingerprint"]
    # Identical schedule shape.
    assert s1["n_independent_units"] == h1["n_independent_units"] == 84
    assert s1["n_replications"] == h1["n_replications"] == 5
    assert s1["expected_calls_total"] == h1["expected_calls_total"] == 420
    assert s1["provider_method_invocations_schedule_max"] == (
        h1["provider_method_invocations_schedule_max"]
    )
    assert s1["http_attempts_schedule_max"] == h1["http_attempts_schedule_max"]

    h1_arm, s1_arm = h1["arms"][0], s1["arms"][0]
    # Identical prompt bytes and packaging.
    assert s1_arm["prompt_version"] == h1_arm["prompt_version"]
    assert s1_arm["prompt_condition_id"] == h1_arm["prompt_condition_id"]
    assert s1_arm["system_prompt_sha256"] == h1_arm["system_prompt_sha256"]
    assert s1_arm["packet_descriptor_sha256"] == h1_arm["packet_descriptor_sha256"]
    assert s1_arm["output_contract_sha256"] == h1_arm["output_contract_sha256"]
    assert s1_arm["package_fingerprint"] == h1_arm["package_fingerprint"]


def test_h1_and_s1_differ_only_in_the_foundation_model_snapshot():
    h1, s1 = _h1(), _s1()
    assert h1["model_ids"] == [HAIKU_MODEL_ID]
    assert s1["model_ids"] == [SONNET_MODEL_ID]
    assert h1["model_ids"] != s1["model_ids"]

    h1_runtime = h1["arms"][0]["runtime_contracts"]["haiku"]
    s1_runtime = s1["arms"][0]["runtime_contracts"]["sonnet"]
    # The only differences between the two runtime contracts are model identity.
    model_identity_fields = {
        "runtime_contract_id",
        "model_key",
        "model_family",
        "exact_model_id",
        "model_revision",
        "agent_config_path",
        "agent_config_model",
        "agent_config_sha256",
        "runtime_contract_fingerprint",
    }
    differing = {k for k in h1_runtime if h1_runtime[k] != s1_runtime.get(k)}
    assert differing <= model_identity_fields, differing
    # Everything else (prompt/package identity + request params) is identical.
    assert s1_runtime["prompt_condition_id"] == h1_runtime["prompt_condition_id"]
    assert s1_runtime["system_prompt_sha256"] == h1_runtime["system_prompt_sha256"]
    assert s1_runtime["package_fingerprint"] == h1_runtime["package_fingerprint"]


def test_h1_and_s1_runtime_request_parameters_are_identical_and_frozen():
    h1_runtime = _h1()["arms"][0]["runtime_contracts"]["haiku"]["runtime"]
    s1_runtime = _s1()["arms"][0]["runtime_contracts"]["sonnet"]["runtime"]
    assert s1_runtime == h1_runtime == rc.SHARED_RUNTIME
    # Section-13 request contract, asserted on the Sonnet arm explicitly.
    assert s1_runtime["temperature"] == 0.0
    assert s1_runtime["top_p"] == "OMITTED_FROM_REQUEST"
    assert s1_runtime["seed"] == "UNSUPPORTED"
    assert s1_runtime["max_output_tokens"] == 4096
    assert s1_runtime["request_timeout_seconds"] == 120
    assert s1_runtime["max_transport_retries_after_initial_request"] == 2
    assert s1_runtime["semantic_or_quality_retries"] == "PROHIBITED"


def test_h1_and_s1_retry_contracts_differ_only_in_identifier():
    h1_retry = _h1()["retry_contract"]
    s1_retry = _s1()["retry_contract"]
    assert h1_retry["retry_contract_id"] == "AA-P5B-HAIKU-FULL-RETRY-001"
    assert s1_retry["retry_contract_id"] == "AA-P5B-SONNET-FULL-RETRY-001"
    for field in (
        "provider_method_invocations_schedule_max",
        "http_attempts_schedule_max",
        "sdk_transport_retries_after_initial_per_provider_invocation",
        "semantic_or_quality_retries",
        "guarded_batch_invocations_authorized",
        "manual_restarts_authorized",
    ):
        assert s1_retry[field] == h1_retry[field], field


# ---------------------------------------------------------------------------
# S0 -> S1 comparability: same S0 universe + gold, repaired v2 contract
# ---------------------------------------------------------------------------

def test_s1_reuses_the_same_84_unit_universe_and_gold_as_the_phase7a_truth():
    s1 = _s1()
    canonical = p7.resolve_evaluated_units(REPO_ROOT)
    canonical_bindings = [unit.meta() for unit in canonical]
    assert s1["ordered_unit_bindings"] == canonical_bindings
    # Gold labels are bound per unit and taken from the frozen universe.
    s1_gold = {b["unit_id"]: b["gold_label"] for b in s1["ordered_unit_bindings"]}
    canonical_gold = {b["unit_id"]: b["gold_label"] for b in canonical_bindings}
    assert s1_gold == canonical_gold
    assert len(s1_gold) == 84


def test_s1_uses_the_repaired_v2_contract_not_the_historical_v1_replay():
    s1 = _s1()
    arm = s1["arms"][0]
    assert arm["prompt_condition_id"] == "study_forensics.taxonomy_aligned.v2"
    assert arm["prompt_version"] == "study_forensics_prompt/v2-taxonomy-aligned-phase5a"
    # The S0 reference it compares against used the historical v1 prompt.
    reference = s1["historical_reference"]
    assert reference["prompt_version"] == "study_forensics_prompt/v1-historical-phase7"
    assert reference["model_id"] == SONNET_MODEL_ID
    assert arm["prompt_condition_id"] != "study_forensics.historical.v1"


def test_s1_historical_reference_is_the_frozen_s0_not_h0_or_h1():
    reference = _s1()["historical_reference"]
    assert reference["aggregate_result_set_fingerprint"] == (
        "e1741121c55e522130a0522bb42ed14f7a6a5c0733b333456c1185c067f32fe8"
    )
    # Neither the Haiku historical (H0) nor the repaired Haiku (H1) fingerprint.
    assert reference["aggregate_result_set_fingerprint"] != (
        "b994672ec89bd05f34b67ac2ea24384fd822787a3795febc639b6039136ced8f"
    )
    assert reference["aggregate_result_set_fingerprint"] != (
        "79ddfa509d302dfcaf5464060e3df4f8a25f7e76ecdf7a68a9a409281aca01ec"
    )
