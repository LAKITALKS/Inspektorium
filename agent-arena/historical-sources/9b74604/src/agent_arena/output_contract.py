"""Robust structured-output (JSON) extraction and parsing for agent responses.

Phase 1 (feat/output-contract-hardening).

This module isolates all fragile JSON handling that previously lived inline in
``runner.parse_agent_output``. The old inline version could raise
``ValueError: substring not found`` when a response opened a ```` ```json ````
fence but never closed it (observed live with truncated model output).

Design guarantees:
- **Never raises** on any string input — always returns a diagnostics object.
- **Behavior for valid output is preserved**: the same 8 core ``AgentResponse``
  fields are mapped with the same ``.get(field, default)`` graceful-degradation
  semantics as the original implementation. Scoring inputs are unchanged.
- **New robustness**: unclosed / duplicated markdown fences, text before/after
  the JSON object, brace scanning that respects strings, best-effort repair of
  truncated JSON, structured parse metadata, and an optional ``finish_reason``
  hint ("length" ⇒ truncation suspected).

This module imports only ``schemas`` — it has no dependency on the runner,
providers, scoring, or reporting layers.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from agent_arena.schemas import AgentResponse


# The 8 core fields the original parser mapped. Kept identical on purpose so
# that parsed responses feed scoring exactly as before. Forecast-specific
# fields are intentionally NOT introduced here (that is a separate, tested
# change outside this phase's scope).
_CORE_LIST_FIELDS = (
    "assumptions",
    "steps",
    "alternative_hypotheses",
    "uncertainties",
    "self_check",
    "key_claims",
)
_CORE_FIELDS = ("final_answer", *_CORE_LIST_FIELDS, "confidence")


@dataclass
class ParseDiagnostics:
    """Metadata describing how (and how well) a raw output was parsed."""

    ok: bool = False
    # How the JSON candidate was located:
    # "raw" | "fenced_json" | "fenced_generic" | "brace_scan" | "repaired" | "none"
    strategy: str = "none"
    had_fence: bool = False
    fence_closed: bool = True
    truncation_suspected: bool = False
    repaired: bool = False
    missing_fields: list[str] = field(default_factory=list)
    unexpected_fields: list[str] = field(default_factory=list)
    finish_reason: str | None = None
    error: str | None = None
    raw_length: int = 0

    def as_dict(self) -> dict:
        return {
            "ok": self.ok,
            "strategy": self.strategy,
            "had_fence": self.had_fence,
            "fence_closed": self.fence_closed,
            "truncation_suspected": self.truncation_suspected,
            "repaired": self.repaired,
            "missing_fields": list(self.missing_fields),
            "unexpected_fields": list(self.unexpected_fields),
            "finish_reason": self.finish_reason,
            "error": self.error,
            "raw_length": self.raw_length,
        }


def _strip_fence(text: str, diag: ParseDiagnostics) -> str:
    """Return the inner content of a markdown code fence, if present.

    Handles both ```` ```json ```` and bare ```` ``` ```` fences, and — crucially —
    the case where the opening fence is never closed (truncated output). No
    ``str.index`` calls that can raise.
    """
    for marker, offset in (("```json", 7), ("```", 3)):
        idx = text.find(marker)
        if idx == -1:
            continue
        diag.had_fence = True
        start = idx + offset
        close = text.find("```", start)
        if close == -1:
            # Opening fence with no closing fence — the original crash case.
            diag.fence_closed = False
            diag.truncation_suspected = True
            return text[start:].strip()
        diag.fence_closed = True
        return text[start:close].strip()
    return text


def _scan_outermost_object(text: str) -> tuple[str | None, bool]:
    """Extract the outermost ``{...}`` object using a string-aware brace scan.

    Returns ``(candidate, complete)``. ``complete`` is False when a top-level
    object was opened but never closed (truncation). String contents and escape
    sequences are respected so a ``}`` inside a string value does not end the
    scan prematurely.
    """
    start = text.find("{")
    if start == -1:
        return None, False

    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1], True
    # Opened but never closed → truncated object, return from start to end.
    return text[start:], False


def _repair_truncated_json(candidate: str) -> str | None:
    """Best-effort repair of a truncated JSON object.

    Closes an unterminated string, drops a dangling trailing comma, and appends
    the missing closing brackets in the correct order based on the open-bracket
    stack. Returns a repaired string or ``None`` if repair is not feasible.

    This handles the common "cut off mid-list / mid-object" truncation. It does
    NOT try to invent missing values (e.g. a key with no value); those still
    degrade gracefully to a parse failure.
    """
    stack: list[str] = []
    in_string = False
    escape = False
    for ch in candidate:
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch in "{[":
            stack.append(ch)
        elif ch in "}]":
            if stack:
                stack.pop()

    repaired = candidate
    if in_string:
        repaired += '"'

    # Remove a dangling trailing comma (optionally followed by whitespace)
    # before we append the synthetic closers.
    trimmed = repaired.rstrip()
    if trimmed.endswith(","):
        repaired = trimmed[:-1]

    closers = {"{": "}", "[": "]"}
    for opener in reversed(stack):
        repaired += closers[opener]

    return repaired if repaired != candidate else None


def _build_response(data: dict, diag: ParseDiagnostics) -> AgentResponse | None:
    """Construct an AgentResponse from a parsed dict, preserving original
    field-mapping semantics with defensive coercion. Never raises."""
    if not isinstance(data, dict):
        diag.error = f"expected JSON object, got {type(data).__name__}"
        return None

    diag.missing_fields = [f for f in _CORE_FIELDS if f not in data]
    diag.unexpected_fields = [
        k for k in data
        if k not in _CORE_FIELDS and k not in AgentResponse.model_fields
    ]

    # Defensive confidence coercion: a non-numeric confidence should degrade to
    # 0.0 rather than fail the whole parse.
    raw_conf = data.get("confidence", 0.0)
    try:
        confidence = float(raw_conf)
    except (TypeError, ValueError):
        confidence = 0.0

    def _as_list(key: str) -> list:
        val = data.get(key, [])
        return val if isinstance(val, list) else []

    try:
        return AgentResponse(
            final_answer=data.get("final_answer", "") or "",
            assumptions=_as_list("assumptions"),
            steps=_as_list("steps"),
            alternative_hypotheses=_as_list("alternative_hypotheses"),
            uncertainties=_as_list("uncertainties"),
            self_check=_as_list("self_check"),
            key_claims=_as_list("key_claims"),
            confidence=confidence,
        )
    except Exception as e:  # pragma: no cover - AgentResponse fields are lenient
        diag.error = f"schema construction failed: {e}"
        return None


def _try_load_dict(text: str) -> dict | None:
    """json.loads that returns the value only if it is a dict, else None."""
    try:
        val = json.loads(text)
    except (json.JSONDecodeError, TypeError, ValueError):
        return None
    return val if isinstance(val, dict) else None


def extract_json_object(
    raw: str,
    finish_reason: str | None = None,
) -> tuple[dict | None, ParseDiagnostics]:
    """Robustly extract a top-level JSON **object** from raw model output.

    Returns ``(dict_or_None, diagnostics)`` and never raises. This is the shared
    extraction core reused by both the agent parser (:func:`parse_structured_output`)
    and the judge parser, so all callers get identical handling of markdown
    fences (including unclosed ones), pre/post prose, brace scanning, and
    best-effort truncation repair.

    ``finish_reason == "length"`` marks the output as truncation-suspected.
    """
    diag = ParseDiagnostics(finish_reason=finish_reason)
    diag.raw_length = len(raw) if isinstance(raw, str) else 0

    if finish_reason == "length":
        diag.truncation_suspected = True

    if not isinstance(raw, str) or not raw.strip():
        diag.error = "empty or non-string output"
        return None, diag

    text = _strip_fence(raw.strip(), diag)

    # Fast path: the (de-fenced) text is already a clean JSON object.
    data = _try_load_dict(text)
    if data is not None:
        diag.strategy = "fenced_json" if diag.had_fence else "raw"
        diag.ok = True
        return data, diag

    # Locate the outermost {...} object (handles pre/post prose, trailing text).
    candidate, complete = _scan_outermost_object(text)
    if candidate is None:
        diag.error = "no JSON object found"
        return None, diag
    if not complete:
        diag.truncation_suspected = True

    data = _try_load_dict(candidate)
    if data is not None:
        diag.strategy = "brace_scan"
        diag.ok = True
        return data, diag

    # Last resort: attempt to repair truncated JSON.
    repaired = _repair_truncated_json(candidate)
    if repaired is not None:
        data = _try_load_dict(repaired)
        if data is not None:
            diag.strategy = "repaired"
            diag.repaired = True
            diag.truncation_suspected = True
            diag.ok = True
            return data, diag
        diag.error = "repair failed"
        return None, diag

    diag.error = "unparseable JSON"
    return None, diag


def parse_structured_output(
    raw: str,
    finish_reason: str | None = None,
) -> tuple[AgentResponse | None, ParseDiagnostics]:
    """Robustly parse a raw model output string into an AgentResponse.

    Returns ``(response_or_None, diagnostics)`` and never raises. Delegates the
    JSON extraction to :func:`extract_json_object` and then maps the parsed dict
    onto the 8 core ``AgentResponse`` fields (with the original graceful-degradation
    defaults). ``finish_reason == "length"`` is threaded through as a truncation
    hint.
    """
    data, diag = extract_json_object(raw, finish_reason)
    if data is None:
        return None, diag
    resp = _build_response(data, diag)
    diag.ok = resp is not None
    return resp, diag
