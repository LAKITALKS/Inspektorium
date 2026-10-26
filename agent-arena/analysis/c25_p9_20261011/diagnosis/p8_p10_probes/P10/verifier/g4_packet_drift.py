"""G2: live review executed (scratch 1.0 authorization, MockTransport), then replay under code whose review
packet differs by one key (in-process build_challenge patch simulating a later code revision)."""
import sys, shutil
from pathlib import Path
D = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new"
S = Path("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_p8_p10/P10/verifier/g4")
sys.path.insert(0, D + "/src"); sys.path.insert(0, D)
shutil.rmtree(S, ignore_errors=True); S.mkdir(parents=True)
from agent_arena import phase10_live as live
live.KNOWN_CLOSED_AUTHORIZATIONS = {}
import tests.test_phase10_live as T
from agent_arena.phase10_bundle import run_audit
from agent_arena import phase9_runtime as rt
H3 = "claude-haiku-5-5@3"; R2 = T.PROFILES[H3].prompt_versions[0]
task, raw = T._conflict_task("aa-g4-drift")
auth = T._authorize(S / "auth", [task], profiles=(H3,), ceiling=300_000)
tr = T.Transport(T.message(raw, request_id="req_p"), T.message(raw, request_id="req_c"))
with T._session(auth, tr) as s:
    res = run_audit(task, live.LiveAuditProvider(s, H3, task.id, "primary", R2), output_root=S / "out", review_state=auth / "phase9-state")
print("live:", res.status, "requests", len(tr.requests))
import httpx
httpx.Client.send = lambda *a, **k: (_ for _ in ()).throw(AssertionError("network attempted"))
with live.LiveSession(auth, mode="replay") as s:
    r1 = run_audit(task, live.ReplayProvider(s, H3, task.id, "primary", R2), output_root=S / "rep_same", review_state=S / "rs1")
print("replay, same code:", r1.status)
orig = rt.build_challenge
def drifted(task, position, additional_positions=()):
    p = orig(task, position, additional_positions); p["packet_note"] = "later code revision"; return p
rt.build_challenge = drifted
with live.LiveSession(auth, mode="replay") as s:
    r2 = run_audit(task, live.ReplayProvider(s, H3, task.id, "primary", R2), output_root=S / "rep_drift", review_state=S / "rs2")
print("replay, review packet changed:", r2.status, [e[:220] for e in r2.errors[:1]])
