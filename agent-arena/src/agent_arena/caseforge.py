"""Gen 3 Caseforge — targeted case candidate generation for agent-arena v0.6.8.

Generates draft case candidates in response to known data gaps, calibration
signals, and explicit requests. Every candidate is marked pending_human_review.
Nothing is finalized or integrated automatically.

Steering axes per candidate:
- generation_mode: why the candidate was created
- category_gap: which category needs coverage
- shape_gap: which sub-shape is targeted
- borderline_need: clear or borderline
- model_confusion_target: which model confusion to probe

Data sources: CalibrationReport, explicit CaseforgeRequest, or shape templates.
"""

from __future__ import annotations

import hashlib
import textwrap
from datetime import datetime, timezone

from agent_arena.schemas import (
    CalibrationProposal,
    CalibrationReport,
    CaseCandidate,
    CaseforgeReport,
    ProposedEvidenceSpan,
    ProposedFinding,
)


# ---------------------------------------------------------------------------
# Shape template library — realistic, plausible input texts
# ---------------------------------------------------------------------------

# Each template: (input_text, gold_label, trap_type, findings, evidence_spans,
#                  alt_reading, summary)

_SHAPE_TEMPLATES: dict[str, dict[str, list[dict]]] = {
    # --- Study Forensics ---
    "solid": {
        "clear": [
            {
                "input_text": textwrap.dedent("""\
                    A randomized controlled trial enrolled 1,200 adults with
                    moderate hypertension across 14 medical centers. Participants
                    were randomly assigned to receive either a new angiotensin
                    receptor blocker or standard-of-care medication for 18 months.
                    The primary endpoint — reduction in systolic blood pressure —
                    showed a statistically significant 8 mmHg advantage for the
                    new drug (p < 0.001). The authors noted that the study was
                    limited to adults without comorbidities, that the follow-up
                    period was relatively short, and that long-term cardiovascular
                    outcomes were not assessed. They concluded that the new
                    medication is a promising addition to antihypertensive therapy
                    but that longer-term studies are needed before changing
                    clinical guidelines."""),
                "trap_type": "none_solid_methodology",
                "gold_label": "solid",
                "summary": "Well-designed RCT with clear limitations acknowledged. No overclaiming.",
                "findings": [
                    {"finding": "evidence_matches_claim", "severity": "minor", "confidence": "high"},
                    {"finding": "cautious_scope_control", "severity": "minor", "confidence": "high"},
                ],
                "evidence_spans": [
                    {"span": "randomized controlled trial enrolled 1,200 adults",
                     "why_it_matters": "Strong study design supports the conclusions drawn.",
                     "supports_finding": "evidence_matches_claim"},
                    {"span": "limited to adults without comorbidities",
                     "why_it_matters": "Authors appropriately scope their claims.",
                     "supports_finding": "cautious_scope_control"},
                ],
                "alt_reading": "Could argue the 18-month follow-up is too short for definitive conclusions, but the authors acknowledge this.",
            },
        ],
        "borderline": [
            {
                "input_text": textwrap.dedent("""\
                    A well-powered cohort study of 45,000 nurses found that those
                    who consumed more than three servings of whole grains daily
                    had a 22% lower incidence of type 2 diabetes over 12 years
                    compared to those eating less than one serving. The researchers
                    adjusted for BMI, physical activity, smoking, and family
                    history. They noted that residual confounding cannot be
                    fully excluded in observational research. The authors
                    concluded that their findings provide strong evidence that
                    whole grains protect against diabetes development."""),
                "trap_type": "observational_with_causal_claim",
                "gold_label": "solid",
                "summary": "Large cohort with appropriate adjustments. The word 'protect' edges toward causal, but overall reporting is careful.",
                "findings": [
                    {"finding": "evidence_matches_claim", "severity": "minor", "confidence": "medium"},
                    {"finding": "cautious_scope_control", "severity": "minor", "confidence": "medium"},
                ],
                "evidence_spans": [
                    {"span": "strong evidence that whole grains protect against diabetes",
                     "why_it_matters": "Uses 'protect' which implies causation from observational data, but overall framing is careful.",
                     "supports_finding": "evidence_matches_claim"},
                ],
                "alt_reading": "The use of 'protect' could be read as overclaiming causation from observational data. Borderline between solid and correlation_vs_causation.",
            },
        ],
    },
    "overclaim": {
        "clear": [
            {
                "input_text": textwrap.dedent("""\
                    A dietary supplement company sponsored a 6-week trial with
                    40 participants testing their proprietary turmeric extract.
                    The study measured inflammatory markers in blood samples.
                    Results showed a modest 12% reduction in CRP levels in the
                    supplement group compared to placebo. The company's press
                    release states: "Groundbreaking clinical evidence proves our
                    turmeric formula eliminates chronic inflammation and prevents
                    heart disease, cancer, and Alzheimer's." The actual paper
                    notes the small sample size, short duration, and lack of
                    clinical endpoints as important limitations."""),
                "trap_type": "press_release_inflation",
                "gold_label": "overclaim",
                "summary": "Modest biomarker result inflated into sweeping disease-prevention claims by sponsor press release.",
                "findings": [
                    {"finding": "conclusion_exceeds_results", "severity": "major", "confidence": "high"},
                    {"finding": "unsupported_generalization", "severity": "major", "confidence": "high"},
                ],
                "evidence_spans": [
                    {"span": "eliminates chronic inflammation and prevents heart disease, cancer, and Alzheimer's",
                     "why_it_matters": "Sweeping prevention claims from a 6-week biomarker study with 40 participants.",
                     "supports_finding": "conclusion_exceeds_results"},
                    {"span": "40 participants",
                     "why_it_matters": "Tiny sample extrapolated to universal disease prevention.",
                     "supports_finding": "unsupported_generalization"},
                ],
                "alt_reading": "None reasonable. The gap between evidence and claims is extreme.",
            },
        ],
        "borderline": [
            {
                "input_text": textwrap.dedent("""\
                    A university research team conducted a 200-person RCT of a
                    mindfulness-based stress reduction program for chronic pain
                    patients. After 8 weeks, participants in the mindfulness
                    group reported 30% lower pain scores on a visual analog scale
                    compared to the control group. The lead researcher told media:
                    "This shows that mindfulness can be a viable alternative to
                    opioid medications for managing chronic pain." The paper
                    itself notes limitations including reliance on self-reported
                    outcomes, lack of active control, and the impossibility of
                    blinding participants to the intervention."""),
                "trap_type": "media_quote_overreach",
                "gold_label": "overclaim",
                "summary": "Reasonable RCT, but media quote suggests mindfulness replaces opioids — beyond what an 8-week self-report study supports.",
                "findings": [
                    {"finding": "conclusion_exceeds_results", "severity": "moderate", "confidence": "medium"},
                ],
                "evidence_spans": [
                    {"span": "viable alternative to opioid medications",
                     "why_it_matters": "Replaceability claim not supported by the study design or duration.",
                     "supports_finding": "conclusion_exceeds_results"},
                ],
                "alt_reading": "The researcher may have meant 'part of pain management' rather than literal replacement. The study itself is sound; the overclaim is in the media framing.",
            },
        ],
    },
    "correlation_vs_causation": {
        "clear": [
            {
                "input_text": textwrap.dedent("""\
                    A large cross-sectional survey of 85,000 adults found that
                    those who reported drinking three or more cups of coffee daily
                    had 40% lower rates of depression diagnoses compared to
                    non-coffee drinkers. The researchers controlled for age,
                    income, exercise, and alcohol use. A university press release
                    headlined: "Daily coffee habit slashes depression risk by
                    nearly half." The researchers acknowledged the observational
                    design but stated their findings "strongly support the
                    protective role of caffeine against depressive disorders."
                    No interventional evidence was presented."""),
                "trap_type": "observational_sold_as_protective",
                "gold_label": "correlation_vs_causation",
                "summary": "Cross-sectional survey finding framed as evidence for a protective causal role. Classic reverse causation risk (depression → reduced motivation to drink coffee).",
                "findings": [
                    {"finding": "correlation_as_causation", "severity": "major", "confidence": "high"},
                    {"finding": "unsupported_generalization", "severity": "moderate", "confidence": "medium"},
                ],
                "evidence_spans": [
                    {"span": "strongly support the protective role of caffeine",
                     "why_it_matters": "Causal language ('protective role') applied to cross-sectional observational data.",
                     "supports_finding": "correlation_as_causation"},
                    {"span": "slashes depression risk by nearly half",
                     "why_it_matters": "Interventional framing ('slashes') for a survey finding.",
                     "supports_finding": "correlation_as_causation"},
                ],
                "alt_reading": "One could argue 'support' is hedged language, but combined with 'protective role' and the press headline, the causal framing is clear.",
            },
        ],
        "borderline": [
            {
                "input_text": textwrap.dedent("""\
                    A 10-year prospective cohort study following 120,000
                    participants found that higher levels of social engagement
                    were associated with 35% lower risk of developing dementia.
                    The study adjusted for education, income, baseline cognitive
                    function, physical activity, and depression. The authors
                    wrote: "Our findings suggest that maintaining social
                    connections may help preserve cognitive function in aging."
                    They noted the observational design and the possibility
                    that early cognitive decline could reduce social activity."""),
                "trap_type": "careful_hedging_observational",
                "gold_label": "correlation_vs_causation",
                "summary": "Well-designed prospective cohort with careful hedging. The observational design still limits causal inference despite appropriate language.",
                "findings": [
                    {"finding": "correlation_as_causation", "severity": "moderate", "confidence": "medium"},
                ],
                "evidence_spans": [
                    {"span": "may help preserve cognitive function",
                     "why_it_matters": "Hedged but still implies directional causation from observational data.",
                     "supports_finding": "correlation_as_causation"},
                ],
                "alt_reading": "The authors use appropriate hedging ('may help', 'suggest') and acknowledge reverse causation. This could be read as solid observational reporting rather than a correlation-causation error.",
            },
        ],
    },
    "mechanism_vs_evidence": {
        "clear": [
            {
                "input_text": textwrap.dedent("""\
                    Scientists have identified a protein called SIRT6 that
                    dramatically extends lifespan in laboratory mice when
                    overexpressed. Mice with enhanced SIRT6 activity lived 30%
                    longer than controls and showed reduced age-related
                    metabolic decline. The research team announced that their
                    findings "open the door to anti-aging therapeutics that could
                    add decades to human lifespan" and that they are exploring
                    small-molecule SIRT6 activators for eventual clinical use.
                    No human studies have been conducted."""),
                "trap_type": "animal_to_human_overreach",
                "gold_label": "mechanism_vs_evidence",
                "summary": "Mouse lifespan extension extrapolated to human anti-aging therapeutics without any human evidence.",
                "findings": [
                    {"finding": "mechanism_not_demonstrated", "severity": "major", "confidence": "high"},
                    {"finding": "conclusion_exceeds_results", "severity": "moderate", "confidence": "high"},
                ],
                "evidence_spans": [
                    {"span": "add decades to human lifespan",
                     "why_it_matters": "Leaps from mouse overexpression to human lifespan decades.",
                     "supports_finding": "mechanism_not_demonstrated"},
                    {"span": "No human studies have been conducted",
                     "why_it_matters": "Explicitly acknowledges the absence of human evidence.",
                     "supports_finding": "mechanism_not_demonstrated"},
                ],
                "alt_reading": "Could be read as aspirational research communication, but the claim of 'decades' from mouse data is a clear mechanism-evidence gap.",
            },
        ],
        "borderline": [
            {
                "input_text": textwrap.dedent("""\
                    A phase I clinical trial tested a novel gene therapy for
                    age-related macular degeneration in 15 patients. The therapy,
                    which had shown remarkable results in primate models
                    (restoring 80% of lost vision), achieved modest improvements
                    in visual acuity in 8 of 15 patients after 6 months. The
                    researchers described the results as "encouraging preliminary
                    evidence that gene therapy can reverse vision loss" and noted
                    that a larger phase II trial is planned. They cautioned that
                    the human results, while positive, are far more modest than
                    the primate findings."""),
                "trap_type": "preclinical_to_clinical_modest",
                "gold_label": "mechanism_vs_evidence",
                "summary": "Gene therapy with strong primate results but modest human Phase I data. Researchers appropriately hedge but the overall narrative still bridges the gap optimistically.",
                "findings": [
                    {"finding": "mechanism_not_demonstrated", "severity": "moderate", "confidence": "medium"},
                ],
                "evidence_spans": [
                    {"span": "can reverse vision loss",
                     "why_it_matters": "Claims reversal capability from a small Phase I with modest results.",
                     "supports_finding": "mechanism_not_demonstrated"},
                ],
                "alt_reading": "The researchers do have some human evidence (8/15 improved) and acknowledge the gap. This could reasonably be classified as 'overclaim' or even 'solid' given the appropriate hedging.",
            },
        ],
    },
}


