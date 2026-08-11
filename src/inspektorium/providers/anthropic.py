"""Optional Anthropic provider for one strict evaluator proposal call."""

from __future__ import annotations

import json
from typing import Any

from inspektorium.core.models import InspectionInput, ProposalBatch
from inspektorium.providers.base import ProviderError
from inspektorium.providers.parsing import parse_proposal_json

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
        """Make one request and parse one exact ProposalBatch response."""

        try:
            response = self._client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0,
                system=PUBLIC_SYSTEM_PROMPT,
                output_config={
                    "format": {
                        "type": "json_schema",
                        "schema": ProposalBatch.model_json_schema(),
                    }
                },
                messages=[
                    {
                        "role": "user",
                        "content": build_user_prompt(inspection_input),
                    }
                ],
            )
        except Exception as exc:
            raise ProviderError(
                f"Anthropic request failed ({type(exc).__name__})."
            ) from exc

        text_blocks = [
            block.text
            for block in response.content
            if getattr(block, "type", None) == "text" and getattr(block, "text", "")
        ]
        if len(text_blocks) != 1:
            raise ProviderError(
                "Anthropic response did not contain exactly one text block."
            )
        return parse_proposal_json(text_blocks[0])


__all__ = ["AnthropicProvider", "PUBLIC_SYSTEM_PROMPT", "build_user_prompt"]
