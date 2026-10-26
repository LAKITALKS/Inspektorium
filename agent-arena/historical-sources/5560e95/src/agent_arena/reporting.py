"""Report Engine v1 — professional, client-facing audit reports.

Transforms Agent Arena run records into structured, readable reports
with an executive layer for non-technical readers and a technical
appendix for detailed review.

Output formats: Markdown, HTML, PDF (via weasyprint if available).
"""

from __future__ import annotations

import html as html_module
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agent_arena.confidence_validity import confidence_value_if_valid
from agent_arena.phase8_pipeline import phase8_view, render_phase8
from agent_arena.schemas import TaskType
from agent_arena.schemas import (
    DIAGNOSTIC_WEIGHTS,
    EvaluatedResult,
    EvidenceRole,
    FailureInstance,
    RunRecord,
)


# ---------------------------------------------------------------------------
# Category labels — human-readable translations
# ---------------------------------------------------------------------------

CATEGORY_LABELS: dict[str, str] = {
    "solid": "Well-supported — no significant issues found",
    "overclaim": "Overclaim — conclusions exceed the evidence",
    "mechanism_vs_evidence": "Evidence-tier mismatch — claims bridge across evidence gaps",
    "correlation_vs_causation": "Correlation treated as causation",
    "wrong_answer": "Incorrect answer",
    "arithmetic_error": "Arithmetic error",
    "logic_error": "Logic error",
    "missing_key_step": "Missing key reasoning step",
    "unjustified_leap": "Unjustified logical leap",
    "unsupported_conclusion": "Conclusion not supported by evidence",
    "claim_drift": "Claim drifts from evidence",
    "overcompressed_reasoning": "Reasoning too compressed to verify",
    "missed_key_insight": "Missed a key insight",
    "superficial_treatment": "Superficial treatment of the problem",
    "pattern_matching": "Pattern matching without deeper analysis",
    "mechanism_gap": "Missing causal mechanism",
    "shallow_pattern_match": "Shallow pattern matching",
    "self_contradiction": "Self-contradiction detected",
    "confidence_mismatch": "Confidence doesn't match evidence quality",
    "step_answer_mismatch": "Reasoning steps contradict the answer",
    "decorative_self_check": "Self-check is decorative, not substantive",
    "overclaiming": "Claims exceed what evidence supports",
    "verbal_numeric_contradiction": "Verbal claims contradict numeric data",
    "local_fact_reversal": "Facts reversed within the response",
    "intermediate_numeric_error": "Intermediate calculation error",
    "right_answer_wrong_reasoning": "Correct answer, but reasoning is flawed",
    "accidental_correctness": "Correct answer appears accidental",
    "overconfident_forecast": "Overconfident forecast",
    "base_rate_omission": "Base rate not considered",
    "rule_misread": "Rule or condition misread",
    "narrative_overreach": "Narrative exceeds evidence",
    "false_edge_detection": "False edge detected",
}

SEVERITY_ORDER = ["critical", "major", "moderate", "minor", "stylistic"]

STATUS_SYMBOLS: dict[str, str] = {
    "critical": "🔴",
    "major": "🟠",
    "moderate": "🟡",
    "minor": "🔵",
    "stylistic": "⚪",
    "pass": "✅",
    "fail": "❌",
    "warning": "⚠️",
}


def _label(code: str) -> str:
    return CATEGORY_LABELS.get(code, code.replace("_", " ").title())


def _severity_icon(sev: str) -> str:
    return STATUS_SYMBOLS.get(sev, "")


def _agent_name(r: EvaluatedResult) -> str:
    return r.agent_result.provider


def _agent_full(r: EvaluatedResult) -> str:
    return f"{r.agent_result.provider} ({r.agent_result.model})"


def _best_result(results: list[EvaluatedResult]) -> EvaluatedResult | None:
    if not results:
        return None
    return max(results, key=lambda r: r.scores.total)


