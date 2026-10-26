# Evidence A: acceptance items A1–A6 (v1 closeout, 13.10.2026)

Candidate code commit **`5560e95`** (HEAD, branch `c25-p9-conflict/aa-p8-p9-20261011`). This is `fd1ad7c` plus
correction round 1. The canonical CLI is `agent_arena.cli:cli` from the editable install `.venv` (agent-arena 1.0.0,
`src/agent_arena`). Every replay bundle binds the code fingerprint `03984bd436b8…` and the verified source commit
`5560e950af20…`. The acceptance matrix is in [../../CHECKPOINT.md](../../CHECKPOINT.md).

**This set supersedes the evidence for the earlier candidate `fd1ad7c`.** That directory was deleted completely
before this set was written, so every file here was produced against `5560e95`. The scratch outputs of the `fd1ad7c`
run were moved to `<scratch>/_superseded_fd1ad7c/` and are used only for the comparison column
`vs_superseded_fd1ad7c_replay` in `a1_a3_summary.json`.

`<scratch>` in logs and JSON stands for
`__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/v1/evidence-A`.
The scripts in `tools/` keep the full path.

## Safety

- **No provider or network calls.** Every process ran as
  `env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY PYTHONDONTWRITEBYTECODE=1`.
  - Own scripts and the CLI wrapper import `tools/netguard.py` first. It refuses and counts:
    - `httpx.Client.send` and `httpx.AsyncClient.send`
    - `httpx.HTTPTransport.handle_request` and `httpx.AsyncHTTPTransport.handle_async_request`
    - `socket.socket.connect`, `socket.socket.connect_ex` and `socket.create_connection`
  - `httpx.MockTransport` is allowed only inside the A5/A6 demo process, and those sends are counted separately.
  - pytest runs with `-p pytest_netguard_plugin`, which refuses the real transports and sockets. The tests' own
    MockTransport doubles still answer.
  - Refused real network attempts were **0 in every process**. Each log has its own `[netguard]` or
    `[pytest_netguard]` line: replays 3, wrapper inspects 3, archive inspects 3, releases 3, demo 1 plus its 6 CLI children, historical 4+9,
    CLI historical 18 and both pytest runs.
- **Live mode.** No `LiveSession` was opened in live mode on a real authorization directory.
  - Replays used a byte copy of `analysis/c25_p9_20261011/live_retest` at `<scratch>/copy` (79 files). The copy is
    byte-identical after all replays: `logs/copy_tree_initial.sha` was re-diffed with no difference.
  - Live mode ran only on synthetic throwaway authorizations under `<scratch>/a5a6`, built with the helpers in
    `tests/test_phase10_live.py`.
    - Live sessions were opened only for `pred`, `succ1` and `succ2`.
    - A guard in the demo refuses any other directory, and any authorization or predecessor that names
      `live_smoke_20261011` or `c25_p9_20261011`.
  - `KNOWN_CLOSED_AUTHORIZATIONS` was cleared in-process only.
- **Protected files.** [protected_hashes.json](protected_hashes.json) records the state before and after, and
  checks it against `../../hashes_before.json`. Nothing changed:
  - `live_retest/ledger.json`: `ccbbdc4f…`
  - `live_smoke_20261011/repair_r1/successor_claim.json`: `061c414f…`
  - `live_retest`: 79 files, tree hash `8d2480eb…`, the same tree hash as in the superseded evidence
  - git porcelain hash `cf8cb4b1…`, HEAD `5560e95`, 0 staged files, no tracked file changed by this work
  - The four modified tracked docs files (`README.md`, `docs/*`) were already modified before this work.
  - No `.pyc` was written under `src/` or `tests/`.
- **Historical worktree.** The worktree of `558e920` was created at `<scratch>/hist` and removed afterwards with
  `git worktree remove` and `git worktree prune` ([logs/worktree_add.txt](logs/worktree_add.txt),
  [logs/worktree_after_remove.txt](logs/worktree_after_remove.txt)).

Synthetic fixtures (A5/A6 demo) are marked "SYNTHETIC TEST FIXTURE — not an empirical model response".

## Results

