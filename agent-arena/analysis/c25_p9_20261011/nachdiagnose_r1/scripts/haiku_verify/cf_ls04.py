import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
def na_cert(fr,pid='claim:p1'): P(fr,pid)['not_applicable']['certainty']='claim states no certainty level'
def same_int(fr): D(fr,'ev1')['attributes']['intervention']='virtual tutoring program'
def no_dl(fr): D(fr,'ev1')['design_limitations']=[]
combos={'a':[na_cert],'b':[same_int],'c':[no_dl],'a+b':[na_cert,same_int],'a+c':[na_cert,no_dl],'b+c':[same_int,no_dl],'a+b+c':[na_cert,same_int,no_dl]}
for k,fs in combos.items():
    def m(fr,fs=fs):
        for f in fs: f(fr)
    a,o=run(4,m,label='p1 fix '+k)
    if k in ('a+b',): reasons(a)
# a+b+c but b2 removed? b2 irrelevance check: a+b+c with b2 observation support vs inconclusive
def m(fr):
    for f in [na_cert,same_int,no_dl]: f(fr)
    P(fr)['evidence_bindings']=[x for x in P(fr)['evidence_bindings'] if x['binding_id']=='b1']
    f=[x for x in fr['findings'] if x['finding_id']=='claim:p1'][0]
    f['supporting_evidence_ids']=['ev1']; f['contrary_evidence_ids']=[]
    E(fr,'ev2')['material']=False
a,o=run(4,m,label='a+b+c and b2 removed')
# honest population: ev1 population 'struggling elementary students in a rural school district'
def m(fr):
    for f in [na_cert,same_int,no_dl]: f(fr)
    D(fr,'ev1')['attributes']['population']='struggling elementary students in a rural school district'
a,o=run(4,m,label='a+b+c but honest population string'); reasons(a)
# ITT caveat recorded only as design limitation via randomized=None? check: a+b, design limitation kept but moved to uncertainty only
