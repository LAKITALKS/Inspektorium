"""v0.4.2: Claim checker validation across all 3 task shapes.

Documents for each shape:
  - what is reliably extracted
  - what is reliably verified
  - what remains blind
  - what patterns are intentionally unsupported
"""

from agent_arena.claim_checker import (
    count_contradictions,
    extract_comparative_claims,
    extract_numeric_facts,
    extract_probability_direction_claims,
    extract_probability_facts,
    run_claim_checks,
)
from agent_arena.schemas import (
    AgentResponse,
    AgentResult,
    ClaimTruthStatus,
    Difficulty,
    EvaluationConfig,
    Task,
    TaskType,
)


# ===========================================================================
# SHAPE 1: Simpson's Paradox
# ===========================================================================
# Reliably extracted: percentages, fractions, entity context, comparative claims
# Reliably verified:  directional comparisons (higher/lower) per context
# Blind:              implicit comparisons, semantic equivalence
# Unsupported:        non-percentage claims, multi-hop inference

class TestSimpsonsParadox:
    """Validation of claim checker on Simpson's Paradox task shape."""

    TASK = Task(
        id="simpson-001", title="Simpson Test", domain="statistics",
        difficulty=Difficulty.HARD, task_type=TaskType.RUBRIC_BASED,
        prompt=(
            "Engineering: admitted 30/100 men (30%) and 20/50 women (40%)\n"
            "Arts: admitted 300/400 men (75%) and 350/400 women (87.5%)\n"
            "Overall: admitted 330/500 men (66%) and 370/450 women (82.2%)\n"
            "A journalist claims the university discriminates against men."
        ),
    )

    # --- Extraction ---

    def test_extracts_percentages_from_prompt(self):
        facts = extract_numeric_facts(self.TASK.prompt, "task_prompt")
        values = {(f.entity, f.value, f.context) for f in facts}
        # Must find men 30% in engineering, women 40% in engineering
        assert ("men", 30.0, "engineering") in values
        assert ("women", 40.0, "engineering") in values

    def test_extracts_fractions_from_prompt(self):
        facts = extract_numeric_facts(self.TASK.prompt, "task_prompt")
        # Fractions like 30/100 should also be extracted (as 30.0%)
        values = [f.value for f in facts if f.entity == "men" and f.context == "engineering"]
        assert 30.0 in values

    def test_extracts_overall_rates(self):
        facts = extract_numeric_facts(self.TASK.prompt, "task_prompt")
        overall = [(f.entity, f.value) for f in facts if f.context == "overall"]
        assert any(e == "men" and v == 66.0 for e, v in overall)

    def test_extracts_higher_than_claim(self):
        claims = extract_comparative_claims(
            "Women have higher admission rates than men in engineering.",
            "final_answer",
        )
        assert any(c.relation == "higher_than" and c.subject == "women" for c in claims)

    def test_extracts_discrimination_claim(self):
        claims = extract_comparative_claims(
            "The university discriminates against men.",
            "final_answer",
        )
        assert any(c.relation == "discriminates_against" for c in claims)

    # --- Verification ---

    def test_correct_comparison_supported(self):
        """Women > men in engineering is correct → SUPPORTED."""
        parsed = AgentResponse(
            final_answer="Women have higher admission rates than men in engineering.",
            steps=["Engineering: men 30%, women 40%."],
        )
        results = run_claim_checks(self.TASK, parsed)
        supported = [r for r in results if r.truth_status == ClaimTruthStatus.SUPPORTED]
        assert len(supported) >= 1

    def test_wrong_comparison_contradicted(self):
        """Men > women in engineering is wrong → CONTRADICTED."""
        parsed = AgentResponse(
            final_answer="Men have higher admission rates than women in engineering.",
            steps=["Engineering: men 30%, women 40%."],
        )
        results = run_claim_checks(self.TASK, parsed)
        contradicted = [r for r in results if r.truth_status == ClaimTruthStatus.CONTRADICTED]
        assert len(contradicted) >= 1

    def test_correct_answer_zero_contradictions(self):
        """A fully correct Simpson's answer should have 0 contradictions."""
        parsed = AgentResponse(
            final_answer=(
                "The claim is misleading. This is Simpson's Paradox. "
                "Women have higher rates in both departments."
            ),
            steps=[
                "Engineering: men 30%, women 40% — women have higher rate",
                "Arts: men 75%, women 87.5% — women have higher rate",
                "The aggregate reverses because men apply more to engineering",
            ],
        )
        results = run_claim_checks(self.TASK, parsed)
        assert count_contradictions(results) == 0

    # --- Known blind spots ---

    def test_implicit_comparison_unresolved(self):
        """Implicit comparison without keyword should be UNRESOLVED, not wrong."""
        parsed = AgentResponse(
            final_answer="The data is interesting.",
            steps=["Engineering has different rates."],
        )
        results = run_claim_checks(self.TASK, parsed)
        # No comparative claims extracted → nothing to verify
        assert all(r.truth_status != ClaimTruthStatus.CONTRADICTED for r in results)


