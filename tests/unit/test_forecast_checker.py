"""v0.5: Tests for forecast integrity checker.

Tests cover:
  - Each of the 7 checks (A-G)
  - Decision category validation
  - Integration with evaluator
  - Report rendering
  - Synthetic response variants
  - No regression on existing task families
"""

from inspektorium.audit.execution.evaluator import evaluate_result
from inspektorium.audit.checks.forecast_checker import (
    is_forecast_task,
    run_forecast_checks,
)
from inspektorium.audit.schemas import (
    AgentResponse,
    AgentResult,
    Difficulty,
    EvaluationConfig,
    FailureCategory,
    Task,
    TaskType,
)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

RULE_TRAP_TASK = Task(
    id="forecast-rule-trap-001",
    title="Resolution Trap: Earnings Beat",
    domain="forecasting",
    difficulty=Difficulty.HARD,
    task_type=TaskType.FORECASTING_DECISION,
    task_family="forecasting_decision",
    prompt="Will TechCorp Q3 earnings beat expectations?",
    base_rate=0.875,
    resolution_rule=(
        "Resolves YES if reported Q3 EPS EXCEEDS (not matches) "
        "FactSet consensus estimate"
    ),
    correct_decision="forecast",
    expected_probability_range=(0.50, 0.75),
)

BASE_RATE_TRAP_TASK = Task(
    id="forecast-base-rate-001",
    title="Narrative vs Base Rate",
    domain="forecasting",
    difficulty=Difficulty.HARD,
    task_type=TaskType.FORECASTING_DECISION,
    task_family="forecasting_decision",
    prompt="Will DataFlow be acquired within 12 months?",
    base_rate=0.02,
    resolution_rule="Resolves YES if binding acquisition agreement announced within 12 months",
    correct_decision="forecast",
    expected_probability_range=(0.05, 0.25),
)

NO_TRADE_TASK = Task(
    id="forecast-no-trade-001",
    title="Honest No-Trade",
    domain="forecasting",
    difficulty=Difficulty.MEDIUM,
    task_type=TaskType.FORECASTING_DECISION,
    task_family="forecasting_decision",
    prompt="Will the Fed cut rates at the next FOMC meeting?",
    resolution_rule="Resolves YES if FOMC announces any rate cut",
    correct_decision="no_trade",
    expected_probability_range=(0.35, 0.65),
)

# A non-forecast task for regression testing
SIMPSON_TASK = Task(
    id="simpson-regression",
    title="Simpson Regression",
    domain="statistics",
    difficulty=Difficulty.HARD,
    task_type=TaskType.RUBRIC_BASED,
    prompt="Is the claim valid?",
)


def _make_result(parsed: AgentResponse) -> AgentResult:
    return AgentResult(
        provider="test",
        model="test-model",
        raw_output="{}",
        parsed=parsed,
        parse_ok=True,
    )


# ===========================================================================
# Task type detection
# ===========================================================================


class TestTaskDetection:
    def test_forecast_task_detected(self):
        assert is_forecast_task(RULE_TRAP_TASK)

    def test_non_forecast_task_not_detected(self):
        assert not is_forecast_task(SIMPSON_TASK)

    def test_non_forecast_returns_empty(self):
        parsed = AgentResponse(final_answer="No")
        result = run_forecast_checks(SIMPSON_TASK, parsed)
        assert result == {}


# ===========================================================================
# A. Probability-Reasoning Alignment
# ===========================================================================