| Item | Result | Evidence |
|---|---|---|
| A1 | PASS | Replays of Sonnet LR-02, Sonnet LR-03 and Haiku LR-03 each wrote a complete 5-file bundle: REVIEW_REQUIRED, REVIEW_REQUIRED and ANALYSIS_INCOMPLETE (exit 2 = blocked). `audit inspect` is valid with the recorded status for all three (exit 0), both through the guarded wrapper and through `.venv/bin/agent-arena`. The bundles are also valid after extraction from the archive. Every report shows `scientific judgment \| unknown` and "…not conclusively resolved and is not scientifically released". CLI stdout is pure ASCII (VC-2). [replay_cli.json](replay_cli.json), [logs/inspect_replays.log](logs/inspect_replays.log), [logs/archive_inspect.log](logs/archive_inspect.log) |
| A2 | PASS | The status line is unchanged (`<STATUS> — local artifact status`). MD and HTML both carry the ended sentence (below), including the new immutable-revision clause, and `automatic processing \| ended`. The `open cause` values differ pairwise, and so do the CLI `errors`. The MD Independent-states rows equal the HTML rows. No failing-control reason needed a ⟦U+000A⟧/⟦U+0009⟧ token (none of these ids contains a line break). Supplementary: `tests/test_v1_closeout_report.py` 19/19 passed ([logs/pytest_a2_a4.log](logs/pytest_a2_a4.log)). [a1_a3_summary.json](a1_a3_summary.json) |
| A3 | PASS | Replay vs the live bundle (copy) agree on positions (origin, raw_sha256, forensic_record, full phase8), conflicts, triggers, attempts (incl. packet_sha256 and the exact cap reason), adjudications, Phase-9 scalars and uncertainty count. Only the two normalizations below were applied. The Phase-9 history is also strictly equal to the superseded `fd1ad7c` replay, except the LR-03 trigger representative pair (normalization 2). Correction round 1 therefore changed only display text. [a1_a3_summary.json](a1_a3_summary.json): `history_preserved_vs_live_bundle`, `vs_superseded_fd1ad7c_replay` |
| A4 | PASS | `audit release` on each replay bundle (reviewer `TEST ONLY - not a scientific release`, reason naming the synthetic probe) returned `RELEASE_BLOCKED`, exit 2, `path: null`. Reasons: "Candidate is REVIEW_REQUIRED/ANALYSIS_INCOMPLETE; a current READY_FOR_RELEASE candidate is required." No output root was created, 0 files were written, and the bundle bytes are unchanged. [logs/release_attempts.log](logs/release_attempts.log) |
| A5 | PASS | Existing tests: 13/13 passed ([logs/pytest_a5.log](logs/pytest_a5.log)). Scripted demo ([a5_a6_result.json](a5_a6_result.json)): the first run sent 3 requests to the counting double. Resume, review re-execution, inspect and replay sent none (breakdown below). |
| A6 | PASS | A new synthetic successor authorization `EVIDENCE-A-SYNTH-SUCC-2`, in a new directory with its own Phase-9 state, re-ran the identical input (same `task` object in both records, same case key `p9case:dba573bb…`). It sent 3 counted requests and got status REVIEW_REQUIRED with a valid bundle. It received a new revision id (`49e334b2…` → `b540afdf…`) and a new run id (`78fedda5…` → `705c5a65…`). No block by claim text or case id. |
| Historical verification | PASS (with a setup note) | Under the 558e920 worktree code, copies of all 9 live_retest revisions (6 bundles and 3 released) are valid with their recorded statuses. Under the v1 code (`5560e95`) all 9 are reported invalid (exit 2), and the copies stay byte-identical (45 files). The cause is code identity, shown below. |

### A2: ended sentence (MD = HTML, all three cases)

> Automatic processing has ended. The result is not conclusively resolved and is not scientifically released. No
> human reviewer or review queue is assumed. This revision is immutable: only a recorded human decision (agent-arena
> audit review) or a new, explicitly commissioned run creates a new revision.

### A2: Independent states (MD = HTML)

| Row | Sonnet LR-02 | Sonnet LR-03 | Haiku LR-03 |
|---|---|---|---|
| scientific judgment | unknown | unknown | unknown |
| model judgment (composite) | unsupported | unsupported | Not supplied |
| host evidence derivation (composite) | unknown | unknown | Not supplied |
| review route | UNRESOLVED | HUMAN_REVIEW_REQUIRED | HUMAN_REVIEW_REQUIRED |
| review execution | not_executed | completed | not_executed |
| mandatory review | true | true | true |
| automatic processing | ended | ended | ended |
| analysis execution | completed | completed | incomplete |

