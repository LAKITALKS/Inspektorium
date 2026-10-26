# Phase 6.4 — Agent Arena (forensic package) Haiku arm report

### DEVELOPMENT PILOT — NOT HOLDOUT
### same 27 paired development cases; one run per arm; same exact model
### package-level contrast (system prompt + response contract + parser differ together)
### descriptive small-sample analysis; no universal-superiority inference
### no threshold optimized after results; small-n label limitations (corr/mech at n=2)
### the 54 predictions are two paired outputs on 27 cases — never pooled into 54 cases
### holdout remained sealed; residual model nondeterminism possible despite temperature=0
### parser/response-contract asymmetry; the baseline's lighter response burden may favor it

- run_id: `AA-6.2-RUN-6a3b93a24af7431e`  ·  contract: `AA-RTC-6.2-HAIKU-001`  ·  model: `claude-haiku-4-5-20251001`
- generated_at (envelope provenance): `2026-08-05T07:35:06.214022+00:00`

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
protocol=6.1  run_id=AA-6.2-RUN-6a3b93a24af7431e  model=claude-haiku-4-5-20251001  prompt_contract=AA-RTC-6.2-HAIKU-001@sys_sha256=f7704fa50a7689ae56f8fc6d7a383205a5aca34d0c400be36335d6ad8abfcfd5  generated_at=2026-08-05T07:35:06.214022+00:00
abstention_cost_model: coverage_lost_all = 1 - coverage_all (fixed; no tunable cost ratio)
==============================================================================

model: claude-haiku-4-5-20251001
  clear n=26 valid=26 missing=0 invalid=0
  denominators: accuracy/n=26 brier/ece/reliability n_valid=26
  PRIMARY Brier (top-label) = 0.010   ECE (secondary) = 0.091   accuracy(all) = 1
  macro Brier (clear) = 0.010  included=['solid', 'overclaim']  excluded={'correlation_vs_causation': 'n<5', 'mechanism_vs_evidence': 'n<5'}
  predicted-label distribution (descriptive): {'solid': 8, 'overclaim': 14, 'correlation_vs_causation': 2, 'mechanism_vs_evidence': 2}
  reliability (5 fixed bins; empty bins retained):
    [0.0,0.2) n=0 conf=— acc=— gap=—  [empty]
    [0.2,0.4) n=0 conf=— acc=— gap=—  [empty]
    [0.4,0.6) n=0 conf=— acc=— gap=—  [empty]
    [0.6,0.8) n=0 conf=— acc=— gap=—  [empty]
    [0.8,1.0) n=26 conf=0.909 acc=1 gap=0.091
  per-label (clear) — all four labels retained:
    solid: n=8 acc=1 brier=0.013
    overclaim: n=14 acc=1 brier=0.008
    correlation_vs_causation: n=2 acc=1 brier=0.010 [small_n/descriptive-only]
    mechanism_vs_evidence: n=2 acc=1 brier=0.010 [small_n/descriptive-only]
  borderline n=0  development_only n=1 (reported separately)
  risk–coverage (costed; coverage_all includes involuntary abstentions):
    τ=0.0 cov_all=1.000 sel_acc=1 cost(cov_lost)=0.000 benefit=0
    τ=0.1 cov_all=1.000 sel_acc=1 cost(cov_lost)=0.000 benefit=0
    τ=0.2 cov_all=1.000 sel_acc=1 cost(cov_lost)=0.000 benefit=0
    τ=0.3 cov_all=1.000 sel_acc=1 cost(cov_lost)=0.000 benefit=0
    τ=0.4 cov_all=1.000 sel_acc=1 cost(cov_lost)=0.000 benefit=0
    τ=0.5 cov_all=1.000 sel_acc=1 cost(cov_lost)=0.000 benefit=0
    τ=0.6 cov_all=1.000 sel_acc=1 cost(cov_lost)=0.000 benefit=0
    τ=0.7 cov_all=1.000 sel_acc=1 cost(cov_lost)=0.000 benefit=0
    τ=0.8 cov_all=1.000 sel_acc=1 cost(cov_lost)=0.000 benefit=0
    τ=0.9 cov_all=0.692 sel_acc=1 cost(cov_lost)=0.308 benefit=0
    τ=1.0 cov_all=0.000 sel_acc=— cost(cov_lost)=1.000 benefit=—
```

## Descriptive by gold label — ALL 27 (all four labels visible)

| gold label | n | correct | incorrect | accuracy | Brier | flag |
|---|---|---|---|---|---|---|
| solid | 8 | 8 | 0 | 1 | 0.0126 |  |
| overclaim | 15 | 15 | 0 | 1 | 0.0072 |  |
| correlation_vs_causation | 2 | 2 | 0 | 1 | 0.0104 | small_n/descriptive-only |
| mechanism_vs_evidence | 2 | 2 | 0 | 1 | 0.0104 | small_n/descriptive-only |

## Derived descriptive (mean confidence, errors, low-conf-correct)

- high_conf_error := incorrect prediction with VALID confidence >= 0.8
- low_conf_correct := correct prediction with VALID confidence < 0.6
- _descriptive highlighting only; NOT a tuned operating threshold_

| stratum | n | correct | incorrect | mean conf | min conf | max conf |
|---|---|---|---|---|---|---|
| all_27 | 27 | 27 | 0 | 0.9104 | 0.8200 | 0.9800 |
| clear | 26 | 26 | 0 | 0.9088 | 0.8200 | 0.9800 |
| development_only | 1 | 1 | 0 | 0.9500 | 0.9500 | 0.9500 |
| borderline | 0 | 0 | 0 | — | — | — |

### Errors (all 27)

_No incorrect predictions in this arm._

### Low-confidence correct predictions (VALID conf < 0.6)

_None: no correct prediction had VALID confidence < 0.6._
