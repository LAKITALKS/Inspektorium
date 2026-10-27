"""AA-P9-ACCEPTANCE/1.0 expectations; harness 1.1 binds the complete evidence packet."""

import hashlib
import json
from copy import deepcopy
from pathlib import Path

import pytest

from inspektorium.audit.execution.evaluator import evaluate_run
from inspektorium.audit.review.pipeline import refresh_run_phase9
from inspektorium.audit.review.runtime import (
    OfflineReviewProvider,
    execute_review,
    replay_review,
    submit_human_review,
)
from inspektorium.audit.reports.reporting import generate_client_report
from inspektorium.audit.execution.runner import run_agent
from inspektorium.audit.schemas import Task
from tests.forensics_case_factory import raw_record

CORPUS = (
    Path(__file__).resolve().parents[1] / "fixtures/audit/review/acceptance_v1.json"
)
CORPUS_SHA256 = "c8d83b417968163bad3a00a55c43855d3dc9f61d962dd69d405c13e12f7c06fe"
CASES = json.loads(CORPUS.read_text())["cases"]


def sample():
    claim, context, payload = raw_record(
        endpoint="outcome Omega", intervention="compound Lambda"
    )
    evidence = deepcopy(payload["evidence"][0])
    evidence["evidence_id"] = "e2"
    payload["evidence"].append(evidence)
    binding = deepcopy(payload["phase8"]["propositions"][0]["evidence_bindings"][0])
    binding.update(binding_id="b2", evidence_id="e2")
    payload["phase8"]["propositions"][0]["evidence_bindings"].append(binding)
    description = deepcopy(payload["phase8"]["evidence_descriptions"][0])
    description["evidence_id"] = "e2"
    payload["phase8"]["evidence_descriptions"].append(description)
    payload["findings"][0]["supporting_evidence_ids"].append("e2")
    payload["client_findings"][0]["referenced_evidence_ids"].append("e2")
    task = Task(
        id="p9-acceptance-generic",
        title="Generic evidence review",
        domain="study_forensics",
        task_type="study_forensics",
        difficulty="medium",
        prompt=claim,
        context=context,
        gold_label="withheld-oracle",
    )
    return task, payload


def raw(payload, confidence=0.82, wording="Initial abstract explanation"):
    return json.dumps(
        {
            "final_answer": "solid",
            "confidence": confidence,
            "steps": [wording],
            "forensic_record": payload,
        }
    )


def change_state(payload, desired):
    prop = payload["phase8"]["propositions"][0]
    prop["reported_verdict"] = desired
    for binding in prop["evidence_bindings"]:
        binding["observation"] = {
            "supported": "support",
            "unknown": "inconclusive",
            "contradicted": "contradiction",
        }[desired]
    if desired == "contradicted":
        for evidence in payload["evidence"]:
            evidence["role"] = "contradictory"
        payload["findings"][0].update(
            supporting_evidence_ids=[], contrary_evidence_ids=["e1", "e2"]
        )
    payload["phase8"]["transformations"][-1]["asserted_state"] = desired


def change_attribute(payload, key, value):
    payload["phase8"]["propositions"][0]["attributes"][key] = value
    for description in payload["phase8"]["evidence_descriptions"]:
        description["attributes"][key] = value
    for transform in payload["phase8"]["transformations"]:
        transform["from_attributes"][key] = value
        transform["to_attributes"][key] = value


