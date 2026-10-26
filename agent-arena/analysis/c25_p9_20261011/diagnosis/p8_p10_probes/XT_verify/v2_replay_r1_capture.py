"""Gap probe: canonical replay (run_audit + ReplayProvider, and the CLI) of an R1-era live capture under 93cd64d.

Emulates the real -003 situation in a THROWAWAY schema-1.0 authorization under XT_verify: the primary slot of
LS-02 / claude-haiku-5-5@2 was generated live (here: MockTransport returning the byte-identical response body of
the tracked R1 capture attempt-002), and no review slot was ever generated (R1 ran under AA-P8/1.0, where this
answer routed HUMAN_REVIEW_REQUIRED). Then replay under the current code. No real path is opened or written.
"""
import json, shutil, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
import httpx
D = Path("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new")
sys.path.insert(0, str(D / "src"))
import agent_arena
assert str(D) in agent_arena.__file__
X = Path(__file__).parent
W = X / "out_v2"; shutil.rmtree(W, ignore_errors=True); W.mkdir()
from agent_arena import phase10_live as live
live.KNOWN_CLOSED_AUTHORIZATIONS = {}  # throwaway only; the real pinned history is never opened
from agent_arena.phase10_bundle import run_audit, inspect_bundle
from agent_arena.providers.anthropic_live import PROFILES
from agent_arena.runner import run_agent
from agent_arena.task_loader import load_task

H2 = "claude-haiku-5-5@2"
task = load_task(D / "analysis/live_smoke_20261011/live_run/tasks/LS-02.json")
real_auth = json.loads((D / "analysis/live_smoke_20261011/repair_r1/authorization.json").read_text())
capture = json.loads((D / "analysis/live_smoke_20261011/repair_r1/captures/attempt-002.json").read_bytes())
assert capture["slot_key"] == f"{task.id}|{H2}|primary"
out = {"task_binding_equals_real_003": real_auth["task_bindings"][task.id] == live.task_sha256(task),
       "real_003_has_review_caps": "review_caps" in real_auth, "real_003_schema": real_auth["schema"]}

adir = W / "auth"; adir.mkdir()
auth = {"schema": live.AUTH_SCHEMA, "authorization_id": "XTV-THROWAWAY-R1", "work_order": "diag",
        "issued_at": "2026-10-11T00:00:00+00:00",
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(), "status": "ACTIVE",
        "canonical_directory": str(adir.resolve()), "endpoint": "https://api.anthropic.com",
        "total_budget_microusd": 2_000_000, "max_generation_attempts": 40, "max_technical_retries": 4,
        "max_attempts_per_request": 2, "per_call_ceiling_microusd": 400_000,
        "allowed_profiles": {H2: PROFILES[H2].fingerprint()},
        "task_bindings": {task.id: live.task_sha256(task)},
        "slots": [live.slot_key(task.id, H2, k) for k in live.KINDS],
        "supersedes": {"state": "CLOSED_NOT_EXECUTABLE"}}
(adir / "authorization.json").write_text(json.dumps(auth, indent=2))

sent = []
def handler(request):
    sent.append(json.loads(request.content))
    return httpx.Response(200, json=capture["call"]["response_body"], headers={"request-id": "req_xtv"})

# 1) Live primary only (what R1 recorded): no review slot is generated.
with live.LiveSession(adir, mode="live", transport=httpx.MockTransport(handler), api_key="test-key") as s:
    prov = live.LiveAuditProvider(s, H2, task.id, "primary", PROFILES[H2].prompt_versions[0])
    primary = run_agent(prov, task, prompt_version=PROFILES[H2].prompt_versions[0])
out["live_requests"] = len(sent)
out["request_body_equals_real_capture_request"] = sent[0] == capture["call"]["request_body"]
out["primary_p8"] = {k: primary.phase8.get(k) for k in ("technical_status", "composite_state",
                                                       "model_composite_state", "host_composite_state")}
out["primary_p9_route"] = (primary.phase9 or {}).get("route")

def tree(d):
    return sorted(str(p.relative_to(d)) for p in d.rglob("*") if p.is_file())
before = tree(adir)
import hashlib
ledger_before = hashlib.sha256((adir / "ledger.json").read_bytes()).hexdigest()

# 2) Canonical replay through run_audit (review_state outside the authorization dir).
with live.LiveSession(adir, mode="replay") as s:
    rp = live.ReplayProvider(s, H2, task.id, "primary", PROFILES[H2].prompt_versions[0])
    res = run_audit(task, rp, output_root=W / "replay_out", review_state=W / "replay_state")
out["replay_run_audit"] = {"status": res.status, "path": res.path, "errors": [e[:400] for e in res.errors]}
out["replay_state_files"] = tree(W / "replay_state") if (W / "replay_state").exists() else []
out["replay_requests_after"] = len(sent) - 1

# 3) Same replay through the documented CLI.
from click.testing import CliRunner
from agent_arena.phase10_cli import audit
cli = CliRunner().invoke(audit, ["run", "--replay", "--task", str(D / "analysis/live_smoke_20261011/live_run/tasks/LS-02.json"),
                                 "--authorization-dir", str(adir), "--profile", H2,
                                 "--output-root", str(W / "cli_out")])
out["cli_exit"] = cli.exit_code
try:
    out["cli_output"] = json.loads(cli.output)
except ValueError:
    out["cli_output"] = cli.output[:800]
after = tree(adir)
out["auth_dir_files_added_by_cli_replay"] = sorted(set(after) - set(before))
out["ledger_unchanged"] = hashlib.sha256((adir / "ledger.json").read_bytes()).hexdigest() == ledger_before
print(json.dumps(out, indent=1, default=str))
(X / "v2_summary.json").write_text(json.dumps(out, indent=1, default=str))
