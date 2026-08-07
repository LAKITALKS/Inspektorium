"""Tests for the single optional provider without live API calls."""

from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any

import pytest

from inspektorium.core.models import InspectionInput
from inspektorium.providers.anthropic import AnthropicProvider, build_user_prompt
from inspektorium.providers.base import ProviderError


class FakeMessages:
    def __init__(self, response: Any = None, error: Exception | None = None) -> None:
        self.response = response
        self.error = error
        self.kwargs: dict[str, Any] | None = None

    def create(self, **kwargs: Any) -> Any:
        self.kwargs = kwargs
        if self.error is not None:
            raise self.error
        return self.response


def _client(messages: FakeMessages) -> Any:
    return SimpleNamespace(messages=messages)


def test_prompt_contains_only_explicit_input_and_public_schema(
    inspection_input: InspectionInput,
) -> None:
    prompt = build_user_prompt(inspection_input)

    assert inspection_input.answer.text in prompt
    assert "proposed_relation" in prompt
    assert "verified_relation" not in prompt
    assert "chain-of-thought" not in prompt.lower()


def test_anthropic_provider_parses_one_text_response(
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    raw = json.dumps({"schema_version": "0.1", "findings": [supported_proposal_data]})
    messages = FakeMessages(
        SimpleNamespace(content=[SimpleNamespace(type="text", text=raw)])
    )
    provider = AnthropicProvider(model="test-model", client=_client(messages))

    batch = provider.propose_findings(inspection_input)

    assert batch.findings[0].claim_id == "claim-1"
    assert messages.kwargs is not None
    assert messages.kwargs["model"] == "test-model"
    assert len(messages.kwargs["messages"]) == 1


def test_provider_request_failure_cannot_become_fake_success(
    inspection_input: InspectionInput,
) -> None:
    provider = AnthropicProvider(
        model="test-model",
        client=_client(FakeMessages(error=RuntimeError("network unavailable"))),
    )

    with pytest.raises(ProviderError, match="RuntimeError"):
        provider.propose_findings(inspection_input)


def test_multiple_text_blocks_fail_safely(inspection_input: InspectionInput) -> None:
    response = SimpleNamespace(
        content=[
            SimpleNamespace(type="text", text="{}"),
            SimpleNamespace(type="text", text="{}"),
        ]
    )
    provider = AnthropicProvider(
        model="test-model",
        client=_client(FakeMessages(response)),
    )

    with pytest.raises(ProviderError, match="exactly one text block"):
        provider.propose_findings(inspection_input)


def test_model_identifier_is_required() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        AnthropicProvider(model="", client=object())
