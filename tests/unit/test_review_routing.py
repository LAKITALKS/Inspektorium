"""Offline development cases for AA-P9 routing, separate from final acceptance."""

import json
from copy import deepcopy

import pytest

from inspektorium.audit.integrity.output_contract import parse_structured_output
from inspektorium.audit.review.routing import (
    assess_case,
    case_key,
    position_from_result,
)
from inspektorium.audit.schemas import AgentResult, Task
from tests.forensics_case_factory import raw_record


def case():
    claim, context, payload = raw_record()
    task = Task(
        id="phase9-case",
        title="Review case",
        domain="study_forensics",
        difficulty="medium",
        task_type="study_forensics",
        prompt=claim,
        context=context,
    )
    return task, payload


def position(
    task,
    payload,
    *,
    run_id="run1",
    origin="original",
    label="solid",
    confidence=0.82,
    explanation="First wording",
):
    raw = json.dumps(
        {
            "final_answer": label,
            "confidence": confidence,
            "steps": [explanation],
            "forensic_record": payload,
        }
    )
    parsed, diag = parse_structured_output(raw)
    result = AgentResult(
        provider="recorded-offline",
        model="offline-fixture",
        raw_output=raw,
        parsed=parsed,
        parse_ok=diag.ok,
    )
    return position_from_result(task, result, run_id, origin)


def state(payload, desired):
    p = payload["phase8"]["propositions"][0]
    # AA-P8/1.1: a stable case is one where the model judgment and host derivation agree.
    p["reported_verdict"] = desired
    b = p["evidence_bindings"][0]
    b["observation"] = {
        "supported": "support",
        "unsupported": "support",
        "contradicted": "contradiction",
        "unknown": "inconclusive",
    }[desired]
    b["directness"] = "indirect" if desired == "unsupported" else "direct"
    payload["evidence"][0]["role"] = (
        "contradictory" if desired == "contradicted" else "supporting"
    )
    payload["findings"][0]["supporting_evidence_ids"] = (
        [] if desired == "contradicted" else ["e1"]
    )
    payload["findings"][0]["contrary_evidence_ids"] = (
        ["e1"] if desired == "contradicted" else []
    )
    for t in payload["phase8"]["transformations"]:
        if t["stage"] == "summary":
            t["asserted_state"] = desired


def coherent_attribute(payload, name, value):
    payload["phase8"]["propositions"][0]["attributes"][name] = value
    payload["phase8"]["evidence_descriptions"][0]["attributes"][name] = value
    for t in payload["phase8"]["transformations"]:
        t["from_attributes"][name] = value
        t["to_attributes"][name] = value


@pytest.mark.parametrize("scientific", ["supported", "unsupported", "contradicted"])
def test_stable_positive_and_negative_cases_need_no_extra_review(scientific):
    task, payload = case()
    state(payload, scientific)
    first = position(task, payload)
    result = assess_case(task, [first])
    assert result.technical_status == "completed", result.reasons
    assert result.route == "AUTO_RESOLVABLE"
    assert result.mandatory is False
    assert result.execution_status == "not_executed"
    assert result.conflicts == []
    assert result.positions[0].phase8["composite_state"] == scientific


def test_confidence_and_explanatory_wording_alone_are_trivial():
    task, payload = case()
    first = position(task, payload, confidence=0.82)
    second = position(
        task,
        payload,
        run_id="run2",
        origin="model_review",
        confidence=0.78,
        explanation="Different explanatory wording",
    )
    result = assess_case(task, [first, second])
    assert result.route == "AUTO_RESOLVABLE"
    assert result.conflicts == []
    assert len(result.positions) == 2


def test_supported_vs_contradicted_same_proposition_is_material_and_preserved():
    task, payload = case()
    first = position(task, payload)
    opposite = deepcopy(payload)
    state(opposite, "contradicted")
    second = position(task, opposite, run_id="review", origin="model_review")
    before = deepcopy([first.model_dump(), second.model_dump()])
    result = assess_case(task, [first, second])
    assert result.route == "HUMAN_REVIEW_REQUIRED"
    assert result.mandatory is True
    assert any(
        c.field.endswith("derived_state")
        and c.proposition_ids == ["claim:p1"]
        and c.material
        for c in result.conflicts
    )
    assert any(c.dimension == "evidence" for c in result.conflicts)
    assert [first.model_dump(), second.model_dump()] == before
    assert all(c.resolution == "unresolved" for c in result.conflicts)


