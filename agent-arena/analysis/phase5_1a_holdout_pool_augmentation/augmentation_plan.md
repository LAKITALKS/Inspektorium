# Phase 5.1a — Holdout Pool Augmentation Plan (frozen before candidate access)

**created (UTC):** 2026-08-02T20:00:59Z · **source_commit:** f8efe474d3068b7fbc4d149d9be1816b12b1e9cd · **source_tag:** v0.8.11-final-revalidation-results
**phase_designation:** phase5_1a_minimal_holdout_pool_augmentation
**algorithm_version:** holdout_pool_augment_v1
**deterministic_seed:** `agentarena-phase5.1a-augmentation-v1|f8efe474d3068b7fbc4d149d9be1816b12b1e9cd`

## Required approved packet additions
- correlation_vs_causation: **1** · mechanism_vs_evidence: **2** · (solid/overclaim: none)
- Selection from **existing active non-blind cases only**; no new external evidence; no
  model-performance variable; no manual swaps; candidates processed in deterministic rank order;
  a candidate skipped only for a documented packet-suitability failure; then the next ranked
  candidate for that label is processed. Exactly three must ultimately pass. New packets require
  curator approval and remain **holdout candidates only** — no holdout selection/freeze, no model
  evaluation. Gold and taxonomy remain unchanged.
- New blind IDs to assign (verified unused): **BIAA-021, BIAA-022, BIAA-023**.

## Candidate-pool eligibility rules (STEP 4) — a case enters only if ALL hold
1 active · 2 not retired · 3 not development-only · 4 not holdout-ineligible · 5 not BIAA-007/BIAA-019
· 6 no existing approved annotator-facing blind packet · 7 gold ∈ {correlation_vs_causation,
mechanism_vs_evidence} · 8 source YAML + gold record exist with stable hashes · 9 not an exact
duplicate of an approved BIAA case · 10 not an unresolved near-duplicate that would distort the pool
· 11 committed source material sufficient to build a packet without web research or new evidence.
No model results / correctness / confidence / disagreement / difficulty / attractiveness.

Ranking: candidate_key = canonical_case_id + "|" + source_yaml_sha256 + "|" + gold_record_sha256;
hash = SHA-256(seed + "|" + gold_label + "|" + candidate_key); sort ascending per label.

## Packet-suitability rules (STEP 5) — a candidate passes only if ALL hold
1 exactly one concrete public claim isolable · 2 claim in committed source material · 3 verbatim or
only identity-placeholder substitutions · 4 explicit unambiguous source voice · 5 evidence context
independently evaluable · 6 evidence supports present gold rationale · 7 no new evidence required ·
8 gold label unchanged · 9 no synthetic multi-speaker claim · 10 anonymizable without materially
changing the forensic issue · 11 no answer leakage needed · 12 not an exact/near-duplicate of an
approved packet. A candidate FAILS on any of: no single authoritative claim; needs new research;
anonymization changes meaning; ambiguous source voice; incomplete evidence; gold would change;
synthetic combination needed; answer leakage; material duplication.

## FAIL-STOP
If fewer than the required number pass for either label: no partial approval; preserve audits;
report the deficient label; stop for curator decision; do not begin Phase 5.1.

No candidate identity or predicted selection appears in this plan.
