"""Tests for Phase 2 provider contract normalization.

Covers the ModelResponse contract, backward-compatible text providers,
finish_reason/usage/latency propagation, normalized errors, the runner
integration, and that the provider registry still returns all providers.

No test here calls a real Anthropic/OpenAI/Ollama API — all providers are fakes.
"""

from __future__ import annotations

import json

from inspektorium.audit.providers import (
    BaseProvider,
    ModelResponse,
    classify_error_type,
    get_provider,
)
from inspektorium.audit.providers.response import DEFAULT_MAX_TOKENS
from inspektorium.audit.runner import run_agent
from inspektorium.audit.schemas import Task, TaskType


def _task() -> Task:
    return Task(
        id="t-1",
        title="T",
        domain="study_forensics",
        difficulty="easy",
        task_type=TaskType.STUDY_FORENSICS,
        prompt="Analyze the claim.",
    )


def _payload() -> str:
    return json.dumps({
        "final_answer": "overclaim",
        "steps": ["s1"],
        "confidence": 0.8,
    })


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------

class FakeTextProvider(BaseProvider):
    """Legacy-style provider: implements only send_prompt (returns text)."""
    name = "fake_text"

    def __init__(self, text: str):
        self._text = text
        self.model = "fake-model-1"
        self.label = "Fake Text"

    def send_prompt(self, task, system_prompt) -> str:
        return self._text


class FakeModelResponseProvider(BaseProvider):
    """Modern provider: overrides generate to return a rich ModelResponse."""
    name = "fake_mr"

    def __init__(self, response: ModelResponse):
        self._response = response
        self.model = "fake-model-2"
        self.label = "Fake MR"

    def generate(self, task, system_prompt) -> ModelResponse:
        return self._response

    def send_prompt(self, task, system_prompt) -> str:
        resp = self.generate(task, system_prompt)
        if resp.error:
            raise RuntimeError(resp.error)
        return resp.text


class FakeRaisingProvider(BaseProvider):
    """Legacy provider whose send_prompt raises (tests default generate)."""
    name = "fake_raise"

    def __init__(self, exc: Exception):
        self._exc = exc
        self.model = "fake-model-3"
        self.label = "Fake Raise"

    def send_prompt(self, task, system_prompt) -> str:
        raise self._exc


# ---------------------------------------------------------------------------
# ModelResponse basics
# ---------------------------------------------------------------------------

class TestModelResponse:
    def test_defaults_and_ok(self):
        r = ModelResponse(text="hi")
        assert r.ok is True
        assert r.finish_reason is None and r.usage is None

    def test_error_not_ok(self):
        r = ModelResponse(text="", error="boom", error_type="provider_error")
        assert r.ok is False

    def test_as_dict_json_serializable(self):
        r = ModelResponse(text="x", provider="p", model="m",
                          finish_reason="stop", usage={"total_tokens": 5},
                          latency_ms=12)
        json.dumps(r.as_dict())

    def test_default_max_tokens_value(self):
        assert DEFAULT_MAX_TOKENS == 4096


# ---------------------------------------------------------------------------
# Backward compatibility: text-only providers still work
# ---------------------------------------------------------------------------

class TestBackwardCompatText:
    def test_default_generate_wraps_send_prompt(self):
        p = FakeTextProvider(_payload())
        resp = p.generate(_task(), "sys")
        assert isinstance(resp, ModelResponse)
        assert resp.ok is True
        assert resp.finish_reason is None      # not fabricated
        assert resp.latency_ms is not None and resp.latency_ms >= 0
        assert resp.provider == "fake_text"

    def test_run_agent_with_text_provider(self):
        result = run_agent(FakeTextProvider(_payload()), _task())
        assert result.parse_ok is True
        assert result.parsed.final_answer == "overclaim"
        assert result.error is None
        assert result.finish_reason is None
        assert result.latency_ms >= 0


# ---------------------------------------------------------------------------
# ModelResponse providers via runner
# ---------------------------------------------------------------------------

