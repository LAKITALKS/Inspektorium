import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
def fill_et(fr): set_attr(fr,'claim:p1','endpoint_type','clinical')
print('--- LS-02 A: fill endpoint_type only')
a,_=run(2,fill_et); reasons(a)
def m_b(fr):
    fill_et(fr)
    E(fr,'ev-1')['role']='supporting'; B(fr,'bind-1')['observation']='support'
    f=fr['findings'][0]; f['supporting_evidence_ids']=['ev-1']; f['contrary_evidence_ids']=['ev-2']
print('--- LS-02 B: + ev-1 supporting/support (bind-2 kept)')
a,_=run(2,m_b); reasons(a)
def m_c(fr):
    m_b(fr)
    p=P(fr); p['evidence_bindings']=[b for b in p['evidence_bindings'] if b['binding_id']!='bind-2']
    E(fr,'ev-2')['material']=False
    f=fr['findings'][0]; f['contrary_evidence_ids']=[]
    fr['negative_assertions']=[]
    for c in fr['client_findings']:
        c['referenced_evidence_ids']=['ev-1']; c['client_negative_assertions']=[]
    fr['phase8']['evidence_descriptions']=[d for d in fr['phase8']['evidence_descriptions'] if d['evidence_id']!='ev-2']
print('--- LS-02 C: + ev-2 unbound, material false')
a,_=run(2,m_c); reasons(a)
# bridge route: keep both original bindings (inconclusive + no_evidence_found), add unsupported semantic_transfer bridge
def m_d(fr):
    fill_et(fr)
    fr['phase8']['bridges']=[{"bridge_id":"br1","kind":"semantic_transfer","premise_proposition_ids":[],
      "conclusion_proposition_id":"claim:p1","evidence_ids":["ev-1"],"dimensions":["species","endpoint"],
      "state":"unsupported","reason":"Cultured tumour-cell kill does not transfer to treating cancer in patients."}]
    P(fr)['required_bridge_ids']=['br1']
print('--- LS-02 D: original bindings kept + endpoint_type + unsupported semantic_transfer bridge')
a,_=run(2,m_d); reasons(a)
def m_e(fr):
    # bridge only, endpoint_type still missing
    fr['phase8']['bridges']=[{"bridge_id":"br1","kind":"semantic_transfer","premise_proposition_ids":[],
      "conclusion_proposition_id":"claim:p1","evidence_ids":["ev-1"],"dimensions":["species","endpoint"],
      "state":"unsupported","reason":"x"}]
    P(fr)['required_bridge_ids']=['br1']
print('--- LS-02 E: bridge but endpoint_type still null')
a,_=run(2,m_e)
