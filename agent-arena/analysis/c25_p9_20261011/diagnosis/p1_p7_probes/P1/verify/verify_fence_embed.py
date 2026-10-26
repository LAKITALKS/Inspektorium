"""Reproduce the parse diagnostics of tests/test_phase10_render.py hostile fenced case (no files written)."""
import sys, json
B = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
sys.path[:0] = [B + "/src", B]
import agent_arena; assert agent_arena.__file__.startswith(B)
from tests.test_phase10_bundle import recorded
from agent_arena.output_contract import parse_structured_output
for fenced in (False, True):
    task, raw = recorded()
    hostile = "Café β 🧪 <img src=x onerror=alert(1)> [RELEASED](javascript:alert(1)) & O'Brien\n```\n## false status\n" + "W" * 1400 + " END_LONG_VALUE."
    if not fenced:
        hostile = hostile.replace("```", "quoted boundary")
    payload = json.loads(raw.replace("endpoint Delta", "REPLACE_ENDPOINT"))
    def replace(v):
        if isinstance(v, str): return v.replace("REPLACE_ENDPOINT", hostile)
        if isinstance(v, list): return [replace(i) for i in v]
        if isinstance(v, dict): return {k: replace(i) for k, i in v.items()}
        return v
    text = json.dumps(replace(payload))
    p, d = parse_structured_output(text)
    print("fenced" if fenced else "plain", "strategy", d.strategy, "ok", d.ok, "repaired", d.repaired,
          "trunc", d.truncation_suspected, "error", d.error, "valid_json_input", isinstance(json.loads(text), dict),
          "final_answer", (p.final_answer if p else None))
# Minimal: a complete, valid JSON analysis whose string value contains ``` once vs twice
base = {"final_answer": "solid", "steps": ["quote: ```x``` end"], "confidence": 0.9}
for name, obj in (("two_ticks_in_string", base), ("one_tick", dict(base, steps=["quote ``` end"]))):
    t = json.dumps(obj); p, d = parse_structured_output(t, "stop")
    print(name, d.strategy, d.ok, d.truncation_suspected, d.error, p.final_answer if p else None)
