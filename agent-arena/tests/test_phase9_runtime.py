"""Offline parser/runner/persistence/budget regressions, separate from acceptance."""
import json
import pytest
from copy import deepcopy


from agent_arena.evaluator import evaluate_run
from agent_arena.phase9_pipeline import refresh_run_phase9
from agent_arena.phase9_runtime import (
    OfflineReviewProvider, build_challenge, execute_review, replay_review,
    stability_variant, validate_variant, submit_human_review,
)
from agent_arena.phase9_review import position_from_result
from agent_arena.reporting import generate_client_report
from agent_arena.runner import run_agent
from tests.phase8_case_factory import raw_record
from tests.test_phase8_pipeline import task_for


def fixture(state="supported", *, two_evidence=False):
    claim, context, payload = raw_record(endpoint="endpoint Delta", intervention="agent Gamma")
    if two_evidence:
        second = deepcopy(payload["evidence"][0])
        second["evidence_id"] = "e2"
        payload["evidence"].append(second)
        binding = deepcopy(payload["phase8"]["propositions"][0]["evidence_bindings"][0])
        binding.update(binding_id="b2", evidence_id="e2")
        payload["phase8"]["propositions"][0]["evidence_bindings"].append(binding)
        description = deepcopy(payload["phase8"]["evidence_descriptions"][0])
        description["evidence_id"] = "e2"
        payload["phase8"]["evidence_descriptions"].append(description)
        payload["findings"][0]["supporting_evidence_ids"].append("e2")
        payload["client_findings"][0]["referenced_evidence_ids"].append("e2")
    prop = payload["phase8"]["propositions"][0]
    prop["reported_verdict"] = state
    payload["phase8"]["transformations"][-1]["asserted_state"] = state
    if state == "unknown":
        prop["uncertainty"] = ["Unresolved interpretation"]
    if state == "contradicted":
        for binding in prop["evidence_bindings"]:
            binding["observation"] = "contradiction"
        for evidence in payload["evidence"]:
            evidence["role"] = "contradictory"
        payload["findings"][0].update(supporting_evidence_ids=[],
                                      contrary_evidence_ids=[e["evidence_id"] for e in payload["evidence"]])
    raw = json.dumps({"final_answer": "solid", "confidence": .82, "forensic_record": payload})
    return task_for(claim, context), raw


def run_record(state="unknown", *, two_evidence=False):
    task, raw = fixture(state, two_evidence=two_evidence)
    result = run_agent(OfflineReviewProvider(raw), task)
    assert result.error is None, result.error
    assert result.phase8["technical_status"] == "completed", result.phase8
    return evaluate_run(task, "original-run", [result]), raw


def test_stable_case_no_extra_calls_and_roundtrip_output(tmp_path):
    record, raw = run_record("supported")
    reviewer = OfflineReviewProvider(raw)
    outcome = execute_review(record, reviewer, base_dir=tmp_path, authorized=True, budget_calls=2)
    assert outcome.metadata["phase9"]["route"] == "AUTO_RESOLVABLE"
    assert reviewer.requests == []
    assert "Phase 9" in generate_client_report(outcome)
    assert record.results[0].agent_result.raw_output == raw


def test_blind_challenge_full_packet_and_no_task_gold():
    record, raw = run_record(two_evidence=True)
    task = record.task.model_copy(update={"gold_label": "secret-first-label"})
    position = position_from_result(task, record.results[0].agent_result, record.run_id)
    packet = build_challenge(task, position)
    assert packet["original_claim"] == task.prompt
    assert len(packet["evidence"]) == 2
    text = json.dumps(packet)
    for forbidden in ("final_answer", "reported_verdict", "confidence", "Unresolved interpretation",
                      "supporting", "secret-first-label"):
        assert forbidden not in text
    assert validate_variant(packet, stability_variant(packet)) is None
    mutated = stability_variant(packet)
    mutated["original_claim"] += " changed"
    assert "Rejected" in validate_variant(packet, mutated)


