"""Tests for Gen 2 Calibrate — agent-arena v0.6.7.

Tests cover:
- FP reduction candidates from mock data
- Gold review candidates from stable disagreement
- Category refinement candidates from shape decay
- Model confusion candidates from label confusions
- Data gap candidates from thin coverage
- Full pipeline integration
- Report rendering
- Empty input handling
"""

from __future__ import annotations

import pytest

from agent_arena.confidence_validity import INVALID, MISSING, VALID
from agent_arena.schemas import (
    CalibrationProposal,
    CalibrationReport,
    RunJournalEntry,
)
from agent_arena.calibrate import (
    _propose_fp_reduction,
    _propose_gold_review,
    _propose_category_refinement,
    _propose_model_confusion,
    _propose_data_gaps,
    generate_calibration_report,
    render_calibration_report,
)


# ---------------------------------------------------------------------------
# Test data factory
# ---------------------------------------------------------------------------

def _entry(**kwargs) -> RunJournalEntry:
    """Create a RunJournalEntry with defaults."""
    defaults = dict(
        run_id="run_001",
        timestamp="2026-04-01T00:00:00Z",
        task_id="task-001",
        task_family="solid",
        task_type="study_forensics",
        agent_id="test-agent",
        model="claude-sonnet",
        total_score=75.0,
        correctness=0.9,
        support_strength=0.6,
        structural_reasoning=0.7,
        insight_depth=0.8,
        mechanism_quality=0.5,
        self_monitoring_quality=0.4,
        failure_categories=[],
        forensic_flag_types=[],
        reasoning_integrity_class="well_supported",
        decision_category="",
        probability_estimate=None,
        confidence=0.85,
        confidence_state=VALID,
        final_answer="solid",
        n_contradictions=0,
        n_intermediate_errors=0,
    )
    defaults.update(kwargs)
    return RunJournalEntry(**defaults)


# ---------------------------------------------------------------------------
# 1. FP Reduction Candidates
# ---------------------------------------------------------------------------

class TestFPReduction:
    def test_solid_overflagging_detected(self):
        """When solid cases get misclassified frequently, propose FP reduction."""
        entries = [
            _entry(
                run_id=f"r{i}", task_id=f"t{i}", task_family="solid",
                final_answer="overclaim",
                failure_categories=["wrong_answer"],
                forensic_flag_types=["study_forensics_overflagging"],
            )
            for i in range(3)
        ] + [
            _entry(
                run_id="r_ok", task_id="t_ok", task_family="solid",
                final_answer="solid",
            ),
        ]
        proposals = _propose_fp_reduction(entries)
        assert any(p.target == "solid_case_overflagging" for p in proposals)

    def test_per_model_fp_detected(self):
        """A model that consistently misclassifies solid cases."""
        entries = [
            _entry(
                run_id=f"r{i}", task_id=f"t{i}", task_family="solid",
                model="haiku", agent_id="haiku",
                final_answer="overclaim",
                failure_categories=["wrong_answer"],
            )
            for i in range(3)
        ] + [
            _entry(
                run_id="r_ok", task_id="t_ok", task_family="solid",
                model="haiku", agent_id="haiku",
                final_answer="solid",
            ),
        ]
        proposals = _propose_fp_reduction(entries)
        model_proposals = [p for p in proposals if p.target == "haiku"]
        assert len(model_proposals) >= 1
        assert "haiku" in model_proposals[0].affected_models

    def test_no_fp_when_all_correct(self):
        """No FP proposals when all solid cases are correctly classified."""
        entries = [
            _entry(run_id=f"r{i}", task_id=f"t{i}", task_family="solid",
                   final_answer="solid")
            for i in range(5)
        ]
        proposals = _propose_fp_reduction(entries)
        assert len(proposals) == 0

    def test_co_occurring_failure_detected(self):
        """Failure categories that co-occur with wrong_answer."""
        entries = [
            _entry(
                run_id=f"r{i}", task_id=f"t{i}",
                failure_categories=["wrong_answer", "named_not_explained"],
            )
            for i in range(4)
        ]
        proposals = _propose_fp_reduction(entries)
        trigger_proposals = [p for p in proposals if p.target_kind == "trigger"]
        assert any(p.target == "named_not_explained" for p in trigger_proposals)

    def test_empty_entries(self):
        assert _propose_fp_reduction([]) == []


# ---------------------------------------------------------------------------
# 2. Gold Review Candidates
# ---------------------------------------------------------------------------

