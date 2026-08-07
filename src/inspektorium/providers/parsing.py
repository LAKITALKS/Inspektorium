"""Strict parsing for precomputed and provider-generated proposal JSON."""

from __future__ import annotations

import json

from pydantic import ValidationError

from inspektorium.core.models import ProposalBatch
from inspektorium.core.relations import ValidationIssueCode


class ProposalParseError(ValueError):
    """Provider output was not exact valid JSON conforming to ProposalBatch."""

    code = ValidationIssueCode.MALFORMED_PROPOSAL

    def __init__(self, message: str) -> None:
        super().__init__(f"{self.code.value}: {message}")


def _reject_nonstandard_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant: {value}")


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_proposal_json(raw: str) -> ProposalBatch:
    """Parse exact JSON without prose extraction or repair heuristics."""

    try:
        payload = json.loads(
            raw,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonstandard_constant,
        )
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        raise ProposalParseError("Proposal output is not valid JSON.") from exc
    try:
        return ProposalBatch.model_validate(payload)
    except ValidationError as exc:
        raise ProposalParseError(
            "Proposal JSON does not conform to the strict public schema."
        ) from exc


__all__ = ["ProposalParseError", "parse_proposal_json"]
