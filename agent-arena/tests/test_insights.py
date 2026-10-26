"""Tests for Gen 1 Insights — agent-arena v0.6.6.

Tests cover:
- Failure aggregation across entries
- Flag aggregation
- Model profile computation (dimensions, tendencies, integrity)
- Disagreement / instability detection
- Category maturity summary
- Borderline candidate signals
- Report rendering
- Empty input handling
"""

from __future__ import annotations

import pytest

from agent_arena.confidence_validity import INVALID, MISSING, VALID
from agent_arena.schemas import (
    BorderlineCandidateSignal,
    CaseDisagreement,
    CategoryMaturitySummary,
    CountedItem,
    InsightsReport,
    ModelInsightProfile,
    RunJournalEntry,
)
from agent_arena.insights import (
    _build_category_maturity,
    _build_disagreement_summary,
    _build_failure_summary,
    _build_flag_summary,
    _build_model_profiles,
    _counter_to_items,
    _detect_borderline_candidates,
    _detect_label_confusions,
    _detect_tendencies,
    _entropy,
    generate_insights,
    render_insights_report,
)
from collections import Counter


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


# Reusable multi-model, multi-task dataset
def _make_test_dataset() -> list[RunJournalEntry]:
    """Create a controlled 12-entry dataset: 3 models × 4 tasks."""
    entries = []
    models = ["claude-sonnet", "claude-haiku", "claude-opus"]
    tasks = [
        ("task-001", "solid", "solid", 80.0, 1.0),
        ("task-002", "overclaim", "overclaim", 70.0, 0.8),
        ("task-003", "correlation_vs_causation", "correlation_vs_causation", 65.0, 0.7),
        ("task-004", "solid", "solid", 90.0, 1.0),
    ]

    for i, model in enumerate(models):
        for j, (tid, family, answer, score, corr) in enumerate(tasks):
            # Introduce disagreement: haiku says "overclaim" for task-003
            fa = answer
            c = corr
            s = score
            fcs = []
            if model == "claude-haiku" and tid == "task-003":
                fa = "overclaim"
                c = 0.0
                s = 45.0
                fcs = ["wrong_answer"]
            # Sonnet weak mechanism on task-002
            mq = 0.6
            if model == "claude-sonnet" and tid == "task-002":
                mq = 0.1
                fcs = ["named_not_explained"]

            entries.append(_entry(
                run_id=f"run_{i}_{j}",
                task_id=tid,
                task_family=family,
                model=model,
                agent_id=model,
                total_score=s,
                correctness=c,
                mechanism_quality=mq,
                final_answer=fa,
                failure_categories=fcs,
                confidence=0.85,
            ))

    return entries


# ---------------------------------------------------------------------------
# 1. CountedItem helper
# ---------------------------------------------------------------------------

class TestCounterToItems:
    def test_basic(self):
        ctr = Counter({"a": 5, "b": 3, "c": 1})
        items = _counter_to_items(ctr, 10)
        assert len(items) == 3
        assert items[0].name == "a"
        assert items[0].count == 5
        assert items[0].frequency == 0.5

    def test_empty(self):
        assert _counter_to_items(Counter(), 0) == []

    def test_top_n(self):
        ctr = Counter({f"item_{i}": i for i in range(20)})
        items = _counter_to_items(ctr, 100, top_n=5)
        assert len(items) == 5


# ---------------------------------------------------------------------------
# 2. Entropy
# ---------------------------------------------------------------------------

class TestEntropy:
    def test_unanimous(self):
        assert _entropy({"solid": 3}) == 0.0

    def test_split(self):
        e = _entropy({"solid": 1, "overclaim": 1})
        assert e == 1.0  # max entropy for 2 labels

    def test_partial(self):
        e = _entropy({"solid": 2, "overclaim": 1})
        assert 0.0 < e < 1.0

    def test_empty(self):
        assert _entropy({}) == 0.0

    def test_three_way_split(self):
        e = _entropy({"a": 1, "b": 1, "c": 1})
        assert e == 1.0  # max entropy for 3 labels


# ---------------------------------------------------------------------------
# 3. Failure Summary
# ---------------------------------------------------------------------------

