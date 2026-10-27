# Reference-checker guide

This guide checks evaluator proposals for one answer with `inspektorium inspect`.
It assumes the installation from [getting started](../getting-started.md) and a checkout of the repository.
Run the commands from the repository root.

The checker validates text bindings only. [How it works](../concepts/how-it-works.md#proposal-versus-deterministic-check) explains the model.
What a passed check does not establish is listed in [limitations](../evaluation/limitations.md#reference-checker-inspektorium-inspect).

## 1. Prepare the input

The input is one answer and at least one source. There are two ways to supply it.

### As one JSON file

An `InspectionInput` document, as in [example 05](../../examples/inspect/05_mixed_and_fabricated_quote/input.json):

```json
{
  "schema_version": "0.1",
  "answer": {
    "answer_id": "answer",
    "text": "Northbridge Library is open on Saturdays. It closes at 8 p.m. on weekdays. It opened in 1998."
  },
  "sources": [
    {
      "source_id": "northbridge-guide",
      "title": "Northbridge Library visitor guide",
      "text": "Northbridge Library is open on Saturdays from 10 a.m. to 2 p.m. On weekdays, the library closes at 6 p.m. The source does not state when the library opened."
    }
  ]
}
```

- `source_id` values must be unique lowercase identifiers, for example `northbridge-guide`.
- `title` is optional and is not hashed.
- Unknown fields are rejected.

### As text files

Pass the answer with `--answer` and each source with `--source SOURCE_ID=PATH`.
Here `texts/answer.txt` and `texts/guide.txt` are your own UTF-8 files with the texts of example 05:

```sh
inspektorium inspect \
  --answer texts/answer.txt \
  --source northbridge-guide=texts/guide.txt \
  --proposals examples/inspect/05_mixed_and_fabricated_quote/proposals.json \
  --format json
```

Repeat `--source` for more sources. The answer ID is then `answer`.
`--source` cannot be combined with `--input`:

```text
inspektorium: error: --source cannot be combined with --input
```

All text is canonicalized to LF newlines and Unicode NFC when it is parsed.
Offsets are Python character indices into that canonical text ([normalization](../../src/inspektorium/core/normalization.py)).

## 2. Prepare the proposals

The proposals are one `ProposalBatch` document. Each finding needs every key below. Evidence fields may be null.

```json
{
  "claim_id": "claim-2",
  "claim_text": "It closes at 8 p.m. on weekdays.",
  "claim_start": 42,
  "claim_end": 74,
  "proposed_relation": "supported",
  "source_id": "northbridge-guide",
  "evidence_quote": "On weekdays, the library closes at 8 p.m.",
  "evidence_start": 64,
  "evidence_end": 105,
  "rationale": "The proposed quotation appears to state the same weekday closing time.",
  "evidence_sufficiency": "sufficient",
  "evaluator_certainty": "high"
}
```

- `proposed_relation` is one of `supported`, `contradicted`, `not_established` and `attribution_mismatch`.
- `not_established` may set all four evidence fields to null. Every other relation needs a complete citation.
- `evidence_sufficiency` is `sufficient`, `partial` or `insufficient`. `evaluator_certainty` is `high`, `medium` or `low`.
- Offsets are half-open: `answer[claim_start:claim_end]` must equal `claim_text`.

The [report schema](../reference/report-schema.md#proposal-batch) lists every constraint.

## 3. Run the check

```sh
inspektorium inspect \
  --input examples/inspect/05_mixed_and_fabricated_quote/input.json \
  --proposals examples/inspect/05_mixed_and_fabricated_quote/proposals.json \
  --format markdown
```

Markdown is the default format. The report goes to standard output unless you pass `--output`.
Shortened output for the first and third finding:

```text
### Finding 1: `claim-1`

**Atomic claim:** Northbridge Library is open on Saturdays.

- **Answer span:** `[0:41)`
- **Claim span check:** exact
- **Proposed relationship (evaluator judgment):** `supported`
- **Reportable proposed relationship:** `supported`
- **Deterministic guard:** `passed`
- **Citation text and offset check:** exact match (not a check of meaning)
…
### Finding 3: `claim-3`

**Atomic claim:** It opened in 1998.
…
- **Deterministic guard:** `passed` (claim span and structure only; no citation check performed)
- **Citation text and offset check:** not performed — no citation required or supplied for this proposal
…
```

The full output, including the failed second finding, is in [getting started](../getting-started.md#first-inspect-run) and in the [expected report](../../examples/inspect/05_mixed_and_fabricated_quote/expected_report.md).

## 4. Write JSON to a file

```sh
mkdir -p out
inspektorium inspect \
  --input examples/inspect/05_mixed_and_fabricated_quote/input.json \
  --proposals examples/inspect/05_mixed_and_fabricated_quote/proposals.json \
  --format json --output out/report-05.json
```

The parent directory of `--output` must exist. Otherwise the command exits 2:

```text
inspektorium: error: [Errno 2] No such file or directory: 'out/report-05.json'
```

The failed finding in the JSON report:

```json
{
  "claim_id": "claim-2",
  "claim_span_verified": true,
  "deterministic_validation_status": "failed",
  "evidence_span_verified": false,
  "proposed_relation": "supported",
  "reportable_relation": null,
  "validation_issues": [
    {
      "code": "evidence_span_mismatch",
      "message": "The proposed quote does not equal the canonical source span at the proposed offsets."
    }
  ],
  …
}
```

The summary block:

```json
"summary": {
  "citation_spans_verified": 1,
  "claims_inspected": 3,
  "reportable_findings": 2,
  "validation_failures": 1
}
```

## 5. Read the result

For each finding, check these fields:

| Field | Values | Meaning |
| --- | --- | --- |
| `claim_span_verified` | `true`, `false` | The claim text equals the answer at its span |
| `evidence_span_verified` | `true`, `false`, `null` | The quotation equals the source at its offsets; `null` when no citation was proposed |
| `deterministic_validation_status` | `passed`, `failed` | All mandatory checks for this proposal passed |
| `reportable_relation` | a relation or `null` | The unchanged proposed relation, or `null` after a failed check |
| `validation_issues` | list of `{code, message}` | One entry per failed check |

The issue codes are `claim_span_mismatch`, `unknown_source`, `invalid_evidence_offsets`, `evidence_span_mismatch` and `incomplete_evidence_reference` ([relations](../../src/inspektorium/core/relations.py)).
`malformed_proposal` prefixes errors for proposal files that fail parsing.

## 6. Add a timestamp

Reports contain `generated_at: null` by default. Pass an explicit, timezone-aware time to include one:

```sh
inspektorium inspect \
  --input examples/inspect/01_supported/input.json \
  --proposals examples/inspect/01_supported/proposals.json \
  --format markdown --generated-at 2026-10-27T12:00:00Z
```

```text
# Inspection Report

**Generated from explicit metadata:** `2026-10-27T12:00:00+00:00`
…
```

A time without an offset is rejected with exit code 2:

```text
inspektorium: error: --generated-at must include a timezone offset
```

The timestamp is not part of any fingerprint.

## 7. Handle rejected input

Input and proposal files go through a strict JSON decoder before schema validation ([strict JSON](../../src/inspektorium/core/strict_json.py)).
A rejection prints one line and exits 2. Nothing is written, and an existing `--output` file stays unchanged.

A duplicate key in the input:

```text
inspektorium: error: Inspection input is not valid JSON: duplicate object key 'text'.
```

A proposal with missing fields:

```text
inspektorium: error: malformed_proposal: Proposal JSON does not conform to the strict public schema: findings.0.claim_text: Field required; findings.0.claim_start: Field required; findings.0.claim_end: Field required (and 8 more).
```

The full list of rejected constructs is in [methodology](../concepts/methodology.md#strict-json-decoding).

## 8. Optional live provider

Instead of `--proposals`, `--provider anthropic --model MODEL_ID` requests proposals from the Anthropic API.
It needs the `providers` extra and `ANTHROPIC_API_KEY` in the environment.
The input and `--generated-at` are validated before the provider is constructed.
This path makes a paid network call. It is not used in this guide.
The adapter contract is described in [methodology](../concepts/methodology.md#provider-path).

## Exit codes

| Code | Meaning |
| --- | --- |
| 0 | The report was produced, including reports with failed findings |
| 2 | Usage error, rejected input or proposals, unreadable file, invalid `--generated-at` or provider error |

For what exit code 0 does not mean, see [limitations](../evaluation/limitations.md#reference-checker-inspektorium-inspect).

## Check the bundled examples

The five examples in [`examples/inspect/`](../../examples/inspect/) each have an expected JSON and Markdown report.
This loop compares the current output with them:

```sh
for d in examples/inspect/*/; do
  for f in json markdown; do
    ext=$([ $f = json ] && echo json || echo md)
    python -m inspektorium inspect --input $d/input.json --proposals $d/proposals.json --format $f \
      | cmp -s - $d/expected_report.$ext && echo "$(basename $d) $f: identical" || echo "$(basename $d) $f: DIFFERENT"
  done
done
```

```text
01_supported json: identical
01_supported markdown: identical
02_contradicted json: identical
…
05_mixed_and_fabricated_quote markdown: identical
```

The same comparison, through the Python API, is a regression test in [test_examples.py](../../tests/acceptance/test_examples.py).
