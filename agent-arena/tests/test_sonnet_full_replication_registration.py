"""Registration + scientific-binding tests for the Phase-5B Sonnet (S1) plan.

These exercise the newly registered ``AA-P5B-SONNET-FULL-REPLICATION-001`` plan
through the same fail-closed machinery as the Haiku H1 plan.  The delivered plan
is NOT_AUTHORIZED, so nothing here can construct a provider or spend a call.  New
Sonnet coverage lives in this separate file (outside the pinned canonical-QA test
paths) so it cannot shift the immutable Phase-5B Haiku specification fingerprint.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_arena import condition_contract as cc
from agent_arena import full_replication_contract as frc
from agent_arena import runtime_contract as rc
from agent_arena.runner import STUDY_FORENSICS_PROMPT_VERSION_PROSPECTIVE as V2

REPO_ROOT = Path(__file__).resolve().parents[1]

# Frozen reference identities (verified from the repository, not trusted blindly).
S0_AGGREGATE_FINGERPRINT = (
    "e1741121c55e522130a0522bb42ed14f7a6a5c0733b333456c1185c067f32fe8"
)
H1_AGGREGATE_FINGERPRINT = (
    "79ddfa509d302dfcaf5464060e3df4f8a25f7e76ecdf7a68a9a409281aca01ec"
)
H0_AGGREGATE_FINGERPRINT = (
    "b994672ec89bd05f34b67ac2ea24384fd822787a3795febc639b6039136ced8f"
)
SONNET_MODEL_ID = "claude-sonnet-4-5-20250929"
HAIKU_MODEL_ID = "claude-haiku-4-5-20251001"


def _sonnet_plan() -> dict:
    return cc.resolve_registered_plan(frc.SONNET.plan_id, REPO_ROOT)


def _haiku_plan() -> dict:
    return cc.resolve_registered_plan(frc.HAIKU.plan_id, REPO_ROOT)


def _sonnet_definition() -> dict:
    return json.loads((REPO_ROOT / frc.SONNET.plan_path).read_text())["definition"]


# ---------------------------------------------------------------------------
# Registration + schedule/model/prompt binding
# ---------------------------------------------------------------------------

def test_sonnet_plan_is_registered_and_resolves():
    assert frc.SONNET.plan_id in cc._REGISTERED_PLAN_PATHS
    assert frc.SONNET.plan_id in frc.FULL_REPLICATION_PLAN_IDS
    document = _sonnet_plan()
    assert document["specification"]["plan_id"] == frc.SONNET.plan_id


def test_sonnet_specification_binds_exact_schedule_model_and_prompt():
    spec = _sonnet_plan()["specification"]
    arm = spec["arms"][0]
    assert spec["model_keys"] == ["sonnet"]
    assert spec["model_ids"] == [SONNET_MODEL_ID]
    assert spec["n_independent_units"] == 84
    assert spec["n_replications"] == 5
    assert spec["expected_calls_total"] == 420
    assert spec["provider_method_invocations_schedule_max"] == 420
    assert spec["http_attempts_schedule_max"] == 1260
    assert arm["arm_id"] == "prospective_taxonomy_aligned_full_sonnet"
    assert arm["prompt_version"] == V2
    assert arm["prompt_condition_id"] == "study_forensics.taxonomy_aligned.v2"
    assert arm["system_prompt_sha256"] == frc.EXPECTED_PROMPT_SHA256
    assert arm["artifact_namespace"] == "analysis/phase5b_sonnet_full_replication/run"


def test_sonnet_runtime_resolves_to_the_exact_sonnet_snapshot():
    arm = _sonnet_plan()["specification"]["arms"][0]
    runtime = arm["runtime_contracts"]["sonnet"]
    assert runtime["exact_model_id"] == SONNET_MODEL_ID
    assert runtime["model_key"] == "sonnet"
    assert runtime["prompt_condition_id"] == "study_forensics.taxonomy_aligned.v2"


def test_sonnet_pricing_and_budget_are_registered_and_not_haiku_pricing():
    spec = _sonnet_plan()["specification"]
    pricing = spec["pricing_contract"]
    assert pricing["input_usd_per_million_tokens"] == 3.0
    assert pricing["output_usd_per_million_tokens"] == 15.0
    assert pricing["operational_authorization_limit_usd"] == 18.0
    # Sonnet must not silently inherit Haiku's $1/$5 table or $6 budget.
    assert pricing["input_usd_per_million_tokens"] != 1.0
    assert frc.SONNET.operational_budget_usd != frc.HAIKU.operational_budget_usd


# ---------------------------------------------------------------------------
# The Sonnet plan binds the frozen S0 historical reference, never H0
# ---------------------------------------------------------------------------

def test_sonnet_binds_frozen_s0_reference_and_never_the_haiku_h0_reference():
    reference = _sonnet_plan()["specification"]["historical_reference"]
    assert reference["model_id"] == SONNET_MODEL_ID
    assert reference["prompt_version"] == "study_forensics_prompt/v1-historical-phase7"
    assert reference["aggregate_result_set_fingerprint"] == S0_AGGREGATE_FINGERPRINT
    assert reference["raw_records_path"] == (
        "analysis/phase7a_execution/sonnet/raw/sonnet_raw_records.jsonl"
    )
    # Categorically not the Haiku H0 reference.
    assert reference["model_id"] != HAIKU_MODEL_ID
    assert reference["aggregate_result_set_fingerprint"] != H0_AGGREGATE_FINGERPRINT
    assert "haiku" not in reference["raw_records_path"]


def test_sonnet_historical_reference_hashes_reproduce_from_frozen_s0_artifacts():
    reference = _sonnet_plan()["specification"]["historical_reference"]
    for path_field, hash_field in (
        ("raw_records_path", "raw_records_sha256"),
        ("raw_freeze_path", "raw_freeze_sha256"),
        ("analysis_path", "analysis_sha256"),
    ):
        actual = rc._sha256_hex((REPO_ROOT / reference[path_field]).read_bytes())
        assert actual == reference[hash_field], path_field


# ---------------------------------------------------------------------------
# Delivered state: registered but NOT spendable
# ---------------------------------------------------------------------------

def test_sonnet_delivered_state_is_not_authorized_and_not_spendable():
    document = _sonnet_plan()
    authorization = document["authorization"]
    # The delivered plan rests at NOT_AUTHORIZED before a run and at CONSUMED
    # after the one-shot run; both are legitimate non-executable resting states.
    assert authorization["status"] in {cc.AUTH_NOT_AUTHORIZED, cc.AUTH_CONSUMED}
    assert authorization["authorized_budget_calls"] == 0
    assert authorization.get("authorized_model_keys", []) == []
    assert document["progress"]["status"] in {
        cc.PROGRESS_NOT_EXECUTED, cc.PROGRESS_COMPLETE, cc.PROGRESS_PARTIAL_INCOMPLETE
    }
    # Production execution is refused for the live plan in either resting state.
    assert cc.production_authorization_errors(document, REPO_ROOT)


def test_sonnet_plan_document_validates_clean_in_the_delivered_state():
    document = _sonnet_plan()
    assert cc.validate_plan_document(document, REPO_ROOT) == []
    assert frc.validate_document_state(document) == []


# ---------------------------------------------------------------------------
# Tamper checks: the Sonnet contract fails closed
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda d: d.update(model_keys=["haiku"]), "Sonnet only"),
        (lambda d: d["arm"].update(prompt_condition_id="wrong"), "arm identity"),
        (lambda d: d["arm"].update(system_prompt_sha256="0" * 64), "arm identity"),
        (lambda d: d["ordered_unit_ids"].pop(), "ordered 84-unit universe"),
        (
            lambda d: d["historical_reference"].update(raw_records_sha256="0" * 64),
            "hash mismatch",
        ),
        (
            lambda d: d["historical_reference"].update(model_id=HAIKU_MODEL_ID),
            "exact Sonnet snapshot",
        ),
    ],
)
def test_sonnet_contract_tampering_fails_closed(mutation, message):
    definition = copy.deepcopy(_sonnet_definition())
    mutation(definition)
    with pytest.raises(frc.FullReplicationContractError, match=message):
        frc.build_specification(definition, REPO_ROOT)


def test_sonnet_definition_rejected_under_the_haiku_profile_identity():
    """A Sonnet definition carrying the Haiku plan_id cannot reproduce a spec."""
    definition = copy.deepcopy(_sonnet_definition())
    definition["plan_id"] = frc.HAIKU.plan_id
    with pytest.raises(frc.FullReplicationContractError):
        frc.build_specification(definition, REPO_ROOT)


# ---------------------------------------------------------------------------
# CLI entrypoint is registered (kept fail-closed by the NOT_AUTHORIZED plan)
# ---------------------------------------------------------------------------

def test_sonnet_full_replication_cli_command_is_registered():
    from agent_arena.cli import cli

    assert "phase5b-sonnet-full-replication" in cli.commands


# ---------------------------------------------------------------------------
# Frozen reference cells are unchanged by this registration
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("path", "fingerprint"),
    [
        ("analysis/phase7a_execution/sonnet/sonnet_raw_result_freeze.json", S0_AGGREGATE_FINGERPRINT),
        (
            "analysis/phase5b_haiku_full_replication/run/haiku/haiku_raw_result_freeze.json",
            H1_AGGREGATE_FINGERPRINT,
        ),
        ("analysis/phase7a_execution/haiku/haiku_raw_result_freeze.json", H0_AGGREGATE_FINGERPRINT),
    ],
)
def test_frozen_reference_cells_unchanged(path, fingerprint):
    freeze = json.loads((REPO_ROOT / path).read_text())
    assert freeze["aggregate_result_set_fingerprint"] == fingerprint
