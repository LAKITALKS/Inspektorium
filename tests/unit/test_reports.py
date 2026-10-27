"""Report assembly and deterministic rendering tests."""

from __future__ import annotations

import json
from datetime import UTC, datetime
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
    assert "Proposed quotation — no exact text and offset match:" in markdown
    assert "Citation text and offset check:** no exact match" in markdown
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
        "Citation text and offset check:** not performed — no citation required or "
        "supplied for this proposal"
    ) in markdown
    assert (
        "Deterministic guard:** `passed` (claim span and structure only; no "
        "citation check performed)"
    ) in markdown
    assert "exact match (not a check of meaning)" not in markdown
    assert "semantically verified" not in markdown


def test_citation_labels_describe_an_exact_text_and_offset_match_only(
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    failed = {
        **supported_proposal_data,
        "claim_id": "claim-2",
        "evidence_quote": "The blue door opens at nine.",
    }
    not_established = {
        **supported_proposal_data,
        "claim_id": "claim-3",
        "proposed_relation": "not_established",
        "source_id": None,
        "evidence_quote": None,
        "evidence_start": None,
        "evidence_end": None,
    }
    batch = ProposalBatch(
        findings=tuple(
            ProposedFinding.model_validate(data)
            for data in (supported_proposal_data, failed, not_established)
        )
    )
    markdown = render_markdown(inspect_proposals(inspection_input, batch))

    assert "- Citations with an exact text and offset match: 1" in markdown
    assert markdown.count("**Citation text and offset check:**") == 3
    assert (
        "- **Citation text and offset check:** exact match (not a check of meaning)"
    ) in markdown
    assert "- **Citation text and offset check:** no exact match" in markdown
    assert (
        "**Proposed quotation — exact text and offset match (not a check of meaning):**"
    ) in markdown
    assert "**Proposed quotation — no exact text and offset match:**" in markdown
    for retired in (
        "Citation-validated",
        "citation-validated",
        "Exact citation spans confirmed",
        "exact source quotation confirmed",
        "citation failed exact validation",
        "Citation validation:**",
    ):
        assert retired not in markdown


def test_markdown_states_the_display_convention_once(
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    markdown = render_markdown(
        inspect_proposals(inspection_input, _batch(supported_proposal_data))
    )
    summary = markdown.split("## Summary", 1)[1].split("## Findings", 1)[0]

    assert markdown.count("**Display note:**") == 1
    assert "**Display note:**" in summary
    note = " ".join(summary.split("**Display note:**", 1)[1].split())
    assert note == (
        "Text that comes from the evaluator, the answer, or the sources is shown "
        "as data. Markdown and HTML characters in it are escaped. Characters of "
        "the Unicode categories Cc, Cf, Cs, Zl and Zp, such as control characters, "
        "bidirectional controls, zero-width joiners and line separators, are shown "
        "as \N{MATHEMATICAL LEFT WHITE SQUARE BRACKET}U+XXXX"
        "\N{MATHEMATICAL RIGHT WHITE SQUARE BRACKET} markers, as are code points "
        "not assigned in the Unicode database of the running Python (category "
        "Cn); only a line feed inside a quotation is shown as a line break. The "
        "brackets "
        "\N{MATHEMATICAL LEFT WHITE SQUARE BRACKET} and "
        "\N{MATHEMATICAL RIGHT WHITE SQUARE BRACKET} in this text and the at sign "
        "(U+0040) are also shown as markers, preventing e-mail autolinks. In "
        "consecutive runs of nonspacing or enclosing marks (Mn or Me), only the "
        "first four stay raw; the fifth and later characters are marked. This "
        "includes variation selectors and does not guarantee visual integrity in "
        "every font or viewer. Other invisible characters outside these "
        "categories are not marked. The JSON report keeps the exact characters."
    )


def test_timestamp_and_empty_findings_render_with_fixed_structure(
    inspection_input: InspectionInput,
) -> None:
    report = inspect_proposals(
        inspection_input,
        ProposalBatch(findings=()),
        generated_at=datetime(2026, 10, 13, 12, 0, tzinfo=UTC),
    )
    markdown = render_markdown(report)

    assert "**Generated from explicit metadata:** `2026-10-13T12:00:00+00:00`" in (
        markdown
    )
    assert "No findings were proposed." in markdown
    assert "No deterministic validation warnings." in markdown
    headings = [line for line in markdown.splitlines() if line.startswith("#")]
    assert headings == [
        "# Inspection Report",
        "## Summary",
        "## Findings",
        "## Validation Warnings",
        "## Scope and Limitations",
    ]
