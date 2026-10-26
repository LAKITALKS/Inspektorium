#!/bin/zsh
# Usage: post.sh NAME STEP...   STEP = summarize | replay:PROFILE:CASE[:SCRATCH_NAME] | close
# Runs the unchanged frozen after_run scripts of the simulation root NAME (via simwrap.py).
set -u
OP=__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/selftest_v3
PY=__LOCAL_HOME__/Documents/Projects/agent-arena/.venv/bin/python
WHEELPY=__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/clean-b/venv/bin/python
export PYTHONDONTWRITEBYTECODE=1
unset ANTHROPIC_API_KEY
NAME=$1; shift
SIM=$OP/$NAME
export SIM_ROOT=$SIM/root
cd $SIM_ROOT
S=analysis/c25_p9_20261011/live_retest/scripts
i=0
for step in "$@"; do
  i=$((i+1))
  case $step in
    summarize)
      echo "== summarize_retest.py ($i)"
      $PY $OP/scripts/simwrap.py $S/summarize_retest.py > $SIM/summarize.$i.out 2>&1; echo "exit=$?"
      cut -c1-600 $SIM/summarize.$i.out | tail -25 ;;
    replayin:*)
      parts=(${(s/:/)step}); rel=$parts[2]
      echo "== replay_retest.py -> (inside root) $rel ($i)"
      $WHEELPY $OP/scripts/simwrap.py $S/replay_retest.py $SIM_ROOT/$rel > $SIM/replay.$i.out 2>&1; echo "exit=$?"
      cut -c1-400 $SIM/replay.$i.out | tail -12 ;;
    replay*)
      parts=(${(s/:/)step}); scr=${parts[2]:-replay_scratch}
      echo "== replay_retest.py -> $scr ($i)"
      $WHEELPY $OP/scripts/simwrap.py $S/replay_retest.py $SIM/$scr > $SIM/replay.$i.out 2>&1; echo "exit=$?"
      cut -c1-400 $SIM/replay.$i.out | tail -60 ;;
    replayin:*)
      parts=(${(s/:/)step}); rel=$parts[2]
      echo "== replay_retest.py -> (inside root) $rel ($i)"
      $WHEELPY $OP/scripts/simwrap.py $S/replay_retest.py $SIM_ROOT/$rel > $SIM/replay.$i.out 2>&1; echo "exit=$?"
      cut -c1-400 $SIM/replay.$i.out | tail -12 ;;
    close)
      echo "== close_retest.py ($i)"
      $PY $OP/scripts/simwrap.py $S/close_retest.py > $SIM/close.$i.out 2>&1; echo "exit=$?"
      cut -c1-400 $SIM/close.$i.out | tail -30 ;;
    *) echo "unknown step $step"; exit 1 ;;
  esac
done
