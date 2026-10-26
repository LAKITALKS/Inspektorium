"""Verifier: r2 says any structural violation makes the analysis technically incomplete; does a C28
causal_claim violation do so? Offline only."""
import json
import sys
from pathlib import Path

V = Path("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_p8_p10/P8/verifier")
src = (V / "v_f1.py").read_text().split("CASES = [")[0]
ns = {"__file__": str(V / "v_f1.py"), "__name__": "v_f1_lib"}
exec(compile(src, "v_f1_lib", "exec"), ns)
build, TASK = ns["build"], ns["TASK"]
from agent_arena.phase8_pipeline import assess_forensic_payload  # noqa: E402

data = build("cvc", "supported", True)
rec = data["forensic_record"]
rec["phase8_taxonomy"]["causal_claim"] = False  # violates C28: listed p1 has relation causal
a = assess_forensic_payload(rec, original_input=TASK.prompt, context=TASK.context, original_label="solid")
print("P8:", a["technical_status"], "| taxonomy:", a["taxonomy"]["technical_status"], a["taxonomy"]["reasons"],
      "| label:", a["derived_label"])
