"""Compare pre-Phase-1 inline parser (git show e962e85^) with output_contract on multi-object outputs."""
import sys, json
B = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
sys.path[:0] = [B + "/src"]
import agent_arena; assert agent_arena.__file__.startswith(B)
from agent_arena.schemas import AgentResponse
from agent_arena.output_contract import parse_structured_output
src = open("old_parser_src.txt").read()
src = src[: src.index("\n\n\n")] if "\n\n\n" in src else src
ns = {"json": json, "AgentResponse": AgentResponse}
exec("from __future__ import annotations\n" + src, ns)
old = ns["parse_agent_output"]
draft = {"final_answer": "mechanism_vs_evidence", "confidence": 0.75}
final = {"final_answer": "overclaim", "confidence": 0.85}
j = json.dumps
cases = {
    "TWO_FENCES": "```json\n" + j(draft) + "\n```\n\n**CORRECTED RESPONSE:**\n\n```json\n" + j(final) + "\n```",
    "TWO_RAW": j(draft) + "\n\nCorrection after self-check:\n" + j(final),
    "PROSE_TWO_RAW": "Draft:\n" + j(draft) + "\nCorrected:\n" + j(final),
}
for name, text in cases.items():
    try:
        o, ok = old(text); o = (o.final_answer if o else None, ok)
    except Exception as e:
        o = ("RAISES", type(e).__name__)
    n, d = parse_structured_output(text)
    print(f"{name}: old={o} new=({n.final_answer if n else None}, {d.ok}, {d.strategy})")