# ---------------------------------------------------------------------------
# Candidate ID generation
# ---------------------------------------------------------------------------

def _candidate_id(family: str, shape: str, index: int) -> str:
    """Generate a deterministic candidate ID."""
    seed = f"{family}:{shape}:{index}:{datetime.now(timezone.utc).isoformat()[:13]}"
    h = hashlib.md5(seed.encode()).hexdigest()[:8]
    return f"cf_{family[:4]}_{h}"


# ---------------------------------------------------------------------------
# A. Generate from explicit request
# ---------------------------------------------------------------------------

def generate_from_request(
    family: str,
    case_type: str = "clear",
    count: int = 1,
    shape: str = "",
    model_confusion_target: str = "",
) -> list[CaseCandidate]:
    """Generate case candidates from an explicit request.

    Args:
        family: Target family (solid, overclaim, correlation_vs_causation, mechanism_vs_evidence)
        case_type: "clear" or "borderline"
        count: Number of candidates to generate
        shape: Optional sub-shape (e.g., animal_to_human, press_release_inflation)
        model_confusion_target: Optional model confusion to probe
    """
    templates = _SHAPE_TEMPLATES.get(family, {}).get(case_type, [])
    if not templates:
        # Fall back to clear if borderline not available
        templates = _SHAPE_TEMPLATES.get(family, {}).get("clear", [])

    candidates: list[CaseCandidate] = []
    for i in range(min(count, len(templates))):
        t = templates[i % len(templates)]
        cid = _candidate_id(family, shape or case_type, i)

        candidates.append(CaseCandidate(
            candidate_id=cid,
            review_status="pending_human_review",
            generation_mode="explicit_request",
            category_gap=family,
            shape_gap=shape or t.get("trap_type", ""),
            borderline_need=case_type,
            model_confusion_target=model_confusion_target,
            target_family=family,
            target_shape=shape or t.get("trap_type", ""),
            domain="study_forensics",
            difficulty="medium" if case_type == "clear" else "hard",
            trap_type=t.get("trap_type", ""),
            ambiguity_level="low" if case_type == "clear" else "medium",
            title=f"Caseforge Draft: {family} ({case_type})",
            input_text=t["input_text"].strip(),
            proposed_gold_label=t["gold_label"],
            proposed_gold_confidence="high" if case_type == "clear" else "medium",
            proposed_gold_case_type=case_type,
            proposed_gold_summary=t.get("summary", ""),
            proposed_gold_justification=t.get("summary", ""),
            proposed_gold_alternative_reading=t.get("alt_reading", ""),
            proposed_expected_findings=[
                ProposedFinding(**f) for f in t.get("findings", [])
            ],
            proposed_evidence_spans=[
                ProposedEvidenceSpan(**s) for s in t.get("evidence_spans", [])
            ],
            why_this_candidate_exists=f"Explicit request for {count} {case_type} {family} case(s)",
            which_gap_it_addresses=f"category={family}, type={case_type}",
            why_diagnostically_useful=(
                f"Tests model's ability to identify {family} pattern"
                + (f" in a borderline context" if case_type == "borderline" else "")
            ),
            curator_notes=(
                f"CASEFORGE DRAFT — pending human review. "
                f"Generated from template, not a finalized case."
            ),
        ))

    return candidates


