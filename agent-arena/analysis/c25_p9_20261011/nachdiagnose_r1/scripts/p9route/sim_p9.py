"""Offline counterfactual P9 routing over archived AA-P10-LIVE R1 bundles.

In-memory monkeypatch only; no repo file is written, no provider is called.
Usage: python -I sim_p9.py <bundles_dir> <out_json>
"""
import glob
import json
import sys
from copy import deepcopy

import agent_arena.phase8_semantics as sem
from agent_arena.output_contract import parse_structured_output
from agent_arena.phase9_review import assess_case, position_from_result
from agent_arena.schemas import RunRecord

STATE = ": output state hides or changes "
ATTR = ": semantic transformation changes "

ORIG_AUDIT = sem._audit_transformations
ORIG_EVAL = sem.evaluate_phase8
MODE = {"name": "baseline"}
DISAGREEMENTS = []


def audit_patched(ledger, assessments, composite):
    findings = ORIG_AUDIT(ledger, assessments, composite)
    name = MODE["name"]
    if name in ("baseline", "cf_b_keep_findings"):
        return findings
    trans = {t.transformation_id: t for t in ledger.transformations}
    keep = []
    for f in findings:
        tid = f.split(":", 1)[0]
        t = trans.get(tid)
        if STATE in f:
            DISAGREEMENTS.append(f)  # recorded separately, not a finding
            continue
        if name == "cf_c_also_extraction_attrs" and ATTR in f and t is not None and t.stage == "extraction":
            DISAGREEMENTS.append("[waived extraction attr] " + f)
            continue
        keep.append(f)
    return keep


def eval_patched(record):
    result = ORIG_EVAL(record)
    if MODE["name"] != "cf_b_keep_findings" or result.technical_status != "incomplete":
        return result
    tf = result.transformation_findings
    if tf and all(STATE in f for f in tf):
        # Completed; composite = host-derived; mismatch stays visible as transformation finding.
        return result.model_copy(update={"technical_status": "completed",
                                         "composite_state": result.assessed_composite_state})
    return result


sem._audit_transformations = audit_patched
sem.evaluate_phase8 = eval_patched


def model_view(task, result):
    parsed, _ = parse_structured_output(result.raw_output, result.finish_reason)
    fr = parsed.forensic_record if parsed else {}
    ledger = (fr or {}).get("phase8") or {}
    props = {p["proposition_id"]: {"reported_verdict": p.get("reported_verdict"),
                                   "materiality": p.get("materiality")}
             for p in ledger.get("propositions", []) if isinstance(p, dict)}
    trans = [{"id": t.get("transformation_id"), "stage": t.get("stage"),
              "from": t.get("from_proposition_ids"), "asserted_state": t.get("asserted_state"),
              "whole": t.get("asserts_whole_claim")}
             for t in ledger.get("transformations", []) if t.get("asserted_state") is not None]
    return {"final_answer": getattr(parsed, "final_answer", None) if parsed else None,
            "logic": ledger.get("logic"), "propositions": props, "asserted": trans}


def run(bundles, mode):
    MODE["name"] = mode
    rows = []
    for path in sorted(glob.glob(f"{bundles}/*/*/record.json")):
        audit = json.load(open(path))
        rr = deepcopy(audit["run_record"])
        # Fresh record as at _run_live line 210, before any Phase9 carrier is cached.
        rr["metadata"].pop("phase9", None)
        for r in rr["results"]:
            r["agent_result"]["phase9"] = {}
        record = RunRecord.model_validate(rr)
        DISAGREEMENTS.clear()
        positions = [position_from_result(record.task, r.agent_result, record.run_id) for r in record.results]
        a = assess_case(record.task, positions).model_dump(mode="json")
        p8 = positions[0].phase8
        rows.append({
            "profile": path.split("/")[-3], "case": record.task.id.rsplit("-", 1)[-1] if False else record.task.id[-5:],
            "stored_status": audit["status"],
            "stored_route": audit["run_record"]["metadata"]["phase9"]["route"],
            "phase8_technical": p8.get("technical_status"),
            "composite": p8.get("composite_state"), "assessed_composite": p8.get("assessed_composite_state"),
            "taxonomy": p8.get("taxonomy", {}).get("technical_status"),
            "derived_label": p8.get("derived_label"), "original_label": p8.get("original_model_label"),
            "host_states": {p["proposition_id"]: p["derived_state"] for p in p8.get("propositions", [])},
            "remaining_findings": p8.get("transformation_findings", []),
            "phase7_major": [f.get("code") for c in p8.get("phase7_controls", []) for f in c.get("findings", [])
                             if f.get("severity") in {"critical", "major"}],
            "recorded_disagreements": list(DISAGREEMENTS),
            "route": a["route"], "mandatory": a["mandatory"], "p9_technical": a["technical_status"],
            "triggers": sorted({(t["code"], t["field"], t["mandatory"]) for t in a["triggers"]}),
            "counterreview_requested_by__run_live": a["route"] == "REVIEW_RECOMMENDED",
            "model": model_view(record.task, record.results[0].agent_result),
        })
    return rows


if __name__ == "__main__":
    bundles, out = sys.argv[1], sys.argv[2]
    result = {m: run(bundles, m) for m in ("baseline", "cf_a_drop_state_findings",
                                            "cf_b_keep_findings", "cf_c_also_extraction_attrs")}
    json.dump(result, open(out, "w"), indent=1, default=list)
    for m, rows in result.items():
        print("==", m)
        for r in rows:
            print(f"{r['profile'][:13]:13} {r['case']} p8={r['phase8_technical']:10} comp={r['composite']:12} "
                  f"tax={r['taxonomy']:10} route={r['route']:22} mand={r['mandatory']!s:5} "
                  f"CR={r['counterreview_requested_by__run_live']!s:5} "
                  f"trig={sorted({c for c, _, m in r['triggers'] if m})} nonmand={sorted({c for c, _, m in r['triggers'] if not m})}")
