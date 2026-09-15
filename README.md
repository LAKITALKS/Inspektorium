# INSPEKTORIUM

Evidence integrity controls for AI assurance research.

## Purpose and current version

INSPEKTORIUM is a research prototype studying evidence integrity controls for
AI assurance. Its public v0.1 release implements exact claim and citation checks
against supplied text. Broader execution controls are reported from internal
research; scientific inference checks and review workflows remain planned work.

The public package is **0.1.0**, with schema **0.1**. This documentation change
does not expand that executable kernel. INSPEKTORIUM accepts one answer and
explicitly supplied text sources; it performs no automated source search.
The evaluator proposes semantic relationships. Deterministic code checks text
bindings before an individual proposal can remain reportable.

Here, **AI assurance research** means producing inspectable evidence for a
bounded property, including contrary evidence and limitations. **Technical AI
governance** means a named rule enforced at a named system boundary, with a
traceable decision. The current rule gates a finding's reporting field; broader
governance is a research direction. [Scope](SCOPE.md) defines this distinction.

## Run the existing offline demo

From a local checkout, using Python 3.11 or later:

```bash
python -m pip install -e .
inspektorium inspect \
  --input examples/05_mixed_and_fabricated_quote/input.json \
  --proposals examples/05_mixed_and_fabricated_quote/proposals.json \
  --format markdown
```

For JSON, use `--format json`; optionally add `--output report.json`.
The module entry point is `python -m inspektorium`. All five bundled examples
use synthetic, precomputed proposals and need no provider key or live call.

In this example a proposed quotation says the library closes at `8 p.m.`,
while the source span says `6 p.m.`. The failed finding retains its proposal:

```json
{
  "proposed_relation": "supported",
  "evidence_span_verified": false,
  "deterministic_validation_status": "failed",
  "reportable_relation": null
}
```

An unrelated valid finding survives. The report is still emitted and the CLI
exits **0**. Exit 0 is not assurance approval or authorization to release an
artifact. Expected JSON and Markdown are committed beside each example.

## What the control does and does not establish

The four evaluator-proposed relations are `supported`, `contradicted`,
`not_established` and `attribution_mismatch`. Reports preserve
`proposed_relation`, `claim_span_verified`, `evidence_span_verified`,
`deterministic_validation_status` and the gated `reportable_relation`.
Semantic relations remain evaluator judgments, never “verified relations.”

“Fail-closed” describes only the individual `reportable_relation` field:
failed mandatory claim/citation checks set it to null. The original proposal
and the rest of the report remain visible. A true quotation with an
intentionally false semantic relation can pass these mechanical checks.
`not_established` may remain reportable with all citation fields null, without
proving absence of evidence; a supplied optional citation must validate.
Empty findings are allowed, so zero failures does not prove full claim coverage.

Text is normalized to LF/NFC, preserving other whitespace; offsets are half-open
Python character indices, not byte offsets. SHA-256 fingerprints identify
current canonical answer/source content and a source-ID-ordered bundle.
Identical canonical IDs/texts are order-invariant; arbitrary paraphrases are
not hash-equivalent. Hashes do not authenticate historical state or source
authority. JSON includes `generated_at: null` by default; Markdown omits the
date line. [Methodology](METHODOLOGY.md) gives the concrete contracts (P01–P11).

## Capability and evidence status

| Status | Capability or result | Boundary |
| --- | --- | --- |
| IMPLEMENTED + TESTED IN PUBLIC v0.1 | Exact spans, input fingerprints, deterministic JSON/Markdown, strict offline parsing | Public code and regression evidence; P01–P07 |
| OWNER-REPORTED INTERNAL EXPERIMENT | Artifact-fault pilot: 4/12 versus 12/12 blocked; 6/6 clean counterparts accepted | Not reproduced by this package; semantic misses and zero accuracy gain retained; I01–I03 |
| REPORTED IMPLEMENTED/TESTED INTERNALLY | Execution authorization, budget/state/environment controls | No public implementation inspected; I04 |
| PLANNED — PHASE 8 | Semantic/inferential checking | Not executable here; R08 |
| PLANNED — PHASE 9 | Disagreement and review | No public adjudication workflow; R09 |
| PLANNED — PHASE 10 | Canonical operational release workflow | JSON/Markdown renderers already exist; release authorization does not; R10 |
| NOT CLAIMED | General AI safety, regulatory compliance, certification, alignment | No framework endorsement or conformance claim |

The [claim ledger](CLAIMS.md) supplies each claim's evidence, version and access
status. Internal research does not make planned controls available in v0.1.

## Evidence and limitations

[Research results](RESEARCH_RESULTS.md) distinguishes public observations,
historical CI and owner-reported internal studies. Saved examples reproduce
report bytes; they do not measure live-model classification accuracy. The
semantic counterexample in example 02, accepted empty findings, and example
05's successful report exit define important limits.

In the internal pilot, A/B/C each achieved 24/24 main-case accuracy:
B−A was zero percentage points. Both semantically wrong but structurally valid
controls were accepted. The small constructed set, shared B/C responses and
lack of independent human peer review constrain interpretation. No general
accuracy gain or population-wide false-blocking guarantee follows.

Evidence integrity and provenance mean textual/input binding here. Reliability
is limited to fixed saved inputs, proposals and timestamp settings; robustness
evidence names the tested malformed JSON, fields, spans and normalization
disturbances. Neither establishes source quality, evidence completeness,
scientific validity or correctness outside the supplied material.

## Research roadmap

[Phase 8](ROADMAP.md#phase-8--deep-forensics) studies scientific claim forensics;
[Phase 9](ROADMAP.md#phase-9--disagreement--review) studies disagreement and review;
[Phase 10](ROADMAP.md#phase-10--reporting--operational-finish) studies operational
reporting and release controls. A final v1 gate requires fresh efficacy and
fault comparisons, real-case validation, prior criteria and negative results.

[Research plan](RESEARCH_PLAN.md) specifies falsifiable questions, informative
baselines and future demonstrations. These are planned comparisons, not new
capabilities or permission to run studies.

## Development, provider, license and citation

```bash
python -m pip install -e '.[dev]'
ruff check .
mypy src
pytest --cov=inspektorium --cov-report=term-missing
```

The tests use saved proposals and mocked provider transport. See
[Contributing](CONTRIBUTING.md) for scope and claim-ledger requirements.

For the optional Anthropic adapter (P08):

```bash
python -m pip install -e '.[anthropic]'
inspektorium inspect --input inspection.json \
  --provider anthropic --model YOUR_ANTHROPIC_MODEL_ID --format markdown
```

Set `ANTHROPIC_API_KEY` in the process environment for this optional live path
and supply your own input file. The explicit model argument is required.
The adapter uses `client.messages.parse(..., output_format=ProposalBatch)`.
One application SDK invocation and no authored semantic repair loop do not
guarantee one HTTP attempt, bounded billing or authenticated execution.

Source-available under [PolyForm Noncommercial 1.0.0](LICENSE), not an OSI
open-source license. [CITATION.cff](CITATION.cff) retains software version 0.1.0;
no DOI is assigned. Historical release facts and pending publication review
are distinguished in [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md).

**Author and maintainer:** Lazaros Varvatis —
[LAKITALKS](https://github.com/LAKITALKS).
