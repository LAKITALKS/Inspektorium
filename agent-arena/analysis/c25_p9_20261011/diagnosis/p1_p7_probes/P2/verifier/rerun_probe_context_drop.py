"""Counter-case: legacy 4.5 adapter + default v3-phase8 prompt on a task whose evidence lives in task.context."""
import sys, json, types, os
from pathlib import Path
BASE = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
sys.path.insert(0, BASE + "/src"); os.environ.pop("ANTHROPIC_API_KEY", None)
from agent_arena.task_loader import load_task
task = load_task(Path(BASE) / "examples/phase10/positive-task.json")
recording = (Path(BASE) / "examples/phase10/positive-recording.json").read_text()
sent = []
class _Msg:
    content = [types.SimpleNamespace(text=recording)]; stop_reason = "end_turn"
    usage = types.SimpleNamespace(input_tokens=1, output_tokens=1)
class _M:
    def create(self, **kw): sent.append(kw); return _Msg()
class _A:
    def __init__(self, **kw): self.messages = _M()
sys.modules["anthropic"] = types.SimpleNamespace(Anthropic=_A)
from agent_arena.providers.anthropic import AnthropicProvider
from agent_arena.runner import run_agent
r = run_agent(AnthropicProvider(model="claude-haiku-4-5-20251001"), task)
user = sent[0]["messages"][0]["content"]
print("transmitted user message:", repr(user))
print("task.context transmitted:", task.context in user)
print("system says 'Use only the supplied task prompt and context':", "Use only the supplied task prompt and context" in sent[0]["system"])
p8 = r.phase8 or {}
print("phase8 technical_status:", p8.get("technical_status"), "| keys:", sorted(p8)[:12])
ev = (r.parsed.forensic_record or {}).get("evidence", []) if r.parsed else []
print("evidence source_ids accepted in record:", [e.get("source_id") for e in ev])
print("phase8 outcome fields:", {k: p8.get(k) for k in ("status", "outcome", "verdict", "assessment_status", "label") if k in p8})
print("execution_evidence (transmission provenance) on legacy result:", r.execution_evidence)
print("phase9 route:", (r.phase9 or {}).get("route"))
dumped = json.dumps(r.model_dump(mode="json"))
print("any user-message hash/version in legacy AgentResult:", "user_message" in dumped)
# honest-model variant: model says it saw only the claim
honest = json.loads(recording)
honest["forensic_record"]["evidence"] = []
for p in honest["forensic_record"].get("phase8", {}).get("propositions", []):
    for k in list(p):
        if "evidence" in k: p[k] = []
_Msg.content = [types.SimpleNamespace(text=json.dumps(honest))]
r2 = run_agent(AnthropicProvider(model="claude-haiku-4-5-20251001"), task)
p82 = r2.phase8 or {}
print("honest(no-evidence) variant: phase8 technical_status:", p82.get("technical_status"),
      "| reasons:", json.dumps({k: p82.get(k) for k in p82 if k in ("status","reason","reasons","finding","missing")})[:400])
print("phase9 route honest:", (r2.phase9 or {}).get("route"))
