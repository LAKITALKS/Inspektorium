"""Strict parsing for inspection-input JSON and proposal JSON.

Both documents go through the same strict JSON decoder
(``inspektorium.core.strict_json``) and are then validated against their
public schema. There is no prose extraction, repair, or permissive fallback.
"""

from __future__ import annotations

import re

from pydantic import ValidationError

from inspektorium.core.models import InspectionInput, ProposalBatch
from inspektorium.core.relations import ValidationIssueCode
from inspektorium.core.strict_json import (
    StrictJSONError,
    display_key,
    load_strict_json,
)

_SHOWN_SCHEMA_ERRORS = 3
_MESSAGE_LIMIT = 200
_PLAIN_LOCATION_PART = re.compile(r"[A-Za-z0-9_]{1,40}")


class ProposalParseError(ValueError):
    """Provider output was not exact valid JSON conforming to ProposalBatch."""

    code = ValidationIssueCode.MALFORMED_PROPOSAL

    def __init__(self, message: str) -> None:
        super().__init__(f"{self.code.value}: {message}")


class InputParseError(ValueError):
    """Inspection input was not exact valid JSON conforming to InspectionInput."""


def _location(parts: tuple[int | str, ...]) -> str:
    shown = [
        str(part)
        if isinstance(part, int) or _PLAIN_LOCATION_PART.fullmatch(part)
        else display_key(part)
        for part in parts
    ]
    return ".".join(shown)


def _schema_error_summary(exc: ValidationError) -> str:
    """Describe schema failures by location and rule, never by input value."""

    details: list[str] = []
    for error in exc.errors(include_url=False, include_input=False)[
        :_SHOWN_SCHEMA_ERRORS
    ]:
        message = error["msg"][:_MESSAGE_LIMIT]
        if not (message.isascii() and message.isprintable()):
            message = ascii(message)[1:-1]
        location = _location(tuple(error["loc"]))
        details.append(f"{location}: {message}" if location else message)
    hidden = exc.error_count() - len(details)
    summary = "; ".join(details)
    if hidden > 0:
        summary += f" (and {hidden} more)"
    return summary


def parse_proposal_json(raw: str) -> ProposalBatch:
    """Parse exact JSON without prose extraction or repair heuristics."""

    try:
        payload = load_strict_json(raw)
    except StrictJSONError as exc:
        raise ProposalParseError(f"Proposal output is not valid JSON: {exc}.") from exc
    try:
        return ProposalBatch.model_validate(payload)
    except ValidationError as exc:
        raise ProposalParseError(
            "Proposal JSON does not conform to the strict public schema: "
            f"{_schema_error_summary(exc)}."
        ) from exc


def parse_inspection_input_json(raw: str) -> InspectionInput:
    """Parse one InspectionInput document with the same strict JSON rules.

    Clean documents produce the same model as ``InspectionInput`` validation
    always did; duplicate keys, non-standard constants, unpaired surrogates,
    and invalid JSON are rejected before any analysis can start.
    """

    try:
        payload = load_strict_json(raw)
    except StrictJSONError as exc:
        raise InputParseError(f"Inspection input is not valid JSON: {exc}.") from exc
    try:
        return InspectionInput.model_validate(payload)
    except ValidationError as exc:
        raise InputParseError(
            "Inspection input does not conform to the strict public schema: "
            f"{_schema_error_summary(exc)}."
        ) from exc


__all__ = [
    "InputParseError",
    "ProposalParseError",
    "parse_inspection_input_json",
    "parse_proposal_json",
]
