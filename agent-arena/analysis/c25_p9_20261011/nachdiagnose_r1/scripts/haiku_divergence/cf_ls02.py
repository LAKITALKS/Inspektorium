import copy, sys
sys.path.insert(0, "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/wf_second_opinion/haiku_divergence/scripts")
from cf import load, run
from agent_arena.schemas import ForensicRecord
from agent_arena.phase8_models import PropositionLedger
from agent_arena.phase8_semantics import validate_ledger

def setattr_all(fr, key, val):
    fr["phase8"]["propositions"][0]["attributes"][key] = val
    for t in fr["phase8"]["transformations"]:
        t["from_attributes"][key] = val; t["to_attributes"][key] = val
def errs(fr):
    rec = ForensicRecord.model_validate(fr); return validate_ledger(rec, PropositionLedger.model_validate(rec.phase8))
def B(fr, bid): return next(b for b in fr["phase8"]["propositions"][0]["evidence_bindings"] if b["binding_id"]==bid)
def E(fr, eid): return next(e for e in fr["evidence"] if e["evidence_id"]==eid)

base = load(2)["forensic_record"]
fr = copy.deepcopy(base); setattr_all(fr, "endpoint_type", "clinical"); print(errs(fr)); run(fr, "A2: endpoint_type=clinical (all transformations updated)")
fr1 = copy.deepcopy(fr); B(fr1,"bind-1")["observation"]="support"; E(fr1,"ev-1")["role"]="supporting"
fr1["findings"][0]["supporting_evidence_ids"]=["ev-1"]; fr1["findings"][0]["contrary_evidence_ids"]=["ev-2"]
print(errs(fr1)); run(fr1, "B: A2 + ev-1 supporting/support (bind-2 no_evidence_found kept)")
fr2 = copy.deepcopy(fr1); B(fr2,"bind-2")["observation"]="inconclusive"; fr2["negative_assertions"]=[]; fr2["client_findings"][0]["client_negative_assertions"]=[]
print(errs(fr2)); run(fr2, "C: B with bind-2 inconclusive")
fr3 = copy.deepcopy(fr1); fr3["phase8"]["propositions"][0]["evidence_bindings"]=[B(fr3,"bind-1")]; E(fr3,"ev-2")["material"]=False
fr3["negative_assertions"]=[]; fr3["client_findings"][0]["client_negative_assertions"]=[]
fr3["findings"][0]["contrary_evidence_ids"]=[]; fr3["client_findings"][0]["referenced_evidence_ids"]=["ev-1"]
print(errs(fr3)); run(fr3, "D: B with ev-2 unbound/material false")
fr4 = copy.deepcopy(fr); fr4["phase8"]["propositions"][0]["evidence_bindings"]=[B(fr4,"bind-1")]; E(fr4,"ev-2")["material"]=False
fr4["negative_assertions"]=[]; fr4["client_findings"][0]["client_negative_assertions"]=[]
fr4["findings"][0]["contrary_evidence_ids"]=["ev-1"]; fr4["client_findings"][0]["referenced_evidence_ids"]=["ev-1"]
print(errs(fr4)); run(fr4, "E: A2, ev-1 weakening/inconclusive kept, ev-2 unbound")
fr5 = copy.deepcopy(fr); B(fr5,"bind-1")["observation"]="no_effect_observed"
print(errs(fr5)); run(fr5, "F: A2 + bind-1 no_effect_observed (role weakening), bind-2 kept")
