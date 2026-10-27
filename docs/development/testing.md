# Testing

This page explains how to run the tests, the lint and format checks and the type checks.
Results of a release are linked from [evidence](../evaluation/evidence.md#continuous-integration), not stated here.
Passing tests establish software behaviour, not scientific efficacy ([limitations](../evaluation/limitations.md#evidence-and-research-status)).

## Set up

Use Python 3.11 or newer and a fresh virtual environment in a checkout:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev,providers]"
```

The `dev` extra installs pytest, pytest-cov, Ruff, mypy, build, markdown-it-py and linkify-it-py, and the provider SDKs.
The `providers` extra installs the provider SDKs for the live paths ([pyproject.toml](../../pyproject.toml)).
Installing the SDKs authorizes no model call. No test needs a provider key or makes a provider call.
Provider tests use mocked transports or recorded responses.

## Run the tests

```sh
python -m pytest
```

Pytest runs with `--strict-config --strict-markers` and collects from `tests/`.
Run one category by path:

```sh
python -m pytest tests/unit
python -m pytest tests/integration
python -m pytest tests/acceptance
```

| Category | Path | Scope |
| --- | --- | --- |
| Unit | [`tests/unit`](../../tests/unit/) | Single modules: models, validation, normalization, fingerprints, display encoders, parsers, audit checks, gates, review and ledgers |
| Integration | [`tests/integration`](../../tests/integration/) | Command-line behaviour of `inspect` and `audit`, bundle writing and inspection, live and replay sessions with recorded data, rendering and injection resistance |
| Acceptance | [`tests/acceptance`](../../tests/acceptance/) | The five reference examples byte for byte, and frozen forensics and review outcomes |

Coverage uses branch measurement over the `inspektorium` package:

```sh
python -m pytest --cov=inspektorium
```

### Fixtures

Synthetic fixtures live in [`tests/fixtures/`](../../tests/fixtures/).
Audit fixtures that were copied from the research record are listed with source path and SHA-256 in the [fixture notes](../../tests/fixtures/audit/README.md).
Files under `tests/fixtures/audit/historical/` are byte-bound: tests compare their SHA-256 with pinned values. Never edit them.

### Display-safety suites

These suites guard the reference checker's report display and the inputs and models behind it:

| Suite | Guards |
| --- | --- |
| [`test_render_safety.py`](../../tests/unit/test_render_safety.py) | Parsed Markdown structure and visible HTML text for untrusted report text, in two markdown-it-py configurations |
| [`test_display.py`](../../tests/unit/test_display.py) | The display encoders in `inspektorium.report.display` |
| [`test_display_limits.py`](../../tests/unit/test_display_limits.py) | The bounded combining-mark rule and the visible at-sign marker |
| [`test_input_parsing.py`](../../tests/unit/test_input_parsing.py) | The strict JSON helpers and the strict `InspectionInput` parser |
| [`test_model_invariants.py`](../../tests/unit/test_model_invariants.py) | Every report-model invariant, each with exactly one rule violation |

A change to `src/inspektorium/report/` or `src/inspektorium/core/` must keep these suites green.
These modules are also bound to recorded evidence hashes ([reproducibility](../evaluation/reproducibility.md#check-that-a-later-tree-carries-the-measured-product)).
The audit workflow has its own renderers and its own injection tests in `tests/integration`.

## Frozen offline acceptance

The acceptance driver runs separately from pytest, against the installed package:

```sh
python scripts/run_acceptance.py --output /new/directory/outside/the/checkout
```

It exits 0 only when every frozen case passes. Its expectations are in [`acceptance_v1.json`](../../tests/fixtures/audit/workflow/acceptance_v1.json).
Do not edit the expectations or the hashed inputs under `examples/audit/` to make a case pass.
Details are on the [reproducibility page](../evaluation/reproducibility.md#frozen-offline-acceptance).

## Lint and format

```sh
ruff check .
ruff format --check .
```

Ruff targets Python 3.11 with line length 88 and the rule sets `B`, `E`, `F`, `I` and `UP` ([pyproject.toml](../../pyproject.toml)).
The audit runtime, its tests and its two scripts keep the runtime's historical rule set: `E4`, `E7`, `E9` and `F`.
`pyproject.toml` lists these files under `per-file-ignores`.
`src/inspektorium/core/`, `report/`, `providers/` and `evidence/` are never reformatted, because they are byte-bound to the v0.1.1 evidence package.
CI pins Ruff to the version that formatted the tree ([`ci.yml`](../../.github/workflows/ci.yml)).

Comments and docstrings in the audit runtime and its tests cite design documents such as `docs/phase8_9_conflict_addendum.md`.
These paths refer to the runtime folder of the research record ([history](../research/history.md#research-record)).

## Type checking

```sh
mypy src/inspektorium/core src/inspektorium/report src/inspektorium/providers \
  src/inspektorium/cli.py src/inspektorium/__init__.py src/inspektorium/__main__.py
python scripts/check_type_baseline.py
```

Mypy runs in strict mode for Python 3.11.
The reference checker (`core`, `report`, `providers`), `cli.py` and the package root must pass strict mode without errors.

## Type-checking baseline for the audit runtime

The audit runtime `src/inspektorium/audit/` is checked in mypy's default mode; an override in `pyproject.toml` turns the strict flags off for it.
Its known errors are recorded per file in [`scripts/type_baseline.json`](../../scripts/type_baseline.json).
[`scripts/check_type_baseline.py`](../../scripts/check_type_baseline.py) fails when a file has more errors than recorded or a new file has errors.
It also fails when it cannot match mypy's summary line, so a changed output format cannot pass silently.
Fixing errors is welcome; run the script with `--write` afterwards to record the lower count.
Type fixes must not change behavior.

The baseline was recorded for 0.3.0 with mypy 1.20.2, the version CI installs:

| Error code | Count |
| --- | ---: |
| `arg-type` | 31 |
| `union-attr` | 21 |
| `assignment` | 8 |
| `operator` | 4 |
| `var-annotated` | 4 |
| `index` | 4 |
| `import-untyped` | 1 |
| `attr-defined` | 1 |
| **Total, in 15 of 45 files** | **74** |

## Installation check

[`scripts/verify_installation.py`](../../scripts/verify_installation.py) checks a built wheel in a fresh virtual environment outside the checkout.
It verifies that the wheel ships one package and one command and that the installed modules match the source.
It runs the offline counter-checks under the Python network guard of the evidence package and compares the reference examples byte for byte.
With `--readme` it also runs the README quickstart in a new directory.
Before a release exists, `--local-release DIST` maps the release and raw URLs to the local build and checkout; every command stays as written.

```sh
python -m build --outdir dist
python3 -m venv /tmp/verify-venv
/tmp/verify-venv/bin/python -m pip install dist/inspektorium-*.whl
/tmp/verify-venv/bin/python -c "import sys; from pathlib import Path; sys.path.insert(0, 'evidence/v0.1.1/tools'); import setup_env; setup_env.install_guard(Path(sys.prefix))"
/tmp/verify-venv/bin/python scripts/verify_installation.py --repo . --output /tmp/verify --readme --local-release dist
```

## Links

```sh
python scripts/check_links.py
```

It checks every relative link and anchor in the tracked Markdown files.
`--external` also requests each web link once and reports its status.
