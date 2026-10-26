"""Verifier: does task.context in active library cases reveal the gold label / evaluator intent?"""
import re
import sys

B = sys.argv[1]
sys.path.insert(0, B + "/src")
from agent_arena import run_library as rl  # noqa: E402

LABEL_WORDS = {
    "solid": [r"\bsolid\b"],
    "overclaim": [r"\boverclaim", r"\bover-claim"],
    "mechanism_vs_evidence": [r"mechanism[_ -]vs\.?[_ -]evidence", r"mechanism.{0,40}evidence"],
    "correlation_vs_causation": [r"correlation[_ -]vs\.?[_ -]causation", r"correlation.{0,40}caus"],
}
active = [t for _, t in rl.discover_cases()]
agent_should, names_gold, names_other, rows = [], [], [], []
for t in active:
    c = (t.context or "").lower()
    if re.search(r"\b(the )?(agent|model)s? (should|must|needs to|ought)", c):
        agent_should.append(t.id)
    gold_hit = any(re.search(p, c) for p in LABEL_WORDS.get(t.gold_label, []))
    if gold_hit:
        names_gold.append(t.id)
    other = [lab for lab, ps in LABEL_WORDS.items() if lab != t.gold_label and any(re.search(p, c) for p in ps)]
    if other:
        names_other.append((t.id, t.gold_label, other))
print("active cases:", len(active))
print("context addresses the agent/model ('agent should ...'):", len(agent_should))
print("context names the case's own gold label (regex):", len(names_gold))
print("context names a different label (regex):", names_other)
both = sorted(set(agent_should) & set(names_gold))
print("both:", len(both))
for t in active:
    if t.id in both[:6]:
        print(" ", t.id, "gold=", t.gold_label, "|", " ".join(t.context.split())[:200])