@pytest.mark.parametrize("expected", CASES, ids=[c["id"] for c in CASES])
def test_frozen_phase9_acceptance(expected, tmp_path):
    assert hashlib.sha256(CORPUS.read_bytes()).hexdigest() == CORPUS_SHA256
    task, payload = sample()
    name = expected["id"]
    uncertain = name in {
        "necessary_unknown",
        "blind_complete_counterreview",
        "budget_zero",
        "failed_review_and_replay",
        "one_stability_flip",
        "reject_semantic_variant",
    }
    if uncertain:
        change_state(payload, "unknown")
    if name == "stable_negative":
        change_state(payload, "contradicted")
    if name in {"single_position_ceiling", "human_cannot_waive_source_gate"}:
        payload["evidence"][0]["source_id"] = "nonexistent-source"
    first_raw = raw(payload)
    first = run_agent(OfflineReviewProvider(first_raw), task)
    results = [first]
    if name in {
        "trivial_confidence_wording",
        "necessary_proposition_conflict",
        "evidence_direction_conflict",
        "causality_conflict",
        "product_transfer_conflict",
        "population_endpoint_conflict",
        "explicit_human_adjudication",
    }:
        second = deepcopy(payload)
        if name in {
            "necessary_proposition_conflict",
            "evidence_direction_conflict",
            "explicit_human_adjudication",
        }:
            change_state(second, "contradicted")
        if name == "causality_conflict":
            change_attribute(second, "relation", "association")
        if name == "product_transfer_conflict":
            change_attribute(second, "intervention", "other formulation")
        if name == "population_endpoint_conflict":
            change_attribute(second, "population", "different population")
            change_attribute(second, "endpoint", "different endpoint")
        results.append(
            run_agent(
                OfflineReviewProvider(raw(second, 0.78, "Alternative wording")), task
            )
        )
    record = evaluate_run(task, "acceptance-run", results)
    providers = []
    if name in {
        "stable_positive",
        "stable_negative",
        "blind_complete_counterreview",
        "budget_zero",
        "failed_review_and_replay",
        "one_stability_flip",
        "reject_semantic_variant",
    }:
        reviewer = OfflineReviewProvider(
            first_raw,
            error="recorded failure" if name == "failed_review_and_replay" else None,
        )
        providers.append(reviewer)
        record = execute_review(
            record,
            reviewer,
            base_dir=tmp_path,
            authorized=name != "budget_zero",
            budget_calls=0 if name == "budget_zero" else 2,
        )
        if name == "blind_complete_counterreview":
            sent = reviewer.requests[0]
            assert sent["task"]["prompt"] == task.prompt
            assert sent["task"]["gold_label"] is None
            packet = json.loads(
                sent["task"]["context"].split("Bound evidence packet:\n")[1]
            )
            assert len(packet["evidence"]) == 2
            assert "reported_verdict" not in json.dumps(packet)
            assert "Initial abstract explanation" not in json.dumps(packet)
        if name == "failed_review_and_replay":
            record = replay_review(task, base_dir=tmp_path)
            record = execute_review(
                record.model_copy(update={"run_id": "new-id"}),
                reviewer,
                base_dir=tmp_path,
                authorized=True,
                budget_calls=2,
            )
        if name in {"one_stability_flip", "reject_semantic_variant"}:
            stable_payload = deepcopy(payload)
            change_state(stable_payload, "supported")
            stability = OfflineReviewProvider(raw(stable_payload))
            providers.append(stability)
            record = execute_review(
                record,
                stability,
                base_dir=tmp_path,
                authorized=True,
                budget_calls=2,
                kind="stability",
                variant={"claim": "changed"}
                if name == "reject_semantic_variant"
                else None,
            )
            record = execute_review(
                record,
                stability,
                base_dir=tmp_path,
                authorized=True,
                budget_calls=2,
                kind="stability",
            )
    if name == "explicit_human_adjudication":
        positions = record.metadata["phase9"]["positions"]
        record = submit_human_review(
            record,
            base_dir=tmp_path,
            selected_position_id=positions[-1]["position_id"],
            reviewer_provenance="Host submitted fixture reviewer",
            reason="Explicit evidence-linked resolution of competing interpretations",
        )
        assert record.metadata["phase9"]["conflicts"]
        assert len(record.metadata["phase9"]["positions"]) == 2
        assert (
            record.metadata["phase9"]["adjudications"][-1]["reviewer_type"] == "human"
        )
        assert (
            replay_review(task, base_dir=tmp_path).metadata["phase9"]["review_state"]
            == "adjudicated"
        )
    if name == "human_cannot_waive_source_gate":
        with pytest.raises(ValueError):
            submit_human_review(
                record,
                base_dir=tmp_path,
                selected_position_id=record.metadata["phase9"]["positions"][0][
                    "position_id"
                ],
                reviewer_provenance="Host fixture",
                reason="Attempt to waive missing source",
            )
    if name == "historical_no_phase9":
        record.metadata = {}
        record.results[0].agent_result.phase9 = {}
        record = refresh_run_phase9(record)
    data = record.metadata["phase9"]
    assert data["route"] == expected["route"]
    for field in ("execution_status", "technical_status", "review_state"):
        if field in expected:
            assert data[field] == expected[field]
    if "calls" in expected:
        assert sum(len(p.requests) for p in providers) == expected["calls"]
    if "conflicts" in expected:
        assert len(data["conflicts"]) == expected["conflicts"]
    if "dimension" in expected:
        assert any(
            c["dimension"] == expected["dimension"] and c["material"]
            for c in data["conflicts"]
        )
    assert record.results[0].agent_result.raw_output == first_raw
    rendered = generate_client_report(record)
    assert "Phase 9 review" in rendered
    assert data["route"] in rendered
    if data["route"] != "AUTO_RESOLVABLE":
        assert "🟢 PASS" not in rendered
