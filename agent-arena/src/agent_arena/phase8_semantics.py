"""Offline Phase-8 consistency checks. No label ranking and no model calls."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from pydantic import ValidationError

from agent_arena.phase8_models import (
    HOST_RULE_VERSION,
    ClaimLogic,
    ModelHostConflict,
    Phase8Assessment,
    PropositionAssessment,
    PropositionLedger,
    SemanticAttributes,
    ScientificState,
)

if TYPE_CHECKING:
    from agent_arena.schemas import ForensicRecord


def aggregate_claim(logic: ClaimLogic, states: dict[str, ScientificState]) -> ScientificState:
    """Apply AA-P8/1.0 only to a validated, nonempty tree; reject vacuous calls."""
    if logic.operator == "leaf":
        if logic.children or not logic.proposition_id or logic.proposition_id not in states:
            raise ValueError("invalid or unresolved proposition leaf")
        return states[logic.proposition_id]
    if logic.proposition_id is not None or not logic.children:
        raise ValueError("empty or malformed composite")
    children = [aggregate_claim(child, states) for child in logic.children]
    if logic.operator == "and":
        for state in ("contradicted", "unknown", "unsupported"):
            if state in children:
                return state
        return "supported"
    for state in ("supported", "unknown", "unsupported"):
        if state in children:
            return state
    return "contradicted"


def validate_ledger(record: ForensicRecord, ledger: PropositionLedger) -> list[str]:
    """Validate references/coverage against the original record, never inferred aliases."""
    errors: list[str] = []

    def unique(values: list[str], kind: str) -> None:
        if len(values) != len(set(values)):
            errors.append(f"duplicate {kind} IDs")

    prov_ids = [item.provenance_id for item in record.provenance]
    evidence_ids = [item.evidence_id for item in record.evidence]
    scope_ids = [item.search_scope_id for item in record.search_scopes]
    ids = [item.proposition_id for item in ledger.propositions]
    required = [item.proposition_id for item in ledger.propositions
                if item.materiality == "required"]
    for values, kind in ((prov_ids, "provenance"), (evidence_ids, "evidence"),
                         (scope_ids, "scope"), (ids, "proposition"),
                         (ledger.required_proposition_ids, "declared required")):
        unique(values, kind)
    provenance = next((p for p in record.provenance
                       if p.provenance_id == ledger.provenance_id), None)
    if provenance is None or provenance.exact_claim_text != ledger.original_claim:
        errors.append("original claim does not resolve verbatim to captured provenance")
    if not required or set(required) != set(ledger.required_proposition_ids):
        errors.append("empty or missing declared required proposition set")
    binding_ids: list[str] = []
    for prop in ledger.propositions:
        pid = prop.proposition_id
        if not pid.startswith(ledger.claim_id + ":") or pid == ledger.claim_id + ":":
            errors.append(f"{pid}: proposition ID is not claim-bound")
        if prop.parent_claim_id != ledger.claim_id or prop.provenance_id != ledger.provenance_id:
            errors.append(f"{pid}: parent claim/provenance mismatch")
        span = prop.original_span
        if span.end <= span.start or ledger.original_claim[span.start:span.end] != span.text:
            errors.append(f"{pid}: original span mismatch")
        if span.end > len(ledger.original_claim):
            errors.append(f"{pid}: original span outside captured claim")
        for scope_id in prop.search_scope_ids:
            if scope_id not in scope_ids:
                errors.append(f"{pid}: unresolved search scope {scope_id}")
        for binding in prop.evidence_bindings:
            binding_ids.append(binding.binding_id)
            if binding.proposition_id != pid or binding.evidence_id not in evidence_ids:
                errors.append(f"{pid}: unresolved/wrong-proposition evidence binding")
            if binding.search_scope_id is not None and binding.search_scope_id not in scope_ids:
                errors.append(f"{pid}: unresolved binding search scope")
        if prop.reported_verdict in {"supported", "contradicted"} and not prop.evidence_bindings:
            errors.append(f"{pid}: decisive verdict lacks evidence binding")
    unique(binding_ids, "binding")
    leaves: list[str] = []

    def walk(node: ClaimLogic) -> None:
        if node.operator == "leaf":
            if node.children or node.proposition_id not in required:
                errors.append("invalid, unresolved or optional proof leaf")
            elif node.proposition_id is not None:
                leaves.append(node.proposition_id)
        else:
            if node.proposition_id is not None or not node.children:
                errors.append("empty or malformed logical composite")
            for child in node.children:
                walk(child)

    walk(ledger.logic)
    if set(leaves) != set(required):
        errors.append("logical tree omits required proposition(s)")
    errors.extend(_validate_semantic_trace(record, ledger))
    return errors


CORE_DIMENSIONS = frozenset({
    "species", "population", "intervention", "comparator", "endpoint", "endpoint_type",
    "relation", "follow_up", "certainty",
})
PRODUCT_DIMENSIONS = frozenset({"intervention", "dose", "formulation", "route"})
RELATIONS = {
    "description": "description", "descriptive": "description",
    "association": "association", "mechanism": "mechanism",
    "causal": "causal", "causal_effect": "causal",
    "human_clinical_benefit": "clinical", "therapeutic": "clinical", "preventive": "clinical",
}


def _validate_semantic_trace(record, ledger):
    errors = []
    props = {p.proposition_id: p for p in ledger.propositions}
    evidence = {e.evidence_id: e for e in record.evidence}
    descriptions = {d.evidence_id: d for d in ledger.evidence_descriptions}
    bindings = {b.binding_id: b for p in ledger.propositions for b in p.evidence_bindings}
    bridges = {b.bridge_id: b for b in ledger.bridges}
    findings = {f.finding_id: f for f in record.findings}
    scopes = {s.search_scope_id: s for s in record.search_scopes}
    for scope in record.search_scopes:
        if scope.scope_type not in {"reviewed_set", "documented_search"}:
            errors.append(f"{scope.search_scope_id}: invalid search scope type")
        if not scope.reviewed_source_ids or any(not s.strip() for s in scope.reviewed_source_ids):
            errors.append(f"{scope.search_scope_id}: reviewed source basis absent")
        if scope.scope_type == "documented_search" and not (
            scope.resources and scope.query_terms and scope.date_cutoff
            and scope.search_completeness in {"targeted", "structured"}
        ):
            errors.append(f"{scope.search_scope_id}: documented search basis incomplete")
    for items, field, name in (
        (ledger.evidence_descriptions, "evidence_id", "evidence description"),
        (ledger.bridges, "bridge_id", "bridge"),
        (ledger.product_transfers, "transfer_id", "transfer"),
        (ledger.transformations, "transformation_id", "transformation"),
        (record.findings, "finding_id", "finding"),
        (record.client_findings, "client_finding_id", "client finding"),
    ):
        values = [getattr(item, field) for item in items]
        if len(values) != len(set(values)):
            errors.append(f"duplicate {name} IDs")
    referenced = {b.evidence_id for b in bindings.values()}
    for bridge in ledger.bridges:
        if bridge.conclusion_proposition_id not in props or any(
            pid not in props for pid in bridge.premise_proposition_ids
        ):
            errors.append(f"{bridge.bridge_id}: orphan bridge proposition")
        if bridge.kind == "mechanism_to_outcome" and not bridge.premise_proposition_ids:
            errors.append(f"{bridge.bridge_id}: mechanism bridge lacks premise")
        if any(eid not in evidence for eid in bridge.evidence_ids):
            errors.append(f"{bridge.bridge_id}: unresolved bridge evidence")
        referenced.update(bridge.evidence_ids)
    for transfer in ledger.product_transfers:
        if transfer.binding_id not in bindings or any(
            eid not in evidence for eid in transfer.evidence_ids
        ):
            errors.append(f"{transfer.transfer_id}: unresolved product transfer")
        if not set(transfer.dimensions) <= PRODUCT_DIMENSIONS:
            errors.append(f"{transfer.transfer_id}: invalid product dimensions")
        referenced.update(transfer.evidence_ids)
    for description in ledger.evidence_descriptions:
        if description.evidence_id not in evidence:
            errors.append("orphan evidence description")
        aux = description.identification_evidence_ids + description.underlying_evidence_ids
        if any(eid not in evidence or eid not in descriptions for eid in aux):
            errors.append(f"{description.evidence_id}: unresolved underlying/identification evidence")
        referenced.update(aux)
        if description.identification_argument:
            source_texts = [evidence[eid].text for eid in description.identification_evidence_ids
                            if eid in evidence]
            if not any(description.identification_argument in text for text in source_texts):
                errors.append(f"{description.evidence_id}: identification argument is not source-bound")
    if referenced - set(descriptions):
        errors.append("bound evidence lacks capability/semantic description")
    if any(e.material and e.evidence_id not in referenced for e in record.evidence):
        errors.append("orphan material evidence")
    for prop in ledger.propositions:
        pid = prop.proposition_id
        if any(d not in SemanticAttributes.model_fields for d in prop.material_dimensions):
            errors.append(f"{pid}: invalid material dimension")
        if any(d not in SemanticAttributes.model_fields or not reason.strip()
               for d, reason in prop.not_applicable.items()):
            errors.append(f"{pid}: invalid not-applicable explanation")
        for bid in prop.required_bridge_ids:
            if bid not in bridges or bridges[bid].conclusion_proposition_id != pid:
                errors.append(f"{pid}: unresolved/wrong-conclusion required bridge")
        if any(p not in props for p in prop.premise_proposition_ids):
            errors.append(f"{pid}: unresolved inference premise")
        for premise in prop.premise_proposition_ids:
            clinical_conclusion = RELATIONS.get(_norm(prop.attributes.relation)) == "clinical" or (
                RELATIONS.get(_norm(prop.attributes.relation)) == "causal"
                and _norm(prop.attributes.species) == "human"
                and _norm(prop.attributes.endpoint_type) in
                {"clinical", "clinical_event", "mortality", "functional", "symptom"}
            )
            if premise in props and RELATIONS.get(_norm(props[premise].attributes.relation)) == "mechanism" \
                    and clinical_conclusion:
                if not any(b.kind == "mechanism_to_outcome" and premise in b.premise_proposition_ids
                           for b in ledger.bridges if b.bridge_id in prop.required_bridge_ids):
                    errors.append(f"{pid}: material mechanism-to-outcome bridge missing")
        # C15 applies to every proposition (Package B, P8-F2): an observation must match the bound
        # evidence role, also for an optional proposition that carries a client output.
        for binding in prop.evidence_bindings:
            source = evidence.get(binding.evidence_id)
            if source is not None and binding.observation == "support" and source.role.value != "supporting":
                errors.append(f"{pid}: binding support contradicts evidence role")
            if source is not None and binding.observation == "contradiction" and source.role.value != "contradictory":
                errors.append(f"{pid}: binding contradiction contradicts evidence role")
        if prop.materiality != "required":
            continue
        finding = findings.get(pid)
        expected = {b.evidence_id for b in prop.evidence_bindings}
        if finding is None or finding.proposition != prop.proposition_text or (
            finding.provenance_id != prop.provenance_id
        ) or set(finding.supporting_evidence_ids + finding.contrary_evidence_ids) != expected:
            errors.append(f"{pid}: internal finding/evidence trace mismatch")
        if finding is not None:
            for binding in prop.evidence_bindings:
                if binding.observation == "contradiction" and binding.evidence_id not in finding.contrary_evidence_ids:
                    errors.append(f"{pid}: contradictory evidence missing from finding")
        if not prop.search_scope_ids:
            errors.append(f"{pid}: required search scope trace absent")
        reviewed_sources = set().union(*(set(scopes[s].reviewed_source_ids)
                                        for s in prop.search_scope_ids if s in scopes))
        def lineage(ids):
            seen, pending = set(), list(ids)
            while pending:
                eid = pending.pop()
                if eid in seen:
                    continue
                seen.add(eid)
                d = descriptions.get(eid)
                if d:
                    pending.extend(d.underlying_evidence_ids + d.identification_evidence_ids)
            return seen

        for binding in prop.evidence_bindings:
            bound_evidence = evidence.get(binding.evidence_id)
            bound_ids = lineage([binding.evidence_id])
            if any(evidence[eid].source_id not in reviewed_sources for eid in bound_ids if eid in evidence):
                errors.append(f"{pid}: evidence source outside proposition search scope")
            if binding.search_scope_id is not None:
                scope = scopes.get(binding.search_scope_id)
                if bound_evidence is not None and scope is not None and any(
                    evidence[eid].source_id not in scope.reviewed_source_ids
                    for eid in bound_ids if eid in evidence
                ):
                    errors.append(f"{pid}: evidence source outside binding search scope")
            if binding.observation == "no_evidence_found" and not any(
                n.finding_id == pid and n.proposition == prop.proposition_text
                and n.search_scope_id == binding.search_scope_id
                for n in record.negative_assertions
            ):
                errors.append(f"{pid}: no-evidence observation lacks Phase-7 negative-assertion trace")
        auxiliary = {eid for b in ledger.bridges if b.conclusion_proposition_id == pid
                     for eid in b.evidence_ids}
        prop_bindings = {b.binding_id for b in prop.evidence_bindings}
        auxiliary.update(eid for t in ledger.product_transfers if t.binding_id in prop_bindings
                         for eid in t.evidence_ids)
        if any(evidence[eid].source_id not in reviewed_sources
               for eid in lineage(auxiliary) if eid in evidence):
            errors.append(f"{pid}: bridge/transfer evidence source outside search scope")
    if any(f.finding_id not in props for f in record.findings):
        errors.append("orphan internal finding")
    if not record.client_findings:
        errors.append("required client output trace absent")
    expected_targets = {(stage, p.proposition_id) for p in ledger.propositions
                        if p.materiality == "required"
                        for stage in ("extraction", "search_question", "internal")}
    expected_targets.update(("summary", c.client_finding_id) for c in record.client_findings)
    actual_targets = [(t.stage, t.target_id) for t in ledger.transformations]
    if len(actual_targets) != len(set(actual_targets)) or set(actual_targets) != expected_targets:
        errors.append("missing, duplicate or orphan mandatory transformation audit")
    clients = {c.client_finding_id: c for c in record.client_findings}
    for trans in ledger.transformations:
        p = props.get(trans.target_id)
        if trans.stage == "summary":
            client = clients.get(trans.target_id)
            p = props.get(client.parent_finding_id) if client else None
            client_text = (client.display_claim + ("\n" + client.client_explanation
                           if client.client_explanation else "")) if client else None
            if client is None or trans.to_text != client_text:
                errors.append(f"{trans.transformation_id}: summary text/target mismatch")
        if p is None or trans.from_proposition_ids != [p.proposition_id]:
            errors.append(f"{trans.transformation_id}: unresolved transformation origin")
            continue
        if trans.stage == "extraction":
            if trans.from_text != p.original_span.text or trans.to_text != p.proposition_text:
                errors.append(f"{trans.transformation_id}: extraction text provenance mismatch")
            if trans.to_attributes != p.attributes:
                errors.append(f"{trans.transformation_id}: extraction target attributes mismatch")
        else:
            if trans.from_text != p.proposition_text or trans.from_attributes != p.attributes:
                errors.append(f"{trans.transformation_id}: transformed source mismatch")
            if trans.stage == "search_question" and trans.to_text != p.search_question:
                errors.append(f"{trans.transformation_id}: search question target mismatch")
            if trans.stage == "internal":
                finding = findings.get(p.proposition_id)
                internal_text = (finding.proposition + ("\n" + finding.verdict_summary
                                 if finding.verdict_summary else "")) if finding else None
                if trans.to_text != internal_text:
                    errors.append(f"{trans.transformation_id}: internal target mismatch")
    return errors


def _norm(value):
    return value.strip().casefold() if isinstance(value, str) else value


def _unknown_value(value):
    return value is None or _norm(value) in {
        "", "unknown", "unspecified", "unresolved", "unclear", "not_reported", "not reported",
        "n/a", "not_applicable",
    }


def _dimensions(prop):
    # An empty producer-supplied list is never an opt-out from preservation.
    populated = {k for k, v in prop.attributes.model_dump().items() if v is not None}
    return CORE_DIMENSIONS | set(prop.material_dimensions) | populated


def _missing_attributes(prop):
    missing = []
    for dimension in _dimensions(prop):
        value = getattr(prop.attributes, dimension)
        if _unknown_value(value):
            if dimension == "relation" or not prop.not_applicable.get(dimension, "").strip():
                missing.append(dimension)
    return sorted(missing)


def _raw_match(prop, description):
    mismatched, unresolved = [], []
    for dimension in sorted(_dimensions(prop)):
        target = getattr(prop.attributes, dimension)
        source = getattr(description.attributes, dimension)
        if target is None and prop.not_applicable.get(dimension):
            continue
        # Relation is checked by capability. Certainty is a transformation property.
        if dimension in {"relation", "certainty"}:
            continue
        if _unknown_value(target) or _unknown_value(source):
            unresolved.append(dimension)
        elif _norm(target) != _norm(source):
            mismatched.append(dimension)
    return mismatched, unresolved


def _capability(prop, description, descriptions, evidence, seen=None):
    """Categorical ceilings; no evidence-quality score or numeric type ranking."""
    seen = set() if seen is None else seen
    if description.evidence_id in seen:
        return "unknown", "cyclic underlying evidence"
    seen = seen | {description.evidence_id}
    relation = RELATIONS.get(_norm(prop.attributes.relation))
    kind = description.evidence_type
    if relation is None or kind == "unknown":
        return "unknown", "unresolved relation or evidence capability"
    if kind == "review":
        if not description.underlying_evidence_ids:
            return "unknown", "review underlying capability absent"
        results = []
        for eid in description.underlying_evidence_ids:
            child = descriptions[eid]
            mismatch, missing = _raw_match(prop, child)
            # Opposite effect direction is precisely what relevant contrary
            # evidence can report; population/endpoint/comparator still match.
            if evidence[eid].role.value == "contradictory" and "effect_direction" in mismatch:
                mismatch.remove("effect_direction")
            result = _capability(prop, child, descriptions, evidence, seen)
            if mismatch:
                result = ("unsupported", "underlying review scope mismatch")
            elif missing:
                result = ("unknown", "underlying review scope unresolved")
            if result[0] == "supported":
                role = evidence[eid].role.value
                if role == "contradictory":
                    result = ("contradicted", "capable underlying evidence contradicts claim")
                elif role != "supporting":
                    result = ("unknown", "underlying evidence is weakening or missing")
            results.append(result)
        if any(state == "supported" for state, _ in results) and any(
            state == "contradicted" for state, _ in results
        ):
            return "unknown", "conflicting capable underlying review evidence"
        if any(state == "supported" for state, _ in results):
            return "supported", "capable underlying review evidence"
        if any(state == "contradicted" for state, _ in results):
            return "contradicted", "capable underlying review evidence contradicts claim"
        if any(state == "unknown" for state, _ in results):
            return "unknown", "unresolved underlying review capability"
        return "unsupported", "underlying review evidence is incapable"
    if relation == "description":
        return "supported", "descriptive inference permitted"
    if kind == "observational":
        return (("supported", "association permitted") if relation == "association" else
                ("unsupported", "observational evidence alone cannot establish this inference"))
    if kind in {"mechanistic", "in_vitro", "animal"}:
        return (("supported", "mechanism in studied setting permitted") if relation == "mechanism"
                else ("unsupported", "mechanistic/preclinical evidence cannot establish outcome"))
    if kind != "controlled_intervention":
        return "unsupported", "descriptive evidence cannot establish stronger inference"
    if relation == "association":
        return "supported", "observed association permitted"
    if description.design_limitations:
        return "unknown", "unresolved design/identification limitation"
    identified = description.randomized is True or bool(
        description.identification_argument and description.identification_evidence_ids
    )
    if not identified:
        return ("unknown" if description.randomized is None else "unsupported",
                "causal identification not established")
    comparison = _norm(description.attributes.comparison)
    if comparison == "within":
        return "unsupported", "within-arm change cannot establish a between-arm causal effect"
    if comparison != "between":
        # AA-P8-HOST/1.1: a missing or unrecognized comparison is missing information, never
        # evidence that the study lacked a comparison group.
        return "unknown", ("comparison design not represented; no inference about the study design"
                           if _unknown_value(comparison) else
                           f"unrecognized comparison value {comparison[:40]!r}; no inference about the study design")
    if relation == "clinical" and (
        _norm(description.attributes.species) != "human" or
        _norm(description.attributes.endpoint_type) not in
        {"clinical", "clinical_event", "mortality", "functional", "symptom"}
    ):
        return "unsupported", "human clinical benefit requires human outcome evidence"
    return "supported", "identified effect in studied setting permitted"


def _evidence_resolves(prop, ids, descriptions, evidence):
    """Bridges/transfers need actual capable, matching evidence, not a status flag."""
    for eid in ids:
        if evidence[eid].role.value != "supporting":
            continue
        d = descriptions[eid]
        mismatch, unresolved = _raw_match(prop, d)
        state, _ = _capability(prop, d, descriptions, evidence)
        if not mismatch and not unresolved and state == "supported":
            return True
    return False


def _binding_state(prop, binding, ledger, descriptions, scopes, evidence, negatives):
    d = descriptions[binding.evidence_id]
    reasons = [f"{binding.binding_id}: {binding.reason}"]
    if binding.observation == "no_evidence_found":
        if any(n.finding_id == prop.proposition_id and n.assertion_scope == "global_nonexistence"
               for n in negatives):
            return "unknown", reasons + ["bounded absence cannot establish global nonexistence"]
        scope = scopes.get(binding.search_scope_id)
        substantiated = bool(scope and scope.reviewed_source_ids and (
            scope.scope_type == "reviewed_set" or (
                scope.scope_type == "documented_search" and scope.resources and scope.query_terms
                and scope.date_cutoff and scope.search_completeness in {"targeted", "structured"}
            )))
        if not substantiated:
            return "unknown", reasons + ["no-evidence-found search basis insufficient"]
        if prop.observation_target == "no_evidence_found" and RELATIONS.get(
            _norm(prop.attributes.relation)
        ) == "description":
            return "supported", reasons + ["bounded executed search found no evidence"]
        return "unknown", reasons + ["no evidence found does not prove absence or contradiction"]
    if binding.observation in {"search_incomplete", "inconclusive", "unknown"}:
        return "unknown", reasons + [f"preserved observation: {binding.observation}"]
    mismatch, unresolved = _raw_match(prop, d)
    if binding.observation == "contradiction" and "effect_direction" in mismatch:
        mismatch.remove("effect_direction")
    product_mismatch = set(mismatch) & PRODUCT_DIMENSIONS
    if product_mismatch:
        transfers = [t for t in ledger.product_transfers if t.binding_id == binding.binding_id]
        usable = [t for t in transfers if product_mismatch <= set(t.dimensions)]
        if any(t.state == "supported_transfer" and _evidence_resolves(
            prop, t.evidence_ids, descriptions, evidence
        ) for t in usable):
            if binding.observation == "support":
                return "supported", reasons + ["capable target evidence resolves product transfer"]
            mismatch = [m for m in mismatch if m not in PRODUCT_DIMENSIONS]
            reasons.append("source-bound product transfer resolved")
        elif any(t.state == "unknown_transfer" for t in usable):
            return "unknown", reasons + ["product transfer unresolved"]
        else:
            return "unsupported", reasons + ["unsupported product/dose/formulation/route transfer"]
    if mismatch:
        bridges = [b for b in ledger.bridges if b.conclusion_proposition_id == prop.proposition_id
                   and b.kind == "semantic_transfer" and set(mismatch) <= set(b.dimensions)]
        if any(b.state == "supported" and _evidence_resolves(prop, b.evidence_ids, descriptions, evidence)
               for b in bridges):
            if binding.observation == "support":
                return "supported", reasons + ["capable target evidence resolves semantic transfer"]
            reasons.append("source-bound semantic transfer resolved")
        elif any(b.state in {"unknown", "partial"} for b in bridges):
            return "unknown", reasons + ["semantic transfer unresolved"]
        else:
            return "unsupported", reasons + ["semantic mismatch: " + ", ".join(mismatch)]
    if unresolved:
        return "unknown", reasons + ["unresolved evidence attributes: " + ", ".join(unresolved)]
    capability, reason = _capability(prop, d, descriptions, evidence)
    reasons.append(reason)
    if capability not in {"supported", "contradicted"}:
        return capability, reasons
    if binding.directness != "direct":
        contrary = capability == "contradicted" or binding.observation == "contradiction"
        return ("unknown" if contrary or binding.directness in {"unknown", "partial"} else "unsupported",
                reasons + [f"binding directness {binding.directness} cannot establish exact claim"])
    if capability == "contradicted":
        return "contradicted", reasons
    if binding.observation == "no_effect_observed":
        if prop.observation_target == "no_effect_observed" and RELATIONS.get(
            _norm(prop.attributes.relation)
        ) == "description":
            return "supported", reasons + ["honest no-effect-observed description"]
        return "unknown", reasons + ["no significant effect does not establish a zero effect"]
    if binding.observation == "contradiction":
        return "contradicted", reasons + ["relevant capable contradictory evidence"]
    return "supported", reasons


def _assess_proposition(prop, ledger, record):
    descriptions = {d.evidence_id: d for d in ledger.evidence_descriptions}
    scopes = {s.search_scope_id: s for s in record.search_scopes}
    evidence = {e.evidence_id: e for e in record.evidence}
    reasons = [prop.reason, *prop.uncertainty]
    missing = _missing_attributes(prop)
    # Host reasons are host-written sentences only. The model's binding reason (first entry of each
    # binding trail) never becomes one, and model-chosen IDs are replaced by ordinal positions.
    states, host_reasons = [], []
    for number, binding in enumerate(prop.evidence_bindings, start=1):
        state, binding_reasons = _binding_state(
            prop, binding, ledger, descriptions, scopes, evidence, record.negative_assertions,
        )
        states.append(state)
        reasons.extend(binding_reasons)
        host_reasons.extend(f"binding {number}: {item}" for item in binding_reasons[1:])
    host_tail = []  # host-written sentences after the bindings, with ordinal bridge labels

    def note(text, host_text=None):
        reasons.append(text)
        host_tail.append(text if host_text is None else host_text)
    if missing:
        state = "unknown"
        note("unresolved material claim attributes: " + ", ".join(missing))
    elif "supported" in states and "contradicted" in states:
        state = "unknown"
        note("conflicting relevant support and contradiction")
    elif "supported" in states:
        state = "supported"
    elif "contradicted" in states:
        state = "contradicted"
    elif not states or "unknown" in states:
        state = "unknown"
    else:
        state = "unsupported"
    bridges = {b.bridge_id: b for b in ledger.bridges}
    bridge_constraints = []
    resolved_bridge = False
    for number, bid in enumerate(prop.required_bridge_ids, start=1):
        bridge = bridges[bid]
        resolved = bridge.state == "supported" and _evidence_resolves(
            prop, bridge.evidence_ids, descriptions, evidence,
        )
        if resolved:
            note(f"{bid}: source-bound required bridge supported",
                 f"required bridge {number}: source-bound required bridge supported")
            resolved_bridge = True
        elif state != "contradicted":
            # Independent, direct capable evidence can support the same outcome;
            # it does not silently certify the reported mechanism explanation.
            independent = [b for b in prop.evidence_bindings if b.evidence_id not in bridge.evidence_ids
                           and b.directness == "direct" and b.observation == "support"]
            direct_resolves = any(_binding_state(
                prop, b, ledger, descriptions, scopes, evidence, record.negative_assertions,
            )[0]
                                  == "supported" for b in independent)
            if not direct_resolves:
                bridge_constraints.append("unsupported" if bridge.state == "unsupported" else "unknown")
            note(f"{bid}: required bridge {bridge.state}, capable evidence unresolved",
                 f"required bridge {number}: required bridge {bridge.state}, capable evidence unresolved")
    # Required bridges are simultaneous constraints, never sequential overwrites.
    if state != "contradicted":
        if "unknown" in bridge_constraints or missing:
            state = "unknown"
        elif bridge_constraints:
            state = "unsupported"
        elif resolved_bridge and "contradicted" not in states:
            state = "supported"
    profiles = [descriptions[b.evidence_id] for b in prop.evidence_bindings]
    identities = [{(k, getattr(d, k)) for k in ("study_id", "cohort_id", "dataset_id")
                   if getattr(d, k)} for d in profiles]
    dependency = "unknown"
    if any(a & b for i, a in enumerate(identities) for b in identities[i + 1:]):
        dependency = "dependent"
    elif identities and all(identities):
        dependency = "single_source" if len(identities) == 1 else "distinct_reported_identities"
    note(f"evidence dependence: {dependency}; no independent corroboration inferred")
    # AA-P8/1.1: the host state is the evidence derivation alone; the model judgment is kept
    # separately and never mixed in. Any difference, in either direction and including a model
    # UNKNOWN against a decisive host state, is an open conflict with effective state unknown.
    host_state = state
    host_reasons += host_tail
    conflict = prop.reported_verdict != host_state
    if conflict:
        reasons.append(f"model judgment {prop.reported_verdict} differs from host evidence derivation "
                       f"{host_state} ({HOST_RULE_VERSION}); open conflict, effective state unknown "
                       "until a mandatory review resolves it")
    return PropositionAssessment(
        proposition_id=prop.proposition_id, reported_verdict=prop.reported_verdict,
        derived_state="unknown" if conflict else host_state, host_state=host_state,
        host_reasons=list(host_reasons), model_host_conflict=conflict,
        required=prop.materiality == "required", reasons=reasons,
        evidence_ids=[b.evidence_id for b in prop.evidence_bindings], dependency_status=dependency,
    )


def _audit_transformations(ledger, model_states, model_composite):
    """Output integrity of the model's own analysis (AA-P8/1.1).

    An asserted state must restate the model's own judgment; disagreement with the host
    derivation is a separate model/host conflict, not an output defect. Returns the findings
    and the visible list of host-derived copies.
    """
    findings, copies = [], []
    props = {p.proposition_id: p for p in ledger.propositions}
    hedges = re.compile(r"\b(may|might|could|possibly|suggests?|könnte|möglicherweise)\b", re.I)
    certainty = {"hypothesis": 0, "possible": 0, "uncertain": 0, "probable": 1,
                 "established": 2, "certain": 2, "asserted": 2}
    for trans in ledger.transformations:
        source = trans.from_attributes
        if trans.stage == "extraction" and trans.target_id in props and all(
                value is None for value in trans.from_attributes.model_dump().values()):
            # The extraction source is text. An empty from_attributes asserts no change; the audit
            # uses the already validated proposition attributes and records that it did so.
            source = props[trans.target_id].attributes
            copies.append(f"{trans.transformation_id}: extraction from_attributes empty; meaning audit used "
                          "the validated proposition attributes (host-derived copy, not model content)")
        for dimension in SemanticAttributes.model_fields:
            before, after = getattr(source, dimension), getattr(trans.to_attributes, dimension)
            if _norm(before) == _norm(after):
                continue
            # A represented weaker certainty is a legitimate narrowing.
            if dimension == "certainty" and _norm(before) in certainty and _norm(after) in certainty:
                if certainty[_norm(after)] <= certainty[_norm(before)]:
                    continue
            findings.append(f"{trans.transformation_id}: semantic transformation changes {dimension}")
        if hedges.search(trans.from_text) and not hedges.search(trans.to_text):
            findings.append(f"{trans.transformation_id}: hedge removed")
        if trans.asserted_state is not None:
            own = model_composite if trans.asserts_whole_claim else model_states[trans.from_proposition_ids[0]]
            if trans.asserted_state != own:
                findings.append(f"{trans.transformation_id}: output state changes the model's own judgment {own}")
        if trans.stage == "summary" and trans.asserted_state is None:
            findings.append(f"{trans.transformation_id}: summary scientific state missing")
        # AA-P8/1.3: a whole-claim 'supported' summary also needs every source proposition the
        # model itself judges supported; a supported composite alone does not carry it.
        if trans.asserts_whole_claim and trans.asserted_state == "supported" and (
                model_composite != "supported"
                or any(model_states.get(pid) != "supported" for pid in trans.from_proposition_ids)):
            findings.append(f"{trans.transformation_id}: partial-to-whole promotion")
    return findings, copies


def evaluate_phase8(record: ForensicRecord) -> Phase8Assessment:
    """Preserve extraction and return a separately derived, fail-closed assessment."""
    raw = getattr(record, "phase8", None)
    if raw is None:
        return Phase8Assessment(technical_status="not_executed", reasons=["Phase-8 ledger absent"])
    try:
        ledger = PropositionLedger.model_validate(raw)
    except (ValidationError, ValueError, TypeError) as exc:
        return Phase8Assessment(technical_status="incomplete", reasons=[f"invalid ledger: {exc}"])
    errors = validate_ledger(record, ledger)
    if errors:
        return Phase8Assessment(technical_status="incomplete", reasons=errors)
    propositions = [_assess_proposition(prop, ledger, record) for prop in ledger.propositions]
    states = {prop.proposition_id: prop.derived_state for prop in propositions}
    model_states = {prop.proposition_id: prop.reported_verdict for prop in propositions}
    composite = aggregate_claim(ledger.logic, states)
    host_composite = aggregate_claim(ledger.logic, {p.proposition_id: p.host_state for p in propositions})
    model_composite = aggregate_claim(ledger.logic, model_states)
    conflicts = [ModelHostConflict(
        scope="proposition", proposition_id=p.proposition_id, required=p.required,
        model_state=p.reported_verdict, host_state=p.host_state,
        reason="Model judgment and host evidence derivation differ; mandatory review decides, not either side",
    ) for p in propositions if p.model_host_conflict]
    if model_composite != host_composite:
        conflicts.append(ModelHostConflict(
            scope="composite", model_state=model_composite, host_state=host_composite,
            reason="Composite of the model judgments differs from the composite of the host derivation"))
    transformations, copies = _audit_transformations(ledger, model_states, model_composite)
    return Phase8Assessment(
        technical_status="incomplete" if transformations else "completed", propositions=propositions,
        composite_state="unknown" if transformations else composite,
        assessed_composite_state=composite, model_composite_state=model_composite,
        host_composite_state=host_composite, model_host_conflicts=conflicts, host_derived_copies=copies,
        transformation_findings=transformations,
        reasons=[f"Ledger, evidence constraints and transformations evaluated under AA-P8/1.3 ({HOST_RULE_VERSION})",
                 *([f"{len(conflicts)} open model/host conflict(s); effective state unknown where they occur"]
                   if conflicts else []),
                 *transformations],
    )
