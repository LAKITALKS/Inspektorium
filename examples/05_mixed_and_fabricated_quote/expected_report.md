# Inspection Report

## Summary

- Claims inspected: 3
- Relationships allowed to remain reportable: 2
- Citations with an exact text and offset match: 1
- Deterministic validation failures: 1
- Global score: not produced

Evaluator relationships are semantic proposals. Deterministic validation
only checks canonical claim text, source identifiers, quotation text, and
offsets.

**Display note:** Text that comes from the evaluator, the answer, or the
sources is shown as data. Markdown and HTML characters in it are escaped.
Characters of the Unicode categories Cc, Cf, Cs, Zl and Zp, such as control
characters, bidirectional controls, zero-width joiners and line separators,
are shown as ⟦U+XXXX⟧ markers, as are code points not assigned in the
Unicode database of the running Python (category Cn); only a line feed
inside a quotation is shown as a line break. The brackets ⟦ and ⟧ in
this text and the at sign (U+0040) are also shown as markers, preventing
e-mail autolinks. In consecutive runs of nonspacing or enclosing marks
(Mn or Me), only the first four stay raw; the fifth and later characters
are marked. This includes variation selectors and does not guarantee visual
integrity in every font or viewer. Other invisible characters outside these
categories are not marked. The JSON report keeps the exact characters.

## Findings

### Finding 1: `claim-1`

**Atomic claim:** Northbridge Library is open on Saturdays.

- **Answer span:** `[0:41)`
- **Claim span check:** exact
- **Proposed relationship (evaluator judgment):** `supported`
- **Reportable proposed relationship:** `supported`
- **Deterministic guard:** `passed`
- **Citation text and offset check:** exact match (not a check of meaning)
- **Evidence sufficiency (evaluator judgment):** `sufficient`
- **Evaluator certainty:** `high`
- **Rationale (evaluator-generated):** The guide directly states that the library opens on Saturdays.

**Proposed quotation — exact text and offset match (not a check of meaning):**

> Northbridge Library is open on Saturdays from 10 a\.m. to 2 p\.m.

- **Proposed source:** `northbridge-guide`
- **Proposed offsets:** `[0:63)`

### Finding 2: `claim-2`

**Atomic claim:** It closes at 8 p\.m. on weekdays.

- **Answer span:** `[42:74)`
- **Claim span check:** exact
- **Proposed relationship (evaluator judgment):** `supported`
- **Reportable proposed relationship:** None — deterministic guard failed
- **Deterministic guard:** `failed`
- **Citation text and offset check:** no exact match
- **Evidence sufficiency (evaluator judgment):** `sufficient`
- **Evaluator certainty:** `high`
- **Rationale (evaluator-generated):** The proposed quotation appears to state the same weekday closing time.

**Proposed quotation — no exact text and offset match:**

> On weekdays, the library closes at 8 p\.m.

- **Proposed source:** `northbridge-guide`
- **Proposed offsets:** `[64:105)`

### Finding 3: `claim-3`

**Atomic claim:** It opened in 1998.

- **Answer span:** `[75:93)`
- **Claim span check:** exact
- **Proposed relationship (evaluator judgment):** `not_established`
- **Reportable proposed relationship:** `not_established`
- **Deterministic guard:** `passed` (claim span and structure only; no citation check performed)
- **Citation text and offset check:** not performed — no citation required or supplied for this proposal
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
