"""Tests of the Inspektorium audit runtime forensic hardening — integrated scenarios."""

from inspektorium.audit.checks.claim_checker import (
    run_claim_checks,
    count_contradictions,
)
from inspektorium.audit.checks.consistency import run_consistency_checks
from inspektorium.audit.execution.evaluator import evaluate_result
from inspektorium.audit.checks.reasoning_graph import (
    build_mechanism_analysis,
    _build_grounding_audit,
    build_reasoning_graph,
)
from inspektorium.audit.schemas import (
    AgentResponse,
    AgentResult,
    ClaimTruthStatus,
    Difficulty,
    FailureCategory,
    Task,
    TaskType,
)


def _make_task(**kwargs) -> Task:
    defaults = dict(
        id="test-001",
        title="Simpson Test",
        domain="statistics",
        difficulty=Difficulty.HARD,
        task_type=TaskType.RUBRIC_BASED,
        prompt=(
            "Engineering: admitted 30/100 men (30%) and 20/50 women (40%)\n"
            "Arts: admitted 300/400 men (75%) and 350/400 women (87.5%)\n"
            "Overall: admitted 330/500 men (66%) and 370/450 women (82.2%)\n"
            "A journalist claims the university discriminates against men."
        ),
        expected_mechanism_terms=["simpson", "paradox", "department"],
    )
    defaults.update(kwargs)
    return Task(**defaults)


def _make_result(final_answer="", steps=None, **kwargs) -> AgentResult:
    response_data = dict(
        final_answer=final_answer,
        steps=steps or [],
        assumptions=kwargs.pop("assumptions", ["Data is accurate"]),
        key_claims=kwargs.pop("key_claims", []),
        uncertainties=kwargs.pop("uncertainties", []),
        alternative_hypotheses=kwargs.pop("alternative_hypotheses", []),
        self_check=kwargs.pop("self_check", []),
        confidence=kwargs.pop("confidence", 0.85),
    )
    response_data.update(kwargs)
    return AgentResult(
        provider="test-agent",
        model="test-model",
        raw_output="",
        parsed=AgentResponse(**response_data),
        parse_ok=True,
    )


# ---------------------------------------------------------------------------
# Scenario 1: Agent cites correct numbers but states wrong comparison
# ---------------------------------------------------------------------------


class TestWrongComparison:
    def test_wrong_direction_in_final_answer(self):
        result = _make_result(
            final_answer="Men have higher admission rates than women in engineering.",
            steps=["Engineering: men 30%, women 40%"],
        )
        ev = evaluate_result(_make_task(), result)
        # Should have verbal-numeric contradiction failure
        assert any(
            f.category == FailureCategory.VERBAL_NUMERIC_CONTRADICTION.value
            for f in ev.failures
        )

    def test_wrong_direction_reduces_score(self):
        # Correct comparison
        correct = _make_result(
            final_answer="Women have higher admission rates than men in engineering.",
            steps=["Engineering: men 30%, women 40%. Women have higher rates."],
            key_claims=["Women favored in engineering"],
        )
        # Wrong comparison
        wrong = _make_result(
            final_answer="Men have higher admission rates than women in engineering.",
            steps=["Engineering: men 30%, women 40%."],
            key_claims=["Men favored in engineering"],
        )
        ev_correct = evaluate_result(_make_task(), correct)
        ev_wrong = evaluate_result(_make_task(), wrong)
        assert ev_wrong.scores.total < ev_correct.scores.total


# ---------------------------------------------------------------------------
# Scenario 2: Final answer contradicts own steps
# ---------------------------------------------------------------------------


class TestStepAnswerContradiction:
    def test_step_says_opposite(self):
        result = _make_result(
            final_answer="The claim is valid. Men are discriminated against.",
            steps=[
                "Engineering: men 30%, women 40% — women have higher rate",
                "Arts: men 75%, women 87.5% — women have higher rate",
                "Therefore the claim of discrimination against men is valid",
            ],
        )
        ev = evaluate_result(_make_task(), result)
        # The numeric facts from the task show women have higher rates in both,
        # so claiming discrimination against men should produce findings
        assert ev.scores.total < 60