class TestFailureSummary:
    def test_overall_counts(self):
        entries = [
            _entry(failure_categories=["wrong_answer", "logic_error"]),
            _entry(failure_categories=["wrong_answer"]),
            _entry(failure_categories=["named_not_explained"]),
        ]
        fs = _build_failure_summary(entries)
        assert fs.top_overall[0].name == "wrong_answer"
        assert fs.top_overall[0].count == 2

    def test_by_model(self):
        entries = [
            _entry(model="sonnet", failure_categories=["wrong_answer"]),
            _entry(model="haiku", failure_categories=["logic_error"]),
        ]
        fs = _build_failure_summary(entries)
        assert "sonnet" in fs.by_model
        assert "haiku" in fs.by_model
        assert fs.by_model["sonnet"][0].name == "wrong_answer"
        assert fs.by_model["haiku"][0].name == "logic_error"

    def test_by_family(self):
        entries = [
            _entry(task_family="solid", failure_categories=["false_positive"]),
            _entry(task_family="overclaim", failure_categories=["wrong_answer"]),
        ]
        fs = _build_failure_summary(entries)
        assert "solid" in fs.by_family
        assert "overclaim" in fs.by_family

    def test_empty(self):
        fs = _build_failure_summary([])
        assert fs.top_overall == []

    def test_no_failures(self):
        entries = [_entry(failure_categories=[])]
        fs = _build_failure_summary(entries)
        assert fs.top_overall == []


# ---------------------------------------------------------------------------
# 4. Flag Summary
# ---------------------------------------------------------------------------

class TestFlagSummary:
    def test_overall(self):
        entries = [
            _entry(forensic_flag_types=["well_reasoned_wrong", "calibration_gap"]),
            _entry(forensic_flag_types=["well_reasoned_wrong"]),
        ]
        fl = _build_flag_summary(entries)
        assert fl.top_overall[0].name == "well_reasoned_wrong"
        assert fl.top_overall[0].count == 2

    def test_empty(self):
        fl = _build_flag_summary([])
        assert fl.top_overall == []


# ---------------------------------------------------------------------------
# 5. Model Profiles
# ---------------------------------------------------------------------------

class TestModelProfiles:
    def test_basic_profile(self):
        entries = [
            _entry(model="sonnet", correctness=1.0, mechanism_quality=0.2, total_score=80.0),
            _entry(model="sonnet", correctness=0.8, mechanism_quality=0.3, total_score=70.0),
        ]
        profiles = _build_model_profiles(entries)
        assert len(profiles) == 1
        p = profiles[0]
        assert p.model == "sonnet"
        assert p.n_runs == 2
        assert p.avg_score == 75.0
        assert p.dimension_averages["correctness"] == 0.9
        assert "correctness" in p.strongest_dimensions

    def test_multiple_models(self):
        entries = [
            _entry(model="sonnet", total_score=80.0),
            _entry(model="haiku", total_score=60.0),
        ]
        profiles = _build_model_profiles(entries)
        assert len(profiles) == 2
        models = {p.model for p in profiles}
        assert "sonnet" in models
        assert "haiku" in models

    def test_integrity_rates(self):
        entries = [
            _entry(model="m", reasoning_integrity_class="well_supported"),
            _entry(model="m", reasoning_integrity_class="brittle"),
            _entry(model="m", reasoning_integrity_class="accidental"),
            _entry(model="m", reasoning_integrity_class="well_supported"),
        ]
        profiles = _build_model_profiles(entries)
        p = profiles[0]
        assert p.integrity_rates["well_supported"] == 0.5
        assert p.integrity_rates["brittle"] == 0.25
        assert p.integrity_rates["accidental"] == 0.25

    def test_label_confusions(self):
        entries = [
            _entry(
                model="sonnet",
                task_type="study_forensics",
                task_family="correlation_vs_causation",
                final_answer="solid",
            ),
            _entry(
                model="sonnet",
                task_type="study_forensics",
                task_family="correlation_vs_causation",
                final_answer="solid",
            ),
        ]
        profiles = _build_model_profiles(entries)
        p = profiles[0]
        assert len(p.label_confusions) == 1
        assert p.label_confusions[0].gold_label == "correlation_vs_causation"
        assert p.label_confusions[0].detected_label == "solid"
        assert p.label_confusions[0].count == 2


# ---------------------------------------------------------------------------
# 6. Tendencies
# ---------------------------------------------------------------------------