def test_budget_zero_is_unexecuted_and_replay_never_calls(tmp_path):
    record, raw = run_record()
    reviewer = OfflineReviewProvider(raw)
    original = record.model_dump()
    denied = execute_review(record, reviewer, base_dir=tmp_path)
    data = denied.metadata["phase9"]
    assert data["route"] == "UNRESOLVED"
    assert data["execution_status"] == "not_executed"
    assert data["triggers"]
    assert reviewer.requests == []
    replay = replay_review(record.task, base_dir=tmp_path)
    assert replay.metadata["phase9"]["route"] == "UNRESOLVED"
    assert record.model_dump() == original


def test_one_counterreview_one_stability_failed_attempt_consumed(tmp_path):
    record, raw = run_record(two_evidence=True)
    failed = OfflineReviewProvider(error="synthetic reviewer failure")
    first = execute_review(record, failed, base_dir=tmp_path, authorized=True, budget_calls=2)
    assert len(failed.requests) == 1
    assert first.metadata["phase9"]["execution_status"] == "failed"
    again = execute_review(record.model_copy(update={"run_id": "another-run"}), failed,
                           base_dir=tmp_path, authorized=True, budget_calls=2)
    assert len(failed.requests) == 1
    assert len(again.metadata["phase9"]["positions"]) == 2
    stability = OfflineReviewProvider(raw)
    second = execute_review(record, stability, base_dir=tmp_path, authorized=True,
                            budget_calls=2, kind="stability")
    assert len(stability.requests) == 1
    assert len(second.metadata["phase9"]["positions"]) == 3
    ledger = json.loads(next((tmp_path / "phase9").glob("*.ledger.json")).read_text())
    assert len(ledger["attempts"]) == 2
    assert ledger["executable_remaining_microusd"] == 0
    execute_review(record, stability, base_dir=tmp_path, authorized=True, budget_calls=2,
                   kind="stability")
    assert len(stability.requests) == 1
    assert first.results[0].agent_result.raw_output == raw


def test_review_uses_existing_parser_retains_original_and_unknown(tmp_path):
    record, raw = run_record()
    reviewer = OfflineReviewProvider(raw)
    outcome = execute_review(record, reviewer, base_dir=tmp_path, authorized=True, budget_calls=1)
    data = outcome.metadata["phase9"]
    assert data["execution_status"] == "completed"
    assert data["route"] != "AUTO_RESOLVABLE"
    assert data["uncertainty"]
    assert len(data["positions"]) == 2
    assert data["positions"][0]["agent_result"]["raw_output"] == raw
    assert reviewer.requests[0]["task"]["gold_label"] is None
    # AA-P8/1.1: this model UNKNOWN against a host-derived supported is a model/host conflict, so the
    # offline review gets the AA-P9/1.1 prompt that announces both positions, not the blind one.
    assert "AA-P9/1.1 targeted review" in reviewer.requests[0]["system_prompt"]
    assert "UNKNOWN" in generate_client_report(outcome)
    loaded = replay_review(record.task, base_dir=tmp_path)
    assert loaded.metadata["phase9"]["positions"] == data["positions"]


def test_arbitrary_provider_rejected_and_invalid_variant_no_calls(tmp_path):
    record, raw = run_record(two_evidence=True)
    class PretendOffline(OfflineReviewProvider):
        pass
    provider = PretendOffline(raw)
    denied = execute_review(record, provider, base_dir=tmp_path, authorized=True, budget_calls=2)
    assert not provider.requests
    assert denied.metadata["phase9"]["route"] == "UNRESOLVED"
    provider = OfflineReviewProvider(raw)
    invalid = execute_review(record, provider, base_dir=tmp_path, authorized=True, budget_calls=2,
                             kind="stability", variant={"original_claim": "paraphrase"})
    assert invalid.metadata["phase9"]["attempts"][-1]["status"] == "rejected"
    assert not provider.requests


