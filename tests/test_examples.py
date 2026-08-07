"""Byte-for-byte regression tests for all five offline examples."""

from __future__ import annotations

from pathlib import Path

import pytest

from inspektorium.core.inspection import inspect_proposals
from inspektorium.core.models import InspectionInput
from inspektorium.providers.parsing import parse_proposal_json
from inspektorium.report import render_json, render_markdown

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
EXAMPLE_NAMES = (
    "01_supported",
    "02_contradicted",
    "03_not_established",
    "04_attribution_mismatch",
    "05_mixed_and_fabricated_quote",
)


@pytest.mark.parametrize("example_name", EXAMPLE_NAMES)
def test_example_regenerates_expected_reports(example_name: str) -> None:
    directory = EXAMPLES / example_name
    inspection_input = InspectionInput.model_validate_json(
        (directory / "input.json").read_text(encoding="utf-8")
    )
    proposals = parse_proposal_json(
        (directory / "proposals.json").read_text(encoding="utf-8")
    )
    report = inspect_proposals(inspection_input, proposals)

    assert render_json(report) == (directory / "expected_report.json").read_text(
        encoding="utf-8"
    )
    assert render_markdown(report) == (directory / "expected_report.md").read_text(
        encoding="utf-8"
    )


def test_exactly_five_public_example_directories_exist() -> None:
    actual = tuple(sorted(path.name for path in EXAMPLES.iterdir() if path.is_dir()))

    assert actual == EXAMPLE_NAMES


def test_mixed_example_preserves_valid_finding_and_rejects_fabrication() -> None:
    directory = EXAMPLES / "05_mixed_and_fabricated_quote"
    report_json = (directory / "expected_report.json").read_text(encoding="utf-8")
    report_markdown = (directory / "expected_report.md").read_text(encoding="utf-8")

    assert '"reportable_relation": "supported"' in report_json
    assert '"reportable_relation": null' in report_json
    assert "evidence_span_mismatch" in report_json
    assert "Proposed quotation — not citation-validated" in report_markdown