# ===========================================================================
# SHAPE 2: Base Rate Neglect
# ===========================================================================
# Reliably extracted: probability values (%, decimal, P()-notation)
# Reliably verified:  probability value extraction
# Blind:              Bayesian derivation correctness, intermediate steps
# Unsupported:        multi-step calculation verification

class TestBaseRateNeglect:
    """Validation of claim checker on base rate neglect task shape."""

    TASK = Task(
        id="base-rate-001", title="Base Rate Test", domain="probability",
        difficulty=Difficulty.MEDIUM, task_type=TaskType.CLOSED_WITH_REASONING,
        prompt=(
            "A rare disease affects 1 in 1000 people. A test has 99% sensitivity "
            "and 1% false positive rate. A person tests positive. "
            "What is the probability they have the disease?"
        ),
        expected_answer="0.09",
        reference_solution="P(Disease|Positive) = 0.00099 / 0.01098 ≈ 0.09 ≈ 9%",
        evaluation=EvaluationConfig(method="auto", answer_match="contains", tolerance=0.02),
    )

    # --- Extraction ---

    def test_extracts_probability_from_p_notation_chain(self):
        """P(X) = ... ≈ ... ≈ 9% → extracts 9%."""
        facts = extract_probability_facts(
            "P(Disease|Positive) = 0.00099 / 0.01098 ≈ 0.09 ≈ 9%",
            "reference_solution",
        )
        assert any(8 <= f.value <= 10 for f in facts)

    def test_extracts_probability_from_simple_statement(self):
        """'probability is approximately 9%' → extracts 9%."""
        facts = extract_probability_facts(
            "The probability of having the disease is approximately 9%.",
            "final_answer",
        )
        assert any(8 <= f.value <= 10 for f in facts)

    def test_extracts_wrong_probability(self):
        """Common wrong answer: 'probability is 99%' → extracts 99%."""
        facts = extract_probability_facts(
            "The probability of having the disease is 99%.",
            "final_answer",
        )
        assert any(f.value == 99.0 for f in facts)

    def test_extracts_decimal_probability(self):
        """'probability is 0.09' → extracts as 9%."""
        facts = extract_probability_facts(
            "The probability that they have the disease is 0.09.",
            "final_answer",
        )
        assert any(8 <= f.value <= 10 for f in facts)

    # --- Verification ---

    def test_prompt_percentages_need_entity_context(self):
        """Task prompt '99% sensitivity' lacks entity context for extract_numeric_facts.
        This is a known limitation: the entity-based extractor only works for
        entity-comparison tasks (Simpson's Paradox). For base rate tasks,
        probability extraction is handled by extract_probability_facts instead."""
        facts = extract_numeric_facts(self.TASK.prompt, "task_prompt")
        # No entity-bound facts expected (no men/women/engineering entities)
        assert len(facts) == 0  # documents the limitation

        # But probability facts CAN be extracted from the reference solution
        prob_facts = extract_probability_facts(self.TASK.reference_solution, "ref")
        assert len(prob_facts) >= 1

    # --- Known blind spots ---

    def test_cannot_verify_bayesian_derivation(self):
        """We cannot verify intermediate Bayesian steps, only final values."""
        parsed = AgentResponse(
            final_answer="The probability is about 9%.",
            steps=[
                "P(Positive) = 0.99 * 0.001 + 0.01 * 0.999 = WRONG_VALUE",
                "P(Disease|Positive) = 0.00099 / WRONG = 9%",
            ],
        )
        results = run_claim_checks(self.TASK, parsed)
        # Engine cannot verify intermediate calculation correctness
        # It can only check the final claimed probability
        contradictions = count_contradictions(results)
        # No contradiction because the final value (9%) is correct
        # even though the derivation is wrong — this is a known blind spot
        assert contradictions == 0  # known limitation


