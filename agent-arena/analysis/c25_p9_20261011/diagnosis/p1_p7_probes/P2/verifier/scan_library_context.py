"""Scan every library YAML: does task.context state the gold label / address the agent? (read-only)"""
import sys, re
from pathlib import Path
BASE = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
sys.path.insert(0, BASE + "/src")
import agent_arena
assert agent_arena.__file__.startswith(BASE), agent_arena.__file__
from agent_arena.task_loader import load_task
from agent_arena.phase10_pipeline import preflight
LABELS = {"solid": [r"\bsolid\b"], "overclaim": [r"overclaim"], "correlation_vs_causation": [r"correlation", r"causation", r"causal"],
          "mechanism_vs_evidence": [r"mechanism", r"evidence tier", r"animal", r"preclinical"]}
rows = []
for d in ("tasks/study_forensics", "tasks/study_forensics_robustness"):
    for p in sorted((Path(BASE) / d).glob("*.yaml")):
        try:
            t = load_task(p)
        except Exception as e:
            rows.append((p.name, "LOAD_FAIL", str(e)[:80])); continue
        ctx = t.context or ""
        gold = t.gold_label or t.expected_answer
        agent = bool(re.search(r"\b(the )?agent should|\bshould (recognize|flag|identify|detect|notice|classify)|\bmust (recognize|flag|identify)", ctx, re.I))
        names_label = bool(gold) and any(re.search(pat, ctx, re.I) for pat in LABELS.get(gold, [re.escape(gold)]))
        rows.append((p.relative_to(BASE).as_posix(), gold, len(ctx), agent, names_label, preflight(t) == []))
n = len([r for r in rows if r[1] != "LOAD_FAIL"])
print("loaded:", n, "load_fail:", len([r for r in rows if r[1] == "LOAD_FAIL"]))
print("preflight-accepted:", sum(1 for r in rows if r[1] != "LOAD_FAIL" and r[5]))
print("context nonempty:", sum(1 for r in rows if r[1] != "LOAD_FAIL" and r[2] > 0))
print("context addresses the agent ('agent should'/'should recognize|flag|...'):", sum(1 for r in rows if r[1] != "LOAD_FAIL" and r[3]))
print("context contains gold-label keyword:", sum(1 for r in rows if r[1] != "LOAD_FAIL" and r[4]))
print("gold/expected populated:", sum(1 for r in rows if r[1] not in (None, "LOAD_FAIL")))
for r in rows:
    print(r)
