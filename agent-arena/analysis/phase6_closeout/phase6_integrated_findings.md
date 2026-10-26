# Phase 6 — Integrated Findings

All values are verified against committed reports (`phase6_2_results/`,
`phase6_4_prompt_only_results/`). No number here is newly computed; none pools cases; no
universal-superiority, causal, production, or holdout claim is made.

---

## Part A — Three-model development calibration

### DEVELOPMENT CALIBRATION — NOT HOLDOUT

Same 27 development cases per model; **not** pooled into an 81-case benchmark; the 81
predictions are **not** independent cases. Source:
`phase6_2_results/cross_model_descriptive_comparison.json`.

| model | accuracy (all 27) | Brier (clear, n=26) | Brier (all 27) | ECE 5-bin (clear) | high-conf errors | mean conf |
|---|---|---|---|---|---|---|
| Haiku | 27/27 = 1.000 | 0.00957 | 0.00930 | 0.0912 | 0 | 0.910 |
| Sonnet | 24/27 = 0.889 | 0.07467 | 0.10533 | **0.00115** | **3** | 0.923 |
| Opus | 27/27 = 1.000 | 0.00980 | 0.00968 | 0.0927 | 0 | 0.908 |

- **Sonnet's three errors are all gold `overclaim`**, each predicted as a *more specific*
  label: DEV-0011 → `correlation_vs_causation`; DEV-0013 → `mechanism_vs_evidence`;
  DEV-0024 → `mechanism_vs_evidence`. Correctness pattern (Haiku,Sonnet,Opus): `111` ×24,
  `101` ×3.
- **ECE was sparse-bin and potentially misleading:** confidences concentrated in the top
  range, so only the upper bins were occupied. Sonnet had the **lowest** ECE **despite**
  being the only model with errors. **Brier exposed the high-confidence errors more
  appropriately** and is the primary metric.
- **No abstention threshold was approved.** Simple confidence-threshold abstention was not
  established as a reliable operating rule.
- Haiku and Opus reached 27/27 → a plausible **ceiling effect** on this development pool for
  those models.

---

## Part B — Paired Haiku package-level comparison

### DEVELOPMENT PILOT — NOT HOLDOUT

Same 27 **paired** cases; one run per arm; same exact Haiku snapshot
`claude-haiku-4-5-20251001`; a **package-level** contrast (system prompt + response contract
+ parser differ together — **not** one system-prompt string). The 54 predictions are **not**
pooled into a 54-case benchmark. Source: `phase6_4_prompt_only_results/paired_comparison_report.json`.

| metric | Agent Arena | prompt-only |
|---|---|---|
| accuracy (all 27) | 27/27 = **1.000** | 24/27 = **0.889** |
| Brier top-label (all 27, VALID) | **0.0093** | **0.0814** |
| high-confidence errors | 0 | 1 |
| parser completion | 27/27 | 27/27 |

- **Accuracy difference** (AA − prompt-only) = **+0.111**; **Brier difference** (prompt-only −
  AA) = **+0.0721**.
- **Paired correctness:** both correct **24** · Agent Arena only correct **3** · prompt-only
  only correct **0** · both incorrect **0**.
- **Three asymmetric opaque cases (all gold `overclaim`):** DEV-0011, DEV-0013, DEV-0018 —
  each a case where prompt-only chose a *more specific* label instead of `overclaim`.
- Parser completion (27/27 both) is reported **separately** from classification quality: the
  gap is genuine label disagreement, not a parser/confidence-validity artifact.

---

## Part C — Cross-phase convergent-difficulty observation (hypothesis only)

Two independent development runs produced errors **only on gold `overclaim`** cases, and two
of the failing cases **recur across both**:

| failing DEV id | 6.2 Sonnet | 6.4 prompt-only Haiku |
|---|---|---|
| DEV-0011 | ✗ → correlation_vs_causation | ✗ → correlation_vs_causation |
| DEV-0013 | ✗ → mechanism_vs_evidence | ✗ → mechanism_vs_evidence |
| DEV-0018 | (correct) | ✗ → mechanism_vs_evidence |
| DEV-0024 | ✗ → mechanism_vs_evidence | (correct) |

- Every error in **both** phases is an `overclaim` case mislabeled as a *more specific*
  category (`correlation_vs_causation` or `mechanism_vs_evidence`).
- This **overclaim → over-specific** pattern is a **Phase 7 hypothesis**, **not** a proven
  taxonomy defect. It may reflect genuine boundary ambiguity, a prioritization gap without
  the Agent Arena priority-rule scaffold, or dataset-specific phrasing — indistinguishable at
  this n. It is a strong signal to design Phase 7 boundary-robustness cases (overclaim vs
  correlation, overclaim vs mechanism) and explicit primary-label prioritization tests.

---

## Permitted conclusions (this development evidence only)

- Agent Arena's Phase 6 infrastructure is **technically and methodologically functional**.
- On this 27-case paired development pilot, the **Agent Arena Haiku package showed a
  descriptive advantage** over the competent minimal prompt-only package.
- The Phase 6.2 and 6.4 results **support further robustness testing**.
- **Brier was more informative than sparse-bin ECE** in these runs.
- **Simple confidence-threshold abstention was not established** as a reliable operating rule.
- The development pool **may show ceiling effects** for Haiku and Opus.
- **Multiple-run stability and harder boundary cases are justified Phase 7 priorities.**

## Forbidden conclusions (explicitly not claimed)

Agent Arena universally superior; production validated; Haiku/Opus universally perfect;
Sonnet generally inferior; self-reported confidence universally useless; taxonomy proven
defective; holdout confirms development findings; 27 cases constitute statistical proof; the
81 or 54 predictions are independent cases; a confidence threshold approved for production.

## Reporting-frame note (not an inconsistency)

Phase 6.2 cites Haiku Brier ≈ **0.0096** (clear stratum, n=26); Phase 6.4 cites Agent Arena
Haiku Brier = **0.0093** (all 27). These are the **same run** under two frozen reporting
frames (clear-stratum vs all-27 denominators), not conflicting measurements.
