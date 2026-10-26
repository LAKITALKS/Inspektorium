# Inspektorium v0.1.1 — closeout record of the local candidate

> Historical record of 2026-10-13, retained with its original counters and
> known limits. It is not acceptance evidence for the later E1/E2/E3 changes.
> Later follow-ups: [E1/E2/E3 closeout](addendum-20261024/README.md) and
> [current E1 layout closeout](addendum-20261024-e1-layout/README.md).
> In the current setup tool, existing `--venv` targets are refused; the older
> replacement warning below describes the historical tool.

Prepared 2026-10-13 for the maintainer's publication decision. Nothing has been
published: no push, pull request, merge, tag, GitHub release, package upload,
DOI or website change.

**Status: READY_FOR_PUBLICATION_REVIEW.**

| Item | Value |
|---|---|
| Public baseline | `main` at `4bd0ba9218df80a69089838f824ae0ac28881ac4` (package 0.1.0); not the older tag `v0.1.0` (`a376c40`) |
| Branch | `release/v0.1.1-candidate` (local) |
| Product commits | `7c9d43890e25006ae9d035866350f8d62083718e` (first candidate, superseded by correction round 1), `fae18242de35facb7c493ff18e86baff3afe2c24` (**tested product commit**) |
| Documentation and evidence commit | `093ea02630f3a0a8790eb533a9e28220c3c89e32` |
| Closeout commit | the commit that adds this file; product files unchanged after the tested product commit |
| Package / report schema | 0.1.1 / 0.1 (JSON field names and JSON schema documents unchanged) |
| License | PolyForm Noncommercial 1.0.0, byte-identical (SHA-256 `c0ea4a89…fabbe5`) |

Check that a later commit carries the tested product:
`git diff fae18242de35facb7c493ff18e86baff3afe2c24 <commit> -- src tests examples pyproject.toml`
must be empty.

## Gate matrix

| Gate | Criterion | Result | Evidence |
|---|---|---|---|
| R | Known display defects reproduced and fixed; real controls visible; raw data unchanged; clean counterparts readable | PASS | [README §Reproduced on the baseline](README.md), [candidate results](results/candidate-fae1824/), `tests/test_render_safety.py`, `tests/test_display.py` |
| P | Ambiguous inputs rejected early; valid inputs unchanged; model invariants tested | PASS | `tests/test_cli_input_rejection.py`, `tests/test_input_parsing.py`, `tests/test_model_invariants.py`, catalog input cases |
| E | Public offline catalog, honest before/after comparison, measured and version-bound results | PASS | [README.md](README.md), [catalog](catalog/catalog.json), [baseline](results/baseline-4bd0ba9/), [candidate](results/candidate-fae1824/) |
| D | Working rules, scope, limits, historical numbers and release status consistent | PASS (decisions prepared, not approved) | [AGENTS.md](../../AGENTS.md), [CHANGELOG.md](../../CHANGELOG.md), [RELEASE_CHECKLIST.md](../../RELEASE_CHECKLIST.md), [DOCUMENTATION_DECISIONS.md](DOCUMENTATION_DECISIONS.md) |
| V | Independent reviews and clean reproduction of the final product state | PASS (with notes; one of two correction rounds used) | §Independent checks below |

## Defects reproduced and fixed

Reported in the order and reproduced on `4bd0ba9`:

- **C1, line injection and hiding.** A rationale with line feeds and fake
  `passed` lines produced forged control lines; an unterminated `<!--` hid the
  validation warnings, later findings and the limitations section in
  HTML-processing renderers.
  - Catalog result on the baseline: forged status or control lines in 10 of 19
    line-injection cases (37 of 76 renderings), for LF, CR and CRLF in claim,
    rationale and quotation, plus an LF+TAB continuation.
  - The 9 U+2028/U+2029/NEL cases created no new line. They count as manipulated
    only because the raw separator stayed and payload Markdown was rendered.
  - Candidate: 76 of 76 line-injection renderings intact.
- **C5, raw bidirectional controls.** U+202E and similar characters were
  emitted raw. They are now displayed as `⟦U+XXXX⟧` markers by the documented
  category rule (Cc, Cf, Cs, Zl, Zp, and Cn of the running Python's Unicode
  database).
