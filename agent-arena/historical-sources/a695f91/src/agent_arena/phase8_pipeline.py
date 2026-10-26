"""Source-bound Phase-8 adapter for existing analysis and reporting paths.

Only supplied input/context is available to this adapter. It never searches or
contacts a provider. Raw extraction and model classifications remain separate
from the deterministic assessment.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from agent_arena.schemas import AgentResult, ForensicRecord, RunRecord, Task, TaskType


LIMITATION = (
    "Checks validate represented semantics and source spans; they do not prove correct "
    "model extraction, exhaustive evidence search, scientific truth or live-model accuracy."
)


def build_phase8_prompt() -> str:
    """Versioned extraction contract; semantic annotations originate in this response."""
    from agent_arena.phase8_models import PropositionLedger
    from agent_arena.phase8_taxonomy import TaxonomyAssessment
    return """You are a scientific claim analyst using AA-P8/1.0.
Use only the supplied task prompt and context. Return JSON with final_answer (one of
solid, overclaim, correlation_vs_causation, mechanism_vs_evidence), confidence,
brief reasons in steps/uncertainties, and forensic_record matching the schemas below.
Preserve the entire task prompt verbatim as the original claim in ClaimProvenance
and phase8.original_claim. Use source_id input for task.prompt, context for task.context.
Evidence exact_reference AND text must be exact nonempty quotations from that source.
Do not invent a source, external search, study identity, design property or match.
Use null/unknown for unresolved properties and concise reasons for inapplicability.
Use claim_id 'claim', proposition IDs 'claim:p1', 'claim:p2', etc.; no hashes needed.
Each proposition needs a verbatim original_span (zero-based Python character offsets),
required/optional materiality, declared required IDs, genuine AND/OR logic and evidence
bindings to that proposition. Preserve every necessary component, including failed ones.
An alternative is not automatically a conjunction. Optional context cannot prove the claim.
Create an InternalFinding with finding_id equal to each proposition_id, preserving its
text/provenance and evidence IDs. Bind client findings to those findings; do not invent
stronger final claims. Represent search questions and output wording transformations
with their semantic attributes, from/to text and target references, including unchanged
transformations so missing inspection cannot be mistaken for success.
For internal transformations, to_text must contain the finding proposition plus, when
present, a newline and verdict_summary. For summary transformations, to_text must
contain display_claim plus, when present, a newline and client_explanation. Audit the
entire output assertion, including explanations; a matching title alone is insufficient.
The old Phase-7 summary-strength fields use not_assessed, mixed, not_directly_established,
limited_support, not_supported, contradicted or disproven. They are not taxonomy labels.
For positive scientific support use the Phase-8 summary asserted_state; the legacy
summary-strength field can stay not_assessed. Phase-8 scientific states remain separate.
Use existing reviewed_set SearchScopes for supplied material; no external search has
been executed. No evidence found is not no evidence exists. No significant effect is
not a proven zero effect. Unknown study dependence is not independence.
Directness belongs to each binding; capability depends on design, population, endpoint,
intervention and comparison, never a universal evidence-tier ladder. Mechanistic/animal
evidence may support a mechanism-only claim; human benefit needs the relevant clinical
evidence and any claimed mechanism-to-outcome bridge. Controlled does not always mean
causally identified. Keep product, dose, formulation, route and follow-up transfers explicit.
Audit hedge loss, certainty escalation, endpoint/population/comparator changes, within-
versus-between comparisons, relative-versus-absolute magnitude and partial-to-whole claims.
Do not fix the source claim silently. Keep original model verdict separate from derived
assessment. Confidence cannot override missing or unknown mandatory information.
Taxonomy: correlation_vs_causation needs a causal assertion from noncausal/uncontrolled/
confounded evidence AND this must be the core error. Established causation with inflated
magnitude/population scope remains overclaim, not automatically CvC. Mere absence of
adequate efficacy evidence does not establish an actual correlation-to-causation
inference. mechanism_vs_evidence
requires a described biological/preclinical mechanism used to imply unsupported human
clinical benefit and core-error relevance. Biomarker-to-clinical inflation alone is
overclaim; honest reporting limited to observed results may be solid. Do not stretch labels.
Include forensic_record.phase8_taxonomy using the third schema. Record the core error,
explicit true/false/unknown triggers, proposition/evidence references, and a verbatim
trigger_quote bound to the specific trigger_proposition_id/trigger_evidence_id pair.
A trigger description is not proof of its presence. Preserve uncertainty with null.
The taxonomy check is separate from scientific support; neither silently replaces
final_answer or the original proposition verdicts.
ForensicRecord schema (phase8 uses the second schema):
""" + json.dumps(ForensicRecord.model_json_schema(), separators=(",", ":")) + (
        "\nPropositionLedger schema:\n"
    ) + json.dumps(PropositionLedger.model_json_schema(), separators=(",", ":")) + (
        "\nTaxonomyAssessment schema:\n"
    ) + json.dumps(TaxonomyAssessment.model_json_schema(), separators=(",", ":"))


def unavailable(status: str, reason: str, original_label: str | None = None) -> dict:
    return {
        "contract_version": "AA-P8/1.0",
        "technical_status": status,
        "composite_state": "unknown",
        "original_model_label": original_label,
        "derived_label": None,
        "reasons": [reason],
        "propositions": [],
        "limitations": [LIMITATION],
    }


def assess_forensic_payload(
    payload: Any,
    *,
    original_input: str,
    context: str = "",
    original_label: str | None = None,
    parse_complete: bool = True,
) -> dict:
    """Validate extraction against host-owned material, then run semantic checks."""
    if not parse_complete:
        return unavailable(
            "incomplete", "Parsing was failed, truncated or repaired; extraction is incomplete.",
            original_label,
        )
    if payload is None:
        return unavailable("not_executed", "No Phase-8 analysis was supplied.", original_label)
    try:
        record = ForensicRecord.model_validate(payload)
    except (ValueError, TypeError) as exc:
        return unavailable("incomplete", f"Invalid forensic record: {exc}", original_label)

    errors = []
    sources = {"input": original_input, "context": context}
    if not original_input.strip():
        errors.append("Host original input is empty.")
    if len(record.provenance) != 1:
        errors.append("Exactly one host-bound original claim provenance is required.")
    for provenance in record.provenance:
        if provenance.source_id != "input" or provenance.exact_claim_text != original_input:
            errors.append("Original claim/provenance differs from the captured input.")
        if provenance.content_fingerprint is not None:
            from agent_arena.artifact_binding import compute_content_fingerprint
            expected = compute_content_fingerprint(
                provenance.exact_claim_text, provenance.provenance_state,
            )
            if provenance.content_fingerprint != expected:
                errors.append("Original claim content fingerprint is invalid.")
    for evidence in record.evidence:
        source = sources.get(evidence.source_id)
        quote = evidence.exact_reference
        if source is None or not quote or not quote.strip() or quote not in source:
            errors.append(f"Evidence {evidence.evidence_id}: exact source quote does not resolve.")
        if not evidence.text.strip() or source is None or evidence.text not in source:
            errors.append(f"Evidence {evidence.evidence_id}: text is not bound to supplied material.")
    for scope in record.search_scopes:
        if any(s not in sources or not sources[s].strip() for s in scope.reviewed_source_ids):
            errors.append(f"Search scope {scope.search_scope_id}: source was not supplied.")
        # A model cannot certify an external search the host did not execute.
        if scope.scope_type == "documented_search":
            errors.append(f"Search scope {scope.search_scope_id}: external search not executed.")
    if errors:
        assessment = unavailable("incomplete", errors[0], original_label)
        assessment["reasons"] = errors
    else:
        from agent_arena.phase8_semantics import evaluate_phase8
        try:
            result = evaluate_phase8(record)
            assessment = result.model_dump(mode="json")
        except Exception as exc:
            assessment = unavailable("incomplete", f"Semantic control failed: {exc}", original_label)
        assessment["original_model_label"] = original_label
        assessment.setdefault("derived_label", None)
        assessment.setdefault("limitations", []).append(LIMITATION)
    controls, gate_errors = _phase7_controls(record)
    assessment["phase7_controls"] = controls
    if gate_errors:
        assessment["technical_status"] = "incomplete"
        assessment["composite_state"] = "unknown"
        assessment["derived_label"] = None
        assessment.setdefault("reasons", []).extend(gate_errors)
    from agent_arena.phase8_taxonomy import assess_taxonomy
    taxonomy = assess_taxonomy(record, assessment)
    assessment["taxonomy"] = taxonomy
    assessment["derived_label"] = taxonomy["derived_label"]
    from agent_arena.artifact_binding import record_fingerprint
    assessment["record_fingerprint"] = record_fingerprint(record)
    assessment["input_sha256"] = hashlib.sha256(original_input.encode()).hexdigest()
    ledger = record.phase8 or {}
    propositions = ledger.get("propositions", [])
    assessment["canonical_proposition_ids"] = {
        p.get("proposition_id", ""): "p8:" + hashlib.sha256(json.dumps(
            [original_input, p.get("original_span"), p.get("proposition_text")],
            sort_keys=True,
        ).encode()).hexdigest()[:24]
        for p in propositions if isinstance(p, dict)
    } if isinstance(propositions, list) else {}
    return assessment


def _phase7_controls(record: ForensicRecord) -> tuple[list[dict], list[str]]:
    """Reuse every existing check; derive applicability, never accept model opt-outs."""
    from agent_arena.artifact_binding import MANDATORY_PHASE7B_GATE_SPECS
    controls, errors = [], []
    if not record.provenance or not record.findings or not record.client_findings:
        errors.append("Required claim/finding/client trace population is empty.")
    for spec in MANDATORY_PHASE7B_GATE_SPECS:
        try:
            count = spec.eligible_count(record)
            findings = spec.check(record)
            required = spec.population == "client_findings"
            state = "executed" if count else ("incomplete" if required else "not_applicable")
            controls.append({
                "name": spec.gate_id, "status": state, "eligible_count": count,
                "evaluated_count": count,
                "reason": "Objects evaluated" if count else (
                    "Required output population absent" if required else
                    f"No {spec.population} in this record"
                ),
                "findings": [f.model_dump(mode="json") for f in findings],
            })
            errors.extend(f"Phase 7 {f.code}: {f.detail}" for f in findings
                          if f.severity in {"critical", "major"})
        except Exception as exc:
            controls.append({"name": spec.gate_id, "status": "incomplete", "reason": str(exc)})
            errors.append(f"Phase 7 {spec.gate_id} failed: {exc}")
    return controls, errors


def assess_agent_result(task: Task, result: AgentResult) -> dict:
    """Recompute, never trust a cached/model-supplied derived assessment."""
    if task.task_type != TaskType.STUDY_FORENSICS:
        return {}
    from agent_arena.output_contract import parse_structured_output
    from agent_arena.study_forensics_checker import _detect_label

    parsed = result.parsed
    complete = result.parse_ok and not result.error
    if result.raw_output:
        parsed, diagnostics = parse_structured_output(result.raw_output, result.finish_reason)
        complete = complete and diagnostics.ok and not (
            diagnostics.truncation_suspected or diagnostics.repaired
        )
    original_label = _detect_label(parsed) if parsed else None
    if not complete:
        assessment = unavailable("incomplete", "Analysis/parse did not complete.", original_label)
    else:
        assessment = assess_forensic_payload(
            parsed.forensic_record if parsed else None,
            original_input=task.prompt,
            context=task.context,
            original_label=original_label,
            parse_complete=complete,
        )
    assessment["raw_response_sha256"] = hashlib.sha256(result.raw_output.encode()).hexdigest()
    return assessment


def phase8_view(assessment: dict | None) -> dict:
    """Explicit legacy fallback for loaded results and existing renderers."""
    return assessment or unavailable("not_executed", "Legacy result: Phase-8 control not executed.")


def refresh_run_phase8(record: RunRecord) -> RunRecord:
    """Loaded/manual report inputs cannot forge or omit the current assessment."""
    if record.task.task_type != TaskType.STUDY_FORENSICS:
        return record
    results = []
    for evaluated in record.results:
        agent = evaluated.agent_result.model_copy(update={
            "phase8": assess_agent_result(record.task, evaluated.agent_result),
        })
        forensic = dict(evaluated.study_forensics or {})
        forensic.update(is_study_forensics=True,
                        detected_label=agent.phase8.get("original_model_label"),
                        phase8=agent.phase8)
        results.append(evaluated.model_copy(update={
            "agent_result": agent, "study_forensics": forensic,
        }))
    return record.model_copy(update={"results": results})


def render_phase8(assessment: dict | None) -> str:
    data = phase8_view(assessment)
    lines = [
        f"**Phase 8 semantics:** {data['technical_status']} — "
        f"**{data.get('composite_state', 'unknown').upper()}**",
        f"Original model classification: `{data.get('original_model_label') or 'unknown'}`; "
        f"derived classification: `{data.get('derived_label') or 'unknown'}`.",
    ]
    taxonomy = data.get("taxonomy")
    if taxonomy:
        lines.append(f"Taxonomy control: `{taxonomy['technical_status']}`.")
        lines.extend(f"- {reason}" for reason in taxonomy.get("reasons", []))
    if data.get("assessed_composite_state") and data["assessed_composite_state"] != data.get("composite_state"):
        lines.append(
            "Component aggregate before the failed output audit: "
            f"`{data['assessed_composite_state']}`; this is not a completed output decision."
        )
    for reason in data.get("reasons", []):
        lines.append(f"- {reason}")
    for proposition in data.get("propositions", []):
        if isinstance(proposition, dict):
            lines.append(
                f"- `{proposition.get('proposition_id', '?')}`: "
                f"{proposition.get('derived_state', proposition.get('state', 'unknown'))}"
            )
    lines.append(LIMITATION)
    return "\n\n".join(lines)
