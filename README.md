# INSPEKTORIUM

Evidence-bound inspection for model outputs.

Inspektorium is a small reference implementation for a narrow methodological
primitive: an evaluator may propose a source relationship, but ordinary code
must confirm that its quoted source text occurs at the exact stated offsets
before that proposal is allowed to remain reportable.

```text
MODEL PROPOSES A RELATIONSHIP AND CITATION
                    ↓
DETERMINISTIC CODE CHECKS CLAIM AND CITATION SPANS
                    ↓
UNVERIFIABLE EVIDENCE DOES NOT SILENTLY BECOME REPORTABLE
```

Inspektorium grew out of broader research and engineering work on
evidence-grounded evaluation. This repository intentionally focuses on one
small, inspectable methodological primitive.

## The 30-second explanation

Language models can produce persuasive quotations that are slightly wrong or
entirely fabricated. Inspektorium accepts one answer, user-supplied sources, and
strict evaluator proposals. It normalizes the text, verifies exact Python
character spans, computes reproducible SHA-256 fingerprints, and emits stable
JSON or Markdown.

The model's `proposed_relation` remains a semantic judgment. Deterministic
validation does not prove that relationship. It only controls whether the
unchanged proposal may appear as `reportable_relation` after mandatory claim
and citation checks.

## A fabricated quote is rejected

The mixed offline example proposes:

> On weekdays, the library closes at 8 p.m.

At the proposed source offsets, the canonical source actually says `6 p.m.`.
The result is therefore:

```json
{
  "proposed_relation": "supported",
  "evidence_span_verified": false,
  "deterministic_validation_status": "failed",
  "reportable_relation": null,
  "validation_issues": [
    {"code": "evidence_span_mismatch"}
  ]
}
```

The proposal remains visible for inspection. Inspektorium does not repair the
quote, search for a convenient substitute, change the relationship, or conceal
the failure.

## Installation

Inspektorium requires Python 3.11 or later.

```bash
python -m pip install -e .
```

For the optional Anthropic provider:

```bash
python -m pip install -e '.[anthropic]'
```

The deterministic core, reports, CLI, tests, and all bundled examples work
without a provider SDK, API key, or network access.

## Offline demo

Run the methodological heartbeat locally without making an API call:

```bash
inspektorium inspect \
  --input examples/05_mixed_and_fabricated_quote/input.json \
  --proposals examples/05_mixed_and_fabricated_quote/proposals.json \
  --format markdown
```

Produce deterministic JSON instead:

```bash
inspektorium inspect \
  --input examples/05_mixed_and_fabricated_quote/input.json \
  --proposals examples/05_mixed_and_fabricated_quote/proposals.json \
  --format json \
  --output report.json
```

The expected outputs are committed beside each example and regenerated
byte-for-byte by the test suite.

## Inspect separate text files

The compact JSON input bundle is recommended for reproducibility. A direct
single-answer form is also available:

```bash
inspektorium inspect \
  --answer answer.md \
  --source manual=manual.md \
  --source notice=notice.md \
  --proposals proposals.json \
  --format markdown \
  --output report.md
```

`--source` accepts only explicitly named files in `SOURCE_ID=PATH` form. The CLI
does not crawl directories.

## Provider-assisted inspection

Set `ANTHROPIC_API_KEY` in the process environment, choose an Anthropic model
identifier explicitly, and replace the precomputed proposal input:

```bash
inspektorium inspect \
  --input inspection.json \
  --provider anthropic \
  --model YOUR_ANTHROPIC_MODEL_ID \
  --format markdown \
  --output report.md
```

The provider makes one proposal call behind a small interface and uses the
Anthropic Python SDK's Pydantic parse helper to request native JSON-schema
structured output. The returned object is validated against the strict public
proposal model with unknown fields rejected. Malformed output remains a visible
failure; no prose extraction or aggressive JSON repair is attempted.

## Report layers

Every finding separates two different layers:

- **Evaluator judgment:** atomic claim, `proposed_relation`, evidence
  sufficiency, evaluator certainty, rationale, and proposed citation.
- **Deterministic checks:** exact claim span, source existence, exact quotation
  span, guard status, failure codes, and `reportable_relation` gating.

A reportable proposal is not described as semantically verified. Citation
validation confirms textual provenance only.

## Public relationship vocabulary

- `supported` — the evaluator judges that supplied source text directly
  supports the claim within its expressed scope.
- `contradicted` — the evaluator judges that supplied source text directly
  conflicts with the claim.
- `not_established` — the evaluator judges that the supplied material does not
  establish the claim. It may be proposed without inventing a quotation.
- `attribution_mismatch` — the evaluator judges that the answer attributes a
  statement or position to a supplied source that does not state or support it.

These are source-bounded evaluator proposals, not universal truth labels. There
is no global score, severity hierarchy, calibrated probability, ranking, or
answer-level label.

## Text and offsets

Before a model sees text or offsets are calculated, Inspektorium:

1. converts CRLF and bare CR to LF;
2. applies Unicode NFC normalization;
3. preserves every other whitespace character.

Offsets are half-open Python string character indices into that canonical text,
not UTF-8 byte offsets. Fingerprints cover the same canonical representation.

## Five synthetic examples

- `01_supported` — fictional timer documentation.
- `02_contradicted` — fictional desk-lamp documentation.
- `03_not_established` — a fictional shuttle notice without a launch year.
- `04_attribution_mismatch` — a fictional museum admission notice.
- `05_mixed_and_fabricated_quote` — valid, not-established, and rejected
  fabricated-quote findings in one answer.

All examples were written for this repository and run offline from precomputed
synthetic proposals.

## Limitations

Inspektorium compares an answer with sources supplied by the user. It does not
determine:

- truth outside those sources;
- whether a source is accurate, complete, current, or authoritative;
- whether relevant omitted evidence exists elsewhere;
- whether every claim was extracted;
- medical, legal, safety, causal, or regulatory validity;
- whether an answer is globally good or bad.

Exact quotation validation confirms only that text occurs in the named source at
the stated canonical offsets. See [METHODOLOGY.md](METHODOLOGY.md) and
[SCOPE.md](SCOPE.md).

## Development and testing

```bash
python -m pip install -e '.[dev]'
ruff check .
mypy src
pytest --cov=inspektorium --cov-report=term-missing
```

Tests require no provider credential. The named heartbeat regression is
`test_fabricated_quote_cannot_become_reportable_finding`.

## License

Inspektorium is source-available under the
[PolyForm Noncommercial License 1.0.0](LICENSE). This is not an OSI Open Source
license, and commercial use is not granted by these terms.

## Citation

Release citation metadata is prepared in [CITATION.cff](CITATION.cff). No DOI
has been assigned. Any eventual archive record should correspond to a curator-
approved release rather than an intermediate development commit.

## Contributing and independent extension

Inspektorium is a reference implementation and research seed. Researchers and
developers are welcome to fork it, challenge its assumptions, replace the
evaluator, study deterministic citation strategies, or explore alternate
relationship schemas. Changes to this repository should preserve the narrow
v0.1 scope; see [CONTRIBUTING.md](CONTRIBUTING.md).
