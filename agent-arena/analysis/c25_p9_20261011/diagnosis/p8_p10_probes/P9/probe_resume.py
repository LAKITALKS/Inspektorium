"""P2-P4: interruption/lost-sidecar/lost-ledger/stale AA-P9/1.0 state for the per-case review ledger."""
import json, shutil
from pathlib import Path
import common
from common import gold_case, set_model, raw_output, OUT
import agent_arena.phase9_runtime as rt
from agent_arena.phase9_runtime import OfflineReviewProvider, execute_review, replay_review
from agent_arena.phase9_review import case_key
from agent_arena.runner import run_agent
from agent_arena.evaluator import evaluate_run
from agent_arena.phase10_bundle import create_candidate
from agent_arena.schemas import RunRecord

task, payload = gold_case("supported", "unsupported")
rev_payload = json.loads(json.dumps(payload)); set_model(rev_payload, "supported")
def fresh(name):
    b = Path(OUT) / name; shutil.rmtree(b, ignore_errors=True); return b
record = evaluate_run(task, "run1", [run_agent(OfflineReviewProvider(raw_output(payload)), task)])
cid = case_key(task)

# P2: crash after the 'begun' save, while the provider call is in flight; then the sidecar is lost.
base = fresh("p2_state")
class Crash(Exception): pass
orig_run_agent = rt.__dict__.get("run_agent")
import agent_arena.runner as runner
real = runner.run_agent
def crashing(*a, **k): raise Crash("process killed during provider call")
runner.run_agent = crashing
try:
    execute_review(record, OfflineReviewProvider(raw_output(rev_payload)), base_dir=base, authorized=True, budget_calls=2)
except Crash as e:
    print("P2 crash:", e)
runner.run_agent = real
side = base / "phase9" / f"{cid}.json"
print("P2 sidecar attempts after crash:", [(a["kind"], a["status"]) for a in json.loads(side.read_text())["metadata"]["phase9"]["attempts"]])
r = execute_review(record, OfflineReviewProvider(raw_output(rev_payload)), base_dir=base, authorized=True, budget_calls=2)
d = r.metadata["phase9"]; print("P2a resume w/ sidecar:", [(a["kind"], a["status"]) for a in d["attempts"]], d["route"], d.get("execution_status"))
side.unlink()  # lose the outcome sidecar
r = execute_review(record, OfflineReviewProvider(raw_output(rev_payload)), base_dir=base, authorized=True, budget_calls=2)
d = r.metadata["phase9"]
print("P2b resume w/o sidecar:", [(a["kind"], a["status"], a["reason"]) for a in d["attempts"]], d["route"], "execution_status=", d.get("execution_status"))
out = create_candidate(r, output_root=Path(OUT) / "p2_bundle")
print("P2b bundle status:", out.status)
dec = json.loads((Path(out.path) / "decision.json").read_text()) if out.path else {}
rep = (Path(out.path) / "report.md").read_text() if out.path else ""
print("P2b report execution line:", [l for l in rep.splitlines() if "execution" in l.lower()][:3])

# P3: stale AA-P9/1.0 sidecar
base = fresh("p3_state")
r = execute_review(record, OfflineReviewProvider(raw_output(rev_payload)), base_dir=base, authorized=True, budget_calls=2)
side = base / "phase9" / f"{cid}.json"
raw = json.loads(side.read_text()); raw["metadata"]["phase9"]["contract_version"] = "AA-P9/1.0"
for res in raw["results"]: res["agent_result"]["phase9"]["contract_version"] = "AA-P9/1.0"
side.write_text(json.dumps(raw))
for kind in ("counterreview", "stability"):
    try:
        execute_review(record, OfflineReviewProvider(raw_output(rev_payload)), base_dir=base, authorized=True, budget_calls=2, kind=kind)
        print("P3", kind, "NO ERROR")
    except Exception as e:
        print("P3", kind, type(e).__name__, e)
try:
    print("P3 replay route:", replay_review(task, base_dir=base).metadata["phase9"].get("history_validation"))
except Exception as e: print("P3 replay", type(e).__name__, e)
# P3b: stale 1.0 sidecar AND ledger bound to AA-P9/1.0 after sidecar removal
led = base / "phase9" / f"{cid}.ledger.json"; L = json.loads(led.read_text()); L["binding"]["contract_version"] = "AA-P9/1.0"; led.write_text(json.dumps(L)); side.unlink()
try:
    execute_review(record, OfflineReviewProvider(raw_output(rev_payload)), base_dir=base, authorized=True, budget_calls=2, kind="stability")
    print("P3b NO ERROR")
except Exception as e: print("P3b", type(e).__name__, e)

# P4: ledger lost after a completed counterreview
base = fresh("p4_state")
r = execute_review(record, OfflineReviewProvider(raw_output(rev_payload)), base_dir=base, authorized=True, budget_calls=2)
(base / "phase9" / f"{cid}.ledger.json").unlink()
r2 = execute_review(r, OfflineReviewProvider(raw_output(rev_payload)), base_dir=base, authorized=True, budget_calls=2, kind="stability")
print("P4 lost ledger:", [(a["kind"], a["status"], a["reason"][:70]) for a in r2.metadata["phase9"]["attempts"]])
# P4b: both sidecar and ledger lost -> documented file-manipulation limit
base2 = fresh("p4b_state")
r = execute_review(record, OfflineReviewProvider(raw_output(rev_payload)), base_dir=base2, authorized=True, budget_calls=2)
shutil.rmtree(base2 / "phase9")
r3 = execute_review(record, OfflineReviewProvider(raw_output(rev_payload)), base_dir=base2, authorized=True, budget_calls=2)
print("P4b both lost (bare record):", [(a["kind"], a["status"]) for a in r3.metadata["phase9"]["attempts"]])
shutil.rmtree(base2 / "phase9")
r4 = execute_review(r, OfflineReviewProvider(raw_output(rev_payload)), base_dir=base2, authorized=True, budget_calls=2)
print("P4c both lost (returned record carries history):", [(a["kind"], a["status"]) for a in r4.metadata["phase9"]["attempts"]])