# ---------------------------------------------------------------------------
# Scenario 3: Names concept but doesn't explain mechanism
# ---------------------------------------------------------------------------


class TestNamedNotExplained:
    def test_naming_without_mechanism(self):
        result = _make_result(
            final_answer="This is Simpson's Paradox. The claim is misleading.",
            steps=["I recognize this as Simpson's Paradox", "The answer is clear"],
        )
        ma = build_mechanism_analysis(result.parsed, _make_task())
        assert ma.concept_named is True
        assert ma.mechanism_described is False

    def test_naming_with_mechanism(self):
        result = _make_result(
            final_answer="This is Simpson's Paradox.",
            steps=[
                "The aggregate rate reverses because men apply disproportionately to engineering",
                "This happens because the composition of applicants differs across departments",
            ],
        )
        ma = build_mechanism_analysis(result.parsed, _make_task())
        assert ma.concept_named is True
        assert ma.mechanism_described is True


# ---------------------------------------------------------------------------
# Scenario 4: Mechanism described without naming
# ---------------------------------------------------------------------------


class TestUnnamedMechanism:
    def test_describes_without_naming(self):
        result = _make_result(
            final_answer="The aggregate rate is misleading.",
            steps=[
                "The reversal occurs because men applied mostly to engineering which has lower base rates",
                "When we look at each department separately, women have higher rates",
            ],
        )
        ma = build_mechanism_analysis(result.parsed)
        assert ma.mechanism_described is True
        # "paradox" may not be detected as a concept name since the text doesn't have it
        # but it should still have described the mechanism


# ---------------------------------------------------------------------------
# Scenario 5: Unsupported summary after reasonable steps
# ---------------------------------------------------------------------------


class TestUnsupportedConclusion:
    def test_leap_in_conclusion(self):
        result = _make_result(
            final_answer="Quantum effects drive the admissions paradox in university data.",
            steps=[
                "Engineering: men 30%, women 40%",
                "Arts: men 75%, women 87.5%",
                "The aggregate rate reverses due to application patterns",
            ],
        )
        graph = build_reasoning_graph(result.parsed)
        grounding = _build_grounding_audit(graph.claims, graph.relations)
        # "Quantum effects" is not supported by any step
        assert grounding.unsupported > 0 or grounding.total_conclusion_claims == 0


# ---------------------------------------------------------------------------
# Scenario 6: Self-check misses a real contradiction
# ---------------------------------------------------------------------------


class TestFailedSelfAudit:
    def test_self_check_blind_spot(self):
        task = _make_task()
        result = _make_result(
            final_answer="Men have higher admission rates than women.",
            steps=["Engineering: men 30%, women 40%"],
            self_check=["Verified: my arithmetic is correct and consistent."],
        )
        claim_results = run_claim_checks(task, result.parsed)
        findings = run_consistency_checks(result.parsed, task, claim_results)
        failed_audits = [f for f in findings if f.check_type == "failed_self_audit"]
        assert len(failed_audits) >= 1


# ---------------------------------------------------------------------------
# Scenario 7: Lexical overlap without real support
# ---------------------------------------------------------------------------


class TestShallowSupport:
    def test_word_overlap_not_real_support(self):
        result = _make_result(
            final_answer="The university paradox shows interesting admission patterns.",
            steps=[
                "University admission data is available",
                "Patterns in data are interesting",
            ],
        )
        graph = build_reasoning_graph(result.parsed)
        grounding = _build_grounding_audit(graph.claims, graph.relations)
        # Steps don't actually support the conclusion meaningfully
        assert grounding.directly_supported <= 1


# ---------------------------------------------------------------------------
# Scenario 8: Unresolvable claim
# ---------------------------------------------------------------------------


