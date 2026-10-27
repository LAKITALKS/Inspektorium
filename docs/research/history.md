# Project history

This page records where Inspektorium comes from and how its parts were released.
It is the only page that explains the former working title of the audit runtime.
It also holds the exact commands for checking historical evidence with the release that produced it.

## Origin

Inspektorium began as two lines of work by the same author.

- **The reference checker.** A small evidence-binding tool for one answer and its sources.
  It was published as `inspektorium` 0.1.0 and maintained as 0.1.1. Today it is `inspektorium inspect`.
- **The audit runtime.** A local evaluation engine developed in a separate internal project.
  Its offline workflow turns a claim and a recorded response into a checked, reviewable, explicitly released bundle.
  Today it is `inspektorium audit`, implemented by the subpackage `inspektorium.audit`.

Release 0.2.0 joined both under one name and one command.
Release 0.3.0 merges them into one Python distribution.
The research questions behind this work are in the [research plan](plan.md).

## Former working title

Until release 0.2.0, the audit runtime was developed under the working title **Agent Arena**.
The name comes from the runtime's first form.
It was a local evaluation engine in which configured agents, each a provider and a model, answered evaluation tasks as strict JSON.
An evaluator then scored each answer.
The internal Phase 0 baseline of that engine was frozen on 2026-07-01 ([baseline record][rec-baseline]).

Later phases turned the engine into the audit runtime described in [how it works](../concepts/how-it-works.md).
Until 0.2.0, the name stayed in the code for provenance:

| Identity | Former form | Form from 0.3.0 |
| --- | --- | --- |
| Python distribution | `agent-arena` | part of `inspektorium` |
| Import package | `agent_arena` | `inspektorium.audit` |
| Command | `agent-arena audit` | `inspektorium audit` |
| Repository folder | `agent-arena/` | `src/inspektorium/audit/` and `tests/` |
| Release tag | `agent-arena-v1.0.1` | none; the runtime ships with `inspektorium` |

These are earlier identities of the same instrument, not a separate product.
Dated records, archives, module paths and version fields may still carry the old name.
They are historical byte evidence and are not relabelled.
Contract identifiers such as `AA-P10/1.0` keep their original form, because evidence binds those strings.

The **runtime folder** of the research record is its `agent-arena/` folder.
Other pages, such as the [fixture notes](../../tests/fixtures/audit/README.md), refer to it by that phrase.

## Timeline

| Date | Event | Source |
| --- | --- | --- |
| 2026-07-01 | Internal Phase 0 baseline of the audit runtime | [Baseline record][rec-baseline] |
| 2026-08-11 | Release `v0.1.0`: first public reference checker, annotated tag on `a376c40` | [Release v0.1.0][rel-010] |
| 2026-09-15 | Research-positioning documentation (`89bf954`) and dependency bounds (`4bd0ba9`) on `main` | [Historical changelog][rec-changelog] |
| 2026-10-13 | v0.1.1 candidate and its evidence package prepared; internal technical 1.0.0 closeout of the runtime | [Evidence closeout](../../evidence/v0.1.1/CLOSEOUT.md), [runtime closeout][rec-v1-closeout] |
| 2026-10-24 | Display and setup addenda to the v0.1.1 evidence package | [Addendum](../../evidence/v0.1.1/addendum-20261024/README.md), [layout follow-up](../../evidence/v0.1.1/addendum-20261024-e1-layout/README.md) |
| 2026-10-26 | PR #1 (`94eb4fc`) publishes the reference checker 0.1.1 and the audit runtime 1.0.1 | [Release v0.1.1][rel-011], [release agent-arena-v1.0.1][rel-101] |
| 2026-10-26 | PR #2 (`43f29a9`) makes `inspektorium audit` the single public audit entry | [Unified-entry record][rec-unified] |
| 2026-10-26 | PR #3 (`d010e81`) releases 0.2.0 with runtime 1.0.2 under Apache-2.0 | [Release v0.2.0][rel-020] |
| 2026-10-26 | PR #4 (`d086973`) records the 0.2.0 release closeout | [0.2.0 closeout][rec-020-closeout] |
| 2026-10-27 | Research record snapshot of `d086973`, tag `record-2026-10-27` | [Research record][record] |
| 2026-10-27 | 0.3.0 consolidation: `12f0534` moves the study harness and unreached modules to the record; `fc4157f` merges the runtime into `inspektorium` | [CHANGELOG](../../CHANGELOG.md), [migration notes](../development/migration-0.3.md) |

