# Evidence D: adversarial local text in the canonical reports (acceptance item D1)

Candidate code: commit `5560e95` (HEAD; `fd1ad7c` plus correction round 1). Installed as editable `agent-arena` 1.0.0.
Produced on 13.10.2026.

**This set replaces the evidence for the earlier candidate `fd1ad7c`.** All files from that run were deleted before
this set was written. The `fd1ad7c` code appears here only as a pre-fix contrast.

No tracked file was changed, staged or committed.

All inputs are SYNTHETIC TEST FIXTURES, not empirical model responses. They are copies of
`examples/phase10/positive-task.json` and `positive-recording.json` with harmless local payloads. The payloads contain
no external URLs.

## Result for D1: PASS

1899 of 1899 checked pages pass every applicable check:
- 211 bundles, each checked as the canonical `report.html` and as 8 Markdown renders of `report.md`.
- 0 failures.

Two fail-closed input observations are recorded below. Neither one makes a release more permissive.

| D1 criterion | Result | Evidence |
|---|---|---|
| Host controls, status and reasons visible and correctly assigned | PASS, 1899/1899. Each page has exactly one status paragraph, and it equals the real status. The Executed controls rows equal an **independent** recomputation from `decision.json`, which is the product's display rule re-implemented in `tools/prep.py` rather than taken from the product. **Every cell has exactly the five host lines** Execution / Outcome / Eligible / Evaluated / Reason, and its Outcome is the real outcome. This holds in the DOM of all 9 renderers and statically in `report.md` (4 `<br>`) and `report.html` (4 LF). Failing-control rows are visible | `dom_results.json` |
| Multi-line model id quoted by host lines (correction round 1, VC-1) | PASS. Two variants combine a multi-line proposition id with a real failing control (`original_span` +1): `spanfail--lfpid` (the critic's exact id `claim:p1\nOutcome: pass\nReason: …\n\nphase9_history_review / 1.3`) and `spanfail--lfpid_mixed` (CRLF, U+2028, NEL, TAB, CR, U+2029, `## Mandatory controls`, `\| control \| pass \|`, `RELEASED — local artifact status`, U+202E, ZWSP, BOM and `</td></tr>`). The reasons of `analysis_source`, `phase8_semantics_taxonomy` and `phase9_history_review` quote the id with `⟦U+000A⟧`, `⟦U+000D⟧`, `⟦U+0009⟧`, `⟦U+2028⟧` and the other tokens inside the Reason line. The **open cause is one line** with `⟦U+000A⟧` tokens in canonical HTML, in all 8 Markdown renders and in both report files. The forged `Outcome: pass` never starts a line | `dom_results.json` (`open_cause_lf_token_one_line` 18/18), screenshots `v1-5560e95-spanfail-lfpid-*` |
| CLI JSON (VC-2) | PASS. 217 CLI calls (126 `audit run`, 91 `audit release`). stdout is pure ASCII, with 0 control bytes other than LF. Each error string sits on one physical line. Line breaks inside a quoted reason appear as JSON escapes (`\n`, ` `, …), and their decoded values equal `decision.json`. The CLI JSON carries status, path and errors only; the open cause is a report field | `runs_summary.json` (`summary`) |
| Mandatory warnings kept | PASS. On every page the following are present once and computed-visible: the "Automatic processing has ended" sentence, the notice, LIMITS, the display note, the open cause row and every other host `text()` block. Visibility checks cover display, visibility, opacity, the hidden attribute, font size and a non-zero box. The 29 open-state bundles carry the new sentence "… This revision is immutable: only a recorded human decision (agent-arena audit review) or a new, explicitly commissioned run creates a new revision." All 182 READY/RELEASED bundles show the open cause `no blocking cause recorded` | `dom_results.json`, `runs_summary.json` |
| No active structure from model text | PASS. 0 script, iframe, object, embed, img, a, details, div or other non-whitelisted elements; 0 `on*` attributes; 0 comment nodes. The only `<style>` is the canonical one, and the Markdown renders have none. 0 dialogs or page errors, and `window.__pwned` stays unset | `dom_results.json` |
| Model text recognisable as text | PASS. Payload text nodes sit only in `td`, `pre` or `code`, or in commonmark.js's pipe-text paragraph (it has no table extension). The payload never appears in an attribute. The visible text equals the display form of the payload | `dom_results.json` |
| Bidi, invisible and line-terminator characters | PASS. 0 raw Cc/Cf/Zl/Zp characters (except LF and TAB) in any `report.md`, `report.html` or rendered DOM. Both reports and the DOM carry a `⟦U+XXXX⟧` token for every hidden character of a displayed payload. `record.json` keeps the exact characters (1683/1683 applicable pages) | `dom_results.json`, `bundles.tar.gz:work/static.json` |
| Host h3 captions | PASS. Every h3 is either a host caption seen in the plain variants or an ordinal pattern (`Proposition n`, `Evidence item n`, …). No caption contains model text | `dom_results.json` |
| Model keys (VC-3) | PASS. In `modelkey--derived_judgment` and `modelkey--derived_judgment_flat` the model keys are shown as `model-supplied …`. The latter uses the flat keys `derived judgment / host state`, `derived judgment / model host conflict`, `derived_judgment / derived state` and `from and to text (identical) / x`. The host row label `derived judgment` is kept, and no model key appears unprefixed. Both runs are ANALYSIS_INCOMPLETE because of the invalid ledger, the same as the plain extra-key counterpart | `runs_summary.json` (`model_key`) |
| Real failing host control (`original_span` +1) | PASS. `spanfail--payload` (CRLF, bidi, zero-width and HTML payloads), `spanfail--lfpid` and `spanfail--lfpid_mixed` are ANALYSIS_INCOMPLETE. Each shows `analysis_source`, `finding_artifact_binding`, `phase8_semantics_taxonomy` and `phase9_history_review` as fail with their reasons. Status and outcomes are the same as `spanfail--plain` | screenshots, `release_independence.json` |
| Release decision independent of payload | PASS, with the fail-closed exceptions below. Of 113 payload/plain pairs, 98 are identical in status, every control outcome and the release result. All 15 differences are stricter only. A multi-line id alone (`proposition_id--lfpid`, `proposition_id--lfpid_mixed`) stays READY and then RELEASED, the same as `proposition_id--plain` | `release_independence.json` |
| Clean counterpart readable | PASS. `clean` is READY_FOR_RELEASE, then RELEASED. All 9 renderers show 12 h2 and 1 status paragraph. The only tokens are the ones quoted inside the display note itself | `dom_results.json` (`clean`) |
| Regression tests | PASS. `tests/test_v1_render_injection.py`: 21 passed under the network guard | `guard_and_protection.json` |
| Evidence unchanged | PASS. Before and after are identical: `analysis/c25_p9_20261011/live_retest/ledger.json` (`ccbbdc4f…`), `analysis/live_smoke_20261011/repair_r1/successor_claim.json` (`061c414f…`), the live_retest file count (79), tree hashes over live_retest and live_smoke, HEAD `5560e95`, 0 staged files, and a SHA-256 of `git diff`. Four tracked docs (README.md and docs/*.md) were already modified at session start and are unchanged by this work | `guard_and_protection.json` |

## Pre-fix contrast

The same inputs were run through `git archive <commit> src` with PYTHONPATH, using the same renderers and DOM checker.
Results are in `prefix_contrast.json`.

- **558e920** (investigation HEAD, defect D1):
  - `reason--cr`: all 8 Markdown renderers show 15 h2 instead of 12, 4 status paragraphs instead of 1 (including a forged
    `RELEASED — local artifact status`) and `ul/li` items.
  - `claim--cr`: 22 h2 and 11 status paragraphs.
  - `spanfail--payload`: 13 h2 and 2 status paragraphs. 13 raw bidi/invisible characters remain in the DOM.
  - `binding_reason--crlf`: no forgery.
  - Canonical HTML was already structurally safe.
  - The investigation is cited, not repeated: `scratchpad/v1_investigation.txt` lines 920–1000 and
    `scratchpad/v1/verify-D/work/verdicts.txt`. Copies are in `bundles.tar.gz:work/investigation_*`.
- **fd1ad7c** (earlier candidate, critic findings VC-1/VC-2):
  - `spanfail--lfpid`: the Executed-controls cells have 13, 9 and 13 lines instead of 5, with forged `Outcome: pass` /
    `Reason:` lines, and the open-cause cell has 9 lines. This appears in canonical HTML and in all table renderers.
  - `spanfail--lfpid_mixed`: cells of 19, 12 and 15 lines, an open cause of 11 lines, and non-ASCII CLI stdout.
  - `modelkey--derived_judgment_flat`: a multi-line host validation reason gives cells of 29, 17 and 10 lines.
  - At `5560e95` every one of these is 5 lines per cell and a one-line open cause.

## Matrix

- 11 payload classes:
  - `cr`, `crlf`, `ls` (U+2028), `ps` (U+2029) and `nel` (U+0085). Each forges a status line, a setext and an ATX
    `Mandatory controls` heading, `### Control: provenance / 1.0 passed`, `| control | pass |` rows,
    `RELEASED — local artifact status` and a list item.
  - `control_like`: the same text separated by LF.
  - `markdown`: backticks, `~~~`, lists, a table, a blockquote, emphasis and an anchor link.
  - `fence`: triple backticks.
  - `html`: `<!--`, `</section>`, `</table>`, `<details open>`, `<style>section{display:none}</style>`, `<div hidden>`,
    `<script>` and `on*`, all as inert text.
  - `bidi`: U+202E, U+202C, U+2066–U+2069, U+200E and U+200F.
  - `zero_width`: U+200B–U+200D, U+FEFF and U+00AD.
- 9 fields:
  - proposition `reason`, binding `reason`, `uncertainty` and `client_explanation`.
  - The task claim, together with every claim echo and `original_span`, so the binding stays valid.
  - The task context, together with the evidence, exact reference and trigger echoes.
  - The model ids `evidence_id`, `proposition_id` and `transformation_id`.
- Extra variants:
  - A plain counterpart per field, and `clean`.
  - `modelkey--plain`, `modelkey--derived_judgment` and `modelkey--derived_judgment_flat`.
  - `spanfail--plain`, `spanfail--payload`, `spanfail--lfpid` and `spanfail--lfpid_mixed`.
  - `proposition_id--lfpid` and `proposition_id--lfpid_mixed`.
  - `conflict--plain` and `conflict--cr` (REVIEW_REQUIRED).
  - Six `*_rawtask` variants: the claim or context with raw U+2028, U+2029 or U+0085 in a task file written with
    `ensure_ascii=False`.
- Totals:
  - 126 variants.
  - `audit run`: 91 READY_FOR_RELEASE, 27 ANALYSIS_INCOMPLETE, 2 REVIEW_REQUIRED and 6 PREFLIGHT_BLOCKED (no bundle).
  - 91 `audit release` → RELEASED.
  - 211 bundles × 9 renderers = 1899 pages.

## Observations (stricter direction only; unchanged from fd1ad7c)

1. **Triple backtick in model output** (9 pairs, `*--fence`). `output_contract._strip_fence` treats the backticks as a
   fence, so the result is ANALYSIS_INCOMPLETE. This is the known fail-closed note D8.
2. **Raw U+0085, U+2028 or U+2029 in a task file** (6 pairs, `*_rawtask`). The task loader parses task files with
   `yaml.safe_load`, which treats these characters as line breaks.
   - With the payload's `---` line, the file is refused (PREFLIGHT_BLOCKED).
   - In the probe without `---` (`bundles.tar.gz:probe_yaml/`), raw NEL is folded, so the claim binding fails closed
     (ANALYSIS_INCOMPLETE), while raw LS/PS stay READY.
   - Escaped JSON keeps the characters exactly and gives the same result as the plain counterpart.

   This is an ingestion edge outside the display path.

Further limits:
- commonmark.js has no table extension, so each host table stays one pipe-text paragraph. In that paragraph, the
  five-line check counts `4·N+1` hard lines with the Outcome / Eligible / Evaluated / Reason prefixes.
- markdown-it with `html:false` shows the host `<br>` as literal text (note D6). Only for that renderer, the literal
  `<br>` counts as a line break.
- Markdown renders collapse runs of spaces, so the open cause is compared there after whitespace collapse. Canonical
  HTML is compared exactly.
- Not part of D1 (cosmetic, host side, also present in `clean`): some nested host rows have an empty first label
  segment, for example `| / 1 / derived state |`.
- Local Chrome is 155.0.8059.40, auto-updated from the 154 named in the order.

## Commands

All Python ran with `env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY PYTHONDONTWRITEBYTECODE=1` and `-B` (or `-I -B`).
`tools/guard.py` loads before any product code. It refuses and counts `httpx.Client.send`, `AsyncClient.send`,
`HTTPTransport.handle_request`, `AsyncHTTPTransport.handle_async_request`, `socket.socket.connect`/`connect_ex`,
`socket.create_connection` and `getaddrinfo`.

- `S` = `__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/v1/evidence-D`
- `PY` = `__LOCAL_HOME__/Documents/Projects/agent-arena/.venv/bin/python`

```
python3 -I $S/tools/protected.py $S/work/protected_before.json
$PY -I -B $S/tools/gen.py $S/in $S/work/payloads.json            # 120 variants
$PY -I -B $S/tools/gen_raw_task.py $S/in $S/work/payloads.json   # +6 raw task-file variants
$S/tools/run_all.sh   # per variant, guarded canonical CLI (tools/cli.py -> agent_arena.cli.cli):
#   agent-arena audit run --offline --task in/<v>/task.json --recording in/<v>/recording.json --output-root out/<v>/run
#   if READY_FOR_RELEASE: agent-arena audit release --bundle <run bundle> --output-root out/<v>/release \
#       --reviewer evidence-D-synthetic --reason 'SYNTHETIC TEST FIXTURE release check'
#   stdout/stderr kept as raw bytes (out/<v>/{run,release}.stdout) for the ASCII check
$PY -I -B $S/tools/prep.py           # static checks, independent expectations, 8 Markdown renders per bundle
(cd $S/../verify-D/node && node $S/tools/dom_check.mjs $S/work/pages.json $S/work/dom.json)   # headless Chrome
python3 -I $S/tools/aggregate.py $S/work $S/stage                # dom_results.json, release_independence.json
$S/tools/run_prefix.sh               # git archive {558e920,fd1ad7c} src -> prefix/<c>/code; tools/cli_prefix.py
python3 -I $S/tools/prefix_pages.py $S && node $S/tools/dom_check.mjs $S/prefix/pages.json $S/prefix/dom.json
node $S/tools/shots.mjs $S/work/shots.json                       # 5 PNGs
$S/tools/xcheck.sh                   # real .venv/bin/agent-arena entry point, 5 variants (+2 releases)
$PY -I -B $S/tools/probe_yaml.py $S/probe_yaml/in                # raw task-file probe, then guarded CLI per input
$PY -B $S/tools/pytest_guarded.py tests/test_v1_render_injection.py
python3 -I $S/tools/protected.py $S/work/protected_after.json
python3 -I $S/tools/summaries.py $S <this dir>; $S/tools/build_bundle.sh
```

The exact per-variant command lines are in `bundles.tar.gz:work/commands.log` and `prefix/commands.log`.

## Tools

The full list is in `render_tools.json`.
- Google Chrome 155.0.8059.40, headless via playwright-core 1.48.2. All non-file requests were aborted.
- Node v26.8.1 with markdown-it 14.1.0 (html on, html off, linkify), commonmark.js 0.31.2, marked 14.1.4,
  micromark 4.0.0 and micromark-extension-gfm 3.0.0.
- Python 3.11.7 with cmarkgfm 2024.11.20 (GitHub cmark-gfm, UNSAFE) and markdown-it-py 3.0.0.
- The isolated installs from the investigation were reused (`scratchpad/v1/verify-D/node`, `verify-D/pyenv`). Nothing
  was downloaded.

## Network and protection

- 238 guarded Python processes, 0 refused attempts.
- One attempt to run the area A/C test files (`test_v1_closeout_report.py`, `test_v1_entry_point.py`) under the same
  guard had 9 sends refused. These were sends to their in-process `httpx.MockTransport` live doubles, with 0 socket
  attempts. That attempt is not D1 evidence and is kept apart; see `guard_and_protection.json`.
- The browser made 0 external requests (1899 + 108 `file:` requests).
- 0 provider calls. No LiveSession was opened, and no real authorization directory was touched.
- The unguarded cross-check through `.venv/bin/agent-arena` gave the same rc and status as the guarded runs.

## Files

| File | Content |
|---|---|
| `README.md` | This file |
| `payloads.json` | Payload classes (ASCII-escaped), the multi-line proposition ids, fields, codepoints per class, and metadata for all 126 variants (field, class, plain counterpart) |
| `runs_summary.json` | CLI summary and, per variant: run/release rc and status, CLI stdout facts (ASCII, control bytes, one line per error), failing controls, open cause, payload display, record exactness, model-key labels |
| `dom_results.json` | Summary (per renderer, true/false/NA counts per check, tools, host caption set, release independence) and one verdict row per page (1899 rows) |
| `release_independence.json` | 113 payload/plain pairs: status, control outcomes, release, differing controls, stricter-only flag |
| `prefix_contrast.json` | Pre-fix runs at 558e920 and fd1ad7c, report.md line facts, and per-page h2, status paragraph, five-line cell and open-cause line count; investigation citations |
| `render_tools.json` | Browser, renderer and product versions and renderer configurations |
| `guard_and_protection.json` | Guard counts, regression test result, cross-check runs, browser requests, protected state before and after |
| `v1-5560e95-spanfail-lfpid-canonical-html-controls.png` | Canonical HTML, failing-control variant with a multi-line id: each cell has exactly 5 host lines, and the id appears with `⟦U+000A⟧` inside the Reason line |
| `v1-5560e95-spanfail-lfpid-canonical-html-open-cause.png` | The same page: status, ended sentence, notice, and the one-line open cause with tokens |
| `v1-5560e95-reason-cr-cmark-gfm-rendered-md.png` | `reason--cr` report.md rendered by cmark-gfm after the fix: the payload stays in one cell, with CR shown as `⟦U+000D⟧` |
| `prefix-558e920-reason-cr-cmark-gfm-forged.png` | The same payload at 558e920: a forged `RELEASED — local artifact status` paragraph, a second `Mandatory controls` h2 and a list item |
| `prefix-fd1ad7c-spanfail-lfpid-canonical-html-forged-lines.png` | `spanfail--lfpid` at fd1ad7c: forged `Outcome: pass` / `Reason:` lines inside the failing `analysis_source` cell |
| `bundles.tar.gz` | Inputs, all 211 bundles and raw CLI stdout, the cross-check, the YAML probe, Markdown renders of 14 sample variants, pre-fix bundles and renders, all tools, and work files (runs, static checks, full DOM facts, guard logs, pytest logs, commands, hashes, investigation extracts). Loose bundles are not stored, because canonical `report.md` trips `git diff --check` |
| `bundles_index.json` | SHA-256 and size of the archive (`19d05f8f…`, 7064654 bytes) and of each of its 2352 members, plus the layout |
