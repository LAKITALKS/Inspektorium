"""Isolated authorization-state invariant tests for the Phase-5B Haiku replication.

The registered plan legitimately moves between an unauthorized/revoked audit state
and a bounded governance-approved state.  ``tests/test_full_replication_contract.py``
asserts that whichever state the *live* plan holds satisfies the invariant; this
module exercises every state against non-production, in-memory document objects.

Nothing here writes to the registered plan, reaches the provider execution path, or
constructs a real provider.  The authorized-state objects exist only inside these
tests, so proving the contract accepts a legitimate authorization can never make the
live plan spendable.
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
PLAN_PATH = REPO_ROOT / frc.PLAN_PATH

# Historical AUDIT EVIDENCE about the one-shot invocation that was revoked before
# provider construction: an earlier specification under an earlier QA profile.
CONSUMED_INVOCATION_FINGERPRINT = (
    "a00c4eda7b90bd715a0f172c2401fcd47fcc2aacb513dbfd355e60ab2719729c"
)
CONSUMED_INVOCATION_QA_PROFILE = "phase5b-full-replication-production-qa/v1"
HISTORICAL_EVIDENCE_FIELDS = (
    "consumption_reason",
    "lease_fingerprint",
    "consumed_invocation_specification_fingerprint",
    "consumed_invocation_qa_profile",
)


# ---------------------------------------------------------------------------
# Isolated, in-memory document objects. None of these touch the tracked plan.
# ---------------------------------------------------------------------------

def _document() -> dict:
    artifact = json.loads(PLAN_PATH.read_text())
    specification = frc.build_specification(artifact["definition"], REPO_ROOT)
    return {
        "plan_document_schema_version": artifact["plan_document_schema_version"],
        "definition": artifact["definition"],
        "specification": specification,
        "authorization": copy.deepcopy(artifact["authorization"]),
        "progress": copy.deepcopy(artifact["progress"]),
    }


def _not_executed_progress() -> dict:
    return {
        "status": cc.PROGRESS_NOT_EXECUTED,
        "completed_calls": 0,
        "arm_progress": {frc.ARM_ID: cc.PROGRESS_NOT_EXECUTED},
    }


def _authorized_authorization(specification_fingerprint: str) -> dict:
    """State B scope: bounded, Haiku-only, one guarded batch, held only in memory."""
    return {
        "status": cc.AUTH_REAL,
        "specification_fingerprint": specification_fingerprint,
        "authorization_source": "tracked_governance_approval",
        "authorized_budget_calls": frc.EXPECTED_SLOTS,
        "authorized_model_keys": [frc.EXPECTED_MODEL_KEY],
        "authorized_prompt_condition_ids": [frc.EXPECTED_PROMPT_CONDITION],
        "guarded_batch_invocations_authorized": 1,
        "manual_restarts_authorized": 0,
        "operational_budget_usd": frc.OPERATIONAL_BUDGET_USD,
        "authorization_mode": "ONE_SHOT_LEASE_BEFORE_PROVIDER_CONSTRUCTION",
    }


def _consumed_authorization(specification_fingerprint: str) -> dict:
    """State F scope: spent one-shot, zero remaining budget, evidence retained."""
    return {
        "status": cc.AUTH_CONSUMED,
        "specification_fingerprint": specification_fingerprint,
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
        "consumed_invocation_specification_fingerprint": CONSUMED_INVOCATION_FINGERPRINT,
        "consumed_invocation_qa_profile": CONSUMED_INVOCATION_QA_PROFILE,
    }


def _authorized_document() -> dict:
    document = _document()
    document["authorization"] = _authorized_authorization(
        document["specification"]["specification_fingerprint"]
    )
    document["progress"] = _not_executed_progress()
    return document


def _consumed_document() -> dict:
    document = _document()
    document["authorization"] = _consumed_authorization(
        document["specification"]["specification_fingerprint"]
    )
    document["progress"] = {
        "status": cc.PROGRESS_PARTIAL_INCOMPLETE,
        "completed_calls": 0,
        "arm_progress": {frc.ARM_ID: cc.PROGRESS_PARTIAL_INCOMPLETE},
        "stop_stage": "fresh_canonical_qa",
        "provider_constructions": 0,
        "terminal_attempts": 0,
    }
    return document


def _synthetic_document() -> dict:
    document = cc.synthetic_authorized_copy(_document(), expected_calls=frc.EXPECTED_SLOTS)
    document["progress"] = _not_executed_progress()
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
    """Records construction attempts; never returns a real provider."""

    def __init__(self):
        self.constructions = 0

    def __call__(self, model_key: str):  # pragma: no cover - must never be reached
        self.constructions += 1
        raise AssertionError("provider construction is forbidden in this test")


# ---------------------------------------------------------------------------
# State A -- no current authorization
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "status",
    [cc.AUTH_NOT_AUTHORIZED, cc.AUTH_CONSUMED, "SOME_UNKNOWN_STATE"],
)
def test_state_a_without_a_current_authorization_nothing_is_spendable(status):
    """Any state that is not a live governance approval forbids production execution."""
    document = _document()
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
    assert document["progress"]["completed_calls"] == 0


# ---------------------------------------------------------------------------
# State B -- a legitimate authorization must be accepted
# ---------------------------------------------------------------------------

def test_state_b_valid_isolated_authorization_is_accepted_by_the_contract():
    document = _authorized_document()
    assert frc.validate_document_state(document) == []
    assert cc.validate_plan_document(document, REPO_ROOT) == []
    assert cc.production_authorization_errors(document, REPO_ROOT) == []


def test_state_b_authorization_does_not_alter_the_scientific_specification():
    """Authorizing is a governance act; it must not move any scientific binding."""
    baseline = _document()["specification"]
    authorized = _authorized_document()["specification"]
    assert authorized["specification_fingerprint"] == baseline["specification_fingerprint"]
    assert authorized["expected_calls_total"] == frc.EXPECTED_SLOTS
    assert authorized["model_ids"] == [frc.EXPECTED_MODEL_ID]
    assert authorized["n_independent_units"] == frc.EXPECTED_UNITS
    assert authorized["n_replications"] == frc.EXPECTED_REPETITIONS
    assert authorized["governance_constraints"]["sonnet_authorized"] is False
    assert frc.validate_cost_gate(_authorized_document(), REPO_ROOT)["model_generations"] == 0


def test_state_b_building_an_authorized_object_leaves_the_live_plan_unauthorized():
    """The isolated proof must not make the registered plan spendable."""
    before = json.loads(PLAN_PATH.read_text())
    _authorized_document()
    after = json.loads(PLAN_PATH.read_text())
    assert before == after
    live = cc.resolve_registered_plan(frc.PLAN_ID, REPO_ROOT)
    assert live["authorization"]["status"] != cc.AUTH_REAL
    assert live["authorization"]["authorized_budget_calls"] == 0
    assert cc.production_authorization_errors(live, REPO_ROOT)


# ---------------------------------------------------------------------------
# State C -- another model
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("model_keys", [["sonnet"], ["opus"], ["haiku", "sonnet"], []])
def test_state_c_authorization_for_another_model_fails_closed(model_keys):
    document = _authorized_document()
    document["authorization"]["authorized_model_keys"] = model_keys
    assert frc.validate_document_state(document)
    assert cc.production_authorization_errors(document, REPO_ROOT)


def test_state_c_sonnet_is_refused_before_provider_construction(tmp_path):
    builder = _CountingProviderBuilder()
    with pytest.raises(ConditionAuthorizationError, match="outside the registered plan"):
        _run_registered_condition(
            frc.PLAN_ID,
            frc.ARM_ID,
            "sonnet",
            repo_root=REPO_ROOT,
            _synthetic_test=True,
            _plan_resolver=lambda _plan_id, _root: _synthetic_document(),
            _provider_builder=builder,
            _output_dir=tmp_path,
        )
    assert builder.constructions == 0


# ---------------------------------------------------------------------------
# State D -- over scope
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("authorized_budget_calls", frc.EXPECTED_SLOTS + 1),
        ("authorized_budget_calls", frc.EXPECTED_SLOTS * 2),
        ("operational_budget_usd", frc.OPERATIONAL_BUDGET_USD + 1.0),
        ("guarded_batch_invocations_authorized", 2),
        ("manual_restarts_authorized", 1),
        ("authorized_prompt_condition_ids", ["study_forensics.historical.v1"]),
        ("authorization_source", "self_approved"),
        ("authorization_mode", "UNBOUNDED"),
    ],
)
def test_state_d_over_scope_authorization_fails_closed(field, value):
    document = _authorized_document()
    document["authorization"][field] = value
    assert frc.validate_document_state(document)
    assert cc.production_authorization_errors(document, REPO_ROOT)


def test_state_d_authorization_for_another_specification_fails_closed():
    document = _authorized_document()
    document["authorization"]["specification_fingerprint"] = "0" * 64
    assert frc.validate_document_state(document)
    assert cc.production_authorization_errors(document, REPO_ROOT)


def test_state_d_authorized_plan_must_start_not_executed():
    document = _authorized_document()
    document["progress"]["completed_calls"] = 7
    assert frc.validate_document_state(document)


# ---------------------------------------------------------------------------
# State E -- source/environment binding still enforced under authorization
# ---------------------------------------------------------------------------

def test_state_e_valid_authorization_does_not_bypass_source_environment_binding(tmp_path):
    builder = _CountingProviderBuilder()
    invalid_source = _source_binding()
    invalid_source["valid"] = False
    invalid_source["errors"] = ["tracked source tree is dirty"]
    with pytest.raises(ConditionAuthorizationError, match="source state invalid"):
        _run_registered_condition(
            frc.PLAN_ID,
            frc.ARM_ID,
            frc.EXPECTED_MODEL_KEY,
            repo_root=REPO_ROOT,
            _synthetic_test=True,
            _plan_resolver=lambda _plan_id, _root: _synthetic_document(),
            _source_inspector=lambda _root: copy.deepcopy(invalid_source),
            _qa_executor=lambda _root, _source: {"synthetic": True},
            _qa_validator=lambda _qa, _source: (pi.QA_PASSED, []),
            _credential_checker=lambda: {"available": True, "reason": "synthetic"},
            _provider_builder=builder,
            _output_dir=tmp_path,
        )
    assert builder.constructions == 0


def test_state_e_valid_authorization_does_not_bypass_failing_canonical_qa(tmp_path):
    builder = _CountingProviderBuilder()
    with pytest.raises(ConditionAuthorizationError, match="did not authorize execution"):
        _run_registered_condition(
            frc.PLAN_ID,
            frc.ARM_ID,
            frc.EXPECTED_MODEL_KEY,
            repo_root=REPO_ROOT,
            _synthetic_test=True,
            _plan_resolver=lambda _plan_id, _root: _synthetic_document(),
            _source_inspector=lambda _root: _source_binding(),
            _qa_executor=lambda _root, _source: {"synthetic": True},
            _qa_validator=lambda _qa, _source: (pi.QA_FAILED, ["synthetic QA failure"]),
            _credential_checker=lambda: {"available": True, "reason": "synthetic"},
            _provider_builder=builder,
            _output_dir=tmp_path,
        )
    assert builder.constructions == 0


def test_state_e_valid_authorization_does_not_bypass_missing_credential(tmp_path):
    builder = _CountingProviderBuilder()
    with pytest.raises(ConditionAuthorizationError, match="provider unavailable"):
        _run_registered_condition(
            frc.PLAN_ID,
            frc.ARM_ID,
            frc.EXPECTED_MODEL_KEY,
            repo_root=REPO_ROOT,
            _synthetic_test=True,
            _plan_resolver=lambda _plan_id, _root: _synthetic_document(),
            _source_inspector=lambda _root: _source_binding(),
            _qa_executor=lambda _root, _source: {"synthetic": True},
            _qa_validator=lambda _qa, _source: (pi.QA_PASSED, []),
            _credential_checker=lambda: {
                "available": False,
                "reason": "credential_missing",
            },
            _provider_builder=builder,
            _output_dir=tmp_path,
        )
    assert builder.constructions == 0


# ---------------------------------------------------------------------------
# State F -- consumed after authorization
# ---------------------------------------------------------------------------

def test_state_f_consumed_after_authorization_zeroes_budget_and_keeps_evidence():
    document = _consumed_document()
    assert frc.validate_document_state(document) == []
    assert cc.validate_plan_document(document, REPO_ROOT) == []
    authorization = document["authorization"]
    assert authorization["authorized_budget_calls"] == 0
    assert authorization["authorized_model_keys"] == []
    assert authorization["authorized_prompt_condition_ids"] == []
    assert authorization["guarded_batch_invocations_authorized"] == 0
    assert authorization["operational_budget_usd_remaining"] == 0
    assert cc.production_authorization_errors(document, REPO_ROOT)
    assert all(field in authorization for field in HISTORICAL_EVIDENCE_FIELDS)


def test_state_f_consumed_plan_may_not_carry_a_nonzero_budget():
    document = _consumed_document()
    document["authorization"]["authorized_budget_calls"] = frc.EXPECTED_SLOTS
    assert frc.validate_document_state(document)
    assert cc.production_authorization_errors(document, REPO_ROOT)


# ---------------------------------------------------------------------------
# Evidence and current state are separate things
# ---------------------------------------------------------------------------

def test_historical_evidence_and_current_authorization_are_not_conflated():
    current = _document()["specification"]
    fingerprint = current["specification_fingerprint"]
    consumed = _consumed_authorization(fingerprint)
    authorized = _authorized_authorization(fingerprint)

    # The evidence describes an earlier specification under an earlier QA profile,
    # so it can never be read as a statement about what is spendable right now.
    assert consumed["consumed_invocation_specification_fingerprint"] != fingerprint
    assert consumed["consumed_invocation_qa_profile"] != current["qa_specification"]["version"]

    # Only the current state decides spendability; the evidence never does.
    assert consumed["authorized_budget_calls"] == 0
    assert authorized["authorized_budget_calls"] == frc.EXPECTED_SLOTS
    assert set(HISTORICAL_EVIDENCE_FIELDS) <= set(consumed)
    assert set(HISTORICAL_EVIDENCE_FIELDS).isdisjoint(authorized)


def test_both_authorization_states_are_valid_documents_for_the_same_specification():
    """Neither state is rejected, so QA cannot fail merely because one of them holds."""
    for build in (_consumed_document, _authorized_document):
        document = build()
        assert frc.validate_document_state(document) == []
        assert cc.validate_plan_document(document, REPO_ROOT) == []
        assert document["specification"]["specification_fingerprint"] == _document()[
            "specification"
        ]["specification_fingerprint"]


# ---------------------------------------------------------------------------
# The QA-scoped invariant test must accept BOTH live-plan states
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("state", ["authorized", "consumed"])
def test_canonical_qa_scoped_invariant_test_accepts_either_live_plan_state(
    monkeypatch, state
):
    """Canonical QA must not fail merely because a legitimate authorization exists.

    This drives the Canonical-QA-scoped invariant test in
    ``tests/test_full_replication_contract.py`` against a simulated live plan in each
    legitimate state.  The simulation is confined to the resolver used by that one
    call, so the tracked plan on disk is never authorized.
    """
    from tests import test_full_replication_contract as qa_scoped

    document = _authorized_document() if state == "authorized" else _consumed_document()
    monkeypatch.setattr(
        qa_scoped.cc,
        "resolve_registered_plan",
        lambda _plan_id, _root: copy.deepcopy(document),
    )

    qa_scoped.test_registered_plan_holds_the_authorization_invariant_in_whichever_state_it_is_in()

    # The plan on disk is untouched and still carries no spendable budget.
    on_disk = json.loads(PLAN_PATH.read_text())
    assert on_disk["authorization"]["status"] != cc.AUTH_REAL
    assert on_disk["authorization"]["authorized_budget_calls"] == 0
