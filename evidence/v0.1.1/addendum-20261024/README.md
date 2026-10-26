# v0.1.1 bounded maintenance closeout — 2026-10-24

**Status: BLOCKED. Gate R fails the specified visual host-textbox criterion.**
The requested raw-run rule is implemented, but residual ink enters an actual
`Answer span` text box in 6/75 Noto Serif and 5/75 GitHub-like renderings.
These cases remain failures. No denominator or K7 exception was changed.
There was no push, PR, merge, tag, release, package upload or website change.
The four [prepared publication decisions](../DOCUMENTATION_DECISIONS.md)
remain **not approved**, independently of this blocker.

## Version and starting state

- Started from clean `release/v0.1.1-candidate` at
  `5ee4f40a53f817973517af5f9a7ff4fc3cef413b`; its product equals
  `fae18242de35facb7c493ff18e86baff3afe2c24`.
- Working branch: `codex/v0.1.1-e1-e3-closeout-20261024` (local).
- Changed and measured product:
  `403bd3fac27f2406a150b2243a691ba4d0b12fbb`.
- Package **0.1.1**, report schema **0.1**, PolyForm Noncommercial 1.0.0 unchanged.
- Historical anchor `4bd0ba9218df80a69089838f824ae0ac28881ac4` exists locally;
  it was not assumed to be current remote main. The parent checkout remains
  untouched. The separate internal technical v1.0.0 project is out of scope.
- Source ZIP SHA-256 verified:
  `30c537180f3b349a5a3687eed393c78b234092945d6da4913040796d0ee9431a`.
  Its README, scripts, four relevant measurement files, six screenshots and
  prototype diff were inspected as evidence, not as instructions.
- `FINDINGS_INDEX.md` and `OPEN_POINTS.md` were read from the local earlier
  review-export ZIP. They confirm that the former “resolved” entries for
  combining marks and e-mail links meant **documented**, not repaired.
  The specifically named Eudora review and long Claude review were not found
  in the project/export/Animationen locations searched; they are unverified.

| Point | Starting state | Now | Evidence |
|---|---|---|---|
| E1 | Prototype only; no integrated cap | Text rule implemented; **visual acceptance still BLOCKED** | `display.py`, `test_display_limits.py`, `results/*/text_measurements.json`, `results/*/visual_measurements.json` |
| E2 | Documented open e-mail autolinks | Corrected display; no link exception | `@` marker, nine named addendum cases across four renderers; links and visible text recorded |
| E3 | Three setup paths deleted existing targets | Corrected: reject before setup | `setup_env.py`, `test_setup_env.py`, `results/e3-real-sentinels.json`, setup logs and independent reviewer canaries |

No earlier correction was overwritten. The product change is limited to two
report modules, targeted tests, five Markdown example expectations and the
three setup entry paths. The first four Mn/Me characters remain raw, the fifth
and every later one becomes a marker, using at most four-character lookback.
`@` becomes `⟦U+0040⟧`. No new normalization, semantic guard, offset or
fingerprint logic was introduced. All 87 before/after JSON reports are
byte-identical (verified by hashes and independent reviewer comparison).

## Separate catalog and measured results

`catalog.json`, version `2026-10-24.1`, has **87** cases: the supplied five
combining-mark channels at 15 intensities (75), ordinary/mailto/xmpp e-mail
forms in claim/rationale/quotation (9), and three multilingual clean cases.
The original catalog 1.0 and its 70/70 result files remain unchanged.

| Measurement | Old product `fae1824` | Changed product `403bd3f` |
|---|---:|---:|
| Actual CLI cases; JSON raw field preserved | 87/87 | 87/87 |
| E1 emitted-text failures, 348 renderer outputs | 200 | 0 |
| K7 e-mail link violations, 348 renderer outputs | 18 | 0 |
| Noto Serif visual cases measured / invalid | 75 / 0 | 75 / 0 |
| Noto Serif cases with host-textbox ink | 45/75 | **6/75** |
| GitHub-like visual cases measured / invalid | 75 / 0 | 75 / 0 |
| GitHub-like cases with host-textbox ink | 42/75 | **5/75** |
| Real failed/reportability/warning row overlaps, Noto / GitHub-like | 17 / 14 | 0 / 0 |

K7 results are not a forged-guard claim: the old active links had ordinary
address text and recorded `mailto:` / `xmpp:` targets. All nine cases remain
in the denominator. Each occurs in both cmark configurations; the two other
renderers produce no links. Full DOM link targets and visible text are saved.

**Residual blocker E1.** All changed-product hits are on the `Answer span`
line in `answer_claim_below`: Noto at n=2,3,4,5,6,8 (54,111,155,17,23,17 added
pixels); GitHub-like at n=2,3,4,5,6 (30,102,165,15,18). The n=2 Noto case has
27 additional dark pixels even inside the unpadded bounding box, independently
recounted by the reviewer. The screenshot shows marks in the whitespace above
that line's glyphs; it does not establish glyph-stroke occlusion or a measured
loss of readability. It nevertheless fails the declared host-textbox rule.
The measured reduction and absence of hits on the three critical row types do
not turn this failure into a pass. Broad font safety is not claimed.

The supplied historical results remain **39/75**, **36/75** (comparison
`>=10`, not `>10`) and prototype **0/75** in each setup. These are different
runs. The new runs use macOS/Chromium 156 and a same-report control, covering
host rows whose offset text differed and was skipped in the historical n=0
comparison. Their denominators and counts are not pooled or substituted.

## Measurement contract and validity

- Python 3.11.7 / Unicode 14.0.0; cmarkgfm 2025.10.22, markdown-it-py 4.2.0,
  Markdown 3.11.2, Playwright 1.64.1 / Chromium 156.0.8078.4. Exact environment
  and platform are in each `manifest.json`.