def _overall_status(results: list[EvaluatedResult], phase9: dict | None = None) -> tuple[str, str]:
    if not results:
        return "unknown", "No results available"
    if phase9 is not None and (phase9.get("route") != "AUTO_RESOLVABLE"
                              or phase9.get("history_validation") == "invalid" or phase9.get("mandatory")):
        return "unknown", "Phase-9 case review is unresolved or its history is invalid"

    best = _best_result(results)
    if not best:
        return "unknown", "No results available"

    score = best.scores.total

    critical_failures = []
    for r in results:
        for f in r.failures:
            if f.severity == "critical":
                critical_failures.append(f)

    if critical_failures:
        return "critical", "Critical issues found — review required before use"
    forensic = [r for r in results if r.agent_result.phase8 or r.study_forensics.get("is_study_forensics")]
    if forensic:
        if any(r.agent_result.phase9.get("route") != "AUTO_RESOLVABLE" for r in forensic):
            return "unknown", "Phase-9 mandatory review is unresolved or not executed"
        assessments = [phase8_view(r.agent_result.phase8) for r in forensic]
        if any(a["technical_status"] != "completed" or a["composite_state"] == "unknown"
               for a in assessments):
            return "unknown", "Phase-8 support is UNKNOWN or has not been completely assessed"
        if any(a.get("taxonomy", {}).get("technical_status") != "completed"
               or a.get("derived_label") is None for a in assessments):
            return "unknown", "Phase-8 classification is UNKNOWN or has not been completely assessed"
        if any(a["composite_state"] != "supported" for a in assessments):
            return "caution", "The claim is not supported as a whole; see the component assessments"
    if score >= 75:
        return "good", "Analysis appears sound — minor issues only"
    if score >= 50:
        return "caution", "Notable issues found — review recommended"
    return "poor", "Significant issues found — substantial revision needed"


def _status_indicator(status: str) -> str:
    indicators = {
        "critical": "🔴 CRITICAL",
        "good": "🟢 PASS",
        "caution": "🟡 CAUTION",
        "poor": "🔴 ISSUES",
        "unknown": "⚪ UNKNOWN",
    }
    return indicators.get(status, status.upper())


# ---------------------------------------------------------------------------
# Section builders — Markdown
# ---------------------------------------------------------------------------

def _section_executive_summary(record: RunRecord) -> str:
    task = record.task
    results = record.results
    best = _best_result(results)
    status, status_text = _overall_status(results, record.metadata.get("phase9"))

    lines = [
        "# Audit Report",
        "",
        f"**Report generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}  ",
        f"**Run ID:** `{record.run_id}`  ",
        f"**Audit timestamp:** {record.timestamp[:19].replace('T', ' ')} UTC  ",
    ]

    if task.title:
        lines.append(f"**Subject:** {task.title}  ")
    if task.domain:
        lines.append(f"**Domain:** {task.domain}  ")
    if task.task_family:
        lines.append(f"**Category:** {_label(task.task_family)}  ")

    lines.extend([
        "",
        "---",
        "",
        "## 1. Executive Summary",
        "",
        f"### Overall Assessment: {_status_indicator(status)}",
        "",
        f"> {status_text}",
        "",
    ])

    if best:
        lines.append(f"**Overall score:** {best.scores.total:.0f} / 100  ")

    agents = [_agent_name(r) for r in results]
    if len(agents) == 1:
        lines.append(f"**Analyzed by:** {agents[0]}  ")
    else:
        lines.append(f"**Models tested:** {', '.join(agents)}  ")

    # Study forensics classification
    sf_results = [r for r in results if r.study_forensics and r.study_forensics.get("is_study_forensics")]
    if sf_results:
        labels = set()
        for r in sf_results:
            detected = r.study_forensics.get("detected_label", "")
            if detected:
                labels.add(detected)
        if labels:
            label_strs = [f"`{label}`" for label in sorted(labels)]
            lines.append(f"**Original model classification:** {', '.join(label_strs)}  ")
        for result in sf_results:
            lines.append(render_phase8(result.agent_result.phase8))

    # Key findings summary
    top_findings = _extract_top_findings(results, max_count=5)
    if top_findings:
        lines.extend(["", "### Key Findings", ""])
        for i, (sev, cat, desc) in enumerate(top_findings, 1):
            icon = _severity_icon(sev)
            lines.append(f"{i}. {icon} **{_label(cat)}** — {desc}")

    # Quick recommendation
    recommendations = _extract_recommendations(results, status)
    if recommendations:
        lines.extend(["", "### Recommendation", ""])
        for rec in recommendations[:3]:
            lines.append(f"- {rec}")

    return "\n".join(lines)


