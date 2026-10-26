import sys, json, collections
B="__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
sys.path[:0]=[B+"/src", B]
import agent_arena; assert agent_arena.__file__.startswith(B), agent_arena.__file__
from tests.phase8_case_factory import raw_record
from agent_arena.providers import BaseProvider
from agent_arena.providers.response import ModelResponse
from agent_arena.runner import run_agent
from agent_arena.schemas import Task, AgentResult
from agent_arena.phase8_pipeline import assess_agent_result
from agent_arena.output_contract import parse_structured_output
from agent_arena.evaluator import evaluate_result

class Fake(BaseProvider):
    name="offline"; model="fake"
    def __init__(s, text, fr): s.text=text; s.fr=fr; s.seen=[]
    def send_prompt(s, t, sp): return s.text
    def generate(s, task, sp):
        s.seen.append((task.prompt, task.context, sp))
        return ModelResponse(text=s.text, provider="offline", model="fake", finish_reason=s.fr)

claim, context, payload = raw_record()
task = Task(id="probe", title="t", domain="study_forensics", difficulty="medium",
            task_type="study_forensics", prompt=claim, context=context)
# forensic_record first, optional list fields last
resp = {"forensic_record": payload, "final_answer": "solid", "confidence": 0.9,
        "steps": ["s1"], "assumptions": ["a1"], "alternative_hypotheses": [], "uncertainties": [],
        "key_claims": ["k1"], "self_check": ["check one", "check two", "check three"]}
full = json.dumps(resp)

# 1. end-to-end baseline
p = Fake(full, "stop"); r = run_agent(p, task)
print("BASELINE parse_ok", r.parse_ok, "phase8", r.phase8.get("technical_status"), r.phase8.get("composite_state"),
      "phase9", r.phase9.get("technical_status"), r.phase9.get("route"))
print("  claim/context reach provider unchanged:", p.seen[0][0]==claim and p.seen[0][1]==context)
ev = evaluate_result(task, r); print("  evaluate phase8:", ev.agent_result.phase8.get("technical_status"))

# 2. sweep truncation points across the tail (after forensic_record ends)
fr_end = len(json.dumps({"forensic_record": payload})) - 1
outcomes = collections.Counter(); bad=[]
for fr in ("stop", None, "unknown", "length"):
    for cut in range(fr_end, len(full)-1):
        text = full[:cut]
        r = run_agent(Fake(text, fr), task)
        _, d = parse_structured_output(text, fr)
        key = (fr, r.parse_ok, d.strategy, r.phase8.get("technical_status"))
        outcomes[key]+=1
        if r.phase8.get("technical_status")=="completed": bad.append((fr,cut))
for k,v in sorted(outcomes.items(), key=str): print("SWEEP", k, v)
print("SWEEP completed-from-truncated count:", len(bad), bad[:5])

# 3. full-length sweep (cut anywhere) with finish_reason=None: any 'completed'?
bad2=0; rep=0
for cut in range(1, len(full)-1, 7):
    r = run_agent(Fake(full[:cut], None), task)
    _, d = parse_structured_output(full[:cut], None); rep += d.repaired
    bad2 += r.phase8.get("technical_status")=="completed"
print("WIDE sweep repaired:", rep, "completed:", bad2)

# 4. two JSON objects: draft (wrong / incomplete) then final; and two fenced blocks
draft = dict(resp, final_answer="overclaim")
two = json.dumps(draft) + "\n\nCorrection, final answer:\n" + json.dumps(resp)
r = run_agent(Fake(two, "stop"), task); _, d = parse_structured_output(two, "stop")
print("TWO_OBJECTS strategy", d.strategy, "ok", d.ok, "trunc", d.truncation_suspected,
      "label", r.phase8.get("original_model_label"), "phase8", r.phase8.get("technical_status"))
twof = "```json\n"+json.dumps(draft)+"\n```\nRevised:\n```json\n"+json.dumps(resp)+"\n```"
r = run_agent(Fake(twof, "stop"), task); _, d = parse_structured_output(twof, "stop")
print("TWO_FENCES strategy", d.strategy, "ok", d.ok, "label", r.phase8.get("original_model_label"),
      "phase8", r.phase8.get("technical_status"))

# 5. loaded/manual result without raw_output but with parsed + finish_reason=length
parsed, _ = parse_structured_output(full)
lr = AgentResult(provider="x", raw_output="", parsed=parsed, parse_ok=True, finish_reason="length")
a = assess_agent_result(task, lr)
print("NO_RAW finish=length phase8:", a.get("technical_status"), a.get("composite_state"), a.get("raw_response_sha256")[:12])
# same with parsed from a repaired truncation
tparsed, td = parse_structured_output(full[:len(full)-20], None)
lr2 = AgentResult(provider="x", raw_output="", parsed=tparsed, parse_ok=td.ok, finish_reason=None)
print("NO_RAW repaired-parsed phase8:", td.repaired, assess_agent_result(task, lr2).get("technical_status"))
