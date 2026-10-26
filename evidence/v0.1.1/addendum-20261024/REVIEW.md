# Separate E1/E2/E3 review — 2026-10-24

**Verdict: BLOCKED.** E1's requested raw-text rule is implemented and tested,
but its declared visual acceptance criterion still fails. E2 and E3 pass the
bounded checks described below. This report is not publication authorization.

Reviewed product: `403bd3fac27f2406a150b2243a691ba4d0b12fbb`, branch
`codex/v0.1.1-e1-e3-closeout-20261024`. Baseline product:
`fae18242de35facb7c493ff18e86baff3afe2c24`; its `src` and `pyproject.toml`
are identical to the starting closeout commit
`5ee4f40a53f817973517af5f9a7ff4fc3cef413b`.

The reviewer read the authoritative 2026-10-24 request, AGENTS.md,
CONTRIBUTING.md, SCOPE.md, the focused product/test diff, the supplied historical
probe's relevant measurement contract, the new catalog/harness, current rule
documentation and dated addendum. Review stayed within E1/E2/E3. The reviewer
made no product, documentation or harness changes, used no recursive delegation,
and ran no provider, download, installation or public action. Own scripts,
logs and this report were written only in the separate work directory.
The orchestrator records the user-approved substitute configuration as GPT-6
Astra / Extra High (`gpt-6-astra`, `xhigh`). This is a separate read-only role,
not evidence of empirical model independence or backend attestation.

## Open finding

**R1 — P2; blocks E1 acceptance: raw runs of at most four still put ink into
the following host text box.**

Location: `src/inspektorium/report/display.py:138-147`; retained raw characters
in `claim_text` feed the ordinary report layout. The implementation follows
the requested four-mark rule and is linear; the counterexample is to the
visual acceptance claim, not to its text implementation.

Every remaining candidate hit is an actual `Answer span` row in the
`E1-answer_claim_below` scenario. The measurement uses grayscale <160 and
**added dark pixels >=10**, with the declared historical two-pixel margin.

| Intensity n | Noto Serif added pixels | GitHub-like added pixels |
|---:|---:|---:|
| 2 | 54 | 30 |
| 3 | 111 | 102 |
| 4 | 155 | 165 |
| 5 | 17 | 15 |
| 6 | 23 | 18 |
| 8 | 17 | below threshold |

For candidate `E1-answer_claim_below-02`, Noto Serif, the original and control
`Answer span: [42:118)` boxes are both x=48, y=1057.75, width=190.1875,
height=22. Of the 54 added pixels, **27 are inside the unpadded rounded box**
(y=1058:15, y=1059:11, y=1060:1). The failure therefore cannot be dismissed
as the two-pixel margin alone. The independent `review-roi-candidate.json`
records these coordinates. The baseline has the same counts at its shifted
vertical position.

Visual inspection of the saved candidate n=4 Noto image confirms intrusion
near the following span text; baseline n=48 clearly reaches failed controls.
The metric detects added ink in a host text box. Neither that metric nor the
n=2 screenshot establishes glyph-stroke occlusion or a measured readability
loss. Candidate failed-guard, reportability and warning rows have zero measured
hits; that improvement does not remove the other declared host-line failures.

Narrow disposition: retain **BLOCKED / Gate R failed**, preserve these cases
and the threshold, and use the existing counterexample to scope any further
display correction. Do not exclude `Answer span`, weaken the threshold or
rename these measured failures as passes. No broader font audit or additional
product change is recommended as part of this completed review.

## Evidence and implementation conclusions

| Item | Review conclusion |
|---|---|
| E1 text/efficiency | PASS: all shared encoders use the bounded lookup; 4/5 boundary, long/mixed/repeated runs, variation selectors and multilingual clean text are covered. All 348 candidate emitted/rendered text checks pass. |
| E1 images | FAIL: 6/75 Noto Serif and 5/75 GitHub-like cases exceed the threshold; 75/75 per setup were measured, zero INVALID. |
| E2 | PASS: shared `@` marker prevents all nine named ordinary/mailto/xmpp cases in relevant fields. No K7 exception; 18 baseline link violations become zero across 348 renderings. Link destinations and visible text are retained. |
| E3 | PASS for the three requested entry paths: `new_venv_target` at `setup_env.py:271-277` rejects existing directories, files and symlinks, including dangling symlinks, before subprocess setup; the deletion calls are removed. |
| Raw contract | All 87 before/after JSON objects and recorded byte hashes match. Only display modules change under `src`; canonicalization, guards, offsets and fingerprints remain untouched. |
| Evidence validity | PASS for the measured records and independent negative controls below; historical numbers and failed development attempts remain separate. |

