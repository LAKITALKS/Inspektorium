### DEVELOPMENT CALIBRATION — NOT HOLDOUT
### descriptive small-sample analysis
### not evidence of universal superiority
### no threshold was optimized on the reported data
manifest_id=AA-DEVPOOL-6100  commitment=679233c6e8ccadf49045bd183c11e8f47d8dac3c6759eb99cc49b88026ae4332
protocol=6.1  run_id=AA-P62-SONNET-23f5dcc25de6  model=claude-sonnet-4-5-20250929  prompt_contract=AA-RTC-6.2-SONNET-001;system_prompt_sha256=f7704fa50a7689ae56f8fc6d7a383205a5aca34d0c400be36335d6ad8abfcfd5  generated_at=2026-08-05T08:05:06.461408+00:00
abstention_cost_model: coverage_lost_all = 1 - coverage_all (fixed; no tunable cost ratio)
==============================================================================

model: claude-sonnet-4-5-20250929
  clear n=26 valid=26 missing=0 invalid=0
  denominators: accuracy/n=26 brier/ece/reliability n_valid=26
  PRIMARY Brier (top-label) = 0.075   ECE (secondary) = 0.001   accuracy(all) = 0.923
  macro Brier (clear) = 0.072  included=['solid', 'overclaim']  excluded={'correlation_vs_causation': 'n<5', 'mechanism_vs_evidence': 'n<5'}
  predicted-label distribution (descriptive): {'solid': 8, 'overclaim': 12, 'correlation_vs_causation': 3, 'mechanism_vs_evidence': 3}
  reliability (5 fixed bins; empty bins retained):
    [0.0,0.2) n=0 conf=— acc=— gap=—  [empty]
    [0.2,0.4) n=0 conf=— acc=— gap=—  [empty]
    [0.4,0.6) n=0 conf=— acc=— gap=—  [empty]
    [0.6,0.8) n=0 conf=— acc=— gap=—  [empty]
    [0.8,1.0) n=26 conf=0.922 acc=0.923 gap=0.001
  per-label (clear) — all four labels retained:
    solid: n=8 acc=1 brier=0.015
    overclaim: n=14 acc=0.857 brier=0.128
    correlation_vs_causation: n=2 acc=1 brier=0.006 [small_n/descriptive-only]
    mechanism_vs_evidence: n=2 acc=1 brier=0.006 [small_n/descriptive-only]
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
    τ=0.8 cov_all=1.000 sel_acc=0.923 cost(cov_lost)=0.000 benefit=0.000
    τ=0.9 cov_all=0.885 sel_acc=0.913 cost(cov_lost)=0.115 benefit=-0.010
    τ=1.0 cov_all=0.000 sel_acc=— cost(cov_lost)=1.000 benefit=—

## Derived descriptive (items 2 / 6 / 16 / 17 — not new frozen metrics)

- high_conf_error := incorrect prediction with VALID confidence >= 0.8
- low_conf_correct := correct prediction with VALID confidence < 0.6
- _descriptive highlighting only; NOT a tuned operating threshold_

| stratum | n | correct | incorrect | mean conf | min conf | max conf |
|---|---|---|---|---|---|---|
| all_27 | 27 | 24 | 3 | 0.9230 | 0.8000 | 0.9800 |
| clear | 26 | 24 | 2 | 0.9219 | 0.8000 | 0.9800 |
| development_only | 1 | 0 | 1 | 0.9500 | 0.9500 | 0.9500 |
| borderline | 0 | 0 | 0 | — | — | — |

### High-confidence / all errors (item 16)

| dev_id | predicted | gold | stratum | confidence |
|---|---|---|---|---|
| DEV-0011 | correlation_vs_causation | overclaim | clear | 0.92 |
| DEV-0013 | mechanism_vs_evidence | overclaim | development_only | 0.95 |
| DEV-0024 | mechanism_vs_evidence | overclaim | clear | 0.95 |

### Low-confidence correct predictions (item 17)

_None: no correct prediction had VALID confidence < 0.6 (all observed confidences lie in the top primary bin [0.8, 1.0])._
