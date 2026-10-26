#!/bin/bash
# Extract the durable archive into scratch and inspect every extracted bundle through the guarded canonical CLI.
S=__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/v1/evidence-A; PY=__LOCAL_HOME__/Documents/Projects/agent-arena/.venv/bin/python
D=__LOCAL_HOME__/Documents/Projects/agent-arena/analysis/v1_closeout_20261013/evidence/A
cd $S; rm -rf archive-check; mkdir archive-check; tar -xzf $D/replay_bundles.tar.gz -C archive-check
echo "extracted_files=$(find archive-check -type f | wc -l | tr -d ' ')"
for b in $(ls -d archive-check/replay_bundles/*/*/ | sort); do echo "== <scratch>/$b"
  env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY PYTHONDONTWRITEBYTECODE=1 $PY tools/aa_cli.py audit inspect --bundle $S/$b > .out 2> .err; rc=$?
  cat .out; grep netguard .err; echo "exit=$rc"; done | sed "s|$S|<scratch>|g"; rm -f .out .err
