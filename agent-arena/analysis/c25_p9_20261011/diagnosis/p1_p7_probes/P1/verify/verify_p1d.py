import sys, json, copy
B = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
sys.path[:0] = [B + "/src", B]
import agent_arena; assert agent_arena.__file__.startswith(B)
from tests.phase8_case_factory import raw_record
from agent_arena.phase8_pipeline import assess_forensic_payload
claim, context, payload = raw_record()
def show(name, pay):
    a = assess_forensic_payload(pay, original_input=claim, context=context, original_label="x", parse_complete=True)
    print(name, a.get("technical_status"), a.get("composite_state"), [r[:140] for r in a.get("reasons", [])][:6])
    return a
def contra(asserted, role=None):
    d = copy.deepcopy(payload)
    for p in d["phase8"]["propositions"]:
        for b in p["evidence_bindings"]: b["observation"] = "contradiction"
        p["reported_verdict"] = "contradicted"
    for t in d["phase8"].get("transformations", []):
        if t["stage"] == "summary": t["asserted_state"] = asserted
    if role:
        for e in d["evidence"]: e["role"] = role
    return d
show("contra/summary=contradicted", contra("contradicted"))
show("contra/summary=unknown", contra("unknown"))
show("contra/summary=None", contra(None))
show("contra/summary=contradicted/role=contradicting", contra("contradicted", "contradicting"))
print(json.dumps(payload["phase8"], indent=0)[:1500])
