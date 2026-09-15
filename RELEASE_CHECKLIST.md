# v0.1.0 Release Checklist

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
