"""Tests for strict public schemas and semantic naming boundaries."""

from __future__ import annotations

import json
from typing import Any

import pytest
from pydantic import ValidationError

from inspektorium.core.models import InspectionInput, ProposalBatch, ProposedFinding


def test_extra_fields_are_rejected(supported_proposal_data: dict[str, Any]) -> None:
    supported_proposal_data["score"] = 99

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        ProposedFinding.model_validate(supported_proposal_data)


def test_unknown_relationship_is_rejected(
    supported_proposal_data: dict[str, Any],
) -> None:
    supported_proposal_data["proposed_relation"] = "plausible"

    with pytest.raises(ValidationError):
        ProposedFinding.model_validate(supported_proposal_data)


@pytest.mark.parametrize("field", ["evidence_sufficiency", "evaluator_certainty"])
def test_qualitative_vocabularies_are_enforced(
    field: str,
    supported_proposal_data: dict[str, Any],
) -> None:
    supported_proposal_data[field] = "0.95"

    with pytest.raises(ValidationError):
        ProposedFinding.model_validate(supported_proposal_data)


def test_negative_span_is_rejected_by_schema(
    supported_proposal_data: dict[str, Any],
) -> None:
    supported_proposal_data["claim_start"] = -1

    with pytest.raises(ValidationError):
        ProposedFinding.model_validate(supported_proposal_data)


def test_missing_evidence_field_is_parser_failure(
    supported_proposal_data: dict[str, Any],
) -> None:
    del supported_proposal_data["evidence_end"]

    with pytest.raises(ValidationError):
        ProposedFinding.model_validate(supported_proposal_data)


def test_nullable_evidence_fields_allow_visible_incomplete_reference(
    supported_proposal_data: dict[str, Any],
) -> None:
    supported_proposal_data["evidence_end"] = None

    proposal = ProposedFinding.model_validate(supported_proposal_data)

    assert proposal.evidence_field_count == 3
    assert not proposal.has_complete_evidence_reference


def test_duplicate_claim_ids_are_rejected(
    supported_proposal_data: dict[str, Any],
) -> None:
    proposal = ProposedFinding.model_validate(supported_proposal_data)

    with pytest.raises(ValidationError, match="claim_id values must be unique"):
        ProposalBatch(findings=(proposal, proposal))


def test_duplicate_source_ids_are_rejected() -> None:
    source = {"source_id": "manual", "text": "Text."}

    with pytest.raises(ValidationError, match="source_id values must be unique"):
        InspectionInput.model_validate(
            {
                "answer": {"text": "Answer."},
                "sources": [source, source],
            }
        )


def test_semantic_verification_field_cannot_return() -> None:
    schema = json.dumps(ProposalBatch.model_json_schema(), sort_keys=True)

    assert "proposed_relation" in schema
    assert "verified_relation" not in schema


def test_score_like_field_is_absent_from_schema() -> None:
    schema = json.dumps(ProposalBatch.model_json_schema(), sort_keys=True)

    assert '"score"' not in schema
