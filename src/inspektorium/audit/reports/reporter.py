"""Forensic dossier report generator of the Inspektorium audit runtime."""

from __future__ import annotations

from inspektorium.audit.checks.confidence_validity import confidence_value_if_valid
from inspektorium.audit.schemas import (
    AgentProfile,
    ClaimTruthStatus,
    DIAGNOSTIC_WEIGHTS,
    EvaluatedResult,
    EvidenceRole,
    FailureInstance,
    ForensicFlag,
    PatternCluster,
    PostmortemReport,
    RunRecord,
)


def _agent_name(r: EvaluatedResult) -> str:
    return f"{r.agent_result.provider}"


def _agent_full(r: EvaluatedResult) -> str:
    return f"{r.agent_result.provider} ({r.agent_result.model})"


def _find_winner(results: list[EvaluatedResult]) -> EvaluatedResult | None:
    if not results:
        return None
    return max(results, key=lambda r: r.scores.total)


def _score_bar(frac: float, width: int = 10) -> str:
    filled = int(frac * width)
    return "`" + "#" * filled + "." * (width - filled) + "`"


# ---------------------------------------------------------------------------
# 1. Executive Summary
# ---------------------------------------------------------------------------


def _executive_summary(record: RunRecord) -> str:
    results = record.results
    winner = _find_winner(results)
    task = record.task
    lines = [
        f"# Forensic Dossier: {task.title}",
        "",
        f"**Run ID:** `{record.run_id}`  ",
        f"**Task:** {task.id} | {task.domain} | {task.difficulty.value} | {task.task_type.value}  ",
        f"**Timestamp:** {record.timestamp}  ",
    ]
    if task.task_family:
        lines.append(f"**Task Family:** {task.task_family}  ")
    if task.trap_type:
        lines.append(f"**Trap Type:** {task.trap_type}  ")
    if task.ambiguity_level:
        lines.append(f"**Ambiguity:** {task.ambiguity_level}  ")

    lines.extend(["", "## Executive Summary", ""])
    agents = [_agent_name(r) for r in results]
    lines.append(f"**Agents tested:** {', '.join(agents)}")

    if winner:
        totals = sorted(results, key=lambda r: r.scores.total, reverse=True)
        if len(totals) >= 2 and totals[0].scores.total == totals[1].scores.total:
            lines.append(f"**Result:** Tie at **{totals[0].scores.total:.1f}/100**")
        else:
            margin = (
                totals[0].scores.total - totals[1].scores.total
                if len(totals) > 1
                else 0
            )
            lines.append(
                f"**Winner:** {_agent_name(winner)} — **{winner.scores.total:.1f}/100** (margin: {margin:.1f})"
            )

    # Failure + consistency summary
    all_failures: set[str] = set()
    for r in results:
        all_failures.update(r.failure_modes)
    lines.append(
        f"**Failure modes:** {', '.join(sorted(all_failures)) if all_failures else 'none'}"
    )

    total_flags = sum(len(r.forensic_flags) for r in results)
    lines.append(f"**Forensic flags:** {total_flags}")

    total_findings = sum(len(r.consistency_findings) for r in results)
    lines.append(f"**Consistency findings:** {total_findings}")

    # Answer convergence
    answers = [
        r.agent_result.parsed.final_answer[:80] if r.agent_result.parsed else "(none)"
        for r in results
    ]
    if len(set(answers)) == 1:
        lines.append("**Answer convergence:** all agents agree")
    else:
        lines.append(
            f"**Answer convergence:** agents diverge ({len(set(answers))} distinct)"
        )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 2. Score Matrix
# ---------------------------------------------------------------------------


def _score_matrix(results: list[EvaluatedResult]) -> str:
    dims = list(DIAGNOSTIC_WEIGHTS.keys())
    header = (
        "| Agent | "
        + " | ".join(d.replace("_", " ").title()[:16] for d in dims)
        + " | **Total** |"
    )
    sep = "|" + "|".join(["-------"] * (len(dims) + 2)) + "|"
    lines = ["", "## Score Matrix", "", header, sep]
    for r in results:
        row = f"| {_agent_name(r)} "
        for d in dims:
            val = r.scores.weighted(d)
            mx = DIAGNOSTIC_WEIGHTS[d]
            row += f"| {val:.1f}/{mx} "
        row += f"| **{r.scores.total:.1f}/100** |"
        lines.append(row)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 3. Forensic Flags
# ---------------------------------------------------------------------------


def _forensic_flags(results: list[EvaluatedResult]) -> str:
    any_flags = any(r.forensic_flags for r in results)
    if not any_flags:
        return ""

    lines = ["", "## Forensic Flags", ""]
    for r in results:
        if not r.forensic_flags:
            continue
        lines.append(f"### {_agent_name(r)}")
        lines.append("")
        for ff in r.forensic_flags:
            sev = ff.severity.upper()
            lines.append(f"- **[{sev}]** `{ff.flag_type}`: {ff.description}")
            for ev in ff.evidence[:2]:
                text = ev.text.replace("\n", " ")[:100]
                lines.append(f'  - `{ev.source_field}`: "{text}"')
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 4. Evidence Map
# ---------------------------------------------------------------------------


