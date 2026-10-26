"""Synthetic contract regressions, separate from efficacy/acceptance holdouts."""

from __future__ import annotations

from copy import deepcopy
from itertools import product

import pytest

from agent_arena.phase8_models import ClaimLogic, PropositionLedger, proposition_id
from agent_arena.phase8_semantics import aggregate_claim
from agent_arena.phase8_semantics import evaluate_phase8 as _evaluate_phase8
from agent_arena.schemas import (
    ClaimProvenance, ClientFinding, ForensicRecord, InternalFinding, NegativeEvidenceAssertion,
    QAEvidenceItem, SearchScope,
)


def ledger_record(states=("supported", "supported"), operator="and"):
    original = "X activates pathway Y and reduces events."
    props, descriptions, transforms, findings, clients = [], [], [], [], []
    attrs = {"species": "human", "population": "adults", "intervention": "X",
             "comparator": "placebo", "endpoint": "events", "endpoint_type": "clinical_event",
             "relation": "causal", "follow_up": "12 weeks", "certainty": "asserted",
             "comparison": "between"}
    for index, state in enumerate(states, 1):
        pid = proposition_id("claim-1", f"p{index}")
        props.append({
            "proposition_id": pid, "parent_claim_id": "claim-1",
            "proposition_text": f"Component {index}",
            "original_span": {"start": 0, "end": len(original), "text": original},
            "materiality": "required", "attributes": deepcopy(attrs),
            "evidence_bindings": [{"binding_id": f"b{index}", "proposition_id": pid,
                                   "evidence_id": f"e{index}",
                                   "directness": "indirect" if state == "unsupported" else "direct",
                                   "observation": {"supported": "support", "unsupported": "support",
                                                   "contradicted": "contradiction",
                                                   "unknown": "inconclusive"}[state],
                                   "reason": "Source observation"}],
            "reported_verdict": state, "uncertainty": [], "reason": "Executed assessment",
            "provenance_id": "prov-1", "search_question": f"Evidence for component {index}?",
            "search_scope_ids": ["review"],
        })
        descriptions.append({"evidence_id": f"e{index}", "evidence_type": "controlled_intervention",
                             "source_role": "primary study", "attributes": deepcopy(attrs),
                             "randomized": True, "study_id": f"study{index}"})
        findings.append(InternalFinding(
            finding_id=pid, provenance_id="prov-1", proposition=props[-1]["proposition_text"],
            supporting_evidence_ids=[] if state == "contradicted" else [f"e{index}"],
            contrary_evidence_ids=[f"e{index}"] if state == "contradicted" else [],
        ))
        clients.append(ClientFinding(
            client_finding_id=f"c{index}", parent_finding_id=pid, provenance_id="prov-1",
            display_claim=props[-1]["proposition_text"], referenced_evidence_ids=[f"e{index}"],
        ))
        for stage in ("extraction", "search_question", "internal", "summary"):
            transforms.append({
                "transformation_id": f"t{index}-{stage}", "stage": stage,
                "target_id": f"c{index}" if stage == "summary" else pid,
                "from_proposition_ids": [pid],
                "from_text": original if stage == "extraction" else props[-1]["proposition_text"],
                "to_text": props[-1]["search_question"] if stage == "search_question" else
                props[-1]["proposition_text"],
                "from_attributes": deepcopy(attrs), "to_attributes": deepcopy(attrs),
                "asserted_state": state if stage == "summary" else None,
                "reason": "Meaning preserved",
            })
    ids = [p["proposition_id"] for p in props]
    return ForensicRecord(
        record_id="synthetic-phase8", provenance=[ClaimProvenance(
            provenance_id="prov-1", exact_claim_text=original, source_id="input")],
        evidence=[QAEvidenceItem(evidence_id=f"e{i}", source_id="input",
                                 role="contradictory" if state == "contradicted" else "supporting")
                  for i, state in enumerate(states, 1)],
        findings=findings, client_findings=clients,
        search_scopes=[SearchScope(search_scope_id="review", scope_type="reviewed_set",
                                   reviewed_source_ids=["input"])],
        phase8={"claim_id": "claim-1", "provenance_id": "prov-1", "original_claim": original,
                "required_proposition_ids": ids, "propositions": props,
                "logic": {"operator": operator,
                          "children": [{"operator": "leaf", "proposition_id": pid}
                                       for pid in ids]},
                "extraction_provenance": "synthetic offline development fixture",
                "evidence_descriptions": descriptions, "transformations": transforms},
    )


