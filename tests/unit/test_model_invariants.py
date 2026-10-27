"""Direct construction tests for every model invariant error branch.

Each invalid object must fail with exactly one, specific rule violation, so a
test cannot pass because some unrelated rule happened to reject the input.
"""

from __future__ import annotations

import itertools
import json
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta, timezone, tzinfo
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel, ValidationError

from inspektorium.core.inspection import SCOPE_NOTICE, inspect_proposals
from inspektorium.core.models import (
    InputFingerprints,
    InspectionInput,
    InspectionReport,
    ProposedFinding,
    ReportSummary,
    ValidatedFinding,
    ValidationIssue,
)
from inspektorium.core.relations import (
    DeterministicValidationStatus,
    EvidenceRelation,
    ValidationIssueCode,
)
from inspektorium.core.validation import validate_finding
from inspektorium.providers.parsing import parse_proposal_json
from inspektorium.report.json_report import render_json

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "examples" / "inspect"
CLAIM = "The blue door opens at noon."
NO_CITATION: dict[str, Any] = {
    "source_id": None,
    "evidence_quote": None,
    "evidence_start": None,
    "evidence_end": None,
}
ISSUE: dict[str, Any] = {
    "code": "claim_span_mismatch",
    "message": "The claim text does not equal the canonical answer span.",
}
OFFSET_FIELDS = ("claim_start", "claim_end", "evidence_start", "evidence_end")


def _proposal(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "claim_id": "claim-1",
        "claim_text": CLAIM,
        "claim_start": 0,
        "claim_end": 28,
        "proposed_relation": "supported",
        "source_id": "manual",
        "evidence_quote": CLAIM,
        "evidence_start": 0,
        "evidence_end": 28,
        "rationale": "The manual states the same opening time.",
        "evidence_sufficiency": "sufficient",
        "evaluator_certainty": "high",
    }
    data.update(overrides)
    return data


def _finding(**overrides: Any) -> dict[str, Any]:
    """A valid, passed, reportable supported finding unless overridden."""

    data = _proposal()
    data.update(
        claim_span_verified=True,
        evidence_span_verified=True,
        deterministic_validation_status="passed",
        reportable_relation="supported",
        validation_issues=[],
    )
    data.update(overrides)
    return data


def _failed(**overrides: Any) -> dict[str, Any]:
    data = _finding(
        deterministic_validation_status="failed",
        reportable_relation=None,
        validation_issues=[ISSUE],
    )
    data.update(overrides)
    return data


def _rule_violation(model: type[BaseModel], data: dict[str, Any]) -> str:
    """Return the one model-level rule message that rejected ``data``."""

    with pytest.raises(ValidationError) as exc_info:
        model.model_validate(data)
    errors = exc_info.value.errors()
    assert len(errors) == 1, errors
    assert errors[0]["type"] == "value_error"
    assert errors[0]["loc"] == ()
    message = errors[0]["msg"]
    assert message.startswith("Value error, ")
    return message.removeprefix("Value error, ")


def _field_error(model: type[BaseModel], data: dict[str, Any]) -> tuple[Any, ...]:
    with pytest.raises(ValidationError) as exc_info:
        model.model_validate(data)
    errors = exc_info.value.errors()
    assert len(errors) == 1, errors
    return (errors[0]["loc"], errors[0]["type"], errors[0]["msg"])


# --- ValidatedFinding: valid combinations -----------------------------------


@pytest.mark.parametrize(
    "data",
    [
        pytest.param(_finding(), id="passed-supported-with-citation"),
        pytest.param(
            _finding(
                proposed_relation="not_established",
                reportable_relation="not_established",
                evidence_span_verified=None,
                **NO_CITATION,
            ),
            id="passed-not-established-without-citation",
        ),
        pytest.param(
            _finding(
                proposed_relation="not_established",
                reportable_relation="not_established",
            ),
            id="passed-not-established-with-exact-optional-citation",
        ),
        pytest.param(
            _failed(evidence_span_verified=False, **NO_CITATION),
            id="failed-missing-required-citation",
        ),
        pytest.param(
            _failed(claim_span_verified=False), id="failed-claim-span-mismatch"
        ),
        pytest.param(
            _failed(
                proposed_relation="not_established",
                evidence_span_verified=None,
                claim_span_verified=False,
                **NO_CITATION,
            ),
            id="failed-not-established-without-citation",
        ),
    ],
)
def test_consistent_findings_are_accepted(data: dict[str, Any]) -> None:
    finding = ValidatedFinding.model_validate(data)

    assert ValidatedFinding.model_validate(finding.model_dump()) == finding


