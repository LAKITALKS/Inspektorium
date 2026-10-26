# Area C: Python modules that can still reach a provider when invoked directly

Static classification at candidate `5560e95` (committed tree, `git grep HEAD`). None of these modules was run. The raw grep output and its exact commands are in `provider_paths_grep.txt`, produced by `scripts/grep_provider_paths.sh`. `src/` and `tests/` had no uncommitted changes.

None of these modules is a v1 entry point. The only supported v1 path is `agent-arena audit` (validate, run, inspect, review, release). Its live mode (`audit run --live`, `phase10_live.LiveSession` / `LiveAuditProvider`) is gated by an AA-P10-LIVE/1.0 authorization directory and a live budget ledger (`phase10_live.py:1, 26, 392, 500, 786`). The audit path builds its bundle through `phase10_bundle` → `runner.run_agent(provider, task)` with an injected offline, live or replay provider. It never calls `runner.get_provider`/`run_task`. Of the modules below, only the ledger and atomic-write helpers of `bounded_harness_mission` are reused by `phase10_live`/`phase9_runtime`/`phase10_cli`, and those helpers make no provider call.

| Module | Provider reach when invoked directly | Reachable from the `agent-arena` CLI at 5560e95 | Gate / classification |
|---|---|---|---|
| `agent_arena.run_library` | `_build_provider` → `providers.get_provider(provider, model=...)` (line 544) unless `--fake`. The module CLI (`main`, line 547; `__main__`, line 619) has `--provider` for live runs. | No `agent-arena` command. Module CLI only (`python -m agent_arena.run_library`). `phase7a_execution`/`phase7a_real_run` import `run_single`/`FakeLibraryProvider`, and `packet_integrity`/`provision_dev_manifest` import case discovery. | **Historical research harness, not gated.** The help says: "Historical research harness; not an AA-P10/v1 audit or release. Provider calls are not gated by an AA-P10-LIVE authorization." (`help_run_library.txt`). The working-tree README (uncommitted at capture) says the same. A key holder can run it, and it never produces an AA-P10 bundle. |
| `agent_arena.runner.run_task` | `get_provider(name)` (line 347), then `provider.generate` (line 295) | No longer reachable. `agent-arena run` raises a UsageError before it loads a task or provider (`run_rejected_*.txt`: exit 2, 0 `get_provider` calls, 0 constructions). `git grep 'run_task('` finds no caller in `src/` or `tests/`. | Historical library function, reachable only by a Python import. Not gated. |
| `agent_arena.phase7a_real_run` | `_CaptureProvider(AnthropicProvider(...))` (line 303), `anthropic.Anthropic(...)` for preflight/probe (lines 169, 210). The module CLI `--execute-haiku/--execute-sonnet` → `run_model_batch` (line 1135). | `phase5b-haiku-full-replication` / `phase5b-sonnet-full-replication` → `run_registered_condition` (cli.py:955/958, 983/987). The root help marks both `[registered historical experiment, not v1]`. | **Phase-5A/5B registered-plan authorization.** `run_registered_condition` (line 1108) accepts registered plan IDs only. `condition_contract.production_authorization_errors` (cc:662) requires `AUTHORIZED_FOR_REAL_EXECUTION` (cc:44). A consumed one-shot authorization (`CONSUMED_AFTER_SINGLE_GUARDED_INVOCATION`, cc:46) is refused: "one-shot execution authorization already consumed; second invocation prohibited" (line 787). `run_model_batch` also needs the preflight gate ("preflight NO-GO", line 1189), fresh QA, a credential and an exact model universe. Plan material: `analysis/phase5a_scientific_contract/`, `analysis/phase5b_haiku_full_replication/`, `analysis/phase5b_sonnet_full_replication/`. Historical experiment. |
| `agent_arena.bounded_harness_mission` | `AnthropicProvider(MODEL, ...)` (line 278). Line 119 is the deterministic reproduction under a patched `httpx.Client`. | Only via `phase7a_real_run.run_registered_condition("AA-HARNESS-VALUE-20260913-001", ...)` (no dedicated `agent-arena` command) | **Registered mission plan.** It needs `resolve_registered_plan` and clean `production_authorization_errors` (lines 199-200), an unexpired `expiry_utc` (line 203), a plan unchanged after QA and during execution (lines 215, 275) and a fresh ledger: "ledger exists; no fresh identity/restart" (line 141). Historical measurement adapter. |
| `agent_arena.bounded_harness_continuation` | `AnthropicProvider(MODEL, ...)` (line 174) | Only via `run_registered_condition("AA-HARNESS-VALUE-20260913-001-CONTINUATION-001", ...)` | Same gate family (lines 88-104, 171-172). It also needs a consumed parent authorization and a revoked parent ledger. Historical. |
| `agent_arena.judge` | `run_judge` → `get_provider(provider_name, ...)` + `send_prompt` (lines 91, 102, 109) | No caller in `src/` or `tests/` (`git grep run_judge` finds only the definition) | Optional v0.3 LLM-as-judge library function. Not gated, and dead code for every CLI. It can be reached only by a Python import. Historical. |
| `agent_arena.prompt_only_baseline` | None. It has only the frozen descriptor string at line 383. Line 22: "makes **no** model call". | n/a | Frozen Phase-6.4A baseline definition. Any execution would go through the Phase-5A/7A registered-condition gate above. |
| `agent_arena.condition_retry` | None. Line 3: "This module does not implement retries." | n/a | Retry accounting for the registered Phase-5A schedule (`REQUIRES_SEPARATELY_REVIEWED_BUDGET_AND_EXECUTION_AUTHORIZATION`, line 94). No provider reach. |
| `agent_arena.runtime_contract` | None. It has only the descriptor string at line 50. Line 5: "nothing here" makes a model call. | n/a | Offline Phase-6.2 runtime-contract tooling. No provider reach. |

## Summary

These modules can still construct a real provider when invoked directly:

- `run_library`
- `runner.run_task`
- `phase7a_real_run`
- `bounded_harness_mission`
- `bounded_harness_continuation`
- `judge`

They are classified as historical research paths, not v1 entry points.

- **Not gated:** `run_library`, through its module CLI and labelled historical in its help, and `runner.run_task`/`judge.run_judge`, through a Python import only with no CLI caller. None of the three is reachable from `agent-arena audit` or produces an AA-P10 bundle.
- **Gated:** the `phase7a_real_run`/`bounded_harness_*` paths are reachable from the `agent-arena` CLI only through the two `phase5b-*` commands. Those commands are marked `[registered historical experiment, not v1]` and need a registered, unconsumed real-execution plan authorization.
- **No provider reach:** `prompt_only_baseline`, `condition_retry` and `runtime_contract` hold only descriptor strings or constants.
