import json, sys, re, glob, os
REPO='__LOCAL_HOME__/Documents/Projects/agent-arena'
S=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load_capture(n):
    d=json.load(open(f'{REPO}/analysis/live_smoke_20261011/repair_r1/captures/attempt-{n:03d}.json'))
    ft=d['interpretation']['final_text'].strip()
    ft=re.sub(r'^```(?:json)?\s*','',ft); ft=re.sub(r'\s*```$','',ft)
    return d, json.loads(ft)
def find_bundle(task):
    for p in glob.glob(f'{S}/bundles/claude-haiku-5-5@2/*/record.json'):
        r=json.load(open(p))
        s=json.dumps(r)[:20000]
        if f'LS-0{task}' in s: return p, r
    return None,None
if __name__=='__main__':
    n=int(sys.argv[1])
    d,j=load_capture(n)
    print('task',d['task_id'],'slot',d['slot_key'])
    fr=j['forensic_record']; l=fr['phase8']
    print('final_answer', j.get('final_answer'))
    print('== evidence')
    for e in fr['evidence']: print(json.dumps(e,ensure_ascii=False))
    print('== scopes'); print(json.dumps(fr.get('search_scopes'),ensure_ascii=False))
    print('== negative_assertions'); print(json.dumps(fr.get('negative_assertions'),ensure_ascii=False))
    print('== descriptions')
    for e in l['evidence_descriptions']: print(json.dumps(e,ensure_ascii=False))
    print('== propositions')
    for p in l['propositions']: print(json.dumps(p,ensure_ascii=False,indent=1))
    print('== logic', json.dumps(l['logic']))
    print('== bridges', json.dumps(l.get('bridges'),ensure_ascii=False))
    print('== transfers', json.dumps(l.get('product_transfers'),ensure_ascii=False))
    print('== transformations')
    for t in l['transformations']:
        print(t['transformation_id'],t['stage'],t['target_id'],'asserted',t.get('asserted_state'),'whole',t.get('asserts_whole_claim'),'|',t.get('reason'))
    print('== findings'); print(json.dumps(fr.get('findings'),ensure_ascii=False,indent=1))
    print('== client'); print(json.dumps(fr.get('client_findings'),ensure_ascii=False,indent=1))
    print('== client_negative'); print(json.dumps(fr.get('client_negative_assertions'),ensure_ascii=False))