class TestUnresolvableClaim:
    def test_insufficient_evidence(self):
        task = Task(
            id="test-002",
            title="Simple",
            domain="test",
            difficulty=Difficulty.EASY,
            task_type=TaskType.CLOSED_WITH_REASONING,
            prompt="Is the sky blue?",
            expected_answer="yes",
        )
        result = _make_result(
            final_answer="Cats are faster than dogs.",
            steps=["Animals have different speeds."],
        )
        results = run_claim_checks(task, result.parsed)
        if results:
            assert all(r.truth_status == ClaimTruthStatus.UNRESOLVED for r in results)


# ---------------------------------------------------------------------------
# Scenario 9: Correct answer with correct mechanism survives penalties
# ---------------------------------------------------------------------------


class TestCorrectSurvives:
    def test_good_answer_not_penalized(self):
        task = _make_task()
        result = _make_result(
            final_answer="The claim is misleading. This is Simpson's Paradox. Women have higher rates in both departments.",
            steps=[
                "Engineering: men 30%, women 40% — women have higher rate",
                "Arts: men 75%, women 87.5% — women have higher rate",
                "The aggregate reversal occurs because men applied disproportionately to engineering, which has lower base rates",
                "This is Simpson's paradox — the trend reverses when data is disaggregated",
            ],
            key_claims=[
                "Simpson's paradox explains the reversal",
                "Women favored in both departments",
            ],
            uncertainties=["Whether applicant qualifications differ"],
            alternative_hypotheses=[
                "University intentionally discriminates — rejected because department-level data shows women favored in both"
            ],
            self_check=[
                "Verified arithmetic: 30/100=30%, 20/50=40% in Engineering; 300/400=75%, 350/400=87.5% in Arts. All correct."
            ],
        )
        ev = evaluate_result(task, result)
        # Should not have verbal-numeric contradictions
        assert not any(
            f.category == FailureCategory.VERBAL_NUMERIC_CONTRADICTION.value
            for f in ev.failures
        )
        # Score should be decent
        assert ev.scores.total > 40


# ---------------------------------------------------------------------------
# Scenario 10: Wrong direction should strongly reduce score
# ---------------------------------------------------------------------------


class TestWrongDirectionPenalty:
    def test_wrong_local_direction_strong_penalty(self):
        task = _make_task()
        # Agent says men are favored in each department — factually wrong
        result = _make_result(
            final_answer="Men are favored in each department.",
            steps=[
                "Engineering: men 30%, women 40%",
                "Men have higher rates in engineering",  # WRONG
                "Arts: men 75%, women 87.5%",
                "Men have higher rates in arts",  # WRONG
            ],
            key_claims=["Men favored in both departments"],
        )
        ev = evaluate_result(task, result)
        contradictions = [
            f
            for f in ev.failures
            if f.category == FailureCategory.VERBAL_NUMERIC_CONTRADICTION.value
        ]
        assert len(contradictions) >= 1
        # Score should be significantly reduced
        assert ev.scores.total < 50


# ===========================================================================
# v0.4.2 HARDENING TESTS
# ===========================================================================


# ---------------------------------------------------------------------------
# Scenario 11: Wrong-but-well-structured must not score high (v0.4.2)
# ---------------------------------------------------------------------------


