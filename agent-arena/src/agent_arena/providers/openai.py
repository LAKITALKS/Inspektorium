"""OpenAI provider."""

from __future__ import annotations

import time

from agent_arena.providers import BaseProvider
from agent_arena.providers.response import (
    DEFAULT_MAX_TOKENS,
    ModelResponse,
    classify_error_type,
)
from agent_arena.schemas import Task

# OpenAI finish_reason -> normalized finish_reason
_FINISH_REASON_MAP = {
    "stop": "stop",
    "length": "length",
    "content_filter": "error",
    "tool_calls": "stop",
    "function_call": "stop",
}


class OpenAIProvider(BaseProvider):
    name = "openai"

    def __init__(self, model: str = "gpt-4o", temperature: float = 0.0,
                 label: str = "", max_tokens: int = DEFAULT_MAX_TOKENS):
        self.model = model
        self.temperature = temperature
        self.label = label or model
        self.max_tokens = max_tokens

    def generate(self, task: Task, system_prompt: str) -> ModelResponse:
        try:
            from openai import OpenAI
        except ImportError:
            raise RuntimeError("Install openai: pip install 'agent-arena[providers]'")

        start = time.monotonic()
        try:
            client = OpenAI()
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": task.prompt},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            latency = int((time.monotonic() - start) * 1000)

            choice = response.choices[0] if response.choices else None
            text = (choice.message.content or "") if choice else ""
            raw_fr = getattr(choice, "finish_reason", None) if choice else None
            finish_reason = _FINISH_REASON_MAP.get(raw_fr, "unknown") if raw_fr else None

            usage = None
            u = getattr(response, "usage", None)
            if u is not None:
                usage = {
                    "prompt_tokens": getattr(u, "prompt_tokens", None),
                    "completion_tokens": getattr(u, "completion_tokens", None),
                    "total_tokens": getattr(u, "total_tokens", None),
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
            latency = int((time.monotonic() - start) * 1000)
            return ModelResponse(
                text="",
                provider=self.name,
                model=self.model,
                finish_reason="error",
                latency_ms=latency,
                error=str(e),
                error_type=classify_error_type(e),
            )

    def send_prompt(self, task: Task, system_prompt: str) -> str:
        resp = self.generate(task, system_prompt)
        if resp.error:
            raise RuntimeError(resp.error)
        return resp.text