### A2: conflict row and open cause per case

| Case | Model/host conflicts row | Open cause |
|---|---|---|
| Sonnet LR-02 | selected judgment: 2 open; mandatory review not executed, release blocked | mandatory review not executed: counterreview denied: Review cap for this model reached (1 counterreview per profile under AA-P10-LIVE-RETEST-20261011-004); the review stays open |
| Sonnet LR-03 | selected judgment: 2 open; mandatory review executed, conflict still open, release blocked; other positions: 4 (open; see review route) | automatic reviews executed (counterreview completed; stability completed); the material conflict or UNKNOWN remains open |
| Haiku LR-03 | not evaluated (analysis technically incomplete) | technically incomplete analysis; no conflict review was run: claim:p1: original span mismatch; claim:p2: original span mismatch |

### A2: CLI `errors` and history closing sentences

| Case | CLI `errors` | History closing sentence |
|---|---|---|
| Sonnet LR-02 | `phase9_history_review: Review open: mandatory review not executed: …` | "No disagreement between positions is recorded. Model/host conflicts are listed under Execution and release. …" |
| Sonnet LR-03 | `phase9_history_review: Review open: automatic reviews executed …` | None. The history lists 24 conflicts, 29 triggers, 2 attempts and 2 adjudications instead. |
| Haiku LR-03 | `analysis_source: Analysis incomplete: claim:p1: original span mismatch; …`, `phase8_semantics_taxonomy: …`, `phase9_history_review: Review open: technically incomplete …`, plus `finding_artifact_binding: Evaluated client_findings` (Observation 1) | "Conflicts were not evaluated: the selected analysis is technically incomplete." |

The live bundles rendered by the old code show the pre-fix wording for comparison (`live_bundle_under_old_code`):

- no "ended" sentence
- "mandatory review pending" in the conflict row
- "none recorded" / "Current assessment contains no recorded conflicts" for LR-02 and Haiku LR-03

Compared with the superseded `fd1ad7c` replay:

- No Independent-states row changed.
- Only the ended sentence changed. It used to read "…No human reviewer or review queue is assumed: this revision
  changes only through a recorded human decision…", and now reads "…This revision is immutable: only a recorded
  human decision … creates a new revision."

### A3: history preserved per case

| Case | Positions (origin, raw_sha256) | Conflicts | Triggers | Attempts (kind/status/reason) | Adjudications |
|---|---|---|---|---|---|
| Sonnet LR-02 | original `ca8c6d0d…` | 0 | 3 | counterreview / denied / cap reason above | 0 |
| Sonnet LR-03 | original `a604745b…`, model_review `a5e4568f…`, stability `1408ca92…` | 24, all `unresolved` | 29 | counterreview / completed; stability / completed | 2, model `considered` |
| Haiku LR-03 | original `ecc05376…` | 0 | 3 | none | 0 |

The mandatory flag (`true`) and the Phase-9 route, review state and execution status are equal to the live bundle in
all three cases.

### A3: normalizations

1. Phase-8 `contract_version` AA-P8/1.2 → AA-P8/1.3, and the same version label inside `reasons[0]`. This is the
   intended v1 contract bump, and the strict comparison differs only in this field.
2. For Sonnet LR-03, the representative position pair of two same-field conflict triggers can differ.
   - Cause: `trigger_id` hashes (anchor position, code, field, pids), and dedup keeps the last conflict in
     `position_id` order. Position ids are run-bound.
   - The underlying conflicts are preserved identically.

### A5: request counts (synthetic, counting MockTransport)

| Step | Requests to the counting double |
|---|---|
| First run (primary, then counterreview completed, then stability completed) | 3 |
| Resume the same run (same authorization, task, profile and state, live mode): PREFLIGHT_BLOCKED "Slot already answered; a completed live slot is never resent" | 0. The authorization dir is byte-identical and no new bundle was written. |
| Direct `execute_review` of counterreview and of stability with the bound record and the same state | 0 and 0. The stored history is returned. |
| `inspect`: 3x via API and 3x via the canonical CLI | 0 network, 0 mock sends |
| Replay from a copy: 3x via API (`provider.network_attempts` 0, raw_sha256 by origin equal to the live run) and 3x via the canonical CLI `audit run --replay` | 0. The copy is byte-identical afterwards. |

