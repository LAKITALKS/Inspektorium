# Methodology

## Purpose

Inspektorium is a reference implementation of one evaluation primitive:
binding a model-proposed finding to source text that ordinary code can verify.
It evaluates an answer only against documents supplied by the user. Its output
is therefore a statement about a bounded textual relationship, not about truth
in the world.

## The auditability problem

An unconstrained language-model judge can emit a fluent verdict or score
without exposing a reproducible basis for it. Even when a response includes a
quotation, the quotation is itself model output. It may be incomplete,
misattributed, incorrectly transcribed, or fabricated. Treating that output as
evidence simply moves the unsupported assertion into a more persuasive form.

Inspektorium separates generative proposal from deterministic acceptance. The
model may identify claims and propose evidence relationships. A separate,
non-generative validation step decides whether the referenced text exists
exactly where the proposal says it does.

## Atomic claims before evidence binding

An answer sentence can contain several propositions with different evidential
statuses. Binding an entire paragraph to a single quotation makes it unclear
which proposition is being evaluated and encourages evidence that supports
only part of the text.

The claim proposal therefore identifies a specific `claim_text` and half-open
character interval `[claim_start, claim_end)` in the answer. A later validator
must reproduce the text exactly with `answer[claim_start:claim_end]`. Atomicity
is a modeling objective rather than a claim that language always decomposes
uniquely; the explicit span at least makes the chosen unit inspectable.

## Evidence bindings are proposals

For a claim, the model proposes one of four deliberately narrow relationships:

- `supported`: the supplied source directly supports the claim within its
  expressed scope;
- `contradicted`: the supplied source directly conflicts with the claim;
- `not_established`: the supplied material does not provide enough evidence to
  establish the claim;
- `attribution_mismatch`: the answer attributes a statement, result, or
  position to a supplied source that does not state or support it.

For an evidence-bearing relationship, the proposal names a `source_id`, quotes
the source, and supplies a half-open character interval
`[evidence_start, evidence_end)`. It also includes a concise rationale,
evidence sufficiency, and evaluator certainty. These fields are proposals until
the deterministic layer accepts their spans.

## Deterministic span validation

The validation kernel planned for the next implementation phase applies exact
checks:

1. The proposed claim offsets must be within the answer and reproduce
   `claim_text` exactly.
2. The proposed source identifier must name one of the supplied documents.
3. The evidence offsets must be within that source and reproduce
   `evidence_quote` exactly.
4. A relationship that requires evidence cannot be verified when any required
   check fails.

Matching is intentionally exact in v0.1. The validator does not search for a
similar passage, repair a quotation, normalize wording, or replace the model's
evidence with a different span. Those behaviors could conceal the very failure
the report is meant to reveal.

The report preserves the original `relation` as an auditable proposal and adds
`verified_relation`. A passed finding repeats the accepted relation there. A
failed finding sets it to null and emits a visible validation warning. This
distinction is essential for machine consumers as well as readers.

## Evidence sufficiency and evaluator certainty

The two qualitative descriptors answer different questions.

`evidence_sufficiency` describes the relationship between the supplied text
and the claim: whether the evidence is `sufficient`, `partial`, or
`insufficient` for the proposed finding.

`evaluator_certainty` describes how confidently the evaluator made its
interpretive proposal: `high`, `medium`, or `low`.

A clear but incomplete source can yield high evaluator certainty and
insufficient evidence. Conversely, a potentially relevant passage can be
available while its interpretation remains uncertain. Neither vocabulary is a
probability scale, and Inspektorium does not aggregate either into a number.

## Why there is no global score

A single score would collapse distinct claims, evidence conditions, and
validation failures into an apparently comparable quantity. v0.1 has no
empirical basis for such weighting and does not imply one. Findings remain
discrete and inspectable; there is no answer-level label, severity hierarchy,
rank, or trust score.

## Fingerprinting and reproducibility

Reports identify their inputs with SHA-256. The answer fingerprint hashes the
exact UTF-8 bytes of the answer text. Each source fingerprint does the same for
its exact text.

The normalized bundle contains only the inspected text and the identifiers
needed to associate source fingerprints:

```json
{"answer":"<exact answer text>","sources":[{"source_id":"<id>","text":"<exact source text>"}]}
```

Titles and display metadata are excluded. The bundle is encoded as UTF-8 JSON;
object keys are sorted, separators are `,` and `:` without added spaces,
Unicode is not ASCII-escaped, and sources retain input order. Hashing this
canonical serialization provides a compact way to detect whether a report
refers to the same textual inputs. It does not establish authorship or source
quality.

## Source-bounded limitations

Inspektorium does not determine whether:

- the supplied sources are accurate, authoritative, current, or complete;
- relevant evidence exists outside the supplied material;
- reality agrees with the sources;
- a domain-specific causal, clinical, legal, or safety conclusion is valid;
- an omitted claim should have been extracted;
- an answer is globally good or bad.

These limitations apply to every report. Deterministic span verification proves
that a proposed quotation is present at the stated location. It does not prove
that the source, the interpretation, or the world is correct.

## Reference failure case

The hand-authored reference fixture contains a proposal quoting a weekday
closing time of `8 p.m.`. The named source contains `6 p.m.` at the supplied
offsets. The intended validator outcome is failure: the report retains the
proposal for inspection, withholds a verified relationship, and shows the
mismatch. It does not convert the finding into a contradiction even though a
reader might infer one from the source; doing so would silently replace the
model's proposed evidence-binding operation with a different one.
