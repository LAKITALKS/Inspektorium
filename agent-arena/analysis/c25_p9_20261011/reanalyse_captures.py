"""K12: re-analyse every stored live capture under the current AA-P8/AA-P9 contract (offline, no model call).

Provenance class 2 of the work order: a new analysis of the unchanged original response under
the new contract. It never rewrites captures, ledgers, bundles or original results; the
original results are read from the archived run summaries (class 1). Run from the repository
root:  .venv/bin/python analysis/c25_p9_20261011/reanalyse_captures.py OUTPUT.json
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from agent_arena import phase8_models
from agent_arena.output_contract import parse_structured_output
from agent_arena.phase8_pipeline import assess_forensic_payload
from agent_arena.phase9_review import assess_case, position_from_result
from agent_arena.schemas import AgentResult
from agent_arena.task_loader import load_task

BASE = Path("analysis/live_smoke_20261011")
RUNS = (
    ("revision_1", BASE / "live_run", BASE / "evidence/smoke_summary.json"),
    ("repair_r1", BASE / "repair_r1", BASE / "repair_r1/evidence/smoke_summary_r1.json"),
)


def original_rows(summary_path):
    rows = {}
    for slot in json.loads(summary_path.read_text())["slots"]:
        reasons = [r for r in slot["extraction"]["reasons"] if "Phase-8 output binding incomplete" not in r]
        rows[(slot["profile"], slot["case"])] = {
            "status": slot["status"], "phase8_technical": slot["extraction"]["phase8_technical"],
            "composite": slot["semantics"]["composite"], "route": slot["review"]["route"],
            "reasons": reasons}
    return rows


def classify(original, new):
    """Name the cause of every difference between the original and the new analysis."""
    causes = []
    old_c25_state = [r for r in original["reasons"] if "output state hides or changes" in r]
    old_from_attributes = [r for r in original["reasons"] if "semantic transformation changes" in r]
    if old_c25_state and not any("changes the model's own judgment" in f for f in new["findings"]):
        causes.append("AA-P8/1.1 C25: asserted state now checked against the model's own judgment; "
                      "the old host-state mismatch became a model/host conflict")
    if old_from_attributes and not any("semantic transformation changes" in f for f in new["findings"]):
        causes.append("AA-P8/1.1 C23: empty extraction from_attributes is a visible host-derived copy, not a change")
    if new["comparison_reasons"]:
        causes.append("AA-P8-HOST/1.1: missing comparison is unknown; AA-P8/1.0 returned an invented "
                      "within-arm 'unsupported' here")
    if "model_host_conflict" in new["phase9_mandatory_triggers"]:
        causes.append("AA-P9/1.1: material model/host conflict is a mandatory review trigger")
    elif new["model_host_conflicts"]:
        causes.append("AA-P9/1.1: non-material model/host conflict stays visible (bounded trigger)")
    if not causes and original["phase8_technical"] == new["phase8_technical"]:
        causes.append("unchanged")
    return causes


def main(output: Path) -> None:
    # The label follows the code actually imported, so a run with the original code is never
    # presented as an AA-P8/1.1 analysis.
    new_contract = hasattr(phase8_models, "HOST_RULE_VERSION")
    from agent_arena.phase9_models import CONTRACT_VERSION as P9_VERSION
    p8_version = getattr(phase8_models, "Phase8Assessment").model_fields["contract_version"].default
    contract = (f"{p8_version} + {P9_VERSION}" if new_contract
                else "original AA-P8/1.0 + AA-P9/1.0 code (harness check, reproduces provenance class 1)")
    provenance = (f"2 = new analysis of unchanged original responses under {contract}; class 1 "
                  "originals stay in the archived bundles and summaries" if new_contract else
                  "1 (reproduction) = the original AA-P8/1.0 + AA-P9/1.0 code re-run on the unchanged responses; "
                  "checks that this script reproduces the archived class-1 results")
    note = ("Routes are offline routing results under the new contract, not executed reviews and not live results."
            if new_contract else
            "Harness check only: the key 'reanalysis' holds the re-run of the original code; no new contract applied.")
    results, counts = [], {"captures": 0, "phase8_completed_original": 0, "phase8_completed_reanalysis": 0,
                           "with_model_host_conflict": 0, "route_review_recommended_reanalysis": 0,
                           "route_auto_resolvable_reanalysis": 0, "route_human_review_required_reanalysis": 0}
    for run, directory, summary in RUNS:
        originals = original_rows(summary)
        ledger = json.loads((directory / "ledger.json").read_text())
        for attempt in ledger["attempts"]:
            capture_path = directory / "captures" / f"{attempt['attempt_id']}.json"
            raw = capture_path.read_bytes()
            capture = json.loads(raw)
            profile = capture["profile_id"]
            case = capture["task_id"].rsplit("-", 2)[-2] + "-" + capture["task_id"].rsplit("-", 1)[-1]
            task = load_task(BASE / "live_run/tasks" / f"{case}.json")
            final_text = capture["interpretation"]["final_text"]
            parsed, diagnostics = parse_structured_output(final_text, "stop")
            assessment = assess_forensic_payload(parsed.forensic_record if parsed else None,
                                                 original_input=task.prompt, context=task.context,
                                                 parse_complete=diagnostics.ok)
            result = AgentResult(provider="anthropic-live-reanalysis", model=capture["call"]["request_body"]["model"],
                                 raw_output=final_text, parsed=parsed, parse_ok=diagnostics.ok, finish_reason="stop")
            route = assess_case(task, [position_from_result(task, result, f"reanalysis:{attempt['attempt_id']}")])
            findings = assessment.get("transformation_findings", [])
            new = {
                "phase8_technical": assessment["technical_status"],
                "composite_effective": assessment.get("composite_state"),
                "model_composite": assessment.get("model_composite_state"),
                "host_composite": assessment.get("host_composite_state"),
                "propositions": [{k: p.get(k) for k in ("proposition_id", "reported_verdict", "host_state",
                                                        "derived_state", "model_host_conflict")}
                                 for p in assessment.get("propositions", [])],
                "model_host_conflicts": assessment.get("model_host_conflicts", []),
                "host_derived_copies": assessment.get("host_derived_copies", []),
                "findings": findings,
                "other_reasons": [r for r in assessment.get("reasons", []) if r not in findings
                                  and not r.startswith("Ledger, evidence") and "open model/host conflict" not in r][:6],
                "comparison_reasons": sorted({r for p in assessment.get("propositions", [])
                                              for r in p.get("host_reasons", [])
                                              if "no inference about the study design" in r}),
                "phase9_route": route.route, "phase9_mandatory": route.mandatory,
                "phase9_mandatory_triggers": sorted({t.code for t in route.triggers if t.mandatory}),
            }
            original = originals[(profile, case)]
            results.append({"run": run, "attempt_id": attempt["attempt_id"], "profile": profile, "case": case,
                            "capture_sha256": hashlib.sha256(raw).hexdigest(),
                            "capture_verified_against_ledger": hashlib.sha256(raw).hexdigest() == attempt["capture_sha256"],
                            "original": original, "reanalysis": new, "difference_causes": classify(original, new)})
            counts["captures"] += 1
            counts["phase8_completed_original"] += original["phase8_technical"] == "completed"
            counts["phase8_completed_reanalysis"] += new["phase8_technical"] == "completed"
            counts["with_model_host_conflict"] += bool(new["model_host_conflicts"])
            key = f"route_{route.route.lower()}_reanalysis"
            counts[key] = counts.get(key, 0) + 1
    output.write_text(json.dumps({
        "schema": "aa-p8-1-1-historical-reanalysis/1.1",
        "contract_under_test": contract,
        "provenance_class": provenance,
        "note": note,
        "counts": counts, "captures": results}, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(counts, indent=1))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