# Exhaustive binary truth tables are the normative contract, not a numeric rank.
STATES = ("supported", "unsupported", "contradicted", "unknown")
AND = (
    ("supported", "unsupported", "contradicted", "unknown"),
    ("unsupported", "unsupported", "contradicted", "unknown"),
    ("contradicted", "contradicted", "contradicted", "contradicted"),
    ("unknown", "unknown", "contradicted", "unknown"),
)
OR = (
    ("supported", "supported", "supported", "supported"),
    ("supported", "unsupported", "unsupported", "unknown"),
    ("supported", "unsupported", "contradicted", "unknown"),
    ("supported", "unknown", "unknown", "unknown"),
)


@pytest.mark.parametrize("left,right", product(range(4), repeat=2))
@pytest.mark.parametrize("operator,table", [("and", AND), ("or", OR)])
def test_composite_truth_tables(left, right, operator, table):
    record = ledger_record((STATES[left], STATES[right]), operator)
    result = evaluate_phase8(record)
    assert result.technical_status == "completed"
    assert result.composite_state == table[left][right]
    assert [p.derived_state for p in result.propositions] == [STATES[left], STATES[right]]


def test_nested_alternatives_keep_unknown_visible_and_preserve_extraction():
    record = ledger_record(("supported", "unknown", "supported"))
    leaves = record.phase8["logic"]["children"]
    record.phase8["logic"]["children"] = [
        {"operator": "or", "children": leaves[:2]}, leaves[2],
    ]
    original = deepcopy(record.model_dump())
    result = evaluate_phase8(record)
    assert result.composite_state == "supported"
    assert result.propositions[1].derived_state == "unknown"
    assert record.model_dump() == original


@pytest.mark.parametrize("mutation", [
    lambda data: data.update(propositions=[]),
    lambda data: data.update(required_proposition_ids=[]),
    lambda data: data["propositions"].pop(),
    lambda data: data["required_proposition_ids"].append("claim-1:missing"),
    lambda data: data["logic"].update(children=[]),
    lambda data: data["logic"]["children"].pop(),
    lambda data: data["propositions"].append(deepcopy(data["propositions"][0])),
    lambda data: data["propositions"][0].update(parent_claim_id="different"),
    lambda data: data["propositions"][0].update(provenance_id="different"),
    lambda data: data["propositions"][0]["original_span"].update(text="rewritten"),
    lambda data: data["propositions"][0]["original_span"].update(end=1000),
    lambda data: data["propositions"][0]["evidence_bindings"][0].update(evidence_id="missing"),
    lambda data: data["propositions"][0]["evidence_bindings"][0].update(
        proposition_id="claim-1:p2"),
    lambda data: data["propositions"][0].update(evidence_bindings=[]),
    lambda data: data.update(original_claim="Model replacement original"),
    lambda data: data["propositions"][0].update(proposition_id="unbound-local-id"),
])
def test_structural_failures_are_incomplete_never_scientific_unknown_pass(mutation):
    record = ledger_record()
    mutation(record.phase8)
    result = evaluate_phase8(record)
    assert result.technical_status == "incomplete"
    assert result.composite_state == "unknown"
    assert result.reasons


def test_optional_context_is_preserved_but_cannot_supply_proof():
    record = ledger_record(("supported", "unknown"))
    record.phase8["propositions"][1]["materiality"] = "optional"
    record.phase8["required_proposition_ids"].pop()
    assert evaluate_phase8(record).technical_status == "incomplete"
    record.phase8["logic"]["children"].pop()
    record.phase8["transformations"] = [t for t in record.phase8["transformations"]
                                       if t["target_id"] != "claim-1:p2"]
    result = evaluate_phase8(record)
    assert result.technical_status == "completed"
    assert result.composite_state == "supported"
    assert len(result.propositions) == 2


def test_legacy_unexecuted_differs_from_executed_unknown():
    record = ledger_record(("unknown",))
    assert evaluate_phase8(record).technical_status == "completed"
    assert evaluate_phase8(record).composite_state == "unknown"
    record.phase8 = None
    assert evaluate_phase8(record).technical_status == "not_executed"


