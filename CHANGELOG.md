# Changelog

Package versions follow `pyproject.toml`. The report schema is versioned
separately and remains **0.1**. Release status and approvals are tracked in
[RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md).

## [0.1.1] — Unreleased (candidate)

Maintenance candidate prepared against public `main` at
`4bd0ba9218df80a69089838f824ae0ac28881ac4`. It fixes report display and input
parsing and adds a public, offline-reproducible evidence package. It is not
published; no release date is set until publication.

### Fixed

- **Markdown report display.** Claim text, rationales and quotations were
  written into the Markdown report unescaped; the same applied to issue
  messages and scope text of a report read back from JSON. Embedded line
  feeds and carriage returns could create fake report lines such as a
  forged `Deterministic guard: passed`, and an unterminated HTML comment could
  hide everything after it in HTML-rendering viewers, including real warnings,
  later findings and the limitations section. Each such value is now encoded
  exactly once for the place where it is embedded (after a label, at the start
  of a line, or in a block quote), so that it is shown as text instead of
  creating report lines, headings, lists, tables, code, links or HTML.
  Identifiers that match the schema identifier pattern are still shown as code
  spans.
- **Control, bidirectional and zero-width characters.** Such characters (for
  example U+202E) were written raw. Every character of the Unicode general
  categories Cc, Cf, Cs, Zl and Zp is now shown as a visible marker such as
  `⟦U+202E⟧`: control characters including TAB, CR and NEL, bidirectional
  controls, zero-width characters including ZWJ and ZWNJ, and the line and
  paragraph separators. Every code point that is unassigned (category Cn) in
  the Unicode database of the running Python, including noncharacters such as
  U+FFFE, is also shown as a marker. Only a line feed inside a quotation stays
  a line break; everywhere else it is a marker. The exact marker brackets `⟦`
  (U+27E6) and `⟧` (U+27E7) are also shown as markers when they occur in
  embedded text. The 2026-10-24 correction additionally marks `@` and the
  fifth and later character of every consecutive Mn/Me run; variation
  selectors follow that rule. Private-use and other invisible characters
  outside these categories are not marked. Emoji joined with ZWJ and ZWNJ are
  shown as their parts with markers between them. The JSON report keeps the
  exact characters.
- **Unicode version.** Categories come from the Unicode database of the
  running Python (Unicode 14.0 in Python 3.11, 15.1 in Python 3.13). Marking
  unassigned code points keeps format characters assigned in a later Unicode
  version, such as U+13439 to U+1343F (format characters since Unicode 15.0),
  from appearing raw on an older Python. The trade-off: other characters
  assigned in a newer Unicode version than the running Python knows, such as
  recently added emoji, are shown as markers there, so the Markdown of the same
  JSON report can differ between Python versions. The recorded evidence runs
  used Python 3.11.7 with Unicode 14.0.0.
- **Markdown and HTML characters.** Characters that Markdown or HTML would
  interpret are escaped: `<` and `&` as `&lt;` and `&amp;`, a backslash only
  for characters that both CommonMark and Python-Markdown accept after a
  backslash, and a decimal numeric character reference such as `&#58;` for
  every other escaped character. Multi-line quotations end each continued line
  with two spaces, the Markdown hard line break, so the lines stay separate;
  before, renderers joined them into one line.
- **Strict `--input` parsing.** `--input` JSON with duplicate keys was
  accepted, with the last value silently winning, although proposal parsing
  already rejected duplicates. `--input` now uses the same strict decoder as
  proposal JSON. It rejects duplicate keys at any nesting level, including keys
  that are equal only after JSON escape decoding; the constants `NaN`,
  `Infinity` and `-Infinity`; strings or keys with an unpaired UTF-16
  surrogate; a leading byte order mark; trailing data; nesting deeper than 64
  arrays or objects; and any other invalid JSON. A rejected input ends with
  exit code 2 before proposals are loaded, a provider is constructed, analysis
  runs or output is written, and an existing `--output` file stays untouched.
  Apart from duplicate keys, 0.1.0 already rejected these inputs with exit
  code 2, with less specific messages. Clean inputs give the same models,
  fingerprints and JSON reports as before.
- **Bounded error messages.** An error about a rejected `--input` or
  `--proposals` file is one line that names the reason, or up to three schema
  locations and rules, and does not quote input values; a duplicated key name,
  or an unknown key name in a schema-error location, is shown ASCII-escaped
  and truncated. Before, `--input` schema errors printed
  multi-line validation text that could include input excerpts and raw
  untrusted key names. `--proposals` errors keep their `malformed_proposal:`
  prefixes and now add the reason. Errors on the `--answer`/`--source` path
  keep their previous form.
- **Deeply nested proposals.** A deeply nested `--proposals` file now exits
  with code 2 and a one-line error instead of a traceback with exit code 1.
