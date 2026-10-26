# Inspektorium v0.1.1 evidence package

> Historical record of 2026-10-13, retained with its original counters and
> known limits. It is not acceptance evidence for the later E1/E2/E3 changes.
> Later follow-ups: [E1/E2/E3 closeout](addendum-20261024/README.md) and
> [current E1 layout closeout](addendum-20261024-e1-layout/README.md).
> In the current setup tool, existing `--venv` targets are refused; the older
> replacement warning below describes the historical tool.

This directory holds a small, offline-reproducible evidence package for the
v0.1.1 fixes to report display (Markdown rendering) and input parsing. It
measures two exactly identified versions on one frozen synthetic catalog:

* **Baseline:** public `main@4bd0ba9218df80a69089838f824ae0ac28881ac4`
  (package 0.1.0, report schema 0.1). This is not the historical tag `v0.1.0`.
* **Candidate:** commit `fae18242de35facb7c493ff18e86baff3afe2c24`
  (package 0.1.1, report schema 0.1).

An earlier candidate, commit `7c9d43890e25006ae9d035866350f8d62083718e`, was
measured before a correction from the independent review (code points that
are unassigned in the running Python's Unicode database were not marked). It
is superseded by the candidate above; its runs are not part of this package.

Everything here is synthetic. No model or provider was called, no API key was
present, and no internal project data is included.

## Result in one paragraph

In the published synthetic catalog (70 cases, 4 renderer configurations), the
tested inputs produced no forged control displays after the fix and hid no
warnings; the clean counterparts stayed correctly displayable. Measured: the
baseline run is `FAIL` (22 of 70 cases hold, 48 fail); the candidate run is
`PASS` (70 of 70 cases hold). On the candidate all 42 attack cases hold, with
168 of 168 attack renderings `RENDERED_CONTROLS_INTACT`, and all 7 clean
counterparts and 3 readability cases hold (40 of 40 renderings intact). All 12
ambiguous or invalid inputs are rejected before rendering without touching an
existing output file, all 3 valid inputs are accepted, and the JSON reports are
byte-identical between the two versions for all 56 cases that both versions
accept. These numbers apply to this catalog only; they are not a detection
rate, not a false-alarm rate and not a guarantee for other inputs or viewers.

## Version binding

| | Baseline | Candidate |
|---|---|---|
| Commit | `4bd0ba9218df80a69089838f824ae0ac28881ac4` | `fae18242de35facb7c493ff18e86baff3afe2c24` |
| Package / report schema | 0.1.0 / 0.1 | 0.1.1 / 0.1 |
| `git archive` (tar) SHA-256 | `1a8ff3fddde3ddd30868e828e87673c84d636870c0c84e1f392e9e7aad41a77b` | `2c00a9cdcf0684c378afabea3524ca9e99f18f9b01eea580a1e8eb5723d2d897` |
| Wheel | `inspektorium-0.1.0-py3-none-any.whl` | `inspektorium-0.1.1-py3-none-any.whl` |
| Wheel SHA-256 | `3ee9e4019fc00f31513a402a23c4b1d8d9c184221dba79436832e89a8dece0aa` | `9c71b5970fd2c8f97c5cfa5efdacd25d29c50388f14647301ada4e59391f6f81` |
| Import check | `site-packages` of its own venv, `__version__` 0.1.0, not from the source tree | `site-packages` of its own venv, `__version__` 0.1.1, not from the source tree |
| Label map (`config/versions.json`) | `inspektorium-0.1.0` | `inspektorium-0.1.1-candidate` |
| Run label and results | `baseline-4bd0ba9`, `results/baseline-4bd0ba9/` | `candidate-fae1824`, `results/candidate-fae1824/` |
| Run result | `FAIL` | `PASS` |

Inputs shared by both runs (recorded in each `run_manifest.json`):

* catalog `catalog/catalog.json`: `inspektorium-v0.1.1-display-and-input`
  version 1.0, frozen, 70 cases, SHA-256
  `966ea98a55ba54db8f7d1149955a0f6997f34598da68f7263bda053d5ec06fc0`;
* label maps `config/versions.json`, SHA-256
  `925d3df10ba85e73d3d32ed5904c5b66aeb797f8081cc5875611d1a26e59b818`;
* case inputs: `cases_manifest.json` lists the SHA-256 of every generated
  `input.json` and `proposals.json`; the file is identical in both runs (SHA-256
  `e085223b057d247fe3a8bdba51e72e25058727305c50adc3490015dffd2f768c`);
* tools: `harness.tool_sha256` in both manifests lists the same hashes as the
  files in `tools/`.

Environment of the recorded runs:

* Python 3.11.7 (Unicode database 14.0.0) on macOS 14.6.1 (arm64).
* Product runtime, identical in both product venvs (`requirements-product.txt`):
  pydantic 2.14.1, pydantic_core 2.50.1, annotated-types 0.8.0,
  typing-inspection 0.4.4, typing_extensions 4.16.0. No provider SDK is
  installed, so the two product venvs differ only in the Inspektorium wheel.
* Wheel build (`requirements-build.txt`): build 1.6.1, hatchling 1.32.4,
  `python -m build --wheel --no-isolation` on the extracted `git archive`.
* Harness (`requirements.txt`): cmarkgfm 2025.10.22 (cmark-gfm
  0.29.0.gfm.13), markdown-it-py 4.2.0 with mdurl 0.1.2, Markdown 3.11,
  playwright 1.63.0.
* Browser: Chromium 153.0.8010.12 (Playwright build, headless), page
  JavaScript disabled, service workers blocked, launch argument
  `--host-resolver-rules=MAP * ~NOTFOUND`.

## Files of the public evidence package

| Path | Content |
|---|---|
| `README.md` | this guide (method, criteria, results, reproduction, limits) |
| `catalog/catalog.json` | frozen catalog: cases, families, kinds, criteria, outcome classes, non-applicable findings |
| `config/versions.json` | per-version label maps that derive the expected rendered lines from a JSON report |
| `requirements.txt` | exact pins of the harness (renderers, Playwright) |
| `requirements-build.txt` | exact pins of the wheel build environment |
| `requirements-product.txt` | constraints for the product runtime (same for every version) |
| `tools/*.py`, `tools/dom_probe.js` | the harness (13 Python files and one JavaScript file; see below) |
| `results/setup/setup_log.jsonl` | the setup steps of the recorded runs, including every download (kept apart from the offline runs) |
| `results/baseline-4bd0ba9/` | binding baseline run (file list below) |
| `results/candidate-fae1824/` | binding candidate run (file list below) and `compare_to_baseline.json` |

Each results directory contains `run_manifest.json` (versions, hashes,
environment, command), `cases_manifest.json` (input hashes),
`cli_results.jsonl` (one row per CLI invocation), `outputs.jsonl` (the report
files written by the CLI, read as strict UTF-8 without newline translation, so
`text` hashes to `sha256`), `measurements.jsonl` (one row per case and
renderer), `browser_network.jsonl` (every request seen by the browser route
handler), `netguard.jsonl` (all guard records of the run), `case_verdicts.jsonl`,
`summary.json`, `selftest.json`, and `canary/canary.json` with
`canary/canary_netguard.jsonl`. The candidate directory additionally contains
`compare_to_baseline.json`.

`DOCUMENTATION_DECISIONS.md` in this directory belongs to the documentation
work package; it is not a measurement file. Non-binding development runs made
while the fixes were written are not part of this package.

### Tools

| Tool | Role |
|---|---|
| `setup_env.py` | the only step that downloads: venvs, wheel build from `git archive <commit>`, Playwright Chromium, guard installation; `publish-log` copies setup-log entries with local paths replaced |
| `netguard.py` | self-written Python network guard, installed into every venv through a `.pth` file |
| `build_cases.py` | turns catalog cases into `input.json` / `proposals.json` with SHA-256 digests |
| `run_cli.py` | runs the real installed `inspektorium` console script per case and format |
| `renderers.py` | the four Markdown-to-HTML configurations |
| `browser_check.py`, `dom_probe.js` | loads each page in Chromium and extracts DOM and visibility facts |
| `evaluate.py` | criteria, outcome classes and case verdicts (pure functions) |
| `aggregate.py` | recomputes verdicts and the run summary from the recorded rows |
| `run_evidence.py` | one complete offline run for one installed version |
| `canary.py` | controlled check that the network guards refuse (no request is sent) |
| `selftest.py` | sabotage tests of the measurement chain and a sanity check of the label map's criteria parameters |
| `compare_versions.py` | before/after comparison of two runs, including JSON byte identity |

## Method

1. **Versions.** Each version is built from `git archive <full commit id>` into
   a wheel outside the source tree and installed into its own new venv with the
   same pinned runtime (`requirements-product.txt`). Before measuring, the
   harness imports the package from that venv and records `__file__`,
   `__version__` and the distribution version; a package imported from the
   source tree aborts the run.
2. **Cases.** `build_cases.py` composes answer and source texts from each
   fixture and computes offsets on the product's documented canonical text (LF
   newlines, NFC). Input cases use the exact raw JSON text stored in the
   catalog. Every file is hashed; `run_cli.py` re-checks the hashes.
