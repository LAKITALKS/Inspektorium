#!/bin/zsh
# Usage: scenario.sh NAME 'FAULTS_JSON' ['PLAN_JSON']
# Fresh throwaway root -> unchanged prepare_retest.py -> unchanged run_retest.py (stand-in CLI) -> ledger dump.
# Summarize / replay / close are run separately (post.sh) so their order and repetition can be varied.
set -u
OP=__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/selftest_v3
PY=__LOCAL_HOME__/Documents/Projects/agent-arena/.venv/bin/python
export PYTHONDONTWRITEBYTECODE=1
unset ANTHROPIC_API_KEY
NAME=$1
case "$NAME" in */*|.*|'') echo "bad name"; exit 1;; esac
SIM=$OP/$NAME
export SIM_ROOT=$SIM/root
rm -rf $SIM && mkdir -p $SIM
$PY $OP/scripts/setup_root.py $SIM_ROOT > $SIM/setup.log 2>&1 || { echo "setup failed"; cat $SIM/setup.log; exit 1; }
F=${2:-}; [ -z "$F" ] && F="{}"; print -r -- "$F" > $SIM_ROOT/faults.json
P=${3:-}; [ -z "$P" ] && P="{}"; print -r -- "$P" > $SIM_ROOT/plan.json
cd $SIM_ROOT
$PY $OP/scripts/simwrap.py draft/prepare_retest.py > $SIM/prepare.log 2>&1 || { echo "prepare failed"; cat $SIM/prepare.log; exit 1; }
if [ "${SKIP_COMMIT:-}" != 1 ]; then
  GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null git -c user.name=sim -c user.email=sim@example.invalid -c commit.gpgsign=false add analysis/c25_p9_20261011/live_retest
  GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null git -c user.name=sim -c user.email=sim@example.invalid -c commit.gpgsign=false commit -q -m "sim freeze"
fi
if [ "${SKIP_RUN:-}" = 1 ]; then echo "(run skipped)"; exit 0; fi
echo "== run_retest.py (unchanged frozen copy)"
if [ "${SIM_NO_ENV_KEY:-}" = 1 ]; then RK=""; else RK="sim-placeholder-not-a-key"; fi
ANTHROPIC_API_KEY=$RK $PY analysis/c25_p9_20261011/live_retest/scripts/run_retest.py > $SIM/run.out 2> $SIM/run.err
echo "runner exit=$?"
cat $SIM/run.out | cut -c1-330
echo "== requests (n_total model case kind n user_bytes)"
[ -f $SIM_ROOT/requests.jsonl ] && $PY -c "
import sys,json
for r in map(json.loads, open('$SIM_ROOT/requests.jsonl')):
    print(r['n_total'], r['model'], r['case'], r['kind'], r['n'], r['user_bytes'], 'conflict_pkt' if r['has_conflict_positions'] else '', 'testkey' if r['api_key_is_test_key'] else 'NO-TEST-KEY')
"
echo "== ledger"
$PY $OP/scripts/dump_ledger.py $SIM_ROOT/analysis/c25_p9_20261011/live_retest