Total MockTransport sends in the demo process: 7 = predecessor setup 1 + first run 3 + A6 run 3.

### Historical verification

Setup note: with the `.venv` python and `PYTHONPATH=<worktree>/src` alone, all 9 revisions are invalid
([hist_inspect_558e920_without_version_shim.json](hist_inspect_558e920_without_version_shim.json)).

- Cause: bound provenance contains `package_version` = `importlib.metadata.version("agent-arena")`. The `.venv`
  dist-info says 1.0.0, while the bundles bind 0.1.0.
- With a scratch metadata shim `<scratch>/hist-meta/agent_arena-0.1.0.dist-info` (Version 0.1.0, matching
  `pyproject.toml` at 558e920) also on `PYTHONPATH`, the worktree code fingerprint `a1654da6…` equals the bound one,
  and all 9 revisions are valid with their recorded statuses:
  - API: [hist_inspect_558e920.json](hist_inspect_558e920.json)
  - CLI: [logs/hist_inspect_cli.log](logs/hist_inspect_cli.log), `[hist]` rows, exit 0
  - Statuses: 3 READY_FOR_RELEASE, 1 ANALYSIS_INCOMPLETE and 2 REVIEW_REQUIRED bundles, and 3 RELEASED.

Under v1 `5560e95` all 9 are invalid (exit 2). [hist_inspect_v1.json](hist_inspect_v1.json) shows the inspect
messages, which name symptoms:

- "Stale operational status: expected REVIEW_REQUIRED …"
- "HTML section/order/content parity failed"
- "Host intent cannot waive a blocked control"

[why_not_verifiable_v1.json](why_not_verifiable_v1.json) shows the cause is code identity, not the evidence:

- bound `a1654da6…` vs installed `03984bd4…`
- 14 modules differ
- `provenance` now fails
- the stored AA-P9/1.2 history fails closed: `phase9_history_review` 1.2→1.3, outcome fail
- registry versions changed: `analysis_source` 1.0→1.1, `phase8_semantics_taxonomy` 1.2→1.3

[v1_invalid_history_detail.json](v1_invalid_history_detail.json) shows the effect of VC-4. For the invalid AA-P9/1.2
history, v1 now states the open cause as "review history invalid: Invalid Phase9 history: Selected Phase9 history is
invalid". The constant routing sentence is no longer shown as the cause (Observation 2).

The copies are byte-identical before and after (45 files).

## Observations (not acceptance failures)

1. Haiku LR-03 CLI errors still include the static text `finding_artifact_binding: Evaluated client_findings`.
   - That control was outside the v1 spec (XT-F3 was fixed only for `analysis_source`,
     `phase8_semantics_taxonomy` and `phase9_history_review`).
   - The cause itself is named by those three controls.
2. VC-4 now names a recorded invalid-history reason instead of the routing sentence. However, `_review_cause` picks
   the last `Invalid…` uncertainty entry, which is the generic "Selected Phase9 history is invalid". The more specific
   preceding entry, "Phase9 case/contract binding changed; execution is unverified.", is recorded but not shown as the
   cause.
   - This is visible only when verifying pre-v1 bundles with v1 code, which fails closed anyway.
3. The v1 inspect message after a code change still names symptoms, not the code identity. This is the documented
   residual D7-A; the cause is shown here by `why_not_verifiable_v1.json`.
4. Historical verification needs the matching distribution metadata (0.1.0) as well as the code. A worktree on
   `PYTHONPATH` next to a newer editable install is not enough. Use a clean install of the producing commit, or the
   shim described above.
5. Sonnet LR-03 and Haiku LR-03 keep the Phase-9 `review route HUMAN_REVIEW_REQUIRED` / `review_state pending`
   labels. This is the documented boundary A-D5; the `open cause` row states the actual cause and no human queue is
   assumed.

## Exact commands

All commands ran from `<scratch>` unless stated otherwise. `$PY` = `__LOCAL_HOME__/Documents/Projects/agent-arena/.venv/bin/python`.

1. **Protected state.** [tools/protect.sh](tools/protect.sh), before and after
   (`logs/protected_before.txt`, `logs/protected_after.txt`).
