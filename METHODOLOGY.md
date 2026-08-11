# Methodology

## Purpose

Inspektorium is a reference implementation and research seed for evidence-bound
evaluation. It focuses on one inspectable operation: an evaluator proposes how
an answer relates to supplied sources, and deterministic code checks the exact
textual provenance of the proposed claim and citation spans before allowing
that proposal to remain reportable.

## The auditability problem

A free-floating language-model judgment can be fluent without being
reproducible. A label or numeric score does not tell a reader which answer text
was inspected, which source passage mattered, or whether a quoted passage
exists. Adding a quotation does not solve the problem by itself because the
quotation is also model output. It can be truncated, misattributed, subtly
altered, or fabricated.

Inspektorium therefore treats the evaluator's output as a proposal. The
proposal is preserved, but ordinary deterministic code separately checks its
text spans. This creates an audit boundary that a reader and a machine consumer
can inspect.

## Atomic claims

One sentence can contain several propositions with different source
relationships. Binding a paragraph to one quotation makes it unclear which
proposition is being assessed and can hide partial support.

Each proposal identifies an atomic `claim_text` plus a half-open character
interval `[claim_start, claim_end)` in the canonical answer. The validator
requires:

```python
answer[claim_start:claim_end] == claim_text
```

Atomicity is still an evaluator judgment; natural language does not have a
single uniquely correct decomposition. The explicit span makes the chosen unit
inspectable.

## Semantic proposal versus deterministic validation

This separation is the central design constraint.

The evaluator generates:

- an atomic claim;
- `proposed_relation`;
- a proposed source identifier, quotation, and offsets;
- evidence sufficiency;
- evaluator certainty;
- a concise rationale.

Deterministic code checks:

- whether the claim equals the proposed answer span;
- whether the named source exists in the supplied input;
- whether the evidence offsets are valid;
- whether the source span equals the proposed quotation exactly;
- whether mandatory evidence fields are complete.

If mandatory guards pass, the unchanged proposal may appear as
`reportable_relation`. That field means only that the proposal cleared the
mechanical reporting guard. It does not mean that deterministic code proved the
semantic relationship, the evaluator's interpretation, or the truth of the
claim.

## Public source relationships

The evaluator uses exactly four source-bounded relationships:

- `supported`: supplied source material is judged to directly support the
  claim within its expressed scope;
- `contradicted`: supplied source material is judged to directly conflict with
  the claim;
- `not_established`: supplied material is judged not to establish the claim;
- `attribution_mismatch`: the answer is judged to attribute a statement,
  result, or position to a source that does not state or support it.

These definitions describe evaluator-proposed relationships to the supplied
source set. They are not comprehensive truth or claim-forensics labels.

## Why exact quotation validation matters

Plausible fabricated quotations are especially difficult to notice in a
polished report. v0.1 uses exact matching rather than fuzzy recovery:

```python
source[evidence_start:evidence_end] == evidence_quote
```

If this condition fails, Inspektorium preserves the quotation and proposed
offsets as failed input, assigns a finite failure code, and makes the proposal
non-reportable. It never searches for similar wording, changes offsets, chooses
another source, repairs the quotation, or changes the proposed relationship.

The mixed example intentionally proposes an `8 p.m.` quotation where the source
says `6 p.m.`. The failed quotation remains visible in both JSON and Markdown,
while an unrelated valid finding in the same report survives.

## The special case of `not_established`

Absence of a citation does not prove absence of support. `not_established` is a
semantic evaluator judgment and may be proposed with all evidence fields null
so the schema does not encourage fabricated evidence.

The deterministic guard can confirm the claim span and structural integrity,
but it does not prove source insufficiency. If an evaluator optionally supplies
a passage to explain the limitation, that passage must pass the same exact
citation checks. A failed optional citation makes the proposal non-reportable.

## Canonical text and offset contract

The same canonical representation is used for provider-visible text, offsets,
validation, fingerprints, and reports:

