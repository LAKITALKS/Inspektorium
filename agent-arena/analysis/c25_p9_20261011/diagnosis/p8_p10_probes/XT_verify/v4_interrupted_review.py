"""Check the row's claim 'Replay of a run whose review was interrupted ends as UNRESOLVED (fail-closed)'.

THROWAWAY schema-1.0 authorization under XT_verify, profile haiku@3, MockTransport, api_key='test-key'.
A child process runs the live audit; the transport answers the primary with a material model/host conflict and
crashes the process (os._exit) when the counterreview request is about to be sent, i.e. after its reservation and
before any capture. The parent then (a) retries live, (b) replays like the CLI (fresh review state), (c) replays
with the live Phase-9 state directory. No real path, no network.
"""
import json, os, shutil, subprocess, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
D = Path("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new")
sys.path.insert(0, str(D / "src")); sys.path.insert(0, str(D))
X = Path(__file__).parent
H3 = "claude-haiku-5-5@3"

def setup(W):
    from agent_arena import phase10_live as live
    from agent_arena.providers.anthropic_live import PROFILES
    from agent_arena.task_loader import load_task
    task = load_task(D / "examples/phase10/positive-task.json").model_copy(update={"id": "xtv-interrupted"})
    adir = W / "auth"; adir.mkdir(parents=True)
    auth = {"schema": live.AUTH_SCHEMA, "authorization_id": "XTV-INTERRUPT", "work_order": "diag",
            "issued_at": "2026-10-11T00:00:00+00:00",
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(), "status": "ACTIVE",
            "canonical_directory": str(adir.resolve()), "endpoint": "https://api.anthropic.com",
            "total_budget_microusd": 2_000_000, "max_generation_attempts": 40, "max_technical_retries": 4,
            "max_attempts_per_request": 2, "per_call_ceiling_microusd": 400_000,
            "allowed_profiles": {H3: PROFILES[H3].fingerprint()},
            "task_bindings": {task.id: live.task_sha256(task)},
            "slots": [live.slot_key(task.id, H3, k) for k in live.KINDS],
            "supersedes": {"state": "CLOSED_NOT_EXECUTABLE"}}
    (adir / "authorization.json").write_text(json.dumps(auth))
    return task, adir

def conflict_raw():
    from tests.test_phase8_9_conflict import set_model
    data = json.loads((D / "examples/phase10/positive-recording.json").read_text())
    set_model(data["forensic_record"], "unsupported")
    return json.dumps(data)

if len(sys.argv) > 1 and sys.argv[1] == "child":
    import httpx
    from agent_arena import phase10_live as live
    live.KNOWN_CLOSED_AUTHORIZATIONS = {}
    from agent_arena.phase10_bundle import run_audit
    from agent_arena.providers.anthropic_live import PROFILES
    from agent_arena.task_loader import load_task
    adir = Path(sys.argv[2])
    task = load_task(D / "examples/phase10/positive-task.json").model_copy(update={"id": "xtv-interrupted"})
    raw = conflict_raw(); n = []
    def handler(request):
        n.append(1)
        if len(n) == 2:
            os._exit(17)  # process crash after the counterreview reservation, before any capture
        body = {"id": "msg_1", "type": "message", "role": "assistant", "model": "claude-haiku-5-5",
                "content": [{"type": "text", "text": raw}], "stop_reason": "end_turn", "stop_sequence": None,
                "usage": {"input_tokens": 9000, "output_tokens": 3000}}
        return httpx.Response(200, json=body, headers={"request-id": "req_1"})
    with live.LiveSession(adir, mode="live", transport=httpx.MockTransport(handler), api_key="test-key") as s:
        prov = live.LiveAuditProvider(s, H3, task.id, "primary", PROFILES[H3].prompt_versions[0])
        run_audit(task, prov, output_root=adir.parent / "live_out", review_state=adir / "phase9-state")
    sys.exit(0)

W = X / "out_v4"; shutil.rmtree(W, ignore_errors=True)
task, adir = setup(W)
child = subprocess.run([sys.executable, "-B", "-I", __file__, "child", str(adir)], capture_output=True, text=True)
out = {"child_exit": child.returncode, "child_stderr_tail": child.stderr[-300:]}
from agent_arena import phase10_live as live
live.KNOWN_CLOSED_AUTHORIZATIONS = {}
from agent_arena.phase10_bundle import run_audit
from agent_arena.providers.anthropic_live import PROFILES
ledger = json.loads((adir / "ledger.json").read_text())
out["ledger_attempts"] = [(a["slot_key"].split("|")[2], a["state"]) for a in ledger["attempts"]]
out["ledger_terminal"] = [k.split("|")[2] for k in ledger["terminal_keys"]]
out["live_bundles_written"] = sorted(p.name for p in (W / "live_out").iterdir()) if (W / "live_out").exists() else []
# (a) live retry of the same case
import httpx
with live.LiveSession(adir, mode="live", transport=httpx.MockTransport(lambda r: (_ for _ in ()).throw(AssertionError("no send"))),
                      api_key="test-key") as s:
    out["live_resume_unresolved"] = list(s.unresolved)
    prov = live.LiveAuditProvider(s, H3, task.id, "primary", PROFILES[H3].prompt_versions[0])
    r = run_audit(task, prov, output_root=W / "live_retry", review_state=adir / "phase9-state")
    out["live_retry"] = {"status": r.status, "errors": r.errors[:1]}
# (b) replay like the CLI: fresh review state
with live.LiveSession(adir, mode="replay") as s:
    rp = live.ReplayProvider(s, H3, task.id, "primary", PROFILES[H3].prompt_versions[0])
    r = run_audit(task, rp, output_root=W / "replay_fresh", review_state=W / "rs_fresh")
    out["replay_fresh_state"] = {"status": r.status, "path": bool(r.path), "errors": [e[:300] for e in r.errors[:1]]}
# (c) replay with the live Phase-9 state
try:
    with live.LiveSession(adir, mode="replay") as s:
        rp = live.ReplayProvider(s, H3, task.id, "primary", PROFILES[H3].prompt_versions[0])
        r = run_audit(task, rp, output_root=W / "replay_livestate", review_state=adir / "phase9-state")
        out["replay_live_state"] = {"status": r.status, "path": bool(r.path), "errors": [e[:300] for e in r.errors[:1]]}
except Exception as exc:
    out["replay_live_state"] = f"{type(exc).__name__}: {str(exc)[:300]}"
print(json.dumps(out, indent=1, default=str))
(X / "v4_summary.json").write_text(json.dumps(out, indent=1, default=str))