# --- ValidatedFinding: one test per error branch ------------------------------


@pytest.mark.parametrize(
    "data",
    [
        pytest.param(
            _failed(
                proposed_relation="supported",
                evidence_span_verified=True,
                **NO_CITATION,
            ),
            id="required-citation-missing-but-marked-verified",
        ),
        pytest.param(
            _failed(
                proposed_relation="not_established",
                evidence_span_verified=False,
                **NO_CITATION,
            ),
            id="optional-citation-absent-but-marked-failed",
        ),
        pytest.param(
            _finding(
                proposed_relation="not_established",
                reportable_relation="not_established",
                evidence_span_verified=True,
                **NO_CITATION,
            ),
            id="optional-citation-absent-but-marked-verified",
        ),
    ],
)
def test_evidence_status_must_be_null_without_citation(data: dict[str, Any]) -> None:
    assert _rule_violation(ValidatedFinding, data) == (
        "evidence span status must be null when no citation is proposed"
    )


@pytest.mark.parametrize(
    "data",
    [
        pytest.param(_failed(evidence_span_verified=None), id="complete-citation"),
        pytest.param(
            _failed(
                evidence_span_verified=None,
                **{**NO_CITATION, "source_id": "manual"},
            ),
            id="partial-citation",
        ),
    ],
)
def test_proposed_citation_requires_an_evidence_result(data: dict[str, Any]) -> None:
    assert _rule_violation(ValidatedFinding, data) == (
        "a proposed citation requires an evidence span result"
    )


def test_passed_guard_requires_exact_claim_span() -> None:
    data = _finding(claim_span_verified=False)

    assert _rule_violation(ValidatedFinding, data) == (
        "a passed guard requires an exact claim span"
    )


@pytest.mark.parametrize(
    "data",
    [
        pytest.param(
            _finding(evidence_span_verified=False), id="supported-citation-failed"
        ),
        pytest.param(
            _finding(
                proposed_relation="contradicted",
                reportable_relation="contradicted",
                evidence_span_verified=False,
                **NO_CITATION,
            ),
            id="contradicted-without-citation",
        ),
        pytest.param(
            _finding(
                proposed_relation="attribution_mismatch",
                reportable_relation="attribution_mismatch",
                evidence_span_verified=False,
                **NO_CITATION,
            ),
            id="attribution-mismatch-without-citation",
        ),
    ],
)
def test_passed_guard_requires_exact_citation_when_relation_needs_one(
    data: dict[str, Any],
) -> None:
    assert _rule_violation(ValidatedFinding, data) == (
        "this proposed relation requires an exact citation span"
    )


@pytest.mark.parametrize(
    "citation",
    [
        pytest.param({}, id="complete-but-failed"),
        pytest.param({"evidence_end": None}, id="incomplete"),
    ],
)
def test_passed_guard_requires_supplied_optional_citation_to_validate(
    citation: dict[str, Any],
) -> None:
    data = _finding(
        proposed_relation="not_established",
        reportable_relation="not_established",
        evidence_span_verified=False,
        **citation,
    )

    assert _rule_violation(ValidatedFinding, data) == (
        "a supplied optional citation must validate exactly"
    )


@pytest.mark.parametrize("reportable", [None, "contradicted", "not_established"])
def test_passed_guard_exposes_the_unchanged_proposed_relation(
    reportable: str | None,
) -> None:
    data = _finding(reportable_relation=reportable)

    assert _rule_violation(ValidatedFinding, data) == (
        "a passed guard exposes the unchanged proposed relation"
    )


