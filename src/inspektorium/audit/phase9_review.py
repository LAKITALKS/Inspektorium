"""Pure host-bound Phase-9 conflict detection and routing. Never executes a review."""

from __future__ import annotations

import hashlib
import json
from itertools import combinations

from inspektorium.audit.output_contract import parse_structured_output
from inspektorium.audit.phase8_models import PropositionLedger
from inspektorium.audit.phase8_pipeline import assess_agent_result
from inspektorium.audit.phase8_semantics import aggregate_claim
from inspektorium.audit.phase9_models import (
    CONTRACT_VERSION, ConflictPosition, Disagreement, Phase9Assessment, ReviewPosition, ReviewTrigger,
)
from inspektorium.audit.schemas import AgentResult, Task



ROUTING_REASON = "Routing preserves separate scientific/taxonomy layers; no majority or provider call executed"
def _hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def case_key(task: Task) -> str:
    """Run changes never renew the identity or per-case review allowance."""
    return "p9case:" + _hash([task.id, task.prompt, task.context])[:24]


def position_from_result(task: Task, result: AgentResult, run_id: str, origin="original") -> ReviewPosition:
    """Capture immutable input and recompute Phase8; ignore producer-supplied caches."""
    snapshot = result.model_dump(mode="json")
    snapshot.pop("phase8", None)
    snapshot.pop("phase9", None)
    phase8 = assess_agent_result(task, result)
    parsed = result.parsed
    if result.raw_output:
        parsed, _ = parse_structured_output(result.raw_output, result.finish_reason)
    payload = parsed.forensic_record if parsed else None
    payload = payload if isinstance(payload, dict) else None
    ledger = payload.get("phase8") if payload else None
    claim_id = ledger.get("claim_id", "") if isinstance(ledger, dict) else ""
    raw_hash = hashlib.sha256(result.raw_output.encode()).hexdigest()
    identity = [case_key(task), run_id, origin, _hash(snapshot)]
    return ReviewPosition(
        position_id="p9position:" + _hash(identity)[:24], case_id=case_key(task), run_id=run_id,
        claim_id=claim_id, origin=origin, provider=result.provider, model=result.model,
        raw_sha256=raw_hash, agent_result=snapshot, forensic_record=payload, phase8=phase8,
    )


def _ledger(position):
    try:
        return PropositionLedger.model_validate((position.forensic_record or {}).get("phase8"))
    except (ValueError, TypeError):
        return None


def _states(position):
    return {p["proposition_id"]: p["derived_state"] for p in position.phase8.get("propositions", [])}


def _directly_influences_output(position, pid):
    ledger = _ledger(position)
    states = _states(position)
    if ledger is None or pid not in states:
        return True
    try:
        baseline = aggregate_claim(ledger.logic, states)
        for value in ("supported", "unsupported", "contradicted", "unknown"):
            if aggregate_claim(ledger.logic, {**states, pid: value}) != baseline:
                return True
    except ValueError:
        return True
    # A separately decisive output assertion can be material even when another
    # disjunct establishes the composite. An honestly unknown optional output is not.
    # AA-P9/1.3: a whole-claim summary is decisive for its source propositions too.
    if any(t.stage == "summary" and pid in t.from_proposition_ids
           and t.asserted_state not in {None, "unknown"}
           for t in ledger.transformations):
        return True
    return _decides_derived_label(position, ledger, states, pid)


def _decides_derived_label(position, ledger, states, pid):
    """The derived taxonomy label is a released decisive output (Package B, P8-F1).

    A proposition is material when another state of it would change that label, e.g. a
    conflict-derived or agreed UNKNOWN on the CvC/ME trigger proposition.
    """
    phase8 = position.phase8 or {}
    if (phase8.get("taxonomy") or {}).get("technical_status") != "completed":
        return False
    from inspektorium.audit.phase8_taxonomy import assess_taxonomy
    from inspektorium.audit.schemas import ForensicRecord
    try:
        record = ForensicRecord.model_validate(position.forensic_record)
        semantic = {**phase8, "technical_status": "completed"}

        def label(value):
            changed = {**states, pid: value}
            props = [{**p, "derived_state": changed.get(p["proposition_id"], p.get("derived_state"))}
                     for p in phase8.get("propositions", [])]
            return assess_taxonomy(record, {**semantic, "propositions": props,
                                            "composite_state": aggregate_claim(ledger.logic, changed)})["derived_label"]
        baseline = label(states[pid])
        return any(label(value) != baseline for value in ("supported", "unsupported", "contradicted", "unknown"))
    except (ValueError, TypeError):
        return True