### Releases

| Tag | Contents | Commit | License |
| --- | --- | --- | --- |
| [`v0.1.0`][rel-010] | Reference checker 0.1.0, report schema 0.1 | `a376c40` | PolyForm Noncommercial 1.0.0 |
| [`v0.1.1`][rel-011] | Reference checker 0.1.1, report schema 0.1 | `94eb4fc` | PolyForm Noncommercial 1.0.0 |
| [`agent-arena-v1.0.1`][rel-101] | Audit runtime 1.0.1, technical research prerelease | `94eb4fc` | PolyForm Noncommercial 1.0.0 |
| [`v0.2.0`][rel-020] | `inspektorium` 0.2.0 and audit runtime 1.0.2 | `d010e81` | Apache-2.0 |

Earlier releases stay under the license they were published with ([NOTICE](../../NOTICE)).
Runtime 1.0.2 changed only license and metadata; its version string is the only runtime source change against 1.0.1 ([release v0.2.0][rel-020]).
No separate tag was created for runtime 1.0.2.

### What 0.3.0 changed

- One distribution, `inspektorium` 0.3.0, declared in [pyproject.toml](../../pyproject.toml), with one command, `inspektorium`.
- The former distribution `agent-arena` and its command `agent-arena` are removed. There is no compatibility shim.
- The runtime is the subpackage `inspektorium.audit`, regrouped into `workflow`, `forensics`, `review`, `execution`, `integrity`, `checks` and `reports`.
  The [architecture page](../development/architecture.md) maps the layout.
- `src/inspektorium/core/` and `src/inspektorium/report/` are byte-identical to 0.2.0.
- The study harness, modules that the audit command no longer reaches, their tests, study records and publication logs moved to the research record.

## Research record

The archived companion repository holds the research material up to release 0.2.0:
[`LAKITALKS/inspektorium-research-record` at tag `record-2026-10-27`][record].

| Path in the record | Content |
| --- | --- |
| `agent-arena/` | The runtime folder: runtime source, full historical test suite, study records, case packs, run records, contracts and phase documents as of runtime 1.0.2 |
| `agent-arena/historical-sources/` | Snapshots of the modules that produced important evidence |
| `publication/` | Publication and verification records of 2026-10-26, including the import index |
| `historical-docs/` | The top-level documents of 0.2.0: claims, methodology, research plan and results, roadmap, scope and checklists |

`agent-arena/`, `publication/`, `LICENSE` and `NOTICE` in the record are byte-identical to commit `d086973`.
Paths in the 2026-10-26 import index therefore resolve there.
`MANIFEST.sha256` lists the SHA-256 of every other file. Verify a clone of the record with:

```sh
shasum -a 256 -c MANIFEST.sha256
```

No authorization or budget in the record is active.
The launchers in `agent-arena/research/legacy-launchers/` can call model providers and are not authorized by any release.

## Checking historical evidence

