"""Canonical offline P10 entry -> P9 review (offline) -> crash/lost sidecar -> bundle + human review."""
import json, shutil
from pathlib import Path
import common
from common import OUT, set_model
from tests.test_phase8_9_conflict import example
import agent_arena.runner as runner
from agent_arena.phase9_runtime import OfflineReviewProvider, execute_review
from agent_arena.phase10_bundle import run_audit, create_candidate, review_candidate, release_candidate, inspect_bundle
from agent_arena.phase9_review import case_key
from agent_arena.schemas import RunRecord
root = Path(OUT) / "e2e_bundle"; shutil.rmtree(root, ignore_errors=True)
task, raw = example("positive", "unsupported")
res = run_audit(task, OfflineReviewProvider(raw), output_root=root / "c0")
rec = RunRecord.model_validate(json.loads((Path(res.path) / "record.json").read_text())["run_record"])
print("S0 run_audit:", res.status, rec.metadata["phase9"]["route"])
agree = json.loads(raw); set_model(agree["forensic_record"], "supported")
# S1 normal counterreview, bundle
st = root / "state_ok"
r = execute_review(rec, OfflineReviewProvider(json.dumps(agree)), base_dir=st, authorized=True, budget_calls=2)
c = create_candidate(r, output_root=root / "c1"); d = r.metadata["phase9"]
print("S1 after counterreview:", c.status, d["route"], d["execution_status"], [(a["kind"], a["status"]) for a in d["attempts"]])
rev_pid = next(p["position_id"] for p in d["positions"] if p["origin"] == "model_review")
h = review_candidate(Path(c.path), output_root=root / "c2", state_dir=st, selected_position_id=rev_pid, reviewer="DIAG human", reason="diag select review")
print("S2 human selects review position:", h.status, h.errors)
if h.path:
    rel = release_candidate(Path(h.path), output_root=root / "c3", reviewer="DIAG", reason="diag")
    print("S3 release:", rel.status)
# S4 crash during provider call, then lost sidecar
st2 = root / "state_crash"
real = runner.run_agent
runner.run_agent = lambda *a, **k: (_ for _ in ()).throw(KeyboardInterrupt("kill"))
try: execute_review(rec, OfflineReviewProvider(json.dumps(agree)), base_dir=st2, authorized=True, budget_calls=2)
except KeyboardInterrupt: pass
runner.run_agent = real
(st2 / "phase9" / f"{case_key(task)}.json").unlink()
r = execute_review(rec, OfflineReviewProvider(json.dumps(agree)), base_dir=st2, authorized=True, budget_calls=2)
c = create_candidate(r, output_root=root / "c4"); d = r.metadata["phase9"]
print("S4 crash+lost sidecar:", c.status, d["route"], "execution_status:", d["execution_status"], [(a["kind"], a["status"]) for a in d["attempts"]])
rep = (Path(c.path) / "report.md").read_text()
print("   report lines:", [l[:160] for l in rep.splitlines() if "Phase 9 review" in l or "Attempt" in l or "review execution" in l.lower()])
led = json.loads((st2 / "phase9" / f"{case_key(task)}.ledger.json").read_text())
print("   ledger attempts:", [(a["slot_key"], a["state"]) for a in led["attempts"]])
