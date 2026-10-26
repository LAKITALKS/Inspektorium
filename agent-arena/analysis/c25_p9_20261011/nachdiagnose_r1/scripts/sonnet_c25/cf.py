import sys, copy, json
sys.path.insert(0, "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/wf_second_opinion/sonnet_c25/scripts")
from harness import load, run
from agent_arena.schemas import ForensicRecord
from agent_arena.phase8_models import PropositionLedger
from agent_arena.phase8_semantics import _assess_proposition, validate_ledger

def states(fr, label):
    rec = ForensicRecord.model_validate(copy.deepcopy(fr))
    led = PropositionLedger.model_validate(rec.phase8)
    errs = validate_ledger(rec, led)
    print(f"-- {label}; ledger validation errors: {errs if errs else 'none'}")
    for p in led.propositions:
        a = _assess_proposition(p, led, rec)
        print(f"   {a.proposition_id}: reported={a.reported_verdict} derived={a.derived_state}")
        for r in a.reasons[2:]:
            print("      .", r)

def P(fr, pid):
    return next(p for p in fr["phase8"]["propositions"] if p["proposition_id"] == pid)
def D(fr, eid):
    return next(d for d in fr["phase8"]["evidence_descriptions"] if d["evidence_id"] == eid)
def E(fr, eid):
    return next(e for e in fr["evidence"] if e["evidence_id"] == eid)

which = sys.argv[1]
if which == "LS-02":
    fr, task = load("008", "LS-02")
    states(fr, "original")
    f = copy.deepcopy(fr); P(f,"claim:p1")["reported_verdict"]="unknown"; states(f, "same evidence, reported unknown")
    # A: E1 as remote 'support' (role supporting); keep b2 no_evidence_found
    f = copy.deepcopy(fr); E(f,"E1")["role"]="supporting"
    b = P(f,"claim:p1")["evidence_bindings"][0]; b["observation"]="support"; b["directness"]="remote"
    f["findings"][0]["supporting_evidence_ids"]=["E1"]; f["findings"][0]["contrary_evidence_ids"]=["E2"]
    states(f, "A: b1 observation support/remote (E1 role supporting), b2 unchanged")
    # A2: same but keep 'inconclusive' replaced by 'no_effect_observed'
    f2 = copy.deepcopy(fr); P(f2,"claim:p1")["evidence_bindings"][0]["observation"]="no_effect_observed"
    states(f2, "A2: b1 observation no_effect_observed, b2 unchanged")
    # B: A without the E2 no_evidence_found binding
    g = copy.deepcopy(f); P(g,"claim:p1")["evidence_bindings"]=P(g,"claim:p1")["evidence_bindings"][:1]
    g["findings"][0]["contrary_evidence_ids"]=[]
    states(g, "B: A minus b2 (absence statement not bound)")
    # B2: b1 unchanged (inconclusive) minus b2
    h = copy.deepcopy(fr); P(h,"claim:p1")["evidence_bindings"]=P(h,"claim:p1")["evidence_bindings"][:1]
    states(h, "B2: original b1 (inconclusive) only")
    # C: E1 description attributes matched to claim so only capability rule acts
    k = copy.deepcopy(g); d = D(k,"E1"); d["attributes"].update({"population":"patients","endpoint":"cancer treatment","endpoint_type":"clinical"})
    states(k, "C: B + E1 description attributes equal claim (pure capability test)")
