# v0.1.0 Release Checklist

Audit date: 2026-08-11

## Verified release state

- [x] Version is `0.1.0` in package code, project metadata, and citation
  metadata.
- [x] All 71 tests pass on Python 3.11.
- [x] Overall branch coverage is 87.88%; deterministic-core branch coverage is
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
- [x] `CITATION.cff` is valid YAML, names `Inspektorium contributors`, contains
  version `0.1.0`, and contains no DOI or repository URL.
- [x] No global, trust, quality, weighted, or severity score; calibrated
  probability; ranking; or leaderboard behavior is present.
- [x] v0.1 remains source-bounded and offline-first with four relationships, five
  synthetic examples, and exactly one real provider adapter: Anthropic.
- [x] The tracked-content, history, path, credential, and public-IP scans found no
  private-system leakage or external repository imports.

## Provider release gate

- [ ] Re-run one tiny synthetic Anthropic smoke after curator authorization. The
  single authorized audit call reached Anthropic but returned prose around JSON,
  which the strict parser correctly rejected. The adapter now requests native
  JSON-schema structured output and has offline contract coverage, but that fix
  has not been revalidated live.

## Curator release items

- [ ] Confirm public authorship. Current collective author metadata is
  `Inspektorium contributors` in `CITATION.cff` and `pyproject.toml`.
- [ ] Supply the final public GitHub destination, then add it consistently to
  release metadata.
- [ ] After the approved public release, archive that release and add the real
  Zenodo DOI. Do not create or reserve a DOI for a development commit.
- [ ] Set the release date in citation metadata when the release date is known.

Do not tag, push, publish, or contact Zenodo until the curator completes the
release items and the provider release gate passes.
