import sys,os,copy; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
def ci(fr): D(fr,'ev:rct')['evidence_type']='controlled_intervention'
a,o=run(6,ci,label='ev:rct -> controlled_intervention'); reasons(a)
def und(fr):
    src="assigning people to eat breakfast did not cause weight loss"
    fr['evidence'].append({"evidence_id":"ev:rct_trials","source_id":"context","role":"contradictory","endpoint":"body weight","material":True,
       "exact_reference":"meta-analysis of RCTs","text":"meta-analysis of RCTs"})
    d=copy.deepcopy(D(fr,'ev:rct')); d['evidence_id']='ev:rct_trials'; d['evidence_type']='controlled_intervention'; d['source_role']='pooled RCTs'
    fr['phase8']['evidence_descriptions'].append(d)
    D(fr,'ev:rct')['underlying_evidence_ids']=['ev:rct_trials']
a,o=run(6,und,label='review kept + underlying controlled_intervention item'); reasons(a)
# honest intervention/population strings: proposition says 'eating a good breakfast every morning', population 'people generally'
def honest(fr):
    ci(fr); set_attr(fr,'claim:p1','intervention','eating a good breakfast every morning')
a,o=run(6,honest,label='controlled_intervention + honest intervention string (no transfer)'); reasons(a)
def honest2(fr):
    honest(fr)
    fr['phase8']['product_transfers']=[{"transfer_id":"pt","binding_id":"bind:p1:rct","state":"unknown_transfer","dimensions":["intervention"],"evidence_ids":["ev:rct"],"reason":"good-breakfast qualifier untested"}]
a,o=run(6,honest2,label='+ unknown_transfer'); reasons(a)
def honest3(fr):
    ci(fr); set_attr(fr,'claim:p1','population','people generally')
a,o=run(6,honest3,label='controlled_intervention + honest population string'); reasons(a)