def _extract_top_findings(
    results: list[EvaluatedResult], max_count: int = 5
) -> list[tuple[str, str, str]]:
    findings: list[tuple[int, str, str, str]] = []

    for r in results:
        for f in r.failures:
            sev_idx = SEVERITY_ORDER.index(f.severity) if f.severity in SEVERITY_ORDER else 4
            findings.append((sev_idx, f.severity, f.category, f.description))

    findings.sort(key=lambda x: x[0])

    seen_cats: set[str] = set()
    deduped: list[tuple[str, str, str]] = []
    for _, sev, cat, desc in findings:
        if cat not in seen_cats:
            seen_cats.add(cat)
            deduped.append((sev, cat, desc))
        if len(deduped) >= max_count:
            break

    return deduped


def _extract_recommendations(
    results: list[EvaluatedResult], status: str
) -> list[str]:
    recs: list[str] = []

    has_critical = any(
        f.severity == "critical" for r in results for f in r.failures
    )
    has_contradictions = any(
        f.category == "verbal_numeric_contradiction" for r in results for f in r.failures
    )
    has_overclaim = any(
        f.category == "overclaiming" or f.category == "unsupported_conclusion"
        for r in results for f in r.failures
    )

    if has_critical:
        recs.append("Address critical issues before publication or further use.")
    if has_contradictions:
        recs.append("Resolve numeric/verbal contradictions — these undermine credibility.")
    if has_overclaim:
        recs.append("Review and temper unsupported claims.")
    if status == "good":
        recs.append("No blocking issues found. Minor refinements may still improve quality.")
    if not recs:
        recs.append("Review findings below and address issues by severity.")

    return recs


# ---------------------------------------------------------------------------
# Section 2: Key Findings
# ---------------------------------------------------------------------------

def _section_key_findings(record: RunRecord) -> str:
    results = record.results
    all_failures: list[tuple[EvaluatedResult, FailureInstance]] = []
    for r in results:
        for f in r.failures:
            all_failures.append((r, f))

    if not all_failures:
        return "\n".join([
            "",
            "## 2. Key Findings",
            "",
            "No significant findings detected.",
        ])

    all_failures.sort(
        key=lambda x: SEVERITY_ORDER.index(x[1].severity) if x[1].severity in SEVERITY_ORDER else 4
    )

    lines = ["", "## 2. Key Findings", ""]

    for r, f in all_failures[:12]:
        icon = _severity_icon(f.severity)
        conf_tag = f" `[{f.confidence}]`" if f.confidence else ""
        lines.append(f"### {icon} {_label(f.category)}")
        lines.append("")
        lines.append(f"**Severity:** {f.severity.upper()}{conf_tag}  ")
        if len(results) > 1:
            lines.append(f"**Agent:** {_agent_name(r)}  ")
        lines.append(f"**Description:** {f.description}  ")

        if f.impact_on_score:
            lines.append(f"**Impact:** {f.impact_on_score}  ")

        if f.evidence:
            lines.append("")
            lines.append("**Evidence:**")
            for ev in f.evidence[:2]:
                text = ev.text.replace("\n", " ")[:200]
                lines.append(f"> `{ev.source_field}`: \"{text}\"")
        lines.append("")

    # Study forensics findings
    sf_findings = _section_study_forensics_findings(results)
    if sf_findings:
        lines.append(sf_findings)

    return "\n".join(lines)


def _section_study_forensics_findings(results: list[EvaluatedResult]) -> str:
    sf_results = [r for r in results if r.study_forensics and r.study_forensics.get("is_study_forensics")]
    if not sf_results:
        return ""

    lines = ["### Study Forensics Detail", ""]

    for r in sf_results:
        sf = r.study_forensics
        gold = sf.get("gold_label", "")
        detected = sf.get("detected_label", "unknown")
        label_ok = sf.get("label_correct", False)

        lines.append(f"**Agent:** {_agent_name(r)}  ")
        lines.append(f"**Original classification:** `{detected}` {'✅' if label_ok else '❌'}  ")
        lines.append(render_phase8(r.agent_result.phase8))
        if gold:
            lines.append(f"**Expected:** {_label(gold)}  ")

        matched = sf.get("matched_findings", [])
        missed = sf.get("missed_findings", [])
        extra = sf.get("extra_findings", [])
        fp = sf.get("false_positives", [])

        if matched:
            lines.append(f"**Correctly identified:** {', '.join(matched)}  ")
        if missed:
            lines.append(f"**Missed:** {', '.join(missed)}  ")
        if extra:
            lines.append(f"**Additional findings:** {', '.join(extra)}  ")
        if fp:
            lines.append(f"**False positives:** {', '.join(fp)}  ")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Section 3: Recommendations