class TestGoldReview:
    def test_disagreement_flagged(self):
        """Cases with cross-model disagreement should be flagged."""
        entries = [
            _entry(task_id="t1", model="sonnet", final_answer="solid"),
            _entry(task_id="t1", model="haiku", final_answer="overclaim"),
            _entry(task_id="t1", model="opus", final_answer="overclaim"),
        ]
        proposals = _propose_gold_review(entries)
        assert any(p.target == "t1" for p in proposals)

    def test_all_wrong_high_confidence(self):
        """All models wrong with high confidence = strong gold review signal."""
        entries = [
            _entry(task_id="t1", model="a", correctness=0.0, confidence=0.9,
                   final_answer="overclaim"),
            _entry(task_id="t1", model="b", correctness=0.0, confidence=0.85,
                   final_answer="overclaim"),
            _entry(task_id="t1", model="c", correctness=0.0, confidence=0.92,
                   final_answer="overclaim"),
        ]
        proposals = _propose_gold_review(entries)
        gold_proposals = [p for p in proposals if "unanimous" in p.reason.lower()
                          or "all models" in p.reason.lower()]
        assert len(gold_proposals) >= 1
        assert gold_proposals[0].confidence == "high"

    def test_well_reasoned_wrong(self):
        """Model with high total_score but wrong answer = borderline signal."""
        entries = [
            _entry(task_id="t1", model="a", correctness=1.0, total_score=85.0,
                   confidence=0.9, final_answer="solid"),
            _entry(task_id="t1", model="b", correctness=0.0, total_score=72.0,
                   confidence=0.88, final_answer="overclaim"),
            _entry(task_id="t1", model="c", correctness=0.0, total_score=68.0,
                   confidence=0.82, final_answer="overclaim"),
        ]
        proposals = _propose_gold_review(entries)
        # Should flag for disagreement and/or well-reasoned-wrong
        assert any(p.target == "t1" for p in proposals)

    def test_no_proposal_when_all_correct(self):
        """No gold review needed when all models agree correctly."""
        entries = [
            _entry(task_id="t1", model="a", correctness=1.0, final_answer="solid"),
            _entry(task_id="t1", model="b", correctness=1.0, final_answer="solid"),
        ]
        proposals = _propose_gold_review(entries)
        assert len(proposals) == 0

    def test_single_model_not_flagged(self):
        """Single model runs don't generate gold review proposals."""
        entries = [
            _entry(task_id="t1", model="a", correctness=0.0, confidence=0.95),
        ]
        proposals = _propose_gold_review(entries)
        assert len(proposals) == 0

    def test_empty_entries(self):
        assert _propose_gold_review([]) == []

    def test_missing_and_invalid_confidence_do_not_trigger_high_confidence_review(self):
        entries = [
            _entry(task_id="t1", model="valid", correctness=0.0,
                   confidence=0.9, confidence_state=VALID, final_answer="overclaim"),
            _entry(task_id="t1", model="missing", correctness=0.0,
                   confidence=None, confidence_state=MISSING, final_answer="overclaim"),
            _entry(task_id="t1", model="invalid", correctness=0.0,
                   confidence=0.9, confidence_state=INVALID, final_answer="overclaim"),
        ]

        report = generate_calibration_report(entries)

        assert report.n_confidence_observations == 3
        assert report.n_confidence_eligible == 1
        assert report.n_confidence_ineligible == 2
        assert not any(
            "high confidence" in proposal.reason.lower()
            for proposal in report.gold_review_candidates
        )


# ---------------------------------------------------------------------------
# 3. Category Refinement Candidates
# ---------------------------------------------------------------------------

