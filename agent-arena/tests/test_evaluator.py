"""Tests for agent-arena v0.4 evaluator — forensic evaluation engine."""

from agent_arena.evaluator import (
    _all_text,
    _keyword_in_text,
    _normalize,
    _stem,
    evaluate_result,
    insight_match_score,
)
from agent_arena.schemas import (
    AgentResponse,
    AgentResult,
    Difficulty,
    FailureCategory,
    KeyInsight,
    RubricItem,
    Task,
    TaskType,
)


class TestUtilities:
    def test_normalize(self):
        assert _normalize("  Hello, World 42% ") == "hello world 42"

    def test_stem_basic(self):
        assert _stem("calculations") != "calculations"
        assert _stem("cat") == "cat"

    def test_keyword_in_text_exact(self):
        assert _keyword_in_text("paradox", "this is a paradox example")

    def test_keyword_in_text_stem(self):
        assert _keyword_in_text("aggregation", "the aggregate data shows")

    def test_keyword_in_text_hyphen(self):
        assert _keyword_in_text("department-level", "we look at department level data")

    def test_keyword_in_text_miss(self):
        assert not _keyword_in_text("quantum", "this is about statistics")

    def test_all_text_includes_key_claims(self):
        p = AgentResponse(final_answer="answer", steps=["step1"], key_claims=["important claim"])
        text = _all_text(p)
        assert "important claim" in text


class TestInsightMatching:
    def test_exact_match(self):
        ins = KeyInsight(keyword="simpson", variants=["simpson's paradox"])
        score, level = insight_match_score(ins, "this is simpson's paradox")
        assert score == 1.0
        assert level == "exact"

    def test_functional_match(self):
        ins = KeyInsight(
            keyword="xyznoexist", variants=[],
            functional_descriptions=["trend reverses when disaggregated"],
        )
        score, level = insight_match_score(ins, "the trend reverses when disaggregated into subgroups")
        assert score >= 0.5

    def test_miss(self):
        ins = KeyInsight(keyword="quantum", variants=["quantum entanglement"])
        score, level = insight_match_score(ins, "this is about statistics")
        assert score == 0.0


def _make_task(**kwargs) -> Task:
    defaults = dict(
        id="test-001", title="Test", domain="test",
        difficulty=Difficulty.MEDIUM, task_type=TaskType.CLOSED_WITH_REASONING,
        prompt="What is 2+2?", expected_answer="4",
    )
    defaults.update(kwargs)
    return Task(**defaults)


def _make_result(final_answer="4", **kwargs) -> AgentResult:
    response_data = dict(
        final_answer=final_answer,
        steps=["2+2 = 4 because basic arithmetic"],
        assumptions=["Basic arithmetic rules apply to this problem"],
        key_claims=["2+2 equals 4"],
        uncertainties=["None significant for this calculation"],
        alternative_hypotheses=["Could be modular arithmetic, but no — standard math is assumed here based on context"],
        self_check=["Verified: 2+2 = 4 by counting on fingers, also confirmed with calculator"],
        confidence=0.95,
    )
    response_data.update(kwargs)
    return AgentResult(
        provider="test-agent", model="test-model",
        raw_output="", parsed=AgentResponse(**response_data), parse_ok=True,
    )


class TestEvaluateResult:
    def test_correct_answer_scores_high(self):
        ev = evaluate_result(_make_task(), _make_result())
        assert ev.scores.correctness == 1.0
        assert ev.scores.total > 40

    def test_wrong_answer_gets_failure(self):
        ev = evaluate_result(_make_task(), _make_result(final_answer="5"))
        assert ev.scores.correctness == 0.0
        assert any(f.category == FailureCategory.WRONG_ANSWER.value for f in ev.failures)

    def test_unparseable_output(self):
        result = AgentResult(provider="test", model="test", raw_output="garbage", parse_ok=False)
        ev = evaluate_result(_make_task(), result)
        assert ev.scores.total == 0.0

    def test_10_dimensions_in_scores(self):
        ev = evaluate_result(_make_task(), _make_result())
        assert hasattr(ev.scores, "support_strength")
        assert hasattr(ev.scores, "mechanism_quality")
        assert hasattr(ev.scores, "self_monitoring_quality")

    def test_scored_dimensions_populated(self):
        ev = evaluate_result(_make_task(), _make_result())
        assert len(ev.scored_dimensions) > 0
        dim_names = {sd.dimension for sd in ev.scored_dimensions}
        assert "support_strength" in dim_names
        assert "mechanism_quality" in dim_names

    def test_forensic_flags_populated(self):
        ev = evaluate_result(_make_task(), _make_result())
        # Should be a list (may be empty for simple correct answers)
        assert isinstance(ev.forensic_flags, list)

    def test_reasoning_graph_attached(self):
        ev = evaluate_result(_make_task(), _make_result())
        assert ev.reasoning_graph is not None
        assert len(ev.reasoning_graph.claims) > 0

    def test_consistency_findings_populated(self):
        task = _make_task(difficulty=Difficulty.HARD)
        result = _make_result(confidence=0.99, uncertainties=[])
        ev = evaluate_result(task, result)
        assert len(ev.consistency_findings) > 0

    def test_rubric_based_evaluation(self):
        task = _make_task(
            task_type=TaskType.RUBRIC_BASED, expected_answer=None,
            rubric=[
                RubricItem(criterion="identifies paradox", points=50,
                           variants=["simpson's paradox"]),
                RubricItem(criterion="per-department analysis", points=50,
                           variants=["each department"]),
            ],
        )
        result = _make_result(
            final_answer="This is Simpson's paradox. Each department shows different rates.",
            steps=["Simpson's paradox: aggregate reverses", "Each department tells a different story"],
        )
        ev = evaluate_result(task, result)
        assert ev.scores.correctness > 0

    def test_no_assumptions_creates_failure(self):
        result = _make_result()
        result.parsed.assumptions = []
        ev = evaluate_result(_make_task(), result)
        assert any(f.category == FailureCategory.NO_ASSUMPTIONS_STATED.value for f in ev.failures)

    def test_support_strength_grounded(self):
        """When steps mention the same content as the answer, support should be decent."""
        result = _make_result(
            final_answer="The answer is 4 because 2+2=4",
            steps=["We compute 2+2 which equals 4", "Therefore the answer is 4"],
            key_claims=["2+2 equals 4"],
        )
        ev = evaluate_result(_make_task(), result)
        assert ev.scores.support_strength > 0.2

    def test_mechanism_quality_names_and_explains(self):
        result = _make_result(
            final_answer="This is Simpson's Paradox.",
            steps=[
                "The aggregate rate reverses because men apply more to the competitive department",
                "This phenomenon is a well-known paradox in statistics",
            ],
        )
        ev = evaluate_result(_make_task(), result)
        assert ev.scores.mechanism_quality > 0.3

    def test_decorative_self_check_penalized(self):
        result = _make_result(self_check=["I checked my work."])
        ev = evaluate_result(_make_task(), result)
        assert ev.scores.self_monitoring_quality < 0.5

    def test_evidence_roles_present(self):
        """Evidence spans should use the new role classification."""
        ev = evaluate_result(_make_task(), _make_result())
        all_evidence = []
        for sd in ev.scored_dimensions:
            all_evidence.extend(sd.evidence)
        # At least some evidence should have non-default roles
        roles = {e.role for e in all_evidence}
        assert len(roles) >= 1  # at minimum SUPPORTING
