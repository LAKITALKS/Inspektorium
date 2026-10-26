import sys; sys.path.insert(0, sys.argv[1])
from h import *

def fix_from_attrs(fr):
    for t in fr['phase8']['transformations']:
        if t['stage'] == 'extraction' and not any(v for v in (t['from_attributes'] or {}).values()):
            t['from_attributes'] = copy.deepcopy(t['to_attributes'])

def P(fr, pid):
    return next(p for p in fr['phase8']['propositions'] if p['proposition_id'] == pid)
def D(fr, eid):
    return next(d for d in fr['phase8']['evidence_descriptions'] if d['evidence_id'] == eid)
def E(fr, eid):
    return next(d for d in fr['evidence'] if d['evidence_id'] == eid)
def F(fr, fid):
    return next(d for d in fr['findings'] if d['finding_id'] == fid)

# ---------- LS-03 ----------
j, task = load('009'); base = j['forensic_record']
print('#### LS-03 p1 typings')
for et, rnd, lim, comp, rel in [('controlled_intervention', None, None, None, None),
                                ('controlled_intervention', None, [], None, None),
                                ('controlled_intervention', False, [], None, None),
                                ('descriptive', None, None, None, None),
                                ('observational', None, None, None, None),
                                ('controlled_intervention', True, [], None, None),
                                ('controlled_intervention', True, [], 'between', None),
                                ('controlled_intervention', True, [], 'within', None),
                                ('descriptive', None, None, None, 'description'),
                                ('unknown', None, None, None, 'description')]:
    fr = copy.deepcopy(base); d = D(fr, 'e1'); d['evidence_type'] = et
    if rnd is not None or et == 'controlled_intervention': d['randomized'] = rnd
    if lim is not None: d['design_limitations'] = lim
    if comp: d['attributes']['comparison'] = comp
    if rel:
        P(fr, 'claim:p1')['attributes']['relation'] = rel
        for t in fr['phase8']['transformations']:
            if t['from_proposition_ids'] == ['claim:p1']:
                t['to_attributes']['relation'] = rel
                if t['from_attributes']: t['from_attributes']['relation'] = rel
    fix_from_attrs(fr)
    a = run(fr, task)
    if not a['propositions']:
        print('  INVALID', et, rel, a['reasons'][:3]); continue
    p1 = a['propositions'][0]
    print(f"  et={et} rnd={rnd} lim={lim} comp={comp} rel={rel} -> p1 {p1['derived_state']} | {[r for r in p1['reasons'] if 'b1' not in r][-2]}")

print('#### LS-03 p2 alternative encodings')
def ls03_p2(mode, dirn='indirect', e2_role='weakening'):
    fr = copy.deepcopy(base); p2 = P(fr, 'claim:p2'); p8 = fr['phase8']
    E(fr, 'e2')['role'] = e2_role
    if mode == 'bridge':
        p2['evidence_bindings'] = [{"binding_id": "b2", "proposition_id": "claim:p2", "evidence_id": "e1", "directness": dirn,
            "observation": "support", "search_scope_id": "ss1", "reason": "Only LDL, a surrogate, was measured."}]
        p8['bridges'] = [{"bridge_id": "br1", "kind": "semantic_transfer", "premise_proposition_ids": [],
            "conclusion_proposition_id": "claim:p2", "evidence_ids": ["e2"], "dimensions": ["endpoint", "endpoint_type"],
            "state": "unsupported", "reason": "LDL reduction cannot be transferred to heart attacks: no cardiovascular events were tracked."}]
        p2['required_bridge_ids'] = ['br1']; p2['observation_target'] = 'support'
        fr['negative_assertions'] = []
        F(fr, 'claim:p2')['supporting_evidence_ids'] = ['e1']; F(fr, 'claim:p2')['contrary_evidence_ids'] = []
        fr['client_findings'][0]['referenced_evidence_ids'] = ['e1']
    if mode == 'both':  # keep absence binding AND add surrogate binding
        p2['evidence_bindings'].append({"binding_id": "b3", "proposition_id": "claim:p2", "evidence_id": "e1", "directness": dirn,
            "observation": "support", "search_scope_id": "ss1", "reason": "Only LDL, a surrogate, was measured."})
        F(fr, 'claim:p2')['supporting_evidence_ids'] = ['e1']
        fr['client_findings'][0]['referenced_evidence_ids'] = ['e2', 'e1']
    if mode == 'inconclusive':
        p2['evidence_bindings'][0]['observation'] = 'inconclusive'
        fr['negative_assertions'] = []
    tax = fr.get('phase8_taxonomy') or {}
    fix_from_attrs(fr)
    return fr
