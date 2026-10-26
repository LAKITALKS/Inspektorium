import sys,os,json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
def m_d(fr):
    set_attr(fr,'claim:p1','endpoint_type','clinical')
    fr['phase8']['bridges']=[{"bridge_id":"br1","kind":"semantic_transfer","premise_proposition_ids":[],
      "conclusion_proposition_id":"claim:p1","evidence_ids":["ev-1"],"dimensions":["species","endpoint"],
      "state":"unsupported","reason":"Cultured tumour-cell kill does not transfer to treating cancer in patients."}]
    P(fr)['required_bridge_ids']=['br1']
a,o=run(2,m_d,label='LS-02 D taxonomy detail')
print(json.dumps(a['taxonomy'].get('reasons'),ensure_ascii=False)[:1500])
# baseline taxonomy of LS-02 original
a,o=run(2,None,label='LS-02 baseline taxonomy')
print(json.dumps(a['taxonomy'].get('reasons'),ensure_ascii=False)[:800])
# LS-04 p1: only certainty fixed -> reasons
def m(fr): P(fr)['not_applicable']['certainty']='x'
a,o=run(4,m,label='LS-04 a only'); reasons(a)
def m(fr):
    P(fr)['not_applicable']['certainty']='x'
    P(fr)['evidence_bindings']=[x for x in P(fr)['evidence_bindings'] if x['binding_id']=='b1']
    f=[x for x in fr['findings'] if x['finding_id']=='claim:p1'][0]; f['supporting_evidence_ids']=['ev1']; f['contrary_evidence_ids']=[]
    E(fr,'ev2')['material']=False
a,o=run(4,m,label='LS-04 a only, b2 removed')