def test_passed_guard_cannot_contain_validation_failures() -> None:
    data = _finding(validation_issues=[ISSUE])

    assert _rule_violation(ValidatedFinding, data) == (
        "a passed guard cannot contain validation failures"
    )


@pytest.mark.parametrize(
    "data",
    [
        pytest.param(_failed(reportable_relation="supported"), id="same-as-proposed"),
        pytest.param(
            _failed(reportable_relation="contradicted"), id="different-relation"
        ),
        pytest.param(
            _failed(
                claim_span_verified=False,
                evidence_span_verified=False,
                reportable_relation="supported",
            ),
            id="every-check-failed",
        ),
        pytest.param(
            _failed(
                proposed_relation="not_established",
                reportable_relation="not_established",
                evidence_span_verified=None,
                **NO_CITATION,
            ),
            id="not-established",
        ),
    ],
)
def test_failed_guard_cannot_expose_a_reportable_relation(
    data: dict[str, Any],
) -> None:
    assert _rule_violation(ValidatedFinding, data) == (
        "a failed guard cannot expose a reportable relation"
    )


def test_failed_guard_requires_at_least_one_validation_issue() -> None:
    data = _failed(validation_issues=[])

    assert _rule_violation(ValidatedFinding, data) == (
        "a failed guard requires at least one validation issue"
    )


# --- ValidatedFinding: a verified citation needs a complete reference ----------

EVIDENCE_FIELDS = ("source_id", "evidence_quote", "evidence_start", "evidence_end")
VERIFIED_CITATION_RULE = "a verified citation requires a complete evidence reference"
# Every way to drop one, two or three of the four evidence-reference fields.
INCOMPLETE_REFERENCES = [
    missing
    for size in (1, 2, 3)
    for missing in itertools.combinations(EVIDENCE_FIELDS, size)
]
INCOMPLETE_ISSUE: dict[str, Any] = {
    "code": "incomplete_evidence_reference",
    "message": "Evidence reference fields must be either all present or all null.",
}
# Findings whose complete reference is marked verified, in each guard outcome.
VERIFIED_STATES: dict[str, dict[str, Any]] = {
    "passed-supported": _finding(),
    "passed-not-established": _finding(
        proposed_relation="not_established",
        reportable_relation="not_established",
    ),
    "failed-claim-mismatch": _failed(claim_span_verified=False),
}


def _missing_id(missing: tuple[str, ...]) -> str:
    return "without-" + "-".join(missing)


def _without(data: dict[str, Any], missing: tuple[str, ...]) -> dict[str, Any]:
    return {**data, **dict.fromkeys(missing)}


@pytest.mark.parametrize("missing", INCOMPLETE_REFERENCES, ids=_missing_id)
@pytest.mark.parametrize("state", sorted(VERIFIED_STATES))
def test_verified_citation_requires_a_complete_evidence_reference(
    state: str, missing: tuple[str, ...]
) -> None:
    data = _without(VERIFIED_STATES[state], missing)

    assert data["evidence_span_verified"] is True
    assert _rule_violation(ValidatedFinding, data) == VERIFIED_CITATION_RULE


@pytest.mark.parametrize("state", sorted(VERIFIED_STATES))
def test_complete_evidence_reference_may_be_marked_verified(state: str) -> None:
    finding = ValidatedFinding.model_validate(VERIFIED_STATES[state])

    assert finding.has_complete_evidence_reference
    assert finding.evidence_span_verified is True
    assert ValidatedFinding.model_validate_json(finding.model_dump_json()) == finding


@pytest.mark.parametrize("missing", INCOMPLETE_REFERENCES, ids=_missing_id)
def test_incomplete_reference_marked_unverified_is_still_accepted(
    missing: tuple[str, ...],
) -> None:
    data = _without(
        _failed(evidence_span_verified=False, validation_issues=[INCOMPLETE_ISSUE]),
        missing,
    )

    finding = ValidatedFinding.model_validate(data)

    assert finding.evidence_span_verified is False
    assert 0 < finding.evidence_field_count < 4


