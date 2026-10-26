import sys, json, copy
B = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
sys.path[:0] = [B + "/src", B]
import agent_arena; assert agent_arena.__file__.startswith(B)
from tests.phase8_case_factory import raw_record
from agent_arena.phase8_pipeline import assess_forensic_payload
claim, context, payload = raw_record()
def show(name, pay):
    a = assess_forensic_payload(pay, original_input=claim, context=context, original_label="x", parse_complete=True)
    print(name, a.get("technical_status"), a.get("composite_state"), a.get("derived_label"), [r[:110] for r in a.get("reasons", [])][:6])
show("base", payload)
d = copy.deepcopy(payload)
for p in d["phase8"]["propositions"]:
    for b in p["evidence_bindings"]: b["observation"] = "contradict"
    p["reported_verdict"] = "contradicted"
show("contradict", d)
# variant: species mismatch in claim-side attributes? try weakening: indirect evidence
d2 = copy.deepcopy(payload)
for p in d2["phase8"]["propositions"]:
    for b in p["evidence_bindings"]: b["directness"] = "indirect"
    p["reported_verdict"] = "unknown"
show("indirect", d2)
d3 = copy.deepcopy(payload)
for p in d3["phase8"]["propositions"]:
    p["evidence_bindings"] = []
    p["reported_verdict"] = "unknown"
show("nobind", d3)
