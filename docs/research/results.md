# Research results

Inspektorium keeps public reproducibility observations apart from owner-reported internal studies.
One evidence class cannot substitute for another.
Each claim is indexed in the [claim ledger](claims.md).
Historical values appear unchanged, with their original labels and dates.
The 0.3.0 packaging change adds no new measurement to this page.
General limits are stated once in [limitations](../evaluation/limitations.md).

| Section | Evidence label | Claims | Original record |
| --- | --- | --- | --- |
| [Public v0.1 observations](#public-v01-observations) | Supplied reviewer observation, historical CI | P01–P11 | [Results, 2026-09-15][rr-v01] |
| [Public v0.1.1 evidence package](#public-v011-evidence-package) | Public observation, offline, synthetic | P12, P13 | [Evidence package, 2026-10-13](../../evidence/v0.1.1/README.md) |
| [Maintenance addenda](#maintenance-addenda-2026-10-24) | Public observation, bounded engineering check | P12, P18 | [Addendum, 2026-10-24](../../evidence/v0.1.1/addendum-20261024/README.md) |
| [Internal pilot](#owner-reported-internal-pilot) | Owner-reported internal experiment | I01–I04, I06, I07 | [Results, pilot section][rr-pilot] |
| [Contract study](#owner-reported-historical-contract-study) | Owner-reported experiment | I05 | [Results, contract study][rr-contract] |
| [Internal technical v1.0.0](#owner-reported-internal-technical-v100) | Owner-reported closeout, public offline checks | R08–R10 | [Results, v1.0.0 section][rr-v100] |

## Public v0.1 observations

**Label: supplied reviewer observation.** Source: [historical results][rr-v01].
It was not a new measurement by the documentation task.

- Claims P01–P11 apply to reviewed commit `16f572168025c393e953e34ccad184ca577e2bd0`.
- The reviewer inspected all 59 files and verified their fetched Git blob hashes.
- All five offline examples reproduced their ten expected JSON/Markdown outputs byte-for-byte.
- Environment: Python 3.12.14 with Pydantic 2.13.5.
- The reviewer ran neither the full pytest suite nor any live provider call.

**Label: historical CI.** The [CI run for that commit][ci] succeeded on Python 3.11 and 3.12.
It covered lint, type checks and tests.

**Label: historical software-quality measurement, 2026-08-11 audit.**
The [release checklist][checklist] records 74 tests.
It records 88.11% overall branch-enabled coverage.
It records 89.10% deterministic-core branch-enabled coverage.
Local checks for the 2026-09-15 documentation change and for v0.1.1 are in the same checklist.

### Counterexamples and reporting boundary

- **False semantic relation (P09).** The reviewer changed `contradicted` to `supported` in [example 02](../../examples/inspect/02_contradicted/proposals.json).
  The true quote and offsets stayed. The false relation remained mechanically reportable.
  The probe is not a shipped fixture.
- **Finding-level containment (P03, P11).** [Example 05](../../examples/inspect/05_mixed_and_fabricated_quote/expected_report.json) keeps a valid finding.
  It sets the fabricated-quote finding's `reportable_relation` to null.
  The proposal stays visible, the report is emitted and the CLI exits 0.
- **Absence and coverage (P04, P10).** `not_established` can stay reportable with all citation fields null.
  A supplied optional citation must validate. Empty findings are allowed.
- **Current content, not authentication (P05).** Changing source text outside the cited span changes its input hash.
  No historical-state check runs, and the unchanged span can still pass.
- **Deterministic representation (P06).** JSON includes `generated_at: null` by default; Markdown omits the date line.
  Equal bundle hashes hold for identical canonical IDs and texts in any source order.

The five examples use synthetic precomputed proposals.
They show saved-input behaviour and exact fault handling, not live-model accuracy.

## Public v0.1.1 evidence package

**Label: public observation; offline and synthetic; 2026-10-13.** Source: [evidence package](../../evidence/v0.1.1/README.md).

### Setup

- **Versions compared.** Public `main` `4bd0ba9218df80a69089838f824ae0ac28881ac4` (not tag `v0.1.0`) and the v0.1.1 candidate `fae18242de35facb7c493ff18e86baff3afe2c24`.
- **Catalog.** `inspektorium-v0.1.1-display-and-input`, version 1.0, 70 cases, frozen before the comparison.
- **Case kinds.** Attack defence, clean counterparts, readability, reachability, input rejection and input acceptance.
- **Families.** Line injection (LF, CR, CRLF, U+2028, U+2029, NEL, TAB-indented continuation); hiding through HTML comments, elements and styles.
  Also heading, fence, table, list and inline-markup breakouts; links, autolinks, images and entity references.
  Also bidirectional, zero-width, BOM and C0/C1 controls; marker-text collisions; real failures followed by clean findings.
  Also clean multilingual text; host-composed lines; duplicate keys; `NaN`/`Infinity`; unpaired surrogates; clean inputs.
- **Not in the catalog.** E-mail addresses. Byte order mark, trailing data and deep nesting are covered by the test suite instead.
- **Renderers.** cmark-gfm 0.29.0.gfm.13 through `cmarkgfm` 2025.10.22, GFM extensions, once with `CMARK_OPT_UNSAFE` and once in safe mode.
  Also markdown-it-py 4.2.0 (CommonMark preset, `html=True`, table, strikethrough) and Python-Markdown 3.11 (`tables`, `fenced_code`).
- **Browser.** Chromium 153.0.8010.12 (Playwright 1.63.0 build, headless, page JavaScript disabled) for DOM and visibility checks.
- **Python.** 3.11.7 with Unicode database 14.0.0, for product and harness in both binding runs.
- **No provider key.** Network and provider monitoring is reported below.

Each case and renderer configuration gets one outcome class.
The classes are `REJECTED_BEFORE_RENDER`, `RENDERED_CONTROLS_INTACT`, `RENDERED_MANIPULATED` and `NOT_EXECUTED`.
Each case gets one verdict: `HOLDS`, `FAILS`, `NOT_DEMONSTRATED` or `NOT_EXECUTED`.
A rejected input is not a passed rendering test. A skipped measurement never counts as a pass.

### Results

| Measure | Before (`4bd0ba9`) | After (`fae1824`) |
| --- | --- | --- |
| Run result | `FAIL` | `PASS` |
| Cases holding | 22 of 70 (48 fail) | 70 of 70 (none fails) |
| `NOT_DEMONSTRATED` or `NOT_EXECUTED` cases | none | none |
| Attack | 1 of 42 | 42 of 42 |
| Clean counterparts | 6 of 7 | 7 of 7 |
| Readability | 3 of 3 | 3 of 3 |
| Reachability | 3 of 3 | 3 of 3 |
| Input rejection | 6 of 12 | 12 of 12 |
| Input acceptance | 3 of 3 | 3 of 3 |
| Renderings (70 cases × 4 configurations) | 280 | 280 |
| `RENDERED_MANIPULATED` | 165 | 0 |
| `RENDERED_CONTROLS_INTACT` | 83 | 224 |
| `REJECTED_BEFORE_RENDER` | 32 | 56 |
| `NOT_EXECUTED` | 0 | 0 |

Source for every row: [evidence package results](../../evidence/v0.1.1/README.md#results).

**Before, details.** Forged status or control lines appeared in 10 of 19 line-injection cases (37 of 76 renderings).
The 9 U+2028, U+2029 and NEL cases created no new report line.
They count as manipulated because the raw separator stayed and the payload's Markdown rendered as formatting.
The six duplicate-key `--input` cases were accepted with exit code 0.
The failing clean counterpart was interpreted as formatting or HTML by every renderer.
In one link case, each renderer's page attempted a remote image request (4 requests, all blocked by the browser).
Such an attempt also makes the run `FAIL`.

**After, details.** The 56 rejected renderings are the 12 input-rejection cases and 2 reachability cases with a rejected identifier, 4 renderings each.
Each of the four configurations has 56 intact and 14 rejected renderings.
The 19 line-injection cases give 76 of 76 intact renderings.
Clean counterparts and readability cases give 40 of 40.
No rendered page made a request other than loading itself.
No catalog string contains a code point unassigned in Unicode 14.0.0; regression tests cover that marking instead.

**Self-test.** In each run, 17 of 17 scenarios gave the expected result: one unchanged control and 16 sabotaged copies.
4 of 4 label-map sanity checks behaved as expected.

**Before/after comparison.** JSON reports are byte-identical for 56 of 56 cases accepted by both versions.
The other 14 cases are rejected by at least one version: 6 duplicate-key cases by the candidate only, 8 by both.
Markdown reports differ for 62 cases: the 56 accepted by both and the 6 the baseline alone accepted.
Verdict transitions: 48 `FAILS -> HOLDS`, 22 `HOLDS -> HOLDS`, none `HOLDS -> FAILS`.

**Test suite on the tested product commit.** Source: [closeout record](../../evidence/v0.1.1/CLOSEOUT.md).
- On `fae18242de35facb7c493ff18e86baff3afe2c24`, editable install, Python 3.11.7: 1123 passed, 0 failed, 0 skipped.
  Branch coverage 98.02% (gate 80%). `ruff check .` and `mypy src` (strict, 19 source files) report no issues.
- On Python 3.13.1 the same commit gives 1123 passed with 98.02% branch coverage.
- A clean reproduction used a fresh checkout of the documentation commit, with product files unchanged.
  The built wheel was installed outside the source tree, and the tests imported the installed package.
  It confirmed 1123 passed, 0 failed, 0 skipped and 98.02% on Python 3.11.7, 3.12.15 and 3.13.1.
  `ruff check .` and `mypy src` were clean on each.
  It reproduced the evidence package with byte-identical verdicts, measurements and outputs.

**Example outputs.** On `fae1824`, `expected_report.json`, `input.json` and `proposals.json` of all five examples are byte-identical to `4bd0ba9`.
All five `expected_report.md` files change by the new citation labels and the display note.
The one of `05_mixed_and_fabricated_quote` also changes by backslash escapes in one claim and two quotations.

**Network and provider monitoring.** Source: [network measurement](../../evidence/v0.1.1/README.md#network-and-provider-measurement).
- The guard is a Python socket-level hook in the harness and every CLI subprocess.
  Browser requests are blocked by Playwright routing and a host-resolver rule.
- In each binding run, 140 of 140 CLI invocations ran with an armed guard.
  The guard log holds 142 records, all `armed`. The guard refused 0 connection attempts.
- The browser saw 252 requests on the baseline: 248 own page loads and 4 blocked remote image requests.
  It saw 224 on the candidate: all own page loads, 0 blocked.
- Canary before each run: the guard refused 5 of 5 test attempts in product and harness environments.
  The attempts were a DNS lookup, a TCP connection, raw IPv4 and IPv6 connects and a UDP send.
  A loopback control connected. The browser aborted 2 of 2 remote requests.
- These zeros apply only to the monitored runs. Downloads happened only in the separate setup step.

**Limits specific to this package.** The results cover this synthetic catalog and these renderers only.
They do not support any owner-reported number below.
The independent display review observed limits outside the catalog; they are listed under [display limits](../evaluation/limitations.md#display).

## Maintenance addenda 2026-10-24

**Label: public observation; bounded engineering check, not scientific validation.**

- **E1/E2/E3 addendum, commit `403bd3f`.** Source: [addendum](../../evidence/v0.1.1/addendum-20261024/README.md).
  It corrects the e-mail and combining-run text rule and protects existing setup targets (P18).
  Visual Gate R remained BLOCKED: 6/75 Noto and 5/75 GitHub-like cases still added ink inside an Answer span text box.
- **E1 layout follow-up, commit `5ace279`.** Source: [layout follow-up](../../evidence/v0.1.1/addendum-20261024-e1-layout/README.md).
  It places the claim in a separate paragraph.
  The same 87-case addendum then has 0/75 visual hits and 0 INVALID in each named style.
  It records zero text-rule violations across 348 renderings, no e-mail links and 87 unchanged JSON reports.
  The earlier 6/75 and 5/75 results remain historical.
- **Terminology correction, same follow-up.** The earlier 98.04% is overall coverage with branch measurement enabled.
  It is not a separate pure branch-coverage rate. Its numeric value is unchanged.

## Owner-reported internal pilot

**Label: owner-reported internal experiment; not reproduced by public v0.1.** Source: [historical results][rr-pilot].

- Claims I01–I04, I06 and I07 refer to the reported internal final commit `6d0d5cc4b0f14b7fe256e74e81c160ff363eb8f7`.
- At the original report date, internal code and raw evidence were not public.
- The [2026-10-26 import mapping][import-index] identifies public source snapshots and reviewed evidence derivatives.
- The unredacted original package and active authorization are not published.
- No independent replication or authenticated original-directory replay is claimed.

### Conditions and units

| Condition | Owner-reported role | Generations |
| --- | --- | --- |
| A | Minimal task prompt | 32 completed: 24 main cases and eight variants |
| B | Scientific v2 prompt | 32 completed: 24 main cases and eight variants |
| C | Existing processing of B | Shares B's raw responses; no additional independent generations |

There were 64 generative slots, not 96 independent responses.
C's reuse of B cannot demonstrate model stabilization.

### Outcomes, including the null result

| Observation | Owner-reported counts | Interpretation |
| --- | --- | --- |
| Main-case accuracy | A/B/C each 24/24 | **Null result:** B−A = 0 percentage points. Ceiling effect, not equivalence. |
| Variant consistency | All eight original/variant pairs jointly correct and consistent in each condition | Related pairs are not independent main cases. |
| Deliberately corrupted artifacts | Baseline processing blocked 4/12; full controls blocked 12/12 | Eight additional catches; false accepts fell from 8/12 to 0/12. |
| Clean artifact counterparts | 6/6 accepted | No false blocking among these six controls. |
| Semantically wrong but structurally valid answers | Both controls accepted (2/2) | **Miss:** semantic errors escaped the structural controls. |
| Shared pre-execution checks | 4/4 failure cases blocked; 2/2 clean controls passed | Shared infrastructure, not an isolated B/C benefit. |
| Official artifact release | Not applicable | No demonstrated end-to-end official release gate. |

Counts describe this finite injected set.
Catching altered artifacts is a different outcome from detecting a wrong scientific inference.

### Cost, latency and reported reproducibility

- **Known token costs (I06).** A $0.130323, B $0.254577; total known $0.384900.
  The conservative upper bound including one interrupted request is $0.411380.
  Reserved exposure is not actual spend. No subscription usage claim is made.
- **Latency (I06).** Provider median: A 7.67 s, B 14.00 s, each from 32 completed generations.
  C interpretation median: 0.128 ms. Shared checkpoint check: 10.9 ms.
  Interpretation timing is not whole-system overhead.
- **Reproducibility (I07).** The owner reports two identical analysis reproductions, 1,930 passing internal tests and 692 unchanged historical files.
  These are not public test counts.
- **Controls (I04).** Execution authorization, budget ledgers, state/resume authentication and environment binding were reported implemented and tested internally.
  The original report did not inspect a public implementation.
  The audit runtime and its [bounded technical checks][validation] are now publicly inspectable.

### Study limitations

- Small author-constructed set, one model, N=1, unknown pretraining exposure.
- Of 32 stimuli, 31 were reviewed by an isolated AI reviewer and one only by the author.
  This is not independent human peer review.
- Ceiling effects, related variants, shared raw responses and semantic misses restrict the inference.

## Owner-reported historical contract study

**Label: owner-reported experiment; separate from the pilot; raw package not published in full.** Source: [historical results][rr-contract].
Claim I05 concerns a scientific-contract change whose exact commit was not supplied.
The [publication mapping][import-index] identifies the available reviewed derivatives.

| Model | Before | After | Observed change |
| --- | --- | --- | --- |
| Haiku | 61/84 (72.62%) | 78/84 (92.86%) | +20.24 percentage points |
| Sonnet | 65/84 (77.38%) | 70/84 (83.33%) | +5.95 percentage points |

- Both models reached 17/17 ME but shared an Overclaim→CvC regression cluster.
- These labels belong to an internal scientific taxonomy, not the public four-relation schema.
- The 84 units included related variants and were involved in development.
- The results show different responses to one contract change. They do not establish causation by the whole control system.
- Do not pool this study with the pilot or merge their taxonomies.

## Owner-reported internal technical v1.0.0

**Label: owner-reported closeout; public offline technical checks dated 2026-10-26.** Source: [historical results][rr-v100].

- The internal technical v1.0.0 is the source of the public audit runtime 1.0.1 research prerelease.
- It contains implemented Phases 1–10, including R08–R10, with a disclosed nested-path integration correction.
- [Publication checks][validation] record the executed offline technical acceptance.
- The [import mapping][import-index] identifies published source and evidence derivatives and their limits.
- These checks concern the audit runtime, not the reference checker or an independent study replication.
- Historical limited live checks concerned earlier internal states. The final code was not live-tested again.
- No scientific efficacy is demonstrated. The scientific Final v1 gate is not met.

[rr-v01]: https://github.com/LAKITALKS/inspektorium-research-record/blob/record-2026-10-27/historical-docs/RESEARCH_RESULTS.md#public-v01-observations
[rr-pilot]: https://github.com/LAKITALKS/inspektorium-research-record/blob/record-2026-10-27/historical-docs/RESEARCH_RESULTS.md#owner-reported-internal-pilot
[rr-contract]: https://github.com/LAKITALKS/inspektorium-research-record/blob/record-2026-10-27/historical-docs/RESEARCH_RESULTS.md#owner-reported-historical-contract-study
[rr-v100]: https://github.com/LAKITALKS/inspektorium-research-record/blob/record-2026-10-27/historical-docs/RESEARCH_RESULTS.md#owner-reported-internal-technical-v100
[ci]: https://github.com/LAKITALKS/Inspektorium/actions/runs/31686541040
[checklist]: https://github.com/LAKITALKS/inspektorium-research-record/blob/record-2026-10-27/historical-docs/RELEASE_CHECKLIST.md
[import-index]: https://github.com/LAKITALKS/inspektorium-research-record/blob/record-2026-10-27/publication/2026-10-26/import-index.json
[validation]: https://github.com/LAKITALKS/inspektorium-research-record/blob/record-2026-10-27/publication/2026-10-26/VALIDATION.md
