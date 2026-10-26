# Phase 6.1 — Handoff (do not start without explicit instruction)

**Entry point:** commit `3983b7fa39965917bc784095243a42b7497a6e21` (Phase 6.0
checkpoint) on branch `feat/case-library-run-harness`. **No tag.** Phase 5 baseline
remains `cfb78de` / `v0.8.13-phase5-closeout`.

**Phase 6.1 objective:** define confidence semantics and a **development-only**
calibration protocol. No model calls, no holdout, no results-driven choices.

## Required first action — Level-2 preparation checkpoint (before any number)
1. **Confidence-semantics spec.** Fix the numeric range/scale; the operational
   meaning of a value; and **non-silent** handling of missing/non-numeric
   confidence (must be flagged/excluded, never coerced to `0.0` and used as a real
   datum — see risk R-2). Keep model confidence distinct from the heuristic
   finding-confidence labels (`HIGH/MEDIUM/HEURISTIC`) — risk R-12.
2. **Development-pool freeze.** Define the pool **without any reference to holdout
   membership**, starting from the holdout-safe set `{active} \ {eligible-21}`
   (= 26 non-blind active + 1 dev-only), record borderline handling and per-label
   counts. This is the single most leakage-sensitive artifact (risk R-1). Using any
   of the 21 eligible cases is prohibited — 16 of them are the sealed holdout.
3. **Calibration protocol spec.** Pre-specify metrics (ECE and/or documented
   alternatives), reliability-diagram binning, and selective-prediction / risk–
   coverage definitions, with numeric acceptance thresholds — **frozen before any
   result** (risk R-3).

## Hard rules
- Private holdout stays sealed; `internal_only/` untouched; no holdout evaluation.
- No result-driven selection of metrics, thresholds, or pool membership.
- No live model call unless separately authorized; otherwise reuse recorded runs.
- Do not touch taxonomy, gold, schemas, retired status, or historical artifacts.
- Never stage `research/…expansion_150/`; stage only explicit Phase 6.1 paths.

## Read first
- `analysis/phase6_0_startup/phase6_execution_plan.md` (§Phase 6.1),
  `phase6_acceptance_criteria.md` (A6.1-1..4), `phase6_risk_register.md` (R-1..R-4,
  R-10, R-12), `phase6_0_inventory.md` (§5 confidence readiness, §2 dev-pool math).

## Key implementation facts (from the inventory)
- Model confidence exists as `AgentResponse.confidence: float`, captured per run in
  the flat record (`run_library.run_single`); parser defaults missing → `0.0`
  (`output_contract.py`).
- `calibrate.py` is a heuristic proposal generator, **not** probability
  calibration; ECE/reliability/selective-prediction must be built new (with tests).
- Packet integrity is enforced offline via `agent-arena packet-integrity` /
  `agent_arena.packet_integrity` — run it on any development pool before use.

## Status
This handoff is **uncommitted** (the approved Phase 6.0 commit is complete). Include
it in the next approved checkpoint. **Do not begin Phase 6.1 in the Phase 6.0
session.**