class TestProbabilityAlignment:
    def test_overconfident_with_many_uncertainties(self):
        """High probability + many uncertainties = overconfident."""
        parsed = AgentResponse(
            final_answer="Yes, very likely.",
            probability_estimate=0.90,
            decision_category="forecast",
            uncertainties=["unclear data", "missing info", "potential bias"],
            key_drivers=["strong trend"],
        )
        result = run_forecast_checks(RULE_TRAP_TASK, parsed)
        cats = {f.category for f in result["failures"]}
        assert FailureCategory.OVERCONFIDENT_FORECAST.value in cats

    def test_overconfident_with_few_drivers(self):
        """High probability + weak justification = overconfident."""
        parsed = AgentResponse(
            final_answer="Yes.",
            probability_estimate=0.92,
            decision_category="forecast",
            key_drivers=[],
            uncertainties=[],
        )
        result = run_forecast_checks(RULE_TRAP_TASK, parsed)
        cats = {f.category for f in result["failures"]}
        assert FailureCategory.OVERCONFIDENT_FORECAST.value in cats

    def test_well_calibrated_no_overconfident_flag(self):
        """Moderate probability + balanced reasoning = no overconfident flag."""
        parsed = AgentResponse(
            final_answer="Likely but uncertain.",
            probability_estimate=0.65,
            decision_category="forecast",
            key_drivers=["strong past record", "industry trend"],
            counterarguments=["company guided in line"],
            uncertainties=["currency headwinds"],
        )
        result = run_forecast_checks(RULE_TRAP_TASK, parsed)
        cats = {f.category for f in result["failures"]}
        assert FailureCategory.OVERCONFIDENT_FORECAST.value not in cats

    def test_out_of_range_probability(self):
        """Probability outside expected range = weak calibration."""
        parsed = AgentResponse(
            final_answer="Almost certain.",
            probability_estimate=0.95,
            decision_category="forecast",
            key_drivers=["strong record"],
        )
        result = run_forecast_checks(RULE_TRAP_TASK, parsed)
        cats = {f.category for f in result["failures"]}
        assert FailureCategory.CORRECT_DIRECTION_WEAK_CALIBRATION.value in cats


# ===========================================================================
# B. Base Rate Usage
# ===========================================================================


class TestBaseRateUsage:
    def test_base_rate_omission(self):
        """Task provides base rate but agent ignores it."""
        parsed = AgentResponse(
            final_answer="Very likely to be acquired.",
            probability_estimate=0.60,
            decision_category="forecast",
            steps=["The board has ties to Google", "M&A CFO was hired"],
            key_drivers=["board connections", "CFO hire"],
        )
        result = run_forecast_checks(BASE_RATE_TRAP_TASK, parsed)
        cats = {f.category for f in result["failures"]}
        assert FailureCategory.BASE_RATE_OMISSION.value in cats

    def test_base_rate_referenced(self):
        """Agent references base rate — no omission flag."""
        parsed = AgentResponse(
            final_answer="Low probability.",
            probability_estimate=0.15,
            decision_category="forecast",
            base_rate_reference="Only 2% of Series C startups are acquired per year",
            steps=["Base rate is 2%, adjusting upward for signals"],
            key_drivers=["base rate", "board connections"],
        )
        result = run_forecast_checks(BASE_RATE_TRAP_TASK, parsed)
        cats = {f.category for f in result["failures"]}
        assert FailureCategory.BASE_RATE_OMISSION.value not in cats

    def test_base_rate_in_reasoning_counts(self):
        """Mentioning base rate in steps (not field) still counts."""
        parsed = AgentResponse(
            final_answer="Low probability.",
            probability_estimate=0.12,
            decision_category="forecast",
            steps=["The prior probability / base rate is around 2%"],
            key_drivers=["base rate adjustment"],
        )
        result = run_forecast_checks(BASE_RATE_TRAP_TASK, parsed)
        cats = {f.category for f in result["failures"]}
        assert FailureCategory.BASE_RATE_OMISSION.value not in cats
        assert result["scores"]["baseline_awareness"] >= 0.2


# ===========================================================================
# C. Rule / Resolution Integrity
# ===========================================================================


class TestRuleIntegrity:
    def test_rule_not_engaged(self):
        """Agent ignores the resolution rule entirely."""
        parsed = AgentResponse(
            final_answer="They usually beat.",
            probability_estimate=0.80,
            decision_category="forecast",
            steps=["TechCorp has a great track record"],
        )
        result = run_forecast_checks(RULE_TRAP_TASK, parsed)
        cats = {f.category for f in result["failures"]}
        assert FailureCategory.RULE_MISREAD.value in cats

    def test_rule_engaged(self):
        """Agent discusses the resolution rule."""
        parsed = AgentResponse(
            final_answer="Moderate probability.",
            probability_estimate=0.60,
            decision_category="forecast",
            steps=[
                "The resolution rule requires EPS to EXCEED consensus",
                "Matching the estimate does not count as a beat",
                "Company guided 'in line' which points toward matching",
            ],
        )
        result = run_forecast_checks(RULE_TRAP_TASK, parsed)
        cats = {f.category for f in result["failures"]}
        assert FailureCategory.RULE_MISREAD.value not in cats
        assert result["scores"]["rule_comprehension"] > 0.5


# ===========================================================================
# D. Skeptic Coverage
# ===========================================================================


