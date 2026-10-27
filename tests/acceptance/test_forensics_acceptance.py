"""Frozen, small offline acceptance corpus; no empirical efficacy measurement.

Expectations were specified before this corpus's first execution. Abstract input
names and source passages are independent of historical benchmark/gold IDs.
"""

import json

import pytest

from inspektorium.audit.execution.evaluator import evaluate_result
from inspektorium.audit.providers import BaseProvider
from inspektorium.audit.reports.reporting import generate_client_report
from inspektorium.audit.execution.runner import run_agent
from inspektorium.audit.schemas import RunRecord, Task
from tests.forensics_case_factory import raw_record

# (case, technical status, scientific state, component state)
ACCEPTANCE = (
    ("identified_clinical_comparison", "completed", "supported", "supported"),
    ("honest_association", "completed", "supported", "supported"),
    ("honest_mouse_mechanism", "completed", "supported", "supported"),
    ("honest_surrogate_result", "completed", "supported", "supported"),
    ("observational_causal_claim", "incomplete", "unknown", "unsupported"),
    ("mouse_to_human_benefit", "incomplete", "unknown", "unsupported"),
    ("surrogate_to_clinical_event", "incomplete", "unknown", "unsupported"),
    ("ingredient_to_product", "incomplete", "unknown", "unsupported"),
    ("wrong_comparator", "incomplete", "unknown", "unsupported"),
    ("short_to_long_followup", "incomplete", "unknown", "unsupported"),
    ("within_to_between", "incomplete", "unknown", "unsupported"),
    ("unidentified_controlled_design", "incomplete", "unknown", "unsupported"),
    ("unknown_design", "incomplete", "unknown", "unknown"),
    ("scientific_unknown", "completed", "unknown", "unknown"),
    ("legacy_absent_analysis", "not_executed", "unknown", None),
    ("lost_required_proposition", "incomplete", "unknown", None),
    ("unbound_source", "incomplete", "unknown", None),
    ("unchecked_summary_explanation", "incomplete", "unknown", None),
)


def corpus_case(name):
    claim, source, record = raw_record(
        endpoint="functional outcome R", intervention="preparation Z"
    )
    ledger = record["phase8"]
    prop = ledger["propositions"][0]
    desc = ledger["evidence_descriptions"][0]

    def source_attribute(key, value):
        nonlocal source
        old = desc["attributes"][key]
        desc["attributes"][key] = value
        source = source.replace(old, value)

    def both_attribute(key, value):
        nonlocal claim
        old = prop["attributes"][key]
        source_attribute(key, value)
        prop["attributes"][key] = value
        claim = claim.replace(old, value)
        for transformation in ledger["transformations"]:
            transformation["from_attributes"][key] = value
            transformation["to_attributes"][key] = value

    if name == "honest_association":
        both_attribute("relation", "association")
        desc.update(evidence_type="observational", randomized=False)
        claim = "Preparation Z is associated with functional outcome R in adults."
        source = "An observational study associated preparation Z with functional outcome R in adults (human), versus placebo at 12 weeks."
    elif name == "honest_mouse_mechanism":
        both_attribute("species", "mouse")
        both_attribute("population", "laboratory mice")
        both_attribute("relation", "mechanism")
        both_attribute("endpoint", "pathway activation")
        both_attribute("endpoint_type", "mechanistic")
        desc.update(evidence_type="animal", randomized=False)
        claim = "Preparation Z activates a pathway in laboratory mice."
        source = "In laboratory mice, preparation Z activated the pathway versus placebo at 12 weeks."
    elif name == "honest_surrogate_result":
        both_attribute("endpoint", "biomarker concentration")
        both_attribute("endpoint_type", "surrogate")
    elif name == "observational_causal_claim":
        desc.update(evidence_type="observational", randomized=False)
        source = source.replace("randomized comparison", "observational comparison")
    elif name == "mouse_to_human_benefit":
        source_attribute("species", "mouse")
        source_attribute("population", "laboratory mice")
        desc.update(evidence_type="animal", randomized=False)
    elif name == "surrogate_to_clinical_event":
        source_attribute("endpoint", "biomarker concentration")
        source_attribute("endpoint_type", "surrogate")
    elif name == "ingredient_to_product":
        source_attribute("intervention", "isolated ingredient Y")
    elif name == "wrong_comparator":
        source_attribute("comparator", "active comparator W")
    elif name == "short_to_long_followup":
        source_attribute("follow_up", "2 weeks")
    elif name == "within_to_between":
        source_attribute("comparison", "within")
        source = source.replace("versus placebo", "within the treated arm only")
    elif name == "unidentified_controlled_design":
        desc["randomized"] = False
        source = source.replace("randomized comparison", "nonrandomized comparison")
    elif name == "unknown_design":
        desc["evidence_type"] = "unknown"
        desc["randomized"] = None
        source = source.replace(
            "randomized comparison", "comparison of unspecified design"
        )
    elif name == "scientific_unknown":
        prop["reported_verdict"] = "unknown"
        prop["uncertainty"] = ["Material interpretation remains unresolved."]
        ledger["transformations"][-1]["asserted_state"] = "unknown"

    # Bind the independent prose variants to the same existing raw-input path.
    record["provenance"][0]["exact_claim_text"] = claim
    ledger["original_claim"] = claim
    prop["proposition_text"] = claim
    prop["original_span"] = {"start": 0, "end": len(claim), "text": claim}
    prop["search_question"] = f"What supplied evidence bears on: {claim}"
    record["findings"][0]["proposition"] = claim
    record["client_findings"][0]["display_claim"] = claim
    for transformation in ledger["transformations"]:
        transformation["from_text"] = claim
        transformation["to_text"] = (
            prop["search_question"]
            if transformation["stage"] == "search_question"
            else claim
        )
    record["evidence"][0].update(
        text=source, exact_reference=source, endpoint=desc["attributes"]["endpoint"]
    )
    if name == "lost_required_proposition":
        ledger["propositions"] = []
    elif name == "unbound_source":
        record["evidence"][0]["source_id"] = "not-supplied"
    elif name == "unchecked_summary_explanation":
        record["client_findings"][0]["client_explanation"] = (
            "This proves universal lasting benefit."
        )
    return claim, source, None if name == "legacy_absent_analysis" else record


