# Phase 6.1 — Calibration Protocol (frozen preparation spec)

**Governance:** Level 2. **All definitions below are frozen before any Phase 6.2
result is generated or viewed.** Development material only; the sealed holdout is
never opened. No metric, bin, or threshold may be altered after seeing the numbers
it produces (§14).

Scope reminder — the development pool aggregate is frozen at **27** cases (solid 8 ·
overclaim 15 · correlation_vs_causation 2 · mechanism_vs_evidence 2); identity-level
membership is private and pending curator provisioning (see
`development_pool_freeze.md`). correlation/mechanism are at **n = 2** — treat all
per-label calibration for those two labels as *diagnostic only* (§12–13).

---

## 1. Correctness definition (frozen)

For one `(case, model, run)` prediction:

- `correct = 1` iff `detected_label == gold_label` under the frozen four-label
  taxonomy; else `0`.
- Parsing/label extraction uses the existing evaluator/checker unchanged. A
  prediction that fails to parse a label is **not** silently scored: it is
  `label = None` and handled as a **coverage failure** (§7, §9), never counted as
  incorrect-with-confidence unless a VALID confidence accompanies a parsed label.
- Correctness is only paired with confidence when the confidence is **VALID**
  (`confidence_semantics.md §3`).

## 2. Confidence validity (frozen — reference)

Per `confidence_semantics.md`: VALID = numeric, non-bool, non-NaN/Inf, in
`[0.0, 1.0]`. MISSING/INVALID are excluded from calibration and reported as an
explicit tally. **No coercion to 0.0.** Enforced by `confidence_validity.py`.

## 3. Missing-confidence handling (frozen)

MISSING/INVALID confidences are removed from the calibration sample and reported as:
`n_excluded_missing`, `n_excluded_invalid`, and the resulting `n_calibration`
(VALID-with-parsed-label). Every downstream metric states the `n` it was computed
on after these exclusions.

## 4. Fixed binning strategy (frozen)

The development pool is only 27 cases, so ten primary bins would be too sparse and
unstable. The reliability presentation is therefore frozen as:

- **Primary reliability presentation:** fixed-width, **5 equal bins** over
  `[0.0, 1.0]`: `[0.0,0.2), [0.2,0.4), [0.4,0.6), [0.6,0.8), [0.8,1.0]` (last bin
  closed on the right). Bin assignment is deterministic; `1.0` falls in the last bin.
- **Ten-bin view is a pre-specified *sensitivity view only*** (`[0.0,0.1), …,
  [0.9,1.0]`), reported alongside but never the headline.
- Bins are **fixed by definition**, not data-adaptive, and are **not re-chosen after
  seeing results** (§14).
- Per bin, report: **bin count `n`**, **mean confidence**, **empirical accuracy**,
  and **absolute gap** `|accuracy − mean confidence|`.
- **Do not interpret an individual bin with `n < 5`.** Empty bins (`n = 0`) remain
  **explicitly visible**, never interpolated or hidden.

## 5. Primary probabilistic score — Brier (frozen)

- **Brier is the primary overall probabilistic scoring metric**, defined as a
  **binary top-label correctness score**:

  ```
  brier = mean( (reported_confidence − correctness_indicator)^2 )
  ```

  over the VALID calibration sample, per model, where
  `correctness_indicator = 1` when the primary predicted label equals gold and `0`
  otherwise (the correctness of §1), and `reported_confidence` is the single scalar
  confidence the model attaches to its **selected primary label**. Reported with `N`.
- **No multiclass Brier.** The system emits **one scalar confidence for the selected
  primary label, not a complete normalized four-label probability vector.** A
  multiclass Brier is therefore **out of scope for Phase 6** and is neither described
  nor computed here; introducing one would require a full normalized probability
  vector added in a **separately approved future phase**.
- Small-sample caveat (§13) applies: reported as characterization, not a validated
  guarantee.

## 6. Expected Calibration Error — ECE (frozen, secondary/descriptive)

- **ECE is secondary and explicitly descriptive**, subordinate to Brier. **ECE** =
  Σ_b (n_b / N) · |acc_b − conf_b| over the **5 primary bins** (with the 10-bin
  version reported only as a sensitivity view); `N = n_calibration`.