class TestCategoryRefinement:
    def test_low_correctness_flagged(self):
        """Category with low correctness → refinement proposal."""
        entries = [
            _entry(run_id=f"r{i}", task_id=f"t{i}", task_family="mechanism_vs_evidence",
                   correctness=0.0)
            for i in range(4)
        ]
        proposals = _propose_category_refinement(entries)
        assert any(
            p.target == "mechanism_vs_evidence"
            and "correctness" in p.reason.lower()
            for p in proposals
        )

    def test_high_disagreement_flagged(self):
        """Category with high disagreement → refinement proposal."""
        entries = []
        for i in range(3):
            entries.append(_entry(
                run_id=f"r_a_{i}", task_id=f"t{i}", task_family="corr",
                model="a", final_answer="correlation_vs_causation",
            ))
            entries.append(_entry(
                run_id=f"r_b_{i}", task_id=f"t{i}", task_family="corr",
                model="b", final_answer="overclaim",
            ))
        proposals = _propose_category_refinement(entries)
        assert any(
            p.target == "corr" and "disagreement" in p.reason.lower()
            for p in proposals
        )

    def test_label_scatter_flagged(self):
        """Category where the family label isn't dominant."""
        entries = [
            _entry(run_id=f"r{i}", task_id=f"t{i}", task_family="mech",
                   final_answer=label)
            for i, label in enumerate([
                "overclaim", "solid", "overclaim", "solid", "mechanism",
            ])
        ]
        proposals = _propose_category_refinement(entries)
        scatter_proposals = [
            p for p in proposals
            if p.target == "mech" and "scatter" in p.reason.lower()
        ]
        assert len(scatter_proposals) >= 1

    def test_stable_category_no_proposal(self):
        """A well-performing category should not generate proposals."""
        entries = [
            _entry(run_id=f"r{i}", task_id=f"t{i}", task_family="solid",
                   correctness=1.0, final_answer="solid", model="a")
            for i in range(5)
        ]
        proposals = _propose_category_refinement(entries)
        assert len(proposals) == 0

    def test_too_few_runs_skipped(self):
        """Categories with too few runs are skipped."""
        entries = [
            _entry(task_family="rare", correctness=0.0),
        ]
        proposals = _propose_category_refinement(entries)
        assert len(proposals) == 0

    def test_empty_entries(self):
        assert _propose_category_refinement([]) == []


# ---------------------------------------------------------------------------
# 4. Model Confusion Candidates
# ---------------------------------------------------------------------------

class TestModelConfusion:
    def test_stable_confusion_detected(self):
        """Consistent gold→detected mismatch is flagged."""
        entries = [
            _entry(
                run_id=f"r{i}", task_id=f"t{i}",
                task_type="study_forensics",
                task_family="correlation_vs_causation",
                model="sonnet", agent_id="sonnet",
                final_answer="solid",
            )
            for i in range(3)
        ]
        proposals = _propose_model_confusion(entries)
        assert any(
            p.target == "sonnet"
            and "correlation_vs_causation" in p.reason
            and "solid" in p.reason
            for p in proposals
        )

    def test_cross_model_confusion_detected(self):
        """When multiple models share the same confusion, flag it."""
        entries = []
        for model in ["sonnet", "haiku", "opus"]:
            # Need >= 3 entries per model for threshold, and >= 2 confusions
            for i in range(3):
                entries.append(_entry(
                    run_id=f"r_{model}_{i}", task_id=f"t{i}",
                    task_type="study_forensics",
                    task_family="mechanism_vs_evidence",
                    model=model, agent_id=model,
                    final_answer="overclaim",
                ))
        proposals = _propose_model_confusion(entries)
        # Each model should have a per-model proposal
        per_model = [p for p in proposals if p.target_kind == "model"]
        assert len(per_model) >= 2  # at least 2 models flagged
        # Cross-model proposal
        cross_model = [p for p in proposals if p.target_kind == "category"]
        assert len(cross_model) >= 1

    def test_no_confusion_when_correct(self):
        """Correctly classified entries don't generate confusion proposals."""
        entries = [
            _entry(
                run_id=f"r{i}", task_id=f"t{i}",
                task_type="study_forensics",
                task_family="solid",
                model="sonnet",
                final_answer="solid",
            )
            for i in range(5)
        ]
        proposals = _propose_model_confusion(entries)
        assert len(proposals) == 0

    def test_non_study_forensics_ignored(self):
        """Non study_forensics entries are ignored."""
        entries = [
            _entry(
                run_id=f"r{i}", task_id=f"t{i}",
                task_type="closed_with_reasoning",
                task_family="overclaim",
                final_answer="solid",
            )
            for i in range(5)
        ]
        proposals = _propose_model_confusion(entries)
        assert len(proposals) == 0

    def test_single_occurrence_not_flagged(self):
        """Single confusion occurrence is below threshold."""
        entries = [
            _entry(
                task_type="study_forensics",
                task_family="overclaim",
                model="sonnet",
                final_answer="solid",
            ),
            _entry(
                task_type="study_forensics",
                task_family="overclaim",
                model="sonnet",
                final_answer="overclaim",
            ),
            _entry(
                task_type="study_forensics",
                task_family="solid",
                model="sonnet",
                final_answer="solid",
            ),
        ]
        proposals = _propose_model_confusion(entries)
        # Only 1 confusion occurrence, below threshold of 2
        per_model = [p for p in proposals if p.target == "sonnet"]
        assert len(per_model) == 0

    def test_empty_entries(self):
        assert _propose_model_confusion([]) == []


