# Phase 5.1a — Minimal Holdout Pool Augmentation

## Why this phase was necessary
The Phase 5.1 holdout-selection preflight correctly triggered its fail-stop rule: the approved
blind-packet candidate pool had fewer than four eligible cases for two labels — **correlation_vs_causation (3)** and **mechanism_vs_evidence (2)** — below the authorized four-per-label balanced design.

## What this phase did
- Deterministically selected candidates from **existing active non-blind cases** (frozen seed +
  hash ranking; no model-performance inputs, no manual swaps).
- Created exactly **three new approved blind packets** — one correlation_vs_causation and two
  mechanism_vs_evidence — under new opaque blind IDs (BIAA-021, BIAA-022, BIAA-023), each isolating
  exactly one evaluated claim from committed source material.
- Added **no new evidence**; changed **no gold label** and **no taxonomy**; performed **no holdout
  selection or freeze** and **no model evaluation**.

## Result
The approved holdout-candidate pool now has ≥4 cases per label (solid 5, overclaim 8,
correlation_vs_causation 4, mechanism_vs_evidence 4). The three new cases are **holdout candidates
only** — not selected. **Phase 5.1 must be rerun from a fresh checkpoint**, ranking the complete
eligible pool anew with no manual preference for the newly created cases.

*(Per-case gold labels are recorded only in `internal_only/`, following the existing blind-packet
convention; the annotator-facing packets contain no gold labels.)*
