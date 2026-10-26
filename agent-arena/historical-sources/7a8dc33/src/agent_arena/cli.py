"""CLI entry point for agent-arena."""

from __future__ import annotations

import json
from pathlib import Path

import click

from agent_arena.agent_loader import load_agent_config
from agent_arena.evaluator import evaluate_run
from agent_arena.providers import get_provider
from agent_arena.reporter import generate_report
from agent_arena.runner import run_task, run_task_with_providers
from agent_arena.schemas import RunRecord
from agent_arena.task_loader import load_task


RUNS_DIR = Path("runs")
REPORTS_DIR = Path("reports")
INSIGHTS_DIR = Path("reports/insights")


def _save_run(record: RunRecord) -> Path:
    RUNS_DIR.mkdir(exist_ok=True)
    path = RUNS_DIR / f"{record.run_id}.json"
    path.write_text(record.model_dump_json(indent=2))
    return path


def _load_run(path: str) -> RunRecord:
    data = json.loads(Path(path).read_text())
    return RunRecord(**data)


@click.group()
@click.version_option(package_name="agent-arena")
def cli():
    """agent-arena: local-first AI agent evaluation engine."""
    pass


@cli.command()
@click.option("--task", required=True, help="Path to task YAML file")
@click.option("--agents", required=True, help="Comma-separated provider names or agent config YAML paths")
def run(task: str, agents: str):
    """Run agents on a task, evaluate, and save results."""
    task_obj = load_task(task)
    agent_specs = [a.strip() for a in agents.split(",")]

    click.echo(f"Task: {task_obj.title} ({task_obj.id})")

    # Detect if specs are YAML paths or plain provider names
    if any(s.endswith(".yaml") or s.endswith(".yml") for s in agent_specs):
        configs = [load_agent_config(s) for s in agent_specs]
        providers = []
        for cfg in configs:
            p = get_provider(cfg.provider, model=cfg.model, temperature=cfg.temperature, label=cfg.label)
            providers.append(p)
        click.echo(f"Agents: {', '.join(cfg.label for cfg in configs)}")
        click.echo()
        for cfg in configs:
            click.echo(f"  Running {cfg.label} ({cfg.model})...")
        run_id, results = run_task_with_providers(task_obj, providers)
    else:
        click.echo(f"Agents: {', '.join(agent_specs)}")
        click.echo()
        for name in agent_specs:
            click.echo(f"  Running {name}...")
        run_id, results = run_task(task_obj, agent_specs)

    click.echo("\nEvaluating...")
    record = evaluate_run(task_obj, run_id, results)

    path = _save_run(record)
    click.echo(f"Run saved: {path}")

    # Also generate report
    report = generate_report(record)
    REPORTS_DIR.mkdir(exist_ok=True)
    report_path = REPORTS_DIR / f"{run_id}.md"
    report_path.write_text(report)
    click.echo(f"Report saved: {report_path}")

    # Print summary
    click.echo("\n--- Summary ---")
    for r in record.results:
        a = r.agent_result
        status = "OK" if a.parse_ok else ("ERROR" if a.error else "PARSE_FAIL")
        click.echo(f"  {a.provider}: {r.scores.total:.1f}/100 [{status}] ({a.latency_ms}ms)")


@cli.command()
@click.option("--run", "run_path", required=True, help="Path to run JSON file")
def evaluate(run_path: str):
    """Re-evaluate a saved run."""
    record = _load_run(run_path)
    # Re-evaluate from raw results
    raw_results = [r.agent_result for r in record.results]
    new_record = evaluate_run(record.task, record.run_id, raw_results)

    path = _save_run(new_record)
    click.echo(f"Re-evaluated and saved: {path}")


@cli.command()
@click.option("--run", "run_path", required=True, help="Path to run JSON file")
@click.option("--format", "fmt", default="markdown", help="Output format (markdown)")
def report(run_path: str, fmt: str):
    """Generate an internal forensic dossier from a saved run."""
    record = _load_run(run_path)
    md = generate_report(record)

    REPORTS_DIR.mkdir(exist_ok=True)
    report_path = REPORTS_DIR / f"{record.run_id}.md"
    report_path.write_text(md)
    click.echo(f"Report saved: {report_path}")
    click.echo()
    click.echo(md)


CLIENT_REPORTS_DIR = Path("reports/diagnostic/client")


@cli.command("client-report")
@click.option("--run", "run_path", required=True, help="Path to run JSON file")
@click.option("--format", "fmt", default="markdown",
              type=click.Choice(["markdown", "html", "pdf"]),
              help="Output format (default: markdown)")
@click.option("--output", "output_path", default=None,
              help="Output path (default: auto-generated)")
