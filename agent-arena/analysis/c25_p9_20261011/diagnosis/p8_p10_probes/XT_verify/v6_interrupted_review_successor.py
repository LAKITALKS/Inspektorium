"""Same probe as v4 under a schema-1.1 successor with review caps (the only schema allowed for new live budgets).

All authorizations are THROWAWAY under XT_verify/out_v6 (predecessor closed + pinned only in this process's
KNOWN_CLOSED_AUTHORIZATIONS, which starts empty). MockTransport, api_key='test-key'. The child process crashes when
the counterreview request is about to be sent (after review_cap claim and reservation, before any capture).
"""
import json, os, shutil, subprocess, sys
from pathlib import Path
D = Path("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new")
sys.path.insert(0, str(D / "src")); sys.path.insert(0, str(D))
X = Path(__file__).parent
from agent_arena import phase10_live as live
live.KNOWN_CLOSED_AUTHORIZATIONS = {}
import tests.test_phase10_live as T  # helpers only; the module's autouse fixture is not active outside pytest
from agent_arena.phase10_bundle import run_audit
assert all("__LOCAL_HOME__/Documents/Projects/agent-arena" not in str(p) for p in [X])

if len(sys.argv) > 1 and sys.argv[1] == "child":
    import httpx
    succ = Path(sys.argv[2]); pins = json.loads(Path(sys.argv[3]).read_text())
    live.KNOWN_CLOSED_AUTHORIZATIONS.update(pins)
    task, raw = T._conflict_task("xtv-interrupted-succ")
    n = []
    def handler(request):
        n.append(1)
        if len(n) == 2:
            os._exit(17)
        return T.message(raw, request_id="req_p")
    with live.LiveSession(succ, mode="live", transport=httpx.MockTransport(handler), api_key="test-key") as s:
        prov = live.LiveAuditProvider(s, T.HAIKU3, task.id, "primary", T.R2)
        run_audit(task, prov, output_root=succ.parent / "live_out", review_state=succ / "phase9-state")
    sys.exit(0)

W = X / "out_v6"; shutil.rmtree(W, ignore_errors=True); W.mkdir()
pred = T._closed_predecessor(W, "pred")
assert pred["directory"].startswith(str(W.resolve()))
T._pin(pred)
pins = dict(live.KNOWN_CLOSED_AUTHORIZATIONS)
(W / "pins.json").write_text(json.dumps(pins))
task, raw = T._conflict_task("xtv-interrupted-succ")
succ = T._successor(W, [task], [pred], budget=1_500_000, profiles=(T.HAIKU3,))
child = subprocess.run([sys.executable, "-B", "-I", __file__, "child", str(succ), str(W / "pins.json")],
                       capture_output=True, text=True)
out = {"child_exit": child.returncode, "child_stderr_tail": child.stderr[-400:]}
ledger = json.loads((succ / "ledger.json").read_text())
out["schema"] = json.loads((succ / "authorization.json").read_text())["schema"]
out["ledger_attempts"] = [(a["slot_key"].split("|")[2], a["state"]) for a in ledger["attempts"]]
out["review_cap_claims"] = [k.split("|")[2] for k in ledger.get("review_cap_claims", [])]
with live.LiveSession(succ, mode="replay") as s:
    rp = live.ReplayProvider(s, T.HAIKU3, task.id, "primary", T.R2)
    r = run_audit(task, rp, output_root=W / "replay_fresh", review_state=W / "rs_fresh")
out["replay_fresh_state"] = {"status": r.status, "path": bool(r.path), "errors": [e[:300] for e in r.errors[:1]]}
print(json.dumps(out, indent=1, default=str))
(X / "v6_summary.json").write_text(json.dumps(out, indent=1, default=str))
