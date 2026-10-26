import sys, json, re, collections
B="__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
sys.path.insert(0, B+"/src")
from agent_arena import phase7a_execution as p7
units = p7.resolve_evaluated_units(B)
print(len(units), collections.Counter(u.unit_type for u in units))
m = units[0].meta(); print(sorted(m))
v = [u for u in units if u.unit_type=="perturbation_variant"][0]; print({k:(str(x)[:80]) for k,x in v.meta().items()})
blob = json.dumps([u.meta() for u in units])
print("case ids referenced:", sorted(set(re.findall(r"case\d{3}", blob)))[:40])
print("BIAA refs:", sorted(set(re.findall(r"BIAA-\d+", blob))))