def _pipeline_report_json(example_name: str) -> str:
    directory = EXAMPLES / example_name
    inspection_input = InspectionInput.model_validate_json(
        (directory / "input.json").read_text(encoding="utf-8")
    )
    proposals = parse_proposal_json(
        (directory / "proposals.json").read_text(encoding="utf-8")
    )
    return render_json(inspect_proposals(inspection_input, proposals))


@pytest.mark.parametrize("field", EVIDENCE_FIELDS)
@pytest.mark.parametrize(
    "example_name",
    [
        "01_supported",
        "02_contradicted",
        "04_attribution_mismatch",
        "05_mixed_and_fabricated_quote",
    ],
)
def test_report_round_trip_rejects_a_verified_citation_without_a_full_reference(
    example_name: str, field: str
) -> None:
    text = _pipeline_report_json(example_name)
    report = InspectionReport.model_validate_json(text)
    assert render_json(report) == text
    data = json.loads(text)
    index = next(
        position
        for position, finding in enumerate(data["findings"])
        if finding["evidence_span_verified"] is True
    )
    data["findings"][index][field] = None
    tampered = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)

    with pytest.raises(ValidationError) as exc_info:
        InspectionReport.model_validate_json(tampered)

    errors = exc_info.value.errors()
    assert len(errors) == 1, errors
    assert errors[0]["type"] == "value_error"
    assert errors[0]["loc"] == ("findings", index)
    assert errors[0]["msg"] == f"Value error, {VERIFIED_CITATION_RULE}"


# Values per evidence field that, combined, reach every evidence guard outcome:
# exact span, unknown source, invalid offsets and quote mismatch.
EVIDENCE_GRID: dict[str, tuple[Any, ...]] = {
    "source_id": ("manual", "unlisted"),
    "evidence_quote": (CLAIM, "The blue door opens at one!!"),
    "evidence_start": (0, 1000),
    "evidence_end": (28, 1001),
}


def _evidence_grid() -> Iterator[dict[str, Any]]:
    for mask in itertools.product((False, True), repeat=len(EVIDENCE_FIELDS)):
        present = [field for field, on in zip(EVIDENCE_FIELDS, mask, strict=True) if on]
        for values in itertools.product(*(EVIDENCE_GRID[field] for field in present)):
            evidence: dict[str, Any] = dict.fromkeys(EVIDENCE_FIELDS)
            evidence.update(zip(present, values, strict=True))
            yield evidence


@pytest.mark.parametrize("claim_start", [0, 1], ids=["claim-exact", "claim-shifted"])
@pytest.mark.parametrize("relation", list(EvidenceRelation), ids=str)
def test_validate_finding_marks_only_complete_references_verified(
    inspection_input: InspectionInput,
    relation: EvidenceRelation,
    claim_start: int,
) -> None:
    outcomes: set[tuple[int, bool | None, DeterministicValidationStatus]] = set()
    codes: set[ValidationIssueCode] = set()
    cases = 0
    for evidence in _evidence_grid():
        proposal = ProposedFinding.model_validate(
            _proposal(
                proposed_relation=relation.value,
                claim_start=claim_start,
                claim_end=claim_start + len(CLAIM),
                **evidence,
            )
        )

        finding = validate_finding(inspection_input, proposal)

        cases += 1
        if finding.evidence_span_verified is True:
            assert finding.has_complete_evidence_reference
        round_trip = ValidatedFinding.model_validate_json(finding.model_dump_json())
        assert round_trip == finding
        outcomes.add(
            (
                finding.evidence_field_count,
                finding.evidence_span_verified,
                finding.deterministic_validation_status,
            )
        )
        codes.update(issue.code for issue in finding.validation_issues)

    passed = DeterministicValidationStatus.PASSED
    failed = DeterministicValidationStatus.FAILED
    exact = passed if claim_start == 0 else failed
    without_citation = (
        (0, False, failed) if relation.requires_citation else (0, None, exact)
    )
    assert cases == 3**4
    assert outcomes == {
        without_citation,
        (1, False, failed),
        (2, False, failed),
        (3, False, failed),
        (4, False, failed),
        (4, True, exact),
    }
    assert codes == {
        ValidationIssueCode.UNKNOWN_SOURCE,
        ValidationIssueCode.INVALID_EVIDENCE_OFFSETS,
        ValidationIssueCode.EVIDENCE_SPAN_MISMATCH,
        ValidationIssueCode.INCOMPLETE_EVIDENCE_REFERENCE,
    } | ({ValidationIssueCode.CLAIM_SPAN_MISMATCH} if claim_start else set())


