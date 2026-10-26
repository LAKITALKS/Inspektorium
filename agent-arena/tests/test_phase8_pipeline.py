"""Real runner/parser/output integration with offline provider fakes only."""

import json
from copy import deepcopy
from pathlib import Path

import pytest

from agent_arena.artifact_binding import final_binding_check
from agent_arena.evaluator import evaluate_result
from agent_arena.forensic_report import (
    build_forensic_report, render_executive_summary, render_forensic_report_markdown,
)
from agent_arena.phase8_pipeline import assess_agent_result, assess_forensic_payload
from agent_arena.providers import BaseProvider
from agent_arena.reporter import generate_report
from agent_arena.reporting import generate_client_report
from agent_arena.run_library import run_single
from agent_arena.runner import (
    STUDY_FORENSICS_PROMPT_VERSION_HISTORICAL, STUDY_FORENSICS_PROMPT_VERSION_PHASE8,
    run_agent,
)
from agent_arena.schemas import AgentResult, ForensicRecord, RunRecord, Task
from tests.phase8_case_factory import raw_record


def task_for(claim, context):
    return Task(id="synthetic-input", title="Abstract comparison", domain="study_forensics",
                difficulty="medium", task_type="study_forensics", prompt=claim, context=context)


class ExtractionFake(BaseProvider):
    name = "offline"
    model = "no-project-model"

    def __init__(self, payload, expect_phase8=True):
        self.payload = payload
        self.expect_phase8 = expect_phase8
        self.requests = []

    def send_prompt(self, task, system_prompt):
        self.requests.append((task.prompt, task.context, system_prompt))
        if self.expect_phase8:
            assert "AA-P8/1.0" in system_prompt
            assert "PropositionLedger schema" in system_prompt
            assert '"target_id"' in system_prompt
            assert "correlation_vs_causation needs a causal assertion" in system_prompt
        return json.dumps(self.payload)


def response(record):
    return {"final_answer": "solid", "confidence": 0.99, "steps": [],
            "forensic_record": record}


def test_existing_input_to_parser_binding_semantics_and_existing_outputs():
    claim, context, payload = raw_record()
    before = deepcopy(payload)
    task = task_for(claim, context)
    provider = ExtractionFake(response(payload))
    result = run_agent(provider, task)
    assert result.parse_ok and result.error is None
    assert len(provider.requests) == 1
    assert result.parsed.forensic_record == before
    assert json.loads(result.raw_output)["forensic_record"] == before
    assert result.phase8["technical_status"] == "completed", result.phase8
    assert result.phase8["composite_state"] == "supported", result.phase8
    assert result.phase8["original_model_label"] == "solid"
    assert len(result.phase8["canonical_proposition_ids"]) == 1
    assert len(result.phase8["phase7_controls"]) == 5
    assert all(c["status"] in {"executed", "not_applicable"}
               for c in result.phase8["phase7_controls"])
    evaluated = evaluate_result(task, result)
    record = RunRecord(run_id="offline", task=task, results=[evaluated])
    assert "Phase 8" in generate_report(record)
    client = generate_client_report(record)
    assert "SUPPORTED" in client
    assert "not prove correct model extraction" in client
    assert payload == before


@pytest.mark.parametrize("corrupt", [
    lambda r: r["provenance"][0].update(exact_claim_text="Different claim"),
    lambda r: r["evidence"][0].update(source_id="invented-journal"),
    lambda r: r["evidence"][0].update(exact_reference="Nonexistent quotation"),
    lambda r: r["evidence"][0].update(text="Unbound alleged evidence"),
    lambda r: r["evidence"][0].update(value_origin=None, reported_value="5%"),
    lambda r: r.update(client_findings=[]),
    lambda r: r["search_scopes"][0].update(scope_type="documented_search"),
    lambda r: r["phase8"].update(propositions=None),
    lambda r: r["phase8"].update(propositions=[]),
    lambda r: r["phase8"]["propositions"][0]["evidence_bindings"][0].update(evidence_id="absent"),
])
def test_corrupt_model_extraction_fails_closed_without_losing_raw(corrupt):
    claim, context, payload = raw_record()
    corrupt(payload)
    result = run_agent(ExtractionFake(response(payload)), task_for(claim, context))
    assert result.parse_ok, result.error
    assert result.parsed.final_answer == "solid"
    assert result.phase8["technical_status"] == "incomplete", result.phase8
    assert result.phase8["composite_state"] == "unknown"
    assert json.loads(result.raw_output)["forensic_record"] == payload


