"""Tests for Gen 7 Pipeline — agent-arena v0.6.12.

Tests cover:
- Full pipeline execution with small dataset
- Step ordering and completeness
- Optional steps (caseforge enable/disable)
- Dry-run mode
- Pipeline report generation
- Audit trail workflow note
- Filter options (family, task)
- No hidden mutation of data
- Module output propagation
"""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from agent_arena.schemas import RunJournalEntry, DecisionEntry
from agent_arena.journal import append_entries, read_entries
from agent_arena.audit_trail import read_decisions
from agent_arena.pipeline import (
    run_pipeline,
    render_pipeline_report,
    PipelineResult,
    PipelineStep,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _entry(**kwargs) -> RunJournalEntry:
    """Create a RunJournalEntry with defaults."""
    defaults = dict(
        run_id="run_pipe_001",
        timestamp="2026-04-07T10:00:00Z",
        task_id="case_pipe_001",
        task_family="solid",
        task_type="study_forensics",
        agent_id="sonnet",
        model="sonnet",
        total_score=75.0,
        correctness=0.9,
        support_strength=0.7,
        structural_reasoning=0.8,
        insight_depth=0.6,
        mechanism_quality=0.7,
        self_monitoring_quality=0.7,
        failure_categories=[],
        forensic_flag_types=[],
        reasoning_integrity_class="well_supported",
        decision_category="",
        probability_estimate=None,
        confidence=0.85,
        confidence_state="VALID",
        final_answer="solid",
        n_contradictions=0,
        n_intermediate_errors=0,
    )
    defaults.update(kwargs)
    return RunJournalEntry(**defaults)


def _populate_journal(tmp_path) -> list[RunJournalEntry]:
    """Create a small but diagnostically interesting journal dataset."""
    entries = []

    # Case 1: solid — all models agree
    for model, score in [("sonnet", 80.0), ("haiku", 70.0), ("opus", 85.0)]:
        entries.append(_entry(
            run_id=f"run_{model}_solid",
            task_id="case_solid_001", task_family="solid",
            agent_id=model, model=model,
            total_score=score, correctness=1.0,
            final_answer="solid",
        ))

    # Case 2: overclaim — haiku wrong
    entries.append(_entry(
        run_id="run_sonnet_oc", task_id="case_overclaim_002",
        task_family="overclaim", agent_id="sonnet", model="sonnet",
        total_score=78.0, correctness=1.0, final_answer="overclaim",
    ))
    entries.append(_entry(
        run_id="run_haiku_oc", task_id="case_overclaim_002",
        task_family="overclaim", agent_id="haiku", model="haiku",
        total_score=42.0, correctness=0.0, final_answer="solid",
        failure_categories=["wrong_label"],
        reasoning_integrity_class="brittle",
    ))
    entries.append(_entry(
        run_id="run_opus_oc", task_id="case_overclaim_002",
        task_family="overclaim", agent_id="opus", model="opus",
        total_score=84.0, correctness=1.0, final_answer="overclaim",
    ))

    # Case 3: correlation — all wrong
    for model, score in [("sonnet", 35.0), ("haiku", 30.0), ("opus", 38.0)]:
        entries.append(_entry(
            run_id=f"run_{model}_corr",
            task_id="case_corr_003", task_family="correlation_vs_causation",
            agent_id=model, model=model,
            total_score=score, correctness=0.0, final_answer="solid",
            failure_categories=["wrong_label"],
            confidence=0.85,
            reasoning_integrity_class="accidental",
        ))

    append_entries(entries, base_dir=tmp_path)
    return entries


# ---------------------------------------------------------------------------
# 1. Full Pipeline Execution
# ---------------------------------------------------------------------------

class TestFullPipeline:
    def test_pipeline_runs_to_completion(self, tmp_path):
        _populate_journal(tmp_path)
        result = run_pipeline(journal_dir=tmp_path, audit_dir=tmp_path)
        assert result is not None
        assert result.n_entries == 9

        # All expected steps present
        step_names = [s.name for s in result.steps]
        assert "load_journal" in step_names
        assert "insights" in step_names
        assert "calibrate" in step_names
        assert "router" in step_names
        assert "disagreement_lab" in step_names
        assert "audit_trail" in step_names

    def test_pipeline_step_order(self, tmp_path):
        _populate_journal(tmp_path)
        result = run_pipeline(journal_dir=tmp_path, audit_dir=tmp_path)
        completed = [s.name for s in result.steps if s.status == "completed"]
        # Order must be: journal → insights → calibrate → router → disagree → audit
        expected_order = [
            "load_journal", "insights", "calibrate",
            "router", "disagreement_lab", "audit_trail",
        ]
        for i, name in enumerate(expected_order):
            assert completed[i] == name, f"Step {i} should be {name}, got {completed[i]}"

    def test_all_steps_completed(self, tmp_path):
        _populate_journal(tmp_path)
        result = run_pipeline(journal_dir=tmp_path, audit_dir=tmp_path)
        completed = [s for s in result.steps if s.status == "completed"]
        skipped = [s for s in result.steps if s.status == "skipped"]
        # caseforge should be skipped by default
        assert len(completed) == 6  # journal + 4 modules + audit
        assert len(skipped) == 1
        assert skipped[0].name == "caseforge"


# ---------------------------------------------------------------------------
# 2. Module Outputs Propagated
# ---------------------------------------------------------------------------

class TestModuleOutputs:
    def test_insights_output(self, tmp_path):
        _populate_journal(tmp_path)
        result = run_pipeline(journal_dir=tmp_path, audit_dir=tmp_path)
        assert result.insights is not None
        assert len(result.insights.model_profiles) == 3

    def test_calibration_output(self, tmp_path):
        _populate_journal(tmp_path)
        result = run_pipeline(journal_dir=tmp_path, audit_dir=tmp_path)
        assert result.calibration is not None
        assert result.calibration.generated_at != ""

    def test_routing_output(self, tmp_path):
        _populate_journal(tmp_path)
        result = run_pipeline(journal_dir=tmp_path, audit_dir=tmp_path)
        assert result.routing_report is not None
        assert result.routing_report.n_recommendations >= 1

    def test_disagreement_output(self, tmp_path):
        _populate_journal(tmp_path)
        result = run_pipeline(journal_dir=tmp_path, audit_dir=tmp_path)
        assert result.disagreement_report is not None
        assert result.disagreement_report.n_cases_analyzed >= 1


# ---------------------------------------------------------------------------
# 3. Optional Caseforge
# ---------------------------------------------------------------------------

class TestCaseforgeOption:
    def test_caseforge_skipped_by_default(self, tmp_path):
        _populate_journal(tmp_path)
        result = run_pipeline(journal_dir=tmp_path, audit_dir=tmp_path)
        assert result.caseforge_report is None
        cf_step = [s for s in result.steps if s.name == "caseforge"]
        assert len(cf_step) == 1
        assert cf_step[0].status == "skipped"

    def test_caseforge_included_when_enabled(self, tmp_path):
        _populate_journal(tmp_path)
        result = run_pipeline(
            journal_dir=tmp_path, audit_dir=tmp_path,
            include_caseforge=True,
        )
        assert result.caseforge_report is not None
        cf_step = [s for s in result.steps if s.name == "caseforge"]
        assert cf_step[0].status == "completed"

    def test_caseforge_produces_candidates(self, tmp_path):
        _populate_journal(tmp_path)
        result = run_pipeline(
            journal_dir=tmp_path, audit_dir=tmp_path,
            include_caseforge=True,
        )
        # Data gaps should produce candidates
        assert result.caseforge_report.n_candidates >= 1


# ---------------------------------------------------------------------------
# 4. Dry-Run Mode
# ---------------------------------------------------------------------------

class TestDryRun:
    def test_dry_run_no_execution(self, tmp_path):
        _populate_journal(tmp_path)
        result = run_pipeline(
            journal_dir=tmp_path, audit_dir=tmp_path,
            dry_run=True,
        )
        assert result.dry_run is True
        # No module outputs should be set
        assert result.insights is None
        assert result.calibration is None
        assert result.routing_report is None
        assert result.disagreement_report is None

    def test_dry_run_shows_planned_steps(self, tmp_path):
        _populate_journal(tmp_path)
        result = run_pipeline(
            journal_dir=tmp_path, audit_dir=tmp_path,
            dry_run=True,
        )
        planned = [s for s in result.steps if s.status == "planned"]
        assert len(planned) >= 4  # insights, calibrate, router, disagree, audit

    def test_dry_run_no_audit_trail_written(self, tmp_path):
        _populate_journal(tmp_path)
        result = run_pipeline(
            journal_dir=tmp_path, audit_dir=tmp_path,
            dry_run=True,
        )
        decisions = read_decisions(tmp_path)
        assert len(decisions) == 0

    def test_dry_run_journal_loaded(self, tmp_path):
        _populate_journal(tmp_path)
        result = run_pipeline(
            journal_dir=tmp_path, audit_dir=tmp_path,
            dry_run=True,
        )
        assert result.n_entries == 9
        journal_step = [s for s in result.steps if s.name == "load_journal"]
        assert journal_step[0].status == "completed"

    def test_dry_run_render_produces_report(self, tmp_path):
        _populate_journal(tmp_path)
        result = run_pipeline(
            journal_dir=tmp_path, audit_dir=tmp_path,
            dry_run=True,
        )
        md = render_pipeline_report(result)
        assert "DRY RUN" in md
        assert "Pipeline Report" in md


# ---------------------------------------------------------------------------
# 5. Pipeline Report
# ---------------------------------------------------------------------------

class TestPipelineReport:
    def test_report_has_all_sections(self, tmp_path):
        _populate_journal(tmp_path)
        result = run_pipeline(journal_dir=tmp_path, audit_dir=tmp_path)
        md = render_pipeline_report(result)
        assert "# Agent Arena" in md
        assert "## Steps Executed" in md
        assert "## Insights Summary" in md
        assert "## Calibration Summary" in md
        assert "## Routing Recommendations" in md
        assert "## Disagreement Findings" in md
        assert "## Audit Trail" in md

    def test_report_includes_review_items(self, tmp_path):
        _populate_journal(tmp_path)
        result = run_pipeline(journal_dir=tmp_path, audit_dir=tmp_path)
        md = render_pipeline_report(result)
        if result.items_requiring_review:
            assert "## Items Requiring Human Review" in md

    def test_report_includes_next_actions(self, tmp_path):
        _populate_journal(tmp_path)
        result = run_pipeline(journal_dir=tmp_path, audit_dir=tmp_path)
        md = render_pipeline_report(result)
        assert "## Recommended Next Actions" in md

    def test_report_has_footer(self, tmp_path):
        _populate_journal(tmp_path)
        result = run_pipeline(journal_dir=tmp_path, audit_dir=tmp_path)
        md = render_pipeline_report(result)
        assert "orchestration only" in md
        assert "No decisions made" in md

    def test_report_length_reasonable(self, tmp_path):
        _populate_journal(tmp_path)
        result = run_pipeline(journal_dir=tmp_path, audit_dir=tmp_path)
        md = render_pipeline_report(result)
        assert len(md) > 500


# ---------------------------------------------------------------------------
# 6. Audit Trail Workflow Note
# ---------------------------------------------------------------------------

class TestAuditTrailNote:
    def test_workflow_note_written(self, tmp_path):
        _populate_journal(tmp_path)
        result = run_pipeline(journal_dir=tmp_path, audit_dir=tmp_path)
        decisions = read_decisions(tmp_path)
        assert len(decisions) == 1
        d = decisions[0]
        assert d.decision_type == "workflow_note"
        assert d.target == "pipeline_run"
        assert d.target_kind == "workflow"
        assert d.source_module == "manual"

    def test_workflow_note_has_provenance(self, tmp_path):
        _populate_journal(tmp_path)
        result = run_pipeline(journal_dir=tmp_path, audit_dir=tmp_path)
        decisions = read_decisions(tmp_path)
        d = decisions[0]
        assert d.upstream_module == "pipeline"
        assert "orchestration" in d.upstream_dependency_summary.lower()
        assert d.dependency_confidence == "high"
        assert d.propagation_risk_level == "low"

    def test_workflow_note_records_steps(self, tmp_path):
        _populate_journal(tmp_path)
        result = run_pipeline(journal_dir=tmp_path, audit_dir=tmp_path)
        decisions = read_decisions(tmp_path)
        d = decisions[0]
        assert "insights" in d.evidence_summary
        assert "calibrate" in d.evidence_summary

    def test_workflow_note_in_result(self, tmp_path):
        _populate_journal(tmp_path)
        result = run_pipeline(journal_dir=tmp_path, audit_dir=tmp_path)
        assert result.audit_note is not None
        assert result.audit_note.decision_id.startswith("dec_")


# ---------------------------------------------------------------------------
# 7. Filters
# ---------------------------------------------------------------------------

class TestFilters:
    def test_family_filter(self, tmp_path):
        _populate_journal(tmp_path)
        result = run_pipeline(
            journal_dir=tmp_path, audit_dir=tmp_path,
            families=["solid"],
        )
        assert result.n_entries == 3  # only solid entries
        assert result.families_filter == ["solid"]

    def test_task_filter(self, tmp_path):
        _populate_journal(tmp_path)
        result = run_pipeline(
            journal_dir=tmp_path, audit_dir=tmp_path,
            task_ids=["case_solid_001"],
        )
        assert result.n_entries == 3  # 3 models on 1 task
        assert result.task_filter == ["case_solid_001"]

    def test_combined_filters(self, tmp_path):
        _populate_journal(tmp_path)
        result = run_pipeline(
            journal_dir=tmp_path, audit_dir=tmp_path,
            families=["overclaim"],
            task_ids=["case_overclaim_002"],
        )
        assert result.n_entries == 3

    def test_filter_no_match(self, tmp_path):
        _populate_journal(tmp_path)
        result = run_pipeline(
            journal_dir=tmp_path, audit_dir=tmp_path,
            families=["nonexistent_family"],
        )
        assert result.n_entries == 0
        # Should only have journal step
        assert len(result.steps) == 1
        assert result.steps[0].name == "load_journal"


# ---------------------------------------------------------------------------
# 8. Empty Journal
# ---------------------------------------------------------------------------

class TestEmptyJournal:
    def test_empty_journal_graceful(self, tmp_path):
        result = run_pipeline(journal_dir=tmp_path, audit_dir=tmp_path)
        assert result.n_entries == 0
        assert result.insights is None
        assert len(result.steps) == 1

    def test_empty_journal_report(self, tmp_path):
        result = run_pipeline(journal_dir=tmp_path, audit_dir=tmp_path)
        md = render_pipeline_report(result)
        assert "Pipeline Report" in md
        assert "0" in md


# ---------------------------------------------------------------------------
# 9. No Hidden Mutation
# ---------------------------------------------------------------------------

class TestNoMutation:
    def test_journal_unchanged_after_pipeline(self, tmp_path):
        entries = _populate_journal(tmp_path)
        original_count = len(entries)

        run_pipeline(journal_dir=tmp_path, audit_dir=tmp_path)

        # Journal should have same entries
        reloaded = read_entries(tmp_path)
        assert len(reloaded) == original_count

    def test_no_gold_label_changes(self, tmp_path):
        """Pipeline must not modify any task/case files."""
        _populate_journal(tmp_path)
        # No task files in tmp_path to begin with — that's the point.
        # Pipeline should not create any task/case YAML files.
        result = run_pipeline(journal_dir=tmp_path, audit_dir=tmp_path)

        # Only decisions.jsonl should be created (audit note)
        files = list(tmp_path.iterdir())
        file_names = {f.name for f in files}
        assert "journal.jsonl" in file_names
        assert "decisions.jsonl" in file_names
        # No YAML files (no case modifications)
        yaml_files = [f for f in files if f.suffix in (".yaml", ".yml")]
        assert yaml_files == []

    def test_only_workflow_note_in_audit(self, tmp_path):
        """Pipeline should only write a workflow_note, not accept/reject."""
        _populate_journal(tmp_path)
        run_pipeline(journal_dir=tmp_path, audit_dir=tmp_path)
        decisions = read_decisions(tmp_path)
        assert len(decisions) == 1
        assert decisions[0].decision_type == "workflow_note"
        # Not accepting or rejecting anything
        assert decisions[0].decision == "accepted"  # workflow note is "accepted" as logged


# ---------------------------------------------------------------------------
# 10. Review Items and Next Actions
# ---------------------------------------------------------------------------

class TestReviewItems:
    def test_review_items_populated(self, tmp_path):
        _populate_journal(tmp_path)
        result = run_pipeline(journal_dir=tmp_path, audit_dir=tmp_path)
        # With our dataset (all-wrong correlation, disagreement overclaim)
        # there should be review items
        assert len(result.items_requiring_review) >= 1

    def test_next_actions_populated(self, tmp_path):
        _populate_journal(tmp_path)
        result = run_pipeline(journal_dir=tmp_path, audit_dir=tmp_path)
        assert len(result.next_actions) >= 1

    def test_review_items_have_source_module(self, tmp_path):
        _populate_journal(tmp_path)
        result = run_pipeline(journal_dir=tmp_path, audit_dir=tmp_path)
        for item in result.items_requiring_review:
            # Each item should indicate which module flagged it
            assert "[" in item and "]" in item


# ---------------------------------------------------------------------------
# 11. Multiple Pipeline Runs
# ---------------------------------------------------------------------------

class TestMultipleRuns:
    def test_second_run_appends_audit_note(self, tmp_path):
        _populate_journal(tmp_path)
        run_pipeline(journal_dir=tmp_path, audit_dir=tmp_path)
        run_pipeline(journal_dir=tmp_path, audit_dir=tmp_path)
        decisions = read_decisions(tmp_path)
        assert len(decisions) == 2
        assert all(d.decision_type == "workflow_note" for d in decisions)

    def test_runs_have_different_ids(self, tmp_path):
        _populate_journal(tmp_path)
        r1 = run_pipeline(journal_dir=tmp_path, audit_dir=tmp_path)
        r2 = run_pipeline(journal_dir=tmp_path, audit_dir=tmp_path)
        assert r1.audit_note.decision_id != r2.audit_note.decision_id
