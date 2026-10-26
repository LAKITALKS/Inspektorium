import json, re, sys, copy, glob, os
REPO = "__LOCAL_HOME__/Documents/Projects/agent-arena"
SCR = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/wf_second_opinion/adv_verify_sonnet"
sys.path.insert(0, REPO + "/src")
from agent_arena.phase8_pipeline import assess_forensic_payload

def load(att):
    d = json.load(open(f"{REPO}/analysis/live_smoke_20261011/repair_r1/captures/attempt-{att}.json"))
    t = d['interpretation']['final_text'].strip()
    t = re.sub(r'^```(?:json)?\s*', '', t); t = re.sub(r'```\s*$', '', t)
    j = json.loads(t)
    task = json.load(open(f"{REPO}/analysis/live_smoke_20261011/live_run/tasks/{d['task_id'].split('-')[-2]}-{d['task_id'].split('-')[-1]}.json"))
    return j, task

def run(fr, task, label=None):
    return assess_forensic_payload(copy.deepcopy(fr), original_input=task['prompt'], context=task.get('context') or '', original_label=label)

def show(a, tag=''):
    print(f"--- {tag}: status={a['technical_status']} composite={a.get('composite_state')} assessed={a.get('assessed_composite_state')}")
    for p in a.get('propositions', []):
        print(f"   {p['proposition_id']} reported={p['reported_verdict']} derived={p['derived_state']}")
        for r in p['reasons']:
            print('       r:', r[:160])
    for f in a.get('transformation_findings', []) or []:
        print('   F', f)
    if a['technical_status'] != 'completed' and not a.get('transformation_findings'):
        for r in a.get('reasons', [])[:12]: print('   R', r[:220])

def bundle(uuid):
    r = json.load(open(f"{SCR}/bundles/claude-sonnet-5-5@2/{uuid}/record.json"))
    return r['run_record']['results'][0]['agent_result']['phase8']

def same(a, b):
    keys = ['technical_status', 'composite_state', 'assessed_composite_state', 'transformation_findings']
    ok = all(a.get(k) == b.get(k) for k in keys)
    ok &= [(p['proposition_id'], p['derived_state'], p['reasons']) for p in a['propositions']] == \
          [(p['proposition_id'], p['derived_state'], p['reasons']) for p in b['propositions']]
    return ok
