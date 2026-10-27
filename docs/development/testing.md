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

## Type checking

```sh
mypy src
```

Mypy runs in strict mode for Python 3.11.
The reference checker (`core`, `report`, `providers`), `cli.py` and the package root must pass strict mode.
An override sets `ignore_errors` for `inspektorium.audit` and its subpackages.

## Type-checking baseline for the audit runtime

The audit runtime is checked against a recorded baseline, not in strict mode.

<!-- MYPY-BASELINE: filled by the coordinator -->