def _evidence_map(results: list[EvaluatedResult]) -> str:
    lines = ["", "## Evidence Map", ""]

    for r in results:
        lines.append(f"### {_agent_name(r)}")
        lines.append("")
        if not r.scored_dimensions:
            lines.append("No scored dimensions available.")
            lines.append("")
            continue

        for sd in r.scored_dimensions:
            label = sd.dimension.replace("_", " ").title()
            lines.append(f"**{label}:** {sd.weighted_score:.1f}/{sd.weight}")

            # Separate by role
            supporting = [e for e in sd.evidence if e.role == EvidenceRole.SUPPORTING]
            weakening = [
                e
                for e in sd.evidence
                if e.role in (EvidenceRole.WEAKENING, EvidenceRole.CONTRADICTORY)
            ]
            missing = [
                e for e in sd.evidence if e.role == EvidenceRole.MISSING_EXPECTED
            ]
            neutral = [
                e
                for e in sd.evidence
                if e.role
                not in (
                    EvidenceRole.SUPPORTING,
                    EvidenceRole.WEAKENING,
                    EvidenceRole.CONTRADICTORY,
                    EvidenceRole.MISSING_EXPECTED,
                )
            ]

            for ev in (supporting + neutral)[:2]:
                text = ev.text.replace("\n", " ")[:120]
                lines.append(f'  - (+) `{ev.source_field}`: "{text}"')
                if ev.relevance:
                    lines.append(f"    _{ev.relevance}_")

            for ev in weakening[:2]:
                text = ev.text.replace("\n", " ")[:120]
                lines.append(f'  - (-) `{ev.source_field}`: "{text}"')
                if ev.relevance:
                    lines.append(f"    _{ev.relevance}_")

            for ev in missing[:1]:
                text = ev.text.replace("\n", " ")[:120]
                lines.append(f'  - (?) `{ev.source_field}`: "{text}"')
                if ev.relevance:
                    lines.append(f"    _{ev.relevance}_")

            if sd.notes:
                for note in sd.notes[:2]:
                    lines.append(f"  - Note: {note}")
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 5. Failure Analysis
# ---------------------------------------------------------------------------


def _failure_analysis(results: list[EvaluatedResult]) -> str:
    any_failures = any(r.failures for r in results)
    if not any_failures:
        return ""

    lines = ["", "## Failure Analysis", ""]
    for r in results:
        if not r.failures:
            continue
        lines.append(f"### {_agent_name(r)}")
        lines.append("")

        by_severity: dict[str, list[FailureInstance]] = {}
        for f in r.failures:
            by_severity.setdefault(f.severity, []).append(f)

        for severity in ("critical", "major", "moderate", "minor", "stylistic"):
            group = by_severity.get(severity, [])
            if not group:
                continue
            lines.append(f"**{severity.upper()}:**")
            for f in group:
                cat_label = f.category.replace("_", " ").title()
                # v0.4.2: show confidence label
                conf_tag = f" `[{f.confidence}]`" if f.confidence else ""
                lines.append(f"- **{cat_label}**{conf_tag}: {f.description}")
                for ev in f.evidence[:1]:
                    text = ev.text.replace("\n", " ")[:100]
                    lines.append(f'  - `{ev.source_field}`: "{text}"')
                if f.impact_on_score:
                    lines.append(f"  - _Impacts: {f.impact_on_score}_")
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 6. Consistency & Grounding Audit
# ---------------------------------------------------------------------------


def _consistency_audit(results: list[EvaluatedResult]) -> str:
    any_findings = any(r.consistency_findings for r in results)
    if not any_findings:
        return ""

    lines = ["", "## Consistency & Grounding Audit", ""]
    for r in results:
        if not r.consistency_findings:
            continue
        lines.append(f"### {_agent_name(r)}")
        lines.append("")

        for f in r.consistency_findings:
            icon = {
                "pass": "PASS",
                "warning": "WARN",
                "fail": "FAIL",
                "minor": "NOTE",
            }.get(f.status, f.status.upper())
            # v0.4.2: show confidence label
            conf_tag = f" `[{f.confidence}]`" if f.confidence else ""
            lines.append(f"- **[{icon}]**{conf_tag} `{f.check_type}`: {f.description}")
            for ev in f.evidence[:1]:
                text = ev.text.replace("\n", " ")[:100]
                lines.append(f'  - `{ev.source_field}`: "{text}"')
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 7. Comparative Forensics (NEW v0.4)
# ---------------------------------------------------------------------------


