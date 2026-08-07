# Inspection Report

**Generated:** 2026-08-07 00:00:00 UTC  
**Answer SHA-256:** `78903e48852139ba081f1498bea508ea95934f3d8456380144fb80e4c04cf0d1`  
**Input bundle SHA-256:** `9c4d165c8bd2ce4133b82cac10997aae4d52a6f737bc7dc887aa3ac02e10a5ad`

## Summary

Three claims were inspected. One evidence binding passed deterministic
validation. One proposed evidence reference failed validation. No overall score
or answer-level label was produced.

## Claims

### Claim 1

**Claim:** Northbridge Library is open on Saturdays.  
**Answer span:** `[0:41)` — verified  
**Proposed relationship:** `supported`  
**Verified relationship:** `supported`  
**Evidence status:** Passed deterministic validation  
**Verified source quotation:**

> Northbridge Library is open on Saturdays from 10 a.m. to 2 p.m.

**Source reference:** `northbridge-guide[0:63)`  
**Source SHA-256:** `bfed0af89b8740175fba4cd45ee4a5d4bca275044adcc4b16875b388e27b6d18`  
**Evidence sufficiency:** `sufficient`  
**Evaluator certainty:** `high`  
**Rationale:** The source directly states that the library opens on Saturdays
and adds its hours.

### Claim 2

**Claim:** It closes at 8 p.m. on weekdays.  
**Answer span:** `[42:74)` — verified  
**Proposed relationship:** `supported`  
**Verified relationship:** None — validation failed  
**Evidence status:** **Failed deterministic validation**  
**Proposed, unverified quotation:**

> On weekdays, the library closes at 8 p.m.

**Proposed source reference:** `northbridge-guide[64:105)`  
**Evidence sufficiency:** `sufficient`  
**Evaluator certainty:** `high`  
**Rationale:** The proposed quotation appears to state the same weekday closing
time as the answer.

The proposed quotation is not presented as verified evidence. At the stated
offsets, the source says `6 p.m.`, not `8 p.m.` Inspektorium does not repair the
quotation or silently select a different passage.

### Claim 3

**Claim:** It opened in 1998.  
**Answer span:** `[75:93)` — verified  
**Proposed relationship:** `not_established`  
**Verified relationship:** `not_established`  
**Evidence status:** No quotation required or proposed  
**Evidence sufficiency:** `insufficient`  
**Evaluator certainty:** `high`  
**Rationale:** The supplied source explicitly provides no opening year, so the
source set does not establish this claim.

## Validation Warnings

- **Claim 2 — `evidence_quote_mismatch`:** The proposed evidence quote does not
  equal `source[64:105]`. The source span says `6 p.m.`; the proposal says
  `8 p.m.` No replacement quotation was selected.

## Scope

This report evaluates relationships between the inspected answer and the source
supplied with this inspection. It does not establish truth beyond that source,
judge whether the source is accurate or complete, determine whether evidence
exists elsewhere, make domain-specific medical, legal, or safety judgments, or
assign an overall score or answer-level label.