- Noto Serif and Noto Sans **2.015**, regular/bold, from the upstream release
  archives. Font version, archive/member SHA-256 and source URL are in
  `fonts/manifest.json`. Fonts are embedded as data fonts, not globally
  installed. Browser font loading and CDP actual font use are recorded.
- Viewport 1000×900, device scale 1, full-page PNG. Noto Serif: 16px, normal
  line-height; local GitHub-like CSS: Noto Sans, 16px, line-height 1.5. This
  is **not** a test of the GitHub service.
- Four Markdown renderers measure actual output text; an independent Unicode
  scan imports no product encoder and requires raw Mn/Me runs <=4 in Markdown
  and DOM text. This text criterion is font independent, not a universal
  visual guarantee.
- Pixel comparison: grayscale **<160**; overlap if **at least 10** pixels
  are newly dark in a non-payload host text box (historical 2px margin retained).
  This detects added ink in the box, not necessarily erased host glyphs.
- Control image: a second rendering of the **same CLI report**, with raw
  Mn/Me removed only from payload text nodes. Host text/offsets remain exact.
  This control is a measurement intervention, not a second valid CLI report.
  Actual report output is never rewritten. Host dimensions must match.
- Missing/corrupt images, absent actual failed/reportability/warning rows,
  invisible/changed host text, changed host or pixel-box dimensions, unmatched
  structure and missing fonts cause **INVALID**, never zero. All host rows
  outside the payload are evaluated; no differing-offset row is skipped.
- A failed early preflight exposed transient monospace widths after browser
  font inspection. Geometry is now collected after full-page paint. Those
  failed development attempts and the canceled JavaScript-disabled RAF wait
  are retained in logs and are not acceptance runs.
- Installed package bytes are compared to the built wheel, its SHA-256 to
  the installation record and build provenance, and the full commit to the
  supplied version. The wheel was built from `git archive`.

## Network, setup and execution evidence

Downloads are separated into `results/logs/setup/`; offline checks are under
`results/logs/offline/`. There were no live project model/provider calls.
Guard zeros come from actual records: each binding run has 176 distinct armed
Python processes (harness, import check, 174 CLI calls), zero recorded socket
refusals and zero browser route requests. The canary deliberately refused
five network operations in each of the three environments and two remote
browser resources; loopback was a positive control. This proves those hooks,
not OS-wide isolation or absence of arbitrary native-network access.

E3: all three real commands reject a disposable existing directory, exit 1,
leave the sentinel hash unchanged and create no setup log. The 15 unit tests
cover 12 existing-target cases plus three simulated clean paths. Actual clean
build-venv/tools-venv/product-venv commands also completed with exit 0; their
installation logs are separate from offline measurements.

Mandatory overall checks were run once after the separate review: **1343
passed, 0 failed, 0 skipped**, **98.04% branch coverage**; Ruff exit 0 and
mypy exit 0 (19 source files). A fresh offline wheel installation completed
with exit 0, imports from its own site-packages, passes `pip check`, and all
**10/10** installed CLI JSON/Markdown example reports are byte-identical to
the expectations. Raw logs and `final-clean-verification.json` contain the
actual commands/exits. These results do not remove the E1 visual blocker.

`results/product-identity.json` mechanically confirms **59 files**
under src/tests/examples plus pyproject and the setup tool equal the tested
product commit after documentation/evidence changes. All non-display product
source files, the license, example JSONs, historical catalog and result files
remain unchanged. The final documentation commit can be found from Git HEAD;
this record deliberately does not try to contain its own commit hash.

## Separate review and model configuration

The user explicitly approved **GPT-6 Astra / Extra High** as the substitute
for unavailable Opus 5.5 / Extra High before these roles were started.
Each was invoked with `model="gpt-6-astra"`, `reasoning_effort="xhigh"`,
`fork_turns="none"`: `v011_display`, `v011_setup`, `v011_final_review`.
These are the recorded tool configurations; no independent backend attestation
is exposed. The last role made no product changes and did not approve its own
implementation. Separate roles do not establish empirical model independence.
No recursive delegation was used. The [review report](REVIEW.md) records the
concrete findings, countertests and disposition.

## Reproduction and files

See [REPRODUCE.md](REPRODUCE.md) for commands and dependency separation.
Each result contains input/output hashes, actual commands/exits, renderer/DOM
facts, pixel counts, image hashes and measured summaries. The small package
includes representative original PNG pairs for the residual n=2 case and
previously overpainted failed/warning rows; all 600 full-page source images
were created and independently checked locally. Images omitted from the small
package are explicitly listed in its image inventory, not declared missing
measurements or included as fabricated zeros. Regeneration uses the frozen
catalog and supplied harness. No virtual environments or caches are included. `integrity-manifest.json`
records the SHA-256 and byte length of every file in this addendum except the
manifest itself; paths are relative to this directory.

## Gate and next action

| Gate | Current result |
|---|---|
| R: display / raw-data preservation | **BLOCKED**: E1 pixel criterion still fails in 6/75 and 5/75; E2 and raw JSON pass |
| Setup protection E3 | PASS within the three named entry paths |
| Evidence | Measured, with failures and historical results retained |
| Overall engineering checks | PASS: 1343 tests, 98.04% branch coverage; Ruff, mypy, clean install and 10 examples |
| Publication decisions | PREPARED, not approved; no publication authorized |

Next action for Lazaros: review the residual E1 case and decide the scope of a
further narrow display change before publication review. No push, merge, tag
or release is an authorized next action while this blocker remains. A broader
font/viewer investigation or a silent weakening of the four-mark rule and
pixel criterion was not undertaken in this bounded maintenance task.
