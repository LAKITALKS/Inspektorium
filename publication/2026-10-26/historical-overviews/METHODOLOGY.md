# Methodology

## Purpose

INSPEKTORIUM is a research prototype studying evidence integrity controls for
AI assurance. Its public v0.1 kernel focuses on one inspectable operation: an
evaluator proposes how an answer relates to supplied sources, and deterministic
code checks the exact textual binding of the proposed claim and citation spans
before allowing that proposal to remain reportable, and renders a report in
which answer, source and evaluator text is displayed as data. Package 0.1.1;
report schema 0.1.

Here, AI assurance research produces inspectable evidence for a bounded
property, including contrary evidence and limitations. Technical AI governance
means a named rule enforced at a named system boundary with a traceable
decision. The current boundary is one finding's reporting field. Execution,
state and authorization controls are reported internally. Scientific
inference, review and operational reporting workflows (Phases 8–10) are
reported as implemented in a separate, non-public internal technical v1.0.0,
without demonstrated scientific efficacy. None of these are public v0.1
capabilities.
See [claim ledger](CLAIMS.md), [results](RESEARCH_RESULTS.md) and
[scope](SCOPE.md) for separate version and access status.

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

These public contracts are claims P01–P17 in [CLAIMS.md](CLAIMS.md). A failure
sets only the individual finding's `reportable_relation` to null. It neither
erases the proposal nor suppresses the entire report. The mixed faulty-quote
example produces a report with CLI exit code 0. That code means successful
report production, not assurance approval, execution authorization or permission
to release an artifact. Public v0.1 implements no production release gate.

The supplied reviewer counterexample changes example 02's proposed relation
from `contradicted` to `supported` while preserving the exact true quote and
offsets. It remains mechanically reportable despite the intentionally false
semantic relationship. This is a boundary of exact binding, not semantic
verification. Empty findings are also allowed: zero failures establishes
neither complete extraction nor coverage of an answer's claims.

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

The offset rule is strict. A quotation whose text occurs in the source, but not
at the proposed offsets, fails with `invalid_evidence_offsets` or
`evidence_span_mismatch`; INSPEKTORIUM does not search for it or move it. This
intentionally rejects a correct quotation with a wrong offset. The tests and
examples demonstrate the rule; they do not yield a general false-alarm rate
for real evaluator output (P17).

Exactness also has a semantic limit. An excerpt can match its source exactly
and still distort it, for example by omitting a negation: the source says “did
not reduce mortality” and the quotation is “reduce mortality”. Exact text
binding confirms where the words are, not what the relation means (P14).

## The special case of `not_established`

Absence of a citation does not prove absence of support. `not_established` is a
semantic evaluator judgment and may be proposed with all evidence fields null
so the schema does not encourage fabricated evidence.

The deterministic guard can confirm the claim span and structural integrity,
but it does not prove source insufficiency. A reportable `not_established`
without a citation is an evaluator judgment about the supplied material, not a
scientifically examined refutation (P15). If an evaluator optionally supplies
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
  since 0.1.1 the report models accept `true` only together with a complete
  evidence reference (source ID, quotation and both offsets), see
  [invariant tests](tests/test_model_invariants.py);
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

The Anthropic adapter uses the SDK's Pydantic parse helper, which transforms the
public proposal model into the supported native JSON-schema wire format and
validates the response against the original strict model. Provider JSON that is
malformed or violates the strict schema still fails before finding validation.
No prose extraction or schema repair is attempted.

Strict offline proposal parsing separately rejects malformed/ambiguous JSON,
including duplicate keys and nonstandard numeric constants, as well as schema
violations. Evidence is in [parser tests](tests/test_parser.py) and
[model tests](tests/test_models.py) (P07).

