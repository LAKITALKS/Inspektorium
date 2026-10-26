#!/bin/bash
# Replays the three unresolved slots from the scratch COPY of live_retest through the guarded canonical CLI.
S=__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/v1/evidence-A; PY=__LOCAL_HOME__/Documents/Projects/agent-arena/.venv/bin/python
mkdir -p $S/replay
for pc in "claude-sonnet-5-5@3 LR-02" "claude-sonnet-5-5@3 LR-03" "claude-haiku-5-5@3 LR-03"; do set -- $pc; slot=${1%%@*}-$2
  cmd=(env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY PYTHONDONTWRITEBYTECODE=1 $PY $S/tools/aa_cli.py audit run --replay --task $S/copy/tasks/$2.json --authorization-dir $S/copy --profile $1 --output-root $S/replay/$slot)
  echo "$ ${cmd[*]}"
  ( cd $S && "${cmd[@]}" > $S/replay/$slot.cli.json 2> $S/replay/$slot.stderr ); echo "exit=$?" | tee $S/replay/$slot.exit
  cat $S/replay/$slot.cli.json; cat $S/replay/$slot.stderr
done