# --- Field types and boundaries -----------------------------------------------


@pytest.mark.parametrize("model", [ProposedFinding, ValidatedFinding])
@pytest.mark.parametrize("field", OFFSET_FIELDS)
@pytest.mark.parametrize(
    ("value", "error_type", "message"),
    [
        (True, "int_type", "Input should be a valid integer"),
        (False, "int_type", "Input should be a valid integer"),
        (1.0, "int_type", "Input should be a valid integer"),
        (0.0, "int_type", "Input should be a valid integer"),
        ("1", "int_type", "Input should be a valid integer"),
        (-1, "greater_than_equal", "Input should be greater than or equal to 0"),
        (
            -(10**30),
            "greater_than_equal",
            "Input should be greater than or equal to 0",
        ),
    ],
)
def test_offsets_reject_bool_float_string_and_negative_values(
    model: type[BaseModel],
    field: str,
    value: object,
    error_type: str,
    message: str,
) -> None:
    builder = _finding if model is ValidatedFinding else _proposal

    assert _field_error(model, builder(**{field: value})) == (
        (field,),
        error_type,
        message,
    )


@pytest.mark.parametrize("field", OFFSET_FIELDS)
@pytest.mark.parametrize("value", [0, 2**63, 10**30])
def test_offsets_accept_zero_and_very_large_integers(field: str, value: int) -> None:
    proposal = ProposedFinding.model_validate(_proposal(**{field: value}))

    assert getattr(proposal, field) == value
    assert type(getattr(proposal, field)) is int


@pytest.mark.parametrize("field", ["claim_start", "claim_end"])
def test_claim_offsets_are_not_nullable(field: str) -> None:
    loc, error_type, _ = _field_error(ProposedFinding, _proposal(**{field: None}))

    assert (loc, error_type) == ((field,), "int_type")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("claim_span_verified", 1),
        ("claim_span_verified", "true"),
        ("claim_span_verified", None),
        ("evidence_span_verified", 0),
        ("evidence_span_verified", "false"),
    ],
)
def test_guard_flags_are_strict_booleans(field: str, value: object) -> None:
    loc, error_type, _ = _field_error(ValidatedFinding, _finding(**{field: value}))

    assert (loc, error_type) == ((field,), "bool_type")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("deterministic_validation_status", "ok"),
        ("deterministic_validation_status", True),
        ("reportable_relation", "verified"),
        ("proposed_relation", "plausible"),
    ],
)
def test_guard_vocabularies_are_closed(field: str, value: object) -> None:
    loc, error_type, _ = _field_error(ValidatedFinding, _finding(**{field: value}))

    assert (loc, error_type) == ((field,), "enum")


@pytest.mark.parametrize("extra", ["score", "verified_relation", "guard_passed"])
def test_validated_finding_rejects_extra_fields(extra: str) -> None:
    loc, error_type, message = _field_error(ValidatedFinding, _finding(**{extra: 1}))

    assert (loc, error_type) == ((extra,), "extra_forbidden")
    assert message == "Extra inputs are not permitted"


@pytest.mark.parametrize(
    ("issue", "loc", "error_type"),
    [
        ({**ISSUE, "code": "semantic_mismatch"}, ("code",), "enum"),
        ({**ISSUE, "message": ""}, ("message",), "string_too_short"),
        ({**ISSUE, "severity": "high"}, ("severity",), "extra_forbidden"),
    ],
)
def test_validation_issue_contract(
    issue: dict[str, Any], loc: tuple[str, ...], error_type: str
) -> None:
    assert _field_error(ValidationIssue, issue)[:2] == (loc, error_type)


