"""Strict proposal parser failure tests."""

from __future__ import annotations

import json
from typing import Any

import pytest

from inspektorium.core.models import InspectionInput
from inspektorium.core.validation import validate_finding
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


@pytest.mark.parametrize(
    "raw",
    [
        '{"schema_version":"0.1","findings":[Infinity]}',
        '{"schema_version":"0.1","findings":[-Infinity]}',
        '{"schema_version":"0.1","findings":[{"claim_id":"a","claim_id":"b"}]}',
        '{"schema_version":"0.1","findings":[],"\\u0066indings":[]}',
        '{"schema_version":"0.1","findings":[]} trailing',
    ],
)
def test_nested_ambiguity_and_trailing_data_are_rejected(raw: str) -> None:
    with pytest.raises(ProposalParseError, match="not valid JSON"):
        parse_proposal_json(raw)


def test_duplicate_key_reason_is_reported(
    supported_proposal_data: dict[str, Any],
) -> None:
    raw = _batch(supported_proposal_data).replace(
        '"rationale": ', '"rationale": "shadowed", "rationale": ', 1
    )

    with pytest.raises(ProposalParseError) as exc_info:
        parse_proposal_json(raw)

    assert str(exc_info.value) == (
        "malformed_proposal: Proposal output is not valid JSON: "
        "duplicate object key 'rationale'."
    )


def test_unpaired_surrogate_is_rejected_as_invalid_json(
    supported_proposal_data: dict[str, Any],
) -> None:
    raw = _batch(supported_proposal_data).replace(
        '"rationale": "', '"rationale": "\\ud800', 1
    )

    with pytest.raises(ProposalParseError) as exc_info:
        parse_proposal_json(raw)

    assert "not valid JSON: a string contains an unpaired UTF-16 surrogate" in str(
        exc_info.value
    )


@pytest.mark.parametrize(
    "raw",
    [
        '{"schema_version":"0.1","findings":' + "[" * 100_000 + "]" * 100_000 + "}",
        "[" * 100_000,
    ],
    ids=["balanced", "unterminated"],
)
def test_deep_nesting_fails_as_a_parse_error_not_a_recursion_error(raw: str) -> None:
    with pytest.raises(ProposalParseError, match="nesting is deeper than"):
        parse_proposal_json(raw)


def test_bytes_must_be_plain_utf8(supported_proposal_data: dict[str, Any]) -> None:
    raw = _batch(supported_proposal_data)
    utf8: Any = raw.encode("utf-8")

    assert parse_proposal_json(utf8).findings[0].claim_id == "claim-1"
    for encoding in ("utf-16", "utf-32", "utf-8-sig"):
        encoded: Any = raw.encode(encoding)
        with pytest.raises(ProposalParseError, match="not valid JSON"):
            parse_proposal_json(encoded)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("claim_start", "true"),
        ("claim_start", "1.0"),
        ("claim_start", "1e0"),
        ("claim_start", '"0"'),
        ("claim_start", "-1"),
        ("claim_end", "false"),
        ("evidence_start", "0.0"),
        ("evidence_end", '"28"'),
        ("evidence_end", "-28"),
    ],
)
def test_offsets_must_be_non_negative_json_integers(
    field: str,
    value: str,
    supported_proposal_data: dict[str, Any],
) -> None:
    supported_proposal_data[field] = "__PLACEHOLDER__"
    raw = _batch(supported_proposal_data).replace('"__PLACEHOLDER__"', value)

    with pytest.raises(ProposalParseError, match="strict public schema"):
        parse_proposal_json(raw)


def test_schema_error_names_the_location_without_input_values(
    supported_proposal_data: dict[str, Any],
) -> None:
    supported_proposal_data["claim_start"] = True
    supported_proposal_data["proposed_relation"] = "UNTRUSTED-RELATION"

    with pytest.raises(ProposalParseError) as exc_info:
        parse_proposal_json(_batch(supported_proposal_data))

    message = str(exc_info.value)
    assert message.startswith(
        "malformed_proposal: Proposal JSON does not conform to the strict public "
        "schema: findings.0.claim_start: Input should be a valid integer; "
        "findings.0.proposed_relation: Input should be 'supported'"
    )
    assert "UNTRUSTED-RELATION" not in message


def test_very_large_offsets_are_accepted_by_the_schema_and_fail_the_guard(
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    supported_proposal_data["evidence_end"] = 10**30
    batch = parse_proposal_json(_batch(supported_proposal_data))

    finding = validate_finding(inspection_input, batch.findings[0])

    assert batch.findings[0].evidence_end == 10**30
    assert finding.reportable_relation is None
    assert finding.evidence_span_verified is False
