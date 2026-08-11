"""Report assembly and deterministic rendering tests."""

from __future__ import annotations

import json
from typing import Any

from inspektorium.core.inspection import inspect_proposals
from inspektorium.core.models import InspectionInput, ProposalBatch, ProposedFinding
from inspektorium.report import render_json, render_markdown


def _batch(data: dict[str, Any]) -> ProposalBatch:
    return ProposalBatch(findings=(ProposedFinding.model_validate(data),))


def test_json_and_markdown_are_byte_stable(
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    report = inspect_proposals(inspection_input, _batch(supported_proposal_data))

    assert render_json(report) == render_json(report)
    assert render_markdown(report) == render_markdown(report)


def test_fabricated_quote_failure_survives_both_renderers(
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    supported_proposal_data.update(
        evidence_quote="The blue door opens at nine.",
        evidence_end=28,
    )
    report = inspect_proposals(inspection_input, _batch(supported_proposal_data))
    json_text = render_json(report)
    markdown = render_markdown(report)

    parsed = json.loads(json_text)
    assert parsed["findings"][0]["reportable_relation"] is None
    assert parsed["findings"][0]["evidence_quote"].endswith("nine.")
    assert "evidence_span_mismatch" in json_text
    assert "not citation-validated" in markdown
    assert "## Validation Warnings" in markdown
    assert "evidence_span_mismatch" in markdown
    assert "at noon" not in markdown.split("Proposed quotation", 1)[1]


def test_report_has_no_global_score_field(
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    report = inspect_proposals(inspection_input, _batch(supported_proposal_data))
    parsed = json.loads(render_json(report))

    assert "score" not in parsed
    assert "Global score: not produced" in render_markdown(report)


def test_not_established_language_does_not_claim_deterministic_proof(
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    supported_proposal_data.update(
        proposed_relation="not_established",
        source_id=None,
        evidence_quote=None,
        evidence_start=None,
        evidence_end=None,
        evidence_sufficiency="insufficient",
    )
    markdown = render_markdown(
        inspect_proposals(inspection_input, _batch(supported_proposal_data))
    )

    assert "Proposed relationship (evaluator judgment)" in markdown
    assert (
        "Citation validation:** not performed — no citation required or supplied "
        "for this proposal"
    ) in markdown
    assert (
        "Deterministic guard:** `passed` (claim span and structure only; no "
        "citation check performed)"
    ) in markdown
    assert "exact source quotation confirmed" not in markdown
    assert "semantically verified" not in markdown
