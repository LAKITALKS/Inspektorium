"""Verifier: re-run the row's representative traces (positive example, and its model=unsupported conflict
variant) through run_audit/release_candidate, writing only into the verifier directory. Offline only."""
import json
import sys
from pathlib import Path

DIAG = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new"
OUT = Path("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_p8_p10/P8/verifier/out_trace")
sys.path.insert(0, DIAG + "/src")
import agent_arena  # noqa: E402
assert agent_arena.__file__.startswith(DIAG), agent_arena.__file__
from agent_arena.phase9_runtime import OfflineReviewProvider  # noqa: E402
from agent_arena.phase10_bundle import inspect_bundle, release_candidate, run_audit  # noqa: E402
from agent_arena.task_loader import load_task  # noqa: E402

EX = Path(DIAG) / "examples/phase10"
task = load_task(EX / "positive-task.json")
for name in ("positive", "conflict"):
    data = json.loads((EX / "positive-recording.json").read_text())
    if name == "conflict":
        fr = data["forensic_record"]
        fr["phase8"]["propositions"][0]["reported_verdict"] = "unsupported"
        for t in fr["phase8"]["transformations"]:
            if t.get("asserted_state") is not None:
                t["asserted_state"] = "unsupported"
    r = run_audit(task, OfflineReviewProvider(json.dumps(data)), output_root=OUT / name)
    b = Path(r.path)
    rec = json.loads((b / "record.json").read_text())
    p8 = rec["run_record"]["results"][0]["agent_result"]["phase8"]
    p9 = rec["run_record"]["metadata"]["phase9"]
    print(f"== {name}: P10 {r.status} valid {inspect_bundle(b).valid}")
    print("  P7:", [(c["name"], c["status"], c.get("eligible_count")) for c in p8["phase7_controls"]])
    print("  P8:", p8["technical_status"], p8["composite_state"], "model/host", p8["model_composite_state"],
          p8["host_composite_state"], [c["scope"] for c in p8["model_host_conflicts"]], "label", p8["derived_label"])
    print("  P9:", p9["route"], [(t["code"], t["mandatory"]) for t in p9["triggers"]])
    print("  release:", release_candidate(b, output_root=OUT / (name + "_rel"), reviewer="DIAG ONLY",
                                         reason="verifier").status)
