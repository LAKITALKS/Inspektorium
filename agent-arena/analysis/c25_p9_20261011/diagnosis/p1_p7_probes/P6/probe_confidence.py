"""P6 probe: confidence (VALID high / MISSING / INVALID) must never override UNKNOWN or a missing control on the current P10 offline audit path."""
import sys, json, tempfile
from pathlib import Path
B = sys.argv[1]
sys.path.insert(0, B + "/src"); sys.path.insert(0, B)
from tests.test_phase10_bundle import recorded
from agent_arena.phase10_bundle import run_audit
from agent_arena.phase9_runtime import OfflineReviewProvider

SENTINEL = object()
def run(label, state, conf=SENTINEL, mutate=None):
    task, raw = recorded(state)
    resp = json.loads(raw)
    if conf is SENTINEL: pass
    elif conf == "<drop>": resp.pop("confidence")
    else: resp["confidence"] = conf
    if mutate: mutate(resp)
    with tempfile.TemporaryDirectory(dir=sys.argv[2]) as d:
        r = run_audit(task, OfflineReviewProvider(json.dumps(resp)), output_root=Path(d))
        failing = []
        if r.path:
            dec = json.loads((Path(r.path) / "decision.json").read_text())
            failing = [c["control_id"] for c in dec["controls"] if c["outcome"] == "fail"]
            rec = json.loads((Path(r.path) / "record.json").read_text())
            res = rec["run_record"]["results"][0]["agent_result"]; md = (Path(r.path)/"report.md").read_text(); print("   report.md mentions confidence:", "onfidence" in md)
            cs = (res.get("parsed") or {}).get("confidence_state")
            cv = (res.get("parsed") or {}).get("confidence")
        else:
            cs = cv = None
        print(f"{label:48s} status={r.status:20s} conf_state={cs} conf={cv} failing={failing}")

run("supported, default .82", "supported")
run("supported, conf 1.0", "supported", 1.0)
run("unknown, conf 1.0", "unknown", 1.0)
run("contradicted, conf 1.0", "contradicted", 1.0)
run("supported, conf 1.0, evidence emptied", "supported", 1.0, lambda r: r["forensic_record"].__setitem__("evidence", []))
run("supported, conf 1.0, client_findings emptied", "supported", 1.0, lambda r: r["forensic_record"].__setitem__("client_findings", []))
run("supported, confidence MISSING (key dropped)", "supported", "<drop>")
run("supported, confidence INVALID 'high'", "supported", "high")
run("supported, confidence INVALID 1.7", "supported", 1.7)
run("supported, confidence null", "supported", None)
