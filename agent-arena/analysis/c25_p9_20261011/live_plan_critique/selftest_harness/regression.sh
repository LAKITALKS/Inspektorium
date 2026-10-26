#!/bin/zsh
# Final offline regression of the live_retest_draft (v3) in throwaway simulation roots; no network, no real key.
OP=__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/selftest_v3
PY=__LOCAL_HOME__/Documents/Projects/agent-arena/.venv/bin/python
cd $OP; unset ANTHROPIC_API_KEY
run() { name=$1; faults=$2; plan=$3; shift 3; echo "######## $name faults=$faults plan=$plan"; rm -rf $OP/$name; zsh scripts/scenario.sh $name "$faults" "$plan" > /dev/null 2>&1; zsh scripts/post.sh $name "$@" > $name/post.log 2>&1; grep -E "^== |^exit=" $name/post.log | paste - - ; $PY scripts/brief.py $name/root | cut -c1-400; }
run r01_normal '{}' '{}' close replay summarize summarize close replay
echo "-- r01 evidence files:"; ls -a r01_normal/root/analysis/c25_p9_20261011/live_retest/evidence | tr '\n' ' '; echo
$PY -c "import json;r=json.load(open('r01_normal/root/analysis/c25_p9_20261011/live_retest/evidence/replay_check.json'));print('replay', {k:r.get(k) for k in ('target','same_as_live','retest_directory_unchanged','blocked_network_attempts','capture_verified','request_identical','installation_inside_repository')})"
run r02_auth401 '{"*": {"status": 401, "type": "authentication_error"}}' '{}' close summarize replay
run r03_529_retries '{"claude-haiku-5-5|LR-03|primary|1": {"status": 529, "type": "overloaded_error"}, "claude-haiku-5-5|LR-03|primary|2": {"status": 529, "type": "overloaded_error"}, "claude-haiku-5-5|LR-01|primary|1": {"status": 529, "type": "overloaded_error"}, "claude-haiku-5-5|LR-02|primary|1": {"raise": "ReadTimeout"}}' '{}' close summarize
run r04_refusal_trunc '{"claude-haiku-5-5|LR-03|primary|1": {"stop_reason": "refusal"}, "claude-haiku-5-5|LR-01|primary|1": {"stop_reason": "max_tokens"}}' '{}' close summarize
run r05_single_evidence '{}' '{"LR-03|primary": "conflict_unknown_host", "LR-03|review": "review_unsupported"}' close summarize
run r06_review_unsent '{"claude-haiku-5-5|LR-03|primary|1": {"usage": {"input_tokens": 9000, "output_tokens": 1478000, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}}}' '{}' close summarize
run r06b_review_529x2 '{"claude-haiku-5-5|LR-03|review|1": {"status": 529, "type": "overloaded_error"}, "claude-haiku-5-5|LR-03|review|2": {"status": 529, "type": "overloaded_error"}}' '{}' close summarize
run r07_mismatch '{}' '{"LR-03|primary": "mismatch_agreed", "LR-01|primary": "mismatch_conflict", "LR-02|primary": "mixed_conflict", "LR-01|review": "conflict2", "LR-02|review": "conflict2"}' close summarize
echo "######## r08 no key -> accepted restart -> refused third start"
rm -rf r08_restart; SIM_NO_ENV_KEY=1 zsh scripts/scenario.sh r08_restart '{}' '{}' > /dev/null 2>&1
(cd r08_restart/root && SIM_ROOT=$PWD ANTHROPIC_API_KEY=sim-placeholder-not-a-key $PY analysis/c25_p9_20261011/live_retest/scripts/run_retest.py 2>/dev/null | head -1 > /dev/null; SIM_ROOT=$PWD ANTHROPIC_API_KEY=sim-placeholder-not-a-key $PY analysis/c25_p9_20261011/live_retest/scripts/run_retest.py 2>&1 | tail -1)
zsh scripts/post.sh r08_restart summarize > r08_restart/post.log 2>&1
$PY -c "import json;s=json.load(open('r08_restart/root/analysis/c25_p9_20261011/live_retest/evidence/retest_summary.json'));print('run', s['run'], 'attempts', s['attempts_total']);[print(' start', x['restart'], x['accepted'], x['precheck_errors']) for x in s['starts']]"
echo "######## r09 runner killed while a request is in flight"
rm -rf r09_killed; SKIP_RUN=1 zsh scripts/scenario.sh r09_killed '{"claude-haiku-5-5|LR-01|primary|1": {"hang": 6}}' '{}' > /dev/null 2>&1
$PY scripts/kill_runner.py $OP/r09_killed/root runner 2>&1 | grep -E "in flight|exit|alive|finished|\"action\"" | cut -c1-200
zsh scripts/post.sh r09_killed summarize > r09_killed/post.log 2>&1; $PY scripts/brief.py r09_killed/root | cut -c1-300
echo "######## r10 close after expiry"
rm -rf r10_expiry; zsh scripts/scenario.sh r10_expiry '{}' '{"LR-03|primary": "supported"}' > /dev/null 2>&1
(cd r10_expiry/root && SIM_ROOT=$PWD SIM_FAKE_NOW=2026-10-16T00:00:00+00:00 $PY $OP/scripts/simwrap.py analysis/c25_p9_20261011/live_retest/scripts/close_retest.py 2>&1 | grep -E '"action"|"authorization_expired"|"ledger_state"|"executable_remaining' )
echo "######## r11 prepare crash (real mode) and (dry run)"
rm -rf r11_crash; SIM_CRASH_EXPOSURE=1 zsh scripts/scenario.sh r11_crash '{}' '{}' > /dev/null 2>&1; $PY -c "import json;print('real-mode crash ->', json.load(open('r11_crash/root/analysis/c25_p9_20261011/live_retest/authorization.json'))['status'])"
rm -rf r11b; SKIP_RUN=1 SKIP_COMMIT=1 zsh scripts/scenario.sh r11b '{}' '{}' > /dev/null 2>&1; (cd r11b/root && SIM_ROOT=$PWD SIM_CRASH_EXPOSURE=1 $PY $OP/scripts/simwrap.py draft/prepare_retest.py $OP/r11b/dry_out > /dev/null 2>&1; $PY -c "import json;print('dry-run crash ->', json.load(open('$OP/r11b/dry_out/authorization.json'))['status'])"; echo "sim -003 claim files: $(ls analysis/live_smoke_20261011/repair_r1 | grep -c successor_claim)")
echo "######## r12 freeze not committed"; rm -rf r12; SKIP_COMMIT=1 zsh scripts/scenario.sh r12 '{}' '{}' 2>&1 | grep precheck_errors | cut -c1-330
echo "######## r13 replay scratch inside the repository"; zsh scripts/post.sh r01_normal replayin:inside 2>&1 | tail -1
echo "######## r14 never started"; rm -rf r14; SKIP_RUN=1 zsh scripts/scenario.sh r14 '{}' '{}' > /dev/null 2>&1; zsh scripts/post.sh r14 summarize close 2>&1 | grep -E '"run"|"action"|"ledger_state"'
echo "######## r15 manifest edited after the freeze commit"; rm -rf r15; SKIP_RUN=1 zsh scripts/scenario.sh r15 '{}' '{}' > /dev/null 2>&1
(cd r15/root && $PY -c "
import json; p='analysis/c25_p9_20261011/live_retest/manifest.json'; m=json.load(open(p)); m['call_plan']['order'].reverse(); open(p,'w').write(json.dumps(m, indent=2, ensure_ascii=False)+'\n')" && SIM_ROOT=$PWD ANTHROPIC_API_KEY=sim-placeholder-not-a-key $PY analysis/c25_p9_20261011/live_retest/scripts/run_retest.py 2>&1 | head -1 | cut -c1-330; echo "ledger exists: $(ls analysis/c25_p9_20261011/live_retest | grep -c ledger)")
