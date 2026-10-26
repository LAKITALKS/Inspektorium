# Phase 5.1 — Holdout Selection Plan (fresh restart; written before eligibility/ranking/selection)

**created (UTC):** 2026-08-02T20:28:40Z · **source_commit:** babeb11dec4f52feced708626c9f090f61c8afaa · **source_tag:** v0.8.11a-holdout-pool-augmentation
**phase_designation:** phase5_1_prospective_holdout_freeze
**selection_algorithm_version:** holdout_select_v1
**frozen_seed (ORIGINAL, unchanged):** `agentarena-phase5.1-holdout-v1|f8efe474d3068b7fbc4d149d9be1816b12b1e9cd`

> The original Phase 5.1 algorithm and seed are preserved **unchanged**. The seed is the
> pre-feasibility-failure seed and is **not** reseeded with the Phase 5.1a commit hash.

## History
- The earlier Phase 5.1 preflight correctly hit its fail-stop (correlation_vs_causation had 3
  eligible, mechanism_vs_evidence had 2, below 4-per-label). **No selection result** was produced by
  that aborted attempt; its plan + partial eligibility ledger were archived privately and removed.
- The deterministic Phase 5.1a augmentation added three approved blind packets (BIAA-021/022/023),
  raising the eligible pool to ≥4 per label. This restart ranks the **complete** eligible pool anew.

## Target & rules
- 16 cases; **exactly 4 per label** (solid, overclaim, correlation_vs_causation, mechanism_vs_evidence).
- Newest approved packet version only (BIAA-013→v3, BIAA-016→v2, BIAA-021/022/023→v1).
- Deduplicate clusters via SHA-256(seed+"|dedupe|"+canonical_case_id+"|"+version), keep smallest hash.
- Rank via SHA-256(seed+"|rank|"+candidate_key); pick first 4 per label. Opaque order via
  SHA-256(seed+"|opaque-order|"+candidate_key) → HLD-001..016.
- **No manual swaps; no model-performance/correctness/confidence/agreement/difficulty inputs.**
- Private HLD→source map, HLD ordering, HLD→gold map, evaluator packets, and per-HLD gold remain
  sealed (outside Git). Committed: policies, aggregate summaries, hashes, cryptographic commitments.
- No evaluation in this phase; no development access after freeze; a separate precommitted
  evaluation protocol is required later.

## Honest limitation (recorded before selection)
For **correlation_vs_causation** and **mechanism_vs_evidence** the eligible pool currently contains
**exactly four** cases, so **all four necessarily enter the holdout**. Therefore source-case
membership in those two strata may be **inferable to maintainers** who know the approved pool. The
private HLD→source mapping, HLD ordering, HLD→gold mapping, evaluator packets, and per-HLD gold
assignments remain **sealed**. Source membership is **not** described as perfectly secret, and the
holdout is **prospective, not historically untouched**.