class TestTendencies:
    def test_charitable_reading(self):
        entries = [
            _entry(final_answer="solid", correctness=0.0),
            _entry(final_answer="solid", correctness=0.0),
            _entry(final_answer="solid", correctness=0.0),
        ]
        t = _detect_tendencies(entries, {}, [])
        assert any("charitable_reading" in x for x in t)

    def test_brittle_reasoning(self):
        entries = [
            _entry(reasoning_integrity_class="brittle"),
            _entry(reasoning_integrity_class="brittle"),
            _entry(reasoning_integrity_class="well_supported"),
        ]
        t = _detect_tendencies(entries, {}, [])
        assert any("brittle_reasoning" in x for x in t)

    def test_weak_self_monitoring(self):
        t = _detect_tendencies(
            [_entry()],
            {"self_monitoring_quality": 0.1},
            [],
        )
        assert "weak_self_monitoring" in t

    def test_no_tendencies_for_clean_data(self):
        entries = [
            _entry(correctness=1.0, reasoning_integrity_class="well_supported"),
        ]
        t = _detect_tendencies(entries, {"self_monitoring_quality": 0.8, "mechanism_quality": 0.7}, [])
        assert len(t) == 0

    def test_empty(self):
        assert _detect_tendencies([], {}, []) == []


# ---------------------------------------------------------------------------
# 7. Disagreement Summary
# ---------------------------------------------------------------------------

class TestDisagreementSummary:
    def test_detects_disagreement(self):
        entries = [
            _entry(task_id="t1", model="sonnet", final_answer="solid"),
            _entry(task_id="t1", model="haiku", final_answer="overclaim"),
        ]
        ds = _build_disagreement_summary(entries)
        assert len(ds.cases) == 1
        assert ds.cases[0].task_id == "t1"
        assert ds.cases[0].disagreement_score == 1.0  # 50/50 split

    def test_no_disagreement_when_unanimous(self):
        entries = [
            _entry(task_id="t1", model="sonnet", final_answer="solid"),
            _entry(task_id="t1", model="haiku", final_answer="solid"),
        ]
        ds = _build_disagreement_summary(entries)
        assert len(ds.cases) == 0  # unanimous = no disagreement entry

    def test_single_model_ignored(self):
        entries = [_entry(task_id="t1", model="sonnet", final_answer="solid")]
        ds = _build_disagreement_summary(entries)
        assert len(ds.cases) == 0

    def test_three_way_disagreement(self):
        entries = [
            _entry(task_id="t1", model="a", final_answer="solid"),
            _entry(task_id="t1", model="b", final_answer="overclaim"),
            _entry(task_id="t1", model="c", final_answer="correlation_vs_causation"),
        ]
        ds = _build_disagreement_summary(entries)
        assert len(ds.cases) == 1
        assert ds.cases[0].disagreement_score == 1.0

    def test_borderline_flagged(self):
        entries = [
            _entry(task_id="t1", model="sonnet", final_answer="solid"),
            _entry(task_id="t1", model="haiku", final_answer="overclaim"),
        ]
        ds = _build_disagreement_summary(entries)
        # 50/50 split = entropy 1.0 > 0.4 threshold
        assert ds.cases[0].is_borderline_candidate

    def test_models_by_label(self):
        entries = [
            _entry(task_id="t1", model="sonnet", final_answer="solid"),
            _entry(task_id="t1", model="haiku", final_answer="overclaim"),
            _entry(task_id="t1", model="opus", final_answer="overclaim"),
        ]
        ds = _build_disagreement_summary(entries)
        assert "sonnet" in ds.cases[0].models_by_label["solid"]
        assert "haiku" in ds.cases[0].models_by_label["overclaim"]
        assert "opus" in ds.cases[0].models_by_label["overclaim"]


# ---------------------------------------------------------------------------
# 8. Category Maturity
# ---------------------------------------------------------------------------

