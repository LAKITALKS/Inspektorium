import sys; sys.path.insert(0, sys.argv[1])
from h import *
j, task = load('008')
base = j['forensic_record']

def variant(e1_role='supporting', directness='remote', required=True, dims=('population', 'endpoint', 'endpoint_type')):
    fr = copy.deepcopy(base); p8 = fr['phase8']; p = p8['propositions'][0]
    for e in fr['evidence']:
        if e['evidence_id'] == 'E1': e['role'] = e1_role
    p['evidence_bindings'] = [dict(p['evidence_bindings'][0], observation='support', directness=directness,
        reason='Cell-culture killing is reported, but for cultured cells, not patients.')]
    p8['bridges'] = [{"bridge_id": "br1", "kind": "semantic_transfer", "premise_proposition_ids": [],
        "conclusion_proposition_id": "claim:p1", "evidence_ids": ["E2"], "dimensions": list(dims),
        "state": "unsupported", "reason": "Transfer from cultured tumour cells to patients is unsupported: no animal or human data are described."}]
    p['required_bridge_ids'] = ['br1'] if required else []
    p['observation_target'] = 'support'
    fr['negative_assertions'] = []
    f = fr['findings'][0]; f['supporting_evidence_ids'] = ['E1'] if e1_role == 'supporting' else []
    f['contrary_evidence_ids'] = [] if e1_role == 'supporting' else ['E1']
    fr['client_findings'][0]['referenced_evidence_ids'] = ['E1']
    fr['phase8_taxonomy']['evidence_ids'] = ['E1']
    return fr

for kw in [dict(), dict(required=False), dict(directness='direct'), dict(directness='indirect', required=False),
           dict(dims=('population', 'species', 'endpoint', 'endpoint_type'))]:
    a = run(variant(**kw), task, j.get('final_answer'))
    show(a, f'LS-02 bridge variant {kw}')
    print('   derived_label', a.get('derived_label'), 'p7 controls', json.dumps(a.get('phase7_controls'))[:200])
