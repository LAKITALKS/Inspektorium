#!/bin/bash
# A1: inspect each replay bundle via the guarded wrapper (netguard counters) and via the canonical .venv/bin/agent-arena.
S=__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/v1/evidence-A; R=__LOCAL_HOME__/Documents/Projects/agent-arena
cd $S
for rec in $(ls replay/*/*/record.json | sort); do b=$(dirname $rec)
  echo "== $b (recorded status: $($R/.venv/bin/python -I -c 'import json,sys;print(json.load(open(sys.argv[1]))["status"])' $rec))"
  echo "$ env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY PYTHONDONTWRITEBYTECODE=1 \$PY tools/aa_cli.py audit inspect --bundle <scratch>/$b"
  env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY PYTHONDONTWRITEBYTECODE=1 $R/.venv/bin/python tools/aa_cli.py audit inspect --bundle $S/$b; echo "exit=$?"
  echo "$ env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/bin/agent-arena audit inspect --bundle <scratch>/$b"
  env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY PYTHONDONTWRITEBYTECODE=1 $R/.venv/bin/agent-arena audit inspect --bundle $S/$b; echo "exit=$?"
done 2>&1 | sed "s|$S|<scratch>|g"
