# Phase 7A — Execution Plan, Pilot Policy, Work Packages (post-freeze)

Derived from the repository's own conventions (`analysis/phaseN_*` dirs; frozen prep/result
checkpoints; hashed contracts; `run_library` `--fake` dry-run mode; retirement-aware discovery).
The curator design-freeze decisions are applied. **Nothing here is executed in this session.**

---

## 1. Frozen curator decisions (applied across the six docs)

| decision | frozen value |
|---|---|
| Phase separation | 7A (analysis robustness) stays separate from 7B (artifact QA) |
| Primary objective | package-intrinsic robustness (no prompt-only replication required) |
| Model conditions | **Agent-Arena package only**, **2 PRIMARY conditions**: `claude-haiku-4-5-20251001` + `claude-sonnet-4-5-20250929` (Haiku's "ceiling" status is a historical descriptor, not exclusive block authority). **Opus excluded** from primary (later optional, separate authorization) |
| Acceptance semantics | isolated error = INVESTIGATE/LIMITATION; **systematic reproducible failure = BLOCK**, with each BLOCK rule applied **independently to each primary condition** (Haiku or Sonnet alone can block; cross-model recurrence = stronger corroboration, not a prerequisite) |
| Case pool | 34 independent bases (14 Boundary + 16 Adversarial + 4 neutral anchors) + 50 clustered variants |
| Boundary directional counts | B1 3 `overclaim`/2 `correlation`; B2 3 `overclaim`/2 `mechanism`; B3 2 `solid`/2 `overclaim` |
| Perturbation clusters | 10 = 4 neutral anchors + 6 deterministically fingerprint-selected (case contract §6) |
| Replication | **N = 5** (frozen; not changed after variance) |
| Class-B location | separate `tasks/study_forensics_robustness/`; normal library discovery unchanged |
| Metrics | Brier primary · ECE secondary/diagnostic · invariance ≠ correctness · stability ≠ confidence · no universal score |
| Expected volume | **84 × 5 × 2 = 840 planned model calls** (not a sample size) |

---

## 2. Execution order (recommended)

```
0. CURATOR design-freeze commit (this session) — pre-result checkpoint          ← we are here → STOP
1. WP-1  author boundary pool (class B) with frozen gold + fingerprints + tiers  (post-authorization)
2.        CURATOR gold review — gold frozen BEFORE any run
3. WP-2  author adversarial set (A1–A8 × 2) → curator gold review → freeze
4. WP-3  author perturbation variants from frozen bases (deterministic §6 selection)
5.        deterministic / human equivalence validation of every perturbation      (§16 checklist)
6. WP-4  thin reporting extension (stability fields · cluster-aware · transition matrix); `--fake` unit tests
7.        freeze run manifest: N=5 + runtime contract + 2 model conditions
8. WP-5  `--fake` structural dry-run (technical only) → real N=5 run over frozen pool + 2 conditions
9.        deterministic metrics + stability + cluster-aware + transition-matrix diagnostics
10.       evaluate vs pre-result acceptance matrix (successes + counterevidence + limitations)
11.       compact Phase-7A closeout
```

Steps 0–7 are **pre-result**; gold is frozen at steps 2/3, always before step 8. No result from
step 8 (or the dry-run) may revise gold, case selection, acceptance thresholds, perturbation
equivalence, N, or family counts.

---

## 3. Pilot policy (frozen, §23)

A technical **dry-run** is allowed later using the existing offline `FakeLibraryProvider`
(`run_library --fake`) or other non-scored synthetic technical input. **Purpose: verify
orchestration only** (discovery → per-run records → `CaseStability` → metrics/diagnostics → artifact
writer + fingerprints). It **may NOT** be used to alter gold, case selection, acceptance thresholds,
perturbation equivalence, N, or family counts. **No scored live pilot** occurs before the frozen
experiment unless separately authorized.

---

## 4. Budget / stop discipline (frozen, §19/§22)

- **N = 5 is fixed.** It is **not** reduced to N = 3 later because of cost after seeing results
  (that would be "changing N after variance", a governance blocker).
- If, **before any model run**, the execution budget proves insufficient for the full **840**
  planned calls, the correct action is **STOP for curator rescoping** — do **not** partially run and
  then change N.
- Planned analytical replications (N = 5) are distinct from transport retries (≤ 2 per call,
  infrastructure-only); a retry is **not** an extra replication.

---

## 5. Smallest next work packages (post-authorization)

Prefer ≤ 5 packages, each small and additive; **none started now.**

1. **WP-1 — Boundary pool + gold freeze.** Author the 14 boundary bases (B1/B2/B3 with the frozen
   directional gold counts) with full frozen records + `case_fingerprint` + difficulty tiers;
   curator gold review. (No runs.)
2. **WP-2 — Adversarial pool + gold freeze.** Author the 16 adversarial cases (A1–A8 × 2) with
   pre-declared forensic triggers + frozen gold distribution; curator gold review. (No runs.)
3. **WP-3 — Neutral anchors + perturbation variants + equivalence freeze.** Author the 4 neutral
   anchors; run the deterministic §6 cluster-selection; author 50 variants (P1–P5); deterministic /
   human equivalence validation. (No runs.)
4. **WP-4 — Thin reporting extension + separate robustness discovery path.** Additive stability
   fields (`modal_label`, `label_switch_count`, `confidence_spread`, per-replication Brier),
   cluster-aware / pseudoreplication reporter, 4×4 transition-matrix diagnostic, and a **separate
   robustness discovery/manifest path** (does **not** widen `discover_cases`' library glob).
   `--fake`-unit-tested. (No model calls.)
5. **WP-5 — Execution + closeout.** Freeze run manifest (N=5, 2 conditions); `--fake` dry-run; real
   N=5 run; deterministic metrics + acceptance-matrix evaluation; compact closeout (one machine
   report + one human report + one audit manifest + one generator).

**Recommended immediate next package: WP-1 (Boundary pool authoring + gold freeze).** Do not
implement until curator authorization.

---

## 6. Post-render QA classification (§56)

Post-render PDF/HTML verification is **BELONGS LATER (report-engineering)**, consistent with the
Phase-7B note. It is **not** a Phase-7A blocker and is **not** implemented here.

---

## 7. Governance-overhead recommendation

Phase 7A stays compact: this 6-document startup package (now the frozen design), then a **single**
frozen case/variant manifest, a **single** run manifest, a **single** result report, and a
**single** closeout — reusing the existing `run_library`/`calibration` generators. No new reporting
architecture, no universal ontology, no leaderboard number.

---

## 8. Remaining genuine curator decisions

The design-freeze patch resolved model conditions, case counts, directional counts, perturbation
selection, N, class-B location, and acceptance semantics. Nothing further is required to author
WP-1. Any later choice (Opus optional condition; the optional prompt-only perturbation contrast; a
7A tag at closeout) is deferred to its own authorization and is **not** needed now.
