# v0.1.0 Release Checklist

> **Current scope — 2026-10-26:** Inspektorium core remains 0.1.1/schema 0.1.
> Agent Arena P1–P10 is now included as a separate [public research package](agent-arena/README.md).
> [Publication mapping and current checks](publication/2026-10-26/README.md)
> supersede earlier access/publication statements below. Historical numbers,
> original dates and limits remain unchanged; publication is not independent
> replication. The scientific Final v1 gate is not met. No new live calls.

Audit date: 2026-08-11

## Verified release state

- [x] Version is `0.1.0` in package code, project metadata, and citation
  metadata.
- [x] All 74 tests pass on Python 3.11.
- [x] Overall branch coverage is 88.11%; deterministic-core branch coverage is
  89.10%.
- [x] Ruff, strict mypy, Python compilation, and Git whitespace checks pass.
- [x] All five synthetic examples regenerate byte-for-byte in JSON and Markdown
  across two independent installed-package runs.
- [x] The fabricated-quotation heartbeat rejects the mismatched citation without
  substitution while preserving an unrelated valid finding.
- [x] Both the wheel and sdist build; the wheel installs in a clean environment;
  the console and module entry points run without provider credentials.
- [x] `LICENSE` is the unchanged PolyForm Noncommercial License 1.0.0 with
  SHA-256 `c0ea4a896d2c8c394b29f9427589996db826cd501c512279ff0ed3ef48fabbe5`.
- [x] `CITATION.cff` is valid YAML, names `Lazaros Varvatis`, contains
  version `0.1.0`, and contains no DOI or repository URL.
- [x] No global, trust, quality, weighted, or severity score; calibrated
  probability; ranking; or leaderboard behavior is present.
- [x] v0.1 remains source-bounded and offline-first with four relationships, five
  synthetic examples, and exactly one real provider adapter: Anthropic.
- [x] The tracked-content, history, path, credential, and public-IP scans found no
  private-system leakage or external repository imports.

## Provider integration

- [x] Initial provider integration attempts exposed request/output contract
  defects during pre-release smoke testing. The final adapter uses the current
  supported Anthropic Pydantic structured-output interface and passed one
  end-to-end integration smoke on 2026-08-11. No repair or second model request
  was used. This was an integration check, not a reliability benchmark or model-
  quality evaluation.

## Curator release items

- [x] Confirm public authorship. Current author metadata is `Lazaros Varvatis`
  in `CITATION.cff` and `pyproject.toml`.
- [x] Public GitHub destination is
  `https://github.com/LAKITALKS/Inspektorium`; GitHub Release `v0.1.0` is
  published.
- [ ] After the approved public release, archive that release and add the real
  Zenodo DOI. Do not create or reserve a DOI for a development commit.
- [ ] Set the release date in citation metadata when the release date is known.

GitHub publication is complete. Zenodo archival, DOI creation, and citation
release-date metadata remain separate curator-controlled items.

## Documentation review — 2026-09-15

The checklist above is retained verbatim from the reviewed base as a historical
record. Its audit date and measurements are not relabeled as current evidence.
Its statement that GitHub publication is complete concerns the existing
v0.1.0 release, not approval to publish this documentation change.

Base: `16f572168025c393e953e34ccad184ca577e2bd0`.
Branch: `docs/inspektorium-research-positioning-20260915`.
This review documents the current evidence-integrity kernel and a bounded
assurance research direction. Software remains 0.1.0 and schema remains 0.1.

- [x] Public v0.1 capability, owner-reported internal experiments, reported
  internal controls and planned Phases 8–10 are explicitly separated in
  [CLAIMS.md](CLAIMS.md), [RESEARCH_RESULTS.md](RESEARCH_RESULTS.md) and
  [RESEARCH_PLAN.md](RESEARCH_PLAN.md).
- [x] The semantic counterexample, finding-level gating, CLI exit-0 boundary,
  empty findings and the not_established exception are documented.
- [x] Timestamp/hash descriptions match the current implementation: JSON
  generated_at defaults to null; identical canonical source IDs/texts are
  order-invariant, while paraphrases are not hash-equivalent.
