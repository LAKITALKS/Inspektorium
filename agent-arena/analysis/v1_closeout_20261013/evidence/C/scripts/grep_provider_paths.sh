#!/bin/bash
# Static grep of provider-reachable code at the committed HEAD tree (git grep HEAD); nothing is executed.
R=__LOCAL_HOME__/Documents/Projects/agent-arena; cd $R
H=$(git rev-parse --short HEAD)
g() { git grep -n "$@" HEAD -- | sed 's/^HEAD://'; }
echo "# Provider-reachable call sites outside agent_arena/providers (git HEAD $H, committed tree via 'git grep HEAD'); static grep only, nothing executed"
echo "# src/ and tests/ have no uncommitted changes: $(git status --porcelain -- src tests | wc -l | tr -d ' ') entries in 'git status --porcelain -- src tests'"
echo
echo "\$ git grep -n -E 'get_provider\(|AnthropicProvider\(|OpenAIProvider\(|OllamaProvider\(|anthropic\.Anthropic\(|LiveAuditProvider\(|\.generate\(|send_prompt\(' HEAD -- 'src/agent_arena/*.py' ':!src/agent_arena/providers/'"
g -E 'get_provider\(|AnthropicProvider\(|OpenAIProvider\(|OllamaProvider\(|anthropic\.Anthropic\(|LiveAuditProvider\(|\.generate\(|send_prompt\(' -- 'src/agent_arena/*.py' ':!src/agent_arena/providers/'
echo
M='src/agent_arena/run_library.py src/agent_arena/phase7a_real_run.py src/agent_arena/bounded_harness_mission.py src/agent_arena/bounded_harness_continuation.py src/agent_arena/judge.py src/agent_arena/prompt_only_baseline.py src/agent_arena/condition_retry.py src/agent_arena/runtime_contract.py src/agent_arena/runner.py'
echo "\$ git grep -n -E '__main__|^def main' HEAD -- <the nine listed modules>"
g -E '__main__|^def main' -- $M
echo
echo "\$ git grep -n -E 'run_judge|run_task\(' HEAD -- src tests"
g -E 'run_judge|run_task\(' -- src tests
echo
echo "\$ git grep -n -E 'from agent_arena(\.| import )(run_library|bounded_harness_mission|bounded_harness_continuation|phase7a_real_run|judge|runner)([^a-z_]|$)' HEAD -- src   (importers)"
g -E 'from agent_arena(\.| import )(run_library|bounded_harness_mission|bounded_harness_continuation|phase7a_real_run|judge|runner)([^a-z_]|$)' -- src
echo
echo "\$ git grep -n -E 'def get_provider|get_provider' HEAD -- src/agent_arena/cli.py src/agent_arena/runner.py src/agent_arena/phase10_cli.py src/agent_arena/phase10_pipeline.py"
g -E 'get_provider' -- src/agent_arena/cli.py src/agent_arena/runner.py src/agent_arena/phase10_cli.py src/agent_arena/phase10_pipeline.py
echo
echo "\$ git grep -n -E 'phase5b-(haiku|sonnet)-full-replication|run_registered_condition|Disabled in v1|disabled in v1' HEAD -- src/agent_arena/cli.py"
g -E 'phase5b-(haiku|sonnet)-full-replication|run_registered_condition|Disabled in v1|disabled in v1' -- src/agent_arena/cli.py
echo
echo "\$ gating anchors: git grep -n -E 'AUTHORIZED_FOR_REAL_EXECUTION|CONSUMED_AFTER|def production_authorization_errors|one-shot execution authorization already consumed|def run_registered_condition|def run_model_batch|preflight NO-GO|resolve_registered_plan|production_authorization_errors|ledger exists|expiry_utc' HEAD -- condition_contract.py phase7a_real_run.py bounded_harness_*.py"
g -E 'AUTHORIZED_FOR_REAL_EXECUTION|CONSUMED_AFTER|def production_authorization_errors|one-shot execution authorization already consumed|def run_registered_condition|def run_model_batch|preflight NO-GO|resolve_registered_plan|production_authorization_errors|ledger exists|expiry_utc' -- src/agent_arena/condition_contract.py src/agent_arena/phase7a_real_run.py src/agent_arena/bounded_harness_mission.py src/agent_arena/bounded_harness_continuation.py | cut -c1-200
echo
echo "\$ AA-P10-LIVE gate anchors: git grep -n -E 'AA-P10-LIVE|class LiveAuditProvider|class LiveSession|BudgetLedger\(' HEAD -- src/agent_arena/phase10_live.py"
g -E 'AA-P10-LIVE|class LiveAuditProvider|class LiveSession|BudgetLedger\(' -- src/agent_arena/phase10_live.py | cut -c1-200
echo
echo "\$ no-call statements: git grep -n -E 'does not implement retries|nothing here|makes \*\*no\*\* model call|REQUIRES_SEPARATELY_REVIEWED' HEAD -- condition_retry.py runtime_contract.py prompt_only_baseline.py"
g -E 'does not implement retries|nothing here|makes \*\*no\*\* model call|REQUIRES_SEPARATELY_REVIEWED' -- src/agent_arena/condition_retry.py src/agent_arena/runtime_contract.py src/agent_arena/prompt_only_baseline.py | cut -c1-200
