# v0.1.1 E1 layout follow-up — 2026-10-24

**READY_FOR_PUBLICATION_REVIEW. Visual Gate R and the mandatory engineering
checks pass for the recorded conditions.**
The four publication decisions remain **PREPARED, not approved**.
No push, PR, merge, tag, release, upload, website change or live provider call.

## Version and bounded change

Started clean at `75ffd03e82a377f07027cfc0b884b454146c0a1e`, previous product
`403bd3fac27f2406a150b2243a691ba4d0b12fbb`. Local branch:
`codex/v0.1.1-e1-layout-20261024`. Measured product:
`5ace2797e4a9075ca53ccd780be616719923c288`.
Package 0.1.1, schema 0.1, license, E2 at-sign marking, E3 setup refusal,
Mn/Me four-character rule, raw values, offsets and fingerprints are unchanged.
Only the Markdown claim layout, its structural tests and five Markdown
expectations changed. Claim text is now a standalone paragraph before the
tight host-control list. Spacing comes from ordinary Markdown block layout;
no test-only CSS or extra invisible spacer was added.

The supplied Eudora review is preserved in `sources/`; its statements about
Eudora's own executions are attributed to that report, not counted as our
new executions. The current checkout and every new result were checked locally.
No Agent Arena work was reopened.

## Measurement result

The catalog is the unchanged sibling `../addendum-20261024/catalog.json`
(version 2026-10-24.1, 75 combining, 9 e-mail, 3 multilingual clean cases).

| Check | Previous product 403bd3f | New product 5ace279 |
|---|---:|---:|
| Noto Serif visual hits / cases | 6/75 | 0/75 |
| GitHub-like visual hits / cases | 5/75 | 0/75 |
| INVALID per style | 0 | 0 |
| Text-rule failures / renderer outputs | 0/348 | 0/348 |
| E-mail link violations / renderer outputs | 0/348 | 0/348 |
| JSON reports preserved byte-for-byte | 87/87 | 87/87 |

Grayscale <160, at least 10 newly dark pixels, the same two-pixel crop margin,
1000x900 viewport, scale 1, Noto Serif/Sans 2.015 and CSS are unchanged.
Python 3.11.7, Unicode 14.0.0, Playwright 1.64.1, Chromium 156.0.8078.4;
renderer/library versions and font hashes are in the run manifest.
The four text configurations are cmark-gfm safe/unsafe, markdown-it-py with
HTML, and Python-Markdown with tables/fenced_code. The two visual styles use
cmark-gfm safe. The control removes only raw Mn/Me from the same report's
payload DOM nodes; host text/offsets stay exact.

The pixel rule detects added ink inside host text boxes. It does not measure
human readability, full glyph occlusion, all fonts/viewers or GitHub's service.
The former n=2 counterexample was not proof of unreadability; that distinction
is retained even though it now passes the declared measurement.

## Mapping and negative controls

The harness changes only the claim selector (LI or standalone P) and a
reviewer-requested finding-row inventory guard. Claim paragraph and list are
siblings, so there is no nested LI/P pair to count twice. Every former host
row, including all Answer span rows, remains measured; payload membership
is not expanded to the following controls. No case, threshold or denominator
was removed or relaxed.

The reviewer discovered that matching Answer span omissions in both DOMs
previously escaped the comparison. The new guard checks both DOMs against
this catalog's fixed three-finding, ten-label inventory. Missing or duplicate
finding headings/labels and host controls misclassified as payload are INVALID.
Existing missing-image, changed-text/box, visibility and critical-warning checks
remain. This inventory is deliberately specific to the frozen catalog.

The old saved baseline/candidate pixels are recounted with the new comparison
instead of regenerating them. Their 45/75 and 42/75 (fae1824), then 6/75 and
5/75 (403bd3f) remain unchanged. `comparison-results.json` records host-row
and raw-JSON identity. The old 70-case catalog and every older result and
inner manifest remain untouched.

The first five-case decision run (n2, n3, n4, claim48 and rationale80) passed
both styles. A preliminary 87-case run also passed before the reviewer found
the inventory weakness; it is retained as a preliminary record. The binding
`layout-final-results` run was repeated once after that concrete correction.
An initial inventory-only command used the system interpreter and stopped at
missing cmarkgfm before measurements; the guarded dev retry succeeded.

## Execution, review and remaining closeout

The changed structural tests pass, including multilingual clean text; the
new two-mark boundary test fails on the old installed product as expected.
The same dependency/font/browser installations were reused. New product and
final verification environments use the already downloaded wheelhouse with
PIP_NO_INDEX=1. No dependency download was required for this follow-up.
The historical setup logger's fixed label mentions download; the captured
commands, PIP_NO_INDEX and local Looking-in-links output establish offline use.

Python .pth socket guards and browser request blocking were active. The
network canary has deliberate refusals and a loopback positive control.
Actual process/request counts are recorded, not assumed. These hooks do not
prove OS-wide network isolation.

One separate reviewer was invoked as the user-approved substitute:
`model="gpt-6-astra"`, `reasoning_effort="xhigh"`, `fork_turns="none"`, role
`e1_layout_review`. It changed no product, documentation or harness files.
This records the tool configuration, not backend attestation or empirical
model independence. There was no recursive delegation or broad audit.

After the separate review, the mandatory checks were run once: **1355
passed, 0 failed, 0 skipped**, **98.04% overall coverage with branch
measurement enabled**; Ruff and mypy exit 0 (19 source files). Fresh offline
installation and `pip check` pass; all 10 installed CLI example reports match
byte-for-byte. The reviewer report retains its earlier cutoff; these final
engineering results belong to this closeout. `results/product-identity.json`
confirms all 59 relevant product files still equal the tested commit after
later documentation/evidence changes. The final documentation commit is Git
HEAD, intentionally not embedded recursively in this report.

The binding run recorded 176 distinct armed Python processes, zero socket
refusals and zero browser requests. The separate canary's deliberate refusals
and loopback control passed; these are recorded counters, not inferred zeros.
The independent reviewer found no remaining E1 blocker, checked all 300 new
PNG hashes and 9,000 host crops, and confirmed all 450 measured Answer span
rows remain included. The 36 invalid variants and one clean control pass.

Reviewer scripts with `.sanitized.txt` replace local workspace bindings and
are explicitly not byte-identical executable originals. Portable root scripts
with `.py.txt` retain their executed bytes. `integrity-manifest.json` lists
all published follow-up files except itself, with SHA-256 and byte lengths.

Next step for Lazaros: review this candidate and explicitly decide the four
[prepared publication points](../DOCUMENTATION_DECISIONS.md). Technical
readiness does not approve those decisions or authorize any public action.

Coverage terminology: 98.04% in the previous closeout was overall coverage
with branch measurement enabled, not a separate pure branch percentage.
The old log and its numeric value are preserved.

See `REPRODUCE.md`, `REVIEW.md`, raw results/logs and `integrity-manifest.json`.
The compact export selects original screenshots; the image inventory lists
all 300 binding PNGs and their hashes. No venvs, caches or private paths are
part of the export.