elif which == "LS-03":
    fr, task = load("009", "LS-03")
    states(fr, "original")
    f = copy.deepcopy(fr); d=D(f,"e1"); d["evidence_type"]="controlled_intervention"
    states(f, "A: e1 typed controlled_intervention, randomized null, design_limitations kept")
    f2 = copy.deepcopy(f); D(f2,"e1")["design_limitations"]=[]
    states(f2, "A2: + design_limitations []")
    f3 = copy.deepcopy(f2); D(f3,"e1")["randomized"]=False
    states(f3, "A3: + randomized false")
    f4 = copy.deepcopy(fr); D(f4,"e1")["evidence_type"]="descriptive"
    states(f4, "B: e1 typed descriptive")
    f5 = copy.deepcopy(f4); P(f5,"claim:p1")["attributes"]["relation"]="description"
    states(f5, "B2: e1 descriptive + p1 relation description")
    f6 = copy.deepcopy(fr); D(f6,"e1")["evidence_type"]="observational"
    states(f6, "B3: e1 typed observational")
    f7 = copy.deepcopy(f2); D(f7,"e1")["randomized"]=True; D(f7,"e1")["attributes"]["comparison"]="between"
    states(f7, "INVENTED: controlled_intervention, randomized true, comparison between, no limitations")
    # p2: what would make p2 unsupported?
    g = copy.deepcopy(fr); P(g,"claim:p2")["evidence_bindings"][0]["observation"]="no_effect_observed"
    states(g, "p2-A: b2 observation no_effect_observed (not honest)")
    g2 = copy.deepcopy(fr); P(g2,"claim:p2")["evidence_bindings"].append({"binding_id":"b3","proposition_id":"claim:p2","evidence_id":"e1","directness":"remote","observation":"support","search_scope_id":"ss1","reason":"LDL surrogate only"})
    states(g2, "p2-B: add e1 (LDL) as remote support for p2, b2 kept")
    g3 = copy.deepcopy(g2); P(g3,"claim:p2")["evidence_bindings"]=P(g3,"claim:p2")["evidence_bindings"][1:]
    states(g3, "p2-C: only e1 (LDL) as remote support for p2")
elif which == "LS-04":
    fr, task = load("010", "LS-04")
    states(fr, "original")
    f = copy.deepcopy(fr); D(f,"E1")["attributes"]["comparison"]="between"
    states(f, "A: E1 description comparison 'between'")
    f2 = copy.deepcopy(fr); D(f2,"E1")["attributes"]["comparison"]="unknown"
    states(f2, "A2: E1 description comparison 'unknown'")
    f3 = copy.deepcopy(fr); D(f3,"E1")["attributes"]["comparison"]="within"
    states(f3, "A3: E1 description comparison 'within'")
    a = run(f, task, label="A full pipeline (with comparison=between)")
    # also fix t4 from_attributes
    f4 = copy.deepcopy(f)
    for t in f4["phase8"]["transformations"]:
        if t["stage"]=="extraction": t["from_attributes"]=copy.deepcopy(t["to_attributes"])
    run(f4, task, label="A + extraction from_attributes = to_attributes")
elif which == "LS-05":
    fr, task = load("011", "LS-05")
    run(fr, task, label="original")
    f = copy.deepcopy(fr)
    for t in f["phase8"]["transformations"]:
        if t["stage"]=="extraction": t["from_attributes"]=copy.deepcopy(t["to_attributes"])
    run(f, task, label="extraction from_attributes = to_attributes")
    g = copy.deepcopy(fr); P(g,"claim:p1")["reported_verdict"]="unsupported"
    states(g, "reported unsupported instead (evidence unchanged)")
elif which == "LS-06":
    fr, task = load("012", "LS-06")
    states(fr, "original")
    f = copy.deepcopy(fr); d=D(f,"e2"); d["evidence_type"]="controlled_intervention"; d["randomized"]=True; d["attributes"]["comparison"]="between"
    states(f, "A: e2 typed controlled_intervention randomized true comparison between, limitations kept")
    f2 = copy.deepcopy(f); D(f2,"e2")["design_limitations"]=[]
    states(f2, "A2: + no design limitations")
    # B: keep review, add underlying RCT evidence item from source
    g = copy.deepcopy(fr)
    g["evidence"].append({"evidence_id":"e3","source_id":"context","role":"contradictory","endpoint":"body weight","material":True,
        "exact_reference":"Randomized controlled trials tell a different story","text":"Randomized controlled trials tell a different story","value_origin":"source_reported"})
    D(g,"e2")["underlying_evidence_ids"]=["e3"]
    dd = copy.deepcopy(D(g,"e2")); dd.update({"evidence_id":"e3","evidence_type":"controlled_intervention","source_role":"RCTs underlying the meta-analysis","randomized":True,"design_limitations":[]})
    dd["attributes"]["comparison"]="between"
    g["phase8"]["evidence_descriptions"].append(dd)
    states(g, "B: review e2 with underlying e3 (RCTs; randomized, between)")
    g2 = copy.deepcopy(g); P(g2,"claim:p1")["evidence_bindings"][1]["observation"]="no_effect_observed"
    states(g2, "B2: as B but b2 observation no_effect_observed")
    g3 = copy.deepcopy(g)
    for t in g3["phase8"]["transformations"]:
        if t["stage"]=="extraction": t["from_attributes"]=copy.deepcopy(t["to_attributes"])
    run(g3, task, label="B + extraction from_attributes fixed, full pipeline")
