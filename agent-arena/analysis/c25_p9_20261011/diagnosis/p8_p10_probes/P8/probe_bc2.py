import json, sys
from pathlib import Path
DIAG = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new"
OUT = Path(__file__).resolve().parent / "out_probeC2"
sys.path.insert(0, DIAG + "/src"); sys.path.insert(0, DIAG)
import agent_arena; assert agent_arena.__file__.startswith(DIAG)
src = open(Path(__file__).resolve().parent / "probe_bc.py").read()
# reuse builders by exec up to section C' (stop before running audits again)
ns = {"__file__": str(Path(__file__).resolve().parent / "probe_bc.py")}
exec(compile(src.split("# ---- C:")[0], "probe_bc_B", "exec"), ns)  # B again (prints)
from agent_arena.output_contract import parse_structured_output
from agent_arena.phase9_review import assess_case, position_from_result
from agent_arena.phase9_runtime import OfflineReviewProvider, build_challenge
from agent_arena.phase10_bundle import release_candidate, run_audit
from agent_arena.schemas import AgentResult, Task
# B with conflict: model says unsupported for p1 and all asserted states
rec = ns["rec"]; claim = ns["claim"]; context = ns["context"]
rec["phase8"]["propositions"][0]["reported_verdict"] = "unsupported"
for t in rec["phase8"]["transformations"]:
    if t.get("asserted_state") is not None: t["asserted_state"] = "unsupported"
task = Task(id="probe-b2", title="B2", domain="study_forensics", difficulty="medium", task_type="study_forensics", prompt=claim, context=context)
raw = json.dumps({"final_answer": "overclaim", "confidence": 0.5, "forensic_record": rec})
parsed, d = parse_structured_output(raw)
pos = position_from_result(task, AgentResult(provider="recorded-offline", model="m", raw_output=raw, parsed=parsed, parse_ok=d.ok), "run1")
packet = build_challenge(task, pos)
for c in packet.get("model_host_conflicts", []):
    print("B2 packet host_position:", c["scope"], json.dumps(c["host_position"])[:400])
print("B2 gold/expected keys in packet:", [k for k in json.dumps(packet).split('"') if k in {"expected","gold","rubric","curator","expected_label","final_answer"}])
