"""K11-style live conflict review on a throwaway authorization (MockTransport, test-key); inspect P9 records."""
import json, shutil
from pathlib import Path
import common
from common import OUT
from agent_arena import phase10_live as live
live.KNOWN_CLOSED_AUTHORIZATIONS = {}
import tests.test_phase10_live as T
from agent_arena.phase10_bundle import run_audit
from agent_arena.providers.anthropic_live import PROFILES
HAIKU3 = "claude-haiku-5-5@3"
root = Path(OUT) / "live_adj"; shutil.rmtree(root, ignore_errors=True)
task, raw = T._conflict_task("aa-diag-live-adj")
directory = T._authorize(root / "auth", [task], profiles=(HAIKU3,), ceiling=300_000)
transport = T.Transport(T.message(raw, request_id="req_p"), T.message(raw, request_id="req_c"))
with T._session(directory, transport) as session:
    prov = live.LiveAuditProvider(session, HAIKU3, task.id, "primary", PROFILES[HAIKU3].prompt_versions[0])
    res = run_audit(task, prov, output_root=root / "out", review_state=directory / "phase9-state")
print("status", res.status, "requests", len(transport.requests))
p9 = T._record(res.path)["run_record"]["metadata"]["phase9"]
for a in p9["attempts"]: print("attempt", a["kind"], a["status"], "| independence:", a.get("independence", "")[:200])
for d in p9["adjudications"]:
    print("adjudication", d["reviewer_type"], d["origin"], d["outcome"], "| provenance:", d["reviewer_provenance"], "| independence:", d["independence"])
rv = next(p for p in p9["positions"] if p["origin"] == "model_review")
print("review position provider/model:", rv["provider"], rv["model"])
md = (Path(res.path) / "report.md").read_text()
print("report mentions:", [l.strip()[:160] for l in md.splitlines() if "offline" in l.lower() and ("adjudic" in l.lower() or "recording" in l.lower() or "independence" in l.lower())][:6])
# gold check on wire
blob = json.dumps(transport.requests)
print("wire contains expected_answer/rubric keys:", any(k in blob for k in ("expected_answer", "reference_solution", "rubric")))
