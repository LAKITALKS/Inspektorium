"""Verifier: census of task.context in active library cases (cwd must be the checkout)."""
import sys

B = sys.argv[1]
sys.path.insert(0, B + "/src")
from agent_arena import run_library as rl  # noqa: E402

active = rl.discover_cases()
allc = rl.discover_cases(include_retired=True)
retired = [t.id for _, t in allc if rl.is_retired(t)]
nonempty = [t for _, t in active if (t.context or "").strip()]
contained = [t.id for t in nonempty if t.context.strip() in t.prompt]
line_overlap = [t.id for t in nonempty
                if any(ln.strip() and ln.strip() in t.prompt for ln in t.context.splitlines())]
print("active", len(active), "retired", retired, "all", len(allc))
print("active with non-empty context:", len(nonempty))
print("context fully contained in prompt:", contained)
print("any context line contained in prompt:", line_overlap)
lens = sorted(len(t.context) for t in nonempty)
print("context length min/median/max:", lens[0], lens[len(lens) // 2], lens[-1])
for t in nonempty[:3]:
    print("---", t.id, "gold", t.gold_label, "| context:", t.context.strip()[:160].replace("\n", " "))
