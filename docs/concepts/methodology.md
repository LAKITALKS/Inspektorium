# Methodology

Inspektorium is a research instrument for evidence integrity controls in AI assurance.
It has one command, `inspektorium`, with two subcommands.

- `inspektorium inspect` is the smaller reference checker (`inspektorium.core`, `inspektorium.report`, `inspektorium.providers`). Its report schema is 0.1.
- `inspektorium audit` is the audit workflow (`inspektorium.audit`) with `validate`, `run`, `inspect`, `review` and `release`.

The two pipelines are separate. Audit does not invoke the reference checker or reuse its validation pipeline.
Claim IDs below refer to the [claim ledger](../research/claims.md).
Limits are listed once in [limitations](../evaluation/limitations.md).

Here, AI assurance research produces inspectable evidence for a bounded property, including contrary evidence.
Technical AI governance means a named rule enforced at a named system boundary with a traceable decision.
The reference checker's boundary is one finding's reporting field.

## The auditability problem

A free-floating language-model judgment can be fluent without being reproducible.
A label or score does not show which answer text was inspected or which source passage mattered.
Adding a quotation does not solve this, because the quotation is also model output.
It can be truncated, misattributed, subtly altered or fabricated.

Inspektorium therefore treats evaluator output as a proposal.
The proposal is preserved, and deterministic code separately checks its text spans.
This creates an audit boundary that a reader and a machine consumer can inspect.

## Proposal versus deterministic check

This separation is the central design constraint.

The evaluator proposes:

- an atomic claim;
- `proposed_relation`;
- a source identifier, quotation and offsets;
- evidence sufficiency;
- evaluator certainty;
- a concise rationale.

Deterministic code checks:

- whether the claim equals the proposed answer span;
- whether the named source exists in the supplied input;
- whether the evidence offsets are valid;
- whether the source span equals the proposed quotation exactly;
- whether mandatory evidence fields are complete.

### Atomic claims

One sentence can contain several propositions with different source relationships.
Each proposal therefore identifies an atomic `claim_text` and a half-open interval `[claim_start, claim_end)` in the canonical answer.
The validator requires:

```python
answer[claim_start:claim_end] == claim_text
```

Atomicity is still an evaluator judgment. The explicit span makes the chosen unit inspectable (P01).

### Reportability gate

If the mandatory guards pass, the unchanged proposal may appear as `reportable_relation`.
That field means only that the proposal cleared the mechanical reporting guard.
It does not mean that code proved the semantic relationship or the claim.
A failure sets only that finding's `reportable_relation` to null (P03).
The proposal stays visible, and the rest of the report is still emitted.
"Fail-closed" describes only this field.

## The four relations

The evaluator uses exactly four source-bounded relations:

- `supported`: supplied source material is judged to directly support the claim within its expressed scope;
- `contradicted`: supplied source material is judged to directly conflict with the claim;
- `not_established`: supplied material is judged not to establish the claim;
- `attribution_mismatch`: the answer is judged to attribute a statement, result or position to a source that does not state or support it.

These are evaluator-proposed relations to the supplied source set.
They are not comprehensive truth labels or claim-forensics labels.

### `not_established`

`not_established` may be proposed with all evidence fields null (P04).
This keeps the schema from encouraging fabricated evidence.
An optional explanatory citation must pass the same exact checks.
A failed optional citation makes the proposal non-reportable.

## Exact quotations and strict offsets

The quotation check is exact, with no fuzzy recovery:

```python
source[evidence_start:evidence_end] == evidence_quote
```

If this fails, Inspektorium keeps the quotation and offsets as failed input (P02).
It assigns a finite failure code and makes the proposal non-reportable.
It never searches for similar wording, changes offsets, chooses another source or repairs the quotation.

[Example 05](../../examples/inspect/05_mixed_and_fabricated_quote/input.json) proposes an `8 p.m.` quotation where the source says `6 p.m.`.
The failed quotation stays visible in JSON and Markdown. An unrelated valid finding survives.

Offsets are strict (P17).
A quotation whose text occurs in the source, but not at the proposed offsets, fails.
The failure code is `invalid_evidence_offsets` or `evidence_span_mismatch`. Nothing is moved.

## Canonical text and offsets

One canonical representation is used for provider-visible text, offsets, validation, fingerprints and reports ([normalization](../../src/inspektorium/core/normalization.py)):

1. Convert CRLF and bare CR newlines to LF.
2. Apply Unicode NFC normalization.
3. Preserve all other whitespace exactly.
4. Use Python string character indices with half-open intervals.
5. Encode canonical text as UTF-8 only when hashing or serializing.

Offsets are character indices, not byte offsets.
Normalization happens when the inspection input is parsed, before proposals are requested or validated.
Model-produced quotations are not normalized or repaired after generation.

## Validation outcomes and failure codes