# ===========================================================================
# SHAPE 3: Monty Hall Variant
# ===========================================================================
# Reliably extracted: probability fractions for doors, switch recommendation
# Reliably verified:  switch vs stay direction claims
# Blind:              host behavior reasoning, conditional probability chain
# Unsupported:        verifying WHY 2/3 is the right answer

class TestMontyHallVariant:
    """Validation of claim checker on Monty Hall variant task shape."""

    TASK = Task(
        id="monty-001", title="Monty Hall Lazy Host", domain="probability",
        difficulty=Difficulty.HARD, task_type=TaskType.CLOSED_WITH_REASONING,
        prompt=(
            "3 doors, car behind one. You pick door 1. "
            "Lazy host: if car behind door 1, randomly opens 2 or 3 (50/50). "
            "If car behind 2, opens 3. If car behind 3, opens 2. "
            "Host opens door 3. Probability car behind door 2?"
        ),
        expected_answer="2/3",
        reference_solution=(
            "P(Car=2 | Host opens 3) = (1/3 * 1) / (1/2) = 2/3. "
            "P(Car=1 | Host opens 3) = (1/3 * 1/2) / (1/2) = 1/3. "
            "You should switch."
        ),
        evaluation=EvaluationConfig(method="auto", answer_match="contains", tolerance=0.02),
    )

    # --- Extraction ---

    def test_extracts_fraction_probability(self):
        """'probability is 2/3' → 66.67%."""
        facts = extract_probability_facts(
            "The probability of the car being behind door 2 is 2/3.",
            "steps[0]",
        )
        assert any(abs(f.value - 66.67) < 1.0 for f in facts)

    def test_extracts_p_notation_fraction(self):
        """'P(Car=1 | Host opens 3) = 1/3' → 33.33%."""
        facts = extract_probability_facts(
            "P(Car=1 | Host opens 3) = 1/3.",
            "steps[1]",
        )
        assert any(abs(f.value - 33.33) < 1.0 for f in facts)

    def test_extracts_switch_recommendation(self):
        """'You should switch' → direction claim."""
        claims = extract_probability_direction_claims(
            "You should switch. Switching gives a 2/3 chance of winning.",
            "final_answer",
        )
        assert any(c.relation == "higher_than" and c.subject == "door_2_switch" for c in claims)

    def test_extracts_equal_probability_claim(self):
        """'Doesn't matter if you switch' → equal claim."""
        claims = extract_probability_direction_claims(
            "It doesn't matter whether you switch or stay.",
            "final_answer",
        )
        assert any(c.relation == "equal_to" for c in claims)

    # --- Verification ---

    def test_correct_switch_not_contradicted(self):
        """Correct answer (switch, 2/3) should not be contradicted."""
        parsed = AgentResponse(
            final_answer="You should switch. The probability the car is behind door 2 is 2/3.",
            steps=[
                "P(Car=2 | Host opens 3) = (1/3 * 1) / (1/2) = 2/3",
                "P(Car=1 | Host opens 3) = (1/3 * 1/2) / (1/2) = 1/3",
                "Therefore you should switch.",
            ],
        )
        results = run_claim_checks(self.TASK, parsed)
        assert count_contradictions(results) == 0

    # --- Known blind spots ---

    def test_right_answer_wrong_reasoning_not_caught(self):
        """Agent gets 2/3 by luck (standard Monty Hall) — not detectable."""
        parsed = AgentResponse(
            final_answer="Switch. Probability is 2/3 by standard Monty Hall logic.",
            steps=[
                "In Monty Hall you should always switch.",
                "The probability of winning by switching is 2/3.",
            ],
        )
        results = run_claim_checks(self.TASK, parsed)
        # The numeric answer 2/3 matches, and "should switch" is correct.
        # But the reasoning ignores the lazy host — this is NOT detectable
        # by the claim checker (it checks values, not reasoning quality).
        assert count_contradictions(results) == 0  # known limitation

    def test_wrong_probability_stays_unresolved_without_facts(self):
        """Without explicit fractions in steps, claim checker can't verify."""
        parsed = AgentResponse(
            final_answer="The probability is 50%. It doesn't matter.",
            steps=["Each door is equally likely after host opens one."],
        )
        results = run_claim_checks(self.TASK, parsed)
        # The "equal" direction claim may be detected but verification
        # depends on whether reference_solution facts are extracted.
        # At minimum, no false SUPPORTED status.
        for r in results:
            if r.truth_status == ClaimTruthStatus.SUPPORTED:
                # Should not claim 50/50 is supported
                assert "equal" not in r.claim.relation or abs(50 - 66.67) < 5