class TestSkepticCoverage:
    def test_no_counterarguments(self):
        """Zero counterarguments = insufficient skepticism."""
        parsed = AgentResponse(
            final_answer="Yes.",
            probability_estimate=0.75,
            decision_category="forecast",
            counterarguments=[],
            alternative_hypotheses=[],
        )
        result = run_forecast_checks(RULE_TRAP_TASK, parsed)
        cats = {f.category for f in result["failures"]}
        assert FailureCategory.INSUFFICIENT_SKEPTICISM.value in cats

    def test_substantive_counterarguments(self):
        """Substantive counterarguments earn good skeptic score."""
        parsed = AgentResponse(
            final_answer="Moderate.",
            probability_estimate=0.60,
            decision_category="forecast",
            counterarguments=[
                "However, the company guided 'in line' which historically means matching not beating estimates",
                "Currency headwinds could reduce EPS by $0.02-0.05, pushing toward a miss",
            ],
            uncertainties=["pending guidance update"],
        )
        result = run_forecast_checks(RULE_TRAP_TASK, parsed)
        assert result["scores"]["skeptic_depth"] >= 0.5

    def test_decorative_counterarguments(self):
        """Short, vacuous counterarguments flag decorative skepticism."""
        parsed = AgentResponse(
            final_answer="Yes.",
            probability_estimate=0.75,
            decision_category="forecast",
            counterarguments=["Maybe not"],
        )
        result = run_forecast_checks(RULE_TRAP_TASK, parsed)
        flag_types = {f.flag_type for f in result["flags"]}
        assert "decorative_skepticism" in flag_types


# ===========================================================================
# E. No-Trade Integrity
# ===========================================================================


class TestNoTradeIntegrity:
    def test_well_justified_no_trade(self):
        """Substantive no_trade with reasoning = high score."""
        parsed = AgentResponse(
            final_answer="No trade — signals are balanced with insufficient edge.",
            decision_category="no_trade",
            steps=[
                "CPI trending down but still above target",
                "Two FOMC members favor cut, two oppose",
                "Market implies 48% — no clear edge exists",
                "Two more data releases pending",
            ],
            counterarguments=["Could cut if next CPI drops sharply"],
            uncertainties=["Pending data releases make any forecast unreliable"],
        )
        result = run_forecast_checks(NO_TRADE_TASK, parsed)
        assert result["scores"]["no_action_quality"] >= 0.5
        cats = {f.category for f in result["failures"]}
        assert FailureCategory.WEAK_NO_TRADE_JUSTIFICATION.value not in cats

    def test_empty_abstention(self):
        """Abstention with no reasoning = abstention without cause."""
        parsed = AgentResponse(
            final_answer="I abstain.",
            decision_category="abstain",
            steps=[],
        )
        result = run_forecast_checks(NO_TRADE_TASK, parsed)
        cats = {f.category for f in result["failures"]}
        assert FailureCategory.ABSTENTION_WITHOUT_CAUSE.value in cats

    def test_weak_no_trade(self):
        """No-trade with no justification words = weak."""
        parsed = AgentResponse(
            final_answer="No trade.",
            decision_category="no_trade",
            steps=["Looking at the question"],
        )
        result = run_forecast_checks(NO_TRADE_TASK, parsed)
        cats = {f.category for f in result["failures"]}
        assert FailureCategory.WEAK_NO_TRADE_JUSTIFICATION.value in cats

    def test_correct_no_trade_decision(self):
        """Correct no_trade decision gets credit."""
        parsed = AgentResponse(
            final_answer="No trade — insufficient information to form an edge.",
            decision_category="no_trade",
            steps=["Signals are contradictory and balanced"],
            counterarguments=["Could argue either direction but no clear basis"],
        )
        result = run_forecast_checks(NO_TRADE_TASK, parsed)
        assert result["scores"]["no_action_quality"] >= 0.4


# ===========================================================================
# F. Shrinkage Discipline
# ===========================================================================