- **C4, duplicate keys in `--input`.** These were silently resolved with the
  last value winning (6 of 6 duplicate-key catalog cases accepted with exit 0).
  `--input` now uses the same strict decoder as proposals. The duplicates are
  rejected with exit 2 before any provider call or output, and an existing
  `--output` file stays byte-identical.

Found and fixed during the work (each with a regression test that fails on the
vulnerable state):

- Model invariant gap: a finding could be marked as having a verified citation
  with an incomplete evidence reference, and such a report passed validation.
  Pipeline outputs and JSON schema documents are unchanged.
- Deeply nested `--proposals` crashed with a traceback (exit 1). It now exits 2
  with a bounded message.
- A late encoding failure truncated an existing `--output` file. Encodability
  is now checked before the file is opened.
- `--input` errors echoed input values, including raw control and bidi
  characters, to standard error. Messages are now one bounded ASCII line.
- `--generated-at` is now validated before proposals are loaded or a provider
  is constructed.
- Unicode-version dependence of the marker rule, found by the independent
  display review: format characters assigned after the running Python's
  Unicode version stayed raw. This was fixed in correction round 1 by also
  marking unassigned (Cn) code points.

Documented non-reproductions, not counted as baseline failures:

- R-HH-02: an inline `<!--` without a line break.
- NaN/Infinity and unpaired surrogates in `--input` were already rejected by
  0.1.0.
- Duplicate keys in proposals were already rejected.
- Source titles and identifiers are not reachable as display payloads.
- Line forging by U+2028, U+2029 and NEL did not occur on the baseline.

## Measured results

- **Evidence package** (catalog 1.0, 70 cases, 4 renderer configurations):
  - Baseline `FAIL`: 22 of 70 cases hold. Of 280 renderings, 32 were rejected
    before rendering, 83 intact, 165 manipulated and 0 not executed.
  - Candidate `PASS`: 70 of 70 cases hold. Of 280 renderings, 56 were rejected
    before rendering, 224 intact, 0 manipulated and 0 not executed.
  - JSON reports are byte-identical for 56 of 56 cases accepted by both
    versions.
  - Self-test in each run: 17 of 17 scenarios and 4 of 4 label-map checks as
    expected.
  - These results apply to this synthetic catalog only; they are not a
    detection or false-alarm rate.
- **Renderers:**
  - cmark-gfm 0.29.0.gfm.13 (cmarkgfm 2025.10.22): unsafe mode with GFM
    extensions, and safe mode;
  - markdown-it-py 4.2.0: commonmark, `html=True`;
  - Python-Markdown 3.11: tables, fenced_code;
  - Chromium 153.0.8010.12 via Playwright 1.63.0, with page JavaScript
    disabled;
  - Python 3.11.7 with Unicode 14.0.0.
  - "GFM-compatible" means the local library; GitHub's web service was not
    tested.
- **Test suite on `fae18242…`:** 1123 passed, 0 failed, 0 skipped; branch
  coverage 98.02% (CI gate 80%); `ruff check .` and `mypy src` (strict) clean.
  - Measured in the development environment on Python 3.11.7 and 3.13.1.
  - Confirmed by the clean reproduction with the installed wheel on Python
    3.11.7, 3.12.15 and 3.13.1.
  - Baseline `4bd0ba9`: 74 passed, 88.11%.
- **Examples:** the five `expected_report.json`, `input.json` and
  `proposals.json` files are byte-identical to `4bd0ba9`.
  - The five `expected_report.md` files change by the citation labels and the
    display note; example 05 also gains escapes such as `p\.m.`.
  - The installed CLI regenerated all of them: 20 of 20 byte-identical.
- **Network and provider measurement:**
  - **Reach:** a Python socket-level guard covers the harness and every CLI
    subprocess, and Playwright routing plus a host-resolver rule cover the
    browser. Native programs outside these paths are not covered.
  - **Per evidence run:** 140 of 140 CLI processes had an armed guard and the
    guard refused 0 attempts. The browser blocked 4 remote image requests on
    the baseline and 0 on the candidate.
  - **Canary:** passed; 5 of 5 test attempts were refused per environment, and
    no request was sent.
  - **Scope of the zeros:** they apply to the monitored runs only.
  - **Setup downloads:** listed separately in the [setup log](results/setup/setup_log.jsonl).
  - **Project API:** no live model call, no token counting and no provider
    credential was used.

## Independent checks

Independence here means separate roles with their own counter-probes; it does
not mean empirically demonstrated independence of the models used.

