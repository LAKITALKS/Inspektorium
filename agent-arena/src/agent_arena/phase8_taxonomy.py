"""Bounded taxonomy precedence checks, separate from semantic support states.

Core-error and trigger extraction remains model-dependent. This module rejects
inconsistent represented triggers; it does not infer scientific meaning from prose.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from agent_arena.phase8_models import PropositionLedger


class TaxonomyAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    core_error: Literal["overstatement", "causal_inference", "mechanism_to_outcome", "none", "unknown"]
    causal_claim: bool | None
    noncausal_result_used: bool | None
    described_biological_mechanism: bool | None
    implies_human_benefit: bool | None
    proposition_ids: list[str] = Field(min_length=1)
    evidence_ids: list[str] = Field(min_length=1)
    trigger_proposition_id: str = Field(min_length=1)
    trigger_evidence_id: str = Field(min_length=1)
    trigger_quote: str = Field(min_length=1)
    reason: str = Field(min_length=1)


ASSURANCE = (
    "Taxonomy decisions check represented trigger, core-error and evidence/proposition "
    "consistency. Quote containment does not prove entailment or correct model interpretation."
)
CAUSAL_RELATIONS = {"causal", "causal_effect", "human_clinical_benefit", "therapeutic", "preventive"}
CLINICAL_ENDPOINTS = {"clinical", "clinical_event", "mortality", "functional", "symptom"}
MECHANISM_TYPES = {"mechanistic", "animal", "in_vitro"}


def assess_taxonomy(record, semantic_assessment) -> dict:
    """Return a separate derived label; never mutate the record or the model label."""
    def result(status, label, reason):
        return {"technical_status": status, "derived_label": label,
                "reasons": [reason], "assurance_scope": ASSURANCE}

    raw = getattr(record, "phase8_taxonomy", None)
    if raw is None:
        return result("not_executed", None, "Taxonomy trigger analysis absent")
    semantic = (semantic_assessment.model_dump() if hasattr(semantic_assessment, "model_dump")
                else semantic_assessment)
    if not isinstance(semantic, dict) or semantic.get("technical_status") != "completed":
        return result("incomplete", None, "Semantic analysis did not complete; no taxonomy correction")
    try:
        annotation = TaxonomyAssessment.model_validate(raw)
        ledger = PropositionLedger.model_validate(record.phase8)
    except (ValidationError, ValueError, TypeError) as exc:
        return result("incomplete", None, f"Invalid taxonomy/ledger payload: {exc}")
    props = {p.proposition_id: p for p in ledger.propositions}
    evidence = {e.evidence_id: e for e in record.evidence}
    profiles = {d.evidence_id: d for d in ledger.evidence_descriptions}
    prop_ids, ev_ids = set(annotation.proposition_ids), set(annotation.evidence_ids)
    if len(prop_ids) != len(annotation.proposition_ids) or len(ev_ids) != len(annotation.evidence_ids):
        return result("incomplete", None, "Duplicate taxonomy reference")
    if not prop_ids <= set(props) or not ev_ids <= set(evidence) or not ev_ids <= set(profiles):
        return result("incomplete", None, "Unresolved taxonomy proposition/evidence reference")
    bindings = {p.proposition_id: {b.evidence_id for b in p.evidence_bindings}
                for p in props.values()}
    if not ev_ids <= set().union(*(bindings[pid] for pid in prop_ids)) or any(
        not bindings[pid] & ev_ids for pid in prop_ids
    ):
        return result("incomplete", None, "Taxonomy evidence is not bound to the referenced proposition")
    trigger_pid, trigger_eid = annotation.trigger_proposition_id, annotation.trigger_evidence_id
    if trigger_pid not in prop_ids or trigger_eid not in ev_ids or trigger_eid not in bindings[trigger_pid]:
        return result("incomplete", None, "Trigger evidence/proposition pair does not resolve")
    quote_sources = [props[trigger_pid].original_span.text, evidence[trigger_eid].text]
    if not annotation.trigger_quote.strip() or not any(annotation.trigger_quote in s for s in quote_sources):
        return result("incomplete", None, "Taxonomy trigger quote is not source-bound")
    states = {p["proposition_id"]: p["derived_state"] for p in semantic.get("propositions", [])}
    if not prop_ids <= set(states):
        return result("incomplete", None, "Taxonomy proposition lacks a derived semantic decision")
    flags = (annotation.causal_claim, annotation.noncausal_result_used,
             annotation.described_biological_mechanism, annotation.implies_human_benefit)
    if annotation.core_error == "unknown" or any(flag is None for flag in flags):
        return result("completed", None, "Unresolved taxonomy trigger/core error; no deterministic relabeling")
    selected = [props[pid] for pid in prop_ids]
    causal = [p for p in selected if p.attributes.relation in CAUSAL_RELATIONS]
    if annotation.causal_claim != bool(causal):
        return result("completed", None, "Causal trigger conflicts with represented proposition relation")
    if annotation.core_error == "none":
        if semantic.get("composite_state") == "supported" and all(states[pid] == "supported" for pid in prop_ids):
            return result("completed", "solid", "Honest reporting with supported represented propositions")
        return result("completed", None, "No-core-error annotation does not resolve unsupported/unknown semantics")
    if semantic.get("composite_state") == "supported":
        return result("completed", None, "Supported claim logic cannot be relabeled from a failed alternative")
    if annotation.core_error == "overstatement":
        if semantic.get("composite_state") in {"unsupported", "contradicted"} and any(
            states[pid] in {"unsupported", "contradicted"} for pid in prop_ids
        ):
            return result("completed", "overclaim", "Generic overstatement is the represented core error")
        return result("completed", None, "Overstatement annotation lacks a represented support gap")
    if annotation.core_error == "causal_inference":
        if not annotation.causal_claim or not annotation.noncausal_result_used:
            return result("completed", None, "CvC requires a causal claim using an actual noncausal result")
        for prop in causal:
            if prop.proposition_id != trigger_pid:
                continue
            for eid in {trigger_eid}:
                d = profiles[eid]
                noncausal = d.evidence_type == "observational" or (
                    d.evidence_type == "controlled_intervention" and (
                        d.randomized is False or bool(d.design_limitations)
                        or d.attributes.comparison == "within"
                    ) and not (d.identification_argument and d.identification_evidence_ids)
                )
                result_claim = d.attributes.relation in {"association", "description", "descriptive"}
                if noncausal and result_claim and states[prop.proposition_id] != "supported":
                    return result("completed", "correlation_vs_causation",
                                  "Source-bound noncausal result is used causally and is the core error")
        return result("completed", None, "CvC trigger is not established by the linked evidence/result")
    if not annotation.described_biological_mechanism or not annotation.implies_human_benefit:
        return result("completed", None, "ME requires a described biological mechanism implying human benefit")
    for prop in causal:
        if prop.proposition_id != trigger_pid:
            continue
        human_outcome = prop.attributes.species == "human" and prop.attributes.endpoint_type in CLINICAL_ENDPOINTS
        relevant = {trigger_eid}
        mechanism = any(profiles[eid].evidence_type in MECHANISM_TYPES
                        and profiles[eid].attributes.relation == "mechanism" for eid in relevant)
        if human_outcome and mechanism and states[prop.proposition_id] != "supported":
            return result("completed", "mechanism_vs_evidence",
                          "Described biological mechanism is used for unresolved human clinical benefit")
    return result("completed", None, "ME trigger absent; a surrogate endpoint alone is insufficient")