# ---------------------------------------------------------------------------
# B. Generate from calibration data gaps
# ---------------------------------------------------------------------------

def generate_from_calibration(
    calibration_report: CalibrationReport,
    max_per_gap: int = 1,
) -> list[CaseCandidate]:
    """Generate case candidates from CalibrationReport data gap signals.

    Reads data_gap_candidates and category_refinement_candidates to determine
    what types of cases are needed.
    """
    candidates: list[CaseCandidate] = []

    # Process data gap proposals
    for proposal in calibration_report.data_gap_candidates:
        family = proposal.target
        if family not in _SHAPE_TEMPLATES:
            continue

        # Determine if we need clear or borderline
        need_borderline = "borderline" in proposal.reason.lower()
        case_type = "borderline" if need_borderline else "clear"

        new_candidates = generate_from_request(
            family=family,
            case_type=case_type,
            count=max_per_gap,
        )

        # Override metadata for data-gap context
        for c in new_candidates:
            c.generation_mode = "data_gap"
            c.why_this_candidate_exists = (
                f"Data gap signal: {proposal.reason}"
            )
            c.which_gap_it_addresses = (
                f"Calibrate proposal: {proposal.target} ({proposal.target_kind})"
            )

        candidates.extend(new_candidates)

    # Process model confusion proposals → confusion probes
    for proposal in calibration_report.model_confusion_candidates:
        if proposal.target_kind != "model":
            continue

        # Extract gold→detected confusion from the reason
        reason = proposal.reason.lower()
        gold_family = ""
        detected_as = ""
        for fam in _SHAPE_TEMPLATES:
            if f"'{fam}'" in reason:
                if not gold_family:
                    gold_family = fam
                elif not detected_as:
                    detected_as = fam

        if gold_family and gold_family in _SHAPE_TEMPLATES:
            new_candidates = generate_from_request(
                family=gold_family,
                case_type="clear",
                count=max_per_gap,
                model_confusion_target=proposal.reason[:100],
            )
            for c in new_candidates:
                c.generation_mode = "confusion_probe"
                c.model_confusion_target = proposal.reason[:100]
                c.why_this_candidate_exists = (
                    f"Model confusion signal: {proposal.reason}"
                )
                c.which_gap_it_addresses = (
                    f"Tests whether confusion {gold_family}→{detected_as} "
                    f"persists on new case material"
                )
                c.why_diagnostically_useful = (
                    f"Probes stable confusion pattern for {proposal.target}"
                )

            candidates.extend(new_candidates)

    # Process category refinement proposals → borderline probes
    for proposal in calibration_report.category_refinement_candidates:
        family = proposal.target
        if family not in _SHAPE_TEMPLATES:
            continue

        # Unstable categories need clear cases to anchor the definition
        if "scatter" in proposal.reason.lower() or "correctness" in proposal.reason.lower():
            new_candidates = generate_from_request(
                family=family,
                case_type="clear",
                count=max_per_gap,
            )
            for c in new_candidates:
                c.generation_mode = "calibration_signal"
                c.why_this_candidate_exists = (
                    f"Category instability: {proposal.reason}"
                )
                c.which_gap_it_addresses = (
                    f"Anchoring case for unstable category '{family}'"
                )

            candidates.extend(new_candidates)

    return candidates


