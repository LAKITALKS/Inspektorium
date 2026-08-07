"""Schema-focused tests for the Phase A data contracts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from inspektorium.core.models import (
    EvidenceRelation,
    InspectionInput,
    InspectionReport,
    ProposedFinding,
    ValidatedFinding,
)


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "examples" / "reference"


def reference_report_data() -> dict[str, object]:
    return json.loads((REFERENCE / "report.json").read_text(encoding="utf-8"))


def supported_proposal_data() -> dict[str, object]:
    return {
        "claim_id": "claim-1",
        "claim_text": "The door is blue.",
        "claim_start": 0,
        "claim_end": 17,
        "relation": "supported",
        "source_id": "source-1",
        "evidence_quote": "The door is blue.",
        "evidence_start": 4,
        "evidence_end": 21,
        "rationale": "The source states the claim directly.",
        "evidence_sufficiency": "sufficient",
        "evaluator_certainty": "high",
    }


def test_reference_input_conforms_to_schema() -> None:
    payload = (REFERENCE / "input.json").read_text(encoding="utf-8")

    inspection_input = InspectionInput.model_validate_json(payload)

    assert inspection_input.sources[0].source_id == "northbridge-guide"


def test_reference_report_conforms_to_schema() -> None:
    payload = (REFERENCE / "report.json").read_text(encoding="utf-8")

    report = InspectionReport.model_validate_json(payload)

    assert report.summary.claims_inspected == 3
    assert report.findings[1].validation_status.value == "failed"
    assert report.findings[1].verified_relation is None


def test_reference_files_and_fingerprints_are_internally_consistent() -> None:
    input_data = json.loads((REFERENCE / "input.json").read_text(encoding="utf-8"))
    report = InspectionReport.model_validate_json(
        (REFERENCE / "report.json").read_text(encoding="utf-8")
    )
    answer = input_data["answer"]["text"]
    source = input_data["sources"][0]["text"]
    source_id = input_data["sources"][0]["source_id"]

    assert (REFERENCE / "answer.md").read_text(encoding="utf-8").rstrip("\n") == answer
    assert (REFERENCE / "source.md").read_text(encoding="utf-8").rstrip("\n") == source
    assert hashlib.sha256(answer.encode("utf-8")).hexdigest() == report.fingerprints.answer_sha256
    assert hashlib.sha256(source.encode("utf-8")).hexdigest() == report.fingerprints.sources[0].sha256

    normalized_bundle = json.dumps(
        {
            "answer": answer,
            "sources": [{"source_id": source_id, "text": source}],
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    assert (
        hashlib.sha256(normalized_bundle.encode("utf-8")).hexdigest()
        == report.fingerprints.normalized_bundle_sha256
    )


def test_reference_fabricated_quote_is_visibly_rejected() -> None:
    input_data = json.loads((REFERENCE / "input.json").read_text(encoding="utf-8"))
    report = InspectionReport.model_validate_json(
        (REFERENCE / "report.json").read_text(encoding="utf-8")
    )
    finding = report.findings[1]
    source = input_data["sources"][0]["text"]

    actual_span = source[finding.evidence_start : finding.evidence_end]
    assert actual_span == "On weekdays, the library closes at 6 p.m."
    assert actual_span != finding.evidence_quote
    assert finding.evidence_span_verified is False
    assert finding.validation_status.value == "failed"
    assert finding.verified_relation is None


def test_unknown_relation_is_rejected() -> None:
    data = supported_proposal_data()
    data["relation"] = "plausible"

    with pytest.raises(ValidationError):
        ProposedFinding.model_validate(data)


@pytest.mark.parametrize("field", ["evidence_sufficiency", "evaluator_certainty"])
def test_qualitative_vocabularies_are_enforced(field: str) -> None:
    data = supported_proposal_data()
    data[field] = "0.95"

    with pytest.raises(ValidationError):
        ProposedFinding.model_validate(data)


def test_extra_fields_are_rejected() -> None:
    data = supported_proposal_data()
    data["score"] = 99

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        ProposedFinding.model_validate(data)


def test_evidence_relationship_requires_complete_reference() -> None:
    data = supported_proposal_data()
    for field in ("source_id", "evidence_quote", "evidence_start", "evidence_end"):
        data[field] = None

    with pytest.raises(ValidationError, match="requires an evidence reference"):
        ProposedFinding.model_validate(data)


def test_partial_evidence_reference_is_rejected() -> None:
    data = supported_proposal_data()
    data["evidence_end"] = None

    with pytest.raises(ValidationError, match="must be supplied together"):
        ProposedFinding.model_validate(data)


def test_not_established_can_omit_evidence() -> None:
    data = supported_proposal_data()
    data["relation"] = "not_established"
    data["evidence_sufficiency"] = "insufficient"
    for field in ("source_id", "evidence_quote", "evidence_start", "evidence_end"):
        data[field] = None

    finding = ProposedFinding.model_validate(data)

    assert finding.relation is EvidenceRelation.NOT_ESTABLISHED
    assert not finding.has_evidence_reference


def test_structural_span_length_mismatch_is_rejected() -> None:
    data = supported_proposal_data()
    data["claim_end"] = 16

    with pytest.raises(ValidationError, match="same length as claim_text"):
        ProposedFinding.model_validate(data)


def test_failed_validation_cannot_expose_verified_relation() -> None:
    data = supported_proposal_data()
    data.update(
        claim_span_verified=True,
        evidence_span_verified=False,
        validation_status="failed",
        verified_relation="supported",
    )

    with pytest.raises(ValidationError, match="cannot expose a verified relation"):
        ValidatedFinding.model_validate(data)


def test_passed_binding_requires_verified_evidence_span() -> None:
    data = supported_proposal_data()
    data.update(
        claim_span_verified=True,
        evidence_span_verified=False,
        validation_status="passed",
        verified_relation="supported",
    )

    with pytest.raises(ValidationError, match="requires a verified evidence span"):
        ValidatedFinding.model_validate(data)


def test_report_summary_must_match_findings() -> None:
    data = reference_report_data()
    data["summary"]["claims_inspected"] = 4  # type: ignore[index]

    with pytest.raises(ValidationError, match="summary counts"):
        InspectionReport.model_validate(data)


def test_every_failed_finding_requires_warning() -> None:
    data = reference_report_data()
    data["validation_warnings"] = []

    with pytest.raises(ValidationError, match="requires a validation warning"):
        InspectionReport.model_validate(data)


def test_source_ids_must_be_unique() -> None:
    payload = json.loads((REFERENCE / "input.json").read_text(encoding="utf-8"))
    payload["sources"].append(dict(payload["sources"][0]))

    with pytest.raises(ValidationError, match="source_id values must be unique"):
        InspectionInput.model_validate(payload)


def test_json_schema_has_no_score_field() -> None:
    schema_text = json.dumps(InspectionReport.model_json_schema())

    assert '"score"' not in schema_text