def _premises(ledger, pid):
    proposition = next((p for p in ledger.propositions if p.proposition_id == pid), None)
    return set(proposition.premise_proposition_ids if proposition else []) | {
        premise for bridge in ledger.bridges if bridge.conclusion_proposition_id == pid
        for premise in bridge.premise_proposition_ids
    }


def _influences_output(position, pid):
    ledger = _ledger(position)
    if ledger is None:
        return True
    # A premise inherits the materiality of every conclusion that actually cites it.
    pending, seen = [pid], set()
    while pending:
        current = pending.pop()
        if current in seen:
            continue
        seen.add(current)
        if _directly_influences_output(position, current):
            return True
        pending.extend(p.proposition_id for p in ledger.propositions
                       if current in _premises(ledger, p.proposition_id))
    return False


def _evidence_closure(ledger, proposition):
    """All source objects that can affect this proposition's represented inference."""
    props = {p.proposition_id: p for p in ledger.propositions}
    pending_props, seen_props, pending = [proposition.proposition_id], set(), []
    while pending_props:
        pid = pending_props.pop()
        if pid in seen_props or pid not in props:
            continue
        seen_props.add(pid)
        prop = props[pid]
        bindings = {b.binding_id for b in prop.evidence_bindings}
        pending.extend(b.evidence_id for b in prop.evidence_bindings)
        pending.extend(eid for bridge in ledger.bridges
                       if bridge.conclusion_proposition_id == pid for eid in bridge.evidence_ids)
        pending.extend(eid for transfer in ledger.product_transfers
                       if transfer.binding_id in bindings for eid in transfer.evidence_ids)
        pending_props.extend(_premises(ledger, pid))
    descriptions = {d.evidence_id: d for d in ledger.evidence_descriptions}
    seen = set()
    while pending:
        eid = pending.pop()
        if eid in seen:
            continue
        seen.add(eid)
        description = descriptions.get(eid)
        if description:
            pending.extend(description.underlying_evidence_ids + description.identification_evidence_ids)
    return seen


def _evidence_ids(position, pid=None):
    ledger = _ledger(position)
    if not ledger:
        return []
    return sorted({eid for p in ledger.propositions if pid is None or p.proposition_id == pid
                   for eid in _evidence_closure(ledger, p)})


def _trigger(position, code, field, reason, *, pids=(), evidence=(), mandatory=True):
    return ReviewTrigger(
        trigger_id="p9trigger:" + _hash([position.position_id, code, field, sorted(pids)])[:24],
        code=code, case_id=position.case_id, claim_id=position.claim_id,
        position_ids=[position.position_id], proposition_ids=sorted(pids), evidence_ids=sorted(evidence),
        field=field, reason=reason, mandatory=mandatory, material=mandatory,
    )