3. **CLI.** For every case and each format (`json`, `markdown`) the harness
   writes a known placeholder into the output file and runs
   `inspektorium inspect --input input.json --proposals proposals.json --format <fmt> --output <file>`
   as a subprocess with a credential-free environment. Exit code, standard
   output, standard error, the output file state and the guard records of that
   process are stored per row.
4. **Rendering matrix.** Every accepted Markdown report is rendered by four
   configurations (`tools/renderers.py`):
   * `cmark-gfm-unsafe`: GitHub's C implementation cmark-gfm 0.29.0.gfm.13
     (Python package `cmarkgfm` 2025.10.22) with the GitHub extensions table,
     autolink, tagfilter, strikethrough and tasklist and `CMARK_OPT_UNSAFE`, so
     raw HTML passes through (an HTML-processing GFM-compatible configuration);
   * `cmark-gfm-safe`: the same library and extensions in its default safe
     mode;
   * `markdown-it-py-html`: markdown-it-py 4.2.0, CommonMark preset,
     `html=True`, plus table and strikethrough;
   * `python-markdown`: Python-Markdown 3.11 with `tables` and `fenced_code`
     (an independent, non-CommonMark implementation). It counts fully toward
     the result.

   "GFM-compatible" means the GFM library rendering above. The GitHub web
   service, including its HTML sanitizer, was not tested.
5. **Browser.** Each page is loaded from a local file in Chromium with page
   JavaScript disabled. `dom_probe.js` collects the rendered line units
   (headings, list items, top-level paragraphs, block quotes, any other block
   element), their computed visibility (`checkVisibility` with opacity and
   visibility checks, `hidden` attribute, display, visibility, opacity, non-zero
   box, font size, transparent colour, closed `details`), comment nodes,
   element tags and attributes, raw control code points, and the position and
   visibility of the payload sentinels.
