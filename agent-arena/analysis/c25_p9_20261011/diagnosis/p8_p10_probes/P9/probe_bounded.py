"""P5/P6: non-material (bounded) model/host conflict; human selecting a review that differs on another proposition."""
import json, shutil
from pathlib import Path
import common
from common import OUT, set_model
from agent_arena.task_loader import load_task
from agent_arena.phase9_runtime import OfflineReviewProvider, execute_review
from agent_arena.phase10_bundle import run_audit, create_candidate, review_candidate, release_candidate
from agent_arena.schemas import RunRecord
EX = Path(common.D) / "examples/phase10"
root = Path(OUT) / "bounded"; shutil.rmtree(root, ignore_errors=True)
task = load_task(EX / "positive-task.json")
base = json.loads((EX / "optional-unknown-recording.json").read_text())
def raw(model_p1=None, model_opt=None, drop_opt=False):
    d = json.loads(json.dumps(base)); l = d["forensic_record"]["phase8"]
    if model_p1:
        set_model(d["forensic_record"], model_p1)
    if model_opt:
        opt = next(p for p in l["propositions"] if p["proposition_id"] == "claim:optional")
        opt["evidence_bindings"] = [{"binding_id": "b_opt", "proposition_id": "claim:optional", "evidence_id": "e1",
                                     "directness": "direct", "observation": "support", "reason": "Matching trial"}]
        opt["reported_verdict"] = model_opt
    if drop_opt:
        l["propositions"] = [p for p in l["propositions"] if p["proposition_id"] != "claim:optional"]
    return json.dumps(d)
def summarize(tag, res):
    rec = json.loads((Path(res.path) / "record.json").read_text())["run_record"]
    p9 = rec["metadata"]["phase9"]; p8 = rec["results"][0]["agent_result"]["phase8"]
    rep = (Path(res.path) / "report.md").read_text()
    print(tag, res.status, p9["route"], "mandatory", p9["mandatory"], "codes", sorted({(t["code"], t["mandatory"]) for t in p9["triggers"]}))
    print("   p8 conflicts", [(c["scope"], c.get("proposition_id"), c["model_state"], c["host_state"]) for c in p8["model_host_conflicts"]], "composite", p8["composite_state"])
    print("   report conflict lines:", [l.strip()[:170] for l in rep.splitlines() if "conflict" in l.lower()][:4])
    return rec
# P5: optional proposition, model says supported, host unknown -> bounded conflict only
r5 = run_audit(task, OfflineReviewProvider(raw(model_opt="unknown")), output_root=root / "p5")
summarize("P5 bounded only:", r5)
rel = release_candidate(Path(r5.path), output_root=root / "p5rel", reviewer="DIAG", reason="diag")
print("   release:", rel.status)
# P6: original has MATERIAL conflict on p1 (model unsupported vs host supported);
#     review agrees with host on p1 but has bounded conflict on optional; human selects review.
r6 = run_audit(task, OfflineReviewProvider(raw(model_p1="unsupported")), output_root=root / "p6")
rec = summarize("P6 original:", r6)
record = RunRecord.model_validate(rec)
st = root / "state6"
rv = execute_review(record, OfflineReviewProvider(raw(model_opt="unknown")), base_dir=st, authorized=True, budget_calls=2)
d = rv.metadata["phase9"]
print("P6 after review:", d["route"], [(c["dimension"], c["field"], c["material"]) for c in d["conflicts"]])
c = create_candidate(rv, output_root=root / "p6c")
pid = next(p["position_id"] for p in d["positions"] if p["origin"] == "model_review")
h = review_candidate(Path(c.path), output_root=root / "p6h", state_dir=st, selected_position_id=pid, reviewer="DIAG human", reason="select review")
print("P6 human selects review w/ bounded conflict:", h.status, h.errors[:1])
if h.path:
    summarize("P6 adjudicated:", h)
    hp = json.loads((Path(h.path) / "record.json").read_text())["run_record"]["metadata"]["phase9"]
    sel = next(p for p in hp["positions"] if p["position_id"] == hp["final_position_id"])
    print("   final position conflicts:", [(c["scope"], c.get("proposition_id"), c["model_state"], c["host_state"]) for c in sel["phase8"]["model_host_conflicts"]], "final composite", sel["phase8"]["composite_state"])
    rep = (Path(h.path) / "report.md").read_text()
    print("   report:", [l.strip()[:200] for l in rep.splitlines() if "selected judgment" in l][:2])
# P6b: review drops the optional proposition entirely (different proposition set)
st = root / "state6b"
rv = execute_review(record, OfflineReviewProvider(raw(drop_opt=True)), base_dir=st, authorized=True, budget_calls=2)
d = rv.metadata["phase9"]
print("P6b review w/o optional:", d["route"], [(c["dimension"], c["field"], c["material"]) for c in d["conflicts"]][:4])
c = create_candidate(rv, output_root=root / "p6bc")
pid = next(p["position_id"] for p in d["positions"] if p["origin"] == "model_review")
h = review_candidate(Path(c.path), output_root=root / "p6bh", state_dir=st, selected_position_id=pid, reviewer="DIAG human", reason="select review")
print("P6b human selects review:", h.status, h.errors[:1])
