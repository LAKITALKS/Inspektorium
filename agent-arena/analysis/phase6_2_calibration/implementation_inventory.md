# Phase 6.2 — Implementation Inventory

Deterministic, offline, no-model-call tooling. Reuses Phase 6.1 modules where
possible; new logic is in `calibration.py`.

## Reused (Phase 6.1)
| module | role in 6.2 |
|--------|-------------|
| `confidence_validity.py` | VALID/MISSING/INVALID classification (no 0.0 coercion) |
| `dev_manifest.py` | frozen labels + aggregate (`GOLD_LABELS`, `FROZEN_AGGREGATE`) |
| `provision_dev_manifest.py` | (unchanged) private-run derivation; not invoked here |

## New (`src/agent_arena/calibration.py`)
| function | purpose |
|----------|---------|
| `validate_result_envelope` | binds records to the tracked `manifest_id` + public salted commitment; checks protocol/count/gold-aggregate; rejects canonical/BIAA/HLD/salt anywhere |
| `load_public_manifest_binding` | reads the tracked public manifest → `(manifest_id, commitment)` for the analyzer's binding check |
| `validate_result_records` | schema/gold-aggregate/label/stratum/dup/correctness/confidence validation; **gold** aggregate only, predicted labels never constrained; id-structural errors |
| `confidence_audit` | VALID/MISSING/INVALID tallies |
| `brier_top_label` | **primary** binary top-label Brier over VALID records |
| `reliability_table` | 5-bin (primary) / 10-bin (sensitivity); all bins retained |
| `ece_from_table` | **secondary** descriptive ECE |
| `assert_reliability_bins_complete` | guard: reports must retain every bin |
| `risk_coverage_curve` | costed abstention (coverage_all + coverage_valid, selective acc, benefit, cost, involuntary count) |
| `select_operating_threshold` | **raises** — encodes the no-tuning prohibition |
| `build_report` | per-model micro + macro(clear, n≥5, included/excluded stated) + strata; denominators, predicted-label distribution, confidence-coverage warning, status/provenance banner, `synthetic_fixture` flag |
| `render_report_text` | human-readable summary: DEVELOPMENT-NOT-HOLDOUT banner, provenance, denominators, all four labels, small-sample marks |

## Contracts / schemas
- `result_input_schema.json` — anonymized result records (opaque DEV ids only).
- `anonymized_result_contract.md` — private-run → engine boundary.
- `metric_definitions.md` — frozen formulas realized in code.
- `reporting_template.md` — machine + human report shape.

## Tests (`tests/test_calibration.py`, synthetic only)
validation (dup/label/stratum/out-of-range/boolean/missing-not-zero/impossible-
correct/aggregate) · exact Brier · missing/invalid excluded not coerced · 5-bin
retention incl. empty · bin-completeness guard · ECE · costed risk–coverage +
involuntary abstention · threshold-optimization prohibited · report structure/strata
· determinism · small-sample rendering.

## Determinism
Pure functions over inputs; deterministic ordering; no randomness; `build_report`
is idempotent (tested). Machine-readable dict + text renderer.

## Pending (separate authorization; NOT built/run here)
Trusted private runner execution against the 27-case manifest; live model calls;
actual results; result interpretation; any operating-threshold decision.