# ---------------------------------------------------------------------------
# 5. Data Gap Candidates
# ---------------------------------------------------------------------------

class TestDataGaps:
    def test_few_cases_flagged(self):
        """Category with too few cases → data gap."""
        entries = [
            _entry(task_id="t1", task_family="rare_type"),
        ]
        proposals = _propose_data_gaps(entries)
        assert any(
            p.target == "rare_type" and "insufficient" in p.reason.lower()
            for p in proposals
        )

    def test_single_model_coverage_flagged(self):
        """Cases with only one model → data gap."""
        entries = [
            _entry(run_id=f"r{i}", task_id=f"t{i}", task_family="narrow",
                   model="sonnet")
            for i in range(3)
        ]
        proposals = _propose_data_gaps(entries)
        assert any(
            p.target == "narrow" and "single-model" in p.reason.lower()
            for p in proposals
        )

    def test_all_correct_borderline_gap(self):
        """Category with 100% correctness may lack borderline cases."""
        entries = [
            _entry(run_id=f"r{i}", task_id=f"t{i % 3}", task_family="easy",
                   correctness=1.0)
            for i in range(6)
        ]
        proposals = _propose_data_gaps(entries)
        assert any(
            p.target == "easy" and "borderline" in p.reason.lower()
            for p in proposals
        )

    def test_well_covered_no_gap(self):
        """Category with enough cases and multi-model coverage → no gap."""
        entries = []
        for i in range(4):
            for model in ["a", "b"]:
                entries.append(_entry(
                    run_id=f"r_{model}_{i}", task_id=f"t{i}",
                    task_family="covered", model=model,
                    correctness=0.5 if i % 2 == 0 else 1.0,
                ))
        proposals = _propose_data_gaps(entries)
        # Has 4 cases with dual-model coverage, mixed correctness
        gap_for_covered = [p for p in proposals if p.target == "covered"
                           and "insufficient" in p.reason.lower()]
        assert len(gap_for_covered) == 0

    def test_empty_entries(self):
        assert _propose_data_gaps([]) == []


# ---------------------------------------------------------------------------
# 6. Full Pipeline
# ---------------------------------------------------------------------------

class TestGenerateCalibrationReport:
    def test_empty_entries(self):
        report = generate_calibration_report([])
        assert report.n_entries_analyzed == 0
        assert report.n_proposals == 0

    def test_clean_system_few_proposals(self):
        """A well-calibrated system should produce few/no proposals."""
        entries = []
        for i in range(5):
            for model in ["a", "b", "c"]:
                entries.append(_entry(
                    run_id=f"r_{model}_{i}", task_id=f"t{i}",
                    task_family="solid", model=model,
                    final_answer="solid", correctness=1.0,
                ))
        report = generate_calibration_report(entries)
        # May have a "borderline cases missing" data gap, but no critical proposals
        critical = [
            p for p in (
                report.fp_reduction_candidates
                + report.gold_review_candidates
                + report.category_refinement_candidates
            )
            if p.confidence in ("high", "medium")
        ]
        assert len(critical) == 0

    def test_problematic_system_generates_proposals(self):
        """A system with known issues should produce proposals."""
        entries = []
        # Case with all-wrong high confidence (gold review)
        for model in ["a", "b", "c"]:
            entries.append(_entry(
                run_id=f"r_wrong_{model}", task_id="t_wrong",
                task_family="overclaim", model=model,
                final_answer="solid", correctness=0.0, confidence=0.9,
                failure_categories=["wrong_answer"],
                task_type="study_forensics",
            ))
        # Multiple cases in unstable category
        for i in range(4):
            entries.append(_entry(
                run_id=f"r_unstable_{i}", task_id=f"t_unstable_{i}",
                task_family="mechanism_vs_evidence",
                final_answer="overclaim", correctness=0.0,
                task_type="study_forensics", model="a",
            ))

        report = generate_calibration_report(entries)
        assert report.n_proposals > 0
        assert len(report.gold_review_candidates) > 0

    def test_report_counts_match(self):
        """n_proposals should equal sum of all proposal lists."""
        entries = [
            _entry(task_id="t1", model="a", correctness=0.0,
                   confidence=0.9, final_answer="overclaim"),
            _entry(task_id="t1", model="b", correctness=0.0,
                   confidence=0.9, final_answer="overclaim"),
        ]
        report = generate_calibration_report(entries)
        total = (
            len(report.fp_reduction_candidates)
            + len(report.gold_review_candidates)
            + len(report.category_refinement_candidates)
            + len(report.model_confusion_candidates)
            + len(report.data_gap_candidates)
        )
        assert report.n_proposals == total