1. Convert CRLF and bare CR newlines to LF.
2. Apply Unicode NFC normalization.
3. Preserve all other whitespace exactly.
4. Use Python string character indices with half-open intervals.
5. Encode canonical text as UTF-8 only when hashing or serializing.

Offsets are character indices, not byte offsets. Normalization occurs when the
inspection input is parsed, before proposals are requested or validated. Model-
produced quotations are not normalized or repaired after generation.

## Validation outcomes and failure codes

Each finding preserves:

- `claim_span_verified`;
- `evidence_span_verified` (`true`, `false`, or `null` when none was proposed);
- `deterministic_validation_status`;
- `proposed_relation`;
- `reportable_relation` or null;
- `validation_issues` with a small finite code vocabulary.

The public failure codes are:

- `claim_span_mismatch`;
- `unknown_source`;
- `invalid_evidence_offsets`;
- `evidence_span_mismatch`;
- `incomplete_evidence_reference`;
- `malformed_proposal` for parsing-layer failures.

The Anthropic adapter requests native JSON-schema structured output. Provider
JSON that is malformed or violates the strict schema still fails before finding
validation. No prose extraction or schema repair is attempted.

## Evidence sufficiency and evaluator certainty

The two qualitative descriptors answer different questions.

`evidence_sufficiency` describes the evaluator's view of how fully the supplied
text addresses the claim: `sufficient`, `partial`, or `insufficient`.

`evaluator_certainty` describes the evaluator's confidence in its own proposal:
`high`, `medium`, or `low`.

A source can clearly omit required information, yielding high evaluator
certainty and insufficient evidence. Conversely, potentially useful text can
exist while its interpretation remains uncertain. Neither vocabulary is an
empirically calibrated probability, and neither is converted into a number.

## Fingerprinting and provenance

Inspektorium computes SHA-256 over the canonical UTF-8 answer text and each
canonical source. It also hashes a canonical JSON bundle of this form:

```json
{"answer":"<canonical answer>","sources":[{"source_id":"<id>","text":"<canonical source>"}]}
```

Object keys are sorted, separators contain no optional spaces, Unicode is not
ASCII-escaped, and sources are sorted by `source_id`. Display titles and
timestamps are excluded. Therefore semantically identical source sets have the
same bundle digest regardless of input order. The hash identifies bytes; it
does not establish authorship or source quality.

## Deterministic reports

JSON rendering uses sorted keys, fixed indentation, UTF-8-compatible Unicode,
and one terminal newline. Markdown is assembled from the validated report
object with fixed section order and wording. Neither renderer reads the system
clock. `generated_at` is absent by default and can appear only when supplied as
explicit timezone-aware input metadata.

The report visually labels evaluator-generated semantic content separately
from deterministic checks. A citation-validated quotation is identified as
such; a failed proposal is labeled unvalidated and repeated in the warning
section.

## Why there is no global score

A single number would collapse heterogeneous claims, semantic judgments, and
mechanical failures into apparent precision without an empirical basis for the
weighting. v0.1 therefore has no aggregate quality score, trust score, severity
weight, rank, probability, or answer-level label. Findings remain discrete and
inspectable.

## What deterministic validation does not prove

Exact span checks do not prove:

- that a proposed relationship is semantically correct;
- that the source is accurate, authoritative, current, or complete;
- that reality agrees with the source;
- that omitted evidence does not exist elsewhere;
- that every relevant claim was extracted;
- that a scientific, causal, clinical, legal, or safety conclusion is valid;
- that an answer is globally good or bad.

These are limits of the question Inspektorium asks, not exceptions hidden from
the report.

## Extensibility and independent study

Inspektorium is intentionally a small reference point, not a complete doctrine.
Researchers and developers are encouraged to fork it, challenge its
assumptions, replace the evaluator prompt, add providers in their own work,
study failure cases, test alternative evidence-binding strategies, or develop
different relationship vocabularies. Changes to this repository remain subject
to its frozen v0.1 scope.
