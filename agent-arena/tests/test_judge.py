"""Tests for agent-arena v0.4 judge module."""

from agent_arena.judge import _parse_judge_output, _build_judge_prompt
from agent_arena.schemas import AgentResponse, Difficulty, Task, TaskType


def _make_task() -> Task:
    return Task(
        id="test-001", title="Test", domain="test",
        difficulty=Difficulty.MEDIUM, task_type=TaskType.CLOSED_WITH_REASONING,
        prompt="test prompt", expected_answer="42",
        reference_solution="The answer is 42.",
    )


def _make_response() -> AgentResponse:
    return AgentResponse(
        final_answer="42", steps=["compute"],
        key_claims=["answer is 42"], confidence=0.9,
    )


class TestJudgePrompt:
    def test_prompt_includes_task(self):
        prompt = _build_judge_prompt(_make_task(), _make_response())
        assert "test prompt" in prompt

    def test_prompt_includes_key_claims(self):
        prompt = _build_judge_prompt(_make_task(), _make_response())
        assert "answer is 42" in prompt


class TestJudgeOutputParsing:
    def test_parses_valid_json(self):
        raw = '''{
            "dimension_scores": {"correctness": 0.9},
            "evidence_citations": ["answer is correct"],
            "failure_modes": [],
            "claim_audit": [{"claim": "answer is 42", "status": "supported", "evidence": "matches", "confidence": 0.95}],
            "comparative_note": "Good response",
            "judge_confidence": 0.85
        }'''
        result = _parse_judge_output(raw)
        assert result.enabled
        assert result.dimension_scores["correctness"] == 0.9

    def test_handles_garbage(self):
        result = _parse_judge_output("not json")
        assert result.enabled
        assert "not parseable" in result.comparative_note
