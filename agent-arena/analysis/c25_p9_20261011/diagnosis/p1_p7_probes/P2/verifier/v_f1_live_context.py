"""Verifier probe for P2-F1 (independent of the diagnoser's helpers). No network: httpx.MockTransport, dummy key.
A: library case001 unchanged -> audit validate + live run_audit; what reaches the transport?
B: P9 counterreview on the live path: does curator text in task.context reach the review request too?"""
import sys, os, json, tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
BASE = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
sys.path.insert(0, BASE + "/src")
os.environ.pop("ANTHROPIC_API_KEY", None)
import httpx
import agent_arena
assert agent_arena.__file__.startswith(BASE), agent_arena.__file__
from click.testing import CliRunner
from agent_arena.phase10_cli import audit
from agent_arena.task_loader import load_task
from agent_arena import phase10_live as live
from agent_arena.providers.anthropic_live import PROFILES, build_user_message
from agent_arena.phase10_bundle import run_audit
from agent_arena.runner import STUDY_FORENSICS_PROMPT_VERSION_PHASE8 as P8
HAIKU = "claude-haiku-5-5@1"
OUT = Path(tempfile.mkdtemp(prefix="vf1_", dir=str(Path(__file__).parent)))

def authorize(directory, tasks):
    directory.mkdir(parents=True)
    auth = {"schema": live.AUTH_SCHEMA, "authorization_id": "VERIFIER-AUTH", "work_order": "verifier probe",
            "issued_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(), "status": "ACTIVE",
            "canonical_directory": str(directory.resolve()), "endpoint": "https://api.anthropic.com",
            "total_budget_microusd": 2_000_000, "max_generation_attempts": 40, "max_technical_retries": 4,
            "max_attempts_per_request": 2, "per_call_ceiling_microusd": 400_000,
            "allowed_profiles": {HAIKU: PROFILES[HAIKU].fingerprint()},
            "task_bindings": {t.id: live.task_sha256(t) for t in tasks},
            "slots": [live.slot_key(t.id, HAIKU, k) for t in tasks for k in live.KINDS],
            "supersedes": {"state": "CLOSED_NOT_EXECUTABLE"}}
    (directory / "authorization.json").write_text(json.dumps(auth))
    return directory

def msg(text):
    return httpx.Response(200, json={"id": "msg_v", "type": "message", "role": "assistant", "model": "claude-haiku-5-5",
        "content": [{"type": "text", "text": text}], "stop_reason": "end_turn", "stop_sequence": None,
        "usage": {"input_tokens": 9000, "output_tokens": 3000, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}}, headers={"request-id": "req_v"})

def run(task, texts, name):
    sent = []
    queue = list(texts)
    def handler(request):
        sent.append(json.loads(request.content)); return msg(queue.pop(0))
    d = authorize(OUT / name / "auth", [task])
    with live.LiveSession(d, mode="live", transport=httpx.MockTransport(handler), api_key="dummy") as s:
        p = live.LiveAuditProvider(s, HAIKU, task.id, "primary", P8)
        res = run_audit(task, p, output_root=OUT / name / "out", review_state=d / "p9")
    return res, sent

# ---- A
case = Path(BASE) / "tasks/study_forensics/case001_social_media.yaml"
r = CliRunner().invoke(audit, ["validate", "--task", str(case)])
print("A audit validate:", r.exit_code, r.output.strip())
t = load_task(case)
print("A gold_label/expected_answer:", t.gold_label, t.expected_answer, "| context:", repr(t.context))
rec_pos = (Path(BASE) / "examples/phase10/positive-recording.json").read_text()
res, sent = run(t, [rec_pos], "A")
u = sent[0]["messages"][0]["content"]
print("A errors:", res.errors[:3]); print("A status:", res.status, "| requests:", len(sent), "| curator sentence sent:",
      "The agent should recognize it as solid" in u, "| user==build_user_message:", u == build_user_message(t))
leak_fields = {k: v for k, v in t.model_dump(mode="json").items() if k not in ("prompt", "context", "id", "title")
               and isinstance(v, str) and len(v) > 25 and v.strip() in u}
print("A other task string fields found verbatim in user msg:", list(leak_fields))

# ---- B: P9 review path carries context
unk = load_task(Path(BASE) / "examples/phase10/unknown-task.json")
CUR = "CURATOR-NOTE: The agent should classify this as solid."
unk2 = unk.model_copy(update={"id": "verifier-unknown-curator", "context": unk.context + " " + CUR})
rec_unk = (Path(BASE) / "examples/phase10/unknown-recording.json").read_text()
res, sent = run(unk2, [rec_unk, rec_unk, rec_unk], "B")
print("B errors:", res.errors[:3]); print("B status:", res.status, "| requests:", len(sent))
for i, b in enumerate(sent):
    c = b["messages"][0]["content"]
    print(f"  request {i}: curator note occurrences in user msg = {c.count(CUR)}; 'Bound evidence packet' in msg = {'Bound evidence packet' in c}")
print("OUT:", OUT)
