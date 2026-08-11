"""Optional Anthropic provider for one strict evaluator proposal call."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from typing import Any

from inspektorium.core.models import InspectionInput, ProposalBatch
from inspektorium.providers.base import ProviderError

PUBLIC_SYSTEM_PROMPT = """You are the evaluator component of Inspektorium, a
public evidence-binding reference tool.

Inspect only the canonical answer and sources supplied in the user message.
Do not use external knowledge.

Identify atomic claims in the answer. For each claim, propose exactly one
relationship to the supplied sources: supported, contradicted, not_established,
or attribution_mismatch.

For supported, contradicted, and attribution_mismatch, quote one supplied source
exactly and provide its exact source_id and Python string character offsets
[start, end). Never invent, paraphrase, normalize, or repair a quotation. For
not_established, use null for every evidence field unless an exact source
passage is genuinely useful to explain the limitation.

Evidence sufficiency is one of sufficient, partial, or insufficient. Evaluator
certainty is one of high, medium, or low. They are qualitative and distinct.
Provide only a concise rationale, not hidden reasoning or chain-of-thought.

Return only one JSON object conforming exactly to the supplied schema. Do not
use Markdown fences or add prose."""


def build_user_prompt(inspection_input: InspectionInput) -> str:
    """Serialize only explicit inspection inputs and the public output schema."""

    input_json = json.dumps(
        inspection_input.model_dump(mode="json"),
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )
    schema_json = json.dumps(
        ProposalBatch.model_json_schema(),
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )
    return (
        f"INSPECTION INPUT\n{input_json}\n\nREQUIRED OUTPUT JSON SCHEMA\n{schema_json}"
    )


def _safe_api_message(message: str, inspection_input: InspectionInput) -> str:
    """Redact inspection text and credential-shaped material from API errors."""

    redacted = message
    private_texts = [
        inspection_input.answer.text,
        *(source.text for source in inspection_input.sources),
        *(source.title for source in inspection_input.sources if source.title),
    ]
    for private_text in sorted(private_texts, key=len, reverse=True):
        redacted = redacted.replace(private_text, "[redacted inspection text]")
    redacted = re.sub(r"sk-ant-[A-Za-z0-9_-]+", "[redacted credential]", redacted)
    redacted = re.sub(
        r"(?i)(authorization|x-api-key)\s*[:=]\s*\S+",
        r"\1=[redacted credential]",
        redacted,
    )
    redacted = " ".join(redacted.split())
    return redacted if len(redacted) <= 500 else redacted[:497] + "..."


def _request_failure_message(
    exc: Exception, inspection_input: InspectionInput
) -> str:
    """Describe only safe, bounded fields from an Anthropic request error."""

    details: list[str] = []
    status_code = getattr(exc, "status_code", None)
    if isinstance(status_code, int):
        details.append(f"HTTP {status_code}")

    body = getattr(exc, "body", None)
    error = body.get("error") if isinstance(body, Mapping) else None
    if isinstance(error, Mapping):
        error_type = error.get("type")
        if isinstance(error_type, str) and re.fullmatch(
            r"[A-Za-z0-9_.-]{1,80}", error_type
        ):
            details.append(error_type)
        message = error.get("message")
        if isinstance(message, str) and message:
            details.append(_safe_api_message(message, inspection_input))

    if details:
        return f"Anthropic request failed ({'; '.join(details)})."
    return f"Anthropic request failed ({type(exc).__name__})."


class AnthropicProvider:
    """Exactly one real provider, loaded only when explicitly requested."""

    def __init__(self, *, model: str, client: Any | None = None) -> None:
        if not model:
            raise ValueError("model must be a non-empty Anthropic model identifier")
        self.model = model
        if client is not None:
            self._client = client
            return
        try:
            import anthropic
        except ImportError as exc:
            raise ProviderError(
                "Anthropic support is not installed; install inspektorium[anthropic]."
            ) from exc
        self._client = anthropic.Anthropic()

    def propose_findings(self, inspection_input: InspectionInput) -> ProposalBatch:
        """Make one SDK-transformed, strictly parsed ProposalBatch request."""

        try:
            response = self._client.messages.parse(
                model=self.model,
                max_tokens=4096,
                temperature=0,
                system=PUBLIC_SYSTEM_PROMPT,
                output_format=ProposalBatch,
                messages=[
                    {
                        "role": "user",
                        "content": build_user_prompt(inspection_input),
                    }
                ],
            )
        except Exception as exc:
            message = _request_failure_message(exc, inspection_input)
            raise ProviderError(message) from exc

        parsed_blocks = [
            block.parsed_output
            for block in response.content
            if getattr(block, "type", None) == "text"
            and getattr(block, "parsed_output", None) is not None
        ]
        if len(parsed_blocks) != 1:
            raise ProviderError(
                "Anthropic response did not contain exactly one parsed output."
            )
        proposal_batch = parsed_blocks[0]
        if not isinstance(proposal_batch, ProposalBatch):
            raise ProviderError("Anthropic parsed output had an unexpected type.")
        return proposal_batch


__all__ = ["AnthropicProvider", "PUBLIC_SYSTEM_PROMPT", "build_user_prompt"]