def test_historical_and_stale_outputs_do_not_gain_review_pass():
    record, raw = run_record("supported")
    historical = record.model_copy(deep=True)
    historical.metadata = {}
    historical.results[0].agent_result.phase9 = {}
    assert refresh_run_phase9(historical).metadata["phase9"]["technical_status"] == "not_executed"
    assert "🟢 PASS" not in generate_client_report(historical)
    stale = record.model_copy(deep=True)
    stale.results[0].agent_result.raw_output = "{}"
    text = generate_client_report(stale)
    assert "Invalid Phase9 history" in text
    assert "🟢 PASS" not in text


def test_frozen_historical_prompt_bytes():
    import hashlib
    from agent_arena.runner import resolve_study_forensics_prompt
    hashes = {
        "study_forensics_prompt/v1-historical-phase7": "f7704fa50a7689ae56f8fc6d7a383205a5aca34d0c400be36335d6ad8abfcfd5",
        "study_forensics_prompt/v2-taxonomy-aligned-phase5a": "37d91b813bee2b4febb9dba5da66fa8e2bda1e091989785adf6ca5acc132b7ef",
        "study_forensics_prompt/v3-phase8": "4399b8eb743e951ad4c38ec26d4125ecabc19da880b748d2949af04ec5bb2063",
    }
    for version, expected in hashes.items():
        assert hashlib.sha256(resolve_study_forensics_prompt(version).encode()).hexdigest() == expected


def test_reservation_precedes_provider_and_interruption_cannot_reset_cap(tmp_path, monkeypatch):
    from agent_arena.providers import BaseProvider
    record, raw = run_record()
    provider = OfflineReviewProvider(raw)
    original = BaseProvider.generate
    def guarded(self, task, system_prompt):
        ledger = json.loads(next((tmp_path / "phase9").glob("*.ledger.json")).read_text())
        assert ledger["attempts"][0]["state"] == "RESERVED_POSSIBLY_BILLABLE"
        assert len(ledger["attempts"]) == 1
        return original(self, task, system_prompt)
    monkeypatch.setattr(BaseProvider, "generate", guarded)
    execute_review(record, provider, base_dir=tmp_path, authorized=True, budget_calls=2)
    assert len(provider.requests) == 1
    # Simulate a lost result checkpoint, leaving the pessimistic reservation intact.
    next(p for p in (tmp_path / "phase9").glob("*.json") if ".ledger." not in p.name).unlink()
    again = execute_review(record, provider, base_dir=tmp_path, authorized=True, budget_calls=2)
    assert len(provider.requests) == 1
    assert again.metadata["phase9"]["route"] == "UNRESOLVED"
    assert "durable ledger" in again.metadata["phase9"]["attempts"][-1]["reason"]


def test_human_selection_history_replay_and_existing_audit_log(tmp_path):
    from agent_arena.audit_trail import read_decisions
    task, positive = fixture("supported")
    _, negative = fixture("contradicted")
    record = evaluate_run(task, "competing-originals", [
        run_agent(OfflineReviewProvider(positive), task),
        run_agent(OfflineReviewProvider(negative), task),
    ])
    before = record.model_dump()
    positions = record.metadata["phase9"]["positions"]
    outcome = submit_human_review(record, base_dir=tmp_path,
                                  selected_position_id=positions[-1]["position_id"],
                                  reviewer_provenance="Explicit host fixture reviewer",
                                  reason="Select the contrary source interpretation with all evidence considered")
    data = outcome.metadata["phase9"]
    assert data["route"] == "AUTO_RESOLVABLE" and data["review_state"] == "adjudicated"
    assert len(data["positions"]) == 2 and data["conflicts"]
    assert all(c["resolution"] == "adjudicated" for c in data["conflicts"] if c["material"])
    assert data["adjudications"][0]["reviewer_type"] == "human"
    assert len(read_decisions(tmp_path)) == 1
    for _ in range(2):
        replay = replay_review(task, base_dir=tmp_path)
        assert replay.metadata["phase9"]["review_state"] == "adjudicated"
        assert "Final adjudicated scientific state: **CONTRADICTED**" in generate_client_report(replay)
    assert len(read_decisions(tmp_path)) == 1
    assert record.model_dump() == before


