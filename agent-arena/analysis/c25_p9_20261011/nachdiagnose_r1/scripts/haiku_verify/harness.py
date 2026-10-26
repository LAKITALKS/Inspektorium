import json, sys, re, copy, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
REPO='__LOCAL_HOME__/Documents/Projects/agent-arena'
sys.path.insert(0, REPO+'/src')
from dump import load_capture
from agent_arena.phase8_pipeline import assess_forensic_payload
def task(tid):
    return json.load(open(f'{REPO}/analysis/live_smoke_20261011/live_run/tasks/{tid}.json'))
def run(n, mutate=None, verbose=True, label=''):
    d,j=load_capture(n)
    t=task(d['task_id'].split('-')[-1] if False else 'LS-0'+d['task_id'][-1])
    fr=copy.deepcopy(j['forensic_record'])
    if mutate: mutate(fr)
    a=assess_forensic_payload(fr, original_input=t['prompt'], context=t['context'], original_label=j.get('final_answer'))
    out={'label':label,'status':a['technical_status'],'composite':a.get('composite_state'),'assessed':a.get('assessed_composite_state'),
         'props':[(p['proposition_id'],p['reported_verdict'],p['derived_state']) for p in a.get('propositions',[])],
         'tf':a.get('transformation_findings'),'taxonomy':a.get('taxonomy',{}).get('technical_status'),'derived_label':a.get('derived_label')}
    if verbose:
        print(json.dumps(out,ensure_ascii=False))
    return a,out
def P(fr,pid='claim:p1'):
    return next(p for p in fr['phase8']['propositions'] if p['proposition_id']==pid)
def B(fr,bid):
    for p in fr['phase8']['propositions']:
        for b in p['evidence_bindings']:
            if b['binding_id']==bid: return b
def D(fr,eid):
    return next(x for x in fr['phase8']['evidence_descriptions'] if x['evidence_id']==eid)
def E(fr,eid):
    return next(x for x in fr['evidence'] if x['evidence_id']==eid)
def set_attr(fr,pid,k,v):
    """set proposition attribute AND keep transformations in sync"""
    P(fr,pid)['attributes'][k]=v
    for t in fr['phase8']['transformations']:
        if t['from_proposition_ids']==[pid] or (t['stage']=='summary' and t['from_proposition_ids']==[pid]):
            if t.get('from_attributes') is not None: t['from_attributes'][k]=v
            if t.get('to_attributes') is not None: t['to_attributes'][k]=v
def reasons(a,pid='claim:p1'):
    for p in a['propositions']:
        if p['proposition_id']==pid:
            for i,r in enumerate(p['reasons']): print(f'  [{i}] {r}')
