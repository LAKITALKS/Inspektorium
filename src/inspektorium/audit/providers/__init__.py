"""Provider abstraction for the Inspektorium audit runtime."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod

from inspektorium.audit.providers.response import (
    DEFAULT_MAX_TOKENS,
    ModelResponse,
    classify_error_type,
)
from inspektorium.audit.schemas import Task

__all__ = [
    "BaseProvider",
    "get_provider",
    "ModelResponse",
    "classify_error_type",
    "DEFAULT_MAX_TOKENS",
]


class BaseProvider(ABC):
    name: str = "base"

    @abstractmethod
    def send_prompt(self, task: Task, system_prompt: str) -> str:
        """Send prompt to the model, return raw text response.

        This remains the stable primitive every provider implements. It raises
        on provider failure (backward-compatible with pre-Phase-2 behavior).
        """
        ...

    def generate(self, task: Task, system_prompt: str) -> ModelResponse:
        """Return a normalized :class:`ModelResponse`.

        Default implementation wraps :meth:`send_prompt`, measuring latency and
        catching errors so callers get a consistent, never-raising contract.
        Providers override this to add ``finish_reason`` and token ``usage``.
        Because real providers override ``generate`` (and their ``send_prompt``
        delegates to it), this default is used only by providers that implement
        ``send_prompt`` alone (e.g. test fakes) — no recursion occurs.
        """
        model_id = getattr(self, "model", None)
        start = time.monotonic()
        try:
            text = self.send_prompt(task, system_prompt)
            latency = int((time.monotonic() - start) * 1000)
            return ModelResponse(
                text=text or "",
                provider=self.name,
                model=model_id,
                finish_reason=None,
                usage=None,
                latency_ms=latency,
            )
        except Exception as e:
            latency = int((time.monotonic() - start) * 1000)
            return ModelResponse(
                text="",
                provider=self.name,
                model=model_id,
                finish_reason="error",
                latency_ms=latency,
                error=str(e),
                error_type=classify_error_type(e),
            )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


def get_provider(name: str, **kwargs) -> BaseProvider:
    registry: dict[str, type[BaseProvider]] = {}

    from inspektorium.audit.providers.anthropic import AnthropicProvider
    from inspektorium.audit.providers.ollama import OllamaProvider
    from inspektorium.audit.providers.openai import OpenAIProvider

    registry["anthropic"] = AnthropicProvider
    registry["openai"] = OpenAIProvider
    registry["ollama"] = OllamaProvider

    if name not in registry:
        raise ValueError(
            f"Unknown provider: {name}. Available: {list(registry.keys())}"
        )
    return registry[name](**kwargs)