class TestShrinkageDiscipline:
    def test_extreme_without_shrinkage(self):
        """Extreme probability without shrinkage rationale = failure."""
        parsed = AgentResponse(
            final_answer="95% chance.",
            probability_estimate=0.95,
            decision_category="forecast",
        )
        result = run_forecast_checks(RULE_TRAP_TASK, parsed)
        cats = {f.category for f in result["failures"]}
        assert FailureCategory.SHRINKAGE_FAILURE.value in cats

    def test_extreme_with_shrinkage(self):
        """Extreme but with rationale = no shrinkage failure."""
        parsed = AgentResponse(
            final_answer="Very likely.",
            probability_estimate=0.92,
            decision_category="forecast",
            shrinkage_rationale=(
                "Raw estimate was 95% based on base rate of 87.5%, "
                "but adjusted down to 92% due to 'in line' guidance"
            ),
            base_rate_reference="14/16 quarters beaten = 87.5%",
        )
        result = run_forecast_checks(RULE_TRAP_TASK, parsed)
        cats = {f.category for f in result["failures"]}
        assert FailureCategory.SHRINKAGE_FAILURE.value not in cats

    def test_moderate_no_shrinkage_ok(self):
        """Moderate probability doesn't require shrinkage rationale."""
        parsed = AgentResponse(
            final_answer="60% likely.",
            probability_estimate=0.60,
            decision_category="forecast",
        )
        result = run_forecast_checks(RULE_TRAP_TASK, parsed)
        cats = {f.category for f in result["failures"]}
        assert FailureCategory.SHRINKAGE_FAILURE.value not in cats


# ===========================================================================
# G. Narrative Edge
# ===========================================================================


class TestNarrativeEdge:
    def test_rhetorical_edge(self):
        """Edge with narrative words and no evidence = narrative overreach."""
        parsed = AgentResponse(
            final_answer="Clearly will beat.",
            probability_estimate=0.85,
            decision_category="forecast",
            edge_justification="It's obviously clear that the market is wrong and this will definitely happen",
        )
        result = run_forecast_checks(RULE_TRAP_TASK, parsed)
        cats = {f.category for f in result["failures"]}
        assert FailureCategory.NARRATIVE_OVERREACH.value in cats

    def test_evidence_based_edge(self):
        """Edge with evidence-based reasoning = no narrative flag."""
        parsed = AgentResponse(
            final_answer="Likely to beat.",
            probability_estimate=0.70,
            decision_category="forecast",
            edge_justification=(
                "Historically, data shows that companies with this product cycle "
                "pattern beat estimates 80% of the time. According to analysis of "
                "the last 4 quarters, the trend supports a beat."
            ),
        )
        result = run_forecast_checks(RULE_TRAP_TASK, parsed)
        cats = {f.category for f in result["failures"]}
        assert FailureCategory.NARRATIVE_OVERREACH.value not in cats

    def test_forecast_without_edge(self):
        """Forecast decision without any edge justification = false edge."""
        parsed = AgentResponse(
            final_answer="Will beat.",
            probability_estimate=0.80,
            decision_category="forecast",
            edge_justification="",
        )
        result = run_forecast_checks(RULE_TRAP_TASK, parsed)
        cats = {f.category for f in result["failures"]}
        assert FailureCategory.FALSE_EDGE_DETECTION.value in cats


# ===========================================================================
# Decision Category
# ===========================================================================


class TestDecisionCategory:
    def test_wrong_decision_category(self):
        """Agent forecasts when no_trade is correct."""
        parsed = AgentResponse(
            final_answer="75% chance of cut.",
            probability_estimate=0.75,
            decision_category="forecast",
        )
        result = run_forecast_checks(NO_TRADE_TASK, parsed)
        cats = {f.category for f in result["failures"]}
        assert FailureCategory.OPPORTUNITY_MISCLASSIFICATION.value in cats

    def test_correct_decision_category(self):
        """Agent correctly identifies no_trade."""
        parsed = AgentResponse(
            final_answer="No trade.",
            decision_category="no_trade",
            steps=["Balanced signals, no edge"],
        )
        result = run_forecast_checks(NO_TRADE_TASK, parsed)
        cats = {f.category for f in result["failures"]}
        assert FailureCategory.OPPORTUNITY_MISCLASSIFICATION.value not in cats

    def test_abstain_equivalent_to_no_trade(self):
        """Abstain and no_trade are equivalent decisions."""
        parsed = AgentResponse(
            final_answer="Abstaining.",
            decision_category="abstain",
            steps=["Cannot determine direction"],
        )
        result = run_forecast_checks(NO_TRADE_TASK, parsed)
        cats = {f.category for f in result["failures"]}
        assert FailureCategory.OPPORTUNITY_MISCLASSIFICATION.value not in cats


# ===========================================================================
# Evaluator Integration
# ===========================================================================


