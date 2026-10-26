# Research results and evidence limits

> **Current scope — 2026-10-26:** Inspektorium core remains 0.1.1/schema 0.1.
> Agent Arena P1–P10 is now included as a separate [public research package](agent-arena/README.md).
> [Publication mapping and current checks](publication/2026-10-26/README.md)
> supersede earlier access/publication statements below. Historical numbers,
> original dates and limits remain unchanged; publication is not independent
> replication. The scientific Final v1 gate is not met. No new live calls.

INSPEKTORIUM separates public reproducibility observations from owner-reported
internal studies. These evidence classes cannot substitute for one another.
Claims are indexed in [CLAIMS.md](CLAIMS.md). Documentation review: 2026-09-15;
v0.1.1 candidate update: 2026-10-13. Package 0.1.1; report schema 0.1.
Historical sections keep their original values; new evidence is added in
separate, dated sections.

## Public v0.1 observations

**Access: public code, tests and synthetic saved-input examples.** Claims P01–P11
apply to reviewed commit `16f572168025c393e953e34ccad184ca577e2bd0`.
The supplied reviewer report says all 59 files were inspected and their fetched
Git blob hashes verified. All five offline examples reproduced their ten
expected JSON/Markdown outputs byte-for-byte on Python 3.12.14 with Pydantic
2.13.5. The reviewer did not locally run the full pytest suite or any live
provider call. These are supplied reviewer observations, not new measurements
made by this documentation task.

