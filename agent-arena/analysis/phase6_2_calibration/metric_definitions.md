# Phase 6.2 — Metric Definitions (implement the frozen Phase 6.1 protocol)

**Governance:** Level 2. These definitions **implement** the frozen
`analysis/phase6_1_confidence_protocol/` protocol; they do not change it. Nothing
here is tuned on results. All formulas are realized deterministically in
`src/agent_arena/calibration.py`.

## Confidence validity (reused, frozen)
`classify_confidence` → VALID (finite non-bool number in `[0,1]`), MISSING
(null/empty), INVALID (bool, NaN/Inf, out of range, non-numeric). Only VALID enters
calibration; MISSING/INVALID are counted and reported, **never coerced to 0.0**.

## Correctness & gold-vs-predicted (frozen)
`correctness_indicator = 1` iff `predicted_label == gold_label`, else `0`. An
explicit `correct` field, if provided, must equal this.

**Gold distribution ≠ prediction distribution.** The frozen 8/15/2/2 aggregate is the
**gold-label** composition of the pool; the validator enforces it on `gold_label`
**only**. Predicted labels are checked to be in the vocabulary but are **never**
constrained to any distribution; the predicted-label distribution is reported
descriptively (`predicted_label_distribution`).

## Metric denominators (frozen, always reported)
- **ordinary classification accuracy** uses **all records** with valid labels,
  **regardless of confidence validity** (denominator = `n_all`);
- **Brier, reliability bins, ECE** use **only VALID-confidence records**
  (denominator = `n_valid`);
- **MISSING / INVALID** confidences are counted (`confidence_audit`) and **never**
  converted to `0.0`; a MISSING/INVALID record still contributes its classification
  outcome to accuracy but is excluded from confidence metrics;
- every subset reports `denominators = {accuracy: n_all, brier/ece/reliability:
  n_valid}` and a `confidence_coverage_warning` whenever VALID coverage `< 100%`.

## Primary — binary top-label Brier
```
brier = mean( (confidence − correctness_indicator)^2 )   over VALID records, per model
```
Single scalar confidence for the selected primary label. **No multiclass Brier**
(would require a full normalized four-label probability vector — out of scope).

## Reliability (primary = 5 fixed bins)
Bins `[0.0,0.2) [0.2,0.4) [0.4,0.6) [0.6,0.8) [0.8,1.0]` (last closed). Per bin:
`n`, `mean_confidence`, `accuracy`, `abs_gap = |accuracy − mean_confidence|`.
**Every bin is retained**, empty bins shown with `n=0` and `None` stats. Bins with
`n < 5` carry an `underpowered` flag and are not interpreted. A **ten-bin** table is
produced only as a **sensitivity** view.

## Secondary — ECE (descriptive)
`ECE = Σ_bins (n_b / N) · abs_gap_b` over the 5 primary bins (`N` = valid count),
descriptive only, reported with `N` and per-bin `n`; never used to assert
"well-calibrated".

## Accuracy by confidence range
The reliability table itself (per-bin accuracy vs mean confidence).

## Coverage / selective accuracy / abstention (costed)
For threshold `τ` on the fixed grid `{0.0,…,1.0}` (abstain if `confidence < τ`):
- `n_covered` = VALID records with `confidence ≥ τ`;
- `selective_accuracy` = accuracy among covered; `selective_risk = abstention_error_rate = 1 − selective_accuracy`;
- `benefit_vs_tau0` = baseline risk (τ=0) − selective_risk;
- **cost** = `coverage_lost_all = 1 − coverage_all`.

**Coverage denominator (documentation reconciliation — no methodology change).** The
frozen `abstention_policy.md` §1 counts MISSING/INVALID confidences as *involuntary
abstentions in the coverage denominator*, while §2/§8 phrasing says "over VALID-with-
label". The engine reports **both**: `coverage_all` (denominator = all records, the
operational coverage per §1) and `coverage_valid` (VALID-only per §8), plus
`n_involuntary_abstained`. This surfaces the phrasing tension for curator review
rather than silently choosing; no frozen rule is altered.

## Class imbalance & strata
- micro (pooled) **and** macro (mean over clear labels with `n ≥ 5`).
- correlation/mechanism at `n = 2` are **descriptive only**, excluded from macro.
- **clear** = headline; **borderline** and **development_only** reported separately,
  never pooled into the headline.

## Small-sample discipline
Every metric prints its `n`; `n < 5` flagged; whole report labelled small-sample
**characterization**, not a validated guarantee. The 16-case holdout stays sealed.

## Frozen constants (stated here and in report metadata)
- **Reliability bins (primary):** `[0.0,0.2) [0.2,0.4) [0.4,0.6) [0.6,0.8) [0.8,1.0]`
  (confidence `1.0` → last bin); ten-bin edges `0.0,0.1,…,1.0` = sensitivity only.
- **Operating-threshold grid (fixed in advance):** `τ ∈ {0.0, 0.1, …, 1.0}`.
- **Abstention cost (fixed):** `coverage_lost_all = 1 − coverage_all`; **no tunable
  cost ratio**. These constants appear in `report["params"]` (`five_bin_edges`,
  `ten_bin_edges`, `tau_grid`, `abstention_cost_model`).

## Report provenance & status (every report)
Each report embeds a `status` block: the banner `DEVELOPMENT CALIBRATION — NOT
HOLDOUT` + descriptive-small-sample + not-universal-superiority + no-threshold-
optimized; the `manifest_id` and `public_commitment`; `protocol_version`; `run_id`,
`model`, `provider`, `prompt_contract_version`, `generated_at`; the valid/missing/
invalid confidence counts and denominators; and a `synthetic_fixture` flag (true for
synthetic tests — never formatted as real performance).

## Prohibited
`select_operating_threshold()` raises — choosing/tuning a threshold on the same
result set later reported as unbiased is prohibited (`calibration_protocol.md §14`).
No other helper selects a result-dependent threshold under a different name.
