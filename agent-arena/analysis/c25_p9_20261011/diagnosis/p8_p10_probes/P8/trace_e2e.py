import json, sys
from pathlib import Path
DIAG = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new"
OUT = Path(__file__).resolve().parent / "out_trace"
sys.path.insert(0, DIAG + "/src"); sys.path.insert(0, DIAG)
import agent_arena; assert agent_arena.__file__.startswith(DIAG)
from agent_arena.phase9_runtime import OfflineReviewProvider
from agent_arena.phase10_bundle import inspect_bundle, release_candidate, run_audit
from agent_arena.phase8_pipeline import render_phase8
from agent_arena.task_loader import load_task
EX = Path(DIAG) / "examples/phase10"
for name, task_name in (("positive", "positive"), ("conflict", "positive")):
    task = load_task(EX / f"{task_name}-task.json")
    raw = (EX / f"{name}-recording.json").read_text()
    r = run_audit(task, OfflineReviewProvider(raw), output_root=OUT / name)
    b = Path(r.path); rec = json.loads((b / "record.json").read_text())
    p8 = rec["run_record"]["results"][0]["agent_result"]["phase8"]; p9 = rec["run_record"]["metadata"]["phase9"]
    print(f"== {name}: status {r.status} bundle_valid {inspect_bundle(b).valid}")
    print("  P7 controls:", [(c["name"], c["status"], c.get("eligible_count")) for c in p8["phase7_controls"]])
    print("  P8:", p8["technical_status"], p8["composite_state"], "model/host", p8["model_composite_state"], p8["host_composite_state"],
          "conflicts", [(c["scope"], c.get("proposition_id")) for c in p8["model_host_conflicts"]], "label", p8["derived_label"])
    print("  P9 route:", p9["route"], "triggers:", [(t["code"], t["mandatory"]) for t in p9["triggers"]])
    print("  P9 attempts:", [(a.get("kind"), a.get("status"), a.get("prompt_version")) for a in p9.get("review_attempts", p9.get("attempts", []))][:4])
    print("  release:", release_candidate(b, output_root=OUT / (name + "_rel"), reviewer="DIAG", reason="trace").status)
    if name == "conflict":
        print("  render_phase8 head:", render_phase8(p8).split("\n\n")[:1], [l for l in render_phase8(p8).split("\n\n") if "conflict" in l][:3])
