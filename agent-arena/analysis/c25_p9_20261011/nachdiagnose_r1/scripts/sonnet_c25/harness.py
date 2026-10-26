import json, sys, copy
REPO = "__LOCAL_HOME__/Documents/Projects/agent-arena"
from agent_arena.phase8_pipeline import assess_forensic_payload
from agent_arena.schemas import ForensicRecord
from agent_arena.phase8_semantics import evaluate_phase8

def load(attempt, ls):
    cap = json.load(open(f"{REPO}/analysis/live_smoke_20261011/repair_r1/captures/attempt-{attempt}.json"))
    t = cap["interpretation"]["final_text"]
    j = json.loads(t[t.find("{"):t.rfind("}")+1])
    task = json.load(open(f"{REPO}/analysis/live_smoke_20261011/live_run/tasks/{ls}.json"))
    return j["forensic_record"], task

def run(fr, task, show=True, label=""):
    a = assess_forensic_payload(copy.deepcopy(fr), original_input=task["prompt"], context=task["context"])
    if show:
        print("==", label, "status", a["technical_status"], "composite", a.get("composite_state"), "assessed", a.get("assessed_composite_state"))
        for p in a.get("propositions", []):
            print("   ", p["proposition_id"], p["reported_verdict"], "->", p["derived_state"])
            for r in p["reasons"]:
                print("       -", r)
        print("    TF:", a.get("transformation_findings"))
        other = [r for r in a.get("reasons", []) if not r.startswith("t") and "Ledger, evidence" not in r and "Phase 7 artifact_source_binding_drift" not in r]
        if other: print("    other reasons:", other[:6])
    return a