def test_findings_are_immutable_after_validation() -> None:
    finding = ValidatedFinding.model_validate(_failed())

    with pytest.raises(ValidationError, match="Instance is frozen"):
        finding.reportable_relation = finding.proposed_relation  # type: ignore[misc]


# --- InputFingerprints ----------------------------------------------------------


def _fingerprints(*source_ids: str) -> dict[str, Any]:
    return {
        "algorithm": "sha256",
        "answer_sha256": "0" * 64,
        "sources": [
            {"source_id": source_id, "sha256": "1" * 64} for source_id in source_ids
        ],
        "canonical_bundle_sha256": "2" * 64,
    }


def test_fingerprinted_sources_must_be_unique() -> None:
    assert _rule_violation(InputFingerprints, _fingerprints("a", "a")) == (
        "fingerprinted source_id values must be unique"
    )


def test_fingerprinted_sources_must_be_sorted() -> None:
    assert _rule_violation(InputFingerprints, _fingerprints("b", "a")) == (
        "fingerprinted sources must be ordered by source_id"
    )


@pytest.mark.parametrize(
    ("overrides", "loc", "error_type"),
    [
        ({"sources": []}, ("sources",), "too_short"),
        ({"algorithm": "md5"}, ("algorithm",), "literal_error"),
        ({"answer_sha256": "A" * 64}, ("answer_sha256",), "string_pattern_mismatch"),
        (
            {"canonical_bundle_sha256": "2" * 63},
            ("canonical_bundle_sha256",),
            "string_pattern_mismatch",
        ),
    ],
)
def test_fingerprint_fields_are_constrained(
    overrides: dict[str, Any], loc: tuple[str, ...], error_type: str
) -> None:
    data = {**_fingerprints("a"), **overrides}

    assert _field_error(InputFingerprints, data)[:2] == (loc, error_type)


# --- InspectionReport -----------------------------------------------------------


def _summary(
    claims: int, reportable: int, verified: int, failures: int
) -> dict[str, int]:
    return {
        "claims_inspected": claims,
        "reportable_findings": reportable,
        "citation_spans_verified": verified,
        "validation_failures": failures,
    }


def _report(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "generated_at": None,
        "fingerprints": _fingerprints("manual", "notice"),
        "summary": _summary(1, 1, 1, 0),
        "findings": [_finding()],
        "scope": SCOPE_NOTICE.model_dump(),
    }
    data.update(overrides)
    return data


class _NoOffset(tzinfo):
    def utcoffset(self, dt: datetime | None) -> timedelta | None:
        return None

    def dst(self, dt: datetime | None) -> timedelta | None:
        return None

    def tzname(self, dt: datetime | None) -> str | None:
        return None


@pytest.mark.parametrize(
    "generated_at",
    [
        None,
        datetime(2026, 10, 13, 12, 0, tzinfo=UTC),
        datetime(2026, 10, 13, 14, 0, tzinfo=timezone(timedelta(hours=2))),
        "2026-10-13T12:00:00Z",
    ],
)
def test_report_accepts_absent_or_timezone_aware_timestamps(
    generated_at: object,
) -> None:
    report = InspectionReport.model_validate(_report(generated_at=generated_at))

    assert report.generated_at is None or report.generated_at.utcoffset() is not None


@pytest.mark.parametrize(
    "generated_at",
    [
        datetime(2026, 10, 13, 12, 0),
        "2026-10-13T12:00:00",
        datetime(2026, 10, 13, 12, 0, tzinfo=_NoOffset()),
    ],
)
def test_report_rejects_naive_timestamps(generated_at: object) -> None:
    assert _rule_violation(InspectionReport, _report(generated_at=generated_at)) == (
        "generated_at must include a timezone offset"
    )


