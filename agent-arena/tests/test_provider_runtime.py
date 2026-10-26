"""Offline, mock-based tests that the Anthropic provider enforces the frozen Phase 6.2
runtime-contract transport/request values. No network, no model call.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from agent_arena.agent_loader import load_agent_config
from agent_arena.providers import get_provider
from agent_arena.providers.anthropic import (
    MAX_TRANSPORT_RETRIES,
    REQUEST_TIMEOUT_SECONDS,
    AnthropicProvider,
)
from agent_arena.runner import run_agent
from agent_arena.task_loader import load_task

TASK = load_task("tasks/study_forensics/case013_gut_microbes.yaml")
VALID_JSON = '{"final_answer":"mechanism_vs_evidence","confidence":0.8}'
MALFORMED = "this is not the required json"


def _mock_message(text: str) -> MagicMock:
    m = MagicMock()
    block = MagicMock()
    block.text = text
    m.content = [block]
    m.stop_reason = "end_turn"
    usage = MagicMock()
    usage.input_tokens = 100
    usage.output_tokens = 50
    m.usage = usage
    return m


def _generate(model_id: str, text: str = VALID_JSON):
    """Patch the Anthropic SDK, run one generate, return (MockClass, instance, resp)."""
    with patch("anthropic.Anthropic") as MockCls:
        inst = MockCls.return_value

        def create(**_kwargs):
            http_client = MockCls.call_args.kwargs["http_client"]
            http_client.event_hooks["request"][0](MagicMock())
            return _mock_message(text)

        inst.messages.create.side_effect = create
        provider = AnthropicProvider(model=model_id)
        resp = provider.generate(TASK, "SYSTEM")
        return MockCls, inst, resp


# ------------------- client construction (no SDK-default fallback) -------------------

def test_client_receives_timeout_120():
    MockCls, _inst, _ = _generate("claude-sonnet-4-5-20250929")
    kwargs = MockCls.call_args.kwargs
    assert kwargs.get("timeout") == REQUEST_TIMEOUT_SECONDS == 120.0


def test_client_receives_max_retries_2():
    MockCls, _inst, _ = _generate("claude-sonnet-4-5-20250929")
    kwargs = MockCls.call_args.kwargs
    assert kwargs.get("max_retries") == MAX_TRANSPORT_RETRIES == 2


def test_no_hidden_fallback_to_sdk_defaults():
    MockCls, _inst, _ = _generate("claude-opus-4-5-20251101")
    kwargs = MockCls.call_args.kwargs
    assert "timeout" in kwargs and kwargs["timeout"] == 120.0
    assert "max_retries" in kwargs and kwargs["max_retries"] == 2


def test_observed_http_attempts_and_transport_retries_are_reported_exactly():
    with patch("anthropic.Anthropic") as MockCls:
        inst = MockCls.return_value

        def create(**_kwargs):
            http_client = MockCls.call_args.kwargs["http_client"]
            for _ in range(3):
                http_client.event_hooks["request"][0](MagicMock())
            return _mock_message(VALID_JSON)

        inst.messages.create.side_effect = create
        response = AnthropicProvider(model="claude-haiku-4-5-20251001").generate(
            TASK, "SYSTEM"
        )
        assert response.usage["http_attempts"] == 3
        assert response.usage["transport_retries"] == 2


# ------------------- request parameters -------------------

def test_request_omits_top_p_and_seed():
    _MockCls, inst, _ = _generate("claude-haiku-4-5-20251001")
    create_kwargs = inst.messages.create.call_args.kwargs
    assert "top_p" not in create_kwargs
    assert "seed" not in create_kwargs


def test_request_temperature_and_max_tokens():
    _MockCls, inst, _ = _generate("claude-haiku-4-5-20251001")
    create_kwargs = inst.messages.create.call_args.kwargs
    assert create_kwargs["temperature"] == 0.0
    assert create_kwargs["max_tokens"] == 4096


def test_exact_dated_model_from_config_is_sent():
    cfg = load_agent_config("agents/claude_opus.yaml")
    assert cfg.model == "claude-opus-4-5-20251101"  # config is pinned to the dated snapshot
    with patch("anthropic.Anthropic") as MockCls:
        inst = MockCls.return_value
        inst.messages.create.return_value = _mock_message(VALID_JSON)
        provider = get_provider("anthropic", model=cfg.model, temperature=cfg.temperature, label=cfg.label)
        provider.generate(TASK, "SYSTEM")
        assert inst.messages.create.call_args.kwargs["model"] == "claude-opus-4-5-20251101"


# ------------------- no semantic/quality retries -------------------

def test_parser_failure_does_not_trigger_another_request():
    with patch("anthropic.Anthropic") as MockCls:
        inst = MockCls.return_value
        inst.messages.create.return_value = _mock_message(MALFORMED)
        provider = AnthropicProvider(model="claude-haiku-4-5-20251001")
        result = run_agent(provider, TASK)
        assert inst.messages.create.call_count == 1     # no re-request on parse failure
        assert result.parse_ok is False


def test_malformed_semantic_response_not_retried():
    _MockCls, inst, _resp = _generate("claude-sonnet-4-5-20250929", text=MALFORMED)
    assert inst.messages.create.call_count == 1


def test_exhausted_transport_failure_is_an_explicit_failed_record():
    with patch("anthropic.Anthropic") as MockCls:
        inst = MockCls.return_value
        inst.messages.create.side_effect = RuntimeError("boom")
        provider = AnthropicProvider(model="claude-haiku-4-5-20251001")
        resp = provider.generate(TASK, "SYSTEM")
        assert inst.messages.create.call_count == 1     # no application-layer retry
        assert resp.error and resp.finish_reason == "error"
        assert resp.usage["http_attempts"] == 0
        assert resp.usage["transport_retries"] == 0