- **Display review (V1), on `7c9d438`:** PASS_WITH_NOTES. R1–R4, R6 and R7
  were confirmed with 48 additional probes and 6 tampered reports across 7
  renderer configurations and Chromium.
  - R5 was refuted by the Unicode-version finding and fixed in correction
    round 1.
  - The remaining items were notes on combining marks, `mailto:`/`xmpp:`
    autolinks, label-map scope and look-alike brackets. Each is documented.
- **Parser and measurement review (V2), on `7c9d438`:** PASS_WITH_NOTES. P1–P6
  and E1–E5 were confirmed with a differential corpus of 195 documents (0 accepted
  by the candidate only), a wheel rebuild, independent recounts and sabotage
  runs.
  - Three should-fix findings were fixed in correction round 1:
    - the aggregator trusted stored derived fields;
    - CR-normalised stored texts;
    - an overstated baseline C1 statement.
- **Correction round 1:** product commit `fae18242…`, hardened evidence tools,
  and both binding runs re-measured.
- **Re-check (V1, V2):** every finding RESOLVED, with no regression. The
  probes and the evidence harness copy reproduced the earlier classification.
  Two new notes remain (see later tasks). The second correction round was not
  needed.
- **Clean reproduction (V3), on `093ea02…`:** PASS_WITH_NOTES.
  - Fresh clone; sdist and wheel built; the wheel holds only package files and
    metadata; installed outside the checkout; the installed package was
    imported.
  - Full suite, ruff and mypy on Python 3.11.7, 3.12.15 and 3.13.1 as listed
    above. CLI and examples as listed above.
  - Both evidence runs reproduced with byte-identical verdicts, measurements,
    outputs and browser-request logs.
  - Every documented number was matched against its own measurements.
  - A scan of all tracked files found no secrets, absolute local paths or raw
    control characters, and no internal material beyond the pre-existing
    pilot commit id.
  - Its notes were documented (wheel hash of documentation-only commits,
    CLAIMS intro wording, independent re-run recipe, `setup_env.py` path
    caution) or listed as later tasks.

## Deliberate limits

- **Exact text binding is not meaning.**
  - An exact excerpt can omit a negation (P14).
  - A true quote can carry a false relation (P09).
  - `not_established` is not a refutation (P15).
  - Empty findings and exit 0 do not prove coverage (P10, P11).
  - Schema validity is neither a re-check nor a proof of origin (P16).
  - Strict offsets reject correct text at a wrong offset, and no general
    false-alarm rate follows from that (P17).
