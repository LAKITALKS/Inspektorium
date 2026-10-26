import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
for et in ['descriptive','controlled_intervention','observational','in_vitro','review']:
    def m(fr,et=et): D(fr,'ev:1')['evidence_type']=et
    a,_=run(3,m,label='ev:1 type='+et)
# faithful causal coding of p1 with unknown type
def m2(fr): set_attr(fr,'claim:p1','relation','causal')
a,_=run(3,m2,label='p1 relation causal, ev:1 unknown'); reasons(a)
def m3(fr):
    set_attr(fr,'claim:p1','relation','causal'); D(fr,'ev:1')['evidence_type']='controlled_intervention'
a,_=run(3,m3,label='p1 causal, ev:1 controlled_intervention (randomized None, limitations kept)'); reasons(a)
# p2 without the bridge
def m4(fr):
    P(fr,'claim:p2')['required_bridge_ids']=[]
a,_=run(3,m4,label='p2 bridge requirement removed'); reasons(a,'claim:p2')