def test_invalid_schema_and_empty_record_fail_closed():
    record = ledger_record()
    record.phase8["propositions"][0]["materiality"] = "whatever passes"
    assert evaluate_phase8(record).technical_status == "incomplete"
    record.phase8 = {}
    assert evaluate_phase8(record).technical_status == "incomplete"
    record.phase8 = ledger_record().phase8
    record.provenance = []
    assert evaluate_phase8(record).technical_status == "incomplete"


def test_single_leaf_and_stable_claim_bound_ids():
    record = ledger_record(("supported",))
    record.phase8["logic"] = record.phase8["logic"]["children"][0]
    assert evaluate_phase8(record).composite_state == "supported"
    assert proposition_id("claim-1", "p1") == proposition_id("claim-1", "p1")
    assert proposition_id("claim-2", "p1") != proposition_id("claim-1", "p1")
    ledger = PropositionLedger.model_validate(record.phase8)
    assert ledger.propositions[0].proposition_id == "claim-1:p1"


def test_aggregation_helper_rejects_vacuous_or_unresolved_calls():
    with pytest.raises(ValueError):
        aggregate_claim(ClaimLogic(operator="and"), {})
    with pytest.raises(ValueError):
        aggregate_claim(ClaimLogic(operator="leaf", proposition_id="missing"), {})


# id(record) -> index of the proposition whose model judgment expect_summary set in this test.
_MODEL_JUDGMENT_SET: dict[int, int] = {}


@pytest.fixture(autouse=True)
def _fresh_expectations():
    _MODEL_JUDGMENT_SET.clear()
    yield
    _MODEL_JUDGMENT_SET.clear()


def evaluate_phase8(record):
    """Evaluate; where expect_summary set the model judgment, the host must derive that state.

    Otherwise a model judgment equal to the expected state would mask a host rule: a model
    UNKNOWN makes the effective state unknown whatever the host derives (AA-P8/1.1).
    """
    result = _evaluate_phase8(record)
    index = _MODEL_JUDGMENT_SET.get(id(record))
    if index is not None and result.technical_status == "completed":
        prop = result.propositions[index]
        assert prop.host_state == prop.reported_verdict, (prop.host_state, prop.reported_verdict, prop.reasons)
    return result


def expect_summary(record, state, index=0, *, model_judgment=True):
    """Set the summary assertion; by default the model judgment says the same (AA-P8/1.1 C25).

    Host-rule tests then check the host derivation itself: evaluate_phase8 above asserts that the
    host derives exactly this state, so neither a conflict nor a masking model UNKNOWN passes.
    """
    if model_judgment:
        record.phase8["propositions"][index]["reported_verdict"] = state
        _MODEL_JUDGMENT_SET[id(record)] = index
    else:
        _MODEL_JUDGMENT_SET.pop(id(record), None)
    for trans in record.phase8["transformations"]:
        if trans["stage"] == "summary" and trans["target_id"] == f"c{index + 1}":
            trans["asserted_state"] = state


def claim_attributes(record, index=0, **changes):
    prop = record.phase8["propositions"][index]
    prop["attributes"].update(changes)
    for trans in record.phase8["transformations"]:
        if prop["proposition_id"] in trans["from_proposition_ids"]:
            trans["from_attributes"].update(changes)
            trans["to_attributes"].update(changes)


@pytest.mark.parametrize("dimension,other", [
    ("population", "children"), ("species", "mouse"), ("endpoint", "biomarker"),
    ("endpoint_type", "biomarker"), ("comparator", "baseline"),
    ("follow_up", "1 week"), ("comparison", "within"),
    ("intervention", "ingredient Y"), ("dose", "1 mg"),
    ("formulation", "capsule"), ("route", "topical"),
    ("effect_magnitude", "10%"), ("effect_basis", "relative"),
])
def test_material_attribute_mismatch_and_direct_matched_control(dimension, other):
    record = ledger_record(("supported",))
    if dimension not in record.phase8["propositions"][0]["attributes"]:
        claim_attributes(record, **{dimension: "target value"})
    profile = record.phase8["evidence_descriptions"][0]
    target = record.phase8["propositions"][0]["attributes"][dimension]
    profile["attributes"][dimension] = other
    expect_summary(record, "unsupported")
    result = evaluate_phase8(record)
    assert result.technical_status == "completed", result.reasons
    assert result.composite_state == "unsupported"
    profile["attributes"][dimension] = target
    expect_summary(record, "supported")
    assert evaluate_phase8(record).composite_state == "supported"


