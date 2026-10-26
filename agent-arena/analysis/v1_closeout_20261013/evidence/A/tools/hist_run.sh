#!/bin/bash
# Historical verification (API): COPIES of the 9 live_retest revisions under 558e920 worktree code (+/- 0.1.0 metadata
# shim) and under the v1 editable install (HEAD 5560e95); plus the v1 code-identity diagnosis. Read-only on the copies.
S=__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/v1/evidence-A; PY=__LOCAL_HOME__/Documents/Projects/agent-arena/.venv/bin/python
cd $S
E=(env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY PYTHONDONTWRITEBYTECODE=1)
"${E[@]}" PYTHONPATH=$S/hist/src:$S/hist-meta $PY tools/hist_inspect.py $S/hist-copies > hist_inspect_558e920.json 2> logs/hist_inspect_558e920.stderr
"${E[@]}" PYTHONPATH=$S/hist/src $PY tools/hist_inspect.py $S/hist-copies > hist_inspect_558e920_without_version_shim.json 2> logs/hist_inspect_558e920_without_version_shim.stderr
"${E[@]}" $PY tools/hist_inspect.py $S/hist-copies > hist_inspect_v1.json 2> logs/hist_inspect_v1.stderr
"${E[@]}" $PY tools/why_not_verifiable.py $(find $S/hist-copies -name record.json | sort | xargs -n1 dirname) > why_not_verifiable_v1.json 2> logs/why_v1.stderr
