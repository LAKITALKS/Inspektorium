"""Verifier: under a Phase-7-only failure, are model/host conflicts kept? (row transition claim). Offline."""
import json
import sys

DIAG = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new"
sys.path.insert(0, DIAG + "/src")
sys.path.insert(0, DIAG)
import agent_arena  # noqa: E402
assert agent_arena.__file__.startswith(DIAG), agent_arena.__file__
from agent_arena.output_contract import parse_structured_output  # noqa: E402
from agent_arena.phase9_review import assess_case, position_from_result  # noqa: E402
from agent_arena.schemas import AgentResult, Task  # noqa: E402
from tests.phase8_case_factory import raw_record  # noqa: E402

claim, context, rec = raw_record()
rec["phase8"]["propositions"][0]["reported_verdict"] = "unsupported"
for t in rec["phase8"]["transformations"]:
    if t.get("asserted_state") is not None:
        t["asserted_state"] = "unsupported"
rec["client_findings"][0]["client_strength"] = "limited_support"  # Phase-7 summary strength escalation only
task = Task(id="v-p7", title="V", domain="study_forensics", difficulty="medium", task_type="study_forensics",
            prompt=claim, context=context)
raw = json.dumps({"final_answer": "overclaim", "confidence": 0.5, "forensic_record": rec})
parsed, d = parse_structured_output(raw)
pos = position_from_result(task, AgentResult(provider="x", model="m", raw_output=raw, parsed=parsed,
                                             parse_ok=d.ok), "run1")
a = pos.phase8
print("technical", a["technical_status"], "composite", a["composite_state"], "assessed", a["assessed_composite_state"],
      "transformation_findings", a["transformation_findings"])
print("conflicts kept:", [(c["scope"], c["model_state"], c["host_state"]) for c in a["model_host_conflicts"]])
r = assess_case(task, [pos])
print("P9", r.route, sorted({(t.code, t.mandatory) for t in r.triggers}))
