"""Verifier for P8-F5: render_phase8 wording when only a Phase-7 gate failed. Offline only."""
import sys

DIAG = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new"
sys.path.insert(0, DIAG + "/src")
sys.path.insert(0, DIAG)
import agent_arena  # noqa: E402
assert agent_arena.__file__.startswith(DIAG), agent_arena.__file__
from agent_arena.phase8_pipeline import assess_forensic_payload, render_phase8  # noqa: E402
from tests.phase8_case_factory import raw_record  # noqa: E402

claim, context, rec = raw_record()
rec["client_findings"][0]["client_strength"] = "limited_support"  # exceeds allowed not_assessed
a = assess_forensic_payload(rec, original_input=claim, context=context, original_label="solid")
print("technical:", a["technical_status"], "| composite:", a["composite_state"], "| assessed:",
      a.get("assessed_composite_state"), "| transformation_findings:", a.get("transformation_findings"))
print("P7 major:", [(c["name"], f["code"], f["severity"]) for c in a["phase7_controls"] for f in c.get("findings", [])
                    if f.get("severity") in {"critical", "major"}])
for line in render_phase8(a).split("\n\n"):
    if "Component aggregate" in line or "Phase 7" in line:
        print("render:", line)
