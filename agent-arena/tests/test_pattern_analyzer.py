"""Tests for pattern_analyzer.py — cross-run pattern detection (v0.6)."""

from __future__ import annotations

import pytest

from agent_arena.pattern_analyzer import (
    build_agent_profile,
    compute_all_trends,
    compute_trend,
    detect_failure_patterns,
    detect_flag_patterns,
    detect_forecast_bias_patterns,
)
from agent_arena.schemas import RunJournalEntry


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _entry(
    agent_id="agent-a",
    task_id="t1",
    timestamp="2024-01-01T00:00:00Z",
    failure_categories=None,
    forensic_flag_types=None,
    decision_category="",
    probability_estimate=None,
    reasoning_integrity_class="well_supported",
    n_contradictions=0,
    correctness=0.8,
    total_score=65.0,
    **kw,
) -> RunJournalEntry:
    return RunJournalEntry(
        run_id="r1",
        timestamp=timestamp,
        task_id=task_id,
        task_family="reasoning",
        agent_id=agent_id,
        model="gpt-4",
        total_score=total_score,
        correctness=correctness,
        support_strength=0.6,
        structural_reasoning=0.7,
        insight_depth=0.5,
        mechanism_quality=0.4,
        self_monitoring_quality=0.5,
        failure_categories=failure_categories or [],
        forensic_flag_types=forensic_flag_types or [],
        reasoning_integrity_class=reasoning_integrity_class,
        decision_category=decision_category,
        probability_estimate=probability_estimate,
        n_contradictions=n_contradictions,
        **kw,
    )


# ---------------------------------------------------------------------------
# Test: Failure pattern detection
# ---------------------------------------------------------------------------

class TestFailurePatterns:
    def test_recurring_failure_detected(self):
        entries = [
            _entry(task_id="t1", failure_categories=["wrong_answer"]),
            _entry(task_id="t2", failure_categories=["wrong_answer"]),
            _entry(task_id="t3", failure_categories=["logic_error"]),
        ]
        patterns = detect_failure_patterns(entries)
        wa = [p for p in patterns if p.category == "wrong_answer"]
        assert len(wa) == 1
        assert wa[0].occurrences == 2
        assert wa[0].frequency == pytest.approx(2 / 3, abs=0.01)
        assert "t1" in wa[0].affected_tasks
        assert "t2" in wa[0].affected_tasks

    def test_infrequent_failure_not_pattern(self):
        entries = [
            _entry(task_id=f"t{i}", failure_categories=["wrong_answer"] if i == 0 else [])
            for i in range(10)
        ]
        patterns = detect_failure_patterns(entries)
        wa = [p for p in patterns if p.category == "wrong_answer"]
        assert len(wa) == 0  # 1/10 = 10% < 25% threshold

    def test_empty_entries(self):
        assert detect_failure_patterns([]) == []

    def test_multiple_patterns(self):
        entries = [
            _entry(task_id="t1", failure_categories=["wrong_answer", "logic_error"]),
            _entry(task_id="t2", failure_categories=["wrong_answer", "logic_error"]),
            _entry(task_id="t3", failure_categories=["wrong_answer"]),
        ]
        patterns = detect_failure_patterns(entries)
        assert len(patterns) == 2


# ---------------------------------------------------------------------------
# Test: Flag pattern detection
# ---------------------------------------------------------------------------

class TestFlagPatterns:
    def test_recurring_flag_detected(self):
        entries = [
            _entry(task_id="t1", forensic_flag_types=["calibration_gap"]),
            _entry(task_id="t2", forensic_flag_types=["calibration_gap"]),
        ]
        patterns = detect_flag_patterns(entries)
        assert len(patterns) == 1
        assert patterns[0].category == "calibration_gap"


# ---------------------------------------------------------------------------
# Test: Forecast bias detection
# ---------------------------------------------------------------------------

class TestForecastBias:
    def test_overconfidence_pattern(self):
        entries = [
            _entry(decision_category="forecast", failure_categories=["overconfident_forecast"]),
            _entry(decision_category="forecast", failure_categories=["overconfident_forecast"]),
            _entry(decision_category="forecast", failure_categories=[]),
        ]
        patterns = detect_forecast_bias_patterns(entries)
        oc = [p for p in patterns if p.category == "overconfidence"]
        assert len(oc) == 1
        assert oc[0].frequency == pytest.approx(2 / 3, abs=0.01)

    def test_base_rate_neglect_pattern(self):
        entries = [
            _entry(decision_category="forecast", failure_categories=["base_rate_omission"]),
            _entry(decision_category="forecast", failure_categories=["base_rate_omission"]),
        ]
        patterns = detect_forecast_bias_patterns(entries)
        br = [p for p in patterns if p.category == "base_rate_neglect"]
        assert len(br) == 1

    def test_no_forecast_entries(self):
        entries = [_entry(), _entry()]
        assert detect_forecast_bias_patterns(entries) == []


# ---------------------------------------------------------------------------
# Test: Agent profile
# ---------------------------------------------------------------------------