# ---------------------------------------------------------------------------

def _section_recommendations(record: RunRecord) -> str:
    results = record.results
    lines = ["", "## 3. What To Change", ""]

    critical = []
    major = []
    stable = []
    borderline = []

    for r in results:
        for f in r.failures:
            entry = f"{_label(f.category)}: {f.description}"
            if f.severity == "critical":
                critical.append(entry)
            elif f.severity == "major":
                major.append(entry)
            elif f.severity == "moderate":
                borderline.append(entry)

    # Check for stable aspects
    best = _best_result(results)
    if best:
        for dim_name, weight in DIAGNOSTIC_WEIGHTS.items():
            val = getattr(best.scores, dim_name)
            if val >= 0.7:
                label = dim_name.replace("_", " ").title()
                stable.append(f"{label} ({best.scores.weighted(dim_name):.0f}/{weight})")

    if critical:
        lines.append("### Must Fix Before Use")
        lines.append("")
        for item in critical:
            lines.append(f"- 🔴 {item}")
        lines.append("")

    if major:
        lines.append("### Should Address")
        lines.append("")
        for item in major:
            lines.append(f"- 🟠 {item}")
        lines.append("")

    if borderline:
        lines.append("### Borderline — Review Recommended")
        lines.append("")
        for item in borderline[:5]:
            lines.append(f"- 🟡 {item}")
        lines.append("")

    if stable:
        lines.append("### Stable Areas")
        lines.append("")
        for item in stable:
            lines.append(f"- ✅ {item}")
        lines.append("")

    phase8_pending = any(
        r.agent_result.phase8 and (
            r.agent_result.phase8.get("technical_status") != "completed"
            or r.agent_result.phase8.get("composite_state") != "supported"
            or r.agent_result.phase8.get("derived_label") is None
        ) for r in results
    )
    phase9 = record.metadata.get("phase9")
    if phase9 is not None and (phase9.get("route") != "AUTO_RESOLVABLE"
                              or phase9.get("history_validation") == "invalid" or phase9.get("mandatory")):
        lines.append("Resolve the Phase-9 case review and history validation before relying on this analysis.")
    elif phase8_pending:
        lines.append("Resolve the Phase-8 limitations before treating the claim as supported.")
    elif not critical and not major and not borderline:
        lines.append("No significant changes required. Analysis appears sound.")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Section 4: Method Note
# ---------------------------------------------------------------------------

def _section_method_note(record: RunRecord) -> str:
    task = record.task
    lines = [
        "",
        "## 4. Method Note",
        "",
        "### What This Audit Covers",
        "",
        "Agent Arena performs automated forensic analysis of AI-generated reasoning. "
        "The system evaluates:",
        "",
        "- **Correctness** — Does the answer match the expected result?",
        "- **Reasoning quality** — Are claims supported by evidence and logic?",
        "- **Internal consistency** — Do different parts of the response agree?",
        "- **Mechanism quality** — Are causal explanations grounded, not just named?",
        "- **Self-monitoring** — Does the response acknowledge its own limitations?",
        "",
        "### What This Audit Does Not Cover",
        "",
        "- External fact-checking against live databases or sources",
        "- Ethical or legal assessment of conclusions",
        "- Domain-specific regulatory compliance",
        "- Comparison with human expert judgment",
        "",
        "### Category Definitions",
        "",
    ]

    relevant_cats = set()
    for r in record.results:
        for f in r.failures:
            relevant_cats.add(f.category)
        if r.study_forensics and r.study_forensics.get("detected_label"):
            relevant_cats.add(r.study_forensics["detected_label"])

    if relevant_cats:
        for cat in sorted(relevant_cats):
            label = _label(cat)
            if label != cat.replace("_", " ").title():
                lines.append(f"- **{cat}**: {label}")
        lines.append("")

    lines.extend([
        "### Confidence Levels",
        "",
        "Findings are tagged with confidence levels:",
        "",
        "- **HIGH CONFIDENCE**: Deterministic or numerically verified",
        "- **MEDIUM CONFIDENCE**: Grounded heuristic with supporting evidence",
        "- **HEURISTIC**: Pattern-based detection, may require manual review",
        "",
    ])

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Section 5: Technical Appendix
# ---------------------------------------------------------------------------

