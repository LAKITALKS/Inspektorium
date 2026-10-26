"""Bundle status (phase10_pipeline.evaluate) for fresh records under baseline and CF-A; no bundle written."""
import glob, json, sys
from copy import deepcopy
import agent_arena.phase8_semantics as sem
from agent_arena.phase10_pipeline import evaluate
from agent_arena.schemas import AgentResult, RunRecord
from agent_arena.phase9_pipeline import initial_assessment
ORIG = sem._audit_transformations
for mode in ("baseline", "cf_a"):
    sem._audit_transformations = ORIG if mode == "baseline" else (
        lambda l, a, c: [f for f in ORIG(l, a, c) if ": output state hides or changes " not in f])
    for path in sorted(glob.glob(f"{sys.argv[1]}/*/*/record.json")):
        audit = json.load(open(path)); rr = deepcopy(audit["run_record"])
        rr["metadata"].pop("phase9", None)
        for r in rr["results"]:
            r["agent_result"]["phase9"] = {}
        rec0 = RunRecord.model_validate(rr)
        for r in rr["results"]:
            r["agent_result"]["phase9"] = initial_assessment(rec0.task, AgentResult.model_validate(r["agent_result"]))
        rec = RunRecord.model_validate(rr)
        status, controls, review, *_ = evaluate(rec, "sim", audit["provenance"])
        failed = [c.control_id for c in controls if c.outcome == "fail"]
        print(mode, path.split("/")[-3][:13], rec.task.id[-5:], status, review.get("route"), failed)
