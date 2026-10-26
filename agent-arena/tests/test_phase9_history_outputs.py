"""Current review routing governs output while historical carriers stay intact."""

import json
from copy import deepcopy

import pytest

from agent_arena.evaluator import evaluate_run
from agent_arena.phase9_pipeline import refresh_run_phase9
from agent_arena.phase9_runtime import OfflineReviewProvider, submit_human_review
from agent_arena.reporter import generate_report
from agent_arena.reporting import generate_client_report
from agent_arena.runner import run_agent
from agent_arena.schemas import DIAGNOSTIC_WEIGHTS
from tests.test_phase8_pipeline import task_for
from tests.test_phase8_taxonomy import taxonomy_record


@pytest.fixture
def approved_case(tmp_path):
    payload = taxonomy_record().model_dump(mode="json")
    task = task_for(payload["phase8"]["original_claim"], payload["evidence"][0]["text"])
    raw = json.dumps({"final_answer": "solid", "confidence": 0.82, "forensic_record": payload})
    provider = OfflineReviewProvider(raw)
    original = evaluate_run(task, "output-history", [run_agent(provider, task)])
    assert original.results[0].agent_result.phase8["derived_label"] == "solid"
    approved = submit_human_review(
        original, base_dir=tmp_path,
        selected_position_id=original.metadata["phase9"]["positions"][0]["position_id"],
        reviewer_provenance="Explicit offline host", reason="Review complete bound history",
    )
    for evaluated in approved.results:
        evaluated.failures = []
        evaluated.failure_modes = []
        for name in DIAGNOSTIC_WEIGHTS:
            setattr(evaluated.scores, name, 1.0)
    return original, approved, provider


def test_invalid_current_history_cannot_produce_positive_client_or_internal_conclusion(approved_case):
    original, approved, provider = approved_case
    incoming = approved.model_copy(update={"metadata": deepcopy(original.metadata)}, deep=True)
    before = incoming.model_dump(mode="json")
    checked = refresh_run_phase9(incoming)
    assert checked.metadata["phase9"]["route"] == "UNRESOLVED"
    assert checked.metadata["phase9"]["history_validation"] == "invalid"
    assert checked.results[0].agent_result.phase9 == approved.results[0].agent_result.phase9
    client, internal = generate_client_report(incoming), generate_report(incoming)
    for text in (client, internal):
        assert "UNRESOLVED" in text and "UNVALIDATED HISTORY" in text
    assert "🟢 PASS" not in client
    assert "Analysis appears sound" not in client
    assert "No significant changes required" not in client
    assert "No blocking issues found" not in client
    assert "Resolve the Phase-9 case review" in client
    assert "All agents completed without critical failure modes" not in internal
    assert "Phase-9 case review or history validation remains unresolved" in internal
    assert incoming.model_dump(mode="json") == before
    assert len(provider.requests) == 1


def test_valid_adjudicated_case_keeps_eligible_positive_output(approved_case):
    _, approved, provider = approved_case
    before = approved.model_dump(mode="json")
    client, internal = generate_client_report(approved), generate_report(approved)
    assert "AUTO_RESOLVABLE" in client and "review `adjudicated`" in client
    assert "🟢 PASS" in client and "No significant changes required" in client
    assert "All agents completed without critical failure modes" in internal
    assert "UNVALIDATED HISTORY" not in client
    assert approved.model_dump(mode="json") == before
    assert len(provider.requests) == 1