class TestCategoryMaturity:
    def test_mature_category(self):
        entries = [
            _entry(task_family="solid", correctness=1.0, task_id="t1", model="a"),
            _entry(task_family="solid", correctness=1.0, task_id="t1", model="b"),
            _entry(task_family="solid", correctness=0.9, task_id="t2", model="a"),
            _entry(task_family="solid", correctness=0.9, task_id="t2", model="b"),
        ]
        cms = _build_category_maturity(entries)
        assert len(cms) == 1
        assert cms[0].maturity == "mature"
        assert cms[0].correctness_rate == 1.0  # all >= 0.8

    def test_unstable_category(self):
        entries = [
            _entry(task_family="mech", correctness=0.0, task_id="t1", model="a"),
            _entry(task_family="mech", correctness=0.0, task_id="t1", model="b"),
            _entry(task_family="mech", correctness=0.0, task_id="t2", model="a"),
        ]
        cms = _build_category_maturity(entries)
        assert cms[0].maturity == "unstable"

    def test_insufficient_data(self):
        entries = [
            _entry(task_family="rare", correctness=1.0),
            _entry(task_family="rare", correctness=1.0),
        ]
        cms = _build_category_maturity(entries)
        assert cms[0].maturity == "insufficient_data"

    def test_developing_category(self):
        """Category with mixed correctness (60%) and moderate disagreement → developing."""
        entries = [
            _entry(task_family="dev", correctness=0.9, task_id="t1", model="a"),
            _entry(task_family="dev", correctness=0.9, task_id="t1", model="b"),
            _entry(task_family="dev", correctness=0.0, task_id="t2", model="a"),
            _entry(task_family="dev", correctness=0.9, task_id="t2", model="b"),
            _entry(task_family="dev", correctness=0.0, task_id="t3", model="a"),
        ]
        # 60% correctness (3/5 >= 0.8), one multi-model disagreement case
        # Not mature (correctness < 80%), not unstable (correctness >= 50%, disagreement <= 60%)
        cms = _build_category_maturity(entries)
        assert cms[0].maturity == "developing"

    def test_empty_family_skipped(self):
        entries = [_entry(task_family="")]
        cms = _build_category_maturity(entries)
        assert len(cms) == 0

    def test_disagreement_rate(self):
        entries = [
            _entry(task_family="test", task_id="t1", model="a", final_answer="solid"),
            _entry(task_family="test", task_id="t1", model="b", final_answer="overclaim"),
            _entry(task_family="test", task_id="t2", model="a", final_answer="solid"),
            _entry(task_family="test", task_id="t2", model="b", final_answer="solid"),
        ]
        cms = _build_category_maturity(entries)
        # task-001: disagreement, task-002: agreement → 50% disagreement
        assert cms[0].disagreement_rate == 0.5


# ---------------------------------------------------------------------------
# 9. Borderline Candidate Signals
# ---------------------------------------------------------------------------

class TestBorderlineCandidates:
    def test_high_disagreement_flagged(self):
        entries = [
            _entry(task_id="t1", model="a", final_answer="solid"),
            _entry(task_id="t1", model="b", final_answer="overclaim"),
        ]
        ds = _build_disagreement_summary(entries)
        bcs = _detect_borderline_candidates(entries, ds)
        assert any(bc.task_id == "t1" for bc in bcs)

    def test_all_incorrect_high_confidence(self):
        entries = [
            _entry(task_id="t1", model="a", correctness=0.0, confidence=0.9),
            _entry(task_id="t1", model="b", correctness=0.0, confidence=0.85),
        ]
        ds = _build_disagreement_summary(entries)
        bcs = _detect_borderline_candidates(entries, ds)
        assert any(
            bc.task_id == "t1" and "gold label issue" in bc.reason
            for bc in bcs
        )

    def test_single_run_not_flagged(self):
        entries = [_entry(task_id="t1", correctness=0.0, confidence=0.9)]
        ds = _build_disagreement_summary(entries)
        bcs = _detect_borderline_candidates(entries, ds)
        assert len(bcs) == 0

    def test_correct_runs_not_flagged(self):
        entries = [
            _entry(task_id="t1", model="a", correctness=1.0, confidence=0.9),
            _entry(task_id="t1", model="b", correctness=1.0, confidence=0.9),
        ]
        ds = _build_disagreement_summary(entries)
        bcs = _detect_borderline_candidates(entries, ds)
        assert len(bcs) == 0


# ---------------------------------------------------------------------------
# 10. Full generate_insights pipeline
# ---------------------------------------------------------------------------

