# Inspektorium 0.2.0 — release closeout (2026-10-26)

Inspektorium 0.2.0 is the single current release of the instrument. It ships
the root distribution `inspektorium` 0.2.0 and the audit runtime distribution
`agent-arena` 1.0.2 (the Inspektorium audit runtime; internal/former name
Agent Arena, retained in package, module and folder names for provenance).
The maintainer decided and authorized this release on 2026-10-26; see
[AGENTS.md](../../AGENTS.md#current-authorization). This record lists only
checks that were executed for this release.

## Identities

| Item | Value |
| --- | --- |
| Starting point | `main` at `43f29a985b6ebda0d08aebc5875bab0e82d4222c` (PR #2) |
| Pull request | [PR #3](https://github.com/LAKITALKS/Inspektorium/pull/3), regular merge |
| Branch commits | `c820d01b48fa9dbb7e51a2796920573714832786` (presentation); `b42a8b6ec00ba96b360567121d7705a995aef4bc` (runtime folder); `8c655d77d763bb3486a55213f58e3bd5d39c1be7` (license); `325b1bb793488e6fc782dc95a17a7cc9ac8f9304` (versions and changelog) |
| Merge commit | `d010e81fa46363e109f3dbc11d60fda95b0e7e11` |
| Tag | annotated `v0.2.0` (object `35fd5bf8840ea1744df4aa50b3f2a2d607fe491c`) on `d010e81fa46363e109f3dbc11d60fda95b0e7e11`, tagger Lazaros Varvatis |
| Release | [Inspektorium 0.2.0](https://github.com/LAKITALKS/Inspektorium/releases/tag/v0.2.0), Latest, published 2026-10-26T21:36:04Z |
| CI on PR #3 | [run 40400986436](https://github.com/LAKITALKS/Inspektorium/actions/runs/40400986436): 6/6 jobs passed |
| CI on merge commit | [run 40403300527](https://github.com/LAKITALKS/Inspektorium/actions/runs/40403300527): 6/6 jobs passed |

No separate `agent-arena-v1.0.2` tag was created.

## Release assets

Built from the tagged merge commit in a fresh clone and fresh build
environment (Python 3.12.14, build 1.6.1, hatchling 1.32.4, setuptools 84.2.1, wheel 0.48.0, `--no-isolation`, `SOURCE_DATE_EPOCH` = commit
time).

| Asset | Bytes | SHA-256 |
| --- | --- | --- |
| `inspektorium-0.2.0-py3-none-any.whl` | 42,746 | `5e557719c7459e8d7413d2b1f212c68d12cae737e96ae6b8ffe3c0e2c57c7955` |
| `inspektorium-0.2.0.tar.gz` | 32,549,192 | `0cbe9098ffcbb4b75a9c235c2c851b9a51f529708e4746835970f62a1558cd63` |
| `agent_arena-1.0.2-py3-none-any.whl` | 489,276 | `f1fb40df47171afcf19d4cd2a96477278c68e81228b4bf192370780f5b988ca6` |
| `agent_arena-1.0.2.tar.gz` | 29,408,676 | `97d3ea6351a23ffb44c5c43ceb5dbc2bc783ae9bf3aa3de96762f4f9726467e7` |

`SHA256SUMS.txt` (SHA-256 `3a5812340d956fe95f4e3a4498949d6fa71308872a52ef4d65dd8ffff2a42637`) lists the four package assets.

## Checks

All evaluation runs used Python 3.12.14 on macOS arm64 with the repository's
Python socket guard armed (canary passed) and `PIP_NO_INDEX=1`, and without
provider credentials. The guard covers Python socket operations only, not
native or OS-wide traffic. Dependency and build-backend downloads happened
in separate setup steps before the guarded runs.

### Local, before the merge (branch head `325b1bb`, same tree as the merge commit)

| Check | Result |
| --- | --- |
| Root Ruff (`ruff check .`) | passed |
| Root Mypy strict (`mypy src`, 20 source files) | passed |
| Root pytest with coverage | passed: 1,363 passed, 0 failed; total coverage 97.90% (threshold 80%) |
| Audit runtime environment-binding tests | passed: 2 passed |
| Audit runtime full suite (`python -m pytest tests`) | passed: 2,560 passed, 0 failed, 2 warnings. Reference run on unchanged `main` `43f29a9`: 2,560 passed |
| P10 acceptance (`scripts/phase10_acceptance.py`) | passed: 21/21 |
| Scoped release Ruff and `compileall` (runtime) | passed |
| Build with the declared minimum backends | hatchling 1.26.0 built the wheel but wrote no `License-Expression`, so the minimum was raised to 1.27; hatchling 1.27.0 and setuptools 77.0.3 then wrote `License-Expression: Apache-2.0` |
| Package contents of all four archives | passed: Apache LICENSE and NOTICE present; no `.pyc`, `.DS_Store`, virtual environments, moved datasets or launchers; no checkout paths. The runtime sdist keeps its historical evidence, which includes temporary paths and one log with the maintainer's local user name, as in 1.0.1 |
| Comparison with the published `agent_arena-1.0.1` assets | passed: the wheel differs only in `agent_arena/__init__.py`, the license files and the metadata; the sdist differs also in the edited documents, `MANIFEST.in`, `pyproject.toml` and the version test |
| Root wheel alone, `inspektorium audit --help` | passed: exit 2, empty stdout, joint-install hint |
| Installed workflow (`scripts/verify_instrument.py`) from branch-built wheels | passed: 40/40 checks |
| Installed workflow from branch-built sdists | passed: 40/40 checks |
| README installation and workflow from a clean clone | passed: validate, run, inspect, release and inspect of the released revision; reference report 05 byte-identical |
| Relative links in the 18 changed Markdown files | passed: 317 links, 0 broken |

### CI

| Run | Result |
| --- | --- |
| [PR #3, `325b1bb`](https://github.com/LAKITALKS/Inspektorium/actions/runs/40400986436) | passed: 6/6 jobs (instrument, core and arena on Python 3.11 and 3.12) |
| [Merge commit, `d010e81`](https://github.com/LAKITALKS/Inspektorium/actions/runs/40403300527) | passed: 6/6 jobs |

### Release assets and public counter-check

| Check | Result |
| --- | --- |
| Release assets built from `d010e81`, installed in a fresh environment | passed: `verify_instrument.py` 40/40 |
| Anonymous fresh clone | passed: `main` = `d010e81`; `v0.2.0` → `d010e81`; `v0.1.0` (object `648e24a`), `v0.1.1` (`cee18b1`) and `agent-arena-v1.0.1` (`2130059`) unchanged |
| Anonymous download of the five assets | passed: `shasum -c SHA256SUMS.txt` OK for all four packages; every file byte-identical to the local release build; GitHub asset digests equal |
| Downloaded wheels installed in a fresh environment | passed: `verify_instrument.py` 40/40 (positive and negative run `READY_FOR_RELEASE`, unknown run exit 2 / `REVIEW_REQUIRED`, ten byte-identical `inspektorium inspect` reference outputs, `pip check`); separate manual run of the unknown example: exit 2, `REVIEW_REQUIRED`, inspect valid |
| Downloaded sdists installed in a fresh environment | passed: 40/40 |
| Release pages read without sign-in | passed: v0.2.0 is Latest; agent-arena-v1.0.1 is a pre-release with its new title; 13/13 links in the notes return 200; every remaining "attached" statement refers to an existing asset; Agent Arena appears only as the explained internal name |
| README of `main` | passed: 34 relative links resolve, 5 absolute links return 200; `python -m pip install . ./agent-arena` and the first offline commands work from the anonymous clone |

Every guarded run had 0 refused socket operations.

### Not executed

- Live provider calls, paid runs and new live validation (excluded by the order).
- Local runs on Python 3.11 (covered only by CI).
- Full-source runtime lint (historical baseline of 368 findings) and a strict
  type check of the runtime (none established).

## License change

- `LICENSE` in the root and in `agent-arena/` is the unchanged official Apache
  License 2.0 text (SHA-256
  `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`, equal to
  apache.org's `LICENSE-2.0.txt` and to three independent package copies).
- `NOTICE` in the root and in `agent-arena/` names the copyright holder, the
  scope (own code and documentation from 0.2.0) and that v0.1.0, v0.1.1 and
  agent-arena-v1.0.1 remain under PolyForm Noncommercial 1.0.0, as published.
  Quoted third-party texts, source excerpts, dependencies and rendering tools
  keep their own rights. A scan for license files, SPDX headers and copyright
  notices found no file with a license of its own.
- Both `pyproject.toml` files declare `license = "Apache-2.0"`; wheels carry
  `License-Expression: Apache-2.0` with LICENSE, NOTICE and AUTHORS.md as
  license files. Minimum build backends: hatchling 1.27, setuptools 77
  (hatchling 1.26 was tested and wrote no license expression).
- Both `CITATION.cff` files, the current documents and the rules in
  `AGENTS.md` and `CONTRIBUTING.md` state Apache-2.0. Dated historical records
  keep their original license wording; current documents add dated notes.

## File moves

All moves used `git mv`; contents are unchanged. The SHA-256 of every moved
file equals the public hash recorded for its old path in the 2026-10-26
import index. The full table is in
[agent-arena/research/README.md](../../agent-arena/research/README.md).

- `agent-arena/Dataset 2.pdf` … `Dataset 6.pdf`, `Dataset 5.json` →
  `agent-arena/research/datasets/dataset-2.pdf` … `dataset-6.pdf`,
  `dataset-5.json`;
- `agent-arena/pilot_dataset_6_cases (1).json` →
  `agent-arena/research/datasets/pilot-dataset-6-cases.json`;
- thirteen `agent-arena/run_*.py` launchers →
  `agent-arena/research/legacy-launchers/` (names unchanged). Twelve can call
  model providers; `run_study_forensics_pilot.py` uses synthetic responses.

Historical references keep the old paths, bound to commit `94eb4fc`: the
import index and other 2026-10-26 records, historical inventories under
`agent-arena/analysis/`, task notes and run records.

## Version change

`agent-arena` 1.0.2 is a license and metadata change. The only runtime source
change is `__version__ = "1.0.2"` in `agent_arena/__init__.py`; the other 73
of the 74 runtime Python files are byte-identical to agent-arena-v1.0.1. The
test that pins the package version (`test_package_version_is_1_0_2`) now
expects 1.0.2; no test that binds provenance or module hashes changed or
failed. `inspektorium` stays 0.2.0.

## Earlier releases

The previous texts were saved before editing. Tags and assets are untouched.

- **v0.1.1** — title unchanged; no longer Latest; new first line "Superseded
  by Inspektorium 0.2.0 (one instrument, Apache-2.0). This release remains
  available under PolyForm Noncommercial 1.0.0 as published." The two
  references to an attached `PUBLICATION-CLOSEOUT.md` now link to the record
  at commit `43f29a9`; the sentence on the "separate Agent Arena research
  package" now names the audit runtime and its historical component
  prerelease. Numbers and limits are unchanged.
- **agent-arena-v1.0.1** — title now "Inspektorium audit runtime 1.0.1
  (internal name Agent Arena) — historical research prerelease"; still a
  pre-release; new first line "Historical component release. The current
  instrument is Inspektorium 0.2.0."; the two references to an attached
  closeout now link to the record at `43f29a9`; the first sentence names the
  audit runtime; "strict Arena type-check" now reads "strict runtime
  type-check". Numbers and limits are unchanged.
- **v0.1.0** — unchanged.

## Deliberately unchanged

- Distribution, package, module and CLI names, the `agent-arena/` folder,
  evaluation logic and semantics. Runtime report headings that print the
  internal name are runtime code and stay unchanged.
- Historical records: `publication/2026-10-26*/`, `evidence/`,
  `RELEASE_CHECKLIST.md` (v0.1.0 checklist), the dated runtime documents
  (`agent-arena/docs/`, `V1_SCOPE.md`, `BASELINE_PHASE_0.md`) and the import
  index. Two historical logs that contain the maintainer's local user name
  stay as they are.

## Limits

Technical integrity is not scientific validation. These checks establish
installation, packaging and offline workflow behavior of the released source,
not efficacy. The scientific Final v1 gate remains **NOT MET**. No live
provider call, paid run, PyPI upload, DOI or website change was made, and
there is no new live validation; historical live evidence concerns bounded
synthetic cases on older code.
