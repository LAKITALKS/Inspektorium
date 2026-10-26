"""Verifier: re-run the committed K12 re-analysis (read-only on the checkout's committed captures) and
scan the 24 real captures for the F1/F2/F3 shapes. No provider call, no live session, no ledger write."""
import importlib.util
import json
import os
import sys
from copy import deepcopy
from pathlib import Path

DIAG = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new"
VDIR = Path("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_p8_p10/P8/verifier")
sys.path.insert(0, DIAG + "/src")
import agent_arena  # noqa: E402
assert agent_arena.__file__.startswith(DIAG), agent_arena.__file__
os.chdir(DIAG)  # the script uses repository-relative read paths; output goes to VDIR
spec = importlib.util.spec_from_file_location("k12", DIAG + "/analysis/c25_p9_20261011/reanalyse_captures.py")
k12 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(k12)
out = VDIR / "k12_rerun.json"
k12.main(out)
mine = json.loads(out.read_text())
committed = json.loads(Path(DIAG + "/analysis/c25_p9_20261011/historical_reanalysis.json").read_text())
print("counts equal:", mine["counts"] == committed["counts"])
diff = [c["attempt_id"] for c, d in zip(mine["captures"], committed["captures"])
        if c["reanalysis"] != d["reanalysis"] or c["difference_causes"] != d["difference_causes"]]
print("captures differing from committed K12:", len(diff), diff[:5])

# --- scan the same captures for F1/F2/F3 shapes
from agent_arena.output_contract import parse_structured_output  # noqa: E402
from agent_arena.phase8_pipeline import assess_forensic_payload  # noqa: E402
from agent_arena.phase8_taxonomy import assess_taxonomy  # noqa: E402
from agent_arena.phase9_review import assess_case, position_from_result  # noqa: E402
from agent_arena.schemas import AgentResult, ForensicRecord  # noqa: E402
from agent_arena.task_loader import load_task  # noqa: E402

BASE = Path("analysis/live_smoke_20261011")
f1_hits, f2_hits, f3_hits, optional_with_client, labels = [], [], [], 0, []
for run, directory in (("revision_1", BASE / "live_run"), ("repair_r1", BASE / "repair_r1")):
    ledger = json.loads((directory / "ledger.json").read_text())
    for attempt in ledger["attempts"]:
        capture = json.loads((directory / "captures" / f"{attempt['attempt_id']}.json").read_text())
        case = capture["task_id"].rsplit("-", 2)[-2] + "-" + capture["task_id"].rsplit("-", 1)[-1]
        task = load_task(BASE / "live_run/tasks" / f"{case}.json")
        text = capture["interpretation"]["final_text"]
        parsed, diag = parse_structured_output(text, "stop")
        payload = parsed.forensic_record if parsed else None
        a = assess_forensic_payload(payload, original_input=task.prompt, context=task.context,
                                    parse_complete=diag.ok)
        tag = f"{run}/{capture['profile_id']}/{case}"
        labels.append((tag, a["technical_status"], a.get("taxonomy", {}).get("technical_status"), a["derived_label"]))
        if not isinstance(payload, dict) or not isinstance(payload.get("phase8"), dict):
            continue
        led = payload["phase8"]
        ev_role = {e.get("evidence_id"): e.get("role") for e in payload.get("evidence", []) if isinstance(e, dict)}
        clients = {c.get("parent_finding_id") for c in payload.get("client_findings", []) if isinstance(c, dict)}
        for p in led.get("propositions", []) if isinstance(led.get("propositions"), list) else []:
            if not isinstance(p, dict) or p.get("materiality") == "required":
                continue
            if p.get("proposition_id") in clients:
                optional_with_client += 1
            for b in p.get("evidence_bindings", []):
                role = ev_role.get(b.get("evidence_id"))
                if (b.get("observation") == "support" and role != "supporting") or \
                        (b.get("observation") == "contradiction" and role != "contradictory"):
                    f2_hits.append((tag, p.get("proposition_id"), b.get("observation"), role,
                                    p.get("proposition_id") in clients))
        bids = [b.get("bridge_id", "") for b in led.get("bridges", []) if isinstance(b, dict)]
        if any(x != y and y.startswith(x + ": ") for x in bids for y in bids):
            f3_hits.append(tag)
        if a["technical_status"] == "completed" and a.get("taxonomy", {}).get("technical_status") == "completed":
            conflicted = [p["proposition_id"] for p in a["propositions"] if p["model_host_conflict"]]
            if conflicted:
                record = ForensicRecord.model_validate(payload)
                alt = {}
                for side in ("host_state", "reported_verdict"):
                    sem = deepcopy(a)
                    for p in sem["propositions"]:
                        if p["model_host_conflict"]:
                            p["derived_state"] = p[side]
                    alt[side] = assess_taxonomy(record, sem)["derived_label"]
                res = AgentResult(provider="x", model="m", raw_output=text, parsed=parsed, parse_ok=diag.ok,
                                  finish_reason="stop")
                route = assess_case(task, [position_from_result(task, res, "scan")])
                f1_hits.append((tag, a["derived_label"], alt, route.route,
                                sorted({t.code for t in route.triggers})))
print("labels (tag, p8, taxonomy, derived_label):")
for row in labels:
    print("  ", row)
print("F1 shape (completed + conflict): label actual vs label if host/model side adopted, route, triggers")
for row in f1_hits:
    print("  ", row)
print("F2 shape (optional proposition role/observation mismatch):", f2_hits,
      "| optional propositions with a client output:", optional_with_client)
print("F3 shape (bridge-ID prefix collision):", f3_hits)
