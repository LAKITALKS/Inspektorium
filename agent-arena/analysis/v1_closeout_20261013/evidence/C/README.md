# Evidence Area C: v1 entry path (acceptance items C1 and C2)

- **Candidate:** `5560e950af20cee8c35fb2c8e2bfb38807043fab`, HEAD of `c25-p9-conflict/aa-p8-p9-20261011`. This is fd1ad7c plus correction round 1.
- **Supersedes:** this set replaces the earlier area-C evidence of candidate `fd1ad7c`. The old files were deleted from this directory before the new set was written. The new outputs are all from 5560e95, and the bundle manifests bind `5560e950…`.
- **Package:** `agent-arena` 1.0.0, editable install in `.venv`.
- **Tools:** Python 3.11.7, click 8.5.0, pydantic 2.13.4, httpx 0.28.1, pytest 9.0.2, git 2.39.5.
- **Captured:** 2026-10-13.
- **Repository changes:** this run modified, staged or committed no tracked file (see `protected_hashes.txt`). Four tracked documentation files (README.md and three docs) already had uncommitted edits before the run. The `git diff HEAD` hash is identical before and after. `src/` and `tests/` have no uncommitted changes.
- **Network and providers:** nothing contacted a network or a provider. Every process ran under `env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY PYTHONDONTWRITEBYTECODE=1 COLUMNS=100`.
- **Live mode:** no LiveSession was opened. No authorization directory was read, copied or used, because area C needs no replay.

## Results

| Item | Result | Basis |
|---|---|---|
| C1 | **PASS** | **Rejected commands.** `agent-arena run --agents anthropic` and `--agents agents/claude_sonnet.yaml` both exit 2 with the v1 message. Each empty cwd stays empty, and no `runs/` or `reports/` is written. `get_provider` is called 0 times and 0 providers are constructed. `official-release` exits 2 with its message and writes nothing: the output root is never created.<br>**Help.** `run --help` and `official-release --help` now say "Disabled in v1: …". `audit run --help` gives `claude-haiku-5-5@3` as its profile example (not `@1`).<br>**Supported offline path.** It works end to end: validate 0 (`input_valid`), run 0 READY_FOR_RELEASE, inspect 0 READY_FOR_RELEASE, release 0 RELEASED, inspect 0 RELEASED. All 12 controls executed: 11 pass and `search_scope_binding` is not_applicable. Both reports show `open cause` = "no blocking cause recorded". The audit CLI output is pure ASCII JSON.<br>**Tests.** `tests/test_release_boundary.py` 43 passed. `tests/test_v1_entry_point.py` 16 passed, including the new help tests. |
| C2 | **PASS** | There is exactly one canonical v1 path, `agent-arena audit`. The root help says so ("Supported v1 path: 'agent-arena audit'"), and so does README at HEAD (lines 19 and 58-66). `run` and `official-release` are rejected and their own help says so. Every other command is marked `[legacy/diagnostic, not v1]`, `[legacy journal …]` or `[registered historical experiment, not v1]`. The `release_boundary` API stays available for historical verification: 43 tests pass, including `test_public_official_release_cli_is_disabled_in_v1_while_api_still_releases`. The Python modules that can still reach providers directly are classified as historical research paths, with their gates, in `historical_provider_paths.md`. |

Guard counters were 0 for every invocation and for both pytest sessions (`guard_counts.json`). The exception is the canary self-test, which counted each patched path as intended: 1 per network path, 2 `get_provider` and 1 provider construction. All 14 automated checks in `scripts/post_area_c.py` are true (`summary.json` → `checks`).

### Non-blocking observations

