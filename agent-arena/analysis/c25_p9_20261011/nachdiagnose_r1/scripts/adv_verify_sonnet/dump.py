import json, sys, re
path = sys.argv[1]
d = json.load(open(path))
t = d['interpretation']['final_text'].strip()
t = re.sub(r'^```(?:json)?\s*', '', t); t = re.sub(r'```\s*$', '', t)
j = json.loads(t)
fr = j['forensic_record']
p8 = fr['phase8']
out = {
 'slot': d['slot_key'], 'final_answer': j.get('final_answer'),
 'evidence': fr.get('evidence'), 'search_scopes': fr.get('search_scopes'),
 'negative_assertions': fr.get('negative_assertions'), 'findings': fr.get('findings'),
 'client_findings': fr.get('client_findings'),
 'propositions': p8.get('propositions'), 'logic': p8.get('logic'),
 'evidence_descriptions': p8.get('evidence_descriptions'), 'bridges': p8.get('bridges'),
 'product_transfers': p8.get('product_transfers'), 'transformations': p8.get('transformations'),
}
print(json.dumps(out, indent=1, ensure_ascii=False))
