import sys, json
B="__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
sys.path.insert(0, B+"/src")
from pathlib import Path
from agent_arena import condition_contract as cc, full_replication_contract as frc, full_replication_analysis as fra
root=Path(B)
def load(p): return [json.loads(l) for l in (root/p).read_text().splitlines() if l.strip()]
def walk(a,b,path=""):
    out=[]
    if isinstance(a,dict) and isinstance(b,dict):
        for k in sorted(set(a)|set(b)):
            if k not in a or k not in b: out.append((path+"/"+k,"missing", k in a, k in b)); continue
            out+=walk(a[k],b[k],path+"/"+k)
    elif isinstance(a,list) and isinstance(b,list):
        if len(a)!=len(b): out.append((path,"len",len(a),len(b)))
        for i,(x,y) in enumerate(zip(a,b)): out+=walk(x,y,f"{path}[{i}]")
    elif a!=b: out.append((path, str(a)[:90], str(b)[:90]))
    return out
for prof in (frc.HAIKU, frc.SONNET):
    doc = cc.resolve_registered_plan(prof.plan_id, root); spec=doc["specification"]
    ns = Path(prof.artifact_namespace)/prof.model_key
    hist_p = spec["historical_reference"]["raw_records_path"]
    comp = fra.build_comparison(load(hist_p), load(ns/"raw"/f"{prof.model_key}_raw_records.jsonl"), document=doc, historical_raw_path=root/hist_p, prospective_raw_path=root/ns/"raw"/f"{prof.model_key}_raw_records.jsonl")
    frozen = json.loads((root/ns/f"{prof.model_key}_historical_comparison.json").read_text())
    comp=json.loads(json.dumps(comp)); d=walk(comp,frozen); print(prof.model_key, len(d)); [print(" ",x) for x in d[:12]]
print("--- path-substituted recompute")
for prof in (frc.HAIKU, frc.SONNET):
    doc = cc.resolve_registered_plan(prof.plan_id, root); spec=doc["specification"]; arm=cc.resolve_arm(doc, prof.arm_id)
    ns = Path(prof.artifact_namespace)/prof.model_key
    frozen = json.loads((root/ns/f"{prof.model_key}_historical_comparison.json").read_text())
    hist_p = spec["historical_reference"]["raw_records_path"]
    comp = fra.build_comparison(load(hist_p), load(ns/"raw"/f"{prof.model_key}_raw_records.jsonl"), document=doc, historical_raw_path=root/hist_p, prospective_raw_path=root/ns/"raw"/f"{prof.model_key}_raw_records.jsonl")
    comp["historical_raw"]["path"]=frozen["historical_raw"]["path"]; comp["prospective_raw"]["path"]=frozen["prospective_raw"]["path"]
    body={k:v for k,v in comp.items() if k!="comparison_fingerprint"}
    print(prof.model_key, "fp with frozen abs paths", cc._fp(body)==frozen["comparison_fingerprint"], "| json-normalized", cc._fp(json.loads(json.dumps(body)))==frozen["comparison_fingerprint"])
    ana=json.loads((root/ns/f"{prof.model_key}_condition_analysis.json").read_text())
    d=walk(json.loads(json.dumps(comp["prospective"])), ana["report"]); print("  analysis.report diffs", len(d), d[:3])
    body={k:v for k,v in ana.items() if k!="analysis_artifact_fingerprint"}
    import agent_arena.phase7a_execution as p7
    print("  analysis artifact fp reproduces", p7._fp(body)==ana["analysis_artifact_fingerprint"])
