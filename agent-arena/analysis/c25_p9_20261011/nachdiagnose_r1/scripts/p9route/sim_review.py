"""Offline downstream of the CF-A counterfactual: what _run_live would do after REVIEW_RECOMMENDED.

Reviewer = OfflineReviewProvider replaying the slot's own original raw output (best case: the
review fully agrees). No live provider, no network; state lives under <out>/state only.
Usage: python -B -I sim_review.py <bundles_dir> <out_dir>
"""
import glob
import json
import sys
from copy import deepcopy
from pathlib import Path

import agent_arena.phase8_semantics as sem
from agent_arena.phase9_pipeline import assess_run
from agent_arena.phase9_runtime import OfflineReviewProvider, execute_review
from agent_arena.schemas import RunRecord

ORIG = sem._audit_transformations


def audit_cf_a(ledger, assessments, composite):
    return [f for f in ORIG(ledger, assessments, composite) if ": output state hides or changes " not in f]


sem._audit_transformations = audit_cf_a

bundles, out = sys.argv[1], Path(sys.argv[2])
for path in sorted(glob.glob(f"{bundles}/*/*/record.json")):
    rr = deepcopy(json.load(open(path))["run_record"])
    rr["metadata"].pop("phase9", None)
    for r in rr["results"]:
        r["agent_result"]["phase9"] = {}
    record = RunRecord.model_validate(rr)
    slot = path.split("/")[-3][:13] + ":" + record.task.id[-5:]
    route0 = assess_run(record)["route"]
    if route0 != "REVIEW_RECOMMENDED":
        print(slot, "initial", route0, "-> no counterreview in _run_live")
        continue
    state = out / "state" / slot.replace(":", "_")
    raw = record.results[0].agent_result.raw_output
    after_cr = execute_review(record, OfflineReviewProvider(raw), base_dir=state, authorized=True,
                              budget_calls=2, kind="counterreview")
    d1 = after_cr.metadata["phase9"]
    cr = [a for a in d1.get("attempts", []) if a["kind"] == "counterreview"]
    line = (f"{slot} initial {route0} -> counterreview {cr[-1]['status'] if cr else None}; "
            f"route={d1['route']} mandatory={d1['mandatory']} tech={d1['technical_status']} "
            f"conflicts={len(d1.get('conflicts', []))} material={sum(c['material'] for c in d1.get('conflicts', []))} "
            f"adjudication={[a['outcome'] for a in d1.get('adjudications', [])]}")
    if cr and cr[-1]["status"] == "completed" and d1.get("mandatory") is True and d1.get("technical_status") == "completed":
        after_st = execute_review(after_cr, OfflineReviewProvider(raw), base_dir=state, authorized=True,
                                  budget_calls=2, kind="stability")
        d2 = after_st.metadata["phase9"]
        st = [a for a in d2.get("attempts", []) if a["kind"] == "stability"]
        n_ev = len((after_st.results[0].agent_result.parsed.forensic_record or {}).get("evidence", [])) \
            if after_st.results[0].agent_result.parsed else None
        line += (f" | stability {st[-1]['status'] if st else None} ({(st[-1].get('reason') or '')[:70]}); "
                 f"evidence_items={n_ev}; final route={d2['route']} review_state={d2['review_state']}")
    print(line)
