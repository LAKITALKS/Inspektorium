import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
def fixp1(fr):
    P(fr)['not_applicable']['certainty']='x'; D(fr,'ev1')['attributes']['intervention']='virtual tutoring program'; D(fr,'ev1')['design_limitations']=[]
def a2(fr):
    P(fr,'claim:p2')['not_applicable']['certainty']='claim states no certainty level'
    set_attr(fr,'claim:p2','endpoint_type','educational_outcome')
a,o=run(4,a2,label='p2: C12 fixed only'); reasons(a,'claim:p2')
def m(fr): fixp1(fr); a2(fr)
a,o=run(4,m,label='p1 a+b+c and p2 C12 fixed')
# bridge route for p2: unsupported semantic_transfer bridge from reading evidence to absenteeism
def m(fr):
    fixp1(fr); a2(fr)
    fr['phase8']['bridges']=[{"bridge_id":"br2","kind":"semantic_transfer","premise_proposition_ids":[],
      "conclusion_proposition_id":"claim:p2","evidence_ids":["ev1"],"dimensions":["endpoint"],
      "state":"unsupported","reason":"Reading-progress results do not transfer to absenteeism."}]
    P(fr,'claim:p2')['required_bridge_ids']=['br2']
a,o=run(4,m,label='p1 fixed, p2 C12 fixed + unsupported semantic_transfer bridge'); reasons(a,'claim:p2')
# p2 with observation_target no_evidence_found AND relation description? (not faithful)
def m(fr):
    a2(fr); set_attr(fr,'claim:p2','relation','description')
a,o=run(4,m,label='p2 relation=description (unfaithful)')
# p2 with no bindings at all