def _section_technical_appendix(record: RunRecord) -> str:
    results = record.results
    task = record.task

    lines = [
        "",
        "## 5. Technical Appendix",
        "",
        "*This section is for technical reviewers and internal use.*",
        "",
    ]

    # 5a: Score breakdown
    lines.extend(_appendix_score_matrix(results))

    # 5b: Per-agent detail
    for r in results:
        lines.extend(_appendix_agent_detail(r))

    # 5c: Consistency findings
    consistency_lines = _appendix_consistency(results)
    if consistency_lines:
        lines.extend(consistency_lines)

    # 5d: Forensic flags
    flag_lines = _appendix_forensic_flags(results)
    if flag_lines:
        lines.extend(flag_lines)

    # 5e: Reasoning integrity
    integrity_lines = _appendix_reasoning_integrity(results)
    if integrity_lines:
        lines.extend(integrity_lines)

    # 5f: Task metadata
    lines.extend(_appendix_task_metadata(task))

    return "\n".join(lines)


def _appendix_score_matrix(results: list[EvaluatedResult]) -> list[str]:
    dims = list(DIAGNOSTIC_WEIGHTS.keys())
    lines = ["### Score Matrix", ""]

    header = "| Dimension | Weight | " + " | ".join(_agent_name(r) for r in results) + " |"
    sep = "|" + "|".join(["---"] * (len(results) + 2)) + "|"
    lines.extend([header, sep])

    for dim in dims:
        weight = DIAGNOSTIC_WEIGHTS[dim]
        label = dim.replace("_", " ").title()
        row = f"| {label} | {weight} "
        for r in results:
            val = r.scores.weighted(dim)
            row += f"| {val:.1f}/{weight} "
        row += "|"
        lines.append(row)

    total_row = "| **Total** | **100** "
    for r in results:
        total_row += f"| **{r.scores.total:.1f}** "
    total_row += "|"
    lines.append(total_row)
    lines.append("")

    return lines


def _appendix_agent_detail(r: EvaluatedResult) -> list[str]:
    lines = [f"### Agent: {_agent_full(r)}", ""]

    lines.append(f"**Score:** {r.scores.total:.1f}/100  ")
    lines.append(f"**Latency:** {r.agent_result.latency_ms}ms  ")
    lines.append(f"**Parse OK:** {r.agent_result.parse_ok}  ")

    if r.agent_result.parsed:
        p = r.agent_result.parsed
        conf = confidence_value_if_valid(p.confidence, p.confidence_state)
        if conf is None:
            lines.append(f"**Agent confidence:** unavailable ({p.confidence_state or 'UNKNOWN'})  ")
        else:
            conf_tag = " `[UNKALIBRIERT]`" if conf > 0 else ""
            lines.append(f"**Agent confidence:** {conf:.0%}{conf_tag}  ")
        if p.final_answer:
            answer = p.final_answer[:300]
            lines.append(f"**Final answer:** {answer}  ")

    # Reasoning integrity
    ri = r.reasoning_integrity
    if ri:
        classification = ri.get("classification", "")
        if classification:
            lines.append(f"**Reasoning integrity:** {classification}  ")

    # Claim check summary
    if r.claim_check_results:
        supported = sum(1 for c in r.claim_check_results if c.truth_status.value == "supported")
        contradicted = sum(1 for c in r.claim_check_results if c.truth_status.value == "contradicted")
        lines.append(f"**Claims verified:** {supported} supported, {contradicted} contradicted  ")

    # Mechanism analysis
    ma = r.mechanism_analysis
    if ma:
        parts = []
        if ma.concept_named:
            parts.append("concept named")
        if ma.mechanism_described:
            parts.append("mechanism described")
        if ma.mechanism_grounded_to_case:
            parts.append("grounded to case")
        if parts:
            lines.append(f"**Mechanism:** {', '.join(parts)}  ")
        if ma.missing_elements:
            lines.append(f"**Missing:** {', '.join(ma.missing_elements)}  ")

    # Grounding audit
    ga = r.grounding_audit
    if ga and ga.total_conclusion_claims > 0:
        lines.append(
            f"**Grounding:** {ga.directly_supported} direct, "
            f"{ga.indirectly_supported} indirect, "
            f"{ga.unsupported} unsupported, "
            f"{ga.contradicted} contradicted  "
        )

    lines.append("")
    return lines


