import copy, sys
sys.path.insert(0, "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/wf_second_opinion/haiku_divergence/scripts")
from cf import load, run

def P(fr, pid):
    return next(p for p in fr["phase8"]["propositions"] if p["proposition_id"] == pid)
def D(fr, eid):
    return next(d for d in fr["phase8"]["evidence_descriptions"] if d["evidence_id"] == eid)
def B(fr, bid):
    for p in fr["phase8"]["propositions"]:
        for b in p["evidence_bindings"]:
            if b["binding_id"] == bid: return b
def E(fr, eid):
    return next(e for e in fr["evidence"] if e["evidence_id"] == eid)

print("==== LS-02 (attempt-002)")
base = load(2)["forensic_record"]
fr = copy.deepcopy(base); P(fr,"claim:p1")["not_applicable"]["endpoint_type"] = "x"
run(fr, "A: endpoint_type given n/a reason only")
fr = copy.deepcopy(base); P(fr,"claim:p1")["attributes"]["endpoint_type"] = "clinical"
run(fr, "A2: endpoint_type='clinical' only")
fr = copy.deepcopy(base); P(fr,"claim:p1")["attributes"]["endpoint_type"] = "clinical"
B(fr,"bind-1")["observation"]="support"; E(fr,"ev-1")["role"]="supporting"
run(fr, "B: A2 + ev-1 role supporting/obs support (bind-2 no_evidence_found kept)")
fr = copy.deepcopy(base); P(fr,"claim:p1")["attributes"]["endpoint_type"] = "clinical"
B(fr,"bind-1")["observation"]="support"; E(fr,"ev-1")["role"]="supporting"
B(fr,"bind-2")["observation"]="inconclusive"
run(fr, "C: B but bind-2 inconclusive")
fr = copy.deepcopy(base); P(fr,"claim:p1")["attributes"]["endpoint_type"] = "clinical"
B(fr,"bind-1")["observation"]="support"; E(fr,"ev-1")["role"]="supporting"
P(fr,"claim:p1")["evidence_bindings"] = [B(fr,"bind-1")]
E(fr,"ev-2")["material"]=False
fr["negative_assertions"]=[]; fr["client_findings"][0]["client_negative_assertions"]=[]
fr["findings"][0]["supporting_evidence_ids"]=["ev-1"]; fr["findings"][0]["contrary_evidence_ids"]=[]
fr["client_findings"][0]["referenced_evidence_ids"]=["ev-1"]
run(fr, "D: A2 + ev-1 supporting/support, ev-2 unbound")

print("==== LS-03 (attempt-003)")
base = load(3)["forensic_record"]
for t in ["descriptive","controlled_intervention","observational"]:
    fr = copy.deepcopy(base); D(fr,"ev:1")["evidence_type"]=t
    run(fr, f"ev:1 evidence_type={t}")

print("==== LS-04 (attempt-004)")
base = load(4)["forensic_record"]
def fix_cert(fr):
    for pid in ("claim:p1","claim:p2"):
        P(fr,pid)["not_applicable"]["certainty"]="unhedged"
fr = copy.deepcopy(base); fix_cert(fr); run(fr, "A: certainty n/a only")
fr = copy.deepcopy(base); fix_cert(fr); D(fr,"ev1")["attributes"]["intervention"]="virtual tutoring program"; D(fr,"ev2")["attributes"]["intervention"]="virtual tutoring program"
run(fr, "B: A + identical intervention strings")
fr2 = copy.deepcopy(fr); D(fr2,"ev1")["design_limitations"]=[]
run(fr2, "C: B + ev1 design_limitations empty")
fr3 = copy.deepcopy(fr2); P(fr3,"claim:p2")["not_applicable"]["endpoint_type"]="n/a"
run(fr3, "D: C + p2 endpoint_type n/a")
fr4 = copy.deepcopy(base); D(fr4,"ev1")["design_limitations"]=[]; D(fr4,"ev1")["attributes"]["intervention"]="virtual tutoring program"
run(fr4, "E: no certainty fix; intervention+design fixed")

print("==== LS-05 (attempt-005)")
base = load(5)["forensic_record"]
for obs in ["no_effect_observed","unknown","search_incomplete","no_evidence_found"]:
    fr = copy.deepcopy(base); B(fr,"b1")["observation"]=obs
    try: run(fr, f"b1 observation={obs}")
    except Exception as e: print("ERR", obs, e)
fr = copy.deepcopy(base); B(fr,"b1")["observation"]="no_effect_observed"; B(fr,"b1")["directness"]="direct"
run(fr, "b1 no_effect_observed + direct")

print("==== LS-06 (attempt-006)")
base = load(6)["forensic_record"]
fr = copy.deepcopy(base); D(fr,"ev:rct")["evidence_type"]="controlled_intervention"
run(fr, "ev:rct typed controlled_intervention")
# add underlying item quoting the pooled RCT result
fr = copy.deepcopy(base)
q = "adults assigned to eat breakfast consumed more total daily calories and, if anything, weighed slightly more than those assigned to skip it"
fr["evidence"].append({"evidence_id":"ev:rct-trials","source_id":"context","role":"contradictory","endpoint":"body weight","material":True,"exact_reference":q,"text":q})
d = copy.deepcopy(D(fr,"ev:rct")); d["evidence_id"]="ev:rct-trials"; d["evidence_type"]="controlled_intervention"; d["source_role"]="pooled RCTs"
fr["phase8"]["evidence_descriptions"].append(d)
D(fr,"ev:rct")["underlying_evidence_ids"]=["ev:rct-trials"]
run(fr, "ev:rct review + underlying controlled_intervention item")