@click.option("--quiet", is_flag=True, help="Only save, don't print to stdout")
def client_report(run_path: str, fmt: str, output_path: str | None, quiet: bool):
    """Generate a diagnostic client-style preview (never an official release)."""
    from agent_arena.release_boundary import is_authoritative_release_path
    from agent_arena.reporting import (
        generate_client_report,
        generate_html_report,
        generate_pdf_report,
        pdf_available,
    )

    record = _load_run(run_path)

    if fmt == "markdown":
        content = generate_client_report(record)
        ext = "md"
    elif fmt == "html":
        content = generate_html_report(record)
        ext = "html"
    elif fmt == "pdf":
        if not pdf_available():
            click.echo("PDF generation requires weasyprint.")
            click.echo("Install with: pip install weasyprint")
            click.echo("Falling back to HTML...")
            content = generate_html_report(record)
            ext = "html"
        else:
            content = None
            ext = "pdf"
    else:
        click.echo(f"Unknown format: {fmt}")
        return

    if output_path:
        out = Path(output_path)
    else:
        CLIENT_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        out = CLIENT_REPORTS_DIR / f"{record.run_id}_diagnostic_preview.{ext}"
    if is_authoritative_release_path(out):
        raise click.ClickException(
            "diagnostic client-report cannot write into the official release namespace"
        )

    if fmt == "pdf" and content is None:
        generate_pdf_report(record, out)
    else:
        out.write_text(content)

    click.echo(f"Diagnostic non-release report saved: {out}")

    if not quiet and content and fmt == "markdown":
        click.echo()
        click.echo(content)
    raise SystemExit(2)


@cli.command()
@click.option("--journal", "journal_dir", default=None,
              help="Journal directory (default: .agent_arena)")
@click.option("--output", "output_path", default=None,
              help="Output path for the insights report (default: auto-generated)")
@click.option("--quiet", is_flag=True, help="Only save, don't print to stdout")
def insights(journal_dir: str | None, output_path: str | None, quiet: bool):
    """Generate a Gen 1 Insights report from stored journal entries."""
    from agent_arena.journal import read_entries
    from agent_arena.insights import generate_insights, render_insights_report

    entries = read_entries(journal_dir)
    if not entries:
        click.echo("No journal entries found. Run evaluations first.")
        click.echo("Hint: journal entries are stored in .agent_arena/journal.jsonl")
        return

    click.echo(f"Analyzing {len(entries)} journal entries...")
    report = generate_insights(entries)
    md = render_insights_report(report)

    # Save
    INSIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    if output_path:
        out = Path(output_path)
    else:
        ts = report.generated_at[:19].replace(":", "-").replace("T", "_")
        out = INSIGHTS_DIR / f"insights_{ts}.md"

    out.write_text(md)
    click.echo(f"Insights report saved: {out}")

    if not quiet:
        click.echo()
        click.echo(md)


CALIBRATE_DIR = Path("reports/calibrate")


@cli.command()
@click.option("--journal", "journal_dir", default=None,
              help="Journal directory (default: .agent_arena)")
@click.option("--output", "output_path", default=None,
              help="Output path for the calibration report (default: auto-generated)")
@click.option("--quiet", is_flag=True, help="Only save, don't print to stdout")
def calibrate(journal_dir: str | None, output_path: str | None, quiet: bool):
    """Generate a Gen 2 Calibration report with review-ready proposals."""
    from agent_arena.journal import read_entries
    from agent_arena.calibrate import generate_calibration_report, render_calibration_report

    entries = read_entries(journal_dir)
    if not entries:
        click.echo("No journal entries found. Run evaluations first.")
        click.echo("Hint: journal entries are stored in .agent_arena/journal.jsonl")
        return

    click.echo(f"Analyzing {len(entries)} journal entries for calibration...")
    report = generate_calibration_report(entries)
    md = render_calibration_report(report)

    # Save
    CALIBRATE_DIR.mkdir(parents=True, exist_ok=True)
    if output_path:
        out = Path(output_path)
    else:
        ts = report.generated_at[:19].replace(":", "-").replace("T", "_")
        out = CALIBRATE_DIR / f"calibrate_{ts}.md"

    out.write_text(md)
    click.echo(f"Calibration report saved: {out}")
    click.echo(f"Proposals generated: {report.n_proposals}")

    if not quiet:
        click.echo()
        click.echo(md)


CASEFORGE_DIR = Path("reports/caseforge")


@cli.command()
@click.option("--family", default=None,
              help="Target family (solid, overclaim, correlation_vs_causation, mechanism_vs_evidence)")
@click.option("--case-type", "case_type", default="clear",
              help="Case type: clear or borderline (default: clear)")
@click.option("--count", default=1, type=int,
              help="Number of candidates to generate (default: 1)")