- [x] Current local verification on 2026-09-15: one public pytest run passed
  all 74 tests, including the five-example byte comparisons and mocked
  transport. Current coverage with branches enabled is 88.11% overall and
  89.10% for the deterministic core. These are new local measurements, separate
  from the historical audit above.
- [x] `ruff check .`, `mypy src` and `git diff --check` passed. The existing
  local tools were Python 3.11.7, Pydantic 2.12.5, pytest 9.0.2, pytest-cov
  7.1.0, Ruff 0.15.8, mypy 2.1.0 and Anthropic SDK 0.86.0. Mypy 2.1.0 is
  outside the declared development range (`>=1.13,<2`); this is not a freshly
  recreated dependency-constrained environment. No dependency was changed.
- [x] Tests and the existing example-05 Markdown CLI demo ran with
  `ANTHROPIC_API_KEY` removed. `PYTHONPATH=src` selected this checkout because
  the package was not installed in the available interpreter. The demo exited
  0, retained its clean finding and visibly rejected the mismatched quotation.
  No live provider request was made.
- [x] Relative document/heading links and table structure checked; full
  documentation diff reviewed. Executable source, tests, all five examples,
  workflow, LICENSE, package/CFF metadata and .gitignore match the base.
  The historical checklist above is preserved byte-for-byte.
- [x] Annotated `v0.1.0` remains object
  `648e24aecfceed2f19e02f983ad6f0f14e8d0a74`, targeting
  `a376c4019ca4e616e996f48e108a4214d78fd800`. The license SHA-256 is unchanged.
- [ ] Coordinator independently reviews the concrete diff.
- [ ] Coordinator issues APPROVE PUBLICATION for this documentation change.
- [ ] Authorized documentation publication completed.

