"""Gen 7 Pipeline — workflow orchestration layer for agent-arena v0.6.12.

Convenience orchestrator that runs the existing meta-stack modules in
sequence, collects their outputs, and produces a unified pipeline report.

Does NOT add new intelligence, heuristics, or decision logic.
Does NOT modify gold labels, scores, or case data.
Does NOT accept/reject proposals automatically.

Only orchestrates, documents, and summarizes.

Standard flow:
  1. Load journal entries (with optional filters)
  2. Generate Insights report
  3. Generate Calibration report
  4. Generate Routing recommendations
  5. Analyze Disagreements
  6. (optional) Generate Caseforge candidates
  7. Log workflow note to Audit Trail
  8. Produce unified Pipeline Report
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from agent_arena.schemas import (
    CalibrationReport,
    CaseforgeReport,
    DecisionEntry,
    InsightsReport,
    RunJournalEntry,
)


# ---------------------------------------------------------------------------
# Pipeline Result — collected outputs from all modules
# ---------------------------------------------------------------------------

@dataclass
class PipelineStep:
    """Record of a single pipeline step."""
    name: str
    status: str = ""           # "completed" | "skipped" | "planned"
    detail: str = ""           # short human-readable result
    n_items: int = 0           # items produced (proposals, recommendations, etc.)


@dataclass
class PipelineResult:
    """Collected outputs from a full pipeline run."""
    generated_at: str = ""
    journal_dir: str = ""
    n_entries: int = 0
    families_filter: list[str] = field(default_factory=list)
    task_filter: list[str] = field(default_factory=list)
    dry_run: bool = False
    include_caseforge: bool = False

    steps: list[PipelineStep] = field(default_factory=list)

    # Module outputs (None = not executed)
    insights: InsightsReport | None = None
    calibration: CalibrationReport | None = None
    routing_report: object | None = None        # RoutingReport
    disagreement_report: object | None = None   # DisagreementLabReport
    caseforge_report: CaseforgeReport | None = None
    audit_note: DecisionEntry | None = None

    # Aggregated review items
    items_requiring_review: list[str] = field(default_factory=list)
    next_actions: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Pipeline Execution
# ---------------------------------------------------------------------------

def run_pipeline(
    journal_dir: str | Path | None = None,
    families: list[str] | None = None,
    task_ids: list[str] | None = None,
    include_caseforge: bool = False,
    dry_run: bool = False,
    audit_dir: str | Path | None = None,
) -> PipelineResult:
    """Execute the full meta-stack pipeline.

    Args:
        journal_dir: Journal directory (default: .agent_arena)
        families: Restrict analysis to specific families
        task_ids: Restrict analysis to specific task IDs
        include_caseforge: Include Caseforge candidate generation
        dry_run: Plan only — don't write audit trail entries
        audit_dir: Audit trail directory (default: same as journal_dir)

    Returns:
        PipelineResult with all module outputs collected.
    """
    result = PipelineResult(
        generated_at=datetime.now(timezone.utc).isoformat(),
        journal_dir=str(journal_dir or ".agent_arena"),
        families_filter=families or [],
        task_filter=task_ids or [],
        dry_run=dry_run,
        include_caseforge=include_caseforge,
    )

    if audit_dir is None:
        audit_dir = journal_dir

    # ------------------------------------------------------------------
    # Step 1: Load journal entries
    # ------------------------------------------------------------------
    from agent_arena.journal import read_entries

    all_entries = read_entries(journal_dir)

    # Apply filters
    entries = all_entries
    if families:
        entries = [e for e in entries if e.task_family in families]
    if task_ids:
        entries = [e for e in entries if e.task_id in task_ids]

    result.n_entries = len(entries)

    if not entries:
        result.steps.append(PipelineStep(
            name="load_journal",
            status="completed",
            detail="No journal entries found (after filters)",
            n_items=0,
        ))
        return result

    result.steps.append(PipelineStep(
        name="load_journal",
        status="completed",
        detail=f"Loaded {len(entries)} entries "
               f"({len(set(e.task_id for e in entries))} tasks, "
               f"{len(set(e.model or e.agent_id for e in entries))} models)",
        n_items=len(entries),
    ))

    if dry_run:
        return _plan_pipeline(result, entries, include_caseforge)

    # ------------------------------------------------------------------
    # Step 2: Insights
    # ------------------------------------------------------------------
    from agent_arena.insights import generate_insights

    insights = generate_insights(entries)
    result.insights = insights

    n_profiles = len(insights.model_profiles)
    n_maturity = len(insights.category_maturity)
    n_borderline = len(insights.borderline_candidates)
    n_disagree = len(insights.disagreement_summary.cases)

    result.steps.append(PipelineStep(
        name="insights",
        status="completed",
        detail=f"{n_profiles} model profiles, "
               f"{n_maturity} category maturity assessments, "
               f"{n_disagree} disagreement cases, "
               f"{n_borderline} borderline signals",
        n_items=n_profiles,
    ))

    if n_borderline > 0:
        for bc in insights.borderline_candidates:
            result.items_requiring_review.append(
                f"[insights] Borderline candidate: {bc.task_id} — {bc.reason}"
            )

    # ------------------------------------------------------------------
    # Step 3: Calibrate
    # ------------------------------------------------------------------
    from agent_arena.calibrate import generate_calibration_report

    calibration = generate_calibration_report(entries, insights)
    result.calibration = calibration

    result.steps.append(PipelineStep(
        name="calibrate",
        status="completed",
        detail=f"{calibration.n_proposals} proposals "
               f"(gold_review: {len(calibration.gold_review_candidates)}, "
               f"data_gap: {len(calibration.data_gap_candidates)}, "
               f"cat_refinement: {len(calibration.category_refinement_candidates)}, "
               f"model_confusion: {len(calibration.model_confusion_candidates)}, "
               f"fp_reduction: {len(calibration.fp_reduction_candidates)})",
        n_items=calibration.n_proposals,
    ))

    for p in calibration.gold_review_candidates:
        result.items_requiring_review.append(
            f"[calibrate] Gold review: {p.target} — {p.reason}"
        )
    for p in calibration.category_refinement_candidates:
        result.items_requiring_review.append(
            f"[calibrate] Category refinement: {p.target} — {p.reason}"
        )

    # ------------------------------------------------------------------
    # Step 4: Router
    # ------------------------------------------------------------------
    from agent_arena.router import route_from_reports

    routing = route_from_reports(insights, calibration, families)
    result.routing_report = routing

    result.steps.append(PipelineStep(
        name="router",
        status="completed",
        detail=f"{routing.n_recommendations} routing recommendations",
        n_items=routing.n_recommendations,
    ))

    # ------------------------------------------------------------------
    # Step 5: Disagreement Lab
    # ------------------------------------------------------------------
    from agent_arena.disagreement_lab import analyze_disagreements

    disagree = analyze_disagreements(entries, task_ids=task_ids, families=families)
    result.disagreement_report = disagree

    result.steps.append(PipelineStep(
        name="disagreement_lab",
        status="completed",
        detail=f"{disagree.n_disagreement_cases} disagreement cases, "
               f"{disagree.n_borderline_signals} borderline signals, "
               f"{disagree.n_gold_review_signals} gold-review signals",
        n_items=disagree.n_disagreement_cases,
    ))

    for case in disagree.cases:
        if case.likely_gold_review:
            result.items_requiring_review.append(
                f"[disagreement_lab] Gold review signal: {case.task_id} — "
                f"root issue: {case.likely_root_issue}"
            )
        if case.likely_borderline:
            result.items_requiring_review.append(
                f"[disagreement_lab] Borderline: {case.task_id} — "
                f"entropy {case.disagreement_score:.2f}"
            )

    # ------------------------------------------------------------------
    # Step 6: Caseforge (optional)
    # ------------------------------------------------------------------
    if include_caseforge:
        from agent_arena.caseforge import forge_cases

        cf = forge_cases(calibration_report=calibration)
        result.caseforge_report = cf

        result.steps.append(PipelineStep(
            name="caseforge",
            status="completed",
            detail=f"{cf.n_candidates} candidates generated",
            n_items=cf.n_candidates,
        ))

        if cf.n_candidates > 0:
            result.items_requiring_review.append(
                f"[caseforge] {cf.n_candidates} case candidate(s) pending review"
            )
    else:
        result.steps.append(PipelineStep(
            name="caseforge",
            status="skipped",
            detail="Use --include-caseforge to enable",
        ))

    # ------------------------------------------------------------------
    # Step 7: Audit Trail — workflow note
    # ------------------------------------------------------------------
    from agent_arena.audit_trail import log_decision, generate_decision_id

    note = DecisionEntry(
        decision_id=generate_decision_id(),
        timestamp=datetime.now(timezone.utc).isoformat(),
        decision_type="workflow_note",
        target="pipeline_run",
        target_kind="workflow",
        source_module="manual",
        decision="accepted",
        reason=f"Pipeline run completed on {result.n_entries} entries",
        evidence_summary=(
            f"Steps: {', '.join(s.name for s in result.steps if s.status == 'completed')}. "
            f"Families: {', '.join(families) if families else 'all'}. "
            f"Tasks: {', '.join(task_ids) if task_ids else 'all'}."
        ),
        notes=f"Review items: {len(result.items_requiring_review)}",
        upstream_module="pipeline",
        upstream_dependency_summary="Automated pipeline orchestration — no decisions made",
        dependency_confidence="high",
        propagation_risk_level="low",
        review_override=False,
    )
    result.audit_note = note

    log_decision(note, audit_dir)

    result.steps.append(PipelineStep(
        name="audit_trail",
        status="completed",
        detail=f"Workflow note logged: {note.decision_id}",
        n_items=1,
    ))

    # ------------------------------------------------------------------
    # Aggregate next actions
    # ------------------------------------------------------------------
    result.next_actions = _derive_next_actions(result)

    return result


# ---------------------------------------------------------------------------
# Dry-run / Plan mode
# ---------------------------------------------------------------------------

def _plan_pipeline(
    result: PipelineResult,
    entries: list[RunJournalEntry],
    include_caseforge: bool,
) -> PipelineResult:
    """Plan-only mode: show what would run without executing."""
    n_tasks = len(set(e.task_id for e in entries))
    n_models = len(set(e.model or e.agent_id for e in entries))
    n_families = len(set(e.task_family for e in entries))

    steps = [
        PipelineStep(
            name="insights",
            status="planned",
            detail=f"Would analyze {len(entries)} entries across "
                   f"{n_tasks} tasks, {n_models} models, {n_families} families",
        ),
        PipelineStep(
            name="calibrate",
            status="planned",
            detail=f"Would generate calibration proposals from {len(entries)} entries",
        ),
        PipelineStep(
            name="router",
            status="planned",
            detail=f"Would generate routing recommendations for {n_families} families",
        ),
        PipelineStep(
            name="disagreement_lab",
            status="planned",
            detail=f"Would analyze disagreement across {n_tasks} tasks",
        ),
    ]

    if include_caseforge:
        steps.append(PipelineStep(
            name="caseforge",
            status="planned",
            detail="Would generate case candidates from calibration gaps",
        ))
    else:
        steps.append(PipelineStep(
            name="caseforge",
            status="skipped",
            detail="Not included (use --include-caseforge)",
        ))

    steps.append(PipelineStep(
        name="audit_trail",
        status="planned",
        detail="Would log workflow note (dry-run: skipped)",
    ))

    result.steps.extend(steps)
    return result


# ---------------------------------------------------------------------------
# Next-action derivation (observational only)
# ---------------------------------------------------------------------------

def _derive_next_actions(result: PipelineResult) -> list[str]:
    """Derive suggested next actions from pipeline results.

    Pure observation — no decisions or mutations.
    """
    actions: list[str] = []

    if result.calibration:
        if result.calibration.gold_review_candidates:
            actions.append(
                f"Review {len(result.calibration.gold_review_candidates)} "
                f"gold-review candidate(s) via `agent-arena audit-log add`"
            )
        if result.calibration.data_gap_candidates:
            actions.append(
                f"Address {len(result.calibration.data_gap_candidates)} "
                f"data gap(s) — consider `agent-arena caseforge`"
            )

    if result.disagreement_report:
        dr = result.disagreement_report
        if hasattr(dr, 'n_gold_review_signals') and dr.n_gold_review_signals > 0:
            actions.append(
                f"Investigate {dr.n_gold_review_signals} gold-review signal(s) "
                f"from disagreement analysis"
            )

    if result.caseforge_report and result.caseforge_report.n_candidates > 0:
        actions.append(
            f"Review {result.caseforge_report.n_candidates} caseforge "
            f"candidate(s) — all pending human review"
        )

    if result.items_requiring_review:
        n = len(result.items_requiring_review)
        if not actions:
            actions.append(f"Review {n} flagged item(s)")

    if not actions:
        actions.append("No immediate actions — pipeline produced clean results")

    return actions


# ---------------------------------------------------------------------------
# Pipeline Report Rendering
# ---------------------------------------------------------------------------

def render_pipeline_report(result: PipelineResult) -> str:
    """Render PipelineResult as a unified Markdown report."""
    lines: list[str] = []

    def _h1(t: str) -> None:
        lines.append(f"# {t}")
        lines.append("")

    def _h2(t: str) -> None:
        lines.append(f"## {t}")
        lines.append("")

    def _h3(t: str) -> None:
        lines.append(f"### {t}")
        lines.append("")

    def _p(t: str) -> None:
        lines.append(t)
        lines.append("")

    # Header
    _h1("Agent Arena — Pipeline Report")
    _p(f"**Generated:** {result.generated_at}  ")
    _p(f"**Journal:** `{result.journal_dir}`  ")
    _p(f"**Entries analyzed:** {result.n_entries}")

    if result.families_filter:
        _p(f"**Family filter:** {', '.join(result.families_filter)}")
    if result.task_filter:
        _p(f"**Task filter:** {', '.join(result.task_filter)}")
    if result.dry_run:
        _p("**Mode:** DRY RUN — no outputs written")

    # Steps executed
    _h2("Steps Executed")
    lines.append("| Step | Status | Detail |")
    lines.append("|------|--------|--------|")
    for s in result.steps:
        status_icon = {"completed": "+", "skipped": "-", "planned": "?"}
        icon = status_icon.get(s.status, " ")
        lines.append(f"| {s.name} | [{icon}] {s.status} | {s.detail} |")
    lines.append("")

    if result.dry_run:
        _p("_Dry run complete. No modules executed, no outputs written._")
        return "\n".join(lines)

    # Insights summary
    if result.insights:
        ins = result.insights
        _h2("Insights Summary")
        _p(f"**Model profiles:** {len(ins.model_profiles)}")
        for p in ins.model_profiles:
            _p(f"- **{p.model}**: avg score {p.avg_score:.1f}, "
               f"{p.n_runs} runs")
        if ins.category_maturity:
            _h3("Category Maturity")
            lines.append("| Category | Correctness | Maturity | Runs |")
            lines.append("|----------|-------------|----------|------|")
            for m in ins.category_maturity:
                lines.append(
                    f"| {m.category} | {m.correctness_rate:.0%} | "
                    f"{m.maturity} | {m.n_runs} |"
                )
            lines.append("")

    # Calibration summary
    if result.calibration:
        cal = result.calibration
        _h2("Calibration Summary")
        _p(f"**Total proposals:** {cal.n_proposals}")
        if cal.gold_review_candidates:
            _h3("Gold Review Candidates")
            for p in cal.gold_review_candidates:
                _p(f"- **{p.target}**: {p.reason}")
        if cal.data_gap_candidates:
            _h3("Data Gaps")
            for p in cal.data_gap_candidates:
                _p(f"- **{p.target}**: {p.reason}")
        if cal.category_refinement_candidates:
            _h3("Category Refinement")
            for p in cal.category_refinement_candidates:
                _p(f"- **{p.target}**: {p.reason}")

    # Routing summary
    if result.routing_report:
        rr = result.routing_report
        _h2("Routing Recommendations")
        if hasattr(rr, 'recommendations'):
            lines.append("| Target | Mode | Confidence | Models | Cost |")
            lines.append("|--------|------|------------|--------|------|")
            for r in rr.recommendations:
                models_str = ", ".join(r.recommended_models[:3])
                lines.append(
                    f"| {r.target} | {r.recommended_mode} | "
                    f"{r.confidence} | {models_str} | {r.cost_sensitivity} |"
                )
            lines.append("")

    # Disagreement summary
    if result.disagreement_report:
        dr = result.disagreement_report
        _h2("Disagreement Findings")
        _p(f"**Cases analyzed:** {dr.n_cases_analyzed}")
        _p(f"**Disagreement cases:** {dr.n_disagreement_cases}")
        _p(f"**Borderline signals:** {dr.n_borderline_signals}")
        _p(f"**Gold-review signals:** {dr.n_gold_review_signals}")
        if dr.cases:
            _h3("Disagreement Cases")
            for c in dr.cases:
                labels = ", ".join(
                    f"{k}({v})" for k, v in c.label_distribution.items()
                )
                _p(f"- **{c.task_id}**: {labels} — "
                   f"entropy {c.disagreement_score:.2f}, "
                   f"root issue: {c.likely_root_issue}")

    # Caseforge summary
    if result.caseforge_report:
        cf = result.caseforge_report
        _h2("Caseforge Candidates")
        _p(f"**Candidates generated:** {cf.n_candidates}")
        for c in cf.candidates:
            _p(f"- **{c.candidate_id}**: {c.target_family} "
               f"({c.generation_mode}) — {c.proposed_gold_label}")

    # Audit trail note
    if result.audit_note:
        _h2("Audit Trail")
        _p(f"Workflow note logged: `{result.audit_note.decision_id}`")

    # Items requiring review
    if result.items_requiring_review:
        _h2("Items Requiring Human Review")
        for item in result.items_requiring_review:
            lines.append(f"- {item}")
        lines.append("")

    # Next actions
    if result.next_actions:
        _h2("Recommended Next Actions")
        for i, action in enumerate(result.next_actions, 1):
            lines.append(f"{i}. {action}")
        lines.append("")

    # Footer
    lines.append("---")
    _p("*Gen 7 Pipeline — orchestration only. "
       "No decisions made, no data modified. All items require human review.*")

    return "\n".join(lines)
