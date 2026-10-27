"""Tests of the Inspektorium audit runtime claim checker — numeric/verbal consistency engine."""

from inspektorium.audit.checks.claim_checker import (
    check_claims_against_facts,
    extract_comparative_claims,
    extract_numeric_facts,
    run_claim_checks,
)
from inspektorium.audit.schemas import (
    AgentResponse,
    ClaimTruthStatus,
    ComparativeClaim,
    Difficulty,
    NumericFact,
    Task,
    TaskType,
)


# ---------------------------------------------------------------------------
# Numeric fact extraction
# ---------------------------------------------------------------------------


class TestNumericFactExtraction:
    def test_extracts_percentages(self):
        text = "Engineering: admitted 30/100 men (30%) and 20/50 women (40%)"
        facts = extract_numeric_facts(text, "test")
        values = {(f.entity, f.value) for f in facts}
        assert ("men", 30.0) in values
        assert ("women", 40.0) in values

    def test_extracts_fractions(self):
        text = "admitted 30/100 men"
        facts = extract_numeric_facts(text, "test")
        assert any(f.value == 30.0 and f.entity == "men" for f in facts)

    def test_overall_rate(self):
        text = "Overall: admitted 330/500 men (66%) and 370/450 women (82.2%)"
        facts = extract_numeric_facts(text, "test")
        values = {(f.entity, f.value) for f in facts}
        assert ("men", 66.0) in values or ("men", 66.0) in values


# ---------------------------------------------------------------------------
# Comparative claim extraction
# ---------------------------------------------------------------------------


class TestComparativeClaimExtraction:
    def test_higher_than_pattern(self):
        text = "Men have higher admission rates than women."
        claims = extract_comparative_claims(text, "test")
        assert any(c.relation == "higher_than" for c in claims)

    def test_discrimination_pattern(self):
        text = "The university discriminates against men."
        claims = extract_comparative_claims(text, "test")
        assert any(c.relation == "discriminates_against" for c in claims)

    def test_percentage_comparison(self):
        text = "66% of men versus 82.2% of women were admitted."
        claims = extract_comparative_claims(text, "test")
        assert len(claims) >= 1

    def test_lower_than_pattern(self):
        text = "Women are admitted at a lower rate than men in engineering."
        claims = extract_comparative_claims(text, "test")
        assert any(c.relation == "lower_than" for c in claims)


# ---------------------------------------------------------------------------
# Claim verification
# ---------------------------------------------------------------------------


class TestClaimVerification:
    def test_correct_higher_claim(self):
        claims = [
            ComparativeClaim(
                subject="women",
                object="men",
                relation="higher_than",
                metric="rate",
                source_field="test",
                source_text="women higher than men",
            )
        ]
        facts = [
            NumericFact(entity="women", metric="rate", value=82.2, source_field="task"),
            NumericFact(entity="men", metric="rate", value=66.0, source_field="task"),
        ]
        results = check_claims_against_facts(claims, facts)
        assert results[0].truth_status == ClaimTruthStatus.SUPPORTED

    def test_incorrect_higher_claim(self):
        """Agent says men have higher rates when they don't."""
        claims = [
            ComparativeClaim(
                subject="men",
                object="women",
                relation="higher_than",
                metric="rate",
                source_field="test",
                source_text="men have higher rates",
            )
        ]
        facts = [
            NumericFact(entity="men", metric="rate", value=30.0, source_field="task"),
            NumericFact(entity="women", metric="rate", value=40.0, source_field="task"),
        ]
        results = check_claims_against_facts(claims, facts)
        assert results[0].truth_status == ClaimTruthStatus.CONTRADICTED

    def test_reversed_direction(self):
        """Agent reverses the direction of comparison."""
        claims = [
            ComparativeClaim(
                subject="men",
                object="women",
                relation="lower_than",
                metric="rate",
                source_field="test",
                source_text="men lower rate",
            )
        ]
        facts = [
            NumericFact(entity="men", metric="rate", value=75.0, source_field="task"),
            NumericFact(entity="women", metric="rate", value=40.0, source_field="task"),
        ]
        results = check_claims_against_facts(claims, facts)
        assert results[0].truth_status == ClaimTruthStatus.CONTRADICTED

    def test_unresolvable_claim(self):
        claims = [
            ComparativeClaim(
                subject="cats",
                object="dogs",
                relation="higher_than",
                metric="rate",
                source_field="test",
                source_text="cats higher",
            )
        ]
        results = check_claims_against_facts(claims, [])
        assert results[0].truth_status == ClaimTruthStatus.UNRESOLVED


# ---------------------------------------------------------------------------
# Full pipeline: run_claim_checks
# ---------------------------------------------------------------------------


def _make_task() -> Task:
    return Task(
        id="test-001",
        title="Test",
        domain="test",
        difficulty=Difficulty.HARD,
        task_type=TaskType.RUBRIC_BASED,
        prompt=(
            "Engineering: admitted 30/100 men (30%) and 20/50 women (40%)\n"
            "Arts: admitted 300/400 men (75%) and 350/400 women (87.5%)\n"
            "Overall: admitted 330/500 men (66%) and 370/450 women (82.2%)"
        ),
    )


class TestRunClaimChecks:
    def test_correct_answer_no_contradictions(self):
        """Agent correctly says women have higher rates overall."""
        task = _make_task()
        response = AgentResponse(
            final_answer="Women have higher admission rates than men overall.",
            steps=["The overall rate for women is 82.2% vs 66% for men."],
        )
        results = run_claim_checks(task, response)
        contradictions = [
            r for r in results if r.truth_status == ClaimTruthStatus.CONTRADICTED
        ]
        assert len(contradictions) == 0

    def test_wrong_comparison_flagged(self):
        """Agent incorrectly says men have higher rates."""
        task = _make_task()
        response = AgentResponse(
            final_answer="Men have higher admission rates than women.",
            steps=["Men are admitted at 66% which is higher than women at 82.2%."],
        )
        results = run_claim_checks(task, response)
        contradictions = [
            r for r in results if r.truth_status == ClaimTruthStatus.CONTRADICTED
        ]
        assert len(contradictions) >= 1

    def test_correct_with_mechanism_survives(self):
        """Correct answer with correct mechanism should produce no contradictions."""
        task = _make_task()
        response = AgentResponse(
            final_answer="The claim is misleading. Women have higher rates in both departments.",
            steps=[
                "Engineering: men 30%, women 40%. Women have higher rate.",
                "Arts: men 75%, women 87.5%. Women have higher rate.",
                "The aggregate reversal is due to Simpson's paradox.",
            ],
        )
        results = run_claim_checks(task, response)
        contradictions = [
            r for r in results if r.truth_status == ClaimTruthStatus.CONTRADICTED
        ]
        assert len(contradictions) == 0


# ---------------------------------------------------------------------------
# Self-check misses contradiction
# ---------------------------------------------------------------------------


class TestSelfCheckBlindSpot:
    def test_self_check_misses_error(self):
        """Self-check says 'verified correct' but answer has wrong comparison."""
        task = _make_task()
        response = AgentResponse(
            final_answer="Men have higher admission rates than women in engineering.",
            steps=["Men are admitted at 30% and women at 40% in engineering."],
            self_check=["Verified: my arithmetic is correct and consistent."],
        )
        results = run_claim_checks(task, response)
        contradictions = [
            r for r in results if r.truth_status == ClaimTruthStatus.CONTRADICTED
        ]
        assert len(contradictions) >= 1
