"""Verifier: dump every tracked study_forensics task context with its gold label (read-only)."""
import sys, glob
from pathlib import Path
B = sys.argv[1]; sys.path.insert(0, B + "/src")
from agent_arena.task_loader import load_task
from agent_arena.run_library import TASK_DIR, discover_cases
print("TASK_DIR", TASK_DIR)
active = {p.name for p, t in discover_cases(task_dir=Path(B)/"tasks/study_forensics")}
print("active discover_cases:", len(active))
rows = []
for f in sorted((Path(B) / "tasks/study_forensics").glob("*.yaml")):
    try:
        t = load_task(str(f))
    except Exception as e:
        print("LOADFAIL", f.name, e); continue
    ctx = " ".join((t.context or "").split())
    g = (t.gold_label or "")
    own = bool(g) and (g in ctx.lower() or g.replace("_", " ") in ctx.lower())
    rows.append((f.name, g, t.status, f.name in active, own, ctx))
for r in rows:
    print(f"{r[0]:45s} gold={r[1]:26s} status={r[2]} active={r[3]} own={r[4]}\n    CTX: {r[5]}")
print("n=", len(rows), "own=", sum(r[4] for r in rows), "active=", sum(r[3] for r in rows), "own&active=", sum(r[3] and r[4] for r in rows))