def test_empty_material_list_cannot_opt_out_and_missing_is_scientific_unknown():
    record = ledger_record(("supported",))
    claim_attributes(record, population=None)
    record.phase8["propositions"][0]["material_dimensions"] = []
    expect_summary(record, "unknown")
    result = evaluate_phase8(record)
    assert result.technical_status == "completed"
    assert result.composite_state == "unknown"
    assert any("population" in r for r in result.propositions[0].reasons)


@pytest.mark.parametrize("kind,randomized,expected", [
    ("observational", None, "unsupported"), ("controlled_intervention", False, "unsupported"),
    ("controlled_intervention", None, "unknown"), ("unknown", None, "unknown"),
    ("controlled_intervention", True, "supported"),
])
def test_causal_capability_requires_identification(kind, randomized, expected):
    record = ledger_record(("supported",))
    record.phase8["evidence_descriptions"][0].update(evidence_type=kind, randomized=randomized)
    expect_summary(record, expected)
    assert evaluate_phase8(record).composite_state == expected


def test_valid_observation_and_mouse_mechanism_do_not_need_clinical_evidence():
    record = ledger_record(("supported",))
    claim_attributes(record, relation="association")
    record.phase8["evidence_descriptions"][0].update(evidence_type="observational", randomized=None)
    assert evaluate_phase8(record).composite_state == "supported"
    claim_attributes(record, relation="mechanism", species="mouse", population="adult mice")
    profile = record.phase8["evidence_descriptions"][0]
    profile.update(evidence_type="animal", quality="high")
    profile["attributes"].update(species="mouse", population="adult mice")
    assert evaluate_phase8(record).composite_state == "supported"
    claim_attributes(record, relation="human_clinical_benefit", species="human", population="adults")
    expect_summary(record, "unsupported")
    assert evaluate_phase8(record).composite_state == "unsupported"


def test_human_surrogate_trial_cannot_establish_clinical_benefit():
    record = ledger_record(("supported",))
    claim_attributes(record, relation="human_clinical_benefit", endpoint_type="biomarker")
    record.phase8["evidence_descriptions"][0]["attributes"]["endpoint_type"] = "biomarker"
    expect_summary(record, "unsupported")
    assert evaluate_phase8(record).composite_state == "unsupported"
    claim_attributes(record, relation="causal")
    expect_summary(record, "supported")
    assert evaluate_phase8(record).composite_state == "supported"


def test_unresolved_design_limitation_and_within_arm_cannot_be_rescued_by_quality():
    record = ledger_record(("supported",))
    profile = record.phase8["evidence_descriptions"][0]
    profile.update(design_limitations=["unresolved allocation confounding"], quality="excellent")
    expect_summary(record, "unknown")
    assert evaluate_phase8(record).composite_state == "unknown"
    profile["design_limitations"] = []
    claim_attributes(record, comparison="within")
    profile["attributes"]["comparison"] = "within"
    expect_summary(record, "unsupported")
    assert evaluate_phase8(record).composite_state == "unsupported"


def add_auxiliary_evidence(record, eid="bridge-evidence"):
    record.evidence.append(QAEvidenceItem(evidence_id=eid, source_id="input", text="Support span"))
    profile = deepcopy(record.phase8["evidence_descriptions"][0])
    profile["evidence_id"] = eid
    profile["study_id"] = eid
    record.phase8["evidence_descriptions"].append(profile)
    return profile


def test_source_bound_product_transfer_requires_matching_capable_evidence():
    record = ledger_record(("supported",))
    auxiliary = add_auxiliary_evidence(record)
    record.phase8["evidence_descriptions"][0]["attributes"]["intervention"] = "ingredient"
    record.phase8["product_transfers"] = [{
        "transfer_id": "transfer", "binding_id": "b1", "state": "supported_transfer",
        "dimensions": ["intervention"], "evidence_ids": [], "reason": "Declared equivalence",
    }]
    # Auxiliary evidence is not allowed to sit unbound in the record.
    record.phase8["product_transfers"][0]["evidence_ids"] = ["bridge-evidence"]
    auxiliary["attributes"]["intervention"] = "other product"
    expect_summary(record, "unsupported")
    assert evaluate_phase8(record).composite_state == "unsupported"
    auxiliary["attributes"]["intervention"] = "X"
    expect_summary(record, "supported")
    assert evaluate_phase8(record).composite_state == "supported"