# ---------------------------------------------------------------------------
# 7. Report Rendering
# ---------------------------------------------------------------------------

class TestRenderCalibrationReport:
    def test_empty_report(self):
        report = generate_calibration_report([])
        md = render_calibration_report(report)
        assert "Gen 2 Calibration Report" in md
        assert "No journal entries" in md

    def test_full_report_has_all_sections(self):
        entries = []
        for model in ["a", "b", "c"]:
            entries.append(_entry(
                run_id=f"r_{model}", task_id="t1",
                task_family="corr", model=model,
                final_answer="solid" if model == "a" else "overclaim",
                correctness=0.0, confidence=0.9,
                failure_categories=["wrong_answer"],
                task_type="study_forensics",
            ))
        report = generate_calibration_report(entries)
        md = render_calibration_report(report)
        assert "## A. False Positive Reduction" in md
        assert "## B. Gold Review" in md
        assert "## C. Category Refinement" in md
        assert "## D. Model Confusion" in md
        assert "## E. Data Gap" in md
        assert "## F. Recommended Next Actions" in md

    def test_report_contains_footer(self):
        """Report with proposals should contain the footer disclaimer."""
        entries = []
        for model in ["a", "b"]:
            entries.append(_entry(
                run_id=f"r_{model}", task_id="t1", model=model,
                correctness=0.0, confidence=0.9, final_answer="overclaim",
            ))
        report = generate_calibration_report(entries)
        md = render_calibration_report(report)
        assert "proposals only" in md
        assert "Human review required" in md

    def test_zero_proposals_message(self):
        report = CalibrationReport(
            generated_at="2026-04-06T00:00:00Z",
            n_entries_analyzed=10,
            n_proposals=0,
        )
        md = render_calibration_report(report)
        assert "well-calibrated" in md

    def test_proposal_summary_table(self):
        entries = []
        for model in ["a", "b"]:
            entries.append(_entry(
                run_id=f"r_{model}", task_id="t1", model=model,
                correctness=0.0, confidence=0.9, final_answer="overclaim",
            ))
        report = generate_calibration_report(entries)
        md = render_calibration_report(report)
        assert "Proposal Summary" in md
        assert "| Type | Count |" in md


# ---------------------------------------------------------------------------
# 8. Proposal Structure Validation
# ---------------------------------------------------------------------------

class TestProposalStructure:
    def test_all_proposals_have_required_fields(self):
        """Every proposal must have type, target, reason, confidence."""
        entries = []
        for model in ["a", "b", "c"]:
            for i in range(3):
                entries.append(_entry(
                    run_id=f"r_{model}_{i}", task_id=f"t{i}",
                    task_family="mechanism_vs_evidence",
                    model=model, agent_id=model,
                    final_answer="overclaim" if model == "a" else "solid",
                    correctness=0.0, confidence=0.85,
                    failure_categories=["wrong_answer"],
                    task_type="study_forensics",
                ))
        report = generate_calibration_report(entries)
        all_proposals = (
            report.fp_reduction_candidates
            + report.gold_review_candidates
            + report.category_refinement_candidates
            + report.model_confusion_candidates
            + report.data_gap_candidates
        )
        for p in all_proposals:
            assert p.proposal_type, f"Missing proposal_type: {p}"
            assert p.target, f"Missing target: {p}"
            assert p.reason, f"Missing reason: {p}"
            assert p.confidence in ("high", "medium", "low", "heuristic"), \
                f"Invalid confidence '{p.confidence}': {p}"
            assert p.recommended_action, f"Missing recommended_action: {p}"

    def test_proposal_types_are_valid(self):
        """All proposal_type values should be from the defined set."""
        valid_types = {
            "fp_reduction", "gold_review", "category_refinement",
            "model_confusion", "data_gap",
        }
        entries = []
        for model in ["a", "b"]:
            entries.append(_entry(
                run_id=f"r_{model}", task_id="t1", model=model,
                correctness=0.0, confidence=0.9, final_answer="overclaim",
                task_type="study_forensics", task_family="solid",
                failure_categories=["wrong_answer"],
            ))
        report = generate_calibration_report(entries)
        all_proposals = (
            report.fp_reduction_candidates
            + report.gold_review_candidates
            + report.category_refinement_candidates
            + report.model_confusion_candidates
            + report.data_gap_candidates
        )
        for p in all_proposals:
            assert p.proposal_type in valid_types, \
                f"Invalid type '{p.proposal_type}': {p}"
