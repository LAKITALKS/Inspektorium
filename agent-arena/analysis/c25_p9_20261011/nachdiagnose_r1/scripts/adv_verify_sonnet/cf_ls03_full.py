import sys; sys.path.insert(0, sys.argv[1])
from h import *
exec(open(sys.argv[1] + '/cf_rest.py').read().split('# ---------- LS-03 ----------')[0].split('from h import *')[1])
j, task = load('009'); base = j['forensic_record']
fr = copy.deepcopy(base); p8 = fr['phase8']; p2 = P(fr, 'claim:p2'); p1 = P(fr, 'claim:p1')
# p2: surrogate binding + unsupported semantic_transfer bridge citing e2 (C26)
p2['evidence_bindings'] = [{"binding_id": "b2", "proposition_id": "claim:p2", "evidence_id": "e1", "directness": "indirect",
    "observation": "support", "search_scope_id": "ss1", "reason": "Only LDL, a surrogate, was measured."}]
p8['bridges'] = [{"bridge_id": "br1", "kind": "semantic_transfer", "premise_proposition_ids": [], "conclusion_proposition_id": "claim:p2",
    "evidence_ids": ["e2"], "dimensions": ["endpoint", "endpoint_type"], "state": "unsupported",
    "reason": "LDL reduction cannot be transferred to heart attacks: no cardiovascular events were tracked."}]
p2['required_bridge_ids'] = ['br1']; p2['observation_target'] = 'support'; fr['negative_assertions'] = []
F(fr, 'claim:p2')['supporting_evidence_ids'] = ['e1']; F(fr, 'claim:p2')['contrary_evidence_ids'] = []
fr['client_findings'][0]['referenced_evidence_ids'] = ['e1']
# p1: honest unknown (model's own uncertainty: control arm not stated)
p1['reported_verdict'] = 'unknown'
for t in p8['transformations']:
    if t['transformation_id'] == 't3': t['asserted_state'] = 'unknown'
fix_from_attrs(fr); fr["phase8_taxonomy"]["evidence_ids"] = ["e1"]; fr["phase8_taxonomy"]["trigger_evidence_id"] = "e1"
a = run(fr, task, j.get('final_answer')); show(a, 'LS-03 full honest variant'); print("derived_label", a.get("derived_label"), json.dumps(a.get("taxonomy"))[:900])
