"""Strict proposal parser failure tests."""

from __future__ import annotations

import json
from typing import Any

import pytest

from inspektorium.providers.parsing import ProposalParseError, parse_proposal_json


def _batch(data: dict[str, Any]) -> str:
    return json.dumps({"schema_version": "0.1", "findings": [data]})


def test_valid_json_and_schema_parse(supported_proposal_data: dict[str, Any]) -> None:
    parsed = parse_proposal_json(_batch(supported_proposal_data))

    assert parsed.findings[0].claim_id == "claim-1"


def test_malformed_json_is_not_repaired() -> None:
    with pytest.raises(ProposalParseError, match="malformed_proposal") as exc_info:
        parse_proposal_json("```json\n{}\n```")

    assert exc_info.value.code.value == "malformed_proposal"


@pytest.mark.parametrize(
    "raw",
    [
        '{"schema_version":"0.1","findings":NaN}',
        '{"schema_version":"0.1","schema_version":"0.1","findings":[]}',
    ],
)
def test_nonstandard_or_ambiguous_json_is_rejected(raw: str) -> None:
    with pytest.raises(ProposalParseError, match="not valid JSON"):
        parse_proposal_json(raw)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("proposed_relation", "likely"),
        ("evidence_sufficiency", "0.8"),
        ("evaluator_certainty", "certain"),
    ],
)
def test_invalid_vocabularies_fail(
    field: str,
    value: str,
    supported_proposal_data: dict[str, Any],
) -> None:
    supported_proposal_data[field] = value

    with pytest.raises(ProposalParseError, match="strict public schema"):
        parse_proposal_json(_batch(supported_proposal_data))


def test_extra_field_fails(supported_proposal_data: dict[str, Any]) -> None:
    supported_proposal_data["unexpected"] = True

    with pytest.raises(ProposalParseError):
        parse_proposal_json(_batch(supported_proposal_data))


def test_missing_field_fails(supported_proposal_data: dict[str, Any]) -> None:
    del supported_proposal_data["rationale"]

    with pytest.raises(ProposalParseError):
        parse_proposal_json(_batch(supported_proposal_data))
