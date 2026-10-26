# Phase 7A — Two-Model Failure Topology (Haiku 4.5 vs Sonnet 4.5)

*WP-7C deterministic comparison. Derived entirely from the frozen raw records and deterministic
analyses of the two independently-primary Phase-7A conditions. **No model calls.** No scientific
content changed. Per-model throughout — the two models are **never pooled** into a single score.*

## Provenance (both conditions ran the identical frozen science)

| binding | Haiku | Sonnet | same? |
|---|---|---|---|
| model id | `claude-haiku-4-5-20251001` | `claude-sonnet-4-5-20250929` | — |
| scientific manifest fp | `55217a9d…` | `55217a9d…` | **yes** |
| execution manifest fp | `9c43aa4b…` | `9c43aa4b…` | **yes** |
| call-plan fp | `7b1b58e7…` | `7b1b58e7…` | **yes** |
| package/prompt fp | `6f572faa…` | `6f572faa…` | **yes** |
| runtime-contract fp | `7bd5509a…` | `d3e175f3…` | **differs by design** (per-model contract) |
| result-set fp | `b994672e…` | `e1741121…` | (distinct results) |
| result commit | `e6cd374` | `6644f7e` | — |
| completed | 420/420 | 420/420 | — |

Same 34 independent bases / 84 evaluated units / 50 variants / 10 clusters / N=5 / gold / perturbations.
Total input tokens are **byte-identical** (562,145 each) — a direct confirmation the two models saw the
same frozen prompts. Only the model and its pre-registered runtime contract differ.

## Harness vs model vs robustness (three distinct concepts — §8)

1. **Harness execution quality.** Agent Arena executed the frozen experiment correctly for both models:
   420/420 completed, 0 provider failures in the frozen sets, 0 parse failures, 0 truncation, all
   `finish_reason=stop`, all confidence VALID, aggregate fingerprints reproduce. **Execution is sound.**
2. **Model performance under the harness.** Both models are accurate on the easy strata and both
   **BLOCK** on the hard forensic boundary (below). A model BLOCK is a *finding about the model*, not a
   harness failure.
3. **Harness robustness findings.** The harness **did** expose reproducible, systematic weaknesses
   (boundary/adversarial/perturbation blockers fired for both models, unanimously at temperature 0).
   Exposing real limitations is the robustness suite working as designed — not the harness failing.

## A. Overall performance

| metric | Haiku 4.5 | Sonnet 4.5 |
|---|--:|--:|
| replication-level accuracy | 0.7262 (305/420) | 0.7786 (327/420) |
| unit-modal accuracy | 0.7262 (61/84) | 0.7738 (65/84) |
| base accuracy | 0.7059 (24/34) | 0.7353 (25/34) |
| variant accuracy | 0.74 (37/50) | 0.80 (40/50) |
| mean Brier (valid) | 0.2401 | 0.2013 |
| ECE (secondary diagnostic) | 0.217 | 0.175 |
| mean confidence | 0.940 | 0.944 |
| overconfidence gap (conf − acc) | +0.214 | +0.166 |
| high-confidence-wrong (units) | 23 | 19 |
| parse / provider / truncation | 0 / 0 / 0 | 0 / 0 / 0 |

Both models are **materially overconfident** (mean confidence ≈ 0.94 against ≈ 0.73–0.78 accuracy);
Sonnet is the better-calibrated of the two on every diagnostic, but neither is well-calibrated.

## B. Gold-label performance (unit-modal correct / total)

| gold label | Haiku | Sonnet | pattern |
|---|--:|--:|---|
| `solid` | 13/13 | 13/13 | **shared strength** |
| `overclaim` | 44/44 | 35/44 | Haiku perfect; Sonnet loses 9 → `mechanism_vs_evidence` |
| `correlation_vs_causation` | 4/10 | 9/10 | **model-capacity difference** (Sonnet substantially stronger) |
| `mechanism_vs_evidence` | 0/17 | 8/17 | **shared difficult locus**; Sonnet materially better but still confused |

This reproduces — from repository evidence, not assumption — the pre-flagged taxonomy note that
"models do not reliably produce `mechanism_vs_evidence`".

## C. Boundary (frozen rule: ≥2 same directional confusions, each wrong modal ≥3/5)

| priority boundary | Haiku | Sonnet |
|---|---|---|
| **B1** (corr_vs_caus ↔ overclaim) | **BLOCK** — corr→overclaim on BND-004, BND-005 | **PASS** (BND-004/005 both correct 5/5) |
| **B2** (mech_vs_evid ↔ overclaim) | **BLOCK** — mech→overclaim on BND-009, BND-010 | **BLOCK** — *bidirectional*: mech→overclaim (BND-009, BND-010) **and** overclaim→mech (BND-016, BND-018) |
| **B3** (solid ↔ overclaim) | **PASS** | **PASS** |

## D. Adversarial (frozen rule: 0/2 PASS · 1/2 INVESTIGATE · 2/2 BLOCK)

