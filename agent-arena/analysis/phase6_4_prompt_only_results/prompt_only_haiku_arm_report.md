# Phase 6.4 — prompt-only (competent minimal package) Haiku arm report

### DEVELOPMENT PILOT — NOT HOLDOUT
### same 27 paired development cases; one run per arm; same exact model
### package-level contrast (system prompt + response contract + parser differ together)
### descriptive small-sample analysis; no universal-superiority inference
### no threshold optimized after results; small-n label limitations (corr/mech at n=2)
### the 54 predictions are two paired outputs on 27 cases — never pooled into 54 cases
### holdout remained sealed; residual model nondeterminism possible despite temperature=0
### parser/response-contract asymmetry; the baseline's lighter response burden may favor it

- run_id: `AA-6.4B-HAIKU-PROMPTONLY-f44d734f00162c03`  ·  contract: `AA-RTC-6.4-HAIKU-PROMPT-ONLY-001`  ·  model: `claude-haiku-4-5-20251001`
- generated_at (envelope provenance): `2026-08-05T22:33:07.630125+00:00`

## Parser completion & confidence validity (reported SEPARATELY from accuracy)

- parser completion: **27/27** (parser failures: **0**)
- confidence: VALID=27  MISSING=0  INVALID=0 (no missing/invalid coerced to 0.0)

_parse completion is reported separately from classification accuracy; the envelope schema marks a completed parse by a valid predicted_label._

## Denominators (frozen)

- accuracy → all records (valid labels), regardless of confidence validity
- Brier / reliability / ECE → VALID-confidence records only
- MISSING/INVALID counted, never coerced; here all 27 are VALID so every denominator = 27

## Frozen calibration engine output

```
### DEVELOPMENT CALIBRATION — NOT HOLDOUT
### descriptive small-sample analysis
### not evidence of universal superiority
### no threshold was optimized on the reported data
manifest_id=AA-DEVPOOL-6100  commitment=679233c6e8ccadf49045bd183c11e8f47d8dac3c6759eb99cc49b88026ae4332
protocol=6.1  run_id=AA-6.4B-HAIKU-PROMPTONLY-f44d734f00162c03  model=claude-haiku-4-5-20251001  prompt_contract=AA-RTC-6.4-HAIKU-PROMPT-ONLY-001  generated_at=2026-08-05T22:33:07.630125+00:00
abstention_cost_model: coverage_lost_all = 1 - coverage_all (fixed; no tunable cost ratio)
==============================================================================

model: claude-haiku-4-5-20251001
  clear n=26 valid=26 missing=0 invalid=0
  denominators: accuracy/n=26 brier/ece/reliability n_valid=26
  PRIMARY Brier (top-label) = 0.052   ECE (secondary) = 0.120   accuracy(all) = 0.923
  macro Brier (clear) = 0.049  included=['solid', 'overclaim']  excluded={'correlation_vs_causation': 'n<5', 'mechanism_vs_evidence': 'n<5'}
  predicted-label distribution (descriptive): {'solid': 8, 'overclaim': 12, 'correlation_vs_causation': 3, 'mechanism_vs_evidence': 3}
  reliability (5 fixed bins; empty bins retained):
    [0.0,0.2) n=0 conf=— acc=— gap=—  [empty]
    [0.2,0.4) n=0 conf=— acc=— gap=—  [empty]
    [0.4,0.6) n=0 conf=— acc=— gap=—  [empty]
    [0.6,0.8) n=3 conf=0.730 acc=0.333 gap=0.397  [n<5]
    [0.8,1.0) n=23 conf=0.917 acc=1 gap=0.083
  per-label (clear) — all four labels retained:
    solid: n=8 acc=1 brier=0.012
    overclaim: n=14 acc=0.857 brier=0.087
    correlation_vs_causation: n=2 acc=1 brier=0.004 [small_n/descriptive-only]
    mechanism_vs_evidence: n=2 acc=1 brier=0.014 [small_n/descriptive-only]
  borderline n=0  development_only n=1 (reported separately)
  risk–coverage (costed; coverage_all includes involuntary abstentions):
    τ=0.0 cov_all=1.000 sel_acc=0.923 cost(cov_lost)=0.000 benefit=0.000
    τ=0.1 cov_all=1.000 sel_acc=0.923 cost(cov_lost)=0.000 benefit=0.000
    τ=0.2 cov_all=1.000 sel_acc=0.923 cost(cov_lost)=0.000 benefit=0.000
    τ=0.3 cov_all=1.000 sel_acc=0.923 cost(cov_lost)=0.000 benefit=0.000
    τ=0.4 cov_all=1.000 sel_acc=0.923 cost(cov_lost)=0.000 benefit=0.000
    τ=0.5 cov_all=1.000 sel_acc=0.923 cost(cov_lost)=0.000 benefit=0.000
    τ=0.6 cov_all=1.000 sel_acc=0.923 cost(cov_lost)=0.000 benefit=0.000
    τ=0.7 cov_all=1.000 sel_acc=0.923 cost(cov_lost)=0.000 benefit=0.000
    τ=0.8 cov_all=0.885 sel_acc=1 cost(cov_lost)=0.115 benefit=0.077
    τ=0.9 cov_all=0.692 sel_acc=1 cost(cov_lost)=0.308 benefit=0.077
    τ=1.0 cov_all=0.000 sel_acc=— cost(cov_lost)=1.000 benefit=—
```

## Descriptive by gold label — ALL 27 (all four labels visible)

| gold label | n | correct | incorrect | accuracy | Brier | flag |
|---|---|---|---|---|---|---|
| solid | 8 | 8 | 0 | 1 | 0.0119 |  |
| overclaim | 15 | 12 | 3 | 0.8000 | 0.1377 |  |
| correlation_vs_causation | 2 | 2 | 0 | 1 | 0.0044 | small_n/descriptive-only |
| mechanism_vs_evidence | 2 | 2 | 0 | 1 | 0.0144 | small_n/descriptive-only |

## Derived descriptive (mean confidence, errors, low-conf-correct)

- high_conf_error := incorrect prediction with VALID confidence >= 0.8
- low_conf_correct := correct prediction with VALID confidence < 0.6
- _descriptive highlighting only; NOT a tuned operating threshold_

| stratum | n | correct | incorrect | mean conf | min conf | max conf |
|---|---|---|---|---|---|---|
| all_27 | 27 | 24 | 3 | 0.8959 | 0.7200 | 0.9500 |
| clear | 26 | 24 | 2 | 0.8950 | 0.7200 | 0.9500 |
| development_only | 1 | 0 | 1 | 0.9200 | 0.9200 | 0.9200 |
| borderline | 0 | 0 | 0 | — | — | — |

### Errors (all 27) — high-confidence errors flagged

| dev_id | predicted | gold | stratum | confidence | high_conf(≥0.8) |
|---|---|---|---|---|---|
| DEV-0011 | correlation_vs_causation | overclaim | clear | 0.75 | no |
| DEV-0013 | mechanism_vs_evidence | overclaim | development_only | 0.92 | YES |
| DEV-0018 | mechanism_vs_evidence | overclaim | clear | 0.72 | no |

### Low-confidence correct predictions (VALID conf < 0.6)

_None: no correct prediction had VALID confidence < 0.6._
