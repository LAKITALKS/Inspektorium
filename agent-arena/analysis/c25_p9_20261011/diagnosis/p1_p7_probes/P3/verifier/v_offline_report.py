"""Offline P10 audit on an unmodified library YAML (built-in recorded provider; no network)."""
import sys, os, json
from pathlib import Path
B, D = sys.argv[1], sys.argv[2]
sys.path.insert(0, B + "/src")
os.chdir(B)
from agent_arena.task_loader import load_task
from agent_arena.phase10_bundle import run_audit
from agent_arena.phase9_runtime import OfflineReviewProvider

task = load_task("tasks/study_forensics/case001_social_media.yaml")
rec = Path("examples/phase10/positive-recording.json").read_text(encoding="utf-8")
out = Path(D) / "offline_audit_case001"
res = run_audit(task, OfflineReviewProvider(rec), output_root=out)
print("status", res.status, "errors", (res.errors or [])[:3])
hits = []
for p in out.rglob("*"):
    if p.is_file() and p.suffix in {".md", ".html", ".json"}:
        txt = p.read_text(encoding="utf-8", errors="replace")
        if "should recognize it as solid" in txt:
            hits.append(str(p.relative_to(out)))
print("files containing curator sentence:", hits)
for p in out.rglob("report*.md"):
    t = p.read_text(encoding="utf-8")
    i = t.find("Captured context")
    print(p.relative_to(out), "->", repr(t[i:i + 220]) if i >= 0 else "no 'Captured context' section")
