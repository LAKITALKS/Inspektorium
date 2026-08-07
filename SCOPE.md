# Inspektorium v0.1 Scope

This document freezes the intended boundary of Inspektorium v0.1. Work that is
not listed under **In scope** is out of scope for v0.1, even when it would be
straightforward to implement.

## In scope

- Inspecting one answer per invocation.
- Accepting one or more source documents supplied by the user.
- Proposing atomic claim spans from the answer.
- Proposing evidence bindings to exact spans in named supplied sources.
- Deterministically verifying claim text, source identifiers, quotations, and
  character offsets.
- Reporting only these evidence relationships: `supported`, `contradicted`,
  `not_established`, and `attribution_mismatch`.
- Describing evidence sufficiency as `sufficient`, `partial`, or `insufficient`.
- Describing evaluator certainty as `high`, `medium`, or `low` without implying
  empirical calibration.
- Producing strict JSON and restrained Markdown reports.
- Fingerprinting the answer, each source, and a normalized input bundle with
  SHA-256.
- Making failed citation validation conspicuous and withholding a verified
  relationship when required evidence does not validate.

## Out of scope

- Scores, rankings, weighted aggregates, answer-level labels, or trust badges.
- Batch processing, benchmarks, leaderboards, or comparative model evaluation.
- Databases, web applications, hosted services, distributed processing, agent
  orchestration, plugin systems, or pipeline languages.
- Retrieving sources or judging their quality, authority, completeness, or
  scientific strength.
- Establishing truth beyond the user-supplied source set.
- Domain-specific medical, legal, safety, causal, or regulatory conclusions.
- Human adjudication, annotation workflows, calibration, empirical confidence
  estimates, or hidden severity hierarchies.
- Automatic quotation repair, fuzzy citation matching, or silent evidence
  substitution.
- An overall judgment that an answer is globally good or bad.

## v0.1 report contract

Each finding preserves the model-proposed `relation`. Deterministic validation
adds `claim_span_verified`, `evidence_span_verified`, `validation_status`, and
`verified_relation`. A failed validation requires `verified_relation` to be
null. The proposal remains visible for auditability but cannot masquerade as a
verified result.

`not_established` may pass without a quotation because its conclusion is that
the supplied source set does not establish the claim. The other three
relationships require a complete evidence reference and a deterministically
verified source span.

## Change control

This boundary remains fixed through v0.1. Candidate capabilities belong in
[ROADMAP.md](ROADMAP.md) and require an explicit post-v0.1 design decision.