2. **Copy.** `cp -a analysis/c25_p9_20261011/live_retest <scratch>/copy`, then a diff of
   `shasum -a 256` lists: 79 files identical.
3. **A1 replay.** [tools/replay_three.sh](tools/replay_three.sh). For each `(profile, case)` in
   `claude-sonnet-5-5@3 LR-02`, `claude-sonnet-5-5@3 LR-03` and `claude-haiku-5-5@3 LR-03`:

   ```
   env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY PYTHONDONTWRITEBYTECODE=1 $PY tools/aa_cli.py audit run --replay \
     --task <scratch>/copy/tasks/<case>.json --authorization-dir <scratch>/copy --profile <profile> \
     --output-root <scratch>/replay/<slot>
   ```

   `tools/aa_cli.py` imports `netguard`, then calls `agent_arena.cli:cli`, the `agent-arena` entry point.
4. **A1 inspect.** [tools/inspect_replays.sh](tools/inspect_replays.sh) runs
   `tools/aa_cli.py audit inspect --bundle <b>` and `.venv/bin/agent-arena audit inspect --bundle <b>`.
5. **A1–A3 summary.** `$PY -I tools/summarize_a.py <scratch> <scratch>/a1_a3_summary.json`. It only reads files
   and does not import agent_arena.
6. **A4 release.** [tools/release_try.sh](tools/release_try.sh), which runs:

   ```
   tools/aa_cli.py audit release --bundle <b> --output-root <scratch>/release_try/<slot> \
     --reviewer "TEST ONLY - not a scientific release" \
     --reason "SYNTHETIC TEST release probe on scratch replay <slot> (copy of live_retest); expected RELEASE_BLOCKED"
   ```

7. **A5 tests.** [tools/pytest_a5.sh](tools/pytest_a5.sh), run in the repo:

   ```
   $PY -m pytest -p no:cacheprovider -p pytest_netguard_plugin --basetemp <scratch>/pytest-a5 -v
   ```

   On these 13 node ids:
   - `test_L7_*` (3)
   - `test_L8_capture_persisted_before_crash_is_settled_on_resume`
   - `test_crash_between_settlement_and_terminal_is_completed_on_resume`
   - `test_round2_foreign_capture_does_not_settle_and_interrupted_retry_resumes`
   - `test_M2_existing_capture_is_never_overwritten`
   - `test_L1_*` (2)
   - `test_review_cap_decision_is_recorded_before_the_request_and_replayed_exactly`
   - `test_replay_from_a_copy_keeps_a_never_executed_mandatory_review_open`
   - `test_an_interrupted_live_review_replays_as_an_open_review_with_a_bundle`
   - `tests/test_v1_semantics.py::test_a_second_authorization_with_a_shared_review_state_is_refused_before_any_request`

   Supplementary: [tools/pytest_a2_a4.sh](tools/pytest_a2_a4.sh) runs `tests/test_v1_closeout_report.py`.
8. **A5/A6 demo.** `$PY tools/a5_a6_demo.py` (same env). It writes `<scratch>/a5_a6_result.json`, and stderr goes to
   `logs/a5_a6_demo.stderr.log`.
9. **Historical verification.**
   1. `git worktree add --detach <scratch>/hist 558e920`
   2. `cp -a live_retest/{bundles,released} <scratch>/hist-copies`
   3. [tools/hist_run.sh](tools/hist_run.sh) runs `hist_inspect.py` under three settings and then
      `why_not_verifiable.py`:
      - `PYTHONPATH=<scratch>/hist/src:<scratch>/hist-meta`
      - `PYTHONPATH=<scratch>/hist/src`
      - none (v1)
   4. [tools/hist_inspect_cli.sh](tools/hist_inspect_cli.sh) runs CLI inspect, `[hist]` vs `[v1]`.
   5. `tools/v1_invalid_history_detail.py <bundle>` for each of the 9 copies.
   6. `git worktree remove <scratch>/hist && git worktree prune`
10. **Archive.** `$PY -I tools/pack_bundles.py <scratch> <this dir>`. It is deterministic (mtime 0, sorted, PAX), and
    a second pack gave the same SHA-256. [tools/archive_inspect.sh](tools/archive_inspect.sh) extracts the archive to
    scratch and re-inspects: 15 files, 3/3 valid.

## Tool versions

