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
