import sys, json
B, S = sys.argv[1], sys.argv[2]
sys.path.insert(0, B+"/src")
schema=json.load(open(B+"/analysis/phase6_3_report_prototype/forensic_report_schema.json"))
print("schema top additionalProperties:", schema.get("additionalProperties"), "required:", len(schema.get("required",[])))
props=set(schema.get("properties",{}))
for name,path in (("committed",B+"/analysis/phase6_3_report_prototype/example_full_report.json"),("regen",S+"/regen63/example_full_report.json")):
    r=json.load(open(path)); print(name, "keys not in schema:", sorted(set(r)-props))
try:
    import jsonschema
    for name,path in (("committed",B+"/analysis/phase6_3_report_prototype/example_full_report.json"),("regen",S+"/regen63/example_full_report.json")):
        errs=list(jsonschema.Draft202012Validator(schema).iter_errors(json.load(open(path))))
        print(name,"jsonschema errors:",len(errs), [e.message[:120] for e in errs[:3]])
except ImportError: print("no jsonschema")
from agent_arena import forensic_report as fr
print([n for n in dir(fr) if "schema" in n.lower() or "valid" in n.lower()])
