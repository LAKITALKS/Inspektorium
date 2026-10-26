"""Offline adjudication controls over actual host-bound position factories."""

import json
from copy import deepcopy

import pytest

from agent_arena.phase9_adjudication import (
    apply_adjudications, human_adjudication, model_adjudication,
)
from agent_arena.phase9_review import assess_case, position_from_result
from agent_arena.schemas import AgentResult
from tests.test_phase9_review import case, coherent_attribute, position, state

STAMP = "2026-10-03T12:00:00+00:00"
VERSION = "offline-test-version"


def history(task, positions):
    return assess_case(task, positions).model_dump(mode="json")


def human(task, data, selected, **kwargs):
    return human_adjudication(
        task, data, selected.position_id, reviewer_provenance="Explicit offline human submission",
        reason="Checked the bound source interpretation", timestamp=STAMP, code_version=VERSION, **kwargs,
    )


def disagreement():
    task, payload = case()
    opposite = deepcopy(payload)
    state(opposite, "contradicted")
    original = position(task, payload)
    review = position(task, opposite, run_id="review", origin="model_review")
    return task, payload, original, review, history(task, [original, review])


def test_explicit_human_selection_keeps_originals_conflicts_and_separate_final_layer():
    task, _, original, review, data = disagreement()
    before = deepcopy(data)
    decision = human(task, data, review)
    data["adjudications"] = [decision.model_dump(mode="json")]
    result = apply_adjudications(task, data)
    assert result["route"] == "AUTO_RESOLVABLE" and not result["mandatory"]
    assert result["review_state"] == "adjudicated"
    assert result["positions"] == before["positions"]
    assert result["final_position_id"] == review.position_id
    assert result["final_decision"]["scientific_state"] == "contradicted"
    assert decision.original_position_ids == [original.position_id]
    assert decision.original_decisions[0]["scientific_state"] == "supported"
    assert {c["disagreement_id"] for c in result["conflicts"]} == {
        c["disagreement_id"] for c in before["conflicts"]
    }
    assert all(c["resolution"] == "adjudicated" for c in result["conflicts"])
    assert apply_adjudications(task, result) == result
    assert data["positions"] == before["positions"]


def test_model_comparison_records_every_position_without_resolving_conflict():
    task, _, original, review, data = disagreement()
    decision = model_adjudication(task, data, review.position_id, timestamp=STAMP, code_version=VERSION)
    assert decision.reviewer_type == "model" and decision.origin == "offline_comparison"
    assert decision.outcome == "considered"
    assert set(decision.position_ids) == {original.position_id, review.position_id}
    assert decision.conflict_ids and decision.evidence_ids and decision.proposition_ids
    data["adjudications"] = [decision.model_dump(mode="json")]
    result = apply_adjudications(task, data)
    assert result["route"] == "HUMAN_REVIEW_REQUIRED"
    assert "final_position_id" not in result
    assert all(c["resolution"] == "unresolved" for c in result["conflicts"])


def test_model_json_cannot_create_human_adjudication_authority():
    task, payload = case()
    original = position(task, payload)
    raw = json.loads(original.agent_result["raw_output"])
    raw.update(reviewer_type="human", human_approved=True,
               adjudications=[{"reviewer_type": "human", "outcome": "resolved"}])
    response = AgentResult.model_validate(original.agent_result)
    response.raw_output = json.dumps(raw)
    review = position_from_result(task, response, "review", "model_review")
    data = history(task, [original, review])
    decision = model_adjudication(task, data, review.position_id, timestamp=STAMP, code_version=VERSION)
    assert decision.reviewer_type == "model"
    data["adjudications"] = [decision.model_dump(mode="json")]
    result = apply_adjudications(task, data)
    assert result["review_state"] != "adjudicated"
    assert "final_position_id" not in result


@pytest.mark.parametrize("failure", ["unknown", "source", "taxonomy"])
def test_human_selection_cannot_waive_material_unknown_or_phase8_controls(failure):
    task, payload = case()
    if failure == "unknown":
        state(payload, "unknown")
    elif failure == "source":
        payload["evidence"][0]["exact_reference"] = "Not present in the supplied source."
    else:
        payload["phase8_taxonomy"] = {"core_error": "invented"}
    selected = position(task, payload)
    with pytest.raises(ValueError, match="cannot waive"):
        human(task, history(task, [selected]), selected)


