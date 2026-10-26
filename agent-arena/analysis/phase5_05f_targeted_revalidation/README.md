# Phase 5.05f — Targeted Blind Revalidation (Preparation)

## Purpose
Prepare — but not yet execute — the targeted model revalidation approved after Phase 5.05e.
This phase produces the blind, opaque-identifier revalidation materials and freezes the
design and acceptance criteria. **No collection, no metrics, no live model calls occur here.**

## Scope
- Only **RVAL-001** and **RVAL-002** are being revalidated.
- The packets are derived from the approved **version-2** revisions (identifier-substituted
  copies; claim, evidence, caveats, structure, and `packet_version: 2` preserved exactly).
- External revalidators receive **only** annotator-facing material (README, taxonomy
  reference, the two RVAL packets, and a blank response sheet) — never any internal mapping,
  gold label, or curation record.
- **Three independent model families** are planned (Revalidator X / Y / Z); a two-family
  fallback has stricter, pre-specified acceptance criteria (see `revalidation_plan.md`).
- **No human review is executed.** Model revalidation is not a substitute for human review.

## Case lifecycle notes
- **BIAA-007** remains a **development-only borderline case** (independent human review
  deferred; see `deferred_scope_decision.md`); it stays holdout-ineligible.
- **BIAA-019** remains **retired** (excluded from default active loading; historically
  preserved).
- **No holdout has been selected or frozen.**

## What happens next (future steps, not this phase)
Independent collection of the three (or two) revalidator response sheets, raw-response
preservation, then result analysis against the frozen acceptance criteria. Passing packets
become eligible for later holdout consideration; failing packets return for a third
revalidator or further curation.

*This README contains no gold labels and no internal mapping.*