6. **Criteria and classes.** `evaluate.py` compares those facts with the lines
   that the version's label map derives from the JSON report of the same case.
   Each (case, renderer) measurement gets exactly one outcome class; each case
   gets one verdict.
7. **Aggregation.** `aggregate.py` does not trust stored derived fields. It
   recomputes the CLI class of every CLI row from its raw fields (exit code,
   standard output and error, output file SHA-256 and size against the known
   placeholder) with the classifier used at measurement time; it derives the
   outcome of every rendered row from that row's criteria (intact if and only
   if every applicable criterion passed, with the applicable set taken from
   the catalog rule) and the case-level flag from the stored K13/K14 results; and
   it counts the guard's `armed` records per distinct CLI process id in
   `netguard.jsonl` and the refusals in that log. Any disagreement between a
   stored class and the recorded facts makes the row or case `NOT_EXECUTED`
   and the run `INCOMPLETE`, never `PASS`. Aggregation does not re-run the
   renderers or the browser: a stored criterion result or browser-network row
   that was altered consistently is not detected by aggregation alone. The
   check for that is an independent re-run of the measurement (see
   Reproduction), whose rows can be compared with the published ones.

### Outcome classes (per case and renderer)

| Class | Meaning |
|---|---|
| `REJECTED_BEFORE_RENDER` | the CLI rejected the input for both formats: exit 2, `inspektorium: error:` on standard error without a traceback, nothing on standard output, the pre-existing output file byte-identical |
| `RENDERED_CONTROLS_INTACT` | rendered and every applicable criterion held |
| `RENDERED_MANIPULATED` | rendered and at least one criterion failed |
| `NOT_EXECUTED` | not measurable: CLI outcome irregular, unmet precondition, browser error, missing row, a stored row that disagrees with its recorded facts, or label map not validated for that renderer |

### Case verdicts

| Verdict | Meaning |
|---|---|
| `HOLDS` | the expected protection was observed (all four renderings intact, or a clean rejection where rejection is expected) |
| `FAILS` | the expected protection was not observed (for example a manipulated rendering, an accepted ambiguous input, a rejected valid input, a crash or a damaged output file) |
| `NOT_DEMONSTRATED` | a rendering case was rejected before rendering; this never counts as a passed rendering test |
| `NOT_EXECUTED` | at least one required measurement is missing, failed or inconsistent with its recorded facts |

The run result is `PASS` only if every case `HOLDS`, every CLI and harness
process had an armed guard (at least as many CLI processes with an `armed`
record in `netguard.jsonl` as CLI rows), the guard refused nothing, the rendered
pages made no blocked network request, no row or log is missing and no stored
class disagrees with the recorded facts. Any `FAILS`, guard refusal or page
network attempt makes it `FAIL`; anything else missing or inconsistent makes it
`INCOMPLETE`. Nothing is summed by hand.

### Criteria

The binding definitions are in `catalog/catalog.json` (`criteria`,
`cli_criteria`, `criteria_application`). In short:

| Id | Check |
|---|---|
| K1 | section headings exactly as the label map says, in order, visible |
| K2 | exactly one visible finding heading per JSON finding, in order; no other h3-h6 |
| K3 | per finding exactly one visible guard line whose value equals the JSON `deterministic_validation_status`; the number of lines starting with any host control label equals what the JSON implies |
| K4 | one visible line per JSON validation issue, the scope statement and one visible line per JSON limitation, with exact text |
| K5 | the full ordered sequence of rendered line units equals the sequence derived from the JSON report |
| K6 | every payload sentinel occurs once, visibly, inside its intended field |
| K7 | no element outside the allowed tag set, no attributes, no comment nodes; inside a payload only the field's allowed inline tags |
| K8 | every unit visible and no text outside a unit |
| K9 | no raw code point of category Cc (except TAB, LF, CR), Cf, Zl, Zp or Cs in the rendered text |
| K10 | fields are displayed exactly as the version's display rule derives from the raw JSON value (whitespace-normalized) |
| K11 | collision case: literal marker text and the real control character are displayed differently |
| K12 | the page made no request other than loading itself |
| K13 | reachability: unreachable text appears in neither report |
| K14 | equivalent inputs produce byte-identical JSON reports |
| R1-R4 | clean rejection (exit 2, error prefix, empty stdout, output file unchanged) |

K9 applies to both versions without exceptions; measuring the baseline against
it is how raw bidirectional controls (C5) are reproduced.

### Label maps

Labels differ between versions, so each version has a label map in
`config/versions.json`. A map is used for a renderer only if the label-map
validation case `R-RC-00` is `RENDERED_CONTROLS_INTACT` with that map;
otherwise every rendered row of that renderer becomes `NOT_EXECUTED`
(self-test S13). `R-RC-00` is plain ASCII with five findings: guard passed with
an exact citation, a failed citation, guard passed without a citation check, a
claim-span failure, and an incomplete evidence reference.

`R-RC-00` validates the labels and the report skeleton only for the branches
these five findings exercise (see "Label-map branches" under Limits). It does
not validate the criteria parameters of a map: the display rule,
`guard_label`, `control_labels`, `allowed_tags` and `payload_allowed_tags`.
These are fixed review inputs, identified by the `versions_json_sha256`
recorded in each run manifest. `selftest.py` adds a small sanity check of them
(M0-M3): no link, image, script, style, frame, form or generic container tag
in the allowed tag sets; the guard label is a control label and starts the
status line; every control label starts a template line; a `tokenize` display
rule marks at least Cc, Cf, Cs, Zl and Zp and lists only valid Unicode
categories. Three deliberately weakened copies of the map must be flagged. The
check does not detect every weakening; for example, a shortened control-label
list whose remaining labels exist passes it.

