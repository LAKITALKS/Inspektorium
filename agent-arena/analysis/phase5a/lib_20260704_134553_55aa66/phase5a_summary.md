# Phase 5A — Single-Model Multi-Run Case Diagnostics

**Run:** `lib_20260704_134553_55aa66` | **Model:** anthropic / claude-opus-4-5 | **runs/case:** 3

> **Methodological caveat.** This is a *single strong model* (Opus 4.5) **ceiling / stability** diagnostic, not a discrimination-power measurement. A case that every run of one strong model gets right tells us the case is unambiguous *for this model* — not that it separates strong from weak models. True discrimination power requires a **heterogeneous model panel** (Phase 5B). All `confidence` values are the model's **uncalibrated self-report** and must not be treated as calibrated probabilities.

## 1-2. Accuracy

- Per-run accuracy: **96.0%** (144/150)
- Case-majority accuracy: **96.0%** (48/50)

## 3. Per-label accuracy

| gold label | correct/total | accuracy |
|---|---|---|
| solid | 42/42 | 100.0% |
| overclaim | 66/72 | 91.7% |
| mechanism_vs_evidence | 18/18 | 100.0% |
| correlation_vs_causation | 18/18 | 100.0% |

## 4. Confusion matrix (rows=gold, cols=detected, per run)

| gold \ detected | solid | overclaim | mechanism_vs_evidence | correlation_vs_causation |
|---|---|---|---|---|
| solid | 42 | 0 | 0 | 0 |
| overclaim | 3 | 66 | 3 | 0 |
| mechanism_vs_evidence | 0 | 0 | 18 | 0 |
| correlation_vs_causation | 0 | 0 | 0 | 18 |

## 5. Solid-label confusion (two directional metrics)

These are reported separately to avoid the ambiguous term 'solid false-positive rate'. See solid_confusion_cases.md.

- **solid_as_problem_rate** (gold==solid but predicted!=solid; a supported claim wrongly flagged as a problem — the commercially important FP direction): **0.0%** (0/42).
- **problem_as_solid_rate** (gold!=solid but predicted==solid; a real problem under-flagged as solid — false-negative-style): **2.78%** (3/108, all from case042, a documented borderline whose alternative reading is solid — not relabelled).

## 6. Label consistency per case

- Fully consistent (1 unique label / 3 runs): **50/50**
- 2 unique labels: 0 | 3 unique labels: 0

## 7-8. Score & confidence dispersion

- Score range > 15 (high variance): **0** cases
- Max per-case score range observed: 8.3
- Confidence is uncalibrated self-report; per-case stats in case_diagnostics.csv.

## 9. Run health

- Successful: 150/150 | parse failures: 0 | truncation: 0 | provider errors: 0

## 10-14. Stability buckets

- Stable-correct: **48**
- Stable-wrong: **2** → study-forensics-042, study-forensics-054
- Stable-alternative (documented borderline+alt): **2** → study-forensics-042, study-forensics-054
- Unstable: **0** → none
- High-score-variance: **0** → none

## 15. Preliminary case-suite draft

| suite bucket | count | cases |
|---|---|---|
| core_candidate | 35 | 35 cases |
| anchor_candidate | 5 | study-forensics-026, study-forensics-033, study-forensics-039, study-forensics-050, study-forensics-052 |
| boundary_candidate | 10 | study-forensics-007, study-forensics-022, study-forensics-031, study-forensics-037, study-forensics-042, study-forensics-043, study-forensics-045, study-forensics-048, study-forensics-054, study-forensics-059 |
| quarantine_candidate | 0 | — |
| review_required | 0 | — |

(Full assignment in suite_assignment_draft.csv. `case042`/`case054` are boundary_candidate + review_required; no labels were flipped and nothing was quarantined.)

## Token & latency

- Tokens: input 189,516 / output 125,024 / total 314,540
- Latency (ms): mean 21433, median 15988, min 12148, max 618700 (the max is a single transient network stall; median is representative)

## Recommended Phase 5B candidate-selection strategy (model-panel probe)

Because a single strong model saturates the suite (48/50 trivially stable-correct), real discrimination power needs a heterogeneous panel. Suggested design for a later, cost-controlled 5B:

1. **Panel:** add ≥1 weaker/cheaper model (e.g. Haiku) and ≥1 mid model (e.g. Sonnet) alongside Opus, so cases can separate strong-from-weak.
2. **Candidate subset first (not full 50×panel):** prioritise (a) the 2 boundary cases (042, 054), (b) a stratified sample of ~3 per gold label across difficulties, and (c) all 9 borderline cases — ~15-20 cases × 3 runs × panel, to control cost.
3. **Discrimination metric:** per-case cross-model disagreement (entropy) + weak-model error rate; cases that strong models pass and weak models fail are the high-discrimination core.
4. **Keep this 5A run as the Opus ceiling reference** to compare panel results against.
5. No gold flips from panel behaviour without an independent taxonomy justification (same discipline as Phase 4.2).
