"""Adversarial Phase-5A registered-condition guard matrix (offline only)."""

from __future__ import annotations

import copy
import json
import subprocess
from pathlib import Path

import pytest

from agent_arena import artifact_binding as ab
from agent_arena import condition_analysis as ca
from agent_arena import condition_contract as cc
from agent_arena import condition_retry as cr
from agent_arena import phase7a_execution as p7
from agent_arena import preflight_integrity as pi
from agent_arena import release_boundary as rb
from agent_arena import resume_integrity as ri
from agent_arena.phase7a_real_run import (
    ConditionAuthorizationError,
    _load_jsonl,
    _run_registered_condition,
    build_condition_analysis,
    run_registered_condition,
)
from agent_arena.providers import BaseProvider
from agent_arena.providers.response import ModelResponse
from agent_arena.runner import (
    STUDY_FORENSICS_PROMPT_PROSPECTIVE,
    STUDY_FORENSICS_PROMPT_VERSION_HISTORICAL,
    STUDY_FORENSICS_PROMPT_VERSION_PROSPECTIVE,
    run_agent,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
RECORD_FIXTURE = REPO_ROOT / "tests/fixtures/pipeline_qa/qa_release_gate_consolidated.json"


def _definition(*, unit_ids=("P7A-NEU-001",), n_replications=3):
    analysis_contract = ca.build_analysis_contract(
        primary_stratum_ids=["synthetic_primary"],
        control_stratum_ids=[],
        expected_primary_units=len(unit_ids),
        expected_control_units=0,
        n_replications=n_replications,
    )
    call_accounting = cc.build_call_accounting(
        n_units=len(unit_ids),
        n_replications=n_replications,
        primary_units=len(unit_ids),
        control_units=0,
    )
    return {
        "plan_id": cc.PAIRED_PLAN_ID,
        "comparison_id": cc.PAIRED_COMPARISON_ID,
        "research_question": "Does taxonomy alignment change ME/OV contract behavior?",
        "hypothesis": "The revised prompt reduces contract-discordant ME/OV primary labels.",
        "model_keys": ["haiku", "sonnet"],
        "n_replications": n_replications,
        "execution_mode": "independent_model_adjudication",
        "qa_profile": pi.CONDITION_CONTRACT_QA_VERSION,
        "unit_selection_rule": "fixed synthetic unit list declared before responses",
        "unit_strata": [
            {"stratum_id": "synthetic_primary", "purpose": "test only", "unit_ids": list(unit_ids)}
        ],
        "arms": [
            {
                "arm_id": cc.HISTORICAL_ARM_ID,
                "analytical_condition_id": "AA-P5A-COND-HISTORICAL-001",
                "prompt_version": STUDY_FORENSICS_PROMPT_VERSION_HISTORICAL,
                "artifact_namespace": "analysis/phase5a_scientific_contract/runs/historical-control",
            },
            {
                "arm_id": cc.PROSPECTIVE_ARM_ID,
                "analytical_condition_id": "AA-P5A-COND-TAXONOMY-ALIGNED-001",
                "prompt_version": STUDY_FORENSICS_PROMPT_VERSION_PROSPECTIVE,
                "artifact_namespace": "analysis/phase5a_scientific_contract/runs/taxonomy-aligned",
            },
        ],
        "analysis_contract": analysis_contract,
        "registered_identity_contract": cc.registered_identity_contract(),
        "provider_state": cc.registered_provider_state(),
        "call_accounting": call_accounting,
        "retry_contract": cr.build_retry_contract(
            analytical_slots=call_accounting["analytical_slots_total"],
            guarded_batch_invocations=call_accounting[
                "guarded_batch_invocations_in_schedule"
            ],
            slots_per_batch=call_accounting["analytical_slots_per_model_arm_batch"],
        ),
    }


def _synthetic_document(**kwargs):
    document = cc.build_plan_document(_definition(**kwargs), REPO_ROOT)
    return cc.synthetic_authorized_copy(
        document,
        expected_calls=document["specification"]["expected_calls_total"],
    )


def _source_binding(**changes):
    value = {
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
    value.update(changes)
    return value


def _valid_json(label="solid", confidence=0.8):
    return json.dumps({
        "final_answer": label,
        "evidence_tier": "clinical_human",
        "conclusion_tier": "same as evidence",
        "bridge_supported": True,
        "assumptions": [],
        "steps": ["synthetic local response"],
        "alternative_hypotheses": [],
        "uncertainties": [],
        "key_claims": [],
        "self_check": [],
        "confidence": confidence,
    })


class CountingCaptureProvider(BaseProvider):
    name = "synthetic-counting-provider"

    def __init__(self, model):
        self.model = model
        self.label = model
        self.requests = []
        self.captures = []

    def generate(self, task, system_prompt):
        self.requests.append({
            "system": system_prompt,
            "messages": [{"role": "user", "content": task.prompt}],
        })
        text = _valid_json()
        self.captures.append({
            "task_id": task.id,
            "raw_response": text,
            "raw_response_sha256": cc.rc._sha256_hex(text.encode()),
            "usage": {"input_tokens": 1, "output_tokens": 1},
            "finish_reason": "stop",
            "error": None,
            "error_type": None,
        })
        return ModelResponse(
            text=text,
            provider=self.name,
            model=self.model,
            finish_reason="stop",
            usage={"input_tokens": 1, "output_tokens": 1},
        )

    def send_prompt(self, task, system_prompt):  # pragma: no cover - normalized path is generate
        return self.generate(task, system_prompt).text


class ProviderBuilder:
    def __init__(self):
        self.constructions = 0
        self.providers = []

    def __call__(self, model_key):
        self.constructions += 1
        provider = CountingCaptureProvider(cc.rc.MODELS[model_key]["exact_model_id"])
        self.providers.append(provider)
        return provider


def _run_synthetic(tmp_path, document, *, arm_id=cc.PROSPECTIVE_ARM_ID,
                   builder=None, source_inspector=None, plan_resolver=None):
    builder = builder or ProviderBuilder()
    source = _source_binding()
    return _run_registered_condition(
        cc.PAIRED_PLAN_ID,
        arm_id,
        "haiku",
        repo_root=REPO_ROOT,
        _synthetic_test=True,
        _plan_resolver=plan_resolver or (lambda _plan_id, _root: copy.deepcopy(document)),
        _source_inspector=source_inspector or (lambda _root: copy.deepcopy(source)),
        _qa_executor=lambda _root, _binding: {"synthetic": True},
        _qa_validator=lambda _qa, _binding: (pi.QA_PASSED, []),
        _credential_checker=lambda: {"available": True, "reason": "synthetic"},
        _provider_builder=builder,
        _output_dir=tmp_path,
    ), builder


def test_A_registered_production_plan_is_explicitly_non_authorizing():
    document = cc.resolve_registered_plan(cc.PAIRED_PLAN_ID, REPO_ROOT)
    assert document["authorization"]["status"] == cc.AUTH_NOT_AUTHORIZED
    assert document["progress"]["status"] == cc.PROGRESS_NOT_EXECUTED
    assert cc.production_authorization_errors(document)


def test_B_unknown_plan_fails_before_provider_construction(tmp_path):
    builder = ProviderBuilder()
    with pytest.raises(cc.ConditionContractError, match="unknown registered plan"):
        _run_registered_condition(
            "AA-UNKNOWN",
            cc.PROSPECTIVE_ARM_ID,
            "haiku",
            repo_root=REPO_ROOT,
            _synthetic_test=True,
            _provider_builder=builder,
            _output_dir=tmp_path,
        )
    assert builder.constructions == 0


def test_C_unapproved_registered_plan_fails_before_provider_construction():
    builder = ProviderBuilder()
    with pytest.raises(ConditionAuthorizationError, match="not authorized"):
        _run_registered_condition(
            cc.PAIRED_PLAN_ID,
            cc.PROSPECTIVE_ARM_ID,
            "haiku",
            repo_root=REPO_ROOT,
            _provider_builder=builder,
        )
    assert builder.constructions == 0


@pytest.mark.parametrize("keyword", ["approved", "units", "n_replications", "qa_scope", "provider_factory"])
def test_D_public_caller_cannot_supply_authorization_or_execution_material(keyword):
    with pytest.raises(TypeError):
        run_registered_condition(
            cc.PAIRED_PLAN_ID,
            cc.PROSPECTIVE_ARM_ID,
            "haiku",
            repo_root=REPO_ROOT,
            **{keyword: True},
        )


def test_E_approved_NOT_EXECUTED_synthetic_plan_reaches_one_provider_construction(tmp_path):
    document = _synthetic_document()
    result, builder = _run_synthetic(tmp_path, document)
    assert builder.constructions == 1
    assert len(result["records"]) == 3
    assert document["progress"]["status"] == cc.PROGRESS_NOT_EXECUTED
    assert result["records"][0]["prompt_condition_id"] == cc.resolve_arm(
        document, cc.PROSPECTIVE_ARM_ID
    )["prompt_condition_id"]


@pytest.mark.parametrize(
    "arm_id,prompt_version",
    [
        (cc.HISTORICAL_ARM_ID, STUDY_FORENSICS_PROMPT_VERSION_HISTORICAL),
        (cc.PROSPECTIVE_ARM_ID, STUDY_FORENSICS_PROMPT_VERSION_PROSPECTIVE),
    ],
)
def test_F_guarded_request_uses_authenticated_prompt_condition(
    tmp_path, arm_id, prompt_version
):
    document = _synthetic_document()
    result, builder = _run_synthetic(tmp_path / arm_id, document, arm_id=arm_id)
    request = builder.providers[0].requests[0]
    arm = cc.resolve_arm(document, arm_id)
    assert arm["prompt_version"] == prompt_version
    assert cc.rc._sha256_hex(request["system"].encode()) == arm["system_prompt_sha256"]
    assert result["records"][0]["prompt_version"] == prompt_version


def test_G_actual_anthropic_request_contains_selected_prompt_and_only_task_prompt(monkeypatch):
    calls = []

    class Messages:
        def create(self, **kwargs):
            calls.append(kwargs)
            return type("Response", (), {
                "content": [type("Block", (), {"text": _valid_json()})()],
                "stop_reason": "end_turn",
                "usage": None,
            })()

    class Client:
        messages = Messages()

    fake_module = type("AnthropicModule", (), {"Anthropic": lambda **_kwargs: Client()})
    monkeypatch.setitem(__import__("sys").modules, "anthropic", fake_module)
    from agent_arena.providers.anthropic import AnthropicProvider

    unit = cc.units_for_plan(_synthetic_document(), REPO_ROOT)[0]
    result = run_agent(
        AnthropicProvider(model=cc.rc.MODELS["haiku"]["exact_model_id"]),
        unit.task,
        prompt_version=STUDY_FORENSICS_PROMPT_VERSION_PROSPECTIVE,
    )
    assert result.parse_ok
    assert calls[0]["system"] == STUDY_FORENSICS_PROMPT_PROSPECTIVE
    assert calls[0]["messages"] == [{"role": "user", "content": unit.task.prompt}]
    combined = json.dumps({"system": calls[0]["system"], "messages": calls[0]["messages"]})
    assert unit.task.reference_solution not in combined
    assert unit.task.gold_justification not in combined


def test_H_progress_changes_do_not_change_immutable_specification_fingerprint():
    document = _synthetic_document()
    before = cc.specification_fingerprint(document)
    document["progress"] = {
        "status": cc.PROGRESS_PARTIAL,
        "completed_calls": 1,
        "arm_progress": {cc.HISTORICAL_ARM_ID: cc.PROGRESS_PARTIAL},
    }
    assert cc.specification_fingerprint(document) == before
    assert cc.validate_plan_document(document, REPO_ROOT, _allow_synthetic_test=True) == []


@pytest.mark.parametrize(
    "damage",
    ["prompt", "package", "runtime", "manifest", "call_plan"],
)
def test_I_prompt_package_runtime_manifest_or_call_plan_mismatch_fails_closed(damage):
    document = _synthetic_document()
    arm = cc.resolve_arm(document, cc.PROSPECTIVE_ARM_ID)
    if damage == "prompt":
        arm["system_prompt_sha256"] = "0" * 64
    elif damage == "package":
        arm["package_fingerprint"] = "0" * 64
    elif damage == "runtime":
        arm["runtime_contracts"]["haiku"]["temperature"] = 1
    elif damage == "manifest":
        arm["execution_manifest"]["n_independent_units"] += 1
    else:
        arm["call_plan"]["expected_calls"] += 1
    errors = cc.verify_arm_bindings(
        document, arm, "haiku", REPO_ROOT, _allow_synthetic_test=True
    )
    assert errors


def test_J_wrong_condition_artifact_fails_before_provider_construction(tmp_path):
    document = _synthetic_document()
    damaged = copy.deepcopy(document)
    damaged["specification"]["arms"][1]["package_fingerprint"] = "0" * 64
    builder = ProviderBuilder()
    with pytest.raises(ConditionAuthorizationError):
        _run_synthetic(tmp_path, damaged, builder=builder)
    assert builder.constructions == 0


def test_K_source_change_after_QA_fails_before_provider_construction(tmp_path):
    document = _synthetic_document()
    states = [_source_binding(), _source_binding(source_state_fingerprint="0" * 64)]
    builder = ProviderBuilder()

    def inspect(_root):
        return copy.deepcopy(states.pop(0))

    with pytest.raises(ConditionAuthorizationError, match="source binding mismatch"):
        _run_synthetic(tmp_path, document, builder=builder, source_inspector=inspect)
    assert builder.constructions == 0


def test_L_cross_condition_checkpoint_and_missing_condition_identity_fail_closed(tmp_path):
    document = _synthetic_document()
    result, _builder = _run_synthetic(tmp_path / "source", document)
    record = result["records"][0]
    units = cc.units_for_plan(document, REPO_ROOT)
    source = _source_binding()
    historical_arm = cc.resolve_arm(document, cc.HISTORICAL_ARM_ID)
    historical_contract = ri.build_condition_resume_contract(
        document,
        historical_arm,
        "haiku",
        units,
        REPO_ROOT,
        execution_type=p7.EXEC_TYPE_DRY_RUN,
        dry_run=True,
        source_binding=source,
        checkpoint_root=tmp_path / "other",
    )
    cross = ri.validate_checkpoint_records([record], historical_contract, units)
    assert not cross["valid"]
    missing = copy.deepcopy(record)
    missing.pop("prompt_condition_id")
    same_contract = ri.build_condition_resume_contract(
        document,
        cc.resolve_arm(document, cc.PROSPECTIVE_ARM_ID),
        "haiku",
        units,
        REPO_ROOT,
        execution_type=p7.EXEC_TYPE_DRY_RUN,
        dry_run=True,
        source_binding=source,
        checkpoint_root=tmp_path / "source",
    )
    absent = ri.validate_checkpoint_records([missing], same_contract, units)
    assert not absent["valid"]
    assert any("prompt_condition_id" in error for error in absent["errors"])


def test_M_cross_plan_or_mixed_contract_records_fail_closed(tmp_path):
    document = _synthetic_document()
    result, _builder = _run_synthetic(tmp_path / "source", document)
    record = result["records"][0]
    changed_definition = _definition()
    changed_definition["comparison_id"] = "AA-P5A-MEOV-COMPARISON-CHANGED"
    other_document = cc.build_plan_document(changed_definition, REPO_ROOT)
    other = cc.synthetic_authorized_copy(
        other_document,
        expected_calls=other_document["specification"]["expected_calls_total"],
    )
    units = cc.units_for_plan(other, REPO_ROOT)
    contract = ri.build_condition_resume_contract(
        other,
        cc.resolve_arm(other, cc.PROSPECTIVE_ARM_ID),
        "haiku",
        units,
        REPO_ROOT,
        execution_type=p7.EXEC_TYPE_DRY_RUN,
        dry_run=True,
        source_binding=_source_binding(),
        checkpoint_root=tmp_path / "other",
    )
    report = ri.validate_checkpoint_records([record], contract, units)
    assert not report["valid"]
    mixed = ri.validate_checkpoint_records([record, copy.deepcopy(record)], contract, units)
    assert not mixed["valid"]
    assert mixed["duplicate_slots"] == 1


def test_N_condition_analysis_rejects_mixed_identity(tmp_path):
    document = _synthetic_document()
    result, _builder = _run_synthetic(tmp_path, document)
    record = copy.deepcopy(result["records"][0])
    record["analytical_condition_id"] = "another-condition"
    with pytest.raises(ri.ResumeIntegrityError, match="condition analysis record"):
        build_condition_analysis(
            [record],
            document=document,
            arm=cc.resolve_arm(document, cc.PROSPECTIVE_ARM_ID),
            model_key="haiku",
            dry_run=True,
        )


def test_O_legacy_historical_records_remain_readable_without_silent_migration():
    path = REPO_ROOT / "analysis/phase7a_execution/haiku/raw/haiku_raw_records.jsonl"
    records = _load_jsonl(path)
    assert len(records) == 420
    assert "prompt_condition_id" not in records[0]
    assert "specification_fingerprint" not in records[0]


def test_P_invalid_confidence_and_terminal_semantics_are_unchanged():
    invalid = {
        "parse_ok": True,
        "label": "solid",
        "confidence": 2.0,
        "error": None,
        "finish_reason": "stop",
    }
    state = p7.analytical_state(invalid)
    assert state == {
        "terminal_attempt": True,
        "classification_valid": True,
        "calibration_valid": False,
        "model_call_again_allowed": False,
    }
    semantic_failure = {"parse_ok": False, "error": None, "finish_reason": "stop"}
    assert p7.is_terminal_attempt(semantic_failure) is True
    assert p7.model_call_again_allowed(semantic_failure) is False


def _git(root: Path, *args):
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


def test_Q_condition_aware_release_source_rejects_identity_change(tmp_path):
    record = ab.load_forensic_record(RECORD_FIXTURE).model_copy(deep=True)
    record.synthetic_fixture = True
    record.fixture_class = "release_boundary_qa"
    for provenance in record.provenance:
        provenance.content_fingerprint = ab.compute_content_fingerprint(
            provenance.exact_claim_text, provenance.provenance_state
        )
    repo = tmp_path / "release-source"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.name", "Agent Arena QA")
    _git(repo, "config", "user.email", "qa@example.invalid")
    source = repo / "source.json"
    manifest = {
        "release_source_schema_version": rb.CONDITION_RELEASE_SOURCE_SCHEMA_VERSION,
        "data_role": "synthetic_release_qa",
        "execution_id": "condition-execution",
        "analysis_id": "condition-analysis",
        "package_fingerprint": "a" * 64,
        "runtime_contract_fingerprint": "b" * 64,
        "forensic_record_fingerprint": ab.record_fingerprint(record),
        "plan_id": cc.PAIRED_PLAN_ID,
        "specification_fingerprint": "c" * 64,
        "arm_id": cc.PROSPECTIVE_ARM_ID,
        "arm_specification_fingerprint": "d" * 64,
        "analytical_condition_id": "AA-P5A-COND-TAXONOMY-ALIGNED-001",
        "prompt_condition_id": "study_forensics.taxonomy_aligned.v2",
    }
    source.write_text(json.dumps(manifest, sort_keys=True) + "\n")
    _git(repo, "add", "source.json")
    _git(repo, "commit", "-qm", "condition source")
    candidate = rb.build_release_object(
        record,
        release_object_id="condition-source-test",
        source_artifact_path="source.json",
        repo_root=repo,
    )
    manifest["prompt_condition_id"] = "study_forensics.historical.v1"
    source.write_text(json.dumps(manifest, sort_keys=True) + "\n")
    _git(repo, "add", "source.json")
    _git(repo, "commit", "-qm", "change condition")
    result = rb.release_official_artifact(candidate, output_root=tmp_path / "out", repo_root=repo)
    assert result.released is False
    assert any("source binding mismatch" in error for error in result.errors)


def test_R_validation_artifact_role_is_not_a_supported_release_source(tmp_path):
    path = tmp_path / "diagnostic.json"
    path.write_text(json.dumps({
        "release_source_schema_version": rb.RELEASE_SOURCE_SCHEMA_VERSION,
        "data_role": "diagnostic_validation",
        "execution_id": "x",
        "analysis_id": "y",
        "package_fingerprint": "a" * 64,
        "runtime_contract_fingerprint": "b" * 64,
        "forensic_record_fingerprint": "c" * 64,
    }))
    with pytest.raises(rb.ReleaseBoundaryError, match="data role is unsupported"):
        rb._read_source_manifest(path)