def test_model_claiming_human_approval_has_no_human_authority(tmp_path):
    record, raw = run_record()
    payload = json.loads(raw)
    payload.update(reviewer_type="human", human_approved=True, adjudication={"outcome": "resolved"})
    reviewer = OfflineReviewProvider(json.dumps(payload))
    result = execute_review(record, reviewer, base_dir=tmp_path, authorized=True, budget_calls=1)
    data = result.metadata["phase9"]
    assert data["route"] == "HUMAN_REVIEW_REQUIRED"
    assert data["adjudications"] and all(d["reviewer_type"] == "model" for d in data["adjudications"])
    assert not data.get("final_position_id")


def test_human_correction_version_reruns_source_gates(tmp_path):
    task, valid_raw = fixture("supported")
    bad = json.loads(valid_raw)
    bad["forensic_record"]["evidence"][0]["source_id"] = "invented"
    record = evaluate_run(task, "bad-source", [run_agent(OfflineReviewProvider(json.dumps(bad)), task)])
    parent = record.metadata["phase9"]["positions"][0]["position_id"]
    with pytest.raises(ValueError):
        submit_human_review(record, base_dir=tmp_path, selected_position_id=parent,
                            reviewer_provenance="Host fixture", reason="Cannot waive source failure")
    outcome = submit_human_review(record, base_dir=tmp_path, selected_position_id=parent,
                                  reviewer_provenance="Host fixture", reason="Correct source binding to supplied text",
                                  corrected_raw_output=valid_raw)
    data = outcome.metadata["phase9"]
    assert data["review_state"] == "adjudicated"
    assert len(data["positions"]) == 2
    assert data["positions"][0]["phase8"]["technical_status"] == "incomplete"
    assert data["positions"][-1]["phase8"]["technical_status"] == "completed"
    assert data["adjudications"][-1]["corrected_parent_position_id"] == parent
    assert record.results[0].agent_result.raw_output == json.dumps(bad)
    assert replay_review(task, base_dir=tmp_path).metadata["phase9"]["review_state"] == "adjudicated"


def test_denial_is_not_an_attempt_but_only_explicit_new_grant_can_execute(tmp_path):
    record, raw = run_record()
    provider = OfflineReviewProvider(raw)
    execute_review(record, provider, base_dir=tmp_path)
    replay_review(record.task, base_dir=tmp_path)
    assert not provider.requests
    executed = execute_review(record, provider, base_dir=tmp_path, authorized=True, budget_calls=1)
    assert len(provider.requests) == 1
    assert [a["status"] for a in executed.metadata["phase9"]["attempts"]] == ["denied", "completed"]
    assert executed.metadata["phase9"]["execution_status"] == "completed"
    replay_review(record.task, base_dir=tmp_path)
    assert len(provider.requests) == 1


def test_incoming_competing_analysis_cannot_be_discarded_by_stored_human_review(tmp_path):
    record, positive = run_record("supported")
    execute_review(record, base_dir=tmp_path)
    before_files = {p.name: p.read_bytes() for p in (tmp_path / "phase9").glob("*.json")}
    _, negative = fixture("contradicted")
    incoming = evaluate_run(record.task, "new-run", [record.results[0].agent_result,
                           run_agent(OfflineReviewProvider(negative), record.task)])
    before = incoming.model_dump()
    with pytest.raises(ValueError, match="both histories retained"):
        submit_human_review(incoming, base_dir=tmp_path,
                            selected_position_id=record.metadata["phase9"]["positions"][0]["position_id"],
                            reviewer_provenance="Host fixture", reason="Must consider new opposing original")
    assert incoming.model_dump() == before
    assert {p.name: p.read_bytes() for p in (tmp_path / "phase9").glob("*.json")} == before_files