1. **The disabled-command help is redundant.** `run --help` and `official-release --help` start with "Disabled in v1: …". They still append the generic addendum "Not the canonical Phase10 path. Diagnostic or legacy Phase7-only artifacts; use 'agent-arena audit' …". This is redundant but not contradictory.
2. **The README fix is not committed yet.** README.md as committed at 5560e95 still describes the old `run`/`official-release` outputs as "diagnostic" and "Phase-7-only" (lines 201-203). The uncommitted working-tree README, which existed before this run and was not touched by it, replaces this with "disabled in v1" (lines 222-230) and adds "The only supported entry point is `agent-arena audit`" (line 14). Both versions document the `audit` commands as the supported path.
3. **Some research paths have no gate.** `python -m agent_arena.run_library`, `runner.run_task` and `judge.run_judge` can still construct a real provider when called directly, without an AA-P10-LIVE gate. `run_library` labels itself a historical research harness in its help. The other two have no caller in `src/` or `tests/`. None of the three is reachable from `agent-arena audit` or produces an AA-P10 bundle.

## Files

| File | Content |
|---|---|
| `README.md` | This file |
| `summary.json` | Machine-readable result per item, statuses, controls, checks, counts and observations |
| `commands.log` | Tab-separated: output name, exit code and the exact command with its cwd. It also records the candidate HEAD and the bundle and release paths |
| `version.txt` | `agent-arena --version` → 1.0.0 |
| `help_root.txt` | `agent-arena --help` |
| `help_audit.txt` | `agent-arena audit --help` |
| `help_audit_{validate,run,inspect,review,release}.txt` | Help for each audit subcommand. `help_audit_run.txt` gives the `claude-haiku-5-5@3` example |
| `help_run.txt`, `help_official_release.txt` | Help for the disabled commands, which say "Disabled in v1" |
| `help_forensic_report.txt` | `forensic-report --help`, marked as not the canonical path |
| `help_run_library.txt` | `python -m agent_arena.run_library --help` |
| `guarded_help_root.txt`, `guarded_help_run_library.txt` | The same help produced through the guard wrapper. It is byte-identical to the console-script output |
| `guard_canary.txt` | Guard self-test invocation. The counts are in `guard_counts.json` → `canary` |
| `run_rejected_anthropic.txt`, `run_rejected_yaml.txt` | Guarded `agent-arena run` from empty cwds: exit 2 and the v1 message |
| `official_release_rejected.txt` | Guarded `official-release --input <dummy> --output-root <scratch>/out --repo-root <repo>`: exit 2 and the message. The dummy input is labelled "SYNTHETIC TEST FIXTURE — not an empirical model response" |
| `postconditions.txt` | The three rejected-command cwds have 0 entries. `official_out` does not exist. Repo `runs/` and `reports/` have 0 files newer than the driver. Also lists the supported-path tree |
| `audit_validate.txt`, `audit_run_offline.txt`, `audit_inspect_candidate.txt`, `audit_release.txt`, `audit_inspect_release.txt` | Supported v1 path outputs and exit codes |
| `supported_path_controls.txt` | For the candidate and the released bundle: control id, execution, outcome, version and release intent, plus the report.md lines "Automatic processing …" and `open cause` |
| `supported_path_bundles.tar.gz` | The candidate and released bundles (decision, manifest, record, report.md, report.html), 10 members. sha256 `30594755…46ac8` |
| `supported_path_bundles.index.json` | Archive SHA-256 and the SHA-256 and size of each member. Each member was checked byte-equal to its source |
| `pytest_test_release_boundary.txt`, `pytest_test_v1_entry_point.txt` | `-rA` pytest output |
| `guard_counts.json` | Refusal counters for every guarded invocation and pytest session, the canary, and the total excluding the canary |
| `provider_paths_grep.txt` | Static `git grep HEAD` of provider call sites, module CLIs, importers, CLI anchors and gate anchors. Nothing from it was executed |
| `historical_provider_paths.md` | Classification of `run_library`, `runner.run_task`, `phase7a_real_run`, `bounded_harness_mission`/`continuation`, `judge`, `prompt_only_baseline`, `condition_retry` and `runtime_contract` as historical, not v1 entry points, with their gates |
| `protected_hashes.txt` | Before and after: sha256 of `analysis/c25_p9_20261011/live_retest/ledger.json` (`ccbbdc4f…2cac`), sha256 of `analysis/live_smoke_20261011/repair_r1/successor_claim.json` (`061c414f…9e94`), the live_retest file count (79), the tracked-change list, the `git diff HEAD` hash and the staged count (0). All unchanged |
| `scripts/guard_cli.py` | The guard wrapper. Before importing the CLI it refuses and counts `socket.socket.connect`/`connect_ex` (except AF_UNIX), `socket.create_connection`, `httpx.Client.send` and `httpx.HTTPTransport.handle_request`. It also replaces `agent_arena.providers.get_provider`, `agent_arena.runner.get_provider`, `agent_arena.cli.get_provider` and the `__init__` of `AnthropicProvider`/`OpenAIProvider`/`OllamaProvider` with refusing counters. It then calls `agent_arena.cli.cli.main(prog_name="agent-arena")` or `run_library.main`. The `canary` target is the self-test |
| `scripts/areac_netguard.py` | Pytest plugin that refuses and counts the same network paths for a whole session |
| `scripts/run_area_c.sh` | Driver that produced every `.txt` output and `commands.log` |
| `scripts/post_area_c.py` | Post-processing: control extract, the 14 checks, guard aggregate, archive and index |
| `scripts/grep_provider_paths.sh` | Produces `provider_paths_grep.txt` |
| `scripts/protected.sh` | Protected-state snapshot used before and after |

