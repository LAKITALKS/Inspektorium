# Reproducibility

This page explains how to recompute the published evidence.
It covers the v0.1.1 evidence package, the frozen offline acceptance, the test suite and historical evidence.
What each piece establishes is on the [evidence page](evidence.md).
Limits are listed once in [limitations](limitations.md).

All procedures here run offline. None needs a provider key.
Setup steps that download packages are named as such and run before the measured steps.

## The v0.1.1 evidence package

The package in [`evidence/v0.1.1/`](../../evidence/v0.1.1/README.md) measures the reference checker's Markdown display and input parsing.
Its README is the authoritative procedure. This section is a map of it.

### Recompute the verdicts from the recorded rows

This check needs only Python 3.11 or newer and the repository. It downloads nothing.
The aggregator reads the recorded CLI rows, measurements and network logs.
It recomputes every case verdict and the run result without trusting stored derived fields.

```sh
T=evidence/v0.1.1/tools
python3 -B $T/aggregate.py --catalog evidence/v0.1.1/catalog/catalog.json \
  --results evidence/v0.1.1/results/baseline-4bd0ba9
python3 -B $T/aggregate.py --catalog evidence/v0.1.1/catalog/catalog.json \
  --results evidence/v0.1.1/results/candidate-fae1824
```

Without `--write`, nothing is written. Compare the printed result with the [published results](../../evidence/v0.1.1/README.md#results).

### Re-run the measurement

A full re-run builds wheels, installs the renderers and a headless browser, and measures both versions again.

1. **Setup (downloads).** `setup_env.py` creates the build, tools and product environments and installs the Python network guard.
   Pass a new path for every `--venv`; the tool refuses existing targets.
2. **Offline measurement.** `canary.py`, `run_evidence.py`, `selftest.py` and `compare_versions.py` run with provider variables removed.
3. **Independent re-run.** Use `--binding no` and point every `--results` and `--out` path outside the repository.
   Then compare the new files with the published ones.

The commands and the list of fields that may differ between runs are in the package README under [Reproduction](../../evidence/v0.1.1/README.md#reproduction).
The two addenda have their own guides: [display and setup addendum](../../evidence/v0.1.1/addendum-20261024/REPRODUCE.md) and [layout follow-up](../../evidence/v0.1.1/addendum-20261024-e1-layout/REPRODUCE.md).

`setup_env.py build-wheel --commit` builds from `git archive` and needs that commit in the local clone.
The public history contains the baseline commit `4bd0ba9`.
It does not contain the candidate and addendum product commits named in the package.
For those, check module bytes instead, as described next.

### Check that a later tree carries the measured product

A wheel hash changes with any documentation change, because the wheel embeds `README.md`.
Compare module bytes instead ([wheel hashes of later commits](../../evidence/v0.1.1/README.md#wheel-hashes-of-later-commits)).
The layout follow-up records the SHA-256 of every product file of its measured commit in [`product-identity.json`](../../evidence/v0.1.1/addendum-20261024-e1-layout/results/product-identity.json).
In 0.3.0, `core`, `report` and `providers` match these hashes, and the five reference examples match at their new path under `examples/inspect/`.

```sh
python3 - <<'PY'
import hashlib, json, pathlib
identity = json.loads(pathlib.Path(
    "evidence/v0.1.1/addendum-20261024-e1-layout/results/product-identity.json").read_text())
for row in identity["files_equal_to_tested_commit"]:
    path = row["path"]
    if path.startswith("examples/"):
        path = "examples/inspect/" + path.removeprefix("examples/")
    elif not path.startswith(("src/inspektorium/core/", "src/inspektorium/report/",
                              "src/inspektorium/providers/")):
        continue
    actual = hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
    print("match" if actual == row["sha256"] else "DIFFERS", path)
PY
```

`src/inspektorium/__init__.py`, `src/inspektorium/cli.py` and `pyproject.toml` differ by design.
They carry the 0.3.0 version and the in-package audit entry.

## Frozen offline acceptance

The acceptance driver checks the audit workflow against frozen expectations.
It is separate from the development tests and from any efficacy holdout.

```sh
python -m pip install .
python scripts/run_acceptance.py --output /new/directory/outside/the/checkout
```

- The driver imports the installed `inspektorium` package. It adds no source path.
- Before any case runs, it compares the SHA-256 of every input under `examples/audit/` with the frozen values.
- Expectations and input hashes live in [`acceptance_v1.json`](../../tests/fixtures/audit/workflow/acceptance_v1.json).
- Every case uses the built-in offline recording provider. No provider call is made.
- The output directory must not exist yet. The driver writes one bundle folder per case and `results.json`.
- `results.json` holds each case's expected and actual observations, plus the SHA-256 of the expectations and of the driver.
- The exit code is 0 only when every case passes.

The [driver source](../../scripts/run_acceptance.py) lists the cases.
The audit operations it exercises are described in the [audit workflow guide](../guides/audit-workflow.md).

## Test suite

The development suite runs from an editable install:

```sh
python -m pip install -e ".[dev,providers]"
python -m pytest
```

Categories, lint and type checks are described in [testing](../development/testing.md).
Test results are software checks; [evidence](evidence.md) says what they do and do not establish.

## Behavior comparison with 0.2.0

The evidence package [`v0.3.0-behavior`](../../evidence/v0.3.0-behavior/README.md#reproduce) lists the commands that record both releases and compare their decisions.
Its tools need only the two release wheels, an export of commit `d086973` and a 0.3.0 checkout.

## Historical evidence

Historical audit bundles bind the code that produced them.
Each bundle records a code fingerprint over every `*.py` file of the installed runtime package, keyed by relative path.
It also records the installed package version.
`audit inspect` recomputes this identity under the installed code and compares it with the bound value.

Historical bundles were produced by the historical audit-runtime release, under a different package path and with different bytes.
Inspektorium 0.3.0 therefore does not verify them. Inspecting one with 0.3.0 reports it as invalid.
This is expected and says nothing about the bundle's integrity.
The binding design is explained in [architecture](../development/architecture.md#code-binding).

To check historical evidence, install the release that produced it in a fresh environment:

| Evidence | Release |
| --- | --- |
| Reference-checker 0.1.1 reports | Release [`v0.1.1`](https://github.com/LAKITALKS/Inspektorium/releases/tag/v0.1.1) |
| Audit bundles of the 2026-10-26 publication | The historical audit-runtime release 1.0.1 |
| Audit bundles of release 0.2.0 | Release [`v0.2.0`](https://github.com/LAKITALKS/Inspektorium/releases/tag/v0.2.0), both wheels |

The exact download, hash and install commands are in [history](../research/history.md#checking-historical-evidence).
The historical runtime test suite runs from the [research record](https://github.com/LAKITALKS/inspektorium-research-record/tree/record-2026-10-27); its commands are also in [history](../research/history.md#historical-test-suite).

### Recorded captures

[`scripts/extract_recorded_capture.py`](../../scripts/extract_recorded_capture.py) turns one complete primary capture into a new recorded-offline input.

```sh
python scripts/extract_recorded_capture.py --capture CAPTURE.json --task TASK.json \
  --output /new/output/directory
```

It checks the capture schema, the task identity and hash, and a successful complete response.
The new output directory receives `recording.json`, `task.json` and `derivation.json`.
`derivation.json` records the SHA-256 of the supplied capture, the task file and the recording, and lists what stays unverified.
It does not verify or recreate a historical authorization, ledger, review history or bundle.
A run on its output is a new offline analysis, not a replay of the original live run.
