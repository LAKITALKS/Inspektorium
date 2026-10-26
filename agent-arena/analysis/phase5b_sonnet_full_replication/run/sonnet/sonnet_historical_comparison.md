# Phase 5B Haiku Full Replication — Historical Reference Comparison

- Model: `claude-sonnet-4-5-20250929`
- Design: `historical_reference_replication_not_simultaneous_randomized_ab`
- Expected slots per condition: **420**
- Historical terminal/classification/calibration: **420 / 420 / 420**
- Prospective terminal/classification/calibration: **420 / 420 / 420**

## Metrics

| Metric | Historical old prompt | Prospective corrected prompt | Difference |
|---|---:|---:|---:|
| Unit-level modal accuracy | 0.7738095238095238 | 0.8333333333333334 | 0.059523809523809534 |
| Response-level accuracy | 0.7785714285714286 | 0.8333333333333334 | 0.05476190476190479 |
| Brier | 0.20126261904761905 | 0.14901999999999999 | -0.052242619047619065 |
| ECE (5 bins) | 0.16830952380952383 | 0.10242857142857144 | -0.06588095238095239 |
| Targeted-19 modal accuracy | 0.5789473684210527 | 0.8421052631578947 | 0.26315789473684204 |
| Remaining-65 modal accuracy | 0.8307692307692308 | 0.8307692307692308 | 0.0 |

## Interpretation boundary

The prospective corrected-prompt run differs from the historical old-prompt reference; prompt condition, stochastic variation, and temporal provider/runtime effects are all potential contributors. Prompt-only causal attribution is prohibited.