Each finding preserves:

- `claim_span_verified`;
- `evidence_span_verified` (`true`, `false`, or `null` when none was proposed);
- `deterministic_validation_status`;
- `proposed_relation`;
- `reportable_relation` or null;
- `validation_issues` with a small finite code vocabulary.

Since 0.1.1 the report models accept `evidence_span_verified: true` only with a complete evidence reference.
A complete reference has source ID, quotation and both offsets ([invariant tests](../../tests/unit/test_model_invariants.py), P13).
Otherwise `ValidatedFinding`, and therefore `InspectionReport` parsing, fails.
The validator never produced such findings, so pipeline outputs and report schema 0.1 are unchanged.

The public failure codes are:

- `claim_span_mismatch`;
- `unknown_source`;
- `invalid_evidence_offsets`;
- `evidence_span_mismatch`;
- `incomplete_evidence_reference`;
- `malformed_proposal` for parsing-layer failures.

### Strict JSON decoding

`--input` files and proposal JSON go through one [strict decoder](../../src/inspektorium/core/strict_json.py) before schema validation (P07, P13). It rejects:

- duplicate keys at any nesting level, including keys equal only after JSON escape decoding;
- the constants `NaN`, `Infinity` and `-Infinity`;
- strings or keys with an unpaired UTF-16 surrogate;
- a leading byte order mark;
- trailing data;
- nesting deeper than 64 arrays or objects;
- any other invalid JSON.

Nothing is repaired or retried with a more permissive parser.
The CLI validates the `--input` file and `--generated-at` before loading proposals or constructing a provider.
A rejected input ends with exit code 2 before analysis or output.
An existing `--output` file stays untouched.
The rendered report is checked for UTF-8 encodability before anything is written.

The error is one bounded line naming the reason or up to three schema locations and rules.
It does not quote input values.
A duplicated or unknown key name is shown ASCII-escaped and truncated.
Clean inputs produce the same models, fingerprints and reports as before.
Evidence: [CLI rejection tests](../../tests/integration/test_cli_input_rejection.py) and [input parsing tests](../../tests/unit/test_input_parsing.py).

Library code that handles untrusted JSON should call `parse_inspection_input_json` or `parse_proposal_json` from `inspektorium.providers.parsing`.

### Provider path

The optional Anthropic adapter uses the SDK's Pydantic parse helper (P08, [adapter](../../src/inspektorium/providers/anthropic.py)).
It transforms the proposal model into the native JSON-schema wire format.
It validates the response against the original strict model.
Malformed or schema-violating provider JSON fails before finding validation.
There is one application SDK invocation and no authored semantic repair loop.

## Evidence sufficiency and evaluator certainty

The two qualitative descriptors answer different questions.

- `evidence_sufficiency` is the evaluator's view of how fully the supplied text addresses the claim: `sufficient`, `partial` or `insufficient`.
- `evaluator_certainty` is the evaluator's confidence in its own proposal: `high`, `medium` or `low`.

A source can clearly omit required information: high certainty, insufficient evidence.
Neither vocabulary is a calibrated probability, and neither is converted into a number.

## Fingerprints

Inspektorium computes SHA-256 over the canonical UTF-8 answer and each canonical source (P05, [fingerprints](../../src/inspektorium/core/fingerprints.py)).
It also hashes a canonical JSON bundle of this form:

```json
{"answer":"<canonical answer>","sources":[{"source_id":"<id>","text":"<canonical source>"}]}
```

- Object keys are sorted.
- Separators contain no optional spaces.
- Unicode is not ASCII-escaped.
- Sources are sorted by `source_id`.
- Display titles and timestamps are excluded.

The same canonical source IDs and texts, with the same answer, give the same bundle digest in any source order.
Semantically equivalent paraphrases are not hash-equivalent.
The raw bytes of an input file are not hashed, only the canonical text.
Changing source text outside a cited span changes the source and bundle hashes.

## Deterministic reports

JSON rendering uses sorted keys, fixed indentation, UTF-8-compatible Unicode and one terminal newline ([JSON renderer](../../src/inspektorium/report/json_report.py)).
Markdown is assembled from the validated report object with fixed section order and wording ([Markdown renderer](../../src/inspektorium/report/markdown_report.py)).
Neither renderer reads the system clock.
JSON contains `generated_at: null` by default; Markdown then omits its date line.
A non-null timestamp must be explicit timezone-aware input metadata. It is excluded from fingerprints.

Determinism means fixed inputs, saved proposals and timestamp settings give stable report bytes (P06).
It does not mean repeated live model calls are identical.

The report labels evaluator content separately from deterministic checks.
Each finding's `Citation text and offset check:` line reads one of three values:

- `exact match (not a check of meaning)`;
- `no exact match`;
- `not performed — no citation required or supplied for this proposal`.

