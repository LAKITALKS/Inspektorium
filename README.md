# Inspektorium

Inspektorium is a small evidence-binding reference tool that requires
model-generated findings to point to verifiable source text.

This repository is currently at the **v0.0.1 specification phase**. It defines
the v0.1 scope, methodology, strict data contracts, and a hand-authored
reference report. The deterministic validation kernel, model integration, and
CLI are intentionally not implemented in this phase.

## Central principle

An LLM may propose a claim, an evidence relationship, and a quotation. Ordinary
deterministic code must verify that the claim and quotation occur at the stated
character offsets before the relationship can be presented as verified.

The reference fixture makes the failure behavior explicit. A model proposes
this quotation:

> On weekdays, the library closes at 8 p.m.

The supplied source says `6 p.m.` at those offsets. The report therefore keeps
`relation: "supported"` only as an inspectable proposal, sets
`validation_status: "failed"`, and sets `verified_relation: null`. It does not
repair the quotation or silently select different evidence.

See:

- [SCOPE.md](SCOPE.md) for the frozen v0.1 boundary;
- [METHODOLOGY.md](METHODOLOGY.md) for the methodological rationale;
- [examples/reference/report.json](examples/reference/report.json) for the
  machine-readable reference report;
- [examples/reference/report.md](examples/reference/report.md) for its intended
  human-readable presentation.

## Phase A development

Requires Python 3.11 or later.

```bash
python -m pip install -e '.[dev]'
pytest
```

There is no CLI or live provider in this phase. No API credential is needed to
run the tests.

## Scope notice

Inspektorium evaluates relationships between an answer and sources supplied by
the user. It does not determine whether reality is true beyond those sources,
whether the sources are complete or high quality, or whether an answer is
globally good, safe, medically valid, or legally compliant.

## License status

No license grant is included in this specification phase. The intended initial
release posture is source-available and non-commercial, using an unmodified
standard license selected and reviewed by the curator before release.

