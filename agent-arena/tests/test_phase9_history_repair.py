"""Continuation regressions: all persisted history carriers precede adjudication."""

from copy import deepcopy

import pytest

from agent_arena.audit_trail import read_decisions
from agent_arena.evaluator import evaluate_run
from agent_arena.phase9_pipeline import refresh_run_phase9
from agent_arena.phase9_review import case_key
from agent_arena.phase9_runtime import (
    OfflineReviewProvider, execute_review, replay_review, submit_human_review,
)
from agent_arena.runner import run_agent
from tests.test_phase9_runtime import fixture


@pytest.fixture
def reviewed_case(tmp_path):
    task, positive = fixture("supported")
    _, negative = fixture("contradicted")
    _, unknown = fixture("unknown")
    original = evaluate_run(task, "originals", [
        run_agent(OfflineReviewProvider(positive), task),
        run_agent(OfflineReviewProvider(negative), task),
    ])
    provider = OfflineReviewProvider(unknown)
    reviewed = execute_review(original, provider, base_dir=tmp_path / "source",
                              authorized=True, budget_calls=1)
    assert len(reviewed.metadata["phase9"]["positions"]) == 3
    assert len(provider.requests) == 1
    return original, reviewed, provider


def files(base):
    return {str(p.relative_to(base)): p.read_bytes() for p in base.rglob("*")
            if p.is_file() and p.suffix != ".lock"}


def submit(record, base):
    return submit_human_review(
        record, base_dir=base,
        selected_position_id=record.metadata["phase9"]["positions"][0]["position_id"],
        reviewer_provenance="Explicit offline host reviewer", reason="All positions reviewed",
    )


def assert_rejected_unchanged(record, base):
    before, disk = record.model_dump(mode="json"), files(base)
    with pytest.raises(ValueError):
        submit(record, base)
    assert record.model_dump(mode="json") == before
    assert files(base) == disk


@pytest.mark.parametrize("sidecar", [False, True])
def test_older_metadata_cannot_discard_newer_result_history(reviewed_case, tmp_path, sidecar):
    original, reviewed, provider = reviewed_case
    base = tmp_path / "destination"
    if sidecar:
        # Existing sidecar is older too; neither may displace the submitted review.
        execute_review(original, base_dir=base)
    incoming = reviewed.model_copy(update={"metadata": deepcopy(original.metadata)})
    assert_rejected_unchanged(incoming, base)
    assert len(provider.requests) == 1


@pytest.mark.parametrize("sidecar", [False, True])
def test_consistent_executed_import_human_and_replay_keep_all_layers(reviewed_case, tmp_path, sidecar):
    _, reviewed, provider = reviewed_case
    base = tmp_path / "destination"
    if sidecar:
        execute_review(reviewed, provider, base_dir=base, authorized=True, budget_calls=1)
    before = reviewed.model_dump(mode="json")
    result = submit(reviewed, base)
    data = result.metadata["phase9"]
    assert data["route"] == "AUTO_RESOLVABLE" and data["review_state"] == "adjudicated"
    assert data["positions"] == before["metadata"]["phase9"]["positions"]
    assert data["attempts"] == before["metadata"]["phase9"]["attempts"]
    assert data["adjudications"][:-1] == before["metadata"]["phase9"]["adjudications"]
    assert [d["reviewer_type"] for d in data["adjudications"]] == ["model", "human"]
    for _ in range(2):
        replay = replay_review(reviewed.task, base_dir=base)
        assert replay.metadata["phase9"] == data
        assert all(r.agent_result.phase9 == data for r in replay.results)
    assert len(read_decisions(base)) == 2
    assert len(provider.requests) == 1
    assert reviewed.model_dump(mode="json") == before


def test_valid_older_result_subset_is_covered_by_complete_metadata(reviewed_case, tmp_path):
    original, reviewed, provider = reviewed_case
    incoming = reviewed.model_copy(deep=True)
    incoming.results[0].agent_result.phase9 = deepcopy(original.metadata["phase9"])
    result = submit(incoming, tmp_path / "covered")
    assert result.metadata["phase9"]["positions"] == reviewed.metadata["phase9"]["positions"]
    assert len(result.metadata["phase9"]["adjudications"]) == 2
    assert len(provider.requests) == 1