def _appendix_consistency(results: list[EvaluatedResult]) -> list[str]:
    any_findings = any(r.consistency_findings for r in results)
    if not any_findings:
        return []

    lines = ["### Consistency Checks", ""]
    for r in results:
        if not r.consistency_findings:
            continue
        if len(results) > 1:
            lines.append(f"**{_agent_name(r)}:**")
            lines.append("")
        for f in r.consistency_findings:
            icon = {"pass": "✅", "warning": "⚠️", "fail": "❌"}.get(f.status, f.status)
            conf_tag = f" `[{f.confidence}]`" if f.confidence else ""
            lines.append(f"- {icon}{conf_tag} `{f.check_type}`: {f.description}")
        lines.append("")

    return lines


def _appendix_forensic_flags(results: list[EvaluatedResult]) -> list[str]:
    any_flags = any(r.forensic_flags for r in results)
    if not any_flags:
        return []

    lines = ["### Forensic Flags", ""]
    for r in results:
        if not r.forensic_flags:
            continue
        if len(results) > 1:
            lines.append(f"**{_agent_name(r)}:**")
            lines.append("")
        for ff in r.forensic_flags:
            sev = _severity_icon(ff.severity)
            lines.append(f"- {sev} `{ff.flag_type}`: {ff.description}")
            for ev in ff.evidence[:1]:
                text = ev.text.replace("\n", " ")[:150]
                lines.append(f"  > `{ev.source_field}`: \"{text}\"")
        lines.append("")

    return lines


def _appendix_reasoning_integrity(results: list[EvaluatedResult]) -> list[str]:
    any_data = any(r.reasoning_integrity for r in results)
    if not any_data:
        return []

    lines = ["### Reasoning Integrity", ""]
    for r in results:
        ri = r.reasoning_integrity
        if not ri:
            continue

        classification = ri.get("classification", "unknown")
        n_int_errors = ri.get("n_intermediate_errors", 0)
        n_lb_errors = ri.get("n_load_bearing_errors", 0)
        lb_mask = ri.get("load_bearing_mask", [])

        if len(results) > 1:
            lines.append(f"**{_agent_name(r)}:**")

        lines.append(f"- Classification: **{classification}**")
        if lb_mask:
            lines.append(f"- Load-bearing steps: {sum(lb_mask)} / {len(lb_mask)}")
        if n_int_errors > 0:
            lines.append(f"- Intermediate errors: {n_int_errors}")
        if n_lb_errors > 0:
            lines.append(f"- Load-bearing errors: {n_lb_errors} `[HIGH CONFIDENCE]`")

        failed_lb = ri.get("failed_load_bearing", [])
        for idx, expl in failed_lb:
            lines.append(f"  - ❌ `steps[{idx}]`: {expl}")
        lines.append("")

    return lines


def _appendix_task_metadata(task) -> list[str]:
    lines = ["### Task Metadata", ""]

    lines.append(f"| Field | Value |")
    lines.append(f"|---|---|")
    lines.append(f"| Task ID | `{task.id}` |")
    lines.append(f"| Type | {task.task_type.value} |")
    lines.append(f"| Domain | {task.domain} |")
    lines.append(f"| Difficulty | {task.difficulty.value} |")
    if task.task_family:
        lines.append(f"| Family | {task.task_family} |")
    if task.trap_type:
        lines.append(f"| Trap type | {task.trap_type} |")
    if task.ambiguity_level:
        lines.append(f"| Ambiguity | {task.ambiguity_level} |")
    if task.gold_label:
        lines.append(f"| Gold label | {task.gold_label} |")
    if task.gold_confidence:
        lines.append(f"| Gold confidence | {task.gold_confidence} |")
    if task.gold_case_type:
        lines.append(f"| Case type | {task.gold_case_type} |")
    lines.append("")

    return lines


# ---------------------------------------------------------------------------
# Main entry point — Markdown
# ---------------------------------------------------------------------------

def generate_client_report(record: RunRecord) -> str:
    """Generate a diagnostic client-style preview, never an official release."""
    from agent_arena.phase8_pipeline import refresh_run_phase8
    record = refresh_run_phase8(record)
    from agent_arena.phase9_pipeline import refresh_run_phase9, render_phase9
    record = refresh_run_phase9(record)
    diagnostic_header = [
        "> **DIAGNOSTIC / NON-RELEASE ARTIFACT — NOT OFFICIALLY RELEASE-AUTHORIZED**",
        "",
        "`artifact_role=diagnostic_non_release` · `official_release_authorized=false`",
        "",
    ]
    sections = [
        render_phase9(record.metadata.get("phase9")) if record.task.task_type == TaskType.STUDY_FORENSICS else "",
        _section_executive_summary(record),
        _section_key_findings(record),
        _section_recommendations(record),
        _section_method_note(record),
        _section_technical_appendix(record),
    ]

    footer = [
        "---",
        "",
        "*Report generated by Agent Arena — local-first AI evaluation engine.*  ",
        f"*Run ID: `{record.run_id}` | {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*",
    ]

    return "\n".join(diagnostic_header + sections) + "\n" + "\n".join(footer) + "\n"