[Historical GitHub CI](https://github.com/LAKITALKS/Inspektorium/actions/runs/31686541040)
for that exact commit succeeded on Python 3.11 and 3.12, including lint, type
checks and tests. The [historical release checklist](RELEASE_CHECKLIST.md)
records 74 tests, 88.11% overall branch-enabled coverage and 89.10%
deterministic-core branch-enabled coverage from its 2026-08-11 audit. Those
values are dated software-quality measurements, not new scientific results.
Local checks for the 2026-09-15 documentation change are recorded in the
documentation-review section of that checklist; checks for v0.1.1 are in its
v0.1.1 section and in the evidence package below.

### Counterexamples and reporting boundary

- **False semantic relation (P09):** in
  [example 02](examples/02_contradicted/proposals.json), the supplied reviewer
  changed `contradicted` to `supported` while retaining the true source quote
  and offsets. The intentionally false relation remained mechanically
  reportable. The exact guard does not understand whether a passage supports
  a claim. This probe is not a new fixture shipped in the repository.
- **Finding-level containment (P03, P11):**
  [example 05](examples/05_mixed_and_fabricated_quote/expected_report.json)
  preserves a valid finding while setting the fabricated-quote finding's
  `reportable_relation` to null. The proposal remains visible, the report is
  emitted successfully, and the CLI exits 0. Exit 0 is not assurance approval
  or authorization to release an artifact.
- **Absence and coverage (P04, P10):** `not_established` can remain reportable
  with all citation fields null; this does not prove absence of evidence. A
  supplied optional citation must validate. Empty findings are allowed, so
  zero guard failures does not establish that all relevant claims were found.
- **Current content, not authentication (P05):** changing source text outside
  the cited span changes its input hash without invoking a historical-state
  authentication check. The unchanged span can still pass. Hashes are not
  signatures or evidence of source authority.
- **Deterministic representation (P06):** JSON includes `generated_at: null`
  by default; Markdown omits the date line. Equal bundle hashes are intended
  for identical canonical IDs/texts irrespective of source order, not for
  arbitrary semantically equivalent paraphrases.

The five examples use synthetic precomputed proposals. They demonstrate saved
input behavior and exact fault handling, not live-model classification
accuracy, full claim coverage or broad reliability. Robustness evidence is
limited to the specific malformed fields, offsets, quotes and normalization
disturbances covered by existing regressions.

## Public v0.1.1 evidence package

**Access: public, offline and synthetic.** The [evidence package](evidence/v0.1.1/)
runs one versioned synthetic catalog against public `main`
`4bd0ba9218df80a69089838f824ae0ac28881ac4` (not tag `v0.1.0`) and against the
v0.1.1 candidate. It runs without a provider key; network and provider
monitoring of the measured runs is reported below. The catalog
`inspektorium-v0.1.1-display-and-input`, version 1.0, has 70 cases and was
frozen before the comparison. It separates attack defence, clean counterparts
(accidental damage), readability, reachability, input rejection and input
acceptance. Its families cover attempted line injection through LF, CR,
CRLF, U+2028, U+2029, NEL and a TAB-indented continuation; hiding through HTML
comments, elements and styles; heading, fence, table, list and inline-markup
breakouts; links, autolinks, images and entity references; bidirectional,
zero-width, BOM and C0/C1 control characters; a collision between literal
marker text and a real control character; reports with real failures followed
by clean findings; clean multilingual and punctuation-heavy text; untrusted
text in host-composed lines; duplicate keys (also escape-equivalent keys and
keys in a proposal); `NaN`/`Infinity`; unpaired surrogates; and clean inputs
that must stay accepted. The catalog has no e-mail address case. Other input
rejections (byte order mark, trailing data, deep nesting) are covered by the
test suite, not by the catalog.

Each case and renderer configuration gets one outcome class:
`REJECTED_BEFORE_RENDER`, `RENDERED_CONTROLS_INTACT`, `RENDERED_MANIPULATED` or
`NOT_EXECUTED`. Each case gets one verdict: `HOLDS`, `FAILS`,
`NOT_DEMONSTRATED` (a rendering case that was rejected before rendering) or
`NOT_EXECUTED`. A rejected input is not a passed rendering test, and a missing
or skipped measurement is never counted as a pass. Cases and renderings are
counted separately, always with their denominators. The results of each run
also include a self-test that sabotages copies of the recorded results and
re-runs the measurement chain on them; each sabotage must turn the result into
a failure or an incomplete run.

- Markdown implementations, browser, Python and Unicode database versions:
  cmark-gfm 0.29.0.gfm.13 through the Python package `cmarkgfm` 2025.10.22,
  with the GitHub Flavored Markdown extensions table, autolink, tagfilter,
  strikethrough and tasklist, once with raw HTML allowed (`CMARK_OPT_UNSAFE`)
  and once in its default safe mode; markdown-it-py 4.2.0 (CommonMark preset,
  `html=True`, table and strikethrough); Python-Markdown 3.11 (`tables` and
  `fenced_code`); Chromium 153.0.8010.12 (Playwright 1.63.0 build, headless,
  page JavaScript disabled) for DOM and visibility checks; Python 3.11.7 with
  Unicode database 14.0.0 for the product and the harness in both binding
  runs.
- Before (`4bd0ba9`): run result `FAIL`. 22 of 70 cases hold and 48 fail;
  none is `NOT_DEMONSTRATED` or `NOT_EXECUTED`. By kind, attack 1 of 42, clean
  counterparts 6 of 7, readability 3 of 3, reachability 3 of 3, input
  rejection 6 of 12 and input acceptance 3 of 3 hold. Of the 280 renderings
  (70 cases × 4 configurations), 165 are `RENDERED_MANIPULATED`, 83
  `RENDERED_CONTROLS_INTACT`, 32 `REJECTED_BEFORE_RENDER` and 0
  `NOT_EXECUTED`. In the line-injection family, forged status or control lines
  appeared in 10 of 19 cases (37 of 76 renderings); the 9 U+2028, U+2029 and
  NEL cases created no new report line on the baseline and count as
  manipulated only because the raw separator stayed in the rendered text and
  the payload's Markdown was rendered as formatting. The six duplicate-key
  `--input` cases were accepted with exit code 0, and the failing clean
  counterpart was interpreted as formatting or HTML by every renderer. In one
  link case, each renderer's page attempted a remote image request, which the
  browser blocked (4 requests); such an attempt also makes the run `FAIL`.
- After (v0.1.1 candidate, commit `fae18242de35facb7c493ff18e86baff3afe2c24`):
  run result `PASS`. 70 of 70 cases hold; none fails and none is
  `NOT_DEMONSTRATED` or `NOT_EXECUTED`. By kind, attack 42 of 42, clean
  counterparts 7 of 7, readability 3 of 3, reachability 3 of 3, input
  rejection 12 of 12 and input acceptance 3 of 3 hold. Of the 280 renderings,
  224 are `RENDERED_CONTROLS_INTACT`, 56 `REJECTED_BEFORE_RENDER` (the 12
  input-rejection cases and the 2 reachability cases with a rejected
  identifier, 4 renderings each) and 0 `RENDERED_MANIPULATED` or
  `NOT_EXECUTED`; each of the four configurations has 56 intact and 14
  rejected renderings. The 19 line-injection cases give 76 of 76 intact
  renderings, the clean counterparts and readability cases 40 of 40, and no
  rendered page made a request other than loading itself. No catalog string
  contains a code point that is unassigned in Unicode 14.0.0, so the catalog
  does not exercise the marking of unassigned code points; the regression
  tests cover it. Self-test: in each run (baseline and candidate), 17 of 17
  scenarios (one unchanged control and 16 sabotaged copies) gave the expected
  result, and 4 of 4 label-map sanity checks behaved as expected.
- Before/after JSON comparison: the JSON reports are byte-identical for 56 of
  56 cases accepted by both versions; the other 14 cases are rejected by at
  least one version (6 duplicate-key cases by the candidate only, 8 cases by
  both). The Markdown reports differ for 62 cases: the 56 accepted by both and
  the 6 duplicate-key cases that only the baseline accepted. Verdict
  transitions: 48 `FAILS -> HOLDS`, 22 `HOLDS -> HOLDS`, none from `HOLDS` to
  `FAILS`.
- Test suite on the tested product commit: measured on
  `fae18242de35facb7c493ff18e86baff3afe2c24` in the development environment
  (editable install, Python 3.11.7): 1123 passed, 0 failed, 0 skipped, 98.02%
  branch coverage (gate 80%); `ruff check .` and `mypy src` (strict, 19 source
  files) report no issues. On Python 3.13.1 the same commit gives 1123 passed
  with 98.02% branch coverage. A clean reproduction from a fresh checkout of
  the documentation commit (product files unchanged), with the built wheel
  installed outside the source tree and the tests importing the installed
  package, confirmed 1123 passed, 0 failed, 0 skipped and 98.02% branch
  coverage on Python 3.11.7, 3.12.15 and 3.13.1, with `ruff check .` and
  `mypy src` clean on each; it also reproduced the evidence package with
  byte-identical case verdicts, measurements and outputs (see
  [the closeout record](evidence/v0.1.1/CLOSEOUT.md)).
- Example outputs: on `fae18242de35facb7c493ff18e86baff3afe2c24`, the
  `expected_report.json`, `input.json` and `proposals.json` files of all five
  examples are byte-identical to `4bd0ba9`; all five `expected_report.md`
  files change by the new citation labels and the display note, and the one of
  `05_mixed_and_fabricated_quote` also by backslash escapes in one claim and
  two quotations.
- Network and provider monitoring: the guard is a Python socket-level hook in
  the harness process and in every CLI subprocess; browser requests are
  blocked by Playwright routing and a host-resolver rule; native code outside
  these paths is not covered. In each binding run, 140 of 140 CLI invocations
  ran with an armed guard, the guard log holds 142 records, all `armed`, and
  the guard refused 0 connection attempts. The browser saw 252 requests on the
  baseline (248 own page loads and 4 blocked remote image requests) and 224
  on the candidate (all own page loads, 0 blocked). The canary before each run
  passed: in the product and harness environments the guard refused 5 of 5
  test attempts (a DNS lookup, a TCP connection, raw connects over IPv4 and
  IPv6, and a UDP send) while a loopback control connected, and the browser
  aborted 2 of 2 remote requests. These zeros apply only to the monitored
  runs; downloads happened only in the separate setup step.

These are software-regression and display observations for this synthetic
catalog and these renderers only. They are not a universal guarantee, not a
benchmark, not live-model accuracy and not evidence of scientific correctness.
They do not retroactively support any owner-reported number below. The
independent display review also observed limits outside the catalog, which
the catalog does not measure: e-mail autolinks in cmark-gfm (including
`mailto:` and `xmpp:` forms), long runs of combining marks drawn over
neighbouring lines in a browser, and look-alike marker brackets. They are
listed in the [changelog](CHANGELOG.md#known-display-limits).

## Owner-reported internal pilot

**Access/status: OWNER-REPORTED INTERNAL EXPERIMENT; not reproduced by public
v0.1.** Claims I01–I04, I06 and I07 refer to the owner's reported internal final
commit `6d0d5cc4b0f14b7fe256e74e81c160ff363eb8f7`. At the original report date,
the internal code and raw evidence were not publicly accessible. The
[2026-10-26 import mapping](publication/2026-10-26/import-index.json) now
identifies public source snapshots and reviewed evidence derivatives. The
unredacted original package and active authorization are not published; no
independent replication or authenticated original-directory replay is claimed.

*Historical record.* The values in this section are retained unchanged. They
are not current public performance claims, and the v0.1.1 evidence package does
not support them retroactively.

### Conditions and units

| Condition | Owner-reported role | Generations |
| --- | --- | --- |
| A | Minimal task prompt | 32 completed: 24 main cases and eight variants |
| B | Scientific v2 prompt | 32 completed: 24 main cases and eight variants |
| C | Existing processing of B | Shares B's raw responses; no additional independent generations |

There were 64 generative slots, not 96 independent responses. C's reuse of B
cannot demonstrate model stabilization. Model evaluation and processing-control
evaluation are different comparisons.

### Outcomes, including null results and misses

| Observation | Owner-reported counts | Interpretation and limit |
| --- | --- | --- |
| Main-case accuracy | A/B/C each 24/24 | B−A = 0 percentage points; ceiling effect, not equivalence or general zero uncertainty. |
| Variant consistency | All eight original/variant pairs jointly correct and consistent in each condition | Related pairs are not independent additional main cases. |
| Deliberately corrupted artifacts | Baseline processing blocked 4/12; full controls blocked 12/12 | Eight additional catches; false accepts on this injected set fell from 8/12 to 0/12. |
| Clean artifact counterparts | 6/6 accepted | No false blocking among these six controls; no population-wide guarantee. |
| Semantically wrong but structurally valid answers | Both controls accepted (2/2) | Semantic errors escaped the structural controls. |
| Shared pre-execution checks | 4/4 failure cases blocked; 2/2 clean controls passed | Shared infrastructure; not an isolated incremental B/C benefit. |
| Official artifact release | Not applicable | No demonstrated end-to-end official release gate. |

Counts describe this finite injected set. They do not establish general AI
safety or improved model accuracy. In particular, catching altered artifacts
is a different outcome from detecting a wrong scientific inference.

### Cost, latency and reported reproducibility

- Known token costs: A **$0.130323**, B **$0.254577**; total known
  **$0.384900**. The conservative upper bound including one interrupted request
  is **$0.411380**. Reserved exposure is not actual spend. No subscription
  usage claim is made (I06).
- Provider median latency: A **7.67 s**, B **14.00 s**, each from 32 completed
  generations. C interpretation median: **0.128 ms**; shared checkpoint check:
  **10.9 ms**. Interpretation timing is not the whole system's overhead (I06).
- The owner reports two identical analysis reproductions, **1,930 passing
  internal tests**, and **692 unchanged historical files**. These are neither
  public v0.1 test counts nor checks performed in this task (I07).

Execution authorization, budget ledgers, state/resume authentication and
environment binding were **REPORTED IMPLEMENTED/TESTED INTERNALLY** in that
pilot (I04); its original report did not inspect a public implementation.
The separate Arena implementation and its current bounded technical checks are
now [publicly inspectable](publication/2026-10-26/VALIDATION.md). A source
fingerprint in core v0.1 must not be represented as one of these execution controls.

### Study limitations

This was a small author-constructed set with one model, N=1, unknown pretraining
exposure and no basis for population estimates. Of 32 stimuli, 31 were reviewed
by an isolated AI reviewer and one only by the author. That is not independent
human peer review. The role describes a study procedure, not project authorship.
Ceiling effects, related variants, shared raw responses, semantic misses and
the inapplicable official-release endpoint restrict the inference.

## Owner-reported historical contract study

**Access/status: owner-reported experiment, separate from the pilot and public
v0.1; original raw package not published in full.** The
[publication mapping](publication/2026-10-26/import-index.json) identifies the
available reviewed source/evidence derivatives. Claim I05 concerns a historical
scientific-contract change whose exact commit was not supplied.

*Historical record.* The values in this section are retained unchanged. They
are not current public performance claims, and the v0.1.1 evidence package does
not support them retroactively.

| Model | Before | After | Observed change |
| --- | --- | --- | --- |
| Haiku | 61/84 (72.62%) | 78/84 (92.86%) | +20.24 percentage points |
| Sonnet | 65/84 (77.38%) | 70/84 (83.33%) | +5.95 percentage points |

Both reached 17/17 ME but shared an Overclaim→CvC regression cluster. These
labels belong to an internal scientific taxonomy, not the public four-relation
schema. The 84 units included related variants and were involved in
development; repeated outputs are not independent cases.

The observations show different responses to a scientific-contract change.
They do not establish that the entire governance control system caused the
gains, or independently establish a causal model-by-contract interaction.
Do not combine this study, the later pilot or their taxonomies into one pooled
efficacy figure. The 2026-10-26 [publication mapping](publication/2026-10-26/README.md)
now identifies reviewed source snapshots, publishable evidence derivatives,
original/public hashes and the remaining reproduction limits.

## Owner-reported internal technical v1.0.0

**Access/status updated 2026-10-26:** the historical internal technical v1.0.0
is now the source of the separate public [Arena 1.0.1 research package](agent-arena/README.md).
It contains implemented Phases 1–10, including R08–R10, with a disclosed nested-path
integration correction. [Current publication checks](publication/2026-10-26/VALIDATION.md)
record the actually executed offline technical acceptance; the
[import mapping](publication/2026-10-26/import-index.json) identifies published
source and evidence derivatives and their limits. These are Arena checks, not
measurements of the Inspektorium core 0.1.1 or independent study replication.
Historical limited live checks concerned earlier internal states; neither the
internal closeout nor this final public code was live-tested again. No scientific
efficacy is demonstrated, and the [final v1 gate](ROADMAP.md#final-v1-gate) is not met.

## Maintenance evidence addendum — 2026-10-24

The [E1/E2/E3 addendum](evidence/v0.1.1/addendum-20261024/README.md) records
new bounded engineering checks for `403bd3f`, separately from the historical
`fae1824` results above. It corrects the formerly documented e-mail and
combining-run text rule and protects existing setup targets. The visual Gate R
remains BLOCKED: 6/75 Noto and 5/75 GitHub-like cases still add ink inside an
Answer span text box. This is not a
scientific validation or benchmark; none of the historical numbers changes.


### 2026-10-24 E1 layout follow-up

The [layout follow-up](evidence/v0.1.1/addendum-20261024-e1-layout/README.md)
records a separate claim paragraph at `5ace279`. The same 87-case addendum
now has 0/75 visual hits and 0 INVALID in each named style, zero text-rule
violations across 348 renderings, no e-mail links, and 87 unchanged JSON
reports. The earlier 6/75 and 5/75 results above remain historical.
These are engineering checks, not new scientific validation. Terminology
correction: the earlier 98.04% is overall coverage with branch measurement
enabled, not a separate pure branch-coverage rate; its numeric value is unchanged.
