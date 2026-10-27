"""Bounded offline execution, lease and persisted status integration regressions."""

import fcntl
import json
from pathlib import Path

import pytest

from inspektorium.audit.execution.evaluator import evaluate_run
from inspektorium.audit.execution.runner import run_agent
from inspektorium.audit.forensics.forensic_report import (
    build_forensic_report,
    render_executive_summary,
    render_forensic_report_markdown,
)
from inspektorium.audit.review.pipeline import refresh_run_phase9
from inspektorium.audit.review.routing import case_key
from inspektorium.audit.review.runtime import (
    OfflineReviewProvider,
    execute_review,
    replay_review,
)
from inspektorium.audit.reports.reporter import generate_report
from inspektorium.audit.execution.run_library import run_single
from inspektorium.audit.schemas import RunRecord
from tests.unit.test_forensic_report import base_input
from tests.unit.test_review_runtime import fixture


def run_record(state="unknown", *, two_evidence=False):
    task, raw = fixture(state, two_evidence=two_evidence)
    result = run_agent(OfflineReviewProvider(raw), task)
    record = evaluate_run(task, "original-run", [result])
    assert record.results[0].agent_result.phase8["technical_status"] == "completed"
    assert record.results[0].agent_result.phase8["composite_state"] == state
    return record, raw


def ledger_at(directory):
    return json.loads(next((directory / "phase9").glob("*.ledger.json")).read_text())


def test_one_call_grant_cannot_fund_stability_after_completed_counterreview(tmp_path):
    record, raw = run_record(two_evidence=True)
    provider = OfflineReviewProvider(raw)
    execute_review(record, provider, base_dir=tmp_path, authorized=True, budget_calls=1)
    result = execute_review(
        record,
        provider,
        base_dir=tmp_path,
        authorized=True,
        budget_calls=1,
        kind="stability",
    )
    assert len(provider.requests) == 1
    assert len(ledger_at(tmp_path)["attempts"]) == 1
    data = result.metadata["phase9"]
    assert data["route"] == "UNRESOLVED"
    assert data["attempts"][-1]["status"] == "denied"
    assert "grant exhausted" in data["attempts"][-1]["reason"]
    assert len(data["positions"]) == 2


@pytest.mark.parametrize(
    "authorized,budget,missing",
    [
        (False, 2, False),
        (True, 0, False),
        (True, 1, True),
    ],
)
def test_absent_authorization_budget_or_reviewer_never_crosses_provider_boundary(
    tmp_path, authorized, budget, missing
):
    record, raw = run_record()
    provider = OfflineReviewProvider(raw)
    result = execute_review(
        record,
        None if missing else provider,
        base_dir=tmp_path,
        authorized=authorized,
        budget_calls=budget,
    )
    assert provider.requests == []
    assert not list((tmp_path / "phase9").glob("*.ledger.json"))
    assert result.metadata["phase9"]["route"] == "UNRESOLVED"
    assert result.metadata["phase9"]["execution_status"] == "not_executed"
    assert (
        replay_review(record.task, base_dir=tmp_path).metadata["phase9"]["route"]
        == "UNRESOLVED"
    )


def test_material_stability_flip_retains_three_positions_and_never_exceeds_two_calls(
    tmp_path,
):
    record, original = run_record(two_evidence=True)
    _, positive = fixture("supported", two_evidence=True)
    _, negative = fixture("contradicted", two_evidence=True)
    counter, stability = (
        OfflineReviewProvider(positive),
        OfflineReviewProvider(negative),
    )
    first = execute_review(
        record, counter, base_dir=tmp_path, authorized=True, budget_calls=2
    )
    final = execute_review(
        record,
        stability,
        base_dir=tmp_path,
        authorized=True,
        budget_calls=2,
        kind="stability",
    )
    data = final.metadata["phase9"]
    assert len(counter.requests) == len(stability.requests) == 1
    assert [p["origin"] for p in data["positions"]] == [
        "original",
        "model_review",
        "stability",
    ]
    assert [p["agent_result"]["raw_output"] for p in data["positions"]] == [
        original,
        positive,
        negative,
    ]
    assert [p["phase8"]["composite_state"] for p in data["positions"]] == [
        "unknown",
        "supported",
        "contradicted",
    ]
    review_ids = {p["position_id"] for p in data["positions"][1:]}
    assert any(
        set(c["provenance"]) == review_ids and c["material"] for c in data["conflicts"]
    )
    assert data["route"] == "HUMAN_REVIEW_REQUIRED" and not data.get(
        "final_position_id"
    )
    assert len(data["adjudications"]) == 2
    assert len(ledger_at(tmp_path)["attempts"]) == 2
    assert first.metadata["phase9"]["positions"] == data["positions"][:2]
    for kind in ("counterreview", "stability"):
        execute_review(
            record.model_copy(update={"run_id": "new-run"}),
            stability,
            base_dir=tmp_path,
            authorized=True,
            budget_calls=2,
            kind=kind,
        )
    assert len(counter.requests) + len(stability.requests) == 2
    loaded = replay_review(record.task, base_dir=tmp_path)
    assert loaded.metadata["phase9"]["conflicts"] == data["conflicts"]