# ---------------------------------------------------------------------------
# C. Generate borderline probes
# ---------------------------------------------------------------------------

def generate_borderline_probes(
    families: list[str] | None = None,
    count_per_family: int = 1,
) -> list[CaseCandidate]:
    """Generate borderline case candidates for specified families.

    Borderline cases stress-test category boundaries and help identify
    where the gold label distinction is genuinely difficult.
    """
    if families is None:
        families = list(_SHAPE_TEMPLATES.keys())

    candidates: list[CaseCandidate] = []
    for family in families:
        if family not in _SHAPE_TEMPLATES:
            continue

        new_candidates = generate_from_request(
            family=family,
            case_type="borderline",
            count=count_per_family,
        )
        for c in new_candidates:
            c.generation_mode = "borderline_probe"
            c.why_this_candidate_exists = (
                f"Borderline probe for '{family}' category boundary"
            )
            c.why_diagnostically_useful = (
                f"Tests whether models handle ambiguous {family} cases correctly"
            )

        candidates.extend(new_candidates)

    return candidates


# ---------------------------------------------------------------------------
# Main: forge_cases
# ---------------------------------------------------------------------------

def forge_cases(
    family: str | None = None,
    case_type: str = "clear",
    count: int = 1,
    shape: str = "",
    calibration_report: CalibrationReport | None = None,
    borderline_mode: bool = False,
    model_confusion_target: str = "",
) -> CaseforgeReport:
    """Main entry point for case generation.

    Modes:
    1. Explicit request: family + case_type + count
    2. Calibration-driven: calibration_report provided
    3. Borderline probes: borderline_mode=True

    All modes can be combined. All candidates are marked pending_human_review.
    """
    candidates: list[CaseCandidate] = []
    gaps_addressed: list[str] = []

    # Mode 1: Explicit request
    if family:
        new = generate_from_request(
            family=family,
            case_type=case_type,
            count=count,
            shape=shape,
            model_confusion_target=model_confusion_target,
        )
        candidates.extend(new)
        gaps_addressed.append(f"explicit:{family}/{case_type}×{count}")

    # Mode 2: Calibration-driven
    if calibration_report:
        new = generate_from_calibration(calibration_report)
        candidates.extend(new)
        n_gaps = (
            len(calibration_report.data_gap_candidates)
            + len(calibration_report.model_confusion_candidates)
            + len(calibration_report.category_refinement_candidates)
        )
        gaps_addressed.append(f"calibration:{n_gaps} signals")

    # Mode 3: Borderline probes
    if borderline_mode:
        families = [family] if family else None
        new = generate_borderline_probes(families=families)
        candidates.extend(new)
        gaps_addressed.append("borderline_probes")

    # Build review summary
    by_family = {}
    by_mode = {}
    for c in candidates:
        by_family[c.target_family] = by_family.get(c.target_family, 0) + 1
        by_mode[c.generation_mode] = by_mode.get(c.generation_mode, 0) + 1

    summary_parts = [
        f"{len(candidates)} candidate(s) generated.",
        f"Families: {dict(by_family)}." if by_family else "",
        f"Modes: {dict(by_mode)}." if by_mode else "",
        "All candidates require human review before integration.",
    ]

    return CaseforgeReport(
        generated_at=datetime.now(timezone.utc).isoformat(),
        n_candidates=len(candidates),
        candidates=candidates,
        gaps_addressed=gaps_addressed,
        review_summary=" ".join(p for p in summary_parts if p),
    )