@pytest.mark.parametrize(
    "attribute,value,dimension",
    [
        ("population", "older adults", "proposition"),
        ("endpoint", "other event", "proposition"),
        ("relation", "association", "causal_strength"),
        ("intervention", "other product", "product_transfer"),
    ],
)
def test_bound_semantic_changes_trigger_even_when_both_verdicts_are_supported(
    attribute, value, dimension
):
    task, payload = case()
    changed = deepcopy(payload)
    coherent_attribute(changed, attribute, value)
    result = assess_case(
        task,
        [
            position(task, payload),
            position(task, changed, run_id="review", origin="model_review"),
        ],
    )
    assert result.route == "HUMAN_REVIEW_REQUIRED"
    assert any(
        c.dimension == dimension and c.field.endswith(attribute)
        for c in result.conflicts
    )


def test_scientific_unknown_is_not_unexecuted_and_requires_one_targeted_review_when_material():
    task, payload = case()
    state(payload, "unknown")
    result = assess_case(task, [position(task, payload)])
    assert result.technical_status == "completed"
    assert result.route == "REVIEW_RECOMMENDED"
    assert result.mandatory and result.review_state == "pending"
    assert result.execution_status == "not_executed"
    assert result.uncertainty
    assert any(
        t.code == "necessary_unknown" and t.proposition_ids == ["claim:p1"]
        for t in result.triggers
    )


def test_optional_unknown_context_does_not_force_human_or_counterreview():
    task, payload = case()
    p = deepcopy(payload["phase8"]["propositions"][0])
    p.update(
        proposition_id="claim:optional",
        materiality="optional",
        reported_verdict="unknown",
        evidence_bindings=[],
    )
    payload["phase8"]["propositions"].append(p)
    result = assess_case(task, [position(task, payload)])
    assert result.technical_status == "completed"
    assert result.route == "AUTO_RESOLVABLE"
    assert not result.mandatory
    assert result.uncertainty
    assert any(t.code == "bounded_unknown" and not t.mandatory for t in result.triggers)


@pytest.mark.parametrize(
    "model,host",
    [
        ("supported", "unsupported"),
        ("unsupported", "supported"),
        ("unknown", "supported"),
        ("supported", "contradicted"),
    ],
)
def test_model_host_difference_within_one_position_is_a_mandatory_review_trigger(
    model, host
):
    """AA-P9/1.1 replaces AA-P9/1.0 rule 1 ('a Phase8 ceiling within one position is not a
    disagreement') for model/host differences: both directions, also against a decisive host state."""
    task, payload = case()
    state(payload, host)
    payload["phase8"]["propositions"][0]["reported_verdict"] = model
    for t in payload["phase8"]["transformations"]:
        if t["stage"] == "summary":
            t["asserted_state"] = model
    p = position(task, payload, label="solid")
    assert p.phase8["technical_status"] == "completed", p.phase8["reasons"]
    assert p.phase8["propositions"][0]["host_state"] == host
    assert p.phase8["composite_state"] == "unknown"
    result = assess_case(task, [p])
    assert result.conflicts == []  # no position-to-position disagreement exists
    codes = {t.code for t in result.triggers if t.mandatory}
    assert "model_host_conflict" in codes
    assert result.route == "REVIEW_RECOMMENDED" and result.mandatory is True
    assert result.review_state == "pending" and result.technical_status == "completed"


def test_raw_and_derived_label_layers_are_never_compared_to_each_other():
    task, payload = case()
    first = position(task, payload, label="solid")
    second = position(
        task, payload, label="overclaim", run_id="review", origin="model_review"
    )
    result = assess_case(task, [first, second])
    labels = [c for c in result.conflicts if c.dimension == "label"]
    assert len(labels) == 1
    assert labels[0].field == "phase8.original_model_label"