def test_mechanism_bridge_requires_actual_capable_evidence_and_records_partial_unknown():
    record = ledger_record(("supported", "unsupported"))
    claim_attributes(record, 0, relation="mechanism")
    claim_attributes(record, 1, relation="human_clinical_benefit")
    record.phase8["evidence_descriptions"][0]["evidence_type"] = "mechanistic"
    record.phase8["evidence_descriptions"][1]["evidence_type"] = "mechanistic"
    prop = record.phase8["propositions"][1]
    prop["reported_verdict"] = "supported"
    prop["premise_proposition_ids"] = ["claim-1:p1"]
    assert evaluate_phase8(record).technical_status == "incomplete"
    prop["required_bridge_ids"] = ["bridge"]
    record.phase8["bridges"] = [{
        "bridge_id": "bridge", "kind": "mechanism_to_outcome",
        "premise_proposition_ids": ["claim-1:p1"], "conclusion_proposition_id": "claim-1:p2",
        "state": "partial", "evidence_ids": ["e1"], "reason": "Plausibility only",
    }]
    expect_summary(record, "unknown", 1)
    assert evaluate_phase8(record).composite_state == "unknown"
    record.phase8["bridges"][0]["state"] = "supported"
    assert evaluate_phase8(record).composite_state == "unknown"
    auxiliary = add_auxiliary_evidence(record)
    auxiliary.update(evidence_type="controlled_intervention", randomized=True)
    record.phase8["bridges"][0]["evidence_ids"] = ["bridge-evidence"]
    expect_summary(record, "supported", 1)
    assert evaluate_phase8(record).composite_state == "supported"


@pytest.mark.parametrize("observation", ["search_incomplete", "no_effect_observed", "inconclusive", "unknown"])
def test_negative_and_inconclusive_observations_are_not_contradiction(observation):
    record = ledger_record(("supported",))
    record.phase8["propositions"][0]["evidence_bindings"][0]["observation"] = observation
    # AA-P8/1.1: the summary restates the model's own judgment; the host derives unknown
    # (never contradicted) and the difference is an open conflict, not a silent override.
    expect_summary(record, "supported", model_judgment=False)
    result = evaluate_phase8(record)
    assert result.technical_status == "completed"
    assert result.composite_state == "unknown"
    assert result.propositions[0].reported_verdict == "supported"
    assert result.propositions[0].host_state == "unknown"
    assert result.propositions[0].model_host_conflict is True
    assert [(c.scope, c.model_state, c.host_state) for c in result.model_host_conflicts] == [
        ("proposition", "supported", "unknown"), ("composite", "supported", "unknown")]


def test_no_effect_is_honestly_reportable_without_proving_zero_effect():
    record = ledger_record(("supported",))
    p = record.phase8["propositions"][0]
    p["evidence_bindings"][0]["observation"] = "no_effect_observed"
    p["observation_target"] = "no_effect_observed"
    claim_attributes(record, relation="description")
    assert evaluate_phase8(record).composite_state == "supported"
    p["observation_target"] = None
    expect_summary(record, "unknown")
    assert evaluate_phase8(record).composite_state == "unknown"


def test_no_evidence_found_is_bounded_by_actual_scope():
    record = ledger_record(("supported",))
    p = record.phase8["propositions"][0]
    b = p["evidence_bindings"][0]
    b.update(observation="no_evidence_found", search_scope_id="review")
    record.negative_assertions.append(NegativeEvidenceAssertion(
        assertion_id="neg", finding_id="claim-1:p1", proposition=p["proposition_text"],
        assertion_scope="reviewed_set", search_scope_id="review",
    ))
    expect_summary(record, "unknown")
    assert evaluate_phase8(record).composite_state == "unknown"
    p["observation_target"] = "no_evidence_found"
    claim_attributes(record, relation="description")
    expect_summary(record, "supported")
    assert evaluate_phase8(record).composite_state == "supported"
    record.search_scopes[0].reviewed_source_ids = []
    expect_summary(record, "unknown")
    assert evaluate_phase8(record).composite_state == "unknown"