@click.option("--shape", default="",
              help="Target sub-shape (e.g., animal_to_human)")
@click.option("--from-calibrate", "calibrate_path", default=None,
              help="Path to calibration report JSON for data-gap-driven generation")
@click.option("--borderline", "borderline_mode", is_flag=True,
              help="Generate borderline probes for all (or specified) families")
@click.option("--output", "output_path", default=None,
              help="Output path for the report (default: auto-generated)")
@click.option("--quiet", is_flag=True, help="Only save, don't print to stdout")
def caseforge(
    family: str | None,
    case_type: str,
    count: int,
    shape: str,
    calibrate_path: str | None,
    borderline_mode: bool,
    output_path: str | None,
    quiet: bool,
):
    """Generate draft case candidates for known data gaps."""
    import json
    from agent_arena.caseforge import forge_cases, render_caseforge_report, candidate_to_yaml_draft
    from agent_arena.schemas import CalibrationReport as CalReport

    cal_report = None
    if calibrate_path:
        data = json.loads(Path(calibrate_path).read_text())
        cal_report = CalReport(**data)

    if not family and not cal_report and not borderline_mode:
        click.echo("Specify --family, --from-calibrate, or --borderline.")
        click.echo("Example: agent-arena caseforge --family overclaim --count 2")
        return

    report = forge_cases(
        family=family,
        case_type=case_type,
        count=count,
        shape=shape,
        calibration_report=cal_report,
        borderline_mode=borderline_mode,
    )

    md = render_caseforge_report(report)

    # Save report
    CASEFORGE_DIR.mkdir(parents=True, exist_ok=True)
    if output_path:
        out = Path(output_path)
    else:
        ts = report.generated_at[:19].replace(":", "-").replace("T", "_")
        out = CASEFORGE_DIR / f"caseforge_{ts}.md"
    out.write_text(md)
    click.echo(f"Caseforge report saved: {out}")

    # Save YAML drafts
    if report.candidates:
        drafts_dir = CASEFORGE_DIR / "drafts"
        drafts_dir.mkdir(exist_ok=True)
        for c in report.candidates:
            yaml_path = drafts_dir / f"{c.candidate_id}.yaml"
            yaml_path.write_text(candidate_to_yaml_draft(c))
        click.echo(f"YAML drafts saved to: {drafts_dir}/")

    click.echo(f"Candidates generated: {report.n_candidates}")

    if not quiet:
        click.echo()
        click.echo(md)


ROUTING_DIR = Path("reports/routing")


@cli.command()
@click.option("--journal", "journal_dir", default=None,
              help="Journal directory (default: .agent_arena)")
@click.option("--family", default=None,
              help="Restrict to specific family (comma-separated for multiple)")
@click.option("--from-insights", "insights_path", default=None,
              help="Path to pre-computed insights report JSON")
@click.option("--from-calibrate", "calibrate_path", default=None,
              help="Path to pre-computed calibration report JSON")
@click.option("--output", "output_path", default=None,
              help="Output path for the routing report (default: auto-generated)")
@click.option("--quiet", is_flag=True, help="Only save, don't print to stdout")
def route(
    journal_dir: str | None,
    family: str | None,
    insights_path: str | None,
    calibrate_path: str | None,
    output_path: str | None,
    quiet: bool,
):
    """Generate Gen 4 routing recommendations for run strategies."""
    import json
    from agent_arena.router import route_from_reports, route_from_entries, render_routing_report
    from agent_arena.schemas import InsightsReport as IR, CalibrationReport as CR

    families = [f.strip() for f in family.split(",")] if family else None

    # Load pre-computed reports if provided
    if insights_path:
        data = json.loads(Path(insights_path).read_text())
        insights = IR(**data)
        cal_report = None
        if calibrate_path:
            cal_data = json.loads(Path(calibrate_path).read_text())
            cal_report = CR(**cal_data)
        report = route_from_reports(insights, cal_report, families)
    else:
        # Compute from journal entries
        from agent_arena.journal import read_entries
        entries = read_entries(journal_dir)
        if not entries:
            click.echo("No journal entries found. Run evaluations first.")
            click.echo("Hint: journal entries are stored in .agent_arena/journal.jsonl")
            return
        click.echo(f"Analyzing {len(entries)} journal entries for routing...")
        report = route_from_entries(entries, families)

    md = render_routing_report(report)

    # Save
    ROUTING_DIR.mkdir(parents=True, exist_ok=True)
    if output_path:
        out = Path(output_path)
    else:
        ts = report.generated_at[:19].replace(":", "-").replace("T", "_")
        out = ROUTING_DIR / f"routing_{ts}.md"

    out.write_text(md)
    click.echo(f"Routing report saved: {out}")
    click.echo(f"Recommendations: {report.n_recommendations}")

    if not quiet:
        click.echo()
        click.echo(md)