## Exact commands

The scratch directory is `S=__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/v1/evidence-C`, and `R` is the repository root. `ENV` is the prefix `env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY PYTHONDONTWRITEBYTECODE=1 COLUMNS=100`. `G` is the guard wrapper, `$R/.venv/bin/python -I -B $S/guard_cli.py <counts.json>`.

The run sequence was:
1. `$S/protected.sh $S/protected_before.txt`
2. `bash $S/run_area_c.sh`
3. `$R/.venv/bin/python -I -B $S/post_area_c.py` (exit 0, all checks true)
4. `$S/grep_provider_paths.sh > provider_paths_grep.txt`
5. `$S/protected.sh $S/protected_after.txt`

Inside the driver:

1. **Guard self-test.** `ENV G $S/counts/canary.json canary`
2. **Help.** Run from an empty cwd:
   - `ENV $R/.venv/bin/agent-arena --help`
   - `audit --help` and `audit {validate,run,inspect,review,release} --help`
   - `run --help`, `official-release --help`, `forensic-report --help`, `--version`
   - `ENV $R/.venv/bin/python -B -m agent_arena.run_library --help`
   - The same root help and run_library help through `G`
3. **Rejected commands.** Each runs from its own new empty cwd:
   - `ENV G … cli run --task $R/examples/phase10/positive-task.json --agents anthropic`
   - `ENV G … cli run --task $R/examples/phase10/positive-task.json --agents $R/agents/claude_sonnet.yaml`
   - `ENV G … cli official-release --input $S/work/dummy_release_input.json --output-root $S/work/official_out/out --repo-root $R`
4. **Supported path.** Run in `$S/work/supported`:
   1. `ENV G … cli audit validate --task $R/examples/phase10/positive-task.json`
   2. `ENV G … cli audit run --offline --task $R/examples/phase10/positive-task.json --recording $R/examples/phase10/positive-recording.json --output-root $S/work/supported/runs`
   3. `ENV G … cli audit inspect --bundle <runs/…>`
   4. `ENV G … cli audit release --bundle <runs/…> --output-root $S/work/supported/release --reviewer area-c-evidence --reason "v1 closeout area C supported-path demonstration (offline recorded example)"`
   5. `ENV G … cli audit inspect --bundle <release/…>`
5. **Tests.** Run in `$R`:
   - `ENV PYTHONPATH=$S/plugins AREAC_NETGUARD_OUT=… $R/.venv/bin/python -B -m pytest -p areac_netguard -p no:cacheprovider --basetemp $S/work/pt_<t> -q -rA tests/<t>.py`
   - This runs for `<t>` in `test_release_boundary` and `test_v1_entry_point`.
