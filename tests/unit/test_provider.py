"""Tests for the single optional provider without live API calls."""

from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any

import pytest

from inspektorium.core.models import InspectionInput, ProposalBatch
from inspektorium.providers.anthropic import AnthropicProvider, build_user_prompt
from inspektorium.providers.base import ProviderError


class FakeMessages:
    def __init__(self, response: Any = None, error: Exception | None = None) -> None:
        self.response = response
        self.error = error
        self.kwargs: dict[str, Any] | None = None

    def parse(self, **kwargs: Any) -> Any:
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


def test_anthropic_provider_uses_sdk_pydantic_parse_helper(
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    raw = json.dumps({"schema_version": "0.1", "findings": [supported_proposal_data]})
    parsed = ProposalBatch.model_validate_json(raw)
    messages = FakeMessages(
        SimpleNamespace(
            content=[SimpleNamespace(type="text", parsed_output=parsed)]
        )
    )
    provider = AnthropicProvider(model="test-model", client=_client(messages))

    batch = provider.propose_findings(inspection_input)

    assert batch.findings[0].claim_id == "claim-1"
    assert messages.kwargs is not None
    assert messages.kwargs["model"] == "test-model"
    assert len(messages.kwargs["messages"]) == 1
    assert messages.kwargs["output_format"] is ProposalBatch
    assert "output_config" not in messages.kwargs


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
    parsed = ProposalBatch(findings=())
    response = SimpleNamespace(
        content=[
            SimpleNamespace(type="text", parsed_output=parsed),
            SimpleNamespace(type="text", parsed_output=parsed),
        ]
    )
    provider = AnthropicProvider(
        model="test-model",
        client=_client(FakeMessages(response)),
    )

    with pytest.raises(ProviderError, match="exactly one parsed output"):
        provider.propose_findings(inspection_input)


def _sdk_message(text: str) -> dict[str, Any]:
    return {
        "id": "msg_synthetic",
        "type": "message",
        "role": "assistant",
        "model": "test-model",
        "content": [{"type": "text", "text": text}],
        "stop_reason": "end_turn",
        "stop_sequence": None,
        "usage": {"input_tokens": 1, "output_tokens": 1},
    }


def _schema_keywords(value: Any) -> set[str]:
    if isinstance(value, dict):
        return set(value) | {
            keyword
            for child in value.values()
            for keyword in _schema_keywords(child)
        }
    if isinstance(value, list):
        return {
            keyword for child in value for keyword in _schema_keywords(child)
        }
    return set()


def _all_objects_are_closed(value: Any) -> bool:
    if isinstance(value, dict):
        is_open_object = (
            value.get("type") == "object"
            and value.get("additionalProperties") is not False
        )
        if is_open_object:
            return False
        return all(_all_objects_are_closed(child) for child in value.values())
    if isinstance(value, list):
        return all(_all_objects_are_closed(child) for child in value)
    return True


def test_anthropic_transport_uses_sdk_schema_transformation(
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    import anthropic
    import httpx

    captured: dict[str, Any] = {}
    raw = json.dumps({"schema_version": "0.1", "findings": [supported_proposal_data]})

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(request.content)
        captured["headers"] = dict(request.headers)
        return httpx.Response(
            200,
            headers={"request-id": "req_synthetic"},
            json=_sdk_message(raw),
        )

    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    client = anthropic.Anthropic(api_key="synthetic-test-key", http_client=http_client)
    provider = AnthropicProvider(model="test-model", client=client)

    batch = provider.propose_findings(inspection_input)

    assert batch.findings[0].claim_id == "claim-1"
    body = captured["body"]
    assert body["max_tokens"] == 4096
    assert body["model"] == "test-model"
    assert body["temperature"] == 0
    assert [message["role"] for message in body["messages"]] == ["user"]
    assert "tools" not in body
    assert "thinking" not in body
    assert "citations" not in body
    assert "output_format" not in body
    assert "anthropic-beta" not in captured["headers"]

    output_format = body["output_config"]["format"]
    assert output_format["type"] == "json_schema"
    transformed_schema = output_format["schema"]
    assert _all_objects_are_closed(transformed_schema)
    assert not (
        _schema_keywords(transformed_schema)
        & {"minimum", "maximum", "multipleOf", "minLength", "maxLength"}
    )


def test_malformed_sdk_parsed_output_fails_without_fallback(
    inspection_input: InspectionInput,
) -> None:
    import anthropic
    import httpx

    requests = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal requests
        requests += 1
        return httpx.Response(
            200,
            headers={"request-id": "req_synthetic"},
            json=_sdk_message('{"schema_version":"0.1","findings":[{}]}'),
        )

    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    client = anthropic.Anthropic(api_key="synthetic-test-key", http_client=http_client)
    provider = AnthropicProvider(model="test-model", client=client)

    with pytest.raises(ProviderError, match="ValidationError"):
        provider.propose_findings(inspection_input)

    assert requests == 1


def test_anthropic_http_error_reports_only_sanitized_fields(
    inspection_input: InspectionInput,
) -> None:
    import anthropic
    import httpx

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            400,
            headers={"request-id": "req_synthetic"},
            json={
                "type": "error",
                "error": {
                    "type": "invalid_request_error",
                    "message": (
                        "Unsupported schema for "
                        f"{inspection_input.answer.text}; Authorization: placeholder"
                    ),
                },
            },
        )

    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    client = anthropic.Anthropic(api_key="synthetic-test-key", http_client=http_client)
    provider = AnthropicProvider(model="test-model", client=client)

    with pytest.raises(ProviderError) as error:
        provider.propose_findings(inspection_input)

    message = str(error.value)
    assert "HTTP 400" in message
    assert "invalid_request_error" in message
    assert "Unsupported schema" in message
    assert "[redacted inspection text]" in message
    assert "Authorization=[redacted credential]" in message
    assert inspection_input.answer.text not in message
    assert "placeholder" not in message


def test_model_identifier_is_required() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        AnthropicProvider(model="", client=object())
