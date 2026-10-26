"""Verifier end-to-end re-run (fake provider + stubbed SDK; no network)."""
import sys, os, json, types, io, contextlib
B, D = sys.argv[1], sys.argv[2]
sys.path.insert(0, B + "/src")
os.chdir(B)
from agent_arena import run_library as rl

buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc = rl.main(["--all", "--fake", "--out-dir", D + "/e2e_fake_v"])
print("stdout:", buf.getvalue().strip().splitlines()[:2])
recs = [json.loads(l) for l in open(D + "/e2e_fake_v/results.jsonl")]
print("rc", rc, "runs", len(recs), "label_correct", sum(r["label_correct"] is True for r in recs),
      "retired present", [r["case_id"] for r in recs if r["case_id"] in ("study-forensics-031", "study-forensics-042")],
      "keys with 'prompt'", [k for k in recs[0] if "prompt" in k])
print("phase8 states", sorted({(r.get("phase8") or {}).get("technical_status") for r in recs}))

# Legacy AnthropicProvider with a stub SDK (captures request; no network)
captured = []
class _Msg:
    content = [types.SimpleNamespace(type="text", text=json.dumps(
        {"final_answer": "solid", "steps": ["x"], "key_claims": ["y"], "confidence": 0.5}))]
    stop_reason = "end_turn"; model = "stub"
    usage = types.SimpleNamespace(input_tokens=1, output_tokens=1)
class _Client:
    def __init__(self, **k): self.messages = self
    def create(self, **k): captured.append(k); return _Msg()
sys.modules["anthropic"] = types.SimpleNamespace(Anthropic=_Client)
from agent_arena.providers.anthropic import AnthropicProvider
cases = {t.id: (f, t) for f, t in rl.discover_cases()}
for cid in ("study-forensics-001", "study-forensics-044"):
    captured.clear()
    f, t = cases[cid]
    rec = rl.run_single(AnthropicProvider(model="stub"), f, t, 0, "v")
    m = captured[0]["messages"]
    print(cid, "n_msgs", len(m), "user==prompt", m[0]["content"] == t.prompt,
          "ctx in any request field", any(t.context.strip()[:40] in json.dumps(v) for v in captured[0].values()),
          "gold", rec["gold_label"], "detected", rec["label"], "label_correct", rec["label_correct"],
          "error", rec["error"])

# Wrong cwd -> fail closed
os.chdir("/")
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc2 = rl.main(["--all", "--fake", "--out-dir", D + "/e2e_wrongcwd"])
print("wrong cwd rc", rc2, buf.getvalue().strip(), "artifacts written:", os.path.exists(D + "/e2e_wrongcwd"))
