import sys, json
B, V = sys.argv[1], sys.argv[2]
sys.path.insert(0, B + "/src")
schema = json.load(open(B + "/analysis/phase6_3_report_prototype/forensic_report_schema.json"))
props = set(schema["properties"])
try:
    import jsonschema
    val = jsonschema.Draft202012Validator(schema)
except ImportError:
    val = None
print("jsonschema available:", val is not None)
for name, path in (("committed", B + "/analysis/phase6_3_report_prototype/example_full_report.json"),
                   ("regen_head", V + "/regen63_head/example_full_report.json")):
    r = json.load(open(path))
    print(name, "extra top keys:", sorted(set(r) - props), "| version:", r.get("report_schema_version"))
    if val:
        errs = list(val.iter_errors(r))
        print("   schema errors:", len(errs), [e.message[:110] for e in errs[:4]])
# Also all 15 fixtures through build_forensic_report at HEAD
from pathlib import Path
from agent_arena.forensic_report import build_forensic_report, validate_forensic_report
bad = 0
for fx in sorted(Path(B + "/analysis/phase6_3_report_prototype/fixtures").glob("*.json")):
    rep = build_forensic_report(json.loads(fx.read_text()))
    ok_py, _ = validate_forensic_report(rep)
    n = len(list(val.iter_errors(rep))) if val else None
    extra = sorted(set(rep) - props)
    if n: bad += 1
    print(f"  {fx.name:36s} py_validator_ok={ok_py} jsonschema_errors={n} extra={extra}")
print("fixtures failing frozen JSON schema:", bad)
