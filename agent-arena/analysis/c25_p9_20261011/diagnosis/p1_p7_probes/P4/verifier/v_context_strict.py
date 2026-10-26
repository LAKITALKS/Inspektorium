"""Verifier: strict count of active library contexts that literally name their own gold label."""
import re
import sys

B = sys.argv[1]
sys.path.insert(0, B + "/src")
from agent_arena import run_library as rl  # noqa: E402

STRICT = {
    "solid": r"\bsolid\b",
    "overclaim": r"\boverclaim\b",
    "mechanism_vs_evidence": r"mechanism[ _-]+(vs\.?|versus)[ _-]+evidence",
    "correlation_vs_causation": r"correlation[ _-]+(vs\.?|versus)[ _-]+causation",
}
active = [t for _, t in rl.discover_cases()]
hits = [(t.id, t.gold_label) for t in active if re.search(STRICT[t.gold_label], (t.context or "").lower())]
any_label = [t.id for t in active if any(re.search(p, (t.context or "").lower()) for p in STRICT.values())]
print("active:", len(active), "| context literally names own gold label:", len(hits),
      "| names any label:", len(any_label))
print(hits)
