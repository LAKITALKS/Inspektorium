# Inspection Report

## Summary

- Claims inspected: 3
- Relationships allowed to remain reportable: 2
- Exact citation spans confirmed: 1
- Deterministic validation failures: 1
- Global score: not produced

Evaluator relationships are semantic proposals. Deterministic validation
only checks canonical claim text, source identifiers, quotation text, and
offsets.

## Findings

### Finding 1: `claim-1`

- **Atomic claim:** Northbridge Library is open on Saturdays.
- **Answer span:** `[0:41)`
- **Claim span check:** exact
- **Proposed relationship (evaluator judgment):** `supported`
- **Reportable proposed relationship:** `supported`
- **Deterministic guard:** `passed`
- **Citation validation:** exact source quotation confirmed
- **Evidence sufficiency (evaluator judgment):** `sufficient`
- **Evaluator certainty:** `high`
- **Rationale (evaluator-generated):** The guide directly states that the library opens on Saturdays.

**Citation-validated source quotation:**

> Northbridge Library is open on Saturdays from 10 a.m. to 2 p.m.

- **Proposed source:** `northbridge-guide`
- **Proposed offsets:** `[0:63)`

### Finding 2: `claim-2`

- **Atomic claim:** It closes at 8 p.m. on weekdays.
- **Answer span:** `[42:74)`
- **Claim span check:** exact
- **Proposed relationship (evaluator judgment):** `supported`
- **Reportable proposed relationship:** None — deterministic guard failed
- **Deterministic guard:** `failed`
- **Citation validation:** citation failed exact validation
- **Evidence sufficiency (evaluator judgment):** `sufficient`
- **Evaluator certainty:** `high`
- **Rationale (evaluator-generated):** The proposed quotation appears to state the same weekday closing time.

**Proposed quotation — not citation-validated:**

> On weekdays, the library closes at 8 p.m.

- **Proposed source:** `northbridge-guide`
- **Proposed offsets:** `[64:105)`

### Finding 3: `claim-3`

- **Atomic claim:** It opened in 1998.
- **Answer span:** `[75:93)`
- **Claim span check:** exact
- **Proposed relationship (evaluator judgment):** `not_established`
- **Reportable proposed relationship:** `not_established`
- **Deterministic guard:** `passed`
- **Citation validation:** no citation proposed
- **Evidence sufficiency (evaluator judgment):** `insufficient`
- **Evaluator certainty:** `high`
- **Rationale (evaluator-generated):** The supplied guide does not establish an opening year.

## Validation Warnings

- **`claim-2` / `evidence_span_mismatch`:** The proposed quote does not equal the canonical source span at the proposed offsets.

## Scope and Limitations

This report compares evaluator proposals with the answer and sources supplied for this inspection.

- Citation validation confirms exact text and offsets, not semantic truth.
- Evaluator-proposed relationships remain qualitative judgments.
- The report does not assess source quality, completeness, or authority.
- The report does not determine whether relevant evidence exists elsewhere.
- The report does not provide domain-specific medical, legal, or safety conclusions.
- The report does not assign a global score or answer-level label.
