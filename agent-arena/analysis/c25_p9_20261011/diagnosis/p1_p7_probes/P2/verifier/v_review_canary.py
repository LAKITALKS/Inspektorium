"""Field-level canaries on the live P9 counterreview request (mock transport, dummy key)."""
import sys, os, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import v_f1_live_context as V  # reuses authorize/run helpers (module runs its own probes A/B first)
from agent_arena.task_loader import load_task
unk = load_task(Path(V.BASE) / "examples/phase10/unknown-task.json")
CAN = {k: f"CANARY_{k.upper()}_9q" for k in ("expected_answer", "reference_solution", "gold_label", "gold_summary",
       "gold_justification", "gold_alternative_reading", "curator_notes", "evaluator_notes", "diagnostic_focus")}
t = unk.model_copy(update=dict(CAN, id="verifier-review-canary", key_insights=["CANARY_KEY_INSIGHT_9q"],
                               common_errors=["CANARY_COMMON_ERROR_9q"], likely_shortcuts=["CANARY_SHORTCUT_9q"]))
rec = (Path(V.BASE) / "examples/phase10/unknown-recording.json").read_text()
res, sent = V.run(t, [rec, rec, rec], "C")
print("C status:", res.status, "| requests:", len(sent))
for i, b in enumerate(sent):
    blob = json.dumps(b, ensure_ascii=False)
    import re
    found = sorted(set(re.findall(r"CANARY_[A-Z_]+_9q", blob)))
    print("  request", i, "canaries present =", found, "| packet =", "Bound evidence packet" in b["messages"][0]["content"])
