import json, re, sys
REPO = "__LOCAL_HOME__/Documents/Projects/agent-arena/"
a = int(sys.argv[1])
d = json.load(open(REPO + f"analysis/live_smoke_20261011/repair_r1/captures/attempt-{a:03d}.json"))
t = d["interpretation"]["final_text"].strip()
t = re.sub(r"^```(json)?\s*", "", t); t = re.sub(r"\s*```$", "", t)
j = json.loads(t)
fr = j["forensic_record"]
print("top keys", [k for k in j if k != "forensic_record"])
for k in j:
    if k != "forensic_record": print(k, json.dumps(j[k], indent=1))
print("EVIDENCE", json.dumps([{k: e[k] for k in ("evidence_id","source_id","role","endpoint","material","exact_reference")} for e in fr["evidence"]], indent=1))
print("FINDINGS", json.dumps([{k: f.get(k) for k in ("finding_id","verdict_summary","supporting_evidence_ids","contrary_evidence_ids","predicted_label")} for f in fr["findings"]], indent=1))
print("CLIENT", json.dumps([{k: c.get(k) for k in ("client_finding_id","parent_finding_id","display_claim","client_explanation")} for c in fr["client_findings"]], indent=1))
p8 = fr["phase8"]
for p in p8["propositions"]:
    q = {k: v for k, v in p.items() if k not in ("original_span",)}
    print("PROP", json.dumps(q, indent=1))
print("LOGIC", json.dumps(p8["logic"]))
print("DESCS", json.dumps(p8.get("evidence_descriptions"), indent=1))
print("BRIDGES", json.dumps(p8.get("bridges"), indent=1))
print("TRANSFERS", json.dumps(p8.get("product_transfers"), indent=1))
for tr in p8["transformations"]:
    print("TRANS", tr["transformation_id"], tr["stage"], tr["target_id"], "asserted", tr["asserted_state"], "whole", tr["asserts_whole_claim"], "| reason:", tr["reason"])
print("TAXO", json.dumps(fr.get("phase8_taxonomy"), indent=1))
