"""Replay of a schema-1.0 live run whose live routing had no review, but whose re-evaluation now routes
REVIEW_RECOMMENDED (the R1 situation: 10/12 captures, analysis/c25_p9_20261011/historical_reanalysis.json).
Throwaway authorization under scratch; httpx MockTransport; api_key='test-key'; KNOWN_CLOSED={}."""
import json, shutil
from pathlib import Path
import common
from common import OUT
from agent_arena import phase10_live as live
live.KNOWN_CLOSED_AUTHORIZATIONS = {}
import tests.test_phase10_live as T
import agent_arena.phase9_pipeline as p9p
from agent_arena.phase10_bundle import run_audit
root = Path(OUT) / "replay_nocaps"; shutil.rmtree(root, ignore_errors=True)
assert str(root).startswith("/private/tmp/")
task, raw = T._conflict_task("aa-diag-nocaps")
directory = T._authorize(root / "auth", [task], profiles=(T.HAIKU,))
auth = json.loads((directory / "authorization.json").read_text()); print("schema", auth["schema"], "review_caps" in auth)
transport = T.Transport(T.message(raw, request_id="req_p"))
real = p9p.refresh_run_phase9
def historical_route(record):   # simulate the AA-P8/1.0-era live routing (C25 block): no review triggered
    out = real(record); d = dict(out.metadata.get("phase9", {})); d["route"] = "HUMAN_REVIEW_REQUIRED"
    return out.model_copy(update={"metadata": {**out.metadata, "phase9": d}})
p9p.refresh_run_phase9 = historical_route
with T._session(directory, transport) as session:
    prov = live.LiveAuditProvider(session, T.HAIKU, task.id, "primary", T.P8)
    res = run_audit(task, prov, output_root=root / "live_out", review_state=directory / "phase9-state")
p9p.refresh_run_phase9 = real
lrec = T._record(res.path)["run_record"]["metadata"]["phase9"]
print("LIVE:", res.status, "requests", len(transport.requests), "attempts", lrec.get("attempts"), "route", lrec["route"])
led = json.loads((directory / "ledger.json").read_text())
print("live ledger slots:", [a["slot_key"].split("|")[2] for a in led["attempts"]], "claims", led.get("review_cap_claims"))
import agent_arena.phase10_bundle as B
captured = {}
orig_cc = B.create_candidate
def cap(record, **kw):
    captured["r"] = record; return orig_cc(record, **kw)
B.create_candidate = cap
with T._session(directory, None, mode="replay") as session:
    prov = live.ReplayProvider(session, T.HAIKU, task.id, "primary", T.P8)
    rep = run_audit(task, prov, output_root=root / "replay_out", review_state=root / "replay_state")
print("REPLAY RESULT:", rep.status, rep.errors)
r9 = captured["r"].metadata["phase9"]
print("  P9 attempts:", [(a["kind"], a["status"], a["reason"]) for a in r9["attempts"]], "route", r9["route"], "exec", r9.get("execution_status"))
for p in r9["positions"]:
    if p["origin"] != "original":
        ev = p["agent_result"].get("execution_evidence") or {}
        print("  review carrier:", p["origin"], {k: ev.get(k) for k in ("current_execution","request_sent","denial_reason","new_generation","attempt_ids","replay_of_unsent_request")})
print("  ledger after replay unchanged:", json.loads((directory / "ledger.json").read_text()) == led)
raise SystemExit