No paid model call, new study, internal test suite, code migration, tag/release,
DOI creation, license change or deployment is part of this documentation review.
Historical CI for the base is distinct from current local verification; see
[RESEARCH_RESULTS.md](RESEARCH_RESULTS.md#public-v01-observations).

## v0.1.1 candidate — prepared 2026-10-13

The sections above are historical records and stay unchanged. This section
separates facts about the existing public state, the local preparation of the
v0.1.1 candidate and the publication steps that require the maintainer's
decision. An unchecked box means not done or not yet confirmed; nothing here is
back-dated.

### A. Existing public state (facts at preparation time)

- Public `main` is `4bd0ba9218df80a69089838f824ae0ac28881ac4` (package 0.1.0,
  schema 0.1). It is the baseline for the v0.1.1 comparison.
- Annotated tag `v0.1.0` is object `648e24aecfceed2f19e02f983ad6f0f14e8d0a74`,
  targeting `a376c4019ca4e616e996f48e108a4214d78fd800`; it stays unchanged.
- Between `a376c40` and `4bd0ba9`, no file under `src/`, `tests/` or
  `examples/` changed. The later commits changed authorship metadata,
  documentation and dependency bounds.
- The 2026-09-15 documentation review above was merged into public `main`
  (`89bf954` is an ancestor of `4bd0ba9`). Its three approval/publication boxes
  were left unchecked in that record; this candidate does not back-fill them.
- `LICENSE` SHA-256 is
  `c0ea4a896d2c8c394b29f9427589996db826cd501c512279ff0ed3ef48fabbe5`.
- Baseline checks on `4bd0ba9`, measured at the start of preparation on
  Python 3.11.7: 74 passed with 88.11% branch coverage; `ruff check .` and
  `mypy src` report no issues.

### B. Local preparation of the v0.1.1 candidate

Ticked only after the named confirmation. "Independent review" means the
separate display and parser/measurement reviews with their own counter-probes;
"clean reproduction" means the final reproduction from a fresh checkout of
`093ea02630f3a0a8790eb533a9e28220c3c89e32` (documentation commit; product files
unchanged from the tested product commit) with the built wheel installed
outside the source tree. Both are summarised in the
[closeout record](evidence/v0.1.1/CLOSEOUT.md).

- [x] Markdown display fix for line injection and comment hiding, context
  escaping, `⟦U+XXXX⟧` markers for the Unicode categories Cc, Cf, Cs, Zl and
  Zp and for code points unassigned (Cn) in the running Python's Unicode
  database, reworded citation labels and the display note, with regression
  tests in `tests/test_render_safety.py` and `tests/test_display.py`; known
  display limits documented in [CHANGELOG.md](CHANGELOG.md#known-display-limits)
  (confirmed by the independent display review, its re-check after correction
  round 1, and the clean reproduction).
- [x] Strict `--input` parsing through the shared decoder in
  `src/inspektorium/core/strict_json.py`, with rejection before any provider
  call, analysis or report output, no change to an existing output file,
  bounded error messages, and the new invariant that a verified citation
  requires a complete evidence reference; tests in
  `tests/test_cli_input_rejection.py`, `tests/test_input_parsing.py` and
  `tests/test_model_invariants.py` (confirmed by the independent parser review,
  its re-check, and the clean reproduction).
- [x] Package version 0.1.1 in `pyproject.toml`, `src/inspektorium/__init__.py`
  and `CITATION.cff`; the installed wheel reports 0.1.1; report schema remains
  0.1 and JSON field names and schema documents are unchanged (confirmed by the
  clean reproduction).
- [x] Full suite on the tested product commit
  `fae18242de35facb7c493ff18e86baff3afe2c24`: 1123 passed, 0 failed, 0 skipped,
  98.02% branch coverage (gate 80%); `ruff check .` and `mypy src` (strict, 19
  source files) report no issues. Measured in the development environment on
  Python 3.11.7 and 3.13.1, and confirmed by the clean reproduction with the
  installed wheel on Python 3.11.7, 3.12.15 and 3.13.1 (ruff 0.17.0, mypy
  1.20.2, pytest 9.1.1, pytest-cov 7.1.0).
- [x] Five examples: expected JSON, inputs and proposals byte-identical to
  `4bd0ba9`; expected Markdown changed only by the documented display and
  label changes (verified with `git diff` between
  `4bd0ba9218df80a69089838f824ae0ac28881ac4` and
  `fae18242de35facb7c493ff18e86baff3afe2c24`: the `expected_report.json`,
  `input.json` and `proposals.json` files of all five examples are unchanged;
  all five `expected_report.md` files change by the new citation labels and the
  display note, and the one of example 05 also by backslash escapes in one
  claim and two quotations). The clean reproduction regenerated all five
  examples through the installed CLI in both formats, to a file and to
  standard output: 20 of 20 byte-identical to the committed files.
- [x] Wheel and sdist build; the wheel contains only the package files plus
  metadata and the license; it installs outside the source tree, the installed
  package (not the checkout) is imported, and the console and module entry
  points run without provider credentials (confirmed by the clean
  reproduction).
- [x] Evidence package `evidence/v0.1.1/` measured on the tested product
  commit `fae18242de35facb7c493ff18e86baff3afe2c24` with catalog version 1.0
  (70 cases): candidate run `PASS`, 70 of 70 cases hold; of 280 renderings,
  224 `RENDERED_CONTROLS_INTACT`, 56 `REJECTED_BEFORE_RENDER`, 0
  `RENDERED_MANIPULATED` and 0 `NOT_EXECUTED`. Baseline run on `4bd0ba9`:
  `FAIL`, 22 of 70 cases hold and 48 fail; of 280 renderings, 83 intact, 32
  rejected, 165 manipulated and 0 not executed. Self-test in each run: 17 of
  17 scenarios and 4 of 4 label-map sanity checks as expected. The clean
  reproduction re-ran both runs and obtained byte-identical case verdicts,
  measurements, outputs and browser-request logs.
- [x] No provider or network access during the monitored runs, within the
  documented scope of the network guard: a Python socket-level hook in the
  harness process and in every CLI subprocess, and Playwright routing with a
  host-resolver rule for the browser; native code outside these paths is not
  covered. In each run 140 of 140 CLI invocations had an armed guard and the
  guard refused 0 attempts (142 guard records, all `armed`); the browser
  blocked 4 requests on the baseline (the remote image of one link case, once
  per renderer) and 0 on the candidate; the canary passed before both runs
  (5 of 5 test attempts refused in each guarded environment, loopback control
  connected, 2 of 2 remote browser requests aborted). The clean reproduction's
  own guarded test and CLI runs also recorded 0 refused attempts.
- [x] `LICENSE` byte-identical (SHA-256 above) and `v0.1.0` tag unchanged
  (confirmed by the clean reproduction).
- [x] Public file set checked for secrets, personal data, absolute local paths,
  raw control characters and internal material (clean reproduction scan of all
  tracked files). The pre-existing owner-reported pilot commit id in CLAIMS I01
  and RESEARCH_RESULTS is unchanged from `4bd0ba9`; whether it stays is part of
  the maintainer's documentation decision.
- [x] Documentation updated: [AGENTS.md](AGENTS.md),
  [CHANGELOG.md](CHANGELOG.md), README, SCOPE, CLAIMS, RESEARCH_RESULTS,
  RESEARCH_PLAN, ROADMAP, METHODOLOGY, CONTRIBUTING and CITATION.cff; the
  prepared historical-numbers decision is recorded in
  [DOCUMENTATION_DECISIONS.md](evidence/v0.1.1/DOCUMENTATION_DECISIONS.md)
  (numbers and statements checked against the measurements by the clean
  reproduction).
- [x] Local commits on branch `release/v0.1.1-candidate`: tested product
  commit `fae18242de35facb7c493ff18e86baff3afe2c24`; documentation and evidence
  commit `093ea02630f3a0a8790eb533a9e28220c3c89e32`; closeout record in the
  commit that adds [CLOSEOUT.md](evidence/v0.1.1/CLOSEOUT.md). Product files are
  unchanged after the tested product commit (verifiable with
  `git diff fae18242de35facb7c493ff18e86baff3afe2c24 <commit> -- src tests examples pyproject.toml`).

### C. Publication — pending the maintainer's decision

- [ ] Maintainer reviews the concrete diff against `4bd0ba9`, including the
  prepared historical-numbers and documentation decisions.
- [ ] Maintainer issues APPROVE PUBLICATION for v0.1.1.
- [ ] Before tagging, in the commit to be tagged: replace "Unreleased
  (candidate)" in `CHANGELOG.md` with the publication date and, if wanted, add
  `date-released` to `CITATION.cff`.
- [ ] Push the approved commit to `main` on GitHub.
- [ ] Create annotated tag `v0.1.1` on the approved commit; `v0.1.0` stays
  unchanged.
- [ ] Publish GitHub Release `v0.1.1` with the CHANGELOG notes.
- [ ] Separate decisions, not part of this candidate: package-index upload,
  Zenodo archive and DOI, and any change to
  [inspektorium.org](https://inspektorium.org).

No push, tag, release, package upload, DOI, website change or live provider
call is part of the local preparation.

## v0.1.1 maintenance follow-up — 2026-10-24

**BLOCKED for publication review.** The dated historical checklist above is
retained. Current product `403bd3f` implements the E1 raw-run bound, E2 at-sign
marker and E3 existing-target refusal. Gate R still fails its pixel criterion
in 6/75 Noto Serif and 5/75 GitHub-like cases, all on an Answer span text box;
no real failed/reportability/warning row is hit in the changed product's run.
See the [current closeout](evidence/v0.1.1/addendum-20261024/README.md),
[separate review](evidence/v0.1.1/addendum-20261024/REVIEW.md) and raw results.
The prepared publication decisions remain unapproved. No push, PR, merge,
tag, release, upload or website action follows from a local test result.


## E1 paragraph follow-up — 2026-10-24

**READY_FOR_PUBLICATION_REVIEW**, product `5ace279`. The earlier blocked
closeout above remains historical; it is superseded for current E1 acceptance
by the [layout closeout](evidence/v0.1.1/addendum-20261024-e1-layout/README.md).

- [x] Same 87 cases: 0/75 hits per visual style, 0 INVALID, no e-mail links,
  87 byte-identical JSON reports; all Answer span rows retained.
- [x] Separate focused E1 review passed after the missing-row guard correction.
- [x] 1355 tests passed, 98.04% overall coverage with branch measurement
  enabled; Ruff and mypy passed. Fresh offline installation and 10 examples pass.
- [x] E2, E3, four-mark rule, license, raw data and historical evidence preserved.
- [ ] Four prepared publication decisions: still not approved.
- [ ] Any public action: not authorized or performed.