- **Order of checks.** `--generated-at` is validated before proposals are
  loaded or a provider is constructed; before, a malformed timestamp was
  detected only after a provider call.
- **Output protection.** The rendered report is checked for UTF-8
  encodability before standard output or the output file is opened, so a late
  encoding failure exits with code 2 and leaves an existing `--output` file
  intact instead of truncating it. This is reachable only with report objects
  built without validation.
- **Verified citations require a complete reference.** `ValidatedFinding`, and
  therefore parsing of an `InspectionReport`, now rejects
  `evidence_span_verified: true` when the evidence reference is incomplete
  (`source_id`, `evidence_quote`, `evidence_start` and `evidence_end` not all
  present), with the message "a verified citation requires a complete evidence
  reference". The pipeline never produced such findings; its outputs, the JSON
  schema documents of the public models and report schema 0.1 are unchanged.

### Changed

- Markdown citation labels describe an exact text and offset match instead of
  wording that could suggest semantic or scientific confirmation (wording
  only; no relation, guard rule or JSON field changes):

  | Markdown element | 0.1.0 | 0.1.1 |
  | --- | --- | --- |
  | Summary count | `Exact citation spans confirmed: N` | `Citations with an exact text and offset match: N` |
  | Finding field label | `Citation validation:` | `Citation text and offset check:` |
  | Field value, quotation matched | `exact source quotation confirmed` | `exact match (not a check of meaning)` |
  | Field value, quotation not matched | `citation failed exact validation` | `no exact match` |
  | Quotation heading, matched | `Citation-validated source quotation:` | `Proposed quotation — exact text and offset match (not a check of meaning):` |
  | Quotation heading, not matched | `Proposed quotation — not citation-validated:` | `Proposed quotation — no exact text and offset match:` |

  The field value `not performed — no citation required or supplied for this
  proposal` is unchanged. The scope limitation "Citation validation confirms
  exact text and offsets, not semantic truth." is also unchanged, because it is
  part of the JSON report.
- The Summary section of every Markdown report has a display note that states
  the display convention above.
- An unpaired surrogate in proposal JSON is reported as invalid JSON instead
  of as a schema error; it is rejected either way.
- Python API: `parse_proposal_json` given bytes accepts only strict UTF-8
  without a byte order mark; before, UTF-16, UTF-32 and BOM-prefixed bytes were
  auto-detected. The CLI reads files as UTF-8 text, as before. New public names:
  `inspektorium.providers.parsing.parse_inspection_input_json` and
  `InputParseError`; the modules `inspektorium.core.strict_json` and
  `inspektorium.report.display`; and
  `inspektorium.report.markdown_report.DISPLAY_NOTE`. For untrusted JSON, use
  `parse_inspection_input_json` or `parse_proposal_json` rather than
  `InspectionInput.model_validate_json` or `ProposalBatch.model_validate_json`;
  the latter keep Pydantic's behaviour of letting the last duplicate key win.
- The committed expected Markdown outputs of the examples change accordingly.
  On the tested product commit `fae18242de35facb7c493ff18e86baff3afe2c24`, the
  `expected_report.json`, `input.json` and `proposals.json` files of all five
  examples are byte-identical to `4bd0ba9`. All five `expected_report.md`
  files change by the new citation labels and the display note; the one of
  `05_mixed_and_fabricated_quote` also gains backslash escapes (for example
  `p\.m.`) in one claim and two quotations.
- Documentation: new [AGENTS.md](AGENTS.md); clearer purpose and known limits
  in README, SCOPE and METHODOLOGY; new claim rows P12–P17; status of the
  Phase 8–10 rows (R08–R10); owner-reported historical numbers presented
  qualitatively in the README while the original records stay unchanged (see
  [documentation decisions](evidence/v0.1.1/DOCUMENTATION_DECISIONS.md)).

### Added

- Regression tests: [render safety](tests/test_render_safety.py) and
  [display encoders](tests/test_display.py) for the Markdown display,
  [CLI input rejection](tests/test_cli_input_rejection.py) and
  [input parsing](tests/test_input_parsing.py) for strict input handling, and
  [model invariants](tests/test_model_invariants.py) for every model invariant
  failure branch; further cases in the existing report, example, CLI and parser
  tests. Measured on `fae18242de35facb7c493ff18e86baff3afe2c24`, the full
  suite gives 1123 passed, 0 failed and 0 skipped with 98.02% branch coverage
  on Python 3.11.7, and 1123 passed with 98.02% branch coverage on Python
  3.13.1 (public `main` `4bd0ba9`: 74 passed, 88.11%, on Python 3.11.7). A
  clean reproduction from a fresh checkout, with the built wheel installed
  outside the source tree, confirmed 1123 passed and 98.02% branch coverage on
  Python 3.11.7, 3.12.15 and 3.13.1, with `ruff check .` and `mypy src` clean
  on each.