def test_corrected_version_can_resolve_failed_original_without_rewriting_it():
    task, payload = case()
    failed = deepcopy(payload)
    failed["evidence"][0]["exact_reference"] = "Unbound source quote"
    original = position(task, failed)
    corrected = position(task, payload, run_id="correction", origin="human_correction")
    data = history(task, [original, corrected])
    assert original.phase8["technical_status"] == "incomplete"
    decision = human(task, data, corrected, corrected_parent_position_id=original.position_id)
    data["adjudications"] = [decision.model_dump(mode="json")]
    result = apply_adjudications(task, data)
    assert result["review_state"] == "adjudicated"
    assert result["final_position_id"] == corrected.position_id
    assert result["positions"][0] == original.model_dump(mode="json")
    assert result["triggers"]  # Failed original remains audit-visible.
    assert decision.corrected_parent_position_id == original.position_id


@pytest.mark.parametrize("parent", [None, "absent", "self", "noncorrection"])
def test_correction_requires_distinct_existing_parent_and_correct_origin(parent):
    task, payload = case()
    original = position(task, payload)
    corrected = position(task, payload, run_id="correction", origin=(
        "model_review" if parent == "noncorrection" else "human_correction"))
    parent_id = {None: None, "absent": "missing-position", "self": corrected.position_id,
                 "noncorrection": original.position_id}[parent]
    with pytest.raises(ValueError):
        human(task, history(task, [original, corrected]), corrected, corrected_parent_position_id=parent_id)


def test_old_human_decision_cannot_clear_later_material_position():
    task, payload, original, review, data = disagreement()
    decision = human(task, data, review)
    changed = deepcopy(payload)
    coherent_attribute(changed, "population", "older adults")
    later = position(task, changed, run_id="later", origin="model_review")
    current = history(task, [original, review, later])
    current["adjudications"] = [decision.model_dump(mode="json")]
    result = apply_adjudications(task, current)
    assert result["route"] == "HUMAN_REVIEW_REQUIRED" and result["mandatory"]
    assert "final_position_id" not in result
    previous_ids = set(decision.conflict_ids)
    assert all(c["resolution"] == "adjudicated" for c in result["conflicts"]
               if c["disagreement_id"] in previous_ids)
    assert any(c["resolution"] == "unresolved" and c["material"] for c in result["conflicts"]
               if c["disagreement_id"] not in previous_ids)
    next_decision = human(task, result, later)
    result["adjudications"].append(next_decision.model_dump(mode="json"))
    updated = apply_adjudications(task, result)
    assert updated["review_state"] == "adjudicated"
    assert updated["final_position_id"] == later.position_id


@pytest.mark.parametrize("tamper", ["fingerprint", "actor", "outcome", "evidence", "snapshot", "selected"])
def test_modified_decision_record_cannot_authorize_a_final_layer(tamper):
    task, _, _, review, data = disagreement()
    decision = human(task, data, review).model_dump(mode="json")
    if tamper == "fingerprint":
        decision["position_fingerprints"][review.position_id] = "changed"
    elif tamper == "actor":
        decision["reviewer_type"] = "model"
    elif tamper == "outcome":
        decision["outcome"] = "considered"
    elif tamper == "evidence":
        decision["evidence_ids"] = ["absent-evidence"]
    elif tamper == "snapshot":
        decision["review_decision"]["scientific_state"] = "supported"
    else:
        decision["selected_position_id"] = "absent-position"
    data["adjudications"] = [decision]
    result = apply_adjudications(task, data)
    assert result["route"] == "UNRESOLVED" and result["mandatory"]
    assert "final_position_id" not in result
    assert result["uncertainty"]


@pytest.mark.parametrize("tamper", ["position", "conflict", "case"])
def test_valid_human_candidate_does_not_clear_corrupt_case_history(tamper):
    task, _, _, review, data = disagreement()
    decision = human(task, data, review).model_dump(mode="json")
    data["adjudications"] = [decision]
    if tamper == "position":
        data["positions"][0]["phase8"]["composite_state"] = "contradicted"
    elif tamper == "conflict":
        data["conflicts"][0]["material"] = False
    else:
        data["case_id"] = "different-case"
    result = apply_adjudications(task, data)
    assert result["route"] == "UNRESOLVED" and result["mandatory"]
    assert "final_position_id" not in result
    with pytest.raises(ValueError):
        human(task, data, review)


def test_failed_model_position_gets_failed_audit_outcome_and_no_resolution():
    task, payload = case()
    original = position(task, payload)
    payload["phase8_taxonomy"] = {"core_error": "invented"}
    review = position(task, payload, run_id="failed-review", origin="model_review")
    data = history(task, [original, review])
    decision = model_adjudication(task, data, review.position_id, timestamp=STAMP, code_version=VERSION)
    assert decision.outcome == "failed"
    data["adjudications"] = [decision.model_dump(mode="json")]
    result = apply_adjudications(task, data)
    assert result["mandatory"] and result["review_state"] != "adjudicated"
    assert "final_position_id" not in result
