"""Verifier probe for P9-F2 (model adjudication provenance/independence text) on live and offline paths.

Live: throwaway authorization built with tests/test_phase10_live._authorize under scratch,
KNOWN_CLOSED_AUTHORIZATIONS={}, httpx MockTransport, api_key='test-key'. Offline: explicit execute_review.
"""
import json
import shutil
import sys
from pathlib import Path

D = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new"
sys.path[:0] = [D + "/src", D]
OUT = Path("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_p8_p10/P9/verify/f2")
assert str(OUT).startswith("/private/tmp/")
shutil.rmtree(OUT, ignore_errors=True)

from agent_arena import phase10_live as live  # noqa: E402
live.KNOWN_CLOSED_AUTHORIZATIONS = {}
import tests.test_phase10_live as T  # noqa: E402
from agent_arena.phase10_bundle import run_audit, review_candidate, release_candidate  # noqa: E402
from agent_arena.providers.anthropic_live import PROFILES  # noqa: E402

H3 = "claude-haiku-5-5@3"
task, raw = T._conflict_task("aa-verify-f2")
directory = T._authorize(OUT / "auth", [task], profiles=(H3,), ceiling=300_000)
# Reviewer agrees with the host (supported), so a human can select the review position afterwards.
data = json.loads(raw)
from tests.test_phase8_9_conflict import set_model  # noqa: E402
set_model(data["forensic_record"], "supported")
review_raw = json.dumps(data)
transport = T.Transport(T.message(raw, request_id="req_p"), T.message(review_raw, request_id="req_c"))
with T._session(directory, transport) as session:
    prov = live.LiveAuditProvider(session, H3, task.id, "primary", PROFILES[H3].prompt_versions[0])
    res = run_audit(task, prov, output_root=OUT / "out", review_state=directory / "phase9-state")
print("LIVE status", res.status, "requests", len(transport.requests))
p9 = T._record(res.path)["run_record"]["metadata"]["phase9"]
for a in p9["attempts"]:
    print(" attempt", a["kind"], a["status"], "| independence:", (a.get("independence") or "")[:120])
for d in p9["adjudications"]:
    print(" adjudication", d["reviewer_type"], d["origin"], d["outcome"], "| provenance:", d["reviewer_provenance"],
          "| independence:", d["independence"][:90])
rv = next(p for p in p9["positions"] if p["origin"] == "model_review")
print(" review position provider:", rv["provider"], "| current_execution:",
      (rv["agent_result"].get("execution_evidence") or {}).get("current_execution"))
md = (Path(res.path) / "report.md").read_text()
print(" report.md contains 'Built-in offline recording via existing runner/parser':",
      "Built-in offline recording via existing runner/parser" in md,
      "| 'first verdict withheld':", "first verdict withheld" in md)
# Human selection of the review position -> READY_FOR_RELEASE -> RELEASED; text persists in released report
hr = review_candidate(Path(res.path), output_root=OUT / "hr", state_dir=directory / "phase9-state" / H3,
                      selected_position_id=rv["position_id"], reviewer="TEST ONLY", reason="verifier")
print("HUMAN status", hr.status, hr.errors[:1])
if hr.status == "READY_FOR_RELEASE":
    rel = release_candidate(Path(hr.path), output_root=OUT / "rel", reviewer="TEST ONLY", reason="verifier")
    rmd = (Path(rel.path) / "report.md").read_text() if rel.path else ""
    print("RELEASE status", rel.status, "| released report keeps the offline provenance text:",
          "Built-in offline recording via existing runner/parser" in rmd)