class CorpusProvider(BaseProvider):
    name, model = "offline-acceptance", "static-raw-extraction"

    def __init__(self, record):
        self.record = record

    def send_prompt(self, task, system_prompt):
        assert "AA-P8/1.0" in system_prompt and "target_id" in system_prompt
        return json.dumps(
            {"final_answer": "solid", "confidence": 1.0, "forensic_record": self.record}
        )


# AA-P8/1.1 (docs/phase8_9_conflict_addendum.md) is a separately versioned contract; the AA-P8/1.0
# rows above stay frozen as historical expectations. Under 1.1 an output that restates the model's
# own judgment against a different host derivation is technically complete with an open model/host
# conflict (effective state unknown) instead of incomplete. These are technical expectation
# changes; the scientific state and the host derivation of the component are unchanged.
CONFLICT_ROWS_1_1 = {
    "observational_causal_claim",
    "mouse_to_human_benefit",
    "surrogate_to_clinical_event",
    "ingredient_to_product",
    "wrong_comparator",
    "short_to_long_followup",
    "within_to_between",
    "unidentified_controlled_design",
    "unknown_design",
}
# The 1.0 component of this row merged the model's UNKNOWN into the derived state; 1.1 keeps the
# host derivation (supported) separately and records the conflict, closing the unknown bypass.
SPLIT_ROWS_1_1 = {"scientific_unknown": "supported"}


def acceptance_1_1():
    rows = []
    for name, technical, scientific, component in ACCEPTANCE:
        conflict = name in CONFLICT_ROWS_1_1 or name in SPLIT_ROWS_1_1
        rows.append(
            (
                name,
                "completed" if name in CONFLICT_ROWS_1_1 else technical,
                scientific,
                SPLIT_ROWS_1_1.get(name, component),
                conflict,
            )
        )
    return rows


def test_aa_p8_1_1_changes_only_technical_status_and_the_split_component():
    for (name, technical, scientific, component), (
        _,
        new_technical,
        new_scientific,
        host,
        conflict,
    ) in zip(ACCEPTANCE, acceptance_1_1()):
        assert new_scientific == scientific, name
        if name in SPLIT_ROWS_1_1:
            assert (component, host, new_technical) == (
                "unknown",
                "supported",
                technical,
            )
        elif name in CONFLICT_ROWS_1_1:
            assert (technical, new_technical, host) == (
                "incomplete",
                "completed",
                component,
            ) and conflict
        else:
            assert (new_technical, host, conflict) == (technical, component, False), (
                name
            )


@pytest.mark.parametrize(
    "name,technical,scientific,host_component,conflict", acceptance_1_1()
)
def test_frozen_offline_acceptance(
    name, technical, scientific, host_component, conflict
):
    claim, context, payload = corpus_case(name)
    task = Task(
        id=name,
        title=name,
        domain="study_forensics",
        difficulty="medium",
        task_type="study_forensics",
        prompt=claim,
        context=context,
    )
    raw = run_agent(CorpusProvider(payload), task)
    assessed = evaluate_result(task, raw).agent_result.phase8
    assert raw.parse_ok and raw.parsed.final_answer == "solid"
    assert json.loads(raw.raw_output)["forensic_record"] == payload
    assert assessed["technical_status"] == technical, assessed
    assert assessed["composite_state"] == scientific, assessed
    if host_component:
        proposition = assessed["propositions"][0]
        assert proposition["host_state"] == host_component, assessed
        assert proposition["model_host_conflict"] is conflict, assessed
        assert proposition["derived_state"] == (
            "unknown" if conflict else host_component
        ), assessed
        assert (
            proposition["reported_verdict"]
            == payload["phase8"]["propositions"][0]["reported_verdict"]
        )
    output = generate_client_report(
        RunRecord(run_id=name, task=task, results=[evaluate_result(task, raw)])
    )
    assert scientific.upper() in output and technical in output
    if scientific == "unknown":
        assert "🟢 PASS" not in output
