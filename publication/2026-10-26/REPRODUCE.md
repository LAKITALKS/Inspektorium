# Offline reproduction

Run from a fresh clone. Use Python 3.11 or 3.12 and distinct environments for
the two packages. Choose new output directories. Dependency setup may use the
public package index; evaluations below require no provider key. Historical
live-launch scripts are not offline examples or permission to reopen budgets.

## Core

From the repository root, install `.[dev]` and `hatchling` in a fresh environment.
Then run `ruff check .`, `mypy src` and
`pytest --cov=inspektorium --cov-report=term-missing --cov-fail-under=80`.
Build using `python -m build --no-isolation`. For the guarded execution and
countercheck used by CI, see [the workflow](../../.github/workflows/tests.yml).
The [five examples](../../examples/) each contain JSON and Markdown expectations.

The E1 layout reproduction uses the existing
[addendum harness](../../evidence/v0.1.1/addendum-20261024-e1-layout/tools/check_addendum.py),
[87-case catalog](../../evidence/v0.1.1/addendum-20261024/catalog.json),
installed core wheel, recorded Noto fonts and renderer versions. Follow the
[layout evidence instructions](../../evidence/v0.1.1/addendum-20261024-e1-layout/README.md)
and [setup tools](../../evidence/v0.1.1/tools/). The publication image archive
contains the actual complete 2026-10-26 results and sanitized command/input
identities. The measured styles and host-control boxes are unchanged.

## Arena

From `agent-arena/`, after installing `.[dev,providers]` into a separate
environment:

```sh
python scripts/phase10_clean_reproduce.py \
  --scratch /new/scratch --output /new/results --full-suite
```

This clones the committed repository, installs a normal wheel and a separate
editable development environment, validates installed module identity, runs
canonical offline operations and the 21-case gate, then runs the full suite.
It arms a Python socket guard and checks five refusals plus a valid loopback
connection before evaluation. Setup downloads are not part of that zero-refusal
evaluation measurement. The resulting logs include all commands and exits.

For a bounded standalone gate: `python scripts/phase10_acceptance.py --output
/new/gates`. The root README and Arena README cover CLI operation. Unknown
evidence returns exit 2 / REVIEW_REQUIRED; it does not become released in the
absence of a recorded human decision.

### Public historical capture as new offline analysis

Still from `agent-arena/`, using the installed CLI:

```sh
python scripts/extract_recorded_capture.py \
  --capture analysis/c25_p9_20261011/live_retest/captures/attempt-002.json \
  --task analysis/c25_p9_20261011/live_retest/tasks/LR-01.json \
  --output /new/derived-recording
agent-arena audit run --offline \
  --task /new/derived-recording/task.json \
  --recording /new/derived-recording/recording.json \
  --output-root /new/offline-bundle
agent-arena audit inspect --bundle /path/returned/by/run
```

The derivation manifest identifies exact supplied capture/task/response bytes.
This is **recorded_offline**, not native historical authorization replay or
verification of the original provider, ledger or review history. Public INERT
authorization directories must continue to reject. The replay regression tests
use explicitly synthetic, mocked, closed histories to test product behavior.

### Older public P6 routes

From `agent-arena/`, four measured offline routes:

```sh
python analysis/phase6_3_report_prototype/build_examples.py --out-dir /new/p63
python analysis/phase6_4_prompt_only_pilot/build_artifacts.py --out-dir /new/p64-fixtures
python analysis/phase6_2_results/build_calibration_reports.py \
  --envelope-dir analysis/public_anonymized_envelopes/phase6_2_envelopes \
  --out-dir /new/p62
python analysis/phase6_4_prompt_only_results/build_paired_comparison.py \
  --agent-arena-envelope analysis/public_anonymized_envelopes/phase6_2_envelopes/haiku_result_envelope.json \
  --prompt-only-envelope analysis/public_anonymized_envelopes/phase6_4_envelopes/haiku_prompt_only_result_envelope.json \
  --out-dir /new/p64-results
```

These regenerate saved synthetic/reported evidence, not new live measurements.
The older bounded-pilot `analysis/harness_value_20260913/reproduce.py` is retained
but stops at its original parent-freeze hash on redacted public inputs. Do not
rewrite that hash and describe the resulting derivative as an original replay.

## Artifact identity

Release `SHA256SUMS.txt` files bind wheels, source archives and evidence assets.
Core wheel contains only its own 19 runtime modules; Arena wheel only its own
74 runtime modules plus package metadata. Tests/examples/tools belong in source
archives or the repository. Archive normalization may remove owner metadata;
the manifest distinguishes archive SHA changes from identical member bytes.
Fresh public download checks are reported separately in release closeout notes.