def test_conflict_and_dependent_evidence_cannot_create_certainty():
    record = ledger_record(("supported",))
    auxiliary = add_auxiliary_evidence(record)
    auxiliary["study_id"] = "study1"
    record.evidence[-1].role = record.evidence[0].role.__class__.CONTRADICTORY
    record.findings[0].contrary_evidence_ids.append("bridge-evidence")
    p = record.phase8["propositions"][0]
    p["evidence_bindings"].append({"binding_id": "b2", "proposition_id": p["proposition_id"],
                                    "evidence_id": "bridge-evidence", "directness": "direct",
                                    "observation": "contradiction", "reason": "Contrary result"})
    expect_summary(record, "unknown")
    result = evaluate_phase8(record)
    assert result.composite_state == "unknown"
    assert result.propositions[0].dependency_status == "dependent"
    assert any("conflicting" in r for r in result.propositions[0].reasons)
    auxiliary["study_id"] = None
    assert evaluate_phase8(record).propositions[0].dependency_status == "unknown"


@pytest.mark.parametrize("dimension,value", [
    ("population", "everybody"), ("endpoint", "mortality"), ("comparator", None),
    ("relation", "human_clinical_benefit"), ("effect_magnitude", "100%"),
    ("intervention", "marketed product"), ("certainty", "certain"),
])
def test_own_summary_semantic_changes_are_detected(dimension, value):
    record = ledger_record(("supported",))
    if dimension == "certainty":
        claim_attributes(record, certainty="possible")
    summary = next(t for t in record.phase8["transformations"] if t["stage"] == "summary")
    summary["to_attributes"][dimension] = value
    result = evaluate_phase8(record)
    assert result.technical_status == "incomplete"
    assert any(dimension in f for f in result.transformation_findings)


def test_mandatory_transformations_cannot_be_skipped_or_rebound():
    record = ledger_record(("supported",))
    record.phase8["transformations"] = []
    assert evaluate_phase8(record).technical_status == "incomplete"
    record = ledger_record(("supported",))
    record.phase8["transformations"][0]["from_text"] = "invented original"
    assert evaluate_phase8(record).technical_status == "incomplete"


def test_summary_cannot_promote_partial_to_whole_or_hide_unknown():
    record = ledger_record(("supported", "unknown"))
    summary = next(t for t in record.phase8["transformations"] if t["target_id"] == "c1")
    summary["asserts_whole_claim"] = True
    result = evaluate_phase8(record)
    assert result.technical_status == "incomplete"
    assert any("partial-to-whole" in f for f in result.transformation_findings)
    # The whole-claim assertion restates the model's own composite (supported AND unknown).
    expect_summary(record, "unknown", 0, model_judgment=False)
    assert evaluate_phase8(record).technical_status == "completed"


def test_hedge_removal_is_detected_even_if_producer_attributes_claim_no_change():
    record = ledger_record(("supported",))
    p = record.phase8["propositions"][0]
    p["proposition_text"] = "X may reduce events."
    record.findings[0].proposition = p["proposition_text"]
    for t in record.phase8["transformations"]:
        if t["stage"] == "extraction":
            t["to_text"] = p["proposition_text"]
        else:
            t["from_text"] = p["proposition_text"]
            if t["stage"] == "internal":
                t["to_text"] = p["proposition_text"]
    result = evaluate_phase8(record)
    assert any("hedge removed" in f for f in result.transformation_findings)


def test_source_bound_identification_argument_and_review_underlying_capability():
    record = ledger_record(("supported",))
    auxiliary = add_auxiliary_evidence(record)
    profile = record.phase8["evidence_descriptions"][0]
    profile.update(randomized=False, identification_argument="Support span",
                   identification_evidence_ids=["bridge-evidence"])
    assert evaluate_phase8(record).composite_state == "supported"
    profile["identification_argument"] = "made up"
    assert evaluate_phase8(record).technical_status == "incomplete"
    profile.update(identification_argument=None, identification_evidence_ids=[],
                   evidence_type="review", underlying_evidence_ids=["bridge-evidence"])
    assert evaluate_phase8(record).composite_state == "supported"
    auxiliary["evidence_type"] = "observational"
    expect_summary(record, "unsupported")
    assert evaluate_phase8(record).composite_state == "unsupported"


