"""Restrained human-readable report rendering."""

from __future__ import annotations

from inspektorium.core.models import InspectionReport, ValidatedFinding


def _quoted(text: str) -> str:
    return "\n".join(f"> {line}" if line else ">" for line in text.split("\n"))


def _finding_markdown(index: int, finding: ValidatedFinding) -> list[str]:
    reportable = (
        f"`{finding.reportable_relation.value}`"
        if finding.reportable_relation is not None
        else "None — deterministic guard failed"
    )
    evidence_status = (
        "exact source quotation confirmed"
        if finding.evidence_span_verified is True
        else "citation failed exact validation"
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
        f"### Finding {index}: `{finding.claim_id}`",
        "",
        f"- **Atomic claim:** {finding.claim_text}",
        f"- **Answer span:** `[{finding.claim_start}:{finding.claim_end})`",
        f"- **Claim span check:** {claim_check}",
        f"- **Proposed relationship (evaluator judgment):** `{proposed}`",
        f"- **Reportable proposed relationship:** {reportable}",
        f"- **Deterministic guard:** {guard}",
        f"- **Citation validation:** {evidence_status}",
        f"- **Evidence sufficiency (evaluator judgment):** `{sufficiency}`",
        f"- **Evaluator certainty:** `{finding.evaluator_certainty.value}`",
        f"- **Rationale (evaluator-generated):** {finding.rationale}",
    ]
    if finding.evidence_quote is not None:
        heading = (
            "**Citation-validated source quotation:**"
            if finding.evidence_span_verified is True
            else "**Proposed quotation — not citation-validated:**"
        )
        lines.extend(["", heading, "", _quoted(finding.evidence_quote)])
    if finding.source_id is not None:
        offsets = f"[{finding.evidence_start}:{finding.evidence_end})"
        lines.extend(
            [
                "",
                f"- **Proposed source:** `{finding.source_id}`",
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
            f"- Exact citation spans confirmed: {citations}",
            f"- Deterministic validation failures: {failures_count}",
            "- Global score: not produced",
            "",
            "Evaluator relationships are semantic proposals. Deterministic validation",
            "only checks canonical claim text, source identifiers, quotation text, and",
            "offsets.",
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
            lines.append(
                f"- **`{finding.claim_id}` / `{issue.code.value}`:** {issue.message}"
            )
    else:
        lines.append("No deterministic validation warnings.")

    lines.extend(
        [
            "",
            "## Scope and Limitations",
            "",
            report.scope.statement,
            "",
        ]
    )
    lines.extend(f"- {limitation}" for limitation in report.scope.limitations)
    return "\n".join(lines) + "\n"


__all__ = ["render_markdown"]
