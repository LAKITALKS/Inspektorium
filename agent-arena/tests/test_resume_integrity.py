"""Adversarial prospective resume/checkpoint matrix A–V (offline only)."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_arena import phase7a_real_run as rr
from agent_arena import resume_integrity as ri
from agent_arena.phase7a_execution import EXEC_TYPE_DRY_RUN, MISSING, INVALID, VALID
from agent_arena.run_library import FakeLibraryProvider


REPO_ROOT = Path(__file__).resolve().parents[1]
PASS_QA = {
    "qa_kind": "pytest_execution",
    "exit_code": 0,
    "tests_collected": 10,
    "tests_passed": 10,
    "tests_failed": 0,
    "tests_errors": 0,
}


class ProviderBoundaryReached(RuntimeError):
    pass


class CountingFakeProvider(FakeLibraryProvider):
    def __init__(self):
        super().__init__(model=rr.HAIKU_MODEL_ID)
        self.calls = 0

    def send_prompt(self, task, system_prompt):
        self.calls += 1
        return super().send_prompt(task, system_prompt)


class CountingFactory:
    def __init__(self, *, sentinel: bool = False):
        self.constructions = 0
        self.inner = CountingFakeProvider()
        self.sentinel = sentinel

    def __call__(self):
        self.constructions += 1
        if self.sentinel:
            raise ProviderBoundaryReached("provider construction boundary reached")
        return rr._CaptureProvider(self.inner)


@pytest.fixture
def resume_material(tmp_path):
    units = rr.resolve_evaluated_units(REPO_ROOT)
    contract = ri.build_resume_contract(
        "haiku",
        units,
        REPO_ROOT,
        execution_type=EXEC_TYPE_DRY_RUN,
        dry_run=True,
        checkpoint_root=tmp_path,
    )
    return units, contract


def _paths(root: Path) -> tuple[Path, Path]:
    raw = root / "raw/haiku_raw_records.jsonl"
    manifest = root / "raw/haiku_checkpoint_manifest.json"
    return raw, manifest


def _record(
    unit,
    run_index: int,
    contract: dict,
    *,
    label: str | None = None,
    confidence: float | None = 0.8,
    confidence_state: str = VALID,
    parse_ok: bool = True,
    error: str | None = None,
    error_type: str | None = None,
    raw_response: str | None = None,
) -> dict:
    if label is None and parse_ok and error is None:
        label = unit.gold_label
    label_correct = None if label is None else label == unit.gold_label
    if raw_response is None:
        raw_response = "" if error else json.dumps({"final_answer": label})
    base = {
        "library_run_id": contract["library_run_id"],
        "case_id": unit.unit_id,
        "case_file": f"{unit.unit_id}.yaml",
        "provider": "synthetic-resume-fixture",
        "model": contract["model"],
        "run_index": run_index,
        "label": label,
        "label_correct": label_correct,
        "score": None,
        "confidence": confidence,
        "confidence_state": confidence_state,
        "parse_ok": parse_ok,
        "finish_reason": "error" if error else "stop",
        "truncation_suspected": False,
        "error": error,
        "error_type": error_type,
        "latency_ms": 1,
        "usage": None,
        "timestamp": "2026-08-27T00:00:00+00:00",
        "raw_result_ref": "inline:raw_response",
        "raw_response": raw_response,
    }
    enriched = rr._enrich(
        base,
        unit,
        contract["model"],
        contract["runtime_contract_fingerprint"],
        True,
        EXEC_TYPE_DRY_RUN,
    )
    return ri.seal_new_record(enriched, unit, contract)


def _all_terminal_records(units: list, contract: dict) -> list[dict]:
    return [
        _record(unit, run_index, contract)
        for unit in units
        for run_index in range(contract["n_replications"])
    ]


def _write_checkpoint(root: Path, records: list[dict], contract: dict, units: list) -> None:
    raw, manifest = _paths(root)
    ri.write_resume_checkpoint(raw, manifest, records, contract, units)


def _write_unchecked(root: Path, records: list[dict], contract: dict) -> None:
    raw, manifest_path = _paths(root)
    rr._write_jsonl_atomic(raw, records)
    manifest = ri.build_checkpoint_manifest(contract, records)
    manifest_path.write_text(json.dumps(manifest, sort_keys=True) + "\n")


def _refresh_record(record: dict) -> None:
    record["resume_record_fingerprint"] = ri.resume_record_fingerprint(record)


def _run(root: Path, factory: CountingFactory):
    return rr.run_haiku_batch(
        repo_root=REPO_ROOT,
        provider_factory=factory,
        run_qa=False,
        qa_record=PASS_QA,
        out_dir=root,
        dry_run=True,
        execution_type=EXEC_TYPE_DRY_RUN,
    )


def _assert_integrity_rejected(root: Path) -> dict:
    factory = CountingFactory(sentinel=True)
    with pytest.raises(rr.CheckpointIntegrityError) as exc:
        _run(root, factory)
    assert factory.constructions == 0
    assert exc.value.report["valid"] is False
    return exc.value.report


def test_A_no_checkpoint_fresh_execution_reaches_provider_boundary(tmp_path):
    factory = CountingFactory(sentinel=True)
    with pytest.raises(ProviderBoundaryReached):
        _run(tmp_path, factory)
    assert factory.constructions == 1


def test_B_fully_valid_checkpoint_reuses_all_without_provider(tmp_path, resume_material):
    units, contract = resume_material
    _write_checkpoint(tmp_path, _all_terminal_records(units, contract), contract, units)
    factory = CountingFactory(sentinel=True)
    result = _run(tmp_path, factory)
    accounting = result["resume_accounting"]
    assert factory.constructions == 0
    assert accounting == {
        "checkpoint_status": "VALID_CHECKPOINT",
        "expected_slots": 420,
        "records_loaded": 420,
        "resume_eligible_terminal_records": 420,
        "authenticated_nonterminal_records": 0,
        "legitimately_missing_slots": 0,
        "invalid_records": 0,
        "duplicate_slots": 0,
        "conflicting_slots": 0,
        "unexpected_slots": 0,
        "provider_calls_required": 0,
        "new_calls_completed": 0,
        "final_terminal_coverage": 420,
        "final_classification_valid_count": 420,
        "final_calibration_valid_count": 420,
        "final_analytical_complete": True,
    }


def test_C_valid_partial_checkpoint_calls_only_legitimately_absent_slot(
    tmp_path, resume_material
):
    units, contract = resume_material
    records = _all_terminal_records(units, contract)[:-1]
    _write_checkpoint(tmp_path, records, contract, units)
    factory = CountingFactory()
    result = _run(tmp_path, factory)
    accounting = result["resume_accounting"]
    assert factory.constructions == 1
    assert factory.inner.calls == 1
    assert accounting["expected_slots"] == 420
    assert accounting["resume_eligible_terminal_records"] == 419
    assert accounting["legitimately_missing_slots"] == 1
    assert accounting["provider_calls_required"] == 1
    assert accounting["new_calls_completed"] == 1
    assert accounting["final_terminal_coverage"] == 420


def test_D_same_key_wrong_unit_fingerprint_fails_before_provider(tmp_path, resume_material):
    units, contract = resume_material
    record = _record(units[0], 0, contract)
    record["unit_fingerprint"] = "0" * 64
    _refresh_record(record)
    _write_unchecked(tmp_path, [record], contract)
    report = _assert_integrity_rejected(tmp_path)
    assert any("unit_fingerprint" in error for error in report["errors"])


@pytest.mark.parametrize("field", ["gold_label", "unit_binding_fingerprint"])
def test_E_same_key_wrong_source_or_gold_binding_fails_before_provider(
    tmp_path, resume_material, field
):
    units, contract = resume_material
    record = _record(units[0], 0, contract)
    record[field] = "solid" if field == "gold_label" else "1" * 64
    _refresh_record(record)
    _write_unchecked(tmp_path, [record], contract)
    report = _assert_integrity_rejected(tmp_path)
    assert any(field in error for error in report["errors"])


def test_F_same_key_wrong_runtime_contract_fails_before_provider(tmp_path, resume_material):
    units, contract = resume_material
    record = _record(units[0], 0, contract)
    record["runtime_contract_fingerprint"] = "2" * 64
    _refresh_record(record)
    _write_unchecked(tmp_path, [record], contract)
    report = _assert_integrity_rejected(tmp_path)
    assert any("runtime_contract_fingerprint" in error for error in report["errors"])


def test_G_same_key_wrong_package_prompt_fails_before_provider(tmp_path, resume_material):
    units, contract = resume_material
    record = _record(units[0], 0, contract)
    record["package_fingerprint"] = "3" * 64
    _refresh_record(record)
    _write_unchecked(tmp_path, [record], contract)
    report = _assert_integrity_rejected(tmp_path)
    assert any("package_fingerprint" in error for error in report["errors"])


@pytest.mark.parametrize(
    ("field", "value"),
    [("execution_type", "independent_model_adjudication"), ("dry_run", False)],
)
def test_H_same_key_wrong_execution_mode_fails_before_provider(
    tmp_path, resume_material, field, value
):
    units, contract = resume_material
    record = _record(units[0], 0, contract)
    record[field] = value
    _refresh_record(record)
    _write_unchecked(tmp_path, [record], contract)
    report = _assert_integrity_rejected(tmp_path)
    assert any(field in error for error in report["errors"])


def test_I_raw_response_changed_without_hash_fails_before_provider(tmp_path, resume_material):
    units, contract = resume_material
    record = _record(units[0], 0, contract)
    record["raw_response"] = "changed"
    _write_unchecked(tmp_path, [record], contract)
    report = _assert_integrity_rejected(tmp_path)
    assert any("content/hash mismatch" in error for error in report["errors"])


def test_J_raw_content_and_hash_changed_without_record_fingerprint_fails(
    tmp_path, resume_material
):
    units, contract = resume_material
    record = _record(units[0], 0, contract)
    record["raw_response"] = "changed together"
    record["raw_response_sha256"] = ri.rc._sha256_hex(b"changed together")
    _write_unchecked(tmp_path, [record], contract)
    report = _assert_integrity_rejected(tmp_path)
    assert any("resume-record fingerprint mismatch" in error for error in report["errors"])


@pytest.mark.parametrize("fingerprint", ["bad", "0" * 64])
def test_K_record_fingerprint_malformed_or_mismatched_fails(
    tmp_path, resume_material, fingerprint
):
    units, contract = resume_material
    record = _record(units[0], 0, contract)
    record["resume_record_fingerprint"] = fingerprint
    _write_unchecked(tmp_path, [record], contract)
    report = _assert_integrity_rejected(tmp_path)
    assert any("resume-record fingerprint" in error for error in report["errors"])


@pytest.mark.parametrize(
    "field",
    [
        "checkpoint_id",
        "checkpoint_namespace",
        "checkpoint_storage_identity",
        "execution_manifest_fingerprint",
        "call_plan_fingerprint",
    ],
)
def test_L_wrong_run_checkpoint_manifest_or_call_plan_binding_fails(
    tmp_path, resume_material, field
):
    units, contract = resume_material
    record = _record(units[0], 0, contract)
    _write_checkpoint(tmp_path, [record], contract, units)
    _, manifest_path = _paths(tmp_path)
    manifest = json.loads(manifest_path.read_text())
    manifest[field] = "wrong-binding"
    manifest["checkpoint_fingerprint"] = ri._checkpoint_fingerprint(manifest)
    manifest_path.write_text(json.dumps(manifest, sort_keys=True) + "\n")
    report = _assert_integrity_rejected(tmp_path)
    assert any(field in error for error in report["errors"])


def test_M_missing_required_provenance_is_non_resumable(tmp_path, resume_material):
    units, contract = resume_material
    record = _record(units[0], 0, contract)
    del record["unit_binding_fingerprint"]
    _refresh_record(record)
    _write_unchecked(tmp_path, [record], contract)
    report = _assert_integrity_rejected(tmp_path)
    assert any("missing required record provenance" in error for error in report["errors"])


@pytest.mark.parametrize("conflicting", [False, True])
def test_N_duplicate_or_conflicting_slot_fails_before_provider(
    tmp_path, resume_material, conflicting
):
    units, contract = resume_material
    first = _record(units[0], 0, contract)
    second = copy.deepcopy(first)
    if conflicting:
        second["label"] = "solid" if first["label"] != "solid" else "overclaim"
        second["label_correct"] = second["label"] == units[0].gold_label
        _refresh_record(second)
    _write_unchecked(tmp_path, [first, second], contract)
    report = _assert_integrity_rejected(tmp_path)
    assert report["duplicate_slots"] == 1
    assert report["conflicting_slots"] == int(conflicting)


@pytest.mark.parametrize("damage", ["unexpected_slot", "mixed_contract"])
def test_O_unexpected_slot_or_mixed_contract_fails_before_provider(
    tmp_path, resume_material, damage
):
    units, contract = resume_material
    first = _record(units[0], 0, contract)
    if damage == "unexpected_slot":
        first["unit_id"] = "P7A-UNEXPECTED-999"
        _refresh_record(first)
        records = [first]
    else:
        second = _record(units[1], 0, contract)
        second["checkpoint_contract_fingerprint"] = "4" * 64
        _refresh_record(second)
        records = [first, second]
    _write_unchecked(tmp_path, records, contract)
    report = _assert_integrity_rejected(tmp_path)
    assert report["unexpected_slots"] == int(damage == "unexpected_slot")


@pytest.mark.parametrize(
    "damage",
    [
        "empty",
        "malformed",
        "truncated",
        "partial",
        "unknown_checkpoint_schema",
        "unknown_record_schema",
        "checkpoint_fingerprint",
    ],
)
def test_P_malformed_truncated_or_partial_checkpoint_fails(
    tmp_path, resume_material, damage
):
    units, contract = resume_material
    record = _record(units[0], 0, contract)
    _write_checkpoint(tmp_path, [record], contract, units)
    raw, manifest_path = _paths(tmp_path)
    if damage == "empty":
        raw.write_text("")
        manifest_path.write_text("")
    elif damage == "malformed":
        raw.write_text("{not-json}\n")
    elif damage == "truncated":
        raw.write_text('{"model": "truncated"\n')
    elif damage == "partial":
        raw.write_text(json.dumps({"model": contract["model"], "unit_id": units[0].unit_id}) + "\n")
    elif damage == "unknown_checkpoint_schema":
        manifest = json.loads(manifest_path.read_text())
        manifest["checkpoint_schema_version"] = "unknown/v999"
        manifest["checkpoint_fingerprint"] = ri._checkpoint_fingerprint(manifest)
        manifest_path.write_text(json.dumps(manifest, sort_keys=True) + "\n")
    elif damage == "unknown_record_schema":
        record["resume_record_schema_version"] = "unknown/v999"
        _refresh_record(record)
        _write_unchecked(tmp_path, [record], contract)
    else:
        manifest = json.loads(manifest_path.read_text())
        manifest["checkpoint_fingerprint"] = "0" * 64
        manifest_path.write_text(json.dumps(manifest, sort_keys=True) + "\n")
    report = _assert_integrity_rejected(tmp_path)
    assert report["status"] == "INVALID_CHECKPOINT"


def test_P_unreadable_checkpoint_is_controlled_no_go(tmp_path, resume_material, monkeypatch):
    units, contract = resume_material
    record = _record(units[0], 0, contract)
    _write_checkpoint(tmp_path, [record], contract, units)
    raw, _ = _paths(tmp_path)
    original = ri.Path.read_bytes

    def controlled_unreadable(path):
        if path == raw:
            raise PermissionError("controlled unreadable checkpoint")
        return original(path)

    monkeypatch.setattr(ri.Path, "read_bytes", controlled_unreadable)
    report = _assert_integrity_rejected(tmp_path)
    assert any("unreadable" in error for error in report["errors"])


def test_Q_wrong_prediction_with_valid_provenance_remains_reusable(
    tmp_path, resume_material
):
    units, contract = resume_material
    records = _all_terminal_records(units, contract)
    wrong = "solid" if units[0].gold_label != "solid" else "overclaim"
    records[0] = _record(units[0], 0, contract, label=wrong)
    _write_checkpoint(tmp_path, records, contract, units)
    factory = CountingFactory(sentinel=True)
    result = _run(tmp_path, factory)
    resumed = next(
        record for record in result["records"]
        if record["unit_id"] == units[0].unit_id and record["run_index"] == 0
    )
    assert factory.constructions == 0
    assert resumed["label"] == wrong
    assert resumed["label_correct"] is False
    assert result["resume_accounting"]["resume_eligible_terminal_records"] == 420


def test_R_provenance_valid_terminal_parser_failure_is_reused_without_semantic_retry(
    tmp_path, resume_material
):
    units, contract = resume_material
    records = _all_terminal_records(units, contract)
    records[0] = _record(
        units[0], 0, contract, label=None, confidence=None, confidence_state=MISSING,
        parse_ok=False, raw_response="terminal malformed semantic output"
    )
    _write_checkpoint(tmp_path, records, contract, units)
    factory = CountingFactory(sentinel=True)
    result = _run(tmp_path, factory)
    assert factory.constructions == 0
    assert result["resume_accounting"]["final_terminal_coverage"] == 420
    assert result["resume_accounting"]["final_classification_valid_count"] == 419
    assert result["resume_accounting"]["final_calibration_valid_count"] == 419
    assert result["resume_accounting"]["final_analytical_complete"] is False


def test_S_valid_label_invalid_confidence_is_reused_without_semantic_retry(
    tmp_path, resume_material
):
    units, contract = resume_material
    records = _all_terminal_records(units, contract)
    records[0] = _record(
        units[0], 0, contract, confidence=None, confidence_state=INVALID
    )
    _write_checkpoint(tmp_path, records, contract, units)
    factory = CountingFactory(sentinel=True)
    result = _run(tmp_path, factory)
    assert factory.constructions == 0
    assert result["resume_accounting"]["final_classification_valid_count"] == 420
    assert result["resume_accounting"]["final_calibration_valid_count"] == 419
    assert result["resume_accounting"]["final_analytical_complete"] is False


def test_T_authenticated_nonterminal_provider_failure_preserves_retry_contract(
    tmp_path, resume_material
):
    units, contract = resume_material
    records = _all_terminal_records(units, contract)
    records[-1] = _record(
        units[-1], 4, contract, label=None, confidence=None, confidence_state=MISSING,
        parse_ok=False, error="timeout", error_type="provider_error", raw_response=""
    )
    _write_checkpoint(tmp_path, records, contract, units)
    factory = CountingFactory()
    result = _run(tmp_path, factory)
    assert factory.constructions == 1
    assert factory.inner.calls == 1
    assert result["resume_accounting"]["authenticated_nonterminal_records"] == 1
    assert result["resume_accounting"]["provider_calls_required"] == 1
    assert result["resume_accounting"]["new_calls_completed"] == 1
    assert result["resume_accounting"]["final_terminal_coverage"] == 420


def test_U_legacy_record_is_readable_but_not_prospectively_resumable(
    tmp_path, resume_material
):
    units, contract = resume_material
    raw, _ = _paths(tmp_path)
    raw.parent.mkdir(parents=True)
    legacy = {
        "model": contract["model"],
        "unit_id": units[0].unit_id,
        "run_index": 0,
        "label": units[0].gold_label,
        "error": None,
    }
    rr._write_jsonl_atomic(raw, [legacy])
    assert rr._load_jsonl(raw) == [legacy]
    report = _assert_integrity_rejected(tmp_path)
    assert report["status"] == "LEGACY_CHECKPOINT_NON_RESUMABLE"
    assert report["legacy_checkpoint"] is True


def test_V_execution_source_change_after_checkpoint_creation_fails_closed(
    tmp_path, resume_material, monkeypatch
):
    units, contract = resume_material
    _write_checkpoint(tmp_path, [_record(units[0], 0, contract)], contract, units)
    monkeypatch.setattr(ri, "_execution_source_fingerprint", lambda root: "f" * 64)
    report = _assert_integrity_rejected(tmp_path)
    assert any("execution_source_fingerprint" in error for error in report["errors"])
