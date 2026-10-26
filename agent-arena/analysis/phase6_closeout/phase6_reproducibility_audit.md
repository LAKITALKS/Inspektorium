# Phase 6 — Reproducibility Audit

Verifies that the deterministic generators reproduce their committed outputs, tests and lint
pass, and committed results whose generators require private envelopes are unchanged since
their commits. No private input was accessed to satisfy this audit.

## Determinism of public-fixture generators (re-run this session)

| generator | inputs | result |
|---|---|---|
| `phase6_3_report_prototype/build_examples.py` | synthetic fixtures (public) | **byte-for-byte identical** to committed `example_full_report.{json,md}`, `example_executive_summary.md`, and `fixtures/`-derived outputs |
| `phase6_4_prompt_only_pilot/build_artifacts.py` | synthetic fixtures (public) | **byte-for-byte identical** to committed `prompt_only_runtime_contract_haiku.json`, `prompt_only_system_prompt.txt` + `.sha256`, and `deterministic_fixture_outputs/` (recursive) |

Both were regenerated in an out-of-repo scratch directory and compared with `cmp`/`diff -rq`.

## Committed results whose generators require private envelopes (NOT re-run)

Per the access boundary, these were **not** regenerated (their generators read the private
result envelopes). Integrity was verified by git blob equality against their commit and by the
test suite:

| artifact set | generator | integrity check |
|---|---|---|
| `phase6_2_results/*calibration_report.*`, `cross_model_descriptive_comparison.*`, `input_integrity_report.*` | `build_calibration_reports.py` | unchanged vs commit `5349ad0` and vs HEAD (git); engine covered by `tests/test_calibration.py` |
| `phase6_4_prompt_only_results/*` | `build_paired_comparison.py` | identical to commit `605660c` (git); logic covered by `tests/test_phase6_4_paired_comparison.py` (synthetic envelopes) |

These two generators are themselves **deterministic** (no wall-clock injection; values derive
from the frozen engine + envelope provenance), as recorded in their own committed status docs
(`phase6_2_results/phase6_2_results_status.md`, `phase6_4_prompt_only_results/phase6_4_results_status.md`),
which document a byte-for-byte double-process regeneration performed at their result commits.

## Tests

| suite | result |
|---|---|
| full test suite | **1309 passed** |
| Phase 6 targeted (`test_calibration`, `test_calibrate`, `test_confidence_validity`, `test_output_contract`, `test_forensic_report`, `test_prompt_only_baseline`, `test_phase6_4_paired_comparison`, `test_packet_integrity`, `test_dev_manifest`) | **316 passed** |

## Lint

`ruff check` on all four Phase 6 generators (`build_calibration_reports.py`,
`build_examples.py`, `build_artifacts.py`, `build_paired_comparison.py`) — **clean**. No
source module was changed this session (closeout adds Markdown only), so no other file needed
linting.

## Frozen-invariant spot checks

- Phase 6.3 schema `report_schema_version` **const 6.3.0** (schema + worked example).
- Four labels unchanged: `solid · overclaim · correlation_vs_causation · mechanism_vs_evidence`
  (`dev_manifest.GOLD_LABELS`).
- `mechanism_vs_evidence` remains **biologically scoped** (`docs/study_forensics_taxonomy.md`).
- Development-pool commitment `679233c6…4332` / `AA-DEVPOOL-6100` and aggregate 8/15/2/2/27
  match the tracked public manifest.

## Verdict

**All Phase 6 outputs reproduce deterministically or are provably unchanged since commit.**
Reproducibility posture is clean.