class TestRunAgentWithModelResponse:
    def test_metadata_preserved(self):
        mr = ModelResponse(
            text=_payload(), provider="fake_mr", model="fake-model-2",
            finish_reason="stop", usage={"input_tokens": 10, "output_tokens": 20},
            latency_ms=42,
        )
        result = run_agent(FakeModelResponseProvider(mr), _task())
        assert result.parse_ok is True
        assert result.finish_reason == "stop"
        assert result.usage == {"input_tokens": 10, "output_tokens": 20}
        assert result.latency_ms == 42

    def test_finish_reason_length_propagates(self):
        # Valid content but truncation reported by the provider.
        mr = ModelResponse(text=_payload(), finish_reason="length", latency_ms=5)
        result = run_agent(FakeModelResponseProvider(mr), _task())
        assert result.finish_reason == "length"
        assert result.parse_ok is True

    def test_finish_reason_length_reaches_parser_diagnostics(self):
        # Prove propagation into the Phase-1 parser: an unclosed/truncated JSON
        # plus finish_reason="length" is repaired and flagged.
        truncated = '{"final_answer": "overclaim", "steps": ["s1"'
        mr = ModelResponse(text=truncated, finish_reason="length", latency_ms=1)
        result = run_agent(FakeModelResponseProvider(mr), _task())
        assert result.finish_reason == "length"
        assert result.parse_ok is True
        assert result.parsed.steps == ["s1"]

    def test_usage_accepted_when_present(self):
        mr = ModelResponse(text=_payload(), usage={"total_tokens": 100}, latency_ms=1)
        result = run_agent(FakeModelResponseProvider(mr), _task())
        assert result.usage == {"total_tokens": 100}


# ---------------------------------------------------------------------------
# Error normalization
# ---------------------------------------------------------------------------

class TestErrorNormalization:
    def test_model_response_error_surfaced(self):
        mr = ModelResponse(text="", finish_reason="error",
                           error="429 too many requests",
                           error_type="rate_limit_error", latency_ms=3)
        result = run_agent(FakeModelResponseProvider(mr), _task())
        assert result.error is not None
        assert result.error_type == "rate_limit_error"
        assert result.parse_ok is False
        assert result.raw_output == ""        # not masked as success

    def test_default_generate_catches_raising_send_prompt(self):
        p = FakeRaisingProvider(RuntimeError("connection reset"))
        resp = p.generate(_task(), "sys")
        assert resp.ok is False
        assert resp.error_type == "provider_error"
        assert resp.finish_reason == "error"

    def test_run_agent_surfaces_raising_provider(self):
        result = run_agent(FakeRaisingProvider(RuntimeError("boom")), _task())
        assert result.error is not None
        assert result.error_type is not None
        assert result.parse_ok is False

    def test_classify_error_types(self):
        class AuthenticationError(Exception): ...
        class NotFoundError(Exception): ...
        class RateLimitError(Exception): ...
        assert classify_error_type(AuthenticationError("bad key")) == "auth_error"
        assert classify_error_type(NotFoundError("404")) == "not_found_error"
        assert classify_error_type(RateLimitError("slow down")) == "rate_limit_error"
        assert classify_error_type(TimeoutError("timed out")) == "timeout_error"
        assert classify_error_type(ValueError("weird")) == "provider_error"

    def test_classify_by_message_status_codes(self):
        assert classify_error_type(Exception("HTTP 401 Unauthorized")) == "auth_error"
        assert classify_error_type(Exception("got 429")) == "rate_limit_error"


# ---------------------------------------------------------------------------
# Registry still intact
# ---------------------------------------------------------------------------

class TestRegistry:
    def test_all_providers_resolve(self):
        for name in ("anthropic", "openai", "ollama"):
            p = get_provider(name)
            assert isinstance(p, BaseProvider)
            assert p.name == name

    def test_registry_accepts_config_kwargs(self):
        # Latent-break fix: openai/ollama now accept temperature/label like anthropic.
        for name in ("anthropic", "openai", "ollama"):
            p = get_provider(name, model="m", temperature=0.0, label="L")
            assert p.model == "m"
            assert p.label == "L"

    def test_unknown_provider_raises(self):
        try:
            get_provider("does_not_exist")
            assert False, "expected ValueError"
        except ValueError as e:
            assert "Unknown provider" in str(e)

    def test_default_max_tokens_applied(self):
        assert get_provider("anthropic").max_tokens == DEFAULT_MAX_TOKENS
        assert get_provider("openai").max_tokens == DEFAULT_MAX_TOKENS
