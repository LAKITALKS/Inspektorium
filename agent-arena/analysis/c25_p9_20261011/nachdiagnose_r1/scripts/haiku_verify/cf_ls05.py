import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
for obs in ['no_effect_observed','unknown','search_incomplete','support']:
    def m(fr,obs=obs):
        B(fr,'b1')['observation']=obs
        if obs=='support': E(fr,'ev1')['role']='supporting'
    a,o=run(5,m,label='b1.observation='+obs); reasons(a)
# no_effect_observed with matching scope (hypothetical: evidence attrs equal to proposition) -> contract row 130
def m(fr):
    B(fr,'b1')['observation']='no_effect_observed'
    D(fr,'ev1')['attributes']=dict(P(fr)['attributes']); D(fr,'ev1')['attributes']['effect_direction']='harm'
    D(fr,'ev1')['evidence_type']='controlled_intervention'; D(fr,'ev1')['randomized']=True; D(fr,'ev1')['design_limitations']=[]
    D(fr,'ev1')['attributes']['comparison']='between'
    B(fr,'b1')['directness']='direct'
a,o=run(5,m,label='hypothetical matching-scope no_effect_observed'); reasons(a)
# reported verdict unknown (what model would need to match host)
def m(fr):
    P(fr)['reported_verdict']='unknown'
    for t in fr['phase8']['transformations']:
        if t.get('asserted_state'): t['asserted_state']='unknown'
a,o=run(5,m,label='model reports unknown + asserts unknown')
