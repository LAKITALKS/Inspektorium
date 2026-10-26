"""Verifier: end-to-end AA-P10-LIVE path on tracked library case004 with the project's own
httpx.MockTransport double (no network; real HTTP transport is patched to raise)."""
import sys, json, tempfile
from pathlib import Path
B, OUT = sys.argv[1], sys.argv[2]
sys.path.insert(0, B + "/src"); sys.path.insert(0, B)
import httpx
def _no_net(*a, **k):
    raise AssertionError("real network attempted")
httpx.HTTPTransport.handle_request = _no_net
from tests.test_phase10_live import _authorize, Transport, message, _recording, HAIKU, P8
from agent_arena import phase10_live as live
from agent_arena.phase10_bundle import run_audit
from agent_arena.phase10_pipeline import preflight
from agent_arena.task_loader import load_task
from agent_arena.packet_integrity import check_task, check_contamination, ModelFacingPacket
from agent_arena.providers.anthropic_live import build_user_message
from agent_arena.runner import resolve_study_forensics_prompt

task = load_task(B + "/tasks/study_forensics/case004_multivitamin.yaml")
print("task", task.id, "gold", task.gold_label, "| P10 preflight errors:", preflight(task))
print("P6 packet_integrity(check_task) ok:", check_task(task, case_file="case004_multivitamin.yaml").ok)
with tempfile.TemporaryDirectory(dir=OUT) as d:
    d = Path(d)
    auth = _authorize(d / "auth", [task])
    tr = Transport(message(_recording("positive")))
    with live.LiveSession(auth, mode="live", transport=tr.mock(), api_key="dummy-not-a-credential") as s:
        prov = live.LiveAuditProvider(s, HAIKU, task.id, "primary", P8)
        res = run_audit(task, prov, output_root=d / "out", review_state=auth / "phase9-state")
    print("run_audit status:", res.status, "| requests captured by double:", len(tr.requests))
    for i, r in enumerate(tr.requests):
        content = r["body"]["messages"][0]["content"]
        print(f" request[{i}] url={r['url']} contains 'should recognise this as solid':",
              "should recognise this as solid" in content)
        pkt = ModelFacingPacket(case_id=task.id, task_type="study_forensics", system=r["body"]["system"], user=content)
        c = check_contamination(task, pkt, case_file="case004_multivitamin.yaml")
        print(f" P6 check_contamination on the ACTUALLY SENT request[{i}]: passed={c.passed} findings={[f.code for f in c.findings]}")

# Counterfactual: if packet_integrity were updated 'in lockstep' to the live builder only,
# which tracked cases would the EXISTING contamination rules flag?
flag = []
for f in sorted(Path(B, "tasks/study_forensics").glob("*.yaml")):
    t = load_task(str(f))
    pkt = ModelFacingPacket(case_id=t.id, task_type="study_forensics",
                            system=resolve_study_forensics_prompt(P8), user=build_user_message(t))
    c = check_contamination(t, pkt, case_file=f.name)
    if not c.passed:
        flag.append((f.name, t.gold_label, sorted({x.code for x in c.findings})))
print("lockstep-only counterfactual: cases flagged by existing rules:", len(flag))
for x in flag: print("  ", x)
