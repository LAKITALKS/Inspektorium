# Phase 6.4 — Paired Haiku package-level development comparison

### DEVELOPMENT PILOT — NOT HOLDOUT
### same 27 paired development cases; one run per arm; same exact model
### package-level contrast (system prompt + response contract + parser differ together)
### descriptive small-sample analysis; no universal-superiority inference
### no threshold optimized after results; small-n label limitations (corr/mech at n=2)
### the 54 predictions are two paired outputs on 27 cases — never pooled into 54 cases
### holdout remained sealed; residual model nondeterminism possible despite temperature=0
### parser/response-contract asymmetry; the baseline's lighter response burden may favor it

**Comparison unit:** 27 paired DEV-#### cases; two arms; paired (per-case), never pooled.

- Agent Arena arm — run `AA-6.2-RUN-6a3b93a24af7431e`, contract `AA-RTC-6.2-HAIKU-001`
- prompt-only arm — run `AA-6.4B-HAIKU-PROMPTONLY-f44d734f00162c03`, contract `AA-RTC-6.4-HAIKU-PROMPT-ONLY-001`
- shared model: `claude-haiku-4-5-20251001`

## Headline (descriptive; frozen sign conventions)

| metric | Agent Arena | prompt-only | difference (frozen sign) |
|---|---|---|---|
| accuracy (all 27) | 1 | 0.8889 | AA − PO = **0.1111** |
| Brier top-label (VALID) — primary | 0.0093 | 0.0814 | PO − AA = **0.0721** |
| ECE 5-bin (all 27) — secondary | 0.0896 | 0.0811 | — |
| mean reported confidence (all 27) | 0.9104 | 0.8959 | — |
| confidence-valid coverage | 1.0000 | 1.0000 | — |
| parser completion | 27/27 | 27/27 | — |
| high-confidence errors (≥0.8) | 0 | 1 | PO − AA = **1** |

> **No accuracy ceiling:** the arms differ in classification accuracy on this pilot. This is a paired development observation for this 27-case pool only — not a general advantage, and not attributed solely to the system prompt (the arms differ as whole packages).

## Paired correctness table (same 27 cases; NOT 54 independent cases)

| quadrant | count | DEV ids |
|---|---|---|
| both correct | 24 | DEV-0001, DEV-0002, DEV-0003, DEV-0004, DEV-0005, DEV-0006, DEV-0007, DEV-0008, DEV-0009, DEV-0010, DEV-0012, DEV-0014, DEV-0015, DEV-0016, DEV-0017, DEV-0019, DEV-0020, DEV-0021, DEV-0022, DEV-0023, DEV-0024, DEV-0025, DEV-0026, DEV-0027 |
| Agent Arena correct / prompt-only incorrect | 3 | DEV-0011, DEV-0013, DEV-0018 |
| Agent Arena incorrect / prompt-only correct | 0 | — |
| both incorrect | 0 | — |

## Predicted-label disagreements: 3 of 27 DEV ids

| dev_id | gold | stratum | Agent Arena | prompt-only |
|---|---|---|---|---|
| DEV-0011 | overclaim | clear | overclaim | correlation_vs_causation |
| DEV-0013 | overclaim | development_only | overclaim | mechanism_vs_evidence |
| DEV-0018 | overclaim | clear | overclaim | mechanism_vs_evidence |

## High-confidence errors (incorrect with VALID confidence ≥ 0.8)

- **Agent Arena**: 0
- **prompt-only**: 1
  - DEV-0013 — predicted `mechanism_vs_evidence`, gold `overclaim`, development_only, conf 0.92

## By gold label — ALL 27 (all four labels visible)

| gold label | AA acc | AA Brier | PO acc | PO Brier | flag |
|---|---|---|---|---|---|
| solid (n=8) | 1 | 0.0126 | 1 | 0.0119 |  |
| overclaim (n=15) | 1 | 0.0072 | 0.8000 | 0.1377 |  |
| correlation_vs_causation (n=2) | 1 | 0.0104 | 1 | 0.0044 | small_n/descriptive-only |
| mechanism_vs_evidence (n=2) | 1 | 0.0104 | 1 | 0.0144 | small_n/descriptive-only |

## By stratum (clear / development_only / borderline; reported separately)

| stratum | AA n | AA correct | PO n | PO correct |
|---|---|---|---|---|
| clear | 26 | 26 | 26 | 24 |
| development_only | 1 | 1 | 1 | 0 |
| borderline | 0 | 0 | 0 | 0 |

## Fixed-threshold selective behavior (clear stratum; frozen τ grid)

_Reporting the pre-declared risk–coverage curve; no threshold is chosen or tuned on these results. coverage_lost_all = 1 - coverage_all (fixed; no tunable cost ratio). Any point showing benefit is development-selected and NOT an unbiased operating guarantee._

| τ | AA cov | AA sel-acc | AA cost | AA benefit | PO cov | PO sel-acc | PO cost | PO benefit |
|---|---|---|---|---|---|---|---|---|
| 0.0 | 1.0000 | 1 | 0.0000 | 0 | 1.0000 | 0.9231 | 0.0000 | 0.0000 |
| 0.1 | 1.0000 | 1 | 0.0000 | 0 | 1.0000 | 0.9231 | 0.0000 | 0.0000 |
| 0.2 | 1.0000 | 1 | 0.0000 | 0 | 1.0000 | 0.9231 | 0.0000 | 0.0000 |
| 0.3 | 1.0000 | 1 | 0.0000 | 0 | 1.0000 | 0.9231 | 0.0000 | 0.0000 |
| 0.4 | 1.0000 | 1 | 0.0000 | 0 | 1.0000 | 0.9231 | 0.0000 | 0.0000 |
| 0.5 | 1.0000 | 1 | 0.0000 | 0 | 1.0000 | 0.9231 | 0.0000 | 0.0000 |
| 0.6 | 1.0000 | 1 | 0.0000 | 0 | 1.0000 | 0.9231 | 0.0000 | 0.0000 |
| 0.7 | 1.0000 | 1 | 0.0000 | 0 | 1.0000 | 0.9231 | 0.0000 | 0.0000 |
| 0.8 | 1.0000 | 1 | 0.0000 | 0 | 0.8846 | 1 | 0.1154 | 0.0769 |
| 0.9 | 0.6923 | 1 | 0.3077 | 0 | 0.6923 | 1 | 0.3077 | 0.0769 |
| 1.0 | 0.0000 | — | 1.0000 | — | 0.0000 | — | 1.0000 | — |

> Paired outcomes on identical cases: a difference reflects the two packages' behavior on the *same* item, not two independent samples. n is far too small (27; corr/mech at n=2) for any universal-superiority claim. The 54 predictions are never pooled into a 54-case benchmark and no pooled score is computed.
