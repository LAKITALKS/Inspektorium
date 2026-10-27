"""Claude 5.5 live adapter for the AA-P10-LIVE/1.0 audit path.

Kept separate from ``providers/anthropic.py``, whose bytes are bound by historical 4.5
runtime contracts. One call sends exactly one HTTP request (no SDK or hidden retries) to the
fixed direct Anthropic endpoint; environment variables cannot redirect it. Sampling
parameters are never sent. Adaptive thinking runs with an explicit effort, and the final
answer is taken only from ``text`` blocks: thinking blocks never substitute for it.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import Any

from inspektorium.audit.providers.response import ModelResponse

LIVE_ENDPOINT = "https://api.anthropic.com"
MESSAGES_URL = LIVE_ENDPOINT + "/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
USER_MESSAGE_VERSION = "aa-p10-live-user-message/1.0"
EVIDENCE_SCHEMA = "aa-p10-live-evidence/1.0"
# Conservative allowance for role/message framing on top of the UTF-8 byte bound.
FRAMING_TOKENS = 2048
PROMPT_TAGS = ("<task_prompt", "</task_prompt>", "<task_context", "</task_context>")
TRANSIENT_ERRORS = {"overloaded", "rate_limit", "server_error", "timeout", "connection"}
# Prompt versions are registered in inspektorium.audit.execution.runner; tests assert these names resolve there.
LEGACY_PROMPT_BINDING = (
    "study_forensics_prompt/v3-phase8",
    "study_forensics_prompt/v3-phase8-review-p9-1",
)
CONTRACT_R1_PROMPT_BINDING = (
    "study_forensics_prompt/v3-phase8-contract-r1",
    "study_forensics_prompt/v3-phase8-contract-r1-review-p9-1",
)
CONTRACT_R2_PROMPT_BINDING = (
    "study_forensics_prompt/v3-phase8-contract-r2",
    "study_forensics_prompt/v3-phase8-contract-r2-review-p9-2",
)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _ceil_div(numerator: int, denominator: int) -> int:
    return -(-numerator // denominator)


@dataclass(frozen=True)
class PriceTier:
    """Micro-USD per million tokens for one prompt-length tier."""

    input: int
    output: int
    cache_write_5m: int
    cache_read: int


@dataclass(frozen=True)
class Pricing:
    standard: PriceTier
    long_context: PriceTier | None = None
    long_context_threshold_tokens: int | None = None

    def tier(self, prompt_tokens: int) -> PriceTier:
        if (
            self.long_context
            and self.long_context_threshold_tokens is not None
            and prompt_tokens > self.long_context_threshold_tokens
        ):
            return self.long_context
        return self.standard


@dataclass(frozen=True)
class LiveProfile:
    profile_id: str
    model_id: str
    effort: str
    max_tokens: int
    thinking_type: str
    timeout_seconds: float
    sdk_max_retries: int
    pricing: Pricing
    pricing_source: str
    rationale: str
    omitted_parameters: tuple[str, ...] = field(
        default=("temperature", "top_p", "top_k")
    )
    # (primary prompt version, Phase9 review prompt version). None is the original AA-P10-LIVE/1.0
    # pair of the @1 profiles; it is serialized only when declared, so @1 fingerprints stay frozen.
    prompt_binding: tuple[str, str] | None = None

    @property
    def prompt_versions(self) -> tuple[str, str]:
        return self.prompt_binding or LEGACY_PROMPT_BINDING

    def request_body(self, system: str, user: str) -> dict:
        return {
            "model": self.model_id,
            "max_tokens": self.max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": user}],
            "thinking": {"type": self.thinking_type},
            "output_config": {"effort": self.effort},
        }

    def fingerprint(self) -> str:
        return sha256_text(canonical_json(profile_dict(self)))


def profile_dict(profile: LiveProfile) -> dict:
    tier = lambda t: (  # noqa: E731
        None
        if t is None
        else {
            "input": t.input,
            "output": t.output,
            "cache_write_5m": t.cache_write_5m,
            "cache_read": t.cache_read,
        }
    )
    data = {
        "profile_id": profile.profile_id,
        "model_id": profile.model_id,
        "effort": profile.effort,
        "max_tokens": profile.max_tokens,
        "thinking_type": profile.thinking_type,
        "timeout_seconds": profile.timeout_seconds,
        "sdk_max_retries": profile.sdk_max_retries,
        "endpoint": MESSAGES_URL,
        "anthropic_version": ANTHROPIC_VERSION,
        "user_message_version": USER_MESSAGE_VERSION,
        "omitted_parameters": list(profile.omitted_parameters),
        "pricing_microusd_per_mtok": {
            "standard": tier(profile.pricing.standard),
            "long_context": tier(profile.pricing.long_context),
            "long_context_threshold_tokens": profile.pricing.long_context_threshold_tokens,
        },
        "pricing_source": profile.pricing_source,
        "rationale": profile.rationale,
    }
    if profile.prompt_binding is not None:
        # Bind prompt bytes, not only names: a changed registry entry changes the fingerprint.
        from inspektorium.audit.execution.runner import resolve_study_forensics_prompt

        primary, review = profile.prompt_binding
        data["prompt_binding"] = {
            "primary": primary,
            "primary_sha256": sha256_text(resolve_study_forensics_prompt(primary)),
            "review": review,
            "review_sha256": sha256_text(resolve_study_forensics_prompt(review)),
        }
    return data


_DOCS = (
    "https://platform.claude.com/docs/en/about-claude/pricing (checked 2026-10-11); "
    "thinking tokens are billed as output and count toward max_tokens"
)

# Frozen before the first live result. New revisions get a new profile ID; never edit in place.
PROFILES: dict[str, LiveProfile] = {
    "claude-haiku-5-5@1": LiveProfile(
        profile_id="claude-haiku-5-5@1",
        model_id="claude-haiku-5-5",
        effort="medium",
        max_tokens=16000,
        thinking_type="adaptive",
        timeout_seconds=300.0,
        sdk_max_retries=0,
        pricing=Pricing(
            standard=PriceTier(100_000, 500_000, 125_000, 10_000),
            long_context=PriceTier(500_000, 2_500_000, 625_000, 50_000),
            long_context_threshold_tokens=100_000,
        ),
        pricing_source=_DOCS,
        rationale=(
            "Default effort medium (documented default and recommended start); adaptive thinking "
            "stays on; 16000 max_tokens leave room for thinking plus the Phase-8 JSON."
        ),
    ),
    "claude-sonnet-5-5@1": LiveProfile(
        profile_id="claude-sonnet-5-5@1",
        model_id="claude-sonnet-5-5",
        effort="medium",
        max_tokens=16000,
        thinking_type="adaptive",
        timeout_seconds=300.0,
        sdk_max_retries=0,
        pricing=Pricing(standard=PriceTier(2_000_000, 10_000_000, 2_500_000, 100_000)),
        pricing_source=_DOCS,
        rationale=(
            "Effort medium instead of default high bounds cost and latency for one structured "
            "extraction; fixed before results; thinking cannot be disabled on this model."
        ),
    ),
}

# Repair revision R1, fixed after the @1 live results and before any @2 result. Only the fields
# named here differ from @1; model, effort, thinking, timeout, retries and pricing are copied.
PROFILES["claude-haiku-5-5@2"] = replace(
    PROFILES["claude-haiku-5-5@1"],
    profile_id="claude-haiku-5-5@2",
    max_tokens=32000,
    prompt_binding=CONTRACT_R1_PROMPT_BINDING,
    rationale=(
        "R1: binds the explicitly stated AA-P8/1.0 host contract prompt. max_tokens 16000 -> 32000 "
        "because @1 used up to 15505 of 16000 output tokens (LS-04) and the stated contract asks for "
        "more trace objects; the documented synchronous maximum is 128K. Effort and thinking unchanged."
    ),
)
PROFILES["claude-sonnet-5-5@2"] = replace(
    PROFILES["claude-sonnet-5-5@1"],
    profile_id="claude-sonnet-5-5@2",
    prompt_binding=CONTRACT_R1_PROMPT_BINDING,
    rationale=(
        "R1: binds the explicitly stated AA-P8/1.0 host contract prompt. All request parameters "
        "equal @1, which used at most 8168 of 16000 output tokens; effort medium kept."
    ),
)

# AA-P8/1.1 + AA-P9/1.1 revision (docs/phase8_9_conflict_addendum.md), fixed before any @3 result.
# Only the fields named here differ from @2.
PROFILES["claude-haiku-5-5@3"] = replace(
    PROFILES["claude-haiku-5-5@2"],
    profile_id="claude-haiku-5-5@3",
    max_tokens=48000,
    prompt_binding=CONTRACT_R2_PROMPT_BINDING,
    rationale=(
        "r2: binds the AA-P8/1.1 output contract (own judgment, host derivation separate, mandatory "
        "conflict review). max_tokens 32000 -> 48000 because @2 used up to 31121 of 32000 output "
        "tokens (LS-04); the documented synchronous maximum is 128K. Effort and thinking unchanged."
    ),
)
PROFILES["claude-sonnet-5-5@3"] = replace(
    PROFILES["claude-sonnet-5-5@2"],
    profile_id="claude-sonnet-5-5@3",
    prompt_binding=CONTRACT_R2_PROMPT_BINDING,
    rationale=(
        "r2: binds the AA-P8/1.1 output contract. All request parameters equal @2, which used at "
        "most 10569 of 16000 output tokens; effort medium kept."
    ),
)


# A canonical audit task carries only identity fields, the claim and its supplied source context.
# Any other Task field (gold, rubric, curator, evaluator or library metadata) marks a curated
# benchmark case, whose `context` is curator commentary that may state the expected label
# (Package B, P2-F1/P3-F1/P6-F1). Such a task is refused, never sent.
AUDIT_TASK_FIELDS = frozenset(
    {
        "id",
        "title",
        "domain",
        "difficulty",
        "task_type",
        "prompt",
        "context",
        "evaluation",
        "output_schema",
    }
)


def benchmark_fields(task) -> list[str]:
    """Non-audit Task fields that differ from their defaults (empty for a canonical audit task)."""
    return sorted(
        name
        for name, info in type(task).model_fields.items()
        if name not in AUDIT_TASK_FIELDS
        and getattr(task, name) != info.get_default(call_default_factory=True)
    )


def build_user_message(task) -> str:
    """Deliver exactly task.prompt and task.context; never gold, rubric or reference fields."""
    curated = benchmark_fields(task)
    if curated:
        raise ValueError(
            "Curated benchmark case fields present ("
            + ", ".join(curated)
            + "); its context may be "
            "curator commentary, so it is never sent to a model"
        )
    prompt, context = task.prompt or "", task.context or ""
    if any(tag in prompt or tag in context for tag in PROMPT_TAGS):
        raise ValueError(
            "Task text contains a reserved live-message delimiter; blocked before sending"
        )
    return (
        f'<task_prompt source_id="input">\n{prompt}\n</task_prompt>\n\n'
        f'<task_context source_id="context">\n{context}\n</task_context>'
    )


def input_token_bound(system: str, user: str) -> int:
    """Conservative upper bound: one token per UTF-8 byte plus framing (labelled assumption)."""
    return len(system.encode("utf-8")) + len(user.encode("utf-8")) + FRAMING_TOKENS


def max_exposure_microusd(
    profile: LiveProfile, system: str, user: str
) -> tuple[int, dict]:
    bound = input_token_bound(system, user)
    tier = profile.pricing.tier(bound)
    value = _ceil_div(bound * tier.input, 1_000_000) + _ceil_div(
        profile.max_tokens * tier.output, 1_000_000
    )
    return value, {
        "input_token_bound": bound,
        "input_bound_basis": "utf8_bytes_plus_framing_assumption",
        "max_output_tokens_including_thinking": profile.max_tokens,
        "tier_input_microusd_per_mtok": tier.input,
        "tier_output_microusd_per_mtok": tier.output,
        "cache_discount_assumed": False,
    }


def cost_microusd(profile: LiveProfile, usage: dict) -> int:
    def count(key):
        value = usage.get(key) or 0
        if type(value) is not int or value < 0:
            raise ValueError(f"Invalid usage field {key}")
        return value

    inputs, writes, reads, outputs = (
        count("input_tokens"),
        count("cache_creation_input_tokens"),
        count("cache_read_input_tokens"),
        count("output_tokens"),
    )
    tier = profile.pricing.tier(inputs + writes + reads)
    return _ceil_div(
        inputs * tier.input
        + writes * tier.cache_write_5m
        + reads * tier.cache_read
        + outputs * tier.output,
        1_000_000,
    )


def interpret_message(raw: dict) -> dict:
    """Classify one Messages API body. Only text blocks form the final answer."""
    blocks = raw.get("content") if isinstance(raw.get("content"), list) else []
    types = [b.get("type") if isinstance(b, dict) else None for b in blocks]
    texts = [
        b.get("text", "")
        for b in blocks
        if isinstance(b, dict)
        and b.get("type") == "text"
        and isinstance(b.get("text"), str)
    ]
    text = "".join(texts)
    stop = raw.get("stop_reason")
    if stop == "max_tokens":
        state = "truncated"
    elif stop == "refusal":
        state = "refusal"
    elif stop != "end_turn":
        state = "unexpected_stop_reason"
    elif not text.strip():
        state = "no_final_text"
    else:
        state = "complete"
    usage = raw.get("usage") if isinstance(raw.get("usage"), dict) else {}
    return {
        "final_text": text,
        "completion_state": state,
        "stop_reason": stop,
        "content_block_types": types,
        "text_block_count": len(texts),
        "thinking_block_count": sum(
            t in {"thinking", "redacted_thinking"} for t in types
        ),
        "returned_model": raw.get("model"),
        "message_id": raw.get("id"),
        "usage": {
            k: usage.get(k)
            for k in (
                "input_tokens",
                "output_tokens",
                "cache_creation_input_tokens",
                "cache_read_input_tokens",
            )
        },
    }


def _error_type(status: int | None, body: dict | None) -> str:
    error = body.get("error") if isinstance(body, dict) else None
    kind = error.get("type") if isinstance(error, dict) else None
    if status == 529 or kind == "overloaded_error":
        return "overloaded"
    if status == 429 or kind == "rate_limit_error":
        return "rate_limit"
    if status in {401} or kind == "authentication_error":
        return "auth_error"
    if status in {403} or kind == "permission_error":
        return "permission_error"
    if status in {404} or kind == "not_found_error":
        return "not_found_error"
    if status is not None and status >= 500:
        return "server_error"
    return "invalid_request"


def send_request(
    profile: LiveProfile,
    system: str,
    user: str,
    *,
    transport=None,
    api_key: str | None = None,
) -> dict:
    """Send exactly one request. Never raises; secrets never enter the returned record."""
    import httpx

    body = profile.request_body(system, user)
    wire = canonical_json(body)
    record: dict[str, Any] = {
        "request_body": body,
        "request_sha256": sha256_text(wire),
        "endpoint": MESSAGES_URL,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "request_sent": False,
        "http_status": None,
        "request_id": None,
        "response_body": None,
        "error_type": None,
        "error": None,
        "billing": "none",
    }
    key = api_key if api_key is not None else os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        record.update(
            error_type="credential_missing", error="ANTHROPIC_API_KEY is not available"
        )
        return record
    headers = {
        "x-api-key": key,
        "anthropic-version": ANTHROPIC_VERSION,
        "content-type": "application/json",
    }
    start = time.monotonic()
    try:
        # trust_env=False: proxy/base-URL environment variables cannot silently redirect the request.
        with httpx.Client(
            transport=transport,
            timeout=profile.timeout_seconds,
            follow_redirects=False,
            trust_env=False,
        ) as client:
            record["request_sent"] = True
            response = client.post(
                MESSAGES_URL, content=wire.encode("utf-8"), headers=headers
            )
        record["latency_ms"] = int((time.monotonic() - start) * 1000)
        record["http_status"] = response.status_code
        record["request_id"] = response.headers.get("request-id")
        try:
            parsed = response.json()
        except ValueError:
            parsed = None
        if not isinstance(parsed, dict):
            parsed = {
                "unparseable_body_sha256": hashlib.sha256(response.content).hexdigest()
            }
        record["response_body"] = parsed
        if response.status_code == 200:
            record["billing"] = (
                "usage_reported" if isinstance(parsed.get("usage"), dict) else "unknown"
            )
        else:
            error = parsed.get("error")
            kind = error.get("type", "error") if isinstance(error, dict) else "error"
            record.update(
                error_type=_error_type(response.status_code, parsed),
                billing="unknown",
                error=f"HTTP {response.status_code}: {kind}",
            )
    except httpx.TimeoutException as exc:
        record.update(
            latency_ms=int((time.monotonic() - start) * 1000),
            error_type="timeout",
            error=f"{type(exc).__name__}",
            billing="unknown",
        )
    except httpx.HTTPError as exc:
        record.update(
            latency_ms=int((time.monotonic() - start) * 1000),
            error_type="connection",
            error=f"{type(exc).__name__}",
            billing="unknown",
        )
    record["completed_at"] = datetime.now(timezone.utc).isoformat()
    return record


@dataclass
class LiveModelResponse(ModelResponse):
    """ModelResponse plus bound live provenance; legacy callers ignore the extra field."""

    execution_evidence: dict | None = None


def response_from_capture(
    profile: LiveProfile, capture: dict
) -> tuple[dict, ModelResponse]:
    """Map one captured call to (interpretation, normalized response) without network access."""
    body = capture.get("response_body")
    if capture.get("http_status") == 200 and isinstance(body, dict):
        info = interpret_message(body)
        state = info["completion_state"]
        if state == "complete":
            return info, ModelResponse(
                text=info["final_text"],
                provider="anthropic-live",
                model=info["returned_model"],
                finish_reason="stop",
                usage=dict(info["usage"]),
                latency_ms=capture.get("latency_ms"),
            )
        if state == "truncated":
            # Keep the partial raw text; the parser marks truncation and analysis stays incomplete.
            return info, ModelResponse(
                text=info["final_text"],
                provider="anthropic-live",
                model=info["returned_model"],
                finish_reason="length",
                usage=dict(info["usage"]),
                latency_ms=capture.get("latency_ms"),
            )
        return info, ModelResponse(
            text="",
            provider="anthropic-live",
            model=info["returned_model"],
            finish_reason="error",
            usage=dict(info["usage"]),
            latency_ms=capture.get("latency_ms"),
            error=f"Live response unusable: {state} (stop_reason={info['stop_reason']})",
            error_type=state,
        )
    info = {
        "final_text": "",
        "completion_state": "provider_error",
        "stop_reason": None,
        "content_block_types": [],
        "text_block_count": 0,
        "thinking_block_count": 0,
        "returned_model": None,
        "message_id": None,
        "usage": {},
    }
    return info, ModelResponse(
        text="",
        provider="anthropic-live",
        model=profile.model_id,
        finish_reason="error",
        latency_ms=capture.get("latency_ms"),
        error=capture.get("error") or "Live request failed",
        error_type=capture.get("error_type") or "provider_error",
    )
