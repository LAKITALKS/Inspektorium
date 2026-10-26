# Phase 6.2 — Reporting Template

Both a **machine-readable** dict (`build_report`) and a **concise human-readable**
summary (`render_report_text`) are produced. All identifiers are opaque
(`DEV-####`) or class labels — never canonical ids.

## Report status / provenance (every report)
```
"status": {
  "banner": ["DEVELOPMENT CALIBRATION — NOT HOLDOUT",
             "descriptive small-sample analysis",
             "not evidence of universal superiority",
             "no threshold was optimized on the reported data"],
  "manifest_id", "public_commitment", "protocol_version",
  "run_id", "model", "provider", "prompt_contract_version", "generated_at",
  "synthetic_fixture": <bool>
}
"params": { primary_score, five_bin_edges, ten_bin_edges, tau_grid,
            min_label_n, expected_total, abstention_cost_model }
```

## Per-model structure
```
"models": { "<model>": {
  "headline_clear":            <subset metrics on CLEAR>,
  "stratum_borderline":        <subset metrics>,
  "stratum_development_only":  <subset metrics>,
  "micro_all":                 <subset metrics over all 27>,
  "per_label_clear": { <label>: {n, accuracy, brier_top_label, small_n, descriptive_only} },
  "macro_brier_clear", "macro_included_labels", "macro_excluded_labels": {label: reason},
  "risk_coverage_clear": [ {tau, n_covered, n_involuntary_abstained, coverage_all,
                            coverage_valid, selective_accuracy, selective_risk,
                            abstention_error_rate, benefit_vs_tau0, coverage_lost_all} ]
}}
```
Each *subset metrics* block: `n`, `n_valid`, `confidence_audit{n_total,n_valid,
n_missing,n_invalid,n_excluded}`, `confidence_valid_coverage`,
`confidence_coverage_warning`, `denominators{accuracy,brier,ece,reliability}`,
`accuracy` (all records), `brier_top_label` (VALID; primary), `reliability_5bin`
(primary), `ece_5bin` (secondary), `reliability_10bin_sensitivity`,
`predicted_label_distribution` (descriptive), `underpowered`.

Each reliability bin: `{index, low, high, n, mean_confidence, accuracy, abs_gap,
underpowered}` — **every** bin present; empty bins keep `n=0` and `None` stats.

## Human-readable summary — required elements
- the banner lines (`DEVELOPMENT CALIBRATION — NOT HOLDOUT`, …) and, for synthetic
  runs, `SYNTHETIC FIXTURE — not real Agent Arena performance`;
- provenance: `manifest_id`, `public_commitment`, `protocol_version`, `run_id`,
  `model`, `prompt_contract_version`, `generated_at`; `abstention_cost_model`;
- per model: clear `n`/valid/missing/invalid; **denominators**; a warning when
  confidence-valid coverage `< 100%`; **primary Brier**; secondary ECE; accuracy(all);
  macro Brier with included/excluded labels; predicted-label distribution;
- the 5-bin reliability table with **empty bins visible** and `[n<5]`/`[empty]` flags;
- **all four** per-label (clear) rows, `small_n/descriptive-only` tagged for `n<5`;
- borderline and development_only counts, reported separately;
- costed risk–coverage rows (coverage, selective accuracy, cost = coverage lost, benefit).

## Reporting rules (enforced)
empty bins never omitted (`assert_reliability_bins_complete`) · `n<5` flagged ·
correlation/mechanism per-label descriptive only · all four labels retained · clear
is the only headline stratum (borderline/development_only never pooled in) ·
abstention always shows benefit **and** cost · no "optimal" threshold selected
(`select_operating_threshold` raises) · no number presented as validated
performance/superiority · synthetic reports never formatted as real results.
