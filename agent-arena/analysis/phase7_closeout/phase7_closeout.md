# Phase 7 — Integrated Closeout (Robustness Evaluation)

**Status: `PHASE 7 CLOSED — ROBUSTNESS LIMITATIONS IDENTIFIED AND FROZEN`.**
Next implementation phase: **Phase 8**. Zero model calls in closeout; no scientific rewrite.

*Canonical, single-source closeout for Phase 7A (empirical robustness) + Phase 7B (artifact/QA gates).
Raw reports are referenced, not duplicated. The empirical experiment remains exactly as executed;
curator findings are a separate post-experiment governance layer that changes nothing in the frozen
data.*

## 1. Scope

Phase 7 asked whether the completed Agent Arena harness, run over a pre-registered robustness suite,
executes correctly and exposes systematic model weaknesses — evaluated on **two independently-primary
frozen model conditions**, then reviewed by a human curator on the one shared difficult boundary. It did
**not** ask "did every model pass": experiment completion and model-robustness perfection are distinct
(a robustness phase closes successfully while documenting real model limits).

## 2. Frozen experiment identifiers

| binding | value |
|---|---|
| scientific manifest fp | `55217a9de2b159388a13fca2038d284e3289f5d5e835b39cea3d980f1467f45c` |
| execution manifest fp | `9c43aa4bf189f373079f00a313c671b5619bf7737ee73e5cefab73e274fcdb89` |
| call-plan fp | `7b1b58e730e394e4985e89c4ab1624266656aa540d1fcd4ee8b00a7389828e4e` |
| package/prompt fp | `6f572faa5ede59c15648ced5258e6d0d54f068871faf64bac9f3d5f5c7dbf3f4` |
| universe | 34 independent bases · 84 evaluated units · 50 variants · 10 clusters · N=5 |
| approved science | boundary `3bdabaf` · adversarial `e9e13e3` · perturbation `84d75d4` |
| Haiku result-set fp / commit | `b994672ec89bd05f…` / `e6cd374` |
| Sonnet result-set fp / commit | `e1741121c55e5221…` / `6644f7e` (path `11f31f2`; incomplete checkpoint `9b74604`) |
| Phase-7B release-gate commit | `aa71c4a` |

Both conditions ran the **identical** frozen science (same scientific/execution/call-plan/package
fingerprints; input tokens byte-identical). Only the model id and its pre-registered runtime contract
differ (`7bd5509a…` Haiku, `d3e175f3…` Sonnet).

## 3. Haiku 4.5 result summary (`claude-haiku-4-5-20251001`, 420/420)

Unit-modal accuracy **0.7262** (bases 0.706 / variants 0.74) · Brier **0.240** · ECE **0.217** · mean
confidence 0.940 · high-confidence-wrong 23 · replication **84/84 unanimous** · parse/provider/truncation
0/0/0. Per-gold: `solid` 13/13 · `overclaim` 44/44 · `correlation_vs_causation` **4/10** ·
`mechanism_vs_evidence` **0/17**. Triggers: boundary **BLOCK** (B1, B2), adversarial **BLOCK** (A2, A7),
perturbation **BLOCK** (NEU-003 under P2/P3/P4), replication OK. **HAIKU BLOCK TRIGGERED.**

## 4. Sonnet 4.5 result summary (`claude-sonnet-4-5-20250929`, 420/420)

Unit-modal accuracy **0.7738** (bases 0.735 / variants 0.80) · Brier **0.201** · ECE **0.175** · mean
confidence 0.944 · high-confidence-wrong 19 · replication **82 unanimous + 2 stable-majority** ·
parse/provider/truncation 0/0/0. Per-gold: `solid` 13/13 · `overclaim` 35/44 ·
`correlation_vs_causation` **9/10** · `mechanism_vs_evidence` **8/17**. Triggers: boundary **BLOCK** (B2,
bidirectional), adversarial **BLOCK** (A2, A5), perturbation **BLOCK** (P3 across 3 clusters; BND-009
under P3/P5), replication OK. **SONNET BLOCK TRIGGERED.** (Batch halted mid-run by an account API usage
cap at 266/420, then resumed to 420/420 running only the 154 missing slots — the 266 completed were
never re-run.)

## 5. Failure topology (see `two_model_failure_topology.md`)

- **Shared failure locus:** the `mechanism_vs_evidence ↔ overclaim` boundary (B2 both; A2 both; a set of
  units where both models collapse `mechanism_vs_evidence → overclaim`).
- **Haiku-specific:** one-directional collapse of `mechanism_vs_evidence → overclaim` (0/17); weak
  `correlation_vs_causation` (4/10; B1 BLOCK, A3 INVESTIGATE).