@pytest.mark.parametrize("invalid", [False, True])
def test_rejected_variant_is_recorded_once_and_cannot_be_resampled(tmp_path, invalid):
    record, raw = run_record(two_evidence=invalid)
    provider = OfflineReviewProvider(raw)
    execute_review(record, provider, base_dir=tmp_path, authorized=True, budget_calls=2)
    first = execute_review(
        record,
        provider,
        base_dir=tmp_path,
        authorized=True,
        budget_calls=2,
        kind="stability",
        variant={"original_claim": "changed"} if invalid else None,
    )
    assert first.metadata["phase9"]["attempts"][-1]["status"] == "rejected"
    assert len(provider.requests) == 1
    again = execute_review(
        record,
        provider,
        base_dir=tmp_path,
        authorized=True,
        budget_calls=2,
        kind="stability",
    )
    assert again.metadata["phase9"]["attempts"] == first.metadata["phase9"]["attempts"]
    assert len(provider.requests) == 1
    assert len(ledger_at(tmp_path)["attempts"]) == 1
    assert again.metadata["phase9"]["route"] == "UNRESOLVED"


def test_os_case_lease_blocks_concurrent_review_without_reserving_or_calling(tmp_path):
    record, raw = run_record()
    directory = tmp_path / "phase9"
    directory.mkdir()
    provider = OfflineReviewProvider(raw)
    with (directory / f"{case_key(record.task)}.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            with pytest.raises(ValueError, match="concurrent review"):
                execute_review(
                    record, provider, base_dir=tmp_path, authorized=True, budget_calls=2
                )
            assert provider.requests == []
            assert not list(directory.glob("*.json"))
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)
    execute_review(record, provider, base_dir=tmp_path, authorized=True, budget_calls=1)
    assert len(provider.requests) == 1


@pytest.mark.parametrize(
    "review_raw",
    [
        "not JSON",
        "{}",
        json.dumps(
            {
                "final_answer": "solid",
                "confidence": 0.8,
                "forensic_record": {
                    "evidence": [None],
                    "phase8": {"propositions": "malformed"},
                },
            }
        ),
    ],
)
def test_malformed_review_is_a_consumed_failed_attempt_with_raw_audit_and_no_retry(
    tmp_path, review_raw
):
    record, original = run_record()
    provider = OfflineReviewProvider(review_raw)
    result = execute_review(
        record, provider, base_dir=tmp_path, authorized=True, budget_calls=2
    )
    data = result.metadata["phase9"]
    assert len(provider.requests) == 1
    assert data["execution_status"] == "failed"
    assert data["route"] == "UNRESOLVED"
    assert data["attempts"][-1]["status"] == "failed"
    assert data["adjudications"][-1]["outcome"] == "failed"
    assert [p["agent_result"]["raw_output"] for p in data["positions"]] == [
        original,
        review_raw,
    ]
    assert len(ledger_at(tmp_path)["attempts"]) == 1
    execute_review(record, provider, base_dir=tmp_path, authorized=True, budget_calls=2)
    replay_review(record.task, base_dir=tmp_path)
    assert len(provider.requests) == 1


def test_library_and_runrecord_roundtrip_preserve_raw_and_separate_phase_statuses(
    tmp_path,
):
    record, raw = run_record()
    provider = OfflineReviewProvider(raw)
    row = run_single(
        provider, Path("offline-case.yaml"), record.task, 1, "offline-library"
    )
    loaded_row = json.loads(json.dumps(row))
    assert loaded_row["raw_output"] == raw
    assert loaded_row["forensic_record"] == json.loads(raw)["forensic_record"]
    assert loaded_row["phase8"]["composite_state"] == "unknown"
    assert loaded_row["phase9"]["execution_status"] == "not_executed"
    assert loaded_row["phase9"]["route"] == "REVIEW_RECOMMENDED"
    reviewed = execute_review(
        record, provider, base_dir=tmp_path, authorized=True, budget_calls=1
    )
    decoded = RunRecord.model_validate_json(reviewed.model_dump_json())
    refreshed = refresh_run_phase9(decoded)
    assert (
        refreshed.metadata["phase9"]["positions"]
        == reviewed.metadata["phase9"]["positions"]
    )
    assert refreshed.results[0].agent_result.raw_output == raw
    calls = len(provider.requests)
    rendered = generate_report(refreshed)
    assert "HUMAN_REVIEW_REQUIRED" in rendered and "execution `completed`" in rendered
    assert len(provider.requests) == calls


def test_legacy_forensic_report_ignores_forged_review_cache_and_reports_not_executed():
    report = build_forensic_report(base_input())
    report["phase9"] = {
        "route": "AUTO_RESOLVABLE",
        "review_state": "adjudicated",
        "technical_status": "completed",
        "execution_status": "completed",
    }
    for render in (render_forensic_report_markdown, render_executive_summary):
        text = render(report)
        assert "Phase 9 review" in text
        assert "execution `not_executed`" in text and "UNRESOLVED" in text
        assert "review `adjudicated`" not in text
