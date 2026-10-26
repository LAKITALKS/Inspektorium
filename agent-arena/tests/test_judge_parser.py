"""Tests for Phase 2.5 judge parser harmonization.

The judge output parser (_parse_judge_output) previously used raw str.index
on markdown fences, raising ValueError on an unclosed ```json fence. It now
delegates to the shared, hardened output_contract.extract_json_object. These
tests prove robust extraction and preserved judge return shape/behavior.

No live API calls — _parse_judge_output is tested directly on strings.
"""

from __future__ import annotations

import json

from agent_arena.judge import _parse_judge_output
from agent_arena.schemas import JudgeResult


def _judge_payload() -> dict:
    return {
        "dimension_scores": {"correctness": 0.9, "insight_depth": 0.7},
        "evidence_citations": ["cite-1", "cite-2"],
        "failure_modes": ["missed_overclaim"],
        "claim_audit": [
            {"claim": "c1", "status": "supported", "evidence": "e1", "confidence": 0.8},
        ],
        "comparative_note": "solid analysis",
        "judge_confidence": 0.75,
    }


def _assert_full_mapping(result: JudgeResult):
    assert result.enabled is True
    assert result.dimension_scores == {"correctness": 0.9, "insight_depth": 0.7}
    assert result.evidence_citations == ["cite-1", "cite-2"]
    assert result.failure_modes == ["missed_overclaim"]
    assert len(result.claim_audit) == 1
    ca = result.claim_audit[0]
    assert ca.claim == "c1" and ca.status == "supported"
    assert ca.evidence == "e1" and ca.confidence == 0.8
    assert result.comparative_note == "solid analysis"
    assert result.judge_confidence == 0.75


# ---------------------------------------------------------------------------
# Valid outputs — behavior/shape preserved
# ---------------------------------------------------------------------------

class TestValidJudgeOutput:
    def test_plain_json(self):
        result = _parse_judge_output(json.dumps(_judge_payload()))
        _assert_full_mapping(result)

    def test_fenced_json(self):
        raw = "```json\n" + json.dumps(_judge_payload()) + "\n```"
        _assert_full_mapping(_parse_judge_output(raw))

    def test_generic_fence(self):
        raw = "```\n" + json.dumps(_judge_payload()) + "\n```"
        _assert_full_mapping(_parse_judge_output(raw))

    def test_text_before_and_after_json(self):
        raw = "Here is the judgment:\n" + json.dumps(_judge_payload()) + "\nDone."
        _assert_full_mapping(_parse_judge_output(raw))

    def test_raw_output_preserved(self):
        raw = json.dumps(_judge_payload())
        result = _parse_judge_output(raw)
        assert result.raw_output == raw


# ---------------------------------------------------------------------------
# The original crash case + graceful failure
# ---------------------------------------------------------------------------

class TestRobustness:
    def test_unclosed_json_fence_does_not_raise(self):
        # Previously raised ValueError("substring not found").
        raw = "```json\n" + json.dumps(_judge_payload())
        result = _parse_judge_output(raw)  # must not raise
        _assert_full_mapping(result)

    def test_malformed_json_graceful_fallback(self):
        result = _parse_judge_output("this is not json")
        assert result.enabled is True
        assert result.comparative_note == "Judge output not parseable"
        assert result.raw_output == "this is not json"
        assert result.claim_audit == []

    def test_empty_output_graceful(self):
        result = _parse_judge_output("")
        assert result.enabled is True
        assert result.comparative_note == "Judge output not parseable"

    def test_truncated_judge_json_graceful(self):
        # Cut off mid-list; must not raise. Repaired or graceful-fail, both fine.
        raw = '{"dimension_scores": {"correctness": 0.9}, "failure_modes": ["a"'
        result = _parse_judge_output(raw)
        assert isinstance(result, JudgeResult)
        assert result.enabled is True

    def test_partial_fields_use_defaults(self):
        raw = json.dumps({"comparative_note": "only a note"})
        result = _parse_judge_output(raw)
        assert result.comparative_note == "only a note"
        assert result.dimension_scores == {}
        assert result.claim_audit == []
        assert result.judge_confidence == 0.0
