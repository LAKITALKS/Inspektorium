import json, sys
sys.path.insert(0, "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/wf_second_opinion/sonnet_c25/scripts")
from harness import load
fr, task = load(sys.argv[1], sys.argv[2])
p8 = fr["phase8"]
print("EVIDENCE"); 
for e in fr["evidence"]: print(" ", json.dumps(e))
print("FINDINGS");
for f in fr["findings"]: print(" ", json.dumps(f))
print("NEG", json.dumps(fr.get("negative_assertions")))
print("SCOPES", json.dumps(fr.get("search_scopes")))
print("LOGIC", json.dumps(p8["logic"]))
for p in p8["propositions"]:
    q = {k: v for k, v in p.items()}
    print("PROP", json.dumps(q, indent=1))
print("DESCRIPTIONS")
for d in p8["evidence_descriptions"]: print(json.dumps(d, indent=1))
print("BRIDGES", json.dumps(p8.get("bridges")), "TRANSFERS", json.dumps(p8.get("product_transfers")))
for t in p8["transformations"]:
    print("T", t["transformation_id"], t["stage"], t["target_id"], "asserted", t.get("asserted_state"), "whole", t.get("asserts_whole_claim"))
    print("   from_attr", json.dumps(t["from_attributes"]))
    print("   to_attr  ", json.dumps(t["to_attributes"]))