A quotation is headed `Proposed quotation — exact text and offset match (not a check of meaning):` or `Proposed quotation — no exact text and offset match:`.
A failed proposal's issue is repeated in the warning section.
The JSON scope statement keeps its wording: "Citation validation confirms exact text and offsets, not semantic truth."

There is no aggregate quality score, trust score, severity weight, rank, probability or answer-level label.
Findings remain discrete and inspectable.

## Display convention for untrusted text

Text from the answer, the sources or the evaluator is data, not report structure (P12).
This holds inside host-composed lines and for issue messages, scope statement and limitations read back from JSON.
The Markdown renderer passes each value exactly once through the encoder for its context ([display module](../../src/inspektorium/report/display.py)).
The contexts are: after a host label, at the start of a line or list item, and inside a block quote.

1. **Markers.** Every character of the Unicode general categories Cc, Cf, Cs, Zl and Zp is shown as `⟦U+XXXX⟧`.
   So is every code point unassigned (Cn) in the running Python's Unicode database.
   The hexadecimal is uppercase with at least four digits, for example `⟦U+202E⟧`.
   This covers TAB, CR, NEL, bidirectional controls, zero-width characters including ZWJ (U+200D) and ZWNJ (U+200C).
   It also covers U+2028, U+2029 and noncharacters such as U+FFFE.
   The only exception is LF inside a quotation, which is a line break.
   LF elsewhere, CR (also the CR of CRLF) and other line terminators become markers on the same line.
   They cannot start a new report or status line.
   The exact marker brackets U+27E6 and U+27E7 are always shown as markers.
2. **At signs and combining runs.** The at sign is displayed as `⟦U+0040⟧`.
   At most four consecutive Mn/Me characters stay raw; the fifth and every later one is marked.
   The bounded lookback examines at most four predecessors per character, so processing is linear.
   Variation selectors and U+034F follow this category rule.
   Private-use characters (Co), Hangul fillers and other characters outside the named categories stay unchanged.
3. **Unicode version.** Category membership comes from the running Python's `unicodedata` module.
   Its Unicode version is 14.0 in Python 3.11 and 15.1 in Python 3.13.
   A character assigned in a newer Unicode version is Cn there and is shown as a marker.
   This keeps later format characters, such as U+13439 to U+1343F, from appearing raw on an older Python.
4. **Escapes.** The characters `` < & \ ` * _ [ ] ~ | $ `` are escaped wherever they occur.
   `.`, `:` and `/` are escaped unless a space or the end of the text follows.
   `.` is also escaped after `www`. This stops URL, `www.` and domain autolinks.
   `<` and `&` are written as `&lt;` and `&amp;`.
   A backslash escape is used only for `` \ ` * _ { } [ ] ( ) > # + - . ! ``, which CommonMark and Python-Markdown both accept.
   Every other escaped character becomes a decimal numeric character reference, for example `&#58;` for `:`.
5. **Line starts.** At a line start, leading spaces become no-break spaces and a leading ASCII punctuation character is escaped.
   The `.` or `)` of an ordered-list marker is escaped.
   No heading, list, block quote, fence, table, thematic break, HTML block or indented code block can begin there.
6. **Quotations.** A quotation is split only on LF. Each line is prefixed with `> `; an empty line becomes `>`.
   A line followed by another non-empty line ends with two spaces, a hard line break.
7. **Identifiers.** A claim or source ID that is a valid schema identifier is shown as a code span.
   Any other value is encoded as text.
8. **Display note.** The Summary section of every Markdown report states this convention.

Markers and escapes are display-only.
The JSON report keeps the exact characters.
Canonical text, offsets, raw proposals and fingerprints are unchanged, and no extra normalization is applied.
Atomic claim text occupies its own paragraph before the host-control list.

## Audit workflow controls

The audit workflow has its own parser, validators, renderers and versioned controls.
Its code lives in `inspektorium.audit`:

| Area | Subpackage | Role |
| --- | --- | --- |
| Command group | `cli` | The five `audit` operations |
| Workflow | `workflow/` | Bundle, live/replay, pipeline, projection, rendering (Phase 10) |
| Forensics | `forensics/` | Semantic and inferential analysis and taxonomy (Phase 8) |
| Review | `review/` | Disagreement routing, adjudication, review history (Phase 9) |
| Execution | `execution/` | Runner, evaluator, task loading |
| Integrity | `integrity/` | Artifact binding, audit trail, output contract, release boundary, budget ledger |
| Checks | `checks/` | Claim, consistency, forecast, reasoning, step and confidence checks |

### Operational states and exits

