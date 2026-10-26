"""Counter-case: what does the documented P4 *live* run_library path send? No network:
a stub `anthropic` module records messages.create kwargs and returns a canned reply."""
import sys, json, types
B, S = sys.argv[1], sys.argv[2]
sys.path.insert(0, B + "/src")
CALLS = []
class _Msg:
    def __init__(self, text): self.content=[types.SimpleNamespace(text=text)]; self.stop_reason="end_turn"; self.usage=types.SimpleNamespace(input_tokens=1,output_tokens=1)
class _Messages:
    def create(self, **kw):
        CALLS.append(kw)
        return _Msg(json.dumps({"final_answer":"solid","steps":["x"],"key_claims":["y"],"confidence":0.7}))
class Anthropic:
    def __init__(self, **kw): self.messages=_Messages()
stub = types.ModuleType("anthropic"); stub.Anthropic = Anthropic
sys.modules["anthropic"] = stub
from agent_arena import run_library as rl
from agent_arena.runner import STUDY_FORENSICS_PROMPT_PHASE8, STUDY_FORENSICS_PROMPT
rc = rl.main(["--case-id","study-forensics-007","--runs-per-case","1","--provider","anthropic","--model","stub-model","--out-dir",S+"/live_stub_run"])
kw = CALLS[0]
from agent_arena.task_loader import load_task
t = load_task(B+"/tasks/study_forensics/case007_vitamin_d_covid.yaml")
print("rc", rc, "n_calls", len(CALLS))
print("system == PHASE8 prompt:", kw["system"] == STUDY_FORENSICS_PROMPT_PHASE8, "| == historical P4 prompt:", kw["system"] == STUDY_FORENSICS_PROMPT)
print("system mentions task.context:", "context for task.context" in kw["system"])
print("messages:", [(m["role"], len(m["content"])) for m in kw["messages"]])
user = kw["messages"][0]["content"]
print("user == task.prompt:", user == t.prompt, "| context present in any message:", t.context.strip()[:40] in user or t.context.strip()[:40] in kw["system"])
print("len(task.context)=", len(t.context))
for fld in ["gold_label","gold_justification","reference_solution","curator_notes","expected_answer"]:
    v = getattr(t, fld) or ""
    probe = v.strip()[:30]
    print(f"leak {fld}:", bool(probe) and (probe in user or probe in kw["system"]))
m = json.load(open(S+"/live_stub_run/manifest.json")); r = json.loads(open(S+"/live_stub_run/results.jsonl").readline())
print("manifest keys:", sorted(m)); print("prompt_version in record:", any("prompt" in k for k in r), "max_tokens sent:", kw["max_tokens"])
