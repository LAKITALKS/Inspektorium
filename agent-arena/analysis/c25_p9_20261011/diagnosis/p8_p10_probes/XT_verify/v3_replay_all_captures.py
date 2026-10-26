"""Extend v2 to all 24 tracked live captures (-002 rev.1 and -003 R1), each in its own THROWAWAY schema-1.0
authorization under XT_verify: live primary only via MockTransport returning the byte-identical captured response
body (what the real run recorded), then canonical replay via run_audit under the current code (93cd64d).
No real authorization directory is opened, no network, api_key='test-key'."""
import hashlib, json, shutil, sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
import httpx
D = Path("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new")
sys.path.insert(0, str(D / "src"))
import agent_arena
assert str(D) in agent_arena.__file__
X = Path(__file__).parent
W = X / "out_v3"; shutil.rmtree(W, ignore_errors=True); W.mkdir()
from agent_arena import phase10_live as live
live.KNOWN_CLOSED_AUTHORIZATIONS = {}
from agent_arena.phase10_bundle import run_audit, inspect_bundle
from agent_arena.providers.anthropic_live import PROFILES
from agent_arena.runner import run_agent
from agent_arena.schemas import RunRecord
from agent_arena.task_loader import load_task

BASE = D / "analysis/live_smoke_20261011"
rows = []
for run in ("live_run", "repair_r1"):
    real_auth = json.loads((BASE / run / "authorization.json").read_text())
    ledger = json.loads((BASE / run / "ledger.json").read_text())
    for attempt in ledger["attempts"]:
        capture = json.loads((BASE / run / "captures" / f"{attempt['attempt_id']}.json").read_bytes())
        task_id, profile, kind = capture["slot_key"].split("|")
        case = task_id.rsplit("-", 2)[-2] + "-" + task_id.rsplit("-", 1)[-1]
        task = load_task(BASE / "live_run/tasks" / f"{case}.json")
        adir = W / f"{run}_{attempt['attempt_id']}"; adir.mkdir()
        auth = {"schema": live.AUTH_SCHEMA, "authorization_id": f"XTV-{run}-{attempt['attempt_id']}", "work_order": "diag",
                "issued_at": "2026-10-11T00:00:00+00:00",
                "expires_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(), "status": "ACTIVE",
                "canonical_directory": str(adir.resolve()), "endpoint": "https://api.anthropic.com",
                "total_budget_microusd": 2_000_000, "max_generation_attempts": 40, "max_technical_retries": 4,
                "max_attempts_per_request": 2, "per_call_ceiling_microusd": 1_000_000,
                "allowed_profiles": {profile: PROFILES[profile].fingerprint()},
                "task_bindings": {task.id: live.task_sha256(task)},
                "slots": [live.slot_key(task.id, profile, k) for k in live.KINDS],
                "supersedes": {"state": "CLOSED_NOT_EXECUTABLE"}}
        (adir / "authorization.json").write_text(json.dumps(auth))
        sent = []
        def handler(request, capture=capture, sent=sent):
            sent.append(json.loads(request.content))
            return httpx.Response(200, json=capture["call"]["response_body"], headers={"request-id": "req_xtv"})
        with live.LiveSession(adir, mode="live", transport=httpx.MockTransport(handler), api_key="test-key") as s:
            prov = live.LiveAuditProvider(s, profile, task.id, "primary", PROFILES[profile].prompt_versions[0])
            primary = run_agent(prov, task, prompt_version=PROFILES[profile].prompt_versions[0])
        with live.LiveSession(adir, mode="replay") as s:
            rp = live.ReplayProvider(s, profile, task.id, "primary", PROFILES[profile].prompt_versions[0])
            res = run_audit(task, rp, output_root=adir.parent / f"{adir.name}_out", review_state=adir.parent / f"{adir.name}_rs")
        row = {"run": run, "attempt": attempt["attempt_id"], "profile": profile, "case": case,
               "task_binding_equals_real": real_auth["task_bindings"].get(task.id) == live.task_sha256(task),
               "request_identical_to_real": sent[0] == capture["call"]["request_body"],
               "p8": primary.phase8.get("technical_status"), "route": (primary.phase9 or {}).get("route"),
               "replay_status": res.status, "bundle": bool(res.path),
               "error_head": (res.errors[0][:140] if res.errors else None)}
        if res.path:
            rec = json.loads((Path(res.path) / "record.json").read_text())
            row["mode"] = rec["execution_mode"]
            row["inspect_valid"] = inspect_bundle(Path(res.path)).valid
        rows.append(row)
summary = {"by_run_status": Counter(f"{r['run']}:{r['replay_status']}" for r in rows),
           "all_requests_identical_to_real": all(r["request_identical_to_real"] for r in rows),
           "all_task_bindings_equal_real": all(r["task_binding_equals_real"] for r in rows),
           "rows": rows}
print(json.dumps(summary, indent=1, default=str))
(X / "v3_summary.json").write_text(json.dumps(summary, indent=1, default=str))