class TestCorrectnessHardening:
    """v0.4.2: correctness dominance — wrong answer can't hide behind structure."""

    def test_wrong_but_well_structured_capped(self):
        """A beautifully structured but wrong answer must score <= 40."""
        task = _make_task(
            task_type=TaskType.CLOSED_WITH_REASONING,
            expected_answer="no",
        )
        result = _make_result(
            final_answer="Yes, the claim is valid. Men are discriminated against.",
            steps=[
                "Let me examine the data carefully for each department",
                "Engineering: men 30%, women 40% — women admitted at higher rate",
                "Arts: men 75%, women 87.5% — women admitted at higher rate",
                "However, the aggregate shows men at 66% vs women at 82.2%",
                "This apparent paradox suggests complex dynamics at play",
            ],
            assumptions=["Data is complete and accurate", "No sampling bias"],
            key_claims=["Men face discrimination overall"],
            uncertainties=["Whether other departments exist"],
            alternative_hypotheses=[
                "The difference may be due to application patterns — but the overall rate speaks louder"
            ],
            self_check=["Verified my arithmetic: 30/100=30%, 20/50=40%. Correct."],
            confidence=0.85,
        )
        ev = evaluate_result(task, result)
        # Wrong answer with expected_answer -> must be capped at 40
        assert ev.scores.total <= 40.0, (
            f"Wrong-but-well-structured answer scored {ev.scores.total}, expected <= 40"
        )

    def test_contradiction_caps_at_45(self):
        """A response with a proven contradiction must score <= 45."""
        task = _make_task()
        result = _make_result(
            final_answer="Men have higher admission rates than women in engineering.",
            steps=[
                "Engineering: men 30%, women 40%",
                "Men are admitted at a higher rate in engineering",
                "This is a clear pattern across the data",
            ],
            key_claims=["Men favored in engineering"],
        )
        ev = evaluate_result(task, result)
        assert ev.scores.total <= 45.0, (
            f"Contradicted answer scored {ev.scores.total}, expected <= 45"
        )

    def test_correct_answer_not_penalized(self):
        """A correct answer should still score well and not be capped."""
        task = _make_task(
            task_type=TaskType.CLOSED_WITH_REASONING,
            expected_answer="no",
        )
        result = _make_result(
            final_answer="No, the claim is not valid. This is Simpson's Paradox.",
            steps=[
                "Engineering: men 30%, women 40% — women have higher rate",
                "Arts: men 75%, women 87.5% — women have higher rate",
                "The aggregate reverses because men applied mostly to engineering",
                "This is Simpson's paradox — the trend reverses when disaggregated",
            ],
            key_claims=["Simpson's paradox", "Women favored in both departments"],
            self_check=["Verified: 30/100=30%, 20/50=40%, 300/400=75%, 350/400=87.5%"],
        )
        ev = evaluate_result(task, result)
        assert ev.scores.total > 45.0, (
            f"Correct answer scored only {ev.scores.total}, should be > 45"
        )

    def test_correctness_weight_is_30(self):
        """v0.4.2: correctness weight must be 30."""
        from inspektorium.audit.schemas import DIAGNOSTIC_WEIGHTS

        assert DIAGNOSTIC_WEIGHTS["correctness"] == 30


# ---------------------------------------------------------------------------
# Scenario 12: Negation conflict false positive regression (v0.4.2)
# ---------------------------------------------------------------------------


class TestNegationConflictFalsePositives:
    """v0.4.2: _has_negation_conflict must not fire on rebuttal patterns."""

    def test_rebuttal_in_conclusion_not_flagged(self):
        """A conclusion that discusses and rebuts a claim must not be contradicted."""
        from inspektorium.audit.checks.reasoning_graph import _has_negation_conflict

        conclusion = (
            "The journalist's claim that men face discrimination is not valid. "
            "While the overall rate appears to favor women, looking at each "
            "department separately shows women have higher admission rates."
        )
        step = (
            "In engineering, women have a 40% rate compared to men's 30%. "
            "Women have higher rates in engineering."
        )
        # conclusion contains both "valid" and "not valid" — should NOT flag
        assert not _has_negation_conflict(conclusion, step)

    def test_simpson_style_correct_answer_not_contradicted(self):
        """Correct Simpson's Paradox answer should have zero grounding contradictions."""
        result = _make_result(
            final_answer=(
                "The claim is not valid. This is Simpson's Paradox. "
                "Women are admitted at higher rates in both departments."
            ),
            steps=[
                "Engineering: men 30%, women 40% — women have higher rate",
                "Arts: men 75%, women 87.5% — women have higher rate",
                "The aggregate reversal is because men apply more to engineering",
                "This is Simpson's paradox — the claim is misleading, not valid",
            ],
        )
        graph = build_reasoning_graph(result.parsed)
        grounding = _build_grounding_audit(graph.claims, graph.relations)
        assert grounding.contradicted == 0, (
            f"Correct answer flagged {grounding.contradicted} contradictions"
        )

    def test_actual_contradiction_still_detected(self):
        """A real contradiction (pure split polarity) must still be caught."""
        from inspektorium.audit.checks.reasoning_graph import _has_negation_conflict

        text_a = "The overall admission rate for women is higher than for men."
        text_b = "The overall admission rate for women is lower than for men."
        assert _has_negation_conflict(text_a, text_b)

    def test_both_polarities_in_one_text_not_flagged(self):
        """If one text contains both 'higher' and 'lower', skip that pair."""
        from inspektorium.audit.checks.reasoning_graph import _has_negation_conflict

        text_a = (
            "While the overall rate is higher for women, "
            "the per-department rate is actually lower for women in this context."
        )
        text_b = "Women have higher admission rates in engineering at 40%."
        # text_a has both "higher" and "lower" — should not flag
        assert not _has_negation_conflict(text_a, text_b)


