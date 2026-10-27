"""Anthropic provider."""

from __future__ import annotations

import time

from inspektorium.audit.providers import BaseProvider
from inspektorium.audit.providers.response import (
    DEFAULT_MAX_TOKENS,
    ModelResponse,
    classify_error_type,
)
from inspektorium.audit.schemas import Task

# Frozen Phase 6.2 runtime-contract transport values. These are enforced explicitly on
# the Anthropic client (not left to SDK defaults) so the runtime contracts and the real
# provider agree. Transport retries only — never semantic/quality-based reruns.
REQUEST_TIMEOUT_SECONDS = 120.0
MAX_TRANSPORT_RETRIES = 2

# Anthropic stop_reason -> normalized finish_reason
_STOP_REASON_MAP = {
    "end_turn": "stop",
    "stop_sequence": "stop",
    "max_tokens": "length",
    "tool_use": "stop",
}


class AnthropicProvider(BaseProvider):
    name = "anthropic"

    def __init__(self, model: str = "claude-sonnet-4-20250514", temperature: float = 0.0,
                 label: str = "", max_tokens: int = DEFAULT_MAX_TOKENS):
        self.model = model
        self.temperature = temperature
        self.label = label or model
        self.max_tokens = max_tokens

    def generate(self, task: Task, system_prompt: str) -> ModelResponse:
        try:
            import anthropic
        except ImportError:
            raise RuntimeError("Install anthropic: pip install 'inspektorium[providers]'")

        import httpx

        start = time.monotonic()
        http_attempts = 0

        def count_http_attempt(_request) -> None:
            nonlocal http_attempts
            http_attempts += 1

        http_client = httpx.Client(event_hooks={"request": [count_http_attempt]})
        try:
            client = anthropic.Anthropic(
                timeout=REQUEST_TIMEOUT_SECONDS,
                max_retries=MAX_TRANSPORT_RETRIES,
                http_client=http_client,
            )
            try:
                message = client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=system_prompt,
                    messages=[{"role": "user", "content": task.prompt}],
                )
            finally:
                http_client.close()
            latency = int((time.monotonic() - start) * 1000)

            text = message.content[0].text if message.content else ""
            finish_reason = _STOP_REASON_MAP.get(
                getattr(message, "stop_reason", None), "unknown"
            )
            usage = None
            u = getattr(message, "usage", None)
            if u is not None:
                usage = {
                    "input_tokens": getattr(u, "input_tokens", None),
                    "output_tokens": getattr(u, "output_tokens", None),
                    "http_attempts": http_attempts,
                    "transport_retries": max(http_attempts - 1, 0),
                }
            return ModelResponse(
                text=text,
                provider=self.name,
                model=self.model,
                finish_reason=finish_reason,
                usage=usage,
                latency_ms=latency,
            )
        except Exception as e:
            if not http_client.is_closed:
                http_client.close()
            latency = int((time.monotonic() - start) * 1000)
            return ModelResponse(
                text="",
                provider=self.name,
                model=self.model,
                finish_reason="error",
                usage={
                    "http_attempts": http_attempts,
                    "transport_retries": max(http_attempts - 1, 0),
                },
                latency_ms=latency,
                error=str(e),
                error_type=classify_error_type(e),
            )

    def send_prompt(self, task: Task, system_prompt: str) -> str:
        resp = self.generate(task, system_prompt)
        if resp.error:
            raise RuntimeError(resp.error)
        return resp.text
