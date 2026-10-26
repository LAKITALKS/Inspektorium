import json, sys
from pathlib import Path
DIAG = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new"
OUT = Path(__file__).resolve().parent / "out_trace_conflict"
sys.path.insert(0, DIAG + "/src"); sys.path.insert(0, DIAG)
import agent_arena; assert agent_arena.__file__.startswith(DIAG)
from agent_arena.phase9_runtime import OfflineReviewProvider
from agent_arena.phase10_bundle import inspect_bundle, release_candidate, run_audit
from agent_arena.task_loader import load_task
EX = Path(DIAG) / "examples/phase10"
task = load_task(EX / "positive-task.json")
data = json.loads((EX / "positive-recording.json").read_text())
fr = data["forensic_record"]
fr["phase8"]["propositions"][0]["reported_verdict"] = "unsupported"
for t in fr["phase8"]["transformations"]:
    if t.get("asserted_state") is not None: t["asserted_state"] = "unsupported"
r = run_audit(task, OfflineReviewProvider(json.dumps(data)), output_root=OUT)
b = Path(r.path); rec = json.loads((b / "record.json").read_text())
p8 = rec["run_record"]["results"][0]["agent_result"]["phase8"]; p9 = rec["run_record"]["metadata"]["phase9"]
print("status", r.status, "valid", inspect_bundle(b).valid)
print("P8", p8["technical_status"], p8["composite_state"], p8["model_composite_state"], p8["host_composite_state"], [(c["scope"]) for c in p8["model_host_conflicts"]])
print("P9", p9["route"], [(t["code"], t["mandatory"]) for t in p9["triggers"]])
print("P9 keys", sorted(p9.keys()))
for k in ("review_attempts", "attempts", "reviews"):
    if k in p9: print(k, [(a.get("kind"), a.get("status"), a.get("prompt_version"), (a.get("independence") or a.get("independence_note") or "")[:60]) for a in p9[k]])
print("release", release_candidate(b, output_root=OUT / "rel", reviewer="DIAG", reason="trace").status)
rep = (b / "report.md").read_text()
print([l for l in rep.splitlines() if "mandatory review" in l or "host evidence derivation" in l][:4])
