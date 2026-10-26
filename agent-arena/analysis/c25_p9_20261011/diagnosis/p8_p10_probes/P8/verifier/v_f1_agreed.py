"""Verifier: same F1 fixture, but an AGREED (non-conflict) bounded UNKNOWN on the CvC trigger proposition.
Shows whether the label mechanism also releases on an agreed unknown (scope of F1). Offline only."""
import json
import sys
from pathlib import Path

V = Path("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_p8_p10/P8/verifier")
src = (V / "v_f1.py").read_text().split("CASES = [")[0]
ns = {"__file__": str(V / "v_f1.py"), "__name__": "v_f1_lib"}
exec(compile(src, "v_f1_lib", "exec"), ns)
build, TASK, OUT = ns["build"], ns["TASK"], V / "out_f1_agreed"
from agent_arena.output_contract import parse_structured_output  # noqa: E402
from agent_arena.phase9_review import assess_case, position_from_result  # noqa: E402
from agent_arena.phase9_runtime import OfflineReviewProvider  # noqa: E402
from agent_arena.phase10_bundle import release_candidate, run_audit  # noqa: E402
from agent_arena.schemas import AgentResult  # noqa: E402

data = build("cvc", "unknown", True)
for d in data["forensic_record"]["phase8"]["evidence_descriptions"]:
    if d["evidence_id"] == "e1":
        d["attributes"]["comparison"] = None  # host: comparison not represented -> unknown
for t in data["forensic_record"]["phase8"]["transformations"]:
    pass
raw = json.dumps(data)
parsed, diag = parse_structured_output(raw)
pos = position_from_result(TASK, AgentResult(provider="x", model="m", raw_output=raw, parsed=parsed,
                                             parse_ok=diag.ok), "run1")
a = pos.phase8
print("P8:", a["technical_status"], a["composite_state"], [(p["proposition_id"], p["reported_verdict"], p["host_state"],
      p["derived_state"], p["model_host_conflict"]) for p in a["propositions"]], "label", a["derived_label"])
r9 = assess_case(TASK, [pos])
print("P9:", r9.route, [(t.code, t.mandatory) for t in r9.triggers])
r = run_audit(TASK, OfflineReviewProvider(raw), output_root=OUT / "audit")
print("P10:", r.status, "| release:", release_candidate(Path(r.path), output_root=OUT / "rel", reviewer="DIAG ONLY",
                                                      reason="verifier").status)
