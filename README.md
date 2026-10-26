# INSPEKTORIUM

Evidence integrity controls for AI assurance research.
Website: [inspektorium.org](https://inspektorium.org).

## Two installable components

This repository contains the **Inspektorium core 0.1.1** at the root and
**[Agent Arena](agent-arena/README.md)**, the complete P1–P10 technical research
implementation, as a separate package under `agent-arena/`. Their Python
imports, CLI commands, tests and scientific evidence remain distinct.
See the [publication record](publication/2026-10-26/README.md) for source
mapping, checks, omissions and release links. Both are source-available under
[PolyForm Noncommercial 1.0.0](LICENSE), not OSI open source.

Install into separate fresh Python 3.11+ environments from this checkout:

```sh
python3 -m venv /new/path/core-env
/new/path/core-env/bin/python -m pip install .
/new/path/core-env/bin/inspektorium inspect \
  --input examples/01_supported/input.json \
  --proposals examples/01_supported/proposals.json --format markdown

python3 -m venv /new/path/arena-env
/new/path/arena-env/bin/python -m pip install ./agent-arena
/new/path/arena-env/bin/agent-arena audit validate \
  --task agent-arena/examples/phase10/positive-task.json
/new/path/arena-env/bin/agent-arena audit run \
  --task agent-arena/examples/phase10/positive-task.json \
  --offline agent-arena/examples/phase10/positive-recording.json \
  --output /new/path/positive-bundle
```

Dependency installation may download public packages. The displayed evaluations
use saved synthetic inputs and run offline. The supported Arena operational
entry is `agent-arena audit`; historical research launchers can call providers
and must not be used as an offline demonstration. This publication authorizes
no live calls or reopening of closed budgets. Arena's own live path requires
fresh authorization and budget controls. The core optional provider adapter has
a different, narrower contract described below.

`HUMAN_REVIEW_REQUIRED` / `REVIEW_REQUIRED` remains unresolved without a recorded
human review. Artifact release is a technical workflow decision, not a truth
certificate. Closed Corpus checks only the supplied source package; exact
quotations can still mislead, and model/host agreement is not independent
confirmation. The scientific Final v1 gate remains **not met**. The Arena
release is a public **research prerelease**, with no new live validation of
the final code and no demonstrated general efficacy.

## Purpose and current version

INSPEKTORIUM is a research prototype with a deliberately narrow purpose:
deterministic checking of selected integrity errors in AI analysis artifacts.
For one answer and explicitly supplied text sources it checks

- that each evaluator-proposed claim matches the answer exactly at its span;
- that each proposed citation matches its source exactly in text and offsets;
- that a finding's relation stays reportable only if these checks pass;

and it renders the result as a JSON report and a Markdown report in which
answer, source and evaluator text is displayed as data. It performs no
automated source search and does not judge whether a claim is true.

The evaluator proposes semantic relationships. Deterministic code checks text
bindings before an individual proposal can remain reportable.

| Name | What it is | Status |
| --- | --- | --- |
| public v0.1.0 | First public release, annotated tag `v0.1.0` | Published |
| public v0.1.1 | This version: Markdown display of untrusted text as data and strict `--input` parsing; package 0.1.1, report schema 0.1 | This package; release status in [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) |
| Agent Arena technical research release | Separate package containing P1–P10; derived from the verified internal 1.0.0 snapshot | Public research prerelease; [version and integration record](agent-arena/PUBLICATION.md); no demonstrated scientific efficacy |
| Final v1 gate | Planned efficacy and validation review in the [roadmap](ROADMAP.md#final-v1-gate) | Not met |

Changes are listed in [CHANGELOG.md](CHANGELOG.md).

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
and the rest of the report remain visible.

Text is normalized to LF/NFC, preserving other whitespace; offsets are half-open
Python character indices, not byte offsets. SHA-256 fingerprints identify
current canonical answer/source content and a source-ID-ordered bundle.
Identical canonical IDs/texts are order-invariant; arbitrary paraphrases are
not hash-equivalent. Hashes do not authenticate historical state or source
authority. JSON includes `generated_at: null` by default; Markdown omits the
date line. [Methodology](METHODOLOGY.md) gives the concrete contracts.

### Known limits

- **Exact text is not meaning.** An excerpt can match its source exactly and
  still distort it, for example by omitting a negation (“did not reduce
  mortality” cited as “reduce mortality”). Exact text binding does not confirm
  the meaning of the proposed relation (P14).
- **True quote, false relation.** A true quotation with an intentionally false
  relation remains mechanically reportable (P09).
- **`not_established` is not a refutation.** It may remain reportable with all
  citation fields null. That records the evaluator's judgment that the supplied
  material does not establish the claim; it is not a scientifically examined
  refutation and does not prove absence of evidence (P04, P15). A supplied
  optional citation must still validate.
- **Empty findings and exit 0.** Empty findings are accepted, so zero failures
  does not prove claim coverage (P10). A report with failed citations is still
  emitted with exit 0 (P11).
- **Strict offsets.** A quotation whose text occurs in the source, but not at
  the proposed offsets, is rejected. Quotes are never searched for or
  repositioned. Such a rejection can be inconvenient when only the offset is
  wrong; the tests and examples do not measure a general false-alarm rate
  (P17).
- **A valid report is not a re-check or proof of origin.** A report that
  validates against the schema 0.1 models has not been checked again against
  its sources and is no proof that INSPEKTORIUM produced it. Reports do not
  record full evaluator provenance. Evaluator provenance and a separate
  `verify` command are later work (P16).

## Report display and input parsing (v0.1.1)

The Markdown report shows answer, source and evaluator text as data. Each such
value is encoded once for the place where it appears (after a label, at the
start of a line, or in a quotation), so that it is displayed as text instead
of adding report lines, headings, lists, tables, code, links or HTML:

- Every character of the Unicode general categories Cc, Cf, Cs, Zl and Zp is
  shown as a visible marker such as `⟦U+202E⟧`: control characters (including
  TAB, CR and NEL), bidirectional controls, zero-width characters (including
  ZWJ and ZWNJ) and the line and paragraph separators. So is every code point
  that is unassigned (category Cn) in the Unicode database of the running
  Python, including noncharacters such as U+FFFE. A line feed inside a
  quotation is a line break; everywhere else it is a marker as well.
- The exact marker brackets `⟦` (U+27E6) and `⟧` (U+27E7) are themselves
  marked when they occur in embedded text, so embedded text cannot write a
  marker with these brackets. Look-alike brackets are not marked (see the
  known display limits).
- The at sign is shown as `⟦U+0040⟧` to prevent e-mail autolinks. In each
  consecutive run of Mn/Me characters, only the first four stay raw; the fifth
  and every later character is marked. Variation selectors follow this rule.
- Atomic claim text occupies a separate paragraph before the host-control list.
- Private-use characters (Co) and other invisible characters outside these
  categories are not marked.
  Emoji joined with ZWJ and words written with ZWNJ are therefore shown as
  their parts with markers between them.
- Categories follow the Unicode database of the running Python (Unicode 14.0
  in Python 3.11, 15.1 in Python 3.13). A character assigned in a newer Unicode
  version than that Python knows is unassigned there and is shown as a marker.
  This keeps format characters added later, such as U+13439 to U+1343F, from
  appearing raw on an older Python; in exchange, newer characters such as
  recently added emoji appear as markers there. The recorded evidence runs
  used Python 3.11.7 with Unicode 14.0.0.
- Markdown- and HTML-significant characters are escaped: `<` and `&` as `&lt;`
  and `&amp;`, a backslash only before characters that both CommonMark and
  Python-Markdown accept escaped, and a numeric character reference such as
  `&#58;` otherwise. Multi-line quotations use two trailing spaces as the hard
  line break.
- Citation labels say that text and offsets matched exactly, for example
  "exact match (not a check of meaning)"; they no longer use wording such as
  "citation-validated". A display note in each Markdown report states this
  convention. The [changelog](CHANGELOG.md) lists every changed label.

These markers and escapes exist only in the Markdown display. The JSON report
keeps the exact characters, offsets and fingerprints refer to the unchanged
canonical text, and no Unicode normalization is added.

Known display limits:

The earlier `403bd3f` check found ink inside the `Answer span` text box in
6/75 Noto Serif and 5/75 local GitHub-like cases. The follow-up `5ace279`
places the claim in its own paragraph before the host-control list. The same
75-case pixel checks now record **0/75 hits and 0 INVALID per style**;
`Answer span` remains measured. See the
[layout follow-up](evidence/v0.1.1/addendum-20261024-e1-layout/README.md).
This bounded result is not a universal font/viewer or readability guarantee.

- The earlier candidate `fae1824` allowed e-mail autolinks and unbounded
  combining-mark runs. The 2026-10-24 correction marks `@` and limits raw
  Mn/Me runs to four. The [dated E1/E2/E3 addendum](evidence/v0.1.1/addendum-20261024/README.md)
  records separate before/after checks; the old 70-case result is unchanged.
- The text bound is independent of font choice; it is not a universal visual
  guarantee. Image evidence covers the named Noto and local GitHub-like CSS
  configurations only.
- Look-alike brackets such as U+301A and U+301B are not marked. Text can use
  them to resemble a marker; they add no report structure.
- Post-render features of the GitHub web service (@mentions, issue
  references, emoji shortcodes, math) and other Markdown viewers were not
  tested, and Python-Markdown was tested only with its `tables` and
  `fenced_code` extensions (not with extensions such as `attr_list` or
  `extra`).
- A tool that strips trailing spaces from the Markdown file joins the lines of
  a multi-line quotation into one displayed line; text and structure stay
  intact.

`--input` JSON now goes through the same strict decoder as proposal JSON.
Duplicate keys at any nesting level (also keys that are equal only after JSON
escape decoding), `NaN` and `Infinity`, unpaired surrogates, a byte order mark,
trailing data, nesting deeper than 64 levels and invalid JSON are rejected with
exit code 2 before any provider call, analysis or output; of these, 0.1.0
accepted only the duplicate keys, silently using the last value. An existing
`--output` file stays untouched, and the one-line error does not quote input
values (a duplicated key name, or an unknown key name in a schema error, is
shown ASCII-escaped and truncated). Python code that parses untrusted JSON
should call `parse_inspection_input_json` or `parse_proposal_json` from
`inspektorium.providers.parsing`, not `InspectionInput.model_validate_json` or
`ProposalBatch.model_validate_json`, which keep Pydantic's behaviour of letting
the last duplicate key win. Report models now also require a complete evidence
reference whenever `evidence_span_verified` is `true`. The methodology
describes the
[display rule](METHODOLOGY.md#display-convention-for-untrusted-text-011) and
the [input checks](METHODOLOGY.md#validation-outcomes-and-failure-codes) in
detail.

The [v0.1.1 evidence package](evidence/v0.1.1/) compares public `main`
`4bd0ba9` with this version (commit
`fae18242de35facb7c493ff18e86baff3afe2c24`) on a published synthetic catalog
of 70 cases. Each Markdown report is rendered by four configurations:
cmark-gfm 0.29.0.gfm.13 (Python package `cmarkgfm` 2025.10.22) with the GitHub
Flavored Markdown extensions, once with raw HTML allowed and once in its
default safe mode; markdown-it-py 4.2.0 (CommonMark preset with HTML enabled,
plus tables and strikethrough); and Python-Markdown 3.11 (`tables` and
`fenced_code`). DOM and visibility are checked in Chromium 153.0.8010.12
(Playwright 1.63.0, headless, page JavaScript disabled). In this published
synthetic catalog, the tested inputs produced no forged control lines after
the fix and hid no warnings; the clean counterparts stayed correctly
displayable. Measured on this version: 70 of 70 cases hold; of 280 renderings
(70 cases × 4 configurations), 224 keep all controls intact and the other 56
belong to the 14 inputs that are, as expected, rejected before rendering. On
`4bd0ba9`, 22 of 70 cases hold and 165 of 280 renderings are manipulated. This
is evidence for that catalog and those renderers, not a universal guarantee or
a statement about scientific correctness; the known display limits above lie
outside the catalog.

## Capability and evidence status

| Status | Capability or result | Boundary |
| --- | --- | --- |
| IMPLEMENTED + TESTED IN PUBLIC v0.1 | Exact spans, input fingerprints, deterministic JSON/Markdown, strict offline proposal parsing | Public code and regression evidence; P01–P07 |
| IMPLEMENTED + TESTED IN PUBLIC v0.1.1 | Markdown display of untrusted text as data; strict `--input` parsing | Public code, tests and the offline [evidence package](evidence/v0.1.1/); synthetic catalog only; P12–P13 |
| OWNER-REPORTED INTERNAL EXPERIMENT | Artifact-fault pilot: full controls blocked more injected artifact faults than baseline processing and accepted all clean counterparts | Small constructed set; not reproduced by this package; no accuracy gain and semantic misses retained; I01–I03 |
| PUBLIC RESEARCH SOURCE | Execution authorization, budget/state/environment controls | [Arena source](agent-arena/src/agent_arena/); historical evidence retains its conditions; I04 |
| PUBLIC RESEARCH IMPLEMENTATION — PHASES 8–10 | Semantic/inferential checks, disagreement and review, operational reporting | [Arena](agent-arena/); separate from core; no demonstrated scientific efficacy; R08–R10 |
| NOT CLAIMED | General AI safety, regulatory compliance, certification, alignment | No framework endorsement or conformance claim |

The [claim ledger](CLAIMS.md) supplies each claim's evidence, version and access
status. Publication makes the separate Arena code inspectable; it does not
retroactively validate historical experimental claims.

## Evidence and limitations

[Research results](RESEARCH_RESULTS.md) distinguishes public observations,
historical CI and owner-reported internal studies. Saved examples reproduce
report bytes; they do not measure live-model classification accuracy.

The owner-reported internal pilot found no main-case accuracy difference
between its conditions, all of which were at ceiling, and both semantically
wrong but structurally valid control answers were accepted. The small
constructed set, shared responses between conditions and lack of independent
human peer review constrain interpretation. The original counts of this pilot and of an
earlier contract study are kept unchanged as historical owner-reported records
in [Research results](RESEARCH_RESULTS.md) and the [claim ledger](CLAIMS.md).
They are not current public performance claims, and the v0.1.1 evidence
package does not support them retroactively.

Evidence integrity and provenance mean textual/input binding here. Reliability
is limited to fixed saved inputs, proposals and timestamp settings; robustness
evidence names the tested malformed JSON, fields, spans, normalization and
display disturbances. Neither establishes source quality, evidence
completeness, scientific validity or correctness outside the supplied material.

## Research roadmap

[Phase 8](ROADMAP.md#phase-8--deep-forensics) covers scientific claim forensics,
[Phase 9](ROADMAP.md#phase-9--disagreement--review) disagreement and review,
and [Phase 10](ROADMAP.md#phase-10--reporting--operational-finish) operational
reporting and release controls. These implementations are now published in
the separate Arena package with offline checks and bounded historical live
evidence on earlier states. The final code was not live-tested again. The final v1 gate requires fresh
efficacy and fault comparisons, real-case validation, prior criteria and
negative results; it is not met.

[Research plan](RESEARCH_PLAN.md) specifies falsifiable questions, informative
baselines and future demonstrations. These are planned comparisons, not new
capabilities or permission to run studies.

## Development, provider, license and citation

```bash
python -m pip install -e '.[dev]'
ruff check .
mypy src
pytest --cov=inspektorium --cov-report=term-missing --cov-fail-under=80
```

The tests use saved proposals and mocked provider transport. See
[Contributing](CONTRIBUTING.md) for scope and claim-ledger requirements and
[AGENTS.md](AGENTS.md) for the working rules that bind agent-assisted changes.

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
open-source license. [CITATION.cff](CITATION.cff) names software version 0.1.1
with the publication date; no DOI is assigned.

**Author and maintainer:** Lazaros Varvatis —
[LAKITALKS](https://github.com/LAKITALKS).