def _position_triggers(position):
    assessment = position.phase8
    triggers = []
    if assessment.get("technical_status") != "completed":
        reasons = assessment.get("reasons", ["Phase8 analysis absent or incomplete"])
        triggers.append(_trigger(position, "failed_mandatory_control", "phase8.technical_status",
                                 "; ".join(reasons)))
    taxonomy = assessment.get("taxonomy", {})
    if taxonomy.get("technical_status") == "incomplete":
        annotation = (position.forensic_record or {}).get("phase8_taxonomy") or {}
        def ids(field):
            value = annotation.get(field, []) if isinstance(annotation, dict) else []
            return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []

        triggers.append(_trigger(position, "failed_mandatory_control", "phase8.taxonomy.technical_status",
                                 "; ".join(taxonomy.get("reasons", ["Invalid taxonomy analysis"])),
                                 pids=ids("proposition_ids"), evidence=ids("evidence_ids")))
    for index, finding in enumerate(assessment.get("transformation_findings", [])):
        ledger = _ledger(position)
        source = next((t for t in ledger.transformations
                       if finding.startswith(t.transformation_id + ":")), None) if ledger else None
        pids = source.from_proposition_ids if source else []
        triggers.append(_trigger(position, "material_transformation",
                                 f"transformations.{source.transformation_id}" if source else
                                 f"phase8.transformation_findings[{index}]", finding,
                                 pids=pids, evidence=sorted({eid for pid in pids
                                                          for eid in _evidence_ids(position, pid)})))
    for control in assessment.get("phase7_controls", []):
        for finding in control.get("findings", []):
            if finding.get("severity") in {"critical", "major"}:
                code = finding.get("code", "failed_mandatory_control")
                triggers.append(_trigger(position, "critical_source_binding" if "binding" in code
                                         else "failed_mandatory_control",
                                         f"phase8.phase7_controls.{control['name']}",
                                         finding.get("detail", code), evidence=finding.get("refs", [])))
    # AA-P9/1.1: a model/host state difference within one position is a review trigger in both
    # directions, also when the host derivation is decisive. A material one is mandatory.
    for conflict in assessment.get("model_host_conflicts", []):
        if conflict.get("scope") == "composite":
            pids, material, field = [], True, "phase8.composite_model_host_conflict"
        else:
            pid = conflict.get("proposition_id")
            pids, material, field = [pid], _influences_output(position, pid), f"propositions.{pid}.model_host_conflict"
        triggers.append(_trigger(
            position, "model_host_conflict" if material else "bounded_model_host_conflict", field,
            f"Model judgment {conflict.get('model_state')} differs from host evidence derivation "
            f"{conflict.get('host_state')} ({conflict.get('host_rule_version')}); "
            + ("mandatory review; neither side is adopted automatically" if material else
               "visible; does not change the composite or a decisive output"),
            pids=pids, evidence=sorted({eid for p in pids for eid in _evidence_ids(position, p)}) if pids
            else _evidence_ids(position), mandatory=material))
    for pid, state in _states(position).items():
        if state == "unknown":
            mandatory = _influences_output(position, pid)
            triggers.append(_trigger(position, "necessary_unknown" if mandatory else "bounded_unknown",
                                     f"propositions.{pid}.derived_state",
                                     "Scientific UNKNOWN affects admissible output" if mandatory else
                                     "UNKNOWN remains visible without changing composite or decisive output",
                                     pids=[pid], evidence=_evidence_ids(position, pid), mandatory=mandatory))
    return triggers


def _conflict(left, right, dimension, field, a, b, *, pids=(), material=True):
    positions = [ConflictPosition(position_id=p.position_id, value=value,
                                  evidence_ids=_evidence_ids(p, pids[0] if len(pids) == 1 else None))
                 for p, value in ((left, a), (right, b))]
    positions.sort(key=lambda p: p.position_id)
    identity = [left.case_id, dimension, field, [p.model_dump() for p in positions]]
    return Disagreement(
        disagreement_id="p9conflict:" + _hash(identity)[:24], case_id=left.case_id,
        claim_id=left.claim_id, proposition_ids=sorted(pids), dimension=dimension, field=field,
        positions=positions, material=material,
        reason="Same-dimension positions change admissible output" if material else
        "Difference is confined to a component without composite or decisive output impact",
        provenance=sorted([left.position_id, right.position_id]),
    )


def _canonical(items):
    return sorted(items, key=lambda item: json.dumps(item, sort_keys=True))


