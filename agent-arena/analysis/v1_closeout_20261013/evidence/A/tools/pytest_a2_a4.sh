#!/bin/bash
# Supplementary: the committed v1 closeout report tests (A2 wording/causes, A4 release block) at HEAD 5560e95.
cd __LOCAL_HOME__/Documents/Projects/agent-arena
set -x
env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/v1/evidence-A/tools .venv/bin/python -m pytest -p no:cacheprovider -p pytest_netguard_plugin --basetemp __LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/v1/evidence-A/pytest-a2a4 -q tests/test_v1_closeout_report.py