DISAGREEMENT_DIR = Path("reports/disagreement")


@cli.command("disagreement-lab")
@click.option("--journal", "journal_dir", default=None,
              help="Journal directory (default: .agent_arena)")
@click.option("--task", "task_id", default=None,
              help="Restrict to specific task ID (comma-separated for multiple)")
@click.option("--family", default=None,
              help="Restrict to specific family (comma-separated for multiple)")
@click.option("--min-entropy", "min_entropy", default=0.0, type=float,
              help="Minimum disagreement entropy to include (default: 0.0)")
@click.option("--output", "output_path", default=None,
              help="Output path for the report (default: auto-generated)")
@click.option("--quiet", is_flag=True, help="Only save, don't print to stdout")
def disagreement_lab(
    journal_dir: str | None,
    task_id: str | None,
    family: str | None,
    min_entropy: float,
    output_path: str | None,
    quiet: bool,
):
    """Analyze cross-model disagreement with forensic depth."""
    from agent_arena.journal import read_entries
    from agent_arena.disagreement_lab import analyze_disagreements, render_disagreement_report

    entries = read_entries(journal_dir)
    if not entries:
        click.echo("No journal entries found. Run evaluations first.")
        click.echo("Hint: journal entries are stored in .agent_arena/journal.jsonl")
        return

    task_ids = [t.strip() for t in task_id.split(",")] if task_id else None
    families = [f.strip() for f in family.split(",")] if family else None

    click.echo(f"Analyzing {len(entries)} journal entries for disagreement...")
    report = analyze_disagreements(
        entries,
        task_ids=task_ids,
        families=families,
        min_entropy=min_entropy,
    )

    md = render_disagreement_report(report)

    # Save
    DISAGREEMENT_DIR.mkdir(parents=True, exist_ok=True)
    if output_path:
        out = Path(output_path)
    else:
        ts = report.generated_at[:19].replace(":", "-").replace("T", "_")
        out = DISAGREEMENT_DIR / f"disagreement_{ts}.md"

    out.write_text(md)
    click.echo(f"Disagreement report saved: {out}")
    click.echo(f"Disagreement cases: {report.n_disagreement_cases}")
    click.echo(f"Borderline signals: {report.n_borderline_signals}")
    click.echo(f"Gold-review signals: {report.n_gold_review_signals}")

    if not quiet:
        click.echo()
        click.echo(md)


# ---------------------------------------------------------------------------
# Gen 6: Audit Trail / Decision Log
# ---------------------------------------------------------------------------

@cli.group("audit-log")
def audit_log():
    """Gen 6 Audit Trail — log and review human decisions."""
    pass


@audit_log.command("add")
@click.option("--type", "decision_type", required=True,
              type=click.Choice([
                  "gold_review_decision", "category_refinement_decision",
                  "routing_decision", "case_candidate_review",
                  "calibration_proposal_decision", "disagreement_resolution",
                  "workflow_note",
              ]),
              help="Decision type")
@click.option("--target", required=True, help="Target (case id, category, model, etc.)")
@click.option("--target-kind", "target_kind", default="case",
              type=click.Choice(["case", "category", "model", "route",
                                 "proposal", "candidate", "workflow"]),
              help="Target kind")
@click.option("--decision", "decision_outcome", required=True,
              type=click.Choice(["accepted", "rejected", "deferred",
                                 "partially_accepted"]),
              help="Decision outcome")
@click.option("--source", "source_module", default="manual",
              type=click.Choice(["calibrate", "caseforge", "router",
                                 "disagreement_lab", "insights", "manual"]),
              help="Source module")
@click.option("--reason", default="", help="Reason for the decision")
@click.option("--reviewer", default="", help="Who made the decision")
@click.option("--notes", default="", help="Additional notes")
@click.option("--before", "before_state", default="", help="State before change")
@click.option("--after", "after_state", default="", help="State after change")
@click.option("--follow-up", "follow_up_action", default="",
              help="Follow-up action to take")
@click.option("--journal", "journal_dir", default=None,
              help="Base directory (default: .agent_arena)")
def audit_add(
    decision_type: str,
    target: str,
    target_kind: str,
    decision_outcome: str,
    source_module: str,
    reason: str,
    reviewer: str,
    notes: str,
    before_state: str,
    after_state: str,
    follow_up_action: str,
    journal_dir: str | None,
):
    """Log a human decision."""
    from agent_arena.audit_trail import log_decision, generate_decision_id
    from agent_arena.schemas import DecisionEntry

    entry = DecisionEntry(
        decision_id=generate_decision_id(),
        decision_type=decision_type,
        target=target,
        target_kind=target_kind,
        source_module=source_module,
        decision=decision_outcome,
        reason=reason,
        reviewer=reviewer,
        notes=notes,
        before_state=before_state,
        after_state=after_state,
        follow_up_action=follow_up_action,
    )

    path = log_decision(entry, journal_dir)
    click.echo(f"Decision logged: {entry.decision_id}")
    click.echo(f"  Type: {decision_type}")
    click.echo(f"  Target: {target} ({target_kind})")
    click.echo(f"  Decision: {decision_outcome}")
    click.echo(f"  File: {path}")


