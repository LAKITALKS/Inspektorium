import sys, glob, collections, re
from pathlib import Path
B = sys.argv[1]; sys.path.insert(0, B + "/src")
from agent_arena.task_loader import load_task
c = collections.Counter(); fails = []; ex = []
for p in sorted(glob.glob(B + "/tasks/**/*.yaml", recursive=True)):
    rel = p.replace(B + "/", "")
    if str(Path(rel).parent) == "tasks/study_forensics":
        continue
    try:
        t = load_task(p)
    except Exception as e:
        fails.append((rel, type(e).__name__)); continue
    if t.task_type.value != "study_forensics":
        c["non_sf"] += 1; continue
    ctx = " ".join((t.context or "").split()).lower()
    g = (t.gold_label or "").lower()
    c["sf"] += 1
    if ctx: c["sf_ctx"] += 1
    if g and ctx and (g in ctx or g.replace("_", " ") in ctx):
        c["own_gold"] += 1
        if len(ex) < 3: ex.append((rel, g, ctx[:110]))
    if re.search(r"\bthe agent should\b", ctx): c["agent_should"] += 1
print(dict(c)); print("load failures:", len(fails), fails[:6]); [print("  e.g.", e) for e in ex]
