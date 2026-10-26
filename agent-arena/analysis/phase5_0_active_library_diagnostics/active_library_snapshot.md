# Phase 5.0 — Active Library Diagnostic Snapshot

*Offline, static diagnostics for the post-v0.7.9 active library. **No live model
calls were made.** Generated from the case YAMLs and the harness discovery
(`agent_arena.run_library.discover_cases`). This is **not** a new live baseline.*

## Repo state [FACT]
- **Tag:** `v0.7.9-taxonomy-precedence-case054`
- **Commit:** `84e6061` — "Add taxonomy precedence rule and adjudicate case054"
- **Branch:** `feat/case-library-run-harness`
- **Tests (last known):** 988 passed
- **New live baseline run:** No — this phase is offline diagnostics/reporting only.

## Library counts [FACT]
- **Active cases (default discovery):** 49
- **Retired historical cases:** 1 — `study-forensics-042`
- **Include-retired discovery:** 50
- Verified: `discover_cases()` → 49; `discover_cases(include_retired=True)` → 50.

## Active label distribution [FACT]
| gold_label | active count | % of active |
|---|---:|---:|
| solid | 14 | 28.6% |
| overclaim | 23 | 46.9% |
| mechanism_vs_evidence | 6 | 12.2% |
| correlation_vs_causation | 6 | 12.2% |
| **TOTAL** | **49** | **100%** |

Case-type split: 40 clear / 9 borderline. Ambiguity: 34 low / 10 medium / 5 high.

## Case status highlights [FACT]
- **case042** — retired from active metrics via real default-exclusion filtering
  (`status: retired`, `excluded_from_active_metrics: true`, `origin: demo_derived`).
  Not deleted, not label-flipped; still loadable via `--case-id` / `--include-retired`.
- **case041** — active **Core**; `origin: curated_showcase`, `intake_review: passed`;
  primary label `overclaim`; prompt unchanged.
- **case054** — active; primary label remains **overclaim** after the v0.7.9
  rule-first, anti-co-evolution no-flip adjudication (a stable 3/3 model reading of
  `mechanism_vs_evidence` was rejected because the mechanism trigger is absent).
  Prompt unchanged.

## Historical Phase-5A — FROZEN [FACT]
- The Phase-5A live baseline (`analysis/phase5a/lib_20260704_134553_55aa66`,
  produced at v0.7.6) was a **50-case** single-model (Opus 4.5) run: 150/150
  successful, 96.0% per-run and case-majority accuracy.
- Those reports are **frozen** and were **not** modified or recalculated here.
- Any active-set number below that is derived from those historical records is
  explicitly labelled as **derived / offline**, not a new live result.

## Derived (NOT a new baseline) [DERIVED — historical v0.7.6 records]
Excluding the now-retired `study-forensics-042` from the historical 50-case run:
- case042 contributed **3 stable-wrong runs** (overclaim→solid) and **1** majority miss.
- Derived per-run accuracy: 144 / 147 = **97.96%**.
- Derived case-majority accuracy: 48 / 49 = **97.96%**.

> ⚠️ This is arithmetic derived from the **frozen** v0.7.6 records, **not** a new
> live run against the 49-case active set. It must not be presented as a new
> benchmark result. A fresh active-set live measurement (Phase 5.1+) has **not**
> been run.

## Files in this bundle
- `active_library_snapshot.md` (this file), `active_library_snapshot.json`
- `active_case_inventory.csv`, `retired_case_inventory.csv`
- `label_distribution_active.csv`
- `suite_status_summary.md`, `post_v079_open_risks.md`, `next_phase_readiness.md`