- **Sonnet-specific:** bidirectional `overclaim ↔ mechanism_vs_evidence` confusion (also maps 9
  `overclaim → mechanism_vs_evidence`; A5 BLOCK) — over-applies the specific label to surrogate cases.
- **Model-capacity difference (observed):** Sonnet stronger on `correlation_vs_causation` (9/10 vs 4/10),
  partial mechanism recovery (8/17 vs 0/17), better calibration.
- **Representation-sensitivity difference (observed):** the models are destabilized by different
  perturbations (Haiku NEU-003 under P2/P3/P4; Sonnet the P3 family across the mechanism boundary).
- **Shared strength:** `solid` (13/13 both) and overt `overclaim` / A1, A4, A6, A8 (PASS both);
  near-deterministic replication at temperature 0 (blocks are stable, not sampling noise).

No causal/architectural claim is drawn from n=2 models (patterns are "observed in / consistent with").

## 6. Human curator decisions (post-experiment governance; see `curator_review_dossier_*.md`)

Reviewed the 12 independent base cases on the shared boundary. **No gold changed, no case retired, no
taxonomy edited, no score recalculated.**

| decision | count | cases |
|---|--:|---|
| **A** gold clearly holds | 9 | ADV-003, ADV-004, ADV-013, BND-009, BND-010, NEU-004, ADV-009, ADV-010, BND-015 |
| **B** case ambiguity | 0 | — |
| **C** taxonomy boundary needs future clarification | 2 | BND-016, BND-018 |
| **D** multiple failure modes, primary label defensible | 1 | ADV-017 |
| **E** material gold problem | 0 | — |

- **BND-016 / BND-018 (C):** frozen `overclaim` gold remains defensible under the surrogate-to-clinical
  (Shape B) rule; but mechanistic language ("cerebral blood flow", "building blocks of bone") can compete
  with the surrogate framing. **Not a material Phase-7 gold problem** — preserved as a future
  semantic-operationalization issue.
- **ADV-017 (D):** claim contains both a described fibrinolytic mechanism and human surrogate markers;
  `mechanism_vs_evidence` stays the defensible primary because the mechanistic leap is used directly to
  imply prevention of heart attack/stroke. **Do not relabel.**

**Material gold problems discovered: 0. Result-driven gold changes: 0. Taxonomy changes: 0. Case
retirements: 0. Phase-7 score recalculations: 0.**

## 7. Completeness

- **Phase 7A: COMPLETE** — boundary/adversarial/neutral/perturbation pools, N=5 replications, calibration
  diagnostics, two primary models, raw freezes (both `complete:true`, fingerprints reproduce),
  deterministic per-model analyses, all frozen failure rules applied, topology + dossier produced,
  curator review completed.
- **Phase 7B: COMPLETE** — Artifact Binding, Derived-Value Provenance, Search-Scope Gate, Evidence
  Symmetry, Final Release Gate (consolidated `aa71c4a`).
- **Harness execution: sound** — 420+420 completed, 0 provider failures in the frozen sets, 0 parse/
  truncation, fingerprints reproduce; resume/dedup proven on real interruption (Sonnet cap recovery).

## 8. Known limitations (frozen, not defects to repair in Phase 7)

- Both primary models BLOCK on the `mechanism_vs_evidence ↔ overclaim` boundary — a documented **model**
  limitation, not a harness defect. Agent Arena does **not** make a weak model perfect; harness quality
  and foundation-model capability are distinct variables.
- Two future taxonomy-clarification points (BND-016, BND-018) and one genuine dual-structure case
  (ADV-017) are recorded for forward work, not resolved here.
- No universal robustness score exists or is claimed; Haiku and Sonnet are never pooled.

## 9. Deferred forward work (routing only; nothing implemented)

| item | routing |
|---|---|
| BND-016 / BND-018 semantic-boundary clarification | **Phase 8** (semantic/evidence typing) |
| Dual / multiple failure-mode handling | **Phase 8** (composite semantics / local-to-global consistency) |
| Independent verdict challenge / disagreement handling | **Phase 9** |
| Professional renderer / post-render PDF/HTML QA | **Phase 10** |
| Case Library expansion | future controlled dataset versions (never reopens a frozen phase) |
| V1.0 Harness Efficacy Benchmark | frozen in `docs/v1_release_gates.md` (final v1.0 release gate) |

No Phase 11 is created. The v1.0 product rule stands: **finish Agent Arena 1.0; do not make it
theoretically perfect before release.**

## 10. Final status

**PHASE 7 CLOSED — ROBUSTNESS LIMITATIONS IDENTIFIED AND FROZEN.**
Experiment complete; model robustness imperfect and documented; harness execution sound. Next
implementation phase: **Phase 8** (not started here).