def _compare(left, right):
    left, right = sorted((left, right), key=lambda p: p.position_id)
    conflicts = []
    for dimension, field in (("label", "original_model_label"), ("label", "derived_label"),
                             ("composite", "composite_state")):
        a, b = left.phase8.get(field), right.phase8.get(field)
        if a != b:
            conflicts.append(_conflict(left, right, dimension, f"phase8.{field}", a, b))
    ll, rl = _ledger(left), _ledger(right)
    if ll is None or rl is None:
        return conflicts
    lp = {p.proposition_id: p for p in ll.propositions}
    rp = {p.proposition_id: p for p in rl.propositions}
    if set(lp) != set(rp):
        conflicts.append(_conflict(left, right, "proposition", "proposition_identity",
                                   sorted(lp), sorted(rp), pids=sorted(set(lp) | set(rp))))
    ls, rs = _states(left), _states(right)
    for pid in sorted(set(lp) & set(rp)):
        a, b = lp[pid], rp[pid]
        material = _influences_output(left, pid) or _influences_output(right, pid)
        if a.original_span != b.original_span or a.parent_claim_id != b.parent_claim_id:
            conflicts.append(_conflict(left, right, "proposition", f"propositions.{pid}.identity",
                                       {"parent_claim_id": a.parent_claim_id, "span": a.original_span.model_dump()},
                                       {"parent_claim_id": b.parent_claim_id, "span": b.original_span.model_dump()},
                                       pids=[pid], material=True))
            continue
        candidates = [("unknown" if "unknown" in {ls.get(pid), rs.get(pid)} else "proposition",
                       "derived_state", ls.get(pid), rs.get(pid)),
                      ("proposition", "materiality", a.materiality, b.materiality),
                      ("proposition", "premise_proposition_ids",
                       sorted(a.premise_proposition_ids), sorted(b.premise_proposition_ids)),
                      ("causal_strength", "required_bridge_ids",
                       sorted(a.required_bridge_ids), sorted(b.required_bridge_ids))]
        for key in type(a.attributes).model_fields:
            dimension = ("causal_strength" if key in {"relation", "certainty"} else
                         "product_transfer" if key in {"intervention", "dose", "formulation", "route"}
                         else "proposition")
            candidates.append((dimension, "attributes." + key, getattr(a.attributes, key), getattr(b.attributes, key)))
        candidates.extend([
            ("evidence", "evidence_bindings", _canonical([
                [x.evidence_id, x.observation, x.directness] for x in a.evidence_bindings]), _canonical([
                [x.evidence_id, x.observation, x.directness] for x in b.evidence_bindings])),
            ("product_transfer", "product_transfers", _canonical([
                [t.state, sorted(t.dimensions), sorted(t.evidence_ids)] for t in ll.product_transfers
                if t.binding_id in {x.binding_id for x in a.evidence_bindings}]), _canonical([
                [t.state, sorted(t.dimensions), sorted(t.evidence_ids)] for t in rl.product_transfers
                if t.binding_id in {x.binding_id for x in b.evidence_bindings}])),
            ("causal_strength", "bridges", _canonical([
                [x.kind, x.state, sorted(x.evidence_ids), sorted(x.premise_proposition_ids)] for x in ll.bridges if x.conclusion_proposition_id == pid]),
             _canonical([[x.kind, x.state, sorted(x.evidence_ids), sorted(x.premise_proposition_ids)] for x in rl.bridges
                         if x.conclusion_proposition_id == pid])),
        ])
        selected_evidence = []
        for position, proposition, ledger in ((left, a, ll), (right, b, rl)):
            bound = _evidence_closure(ledger, proposition)
            selected_evidence.append(_canonical([
                [e["evidence_id"], e.get("source_id"), e.get("text"), e.get("exact_reference"), e.get("role")]
                for e in (position.forensic_record or {}).get("evidence", []) if e["evidence_id"] in bound
            ]))
        candidates.append(("evidence", "selected_source_objects", *selected_evidence))
        evidence_interpretations, transformations = [], []
        for ledger, proposition in ((ll, a), (rl, b)):
            bound = _evidence_closure(ledger, proposition)
            evidence_interpretations.append(_canonical([
                {k: v for k, v in d.model_dump().items() if k != "quality"}
                for d in ledger.evidence_descriptions if d.evidence_id in bound
            ]))
            transformations.append(_canonical([
                [t.stage, t.from_attributes.model_dump(), t.to_attributes.model_dump(),
                 t.asserted_state, t.asserts_whole_claim]
                for t in ledger.transformations if pid in t.from_proposition_ids
            ]))
        candidates.append(("evidence", "evidence_interpretation", *evidence_interpretations))
        candidates.append(("proposition", "output_transformations", *transformations))
        scopes = []
        for position, proposition in ((left, a), (right, b)):
            scopes.append(_canonical([
                [s["scope_type"], sorted(s.get("reviewed_source_ids", [])),
                 sorted(s.get("query_terms", [])), s.get("date_cutoff")]
                for s in (position.forensic_record or {}).get("search_scopes", [])
                if s["search_scope_id"] in proposition.search_scope_ids
            ]))
        candidates.append(("search_scope", "search_scope", *scopes))
        for dimension, field, av, bv in candidates:
            if av != bv:
                conflicts.append(_conflict(left, right, dimension, f"propositions.{pid}.{field}",
                                           av, bv, pids=[pid], material=material))
    if ll.logic != rl.logic:
        conflicts.append(_conflict(left, right, "composite", "claim_logic",
                                   ll.logic.model_dump(), rl.logic.model_dump()))
    return conflicts