# ---------------------------------------------------------------------------
# HTML rendering
# ---------------------------------------------------------------------------

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  :root {{
    --bg: #ffffff;
    --fg: #1a1a2e;
    --accent: #16213e;
    --border: #e0e0e0;
    --muted: #6b7280;
    --green: #059669;
    --red: #dc2626;
    --yellow: #d97706;
    --blue: #2563eb;
    --bg-light: #f9fafb;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: var(--fg);
    background: var(--bg);
    line-height: 1.6;
    max-width: 900px;
    margin: 0 auto;
    padding: 2rem 1.5rem;
  }}
  h1 {{
    font-size: 1.75rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    color: var(--accent);
    border-bottom: 3px solid var(--accent);
    padding-bottom: 0.5rem;
  }}
  h2 {{
    font-size: 1.35rem;
    font-weight: 600;
    margin-top: 2.5rem;
    margin-bottom: 0.75rem;
    color: var(--accent);
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.4rem;
  }}
  h3 {{
    font-size: 1.1rem;
    font-weight: 600;
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
  }}
  p, li {{ margin-bottom: 0.4rem; }}
  strong {{ font-weight: 600; }}
  code {{
    background: var(--bg-light);
    border: 1px solid var(--border);
    border-radius: 3px;
    padding: 0.1em 0.3em;
    font-size: 0.9em;
  }}
  blockquote {{
    border-left: 4px solid var(--accent);
    padding: 0.5rem 1rem;
    margin: 0.75rem 0;
    background: var(--bg-light);
    color: var(--muted);
    font-style: italic;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 1rem 0;
    font-size: 0.9rem;
  }}
  th, td {{
    text-align: left;
    padding: 0.5rem 0.75rem;
    border: 1px solid var(--border);
  }}
  th {{
    background: var(--bg-light);
    font-weight: 600;
  }}
  tr:nth-child(even) {{ background: var(--bg-light); }}
  hr {{
    border: none;
    border-top: 1px solid var(--border);
    margin: 2rem 0;
  }}
  ul {{ padding-left: 1.5rem; }}
  ol {{ padding-left: 1.5rem; }}
  .status-good {{ color: var(--green); font-weight: 700; }}
  .status-caution {{ color: var(--yellow); font-weight: 700; }}
  .status-critical {{ color: var(--red); font-weight: 700; }}
  .footer {{
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border);
    color: var(--muted);
    font-size: 0.85rem;
  }}
  @media print {{
    body {{ max-width: 100%; padding: 1rem; }}
    h2 {{ page-break-before: auto; }}
  }}
  @page {{
    size: A4;
    margin: 2cm;
  }}
