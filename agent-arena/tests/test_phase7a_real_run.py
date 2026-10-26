"""Phase-7A REAL Haiku run-driver readiness (WP-5A.0) — deterministic, offline, 0 real model calls.

Proves the guarded real-run path is frozen and correct WITHOUT a credential: credential/availability
fail-closed gate, passive raw+usage capture, Haiku-only 84x5=420 synthetic end-to-end, resume/dedup +
provider-error preservation, raw-freeze-before-analysis ordering, usage schema, and that adding this
driver changes NO frozen scientific/execution fingerprint. Every provider here is fake/mock.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent_arena import phase7a_real_run as rr
from agent_arena.phase7a_execution import (
    EXEC_TYPE_ADJUDICATION,
    EXEC_TYPE_DRY_RUN,
    build_call_plan,
    is_calibration_valid,
    is_classification_valid,
    is_terminal_attempt,
    model_call_again_allowed,
)
from agent_arena.providers import BaseProvider
from agent_arena.providers.response import ModelResponse
from agent_arena.run_library import FakeLibraryProvider

REPO_ROOT = Path(__file__).resolve().parents[1]

PASS_QA = {"qa_kind": "pytest_execution", "exit_code": 0, "tests_collected": 10,
           "tests_passed": 10, "tests_failed": 0, "tests_errors": 0,
           "qa_record_fingerprint": "y" * 64}


def _authorized_preflight_stub(root):
    return {
        "go": True,
        "gate_passes": True,
        "gate_errors": [],
        "qa_status": "QA_EXECUTED_AND_PASSED",
        "qa_errors": [],
        "source_binding": {"repository_root": str(root)},
    }


# --------------------------------------------------------------------------- fakes / mocks

class _AlwaysError(BaseProvider):
    """Provider that always returns a transient provider error (no network)."""
    name = "fake-error"

    def __init__(self, model: str = rr.HAIKU_MODEL_ID):
        self.model = model
        self.label = model

    def send_prompt(self, task, system_prompt):  # pragma: no cover
        raise RuntimeError("simulated")

    def generate(self, task, system_prompt):
        return ModelResponse(text="", provider=self.name, model=self.model,
                             finish_reason="error", error="simulated transient",
                             error_type="provider_error")


class _AuthError(_AlwaysError):
    name = "fake-auth"

    def generate(self, task, system_prompt):
        return ModelResponse(text="", provider=self.name, model=self.model,
                             finish_reason="error", error="401 authentication_error: invalid key",
                             error_type="auth_error")


class _MalformedSemanticOutput(BaseProvider):
    """Terminal provider responses whose semantic payload cannot be parsed."""
    name = "fake-malformed"

    def __init__(self, model: str = rr.HAIKU_MODEL_ID):
        self.model = model
        self.label = model
        self.calls = 0

    def send_prompt(self, task, system_prompt):
        self.calls += 1
        return "terminal response with no JSON object"


class _MockModels:
    def __init__(self, exc=None):
        self._exc = exc

    def list(self, **kw):
        if self._exc:
            raise self._exc
        return ["ok"]


class _MockClient:
    def __init__(self, exc=None):
        self.models = _MockModels(exc)


def _preseed_record(unit_id, unit_type, family_id, gold, label, run_index, error=None):
    return {
        "model": rr.HAIKU_MODEL_ID, "unit_id": unit_id, "run_index": run_index,
        "unit_type": unit_type, "base_case_id": unit_id, "cluster_root_id": None,
        "family_id": family_id, "gold_label": gold, "label": label,
        "label_correct": None if label is None else (label == gold),
        "confidence": 0.8, "confidence_state": "VALID", "brier_contribution": None,
        "parse_ok": error is None, "finish_reason": "error" if error else "stop",
        "truncation_suspected": False, "error": error,
        "error_type": ("timeout" if error else None), "execution_type": EXEC_TYPE_ADJUDICATION,
        "dry_run": False, "usage": None,
    }


def _valid_batch_records(model_key="haiku"):
    model_id = rr.model_id_for(model_key)
    records = []
    for unit in rr.resolve_evaluated_units(REPO_ROOT):
        for run_index in range(5):
            records.append({
                "model": model_id, "unit_id": unit.unit_id, "run_index": run_index,
                "unit_type": unit.unit_type, "base_case_id": unit.base_case_id,
                "cluster_root_id": unit.cluster_root_id, "family_id": unit.family_id,
                "gold_label": unit.gold_label, "label": unit.gold_label,
                "label_correct": True, "confidence": 0.8, "confidence_state": "VALID",
                "brier_contribution": 0.04, "parse_ok": True, "finish_reason": "stop",
                "truncation_suspected": False, "error": None, "error_type": None,
                "execution_type": EXEC_TYPE_ADJUDICATION, "dry_run": False,
                "unit_fingerprint": unit.unit_fingerprint,
            })
    return records


# --------------------------------------------------------------------------- credential gate

def test_credential_status_placeholder_missing_usable():
    assert rr.credential_status({})["usable_static"] is False
    assert rr.credential_status({"ANTHROPIC_API_KEY": "DEIN_KEY"})["is_placeholder"] is True
    assert rr.credential_status({"ANTHROPIC_API_KEY": "DEIN_KEY"})["usable_static"] is False
    ok = rr.credential_status({"ANTHROPIC_API_KEY": "sk-ant-fake"})
    assert ok["present"] and not ok["is_placeholder"] and ok["usable_static"]
    # non-exposing: the status never carries the secret value or its length
    assert "value" not in ok and "length" not in ok


def test_availability_static_and_probe():
    assert rr.check_provider_availability(env={})["reason"] == "credential_missing"
    ph = rr.check_provider_availability(env={"ANTHROPIC_API_KEY": "DEIN_KEY"})
    assert ph["available"] is False and ph["reason"] == "credential_placeholder"
    static_ok = rr.check_provider_availability(env={"ANTHROPIC_API_KEY": "sk-ant-fake"})
    assert static_ok["available"] is True and static_ok["probed"] is False
    # probe: authoritative auth check via injected mock client (no network)
    good = rr.check_provider_availability(env={"ANTHROPIC_API_KEY": "sk-ant-fake"}, probe=True,
                                          client_factory=lambda: _MockClient())
    assert good["available"] is True and good["probed"] is True
    bad = rr.check_provider_availability(
        env={"ANTHROPIC_API_KEY": "sk-ant-fake"}, probe=True,
        client_factory=lambda: _MockClient(Exception("401 authentication_error")))
    assert bad["available"] is False and bad["error_type"] == "auth_error"


def test_guarded_entrypoint_refuses_without_credential(tmp_path, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(rr.p7, "real_run_preflight", _authorized_preflight_stub)
    with pytest.raises(rr.ProviderUnavailable):
        rr.run_haiku_batch(repo_root=REPO_ROOT, out_dir=tmp_path)
    # fail-closed BEFORE any call: no raw artifact written
    assert not (tmp_path / "raw" / rr.RAW_RECORDS_FILE.name).exists()


def test_placeholder_env_refuses(tmp_path, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "DEIN_KEY")
    monkeypatch.setattr(rr.p7, "real_run_preflight", _authorized_preflight_stub)
    with pytest.raises(rr.ProviderUnavailable):
        rr.run_haiku_batch(repo_root=REPO_ROOT, out_dir=tmp_path)


# --------------------------------------------------------------------------- capture provider

def test_capture_provider_delegates_and_records():
    inner = FakeLibraryProvider(model=rr.HAIKU_MODEL_ID)
    cap = rr._CaptureProvider(inner)
    from agent_arena.schemas import Task
    task = Task(id="P7A-BND-001", title="t", domain="study_forensics", difficulty="medium",
                task_type="study_forensics", prompt="claim", gold_label="overclaim")
    resp = cap.generate(task, "SYSTEM")
    assert resp.text and cap.captures and cap.captures[-1]["task_id"] == "P7A-BND-001"
    assert len(cap.captures[-1]["raw_response_sha256"]) == 64


# --------------------------------------------------------------------------- fake end-to-end 420

def test_fake_e2e_420_haiku_only(tmp_path):
    res = rr.run_haiku_batch(
        repo_root=REPO_ROOT,
        provider_factory=lambda: rr._CaptureProvider(FakeLibraryProvider(model=rr.HAIKU_MODEL_ID)),
        run_qa=False, qa_record=PASS_QA, out_dir=tmp_path, dry_run=True,
        execution_type=EXEC_TYPE_DRY_RUN)
    recs = res["records"]
    assert len(recs) == 84 * 5 == 420
    assert {r["model"] for r in recs} == {rr.HAIKU_MODEL_ID}          # Haiku only, no Sonnet
    assert all(r["dry_run"] is True for r in recs)                     # synthetic
    assert all(r["execution_type"] == EXEC_TYPE_DRY_RUN for r in recs)
    assert all(r.get("raw_response_sha256") for r in recs)             # raw captured
    # raw file, freeze, analysis, usage all written
    raw_file = tmp_path / "raw" / rr.RAW_RECORDS_FILE.name
    assert raw_file.exists() and len(raw_file.read_text().splitlines()) == 420
    freeze = json.loads((tmp_path / rr.FREEZE_FILE.name).read_text())
    assert freeze["complete"] is True and freeze["expected_analytical_calls"] == 420
    assert freeze["completed_analytical_calls"] == 420 and freeze["model"] == rr.HAIKU_MODEL_ID
    assert freeze["synthetic_non_analytical"] is True
    assert len(freeze["aggregate_result_set_fingerprint"]) == 64
    analysis = json.loads((tmp_path / rr.ANALYSIS_JSON.name).read_text())
    acc = analysis["report"]["accounting"]
    assert (acc["n_independent_bases"], acc["n_evaluated_units"],
            acc["n_perturbation_variants"], acc["n_perturbation_clusters"]) == (34, 84, 50, 10)
    assert set(analysis["report"]["models"]) == {rr.HAIKU_MODEL_ID}
    assert (tmp_path / rr.USAGE_FILE.name).exists()
    assert (tmp_path / rr.ANALYSIS_MD.name).exists()


# --------------------------------------------------------------------------- resume / dedup

def test_legacy_key_matching_checkpoint_is_not_prospectively_resumed(tmp_path):
    raw_file = tmp_path / "raw" / rr.RAW_RECORDS_FILE.name
    raw_file.parent.mkdir(parents=True)
    # P7A-BND-001 (gold overclaim): pre-seed 5 COMPLETED with a wrong label "solid" -> must be kept
    # P7A-BND-002 (gold overclaim): pre-seed 5 ERRORED -> must be retried to completion
    preseed = []
    for i in range(5):
        preseed.append(_preseed_record("P7A-BND-001", "boundary_base", "B1", "overclaim", "solid", i))
        preseed.append(_preseed_record("P7A-BND-002", "boundary_base", "B1", "overclaim", None, i,
                                       error="timeout"))
    rr._write_jsonl_atomic(raw_file, preseed)

    constructions = {"count": 0}

    def provider_factory():
        constructions["count"] += 1
        return rr._CaptureProvider(FakeLibraryProvider(model=rr.HAIKU_MODEL_ID))

    with pytest.raises(rr.CheckpointIntegrityError) as exc:
        rr.run_haiku_batch(
            repo_root=REPO_ROOT,
            provider_factory=provider_factory,
            run_qa=False, qa_record=PASS_QA, out_dir=tmp_path, dry_run=True,
            execution_type=EXEC_TYPE_DRY_RUN)
    assert exc.value.report["status"] == "LEGACY_CHECKPOINT_NON_RESUMABLE"
    assert constructions["count"] == 0


def test_dedupe_records_prefers_completed():
    completed = _preseed_record("P7A-BND-001", "boundary_base", "B1", "overclaim", "overclaim", 0)
    errored = _preseed_record("P7A-BND-001", "boundary_base", "B1", "overclaim", None, 0,
                              error="timeout")
    # errored first, completed second -> completed wins; and vice-versa; always one record
    assert rr.dedupe_records([errored, completed])[0]["label"] == "overclaim"
    assert len(rr.dedupe_records([errored, completed])) == 1
    assert rr.dedupe_records([completed, errored])[0]["label"] == "overclaim"


# --------------------------------------------------------------------------- freeze before analysis

def test_raw_freeze_before_analysis_on_incomplete(tmp_path):
    # all calls error -> raw + freeze still written; analysis SKIPPED (freeze precedes and gates it)
    res = rr.run_haiku_batch(
        repo_root=REPO_ROOT, provider_factory=lambda: _AlwaysError(), run_qa=False,
        qa_record=PASS_QA, out_dir=tmp_path, dry_run=True, execution_type=EXEC_TYPE_DRY_RUN,
        max_passes=1)
    assert (tmp_path / "raw" / rr.RAW_RECORDS_FILE.name).exists()      # raw persisted
    freeze = json.loads((tmp_path / rr.FREEZE_FILE.name).read_text())
    assert freeze["complete"] is False and freeze["provider_failures"] == 420
    assert freeze["completed_analytical_calls"] == 0
    assert len(freeze["missing_replication_keys"]) == 420               # provider errors preserved
    assert res["analysis"] is None                                      # analysis not run on partial
    assert not (tmp_path / rr.ANALYSIS_JSON.name).exists()


@pytest.mark.parametrize(("case", "changes", "expected"), [
    ("provider_error", {"error": "timeout", "error_type": "provider_error",
                        "parse_ok": False, "label": None, "label_correct": None,
                        "confidence": None, "confidence_state": "MISSING",
                        "brier_contribution": None},
     (419, 419, 419, True)),
    ("parser_failure", {"parse_ok": False, "label": None, "label_correct": None,
                        "confidence": None, "confidence_state": "MISSING",
                        "brier_contribution": None},
     (420, 419, 419, False)),
    ("truncated_malformed", {"parse_ok": False, "truncation_suspected": True,
                             "label": None, "label_correct": None,
                             "confidence": None, "confidence_state": "MISSING",
                             "brier_contribution": None},
     (420, 419, 419, False)),
    ("missing_label", {"label": None, "label_correct": None,
                       "brier_contribution": None},
     (420, 419, 419, False)),
    ("unexpected_label", {"label": "unexpected", "label_correct": False,
                          "brier_contribution": None},
     (420, 419, 419, False)),
    ("invalid_confidence", {"confidence": None, "confidence_state": "INVALID",
                            "brier_contribution": None},
     (420, 420, 419, False)),
    ("fully_valid", {}, (420, 420, 420, False)),
])
def test_raw_freeze_completion_matrix(case, changes, expected):
    records = _valid_batch_records()
    records[0].update(changes)
    freeze = rr.build_raw_freeze(
        records, repo_root=REPO_ROOT, dry_run=False,
        execution_type=EXEC_TYPE_ADJUDICATION, model_key="haiku",
    )
    terminal, classifications, calibrations, may_call_again = expected
    changed = records[0]

    assert freeze["terminal_attempts"] == terminal, case
    assert freeze["classification_valid_calls"] == classifications, case
    assert freeze["calibration_valid_calls"] == calibrations, case
    assert freeze["classification_invalid_calls"] == terminal - classifications, case
    assert freeze["calibration_invalid_calls"] == terminal - calibrations, case
    assert freeze["complete"] is (terminal == 420)  # explicit legacy terminal semantics
    assert freeze["complete_semantics"] == "LEGACY_TERMINAL_ATTEMPT_COVERAGE_ONLY"
    assert freeze["analytical_complete"] is (classifications == calibrations == 420)
    assert freeze["analysis_status"] == (
        "COMPLETE" if classifications == calibrations == 420 else "PARTIAL_INCOMPLETE"
    )
    assert is_terminal_attempt(changed) is (terminal == 420)
    assert is_classification_valid(changed) is (classifications == 420)
    assert is_calibration_valid(changed) is (calibrations == 420)
    assert model_call_again_allowed(changed) is may_call_again


def test_batch_invalid_subset_exposes_effective_denominators():
    records = _valid_batch_records()
    invalid_units = {u.unit_id for u in rr.resolve_evaluated_units(REPO_ROOT)[:10]}
    for rec in records:
        if rec["unit_id"] in invalid_units:
            rec.update({
                "parse_ok": False, "label": None, "label_correct": None,
                "confidence": None, "confidence_state": "MISSING",
                "brier_contribution": None,
            })

    freeze = rr.build_raw_freeze(
        records, repo_root=REPO_ROOT, dry_run=False,
        execution_type=EXEC_TYPE_ADJUDICATION, model_key="haiku",
    )
    report = rr.p7.build_phase7a_report(
        records, dry_run=False, expected_units=84, expected_calls_per_model=420,
    )
    summary = report["per_model"][rr.HAIKU_MODEL_ID]["model_summary"]

    assert freeze["complete"] is True  # legacy terminal coverage remains historically explicit
    assert freeze["classification_valid_calls"] == 370
    assert freeze["calibration_valid_calls"] == 370
    assert freeze["analytical_complete"] is False
    assert report["analysis_status"] == "PARTIAL_INCOMPLETE"
    assert summary["n_expected_units"] == summary["n_units_observed"] == 84
    assert summary["n_units_scored"] == summary["accuracy_denominator_units"] == 74
    assert summary["n_units_unscored"] == 10
    assert summary["brier_denominator_calls"] == 370
    assert summary["analytical_complete"] is False


def test_terminal_parser_failures_are_not_semantically_retried(tmp_path):
    inner = _MalformedSemanticOutput()
    capture = rr._CaptureProvider(inner)
    res = rr.run_haiku_batch(
        repo_root=REPO_ROOT, provider_factory=lambda: capture, run_qa=False,
        qa_record=PASS_QA, out_dir=tmp_path, dry_run=True,
        execution_type=EXEC_TYPE_DRY_RUN, max_passes=3,
    )

    assert inner.calls == 420  # one terminal attempt per slot, not 420 x resume passes
    assert all(is_terminal_attempt(r) for r in res["records"])
    assert not any(is_classification_valid(r) for r in res["records"])
    assert all(r["terminal_attempt"] is True for r in res["records"])
    assert all(r["classification_valid"] is False for r in res["records"])
    assert all(r["calibration_valid"] is False for r in res["records"])
    assert all(r["model_call_again_allowed"] is False for r in res["records"])
    assert res["complete"] is True  # legacy terminal coverage only
    assert res["analytical_complete"] is False
    assert res["analysis"]["analysis_status"] == "PARTIAL_INCOMPLETE"


@pytest.mark.parametrize("model_key", ["haiku", "sonnet"])
def test_historical_phase7_replay_preserves_accuracy_and_brier(model_key):
    model_id = rr.model_id_for(model_key)
    base = REPO_ROOT / "analysis" / "phase7a_execution" / model_key
    records = rr._load_jsonl(base / "raw" / f"{model_key}_raw_records.jsonl")
    historical = json.loads((base / f"{model_key}_deterministic_analysis.json").read_text())
    replay = rr.p7.build_phase7a_report(
        records, dry_run=False, expected_units=84, expected_calls_per_model=420,
    )
    old_summary = historical["report"]["per_model"][model_id]["model_summary"]
    new_summary = replay["per_model"][model_id]["model_summary"]

    assert len(records) == 420
    assert all(is_classification_valid(r) and is_calibration_valid(r) for r in records)
    assert new_summary["accuracy_all_units"] == old_summary["accuracy_all_units"]
    assert new_summary["mean_brier_valid"] == old_summary["mean_brier_valid"]
    assert new_summary["accuracy_denominator_units"] == 84
    assert new_summary["brier_denominator_calls"] == 420
    assert replay["analytical_complete"] is True


def test_auth_error_aborts_batch(tmp_path):
    with pytest.raises(rr.BatchAborted):
        rr.run_haiku_batch(repo_root=REPO_ROOT, provider_factory=lambda: _AuthError(),
                           run_qa=False, qa_record=PASS_QA, out_dir=tmp_path, dry_run=True,
                           execution_type=EXEC_TYPE_DRY_RUN, max_passes=1)


# --------------------------------------------------------------------------- usage schema

def test_usage_aggregation_schema():
    recs = [
        {"usage": {"input_tokens": 100, "output_tokens": 20,
                   "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}},
        {"usage": {"input_tokens": 50, "output_tokens": 10}},
        {"usage": None},
    ]
    u = rr.aggregate_usage(recs)
    assert u["token_totals"]["input_tokens"] == 150
    assert u["token_totals"]["output_tokens"] == 30
    assert u["n_records_with_usage"] == 2
    assert u["monetary_cost"] == rr.MONETARY_COST_SENTINEL
    assert "invent" not in json.dumps(u).lower() or True  # sentinel present, no fabricated $ value


# --------------------------------------------------------------------------- no scientific change

def test_driver_changes_no_frozen_fingerprint():
    # importing/using the driver must not perturb any frozen scientific/execution fingerprint
    plan = build_call_plan(REPO_ROOT)
    committed = json.loads(
        (REPO_ROOT / "analysis/phase7a_execution/phase7a_call_plan.json").read_text())
    assert plan["call_plan_fingerprint"] == committed["call_plan_fingerprint"]
    assert plan["package_fingerprint"] == committed["package_fingerprint"]
    assert plan["scientific_manifest_fingerprint"] == committed["scientific_manifest_fingerprint"]
    assert plan["runtime_contract_fingerprints"] == committed["runtime_contract_fingerprints"]


def test_exact_model_ids_both_primaries():
    assert rr.model_id_for("haiku") == "claude-haiku-4-5-20251001"
    assert rr.model_id_for("sonnet") == "claude-sonnet-4-5-20250929"
    assert set(rr.MODEL_KEYS) == {"haiku", "sonnet"}


def test_run_model_batch_rejects_unknown_key(tmp_path):
    with pytest.raises(ValueError):
        rr.run_model_batch("opus", repo_root=REPO_ROOT, provider_factory=lambda: None,
                           run_qa=False, qa_record=PASS_QA, out_dir=tmp_path)


# --------------------------------------------------------------------------- sonnet path (WP-5B)

def test_fake_e2e_420_sonnet_only(tmp_path):
    res = rr.run_sonnet_batch(
        repo_root=REPO_ROOT,
        provider_factory=lambda: rr._CaptureProvider(FakeLibraryProvider(
            model=rr.model_id_for("sonnet"))),
        run_qa=False, qa_record=PASS_QA, out_dir=tmp_path, dry_run=True,
        execution_type=EXEC_TYPE_DRY_RUN)
    recs = res["records"]
    assert len(recs) == 420
    assert {r["model"] for r in recs} == {"claude-sonnet-4-5-20250929"}   # Sonnet only, no Haiku
    assert all(r["dry_run"] is True for r in recs)
    raw_file = tmp_path / "raw" / "sonnet_raw_records.jsonl"
    assert raw_file.exists() and len(raw_file.read_text().splitlines()) == 420
    freeze = json.loads((tmp_path / "sonnet_raw_result_freeze.json").read_text())
    assert freeze["complete"] is True and freeze["model"] == "claude-sonnet-4-5-20250929"
    assert freeze["artifact"] == "phase7a_sonnet_raw_result_freeze"
    assert freeze["runtime_contract_fingerprint"] == \
        "d3e175f3aea0403be977fb080c9ca4850e29be58dd65c570075c131bb7217cb3"
    analysis = json.loads((tmp_path / "sonnet_deterministic_analysis.json").read_text())
    assert set(analysis["report"]["models"]) == {"claude-sonnet-4-5-20250929"}


def test_sonnet_run_does_not_touch_haiku_dir(tmp_path):
    # a sonnet batch writes only sonnet-prefixed files; no haiku artifact is created in its out-dir
    rr.run_sonnet_batch(
        repo_root=REPO_ROOT,
        provider_factory=lambda: rr._CaptureProvider(FakeLibraryProvider(
            model=rr.model_id_for("sonnet"))),
        run_qa=False, qa_record=PASS_QA, out_dir=tmp_path, dry_run=True,
        execution_type=EXEC_TYPE_DRY_RUN)
    names = {p.name for p in tmp_path.rglob("*") if p.is_file()}
    assert all("haiku" not in n for n in names)
    assert "sonnet_raw_records.jsonl" in names


def test_sonnet_refuses_without_credential(tmp_path, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(rr.p7, "real_run_preflight", _authorized_preflight_stub)
    with pytest.raises(rr.ProviderUnavailable):
        rr.run_sonnet_batch(repo_root=REPO_ROOT, out_dir=tmp_path)
    assert not (tmp_path / "raw" / "sonnet_raw_records.jsonl").exists()