def assess_case(task: Task, positions: list[ReviewPosition], *, prior_conflicts=()) -> Phase9Assessment:
    """Revalidate snapshots, retain every conflict, and route without adjudicating."""
    case_id = case_key(task)
    if not positions:
        return Phase9Assessment(case_id=case_id, technical_status="not_executed", route="UNRESOLVED",
                                review_state="pending", reasons=["No Phase9 positions supplied"])
    checked, triggers, reasons, invalid = [], [], [], False
    for position in positions:
        try:
            recomputed = position_from_result(task, AgentResult.model_validate(position.agent_result),
                                              position.run_id, position.origin)
            # Raw-derived identities and assessments must agree on replay. The
            # immutable original remains visible even when the cache is corrupt.
            if recomputed != position:
                raise ValueError("Stored position differs from host-bound raw revalidation")
        except (ValueError, TypeError) as exc:
            invalid = True
            triggers.append(_trigger(position, "critical_source_binding", "position.identity", str(exc)))
            checked.append(position)
            continue
        checked.append(recomputed)
        triggers.extend(_position_triggers(recomputed))
    retained = []
    by_id = {}
    for p in checked:
        previous = by_id.get(p.position_id)
        if previous is None:
            by_id[p.position_id] = p
            retained.append(p)
        elif previous == p:
            reasons.append("Identical replay position ignored; no additional position or vote created")
        else:
            invalid = True
            retained.append(p)
            triggers.append(_trigger(p, "critical_source_binding", "position.identity",
                                     "Same position ID contains inconsistent snapshots; all originals retained"))
    checked = retained
    conflicts = []
    if not invalid:
        for left, right in combinations(checked, 2):
            conflicts.extend(_compare(left, right))
    fresh_conflicts = {c.disagreement_id: c for c in conflicts}
    for conflict in prior_conflicts:
        if conflict.case_id != case_id:
            invalid = True
            reasons.append("Prior conflict belongs to a different case")
        elif conflict.disagreement_id in fresh_conflicts:
            if conflict != fresh_conflicts[conflict.disagreement_id]:
                invalid = True
                reasons.append("Prior conflict differs from fresh bound conflict; fresh result retained")
        else:
            conflicts.append(conflict)
            fresh_conflicts[conflict.disagreement_id] = conflict
    conflicts.sort(key=lambda c: c.disagreement_id)
    for conflict in conflicts:
        if conflict.material:
            anchor = next(p for p in checked if p.position_id in conflict.provenance) if any(
                p.position_id in conflict.provenance for p in checked
            ) else checked[0]
            code = {"label": "label_conflict", "evidence": "evidence_direction_or_selection",
                    "proposition": "proposition_conflict", "causal_strength": "causality_conflict",
                    "product_transfer": "product_transfer_conflict", "search_scope": "search_scope_conflict",
                    "composite": "composite_conflict", "unknown": "unknown_conflict"}[conflict.dimension]
            trigger = _trigger(anchor, code, conflict.field, conflict.reason,
                               pids=conflict.proposition_ids,
                               evidence=sorted({eid for p in conflict.positions for eid in p.evidence_ids}))
            trigger.position_ids = [p.position_id for p in conflict.positions]
            triggers.append(trigger)
    mandatory = invalid or any(t.mandatory for t in triggers)
    technical_failure = invalid or any(
        p.phase8.get("technical_status") != "completed" or
        p.phase8.get("taxonomy", {}).get("technical_status") == "incomplete" for p in checked
    )
    if technical_failure or any(c.material for c in conflicts):
        route = "HUMAN_REVIEW_REQUIRED"
    elif mandatory:
        route = "REVIEW_RECOMMENDED"
    else:
        route = "AUTO_RESOLVABLE"
    uncertainty = sorted({f"{p.position_id}/{pid}: scientific UNKNOWN" for p in checked
                          for pid, state in _states(p).items() if state == "unknown"})
    return Phase9Assessment(
        contract_version=CONTRACT_VERSION, case_id=case_id,
        technical_status="incomplete" if technical_failure else "completed", route=route,
        mandatory=mandatory, review_state="pending" if mandatory else "not_required",
        positions=checked, conflicts=conflicts,
        triggers=sorted({t.trigger_id: t for t in triggers}.values(), key=lambda t: t.trigger_id),
        uncertainty=uncertainty, reasons=reasons + [ROUTING_REASON],
    )
