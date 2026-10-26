import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
rows = []
for rec in sorted(root.rglob("record.json")):
    d = json.loads(rec.read_text())
    rr = d.get("run_record", d)
    res = rr["results"][0]
    ar = res["agent_result"]
    case = (rr.get("task") or {}).get("id") or (rr.get("task") or {}).get("task_id")
    p8 = ar.get("phase8") or {}
    p9 = (rr.get("metadata") or {}).get("phase9") or {}
    # model JSON
    final_text = ar.get("raw_output") or ""
    model = None
    for key in ("forensic_record",):
        pass
    try:
        model = json.loads(final_text)
    except Exception:
        model = None
    ledger = None
    if model:
        fr = model.get("forensic_record") or {}
        ledger = fr.get("phase8")
    print("=" * 80)
    print(rec.parent.parent.name, case, "tech=", p8.get("technical_status"),
          "composite=", p8.get("composite_state"), "assessed=", p8.get("assessed_composite_state"),
          "route=", p9.get("route") if isinstance(p9, dict) else None)
    for prop in p8.get("propositions", []):
        print("  prop", prop["proposition_id"], "reported=", prop["reported_verdict"], "derived=", prop["derived_state"])
    for f in p8.get("transformation_findings", []):
        print("  finding:", f)
    if ledger:
        for t in ledger.get("transformations", []):
            fa = t.get("from_attributes") or {}
            nonnull = sum(1 for v in fa.values() if v not in (None, ""))
            print("  trans", t.get("transformation_id"), t.get("stage"), t.get("target_id"),
                  "asserted=", t.get("asserted_state"), "whole=", t.get("asserts_whole_claim"),
                  "from_attr_nonnull=", nonnull)
