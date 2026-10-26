# Inspection Report

## Summary

- Claims inspected: 1
- Relationships allowed to remain reportable: 1
- Citations with an exact text and offset match: 1
- Deterministic validation failures: 0
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

**Atomic claim:** The Lumen desk lamp uses replaceable batteries.

- **Answer span:** `[0:47)`
- **Claim span check:** exact
- **Proposed relationship (evaluator judgment):** `contradicted`
- **Reportable proposed relationship:** `contradicted`
- **Deterministic guard:** `passed`
- **Citation text and offset check:** exact match (not a check of meaning)
- **Evidence sufficiency (evaluator judgment):** `sufficient`
- **Evaluator certainty:** `high`
- **Rationale (evaluator-generated):** The manual describes an internal rechargeable battery and explicitly excludes replaceable batteries.

**Proposed quotation — exact text and offset match (not a check of meaning):**

> The lamp has a built-in rechargeable battery and does not accept replaceable batteries.

- **Proposed source:** `lumen-manual`
- **Proposed offsets:** `[24:111)`

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