Since 0.1.1, `--input` files and proposal JSON go through one
[strict decoder](src/inspektorium/core/strict_json.py) before schema
validation. It rejects duplicate keys at any nesting level, including keys
that are equal only after JSON escape decoding; the constants `NaN`,
`Infinity` and `-Infinity`; strings or keys with an unpaired UTF-16
surrogate; a leading byte order mark; trailing data; nesting deeper than 64
arrays or objects; and any other invalid JSON. Nothing is repaired or retried
with a more permissive parser. In the CLI, the `--input` file and
`--generated-at` are validated before proposals are loaded or a provider is
constructed. A rejected input ends with exit code 2 before analysis or output,
and an existing `--output` file stays untouched; the rendered report is also
checked for UTF-8 encodability before anything is written. An error about a
rejected `--input` or `--proposals` file is one bounded line that names the
reason or up to three schema locations and rules and does not quote input
values; a duplicated key name, or an unknown key name in a schema-error
location, is shown ASCII-escaped and truncated. Clean inputs produce the same
models, fingerprints and reports as before; the raw bytes of an input file are
not hashed, only the canonical text (see fingerprinting below). Evidence:
[CLI rejection tests](tests/test_cli_input_rejection.py) and
[input parsing tests](tests/test_input_parsing.py) (P13).

The strict decoder applies to `--input` and `--proposals` files and to the
two parsing functions that the CLI uses for them. Python code that handles
untrusted JSON should call `parse_inspection_input_json` or
`parse_proposal_json` from `inspektorium.providers.parsing` rather than
`InspectionInput.model_validate_json` or `ProposalBatch.model_validate_json`,
which keep Pydantic's behaviour of letting the last duplicate key win.

Also since 0.1.1, a finding whose `evidence_span_verified` is `true` must carry
a complete evidence reference; otherwise `ValidatedFinding`, and therefore
`InspectionReport` parsing, fails with "a verified citation requires a
complete evidence reference". The validator never produced such findings, so
pipeline outputs, the JSON schema documents and report schema 0.1 are
unchanged; only hand-built or altered findings of this kind are now rejected
(P13).

The optional provider path has one application SDK proposal invocation and no
authored semantic repair loop (P08). This does not guarantee a single HTTP attempt, bounded billing or
authenticated execution. Mocked transport checks are software regressions,
not live-model accuracy experiments.

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
timestamps are excluded. The same canonical source IDs and texts, with the
same canonical answer, have the same bundle digest regardless of source order.
Arbitrary semantically equivalent paraphrases are not hash-equivalent. The
hash identifies current canonical content; it does not establish authorship,
source quality, source authority or historical-state authentication (P05).

Changing source text outside a cited span changes the source and bundle hashes
but need not invalidate that unchanged citation span. Public v0.1 does not
compare the new hash against an authenticated historical state. A hash is not
a signature and cannot protect against replacement of all trusted state/code.

## Deterministic reports

JSON rendering uses sorted keys, fixed indentation, UTF-8-compatible Unicode,
and one terminal newline. Markdown is assembled from the validated report
object with fixed section order and wording. Neither renderer reads the system
clock. JSON contains `generated_at: null` by default; Markdown omits its date
line when no explicit timestamp is supplied. A non-null timestamp must be
explicit timezone-aware input metadata. It is excluded from input fingerprints.

Determinism means fixed canonical inputs, fixed saved proposals and fixed
timestamp settings produce stable report bytes under the tested operating
conditions (P06). It does not mean repeated live model calls are identical.

The report visually labels evaluator-generated semantic content separately
from deterministic checks. Since 0.1.1 each finding's
`Citation text and offset check:` line reads `exact match (not a check of
meaning)`, `no exact match` or `not performed — no citation required or
supplied for this proposal`, and a quotation is headed either
`Proposed quotation — exact text and offset match (not a check of meaning):`
or `Proposed quotation — no exact text and offset match:`. Neither claims a
semantic or scientific confirmation. A failed proposal's issue is repeated in
the warning section. The scope limitation "Citation validation confirms exact
text and offsets, not semantic truth." keeps its wording because it is part of
the JSON report. The [changelog](CHANGELOG.md) lists the 0.1.0 wording.

