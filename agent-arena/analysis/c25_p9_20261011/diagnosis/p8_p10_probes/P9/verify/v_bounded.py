"""Independent re-check of the row's P5 (non-material model/host conflict) through the canonical offline path."""
import json
import shutil
import sys
from pathlib import Path

D = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new"
sys.path[:0] = [D + "/src", D]
OUT = Path("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_p8_p10/P9/verify/bounded")
assert str(OUT).startswith("/private/tmp/")
shutil.rmtree(OUT, ignore_errors=True)
from agent_arena.phase10_bundle import release_candidate, run_audit  # noqa: E402
from agent_arena.phase9_runtime import OfflineReviewProvider  # noqa: E402
from agent_arena.task_loader import load_task  # noqa: E402

EX = Path(D) / "examples/phase10"
task = load_task(EX / "positive-task.json")
data = json.loads((EX / "optional-unknown-recording.json").read_text())
opt = next(p for p in data["forensic_record"]["phase8"]["propositions"] if p["proposition_id"] == "claim:optional")
opt["evidence_bindings"] = [{"binding_id": "b_opt", "proposition_id": "claim:optional", "evidence_id": "e1",
                             "directness": "direct", "observation": "support", "reason": "Matching trial"}]
opt["reported_verdict"] = "unknown"
res = run_audit(task, OfflineReviewProvider(json.dumps(data)), output_root=OUT / "c")
rec = json.loads((Path(res.path) / "record.json").read_text())["run_record"]
p8 = rec["results"][0]["agent_result"]["phase8"]
p9 = rec["metadata"]["phase9"]
print("status", res.status, "| route", p9["route"], "| mandatory", p9["mandatory"])
print("conflicts", [(c["scope"], c.get("proposition_id"), c["model_state"], c["host_state"]) for c in p8["model_host_conflicts"]])
print("triggers", sorted((t["code"], t["mandatory"]) for t in p9["triggers"]))
row = [ln.strip()[:150] for ln in (Path(res.path) / "report.md").read_text().splitlines() if "model/host conflicts" in ln]
print("report row", row[:1])
rel = release_candidate(Path(res.path), output_root=OUT / "rel", reviewer="TEST ONLY", reason="verifier")
print("release", rel.status)
