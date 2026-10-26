#!/bin/zsh
# Each probe: fresh root, prepare (unchanged), one tamper, unchanged runner; expect pre-check refusal, zero requests.
set -u
OP=__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/critic_live2/operational
PY=__LOCAL_HOME__/Documents/Projects/agent-arena/.venv/bin/python
export PYTHONDONTWRITEBYTECODE=1
unset ANTHROPIC_API_KEY
GIT=(git -c user.name=critic-sim -c user.email=critic-sim@example.invalid -c commit.gpgsign=false)
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
for probe in src_dirty src_committed task_changed script_changed expectations_changed auth_changed foreign_claim; do
  SKIP_RUN=1 $OP/scripts/scenario.sh p_$probe > /dev/null 2>&1 || { echo "setup failed $probe"; continue; }
  R=$OP/p_$probe/root
  T=$R/analysis/c25_p9_20261011/live_retest
  cd $R
  case $probe in
    src_dirty) echo "# edit" >> src/marker.py ;;
    src_committed) echo "# edit" >> src/marker.py; $GIT add src/marker.py; $GIT commit -q -m "post-freeze src change" ;;
    task_changed) sed -i '' 's/twelve months/12 months/' $T/tasks/LR-01.json ;;
    script_changed) echo "# tamper" >> $T/scripts/summarize_retest.py ;;
    expectations_changed) sed -i '' 's/"conservative": \[\]/"conservative": ["supported"]/' $T/expectations.json ;;
    auth_changed) sed -i '' 's/"max_technical_retries": 2/"max_technical_retries": 3/' $T/authorization.json ;;
    foreign_claim) print -r -- '{"schema": "aa-p10-live-successor-claim/1.0", "predecessor_authorization_id": "AA-P10-LIVE-SMOKE-20261011-003", "successor_authorization_id": "OTHER", "successor_canonical_directory": "/elsewhere", "successor_authorization_sha256": "00"}' > analysis/live_smoke_20261011/repair_r1/successor_claim.json ;;
  esac
  $PY analysis/c25_p9_20261011/live_retest/scripts/run_retest.py > $OP/p_$probe/run.out 2>&1
  code=$?
  reqs=$( [ -f $R/requests.jsonl ] && wc -l < $R/requests.jsonl || echo 0 )
  ledger=$( [ -f $T/ledger.json ] && echo present || echo absent )
  errs=$($PY -c "import json; print(json.loads(open('$T/evidence/run_log.jsonl').readline())['precheck_errors'])")
  echo "$probe: runner exit=$code requests=$reqs ledger=$ledger errors=$errs"
done