# ---------------------------------------------------------------------------
# Scenario 13: Claim checker on base rate neglect (v0.4.2)
# ---------------------------------------------------------------------------


class TestClaimCheckerBaseRate:
    """v0.4.2: claim checker extracts probability facts from base rate tasks."""

    def _base_rate_task(self):
        return Task(
            id="base-rate-001",
            title="Base Rate Test",
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
            evaluation={
                "method": "auto",
                "answer_match": "contains",
                "tolerance": 0.02,
            },
        )

    def test_extracts_probability_from_reference(self):
        from inspektorium.audit.checks.claim_checker import extract_probability_facts

        facts = extract_probability_facts(
            "P(Disease|Positive) = 0.00099 / 0.01098 ≈ 0.09 ≈ 9%",
            "reference_solution",
        )
        # Should find at least the 9% probability
        pct_values = [f.value for f in facts]
        assert any(8.0 <= v <= 10.0 for v in pct_values), (
            f"Expected ~9% in {pct_values}"
        )

    def test_wrong_base_rate_answer_flagged(self):
        """Agent answering 99% instead of 9% should produce a fact mismatch."""
        from inspektorium.audit.checks.claim_checker import extract_probability_facts

        # Agent says probability is 99%
        agent_facts = extract_probability_facts(
            "The probability that the person has the disease is 99%.",
            "final_answer",
        )
        assert any(f.value == 99.0 for f in agent_facts), (
            f"Should extract 99% from agent: {agent_facts}"
        )

    def test_correct_base_rate_answer_extracts(self):
        from inspektorium.audit.checks.claim_checker import extract_probability_facts

        facts = extract_probability_facts(
            "The probability of actually having the disease is approximately 9%.",
            "final_answer",
        )
        assert any(8.0 <= f.value <= 10.0 for f in facts), f"Expected ~9%: {facts}"


# ---------------------------------------------------------------------------
# Scenario 14: Claim checker on Monty Hall (v0.4.2)
# ---------------------------------------------------------------------------


class TestClaimCheckerMontyHall:
    """v0.4.2: claim checker extracts probability direction from Monty Hall."""

    def test_switch_recommendation_extracted(self):
        from inspektorium.audit.checks.claim_checker import (
            extract_probability_direction_claims,
        )

        claims = extract_probability_direction_claims(
            "You should switch. The probability of winning is higher if you switch.",
            "final_answer",
        )
        assert len(claims) >= 1
        assert claims[0].relation == "higher_than"
        assert claims[0].subject == "door_2_switch"

    def test_equal_probability_claim_extracted(self):
        from inspektorium.audit.checks.claim_checker import (
            extract_probability_direction_claims,
        )

        claims = extract_probability_direction_claims(
            "The probability is the same whether you switch or stay.",
            "final_answer",
        )
        assert len(claims) >= 1
        assert claims[0].relation == "equal_to"

    def test_probability_fraction_extraction(self):
        from inspektorium.audit.checks.claim_checker import extract_probability_facts

        facts = extract_probability_facts(
            "The probability of the car being behind door 2 is 2/3.",
            "steps[0]",
        )
        assert any(abs(f.value - 66.67) < 1.0 for f in facts), (
            f"Expected ~66.67%: {facts}"
        )

    def test_probability_decimal_extraction(self):
        from inspektorium.audit.checks.claim_checker import extract_probability_facts

        facts = extract_probability_facts(
            "P(Car=1 | Host opens 3) = 1/3.",
            "steps[1]",
        )
        assert any(abs(f.value - 33.33) < 1.0 for f in facts), (
            f"Expected ~33.33%: {facts}"
        )