class TestGenerateInsights:
    def test_empty_entries(self):
        report = generate_insights([])
        assert report.n_runs == 0
        assert report.n_tasks == 0
        assert report.n_models == 0

    def test_single_entry(self):
        entries = [_entry()]
        report = generate_insights(entries)
        assert report.n_runs == 1
        assert report.n_tasks == 1
        assert report.n_models == 1
        assert len(report.model_profiles) == 1

    def test_confidence_states_are_filtered_with_explicit_denominators(self):
        entries = [
            _entry(task_id="t1", model="valid", correctness=0.0,
                   confidence=0.9, confidence_state=VALID),
            _entry(task_id="t1", model="missing", correctness=0.0,
                   confidence=None, confidence_state=MISSING),
            _entry(task_id="t1", model="invalid", correctness=0.0,
                   confidence=0.9, confidence_state=INVALID),
        ]

        report = generate_insights(entries)

        assert report.n_confidence_observations == 3
        assert report.n_confidence_eligible == 1
        assert report.n_confidence_ineligible == 2
        assert not any(
            "high confidence" in signal.reason.lower()
            for signal in report.borderline_candidates
        )

    def test_full_dataset(self):
        entries = _make_test_dataset()
        report = generate_insights(entries)
        assert report.n_runs == 12
        assert report.n_tasks == 4
        assert report.n_models == 3
        assert len(report.model_profiles) == 3
        assert len(report.category_maturity) > 0

    def test_disagreement_detected_in_dataset(self):
        entries = _make_test_dataset()
        report = generate_insights(entries)
        # task-003 has haiku saying "overclaim" while others say "correlation_vs_causation"
        disagreement_tasks = [c.task_id for c in report.disagreement_summary.cases]
        assert "task-003" in disagreement_tasks

    def test_report_contains_all_sections(self):
        entries = _make_test_dataset()
        report = generate_insights(entries)
        assert report.failure_summary is not None
        assert report.flag_summary is not None
        assert report.model_profiles is not None
        assert report.disagreement_summary is not None
        assert report.category_maturity is not None
        assert report.borderline_candidates is not None


# ---------------------------------------------------------------------------
# 11. Report Rendering
# ---------------------------------------------------------------------------

class TestRenderInsightsReport:
    def test_empty_report(self):
        report = generate_insights([])
        md = render_insights_report(report)
        assert "Gen 1 Insights" in md
        assert "No journal entries" in md

    def test_full_report_renders(self):
        entries = _make_test_dataset()
        report = generate_insights(entries)
        md = render_insights_report(report)
        assert "## A. Failure Summary" in md
        assert "## B. Flag Summary" in md
        assert "## C. Model Profiles" in md
        assert "## D. Disagreement Summary" in md
        assert "## E. Category Maturity" in md
        assert "## F. Borderline / Gold-Review Candidates" in md
        assert "observation only" in md

    def test_model_names_in_report(self):
        entries = _make_test_dataset()
        report = generate_insights(entries)
        md = render_insights_report(report)
        assert "claude-sonnet" in md
        assert "claude-haiku" in md
        assert "claude-opus" in md

    def test_report_is_markdown(self):
        entries = _make_test_dataset()
        report = generate_insights(entries)
        md = render_insights_report(report)
        # Has markdown table delimiters
        assert "|" in md
        assert "---" in md


# ---------------------------------------------------------------------------
# 12. Label confusion detection
# ---------------------------------------------------------------------------

class TestLabelConfusions:
    def test_detects_confusion(self):
        entries = [
            _entry(
                model="m",
                task_type="study_forensics",
                task_family="overclaim",
                final_answer="solid",
            ),
        ]
        confusions = _detect_label_confusions(entries, "m")
        assert len(confusions) == 1
        assert confusions[0].gold_label == "overclaim"
        assert confusions[0].detected_label == "solid"

    def test_correct_label_not_counted(self):
        entries = [
            _entry(
                model="m",
                task_type="study_forensics",
                task_family="solid",
                final_answer="solid",
            ),
        ]
        confusions = _detect_label_confusions(entries, "m")
        assert len(confusions) == 0

    def test_non_study_forensics_ignored(self):
        entries = [
            _entry(
                model="m",
                task_type="closed_with_reasoning",
                task_family="overclaim",
                final_answer="solid",
            ),
        ]
        confusions = _detect_label_confusions(entries, "m")
        assert len(confusions) == 0
