# Phase 6.2 — Startup

**Governance:** Level 2 methodology/evaluation **implementation** phase. Purpose:
build the reproducible, deterministic calibration & abstention machinery required to
evaluate the frozen 27-case development pool under the already-frozen Phase 6.1
protocol — **without generating any real results in this session**.

## Entry state (verified)
- HEAD at session start `cf65149` (provisioning checkpoint); Task A committed at
  `f9a7e28`; Phase-5 tag `v0.8.13` → `cfb78de` unchanged; no tags added.
- Development-pool public commitment: **provisioned** (salted-sha256; `assert_public_clean` = []).
- Isolation held: no access to the private manifest, salt, eligible/dev id rosters,
  `internal_only/`, or the sealed holdout.

## What this phase does
- Implements deterministic, offline tooling (`src/agent_arena/calibration.py`,
  reusing `confidence_validity.py`) that computes the frozen metrics from an
  **anonymized result envelope** — opaque `DEV-####` records **bound** to the tracked
  `manifest_id` + public salted commitment, with no canonical identity.
- Freezes the input/reporting contracts and acceptance criteria; the 8/15/2/2
  aggregate is a **gold**-label composition, never a prediction constraint.

## What this phase does NOT do (execution boundary)
- No live model calls; no paid APIs; **no real calibration results**.
- No trusted private run against the 27-case manifest (separately authorized later).
- No threshold/bin/cost tuning; no results file; no closeout claiming evaluation.
- Frozen Phase 6.1 methodology is not changed based on results.

## Preservation (frozen, carried into the tooling)
binary top-label Brier (primary) · 5 fixed reliability bins · ECE secondary ·
10-bin sensitivity only · VALID/MISSING/INVALID confidence (no 0.0 coercion) ·
clear/borderline/development-only strata · label `n=2` descriptive only ·
abstention as a costed trade-off.

## Deliverables
The nine `analysis/phase6_2_calibration/` documents, plus `calibration.py` and
`tests/test_calibration.py` (synthetic fixtures only). See
`implementation_inventory.md` and `phase6_2_preparation_status.md`.