* `inspektorium-0.1.0` is the fixed map of the baseline (display rule:
  identity).
* `inspektorium-0.1.1-candidate` is final for commit
  `fae18242de35facb7c493ff18e86baff3afe2c24`. Its labels, the display note and
  its display rule follow `src/inspektorium/report/markdown_report.py` and
  `src/inspektorium/report/display.py` at that commit: characters of the
  categories Cc, Cf, Cs, Zl and Zp (including U+200C and U+200D), code points
  that are unassigned (category Cn) in the Unicode database of the running
  Python (including noncharacters such as U+FFFE), and the marker brackets
  U+27E6/U+27E7 are displayed as `⟦U+XXXX⟧` markers, except LF inside a
  quotation, which is a line break; Markdown escapes (backslash escapes and
  character references) and the two-space hard line break of quotations are
  invisible after rendering.

Unicode categories are looked up in the Unicode database of the running
Python, so which characters the candidate marks follows that database (in the
recorded runs Python 3.11.7, Unicode 14.0.0). A code point assigned in a later
Unicode version is category `Cn` (unassigned) there, and the candidate shows it
as a marker. The harness derives the expected display (K10) with its own
`unicodedata`, records both databases as `unidata_version` in the run manifest
(`product.import_check` and `harness`), and refuses to run a `tokenize` map when
they differ. K9 uses the browser's own Unicode tables. No string in the catalog
contains a code point that is unassigned in Unicode 14.0.0, so the `Cn` part of
the rule is not exercised by these runs.

Both maps validated on all four renderers in their binding runs
(`label_map_valid` in each `summary.json`).

### Catalog

70 cases, frozen as catalog version 1.0 before the baseline/candidate
comparison. Attack defence, accidental damage and readability are separate
kinds:

| Kind | Cases | Purpose |
|---|---:|---|
| `attack` | 42 | a payload must not forge, hide or restructure report content |
| `clean_counterpart` | 7 | legitimate text close to an attack shape must render intact and exactly |
| `readability` | 3 | ordinary German, Greek and emoji text must stay readable |
| `reachability` | 3 | whether a free-text field reaches a report at all |
| `input_rejection` | 12 | ambiguous or invalid input must be rejected early |
| `input_acceptance` | 3 | valid input must be accepted with unchanged results |

Families: line injection via LF, CR, CRLF, U+2028, U+2029, NEL and a
TAB-indented continuation in `rationale`, `claim_text` and `evidence_quote`
(19); HTML hiding (`<!--`, `<div hidden>`, `<style>`, `<details>`, closing
tags, `<span hidden>`; 8); Markdown breakout (heading, fence, table, list,
inline markup; 6); links, autolinks, images and entity references including
`&#x202E;` (2); bidi, zero-width, BOM and C0/C1 controls (5); a collision of
the literal text `⟦U+202E⟧` with a real U+202E (1); a report with real failures
followed by clean findings, with and without the C1 payload (2); clean and
readability texts (9); host-message reachability (3); duplicate keys at top
level, in `answer`, in `sources[i]`, escaped-equivalent keys and in a proposal
(7); NaN/Infinity (3); lone surrogates (2); clean inputs (3).