| Tool | Version |
|---|---|
| macOS | 14.6.1 |
| Python | 3.11.7 (`.venv`) |
| agent-arena | 1.0.0 (editable, `5560e95`, fingerprint `03984bd436b852be…`); historical 0.1.0 (`558e920` worktree, `a1654da6…`) |
| httpx | 0.28.1 |
| click | 8.5.0 |
| pydantic | 2.13.4 |
| pytest | 9.0.2 |
| git | 2.39.5 (Apple Git-154) |

## Files

| File | Content |
|---|---|
| `README.md` | This file |
| `protected_hashes.json` | Protected hashes and counts before and after, plus the expected values from `hashes_before.json` (`unchanged: true`, `matches_expected: true`) |
| `replay_cli.json` | CLI JSON (status, path, errors), exit code, ASCII check and netguard counters of the three replays |
| `a1_a3_summary.json` | Per case, from record.json, report.md and report.html: status line, ended sentence (MD and HTML), immutable-clause check, Independent-states rows, MD/HTML parity, history closing sentences, attempts, triggers, positions (origin, raw_sha256), conflict count and resolutions, adjudications, failing controls, comparison with the live bundle (normalized and strict), comparison with the superseded `fd1ad7c` replay, old-code wording of the live bundle, bundle file SHA-256 |
| `replay_bundles.tar.gz` | The three replay bundles (15 files) |
| `replay_bundles.index.json` | Archive SHA-256 (`6e539557…`) and the SHA-256 of each member |
| `a5_a6_result.json` | A5/A6 demo result. Request counts, ids, CLI inspect and replay outputs with counters, live sessions opened (scratch only) |
| `hist_inspect_558e920.json` | 9 revisions under 558e920 code with 0.1.0 metadata: all valid with recorded status |
| `hist_inspect_558e920_without_version_shim.json` | Same, without the metadata shim: all invalid (setup note) |
| `hist_inspect_v1.json` | 9 revisions under v1 `5560e95`: none valid; bound vs installed code identity |
| `why_not_verifiable_v1.json` | Per revision under v1: recomputed status, modules differing from the bound manifest, controls changed vs decision.json with the current reason |
| `v1_invalid_history_detail.json` | Per revision under v1: reconstructed Phase-9 history validation, reasons, uncertainty and the open cause |
| `logs/replay_three.log` | Command log of the three replays |
| `logs/inspect_replays.log` | Inspect via wrapper and via `.venv/bin/agent-arena` |
| `logs/archive_inspect.log` | Inspect of the bundles extracted from the archive |
| `logs/release_attempts.log` | A4 release attempts |
| `logs/pytest_a5.log` | A5 pytest run (13 passed, 0 real network) |
| `logs/pytest_a2_a4.log` | Supplementary `tests/test_v1_closeout_report.py` (19 passed, 0 real network) |
| `logs/a5_a6_demo.stderr.log` | Netguard counters of the demo |
| `logs/hist_inspect_cli.log` | CLI inspect `[hist]` vs `[v1]` for the 9 revisions |
| `logs/hist_netguard.log` | Netguard counters of the historical API runs |
| `logs/copy_tree_initial.sha`, `logs/hist_copies_before.sha` | Per-file SHA-256 of the scratch copies (re-diffed after all runs, unchanged) |
| `logs/protected_before.txt`, `logs/protected_after.txt` | Raw protected-state records |
| `logs/worktree_add.txt`, `logs/worktree_after_remove.txt` | `git worktree` add and list after removal |
| `tools/` | Every script used (`netguard.py`, `aa_cli.py`, `pytest_netguard_plugin.py`, `protect.sh`, `replay_three.sh`, `inspect_replays.sh`, `summarize_a.py`, `release_try.sh`, `pytest_a5.sh`, `pytest_a2_a4.sh`, `a5_a6_demo.py`, `hist_run.sh`, `hist_inspect.py`, `hist_inspect_cli.sh`, `why_not_verifiable.py`, `v1_invalid_history_detail.py`, `pack_bundles.py`, `archive_inspect.sh`) |

The intermediate trees in scratch (`copy/`, `replay/`, `a5a6/`, `hist-copies/`, `hist-meta/`, `pytest-a5/`,
`pytest-a2a4/`, `archive-check/`, `archive-repro/`, `_superseded_fd1ad7c/`) are not durable evidence.
