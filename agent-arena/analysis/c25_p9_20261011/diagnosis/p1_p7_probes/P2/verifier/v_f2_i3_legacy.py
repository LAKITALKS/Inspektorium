"""Verifier probe for P2-F2 and P2-I3 (fake SDKs, no network)."""
import sys, os, json, types
from pathlib import Path
BASE = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
sys.path.insert(0, BASE + "/src")
for k in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY"): os.environ.pop(k, None)
STATE = {"text": "", "stop": "end_turn", "content": None, "sent": []}
class _Msgs:
    def create(self, **kw):
        STATE["sent"].append(kw)
        content = STATE["content"] if STATE["content"] is not None else [types.SimpleNamespace(type="text", text=STATE["text"])]
        return types.SimpleNamespace(content=content, stop_reason=STATE["stop"],
                                     usage=types.SimpleNamespace(input_tokens=1, output_tokens=1))
class _Client:
    def __init__(self, **kw): self.messages = _Msgs()
sys.modules["anthropic"] = types.SimpleNamespace(Anthropic=_Client)
import agent_arena
assert agent_arena.__file__.startswith(BASE), agent_arena.__file__
from agent_arena.providers.anthropic import AnthropicProvider
from agent_arena.runner import run_agent, STUDY_FORENSICS_PROMPT_VERSION_HISTORICAL as HIST
from agent_arena.task_loader import load_task
task = load_task(Path(BASE) / "examples/phase10/positive-task.json")
rec = (Path(BASE) / "examples/phase10/positive-recording.json").read_text()
print("task.prompt:", repr(task.prompt)); print("task.context[:80]:", repr(task.context[:80]))

# F2 (a): legacy adapter + default prompt, replayed response that quotes context
STATE.update(text=rec, sent=[])
r = run_agent(AnthropicProvider(model="claude-haiku-4-5-20251001"), task)
kw = STATE["sent"][0]
print("F2a sent keys:", sorted(kw), "| user content == task.prompt:", kw["messages"][0]["content"] == task.prompt,
      "| context anywhere in request:", task.context.strip()[:40] in json.dumps(kw))
print("F2a system mentions task.context:", "context for task.context" in kw["system"])
p8 = r.phase8 or {}
srcs = [e.get("source_id") for e in (r.parsed.forensic_record or {}).get("evidence", [])]
print("F2a phase8:", p8.get("technical_status"), "| evidence source_ids:", srcs, "| phase9 route:", (r.phase9 or {}).get("route"),
      "| execution_evidence:", r.execution_evidence)
# F2 (b): same with the historical prompt (what Phase-7 paths pin) -> does the historical prompt mention context?
STATE.update(text=rec, sent=[])
r_h = run_agent(AnthropicProvider(model="claude-haiku-4-5-20251001"), task, prompt_version=HIST)
print("F2b historical system mentions 'context':", "context" in STATE["sent"][0]["system"].lower(),
      "| phase8:", (r_h.phase8 or {}).get("technical_status"))

# I3: stop_reason 'refusal' with empty content and with refusal text
for label, content in (("refusal-empty", []), ("refusal-text", [types.SimpleNamespace(type="text", text="I can't help with that.")])):
    STATE.update(stop="refusal", content=content, sent=[])
    resp = AnthropicProvider(model="claude-haiku-4-5-20251001").generate(task, "sys")
    r3 = run_agent(AnthropicProvider(model="claude-haiku-4-5-20251001"), task)
    print(f"I3 {label}: generate -> error={resp.error!r} finish_reason={resp.finish_reason!r} text={resp.text!r} ok={resp.ok}")
    print(f"   run_agent -> error={r3.error!r} error_type={r3.error_type!r} parse_ok={r3.parse_ok} finish_reason={r3.finish_reason!r} "
          f"phase8={(r3.phase8 or {}).get('technical_status')!r} reasons={(r3.phase8 or {}).get('reasons', [])[:1]} phase9={(r3.phase9 or {}).get('route')!r}")
# thinking-first content block (legacy adapter reads content[0].text)
STATE.update(stop="end_turn", content=[types.SimpleNamespace(type="thinking", thinking="..."), types.SimpleNamespace(type="text", text=rec)], sent=[])
resp = AnthropicProvider().generate(task, "sys")
print("legacy thinking-first block: error_type=", resp.error_type, "| error=", (resp.error or "")[:80])