| Status | Meaning |
| --- | --- |
| `PREFLIGHT_BLOCKED` | Correct the task or offline provider/input selection |
| `RUN_FAILED` | Ended without usable output; a new run creates a new revision |
| `ANALYSIS_INCOMPLETE` | Output could not be bound to the source; not reviewed, not released |
| `REVIEW_REQUIRED` | Not conclusively resolved and not released; needs a recorded human decision or a new run |
| `RELEASE_BLOCKED` | Resolve the named integrity, control or render failure |
| `READY_FOR_RELEASE` | Inspect the candidate; an explicit local release is still required |
| `RELEASED` | These exact local artifact bytes passed the current controls and explicit intent |

- `validate` exits 0 for eligible input and 2 for blocked input.
- `run`, `review` and `release` exit 0 for their ready or released outcome and 2 for a controlled block.
- `inspect` exits 0 for an intact bundle even when its recorded status is blocked. Read both `valid` and `status`.
- Invalid or tampered bundles exit 2. Usage errors exit 2; technical file errors may exit 1.
- There is no force-release switch.

### Controls

- **Execution modes.** `audit run` takes exactly one of `--offline`, `--live` or `--replay`.
  Offline mode accepts only the built-in recording provider and never falls back to a network call.
- **Live authorization.** Live and replay need an authorization directory (authorization, ledger, raw captures) and a registered profile.
  Every provider call first reserves its maximal exposure in the ledger. Unknown billing stays reserved.
- **Raw captures.** The raw response is written to disk before it is interpreted. Answered slots are never resent.
- **Replay.** Replay re-analyses captured responses without a model call and keeps their live origin.
- **Credentials.** Read only from `ANTHROPIC_API_KEY` and never stored.
- **Gate inventory.** Preflight; parse, source and completeness; five binding, strength, symmetry, value-origin and search-scope checks.
  Also Phase-8 semantics and taxonomy, Phase-9 history and review, provenance, and both report files.
  A gate must execute at its current version.
- **Bundles.** Each bundle has `record.json`, `decision.json`, `manifest.json`, `report.md` and `report.html`. Canonical PDF is unsupported.
- **Fingerprint chain.** Reports bind the record and provenance core. The decision binds the checked reports.
  The manifest binds record, decision and reports. Revisions link their parent's manifest fingerprint.
  Bundles also bind the bytes of the installed audit-runtime modules.
- **Inspection.** `audit inspect` recomputes controls from raw-bound history under the installed code.
  Old green fields alone cannot authorize a changed artifact.
- **Release.** `audit release` rechecks the candidate and writes a new immutable revision. Candidate bytes stay unchanged.
- **Review.** `audit review` appends a recorded human decision and creates a new revision.
  A reviewer name or reason cannot waive a failed control.
- **Report text.** Reports use a deterministic projection with no extra model call.
  Model and source text is escaped or literal and cannot supply trusted HTML or status markup.
  Control, bidirectional and invisible format characters are shown as `⟦U+XXXX⟧`; `record.json` keeps the exact characters.

Source for this section: the audit runtime operational guide, preserved as `README.md` in the [research record][record]'s runtime folder.

## Scope boundaries

### Reference checker (`inspektorium inspect`)

The reference checker keeps the 0.1.1 behaviour and report schema 0.1. It provides:

- one answer per inspection, with one or more explicitly supplied text sources;
- evaluator-proposed atomic claims and the four relations;
- exact claim-span and citation-span validation and a citation-gated `reportable_relation`;
- qualitative evidence sufficiency and evaluator certainty;
- NFC/LF canonicalization, Python character offsets and SHA-256 fingerprints;
- deterministic JSON and Markdown reports with the display convention above;
- strict JSON parsing for proposals and `--input`;
- exactly one optional real provider, Anthropic;
- exactly five synthetic offline examples in [examples/inspect](../../examples/inspect/).

It excludes:

- global, weighted, trust, quality or severity scores;
- calibrated probabilities or answer-level labels;
- case libraries, benchmarks, rankings, multi-model comparison or a second provider;
- agents, orchestration, semantic retry loops, batch datasets or directory crawling;
- human adjudication, source-quality ranking or automated web research;
- fuzzy quotation recovery, automatic repair or silent evidence substitution;
- execution authorization, budget ledgers, checkpoint authentication, scientific inference checks and a release gate;
- report authentication, full evaluator provenance and a `verify` command.

### Audit workflow (`inspektorium audit`)

Audit adds input validation, recorded or authorized execution, bundle inspection, explicit human review and local artifact release.
These are bounded research controls.
Phases 8–10 (R08–R10) are implemented and offline tested; their research efficacy is open.
The [v0.1.1 evidence package](../../evidence/v0.1.1/) is reproducibility material for the reference checker, not a runtime feature.

### Not claimed

General AI safety, regulatory compliance, certification and alignment are not claimed.
No NIST, DSIT or regulatory endorsement or conformance is implied.
Improved end decisions at acceptable cost is an untested hypothesis (H01).

[record]: https://github.com/LAKITALKS/inspektorium-research-record/tree/record-2026-10-27