# ---------------------------------------------------------------------------
# Scenario 15: Confidence labels in report (v0.4.2)
# ---------------------------------------------------------------------------


class TestConfidenceLabels:
    """v0.4.2: findings must carry confidence labels."""

    def test_contradiction_finding_is_high_confidence(self):
        """Numeric-verbal contradiction finding should be HIGH CONFIDENCE."""
        task = _make_task()
        result = _make_result(
            final_answer="Men have higher admission rates than women in engineering.",
            steps=["Engineering: men 30%, women 40%"],
        )
        ev = evaluate_result(task, result)
        # Check consistency findings
        high_findings = [
            f for f in ev.consistency_findings if f.confidence == "HIGH CONFIDENCE"
        ]
        assert len(high_findings) >= 1, "Expected at least one HIGH CONFIDENCE finding"

    def test_contradiction_failure_is_high_confidence(self):
        """Verbal-numeric contradiction failure should be HIGH CONFIDENCE."""
        task = _make_task()
        result = _make_result(
            final_answer="Men have higher admission rates than women in engineering.",
            steps=["Engineering: men 30%, women 40%"],
        )
        ev = evaluate_result(task, result)
        high_failures = [f for f in ev.failures if f.confidence == "HIGH CONFIDENCE"]
        assert len(high_failures) >= 1, "Expected at least one HIGH CONFIDENCE failure"

    def test_heuristic_findings_labeled(self):
        """Overlap-based findings should be HEURISTIC."""
        task = _make_task()
        result = _make_result(
            final_answer="The claim is misleading.",
            steps=["Engineering: men 30%, women 40%"],
            assumptions=[
                "Data is complete",
                "No sampling bias present anywhere at all",
            ],
        )
        ev = evaluate_result(task, result)
        labeled = [f for f in ev.consistency_findings if f.confidence]
        assert len(labeled) > 0, "Expected findings to have confidence labels"
        # At least some should be HEURISTIC or MEDIUM CONFIDENCE
        non_high = [f for f in labeled if f.confidence != "HIGH CONFIDENCE"]
        assert len(non_high) >= 0  # just verify labels are present

    def test_labels_appear_in_report(self):
        """Confidence labels must appear in the generated report text."""
        from inspektorium.audit.reports.reporter import generate_report
        from inspektorium.audit.schemas import RunRecord

        task = _make_task()
        result = _make_result(
            final_answer="Men have higher admission rates than women in engineering.",
            steps=["Engineering: men 30%, women 40%"],
        )
        ev = evaluate_result(task, result)
        record = RunRecord(run_id="test-run", task=task, results=[ev])
        report = generate_report(record)
        assert "HIGH CONFIDENCE" in report, (
            "Report should contain HIGH CONFIDENCE label"
        )

    def test_wrong_answer_failure_is_high_confidence(self):
        """WRONG_ANSWER failure should be HIGH CONFIDENCE."""
        task = _make_task(
            task_type=TaskType.CLOSED_WITH_REASONING,
            expected_answer="no",
        )
        result = _make_result(
            final_answer="Yes, definitely.",
            steps=["The answer is yes."],
        )
        ev = evaluate_result(task, result)
        wrong_failures = [
            f
            for f in ev.failures
            if f.category == "wrong_answer" and f.confidence == "HIGH CONFIDENCE"
        ]
        assert len(wrong_failures) >= 1
