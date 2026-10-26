"""Check whether a human adjudication could select the original position after the CF-A review path."""
import json, sys
from pathlib import Path
import agent_arena.phase8_semantics as sem
from agent_arena.schemas import RunRecord
from agent_arena.phase9_runtime import submit_human_review
from agent_arena.phase9_review import case_key
ORIG = sem._audit_transformations
sem._audit_transformations = lambda l, a, c: [f for f in ORIG(l, a, c) if ": output state hides or changes " not in f]
for slot in sys.argv[2:]:
    d = Path(sys.argv[1]) / "state" / slot / "phase9"
    rec = RunRecord.model_validate_json(next(p for p in d.glob("p9case:*.json") if not p.name.endswith(".ledger.json")).read_text())
    for pos in rec.metadata["phase9"]["positions"]:
        try:
            submit_human_review(rec, base_dir=Path(sys.argv[1]) / "state" / slot, selected_position_id=pos["position_id"],
                                reviewer_provenance="offline simulation", reason="simulation probe")
            print(slot, pos["origin"], "ACCEPTED")
        except Exception as exc:
            print(slot, pos["origin"], "REFUSED:", exc)
