"""Isolated authorization-state invariant tests for the Phase-5B Sonnet (S1) plan.

Mirrors ``tests/test_authorization_state_invariant.py`` for the Sonnet profile and
walks Section-16 states A-H.  Every authorized object lives only inside these
tests; proving the contract accepts a legitimate Sonnet authorization can never
make the live (NOT_AUTHORIZED) plan spendable, and no test constructs a provider
or reaches the generation path.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_arena import condition_contract as cc
from agent_arena import full_replication_contract as frc
from agent_arena import preflight_integrity as pi
from agent_arena.phase7a_real_run import (
    ConditionAuthorizationError,
    _run_registered_condition,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SONNET_PLAN_PATH = REPO_ROOT / frc.SONNET.plan_path
HAIKU_PLAN_PATH = REPO_ROOT / frc.HAIKU.plan_path


# ---------------------------------------------------------------------------
# In-memory document builders (never mutate the tracked plan)
# ---------------------------------------------------------------------------

def _document(plan_path: Path) -> dict:
    artifact = json.loads(plan_path.read_text())
    specification = frc.build_specification(artifact["definition"], REPO_ROOT)
    return {
        "plan_document_schema_version": artifact["plan_document_schema_version"],
        "definition": artifact["definition"],
        "specification": specification,
        "authorization": copy.deepcopy(artifact["authorization"]),
        "progress": copy.deepcopy(artifact["progress"]),
    }


def _sonnet_document() -> dict:
    return _document(SONNET_PLAN_PATH)


def _not_executed_progress() -> dict:
    return {
        "status": cc.PROGRESS_NOT_EXECUTED,
        "completed_calls": 0,
        "arm_progress": {frc.SONNET.arm_id: cc.PROGRESS_NOT_EXECUTED},
    }


def _authorized_authorization(spec_fp: str) -> dict:
    """State B scope: bounded, Sonnet-only, one guarded batch, held only in memory."""
    return {
        "status": cc.AUTH_REAL,
        "specification_fingerprint": spec_fp,
        "authorization_source": "tracked_governance_approval",
        "authorized_budget_calls": frc.EXPECTED_SLOTS,
        "authorized_model_keys": [frc.SONNET.model_key],
        "authorized_prompt_condition_ids": [frc.EXPECTED_PROMPT_CONDITION],
        "guarded_batch_invocations_authorized": 1,
        "manual_restarts_authorized": 0,
        "operational_budget_usd": frc.SONNET.operational_budget_usd,
        "authorization_mode": "ONE_SHOT_LEASE_BEFORE_PROVIDER_CONSTRUCTION",
    }


def _consumed_authorization(spec_fp: str) -> dict:
    """State H scope: spent one-shot, zero remaining budget, own-spec audit anchor."""
    return {
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
        "consumed_invocation_specification_fingerprint": spec_fp,
        "consumed_invocation_qa_profile": "phase5b-full-replication-production-qa/v2",
    }


def _authorized_document() -> dict:
    document = _sonnet_document()
    document["authorization"] = _authorized_authorization(
        document["specification"]["specification_fingerprint"]
    )
    document["progress"] = _not_executed_progress()
    return document


def _consumed_document() -> dict:
    document = _sonnet_document()
    document["authorization"] = _consumed_authorization(
        document["specification"]["specification_fingerprint"]
    )
    document["progress"] = {
        "status": cc.PROGRESS_PARTIAL_INCOMPLETE,
        "completed_calls": 0,
        "arm_progress": {frc.SONNET.arm_id: cc.PROGRESS_PARTIAL_INCOMPLETE},
        "stop_stage": "fresh_canonical_qa",
        "provider_constructions": 0,
        "terminal_attempts": 0,
    }
    return document


def _synthetic_document(plan_path: Path) -> dict:
    document = cc.synthetic_authorized_copy(
        _document(plan_path), expected_calls=frc.EXPECTED_SLOTS
    )
    artifact = json.loads(plan_path.read_text())
    arm_id = artifact["definition"]["arm"]["arm_id"]
    document["progress"] = {
        "status": cc.PROGRESS_NOT_EXECUTED,
        "completed_calls": 0,
        "arm_progress": {arm_id: cc.PROGRESS_NOT_EXECUTED},
    }
    return document


def _source_binding() -> dict:
    return {
        "valid": True,
        "errors": [],
        "repository_root": str(REPO_ROOT),
        "repository_identity": "repository-id",
        "commit": "a" * 40,
        "tree": "b" * 40,
        "tracked_source_fingerprint": "c" * 64,
        "tracked_config_fingerprint": "d" * 64,
        "python_executable": "/synthetic/python",
        "python_version": "3.11.synthetic",
        "python_prefix": "/synthetic",
        "python_base_prefix": "/synthetic-base",
        "python_environment_fingerprint": "e" * 64,
        "package_origins": {"agent_arena": str(REPO_ROOT / "src/agent_arena/__init__.py")},
        "source_state_fingerprint": "f" * 64,
    }


class _CountingProviderBuilder:
    def __init__(self):
        self.constructions = 0

    def __call__(self, model_key: str):  # pragma: no cover - must never be reached
        self.constructions += 1
        raise AssertionError("provider construction is forbidden in this test")


# ---------------------------------------------------------------------------
# State A -- no current authorization
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "status", [cc.AUTH_NOT_AUTHORIZED, cc.AUTH_CONSUMED, "SOME_UNKNOWN_STATE"]
)
def test_state_a_without_a_current_authorization_nothing_is_spendable(status):
    document = _sonnet_document()
    fingerprint = document["specification"]["specification_fingerprint"]
    if status == cc.AUTH_CONSUMED:
        document["authorization"] = _consumed_authorization(fingerprint)
        document["progress"] = _consumed_document()["progress"]
    else:
        document["authorization"] = {
            "status": status,
            "specification_fingerprint": fingerprint,
            "authorization_source": "NO_PRODUCTION_APPROVAL_COMMITTED",
            "authorized_budget_calls": 0,
        }
        document["progress"] = _not_executed_progress()
    assert document["authorization"]["authorized_budget_calls"] == 0
    assert document["authorization"].get("authorized_model_keys", []) == []
    assert cc.production_authorization_errors(document, REPO_ROOT)


# ---------------------------------------------------------------------------
# State B -- a legitimate Sonnet authorization must be accepted
# ---------------------------------------------------------------------------

def test_state_b_valid_isolated_sonnet_authorization_is_accepted():
    document = _authorized_document()
    assert frc.validate_document_state(document) == []
    assert cc.validate_plan_document(document, REPO_ROOT) == []
    assert cc.production_authorization_errors(document, REPO_ROOT) == []
    authorization = document["authorization"]
    assert authorization["authorized_model_keys"] == ["sonnet"]
    assert authorization["authorized_budget_calls"] == 420
    assert authorization["operational_budget_usd"] == 18.0


def test_state_b_authorization_does_not_alter_the_scientific_specification():
    baseline = _sonnet_document()["specification"]
    authorized = _authorized_document()["specification"]
    assert authorized["specification_fingerprint"] == baseline["specification_fingerprint"]
    assert authorized["model_ids"] == ["claude-sonnet-4-5-20250929"]
    assert authorized["n_independent_units"] == 84
    assert authorized["expected_calls_total"] == 420


def test_state_b_building_an_authorized_object_leaves_the_live_plan_unauthorized():
    before = json.loads(SONNET_PLAN_PATH.read_text())
    _authorized_document()
    after = json.loads(SONNET_PLAN_PATH.read_text())
    assert before == after
    live = cc.resolve_registered_plan(frc.SONNET.plan_id, REPO_ROOT)
    # Before a run the live plan rests at NOT_AUTHORIZED; after the one-shot run
    # it rests at CONSUMED. Both are legitimate, non-executable resting states
    # (fail-closed set: never AUTH_REAL, never spendable).
    assert live["authorization"]["status"] in {cc.AUTH_NOT_AUTHORIZED, cc.AUTH_CONSUMED}
    assert live["authorization"]["authorized_budget_calls"] == 0
    assert cc.production_authorization_errors(live, REPO_ROOT)


# ---------------------------------------------------------------------------
# State C -- another model in the authorization scope
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("model_keys", [["haiku"], ["opus"], ["haiku", "sonnet"], []])
def test_state_c_authorization_for_another_model_fails_closed(model_keys):
    document = _authorized_document()
    document["authorization"]["authorized_model_keys"] = model_keys
    assert frc.validate_document_state(document)
    assert cc.production_authorization_errors(document, REPO_ROOT)


# ---------------------------------------------------------------------------
# State D -- Haiku used with the Sonnet plan
# ---------------------------------------------------------------------------

def test_state_d_haiku_is_refused_against_the_sonnet_plan(tmp_path):
    builder = _CountingProviderBuilder()
    with pytest.raises(ConditionAuthorizationError, match="outside the registered plan"):
        _run_registered_condition(
            frc.SONNET.plan_id,
            frc.SONNET.arm_id,
            "haiku",
            repo_root=REPO_ROOT,
            _synthetic_test=True,
            _plan_resolver=lambda _p, _r: _synthetic_document(SONNET_PLAN_PATH),
            _provider_builder=builder,
            _output_dir=tmp_path,
        )
    assert builder.constructions == 0


# ---------------------------------------------------------------------------
# State E -- Sonnet used with the Haiku plan
# ---------------------------------------------------------------------------

def test_state_e_sonnet_is_refused_against_the_haiku_plan(tmp_path):
    builder = _CountingProviderBuilder()
    with pytest.raises(ConditionAuthorizationError, match="outside the registered plan"):
        _run_registered_condition(
            frc.HAIKU.plan_id,
            frc.HAIKU.arm_id,
            "sonnet",
            repo_root=REPO_ROOT,
            _synthetic_test=True,
            _plan_resolver=lambda _p, _r: _synthetic_document(HAIKU_PLAN_PATH),
            _provider_builder=builder,
            _output_dir=tmp_path,
        )
    assert builder.constructions == 0


# ---------------------------------------------------------------------------
# State F -- over scope
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("authorized_budget_calls", frc.EXPECTED_SLOTS + 1),
        ("authorized_budget_calls", frc.EXPECTED_SLOTS * 2),
        ("operational_budget_usd", frc.SONNET.operational_budget_usd + 1.0),
        ("guarded_batch_invocations_authorized", 2),
        ("manual_restarts_authorized", 1),
        ("authorized_prompt_condition_ids", ["study_forensics.historical.v1"]),
        ("authorization_source", "self_approved"),
        ("authorization_mode", "UNBOUNDED"),
    ],
)
def test_state_f_over_scope_authorization_fails_closed(field, value):
    document = _authorized_document()
    document["authorization"][field] = value
    assert frc.validate_document_state(document)
    assert cc.production_authorization_errors(document, REPO_ROOT)


# ---------------------------------------------------------------------------
# State G -- source/environment binding still enforced under a valid authorization
# ---------------------------------------------------------------------------

def test_state_g_valid_authorization_does_not_bypass_source_environment_binding(tmp_path):
    builder = _CountingProviderBuilder()
    invalid_source = _source_binding()
    invalid_source["valid"] = False
    invalid_source["errors"] = ["tracked source tree is dirty"]
    with pytest.raises(ConditionAuthorizationError, match="source state invalid"):
        _run_registered_condition(
            frc.SONNET.plan_id,
            frc.SONNET.arm_id,
            frc.SONNET.model_key,
            repo_root=REPO_ROOT,
            _synthetic_test=True,
            _plan_resolver=lambda _p, _r: _synthetic_document(SONNET_PLAN_PATH),
            _source_inspector=lambda _r: copy.deepcopy(invalid_source),
            _qa_executor=lambda _r, _s: {"synthetic": True},
            _qa_validator=lambda _q, _s: (pi.QA_PASSED, []),
            _credential_checker=lambda: {"available": True, "reason": "synthetic"},
            _provider_builder=builder,
            _output_dir=tmp_path,
        )
    assert builder.constructions == 0


def test_state_g_valid_authorization_does_not_bypass_missing_credential(tmp_path):
    builder = _CountingProviderBuilder()
    with pytest.raises(ConditionAuthorizationError, match="provider unavailable"):
        _run_registered_condition(
            frc.SONNET.plan_id,
            frc.SONNET.arm_id,
            frc.SONNET.model_key,
            repo_root=REPO_ROOT,
            _synthetic_test=True,
            _plan_resolver=lambda _p, _r: _synthetic_document(SONNET_PLAN_PATH),
            _source_inspector=lambda _r: _source_binding(),
            _qa_executor=lambda _r, _s: {"synthetic": True},
            _qa_validator=lambda _q, _s: (pi.QA_PASSED, []),
            _credential_checker=lambda: {"available": False, "reason": "credential_missing"},
            _provider_builder=builder,
            _output_dir=tmp_path,
        )
    assert builder.constructions == 0


# ---------------------------------------------------------------------------
# State H -- consumed / revoked
# ---------------------------------------------------------------------------

def test_state_h_consumed_zeroes_budget_and_forbids_execution():
    document = _consumed_document()
    assert frc.validate_document_state(document) == []
    assert cc.validate_plan_document(document, REPO_ROOT) == []
    authorization = document["authorization"]
    assert authorization["authorized_budget_calls"] == 0
    assert authorization["authorized_model_keys"] == []
    assert authorization["operational_budget_usd_remaining"] == 0
    assert cc.production_authorization_errors(document, REPO_ROOT)


def test_state_h_consumed_plan_may_not_carry_a_nonzero_budget():
    document = _consumed_document()
    document["authorization"]["authorized_budget_calls"] = frc.EXPECTED_SLOTS
    assert frc.validate_document_state(document)
    assert cc.production_authorization_errors(document, REPO_ROOT)
