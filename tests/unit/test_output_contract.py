"""Tests for the Phase 1 output-contract hardening (output_contract.py).

Proves robust structured-output handling and graceful parse-failure behavior:
markdown-fenced JSON, unclosed fences, text before/after JSON, malformed JSON,
truncated JSON, finish_reason="length", missing fields, schema validation,
parse metadata, and backward-compatible delegation from runner.parse_agent_output.
"""

from __future__ import annotations

import json

import pytest

from inspektorium.audit.confidence_validity import INVALID, MISSING, VALID
from inspektorium.audit.output_contract import (
    ParseDiagnostics,
    parse_structured_output,
)
from inspektorium.audit.runner import parse_agent_output


def _full_payload() -> dict:
    return {
        "final_answer": "overclaim",
        "assumptions": ["a1"],
        "steps": ["s1", "s2"],
        "alternative_hypotheses": ["h1"],
        "uncertainties": ["u1"],
        "self_check": ["c1"],
        "key_claims": ["k1"],
        "confidence": 0.85,
    }


# ---------------------------------------------------------------------------
# Happy paths — behavior preserved for valid output
# ---------------------------------------------------------------------------

class TestValidOutput:
    def test_clean_json_object(self):
        resp, diag = parse_structured_output(json.dumps(_full_payload()))
        assert diag.ok is True
        assert resp is not None
        assert resp.final_answer == "overclaim"
        assert resp.steps == ["s1", "s2"]
        assert resp.confidence == 0.85
        assert diag.strategy == "raw"
        assert diag.truncation_suspected is False

    def test_markdown_json_fence_closed(self):
        raw = "```json\n" + json.dumps(_full_payload()) + "\n```"
        resp, diag = parse_structured_output(raw)
        assert diag.ok is True
        assert diag.had_fence is True
        assert diag.fence_closed is True
        assert diag.strategy == "fenced_json"
        assert resp.final_answer == "overclaim"

    def test_generic_fence(self):
        raw = "```\n" + json.dumps(_full_payload()) + "\n```"
        resp, diag = parse_structured_output(raw)
        assert diag.ok is True
        assert diag.had_fence is True
        assert resp.confidence == 0.85

    def test_text_before_and_after_json(self):
        raw = (
            "Here is my analysis:\n"
            + json.dumps(_full_payload())
            + "\n\nLet me know if you need more."
        )
        resp, diag = parse_structured_output(raw)
        assert diag.ok is True
        assert diag.strategy == "brace_scan"
        assert resp.final_answer == "overclaim"

    def test_prose_before_json_fence(self):
        raw = "Sure! Here you go:\n```json\n" + json.dumps(_full_payload()) + "\n```"
        resp, diag = parse_structured_output(raw)
        assert diag.ok is True
        assert resp.final_answer == "overclaim"

    def test_brace_inside_string_value_not_miscut(self):
        payload = _full_payload()
        payload["final_answer"] = "the set {a, b} implies }weird{ text"
        raw = json.dumps(payload)
        resp, diag = parse_structured_output(raw)
        assert diag.ok is True
        assert resp.final_answer == "the set {a, b} implies }weird{ text"


# ---------------------------------------------------------------------------
# The original crash case: opening fence with no closing fence
# ---------------------------------------------------------------------------

class TestUnclosedFence:
    def test_unclosed_json_fence_does_not_raise_and_parses(self):
        # Reproduces the live failure: ```json opened, never closed.
        raw = "```json\n" + json.dumps(_full_payload())
        resp, diag = parse_structured_output(raw)
        assert diag.ok is True
        assert diag.had_fence is True
        assert diag.fence_closed is False
        assert diag.truncation_suspected is True
        assert resp.final_answer == "overclaim"

    def test_unclosed_fence_via_legacy_wrapper_no_raise(self):
        raw = "```json\n" + json.dumps(_full_payload())
        # Must not raise ValueError("substring not found") like the old code.
        resp, ok = parse_agent_output(raw)
        assert ok is True
        assert resp is not None


# ---------------------------------------------------------------------------
# Malformed / empty / non-JSON
# ---------------------------------------------------------------------------

class TestMalformed:
    def test_pure_garbage(self):
        resp, diag = parse_structured_output("this is not json at all")
        assert diag.ok is False
        assert resp is None
        assert diag.error is not None

    def test_empty_string(self):
        resp, diag = parse_structured_output("")
        assert diag.ok is False
        assert resp is None

    def test_whitespace_only(self):
        resp, diag = parse_structured_output("   \n\t  ")
        assert resp is None and diag.ok is False

    def test_non_string_input(self):
        resp, diag = parse_structured_output(None)  # type: ignore[arg-type]
        assert resp is None and diag.ok is False

    def test_broken_mid_key_degrades_gracefully(self):
        # Truncated in the middle of a key/value with no recoverable structure.
        raw = '{"final_answer": "overclaim", "confid'
        resp, diag = parse_structured_output(raw)
        # Either None (graceful failure) — must never raise.
        assert diag.ok in (True, False)
        if not diag.ok:
            assert resp is None


# ---------------------------------------------------------------------------
# Truncated JSON — best-effort repair
# ---------------------------------------------------------------------------

