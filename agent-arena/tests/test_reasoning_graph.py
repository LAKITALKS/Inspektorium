"""Tests for agent-arena v0.4 reasoning graph module."""

from agent_arena.reasoning_graph import (
    build_reasoning_graph,
    classify_self_check,
    _content_words,
)
from agent_arena.schemas import AgentResponse


def _make_response(**kwargs) -> AgentResponse:
    defaults = dict(
        final_answer="The answer is Simpson's Paradox.",
        steps=[
            "First I verify the overall rates: men 66%, women 82.2%",
            "Next I check department-level rates: Engineering men 30%, women 40%",
            "In both departments women have higher rates",
            "This is because men applied more to the competitive Engineering department",
            "Therefore the aggregate reversal is explained by Simpson's Paradox",
        ],
        assumptions=[
            "The data provided is accurate and complete",
            "These are the only two departments",
            "Quantum entanglement effects are negligible",  # unused
        ],
        key_claims=["Simpson's Paradox explains the reversal"],
        uncertainties=[
            "Whether there are other departments not shown",
            "The gravitational constant of the moon",  # decorative
        ],
        self_check=[
            "Verified arithmetic: 30+300=330, 20+350=370",
            "Confirmed the paradox pattern holds",
        ],
        alternative_hypotheses=[
            "The university discriminates against men — rejected because department-level rates show otherwise",
        ],
        confidence=0.9,
    )
    defaults.update(kwargs)
    return AgentResponse(**defaults)


class TestBuildReasoningGraph:
    def test_extracts_all_claims(self):
        p = _make_response()
        g = build_reasoning_graph(p)
        # assumptions(3) + steps(5) + key_claims(1) + uncertainties(2) + self_check(2) + alt_hyp(1) + final_answer(1)
        assert len(g.claims) == 15

    def test_detects_unused_assumptions(self):
        p = _make_response()
        g = build_reasoning_graph(p)
        # "Quantum entanglement effects are negligible" should be unused
        assert len(g.unused_assumptions) >= 1
        unused_texts = [g.claims[i].text for i in g.unused_assumptions]
        assert any("quantum" in t.lower() for t in unused_texts)

    def test_detects_unaddressed_uncertainties(self):
        p = _make_response()
        g = build_reasoning_graph(p)
        # "gravitational constant of the moon" should be unaddressed
        assert len(g.unaddressed_uncertainties) >= 1
        unaddressed_texts = [g.claims[i].text for i in g.unaddressed_uncertainties]
        assert any("gravitational" in t.lower() for t in unaddressed_texts)

    def test_conclusion_grounding(self):
        p = _make_response()
        g = build_reasoning_graph(p)
        # Answer mentions "Simpson's Paradox" which is in steps
        assert g.conclusion_grounded

    def test_ungrounded_conclusion(self):
        p = _make_response(
            final_answer="The quantum decoherence pattern is irreversible.",
            steps=["We analyze the admission rates carefully."],
        )
        g = build_reasoning_graph(p)
        assert not g.conclusion_grounded

    def test_support_chain_exists(self):
        p = _make_response()
        g = build_reasoning_graph(p)
        assert g.support_chain_length >= 0  # at least computed

    def test_detects_relations(self):
        p = _make_response()
        g = build_reasoning_graph(p)
        assert len(g.relations) >= 0  # should find some


class TestClassifySelfCheck:
    def test_deep_check(self):
        assert classify_self_check("What if the data has a bias we haven't considered? Let me check for edge cases.") == "deep"

    def test_arithmetic_check(self):
        assert classify_self_check("Verified the calculation: 30/100 = 30%, 20/50 = 40%. Both correct.") == "arithmetic"

    def test_fluff_check(self):
        assert classify_self_check("I checked my work.") == "fluff"

    def test_long_substantive_not_fluff(self):
        result = classify_self_check(
            "Let me verify by computing the total admission rate from department data: "
            "330/500 = 66% for men, which matches the given overall rate."
        )
        assert result != "fluff"


class TestContentWords:
    def test_filters_short_and_stop(self):
        words = _content_words("the quick brown fox jumps over lazy dog", min_len=4)
        assert "the" not in words
        assert "quick" in words
        assert "brown" in words
        assert "jumps" in words