- **Known display limits** (see [CHANGELOG](../../CHANGELOG.md#known-display-limits)):
  - cmark-gfm autolinks e-mail addresses, including the `mailto:` and `xmpp:`
    forms;
  - long runs of combining marks can visually overlap later lines;
  - look-alike brackets are not marked;
  - the marker rule follows the running Python's Unicode database;
  - GitHub's web service, other viewers and Python-Markdown extensions such as
    `attr_list` were not tested;
  - tools that strip trailing spaces join the lines of a quotation.

## Later tasks (observations outside this version)

- `markdown_report.py` docstring: name the cmark-gfm e-mail autolink exception
  next to "cannot add Markdown or HTML structure".
- Evidence aggregator: it does not detect consistently forged criterion values
  or browser-network rows. Re-deriving K12 from `browser_network.jsonl`,
  checking guard-record times and checking `cases_manifest` against the
  manifest would harden it. Independent re-runs remain the check.
- `setup_env.py`: refuse to replace a `--venv` path that is not its own venv.
- The label-map branches for a failed guard without a citation check, the
  `generated_at` line and empty findings are not exercised by catalog 1.0. The
  catalog also has no e-mail case and no unassigned code point. A future
  catalog version could add these, labelled as development additions.
- `compare_versions.py` selects the cases accepted by both versions from stored
  CLI classes.
- The `--answer`/`--source` CLI path still prints multi-line validation text.
- `--output` directories are not validated before an optional provider call.
- An OS-level failure in the middle of a write can still truncate an output
  file.
- `InspectionInput.model_validate_json` keeps Pydantic's last-wins behaviour.
  The documentation points library users to the strict functions.
- Optional hardening: mark or cap long combining-mark runs; always escape `{`
  and `}` for Python-Markdown `attr_list`.
- No public fixture yet demonstrates the negation-omitting excerpt (P14).
- `ruff format --check` was already not clean at the baseline and is not part
  of CI.

## Prepared decisions for the maintainer

- Historical numbers: the owner-reported pilot numbers are presented
  qualitatively in the README, and the original records stay unchanged. See
  [DOCUMENTATION_DECISIONS.md](DOCUMENTATION_DECISIONS.md). This is prepared,
  not approved.
- Naming: public v0.1.1 versus the owner-reported internal technical v1.0.0,
  which is not part of this package, without internal identifiers or counts.
- Whether the pre-existing owner-reported pilot commit id in CLAIMS I01 and
  RESEARCH_RESULTS stays. It is unchanged from `4bd0ba9`.
- Whether this closeout record, including the work log below, is published
  with the release or kept as a local record.
- On publication day:
  - set the CHANGELOG date and optionally `date-released` in `CITATION.cff`;
  - the tagged commit then changes documentation only;
  - a wheel built from it differs from the measured wheel only in its metadata
    (README long description).

## Publication summary (not executed)

1. Review the diff `4bd0ba9218df80a69089838f824ae0ac28881ac4..<closeout commit>`
   on branch `release/v0.1.1-candidate`.
2. If approved, add the publication date in a final documentation commit (see
   above) and fast-forward public `main` on
   `https://github.com/LAKITALKS/Inspektorium` to that commit. The branch is
   based on the current public `main`.
3. Create the annotated tag `v0.1.1` on that commit. `v0.1.0` stays unchanged.
4. Publish a GitHub Release `v0.1.1` with the CHANGELOG notes.
5. Separate decisions, not part of this candidate: package-index upload,
   archive/DOI, and any change to inspektorium.org.

The intended public file set is every tracked file of the closeout commit,
including `AGENTS.md`, `CHANGELOG.md`, the updated documentation and the
complete `evidence/v0.1.1/` directory: catalog, config, tools, pinned
requirements, results, README and DOCUMENTATION_DECISIONS. Whether to include
this closeout record is the maintainer's choice. Internal orchestration notes
and agent transcripts are not in the repository.

## Work log of this preparation

This section records how the candidate was prepared. It is not a requirement
for users or contributors.

- **Orchestration:** one orchestrator coordinated the work. The implementation
  and verification roles were separate sub-agents with disjoint file
  ownership, and sub-agents did not delegate further.
- **Configuration:**
  - Configured for every sub-agent: Claude Opus 5.5 with reasoning effort
    "extra high" (`xhigh`).
  - Evidenced in the runtime metadata: every assistant turn of all 18 agent
    runs (2,730 turns) recorded model `claude-opus-5-5` and effort `xhigh`;
    there was no downgrade.
- **Cost:** sub-agent work consumed about 5.3 million tokens across the
  workflows. This is orchestration usage, separate from the project API
  budget; no project API call was made.

| Role | Runs | Task | File ownership | Result |
|---|---|---|---|---|
| U1 report display | 3 (initial, follow-up, correction) | C1/C5 fix, labels, display rule, regression tests | `src/inspektorium/report/*` except `json_report.py`, render and example tests, `examples/*/expected_report.md` | done; tests fail on the baseline at the symptom |
| U2 input and invariants | 2 | C4 fix, strict decoder, output protection, invariant tests and invariant fix | `cli.py`, `providers/parsing.py`, `core/strict_json.py`, `core/models.py` (one invariant), input and model tests | done; tests fail on the baseline at the symptom |
| U3 evidence package | 4 (catalog and baseline, binding runs, tool hardening, re-runs) | catalog, harness, binding before/after runs | `evidence/v0.1.1/**` except DOCUMENTATION_DECISIONS | done; candidate `PASS`, baseline `FAIL` |
| U4 documentation | 4 (draft, alignment ×2, placeholder fill) | AGENTS, CHANGELOG, public documents, checklist, decisions | top-level documentation, `CITATION.cff`, version lines, DOCUMENTATION_DECISIONS | done; decisions prepared, not approved |
| V1 display review | 2 (review, re-check) | adversarial display verification | read-only | PASS_WITH_NOTES; findings resolved |
| V2 parser and measurement review | 2 (review, re-check) | adversarial parser, aggregation and provenance verification | read-only | PASS_WITH_NOTES; findings resolved |
| V3 clean reproduction | 1 | fresh clone, build, install, full checks, evidence reproduction, documentation consistency | read-only | PASS_WITH_NOTES |