def test_report_rejects_duplicate_claim_ids() -> None:
    data = _report(findings=[_finding(), _finding()], summary=_summary(2, 2, 2, 0))

    assert _rule_violation(InspectionReport, data) == (
        "finding claim_id values must be unique"
    )


@pytest.mark.parametrize(
    "summary",
    [
        _summary(2, 1, 1, 0),
        _summary(1, 0, 1, 0),
        _summary(1, 1, 0, 0),
        _summary(1, 1, 1, 1),
        _summary(0, 0, 0, 0),
    ],
)
def test_report_summary_must_match_findings(summary: dict[str, int]) -> None:
    assert _rule_violation(InspectionReport, _report(summary=summary)) == (
        "summary counts must match report findings"
    )


def test_reportable_citation_must_name_a_fingerprinted_source() -> None:
    data = _report(findings=[_finding(source_id="unlisted")])

    assert _rule_violation(InspectionReport, data) == (
        "a reportable citation must name a fingerprinted source"
    )


@pytest.mark.parametrize(
    ("finding", "summary"),
    [
        pytest.param(
            _failed(source_id="unlisted", evidence_span_verified=False),
            _summary(1, 0, 0, 1),
            id="unreportable-unknown-source",
        ),
        pytest.param(
            _finding(
                proposed_relation="not_established",
                reportable_relation="not_established",
                evidence_span_verified=None,
                **NO_CITATION,
            ),
            _summary(1, 1, 0, 0),
            id="reportable-without-citation",
        ),
    ],
)
def test_report_source_rule_only_applies_to_reportable_citations(
    finding: dict[str, Any], summary: dict[str, int]
) -> None:
    report = InspectionReport.model_validate(
        _report(findings=[finding], summary=summary)
    )

    assert report.summary.claims_inspected == 1


@pytest.mark.parametrize(
    ("overrides", "loc", "error_type"),
    [
        ({"claims_inspected": -1}, ("claims_inspected",), "greater_than_equal"),
        ({"reportable_findings": True}, ("reportable_findings",), "int_type"),
        ({"validation_failures": 1.0}, ("validation_failures",), "int_type"),
    ],
)
def test_summary_counts_are_strict_non_negative_integers(
    overrides: dict[str, Any], loc: tuple[str, ...], error_type: str
) -> None:
    data = {**_summary(0, 0, 0, 0), **overrides}

    assert _field_error(ReportSummary, data)[:2] == (loc, error_type)


def test_report_rejects_extra_fields_and_other_schema_versions() -> None:
    assert _field_error(InspectionReport, _report(score=1))[:2] == (
        ("score",),
        "extra_forbidden",
    )
    assert _field_error(InspectionReport, _report(schema_version="0.2"))[:2] == (
        ("schema_version",),
        "literal_error",
    )


# --- Real pipeline output satisfies every invariant ---------------------------


@pytest.mark.parametrize(
    "example_name",
    sorted(path.name for path in EXAMPLES.iterdir() if path.is_dir()),
)
def test_example_reports_satisfy_the_invariants(example_name: str) -> None:
    directory = EXAMPLES / example_name
    expected = (directory / "expected_report.json").read_text(encoding="utf-8")
    report = InspectionReport.model_validate_json(expected)

    for finding in report.findings:
        assert ValidatedFinding.model_validate(finding.model_dump()) == finding
    assert InspectionReport.model_validate(json.loads(expected)) == report


def test_validate_finding_output_round_trips_through_the_model() -> None:
    directory = EXAMPLES / "05_mixed_and_fabricated_quote"
    inspection_input = InspectionInput.model_validate_json(
        (directory / "input.json").read_text(encoding="utf-8")
    )
    proposals = parse_proposal_json(
        (directory / "proposals.json").read_text(encoding="utf-8")
    )
    report = inspect_proposals(inspection_input, proposals)

    assert {finding.deterministic_validation_status for finding in report.findings} == {
        DeterministicValidationStatus.PASSED,
        DeterministicValidationStatus.FAILED,
    }
    assert InspectionReport.model_validate(report.model_dump()) == report