@audit_log.command("summary")
@click.option("--journal", "journal_dir", default=None,
              help="Base directory (default: .agent_arena)")
@click.option("--quiet", is_flag=True, help="Only save, don't print")
def audit_summary(journal_dir: str | None, quiet: bool):
    """Show audit trail summary."""
    from agent_arena.audit_trail import (
        read_decisions, build_summary, module_effectiveness,
        render_audit_summary, render_module_effectiveness,
    )

    decisions = read_decisions(journal_dir)
    if not decisions:
        click.echo("No decisions recorded yet.")
        click.echo("Use: agent-arena audit-log add --type ... --target ... --decision ...")
        return

    summary = build_summary(decisions)
    effectiveness = module_effectiveness(decisions)

    md = render_audit_summary(summary)
    md += "\n" + render_module_effectiveness(effectiveness)

    click.echo(f"Total decisions: {summary.total_decisions}")
    click.echo(f"Acceptance rate: {summary.acceptance_rate:.0%}")
    click.echo(f"Deferred: {summary.deferred_count}")

    if not quiet:
        click.echo()
        click.echo(md)


@audit_log.command("recent")
@click.option("--n", "count", default=10, type=int,
              help="Number of recent decisions to show")
@click.option("--journal", "journal_dir", default=None,
              help="Base directory (default: .agent_arena)")
def audit_recent(count: int, journal_dir: str | None):
    """Show recent decisions."""
    from agent_arena.audit_trail import query_recent

    recent = query_recent(count, journal_dir)
    if not recent:
        click.echo("No decisions recorded yet.")
        return

    click.echo(f"Last {len(recent)} decision(s):")
    click.echo()
    for d in reversed(recent):
        click.echo(f"  [{d.decision_id}] {d.decision_type}")
        click.echo(f"    Target: {d.target} ({d.target_kind})")
        click.echo(f"    Decision: {d.decision}")
        if d.reason:
            click.echo(f"    Reason: {d.reason}")
        if d.source_module:
            click.echo(f"    Source: {d.source_module}")
        if d.reviewer:
            click.echo(f"    Reviewer: {d.reviewer}")
        click.echo()


@audit_log.command("list")
@click.option("--type", "decision_type", default=None,
              help="Filter by decision type")
@click.option("--decision", "decision_outcome", default=None,
              help="Filter by outcome (accepted/rejected/deferred)")
@click.option("--source", "source_module", default=None,
              help="Filter by source module")
@click.option("--target", default=None,
              help="Filter by target")
@click.option("--journal", "journal_dir", default=None,
              help="Base directory (default: .agent_arena)")
def audit_list(
    decision_type: str | None,
    decision_outcome: str | None,
    source_module: str | None,
    target: str | None,
    journal_dir: str | None,
):
    """List decisions with optional filters."""
    from agent_arena.audit_trail import read_decisions

    decisions = read_decisions(journal_dir)
    if decision_type:
        decisions = [d for d in decisions if d.decision_type == decision_type]
    if decision_outcome:
        decisions = [d for d in decisions if d.decision == decision_outcome]
    if source_module:
        decisions = [d for d in decisions if d.source_module == source_module]
    if target:
        decisions = [d for d in decisions if d.target == target]

    if not decisions:
        click.echo("No matching decisions found.")
        return

    click.echo(f"{len(decisions)} decision(s) found:")
    click.echo()
    for d in decisions:
        click.echo(
            f"  [{d.decision_id}] {d.decision_type} | "
            f"{d.target} ({d.target_kind}) | "
            f"{d.decision} | {d.source_module}"
        )
    click.echo()


@audit_log.command("dependency-summary")
@click.option("--journal", "journal_dir", default=None,
              help="Base directory (default: .agent_arena)")
