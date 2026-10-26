import json, shutil, sys
from pathlib import Path
import common
from common import gold_case, set_model, raw_output, OUT
from agent_arena.phase9_runtime import OfflineReviewProvider, execute_review, replay_review, submit_human_review
from agent_arena.phase9_pipeline import refresh_run_phase9
from agent_arena.runner import run_agent
from agent_arena.evaluator import evaluate_run
base = Path(OUT) / "e2e_state"; shutil.rmtree(base, ignore_errors=True)
task, payload = gold_case("supported", "unsupported")   # material model/host conflict
prim = OfflineReviewProvider(raw_output(payload))
record = evaluate_run(task, "run1", [run_agent(prim, task)])
p9 = refresh_run_phase9(record).metadata["phase9"]
print("T0 initial route", p9["route"], "mandatory", p9["mandatory"], "triggers", sorted({t["code"] for t in p9["triggers"]}))
rev_payload = json.loads(json.dumps(payload)); set_model(rev_payload, "supported")  # reviewer agrees with host
rev = OfflineReviewProvider(raw_output(rev_payload))
r1 = execute_review(record, rev, base_dir=base, authorized=True, budget_calls=2, kind="counterreview")
d = r1.metadata["phase9"]
print("T1 counterreview attempts", [(a["kind"], a["status"]) for a in d["attempts"]], "route", d["route"], "exec", d.get("execution_status"))
print("   conflicts", [(c["dimension"], c["field"], c["material"]) for c in d["conflicts"]])
print("   independence:", d["attempts"][0]["independence"][:80])
req = rev.requests[0]
blob = json.dumps(req)
print("   prompt_version in sys prompt? r2-review:", "p9" in req["system_prompt"][:0] , "| gold leak:", [g for g in ["GOLD_SENTINEL"] if g in blob])
print("   claim verbatim:", task.prompt in req["task"]["prompt"], "context verbatim:", task.context in req["task"]["context"])
print("   review task gold fields:", {k: req["task"][k] for k in ("expected_answer","reference_solution","rubric","key_insights")})
stab = OfflineReviewProvider(raw_output(rev_payload))
r2 = execute_review(r1, stab, base_dir=base, authorized=True, budget_calls=2, kind="stability")
d = r2.metadata["phase9"]
print("T2 stability attempts", [(a["kind"], a["status"], a["reason"][:60]) for a in d["attempts"]], "route", d["route"])
review_pid = next(p["position_id"] for p in d["positions"] if p["origin"] == "model_review")
h = submit_human_review(r2, base_dir=base, selected_position_id=review_pid, reviewer_provenance="DIAG human", reason="diag")
d = h.metadata["phase9"]
print("T3 human route", d["route"], "review_state", d["review_state"], "final", d.get("final_position_id") == review_pid,
      "conflict resolutions", [c["resolution"] for c in d["conflicts"]])
rp = replay_review(task, base_dir=base).metadata["phase9"]
print("T4 replay equal:", rp == d)
print("ledger:", json.loads((base/"phase9"/(d["case_id"]+".ledger.json")).read_text())["attempts"].__len__())
print("primary gold leak:", "GOLD_SENTINEL" in json.dumps(prim.requests))
