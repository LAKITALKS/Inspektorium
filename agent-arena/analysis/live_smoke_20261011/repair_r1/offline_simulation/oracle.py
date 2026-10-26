"""Critic-only: same as scenarios (C12+C14) but asserted_state set to the host-derived state (oracle)."""
import json, sys
from pathlib import Path
src = Path(__file__).with_name("scenarios.py").read_text().split('run("copy-only')[0]
exec(compile(src, "scenarios.py", "exec"), globals())
from agent_arena.phase8_semantics import evaluate_phase8
from agent_arena.schemas import ForensicRecord
from agent_arena.phase8_models import PropositionLedger
from agent_arena.phase8_semantics import _assess_proposition, aggregate_claim
ok_n = 0
for f in sorted((RUN / "captures").glob("attempt-*.json")):
    cap = json.loads(f.read_bytes()); task = tasks[cap["task_id"]]
    parsed, _ = parse_structured_output(cap["interpretation"]["final_text"], "stop")
    fixed, _ = ns["repair"](parsed.forensic_record, task)
    fixed = sync_transformations(c14(c12(fixed)))
    rec = ForensicRecord.model_validate(fixed)
    ledger = PropositionLedger.model_validate(rec.phase8)
    states = {p.proposition_id: _assess_proposition(p, ledger, rec).derived_state for p in ledger.propositions}
    comp = aggregate_claim(ledger.logic, states)
    for t in fixed["phase8"]["transformations"]:
        if t["asserted_state"] is not None or t["stage"] == "summary":
            t["asserted_state"] = comp if t["asserts_whole_claim"] else states[t["from_proposition_ids"][0]]
    a = assess_forensic_payload(fixed, original_input=task.prompt, context=task.context)
    ok = a["technical_status"] == "completed" and a.get("taxonomy", {}).get("technical_status") == "completed"
    ok_n += ok
    print(f.name, cap["profile_id"][:18], task.id[-5:], "P8", a["technical_status"], "tax", a.get("taxonomy", {}).get("technical_status"),
          "composite", a.get("composite_state"), "label", a.get("derived_label"), "| model", getattr(parsed, "final_answer", None),
          [r[:90] for r in a.get("reasons", []) if not r.startswith("Ledger, evidence")][:2], a.get("taxonomy", {}).get("reasons"))
print("oracle strict pass", ok_n, "/12")
