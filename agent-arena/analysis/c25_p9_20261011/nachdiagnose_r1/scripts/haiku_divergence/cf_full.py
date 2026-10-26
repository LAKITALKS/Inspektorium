import copy, json, sys
sys.path.insert(0, "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/wf_second_opinion/haiku_divergence/scripts")
from cf import load
from agent_arena.phase8_pipeline import assess_forensic_payload
REPO = "__LOCAL_HOME__/Documents/Projects/agent-arena/"
def task(n): return json.load(open(REPO + f"analysis/live_smoke_20261011/live_run/tasks/LS-0{n}.json"))
def full(n, fr, label, lab):
    t = task(n)
    a = assess_forensic_payload(fr, original_input=t["prompt"], context=t["context"], original_label=lab)
    print(f"[LS-0{n} {label}] tech={a['technical_status']} composite={a['composite_state']} assessed={a.get('assessed_composite_state')} taxonomy={a['taxonomy'].get('status') or a['taxonomy'].get('technical_status')} derived_label={a['derived_label']} nreasons={len(a['reasons'])}")
for n, att, mod in [(3,3,"ev3"),(5,5,"ev5"),(6,6,"ev6"),(2,2,None),(4,4,None)]:
    j = load(att); fr = j["forensic_record"]
    full(n, copy.deepcopy(fr), "as captured", j["final_answer"])
    f2 = copy.deepcopy(fr)
    if mod == "ev3": f2["phase8"]["evidence_descriptions"][0]["evidence_type"] = "descriptive"
    elif mod == "ev5": f2["phase8"]["propositions"][0]["evidence_bindings"][0]["observation"] = "no_effect_observed"
    elif mod == "ev6": next(d for d in f2["phase8"]["evidence_descriptions"] if d["evidence_id"]=="ev:rct")["evidence_type"] = "controlled_intervention"
    else: continue
    full(n, f2, "one-field edit", j["final_answer"])
