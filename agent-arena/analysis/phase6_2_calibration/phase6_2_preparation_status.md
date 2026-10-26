# Phase 6.2 — Preparation Status (implementation ready; execution gated)

**Governance:** Level 2. **Not a closeout** and **not** an evaluation-completion
claim. The calibration/abstention machinery is implemented and tested with synthetic
fixtures; **no real results were generated** and the private run is not executed.
Baseline: Task A committed at `f9a7e28`; Phase-5 tag `v0.8.13` → `cfb78de` unchanged.

## Audit corrections applied (this revision)
1. **Gold ≠ predicted:** the frozen 8/15/2/2 aggregate is enforced on `gold_label`
   only; predicted labels are never constrained; predicted-label distribution is
   reported descriptively.
2. **Envelope binding:** results arrive as an anonymized envelope carrying
   `manifest_id` + the frozen **public salted commitment** (+ protocol/run/model/
   prompt-contract/timestamp/count/gold-aggregate); the analyzer verifies these
   against the tracked `development_pool_public_manifest.json` before accepting
   records; canonical/BIAA/HLD ids and salt are rejected anywhere.
3. **Denominators:** accuracy uses all records regardless of confidence; Brier/
   reliability/ECE use VALID-confidence records; MISSING/INVALID counted, never
   coerced to 0.0; denominators + a `<100%` coverage warning reported.
4. **Small-n labels:** all four labels retained in machine + human output;
   correlation/mechanism (n=2) marked `small_n/descriptive_only`; macro states
   included/excluded labels and why.
5. **Frozen constants** (5 bins, τ grid, abstention-cost model) stated in docs and
   `report["params"]`; boundary tests for 0.0/0.2/0.4/0.6/0.8/1.0.
6. **Report status/provenance:** every report carries `DEVELOPMENT CALIBRATION — NOT
   HOLDOUT`, small-sample, no-universal-superiority, no-threshold-optimized, manifest
   id + commitment, protocol version, confidence counts, denominators, and a
   `synthetic_fixture` flag; synthetic reports are never formatted as real results.

## IMPLEMENTED (this session)
- **Contracts/schemas:** `result_input_schema.json` (envelope), `anonymized_result_contract.md`,
  `metric_definitions.md`, `reporting_template.md`.
- **Binding + validation:** `validate_result_envelope`, `load_public_manifest_binding`,
  `validate_result_records` (opaque ids, dup, labels/strata, impossible/inconsistent
  correctness, confidence validity without coercion, **gold** aggregate 8/15/2/2 = 27).
- **Metrics:** binary top-label **Brier (primary)**; 5-bin reliability (all bins
  retained; `1.0`→last bin) + 10-bin **sensitivity**; **ECE (secondary, valid-count
  denominator)**; accuracy(all); coverage(all+valid); selective accuracy; abstention
  error rate; **costed** abstention.
- **Reporting:** micro + macro(clear, n≥5, included/excluded) + strata; denominators;
  predicted-label distribution; status/provenance banner; deterministic machine +
  human reports; empty-bin guard; `select_operating_threshold()` raises.
- **Tests:** `tests/test_calibration.py` — 35 tests (synthetic only). Full suite
  **1123 passed**; ruff clean; determinism repeatable across processes.

## Reject/flag coverage (each tested)
duplicate opaque ids ✅ · malformed labels ✅ · confidence outside [0,1] ✅ · boolean
confidence ✅ · missing→not-0.0 ✅ · invalid→not-0.0 ✅ · unknown strata ✅ · impossible/
inconsistent correctness ✅ · totals ≠ frozen 27 / wrong **gold** aggregate ✅ · report
omitting empty bins ✅ · threshold optimization on eval set ✅ · envelope manifest/
commitment/protocol/count/aggregate mismatch ✅ · canonical id / salt in envelope ✅.

## PENDING SEPARATE AUTHORIZATION (not done here)
trusted execution against the fingerprint-verified 27-case manifest · live model
calls / paid APIs · actual results and any results file · result interpretation · any
operating-threshold decision.

## Isolation held
No access to the private manifest, salt, eligible/dev id rosters, BIAA↔canonical
mapping, `internal_only/`, or the sealed holdout. No canonical ids accessed or
inferred. No model/network calls. Frozen Phase 6.1 artifacts unchanged; Task A commit
`f9a7e28` not amended.

## Remaining execution gate
**Phase 6.2 execution is PENDING SEPARATE CURATOR AUTHORIZATION.** Preparation
completion does not authorize execution. No `phase6_2_results.*` and no closeout were
created.