- **Mandatory caveat:** with `N` this small and sparse bins, ECE is a
  **high-variance, low-precision** descriptor, reported **with `N`, per-bin `n`, and
  an explicit "indicative, not validated" statement**. No ECE threshold is used to
  assert "well-calibrated" in Phase 6.
- Reported per model, and (where `n` permits) per clear-stratum; **never** claimed
  per-label for correlation/mechanism (n = 2) — those are descriptive only (§13).

## 7. Accuracy by confidence range (frozen)

- Report empirical accuracy within each fixed bin (the reliability table), with
  per-bin `n` and (where `n ≥ 5`) a Wilson 95% interval; bins with `n < 5` show the
  point value **flagged as underpowered**, no interval implied as reliable.
- A reliability diagram (confidence vs accuracy, with the identity line) is produced
  per model, annotating per-bin `n`.

## 8. Selective accuracy and coverage (frozen)

For a confidence threshold `τ ∈ [0,1]` (abstain if `confidence < τ`):
- **coverage(τ)** = fraction of predictions with `confidence ≥ τ` (among
  VALID-with-label predictions).
- **selective accuracy(τ)** = accuracy among the covered predictions.
- The full **risk–coverage curve** (risk = 1 − selective accuracy) is reported over
  a pre-declared τ grid `{0.0, 0.1, …, 1.0}`. Thresholds are swept for *reporting
  the curve*, not tuned to a target (§14).

## 9. Abstention cost (frozen — reference)

Abstention is evaluated, never assumed beneficial. Its rule and cost accounting are
frozen in `abstention_policy.md`: every abstention reports both the **benefit**
(error reduction on covered items) and the **cost** (coverage lost / cases not
answered). A coverage failure (unparsed label) is accounted as an involuntary
abstention in the coverage denominator.

## 10. Class-imbalance handling (frozen)

- The dev pool is imbalanced (overclaim 15 vs correlation 2 / mechanism 2). All
  accuracy-type metrics are reported **both** micro (pooled) **and** macro (mean of
  per-label values over labels with `n ≥ a declared minimum`, §12).
- Per-label metrics for labels below the minimum-`n` are shown as **diagnostic,
  underpowered** and excluded from any headline/macro summary.
- No resampling/reweighting is applied to change the reported empirical values;
  imbalance is disclosed, not "corrected" silently.

## 11. Clear vs borderline reporting (frozen)

- **Standard calibration metrics are computed on CLEAR cases only.**
- **Borderline** cases are a **separate stratum**, reported on their own as a
  divergence probe; they never enter the headline calibration numbers.
- The two strata are never pooled into a single headline figure.

## 12. Development-only reporting (frozen)

- The **development-only** case(s) form their **own explicitly labelled stratum**,
  reported separately and excluded from headline calibration metrics.

## 13. Minimum sample-size disclosures (frozen)

- **Declared minimum for any per-label headline/macro figure: `n ≥ 5`.** Labels
  below this (correlation = 2, mechanism = 2) are reported only as flagged
  diagnostics and excluded from macro summaries.
- Every metric prints its `n`. Every reliability bin prints its `n`. Any figure
  computed on `n < 5` carries an explicit "underpowered / indicative only" flag.
- The report states up front that the whole exercise is **small-sample calibration
  characterization**, not a validated calibration guarantee, and that the 16-case
  holdout (unopened) is an integrity test, not a broad-claim basis.

## 14. Prohibition on threshold optimization then unbiased-eval reuse (frozen)

- Thresholds, bins, metrics, and criteria are **fixed here, before results.**
- The τ grid and bins are swept **only to report curves/tables**, never to select a
  threshold that is then reported as if it were an unbiased evaluation on the same
  data. If a specific operating threshold is ever chosen from a development
  risk–coverage curve, it is disclosed as **development-selected** and may **not**
  be presented as an unbiased performance estimate; an unbiased estimate would
  require separate, pre-registered data (Level 3, out of Phase 6 scope; the sealed
  holdout stays sealed).
- No metric/bin/threshold defined above may be changed after its value is observed.

## 15. Reproducibility (frozen)

- Every Phase 6.2 numeric output is bound by a **result manifest** to: the private
  development-manifest fingerprint (SHA-256), the code commit, the parameter set
  (bins, τ grid, min-`n`), and a fixed seed. Results must reproduce from the
  manifest. Determinism of the metric code is covered by tests in this phase where
  the logic is pool-independent.