@pytest.mark.parametrize("payload", [None, [], "invalid", {"record_id": "empty"}])
def test_missing_vs_invalid_payload_survives_parser(payload):
    result = run_agent(ExtractionFake(response(payload)), task_for("Claim", "Evidence"))
    expected = "not_executed" if payload is None else "incomplete"
    assert result.parse_ok
    assert result.phase8["technical_status"] == expected
    assert result.phase8["composite_state"] == "unknown"


def test_explicit_historical_path_is_not_silently_phase8_verified():
    fake = ExtractionFake({"final_answer": "solid", "confidence": 1}, expect_phase8=False)
    task = task_for("Original claim", "Supplied source")
    result = run_agent(fake, task, prompt_version=STUDY_FORENSICS_PROMPT_VERSION_HISTORICAL)
    assert "AA-P8/1.0" not in fake.requests[0][2]
    assert result.phase8["technical_status"] == "not_executed"
    record = RunRecord(run_id="legacy", task=task, results=[evaluate_result(task, result)])
    rendered = generate_client_report(record)
    assert "UNKNOWN" in rendered and "not_executed" in rendered
    assert "🟢 PASS" not in rendered


def test_library_path_keeps_payload_raw_and_assessment():
    claim, context, payload = raw_record()
    flat = run_single(ExtractionFake(response(payload)), Path("fake.yaml"),
                      task_for(claim, context), 0, "offline")
    assert flat["phase8"]["technical_status"] == "completed", flat["phase8"]
    assert flat["forensic_record"] == payload
    assert json.loads(flat["raw_output"])["forensic_record"] == payload
    assert flat["label"] == "solid"  # historical scoring target retained separately


def test_manual_evaluation_recomputes_forged_cached_assessment():
    task = task_for("Claim", "Evidence")
    result = AgentResult(provider="manual", raw_output='{"final_answer":"solid"}',
                         parse_ok=True, parsed={"final_answer": "solid"},
                         phase8={"technical_status": "completed", "composite_state": "supported"})
    assert evaluate_result(task, result).agent_result.phase8["technical_status"] == "not_executed"


def test_truncated_output_cannot_gain_semantic_completion_from_parser_repair():
    claim, context, payload = raw_record()
    result = run_agent(ExtractionFake(response(payload)), task_for(claim, context))
    result.finish_reason = "length"
    assessment = assess_agent_result(task_for(claim, context), result)
    assert assessment["technical_status"] == "incomplete"
    assert assessment["composite_state"] == "unknown"


def test_report_path_runs_same_checks_and_preserves_original_model_verdict():
    claim, context, payload = raw_record()
    raw = {"claim": {"claim_text": claim, "claim_context": context},
           "verdict": {"predicted_label": "solid", "confidence": 1.0},
           "forensic_record": payload}
    report = build_forensic_report(raw)
    assert report["phase8"]["composite_state"] == "supported", report["phase8"]
    payload["phase8"]["propositions"] = []
    blocked = build_forensic_report(raw)
    assert blocked["original_model_verdict"]["predicted_label"] == "solid"
    assert blocked["verdict"]["predicted_label"] is None
    assert "UNKNOWN" in render_executive_summary(blocked)
    assert "incomplete" in render_forensic_report_markdown(blocked)


def test_legacy_report_explicitly_exposes_unexecuted_phase8():
    report = build_forensic_report({"claim": {"claim_text": "Claim"},
                                    "verdict": {"predicted_label": "solid"}})
    assert report["phase8"]["technical_status"] == "not_executed"
    assert "not_executed" in render_executive_summary(report)


def test_empty_legacy_binding_check_is_not_a_clean_pass():
    result = final_binding_check(ForensicRecord(record_id="empty"))
    assert not result.releasable
    assert any(f.check == "coverage" for f in result.findings)


def test_explicit_phase8_version_and_canonical_ids_are_reproducible():
    claim, context, record = raw_record()
    task = task_for(claim, context)
    output = run_agent(ExtractionFake(response(record)), task,
                       prompt_version=STUDY_FORENSICS_PROMPT_VERSION_PHASE8)
    first = assess_forensic_payload(record, original_input=claim, context=context)
    second = assess_forensic_payload(deepcopy(record), original_input=claim, context=context)
    assert first == second
    assert first["canonical_proposition_ids"] == output.phase8["canonical_proposition_ids"]