- [`evidence/v0.1.1/`](evidence/v0.1.1/): a versioned synthetic catalog with
  clean counterparts, a before/after comparison of public `main` `4bd0ba9` and
  this candidate, rendering by several Markdown implementations, and local
  browser DOM and visibility checks.
- Development dependencies `markdown-it-py` and `linkify-it-py` for structural
  rendering tests. The runtime dependencies are unchanged.

### Known display limits

The earlier `403bd3f` check found ink inside the `Answer span` text box in
6/75 Noto Serif and 5/75 local GitHub-like cases. The follow-up `5ace279`
places the claim in its own paragraph before the host-control list. The same
75-case pixel checks now record **0/75 hits and 0 INVALID per style**;
`Answer span` remains measured. See the
[layout follow-up](evidence/v0.1.1/addendum-20261024-e1-layout/README.md).
This bounded result is not a universal font/viewer or readability guarantee.

- Historical defects at `fae1824`: ordinary e-mail / `mailto:` / `xmpp:`
  autolinks and overpainting from unbounded Mn/Me runs. The 2026-10-24
  correction marks `@` and caps raw Mn/Me runs at four. These defects were
  not covered by catalog 1.0; its 70/70 result remains historical. See the
  [separate addendum](evidence/v0.1.1/addendum-20261024/README.md).
- The raw-run bound does not guarantee every font or viewer renders intact.
  Pixel evidence is limited to named Noto configurations, local CSS, viewport
  and Chromium version; it does not test the actual GitHub service.
- Only the exact marker brackets U+27E6 and U+27E7 are always marked.
  Look-alike brackets such as U+301A and U+301B are not marked; text can use
  them to resemble a marker, but they add no report structure.
- Characters assigned in a newer Unicode version than the running Python
  knows, such as recently added emoji, are shown as markers on that Python (see
  "Unicode version" above).
- Post-render features of the GitHub web service (@mentions, issue
  references, emoji shortcodes, math) and other Markdown viewers were not
  tested.
- Python-Markdown was tested only with its `tables` and `fenced_code`
  extensions; other extensions such as `attr_list` or `extra` are not covered.
- A tool that strips trailing spaces from the Markdown file joins the lines of
  a multi-line quotation into one displayed line; text and structure stay
  intact.

### Unchanged

- JSON report output and field names, report schema 0.1, the JSON schema
  documents of the public models, canonical text, offsets and fingerprints;
  no Unicode normalization is added.
- The four relation labels and their semantics, the exact claim/citation guard
  rules (no offset tolerance, no repositioning) and reportability gating.
- The optional Anthropic adapter, the exit-code convention (0 when a report is
  produced, 2 on errors) and the license.

### Local maintenance follow-up — 2026-10-24

Product commit `403bd3fac27f2406a150b2243a691ba4d0b12fbb` implements E1/E2
above and E3: all three environment-setup commands refuse existing `--venv`
targets, including files and dangling symlinks, before setup. The clean path
still creates a new environment. No general setup-tool refactor was made.
JSON reports, canonicalization, offsets, fingerprints, guard semantics,
package version 0.1.1 and schema 0.1 stay unchanged. The display note and five
Markdown example expectations changed. Current checks and Gate R are in the
[addendum](evidence/v0.1.1/addendum-20261024/README.md); this remains a local,
unpublished candidate.


### E1 claim layout follow-up — 2026-10-24

- Claim text is now a separate Markdown paragraph before the tight control
  list; the encoding rule, raw JSON and evaluator/guard semantics stay unchanged.
- The dated follow-up retains the same 87 cases and shows 0/75 image hits
  per style, 0 INVALID and no e-mail links. The measurement also rejects
  matching missing finding rows and duplicate claim containers.
- Historical evidence is preserved. See the
  [follow-up closeout](evidence/v0.1.1/addendum-20261024-e1-layout/README.md).

## [0.1.0] — tag `v0.1.0`, 2026-08-11

First public evidence-binding reference release (annotated tag `v0.1.0` on
commit `a376c4019ca4e616e996f48e108a4214d78fd800`): one answer with explicitly
supplied sources; four evaluator-proposed relations; exact claim-span and
citation-span validation with a citation-gated `reportable_relation`; LF/NFC
canonicalization and Python character offsets; SHA-256 input fingerprints;
deterministic JSON and Markdown reports; strict proposal parsing; one optional
Anthropic adapter; five synthetic offline examples.

Later commits on `main` before 0.1.1 changed no source, test or example file:
authorship metadata (`16f5721`), research-positioning documentation
(`89bf954`) and dependency bounds for the Anthropic SDK and HTTPX (`4bd0ba9`).
