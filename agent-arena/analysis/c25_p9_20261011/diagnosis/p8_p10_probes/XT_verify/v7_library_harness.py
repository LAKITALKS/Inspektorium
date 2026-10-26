"""Independent minimal re-check of XT-F2 (library harness, legacy Anthropic adapter with a stubbed SDK; no network)."""
import json, sys, types
from pathlib import Path
D = Path("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new")
sys.path.insert(0, str(D / "src"))
import agent_arena; assert str(D) in agent_arena.__file__
import anthropic
from agent_arena.run_library import discover_cases, run_library
from agent_arena.providers.anthropic import AnthropicProvider
from agent_arena.runner import resolve_study_forensics_prompt
seen = []
class _Msgs:
    def create(self, **kw):
        seen.append(kw)
        return types.SimpleNamespace(content=[types.SimpleNamespace(text='{"final_answer":"solid","confidence":0.5}')],
                                     stop_reason="end_turn", usage=types.SimpleNamespace(input_tokens=1, output_tokens=1))
anthropic.Anthropic = lambda **kw: types.SimpleNamespace(messages=_Msgs())
cases = discover_cases(case_id="study-forensics-045", task_dir=D / "tasks/study_forensics")
summary = run_library(AnthropicProvider(model="stub"), cases, write_artifacts=False)
rec = summary.records[0]
task = cases[0][1]
print(json.dumps({"system_is_v3_phase8": seen[0]["system"] == resolve_study_forensics_prompt("study_forensics_prompt/v3-phase8"),
                  "user_content_is_prompt_only": seen[0]["messages"][0]["content"] == task.prompt,
                  "context_sent": task.context.strip()[:30] in json.dumps(seen[0]),
                  "record_has_prompt_identity": any("prompt" in k for k in rec),
                  "p8_status": rec["phase8"]["technical_status"]}, indent=1))