@pytest.mark.parametrize("sidecar", [False, True])
@pytest.mark.parametrize("change", [
    "position_identity", "position_content", "position_provenance", "source_binding",
    "attempt_provenance", "attempt_packet", "extra_receipt", "decision_content", "conflict_content",
    "case_identity", "contract_version",
])
def test_conflicting_carrier_content_is_rejected_before_any_write(reviewed_case, tmp_path, sidecar, change):
    _, reviewed, _ = reviewed_case
    base = tmp_path / "destination"
    if sidecar:
        execute_review(reviewed, base_dir=base)
    incoming = reviewed.model_copy(deep=True)
    # Deliberately change the second carrier: choosing the first alone is unsafe.
    carrier = deepcopy(incoming.results[-1].agent_result.phase9)
    incoming.results[-1].agent_result.phase9 = carrier
    if change == "position_identity":
        carrier["positions"][0]["position_id"] = "copied-wrong-id"
    elif change == "position_content":
        carrier["positions"][0]["claim_id"] = "different-claim"
    elif change == "position_provenance":
        carrier["positions"][0]["provider"] = "different-reviewer"
    elif change == "source_binding":
        carrier["positions"][0]["forensic_record"]["evidence"][0]["source_id"] = "elsewhere"
    elif change == "attempt_provenance":
        carrier["attempts"][0]["code_version"] = "different-execution-version"
    elif change == "attempt_packet":
        carrier["attempts"][0]["packet_sha256"] = "different-challenge"
    elif change == "extra_receipt":
        carrier["attempts"].append({"kind": "stability", "status": "denied", "reason": "No grant"})
    elif change == "decision_content":
        carrier["adjudications"][0]["reason"] = "Different justification under the same decision ID"
    elif change == "conflict_content":
        carrier["conflicts"][0]["material"] = False
    else:
        carrier["case_id" if change == "case_identity" else "contract_version"] = "different-binding"
    assert_rejected_unchanged(incoming, base)


def test_same_raw_bytes_do_not_hide_changed_original_provider(reviewed_case, tmp_path):
    _, reviewed, _ = reviewed_case
    incoming = reviewed.model_copy(deep=True)
    incoming.results[0].agent_result.provider = "other-provider-same-response"
    assert_rejected_unchanged(incoming, tmp_path / "destination")


def test_refresh_and_replay_preserve_divergent_carriers_without_success(reviewed_case, tmp_path):
    original, reviewed, provider = reviewed_case
    incoming = reviewed.model_copy(update={"metadata": deepcopy(original.metadata)})
    before = incoming.model_dump(mode="json")
    refreshed = refresh_run_phase9(incoming)
    assert refreshed.metadata["phase9"]["history_validation"] == "invalid"
    assert refreshed.metadata["phase9"]["route"] == "UNRESOLVED"
    assert refreshed.metadata["phase9"]["execution_status"] != "completed"
    assert [r.agent_result.phase9 for r in refreshed.results] == [r.agent_result.phase9 for r in incoming.results]
    base = tmp_path / "persisted-import"
    path = base / "phase9" / f"{case_key(incoming.task)}.json"
    path.parent.mkdir(parents=True)
    path.write_text(incoming.model_dump_json())
    disk = files(base)
    replay = replay_review(incoming.task, base_dir=base)
    assert replay.metadata["phase9"]["route"] == "UNRESOLVED"
    assert [r.agent_result.phase9 for r in replay.results] == [r.agent_result.phase9 for r in incoming.results]
    assert files(base) == disk
    assert incoming.model_dump(mode="json") == before
    assert len(provider.requests) == 1


def test_stored_result_carrier_is_checked_even_with_consistent_incoming(reviewed_case, tmp_path):
    original, reviewed, _ = reviewed_case
    base = tmp_path / "destination"
    divergent = reviewed.model_copy(update={"metadata": deepcopy(original.metadata)})
    path = base / "phase9" / f"{case_key(reviewed.task)}.json"
    path.parent.mkdir(parents=True)
    path.write_text(divergent.model_dump_json())
    assert_rejected_unchanged(original, base)


def test_partial_result_carrier_population_without_metadata_keeps_executed_history(reviewed_case, tmp_path):
    _, reviewed, provider = reviewed_case
    incoming = reviewed.model_copy(deep=True)
    incoming.metadata = {}
    incoming.results[0].agent_result.phase9 = {}
    selected = reviewed.metadata["phase9"]["positions"][0]["position_id"]
    result = submit_human_review(incoming, base_dir=tmp_path / "partial-carriers",
                                 selected_position_id=selected, reviewer_provenance="Offline host",
                                 reason="Full history supplied in the other result carrier")
    assert result.metadata["phase9"]["positions"] == reviewed.metadata["phase9"]["positions"]
    assert len(result.metadata["phase9"]["adjudications"]) == 2
    assert len(provider.requests) == 1