def test_same_source_has_proposition_specific_directness_and_does_not_cancel_valid_support():
    record = ledger_record(("supported", "unsupported"))
    record.phase8["propositions"][1]["evidence_bindings"][0]["evidence_id"] = "e1"
    record.findings[1].supporting_evidence_ids = ["e1"]
    record.client_findings[1].referenced_evidence_ids = ["e1"]
    record.evidence.pop()
    record.phase8["evidence_descriptions"].pop()
    result = evaluate_phase8(record)
    assert [p.derived_state for p in result.propositions] == ["supported", "unsupported"]
    # An extra indirect item cannot erase an independent direct capable result.
    p = record.phase8["propositions"][0]
    p["evidence_bindings"].append({"binding_id": "extra", "proposition_id": p["proposition_id"],
                                    "evidence_id": "e1", "directness": "indirect",
                                    "observation": "support", "reason": "Indirect reuse"})
    assert evaluate_phase8(record).propositions[0].derived_state == "supported"


def test_valid_certainty_narrowing_and_failed_summary_keep_computed_state():
    record = ledger_record(("supported",))
    summary = next(t for t in record.phase8["transformations"] if t["stage"] == "summary")
    summary["to_attributes"]["certainty"] = "possible"
    assert evaluate_phase8(record).technical_status == "completed"
    summary["to_attributes"]["population"] = "everyone"
    result = evaluate_phase8(record)
    assert result.technical_status == "incomplete"
    assert result.composite_state == "unknown"
    assert result.assessed_composite_state == "supported"


def test_auxiliary_free_text_cannot_avoid_transformation_audit():
    record = ledger_record(("supported",))
    record.client_findings[0].client_explanation = "This certainly prevents every event."
    assert evaluate_phase8(record).technical_status == "incomplete"
    record = ledger_record(("supported",))
    record.findings[0].verdict_summary = "Entire composite proved."
    assert evaluate_phase8(record).technical_status == "incomplete"


@pytest.mark.parametrize("reported", ["unknown", "unsupported", "contradicted"])
def test_consistent_support_structure_cannot_overwrite_reported_uncertainty_or_conflict(reported):
    record = ledger_record(("supported",))
    record.phase8["propositions"][0]["reported_verdict"] = reported
    expect_summary(record, reported, model_judgment=False)
    result = evaluate_phase8(record)
    assert result.technical_status == "completed"
    assert result.composite_state == "unknown"
    assert result.propositions[0].reported_verdict == reported
    # AA-P8/1.1: the host keeps its own derivation; the model judgment is never overwritten and
    # the disagreement (including a model UNKNOWN) is an explicit conflict.
    assert result.propositions[0].host_state == "supported"
    assert result.propositions[0].model_host_conflict is True
    assert result.host_composite_state == "supported" and result.model_composite_state == reported


@pytest.mark.parametrize("unknown", [None, "unknown", " unspecified ", "not reported", "unresolved"])
def test_matching_unknown_attribute_placeholders_are_not_support(unknown):
    record = ledger_record(("supported",))
    claim_attributes(record, population=unknown)
    record.phase8["evidence_descriptions"][0]["attributes"]["population"] = unknown
    expect_summary(record, "unknown")
    result = evaluate_phase8(record)
    assert result.technical_status == "completed"
    assert result.composite_state == "unknown"


@pytest.mark.parametrize("reverse", [False, True])
def test_required_bridge_constraints_do_not_depend_on_iteration_order(reverse):
    record = ledger_record(("supported",))
    record.phase8["propositions"][0]["evidence_bindings"][0]["directness"] = "indirect"
    add_auxiliary_evidence(record)
    record.phase8["bridges"] = [{
        "bridge_id": bid, "kind": "semantic_transfer", "conclusion_proposition_id": "claim-1:p1",
        "state": state, "evidence_ids": ["bridge-evidence"] if state == "supported" else [],
        "reason": "Independent necessary represented inference",
    } for bid, state in (("resolved", "supported"), ("unresolved", "unknown"))]
    required = ["resolved", "unresolved"]
    record.phase8["propositions"][0]["required_bridge_ids"] = required[::-1] if reverse else required
    expect_summary(record, "unknown")
    result = evaluate_phase8(record)
    assert result.technical_status == "completed"
    assert result.composite_state == "unknown"


