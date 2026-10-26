"""Same claim/context and same model output; only the authoring format differs (JSON vs YAML block scalar).
Offline canonical path (no model): does the outcome flip? And what does the live user message look like?"""
import sys, os, json, tempfile
from pathlib import Path
BASE = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
sys.path.insert(0, BASE + "/src")
import yaml, agent_arena
assert agent_arena.__file__.startswith(BASE)
from click.testing import CliRunner
from agent_arena.phase10_cli import audit
from agent_arena.task_loader import load_task
from agent_arena.phase10_bundle import run_audit
from agent_arena.phase9_runtime import OfflineReviewProvider
from agent_arena.providers.anthropic_live import build_user_message
OUT = Path(tempfile.mkdtemp(prefix="vyaml_", dir=str(Path(__file__).parent)))
src = json.loads((Path(BASE) / "examples/phase10/positive-task.json").read_text())
rec = (Path(BASE) / "examples/phase10/positive-recording.json").read_text()
# YAML authoring with block scalars, as in tasks/study_forensics/*.yaml
lines = [f"{k}: {json.dumps(v)}" for k, v in src.items() if k not in ("prompt", "context")]
lines += ["prompt: |", "  " + src["prompt"], "context: |", "  " + src["context"]]
ypath = OUT / "positive-task.yaml"; ypath.write_text("\n".join(lines) + "\n")
jt, yt = load_task(Path(BASE) / "examples/phase10/positive-task.json"), load_task(ypath)
print("prompt JSON:", repr(jt.prompt), "| prompt YAML:", repr(yt.prompt))
r = CliRunner().invoke(audit, ["validate", "--task", str(ypath)]); print("audit validate YAML:", r.exit_code, r.output.strip())
for name, t in (("json", jt), ("yaml", yt)):
    res = run_audit(t, OfflineReviewProvider(rec), output_root=OUT / name)
    errs = [e for e in res.errors][:2]
    rr = json.loads((Path(res.path) / "record.json").read_text()) if res.path else {}
    p8 = ((rr.get("run_record") or {}).get("results") or [{}])[0].get("agent_result", {}).get("phase8", {}) if rr else {}
    print(f"[{name}] status={res.status} phase8={p8.get('technical_status')} reasons={p8.get('reasons', [])[:1]}")
um = build_user_message(yt)
print("live user message (YAML task) head:", repr(um[:120]))
