"""F1 with a valid draft whose Phase-8 composite differs from the corrected final; hidden-truncation case."""
import sys, json, copy, runpy, io, contextlib
B = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
sys.path[:0] = [B + "/src", B]
import agent_arena; assert agent_arena.__file__.startswith(B)
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    g = runpy.run_path("verify_p1.py")   # reuse Fake/task/final/full_path (its own prints suppressed)
full_path, final, payload = g["full_path"], g["final"], g["payload"]
d = copy.deepcopy(payload)
for p in d["phase8"]["propositions"]:
    for b in p["evidence_bindings"]: b["observation"] = "contradiction"
    p["reported_verdict"] = "contradicted"
for t in d["phase8"]["transformations"]:
    if t["stage"] == "summary": t["asserted_state"] = "contradicted"
for e in d["evidence"]: e["role"] = "contradictory"
for f in d["findings"]:
    f["contrary_evidence_ids"] = f.pop("supporting_evidence_ids"); f["supporting_evidence_ids"] = []
draft = dict(final, final_answer="overclaim", confidence=0.6, forensic_record=d)
j = json.dumps
full_path("DRAFT_ONLY", "```json\n" + j(draft) + "\n```")
full_path("TWO_FENCES(valid draft)", "```json\n" + j(draft) + "\n```\n\n**CORRECTED RESPONSE:**\n\n```json\n" + j(final) + "\n```")
full_path("TWO_RAW(valid draft)", j(draft) + "\n\nCorrection after self-check:\n" + j(final))
tf = "```json\n" + j(draft) + "\n```\n\n**CORRECTED RESPONSE:**\n\n```json\n" + j(final)[: len(j(final)) // 2]
for fr in (None, "unknown", "stop", "length"):
    full_path(f"TRUNC_SECOND(valid draft) fr={fr}", tf, fr)
