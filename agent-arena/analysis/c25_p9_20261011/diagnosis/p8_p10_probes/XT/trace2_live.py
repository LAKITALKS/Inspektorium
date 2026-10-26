"""Trace 2: live path with an httpx transport double (throwaway authorization under XT), mandatory
conflict counterreview, then replay of the same run in place and from a copied directory (K1)."""
import json, sys, shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
import httpx
D = Path("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new")
sys.path.insert(0, str(D / "src")); sys.path.insert(0, str(D))
X = Path(__file__).parent
W = X / "out_trace2"; shutil.rmtree(W, ignore_errors=True); W.mkdir()
from agent_arena import phase10_live as live
live.KNOWN_CLOSED_AUTHORIZATIONS = {}  # isolate from the real pinned history (never touched)
from agent_arena.phase10_bundle import run_audit, inspect_bundle, release_candidate
from agent_arena.phase10_pipeline import reconstruct
from agent_arena.providers.anthropic_live import PROFILES
from agent_arena.runner import resolve_study_forensics_prompt
from agent_arena.schemas import RunRecord
from agent_arena.task_loader import load_task
from tests.test_phase8_9_conflict import set_model

H3 = "claude-haiku-5-5@3"
task = load_task(D / "examples/phase10/positive-task.json").model_copy(update={
    "id": "xt-live-conflict", "gold_label": "GOLD_SENTINEL_overclaim", "gold_summary": "GOLD_SENTINEL_summary",
    "curator_notes": "CURATOR_SENTINEL", "expected_answer": "EXPECTED_SENTINEL", "reference_solution": "REF_SENTINEL"})
data = json.loads((D / "examples/phase10/positive-recording.json").read_text())
set_model(data["forensic_record"], "unsupported")
raw = json.dumps(data)

def authorize(directory):
    directory.mkdir(parents=True)
    auth = {"schema": live.AUTH_SCHEMA, "authorization_id": "XT-THROWAWAY", "work_order": "diag",
            "issued_at": "2026-10-11T00:00:00+00:00",
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(), "status": "ACTIVE",
            "canonical_directory": str(directory.resolve()), "endpoint": "https://api.anthropic.com",
            "total_budget_microusd": 2_000_000, "max_generation_attempts": 40, "max_technical_retries": 4,
            "max_attempts_per_request": 2, "per_call_ceiling_microusd": 300_000,
            "allowed_profiles": {H3: PROFILES[H3].fingerprint()},
            "task_bindings": {task.id: live.task_sha256(task)},
            "slots": [live.slot_key(task.id, H3, k) for k in live.KINDS],
            "supersedes": {"state": "CLOSED_NOT_EXECUTABLE"}}
    (directory / "authorization.json").write_text(json.dumps(auth, indent=2))
    return directory

requests = []
def handler(request):
    requests.append(json.loads(request.content))
    body = {"id": f"msg_{len(requests)}", "type": "message", "role": "assistant", "model": "claude-haiku-5-5",
            "content": [{"type": "thinking", "thinking": "", "signature": "s"}, {"type": "text", "text": raw}],
            "stop_reason": "end_turn", "stop_sequence": None,
            "usage": {"input_tokens": 9000, "output_tokens": 3000, "cache_creation_input_tokens": 0,
                      "cache_read_input_tokens": 0}}
    return httpx.Response(200, json=body, headers={"request-id": f"req_{len(requests)}"})

auth_dir = authorize(W / "auth")
with live.LiveSession(auth_dir, mode="live", transport=httpx.MockTransport(handler), api_key="test-key") as s:
    prov = live.LiveAuditProvider(s, H3, task.id, "primary", PROFILES[H3].prompt_versions[0])
    res = run_audit(task, prov, output_root=W / "live_out", review_state=auth_dir / "phase9-state")
    ledger_summary = s.summary()

def describe(result):
    out = {"status": result.status, "path": bool(result.path), "errors": result.errors[:3]}
    if result.path:
        rec = RunRecord.model_validate(json.loads((Path(result.path) / "record.json").read_text())["run_record"])
        review, sel, ass, _ = reconstruct(rec)
        out["mode"] = json.loads((Path(result.path) / "record.json").read_text())["execution_mode"]
        out["p8"] = {k: ass.get(k) for k in ("technical_status", "composite_state", "model_composite_state", "host_composite_state")}
        out["p8_conflicts"] = [(c["scope"], c.get("proposition_id"), c["model_state"], c["host_state"]) for c in ass.get("model_host_conflicts", [])]
        out["p9"] = {k: review.get(k) for k in ("route", "mandatory", "review_state", "execution_status")}
        out["p9_attempts"] = [(a["kind"], a["status"], a.get("reason", "")[:90]) for a in review.get("attempts", [])]
        out["p9_positions"] = [(p["origin"], p.get("model")) for p in review.get("positions", [])]
        dec = json.loads((Path(result.path) / "decision.json").read_text())
        out["failed_controls"] = [c["control_id"] for c in dec["controls"] if c["outcome"] == "fail"]
        out["inspect_valid"] = inspect_bundle(Path(result.path)).valid
        md = (Path(result.path) / "report.md").read_text()
        out["report_lines_conflict"] = [l[:160] for l in md.splitlines() if "conflict" in l.lower()][:6]
    return out

live_view = describe(res)
sent = json.dumps(requests)
leak = {s: (s in sent) for s in ("GOLD_SENTINEL", "CURATOR_SENTINEL", "EXPECTED_SENTINEL", "REF_SENTINEL")}
systems = [r["system"] if isinstance(r["system"], str) else r["system"][0]["text"] for r in requests]
sys_versions = []
for sysmsg in systems:
    sys_versions.append(next((v for v in PROFILES[H3].prompt_versions if resolve_study_forensics_prompt(v) == sysmsg), "UNKNOWN"))
user0 = requests[0]["messages"][0]["content"]
claim_ok = task.prompt in user0 and task.context in user0
user1 = requests[1]["messages"][0]["content"] if len(requests) > 1 else ""
packet = json.loads(user1.split("Bound evidence packet:\n", 1)[1].rsplit("\n</task_context>", 1)[0]) if user1 else {}

# Replay in place (same canonical directory)
with live.LiveSession(auth_dir, mode="replay") as s:
    rp = live.ReplayProvider(s, H3, task.id, "primary", PROFILES[H3].prompt_versions[0])
    rres = run_audit(task, rp, output_root=W / "replay_out", review_state=W / "replay_state")
replay_view = describe(rres)

# K1: replay from a byte-identical copy at another path
copy = W / "auth_copy"; shutil.copytree(auth_dir, copy)
try:
    live.LiveSession(copy, mode="replay"); k1 = "replay from copy opened"
except Exception as exc:
    k1 = f"{type(exc).__name__}: {exc}"
# K1 bundle-level: is the replay bundle itself inspectable without the authorization dir?
moved = W / "replay_bundle_moved"; shutil.copytree(rres.path, moved)
k1_bundle = inspect_bundle(moved).model_dump()

result = {"live": live_view, "ledger": ledger_summary, "requests": len(requests), "provider_saw_systems": sys_versions,
          "claim_and_context_unchanged_in_user_message": claim_ok, "gold_leak": leak,
          "review_packet_keys": sorted(packet), "review_packet_conflicts": packet.get("model_host_conflicts"),
          "replay": replay_view, "replay_extra_requests": len(requests) - 2, "K1_replay_from_copy": k1,
          "K1_moved_bundle_inspect": k1_bundle}
(X / "trace2_summary.json").write_text(json.dumps(result, indent=1, default=str))
print(json.dumps(result, indent=1, default=str)[:6000])
