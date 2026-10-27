# Behavior comparison of 0.2.0 and 0.3.0

Recorded on 2026-10-27. This package compares the published release 0.2.0 with the 0.3.0 candidate.
It checks that `inspect` output stays byte-identical and that `audit` decisions stay identical.
Only names, versions, module-hash manifests and fields that vary between two runs of the same release may differ.

## Setup

- Python 3.12.14 on macOS arm64, one fresh virtual environment per release.
- 0.2.0: the two release wheels, verified against their published SHA-256 values; examples from commit `d086973`.
- 0.3.0: the wheel built from commit `1d43c6d`; examples from the same commit.
- The Python network guard of the [v0.1.1 package](../v0.1.1/tools/netguard.py) was installed in each environment.
- [`results/environment.json`](results/environment.json) lists the wheel hashes and the guard records: every recorded process was armed, and no network operation was refused.

## Method

1. [`tools/golden.py`](tools/golden.py) records 79 steps per run.
   They cover the five `inspect` examples in JSON and Markdown, on standard output and with `--output`.
   They run `validate`, `run --offline`, `inspect`, `review` and `release` for the positive, negative, unknown and long-hostile cases, and inspect each release.
   They also record the bytes of every bundle and nine counter-checks.
2. Each release was recorded twice; 0.2.0 was recorded twice more for the position-order question below.
3. [`tools/project.py`](tools/project.py) is projection version 1, written before any 0.3.0 run.
   It keeps every decision value and masks run IDs, timestamps, run-derived fingerprints, package names, versions and the module-hash manifest.
4. [`tools/project2.py`](tools/project2.py) (version 2) adds two rules, explained below.
5. [`tools/compare.py`](tools/compare.py) compares two projections step by step; [`tools/summarize.py`](tools/summarize.py) reduces them to one hash per step.

## Results

| Check | Result | File |
| --- | --- | --- |
| `inspect` standard output, 20 steps | byte-identical | [summary](results/summary-v2.json) |
| `inspect --output` files, 10 steps | byte-identical | [summary](results/summary-v2.json) |
| `audit` exit codes and statuses, 35 steps | identical | [summary](results/summary-v2.json) |
| All 79 projected steps, projection version 2 | identical for every pairing of the two 0.2.0 and two 0.3.0 runs | [comparisons](results/comparisons.json) |
| Counter-checks (tampered report and record, live without authorization, missing and conflicting mode, duplicate keys, unknown command) | identical exit codes and statuses | [summary](results/summary-v2.json) |

### Differences under projection version 1

| Pairing | Differences | Cause |
| --- | ---: | --- |
| 0.2.0 run 1 with runs 2, 3 and 4 | 0 | — |
| 0.2.0 run 1 with 0.3.0 run 1 | 32 | The report row `code / module count` shows 74 bound modules in 0.2.0 and 45 in 0.3.0 |
| 0.3.0 run 1 with 0.3.0 run 2 | 24 | The two review positions of the reviewed unknown case appear in swapped order |

Version 2 masks the module-count row, which belongs to the module-hash manifest.
It also sorts the position blocks of a report by their masked content and renumbers them.
Each attribute stays paired with its own position, so a changed position value is still reported.
[`tools/projection_countertest.py`](tools/projection_countertest.py) alters one position value and one binding text in a copy of a recording.
Version 2 reported both altered steps, with 161 differences in total ([counter-test](results/projection-countertest.json)).

### Position order

The report lists review positions sorted by position ID, and the ID hashes the random run ID.
[`tools/order_probe.py`](tools/order_probe.py) repeated the unknown-case review 16 times per release.
In both releases the report order varies from run to run, and every report is sorted by position ID ([0.2.0](results/position-order-0.2.0.json), [0.3.0](results/position-order-0.3.0.json)).
The record keeps one fixed order in both releases.
The four 0.2.0 recordings happened to share one order; this field was therefore not yet recognized as variable in the baseline of 2026-10-27.

### Code and tests

- [`tools/logic_diff.py`](tools/logic_diff.py) compares audit-runtime modules of 0.2.0 with their 0.3.0 successors, without imports and docstrings.
  [`module_map.json`](tools/module_map.json) covers 42 of the 74 Python files of 0.2.0.
  These are the 37 modules that remain and five that moved to the research record in the last step.
  The other 32 files are the package `__init__` and the 31 modules archived first; the [migration guide](../../docs/development/migration-0.3.md#python-imports) lists all 36 archived modules.
  26 of the 37 remaining modules are identical ([logic diff](results/logic-diff.txt)).
  The others differ only in names and identifiers, the package version lookup, dead assignments and the two code-binding functions.
- [`tools/test_checks.py`](tools/test_checks.py) counts the `assert` and `pytest.raises` checks of every retained test function.
  Every function with fewer checks lost only checks of archived modules; the functions and files no longer present tested archived modules ([test checks](results/test-checks.txt)).

## Reproduce

Export the source commit of 0.2.0 (`git archive d086973`), install each release into its own virtual environment and run, for each release and run:

```sh
python -I tools/golden.py --cli VENV/bin/inspektorium \
  --inspect-examples EXAMPLES_INSPECT --audit-examples EXAMPLES_AUDIT --out RUN_DIR
python -I tools/project2.py RUN_DIR > PROJECTION_DIR/steps.json
python -I tools/compare.py PROJECTION_DIR_A PROJECTION_DIR_B
```

Then:

```sh
python -I tools/summarize.py 0.2.0-r1=P1 0.2.0-r2=P2 0.3.0-r1=P3 0.3.0-r2=P4
python -I tools/order_probe.py --cli VENV/bin/inspektorium --examples EXAMPLES_AUDIT --out DIR --runs 16
python -I tools/logic_diff.py --base BASE_EXPORT --repo .
python -I tools/test_checks.py --base BASE_EXPORT --repo .
```

The raw recordings and projections are not included; each is about 4 MB per run.
