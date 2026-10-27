"""Generic precedence regressions; no historical case IDs or relabeled gold."""

from copy import deepcopy

import pytest

from inspektorium.audit.forensics.semantics import evaluate_phase8
from inspektorium.audit.forensics.taxonomy import assess_taxonomy
from inspektorium.audit.schemas import ForensicRecord
from tests.forensics_case_factory import raw_record


def taxonomy_record(core="none", **flags):
    _, source, data = raw_record()
    data["phase8_taxonomy"] = {
        "core_error": core,
        "causal_claim": True,
        "noncausal_result_used": False,
        "described_biological_mechanism": False,
        "implies_human_benefit": True,
        "proposition_ids": ["claim:p1"],
        "evidence_ids": ["e1"],
        "trigger_proposition_id": "claim:p1",
        "trigger_evidence_id": "e1",
        "trigger_quote": source,
        "reason": "Generic represented core-error analysis",
        **flags,
    }
    return ForensicRecord.model_validate(data)


def summary_state(record, state):
    # AA-P8/1.1 C25: the summary restates the model's own judgment, so both are set together.
    # A different host derivation would be an open model/host conflict (effective unknown).
    record.phase8["propositions"][0]["reported_verdict"] = state
    for t in record.phase8["transformations"]:
        if t["stage"] == "summary":
            t["asserted_state"] = state


def source_text(record, text):
    record.evidence[0].text = text
    record.evidence[0].exact_reference = text
    record.phase8_taxonomy["trigger_quote"] = text


def result(record):
    semantics = evaluate_phase8(record)
    assert semantics.technical_status == "completed", semantics.reasons
    return assess_taxonomy(record, semantics)


@pytest.mark.parametrize("kind", ["observational", "uncontrolled_prepost"])
def test_genuine_causal_inference_core_is_cvc(kind):
    record = taxonomy_record("causal_inference", noncausal_result_used=True)
    profile = record.phase8["evidence_descriptions"][0]
    if kind == "observational":
        profile.update(evidence_type="observational", randomized=None)
        profile["attributes"]["relation"] = "association"
        source_text(record, "In adults, exposure X was associated with fewer events Q.")
    else:
        profile.update(evidence_type="controlled_intervention", randomized=False)
        profile["attributes"].update(
            relation="description", comparison="within", comparator="baseline"
        )
        source_text(
            record, "Events decreased from baseline in the single treated group."
        )
    summary_state(record, "unsupported")
    assert result(record)["derived_label"] == "correlation_vs_causation"


def test_missing_efficacy_does_not_become_cvc_from_poor_design_alone():
    record = taxonomy_record("overstatement", noncausal_result_used=False)
    profile = record.phase8["evidence_descriptions"][0]
    profile.update(randomized=False)
    profile["attributes"]["relation"] = "description"
    source_text(
        record,
        "The brochure invokes uncontrolled experiments without an established efficacy result.",
    )
    summary_state(record, "unsupported")
    assert result(record)["derived_label"] == "overclaim"
    record.phase8_taxonomy["core_error"] = "causal_inference"
    assert result(record)["derived_label"] is None


def test_population_overstatement_retains_core_even_when_causal_trigger_is_present():
    record = taxonomy_record("overstatement", noncausal_result_used=True)
    profile = record.phase8["evidence_descriptions"][0]
    profile.update(evidence_type="observational", randomized=None)
    profile["attributes"].update(
        relation="association", population="selected older patients"
    )
    source_text(
        record,
        "A selected older cohort showed an association, generalized to all adults.",
    )
    summary_state(record, "unsupported")
    assert result(record)["derived_label"] == "overclaim"


def test_established_causation_with_excessive_population_scope_is_overclaim_not_cvc():
    record = taxonomy_record("overstatement")
    record.phase8["evidence_descriptions"][0]["attributes"]["population"] = (
        "older adults"
    )
    summary_state(record, "unsupported")
    assert result(record)["derived_label"] == "overclaim"
    record.phase8_taxonomy.update(
        core_error="causal_inference", noncausal_result_used=True
    )
    assert result(record)["derived_label"] is None