class TestEvaluatorIntegration:
    def test_forecast_task_produces_forecast_integrity(self):
        """Evaluator attaches forecast_integrity for forecast tasks."""
        parsed = AgentResponse(
            final_answer="65% likely.",
            probability_estimate=0.65,
            decision_category="forecast",
            steps=["Base rate is 87.5%, adjusting down for in-line guidance"],
            key_drivers=["base rate", "guidance signal"],
            counterarguments=["Currency headwinds"],
            uncertainties=["Pending report"],
            base_rate_reference="14/16 quarters = 87.5%",
        )
        result = evaluate_result(RULE_TRAP_TASK, _make_result(parsed))
        assert result.forecast_integrity
        assert result.forecast_integrity.get("is_forecast") is True
        assert "scores" in result.forecast_integrity

    def test_non_forecast_task_empty_forecast_integrity(self):
        """Non-forecast task produces empty forecast_integrity."""
        parsed = AgentResponse(
            final_answer="No",
            steps=["This is Simpson's paradox"],
        )
        result = evaluate_result(SIMPSON_TASK, _make_result(parsed))
        assert result.forecast_integrity == {}

    def test_forecast_failures_in_main_failures(self):
        """Forecast-specific failures appear in result.failures."""
        parsed = AgentResponse(
            final_answer="95% sure.",
            probability_estimate=0.95,
            decision_category="forecast",
            key_drivers=[],
        )
        result = evaluate_result(RULE_TRAP_TASK, _make_result(parsed))
        cats = {f.category for f in result.failures}
        assert FailureCategory.OVERCONFIDENT_FORECAST.value in cats

    def test_forecast_flags_in_forensic_flags(self):
        """Forecast flags appear in result.forensic_flags."""
        parsed = AgentResponse(
            final_answer="50-50.",
            probability_estimate=0.50,
            decision_category="forecast",
            steps=["Hard to say"],
        )
        result = evaluate_result(BASE_RATE_TRAP_TASK, _make_result(parsed))
        flag_types = {f.flag_type for f in result.forensic_flags}
        assert "baseline_blind" in flag_types


# ===========================================================================
# Report Integration
# ===========================================================================


class TestReportIntegration:
    def test_report_contains_forecast_section(self):
        from inspektorium.audit.reports.reporter import generate_report
        from inspektorium.audit.schemas import RunRecord

        parsed = AgentResponse(
            final_answer="65% likely.",
            probability_estimate=0.65,
            decision_category="forecast",
            steps=["Base rate is 87.5%"],
            key_drivers=["base rate"],
            base_rate_reference="87.5%",
        )
        result = evaluate_result(RULE_TRAP_TASK, _make_result(parsed))
        record = RunRecord(run_id="test-fc", task=RULE_TRAP_TASK, results=[result])
        report = generate_report(record)
        assert "Forecast Integrity Audit" in report

    def test_report_shows_probability(self):
        from inspektorium.audit.reports.reporter import generate_report
        from inspektorium.audit.schemas import RunRecord

        parsed = AgentResponse(
            final_answer="65% likely.",
            probability_estimate=0.65,
            decision_category="forecast",
            steps=["Analysis"],
            key_drivers=["trend"],
        )
        result = evaluate_result(RULE_TRAP_TASK, _make_result(parsed))
        record = RunRecord(run_id="test-fc", task=RULE_TRAP_TASK, results=[result])
        report = generate_report(record)
        assert "65%" in report
        assert "Probability Estimate" in report

    def test_report_no_forecast_section_for_non_forecast(self):
        from inspektorium.audit.reports.reporter import generate_report
        from inspektorium.audit.schemas import RunRecord

        parsed = AgentResponse(final_answer="No", steps=["paradox"])
        result = evaluate_result(SIMPSON_TASK, _make_result(parsed))
        record = RunRecord(run_id="test-nf", task=SIMPSON_TASK, results=[result])
        report = generate_report(record)
        assert "Forecast Integrity Audit" not in report


# ===========================================================================
# No Regression
# ===========================================================================


class TestNoRegression:
    def test_simpson_task_unaffected(self):
        """Non-forecast tasks must produce the same results as before."""
        parsed = AgentResponse(
            final_answer="This is Simpson's paradox — women have higher rates in both departments.",
            steps=[
                "Engineering: men 30%, women 40%",
                "Arts: men 75%, women 87.5%",
                "Overall reversal due to application patterns",
            ],
            assumptions=["Data is accurate"],
            confidence=0.85,
        )
        result = evaluate_result(SIMPSON_TASK, _make_result(parsed))
        # Must still have scores, no crash, no forecast data
        assert result.scores.total > 0
        assert result.forecast_integrity == {}
        assert FailureCategory.OVERCONFIDENT_FORECAST.value not in {
            f.category for f in result.failures
        }
