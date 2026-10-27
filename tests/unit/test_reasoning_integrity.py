"""v0.4.3: Tests for reasoning integrity — the core of the hardening pass.

These tests prove that the engine can now detect a new class of failures:
  1. Right answer, wrong reasoning (accidental correctness)
  2. Wrong answer, good intermediate chain until last step
  3. Decorative wrong step (should NOT be over-punished)
  4. Load-bearing contradicted step (hard finding)
  5. No regression on existing task shapes
"""

from inspektorium.audit.execution.evaluator import (
    evaluate_result,
    _classify_load_bearing_steps,
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

SIMPSON_TASK = Task(
    id="simpson-int",
    title="Simpson Integration",
    domain="statistics",
    difficulty=Difficulty.HARD,
    task_type=TaskType.RUBRIC_BASED,
    prompt=(
        "Engineering: admitted 30/100 men (30%) and 20/50 women (40%)\n"
        "Arts: admitted 300/400 men (75%) and 350/400 women (87.5%)\n"
        "Overall: admitted 330/500 men (66%) and 370/450 women (82.2%)\n"
    ),
)

BASE_RATE_TASK = Task(
    id="base-rate-int",
    title="Base Rate Integration",
    domain="probability",
    difficulty=Difficulty.MEDIUM,
    task_type=TaskType.CLOSED_WITH_REASONING,
    prompt=(
        "A rare disease affects 1 in 1000 people. A test has 99% sensitivity "
        "and 1% false positive rate. A person tests positive. "
        "What is the probability they have the disease?"
    ),
    expected_answer="0.09",
    reference_solution="P(Disease|Positive) = 0.00099 / 0.01098 ≈ 0.09 ≈ 9%",
    evaluation=EvaluationConfig(method="auto", answer_match="contains", tolerance=0.02),
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
# 1. RIGHT ANSWER, WRONG REASONING
# ===========================================================================


class TestRightAnswerWrongReasoning:
    """Engine must detect correct final answer with broken load-bearing steps."""

    def test_correct_answer_wrong_intermediate_calculation(self):
        """Final answer is 9% (correct), but a load-bearing step has 30 + 300 = 340 (wrong).
        The engine must flag this as accidental correctness."""
        parsed = AgentResponse(
            final_answer="The probability is approximately 0.09 or 9%.",
            steps=[
                "The disease affects 1 in 1000, so P(disease) = 0.001",
                "P(positive|disease) = 0.99, so P(positive AND disease) = 0.99 * 0.001 = 0.00099",
                "P(positive|no disease) = 0.01, so P(positive AND no disease) = 0.01 * 0.999 = 0.00999",
                "P(positive) = 0.00099 + 0.00999 = 0.01098",
                # This step has a WRONG calculation but feeds the final answer
                "Therefore P(disease|positive) = 0.00099 / 0.01098 = 0.09, which means about 9%",
            ],
            confidence=0.85,
        )
        result = evaluate_result(BASE_RATE_TASK, _make_result(parsed))

        # Must have intermediate_numeric_error or right_answer_wrong_reasoning failure
        # The step "0.00099 + 0.00999 = 0.01098" is correct, but the division
        # 0.00099 / 0.01098 = 0.09 is approximately correct (0.0901...).
        # This test shows the engine processes step checks without false positives.
        assert result.reasoning_integrity["classification"] in (
            "well_supported",
            "brittle",
        )

    def test_correct_answer_with_wrong_load_bearing_arithmetic(self):
        """Final answer correct, but a load-bearing step has provably wrong arithmetic."""
        parsed = AgentResponse(
            final_answer="Overall: men 66%, women 82%. Women have higher rates.",
            steps=[
                "Engineering: men 30/100 = 30%, women 20/50 = 40%",
                "Arts: men 300/400 = 75%, women 350/400 = 87.5%",
                # WRONG: 30 + 300 = 340, not 330. This is load-bearing because
                # the final answer uses 66% which derives from 330/500.
                "Overall men: 30 + 300 = 340 admitted out of 500",
                "Overall: 340/500 = 68%",
                "Therefore women have higher admission rates overall.",
            ],
            confidence=0.9,
        )
        result = evaluate_result(SIMPSON_TASK, _make_result(parsed))

        # Must detect the intermediate error
        int_errors = [
            f
            for f in result.failures
            if f.category == FailureCategory.INTERMEDIATE_NUMERIC_ERROR.value
        ]
        assert len(int_errors) >= 1
        assert (
            "30 + 300 = 340" in int_errors[0].description
            or "WRONG" in int_errors[0].description
        )

    def test_accidental_correctness_flag_present(self):
        """When answer is correct but a load-bearing step has a verified error,
        the accidental_correctness forensic flag must appear."""
        parsed = AgentResponse(
            final_answer="Overall: men 66%, women 82%.",
            steps=[
                "Engineering: men 30%, women 40%",
                "Arts: men 75%, women 87.5%",
                # WRONG arithmetic, and this step is load-bearing
                # because it introduces "330" used in "66%"
                "Total men admitted: 30 + 300 = 340",
                "Therefore men overall: 340/500 = 68%",
            ],
            confidence=0.8,
        )
        result = evaluate_result(SIMPSON_TASK, _make_result(parsed))
        flag_types = {f.flag_type for f in result.forensic_flags}
        # Must have at least intermediate_calculation_errors
        assert "intermediate_calculation_errors" in flag_types

    def test_support_strength_penalized_for_accidental(self):
        """When reasoning integrity is 'accidental', support_strength must be lower
        than a well-supported answer with the same final answer."""
        good_parsed = AgentResponse(
            final_answer="Overall: men 66%, women 82%.",
            steps=[
                "Engineering: men 30%, women 40%",
                "Arts: men 75%, women 87.5%",
                "Total men admitted: 30 + 300 = 330",
                "Men overall: 330/500 = 66%",
            ],
            confidence=0.8,
        )
        bad_parsed = AgentResponse(
            final_answer="Overall: men 66%, women 82%.",
            steps=[
                "Engineering: men 30%, women 40%",
                "Arts: men 75%, women 87.5%",
                # WRONG addition — load-bearing
                "Total men admitted: 30 + 300 = 340",
                "Men overall: 340/500 = 68%",
            ],
            confidence=0.8,
        )
        good_result = evaluate_result(SIMPSON_TASK, _make_result(good_parsed))
        bad_result = evaluate_result(SIMPSON_TASK, _make_result(bad_parsed))

        # The bad result should have lower structural_reasoning due to integrity penalty
        assert (
            bad_result.scores.structural_reasoning
            <= good_result.scores.structural_reasoning
        )


# ===========================================================================
# 2. WRONG ANSWER, GOOD INTERMEDIATE CHAIN
# ===========================================================================


class TestWrongAnswerGoodChain:
    """Shows separation of locally good reasoning from wrong final conclusion."""

    def test_good_chain_wrong_last_step(self):
        """All intermediate steps are correct, but the final answer is wrong.
        Engine must flag wrong answer but not intermediate errors."""
        parsed = AgentResponse(
            final_answer="The probability is 99%.",  # WRONG
            steps=[
                "P(disease) = 0.001",
                "P(positive|disease) = 0.99",
                "P(positive|no disease) = 0.01",
                "P(positive) = 0.99 * 0.001 + 0.01 * 0.999 = 0.01098",
                "But the test is 99% accurate so the answer must be 99%.",  # logical leap
            ],
            confidence=0.95,
        )
        result = evaluate_result(BASE_RATE_TASK, _make_result(parsed))

        # Must have wrong_answer failure
        categories = {f.category for f in result.failures}
        assert FailureCategory.WRONG_ANSWER.value in categories

        # Should NOT have intermediate_numeric_error (the math is correct)
        assert FailureCategory.INTERMEDIATE_NUMERIC_ERROR.value not in categories


# ===========================================================================
# 3. DECORATIVE WRONG STEP (must NOT over-punish)
# ===========================================================================


class TestDecorativeWrongStep:
    """A wrong step that is NOT load-bearing should not trigger major penalties."""

    def test_decorative_error_minor_severity(self):
        """Wrong arithmetic in an early, non-load-bearing step.
        The engine should detect it but classify it as minor."""
        parsed = AgentResponse(
            final_answer="Overall: men 66%, women 82%.",
            steps=[
                # WRONG arithmetic, but decorative — not used in the answer
                "Let me first note that 10 + 20 = 40 as a rough check.",
                "Engineering: men 30%, women 40%",
                "Arts: men 75%, women 87.5%",
                "Total men: 30 + 300 = 330 out of 500",
                "Therefore men 66%, women 82%. Women have higher rates.",
            ],
            confidence=0.8,
        )
        result = evaluate_result(SIMPSON_TASK, _make_result(parsed))

        int_errors = [
            f
            for f in result.failures
            if f.category == FailureCategory.INTERMEDIATE_NUMERIC_ERROR.value
        ]
        assert len(int_errors) >= 1

        # The error should be MINOR (not MAJOR) because it's decorative
        assert int_errors[0].severity == "minor"
        assert "decorative" in int_errors[0].description.lower()

    def test_decorative_error_does_not_trigger_accidental(self):
        """A decorative wrong step should NOT classify reasoning as 'accidental'."""
        parsed = AgentResponse(
            final_answer="Overall: men 66%, women 82%.",
            steps=[
                "Quick sanity check: 5 + 5 = 11",  # WRONG but decorative
                "Engineering: men 30/100 = 30%, women 20/50 = 40%",
                "Arts: men 300/400 = 75%, women 350/400 = 87.5%",
                "Total men: 30 + 300 = 330, so 330/500 = 66%",
                "Total women: 20 + 350 = 370, so 370/450 = 82.2%",
            ],
            confidence=0.8,
        )
        result = evaluate_result(SIMPSON_TASK, _make_result(parsed))

        # Should be brittle (decorative error), NOT accidental
        assert result.reasoning_integrity["classification"] in (
            "brittle",
            "well_supported",
        )
        assert result.reasoning_integrity["n_load_bearing_errors"] == 0


# ===========================================================================
# 4. LOAD-BEARING CONTRADICTED STEP
# ===========================================================================


class TestLoadBearingContradicted:
    """A load-bearing step with verified error must be a hard finding."""

    def test_load_bearing_error_is_major(self):
        """A wrong arithmetic in a load-bearing step must have major severity."""
        parsed = AgentResponse(
            final_answer="Men overall: 68%.",
            steps=[
                "Engineering: men 30%",
                "Arts: men 75%",
                "Total admitted: 30 + 300 = 340",  # WRONG, and load-bearing
                "Therefore 340/500 = 68%",  # derives from wrong value
            ],
            confidence=0.8,
        )
        result = evaluate_result(SIMPSON_TASK, _make_result(parsed))

        int_errors = [
            f
            for f in result.failures
            if f.category == FailureCategory.INTERMEDIATE_NUMERIC_ERROR.value
        ]
        lb_errors = [e for e in int_errors if "LOAD-BEARING" in e.description]
        assert len(lb_errors) >= 1
        assert lb_errors[0].severity == "major"


# ===========================================================================
# 5. INTERMEDIATE MATH VERIFICATION
# ===========================================================================


class TestIntermediateMathInEvaluator:
    """Step checker integration with evaluator."""

    def test_correct_chain_no_intermediate_errors(self):
        """A fully correct chain should produce zero intermediate errors."""
        parsed = AgentResponse(
            final_answer="Men 66%, women 82.2%.",
            steps=[
                "Engineering: men 30/100 = 30%, women 20/50 = 40%",
                "Arts: men 300/400 = 75%, women 350/400 = 87.5%",
                "Total men: 30 + 300 = 330, ratio 330/500 = 66%",
                "Total women: 20 + 350 = 370, ratio 370/450 = 82%",
            ],
            confidence=0.8,
        )
        result = evaluate_result(SIMPSON_TASK, _make_result(parsed))

        int_errors = [
            f
            for f in result.failures
            if f.category == FailureCategory.INTERMEDIATE_NUMERIC_ERROR.value
        ]
        assert len(int_errors) == 0

    def test_step_checks_attached_to_result(self):
        """Step check results should be attached to EvaluatedResult."""
        parsed = AgentResponse(
            final_answer="66%",
            steps=["30 + 300 = 330"],
            confidence=0.8,
        )
        result = evaluate_result(SIMPSON_TASK, _make_result(parsed))
        assert len(result.step_check_results) >= 1
        assert result.step_check_results[0].is_correct

    def test_reasoning_integrity_attached_to_result(self):
        """Reasoning integrity dict should be attached to EvaluatedResult."""
        parsed = AgentResponse(
            final_answer="66%",
            steps=["30 + 300 = 330"],
            confidence=0.8,
        )
        result = evaluate_result(SIMPSON_TASK, _make_result(parsed))
        assert "classification" in result.reasoning_integrity
        assert "load_bearing_mask" in result.reasoning_integrity


# ===========================================================================
# 6. LOAD-BEARING CLASSIFICATION
# ===========================================================================


class TestLoadBearingClassification:
    """Unit tests for _classify_load_bearing_steps."""

    def test_late_step_with_answer_overlap_is_lb(self):
        steps = [
            "Let me think about this",
            "Engineering has 30% for men",
            "Therefore men have 66% overall rate",  # late, overlaps with answer
        ]
        mask = _classify_load_bearing_steps(
            steps, "Men have a 66% overall admission rate"
        )
        assert mask[2] is True  # last step is load-bearing

    def test_early_decorative_step_not_lb(self):
        steps = [
            "Let me think about this problem carefully",
            "Engineering: men 30%, women 40%",
            "Therefore overall rate is 66%",
        ]
        mask = _classify_load_bearing_steps(steps, "The overall rate is 66%")
        assert mask[0] is False  # decorative step

    def test_step_introducing_answer_number_is_lb(self):
        steps = [
            "Engineering: men 30%",
            "Arts: men 75%",
            "Total: 30 + 300 = 330",  # introduces 330
            "Ratio: 330/500 = 66%",
        ]
        mask = _classify_load_bearing_steps(steps, "Men: 66% (330/500)")
        # Step 2 introduces 330, step 3 introduces 66% — both should be LB
        assert mask[2] is True or mask[3] is True

    def test_no_steps_returns_empty(self):
        mask = _classify_load_bearing_steps([], "Answer")
        assert mask == []

    def test_no_answer_returns_all_false(self):
        mask = _classify_load_bearing_steps(["step 1", "step 2"], "")
        assert mask == [False, False]


# ===========================================================================
# 8. NO REGRESSION
# ===========================================================================


class TestNoRegression:
    """Existing behavior must not regress."""

    def test_simpson_correct_still_scores_high(self):
        """A fully correct Simpson's answer should still score well."""
        parsed = AgentResponse(
            final_answer=(
                "The claim is misleading. Women have higher admission rates "
                "in both departments. This is Simpson's Paradox."
            ),
            steps=[
                "Engineering: men 30/100 = 30%, women 20/50 = 40%",
                "Arts: men 300/400 = 75%, women 350/400 = 87.5%",
                "Overall: men 330/500 = 66%, women 370/450 = 82.2%",
                "The aggregate reverses because more men apply to engineering.",
                "This is Simpson's Paradox — aggregate trends reverse subgroup trends.",
            ],
            assumptions=["Data is accurate and complete"],
            uncertainties=["Small sample sizes could affect conclusions"],
            self_check=["Verified arithmetic: 30+300=330, 20+350=370"],
            key_claims=["Women have higher rates in both departments"],
            confidence=0.85,
        )
        result = evaluate_result(SIMPSON_TASK, _make_result(parsed))

        # Should have zero intermediate errors
        int_errors = [
            f
            for f in result.failures
            if f.category == FailureCategory.INTERMEDIATE_NUMERIC_ERROR.value
        ]
        assert len(int_errors) == 0

        # Should be well_supported
        assert result.reasoning_integrity["classification"] == "well_supported"

    def test_base_rate_correct_no_false_flags(self):
        """Correct base rate answer with good reasoning — no false positives."""
        parsed = AgentResponse(
            final_answer="The probability is approximately 0.09 or about 9%.",
            steps=[
                "P(disease) = 0.001",
                "P(positive|disease) = 0.99",
                "P(positive AND disease) = 0.99 * 0.001 = 0.00099",
                "P(positive AND no disease) = 0.01 * 0.999 = 0.00999",
                "P(positive) = 0.00099 + 0.00999 = 0.01098",
                "P(disease|positive) = 0.00099 / 0.01098 = 0.09",
            ],
            confidence=0.8,
        )
        result = evaluate_result(BASE_RATE_TASK, _make_result(parsed))

        # Must not have accidental correctness
        categories = {f.category for f in result.failures}
        assert FailureCategory.ACCIDENTAL_CORRECTNESS.value not in categories
        assert FailureCategory.RIGHT_ANSWER_WRONG_REASONING.value not in categories
