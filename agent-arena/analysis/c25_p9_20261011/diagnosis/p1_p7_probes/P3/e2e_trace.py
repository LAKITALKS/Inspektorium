import sys, os, json, types
B, D = sys.argv[1], sys.argv[2]
sys.path.insert(0, B+"/src"); os.chdir(B)
from pathlib import Path
from agent_arena import run_library as rl
# 1) CLI end-to-end, fake provider, artifacts into scratch
rc = rl.main(["--all","--fake","--out-dir",D+"/e2e_fake"])
s = json.load(open(D+"/e2e_fake/summary.json"))
recs=[json.loads(l) for l in open(D+"/e2e_fake/results.jsonl")]
print("rc",rc,"total_cases",s["total_cases"],"runs",s["total_runs"],"ok",s["successful_runs"],
      "label_correct",sum(1 for r in recs if r["label_correct"]),"retired_in_run",[r["case_id"] for r in recs if r["case_id"] in ("study-forensics-031","study-forensics-042")])
# 2) legacy Anthropic provider path with a stub SDK capturing the request (no network)
captured=[]
class _Msg:
    content=[types.SimpleNamespace(text=json.dumps({"final_answer":"solid","steps":["x"],"key_claims":["y"],"confidence":0.5}))]
    stop_reason="end_turn"; usage=types.SimpleNamespace(input_tokens=1,output_tokens=1)
class _Client:
    def __init__(self,**k): self.messages=self
    def create(self,**k): captured.append(k); return _Msg()
sys.modules["anthropic"]=types.SimpleNamespace(Anthropic=_Client)
from agent_arena.providers.anthropic import AnthropicProvider
cases=dict((t.id,(f,t)) for f,t in rl.discover_cases())
f,t=cases["study-forensics-044"]
rec=rl.run_single(AnthropicProvider(model="stub"),f,t,0,"trace")
msgs=captured[0]["messages"]
print("legacy: n_messages",len(msgs),"user==prompt",msgs[0]["content"]==t.prompt,"context sent",t.context.strip()[:40] in msgs[0]["content"],
      "label token in user msg","mechanism_vs_evidence" in msgs[0]["content"], "record gold",rec["gold_label"],"detected",rec["label"],"label_correct",rec["label_correct"])
# 3) live builder for same case
from agent_arena.providers.anthropic_live import build_user_message
u=build_user_message(t)
print("live: context sent", t.context.strip()[:40] in u, "label token", "mechanism_vs_evidence" in u)
idx=u.find("mechanism_vs_evidence"); print("live excerpt:", repr(u[max(0,idx-120):idx+40]))