def test_genuine_biological_mechanism_to_human_benefit_is_me():
    record = taxonomy_record(
        "mechanism_to_outcome", described_biological_mechanism=True
    )
    profile = record.phase8["evidence_descriptions"][0]
    profile.update(evidence_type="animal", randomized=None)
    profile["attributes"].update(
        species="mouse", population="adult mice", relation="mechanism"
    )
    record.phase8["propositions"][0]["evidence_bindings"][0]["directness"] = "indirect"
    source_text(
        record,
        "In mice, X activated pathway P, presented as the basis for preventing human events Q.",
    )
    summary_state(record, "unsupported")
    assert result(record)["derived_label"] == "mechanism_vs_evidence"


def test_surrogate_shape_b_is_overclaim_and_cannot_be_stretched_to_me():
    record = taxonomy_record("overstatement")
    profile = record.phase8["evidence_descriptions"][0]
    profile["attributes"].update(endpoint="biomarker B", endpoint_type="biomarker")
    source_text(
        record,
        "The trial changed biomarker B, marketed as protection from clinical events Q.",
    )
    summary_state(record, "unsupported")
    assert result(record)["derived_label"] == "overclaim"
    record.phase8_taxonomy.update(
        core_error="mechanism_to_outcome", described_biological_mechanism=True
    )
    assert result(record)["derived_label"] is None


def test_honest_direct_reporting_is_solid_without_mutating_original_payload():
    record = taxonomy_record()
    before = deepcopy(record.model_dump())
    assert result(record)["derived_label"] == "solid"
    assert record.model_dump() == before


@pytest.mark.parametrize(
    "flag",
    [
        "causal_claim",
        "noncausal_result_used",
        "described_biological_mechanism",
        "implies_human_benefit",
    ],
)
def test_unknown_trigger_does_not_force_any_label(flag):
    record = taxonomy_record(**{flag: None})
    assessed = result(record)
    assert assessed["technical_status"] == "completed"
    assert assessed["derived_label"] is None


def test_scientific_unknown_alone_cannot_establish_overclaim():
    record = taxonomy_record("overstatement")
    record.phase8["evidence_descriptions"][0]["evidence_type"] = "unknown"
    summary_state(record, "unknown")
    assert result(record)["derived_label"] is None


@pytest.mark.parametrize(
    "mutation",
    [
        {"proposition_ids": ["unrelated"]},
        {"evidence_ids": ["unrelated"]},
        {"trigger_proposition_id": "unrelated"},
        {"trigger_evidence_id": "unrelated"},
        {"trigger_quote": "unquoted invention"},
        {"trigger_quote": ""},
        {"core_error": "whichever label passes"},
    ],
)
def test_invalid_trigger_or_reference_is_technical_incomplete(mutation):
    record = taxonomy_record()
    record.phase8_taxonomy.update(mutation)
    assert result(record)["technical_status"] == "incomplete"


def test_absent_or_technically_incomplete_analysis_cannot_relabel():
    record = taxonomy_record()
    assert (
        assess_taxonomy(record, {"technical_status": "incomplete"})["derived_label"]
        is None
    )
    record.phase8_taxonomy = None
    assert (
        assess_taxonomy(record, evaluate_phase8(record))["technical_status"]
        == "not_executed"
    )


def test_false_causal_trigger_conflicts_with_a_genuine_association_claim():
    record = taxonomy_record("causal_inference", noncausal_result_used=True)
    prop = record.phase8["propositions"][0]
    prop["attributes"]["relation"] = "association"
    for t in record.phase8["transformations"]:
        t["from_attributes"]["relation"] = "association"
        t["to_attributes"]["relation"] = "association"
    profile = record.phase8["evidence_descriptions"][0]
    profile.update(evidence_type="observational", randomized=None)
    profile["attributes"]["relation"] = "association"
    assert result(record)["derived_label"] is None