@click.option("--quiet", is_flag=True, help="Only print summary stats")
def audit_dependency_summary(journal_dir: str | None, quiet: bool):
    """Show upstream dependency / error propagation summary (Gen 6.1)."""
    from agent_arena.audit_trail import (
        read_decisions, build_dependency_summary, render_dependency_summary,
    )

    decisions = read_decisions(journal_dir)
    if not decisions:
        click.echo("No decisions recorded yet.")
        return

    summary = build_dependency_summary(decisions)
    click.echo(f"Total decisions: {summary.total_decisions}")
    click.echo(f"With upstream dependency: {summary.decisions_with_upstream}")
    click.echo(f"Override rate: {summary.override_rate:.0%} ({summary.override_count})")
    click.echo(f"Weak-basis accepted: {summary.weak_basis_accepted}")
    click.echo(f"Propagation chains: {len(summary.propagation_chains)}")

    if not quiet:
        md = render_dependency_summary(summary)
        click.echo()
        click.echo(md)


@audit_log.command("trace")
@click.argument("decision_id")
@click.option("--journal", "journal_dir", default=None,
              help="Base directory (default: .agent_arena)")
def audit_trace(decision_id: str, journal_dir: str | None):
    """Trace a single decision's upstream provenance (Gen 6.1)."""
    from agent_arena.audit_trail import (
        read_decisions, trace_decision, render_trace,
    )

    decisions = read_decisions(journal_dir)
    trace = trace_decision(decision_id, decisions)

    if trace is None:
        click.echo(f"Decision not found: {decision_id}")
        return

    md = render_trace(trace)
    click.echo(md)


# ---------------------------------------------------------------------------
# Gen 7: Pipeline — workflow orchestration
# ---------------------------------------------------------------------------

PIPELINE_DIR = Path("reports/pipeline")


@cli.command()
@click.option("--journal", "journal_dir", default=None,
              help="Journal directory (default: .agent_arena)")
@click.option("--family", default=None,
              help="Restrict to specific family (comma-separated)")
@click.option("--task", "task_id", default=None,
              help="Restrict to specific task ID (comma-separated)")
@click.option("--include-caseforge", is_flag=True,
              help="Include Caseforge candidate generation")
@click.option("--dry-run", is_flag=True,
              help="Plan only — show what would run without executing")
@click.option("--output", "output_path", default=None,
              help="Output path for the pipeline report")
@click.option("--quiet", is_flag=True,
              help="Only save, don't print to stdout")
def pipeline(
    journal_dir: str | None,
    family: str | None,
    task_id: str | None,
    include_caseforge: bool,
    dry_run: bool,
    output_path: str | None,
    quiet: bool,
):
    """Run the full meta-stack pipeline (Gen 7 orchestration)."""
    from agent_arena.pipeline import run_pipeline, render_pipeline_report

    families = [f.strip() for f in family.split(",")] if family else None
    task_ids = [t.strip() for t in task_id.split(",")] if task_id else None

    if dry_run:
        click.echo("Pipeline — DRY RUN (no outputs written)")
    else:
        click.echo("Pipeline — running full meta-stack...")

    click.echo()

    result = run_pipeline(
        journal_dir=journal_dir,
        families=families,
        task_ids=task_ids,
        include_caseforge=include_caseforge,
        dry_run=dry_run,
        audit_dir=journal_dir,
    )

    if result.n_entries == 0:
        click.echo("No journal entries found. Run evaluations first.")
        click.echo("Hint: journal entries are stored in .agent_arena/journal.jsonl")
        return

    # Print step summary
    for step in result.steps:
        icon = {"completed": "+", "skipped": "-", "planned": "?"}
        mark = icon.get(step.status, " ")
        click.echo(f"  [{mark}] {step.name}: {step.detail}")
    click.echo()

    # Summary line
    completed = sum(1 for s in result.steps if s.status == "completed")
    review_n = len(result.items_requiring_review)
    click.echo(f"Steps completed: {completed}")
    click.echo(f"Items requiring review: {review_n}")

    if result.next_actions:
        click.echo()
        click.echo("Recommended next actions:")
        for i, a in enumerate(result.next_actions, 1):
            click.echo(f"  {i}. {a}")

    # Render and save report
    md = render_pipeline_report(result)

    if not dry_run:
        PIPELINE_DIR.mkdir(parents=True, exist_ok=True)
        if output_path:
            out = Path(output_path)
        else:
            ts = result.generated_at[:19].replace(":", "-").replace("T", "_")
            out = PIPELINE_DIR / f"pipeline_{ts}.md"
        out.write_text(md)
        click.echo(f"\nPipeline report saved: {out}")

    if not quiet:
        click.echo()
        click.echo(md)


@cli.command("iaa")
@click.option("--sheet-a", "sheet_a", default=None, help="annotator A response sheet CSV")
@click.option("--sheet-b", "sheet_b", default=None, help="annotator B response sheet CSV")
@click.option("--sheet-c", "sheet_c", default=None, help="annotator C response sheet CSV")
@click.option("--index", "index_path", required=True,
              help="internal blind_case_index.csv (internal_only)")
@click.option("--tasks-dir", "tasks_dir", default="tasks/study_forensics",
              help="active case YAML directory (for gold mapping)")