@pytest.mark.parametrize("cached", [{}, {"is_study_forensics": False}])
def test_loaded_high_score_cannot_bypass_phase8_using_cached_routing(cached):
    from agent_arena.schemas import DIAGNOSTIC_WEIGHTS
    task = task_for("Claim", "Evidence")
    raw = AgentResult(provider="legacy", raw_output='{"final_answer":"solid"}',
                      parse_ok=True, parsed={"final_answer": "solid"})
    evaluated = evaluate_result(task, raw)
    evaluated.study_forensics = cached
    evaluated.failures = []
    evaluated.failure_modes = []
    for name in DIAGNOSTIC_WEIGHTS:
        setattr(evaluated.scores, name, 1.0)
    record = RunRecord(run_id="cached-bypass", task=task, results=[evaluated])
    client = generate_client_report(record)
    internal = generate_report(record)
    assert "not_executed" in client and "UNKNOWN" in client
    assert "🟢 PASS" not in client and "Analysis appears sound" not in client
    assert "No significant changes required" not in client
    verdict = internal.split("## Final Verdict", 1)[1]
    assert "UNKNOWN" in verdict and "not_executed" in verdict
    assert "All agents completed without critical failure modes" not in verdict
    assert evaluated.study_forensics == cached  # rendering preserves original record


@pytest.mark.parametrize("malformed", [False, True])
def test_taxonomy_extraction_crosses_real_prompt_parser_and_report(malformed):
    claim, context, payload = raw_record()
    payload["phase8_taxonomy"] = {
        "core_error": "none", "causal_claim": True, "noncausal_result_used": False,
        "described_biological_mechanism": False, "implies_human_benefit": True,
        "proposition_ids": ["claim:p1"], "evidence_ids": ["e1"],
        "trigger_proposition_id": "claim:p1", "trigger_evidence_id": "e1",
        "trigger_quote": context, "reason": "Honest description of the supplied comparison",
    }
    if malformed:
        payload["phase8_taxonomy"]["trigger_evidence_id"] = "unrelated"
    provider = ExtractionFake(response(payload))
    task = task_for(claim, context)
    raw = run_agent(provider, task)
    assert "TaxonomyAssessment schema" in provider.requests[0][2]
    assert "trigger_evidence_id" in provider.requests[0][2]
    assert raw.parsed.forensic_record == payload
    assert raw.phase8["original_model_label"] == "solid"
    assert raw.phase8["derived_label"] == (None if malformed else "solid")
    assert raw.phase8["taxonomy"]["technical_status"] == ("incomplete" if malformed else "completed")
    report = generate_client_report(RunRecord(run_id="taxonomy", task=task,
                                              results=[evaluate_result(task, raw)]))
    assert "Taxonomy control" in report
    if malformed:
        assert "🟢 PASS" not in report


def test_original_cvc_is_preserved_when_bound_generic_overstatement_derives_overclaim():
    claim, context, payload = raw_record()
    payload["phase8"]["evidence_descriptions"][0]["randomized"] = False
    context = context.replace("randomized comparison", "nonrandomized comparison")
    payload["evidence"][0].update(text=context, exact_reference=context)
    # AA-P8/1.1 C25: the summary restates the model's own proposition judgment.
    payload["phase8"]["propositions"][0]["reported_verdict"] = "unsupported"
    payload["phase8"]["transformations"][-1]["asserted_state"] = "unsupported"
    payload["phase8_taxonomy"] = {
        "core_error": "overstatement", "causal_claim": True, "noncausal_result_used": False,
        "described_biological_mechanism": False, "implies_human_benefit": True,
        "proposition_ids": ["claim:p1"], "evidence_ids": ["e1"],
        "trigger_proposition_id": "claim:p1", "trigger_evidence_id": "e1",
        "trigger_quote": context, "reason": "Generic efficacy overstatement; no noncausal result was used",
    }
    extraction = response(payload)
    extraction["final_answer"] = "correlation_vs_causation"
    task = task_for(claim, context)
    result = run_agent(ExtractionFake(extraction), task)
    assert result.parsed.final_answer == "correlation_vs_causation"
    assert json.loads(result.raw_output) == extraction
    assert result.phase8["original_model_label"] == "correlation_vs_causation"
    assert result.phase8["derived_label"] == "overclaim", result.phase8
    assert result.phase8["technical_status"] == "completed"
    rendered = generate_client_report(RunRecord(run_id="cvc-correction", task=task,
                                                results=[evaluate_result(task, result)]))
    assert "derived classification: `overclaim`" in rendered
    assert "Original model classification: `correlation_vs_causation`" in rendered
