"""Structured provider response contract (Phase 2).

Introduces a small, backward-compatible ``ModelResponse`` returned by
``BaseProvider.generate``. Providers previously returned only raw text via
``send_prompt``; that method is preserved. ``generate`` adds observability:
normalized ``finish_reason``, token ``usage``, ``latency_ms``, and normalized
error metadata — without any tool-calling or streaming abstractions.

This module imports nothing from the rest of the package (no cycles).
"""

from __future__ import annotations

from dataclasses import dataclass


# Shared default cap. The pre-Phase-2 audit flagged OpenAI's 2048 as too low
# (caused truncation). Anthropic already used 4096; this makes the default
# consistent across text providers.
DEFAULT_MAX_TOKENS = 4096


# Normalized finish_reason values used across all providers.
FINISH_STOP = "stop"
FINISH_LENGTH = "length"
FINISH_ERROR = "error"
FINISH_UNKNOWN = "unknown"


@dataclass
class ModelResponse:
    """Normalized result of a single provider call.

    ``text`` is always a string (possibly empty on error). ``finish_reason`` is
    one of the normalized constants above or ``None`` when the provider does not
    expose it (never fabricated). ``usage`` uses stable keys where available and
    may be ``None``/``{}``. On failure ``error``/``error_type`` are populated and
    ``text`` is empty — a failed call never masquerades as a successful one.
    """

    text: str = ""
    provider: str | None = None
    model: str | None = None
    finish_reason: str | None = None
    usage: dict | None = None
    latency_ms: int | None = None
    error: str | None = None
    error_type: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None

    def as_dict(self) -> dict:
        return {
            "text": self.text,
            "provider": self.provider,
            "model": self.model,
            "finish_reason": self.finish_reason,
            "usage": self.usage,
            "latency_ms": self.latency_ms,
            "error": self.error,
            "error_type": self.error_type,
        }


def classify_error_type(exc: Exception) -> str:
    """Map a provider exception to a normalized ``error_type`` string.

    Deliberately string/name based so we do not need to import any provider SDK
    (all are optional dependencies). Returns one of: ``auth_error``,
    ``not_found_error``, ``rate_limit_error``, ``timeout_error``,
    ``provider_error`` (default).
    """
    name = type(exc).__name__.lower()
    msg = str(exc).lower()

    def has(*keys: str) -> bool:
        return any(k in name or k in msg for k in keys)

    if (
        has("authentication", "permissiondenied", "unauthorized")
        or "401" in msg
        or "403" in msg
        or "api key" in msg
        or "api_key" in msg
    ):
        return "auth_error"
    if has("notfound", "not_found") or "404" in msg:
        return "not_found_error"
    if has("ratelimit", "rate_limit") or "429" in msg or "too many requests" in msg:
        return "rate_limit_error"
    if has("timeout") or "timed out" in msg:
        return "timeout_error"
    return "provider_error"
