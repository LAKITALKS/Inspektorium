# Phase 6.2 — Execution Contract (frozen by Phase 6.1; not yet executed)

**Governance:** Level 2 (result checkpoint). Phase 6.2 **must not begin** until the
gate in §5 is satisfied and the curator explicitly authorizes result generation.
Development material only; the sealed holdout is never opened.

---

## 1. Inputs (frozen)

- The **frozen calibration protocol / confidence semantics / abstention policy**
  (this directory), unchanged.
- The **curator-provisioned private development manifest** (27 cases; solid 8 /
  overclaim 15 / correlation 2 / mechanism 2) **and its private salt**, loaded only
  by the trusted private runner (§3), with its **salted commitment** verified against
  `development_pool_public_manifest.json`.
- Model predictions for the 27 dev cases: either reused recorded runs or, **only if
  separately authorized**, fresh live model calls. Each prediction must carry the
  **raw/flagged confidence** (VALID/MISSING/INVALID), never the legacy coerced 0.0.

## 2. Outputs (frozen)

1. Reliability table + diagram per model (**5 primary fixed bins**, per-bin `n`,
   mean confidence, empirical accuracy, absolute gap; 10-bin **sensitivity** view
   alongside; bins with `n < 5` not interpreted; empty bins visible).
2. **Brier (primary)** and ECE (secondary/descriptive) per model, each with `N` and
   the mandatory small-sample caveat.
3. Accuracy-by-confidence-range with Wilson intervals where `n ≥ 5`.
4. Risk–coverage curve + selective accuracy over the τ grid; abstention benefit
   **and** cost per point.
5. Per-label (macro, `n ≥ 5` only) and micro summaries; correlation/mechanism shown
   as flagged diagnostics (n = 2).
6. Separate strata blocks: clear (headline), borderline (divergence),
   development-only.
7. A **result manifest** binding every number to: the private-manifest salted
   commitment, code commit, parameters (bins, τ grid, min-`n`), seed. All outputs use
   **only anonymized DEV ids** — never canonical ids.

## 3. Trusted private runner (design; to be built in 6.2)

A runner that isolates canonical identities from all emitted artifacts:

- **loads** the private manifest from a curator-supplied path (outside Git);
  refuses paths under `internal_only/`, `research/…expansion_150/`, or the private
  holdout (reuse `packet_integrity.assert_path_allowed`).
- **verifies** the manifest against `private_manifest_schema` and that the **salted
  commitment** of (manifest, salt) equals the frozen public commitment; aborts on
  mismatch.
- **runs** calibration/abstention **only** on the 27 certified non-holdout cases.
- **keeps canonical identities in-memory only**; every written artifact is keyed by
  DEV id. A leakage guard asserts no canonical id / BIAA id appears in any output
  (reuse the `packet_integrity` contamination checks over emitted files).
- **never emits** the eligible complement, holdout identities, or the private
  mapping.

## 4. Acceptance criteria (frozen — Phase 6.2)

- A6.2-1 metrics computed exactly as pre-registered here, on the 27-case dev pool
  only; no metric/bin/threshold altered after seeing a value.
- A6.2-2 reliability diagram + ECE + Brier produced with `N`/per-bin `n` and result
  manifest; reproducible from the manifest + seed.
- A6.2-3 abstention evaluated via risk–coverage (benefit **and** cost); adopted only
  if the frozen conditional criterion holds, else reported "not demonstrated
  beneficial."
- A6.2-4 no holdout data used; no threshold tuned then reported as unbiased; all
  outputs anonymized (DEV ids only), leakage guard green.

## 5. Stop / gate conditions (frozen)

Phase 6.2 is **blocked** and must not start while any holds:
- the public commitment is still `PENDING_CURATOR_PROVISIONING`;
- the private manifest fails schema/aggregate validation or salted-commitment
  mismatch;
- any step would require holdout, `internal_only`, or the eligible-21 cases;
- live model calls are needed but not separately authorized;
- a metric/threshold would be chosen using the results it is later reported against.

Stop and report if, during 6.2, results tempt re-tuning of any frozen definition —
that is result-driven selection and is prohibited.

## 6. Explicit non-goals of Phase 6.2

No universal-superiority or product/performance claim; the 27-case development pool
and the (unopened) 16-case holdout are integrity/characterization instruments, not a
statistically strong basis for broad claims. Prompt-only comparison (6.4) stays
isolated until its own protocol is frozen.
