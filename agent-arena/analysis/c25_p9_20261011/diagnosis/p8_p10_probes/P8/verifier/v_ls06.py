"""Verifier: for the real LS-06 repair_r1 captures, does a model/host conflict sit on a taxonomy-listed or
trigger proposition (relevant to the scope of the F1 fix option 1)? Read-only, offline."""
import json
import os
import sys
from pathlib import Path

DIAG = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new"
sys.path.insert(0, DIAG + "/src")
import agent_arena  # noqa: E402
assert agent_arena.__file__.startswith(DIAG), agent_arena.__file__
from agent_arena.output_contract import parse_structured_output  # noqa: E402
from agent_arena.phase8_pipeline import assess_forensic_payload  # noqa: E402
from agent_arena.task_loader import load_task  # noqa: E402

os.chdir(DIAG)
BASE = Path("analysis/live_smoke_20261011")
directory = BASE / "repair_r1"
ledger = json.loads((directory / "ledger.json").read_text())
for attempt in ledger["attempts"]:
    capture = json.loads((directory / "captures" / f"{attempt['attempt_id']}.json").read_text())
    case = capture["task_id"].rsplit("-", 2)[-2] + "-" + capture["task_id"].rsplit("-", 1)[-1]
    if case != "LS-06":
        continue
    task = load_task(BASE / "live_run/tasks" / f"{case}.json")
    parsed, diag = parse_structured_output(capture["interpretation"]["final_text"], "stop")
    payload = parsed.forensic_record
    a = assess_forensic_payload(payload, original_input=task.prompt, context=task.context, parse_complete=diag.ok)
    tax = payload.get("phase8_taxonomy") or {}
    print(capture["profile_id"], "label", a["derived_label"], "composite", a["composite_state"],
          "model/host", a["model_composite_state"], a["host_composite_state"])
    print("  taxonomy listed", tax.get("proposition_ids"), "trigger", tax.get("trigger_proposition_id"))
    for p in a["propositions"]:
        print("   ", p["proposition_id"], "req", p["required"], "model", p["reported_verdict"], "host", p["host_state"],
              "derived", p["derived_state"], "conflict", p["model_host_conflict"])