### Display convention for untrusted text (0.1.1)

Claims, rationales, quotations and other text that originates from the answer,
the sources or the evaluator are data, not report structure. This also holds
when such text is embedded in a line that the report composes around it, and
for the issue messages, scope statement and limitations of a report read back
from JSON. The Markdown renderer passes each such value exactly once, where it
is embedded, through the encoder for its context in the
[display module](src/inspektorium/report/display.py): after a host label on
the same line, at the start of a line or list item, or inside a block quote.
The rule is:

1. **Markers.** Every character of the Unicode general categories Cc, Cf, Cs,
   Zl and Zp, and every code point that is unassigned (category Cn) in the
   Unicode database of the running Python, is shown as `⟦U+XXXX⟧` (uppercase
   hexadecimal, at least four digits), for example `⟦U+202E⟧`. This covers
   control characters including TAB, CR and NEL, bidirectional controls,
   zero-width characters including ZWJ (U+200D) and ZWNJ (U+200C), the line
   and paragraph separators U+2028 and U+2029, and noncharacters such as
   U+FFFE. The only exception is LF inside a quotation, which is a line break.
   LF anywhere else, CR (also the CR of CRLF) and the other line terminators
   are markers on the same line, so they cannot start a new report or status
   line. The exact marker brackets U+27E6 and U+27E7 are themselves always
   shown as markers, so embedded text cannot write a marker with these
   brackets; look-alike brackets are a known limit (below).
2. **At signs and combining runs.** The at sign is displayed as `⟦U+0040⟧`.
   At most four consecutive Mn/Me characters stay raw; the fifth and every
   later character is marked. The bounded lookback examines at most four
   predecessors per character, so processing is linear in the input length.
   Variation selectors and U+034F follow this category rule. Private-use
   characters (Co), Hangul fillers and other characters outside the named
   categories remain unchanged. ZWJ/ZWNJ continue to be shown as markers.
3. **Unicode version.** Category membership comes from the `unicodedata`
   module of the running Python, whose Unicode version depends on the Python
   version (Unicode 14.0 in Python 3.11, 15.1 in Python 3.13). A character
   assigned in a newer Unicode version than that Python knows is unassigned
   (Cn) there and is therefore shown as a marker. This keeps format characters
   assigned later, such as U+13439 to U+1343F (format characters since Unicode
   15.0), from appearing raw on an older Python. The trade-off is that other
   characters assigned later, such as recently added emoji, also appear as
   markers on an older Python, so the Markdown of the same JSON report can
   differ between Python versions. The recorded evidence runs used Python
   3.11.7 with Unicode 14.0.0.
4. **Escapes.** The characters `` < & \ ` * _ [ ] ~ | $ `` are escaped
   wherever they occur. The characters `.`, `:` and `/` are escaped unless a
   space or the end of the text follows them, and `.` is also escaped after
   `www`; this stops URL, `www.` and domain autolinks while leaving sentence
   punctuation as it is. `<` and `&` are written as `&lt;` and `&amp;`. A
   backslash escape is used only for the characters that both CommonMark and
   Python-Markdown accept after a backslash
   (`` \ ` * _ { } [ ] ( ) > # + - . ! ``); every other escaped character is
   written as a decimal numeric character reference, for example `&#58;` for
   `:`. Renderers decode these references to the literal character after the
   Markdown structure has been parsed.
5. **Line starts.** At the start of a line (quotation lines, the scope
   statement and limitation items), leading spaces become no-break spaces, a
   leading ASCII punctuation character is escaped, and the `.` or `)` of an
   ordered-list marker is escaped. No heading, list, block quote, fence, table,
   thematic break, HTML block or indented code block can begin there.
6. **Quotations.** A quotation is split only on LF. Each line is prefixed with
   `> `, an empty line becomes `>`, and a line followed by another non-empty
   line ends with two spaces, the hard line break that CommonMark, GitHub
   Flavored Markdown and Python-Markdown render as a line break.
