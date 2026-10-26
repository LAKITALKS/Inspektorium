#!/bin/bash
# A4: attempt a TEST release of each scratch replay bundle; expected RELEASE_BLOCKED, exit 2, nothing written.
S=__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/v1/evidence-A; PY=__LOCAL_HOME__/Documents/Projects/agent-arena/.venv/bin/python
cd $S
for rec in $(ls replay/*/*/record.json | sort); do b=$(dirname $rec); slot=$(basename $(dirname $b))
  reason="SYNTHETIC TEST release probe on scratch replay $slot (copy of live_retest); expected RELEASE_BLOCKED"
  echo "== $slot: agent-arena audit release --bundle <scratch>/$b --output-root <scratch>/release_try/$slot --reviewer 'TEST ONLY - not a scientific release' --reason '$reason'"
  pre=$(cd $b && shasum -a 256 * | shasum -a 256)
  env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY PYTHONDONTWRITEBYTECODE=1 $PY tools/aa_cli.py audit release --bundle $S/$b \
    --output-root $S/release_try/$slot --reviewer "TEST ONLY - not a scientific release" --reason "$reason" 2>&1 | sed "s|$S|<scratch>|g"
  echo "exit=${PIPESTATUS[0]}"
  post=$(cd $b && shasum -a 256 * | shasum -a 256)
  echo "bundle_unchanged=$([ "$pre" = "$post" ] && echo true || echo false) bundle_files=$(ls $b | wc -l | tr -d ' ')"
  if [ -e release_try/$slot ]; then echo "output_root_exists=true files_written=$(find release_try/$slot -type f | wc -l | tr -d ' ')"; else echo "output_root_exists=false files_written=0"; fi
done
echo "release_try_dir_exists=$([ -e release_try ] && echo true || echo false)"
