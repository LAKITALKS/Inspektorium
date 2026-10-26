"""Counter-case: a curated library case (task.context = curator commentary) through `audit validate`
and the live path (MockTransport, dummy key, no network). What reaches the transport?"""
import sys, os, json, tempfile
from pathlib import Path
BASE = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
sys.path.insert(0, BASE + "/src"); sys.path.insert(0, BASE + "/tests"); os.environ.pop("ANTHROPIC_API_KEY", None)
from click.testing import CliRunner
from agent_arena.phase10_cli import audit
from agent_arena.task_loader import load_task
from agent_arena.phase10_pipeline import preflight
case = Path(BASE) / "tasks/study_forensics/case001_social_media.yaml"
res = CliRunner().invoke(audit, ["validate", "--task", str(case)])
print("audit validate exit:", res.exit_code, res.output.strip())
task = load_task(case)
print("gold_label:", task.gold_label, "| expected_answer:", task.expected_answer)
print("task.context:", repr(task.context))
import test_phase10_live as T
from agent_arena import phase10_live as live
from agent_arena.phase10_bundle import run_audit
tmp = Path(tempfile.mkdtemp(dir=str(Path(__file__).parent)))
d = T._authorize(tmp / "auth", [task])
tr = T.Transport(T.message(T._recording("positive")))
with T._session(d, tr) as s:
    prov = live.LiveAuditProvider(s, T.HAIKU, task.id, "primary", T.P8)
    out = run_audit(task, prov, output_root=tmp / "out", review_state=d / "p9")
user = tr.requests[0]["body"]["messages"][0]["content"]
print("live status:", out.status, "| requests:", len(tr.requests))
print("curator sentence 'The agent should recognize it as solid' sent to provider:",
      "The agent should recognize it as solid" in user)
print("gold_label token 'solid' appears in user message:", "solid" in user)
print("--- transmitted user message (tail) ---"); print(user[-260:])