7. **Identifiers.** A claim or source ID that is a valid schema identifier
   (pattern and length) is shown as a code span; any other value, which only
   a report built without validation can contain, is encoded as text.
8. **Display note.** The Summary section of every Markdown report states this
   convention.

Legitimate text such as German, Greek, right-to-left script without control
characters, emoji without joiners (that the running Python's Unicode database
knows) and literal Markdown characters stays readable after rendering. The
rule applies only inside these protected display elements and is not a
document-wide rewrite. Tests:
[render safety](tests/test_render_safety.py) and
[display encoders](tests/test_display.py) (P12).

These markers and escapes are display-only. The JSON report keeps the exact
characters; canonical text, offsets, raw proposals and fingerprints are not
changed, and no additional Unicode normalization is applied. Offsets always
refer to the canonical text, never to the escaped display.

Known display limits:

The earlier `403bd3f` check found ink inside the `Answer span` text box in
6/75 Noto Serif and 5/75 local GitHub-like cases. The follow-up `5ace279`
places the claim in its own paragraph before the host-control list. The same
75-case pixel checks now record **0/75 hits and 0 INVALID per style**;
`Answer span` remains measured. See the
[layout follow-up](evidence/v0.1.1/addendum-20261024-e1-layout/README.md).
This bounded result is not a universal font/viewer or readability guarantee.

- Before the 2026-10-24 correction, cmark-gfm produced ordinary e-mail,
  `mailto:` and `xmpp:` links and long Mn/Me runs could overpaint real warning
  and failed-guard lines. Catalog 1.0 did not cover these cases. The separate
  [addendum](evidence/v0.1.1/addendum-20261024/README.md) preserves these
  violations and checks the corrected display, including actual CLI output,
  a font-independent raw-run criterion and bounded pixel comparisons.
- A maximum of four raw marks is a text property, not proof of visual
  integrity in every font or viewer. The pixel comparisons require all host
  lines, including real failed guards and warnings, and reject missing
  screenshots, changed host box dimensions or unmeasured rows.
- Look-alike brackets such as U+301A and U+301B are not marked. Text can use
  them to resemble a marker; they add no report structure.
- Post-render features of the GitHub web service (@mentions, issue
  references, emoji shortcodes, math) and other Markdown viewers were not
  tested.
- Python-Markdown was tested only with its `tables` and `fenced_code`
  extensions; other extensions such as `attr_list` or `extra` are not covered.
- A tool that strips trailing spaces from the Markdown file joins the lines of
  a multi-line quotation into one displayed line; text and structure stay
  intact.

This is the current public reporting layer. Phase 10 describes a canonical
operational release workflow and post-render QA (public roadmap; internal
implementation owner-reported only); it does not defer the already implemented
JSON and Markdown renderers into future work.

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
- that an answer is globally good or bad;
- that an exact excerpt preserves the meaning of its context (P14);
- that a reportable `not_established` is a scientifically examined refutation
  (P15);
- that a report which validates against the schema was re-checked against its
  sources or was produced by INSPEKTORIUM. Reports do not carry full evaluator
  provenance; evaluator provenance and a separate `verify` command are later
  work (P16).

These are limits of the question Inspektorium asks, not exceptions hidden from
the report.

## Extensibility and independent study

Inspektorium is intentionally a small reference point, not a complete doctrine.
Researchers and developers can study these assumptions and counterexamples
within the [license](LICENSE). Proposed capability changes require separate
review under [SCOPE.md](SCOPE.md). [RESEARCH_PLAN.md](RESEARCH_PLAN.md) separates
system-controls research, model evaluation, scientific claim forensics and
software governance rather than treating exact binding as proof of all four.

The internal fault pilot is owner-reported evidence about its particular
corrupted artifacts and clean controls, not an experiment run by public v0.1.
The public regressions test named quote/offset/JSON/normalization disturbances.
Neither evidence class establishes general AI safety, regulatory compliance,
certification, alignment, or endorsement/conformance to any external framework.
