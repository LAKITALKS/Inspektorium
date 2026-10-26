"""Offline contract and one-shot tests for the Phase-5B Haiku replication."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_arena import condition_contract as cc
from agent_arena import full_replication_analysis as fra
from agent_arena import full_replication_contract as frc
from agent_arena import preflight_integrity as pi
from agent_arena.phase7a_real_run import (
    ConditionAuthorizationError,
    _run_registered_condition,
)
from agent_arena.providers import BaseProvider
from agent_arena.providers.response import ModelResponse


REPO_ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = REPO_ROOT / frc.PLAN_PATH

# Historical AUDIT EVIDENCE about the one-shot invocation that was revoked before
# provider construction. It describes an earlier specification under an earlier QA
# profile and is never a statement about what is spendable now.
CONSUMED_INVOCATION_FINGERPRINT = (
    "a00c4eda7b90bd715a0f172c2401fcd47fcc2aacb513dbfd355e60ab2719729c"
)
CONSUMED_INVOCATION_QA_PROFILE = "phase5b-full-replication-production-qa/v1"


def _plan_artifact() -> dict:
    return json.loads(PLAN_PATH.read_text())


def _document() -> dict:
    artifact = _plan_artifact()
    specification = frc.build_specification(artifact["definition"], REPO_ROOT)
    authorization = copy.deepcopy(artifact["authorization"])
    authorization["specification_fingerprint"] = specification["specification_fingerprint"]
    return {
        "plan_document_schema_version": artifact["plan_document_schema_version"],
        "definition": artifact["definition"],
        "specification": specification,
        "authorization": authorization,
        "progress": artifact["progress"],
    }


def _synthetic_document() -> dict:
    document = cc.synthetic_authorized_copy(
        _document(), expected_calls=frc.EXPECTED_SLOTS
    )
    document["progress"] = {
        "status": cc.PROGRESS_NOT_EXECUTED,
        "completed_calls": 0,
        "arm_progress": {frc.ARM_ID: cc.PROGRESS_NOT_EXECUTED},
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
        "package_origins": {
            "agent_arena": str(REPO_ROOT / "src/agent_arena/__init__.py")
        },
        "source_state_fingerprint": "f" * 64,
    }


def _valid_json() -> str:
    return json.dumps({
        "final_answer": "solid",
        "evidence_tier": "clinical_human",
        "conclusion_tier": "same as evidence",
        "bridge_supported": True,
        "assumptions": [],
        "steps": ["synthetic local response"],
        "alternative_hypotheses": [],
        "uncertainties": [],
        "key_claims": [],
        "self_check": [],
        "confidence": 0.8,
    })


class _CountingProvider(BaseProvider):
    name = "synthetic-counting-provider"

    def __init__(self, model: str):
        self.model = model
        self.label = model
        self.requests = 0
        self.captures = []

    def generate(self, task, system_prompt):
        self.requests += 1
        text = _valid_json()
        usage = {
            "input_tokens": 1,
            "output_tokens": 1,
            "http_attempts": 1,
            "transport_retries": 0,
        }
        self.captures.append({
            "task_id": task.id,
            "raw_response": text,
            "raw_response_sha256": cc.rc._sha256_hex(text.encode()),
            "usage": usage,
            "finish_reason": "stop",
            "error": None,
            "error_type": None,
        })
        return ModelResponse(
            text=text,
            provider=self.name,
            model=self.model,
            finish_reason="stop",
            usage=usage,
        )

    def send_prompt(self, task, system_prompt):  # pragma: no cover - generate is normalized
        return self.generate(task, system_prompt).text


class _ProviderBuilder:
    def __init__(self):
        self.constructions = 0
        self.providers = []

    def __call__(self, model_key: str):
        self.constructions += 1
        provider = _CountingProvider(cc.rc.MODELS[model_key]["exact_model_id"])
        self.providers.append(provider)
        return provider


class _AuthErrorProvider(_CountingProvider):
    def generate(self, task, system_prompt):
        self.requests += 1
        usage = {
            "http_attempts": 1,
            "transport_retries": 0,
        }
        self.captures.append({
            "task_id": task.id,
            "raw_response": "",
            "raw_response_sha256": cc.rc._sha256_hex(b""),
            "usage": usage,
            "finish_reason": "error",
            "error": "synthetic authorization failure",
            "error_type": "auth_error",
        })
        return ModelResponse(
            text="",
            provider=self.name,
            model=self.model,
            finish_reason="error",
            usage=usage,
            error="synthetic authorization failure",
            error_type="auth_error",
        )


class _AuthErrorBuilder(_ProviderBuilder):
    def __call__(self, model_key: str):
        self.constructions += 1
        provider = _AuthErrorProvider(cc.rc.MODELS[model_key]["exact_model_id"])
        self.providers.append(provider)
        return provider


def _run_synthetic(tmp_path: Path, document: dict, builder: _ProviderBuilder):
    source = _source_binding()
    return _run_registered_condition(
        frc.PLAN_ID,
        frc.ARM_ID,
        frc.EXPECTED_MODEL_KEY,
        repo_root=REPO_ROOT,
        _synthetic_test=True,
        _plan_resolver=lambda _plan_id, _root: copy.deepcopy(document),
        _source_inspector=lambda _root: copy.deepcopy(source),
        _qa_executor=lambda _root, _source: {"synthetic": True},
        _qa_validator=lambda _qa, _source: (pi.QA_PASSED, []),
        _credential_checker=lambda: {"available": True, "reason": "synthetic"},
        _provider_builder=builder,
        _output_dir=tmp_path,
    )


def test_full_specification_binds_exact_schedule_model_prompt_and_retry_ceiling():
    document = _document()
    specification = document["specification"]
    arm = specification["arms"][0]
    assert specification["plan_id"] == frc.PLAN_ID
    assert specification["model_ids"] == [frc.EXPECTED_MODEL_ID]
    assert specification["n_independent_units"] == 84
    assert specification["n_replications"] == 5
    assert specification["expected_calls_total"] == 420
    assert specification["provider_method_invocations_schedule_max"] == 420
    assert specification["http_attempts_schedule_max"] == 1260
    assert arm["prompt_condition_id"] == frc.EXPECTED_PROMPT_CONDITION
    assert arm["system_prompt_sha256"] == frc.EXPECTED_PROMPT_SHA256
    assert specification["governance_constraints"]["sonnet_authorized"] is False
    assert specification["governance_constraints"]["historical_prompt_arm_authorized"] is False


def test_existing_paired_plan_remains_not_executed_and_not_authorized():
    paired = cc.resolve_registered_plan(cc.PAIRED_PLAN_ID, REPO_ROOT)
    assert paired["authorization"]["status"] == cc.AUTH_NOT_AUTHORIZED
    assert paired["progress"]["status"] == cc.PROGRESS_NOT_EXECUTED
    assert paired["specification"]["n_independent_units"] == 19
    assert set(fra.TARGETED_19) == {
        binding["unit_id"] for binding in paired["specification"]["ordered_unit_bindings"]
    }


def test_registered_plan_holds_the_authorization_invariant_in_whichever_state_it_is_in():
    """Assert the governance invariant, not one frozen snapshot of the plan.

    The registered plan legitimately moves between an unauthorized/revoked audit
    state and a bounded governance-approved state.  Canonical QA has to accept
    both, so this asserts what must hold in each rather than pinning the live plan
    to one of them.  The isolated per-state coverage (valid authorization, wrong
    model, over-scope, binding mismatch, consumption) lives in
    ``tests/test_authorization_state_invariant.py``.
    """
    document = cc.resolve_registered_plan(frc.PLAN_ID, REPO_ROOT)
    authorization = document["authorization"]
    status = authorization["status"]
    assert status in {cc.AUTH_REAL, cc.AUTH_CONSUMED, cc.AUTH_NOT_AUTHORIZED}
    assert authorization["specification_fingerprint"] == document["specification"][
        "specification_fingerprint"
    ]

    if status == cc.AUTH_REAL:
        # A current authorization exists: it is bounded and never widens the run.
        assert cc.production_authorization_errors(document, REPO_ROOT) == []
        assert authorization["authorization_source"] == "tracked_governance_approval"
        assert authorization["authorized_budget_calls"] == frc.EXPECTED_SLOTS
        assert authorization["authorized_model_keys"] == [frc.EXPECTED_MODEL_KEY]
        assert authorization["authorized_prompt_condition_ids"] == [
            frc.EXPECTED_PROMPT_CONDITION
        ]
        assert authorization["guarded_batch_invocations_authorized"] == 1
        assert authorization["manual_restarts_authorized"] == 0
        assert authorization["operational_budget_usd"] == frc.OPERATIONAL_BUDGET_USD
        assert document["progress"]["status"] == cc.PROGRESS_NOT_EXECUTED
    else:
        # No current authorization: nothing is spendable and execution is refused.
        assert cc.production_authorization_errors(document, REPO_ROOT)
        assert authorization["authorized_budget_calls"] == 0
        assert authorization.get("authorized_model_keys", []) == []
        if status == cc.AUTH_CONSUMED:
            assert authorization["guarded_batch_invocations_authorized"] == 0
            assert authorization["operational_budget_usd_remaining"] == 0
            # The revoked state is where the audit evidence lives; it stays complete
            # and keeps pointing at the earlier invocation it actually describes.
            assert authorization["consumed_invocation_specification_fingerprint"] == (
                CONSUMED_INVOCATION_FINGERPRINT
            )
            assert authorization["consumed_invocation_qa_profile"] == (
                CONSUMED_INVOCATION_QA_PROFILE
            )

    # True in every state: nothing has been spent, and the pre-execution cost gate
    # still binds the current specification with no model generations behind it.
    assert document["progress"]["completed_calls"] == 0
    assert document["progress"].get("provider_constructions", 0) == 0
    cost_gate = frc.validate_cost_gate(document, REPO_ROOT)
    assert cost_gate["specification_fingerprint"] == document["specification"][
        "specification_fingerprint"
    ]
    assert cost_gate["model_generations"] == 0


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda d: d.update(model_keys=["sonnet"]), "Haiku only"),
        (lambda d: d["arm"].update(prompt_condition_id="wrong"), "arm identity"),
        (lambda d: d["arm"].update(system_prompt_sha256="0" * 64), "arm identity"),
        (lambda d: d["ordered_unit_ids"].pop(), "ordered 84-unit universe"),
        (lambda d: d["historical_reference"].update(raw_records_sha256="0" * 64), "hash mismatch"),
    ],
)
def test_contract_tampering_fails_closed(mutation, message):
    definition = copy.deepcopy(_plan_artifact()["definition"])
    mutation(definition)
    with pytest.raises(frc.FullReplicationContractError, match=message):
        frc.build_specification(definition, REPO_ROOT)


def test_synthetic_full_path_executes_exactly_420_and_second_invocation_is_blocked(tmp_path):
    document = _synthetic_document()
    first_builder = _ProviderBuilder()
    result = _run_synthetic(tmp_path, document, first_builder)
    assert first_builder.constructions == 1
    assert first_builder.providers[0].requests == 420
    assert result["freeze"]["terminal_attempts"] == 420
    assert result["freeze"]["classification_valid_calls"] == 420
    assert result["comparison"]["prospective"]["expected_response_slots"] == 420
    assert result["usage_cost"]["http_attempts"] == 420
    assert (tmp_path / frc.LEASE_FILENAME).is_file()

    second_builder = _ProviderBuilder()
    with pytest.raises(ConditionAuthorizationError, match="second invocation prohibited"):
        _run_synthetic(tmp_path, document, second_builder)
    assert second_builder.constructions == 0

    partial_builder = _AuthErrorBuilder()
    partial = _run_synthetic(tmp_path / "partial", document, partial_builder)
    assert partial_builder.constructions == 1
    assert partial_builder.providers[0].requests == 1
    assert partial["batch_abort"] == "non-transient provider error on first calls: auth_error"
    assert partial["freeze"]["terminal_attempts"] == 0
    assert partial["freeze"]["analysis_status"] == cc.PROGRESS_PARTIAL_INCOMPLETE
    assert partial["freeze"]["replication_record_count"] == 1


def test_sonnet_is_rejected_before_provider_construction(tmp_path):
    document = _synthetic_document()
    builder = _ProviderBuilder()
    with pytest.raises(ConditionAuthorizationError, match="outside the registered plan"):
        _run_registered_condition(
            frc.PLAN_ID,
            frc.ARM_ID,
            "sonnet",
            repo_root=REPO_ROOT,
            _synthetic_test=True,
            _plan_resolver=lambda _plan_id, _root: copy.deepcopy(document),
            _provider_builder=builder,
            _output_dir=tmp_path,
        )
    assert builder.constructions == 0


def test_historical_replay_matches_frozen_metrics_and_missingness_does_not_shrink_denominators():
    specification = _document()["specification"]
    historical_path = REPO_ROOT / specification["historical_reference"]["raw_records_path"]
    records = [json.loads(line) for line in historical_path.read_text().splitlines() if line]
    summary = fra.summarize_records(
        records,
        ordered_unit_bindings=specification["ordered_unit_bindings"],
        model_id=frc.EXPECTED_MODEL_ID,
        repetitions=frc.EXPECTED_REPETITIONS,
        condition="historical_test_replay",
    )
    assert summary["unit_level_modal_accuracy"]["fixed_denominator"] == 84
    assert summary["unit_level_modal_accuracy"]["value"] == pytest.approx(0.7262, abs=0.0001)
    assert summary["calibration"]["brier"]["value"] == pytest.approx(0.240072, abs=0.000001)

    incomplete = fra.summarize_records(
        records[:-1],
        ordered_unit_bindings=specification["ordered_unit_bindings"],
        model_id=frc.EXPECTED_MODEL_ID,
        repetitions=frc.EXPECTED_REPETITIONS,
        condition="missingness_test",
    )
    assert incomplete["expected_response_slots"] == 420
    assert incomplete["observed_response_slots"] == 419
    assert incomplete["missing_response_slots"] == 1
    assert incomplete["unit_level_modal_accuracy"]["fixed_denominator"] == 84


def test_model_metadata_gate_accepts_only_exact_returned_identity():
    class Models:
        @staticmethod
        def retrieve(model_id):
            return type("Info", (), {"id": model_id})()

    client = type("Client", (), {"models": Models()})()
    from agent_arena.phase7a_real_run import check_exact_model_availability

    result = check_exact_model_availability(
        frc.EXPECTED_MODEL_ID,
        client_factory=lambda: client,
    )
    assert result["available"] is True
    assert result["returned_model_id"] == frc.EXPECTED_MODEL_ID
    assert result["model_generations"] == 0

    # A model with no registered Phase-5B full-replication plan (e.g. Opus) is
    # refused before any metadata HTTP. Haiku and Sonnet both carry a registered
    # plan, so the gate no longer singles Sonnet out; the plan/model binding is
    # enforced by the resolved plan's model_keys, tested elsewhere.
    blocked = check_exact_model_availability(
        "claude-opus-4-5-20251101",
        client_factory=lambda: client,
    )
    assert blocked["available"] is False
    assert blocked["metadata_http_attempts"] == 0