# ---------------------------------------------------------------------------
# Export: candidate → YAML draft
# ---------------------------------------------------------------------------

def candidate_to_yaml_draft(candidate: CaseCandidate) -> str:
    """Render a CaseCandidate as a YAML-formatted draft for human review.

    NOT a final task YAML — marked clearly as a draft.
    """
    findings_yaml = ""
    for f in candidate.proposed_expected_findings:
        findings_yaml += f"  - finding: {f.finding}\n"
        findings_yaml += f"    severity: {f.severity}\n"
        findings_yaml += f"    confidence: {f.confidence}\n"

    spans_yaml = ""
    for s in candidate.proposed_evidence_spans:
        spans_yaml += f'  - span: "{s.span}"\n'
        spans_yaml += f'    why_it_matters: "{s.why_it_matters}"\n'
        spans_yaml += f'    supports_finding: {s.supports_finding}\n'

    return f"""\
# ============================================================================
# CASEFORGE DRAFT — NOT A FINALIZED CASE
# Candidate ID: {candidate.candidate_id}
# Review Status: {candidate.review_status}
# Generation Mode: {candidate.generation_mode}
# Gap Addressed: {candidate.which_gap_it_addresses}
# ============================================================================

id: {candidate.candidate_id}
title: "{candidate.title}"
domain: {candidate.domain}
difficulty: {candidate.difficulty}
task_type: study_forensics
task_family: {candidate.target_family}
trap_type: {candidate.trap_type}
ambiguity_level: {candidate.ambiguity_level}

prompt: |
{textwrap.indent(candidate.input_text, '  ')}

expected_answer: "{candidate.proposed_gold_label}"

# --- PROPOSED Gold Layer (requires human review) ---
gold_label: {candidate.proposed_gold_label}
gold_confidence: {candidate.proposed_gold_confidence}
gold_case_type: {candidate.proposed_gold_case_type}
gold_summary: |
  {candidate.proposed_gold_summary}
gold_justification: |
  {candidate.proposed_gold_justification}
gold_alternative_reading: |
  {candidate.proposed_gold_alternative_reading}
curator_notes: |
  {candidate.curator_notes}

# --- PROPOSED Expected Findings ---
expected_findings:
{findings_yaml if findings_yaml else '  []'}
# --- PROPOSED Evidence Spans ---
gold_evidence_spans:
{spans_yaml if spans_yaml else '  []'}
# --- Caseforge Metadata ---
# generation_mode: {candidate.generation_mode}
# category_gap: {candidate.category_gap}
# shape_gap: {candidate.shape_gap}
# borderline_need: {candidate.borderline_need}
# model_confusion_target: {candidate.model_confusion_target}
# why_this_candidate_exists: {candidate.why_this_candidate_exists}
# why_diagnostically_useful: {candidate.why_diagnostically_useful}

evaluation:
  method: auto
  answer_match: contains
"""