def test_later_agreement_cannot_erase_earlier_conflict_or_pick_a_majority():
    task, payload = case()
    first = position(task, payload)
    bad = deepcopy(payload)
    state(bad, "contradicted")
    contrary = position(task, bad, run_id="review", origin="model_review")
    agreed = position(task, payload, run_id="stability", origin="stability")
    result = assess_case(task, [first, contrary, agreed])
    assert result.route == "HUMAN_REVIEW_REQUIRED"
    assert len(result.positions) == 3
    assert any(
        first.position_id in c.provenance and contrary.position_id in c.provenance
        for c in result.conflicts
    )


@pytest.mark.parametrize(
    "corrupt",
    [
        lambda p: p["evidence"][0].update(exact_reference="invented quote"),
        lambda p: p["phase8"].update(propositions=[]),
        lambda p: p["client_findings"][0].update(
            client_explanation="A new untracked assertion"
        ),
    ],
)
def test_critical_source_completeness_or_transformation_failure_cannot_be_auto_resolved(
    corrupt,
):
    task, payload = case()
    corrupt(payload)
    result = assess_case(task, [position(task, payload)])
    assert result.technical_status == "incomplete"
    assert result.route == "HUMAN_REVIEW_REQUIRED"
    assert result.mandatory and result.execution_status == "not_executed"
    assert all(t.field and t.position_ids and t.reason for t in result.triggers)


def test_replay_revalidates_raw_and_rejects_forged_cached_scientific_assessment():
    task, payload = case()
    first = position(task, payload)
    first.phase8["composite_state"] = "contradicted"
    result = assess_case(task, [first])
    assert result.technical_status == "incomplete"
    assert any(t.code == "critical_source_binding" for t in result.triggers)


def test_case_and_position_identity_are_deterministic_but_case_cap_ignores_run_id():
    task, payload = case()
    first, second = position(task, payload), position(task, payload, run_id="new-run")
    assert first.case_id == second.case_id == case_key(task)
    assert first.position_id != second.position_id
    assert first == position(task, payload)
    assert assess_case(task, [first, first]).positions == [first]
    changed = task.model_copy(update={"context": task.context + "Additional source"})
    assert case_key(changed) != case_key(task)
    assert assess_case(changed, [first]).route == "HUMAN_REVIEW_REQUIRED"


def test_empty_or_missing_analysis_is_visible_not_successful_review():
    task, _ = case()
    empty = assess_case(task, [])
    assert empty.technical_status == "not_executed"
    assert empty.route == "UNRESOLVED"
    result = AgentResult(
        provider="legacy", raw_output='{"final_answer":"solid"}', parse_ok=True
    )
    legacy = assess_case(task, [position_from_result(task, result, "old")])
    assert legacy.technical_status == "incomplete"
    assert legacy.review_state == "pending"
    assert legacy.execution_status == "not_executed"


def test_missing_proposition_identity_is_never_aligned_by_list_order():
    task, payload = case()
    renamed = json.loads(json.dumps(payload).replace("claim:p1", "claim:different"))
    result = assess_case(
        task,
        [
            position(task, payload),
            position(task, renamed, run_id="review", origin="model_review"),
        ],
    )
    assert any(
        c.field == "proposition_identity" and c.material for c in result.conflicts
    )
    assert result.route == "HUMAN_REVIEW_REQUIRED"


def test_search_scope_difference_is_bound_and_evidence_order_is_not_a_conflict():
    task, payload = case()
    reordered = deepcopy(payload)
    reordered["search_scopes"][0]["reviewed_source_ids"].reverse()
    assert not assess_case(
        task, [position(task, payload), position(task, reordered, run_id="reordered")]
    ).conflicts
    narrower = deepcopy(payload)
    narrower["search_scopes"][0]["reviewed_source_ids"] = ["context"]
    result = assess_case(
        task,
        [
            position(task, payload),
            position(task, narrower, run_id="review", origin="model_review"),
        ],
    )
    assert any(
        c.dimension == "search_scope" and c.proposition_ids == ["claim:p1"]
        for c in result.conflicts
    )


