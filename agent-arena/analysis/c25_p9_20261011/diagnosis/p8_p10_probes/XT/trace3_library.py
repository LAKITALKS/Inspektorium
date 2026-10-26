"""Trace 3 + counter-case: library case through (a) the documented P4 harness run_single with the
legacy Anthropic provider (SDK stubbed, no network) and (b) the canonical P10 live path with a
transport double. Records what the provider sees, what P8 binds against, and P9/P10 outcomes."""
import json, sys, shutil, types
from datetime import datetime, timedelta, timezone
from pathlib import Path
import httpx
D = Path("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new")
sys.path.insert(0, str(D / "src"))
X = Path(__file__).parent
W = X / "out_trace3"; shutil.rmtree(W, ignore_errors=True); W.mkdir()
from agent_arena import phase10_live as live
live.KNOWN_CLOSED_AUTHORIZATIONS = {}
from agent_arena.task_loader import load_task
from agent_arena.run_library import run_single
from agent_arena.providers.anthropic import AnthropicProvider
from agent_arena.providers.anthropic_live import PROFILES, build_user_message
from agent_arena.phase10_pipeline import preflight, reconstruct
from agent_arena.phase10_bundle import run_audit
from agent_arena.runner import resolve_study_forensics_prompt, STUDY_FORENSICS_PROMPT_VERSION_PHASE8
from agent_arena.schemas import RunRecord
import anthropic

case_file = D / "tasks/study_forensics/case045_inflammation_marker_heart.yaml"
task = load_task(case_file)
CUR = "primary forensic finding is rhetorical inflation (overclaim)"

# A recorded answer that follows the P8 prompt literally: it quotes task.context as source "context".
claim = task.prompt
ctx_quote = "hard clinical outcomes (heart attacks) were never measured"
assert ctx_quote in task.context
base = json.loads((D / "examples/phase10/negative-recording.json").read_text())

# ---- (a) P4 library harness, legacy provider, SDK stubbed
seen = {}
class _Msgs:
    def create(self, **kw):
        seen.update(kw)
        return types.SimpleNamespace(content=[types.SimpleNamespace(text=json.dumps(base))], stop_reason="end_turn",
                                     usage=types.SimpleNamespace(input_tokens=1, output_tokens=1))
class _Client:
    def __init__(self, **kw): self.messages = _Msgs()
anthropic.Anthropic = _Client
row = run_single(AnthropicProvider(model="stub-model"), case_file, task, 0, "xt-lib")
user_sent = seen["messages"][0]["content"]
sys_sent = seen["system"]
lib = {"system_prompt_is_v3_phase8": sys_sent == resolve_study_forensics_prompt(STUDY_FORENSICS_PROMPT_VERSION_PHASE8),
       "system_prompt_mentions_task_context": "context for task.context" in sys_sent,
       "user_message_equals_prompt_only": user_sent == task.prompt,
       "context_delivered": task.context.strip()[:40] in user_sent,
       "p8_status": (row["phase8"] or {}).get("technical_status"),
       "p8_reasons_head": (row["phase8"] or {}).get("reasons", [])[:2],
       "p9_route": (row["phase9"] or {}).get("route"),
       "record_keys": sorted(row)}

# ---- (b) canonical P10 path with the same library case
p10 = {"preflight_errors": preflight(task)}
msg = build_user_message(task)
p10["live_user_message_contains_curator_context"] = CUR in msg
p10["live_user_message_contains_gold_fields"] = any(s in msg for s in (task.reference_solution.strip()[:40], task.gold_justification.strip()[:40]))

H3 = "claude-haiku-5-5@3"
adir = W / "auth"; adir.mkdir()
auth = {"schema": live.AUTH_SCHEMA, "authorization_id": "XT-LIB", "work_order": "diag",
        "issued_at": "2026-10-11T00:00:00+00:00", "expires_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "status": "ACTIVE", "canonical_directory": str(adir.resolve()), "endpoint": "https://api.anthropic.com",
        "total_budget_microusd": 2_000_000, "max_generation_attempts": 40, "max_technical_retries": 4,
        "max_attempts_per_request": 2, "per_call_ceiling_microusd": 300_000,
        "allowed_profiles": {H3: PROFILES[H3].fingerprint()}, "task_bindings": {task.id: live.task_sha256(task)},
        "slots": [live.slot_key(task.id, H3, k) for k in live.KINDS], "supersedes": {"state": "CLOSED_NOT_EXECUTABLE"}}
(adir / "authorization.json").write_text(json.dumps(auth))
bodies = []
def handler(request):
    bodies.append(json.loads(request.content))
    body = {"id": "m", "type": "message", "role": "assistant", "model": "claude-haiku-5-5",
            "content": [{"type": "text", "text": json.dumps(base)}], "stop_reason": "end_turn", "stop_sequence": None,
            "usage": {"input_tokens": 100, "output_tokens": 100}}
    return httpx.Response(200, json=body, headers={"request-id": "req_x"})
with live.LiveSession(adir, mode="live", transport=httpx.MockTransport(handler), api_key="test-key") as s:
    prov = live.LiveAuditProvider(s, H3, task.id, "primary", PROFILES[H3].prompt_versions[0])
    res = run_audit(task, prov, output_root=W / "out", review_state=adir / "phase9-state")
p10["live_status"] = res.status
p10["live_requests"] = len(bodies)
p10["curator_context_reached_provider"] = any(CUR in json.dumps(b) for b in bodies)
if res.path:
    md = (Path(res.path) / "report.md").read_text()
    p10["report_quotes_curator_context_as_captured_source"] = CUR in md
out = {"library_harness": lib, "p10_live_with_library_case": p10}
(X / "trace3_summary.json").write_text(json.dumps(out, indent=1, default=str))
print(json.dumps(out, indent=1, default=str))