def test_missing_sidecar_preserves_imported_history_and_missing_ledger_blocks_new_call(tmp_path):
    record, raw = run_record(two_evidence=True)
    provider = OfflineReviewProvider(raw)
    reviewed = execute_review(record, provider, base_dir=tmp_path, authorized=True, budget_calls=2)
    before = reviewed.metadata["phase9"]
    other = tmp_path / "empty-location"
    preserved = execute_review(reviewed, provider, base_dir=other, authorized=True, budget_calls=2)
    assert preserved.metadata["phase9"]["positions"] == before["positions"]
    assert preserved.metadata["phase9"]["adjudications"] == before["adjudications"]
    refused = execute_review(reviewed, provider, base_dir=other, authorized=True, budget_calls=2,
                             kind="stability")
    assert len(provider.requests) == 1
    assert refused.metadata["phase9"]["positions"] == before["positions"]
    assert refused.metadata["phase9"]["adjudications"] == before["adjudications"]
    assert "Governance ledger missing" in refused.metadata["phase9"]["attempts"][-1]["reason"]
    assert not list((other / "phase9").glob("*.ledger.json"))


def test_invalid_replay_retains_all_unvalidated_history_and_cannot_claim_execution(tmp_path):
    from agent_arena.phase9_runtime import revalidate_assessment
    record, raw = run_record()
    reviewed = execute_review(record, OfflineReviewProvider(raw), base_dir=tmp_path,
                              authorized=True, budget_calls=1)
    broken = deepcopy(reviewed.metadata["phase9"])
    broken["positions"][0]["position_id"] = "inconsistent"
    outcome = revalidate_assessment(record.task, broken, reviewed)
    assert outcome["route"] == "UNRESOLVED" and outcome["history_validation"] == "invalid"
    for field in ("positions", "adjudications", "attempts"):
        assert outcome[field] == broken[field]
    rendered = generate_client_report(reviewed.model_copy(update={"metadata": {"phase9": broken}}))
    assert "UNVALIDATED HISTORY" in rendered and "Adjudication" in rendered
    fake = deepcopy(record.metadata["phase9"])
    fake["attempts"] = [{"kind": "counterreview", "status": "completed"}]
    invalid = revalidate_assessment(record.task, fake, record)
    assert invalid["execution_status"] != "completed"
    assert invalid["route"] == "UNRESOLVED"
    assert invalid["attempts"] == fake["attempts"]


def test_agent_result_carrier_is_preserved_without_metadata_and_cannot_be_discarded(tmp_path):
    record, raw = run_record(two_evidence=True)
    provider = OfflineReviewProvider(raw)
    reviewed = execute_review(record, provider, base_dir=tmp_path / "source", authorized=True, budget_calls=2)
    agent_only = reviewed.model_copy(update={"metadata": {}})
    carried = execute_review(agent_only, provider, base_dir=tmp_path / "import", authorized=True, budget_calls=2)
    assert carried.metadata["phase9"]["positions"] == reviewed.metadata["phase9"]["positions"]
    assert carried.metadata["phase9"]["adjudications"] == reviewed.metadata["phase9"]["adjudications"]
    assert len(provider.requests) == 1
    # An existing older sidecar cannot silently ignore the extra agent-carried review.
    execute_review(record, base_dir=tmp_path / "old")
    with pytest.raises(ValueError, match="review history differs"):
        execute_review(agent_only, provider, base_dir=tmp_path / "old", authorized=True, budget_calls=2)
    assert len(provider.requests) == 1


def test_invalid_model_adjudication_cannot_keep_completed_execution(tmp_path):
    from agent_arena.phase9_runtime import revalidate_assessment
    record, raw = run_record()
    reviewed = execute_review(record, OfflineReviewProvider(raw), base_dir=tmp_path,
                              authorized=True, budget_calls=1)
    broken = deepcopy(reviewed.metadata["phase9"])
    broken["adjudications"][0]["position_fingerprints"] = {}
    invalid = revalidate_assessment(record.task, broken, reviewed)
    assert invalid["history_validation"] == "invalid"
    assert invalid["route"] == "UNRESOLVED"
    assert invalid["execution_status"] == "failed"
    for field in ("positions", "adjudications", "attempts"):
        assert invalid[field] == broken[field]