@click.option("--out", "out_dir", default=None,
              help="output run dir (defaults to analysis/phase5_05c_iaa_results/<run_id>)")
@click.option("--validate-only", is_flag=True,
              help="validate sheet structure only; do not compute agreement")
@click.option("--allow-partial", is_flag=True,
              help="allow a STRUCTURE-VALIDATION-ONLY run on incomplete sheets (no disposition)")
def iaa(sheet_a, sheet_b, sheet_c, index_path, tasks_dir, out_dir, validate_only, allow_partial):
    """Phase 5.05c: import + validate blind annotator sheets and compute proxy IAA.

    Final agreement analysis runs only when all supplied sheets are completed and
    valid. Refuses to fabricate results from blank templates.
    """
    from datetime import datetime, timezone

    from agent_arena import iaa_analysis as iaa_mod

    sheets = {aid: p for aid, p in
              (("A", sheet_a), ("B", sheet_b), ("C", sheet_c)) if p}
    if not sheets:
        raise click.UsageError("provide at least one of --sheet-a/--sheet-b/--sheet-c")

    expected = iaa_mod.load_expected_ids(index_path)
    if validate_only:
        for aid, p in sheets.items():
            v = iaa_mod.validate_sheet(p, expected, aid)
            status = ("BLANK TEMPLATE" if v.is_blank_template
                      else ("COMPLETED" if v.completed else "PARTIAL"))
            click.echo(f"[{aid}] {Path(p).name}: {status} — "
                       f"errors={len(v.errors)} warnings={len(v.warnings)}")
            for e in v.errors:
                click.echo(f"    ERROR: {e}")
        return

    run_id = f"iaa_{datetime.now(timezone.utc):%Y%m%d_%H%M%S}"
    target = out_dir or f"analysis/phase5_05c_iaa_results/{run_id}"
    result = iaa_mod.analyze(sheets, index_path, tasks_dir, target,
                             allow_partial=allow_partial)
    click.echo(f"status: {result['status']}")
    if result["status"] == "REFUSED":
        click.echo(f"  {result['reason']}")
    elif result["status"] == "STRUCTURE_VALIDATION_ONLY":
        click.echo(f"  {result['banner']} -> {result['out_dir']}")
    else:
        click.echo(f"  disposition: {result['metrics']['disposition']['level']} -> {result['out_dir']}")


@cli.command("packet-integrity")
@click.option("--task-dir", "task_dir", default=None,
              help="case YAML directory (defaults to tasks/study_forensics); sealed paths refused")
@click.option("--case-id", "case_id", default=None, help="check a single case by id")
@click.option("--include-retired", is_flag=True, help="include retired cases")
@click.option("--json", "as_json", is_flag=True, help="emit machine-readable JSON to stdout")
@click.option("--output", "output_path", default=None, help="write the JSON report to this path")
@click.option("--quiet", is_flag=True, help="suppress the human-readable summary")
def packet_integrity(task_dir, case_id, include_retired, as_json, output_path, quiet):
    """Phase 6.0: offline packet-integrity check (development material only).

    Reconstructs each model-facing packet with no model call and reports two
    SEPARATE outcomes — semantic preservation and contamination/leakage. Exit
    code is non-zero if any case fails either check (usable as a CI/pre-commit
    gate). Refuses sealed/out-of-scope directories.
    """
    from agent_arena.packet_integrity import (
        SealedPathError,
        render_report_text,
        run_packet_integrity,
    )

    try:
        report = run_packet_integrity(
            task_dir=task_dir, case_id=case_id, include_retired=include_retired,
        )
    except SealedPathError as e:
        raise click.ClickException(str(e))

    if output_path:
        Path(output_path).write_text(json.dumps(report.as_dict(), indent=2))
        if not quiet:
            click.echo(f"JSON report written: {output_path}")
    if as_json:
        click.echo(json.dumps(report.as_dict(), indent=2))
    elif not quiet:
        click.echo(render_report_text(report), nl=False)

    if not report.ok:
        raise SystemExit(1)


@cli.command("forensic-report")
@click.option("--input", "input_path", required=True,
              help="Path to a claim-forensics report INPUT JSON (see phase6_3 fixtures)")
@click.option("--format", "fmt", default="markdown",
              type=click.Choice(["markdown", "json", "summary"]),
              help="full markdown (default), machine-readable json, or executive summary")
@click.option("--output", "output_path", default=None,
              help="write output to this path instead of stdout")