# ---------------------------------------------------------------------------
# Report rendering — Markdown
# ---------------------------------------------------------------------------

def render_caseforge_report(report: CaseforgeReport) -> str:
    """Render CaseforgeReport as Markdown."""
    lines: list[str] = []

    lines.append("# Agent Arena — Gen 3 Caseforge Report")
    lines.append("")
    lines.append(f"**Generated:** {report.generated_at}  ")
    lines.append(f"**Candidates:** {report.n_candidates}  ")
    lines.append(f"**Gaps addressed:** {', '.join(report.gaps_addressed)}")
    lines.append("")

    if report.n_candidates == 0:
        lines.append("_No candidates generated._")
        return "\n".join(lines)

    lines.append(f"**Review summary:** {report.review_summary}")
    lines.append("")

    # Summary table
    lines.append("## Candidate Summary")
    lines.append("")
    lines.append("| ID | Family | Type | Mode | Confusion Target |")
    lines.append("|----|--------|------|------|------------------|")
    for c in report.candidates:
        confusion = c.model_confusion_target[:40] if c.model_confusion_target else ""
        lines.append(
            f"| {c.candidate_id} | {c.target_family} | "
            f"{c.proposed_gold_case_type} | {c.generation_mode} | "
            f"{confusion} |"
        )
    lines.append("")

    # Individual candidates
    lines.append("## Candidate Details")
    lines.append("")
    for i, c in enumerate(report.candidates, 1):
        lines.append(f"### {i}. {c.candidate_id}")
        lines.append("")
        lines.append(f"**Family:** {c.target_family} | "
                     f"**Shape:** {c.target_shape} | "
                     f"**Type:** {c.proposed_gold_case_type}")
        lines.append(f"**Mode:** {c.generation_mode} | "
                     f"**Review:** {c.review_status}")
        lines.append("")
        lines.append(f"**Why:** {c.why_this_candidate_exists}")
        lines.append(f"**Gap:** {c.which_gap_it_addresses}")
        if c.model_confusion_target:
            lines.append(f"**Confusion target:** {c.model_confusion_target}")
        lines.append("")
        lines.append(f"**Proposed label:** `{c.proposed_gold_label}` "
                     f"(confidence: {c.proposed_gold_confidence})")
        lines.append(f"**Alternative reading:** {c.proposed_gold_alternative_reading}")
        lines.append("")
        # Truncated input preview
        preview = c.input_text[:200].replace("\n", " ")
        lines.append(f"> {preview}...")
        lines.append("")
        lines.append("---")
        lines.append("")

    # Footer
    lines.append(
        "*Gen 3 Caseforge — draft candidates only. All candidates require "
        "human review before integration. No gold labels are finalized.*"
    )

    return "\n".join(lines)
