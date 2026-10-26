#!/bin/bash
# Canonical CLI inspect of COPIES of the 9 live_retest revisions: [hist] = 558e920 worktree code + 0.1.0 dist metadata
# shim on PYTHONPATH; [v1] = editable install at HEAD 5560e95. Network refused and counted by netguard.
S=__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/v1/evidence-A; PY=__LOCAL_HOME__/Documents/Projects/agent-arena/.venv/bin/python
cd $S
for r in $(find hist-copies -name record.json | sort); do b=$(dirname $r)
  for mode in hist v1; do
    if [ $mode = hist ]; then PP="$S/hist/src:$S/hist-meta"; else PP=""; fi
    out=$(env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PP" $PY tools/aa_cli.py audit inspect --bundle $S/$b 2>$S/logs/.err); rc=$?
    ver=$(grep -o 'agent_arena [0-9.]*' $S/logs/.err); net=$(grep -o '"refused_real_network_attempts": [0-9]*' $S/logs/.err)
    echo "[$mode] $ver | $b | exit=$rc | $net | $(echo $out | tr -s ' ')"
  done
done
rm -f $S/logs/.err