@pytest.mark.parametrize("roles,expected", [
    (["supporting"], "supported"), (["contradictory"], "contradicted"),
    (["supporting", "contradictory"], "unknown"),
])
def test_review_preserves_underlying_direction_and_conflict(roles, expected):
    record = ledger_record(("supported",))
    underlying = []
    for index, role in enumerate(roles):
        eid = f"underlying-{index}"
        add_auxiliary_evidence(record, eid)
        record.evidence[-1].role = record.evidence[-1].role.__class__(role)
        underlying.append(eid)
    record.phase8["evidence_descriptions"][0].update(
        evidence_type="review", underlying_evidence_ids=underlying,
    )
    expect_summary(record, expected)
    result = evaluate_phase8(record)
    assert result.technical_status == "completed", result.reasons
    assert result.composite_state == expected


@pytest.mark.parametrize("scope_type,sources", [
    ("invalid", ["input"]), ("reviewed_set", []), ("reviewed_set", ["different-source"]),
    ("documented_search", ["input"]),
])
def test_search_scope_requires_valid_substantiated_source_basis(scope_type, sources):
    record = ledger_record(("supported",))
    record.search_scopes[0].scope_type = scope_type
    record.search_scopes[0].reviewed_source_ids = sources
    assert evaluate_phase8(record).technical_status == "incomplete"


def test_specific_binding_scope_and_review_underlying_sources_must_cover_actual_evidence():
    record = ledger_record(("supported",))
    record.search_scopes.append(SearchScope(search_scope_id="other", scope_type="reviewed_set",
                                           reviewed_source_ids=["context"]))
    record.phase8["propositions"][0]["evidence_bindings"][0]["search_scope_id"] = "other"
    assert evaluate_phase8(record).technical_status == "incomplete"
    record.phase8["propositions"][0]["evidence_bindings"][0]["search_scope_id"] = "review"
    add_auxiliary_evidence(record)
    record.evidence[-1].source_id = "context"
    record.phase8["evidence_descriptions"][0].update(
        evidence_type="review", underlying_evidence_ids=["bridge-evidence"],
    )
    assert evaluate_phase8(record).technical_status == "incomplete"
    record.search_scopes[0].reviewed_source_ids.append("context")
    assert evaluate_phase8(record).composite_state == "supported"


@pytest.mark.parametrize("mixed,wrong_population,expected", [
    (False, False, "contradicted"), (True, False, "unknown"),
    (True, True, "supported"),
])
def test_review_actual_opposite_effect_direction_preserves_relevant_contradiction(
    mixed, wrong_population, expected,
):
    record = ledger_record(("supported",))
    claim_attributes(record, effect_direction="decrease")
    record.phase8["evidence_descriptions"][0]["attributes"]["effect_direction"] = "decrease"
    ids = []
    if mixed:
        add_auxiliary_evidence(record, "support")
        ids.append("support")
    contrary = add_auxiliary_evidence(record, "contrary")
    contrary["attributes"]["effect_direction"] = "increase"
    if wrong_population:
        contrary["attributes"]["population"] = "different population"
    record.evidence[-1].role = record.evidence[-1].role.__class__.CONTRADICTORY
    ids.append("contrary")
    record.phase8["evidence_descriptions"][0].update(evidence_type="review", underlying_evidence_ids=ids)
    expect_summary(record, expected)
    result = evaluate_phase8(record)
    assert result.technical_status == "completed", result.reasons
    assert result.composite_state == expected


@pytest.mark.parametrize("directness", ["direct", "partial", "indirect", "remote", "unknown"])
def test_review_contradiction_is_limited_by_its_proposition_directness(directness):
    record = ledger_record(("supported",))
    add_auxiliary_evidence(record)
    record.evidence[-1].role = record.evidence[-1].role.__class__.CONTRADICTORY
    record.phase8["evidence_descriptions"][0].update(
        evidence_type="review", underlying_evidence_ids=["bridge-evidence"],
    )
    record.phase8["propositions"][0]["evidence_bindings"][0]["directness"] = directness
    expected = "contradicted" if directness == "direct" else "unknown"
    expect_summary(record, expected)
    result = evaluate_phase8(record)
    assert result.technical_status == "completed", result.reasons
    assert result.composite_state == expected