| family | Haiku | Sonnet |
|---|---|---|
| A1 | PASS | PASS |
| **A2** (mech gold) | **BLOCK** (ADV-003/004 → overclaim) | **BLOCK** (ADV-003/004 → overclaim) |
| A3 (corr gold) | INVESTIGATE (ADV-006 → overclaim) | PASS |
| A4 | PASS | PASS |
| **A5** (overclaim gold) | PASS | **BLOCK** (ADV-009/010 → mech) |
| A6 | PASS | PASS |
| A7 (mech gold) | **BLOCK** (ADV-013/017 → overclaim) | INVESTIGATE (ADV-013 → overclaim; ADV-017 correct) |
| A8 | PASS | PASS |

## E. Perturbation (frozen rule: a family flips ≥2 clusters, OR one cluster flips under ≥2 families)

| | Haiku | Sonnet |
|---|---|---|
| trigger | cluster `P7A-NEU-003` flips under **P2, P3, P4** (one cluster / ≥2 families) | family **P3** flips **3** clusters (BND-009, NEU-003, NEU-004); cluster BND-009 flips under **P3, P5** |
| status | **BLOCK** | **BLOCK** |
| flipped variants | PRT-03 P2/P3/P4 | PRT-03-P3, PRT-04-P3, PRT-06-P3, PRT-06-P5 |

Different representation-sensitivities: Haiku's correlation anchor (NEU-003) is fragile to several
rewrites; Sonnet's **P3** rewrite specifically destabilizes the mechanism/overclaim boundary across
clusters.

## F. Replication stability (temperature 0.0)

| tier | Haiku | Sonnet |
|---|--:|--:|
| 5/5 unanimous | 84 | 82 |
| 4/5 stable-majority | 0 | 2 (`P7A-BND-009`, `P7A-PRT-06-P1`) |
| 3/5 fragile | 0 | 0 |
| ≤2 unstable | 0 | 0 |
| systematic replication trigger | **no (OK)** | **no (OK)** |

Both models are near-deterministic at temperature 0. Consequently every BLOCK above is a **stable,
reproducible** property of the model on the frozen cases — not sampling noise.

## Failure-topology classification (§6 — empirical patterns, no causal claim)

- **SHARED FAILURE LOCUS — the `mechanism_vs_evidence ↔ overclaim` boundary.** Observed in both
  models: B2 BLOCK for both; A2 BLOCK for both; 9 independent-or-derived units where **both** models
  disagree with gold, all collapsing `mechanism_vs_evidence → overclaim` (ADV-003, ADV-004, ADV-013,
  BND-009, BND-010, and the PRT-06/PRT-04 variants). Consistent with the taxonomy's prior "developing"
  rating for this label.
- **SHARED STRENGTH.** `solid` (13/13 both) and the core `overclaim`/adversarial families A1, A4, A6,
  A8 (PASS for both). Both models reliably separate clean reporting and overt rhetorical inflation.
- **HAIKU-SPECIFIC FAILURE.** A near-total, **one-directional** collapse of `mechanism_vs_evidence`
  into `overclaim` (0/17), and weak `correlation_vs_causation` (4/10, B1 BLOCK, A3 INVESTIGATE). Haiku
  never makes the reverse error.
- **SONNET-SPECIFIC FAILURE.** A **bidirectional** confusion at the same boundary: in addition to some
  shared mech→overclaim collapses, Sonnet uniquely maps 9 `overclaim` cases → `mechanism_vs_evidence`
  (ADV-009, ADV-010, BND-016, BND-018, PRT-08 P1–P5; A5 BLOCK). Where Haiku over-uses the generic
  label, Sonnet over-applies the specific one.
- **MODEL-CAPACITY DIFFERENCE (observed).** Sonnet is stronger on `correlation_vs_causation` (9/10 vs
  4/10) and partially recovers `mechanism_vs_evidence` (8/17 vs 0/17), with better calibration
  (Brier 0.201 vs 0.240; ECE 0.175 vs 0.217). Consistent with a higher-capacity model within the same
  harness.
- **REPRESENTATION-SENSITIVITY DIFFERENCE (observed).** The two models are destabilized by *different*
  perturbations (Haiku: NEU-003 under P2/P3/P4; Sonnet: the P3 rewrite across the mechanism boundary).

**No causal/architectural claim is made from n=2 models.** All statements are "observed in / consistent
with / shared empirical pattern", per §6.

## One-line synthesis

Under an identically-frozen, correctly-executed harness, both primary models are strong on `solid` and
overt `overclaim` but **both BLOCK on the `mechanism_vs_evidence ↔ overclaim` boundary** — Haiku by a
one-directional collapse toward `overclaim`, Sonnet by bidirectional confusion — while Sonnet is the
stronger, better-calibrated model on `correlation_vs_causation` and partial mechanism recovery. The
shared boundary is routed to the human curator dossier; it is a documented model limitation, not a
harness defect, and (per §14) does not by itself block Phase-7 experiment closure.