def test_snapshot_excludes_phase9_to_avoid_recursive_history_growth():
    task, payload = case()
    p = position(task, payload)
    result = AgentResult.model_validate(p.agent_result)
    if "phase9" in AgentResult.model_fields:
        result.phase9 = {"positions": [p.model_dump()]}
    fresh = position_from_result(task, result, p.run_id)
    assert "phase9" not in fresh.agent_result
    assert fresh == p


def test_required_unknown_alternative_in_supported_or_remains_visible_without_mandatory_review():
    from inspektorium.audit.schemas import ForensicRecord
    from tests.unit.test_forensics_taxonomy import add_logical_component

    task, payload = case()
    record = ForensicRecord.model_validate(payload)
    add_logical_component(record, operator="or", state="unknown")
    task = task.model_copy(
        update={
            "prompt": record.phase8["original_claim"],
            "context": task.context + "\n" + record.evidence[1].text,
        }
    )
    result = assess_case(task, [position(task, record.model_dump(mode="json"))])
    assert result.technical_status == "completed", result.triggers
    assert result.route == "AUTO_RESOLVABLE"
    assert result.uncertainty and not result.mandatory


def test_same_evidence_id_cannot_hide_changed_source_selection():
    task, payload = case()
    other_quote = (
        "A second randomized trial found the same result in the same population."
    )
    task = task.model_copy(update={"context": task.context + "\n" + other_quote})
    changed = deepcopy(payload)
    changed["evidence"][0].update(text=other_quote, exact_reference=other_quote)
    result = assess_case(
        task,
        [
            position(task, payload),
            position(task, changed, run_id="review", origin="model_review"),
        ],
    )
    assert any(
        c.field.endswith("selected_source_objects") and c.material
        for c in result.conflicts
    )


def test_source_design_interpretation_conflict_is_visible_even_with_same_supported_association():
    task, payload = case()
    coherent_attribute(payload, "relation", "association")
    changed = deepcopy(payload)
    changed["phase8"]["evidence_descriptions"][0].update(
        evidence_type="observational", randomized=None
    )
    first, other = (
        position(task, payload),
        position(task, changed, run_id="review", origin="model_review"),
    )
    assert (
        first.phase8["composite_state"]
        == other.phase8["composite_state"]
        == "supported"
    )
    result = assess_case(task, [first, other])
    assert any(
        c.field.endswith("evidence_interpretation") and c.material
        for c in result.conflicts
    )


def test_failed_transformation_trigger_is_bound_to_its_proposition_and_evidence():
    task, payload = case()
    summary = next(
        t for t in payload["phase8"]["transformations"] if t["stage"] == "summary"
    )
    summary["to_attributes"]["endpoint"] = "stronger endpoint"
    result = assess_case(task, [position(task, payload)])
    trans = next(t for t in result.triggers if t.code == "material_transformation")
    assert trans.proposition_ids == ["claim:p1"]
    assert trans.evidence_ids == ["e1"]
    assert trans.field == "transformations.summary"


