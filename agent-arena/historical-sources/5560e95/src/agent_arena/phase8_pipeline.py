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


def build_phase8_contract_r1() -> str:
    """AA-P10-LIVE/1.0 repair revision R1: state the existing deterministic AA-P8/1.0 checks.

    Live outputs under v3-phase8 failed checks that prompt never stated (exact copy fields,
    vocabularies, required trace objects). This text only discloses the validators in
    phase8_pipeline, phase8_semantics, phase8_taxonomy and the Phase-7 gates; it adds no
    scientific rule, no case content and no expected answer. Vocabularies come from the
    validator constants, and the resulting prompt bytes are pinned by tests.
    """
    from typing import get_args

    from agent_arena.phase8_models import Directness, Observation, SemanticAttributes
    from agent_arena.phase8_semantics import CORE_DIMENSIONS, PRODUCT_DIMENSIONS, RELATIONS
    from agent_arena.phase8_taxonomy import CAUSAL_RELATIONS, CLINICAL_ENDPOINTS
    from agent_arena.schemas import (
        ASSERTION_SCOPES, SUMMARY_STRENGTH_ORDER, VALUE_ORIGINS, EvidenceRole,
    )

    def names(values) -> str:
        return ", ".join(values)

    # The strings phase8_semantics._unknown_value treats as unknown besides None and "" (test-pinned).
    unknown_values = ("unknown", "unspecified", "unresolved", "unclear", "not_reported", "not reported",
                      "n/a", "not_applicable")

    groups: dict[str, list[str]] = {}
    for value, group in RELATIONS.items():
        groups.setdefault(group, []).append(value)
    relations = "; ".join(f"{group}: {names(values)}" for group, values in groups.items())
    return f"""AA-P8/1.0 deterministic host contract (live repair revision R1). The host checks your JSON
with exactly these rules; they make the instructions above precise. Any violation makes the analysis
technically incomplete, so copy values literally wherever a rule says equal. IDs are unique within their
kind, and binding_id values are unique across all propositions.
Shape
C1. forensic_record.phase8 is one PropositionLedger object with only PropositionLedger keys. Do not put
final_answer, confidence or any other key into it and do not wrap it in another object.
forensic_record.phase8_taxonomy is one TaxonomyAssessment object.
C2. forensic_record.provenance has exactly one ClaimProvenance: source_id "input", exact_claim_text equal
to the complete task prompt, provenance_id equal to phase8.provenance_id and content_fingerprint null.
phase8.original_claim equals exact_claim_text.
Evidence
C3. Each evidence item: source_id "input" or "context"; exact_reference and text are character-exact
substrings of that source (no paraphrase, ellipsis or changed punctuation; one quote may serve as both).
role is one of: {names(role.value for role in EvidenceRole)}.
C4. material defaults to true. Every evidence item with material true must be used by an evidence binding,
bridge, product transfer or identification/underlying link of an evidence description; material false is
only for evidence that is not materially relevant to the claim.
C5. Every evidence ID used by a binding, bridge, product transfer or description link has exactly one
phase8.evidence_descriptions entry with that evidence_id; no description for an unknown evidence ID.
C6. value_origin is "{VALUE_ORIGINS[0]}" (the source states the value; exact_reference required) or
"{VALUE_ORIGINS[1]}" (you computed it; list input_evidence_ids). Any other value is unresolved, and an
item with a reported_value but an unresolved value_origin blocks the client output. A client value_claims
entry needs an evidence item with a resolved value_origin even without a reported_value; its
claimed_origin repeats that origin or is "unspecified", and the claimed_source_ids of a system_derived
value stay within the sources of its input_evidence_ids.
C7. identification_argument is null or a character-exact substring of the text of an evidence item listed
in identification_evidence_ids; each listed item needs its own evidence description.
Propositions and logic
C8. proposition_id "claim:p1", "claim:p2", ...; parent_claim_id equals claim_id; provenance_id equals
phase8.provenance_id.
C9. original_span.text is copied from original_claim and original_claim[start:end] equals it exactly
(zero-based Python offsets, end = start + len(text)); count every space and punctuation mark.
C10. required_proposition_ids is nonempty and equals the IDs of all propositions with materiality
"required". logic leaves are {{"operator":"leaf","proposition_id":ID,"children":[]}} for required IDs only;
"and"/"or" nodes have proposition_id null and nonempty children; the leaves cover every required ID.
Optional propositions never appear in logic.
C11. material_dimensions entries and not_applicable keys are only these SemanticAttributes names:
{names(SemanticAttributes.model_fields)}. not_applicable values are nonempty reasons; relation is never
not applicable.
C12. For {names(sorted(CORE_DIMENSIONS))}, every material dimension and every non-null attribute, give a
known value or a not_applicable reason; otherwise the proposition stays unknown.
C13. attributes.relation uses only these values ({relations}); any other value makes the evidence
capability unknown. endpoint_type values counted as human clinical outcomes: {names(sorted(CLINICAL_ENDPOINTS))}.
comparison is "between" (between groups or arms) or "within" (change within one group). species is
"human" for human data.
C14. Each bound evidence description is compared with its proposition on the C12 dimensions except relation
and certainty; a proposition attribute that is null with a not_applicable reason is skipped. Each compared
pair is a case-insensitive exact string match: use identical strings for the same value and different
strings only for real differences; a real difference stays unresolved or unsupported unless a matching
product transfer or semantic_transfer bridge resolves it. An effect_direction difference does not count for
a binding with observation contradiction, nor for contradictory underlying evidence of a review. A null or
unknown value on either side of a
compared dimension leaves that binding unresolved. Treated as unknown: null, "", {names(unknown_values)}.
Write an inapplicable attribute as null plus a not_applicable reason; an unknown-like string such as
not_applicable is still compared.
Bindings, scopes and findings
C15. A binding's proposition_id is its owning proposition and its evidence_id exists. directness is one of
{names(get_args(Directness))}; only direct can establish support or contradiction. observation is one of
{names(get_args(Observation))}. observation support needs evidence role supporting; contradiction needs
role contradictory. A reported_verdict supported or contradicted needs at least one binding.
C16. Each required proposition lists search_scope_ids of forensic_record.search_scopes entries with
scope_type "reviewed_set" and nonempty reviewed_source_ids drawn from "input" and "context" that contain
the source of every evidence item used by its bindings, bridges and transfers, including the underlying
and identification evidence of their descriptions; a binding search_scope_id must exist and contain those
sources too. Never use documented_search: no external search was executed.
C17. For every binding with observation no_evidence_found on a required proposition add one
forensic_record.negative_assertions item with finding_id equal to the proposition_id, proposition equal to
the exact proposition_text and search_scope_id equal to that binding's search_scope_id. A negative
assertion always needs an existing finding with that finding_id.
C18. For each required proposition add one forensic_record.findings item with finding_id equal to the
proposition_id, proposition equal to the exact proposition_text, the same provenance_id, and
supporting_evidence_ids plus contrary_evidence_ids together equal to exactly the evidence IDs of its
bindings (contradiction evidence in contrary_evidence_ids). Findings exist only for proposition IDs.
Client output
C19. At least one client finding. parent_finding_id is an internal finding_id; provenance_id equals the
parent's; referenced_evidence_ids is a subset of the parent's supporting plus contrary IDs and, for each
direction present among the parent's material evidence (supporting versus any other role), includes at
least one material item of that direction, so an empty list fails when the parent has material evidence.
client_strength never exceeds the parent's allowed_summary_strength in this order (lowest first):
{names(SUMMARY_STRENGTH_ORDER)}.
C20. A client negative assertion uses the assertion_id of an internal negative assertion and client_scope
reviewed_set when that assertion has a reviewed_set search_scope_id, or source_local only when it lists
source_local_evidence_ids; never broader and never global_nonexistence. Scope names: {names(ASSERTION_SCOPES)}.
Transformations
C21. phase8.transformations holds exactly one item per (stage, target_id) and nothing else: for every
required proposition P the stages extraction, search_question and internal with target_id P.proposition_id;
for every client finding C the stage summary with target_id C.client_finding_id.
C22. from_proposition_ids is [P.proposition_id]; for summary it is [C.parent_finding_id].
C23. extraction: from_text equals P.original_span.text, to_text equals P.proposition_text and to_attributes
equals P.attributes.
C24. search_question, internal and summary: from_text equals P.proposition_text and from_attributes equals
P.attributes. search_question to_text equals P.search_question. internal to_text equals the finding's
proposition, plus a newline and its verdict_summary when that is nonempty. summary to_text equals
C.display_claim, plus a newline and C.client_explanation when that is nonempty. Add nothing else.
C25. Output audit of every transformation: an attribute change between from_attributes and to_attributes
(except a weaker certainty), a hedge word (may, might, could, possibly, suggest, suggests, könnte,
möglicherweise) present in from_text but missing from to_text, an asserted_state that differs from the
host-derived state of P (of the whole claim when asserts_whole_claim is true), or a whole-claim supported
for an unsupported claim is an output finding. Summary items need asserted_state; on other stages it is
optional and checked the same way when set. Keep to_attributes equal to from_attributes when the meaning
is unchanged.
Bridges, transfers and taxonomy
C26. product_transfers: binding_id is an existing binding; dimensions only {names(sorted(PRODUCT_DIMENSIONS))};
evidence IDs exist. Other attribute differences use a semantic_transfer bridge naming those attributes.
C27. bridges: conclusion and premise IDs are existing propositions; mechanism_to_outcome needs at least one
premise_proposition_id; a proposition's required_bridge_ids name bridges that conclude in it. A proposition
with a premise of relation mechanism needs a required mechanism_to_outcome bridge with that premise when its
own relation is in the clinical group, or is causal with species human and a clinical endpoint_type.
C28. phase8_taxonomy: proposition_ids and evidence_ids exist (each evidence ID with a description); every
listed evidence ID is bound to a listed proposition and every listed proposition binds a listed evidence
ID; trigger_proposition_id and trigger_evidence_id are listed and bound to each other; trigger_quote is a
character-exact substring of that proposition's original_span.text or of that evidence text; causal_claim
is true exactly when a listed proposition's relation is one of {names(sorted(CAUSAL_RELATIONS))}.
State bookkeeping
C29. Part of the host derivation that C25 compares with: a proposition with reported_verdict unknown is
unknown; a reported unsupported or contradicted that differs from the evidence-derived state becomes
unknown. The whole claim combines its logic tree: and is contradicted if any child is contradicted, else
unknown if any is unknown, else unsupported if any is unsupported, else supported; or is supported if any
child is supported, else unknown if any is unknown, else unsupported if any is unsupported, else
contradicted."""