Every attack case names its precondition (for example "the claim span stays
valid so the finding passes the guard", or "the guard fails") and the harness
checks it against the JSON report before measuring; an unmet precondition makes
the case `NOT_EXECUTED`. Most attack fixtures also contain a real failing
finding and a clean finding after the payload, so warnings, later findings and
limitations must stay visible in every attack case.

**Non-applicable finding (NA-01).** In the public code at `4bd0ba9` no
host-composed report line embeds free text: validation messages are fixed
strings, `claim_id` and `source_id` must match the identifier pattern, and the
source title is not rendered. No case was invented for this path; `X-RE-01..03`
measure the reachability claims instead. CLI error messages on standard error
are outside this catalog (NA-02); they never reach a report file.

## Results

All numbers are results on this synthetic catalog only. The four renderings
of one case are not independent observations, so cases and renderings are
counted separately. Sources: `results/*/summary.json`,
`results/*/case_verdicts.jsonl` and
`results/candidate-fae1824/compare_to_baseline.json`.

### Run results

| | Baseline `4bd0ba9` | Candidate `fae1824` |
|---|---|---|
| Run result | `FAIL` | `PASS` |
| Reasons | 48 cases `FAILS`; rendered pages attempted network requests (4 blocked) | none |
| Cases `HOLDS` / `FAILS` / `NOT_DEMONSTRATED` / `NOT_EXECUTED` | 22 / 48 / 0 / 0 (of 70) | 70 / 0 / 0 / 0 (of 70) |
| Label map valid (4 renderers) | 4 of 4 | 4 of 4 |
| Self-test scenarios as expected | 17 of 17 | 17 of 17 |
| Label-map sanity checks (M0-M3) as expected | 4 of 4 | 4 of 4 |

### Cases by family (`HOLDS` / cases)

| Family | Cases | Baseline HOLDS | Baseline FAILS | Candidate HOLDS | Candidate FAILS |
|---|---:|---:|---:|---:|---:|
| render.line_injection | 19 | 0 | 19 | 19 | 0 |
| render.html_hiding | 8 | 1 | 7 | 8 | 0 |
| render.markdown_breakout | 6 | 0 | 6 | 6 | 0 |
| render.link_entity | 2 | 0 | 2 | 2 | 0 |
| render.bidi_invisible | 5 | 0 | 5 | 5 | 0 |
| render.collision | 1 | 0 | 1 | 1 | 0 |
| render.mixed_report_visibility | 2 | 1 | 1 | 2 | 0 |
| render.readability_clean | 9 | 8 | 1 | 9 | 0 |
| render.indirect_host_message | 3 | 3 | 0 | 3 | 0 |
| input.duplicate_keys | 7 | 1 | 6 | 7 | 0 |
| input.nonstandard_constant | 3 | 3 | 0 | 3 | 0 |
| input.lone_surrogate | 2 | 2 | 0 | 2 | 0 |
| input.clean_acceptance | 3 | 3 | 0 | 3 | 0 |
| **Total** | **70** | **22** | **48** | **70** | **0** |

### Cases by kind (`HOLDS` / cases)

| Kind | Cases | Baseline HOLDS | Baseline FAILS | Candidate HOLDS | Candidate FAILS |
|---|---:|---:|---:|---:|---:|
| attack | 42 | 1 | 41 | 42 | 0 |
| clean_counterpart | 7 | 6 | 1 | 7 | 0 |
| readability | 3 | 3 | 0 | 3 | 0 |
| reachability | 3 | 3 | 0 | 3 | 0 |
| input_rejection | 12 | 6 | 6 | 12 | 0 |
| input_acceptance | 3 | 3 | 0 | 3 | 0 |

No case was `NOT_DEMONSTRATED` or `NOT_EXECUTED` in either run.

### Renderings by renderer (280 = 70 cases x 4 renderers per run)

| Renderer | Version | REJECTED_BEFORE_RENDER | RENDERED_CONTROLS_INTACT | RENDERED_MANIPULATED | NOT_EXECUTED |
|---|---|---:|---:|---:|---:|
| cmark-gfm-unsafe | baseline | 8 | 20 | 42 | 0 |
| cmark-gfm-safe | baseline | 8 | 20 | 42 | 0 |
| markdown-it-py-html | baseline | 8 | 20 | 42 | 0 |
| python-markdown | baseline | 8 | 23 | 39 | 0 |
| **all four** | **baseline** | **32** | **83** | **165** | **0** |
| cmark-gfm-unsafe | candidate | 14 | 56 | 0 | 0 |
| cmark-gfm-safe | candidate | 14 | 56 | 0 | 0 |
| markdown-it-py-html | candidate | 14 | 56 | 0 | 0 |
| python-markdown | candidate | 14 | 56 | 0 | 0 |
| **all four** | **candidate** | **56** | **224** | **0** | **0** |

By kind on the candidate: attack 168 intact; clean counterpart 28 intact;
readability 12 intact; input acceptance 12 intact; reachability 4 intact and
8 rejected; input rejection 48 rejected. On the baseline: attack 7 intact and
161 manipulated; clean counterpart 24 intact and 4 manipulated; readability 12
intact; input acceptance 12 intact; reachability 4 intact and 8 rejected; input
rejection 24 rejected and 24 rendered intact (the six accepted duplicate-key
inputs, which is the failure for those cases).

### Before and after

* Verdict transitions (70 cases): `FAILS -> HOLDS` 48, `HOLDS -> HOLDS` 22, no
  `HOLDS -> FAILS`.
* JSON reports: byte-identical for 56 of 56 cases accepted by both versions;
  raw values, offsets and guard results are therefore unchanged. The 14 other
  cases are rejected by at least one version: `I-DK-01`..`I-DK-06` by the
  candidate only; `I-DK-07`, `I-NC-01`..`I-NC-03`, `I-LS-01`, `I-LS-02`,
  `X-RE-02` and `X-RE-03` by both.
* Markdown reports differ for 62 cases: the 56 cases accepted by both (display
  note, labels and escaping) and the 6 duplicate-key cases that only the
  baseline accepted.

### Input handling

* Candidate: all 12 `input_rejection` cases end `REJECTED_BEFORE_RENDER` for
  both formats (24 CLI invocations): exit code 2, `inspektorium: error:` on
  standard error, empty standard output and the pre-existing output file
  byte-identical. The duplicate-key cases `I-DK-01`..`I-DK-06` are reported as
  duplicate object keys. All 3 `input_acceptance` cases are accepted; `I-OK-02`
  (minified, reordered, escaped-equivalent) produces the same JSON bytes as
  `I-OK-01` (K14).
* Baseline: `I-DK-01`..`I-DK-06` were accepted with exit code 0; in the four
  cases with differing values (`I-DK-01`..`I-DK-04`) the report shows that the
  last value was used (C4). The other 6 rejection cases were already rejected.

### Reproduced on the baseline and fixed in the candidate

* **C1** (forged control lines and hiding): `R-MX-01` puts LF-separated
  "Deterministic guard: passed" lines and an unterminated `<!--` into a
  rationale. On the baseline all four renderers show forged control lines (K3,
  K5); in the three CommonMark-family configurations the warnings, later
  findings and the limitations section disappear (K1, K2, K4). In the
  line-injection family, forged status or control lines (K3, K5) appear in 10
  of 19 cases and 37 of 76 renderings: the LF, CR and CRLF cases in
  `rationale`, `claim_text` and `evidence_quote` and the LF+TAB continuation
  (`R-LI-01..03`, `R-LI-07..09`, `R-LI-13..15`, `R-LI-19`) on all four
  renderers, except Python-Markdown in the three `evidence_quote` cases
  (`R-LI-13..15`), where the payload stays inside the quotation and only its
  Markdown is rendered as formatting (K7). The 9 U+2028, U+2029 and NEL cases
  (`R-LI-04..06`, `R-LI-10..12`, `R-LI-16..18`) create no new report line in
  these four renderers; they count as manipulated only because the raw
  separator stays in the rendered text (K9) and the payload's Markdown is
  rendered as formatting (K7). All 76 line-injection renderings are
  `RENDERED_MANIPULATED` on the baseline, but only 37 of them show a forged
  line. On the candidate all 19 cases are intact on all four renderers.
* **C5** (raw bidi controls): on the baseline `R-BI-01` leaves raw U+202E and
  U+202C in the rendered text on all four renderers (K9), and all five
  bidi/invisible cases fail (20 of 20 renderings manipulated). On the candidate
  all five hold; the characters are shown as markers.
* **C4** (duplicate keys): see "Input handling".
* `R-LE-01` (links, autolinks, a remote image): on the baseline each renderer's
  page attempted one remote image request, which the browser blocked (4
  requests, K12). On the candidate no page made any request other than loading
  itself.
* The clean counterpart `R-RC-06` (backticks, asterisks, tildes, a tag and an
  entity meant as data) is interpreted as formatting or HTML by every renderer
  on the baseline (K7, K10) and displayed literally on the candidate.

Not reproduced on the baseline (documented, not counted as baseline failures):

* Line forging by U+2028, U+2029 and NEL (`R-LI-04..06`, `R-LI-10..12`,
  `R-LI-16..18`): none of the four renderers starts a new report line at these
  separators. These 9 cases fail on the baseline only through the raw
  separator (K9) and the payload Markdown rendered as formatting (K7), not
  through a forged line. The same holds for Python-Markdown with LF, CR and
  CRLF inside `evidence_quote` (`R-LI-13..15`; K7 only).
* `R-HH-02`: an unterminated `<!--` inside a single line stays visible text in
  all four renderers.
* `I-NC-01`, `I-NC-02`: NaN/Infinity in `--input` are already rejected (the
  JSON parser reads them as floats and the string fields reject them).
* `I-LS-01`, `I-LS-02`: lone surrogates are already rejected.
* `I-DK-07`, `I-NC-03`: the proposal parser already rejected duplicate keys and
  non-standard constants.
* `X-RE-01..03`: source titles are not rendered; payloads in `claim_id` and
  `source_id` are rejected by the identifier pattern.

### Network and provider measurement

Per run (`network` in `summary.json`, `netguard.jsonl`,
`browser_network.jsonl`):

| | Baseline | Candidate |
|---|---:|---:|
| CLI invocations (CLI rows) | 140 | 140 |
| CLI processes with an `armed` record in `netguard.jsonl` (distinct process ids) | 140 | 140 |
| CLI invocations without an armed guard (per CLI row) | 0 | 0 |
| Guard log records (CLI processes, harness, product import check) | 142 | 142 |
| Guard refusals (counted in `netguard.jsonl`) | 0 | 0 |
| Harness process guard armed | yes | yes |
| Browser requests seen by the route handler | 252 | 224 |
| of which own page loads | 248 | 224 |
| of which blocked requests | 4 (image, `R-LE-01`) | 0 |

Canary (`canary/canary.json`, run before each measurement): in the product
venv and in the harness venv the guard refused a DNS lookup of
`api.anthropic.com`, `socket.create_connection` and raw connects to
`1.1.1.1:443` and `[2606:4700:4700::1111]:443`, and a UDP send to `1.1.1.1:53`
(5 of 5 refused in each venv, with 5 refusal records each); the loopback
positive control connected. In the browser, a remote stylesheet and a remote
image were aborted by the route handler (2 aborted requests). This held for
the baseline venv, the candidate venv and the harness venv. A refused call
never reaches the original socket function, so the canary sends no packet.

Reach: the guard is a Python hook (`socket.getaddrinfo`, `gethostbyname*`,
`gethostbyaddr`, `getnameinfo`, `socket.connect`, `connect_ex`, `sendto`) in
the harness process and in every Python process started from a guarded venv,
including every CLI subprocess. It does not prove that native code outside
Python's `socket` module or other programs could not reach the network.
Browser requests are blocked by Playwright routing and by the host-resolver
rule; the Playwright driver and browser processes are not covered by the
Python hook. The measured zeros apply only to the monitored runs. Downloads
happened only in the separate setup step (`results/setup/setup_log.jsonl`):
Python packages from PyPI and the Playwright Chromium build from the official
Playwright download location.

### Self-test of the measurement chain

`selftest.json` in each results directory. The cases that hold in the run
(22 on the baseline, 70 on the candidate) aggregate to `PASS` unchanged (S0).
Each sabotage re-runs the real probe, evaluation and aggregation code on a
copy and turned the result as expected in both runs: a forged guard line (S1),
an injected `<!--` (S2), a hidden limitations section (S3), a raw U+202E (S4),
a deleted limitation (S5), a remote image (S6) and a guard refusal record (S9)
each gave `FAIL`; a missing measurement row (S7), a missing guard log (S8), a
missing CLI row (S10), an unknown outcome label (S11), a CLI row without an
armed guard (S12), a wrong label map (S13), a criterion set to failed while the
stored outcome stays intact (S14), one CLI process's `armed` record deleted
from the guard log (S15) and a CLI row with exit code 1 and a traceback whose
stored class stays `ACCEPTED` (S16) each gave `INCOMPLETE`. S14-S16 are the
three inconsistency cases found in the independent parser and measurement
review. 17 of 17 scenarios behaved as expected in each run, and the map sanity
check (M0-M3, see "Label maps") passed for the map of each run.

## Reproduction

Commands run from the repository root. `$WORK` is any directory outside the
repository; nothing is written into the source tree except the results
directories named below. Use a new `--work` directory for every run, because
the guard appends to the run's `netguard.jsonl`.

### 1. Setup (downloads; run once)

```sh
WORK=/path/outside/the/repository
PY=python3.11
T=evidence/v0.1.1/tools
LOG="$WORK/setup/setup_log.jsonl"
export PYTHONDONTWRITEBYTECODE=1
$PY -B $T/setup_env.py build-venv --venv "$WORK/venv-build" --setup-log "$LOG"
$PY -B $T/setup_env.py tools-venv --venv "$WORK/venv-tools" --setup-log "$LOG"
$PY -B $T/setup_env.py browser --venv "$WORK/venv-tools" --browsers-path "$WORK/ms-playwright" --setup-log "$LOG"
$PY -B $T/setup_env.py build-wheel --commit 4bd0ba9218df80a69089838f824ae0ac28881ac4 --repo . \
    --out "$WORK/build-baseline" --build-python "$WORK/venv-build/bin/python" --setup-log "$LOG"
$PY -B $T/setup_env.py product-venv --venv "$WORK/venv-baseline" \
    --wheel "$WORK/build-baseline/wheels/inspektorium-0.1.0-py3-none-any.whl" --setup-log "$LOG"
$PY -B $T/setup_env.py build-wheel --commit fae18242de35facb7c493ff18e86baff3afe2c24 --repo . \
    --out "$WORK/build-candidate-fae1824" --build-python "$WORK/venv-build/bin/python" --setup-log "$LOG"
$PY -B $T/setup_env.py product-venv --venv "$WORK/venv-candidate-fae1824" \
    --wheel "$WORK/build-candidate-fae1824/wheels/inspektorium-0.1.1-py3-none-any.whl" --setup-log "$LOG"
```

`product-venv` and `tools-venv` install the guard after the packages, so later
Python processes in those venvs are guarded. The published setup log was
written with
`$PY -B $T/setup_env.py publish-log --setup-log "$LOG" --work "$WORK" --entries 0-9,20-23 --out evidence/v0.1.1/results/setup/setup_log.jsonl`;
each published entry keeps its `log_index` in the full log. The omitted
indices 10-19 belong to non-binding development builds and to the build of the
superseded candidate `7c9d438`.

### 2. Offline measurement

```sh
export PLAYWRIGHT_BROWSERS_PATH="$WORK/ms-playwright" PYTHONDONTWRITEBYTECODE=1
TP="$WORK/venv-tools/bin/python"

# Baseline
B=evidence/v0.1.1/results/baseline-4bd0ba9
mkdir -p "$WORK/canary-baseline" "$WORK/run-baseline"
env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY EVIDENCE_NETGUARD_LOG="$WORK/canary-baseline/harness_netguard.jsonl" \
  "$TP" -B $T/canary.py --venv "$WORK/venv-baseline" --venv "$WORK/venv-tools" \
  --work "$WORK/canary-baseline" --results "$B/canary"
env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY EVIDENCE_NETGUARD_LOG="$WORK/run-baseline/netguard.jsonl" \
  "$TP" -B $T/run_evidence.py --label baseline-4bd0ba9 --product-venv "$WORK/venv-baseline" \
  --build-provenance "$WORK/build-baseline/build_provenance.json" --version-map inspektorium-0.1.0 \
  --work "$WORK/run-baseline" --results "$B" --binding yes \
  --note "binding baseline: public main 4bd0ba9218df80a69089838f824ae0ac28881ac4"
env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY EVIDENCE_NETGUARD_LOG="$WORK/selftest-baseline.jsonl" \
  "$TP" -B $T/selftest.py --run-work "$WORK/run-baseline" --results "$B" \
  --work "$WORK/selftest-baseline" --version-map inspektorium-0.1.0 --out "$B/selftest.json"

# Candidate
C=evidence/v0.1.1/results/candidate-fae1824
mkdir -p "$WORK/canary-candidate" "$WORK/run-candidate"
env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY EVIDENCE_NETGUARD_LOG="$WORK/canary-candidate/harness_netguard.jsonl" \
  "$TP" -B $T/canary.py --venv "$WORK/venv-candidate-fae1824" --venv "$WORK/venv-tools" \
  --work "$WORK/canary-candidate" --results "$C/canary"
env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY EVIDENCE_NETGUARD_LOG="$WORK/run-candidate/netguard.jsonl" \
  "$TP" -B $T/run_evidence.py --label candidate-fae1824 --product-venv "$WORK/venv-candidate-fae1824" \
  --build-provenance "$WORK/build-candidate-fae1824/build_provenance.json" --version-map inspektorium-0.1.1-candidate \
  --work "$WORK/run-candidate" --results "$C" --binding yes \
  --note "binding candidate: commit fae18242de35facb7c493ff18e86baff3afe2c24"
env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY EVIDENCE_NETGUARD_LOG="$WORK/compare.jsonl" \
  "$TP" -B $T/compare_versions.py --before "$B" --after "$C" \
  --catalog evidence/v0.1.1/catalog/catalog.json --out "$C/compare_to_baseline.json"
env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY EVIDENCE_NETGUARD_LOG="$WORK/selftest-candidate.jsonl" \
  "$TP" -B $T/selftest.py --run-work "$WORK/run-candidate" --results "$C" \
  --work "$WORK/selftest-candidate" --version-map inspektorium-0.1.1-candidate --out "$C/selftest.json"
```

The harness also removes every environment variable whose name contains
`API_KEY`, `ANTHROPIC`, `OPENAI`, `TOKEN` or `SECRET` before it starts a CLI
process. Report outputs, verdicts and measurements are deterministic for a
given environment; timestamps, process ids and the recorded command differ
between runs.

`setup_env.py` replaces an existing directory given as `--venv`; always pass a
new, dedicated path.

### 3. Independent re-run without touching the published results

The commands above write the binding results into `evidence/v0.1.1/results/`.
To check them instead, run the same steps with `--binding no` and with every
`--results`/`--out` path pointing to a directory under `$WORK` (for example
`$WORK/results/candidate-fae1824`), then compare with the published files. In
an independent re-run on another checkout, `case_verdicts.jsonl`,
`measurements.jsonl`, `outputs.jsonl`, `browser_network.jsonl`,
`cases_manifest.json`, `selftest.json` and `compare_to_baseline.json` were
byte-identical to the published files. The expected differences are limited to
run-specific fields: `binding` in `summary.json`; `binding`, `note`, the
recorded command, `started`, `finished` and the harness process id in
`run_manifest.json`; `duration_s` in `cli_results.jsonl`; and process ids and
times in the guard and canary logs.

### Wheel hashes of later commits

The wheel hashes above belong to the measured product commits. A wheel built
from a later commit that changes only documentation, such as the commit that
adds this package, has a different hash, because the wheel metadata embeds
`README.md` as the long description. Its module files are byte-identical. To
check that a later commit carries the measured product, compare
`git diff fae18242de35facb7c493ff18e86baff3afe2c24 <commit> -- src tests examples pyproject.toml`
(expected empty) or the installed module bytes, not the wheel hash.

## Limits

* **Synthetic catalog only.** The results are not a detection rate, not a
  false-alarm rate and not a guarantee for other inputs, renderers, viewers or
  browsers, and they say nothing about the scientific correctness of any
  evaluation.
* **Not a holdout set.** The catalog was written with knowledge of the
  reproduced defects, and the candidate's display code was developed while this
  catalog was available. The candidate result shows that the fixes cover these
  cases, not that they generalize.
* **GFM-compatible is not GitHub.** The Markdown matrix is four local library
  configurations. GitHub's web rendering and sanitizer, other Markdown viewers
  and other browsers were not tested.
* **E-mail autolinks.** Separate checks outside this package (cmarkgfm
  2025.10.22, safe and unsafe mode, on the candidate's encoding of an address)
  observed that cmark-gfm's autolink extension still turns e-mail addresses in
  report text into links whose text is the address. This includes the
  `mailto:` and `xmpp:` forms (for example `mailto:x@y.example` and
  `xmpp:u@h.example`), seen in the independent display review; in the same
  review markdown-it-py and Python-Markdown created no such link. The
  candidate documents this limit in `src/inspektorium/report/display.py`. The
  catalog contains no e-mail case, so this package does not measure it.
* **Combining marks.** Long runs of combining marks on one base character in
  report text can paint over neighbouring report lines in a browser, for
  example over the warnings or limitations. The content stays in the DOM and
  passes the visibility checks. K8 and `dom_probe.js` judge the DOM and
  computed styles, not where glyphs are drawn, so this effect is not measured.
  It was observed in the independent display review outside this catalog, on
  the baseline as well as on the candidate.
* **Python-Markdown** was tested only with the `tables` and `fenced_code`
  extensions. Configurations such as `extra` or `attr_list` were not tested.
* **Display scope.** K9 covers the categories Cc, Cf, Cs, Zl and Zp; other
  invisible characters (for example variation selectors) are outside the
  criterion and are not marked by the candidate. The candidate also marks code
  points that are unassigned (Cn) in the running Python's Unicode database;
  K10 follows this rule through the label map, but no catalog case contains
  such a code point. Category membership follows the Unicode database of the
  running Python (Unicode 14.0.0 with Python 3.11.7 in the recorded runs);
  results with another Python version can differ for characters assigned in
  later Unicode versions; the candidate shows such characters as markers when
  the database of its Python does not contain them.
* **Label-map branches.** The catalog's reports exercise the label branches
  listed for `R-RC-00`. A finding whose guard failed without a citation check
  (`deterministic_validation_status` `failed` with `evidence_span_verified`
  `null`), the "Generated from explicit metadata" line and an empty findings
  section do not occur in any catalog report. For the first shape both maps
  would expect the guard line `failed`, while both versions print `failed
  (claim span and structure only; no citation check performed)`; it would be
  measured as a manipulated rendering, not as a pass.
* **Browser.** Page JavaScript was disabled; active content is detected
  structurally, never executed. Visibility is judged from the DOM and computed
  styles of one desktop viewport; there is no pixel-level or screen-reader
  check.
* **Network measurement reach.** The Python hook covers Python processes,
  including the CLI subprocesses; the browser is covered by routing and the
  resolver rule; native code outside these paths is not covered. The measured
  zeros apply only to the monitored runs. Setup downloads are listed separately
  in `results/setup/setup_log.jsonl`.