@pytest.mark.parametrize("link", ["underlying", "identification", "bridge", "transfer"])
def test_transitive_or_inference_auxiliary_evidence_selection_cannot_hide_behind_same_id(
    link,
):
    task, payload = case()
    quote_a, quote_b = (
        "Independent supporting observation A.",
        "Independent supporting observation B.",
    )
    task = task.model_copy(
        update={"context": task.context + "\n" + quote_a + "\n" + quote_b}
    )
    extra = deepcopy(payload["evidence"][0])
    extra.update(evidence_id="aux", text=quote_a, exact_reference=quote_a)
    payload["evidence"].append(extra)
    profile = deepcopy(payload["phase8"]["evidence_descriptions"][0])
    profile["evidence_id"] = "aux"
    payload["phase8"]["evidence_descriptions"].append(profile)
    initial = payload["phase8"]["evidence_descriptions"][0]
    if link == "underlying":
        initial.update(evidence_type="review", underlying_evidence_ids=["aux"])
    elif link == "identification":
        initial["identification_evidence_ids"] = ["aux"]
    elif link == "bridge":
        payload["phase8"]["bridges"] = [
            {
                "bridge_id": "bridge",
                "kind": "semantic_transfer",
                "conclusion_proposition_id": "claim:p1",
                "state": "supported",
                "evidence_ids": ["aux"],
                "reason": "Bound supporting inference",
            }
        ]
    else:
        payload["phase8"]["product_transfers"] = [
            {
                "transfer_id": "transfer",
                "binding_id": "b1",
                "state": "direct_match",
                "evidence_ids": ["aux"],
                "reason": "Bound entity comparison",
            }
        ]
    changed = deepcopy(payload)
    changed["evidence"][1].update(text=quote_b, exact_reference=quote_b)
    before, after = (
        position(task, payload),
        position(task, changed, run_id="review", origin="model_review"),
    )
    assert (
        before.phase8["technical_status"]
        == after.phase8["technical_status"]
        == "completed"
    )
    assert (
        before.phase8["composite_state"]
        == after.phase8["composite_state"]
        == "supported"
    )
    assert (
        assess_case(
            task, [before, position(task, payload, run_id="identical")]
        ).conflicts
        == []
    )
    result = assess_case(task, [before, after])
    assert result.route == "HUMAN_REVIEW_REQUIRED"
    assert any(
        c.field.endswith("selected_source_objects")
        and "aux" in c.positions[0].evidence_ids
        for c in result.conflicts
    )


def test_inconsistent_duplicate_position_id_never_overwrites_original():
    task, payload = case()
    original = position(task, payload)
    altered = original.model_copy(deep=True)
    altered.phase8["composite_state"] = "contradicted"
    result = assess_case(task, [original, altered])
    assert result.technical_status == "incomplete"
    assert result.route == "HUMAN_REVIEW_REQUIRED"
    assert result.positions == [original, altered]
    assert result.positions[0].phase8["composite_state"] == "supported"


def test_prior_conflict_cannot_override_fresh_materiality_or_resolution():
    task, payload = case()
    opposite = deepcopy(payload)
    state(opposite, "contradicted")
    positions = [
        position(task, payload),
        position(task, opposite, run_id="review", origin="model_review"),
    ]
    original = assess_case(task, positions)
    changed = [
        c.model_copy(update={"material": False, "resolution": "adjudicated"})
        for c in original.conflicts
    ]
    result = assess_case(task, positions, prior_conflicts=changed)
    assert result.technical_status == "incomplete"
    assert result.route == "HUMAN_REVIEW_REQUIRED"
    assert result.conflicts == original.conflicts
    valid_replay = assess_case(task, positions, prior_conflicts=original.conflicts)
    assert valid_replay.conflicts == original.conflicts
    assert valid_replay.technical_status == "completed"


@pytest.mark.parametrize(
    "annotation", [{"core_error": "invented"}, {"proposition_ids": 5}]
)
def test_explicit_invalid_taxonomy_is_a_bound_failed_control_while_absence_is_not(
    annotation,
):
    task, payload = case()
    assert assess_case(task, [position(task, payload)]).route == "AUTO_RESOLVABLE"
    payload["phase8_taxonomy"] = annotation
    result = assess_case(task, [position(task, payload)])
    assert result.technical_status == "incomplete"
    assert result.route == "HUMAN_REVIEW_REQUIRED"
    assert any(
        t.field == "phase8.taxonomy.technical_status" and t.position_ids
        for t in result.triggers
    )