class TestAgentProfile:
    def test_basic_profile(self):
        entries = [
            _entry(agent_id="a1", total_score=60.0, correctness=0.7),
            _entry(agent_id="a1", total_score=70.0, correctness=0.9),
        ]
        profile = build_agent_profile("a1", entries)
        assert profile.agent_id == "a1"
        assert profile.n_runs == 2
        assert profile.avg_total_score == 65.0
        assert profile.strongest_dimension != ""
        assert profile.weakest_dimension != ""

    def test_profile_no_entries(self):
        profile = build_agent_profile("a1", [])
        assert profile.n_runs == 0

    def test_profile_filters_by_agent(self):
        entries = [
            _entry(agent_id="a1", total_score=60.0),
            _entry(agent_id="a2", total_score=80.0),
        ]
        p = build_agent_profile("a1", entries)
        assert p.n_runs == 1
        assert p.avg_total_score == 60.0

    def test_integrity_rates(self):
        entries = [
            _entry(agent_id="a1", reasoning_integrity_class="accidental"),
            _entry(agent_id="a1", reasoning_integrity_class="brittle"),
            _entry(agent_id="a1", reasoning_integrity_class="well_supported"),
            _entry(agent_id="a1", reasoning_integrity_class="well_supported"),
        ]
        p = build_agent_profile("a1", entries)
        assert p.accidental_correctness_rate == 0.25
        assert p.brittleness_rate == 0.25
        assert p.contradiction_rate == 0.0

    def test_contradiction_rate(self):
        entries = [
            _entry(agent_id="a1", n_contradictions=1),
            _entry(agent_id="a1", n_contradictions=0),
        ]
        p = build_agent_profile("a1", entries)
        assert p.contradiction_rate == 0.5

    def test_forecast_profile(self):
        entries = [
            _entry(agent_id="a1", decision_category="forecast",
                   probability_estimate=0.7,
                   failure_categories=["overconfident_forecast"]),
            _entry(agent_id="a1", decision_category="forecast",
                   probability_estimate=0.3,
                   failure_categories=[]),
        ]
        p = build_agent_profile("a1", entries)
        assert p.avg_probability_estimate == pytest.approx(0.5, abs=0.01)
        assert p.overconfidence_rate == 0.5
        assert p.base_rate_awareness == "consistently_uses"

    def test_no_trade_quality(self):
        entries = [
            _entry(agent_id="a1", decision_category="no_trade",
                   failure_categories=["weak_no_trade_justification"]),
            _entry(agent_id="a1", decision_category="no_trade",
                   failure_categories=[]),
        ]
        p = build_agent_profile("a1", entries)
        assert p.no_trade_quality == "mixed"

    def test_base_rate_awareness_sometimes_ignores(self):
        entries = [
            _entry(agent_id="a1", decision_category="forecast",
                   failure_categories=["base_rate_omission"]),
            _entry(agent_id="a1", decision_category="forecast",
                   failure_categories=[]),
            _entry(agent_id="a1", decision_category="forecast",
                   failure_categories=[]),
        ]
        p = build_agent_profile("a1", entries)
        assert p.base_rate_awareness == "sometimes_ignores"

    def test_base_rate_awareness_ignores(self):
        entries = [
            _entry(agent_id="a1", decision_category="forecast",
                   failure_categories=["base_rate_omission"]),
            _entry(agent_id="a1", decision_category="forecast",
                   failure_categories=["base_rate_omission"]),
            _entry(agent_id="a1", decision_category="forecast",
                   failure_categories=[]),
        ]
        p = build_agent_profile("a1", entries)
        assert p.base_rate_awareness == "ignores"


# ---------------------------------------------------------------------------
# Test: Trend tracking
# ---------------------------------------------------------------------------

class TestTrends:
    def test_improving_trend(self):
        entries = [
            _entry(agent_id="a1", timestamp="2024-01-01", total_score=50.0),
            _entry(agent_id="a1", timestamp="2024-01-02", total_score=55.0),
            _entry(agent_id="a1", timestamp="2024-01-03", total_score=60.0),
            _entry(agent_id="a1", timestamp="2024-01-04", total_score=70.0),
        ]
        trend = compute_trend("a1", entries, "total_score")
        assert trend.trend_direction == "improving"
        assert trend.delta > 0

    def test_declining_trend(self):
        entries = [
            _entry(agent_id="a1", timestamp="2024-01-01", total_score=80.0),
            _entry(agent_id="a1", timestamp="2024-01-02", total_score=70.0),
            _entry(agent_id="a1", timestamp="2024-01-03", total_score=60.0),
            _entry(agent_id="a1", timestamp="2024-01-04", total_score=50.0),
        ]
        trend = compute_trend("a1", entries, "total_score")
        assert trend.trend_direction == "declining"
        assert trend.delta < 0

    def test_stable_trend(self):
        entries = [
            _entry(agent_id="a1", timestamp=f"2024-01-0{i}", total_score=65.0)
            for i in range(1, 5)
        ]
        trend = compute_trend("a1", entries, "total_score")
        assert trend.trend_direction == "stable"

    def test_insufficient_data(self):
        trend = compute_trend("a1", [], "total_score")
        assert trend.trend_direction == "insufficient_data"

    def test_single_entry(self):
        entries = [_entry(agent_id="a1", total_score=65.0)]
        trend = compute_trend("a1", entries, "total_score")
        assert trend.trend_direction == "insufficient_data"

    def test_dimension_trend(self):
        entries = [
            _entry(agent_id="a1", timestamp="2024-01-01", correctness=0.5),
            _entry(agent_id="a1", timestamp="2024-01-02", correctness=0.6),
            _entry(agent_id="a1", timestamp="2024-01-03", correctness=0.7),
            _entry(agent_id="a1", timestamp="2024-01-04", correctness=0.9),
        ]
        trend = compute_trend("a1", entries, "correctness")
        assert trend.trend_direction == "improving"

    def test_compute_all_trends(self):
        entries = [
            _entry(agent_id="a1", timestamp="2024-01-01"),
            _entry(agent_id="a1", timestamp="2024-01-02"),
            _entry(agent_id="a1", timestamp="2024-01-03"),
        ]
        trends = compute_all_trends("a1", entries)
        assert len(trends) == 7  # total_score + 6 dimensions
        dims = {t.dimension for t in trends}
        assert "total_score" in dims
        assert "correctness" in dims