Historical evidence binds the module paths and bytes of the version that produced it.
Inspektorium 0.3.0 does not verify it; [reproducibility](../evaluation/reproducibility.md#historical-evidence) explains why.
Use the release that matches the evidence, in a fresh virtual environment with Python 3.11 or newer.

| Evidence | Release to use |
| --- | --- |
| Reference-checker 0.1.1 reports | [`v0.1.1`](#reference-checker-011) |
| Audit bundles and checks of the 2026-10-26 publication | [`agent-arena-v1.0.1`](#audit-runtime-101) |
| Audit bundles produced with the 0.2.0 release | [`v0.2.0`](#release-020) |
| Evidence of earlier internal states | No release; inspect the producing modules in `agent-arena/historical-sources/` of the [record][record] |

Bundles recorded with "installed bytes only" need just the matching wheel.
Bundles that record a verified Git source commit also need an editable install from a checkout of that commit.

### Reference checker 0.1.1

Release [`v0.1.1`][rel-011], asset `inspektorium-0.1.1-py3-none-any.whl`.
Expected SHA-256 `7191276995f9f87cb4e7a699ca020d6aa2decd844c123d97601d96fb08c0c721`.

```sh
python3 -m venv .venv-011 && . .venv-011/bin/activate
gh release download v0.1.1 --repo LAKITALKS/Inspektorium \
  --pattern 'inspektorium-0.1.1-py3-none-any.whl'
shasum -a 256 inspektorium-0.1.1-py3-none-any.whl
python -m pip install inspektorium-0.1.1-py3-none-any.whl
inspektorium inspect --help
```

### Audit runtime 1.0.1

Release [`agent-arena-v1.0.1`][rel-101], asset `agent_arena-1.0.1-py3-none-any.whl`.
Expected SHA-256 `0899b28bd3c02e97a814b7a8c43fc251ced61ab79d178f6a26ddfdf7e892ccd1`.
This release has no `inspektorium audit` entry; use the historical command.

```sh
python3 -m venv .venv-101 && . .venv-101/bin/activate
gh release download agent-arena-v1.0.1 --repo LAKITALKS/Inspektorium \
  --pattern 'agent_arena-1.0.1-py3-none-any.whl'
shasum -a 256 agent_arena-1.0.1-py3-none-any.whl
python -m pip install agent_arena-1.0.1-py3-none-any.whl
agent-arena audit inspect --bundle PATH_TO_BUNDLE
```

### Release 0.2.0

Release [`v0.2.0`][rel-020] ships two wheels. Install both together.

| Asset | Expected SHA-256 |
| --- | --- |
| `inspektorium-0.2.0-py3-none-any.whl` | `5e557719c7459e8d7413d2b1f212c68d12cae737e96ae6b8ffe3c0e2c57c7955` |
| `agent_arena-1.0.2-py3-none-any.whl` | `f1fb40df47171afcf19d4cd2a96477278c68e81228b4bf192370780f5b988ca6` |

```sh
python3 -m venv .venv-020 && . .venv-020/bin/activate
gh release download v0.2.0 --repo LAKITALKS/Inspektorium --pattern '*.whl'
shasum -a 256 inspektorium-0.2.0-py3-none-any.whl agent_arena-1.0.2-py3-none-any.whl
python -m pip install inspektorium-0.2.0-py3-none-any.whl agent_arena-1.0.2-py3-none-any.whl
inspektorium audit inspect --bundle PATH_TO_BUNDLE
```

In 0.2.0, `agent-arena audit` is a compatibility entry to the same runtime.
Runtime 1.0.2 has a different code identity from 1.0.1, so each bundle needs its own runtime version.

### Historical test suite

The full historical runtime suite runs from a clone of the [record][record], in a fresh virtual environment:

```sh
python -m pip install -e './agent-arena[dev,providers]'
cd agent-arena
python -m pytest tests
```

It needs no provider key and makes no provider call.
The current suite is described in [testing](../development/testing.md).

[record]: https://github.com/LAKITALKS/inspektorium-research-record/tree/record-2026-10-27
[rec-baseline]: https://github.com/LAKITALKS/inspektorium-research-record/blob/record-2026-10-27/agent-arena/BASELINE_PHASE_0.md
[rec-v1-closeout]: https://github.com/LAKITALKS/inspektorium-research-record/tree/record-2026-10-27/agent-arena/analysis/v1_closeout_20261013
[rec-changelog]: https://github.com/LAKITALKS/inspektorium-research-record/blob/record-2026-10-27/historical-docs/CHANGELOG.md
[rec-unified]: https://github.com/LAKITALKS/inspektorium-research-record/blob/record-2026-10-27/publication/2026-10-26-unified-entry/README.md
[rec-020-closeout]: https://github.com/LAKITALKS/inspektorium-research-record/blob/record-2026-10-27/publication/2026-10-26-v0.2.0/CLOSEOUT.md
[rel-010]: https://github.com/LAKITALKS/Inspektorium/releases/tag/v0.1.0
[rel-011]: https://github.com/LAKITALKS/Inspektorium/releases/tag/v0.1.1
[rel-101]: https://github.com/LAKITALKS/Inspektorium/releases/tag/agent-arena-v1.0.1
[rel-020]: https://github.com/LAKITALKS/Inspektorium/releases/tag/v0.2.0