def _comparative_forensics(record: RunRecord) -> str:
    results = record.results
    if len(results) < 2:
        return ""

    lines = ["", "## Comparative Forensics", ""]

    for r in results:
        name = _agent_name(r)
        lines.append(f"### {name}")
        lines.append("")

        # Strongest trait
        best_dim = max(DIAGNOSTIC_WEIGHTS, key=lambda d: getattr(r.scores, d))
        best_val = r.scores.weighted(best_dim)
        best_label = best_dim.replace("_", " ").title()
        lines.append(
            f"**Strongest trait:** {best_label} ({best_val:.1f}/{DIAGNOSTIC_WEIGHTS[best_dim]})"
        )

        # Weakest trait
        worst_dim = min(DIAGNOSTIC_WEIGHTS, key=lambda d: getattr(r.scores, d))
        worst_val = r.scores.weighted(worst_dim)
        worst_label = worst_dim.replace("_", " ").title()
        lines.append(
            f"**Most important weakness:** {worst_label} ({worst_val:.1f}/{DIAGNOSTIC_WEIGHTS[worst_dim]})"
        )

        # Classification
        s = r.scores
        corr = s.correctness
        support = s.support_strength
        struct = s.structural_reasoning
        mech = s.mechanism_quality

        traits = []
        if corr > 0.8 and support > 0.6 and struct > 0.6 and mech > 0.5:
            traits.append("robust")
        if corr > 0.8 and (support < 0.4 or struct < 0.4):
            traits.append("brittle")
        if corr > 0.8 and mech < 0.3:
            traits.append("shallow")
        if corr < 0.3 and struct > 0.5:
            traits.append("well-reasoned-wrong")
        parsed_confidence = (
            confidence_value_if_valid(
                r.agent_result.parsed.confidence,
                r.agent_result.parsed.confidence_state,
            )
            if r.agent_result.parsed
            else None
        )
        if s.uncertainty_handling < 0.3 or (
            parsed_confidence is not None and parsed_confidence >= 0.95
        ):
            traits.append("overconfident")

        if traits:
            lines.append(f"**Profile:** {', '.join(traits)}")

        # What it caught that others missed
        if r.agent_result.parsed:
            my_text = _all_text_simple(r.agent_result.parsed)
            others_text = " ".join(
                _all_text_simple(o.agent_result.parsed)
                for o in results
                if o is not r and o.agent_result.parsed
            )
            unique_insights = _find_unique_content(my_text, others_text)
            if unique_insights:
                lines.append(f"**Unique contribution:** {unique_insights}")

        # Forensic flags count
        if r.forensic_flags:
            flag_types = [f.flag_type for f in r.forensic_flags]
            lines.append(f"**Risk signals:** {', '.join(flag_types)}")

        lines.append("")

    return "\n".join(lines)


def _all_text_simple(p) -> str:
    parts = [p.final_answer, *p.steps, *p.assumptions, *p.key_claims]
    return " ".join(parts).lower()


def _find_unique_content(my_text: str, others_text: str) -> str:
    """Find noteworthy content words present in one agent but not others."""
    my_words = {w for w in my_text.split() if len(w) > 6}
    other_words = {w for w in others_text.split() if len(w) > 6}
    unique = my_words - other_words

    # Filter for interesting words
    interesting = {
        "paradox",
        "fallacy",
        "bias",
        "theorem",
        "principle",
        "phenomenon",
        "confounding",
        "aggregation",
        "disaggregat",
        "compositional",
        "bayesian",
        "posterior",
        "conditional",
        "asymmetric",
        "discrimination",
        "self-selection",
        "independent",
        "systematic",
    }
    notable = [w for w in unique if any(root in w for root in interesting)]
    if notable:
        return ", ".join(sorted(notable)[:5])
    return ""


# ---------------------------------------------------------------------------
# 8. Concept Coverage Matrix (NEW v0.4)
# ---------------------------------------------------------------------------


def _concept_coverage(record: RunRecord) -> str:
    results = record.results
    insights = record.task.get_key_insights()
    if not insights or len(results) < 2:
        return ""

    lines = ["", "## Concept Coverage Matrix", ""]

    from inspektorium.audit.execution.evaluator import (
        _all_text,
        _insight_matches,
        _content_words,
    )

    # Build header
    header = "| Concept | " + " | ".join(_agent_name(r) for r in results) + " |"
    sep = "|" + "|".join(["-------"] * (len(results) + 1)) + "|"
    lines.append(header)
    lines.append(sep)

    for ins in insights:
        row = f"| {ins.keyword} "
        for r in results:
            if not r.agent_result.parsed:
                row += "| - "
                continue
            text = _all_text(r.agent_result.parsed)
            named = _insight_matches(ins, text)
            # Check mechanism
            mechanism_words = (
                "because",
                "causes",
                "leads to",
                "due to",
                "explained by",
                "driven by",
            )
            has_mechanism = any(mw in text for mw in mechanism_words)
            # Check uncertainty
            has_uncertainty = any(
                ins.keyword.lower() in u.lower()
                for u in r.agent_result.parsed.uncertainties
            )
            # Check alternative
            has_alt = any(
                ins.keyword.lower() in h.lower()
                for h in r.agent_result.parsed.alternative_hypotheses
            )

            markers = []
            if named:
                markers.append("N")  # named
            if has_mechanism:
                markers.append("M")  # mechanism
            if has_uncertainty:
                markers.append("U")  # uncertainty
            if has_alt:
                markers.append("A")  # alternative
            row += f"| {''.join(markers) or '-'} "
        row += "|"
        lines.append(row)

    lines.append("")
    lines.append(
        "_Legend: N=named, M=mechanism explained, U=uncertainty acknowledged, A=alternative considered_"
    )
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 9. Agent Profiles
# ---------------------------------------------------------------------------