def premise_case(*, linked=True):
    task, payload = case()
    quote_a, quote_b = (
        "Supporting premise observation A.",
        "Supporting premise observation B.",
    )
    task = task.model_copy(
        update={"context": task.context + "\n" + quote_a + "\n" + quote_b}
    )
    ledger = payload["phase8"]
    premise = deepcopy(ledger["propositions"][0])
    premise.update(proposition_id="claim:p2", materiality="optional")
    premise["evidence_bindings"][0].update(
        binding_id="b2", proposition_id="claim:p2", evidence_id="e2"
    )
    ledger["propositions"].append(premise)
    evidence = deepcopy(payload["evidence"][0])
    evidence.update(evidence_id="e2", text=quote_a, exact_reference=quote_a)
    payload["evidence"].append(evidence)
    description = deepcopy(ledger["evidence_descriptions"][0])
    description["evidence_id"] = "e2"
    ledger["evidence_descriptions"].append(description)
    if linked:
        ledger["propositions"][0].update(
            premise_proposition_ids=["claim:p2"], required_bridge_ids=["bridge"]
        )
        ledger["bridges"] = [
            {
                "bridge_id": "bridge",
                "kind": "causal_identification",
                "conclusion_proposition_id": "claim:p1",
                "premise_proposition_ids": ["claim:p2"],
                "state": "supported",
                "evidence_ids": ["e1"],
                "reason": "Represented inference depends on the optional premise",
            }
        ]
    return task, payload, quote_b


@pytest.mark.parametrize("link", ["both", "proposition", "bridge"])
def test_explicit_premise_dependencies_propagate_materiality_and_evidence_closure(link):
    task, payload, quote_b = premise_case()
    if link == "proposition":
        payload["phase8"]["bridges"][0]["premise_proposition_ids"] = []
    elif link == "bridge":
        payload["phase8"]["propositions"][0]["premise_proposition_ids"] = []
    changed = deepcopy(payload)
    changed["evidence"][1].update(text=quote_b, exact_reference=quote_b)
    first, second = position(task, payload), position(task, changed, run_id="review")
    assert (
        first.phase8["technical_status"]
        == second.phase8["technical_status"]
        == "completed"
    )
    assert (
        first.phase8["composite_state"]
        == second.phase8["composite_state"]
        == "supported"
    )
    result = assess_case(task, [first, second])
    assert result.route == "HUMAN_REVIEW_REQUIRED"
    assert any(
        c.material and c.proposition_ids == ["claim:p2"] for c in result.conflicts
    )
    assert any(
        c.material
        and c.proposition_ids == ["claim:p1"]
        and c.field.endswith("selected_source_objects")
        and "e2" in c.positions[0].evidence_ids
        for c in result.conflicts
    )
    assert not assess_case(
        task, [first, position(task, payload, run_id="same")]
    ).conflicts


def test_removing_both_declared_premise_edges_is_a_material_conflict():
    task, payload, _ = premise_case()
    changed = deepcopy(payload)
    changed["phase8"]["propositions"][0]["premise_proposition_ids"] = []
    changed["phase8"]["bridges"][0]["premise_proposition_ids"] = []
    first, second = position(task, payload), position(task, changed, run_id="review")
    assert (
        first.phase8["technical_status"]
        == second.phase8["technical_status"]
        == "completed"
    )
    result = assess_case(task, [first, second])
    assert result.route == "HUMAN_REVIEW_REQUIRED"
    assert any(
        c.material and c.field.endswith("premise_proposition_ids")
        for c in result.conflicts
    )
    assert any(c.material and c.field.endswith("bridges") for c in result.conflicts)


def test_unlinked_optional_population_conflict_replays_identically_in_reverse_order():
    task, payload, _ = premise_case(linked=False)
    changed = deepcopy(payload)
    changed["phase8"]["propositions"][1]["attributes"]["population"] = "older adults"
    changed["phase8"]["evidence_descriptions"][1]["attributes"]["population"] = (
        "older adults"
    )
    first, second = position(task, payload), position(task, changed, run_id="review")
    original = assess_case(task, [first, second])
    assert original.conflicts and not any(c.material for c in original.conflicts)
    assert original.route == "AUTO_RESOLVABLE"
    reverse = assess_case(task, [second, first], prior_conflicts=original.conflicts)
    assert reverse.conflicts == original.conflicts
    assert reverse.triggers == original.triggers
    assert reverse.technical_status == "completed"
    assert reverse.route == "AUTO_RESOLVABLE"