_R2_REPLACEMENTS = (
    # (R1 text, R2 text). Each R1 segment must occur exactly once; see build_phase8_contract_r2.
    ("""AA-P8/1.0 deterministic host contract (live repair revision R1). The host checks your JSON
with exactly these rules; they make the instructions above precise. Any violation makes the analysis
technically incomplete, so copy values literally wherever a rule says equal.""",
     """AA-P8/1.1 output contract (revision r2). Responsibilities: you report your own scientific judgment
for every proposition (reported_verdict) and for the whole claim, based only on the supplied evidence.
The host separately derives an evidence state from the fields you represent and compares it with your
judgment; a difference is allowed and is never a format error. A difference that can change the whole-claim
result or a decisive summary statement goes to a mandatory review; any other difference stays visible as an
open, non-material conflict. Do not adjust your judgment to guess the host. This contract replaces the
AA-P8/1.0 references in the text above. The host checks the structure of your JSON with exactly these rules;
they make the instructions above precise. Any structural violation makes the analysis technically
incomplete, so copy values literally wherever a rule says equal."""),
    ("""known value or a not_applicable reason; otherwise the proposition stays unknown.""",
     """known value or a not_applicable reason; otherwise the host evidence state of the proposition stays
unknown."""),
    ("""comparison is "between" (between groups or arms) or "within" (change within one group). species is
"human" for human data.""",
     """comparison is "between" (between groups or arms) or "within" (change within one group); if the source
does not state the design or comparison, leave comparison null rather than guessing "within". species is
"human" for human data."""),
    ("""C23. extraction: from_text equals P.original_span.text, to_text equals P.proposition_text and to_attributes
equals P.attributes.""",
     """C23. extraction: from_text equals P.original_span.text, to_text equals P.proposition_text and to_attributes
equals P.attributes. from_attributes either equals P.attributes or is left completely empty (all null); the
host then uses P.attributes for the meaning audit and records that. Never fill it partially."""),
    ("""an asserted_state that differs from the
host-derived state of P (of the whole claim when asserts_whole_claim is true), or a whole-claim supported
for an unsupported claim is an output finding.""",
     """an asserted_state that differs from your own
judgment (P.reported_verdict; for asserts_whole_claim your whole-claim judgment per C29), or a whole-claim
supported while your own whole-claim judgment is not supported is an output finding."""),
    ("""State bookkeeping
C29. Part of the host derivation that C25 compares with: a proposition with reported_verdict unknown is
unknown; a reported unsupported or contradicted that differs from the evidence-derived state becomes
unknown. The whole claim combines its logic tree:""",
     """Whole-claim judgment
C29. Your whole-claim judgment combines your reported_verdict values over the logic tree:"""),
)


