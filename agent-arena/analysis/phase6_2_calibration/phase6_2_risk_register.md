# Phase 6.2 — Risk Register

| id | risk | L | I | mitigation |
|----|------|---|---|------------|
| **C-1** | **Confidence corruption** — missing/invalid confidence coerced to 0.0 biases every curve | med | **high** | VALID/MISSING/INVALID classifier; no coercion; validator rejects invalid, allows explicit null as involuntary abstention; tested (`test_missing_confidence_allowed_and_not_zero`, `test_brier_excludes_missing_and_invalid_not_coerced`) |
| **C-2** | **Identity leakage** — a canonical/BIAA id or salt reaches an output | low | **critical** | opaque `DEV-####` only; schema `additionalProperties:false` forbids canonical/BIAA/salt; engine keys outputs by dev id/class; id-free error messages |
| **C-3** | **Overfitting via threshold tuning** — picking τ/bins on the eval set then reporting as unbiased | med | high | fixed bins + τ grid pre-registered; `select_operating_threshold()` raises; no "optimal" selection in code |
| **C-4** | **Small-sample over-interpretation** — n=27 (corr/mech n=2) read as validated calibration | **high** | high | Brier primary + small-sample caveat everywhere; per-bin/per-label `n`; `n<5` flagged; corr/mech descriptive only; report header marks characterization |
| **C-5** | **Hidden truncation** — empty reliability bins dropped, implying full coverage | med | med | all bins retained; `assert_reliability_bins_complete`; renderer shows `[empty]` |
| **C-6** | **Aggregate drift** — result set not the frozen 27-case pool | med | high | per-model total + label-aggregate check against `FROZEN_AGGREGATE` (8/15/2/2) |
| **C-7** | **Abstention assumed beneficial** — coverage cost ignored | med | high | risk–coverage reports benefit **and** cost (coverage lost) + involuntary count; adoption only vs frozen criterion |
| **C-8** | **Simulated results mistaken for real performance** | med | med | synthetic fixtures explicitly labelled; no results file; report header disclaims; execution is separately authorized |
| **C-9** | **Premature execution** — running against the private manifest without authorization | low | **critical** | execution boundary documented; no runner invocation here; PENDING SEPARATE AUTHORIZATION |
| **C-10** | **Methodology drift** — changing a frozen 6.1 rule to fit tooling convenience | low | high | frozen docs unchanged; the one coverage-denominator phrasing tension is *reported* (both denominators), not silently resolved |
| **C-11** | **Gold/prediction confusion** — enforcing 8/15/2/2 on predicted labels, or reading gold composition as a prediction result | med | high | aggregate enforced on `gold_label` only; predicted never constrained; predicted distribution reported descriptively; tested (`test_predicted_distribution_may_differ_from_gold`, `test_aggregate_enforced_on_gold_not_predicted`) |
| **C-12** | **Unbound results** — a generic 27-record set accepted as if from the certified pool | med | high | envelope binds `manifest_id` + public salted commitment to the tracked manifest; analyzer verifies before accepting; canonical/BIAA/HLD/salt rejected anywhere; tested |
| **C-13** | **Accuracy erased by confidence handling** — a missing/invalid confidence dropping the classification outcome | low | med | accuracy denominator = all records; confidence metrics denominator = VALID; tested that MISSING changes brier denominator but not accuracy |

**Review:** re-read before any execution authorization; add risks surfaced during
the private run before producing numbers.