</style>
</head>
<body>
{body}
</body>
</html>
"""


def _md_to_html(md: str) -> str:
    """Minimal Markdown-to-HTML converter — no external dependencies."""
    lines = md.split("\n")
    html_lines: list[str] = []
    in_list = False
    in_ol = False
    in_table = False
    in_blockquote = False
    table_rows: list[str] = []

    def _close_list():
        nonlocal in_list, in_ol
        if in_list:
            html_lines.append("</ul>")
            in_list = False
        if in_ol:
            html_lines.append("</ol>")
            in_ol = False

    def _close_table():
        nonlocal in_table, table_rows
        if in_table:
            _render_table(table_rows, html_lines)
            table_rows = []
            in_table = False

    def _close_blockquote():
        nonlocal in_blockquote
        if in_blockquote:
            html_lines.append("</blockquote>")
            in_blockquote = False

    def _inline(text: str) -> str:
        import re
        text = html_module.escape(text)
        text = re.sub(r'`\[([^\]]+)\]`', r'<code>[\1]</code>', text)
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
        text = text.replace("  ", "<br>")
        return text

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("|") and stripped.endswith("|"):
            _close_list()
            _close_blockquote()
            if not in_table:
                in_table = True
            table_rows.append(stripped)
            continue
        else:
            _close_table()

        if stripped.startswith("> "):
            _close_list()
            if not in_blockquote:
                html_lines.append("<blockquote>")
                in_blockquote = True
            html_lines.append(f"<p>{_inline(stripped[2:])}</p>")
            continue
        else:
            _close_blockquote()

        if stripped.startswith("# "):
            _close_list()
            html_lines.append(f"<h1>{_inline(stripped[2:])}</h1>")
        elif stripped.startswith("## "):
            _close_list()
            html_lines.append(f"<h2>{_inline(stripped[3:])}</h2>")
        elif stripped.startswith("### "):
            _close_list()
            html_lines.append(f"<h3>{_inline(stripped[4:])}</h3>")
        elif stripped.startswith("---"):
            _close_list()
            html_lines.append("<hr>")
        elif stripped.startswith("- "):
            if not in_list:
                in_list = True
                html_lines.append("<ul>")
            html_lines.append(f"<li>{_inline(stripped[2:])}</li>")
        elif len(stripped) > 2 and stripped[0].isdigit() and ". " in stripped[:5]:
            if not in_ol:
                in_ol = True
                html_lines.append("<ol>")
            text = stripped.split(". ", 1)[1]
            html_lines.append(f"<li>{_inline(text)}</li>")
        elif stripped.startswith("  > "):
            html_lines.append(f"<blockquote><p>{_inline(stripped[4:])}</p></blockquote>")
        elif stripped == "":
            _close_list()
            html_lines.append("")
        elif stripped.startswith("*") and stripped.endswith("*") and not stripped.startswith("**"):
            _close_list()
            html_lines.append(f"<p><em>{_inline(stripped[1:-1])}</em></p>")
        else:
            _close_list()
            html_lines.append(f"<p>{_inline(stripped)}</p>")

    _close_list()
    _close_table()
    _close_blockquote()

    return "\n".join(html_lines)


def _render_table(rows: list[str], html_lines: list[str]) -> None:
    if len(rows) < 2:
        return

    def _cells(row: str) -> list[str]:
        return [c.strip() for c in row.strip("|").split("|")]

    header = _cells(rows[0])

    # Skip separator row
    data_start = 1
    if len(rows) > 1 and all(c.strip().replace("-", "").replace(":", "") == "" for c in _cells(rows[1])):
        data_start = 2

    html_lines.append("<table>")
    html_lines.append("<thead><tr>")
    for cell in header:
        import re
        cell = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html_module.escape(cell))
        cell = re.sub(r'`([^`]+)`', r'<code>\1</code>', cell)
        html_lines.append(f"  <th>{cell}</th>")
    html_lines.append("</tr></thead>")

    html_lines.append("<tbody>")
    for row in rows[data_start:]:
        cells = _cells(row)
        html_lines.append("<tr>")
        for cell in cells:
            import re
            cell = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html_module.escape(cell))
            cell = re.sub(r'`([^`]+)`', r'<code>\1</code>', cell)
            html_lines.append(f"  <td>{cell}</td>")
        html_lines.append("</tr>")
    html_lines.append("</tbody>")
    html_lines.append("</table>")


def generate_html_report(record: RunRecord) -> str:
    """Generate a professional HTML audit report."""
    md = generate_client_report(record)
    body = _md_to_html(md)
    title = f"Audit Report — {record.task.title or record.run_id}"
    return _HTML_TEMPLATE.format(title=html_module.escape(title), body=body)


# ---------------------------------------------------------------------------
# PDF rendering (optional — requires weasyprint)
# ---------------------------------------------------------------------------

def generate_pdf_report(record: RunRecord, output_path: Path) -> Path:
    """Generate a diagnostic/non-release PDF. Requires weasyprint to be installed.

    Raises ImportError if weasyprint is not available.
    """
    from agent_arena.release_boundary import is_authoritative_release_path

    if is_authoritative_release_path(output_path):
        raise ValueError("diagnostic renderer cannot write into the official release namespace")
    try:
        from weasyprint import HTML as WeasyprintHTML
    except ImportError:
        raise ImportError(
            "PDF generation requires weasyprint. "
            "Install with: pip install weasyprint"
        )

    html_content = generate_html_report(record)
    doc = WeasyprintHTML(string=html_content)
    doc.write_pdf(str(output_path))
    return output_path


def pdf_available() -> bool:
    """Check if PDF generation is available."""
    try:
        import weasyprint  # noqa: F401
        return True
    except ImportError:
        return False