def _agent_profiles(results: list[EvaluatedResult]) -> str:
    lines = ["", "## Agent Profiles", ""]
    for r in results:
        a = r.agent_result
        lines.append(f"### {_agent_full(r)}")
        if a.error:
            lines.append(f"**Error:** {a.error}")
            lines.append("")
            continue

        lines.append(f"**Parse OK:** {a.parse_ok} | **Latency:** {a.latency_ms}ms")
        lines.append("")

        if a.parsed:
            p = a.parsed
            lines.append(f"**Final Answer:** {p.final_answer}")
            lines.append("")
            confidence = confidence_value_if_valid(p.confidence, p.confidence_state)
            confidence_text = (
                str(confidence)
                if confidence is not None
                else (p.confidence_state or "UNKNOWN")
            )
            lines.append(f"**Confidence:** {confidence_text}")
            lines.append("")

            if p.assumptions:
                lines.append("**Assumptions:**")
                for item in p.assumptions:
                    lines.append(f"- {item}")
                lines.append("")

            if p.steps:
                lines.append("**Reasoning Steps:**")
                for i, step in enumerate(p.steps, 1):
                    lines.append(f"{i}. {step}")
                lines.append("")

            if p.key_claims:
                lines.append("**Key Claims:**")
                for item in p.key_claims:
                    lines.append(f"- {item}")
                lines.append("")

            if p.alternative_hypotheses:
                lines.append("**Alternative Hypotheses:**")
                for item in p.alternative_hypotheses:
                    lines.append(f"- {item}")
                lines.append("")

            if p.uncertainties:
                lines.append("**Uncertainties:**")
                for item in p.uncertainties:
                    lines.append(f"- {item}")
                lines.append("")

            if p.self_check:
                lines.append("**Self-Verification:**")
                for item in p.self_check:
                    lines.append(f"- {item}")
                lines.append("")

        # Dimension breakdown
        lines.append("**Dimension Scores:**")
        for dim, weight in DIAGNOSTIC_WEIGHTS.items():
            val = r.scores.weighted(dim)
            raw = getattr(r.scores, dim)
            label = dim.replace("_", " ").title()
            bar = _score_bar(raw)
            lines.append(f"- {label}: {val:.1f}/{weight} {bar}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 10. Judge Report (optional)
# ---------------------------------------------------------------------------


def _judge_report(results: list[EvaluatedResult]) -> str:
    any_judge = any(r.judge_result.enabled for r in results)
    if not any_judge:
        return ""

    lines = ["", "## LLM Judge Assessment", ""]
    for r in results:
        jr = r.judge_result
        if not jr.enabled:
            continue
        lines.append(f"### {_agent_name(r)}")
        lines.append("")

        if jr.dimension_scores:
            lines.append("**Judge Scores:**")
            for dim, score in jr.dimension_scores.items():
                label = dim.replace("_", " ").title()
                lines.append(f"- {label}: {score:.2f}")
            lines.append("")

        if jr.claim_audit:
            lines.append("**Claim Audit:**")
            for ca in jr.claim_audit:
                lines.append(f"- **{ca.status.upper()}**: {ca.claim}")
                if ca.evidence:
                    lines.append(f"  - {ca.evidence}")
            lines.append("")

        if jr.comparative_note:
            lines.append(f"**Assessment:** {jr.comparative_note}")
        lines.append(f"**Judge Confidence:** {jr.judge_confidence:.2f}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 11. Final Verdict
# ---------------------------------------------------------------------------


def _verdict(record: RunRecord) -> str:
    results = record.results
    winner = _find_winner(results)
    lines = ["", "## Final Verdict", ""]

    if not winner:
        lines.append("No results to judge.")
        return "\n".join(lines)

    phase8_results = [r for r in results if r.agent_result.phase8]
    if phase8_results:
        from inspektorium.audit.forensics.pipeline import render_phase8

        lines.append(
            "Historical diagnostic scores below do not establish claim support."
        )
        lines.extend(render_phase8(r.agent_result.phase8) for r in phase8_results)
    totals = sorted(results, key=lambda r: r.scores.total, reverse=True)

    if len(totals) == 1:
        lines.append(
            f"**Solo run: {_agent_name(totals[0])}** scored **{totals[0].scores.total:.1f}/100**."
        )
    elif totals[0].scores.total == totals[1].scores.total:
        lines.append(
            f"**Tie** between {_agent_name(totals[0])} and {_agent_name(totals[1])} "
            f"at {totals[0].scores.total:.1f}/100."
        )
    else:
        margin = totals[0].scores.total - totals[1].scores.total
        lines.append(
            f"**Winner: {_agent_name(winner)}** with **{winner.scores.total:.1f}/100** "
            f"(+{margin:.1f} over {_agent_name(totals[1])})."
        )

    lines.append("")
    lines.append("**Best per dimension:**")
    for dim, weight in DIAGNOSTIC_WEIGHTS.items():
        best = max(results, key=lambda r: getattr(r.scores, dim))
        val = best.scores.weighted(dim)
        label = dim.replace("_", " ").title()
        lines.append(f"- {label}: {_agent_name(best)} ({val:.1f}/{weight})")

    # Latency
    lines.append("")
    lines.append("**Latency vs Quality:**")
    lines.append("")
    lines.append("| Agent | Latency | Score | Points/sec |")
    lines.append("|-------|---------|-------|------------|")
    for r in results:
        ms = r.agent_result.latency_ms
        total = r.scores.total
        pps = total / (ms / 1000) if ms > 0 else 0
        lines.append(
            f"| {_agent_name(r)} | {ms / 1000:.1f}s | {total:.1f}/100 | {pps:.1f} |"
        )

    lines.append("")
    all_failures: set[str] = set()
    for r in results:
        all_failures.update(r.failure_modes)
    phase8_pending = any(
        r.agent_result.phase8.get("technical_status") != "completed"
        or r.agent_result.phase8.get("composite_state") != "supported"
        or r.agent_result.phase8.get("derived_label") is None
        for r in phase8_results
    )
    phase9 = record.metadata.get("phase9")
    if phase9 is not None and (
        phase9.get("route") != "AUTO_RESOLVABLE"
        or phase9.get("history_validation") == "invalid"
        or phase9.get("mandatory")
    ):
        lines.append(
            "Phase-9 case review or history validation remains unresolved; original scores do not resolve it."
        )
    elif phase8_pending:
        lines.append("Phase-8 limitations remain; original scores do not resolve them.")
    elif not all_failures:
        lines.append("All agents completed without critical failure modes.")
    else:
        lines.append(f"Failure modes observed: {', '.join(sorted(all_failures))}.")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def generate_report(
    record: RunRecord,
    postmortems: list[PostmortemReport] | None = None,
    failure_patterns: list[PatternCluster] | None = None,
    agent_profile: AgentProfile | None = None,
) -> str:
    """Generate an internal diagnostic forensic dossier from a run record.

    Optional v0.6 parameters add postmortem, pattern, and profile sections.
    """
    from inspektorium.audit.forensics.pipeline import refresh_run_phase8

    record = refresh_run_phase8(record)
    from inspektorium.audit.review.pipeline import refresh_run_phase9, render_phase9

    record = refresh_run_phase9(record)
    sections = [
        render_phase9(record.metadata.get("phase9"))
        if record.metadata.get("phase9")
        else "",
        _executive_summary(record),
        _score_matrix(record.results),
        _study_forensics_section(record.results),
        _forecast_integrity_section(record.results),
        _reasoning_integrity_section(record.results),
        _claim_check_section(record.results),
        _mechanism_analysis_section(record.results),
        _grounding_audit_section(record.results),
        _forensic_flags(record.results),
        _evidence_map(record.results),
        _failure_analysis(record.results),
        _consistency_audit(record.results),
        _comparative_forensics(record),
        _concept_coverage(record),
        _agent_profiles(record.results),
        _judge_report(record.results),
        # v0.6: cross-run sections
        _postmortem_section(postmortems),
        _pattern_section(failure_patterns),
        _agent_profile_section(agent_profile),
        _verdict(record),
    ]
    header = (
        "> **DIAGNOSTIC / NON-RELEASE ARTIFACT — NOT OFFICIALLY RELEASE-AUTHORIZED**\n\n"
        "`artifact_role=diagnostic_non_release` · `official_release_authorized=false`\n\n"
    )
    return header + "\n".join(s for s in sections if s) + "\n"


# ---------------------------------------------------------------------------
# v0.6: Study Forensics Audit
# ---------------------------------------------------------------------------


def _study_forensics_section(results: list[EvaluatedResult]) -> str:
    """Show study forensics audit results."""
    any_data = any(
        r.study_forensics and r.study_forensics.get("is_study_forensics")
        for r in results
    )
    if not any_data:
        return ""

    lines = ["", "## Study Forensics Audit", ""]

    for r in results:
        sf = r.study_forensics
        if not sf or not sf.get("is_study_forensics"):
            continue

        lines.append(f"### {_agent_name(r)}")
        lines.append("")

        gold = sf.get("gold_label", "")
        detected = sf.get("detected_label", "unknown")
        label_ok = sf.get("label_correct", False)
        icon = "+" if label_ok else "x"
        lines.append(
            f"**Original classification:** `{detected}` [{icon}] (gold: `{gold}`)"
        )
        from inspektorium.audit.forensics.pipeline import render_phase8

        lines.append(render_phase8(r.agent_result.phase8))

        scores = sf.get("scores", {})
        recall = scores.get("finding_recall", 0.0)
        lines.append(f"**Finding Recall:** {recall:.0%}")

        matched = sf.get("matched_findings", [])
        if matched:
            lines.append(f"**Matched Findings:** {', '.join(matched)}")

        missed = sf.get("missed_findings", [])
        if missed:
            lines.append(f"**Missed Findings:** {', '.join(missed)}")

        extra = sf.get("extra_findings", [])
        if extra:
            lines.append(f"**Extra Findings:** {', '.join(extra)}")

        fp = sf.get("false_positives", [])
        if fp:
            lines.append(f"**False Positives:** {', '.join(fp)}")

        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# v0.5: Forecast Integrity Audit
# ---------------------------------------------------------------------------

_DECISION_LABELS = {
    "forecast": "Active forecast",
    "watch": "Watching — insufficient conviction",
    "no_trade": "No trade — no edge found",
    "abstain": "Abstaining — cannot evaluate",
}

_FORECAST_SCORE_LABELS = {
    "probability_calibration_quality": "Probability Calibration",
    "baseline_awareness": "Baseline Awareness",
    "rule_comprehension": "Rule Comprehension",
    "skeptic_depth": "Skeptic Depth",
    "no_action_quality": "No-Action Quality",
    "uncertainty_honesty": "Uncertainty Honesty",
}


def _forecast_integrity_section(results: list[EvaluatedResult]) -> str:
    """Show forecast integrity audit for forecasting_decision tasks."""
    any_data = any(
        r.forecast_integrity and r.forecast_integrity.get("is_forecast")
        for r in results
    )
    if not any_data:
        return ""

    lines = ["## Forecast Integrity Audit", ""]
    for r in results:
        fi = r.forecast_integrity
        if not fi or not fi.get("is_forecast"):
            continue
        name = _agent_name(r)
        cat = fi.get("decision_category", "")
        prob = fi.get("probability_estimate")

        lines.append(f"### {name}")
        cat_label = _DECISION_LABELS.get(cat, cat or "(none)")
        lines.append(f"**Decision:** {cat_label}")
        if prob is not None:
            lines.append(f"**Probability Estimate:** {prob:.0%}")
        lines.append("")

        # Forecast-specific scores
        scores = fi.get("scores", {})
        if scores:
            lines.append("**Forecast Dimensions:**")
            for key, label in _FORECAST_SCORE_LABELS.items():
                val = scores.get(key)
                if val is not None:
                    bar_filled = int(val * 10)
                    bar = "`" + "#" * bar_filled + "." * (10 - bar_filled) + "`"
                    lines.append(f"- {label}: {val:.2f} {bar}")
            lines.append("")

        # Forecast-specific failures
        fc_failures = fi.get("failures", [])
        if fc_failures:
            lines.append("**Findings:**")
            for f in fc_failures:
                cat_label = f.category.replace("_", " ").title()
                conf = f" `[{f.confidence}]`" if f.confidence else ""
                sev = f.severity.upper()
                lines.append(f"- **[{sev}]**{conf} {cat_label}: {f.description}")
            lines.append("")

        # Forecast flags
        fc_flags = fi.get("flags", [])
        if fc_flags:
            lines.append("**Risk Signals:**")
            for f in fc_flags:
                lines.append(f"- `{f.flag_type}`: {f.description}")
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# v0.4.3: Reasoning Integrity Audit
# ---------------------------------------------------------------------------

_INTEGRITY_LABELS = {
    "well_supported": "Correct and well-supported",
    "brittle": "Correct but brittle reasoning",
    "accidental": "Correct but likely accidental",
}


def _reasoning_integrity_section(results: list[EvaluatedResult]) -> str:
    """Show reasoning integrity classification and step-level findings."""
    any_data = any(r.reasoning_integrity for r in results)
    if not any_data:
        return ""

    lines = ["## Reasoning Integrity Audit", ""]
    for r in results:
        ri = r.reasoning_integrity
        if not ri:
            continue
        name = _agent_name(r)
        classification = ri.get("classification", "well_supported")
        n_int_errors = ri.get("n_intermediate_errors", 0)
        n_lb_errors = ri.get("n_load_bearing_errors", 0)
        lb_mask = ri.get("load_bearing_mask", [])
        failed_lb = ri.get("failed_load_bearing", [])

        lines.append(f"### {name}")
        label = _INTEGRITY_LABELS.get(classification, classification)
        lines.append(f"**Classification:** {label}")
        lines.append(f"**Load-bearing steps:** {sum(lb_mask)} / {len(lb_mask)}")
        if n_int_errors > 0:
            conf = "`[HIGH CONFIDENCE]`" if n_lb_errors > 0 else "`[MEDIUM CONFIDENCE]`"
            lines.append(f"**Intermediate arithmetic errors:** {n_int_errors} {conf}")
        if n_lb_errors > 0:
            lines.append(f"**Load-bearing errors:** {n_lb_errors} `[HIGH CONFIDENCE]`")
            for idx, expl in failed_lb:
                lines.append(f"- **[FAIL]** `steps[{idx}]`: {expl}")

        # Step check details
        step_checks = r.step_check_results
        if step_checks:
            verified = [c for c in step_checks if hasattr(c, "is_correct")]
            correct = [c for c in verified if c.is_correct]
            wrong = [c for c in verified if not c.is_correct]
            if correct:
                lines.append(
                    f"**Verified correct:** {len(correct)} intermediate calculation(s)"
                )
            if wrong:
                for c in wrong:
                    lines.append(
                        f"- **[FAIL]** `[{c.confidence}]` `{c.source_field}`: "
                        f"{c.claim_text} — {c.explanation}"
                    )

        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# v0.4.1: Claim Check Section
# ---------------------------------------------------------------------------


def _claim_check_section(results: list[EvaluatedResult]) -> str:
    """Show claim check contradictions per agent."""
    any_results = any(r.claim_check_results for r in results)
    if not any_results:
        return ""

    lines = ["## Claim Verification", ""]
    for r in results:
        name = _agent_name(r)
        checks = r.claim_check_results
        if not checks:
            continue

        contradictions = [
            c for c in checks if c.truth_status == ClaimTruthStatus.CONTRADICTED
        ]
        supported = [c for c in checks if c.truth_status == ClaimTruthStatus.SUPPORTED]
        unresolved = [
            c for c in checks if c.truth_status == ClaimTruthStatus.UNRESOLVED
        ]

        lines.append(f"### {name}")
        lines.append(
            f"Claims checked: {len(checks)} | "
            f"Supported: {len(supported)} | "
            f"Contradicted: {len(contradictions)} | "
            f"Unresolved: {len(unresolved)}"
        )
        lines.append("")

        if contradictions:
            lines.append("**Contradictions found:** `[HIGH CONFIDENCE]`")
            for c in contradictions:
                lines.append(
                    f"- :x: `{c.claim.subject}` {c.claim.relation} `{c.claim.object}` — {c.explanation}"
                )
                lines.append(
                    f'  Source: `{c.claim.source_field}` — "{c.claim.source_text[:120]}"'
                )
            lines.append("")

        if supported:
            lines.append("**Verified claims:** `[HIGH CONFIDENCE]`")
            for c in supported[:5]:
                lines.append(
                    f"- :white_check_mark: `{c.claim.subject}` {c.claim.relation} `{c.claim.object}` — {c.explanation}"
                )
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# v0.4.1: Mechanism Analysis Section
# ---------------------------------------------------------------------------


def _mechanism_analysis_section(results: list[EvaluatedResult]) -> str:
    """Show mechanism analysis breakdown per agent."""
    any_analysis = any(r.mechanism_analysis for r in results)
    if not any_analysis:
        return ""

    lines = ["## Mechanism Analysis", ""]
    for r in results:
        ma = r.mechanism_analysis
        if not ma:
            continue
        name = _agent_name(r)
        lines.append(f"### {name}")

        named_icon = ":white_check_mark:" if ma.concept_named else ":x:"
        desc_icon = ":white_check_mark:" if ma.mechanism_described else ":x:"
        ground_icon = ":white_check_mark:" if ma.mechanism_grounded_to_case else ":x:"

        lines.append(f"| Aspect | Status |")
        lines.append(f"|--------|--------|")
        lines.append(
            f"| Concept named | {named_icon} {', '.join(ma.named_concepts) if ma.named_concepts else 'none'} |"
        )
        lines.append(
            f"| Mechanism described | {desc_icon} ({len(ma.mechanism_sentences)} sentence(s)) |"
        )
        lines.append(
            f"| Grounded to case | {ground_icon} ({len(ma.grounding_sentences)} sentence(s)) |"
        )
        lines.append("")

        if ma.missing_elements:
            lines.append(f"**Missing:** {', '.join(ma.missing_elements)}")
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# v0.4.1: Grounding Audit Section
# ---------------------------------------------------------------------------


def _grounding_audit_section(results: list[EvaluatedResult]) -> str:
    """Show grounding audit per agent."""
    any_audit = any(r.grounding_audit for r in results)
    if not any_audit:
        return ""

    lines = ["## Grounding Audit", ""]
    for r in results:
        ga = r.grounding_audit
        if not ga or ga.total_conclusion_claims == 0:
            continue
        name = _agent_name(r)
        lines.append(f"### {name}")
        lines.append(f"Conclusion claims: {ga.total_conclusion_claims}")
        lines.append(f"- Direct support: {ga.directly_supported}")
        lines.append(f"- Indirect support: {ga.indirectly_supported}")
        lines.append(f"- Unsupported: {ga.unsupported}")
        lines.append(f"- Contradicted: {ga.contradicted}")
        lines.append("")

        if ga.unsupported_claims:
            lines.append("**Unsupported claims:**")
            for uc in ga.unsupported_claims[:5]:
                lines.append(f'- "{uc}"')
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# v0.6: Postmortem Summary
# ---------------------------------------------------------------------------


def _postmortem_section(postmortems: list[PostmortemReport] | None) -> str:
    """Render postmortem findings for the report."""
    if not postmortems:
        return ""

    lines = ["", "## Postmortem Summary", ""]
    for pm in postmortems:
        lines.append(f"### {pm.agent_id} — {pm.task_id}")
        lines.append(f"**Verdict:** {pm.verdict}")
        if pm.was_correct is not None:
            icon = "CORRECT" if pm.was_correct else "INCORRECT"
            lines.append(f"**Outcome:** {icon}")
        if pm.reasoning_integrity:
            lines.append(f"**Reasoning Integrity:** {pm.reasoning_integrity}")
        lines.append("")

        if pm.probable_causal_failures:
            lines.append("**Probable Causal Failures:**")
            for f in pm.probable_causal_failures:
                lines.append(
                    f"- **[{f.severity.upper()}]** `[{f.confidence}]` "
                    f"{f.category}: {f.description}"
                )
            lines.append("")

        if pm.contributing_factors:
            lines.append("**Contributing Factors:**")
            for f in pm.contributing_factors[:5]:
                lines.append(f"- {f.category}: {f.description}")
            lines.append("")

        if pm.mitigating_factors:
            lines.append("**Mitigating Factors:**")
            for f in pm.mitigating_factors[:3]:
                lines.append(f"- {f.category}: {f.description}")
            lines.append("")

        if pm.lessons:
            lines.append("**Lessons:**")
            for lesson in pm.lessons:
                lines.append(f"- {lesson}")
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# v0.6: Repeated Failure Patterns
# ---------------------------------------------------------------------------


def _pattern_section(patterns: list[PatternCluster] | None) -> str:
    """Render recurring failure/flag patterns."""
    if not patterns:
        return ""

    lines = ["", "## Repeated Failure Patterns", ""]
    lines.append("| Pattern | Category | Frequency | Affected Tasks |")
    lines.append("|---------|----------|-----------|----------------|")
    for p in patterns:
        tasks = ", ".join(p.affected_tasks[:5])
        if len(p.affected_tasks) > 5:
            tasks += f" (+{len(p.affected_tasks) - 5})"
        lines.append(
            f"| {p.pattern_type} | {p.category} | "
            f"{p.occurrences}/{p.total_runs} ({p.frequency:.0%}) | {tasks} |"
        )
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# v0.6: Agent Profile Snapshot
# ---------------------------------------------------------------------------


def _agent_profile_section(profile: AgentProfile | None) -> str:
    """Render an aggregated agent profile snapshot."""
    if not profile or profile.n_runs == 0:
        return ""

    p = profile
    lines = [
        "",
        "## Agent Profile Snapshot",
        "",
        f"**Agent:** {p.agent_id}",
    ]
    if p.model:
        lines.append(f"**Model:** {p.model}")
    lines.extend(
        [
            f"**Runs Analyzed:** {p.n_runs}",
            f"**Average Score:** {p.avg_total_score:.1f}/100",
            f"**Strongest Dimension:** {p.strongest_dimension.replace('_', ' ').title()}",
            f"**Weakest Dimension:** {p.weakest_dimension.replace('_', ' ').title()}",
            "",
        ]
    )

    # Integrity rates
    rates = []
    if p.accidental_correctness_rate > 0:
        rates.append(f"Accidental correctness: {p.accidental_correctness_rate:.0%}")
    if p.brittleness_rate > 0:
        rates.append(f"Brittleness: {p.brittleness_rate:.0%}")
    if p.contradiction_rate > 0:
        rates.append(f"Contradictions: {p.contradiction_rate:.0%}")
    if rates:
        lines.append("**Integrity Rates:**")
        for r in rates:
            lines.append(f"- {r}")
        lines.append("")

    # Forecast profile
    if p.overconfidence_rate > 0 or p.base_rate_awareness or p.no_trade_quality:
        lines.append("**Forecast Profile:**")
        if p.avg_probability_estimate is not None:
            lines.append(
                f"- Average probability estimate: {p.avg_probability_estimate:.1%}"
            )
        if p.overconfidence_rate > 0:
            lines.append(f"- Overconfidence rate: {p.overconfidence_rate:.0%}")
        if p.base_rate_awareness:
            lines.append(f"- Base rate awareness: {p.base_rate_awareness}")
        if p.no_trade_quality:
            lines.append(f"- No-trade quality: {p.no_trade_quality}")
        lines.append("")

    # Recurring failures
    if p.recurring_failures:
        lines.append("**Top Recurring Failures:**")
        for rf in p.recurring_failures[:5]:
            lines.append(
                f"- {rf.category}: {rf.occurrences}/{rf.total_runs} ({rf.frequency:.0%})"
            )
        lines.append("")

    return "\n".join(lines)
