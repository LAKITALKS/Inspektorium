# Phase 5B Haiku Full Replication — Historical Reference Comparison

- Model: `claude-haiku-4-5-20251001`
- Design: `historical_reference_replication_not_simultaneous_randomized_ab`
- Expected slots per condition: **420**
- Historical terminal/classification/calibration: **420 / 420 / 420**
- Prospective terminal/classification/calibration: **420 / 420 / 420**

## Metrics

| Metric | Historical old prompt | Prospective corrected prompt | Difference |
|---|---:|---:|---:|
| Unit-level modal accuracy | 0.7261904761904762 | 0.9285714285714286 | 0.20238095238095244 |
| Response-level accuracy | 0.7261904761904762 | 0.9285714285714286 | 0.20238095238095244 |
| Brier | 0.24007214285714287 | 0.06816047619047619 | -0.17191166666666668 |
| ECE (5 bins) | 0.21373809523809528 | 0.006952380952380932 | -0.20678571428571435 |
| Targeted-19 modal accuracy | 0.631578947368421 | 0.9473684210526315 | 0.3157894736842105 |
| Remaining-65 modal accuracy | 0.7538461538461538 | 0.9230769230769231 | 0.1692307692307693 |

## Interpretation boundary

The prospective corrected-prompt run differs from the historical old-prompt reference; prompt condition, stochastic variation, and temporal provider/runtime effects are all potential contributors. Prompt-only causal attribution is prohibited.