for mode, kw in [('bridge', {}), ('bridge', {'dirn': 'remote'}), ('bridge', {'dirn': 'direct'}), ('both', {}), ('inconclusive', {})]:
    a = run(ls03_p2(mode, **kw), task)
    show(a, f'LS-03 p2 {mode} {kw}')
    print('   derived_label', a.get('derived_label'), [c['findings'] for c in a.get('phase7_controls', []) if c['findings']], a.get('taxonomy', {}).get('errors') if isinstance(a.get('taxonomy'), dict) else '')

# ---------- LS-04 ----------
j, task = load('010'); base4 = j['forensic_record']
print('#### LS-04 p1 comparison variants (from_attributes fixed)')
for comp in [None, 'unknown', 'within', 'between']:
    fr = copy.deepcopy(base4); fix_from_attrs(fr)
    if comp: D(fr, 'E1')['attributes']['comparison'] = comp
    a = run(fr, task)
    print(f"  comparison={comp}: status={a['technical_status']} composite={a['composite_state']} p1={a['propositions'][0]['derived_state']} p2={a['propositions'][1]['derived_state']} findings={a.get('transformation_findings')}")
print('#### LS-04 p2 alternative: bind E1 (reading) to p2, E2 material false/dropped')
for drop in ['drop', 'material_false']:
    fr = copy.deepcopy(base4); fix_from_attrs(fr); D(fr, 'E1')['attributes']['comparison'] = 'between'
    p2 = P(fr, 'claim:p2')
    p2['evidence_bindings'] = [{"binding_id": "b2", "proposition_id": "claim:p2", "evidence_id": "E1", "directness": "indirect",
        "observation": "support", "search_scope_id": "S1", "reason": "The trial reports only reading progress, not absenteeism."}]
    p2['observation_target'] = 'support'; fr['negative_assertions'] = []
    F(fr, 'claim:p2')['supporting_evidence_ids'] = ['E1']
    if drop == 'drop':
        fr['evidence'] = [e for e in fr['evidence'] if e['evidence_id'] != 'E2']
        fr['phase8']['evidence_descriptions'] = [d for d in fr['phase8']['evidence_descriptions'] if d['evidence_id'] != 'E2']
        if fr.get('phase8_taxonomy'):
            fr['phase8_taxonomy']['evidence_ids'] = [e for e in fr['phase8_taxonomy'].get('evidence_ids', []) if e != 'E2']
    else:
        E(fr, 'E2')['material'] = False
    a = run(fr, task)
    show(a, f'LS-04 p2 {drop}')

# ---------- LS-05 ----------
j, task = load('011'); fr = copy.deepcopy(j['forensic_record']); fix_from_attrs(fr)
a = run(fr, task); show(a, 'LS-05 from_attributes fixed')
fr2 = copy.deepcopy(fr); P(fr2, 'claim:p1')['reported_verdict'] = 'unsupported'
for t in fr2['phase8']['transformations']: t['asserted_state'] = 'unsupported'
a = run(fr2, task); print('  LS-05 if reported unsupported:', a['technical_status'], a['propositions'][0]['derived_state'], a.get('transformation_findings'))

# ---------- LS-06 ----------
j, task = load('012'); base6 = j['forensic_record']
def ls06(lim_on_e3=None, e3_quote="Randomized controlled trials tell a different story", fix=True):
    fr = copy.deepcopy(base6)
    fr['evidence'].append({"evidence_id": "e3", "source_id": "context", "role": "contradictory", "endpoint": "body weight",
        "material": True, "exact_reference": e3_quote, "text": e3_quote, "value_origin": "source_reported"})
    d2 = D(fr, 'e2'); d2['underlying_evidence_ids'] = ['e3']
    attrs = copy.deepcopy(d2['attributes']); attrs['comparison'] = 'between'
    fr['phase8']['evidence_descriptions'].append({"evidence_id": "e3", "evidence_type": "controlled_intervention",
        "source_role": "RCTs pooled by the meta-analysis", "attributes": attrs, "randomized": True,
        "design_limitations": lim_on_e3 or []})
    if fix: fix_from_attrs(fr)
    return fr
for kw in [dict(), dict(lim_on_e3=['context gives no trial-level details']), dict(fix=False),
           dict(e3_quote="adults assigned to eat breakfast consumed more total daily calories and, if anything, weighed slightly more than those assigned to skip it")]:
    a = run(ls06(**kw), task); show(a, f'LS-06 underlying {kw}')
