"""Restrained human-readable report rendering.

Host-generated structure (headings, labels and status lines) is written
directly. Every text value taken from the report object is embedded through
the context encoders in ``inspektorium.report.display``, so embedded text is
shown as data: it cannot add Markdown or HTML structure, and it cannot remove
later content from the rendered document or hide it with HTML or CSS.

Consecutive nonspacing or enclosing marks (Unicode categories Mn and Me) are
limited to four raw characters; later characters in each run become visible
markers. This bounds the displayed text property, not the rendering behaviour
of every font or viewer. The at sign is also marked to prevent e-mail autolinks.
"""

from __future__ import annotations

from inspektorium.core.models import InspectionReport, ValidatedFinding
from inspektorium.report.display import (
    MARKER_CLOSE,
    MARKER_OPEN,
    encode_identifier,
    encode_inline,
    encode_line,
    encode_quote,
)

_MARKER = f"{MARKER_OPEN}U+XXXX{MARKER_CLOSE}"
_BRACKETS = f"{MARKER_OPEN} and {MARKER_CLOSE}"
DISPLAY_NOTE = (
    "**Display note:** Text that comes from the evaluator, the answer, or the",
    "sources is shown as data. Markdown and HTML characters in it are escaped.",
    "Characters of the Unicode categories Cc, Cf, Cs, Zl and Zp, such as control",
    "characters, bidirectional controls, zero-width joiners and line separators,",
    f"are shown as {_MARKER} markers, as are code points not assigned in the",
    "Unicode database of the running Python (category Cn); only a line feed",
    f"inside a quotation is shown as a line break. The brackets {_BRACKETS} in",
    "this text and the at sign (U+0040) are also shown as markers, preventing",
    "e-mail autolinks. In consecutive runs of nonspacing or enclosing marks",
    "(Mn or Me), only the first four stay raw; the fifth and later characters",
    "are marked. This includes variation selectors and does not guarantee visual",
    "integrity in every font or viewer. Other invisible characters outside these",
    "categories are not marked. The JSON report keeps the exact characters.",
)


def _finding_markdown(index: int, finding: ValidatedFinding) -> list[str]:
    reportable = (
        f"`{finding.reportable_relation.value}`"
        if finding.reportable_relation is not None
        else "None — deterministic guard failed"
    )
    citation_check = (
        "exact match (not a check of meaning)"
        if finding.evidence_span_verified is True
        else "no exact match"
        if finding.evidence_span_verified is False
        else "not performed — no citation required or supplied for this proposal"
    )
    claim_check = "exact" if finding.claim_span_verified else "failed"
    proposed = finding.proposed_relation.value
    guard = f"`{finding.deterministic_validation_status.value}`"
    if finding.evidence_span_verified is None:
        guard += " (claim span and structure only; no citation check performed)"
    sufficiency = finding.evidence_sufficiency.value
    lines = [
        f"### Finding {index}: {encode_identifier(finding.claim_id)}",
        "",
        # A separate paragraph keeps claim ink away from the host-control list.
        f"**Atomic claim:** {encode_inline(finding.claim_text)}",
        "",
        f"- **Answer span:** `[{finding.claim_start}:{finding.claim_end})`",
        f"- **Claim span check:** {claim_check}",
        f"- **Proposed relationship (evaluator judgment):** `{proposed}`",
        f"- **Reportable proposed relationship:** {reportable}",
        f"- **Deterministic guard:** {guard}",
        f"- **Citation text and offset check:** {citation_check}",
        f"- **Evidence sufficiency (evaluator judgment):** `{sufficiency}`",
        f"- **Evaluator certainty:** `{finding.evaluator_certainty.value}`",
        f"- **Rationale (evaluator-generated):** {encode_inline(finding.rationale)}",
    ]
    if finding.evidence_quote is not None:
        heading = (
            "**Proposed quotation — exact text and offset match "
            "(not a check of meaning):**"
            if finding.evidence_span_verified is True
            else "**Proposed quotation — no exact text and offset match:**"
        )
        lines.extend(["", heading, "", encode_quote(finding.evidence_quote)])
    if finding.source_id is not None:
        offsets = f"[{finding.evidence_start}:{finding.evidence_end})"
        lines.extend(
            [
                "",
                f"- **Proposed source:** {encode_identifier(finding.source_id)}",
                f"- **Proposed offsets:** `{offsets}`",
            ]
        )
    return lines


def render_markdown(report: InspectionReport) -> str:
    """Render a deterministic report with explicit semantic/mechanical labels."""

    lines = ["# Inspection Report", ""]
    if report.generated_at is not None:
        generated_at = report.generated_at.isoformat()
        lines.extend(
            [
                f"**Generated from explicit metadata:** `{generated_at}`",
                "",
            ]
        )
    reportable = report.summary.reportable_findings
    citations = report.summary.citation_spans_verified
    failures_count = report.summary.validation_failures
    lines.extend(
        [
            "## Summary",
            "",
            f"- Claims inspected: {report.summary.claims_inspected}",
            f"- Relationships allowed to remain reportable: {reportable}",
            f"- Citations with an exact text and offset match: {citations}",
            f"- Deterministic validation failures: {failures_count}",
            "- Global score: not produced",
            "",
            "Evaluator relationships are semantic proposals. Deterministic validation",
            "only checks canonical claim text, source identifiers, quotation text, and",
            "offsets.",
            "",
            *DISPLAY_NOTE,
            "",
            "## Findings",
            "",
        ]
    )
    if report.findings:
        for index, finding in enumerate(report.findings, start=1):
            lines.extend(_finding_markdown(index, finding))
            lines.append("")
    else:
        lines.extend(["No findings were proposed.", ""])

    lines.extend(["## Validation Warnings", ""])
    failures = [
        (finding, issue)
        for finding in report.findings
        for issue in finding.validation_issues
    ]
    if failures:
        for finding, issue in failures:
            claim_id = encode_identifier(finding.claim_id)
            message = encode_inline(issue.message)
            lines.append(f"- **{claim_id} / `{issue.code.value}`:** {message}")
    else:
        lines.append("No deterministic validation warnings.")

    lines.extend(
        [
            "",
            "## Scope and Limitations",
            "",
            encode_line(report.scope.statement),
            "",
        ]
    )
    lines.extend(
        f"- {encode_line(limitation)}" for limitation in report.scope.limitations
    )
    return "\n".join(lines) + "\n"


__all__ = ["DISPLAY_NOTE", "render_markdown"]
