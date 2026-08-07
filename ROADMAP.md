# Roadmap

The v0.1 boundary is defined in [SCOPE.md](SCOPE.md). This file records release
sequencing, not commitments.

## v0.0.1 — specification and reference contract

- Freeze scope and methodology.
- Define strict Pydantic data models.
- Publish a hand-authored input and ideal JSON/Markdown report pair.
- Test schema constraints without a live API.

## v0.0.2 — deterministic kernel and model layer

- Implement exact span and source-identifier validation.
- Implement deterministic SHA-256 fingerprinting and report rendering.
- Add claim-extractor and evidence-binder interfaces.
- Add exactly one provider implementation with strict parsing and safe failure.

## v0.1.0 — curated reference release

- Add the single-answer CLI.
- Add exactly five original synthetic examples.
- Add continuous integration, coverage reporting, leakage checks, and release
  documentation.
- Select and review an unmodified standard source-available non-commercial
  license before publication.

## Beyond v0.1

Any scoring proposal, additional provider, batch workflow, retrieval feature,
or user interface requires a separate design review. None is part of v0.1 and
none should be inferred from this list.