class TestTruncation:
    def test_truncated_list_repaired(self):
        # Cut off in the middle of a list; outer object never closed.
        raw = '{"final_answer": "overclaim", "steps": ["s1", "s2"'
        resp, diag = parse_structured_output(raw)
        assert diag.ok is True
        assert diag.repaired is True
        assert diag.truncation_suspected is True
        assert resp.final_answer == "overclaim"
        assert resp.steps == ["s1", "s2"]

    def test_truncated_with_trailing_comma_repaired(self):
        raw = '{"final_answer": "overclaim", "steps": ["s1", "s2"],'
        resp, diag = parse_structured_output(raw)
        assert diag.ok is True
        assert resp.final_answer == "overclaim"

    def test_truncated_inside_string_repaired_or_graceful(self):
        raw = '{"final_answer": "overcl'
        resp, diag = parse_structured_output(raw)
        # Must not raise; repair may or may not recover this.
        assert diag.ok in (True, False)

    def test_truncated_fenced_json_repaired(self):
        raw = '```json\n{"final_answer": "overclaim", "steps": ["s1"'
        resp, diag = parse_structured_output(raw)
        assert diag.ok is True
        assert diag.had_fence is True
        assert diag.fence_closed is False
        assert resp.steps == ["s1"]


# ---------------------------------------------------------------------------
# finish_reason handling
# ---------------------------------------------------------------------------

class TestFinishReason:
    def test_length_hint_marks_truncation_suspected(self):
        resp, diag = parse_structured_output(
            json.dumps(_full_payload()), finish_reason="length"
        )
        assert diag.finish_reason == "length"
        assert diag.truncation_suspected is True
        assert diag.ok is True  # still parses the valid content

    def test_stop_hint_no_truncation_flag(self):
        resp, diag = parse_structured_output(
            json.dumps(_full_payload()), finish_reason="stop"
        )
        assert diag.truncation_suspected is False
        assert diag.ok is True


# ---------------------------------------------------------------------------
# Missing fields / schema validation / defensive coercion
# ---------------------------------------------------------------------------

class TestMissingFields:
    def test_missing_fields_default_and_recorded(self):
        raw = json.dumps({"final_answer": "solid"})
        resp, diag = parse_structured_output(raw)
        assert diag.ok is True
        assert resp.final_answer == "solid"
        assert resp.steps == []
        assert resp.confidence is None
        assert resp.confidence_state == MISSING
        assert diag.confidence_state == MISSING
        assert "steps" in diag.missing_fields
        assert "confidence" in diag.missing_fields
        assert "final_answer" not in diag.missing_fields

    @pytest.mark.parametrize(("raw_confidence", "state", "value"), [
        (None, MISSING, None),
        ("", MISSING, None),
        ("high", INVALID, None),
        ("0.85", INVALID, None),
        (True, INVALID, None),
        (False, INVALID, None),
        ([], INVALID, None),
        ({}, INVALID, None),
        (float("nan"), INVALID, None),
        (float("inf"), INVALID, None),
        (float("-inf"), INVALID, None),
        (-0.1, INVALID, None),
        (1.1, INVALID, None),
        (0.0, VALID, 0.0),
        (0.85, VALID, 0.85),
        (1, VALID, 1.0),
    ])
    def test_confidence_raw_type_is_preserved_as_validity(self, raw_confidence, state, value):
        raw = json.dumps({"final_answer": "solid", "confidence": raw_confidence})
        resp, diag = parse_structured_output(raw)
        assert diag.ok is True
        assert resp is not None
        assert diag.confidence_state == state
        assert resp.confidence_state == state
        assert resp.confidence == value

    def test_wrong_typed_list_field_degrades_to_empty(self):
        raw = json.dumps({"final_answer": "x", "steps": "not a list"})
        resp, diag = parse_structured_output(raw)
        assert diag.ok is True
        assert resp.steps == []

    def test_unexpected_fields_recorded(self):
        payload = _full_payload()
        payload["some_hallucinated_key"] = "value"
        resp, diag = parse_structured_output(json.dumps(payload))
        assert diag.ok is True
        assert "some_hallucinated_key" in diag.unexpected_fields

    def test_json_array_not_object_fails_gracefully(self):
        resp, diag = parse_structured_output('["a", "b"]')
        assert resp is None and diag.ok is False


# ---------------------------------------------------------------------------
# Parse metadata shape
# ---------------------------------------------------------------------------

class TestDiagnostics:
    def test_diagnostics_as_dict_serializable(self):
        _, diag = parse_structured_output(json.dumps(_full_payload()))
        d = diag.as_dict()
        assert isinstance(d, dict)
        assert d["ok"] is True
        assert d["strategy"] == "raw"
        assert d["raw_length"] > 0
        # Must be JSON-serializable (usable as parse metadata downstream).
        json.dumps(d)

    def test_default_diagnostics(self):
        d = ParseDiagnostics()
        assert d.ok is False
        assert d.strategy == "none"


# ---------------------------------------------------------------------------
# Backward compatibility of the legacy wrapper
# ---------------------------------------------------------------------------

class TestLegacyWrapper:
    def test_valid_returns_two_tuple(self):
        result = parse_agent_output(json.dumps(_full_payload()))
        assert isinstance(result, tuple) and len(result) == 2
        resp, ok = result
        assert ok is True and resp.final_answer == "overclaim"

    def test_invalid_returns_none_false(self):
        resp, ok = parse_agent_output("not json")
        assert resp is None and ok is False

    def test_missing_fields_still_ok(self):
        resp, ok = parse_agent_output(json.dumps({"final_answer": "solid"}))
        assert ok is True and resp.final_answer == "solid"
