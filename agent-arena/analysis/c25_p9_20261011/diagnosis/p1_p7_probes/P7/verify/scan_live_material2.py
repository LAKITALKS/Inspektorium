import glob, json, runpy, sys
from pathlib import Path
ns = runpy.run_path(str(Path(__file__).with_name("scan_live_material.py")), run_name="lib")
records, files = ns["records"], ns["files"]
uniq, ev_total, ev_false, bound_total = {}, 0, 0, 0
for f in files:
    for fr in records(json.load(open(f))):
        uniq[json.dumps(fr, sort_keys=True)] = fr
for fr in uniq.values():
    p8 = fr.get("phase8") or {}
    bound = {b.get("evidence_id") for p in (p8.get("propositions") or []) if isinstance(p, dict)
             for b in (p.get("evidence_bindings") or []) if isinstance(b, dict)}
    for e in fr.get("evidence", []) or []:
        ev_total += 1
        ev_false += e.get("material") is False
        bound_total += e.get("evidence_id") in bound
print("unique forensic records:", len(uniq), "evidence items:", ev_total, "bound:", bound_total, "material false:", ev_false)