def forensic_report_cmd(input_path: str, fmt: str, output_path: str | None):
    """Phase 6.3: render a deterministic claim-forensics report from an analysis input.

    Offline and deterministic — no model call. The input is a single analysis object
    (schema: analysis/phase6_3_report_prototype/forensic_report_schema.json; synthetic
    fixtures alongside it). Missing/invalid confidence stays explicit and is never
    coerced to 0.0; a parser failure yields a failure report, not a verdict.
    """
    from agent_arena.forensic_report import (
        ForensicReportError,
        build_forensic_report,
        canonical_report_bytes,
        render_executive_summary,
        render_forensic_report_markdown,
    )
    from agent_arena.release_boundary import (
        DIAGNOSTIC_ARTIFACT_ROLE,
        is_authoritative_release_path,
    )

    raw = json.loads(Path(input_path).read_text())
    try:
        report = build_forensic_report(raw)
    except ForensicReportError as e:
        raise click.ClickException(f"invalid forensic-report input: {e}") from e

    if fmt == "json":
        content = canonical_report_bytes({
            "artifact_role": DIAGNOSTIC_ARTIFACT_ROLE,
            "official_release_authorized": False,
            "forensic_report": report,
        }).decode("utf-8")
    elif fmt == "summary":
        content = render_executive_summary(report)
    else:
        content = render_forensic_report_markdown(report)

    if output_path:
        if is_authoritative_release_path(output_path):
            raise click.ClickException(
                "diagnostic forensic-report cannot write into the official release namespace"
            )
        Path(output_path).write_text(content)
        click.echo(f"diagnostic non-release forensic report written: {output_path}")
    else:
        click.echo(content, nl=False)
    raise SystemExit(2)


@cli.command("official-release")
@click.option("--input", "input_path", required=True,
              help="Path to a canonical prospective release-object JSON")
@click.option("--output-root", required=True,
              help="Root under which the controlled official release namespace is created")
@click.option("--repo-root", default=".", show_default=True,
              help="Authenticated Git root containing the tracked release-source manifest")
def official_release_cmd(input_path: str, output_root: str, repo_root: str):
    """Execute the mandatory Phase-7B contract and atomically write an official package."""
    from agent_arena.release_boundary import (
        ReleaseBoundaryError,
        load_release_object,
        release_official_artifact,
    )

    try:
        release_object = load_release_object(input_path)
    except ReleaseBoundaryError as exc:
        raise click.ClickException(str(exc)) from exc
    result = release_official_artifact(
        release_object, output_root=output_root, repo_root=repo_root,
    )
    if not result.released:
        detail = "; ".join(result.errors) or result.status
        raise click.ClickException(f"official release denied [{result.status}]: {detail}")
    click.echo(f"official release written: {result.package_path}")


@cli.command("phase5b-haiku-full-replication")
def phase5b_haiku_full_replication_cmd():
    """Run the one registered, one-shot Phase-5B Haiku full replication."""
    from agent_arena import full_replication_contract as frc
    from agent_arena.phase7a_real_run import run_registered_condition

    try:
        result = run_registered_condition(frc.PLAN_ID, frc.ARM_ID, frc.EXPECTED_MODEL_KEY)
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc
    freeze = result["freeze"]
    usage = result.get("usage_cost") or {}
    click.echo(
        "Phase-5B Haiku full replication: "
        f"terminal={freeze['terminal_attempts']}/{frc.EXPECTED_SLOTS} "
        f"classification_valid={freeze['classification_valid_calls']} "
        f"calibration_valid={freeze['calibration_valid_calls']} "
        f"cost_usd={usage.get('calculated_cost_usd')}"
    )
    if freeze["terminal_attempts"] != frc.EXPECTED_SLOTS:
        raise SystemExit(2)


@cli.command("phase5b-sonnet-full-replication")
def phase5b_sonnet_full_replication_cmd():
    """Run the one registered, one-shot Phase-5B Sonnet (S1) full replication.

    Requires a separate, explicit human authorization of the Sonnet plan
    (``analysis/phase5b_sonnet_full_replication/execution_plan.json``); the
    delivered plan is NOT_AUTHORIZED, so this fails closed until then.
    """
    from agent_arena import full_replication_contract as frc
    from agent_arena.phase7a_real_run import run_registered_condition

    profile = frc.SONNET
    try:
        result = run_registered_condition(profile.plan_id, profile.arm_id, profile.model_key)
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc
    freeze = result["freeze"]
    usage = result.get("usage_cost") or {}
    click.echo(
        "Phase-5B Sonnet full replication: "
        f"terminal={freeze['terminal_attempts']}/{frc.EXPECTED_SLOTS} "
        f"classification_valid={freeze['classification_valid_calls']} "
        f"calibration_valid={freeze['calibration_valid_calls']} "
        f"cost_usd={usage.get('calculated_cost_usd')}"
    )
    if freeze["terminal_attempts"] != frc.EXPECTED_SLOTS:
        raise SystemExit(2)
