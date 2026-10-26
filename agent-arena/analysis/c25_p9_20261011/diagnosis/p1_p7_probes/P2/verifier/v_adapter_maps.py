"""Adapter-level finish_reason/usage/error mapping for the three legacy adapters (fake SDKs, no network)."""
import sys, os, json, types, urllib.request
from pathlib import Path
BASE = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
sys.path.insert(0, BASE + "/src")
for k in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY"): os.environ.pop(k, None)
import agent_arena
assert agent_arena.__file__.startswith(BASE)
from agent_arena.task_loader import load_task
from agent_arena.runner import run_agent
task = load_task(Path(BASE) / "examples/phase10/positive-task.json")
rec = (Path(BASE) / "examples/phase10/positive-recording.json").read_text()

# --- 0. SDK missing: does generate() honour "never raises"?
import importlib.util
print("openai SDK installed:", importlib.util.find_spec("openai") is not None)
from agent_arena.providers.openai import OpenAIProvider
try:
    r = OpenAIProvider().generate(task, "sys"); print("OpenAI generate without SDK -> returned", r.error_type, r.error)
except Exception as e:
    print("OpenAI generate without SDK -> RAISED", type(e).__name__, e)
ra = run_agent(OpenAIProvider(), task)
print("  run_agent(OpenAI) -> error_type", ra.error_type, "| error", ra.error)
saved = sys.modules.get("anthropic", "absent")
sys.modules["anthropic"] = None  # forces ImportError on import
from agent_arena.providers.anthropic import AnthropicProvider
try:
    r = AnthropicProvider().generate(task, "sys"); print("Anthropic generate without SDK -> returned", r.error_type)
except Exception as e:
    print("Anthropic generate without SDK -> RAISED", type(e).__name__, e)

# --- 1. Anthropic stop_reason mapping through run_agent
S = {}
class _Msgs:
    def create(self, **kw):
        return types.SimpleNamespace(content=[types.SimpleNamespace(text=S["text"])], stop_reason=S["stop"],
                                     usage=types.SimpleNamespace(input_tokens=5, output_tokens=7))
sys.modules["anthropic"] = types.SimpleNamespace(Anthropic=lambda **kw: types.SimpleNamespace(messages=_Msgs()))
for stop in ("end_turn", "max_tokens", "pause_turn", None):
    S.update(text=rec, stop=stop)
    r = run_agent(AnthropicProvider(), task)
    print(f"Anthropic stop_reason={stop!r}: finish_reason={r.finish_reason!r} error={r.error!r} parse_ok={r.parse_ok} "
          f"phase8={(r.phase8 or {}).get('technical_status')} usage={r.usage}")

# --- 2. OpenAI finish_reason mapping (fake SDK)
O = {}
class _Comp:
    def create(self, **kw):
        ch = types.SimpleNamespace(message=types.SimpleNamespace(content=O["text"]), finish_reason=O["fr"])
        return types.SimpleNamespace(choices=[ch], usage=types.SimpleNamespace(prompt_tokens=1, completion_tokens=2, total_tokens=3))
sys.modules["openai"] = types.SimpleNamespace(OpenAI=lambda **kw: types.SimpleNamespace(chat=types.SimpleNamespace(completions=_Comp())))
for fr in ("stop", "length", "content_filter", "weird"):
    O.update(text=rec, fr=fr)
    resp = OpenAIProvider().generate(task, "sys")
    r = run_agent(OpenAIProvider(), task)
    print(f"OpenAI finish_reason={fr!r}: ModelResponse finish_reason={resp.finish_reason!r} error={resp.error!r} ok={resp.ok} | "
          f"run_agent error={r.error!r} parse_ok={r.parse_ok} phase8={(r.phase8 or {}).get('technical_status')} phase9={(r.phase9 or {}).get('route')}")

# --- 3. Ollama done_reason mapping (patched urlopen)
OL = {}
class _Resp:
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def read(self): return json.dumps(OL["body"]).encode()
urllib.request.urlopen = lambda req, timeout=None: _Resp()
from agent_arena.providers.ollama import OllamaProvider
for body in ({"message": {"content": rec}, "done_reason": "stop", "prompt_eval_count": 1, "eval_count": 2},
             {"message": {"content": rec}, "done_reason": "length"},
             {"message": {"content": rec}}):
    OL["body"] = body
    resp = OllamaProvider().generate(task, "sys")
    print(f"Ollama done_reason={body.get('done_reason')!r}: finish_reason={resp.finish_reason!r} usage={resp.usage}")