def build_phase8_contract_r2() -> str:
    """AA-P8/1.1 contract text (revision r2): R1 rules with separated model/host responsibilities.

    Changes against R1 are exactly the listed replacements: own judgment instead of predicting the
    host state (C25, C29), the extraction copy rule (C23) and a missing comparison (C13).
    """
    text = build_phase8_contract_r1()
    for old, new in _R2_REPLACEMENTS:
        if text.count(old) != 1:
            raise RuntimeError("R1 contract text changed; the r2 derivation must be revised explicitly")
        text = text.replace(old, new)
    return text


def unavailable(status: str, reason: str, original_label: str | None = None) -> dict:
    return {
        "contract_version": "AA-P8/1.3",
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
        # An output with a second analysis (draft and correction) is ambiguous, never complete.
        complete = complete and diagnostics.ok and not (
            diagnostics.truncation_suspected or diagnostics.repaired or diagnostics.multiple_objects
        )
    else:
        # Without the raw text no parse can be re-checked (truncation, repair, a second analysis),
        # so a cached parse is never a complete analysis (P1-F2, also for finish_reason "length").
        complete = False
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
            # AA-P8/1.1: a conflict-derived unknown must not read like an agreed unknown.
            conflict = (f" (open model/host conflict: model {proposition.get('reported_verdict')}, "
                        f"host {proposition.get('host_state')})" if proposition.get("model_host_conflict") else "")
            lines.append(
                f"- `{proposition.get('proposition_id', '?')}`: "
                f"{proposition.get('derived_state', proposition.get('state', 'unknown'))}{conflict}"
            )
    lines.append(LIMITATION)
    return "\n\n".join(lines)
