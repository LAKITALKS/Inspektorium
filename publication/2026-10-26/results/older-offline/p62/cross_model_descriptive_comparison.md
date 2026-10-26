### DEVELOPMENT CALIBRATION — NOT HOLDOUT
### SECONDARY descriptive cross-model comparison
### all three models evaluated the SAME 27 development cases
### no pooling into an 81-case benchmark; the 81 predictions are NOT independent cases
### no single pooled calibration score; no universal-superiority inference
### no threshold optimized on these results; holdout remained sealed
### model outputs may remain nondeterministic despite frozen request parameters

Models: 3 · cases per model: 27 · **the SAME 27 development cases across all three** (paired, not independent).

## Descriptive per-model summary

| metric | haiku | sonnet | opus |
|---|---|---|---|
| accuracy (all 27) | 1 | 0.8889 | 1 |
| accuracy (clear, n=26) | 1 | 0.9231 | 1 |
| Brier top-label (clear) — primary | 0.0096 | 0.0747 | 0.0098 |
| Brier top-label (all 27) | 0.0093 | 0.1053 | 0.0097 |
| ECE 5-bin (clear) — secondary | 0.0912 | 0.0012 | 0.0927 |
| macro Brier (clear; solid+overclaim only) | 0.0101 | 0.0716 | 0.0105 |
| confidence-valid coverage (all 27) | 1.0000 | 1.0000 | 1.0000 |
| mean reported confidence (all 27) | 0.9104 | 0.9230 | 0.9078 |
| errors (all 27) | 0 | 3 | 0 |
| high-conf errors (all 27) | 0 | 3 | 0 |
| selective acc @τ=0.9 (clear) | 1 | 0.9130 | 1 |
| coverage_all @τ=0.9 (clear) | 0.6923 | 0.8846 | 0.6538 |
| cost=coverage lost @τ=0.9 (clear) | 0.3077 | 0.1154 | 0.3462 |

## Cross-model disagreements (predicted label): 3 of 27 DEV ids

| dev_id | gold | stratum | haiku | sonnet | opus |
|---|---|---|---|---|---|
| DEV-0011 | overclaim | clear | overclaim | correlation_vs_causation | overclaim |
| DEV-0013 | overclaim | development_only | overclaim | mechanism_vs_evidence | overclaim |
| DEV-0024 | overclaim | clear | overclaim | mechanism_vs_evidence | overclaim |

## Paired correctness patterns (Haiku,Sonnet,Opus → 1=correct)

| pattern H,S,O | count |
|---|---|
| 1,1,1 | 24 |
| 1,0,1 | 3 |

> These are paired outcomes on identical cases: a difference reflects the two models' behavior on the *same* item, not two independent samples. n is far too small (27; corr/mech at n=2) to claim universal superiority.