The independent artifact recount checked **all 600 original PNG hashes** and
recomputed saved per-row pixel differences. It confirmed exact case/renderer
denominators and the reported summaries: baseline 45/75 and 42/75 visual hits,
candidate 6/75 and 5/75. Critical-row hit totals are 17/14 before and 0/0
after. It matched all 19 wheel package files per version to `git show` at
their claimed full commits and to recorded installed-file hashes.

The catalog hash is
`245f945b39168ba0fdb250ebcce633d44fef080d7348738a64672e297e1e8380`;
the measured/reviewed harness hash is
`065559f31627bce79d6b6da4e2def7eb7f33ba0dd1310f727242b9a735324d38`.
The environment is Python 3.11.7 / Unicode 14.0.0, Chromium 156.0.8078.4,
Playwright 1.64.1, Noto Serif/Sans 2.015, viewport 1000x900 at device scale 1.
The CSS and renderer versions are bound in each run manifest. These are local
named configurations, not a GitHub-service or universal font guarantee.

## Reviewer executions and limitations

- Focused pytest, exit 0: **220 passed**. Selected files were
  `tests/test_display_limits.py`, `tests/test_setup_env.py`, and
  `tests/test_render_safety.py::test_display_limits_cover_all_report_contexts_without_changing_raw_values`.
  Command used `dev/bin/python -B -m pytest -p no:cacheprovider`, a work-directory
  `--basetemp`, `-q --tb=short`, `PYTHONDONTWRITEBYTECODE=1`, and a dedicated
  `EVIDENCE_NETGUARD_LOG`. Raw result: `review-focused-tests.log`.
- Independent synthetic measurement controls, exit 0: 0 and 9 added pixels
  are non-overlaps; exactly 10 is an overlap. **14 invalid controls** reject
  missing/corrupt PNGs, missing actual failed/reportability/warning rows even
  in both twins, changed width/height/text/visibility, missing host rows,
  missing headings/payload, and crops outside the image. Result:
  `review-final-validity-results.json`; executed source:
  `review-validity-probes.py --repo <REPO> --work <WORK> --prefix review-final-validity`.
  These controls test the comparison function with synthetic fixtures, not
  a new browser run.
- Independent effective E3 counterexample, exit 0: each of the three baseline
  functions deletes its own newly created disposable sentinel, while each
  candidate function rejects and preserves the exact sentinel. Execution stops
  before any subprocess/install. The 15 focused setup tests also cover clean
  paths with installation mocked. Separately reviewed orchestrator records
  show all three real command rejections with exit 1, preserved sentinel hashes,
  and no setup log; clean setup commands have separate installation logs.
- Independent saved-artifact recount, exit 0:
  `review-bound-artifacts.py --repo <REPO> --work <WORK>`;
  result `review-bound-artifacts-results.json`. This rechecks existing artifacts,
  not a second browser experiment.
- Independent ROI recount, exit 0:
  `review-roi.py --results <WORK>/candidate-results`;
  result `review-roi-candidate.json` (baseline counterpart retained).
- All successful reviewer Python checks used the guarded dev interpreter and
  separate guard logs. An initial attempt using tools-env stopped at import
  with `ModuleNotFoundError: PIL` (exit 1), before any probe; its log is retained.
  Corrected dev execution succeeded. No missing attempt is counted as passed.

The reviewer did not run the mandatory full suite, install or all examples.
The orchestrator subsequently ran the mandatory full checks; the reviewer
read their logs: Ruff passed, mypy found no issues in 19 source files, and
pytest reported **1343 passed**, with **98.04%** coverage. Their recorded
commands exited 0. These engineering results do not remove R1.
The final fresh offline installation and installed-example run was still
running at this review's cutoff and is not approved or counted here; its
actual outcome belongs in the orchestrator's closeout record. No publication
approval is inferred from either focused or overall engineering tests.

## Documentation disposition

The dated addendum correctly records BLOCKED, all current and historical
denominators, the residual cases, measurement limitations and unapproved
publication decisions. The observed P3 changelog hierarchy error was corrected:
the v0.1.1 maintenance follow-up now precedes the v0.1.0 heading.
The requested residual-limit correction is also confirmed: README.md:166,
METHODOLOGY.md:393, CHANGELOG.md:172, SCOPE.md:110 and CLAIMS.md:40 explicitly
record the tested 6/75 and 5/75 failures and Gate R BLOCKED. The current notices
in the historical evidence README/CLOSEOUT and the release-checklist addendum
also identify the blocker. No unresolved documentation finding remains in
this focused review. R1 remains the concrete acceptance blocker.
