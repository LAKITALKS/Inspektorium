"""Independent scan: library tasks' context vs gold label words; which tasks the canonical preflight accepts."""
import json, sys
from pathlib import Path
D = Path("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new")
sys.path.insert(0, str(D / "src"))
import agent_arena
assert str(D) in agent_arena.__file__, agent_arena.__file__
from agent_arena.task_loader import load_task
from agent_arena.phase10_pipeline import preflight
from agent_arena.schemas import TaskType

LABELS = ("overclaim", "solid", "correlation_vs_causation", "mechanism_vs_evidence",
          "correlation vs causation", "mechanism vs evidence", "correlation", "mechanism")
rows = []
for f in sorted((D / "tasks").rglob("*.yaml")):
    try:
        t = load_task(f)
    except Exception as exc:  # noqa
        rows.append({"file": str(f.relative_to(D)), "load_error": str(exc)[:80]})
        continue
    if t.task_type != TaskType.STUDY_FORENSICS:
        continue
    ctx = (t.context or "").lower()
    gold = (t.gold_label or "").lower()
    gold_words = {gold, gold.replace("_", " ")} - {""}
    rows.append({"file": str(f.relative_to(D)), "id": t.id, "dir": f.parent.name,
                 "ctx_nonempty": bool(ctx.strip()), "ctx_in_prompt": bool(ctx.strip()) and ctx.strip() in t.prompt.lower(),
                 "ctx_names_any_label": any(w in ctx for w in LABELS[:4] + LABELS[4:6]),
                 "ctx_names_own_gold": any(w in ctx for w in gold_words),
                 "preflight_errors": preflight(t), "gold": t.gold_label})
sf = [r for r in rows if "id" in r]
out = {"n_yaml_study_forensics": len(sf),
       "by_dir": {d: sum(1 for r in sf if r["dir"] == d) for d in sorted({r["dir"] for r in sf})},
       "load_errors": [r for r in rows if "load_error" in r],
       "ctx_nonempty": sum(r["ctx_nonempty"] for r in sf),
       "ctx_in_prompt": sum(r["ctx_in_prompt"] for r in sf),
       "ctx_names_any_label_strict": sum(r["ctx_names_any_label"] for r in sf),
       "ctx_names_own_gold": sum(r["ctx_names_own_gold"] for r in sf),
       "preflight_accepts": sum(not r["preflight_errors"] for r in sf),
       "own_gold_by_dir": {d: sum(1 for r in sf if r["dir"] == d and r["ctx_names_own_gold"]) for d in sorted({r["dir"] for r in sf})},
       "examples_own_gold": [r["id"] for r in sf if r["ctx_names_own_gold"]][:8]}
print(json.dumps(out, indent=1))
