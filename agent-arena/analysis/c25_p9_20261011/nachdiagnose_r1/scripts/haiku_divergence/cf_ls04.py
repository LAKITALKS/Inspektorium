import copy, sys
sys.path.insert(0, "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/wf_second_opinion/haiku_divergence/scripts")
from cf import load, run, detail
base = load(4)["forensic_record"]
fr = copy.deepcopy(base)
for p in fr["phase8"]["propositions"]: p["not_applicable"]["certainty"] = "unhedged"
for d in fr["phase8"]["evidence_descriptions"][:2]: d["attributes"]["intervention"] = "virtual tutoring program"
run(fr, "B: certainty n/a + identical intervention"); detail(fr)
fr2 = copy.deepcopy(fr); fr2["phase8"]["evidence_descriptions"][0]["design_limitations"] = []
run(fr2, "C: B + ev1 design_limitations []"); detail(fr2)
fr3 = copy.deepcopy(fr2); fr3["phase8"]["propositions"][0]["evidence_bindings"] = fr3["phase8"]["propositions"][0]["evidence_bindings"][:1]
run(fr3, "C': C without b2")