def add_logical_component(record, *, operator, state):
    """A genuinely separate, host-preserved alternative/conjunct with its own evidence."""
    second_claim, _, raw = raw_record(endpoint="event R")
    second = ForensicRecord.model_validate(raw)
    first_claim = record.phase8["original_claim"]
    separator = " or " if operator == "or" else " and "
    combined = first_claim + separator + second_claim
    record.phase8["original_claim"] = combined
    record.provenance[0].exact_claim_text = combined
    prop = deepcopy(second.phase8["propositions"][0])
    prop.update(proposition_id="claim:p2", reported_verdict=state)
    prop["original_span"].update(start=len(first_claim + separator), end=len(combined))
    prop["evidence_bindings"][0].update(
        binding_id="b2",
        proposition_id="claim:p2",
        evidence_id="e2",
        observation="unknown" if state == "unknown" else "support",
        directness="indirect" if state == "unsupported" else "direct",
    )
    evidence = second.evidence[0].model_copy(update={"evidence_id": "e2"})
    finding = second.findings[0].model_copy(
        update={"finding_id": "claim:p2", "supporting_evidence_ids": ["e2"]}
    )
    client = second.client_findings[0].model_copy(
        update={
            "client_finding_id": "client2",
            "parent_finding_id": "claim:p2",
            "referenced_evidence_ids": ["e2"],
        }
    )
    record.evidence.append(evidence)
    record.findings.append(finding)
    record.client_findings.append(client)
    description = deepcopy(second.phase8["evidence_descriptions"][0])
    description["evidence_id"] = "e2"
    record.phase8["evidence_descriptions"].append(description)
    record.phase8["propositions"].append(prop)
    record.phase8["required_proposition_ids"].append("claim:p2")
    record.phase8["logic"] = {
        "operator": operator,
        "children": [
            {"operator": "leaf", "proposition_id": pid}
            for pid in ("claim:p1", "claim:p2")
        ],
    }
    for t in second.phase8["transformations"]:
        t = deepcopy(t)
        t["transformation_id"] += "-second"
        t["target_id"] = "client2" if t["stage"] == "summary" else "claim:p2"
        t["from_proposition_ids"] = ["claim:p2"]
        if t["stage"] == "summary":
            t["asserted_state"] = state
            t["asserts_whole_claim"] = False
        record.phase8["transformations"].append(t)
    for t in record.phase8["transformations"]:
        if t["stage"] == "summary":
            t["asserts_whole_claim"] = False


@pytest.mark.parametrize(
    "core", ["overstatement", "causal_inference", "mechanism_to_outcome"]
)
def test_supported_or_cannot_be_relabeled_from_unsupported_alternative(core):
    record = taxonomy_record(
        core, noncausal_result_used=True, described_biological_mechanism=True
    )
    profile = record.phase8["evidence_descriptions"][0]
    if core == "mechanism_to_outcome":
        profile.update(evidence_type="animal", randomized=None)
        profile["attributes"].update(species="mouse", relation="mechanism")
    else:
        profile.update(evidence_type="observational", randomized=None)
        profile["attributes"]["relation"] = "association"
    summary_state(record, "unsupported")
    add_logical_component(record, operator="or", state="supported")
    assert evaluate_phase8(record).composite_state == "supported"
    assert result(record)["derived_label"] is None


def test_unknown_and_does_not_force_overstatement_label():
    record = taxonomy_record("overstatement")
    record.phase8["evidence_descriptions"][0].update(
        evidence_type="observational", randomized=None
    )
    summary_state(record, "unsupported")
    add_logical_component(record, operator="and", state="unknown")
    assert evaluate_phase8(record).composite_state == "unknown"
    assert result(record)["derived_label"] is None


def test_supported_or_with_honest_selected_supported_proposition_can_remain_solid():
    record = taxonomy_record()
    add_logical_component(record, operator="or", state="unknown")
    assert evaluate_phase8(record).composite_state == "supported"
    assert result(record)["derived_label"] == "solid"


def test_unsupported_and_cannot_borrow_an_unreferenced_components_gap():
    record = taxonomy_record("overstatement")
    add_logical_component(record, operator="and", state="unsupported")
    semantics = evaluate_phase8(record)
    assert semantics.technical_status == "completed"
    assert semantics.composite_state == "unsupported"
    assert {p.proposition_id: p.derived_state for p in semantics.propositions} == {
        "claim:p1": "supported",
        "claim:p2": "unsupported",
    }
    assert record.phase8_taxonomy["proposition_ids"] == ["claim:p1"]
    assert assess_taxonomy(record, semantics)["derived_label"] is None
