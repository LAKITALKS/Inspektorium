"""Deterministic claim, citation, and reportability guard tests."""

from __future__ import annotations

from typing import Any

import pytest

from inspektorium.core.models import InspectionInput, ProposedFinding
from inspektorium.core.relations import DeterministicValidationStatus, EvidenceRelation
from inspektorium.core.validation import validate_finding


def _proposal(data: dict[str, Any], **changes: Any) -> ProposedFinding:
    return ProposedFinding.model_validate({**data, **changes})


def test_exact_claim_and_quote_at_offset_zero_pass(
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    result = validate_finding(
        inspection_input,
        _proposal(supported_proposal_data),
    )

    assert result.claim_span_verified is True
    assert result.evidence_span_verified is True
    assert (
        result.deterministic_validation_status is DeterministicValidationStatus.PASSED
    )
    assert result.reportable_relation is EvidenceRelation.SUPPORTED


def test_claim_mismatch_blocks_reportability(
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    result = validate_finding(
        inspection_input,
        _proposal(supported_proposal_data, claim_start=1, claim_end=29),
    )

    assert result.claim_span_verified is False
    assert result.reportable_relation is None
    assert result.validation_issues[0].code.value == "claim_span_mismatch"


def test_claim_at_answer_end_uses_half_open_character_offsets(
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    proposal = _proposal(
        supported_proposal_data,
        claim_id="claim-end",
        claim_text="The blue door closes at six.",
        claim_start=29,
        claim_end=len(inspection_input.answer.text),
        proposed_relation="contradicted",
        evidence_quote="The blue door closes at five.",
        evidence_start=29,
        evidence_end=len(inspection_input.sources[0].text),
    )

    result = validate_finding(inspection_input, proposal)

    assert result.claim_span_verified is True
    assert result.evidence_span_verified is True
    assert result.reportable_relation is EvidenceRelation.CONTRADICTED


def test_repeated_text_uses_the_explicit_offsets(
    supported_proposal_data: dict[str, Any],
) -> None:
    input_data = InspectionInput.model_validate(
        {
            "answer": {"text": "Bell rings. Bell rings."},
            "sources": [{"source_id": "notice", "text": "Bell rings. Bell rings."}],
        }
    )
    proposal = _proposal(
        supported_proposal_data,
        claim_text="Bell rings.",
        claim_start=12,
        claim_end=23,
        source_id="notice",
        evidence_quote="Bell rings.",
        evidence_start=12,
        evidence_end=23,
    )

    result = validate_finding(input_data, proposal)

    assert result.claim_span_verified is True
    assert result.evidence_span_verified is True


def test_quote_at_source_end_passes(
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    proposal = _proposal(
        supported_proposal_data,
        claim_text="The blue door closes at six.",
        claim_start=29,
        claim_end=58,
        proposed_relation="contradicted",
        evidence_quote="The blue door closes at five.",
        evidence_start=29,
        evidence_end=58,
    )

    result = validate_finding(inspection_input, proposal)

    assert result.evidence_span_verified is True


def test_fabricated_quote_cannot_become_reportable_finding(
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    fabricated = _proposal(
        supported_proposal_data,
        evidence_quote="The blue door opens at nine.",
        evidence_end=28,
    )

    result = validate_finding(inspection_input, fabricated)

    assert result.proposed_relation is EvidenceRelation.SUPPORTED
    assert result.evidence_span_verified is False
    assert result.reportable_relation is None
    assert result.validation_issues[0].code.value == "evidence_span_mismatch"
    assert result.evidence_quote == "The blue door opens at nine."


def test_unknown_source_is_rejected(
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    result = validate_finding(
        inspection_input,
        _proposal(supported_proposal_data, source_id="missing"),
    )

    assert result.evidence_span_verified is False
    assert result.validation_issues[0].code.value == "unknown_source"


def test_wrong_offsets_are_not_searched_or_repaired(
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    result = validate_finding(
        inspection_input,
        _proposal(supported_proposal_data, evidence_start=1, evidence_end=29),
    )

    assert result.evidence_span_verified is False
    assert result.evidence_start == 1
    assert result.validation_issues[0].code.value == "evidence_span_mismatch"


def test_invalid_offset_range_has_explicit_code(
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    result = validate_finding(
        inspection_input,
        _proposal(supported_proposal_data, evidence_start=100, evidence_end=128),
    )

    assert result.validation_issues[0].code.value == "invalid_evidence_offsets"


def test_incomplete_reference_has_explicit_code(
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    result = validate_finding(
        inspection_input,
        _proposal(supported_proposal_data, evidence_end=None),
    )

    assert result.evidence_span_verified is False
    assert result.reportable_relation is None
    assert result.validation_issues[0].code.value == "incomplete_evidence_reference"


@pytest.mark.parametrize(
    "relation",
    ["supported", "contradicted", "attribution_mismatch"],
)
def test_mandatory_relations_require_valid_citation(
    relation: str,
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    result = validate_finding(
        inspection_input,
        _proposal(
            supported_proposal_data,
            proposed_relation=relation,
            source_id=None,
            evidence_quote=None,
            evidence_start=None,
            evidence_end=None,
        ),
    )

    assert result.reportable_relation is None
    assert result.evidence_span_verified is False


def test_not_established_is_reportable_without_invented_citation(
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    result = validate_finding(
        inspection_input,
        _proposal(
            supported_proposal_data,
            proposed_relation="not_established",
            source_id=None,
            evidence_quote=None,
            evidence_start=None,
            evidence_end=None,
            evidence_sufficiency="insufficient",
        ),
    )

    assert result.evidence_span_verified is None
    assert result.reportable_relation is EvidenceRelation.NOT_ESTABLISHED
    assert result.validation_issues == ()


def test_invalid_optional_citation_blocks_not_established(
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    result = validate_finding(
        inspection_input,
        _proposal(
            supported_proposal_data,
            proposed_relation="not_established",
            evidence_quote="Fabricated explanatory passage",
            evidence_end=29,
            evidence_sufficiency="insufficient",
        ),
    )

    assert result.evidence_span_verified is False
    assert result.reportable_relation is None
