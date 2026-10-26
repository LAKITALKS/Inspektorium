"""Verifier: what the documented non-fake run_library CLI path sends (stubbed SDK, no network).

A stub `anthropic` module records messages.create kwargs. httpx is the real package but no
request is issued because the stub never uses the passed http_client.
"""
import hashlib
import json
import sys
import types

B, S = sys.argv[1], sys.argv[2]
sys.path.insert(0, B + "/src")
CALLS, CLIENT_KW = [], []


class _Msg:
    def __init__(self, text):
        self.content = [types.SimpleNamespace(text=text)]
        self.stop_reason = "end_turn"
        self.usage = types.SimpleNamespace(input_tokens=1, output_tokens=1)


class _Messages:
    def create(self, **kw):
        CALLS.append(kw)
        return _Msg(json.dumps({"final_answer": "solid", "steps": ["x"], "key_claims": ["y"],
                                "confidence": 0.7}))


class Anthropic:
    def __init__(self, **kw):
        CLIENT_KW.append(sorted(kw))
        self.messages = _Messages()


stub = types.ModuleType("anthropic")
stub.Anthropic = Anthropic
sys.modules["anthropic"] = stub

from agent_arena import run_library as rl  # noqa: E402
from agent_arena import runner  # noqa: E402

out = S + "/live_stub_run"
# --model omitted on purpose: which model would the documented live path default to?
rc = rl.main(["--case-id", "study-forensics-007", "--runs-per-case", "1", "--provider", "anthropic",
              "--out-dir", out])
kw = CALLS[0]
task = [t for _, t in rl.discover_cases(case_id="study-forensics-007")][0]
system, msgs = kw["system"], kw["messages"]
blob = system + "\n".join(m["content"] for m in msgs)
print("rc", rc, "calls", len(CALLS), "client kwargs", CLIENT_KW[0])
print("model sent:", kw["model"], "| max_tokens:", kw["max_tokens"], "| temperature:", kw.get("temperature"))
for name, ver in [("historical", runner.STUDY_FORENSICS_PROMPT_VERSION_HISTORICAL),
                  ("prospective", runner.STUDY_FORENSICS_PROMPT_VERSION_PROSPECTIVE),
                  ("phase8", runner.STUDY_FORENSICS_PROMPT_VERSION_PHASE8),
                  ("phase8_contract_r1", runner.STUDY_FORENSICS_PROMPT_VERSION_PHASE8_CONTRACT_R1)]:
    print(f"system == {name}:", system == runner.resolve_study_forensics_prompt(ver))
print("system sha256:", hashlib.sha256(system.encode()).hexdigest(), "bytes:", len(system.encode()))
print("system says 'Use only the supplied task prompt and context':",
      "Use only the supplied task prompt and context" in system)
print("system says 'context for task.context':", "context for task.context" in system)
print("messages roles/lens:", [(m["role"], len(m["content"])) for m in msgs])
print("user == task.prompt:", msgs[0]["content"] == task.prompt)
print("full task.context in request:", task.context in blob,
      "| any context line (>=20 chars) in request:",
      any(ln.strip() in blob for ln in task.context.splitlines() if len(ln.strip()) >= 20))
m = json.load(open(out + "/manifest.json"))
r = json.loads(open(out + "/results.jsonl").readline())
print("manifest:", {k: m[k] for k in ("provider", "model")}, "keys:", sorted(m))
print("record has prompt/condition key:", [k for k in r if "prompt" in k or "condition" in k])
print("record phase8.technical_status:", (r.get("phase8") or {}).get("technical_status"),
      "| phase9 keys:", sorted((r.get("phase9") or {}))[:6])
print("record model/provider:", r["model"], r["provider"])
