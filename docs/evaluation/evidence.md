# Evidence

This page lists what was measured, where the evidence lives and what each piece establishes.
Measured values stay in their source files and in [research results](../research/results.md).
Claim IDs refer to the [claim ledger](../research/claims.md).
Limits are listed once in [limitations](limitations.md).
How to recompute each piece is on the [reproducibility page](reproducibility.md).

## Evidence classes

Inspektorium keeps four classes of evidence apart. One class cannot stand in for another.

| Class | What it is | Where |
| --- | --- | --- |
| Public offline evidence package | A frozen synthetic catalog measured on exactly identified versions, with raw rows and tools | [`evidence/v0.1.1/`](../../evidence/v0.1.1/README.md) |
| Frozen offline acceptance | Fixed audit-workflow cases with frozen expectations and input hashes | [`scripts/run_acceptance.py`](../../scripts/run_acceptance.py), [`acceptance_v1.json`](../../tests/fixtures/audit/workflow/acceptance_v1.json) |
| Software tests | The development suite and continuous integration | [`tests/`](../../tests/), [testing](../development/testing.md), [continuous integration](#continuous-integration) |
| Owner-reported and historical records | Internal studies, the internal runtime closeout and the 2026-10-26 publication checks | [Research results](../research/results.md), [history](../research/history.md) |

## What was measured

- **Reference-checker display (P12).** Whether answer, source and evaluator text in a Markdown report can forge report lines, hide warnings or break structure.
  Measured across four renderer configurations and a headless browser ([setup](../../evidence/v0.1.1/README.md#version-binding)).
- **Reference-checker input parsing (P13).** Whether ambiguous or invalid `--input` JSON is rejected before any analysis or output.
- **Visual and text residue (P12).** Whether long combining-mark runs and e-mail forms add ink inside host-control text boxes or create links.
- **Evidence tooling (P18).** Whether the setup commands refuse existing targets.
- **Audit workflow (R08–R10).** Whether recorded offline runs reach the frozen outcomes, including blocked, tampered and review-required cases.
- **Network behaviour of the measured runs.** Whether Python processes and the browser attempted network access during measurement.

No measurement here tests semantic correctness, live-model accuracy or scientific efficacy ([limitations](limitations.md#evidence-and-research-status)).

## The v0.1.1 evidence package

The package is offline and synthetic. It needs no provider and no key.
Its README states the version binding, method, criteria, results and reproduction.

| Part | Date | What it measures | Source |
| --- | --- | --- | --- |
| Main package | 2026-10-13 | Display and input parsing, baseline `4bd0ba9` against candidate `fae1824`, on the frozen catalog | [README](../../evidence/v0.1.1/README.md), [closeout](../../evidence/v0.1.1/CLOSEOUT.md) |
| Display and setup addendum | 2026-10-24 | Combining-mark and e-mail display rules on a separate catalog; setup refusal of existing targets | [Addendum](../../evidence/v0.1.1/addendum-20261024/README.md) |
| Layout follow-up | 2026-10-24 | The same separate catalog after the claim moved to its own paragraph | [Layout follow-up](../../evidence/v0.1.1/addendum-20261024-e1-layout/README.md) |

Each part keeps its raw rows, tool sources, environment pins and logs next to its summary.
Results of the main package are summarised in [research results](../research/results.md#public-v011-evidence-package).
Results of the addenda are summarised in [maintenance addenda](../research/results.md#maintenance-addenda-2026-10-24).

### What the package establishes

- For the cases in its catalogs, the measured product shows answer, source and evaluator text as data, not as report structure.
- The measured product rejects the catalog's ambiguous and invalid inputs before rendering, and leaves existing output files untouched.
- JSON reports stay byte-identical between baseline and candidate for every case both versions accept.
- The measurement chain detects its own sabotage: each run includes a self-test with deliberately broken copies.
- In the monitored runs, the Python guard refused no connection attempt, and the browser recorded and blocked every remote request.

### What it does not establish

- A detection rate, a false-alarm rate or a guarantee for other inputs, renderers or viewers.
- Semantic or scientific correctness of any evaluation.
- Anything about the audit workflow, which has its own renderers.
- Anything about the owner-reported studies.

The full list is in [limitations](limitations.md#display) and in the package's own [limits](../../evidence/v0.1.1/README.md#limits).

### Relation to 0.3.0

`src/inspektorium/core/`, `src/inspektorium/report/` and `src/inspektorium/providers/` in 0.3.0 match the recorded file hashes of the last measured product.
The five reference examples match too, at their new path under [`examples/inspect/`](../../examples/inspect/).
The [reproducibility page](reproducibility.md#check-that-a-later-tree-carries-the-measured-product) shows the check.
The package was not re-run on 0.3.0.

## Frozen offline acceptance

The acceptance driver runs fixed audit cases with recorded offline responses.
It covers full positive and negative paths, unresolved cases, and tampered reports and manifests.
It also covers stale or missing controls, hostile render input, replay inspection and invalid input.

**It establishes** that the installed workflow reaches the frozen outcome for each fixed case, with no provider call.
Each result records its actual observations next to the expectation.

**It does not establish** semantic accuracy, reviewer quality or efficacy on real cases.
See [limitations](limitations.md#audit-workflow-inspektorium-audit).

## Behavior comparison of 0.2.0 and 0.3.0

The package [`evidence/v0.3.0-behavior/`](../../evidence/v0.3.0-behavior/README.md) records the published 0.2.0 wheels and the 0.3.0 candidate with the same 79-step script.

**It establishes** that `inspect` output is byte-identical and that `audit` statuses, exit codes, findings, review obligations and release ability are identical.
The counter-checks also keep their outcomes.
Remaining differences are names, versions, the module-hash manifest and the run-dependent order of review positions.

**It does not establish** anything about cases outside the recorded examples, or about live runs.

## Software tests

The suite in [`tests/`](../../tests/) checks software behaviour: models, validation, display encoding, parsing, bundle binding, review and release.
Passing tests establish that the code behaves as its tests specify.
They do not establish scientific efficacy ([limitations](limitations.md#evidence-and-research-status)).
Test counts are not published as evidence on this page. Results of a release are in its CI runs below.

## Historical records

Earlier checks belong to the versions that produced them.

- The 2026-10-26 publication checks, the unified-entry record and the 0.2.0 release closeout are in the [research record](https://github.com/LAKITALKS/inspektorium-research-record/tree/record-2026-10-27).
  The [project history](../research/history.md#timeline) links each one.
- Owner-reported studies and the internal runtime closeout are summarised, with their labels, in [research results](../research/results.md).
- Historical bundles verify only with the release that produced them ([reproducibility](reproducibility.md#historical-evidence)).

Historical counters are not current results. No historical live evidence concerns 0.3.0.

## Continuous integration

The release candidate was checked by every CI job on its pull request: [pull request #5 checks](https://github.com/LAKITALKS/Inspektorium/pull/5/checks).
Runs on `main`, including the run of the release merge, are listed under [CI runs on `main`](https://github.com/LAKITALKS/Inspektorium/actions/workflows/ci.yml?query=branch%3Amain).
The [GitHub release](https://github.com/LAKITALKS/Inspektorium/releases/tag/v0.3.0) links the run of the tagged commit.
