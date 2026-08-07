# Inspection Report

## Summary

- Claims inspected: 1
- Relationships allowed to remain reportable: 1
- Exact citation spans confirmed: 1
- Deterministic validation failures: 0
- Global score: not produced

Evaluator relationships are semantic proposals. Deterministic validation
only checks canonical claim text, source identifiers, quotation text, and
offsets.

## Findings

### Finding 1: `claim-1`

- **Atomic claim:** The Pine Street Museum says Tuesday admission is free.
- **Answer span:** `[0:54)`
- **Claim span check:** exact
- **Proposed relationship (evaluator judgment):** `attribution_mismatch`
- **Reportable proposed relationship:** `attribution_mismatch`
- **Deterministic guard:** `passed`
- **Citation validation:** exact source quotation confirmed
- **Evidence sufficiency (evaluator judgment):** `sufficient`
- **Evaluator certainty:** `high`
- **Rationale (evaluator-generated):** The answer attributes free Tuesday admission to the notice, but the notice says standard admission applies every day.

**Citation-validated source quotation:**

> The museum is open on Tuesdays, and standard admission applies every day.

- **Proposed source:** `museum-notice`
- **Proposed offsets:** `[35:108)`

## Validation Warnings

No deterministic validation warnings.

## Scope and Limitations

This report compares evaluator proposals with the answer and sources supplied for this inspection.

- Citation validation confirms exact text and offsets, not semantic truth.
- Evaluator-proposed relationships remain qualitative judgments.
- The report does not assess source quality, completeness, or authority.
- The report does not determine whether relevant evidence exists elsewhere.
- The report does not provide domain-specific medical, legal, or safety conclusions.
- The report does not assign a global score or answer-level label.
