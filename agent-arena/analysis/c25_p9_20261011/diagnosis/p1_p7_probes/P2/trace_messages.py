"""P2 diagnosis: what exactly reaches each provider transport for a study-forensics task.
No network: SDK modules are replaced by in-process fakes; live path uses httpx.MockTransport."""
import sys, json, types, tempfile, os
from pathlib import Path
BASE = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
sys.path.insert(0, BASE + "/src")
os.environ.pop("ANTHROPIC_API_KEY", None); os.environ.pop("OPENAI_API_KEY", None)
import agent_arena
assert agent_arena.__file__.startswith(BASE), agent_arena.__file__
from agent_arena.schemas import Task, RubricItem, ExpectedFinding, GoldEvidenceSpan

CAN = {k: f"CANARY_{k.upper()}_7f3a" for k in [
    "expected_answer", "reference_solution", "gold_label", "gold_summary", "gold_justification",
    "gold_alternative_reading", "curator_notes", "evaluator_notes", "key_insight", "common_error",
    "rubric", "expected_finding", "gold_span", "fragile", "shortcut", "mechanism_term"]}
PROMPT = "PROMPT_MARK_1: Researchers report that drug X reduced mortality."
CONTEXT = "CONTEXT_MARK_2: The source was an observational cohort of 40 people; no randomisation."

def make_task():
    fields = dict(
        id="p2-diag-task", title="P2 diag", domain="study_forensics", difficulty="medium",
        task_type="study_forensics", prompt=PROMPT, context=CONTEXT,
        expected_answer=CAN["expected_answer"], reference_solution=CAN["reference_solution"],
        gold_label=CAN["gold_label"], gold_summary=CAN["gold_summary"],
        gold_justification=CAN["gold_justification"], gold_alternative_reading=CAN["gold_alternative_reading"],
        curator_notes=CAN["curator_notes"], evaluator_notes=CAN["evaluator_notes"],
        key_insights=[CAN["key_insight"]], common_errors=[CAN["common_error"]],
        fragile_points=[CAN["fragile"]], likely_shortcuts=[CAN["shortcut"]],
        expected_mechanism_terms=[CAN["mechanism_term"]],
    )
    t = Task(**fields)
    # rubric / expected findings / spans: fill via model_validate with minimal shapes
    for name, model, payload in [("rubric", RubricItem, None), ("expected_findings", ExpectedFinding, None),
                                 ("gold_evidence_spans", GoldEvidenceSpan, None)]:
        req = {k for k, f in model.model_fields.items() if f.is_required()}
        data = {}
        for k in req:
            ann = model.model_fields[k].annotation
            data[k] = 1.0 if ann in (float, int) else CAN["rubric" if name == "rubric" else ("expected_finding" if name == "expected_findings" else "gold_span")]
        try:
            setattr(t, name, [model(**data)])
        except Exception as e:
            print("could not set", name, e)
    return t

def scan(label, blob):
    s = blob if isinstance(blob, str) else json.dumps(blob, ensure_ascii=False)
    leaked = sorted(k for k, v in CAN.items() if v in s)
    print(f"[{label}] prompt_present={PROMPT in s} context_present={CONTEXT in s} leaked_gold_fields={leaked}")
    return leaked

task = make_task()
print("task gold fields set:", task.gold_label, len(task.rubric), len(task.expected_findings), len(task.gold_evidence_spans))

# ---------- legacy Anthropic (4.5 adapter) through run_agent (default prompt version) ----------
captured = {}
class _Msg:  # minimal message object
    def __init__(self):
        self.content = [types.SimpleNamespace(text='{"final_answer":"overclaim","confidence":0.5}')]
        self.stop_reason = "end_turn"; self.usage = types.SimpleNamespace(input_tokens=1, output_tokens=1)
class _Messages:
    def create(self, **kw):
        captured.setdefault("anthropic", []).append(kw); return _Msg()
class _Anthropic:
    def __init__(self, **kw): self.kw = kw; self.messages = _Messages()
sys.modules["anthropic"] = types.SimpleNamespace(Anthropic=_Anthropic)
from agent_arena.providers.anthropic import AnthropicProvider
from agent_arena.runner import run_agent, resolve_study_forensics_prompt
r = run_agent(AnthropicProvider(model="claude-haiku-4-5-20251001"), task)
kw = captured["anthropic"][0]
print("legacy anthropic kwargs keys:", sorted(kw))
print("legacy anthropic user content == task.prompt:", kw["messages"] == [{"role": "user", "content": task.prompt}])
scan("legacy-anthropic user", kw["messages"]); scan("legacy-anthropic system", kw["system"])
sp = kw["system"]
print("system prompt (default) contains 'context for task.context':", "context for task.context" in sp,
      "| == v3-phase8:", sp == resolve_study_forensics_prompt("study_forensics_prompt/v3-phase8"))
print("AgentResult has any record of the sent user message:", any(k for k in r.model_dump() if "user_message" in k))
print("phase8 status:", (r.phase8 or {}).get("technical_status"), (r.phase8 or {}).get("status"))

# ---------- OpenAI ----------
class _Comp:
    def create(self, **kw):
        captured.setdefault("openai", []).append(kw)
        ch = types.SimpleNamespace(message=types.SimpleNamespace(content="{}"), finish_reason="stop")
        return types.SimpleNamespace(choices=[ch], usage=None)
class _OpenAI:
    def __init__(self, **kw): self.chat = types.SimpleNamespace(completions=_Comp())
sys.modules["openai"] = types.SimpleNamespace(OpenAI=_OpenAI)
from agent_arena.providers.openai import OpenAIProvider
OpenAIProvider().generate(task, "SYS")
scan("openai messages", captured["openai"][0]["messages"])

# ---------- Ollama ----------
import urllib.request
class _Resp:
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def read(self): return json.dumps({"message": {"content": "{}"}, "done_reason": "stop"}).encode()
def fake_urlopen(req, timeout=None):
    captured.setdefault("ollama", []).append(json.loads(req.data)); return _Resp()
urllib.request.urlopen = fake_urlopen
from agent_arena.providers.ollama import OllamaProvider
OllamaProvider().generate(task, "SYS")
scan("ollama payload", captured["ollama"][0]["messages"])

# ---------- judge ----------
captured["anthropic"].clear()
from agent_arena.judge import run_judge
from agent_arena.schemas import AgentResponse
run_judge(task, AgentResponse(final_answer="overclaim"), provider_name="anthropic", model="judge-model")
jk = captured["anthropic"][0]
scan("judge user", jk["messages"]); 

# ---------- live path: build_user_message + full run_audit with MockTransport ----------
import httpx
from agent_arena.providers.anthropic_live import build_user_message, PROFILES
um = build_user_message(task)
scan("live build_user_message", um)
sys.path.insert(0, BASE + "/tests")
import test_phase10_live as T
from agent_arena import phase10_live as live
from agent_arena.phase10_bundle import run_audit
ex = T._task("positive")
# same example task, but with all gold/curator fields filled with canaries
gtask = ex.model_copy(update={k: getattr(task, k) for k in [
    "expected_answer", "reference_solution", "gold_label", "gold_summary", "gold_justification",
    "gold_alternative_reading", "curator_notes", "evaluator_notes", "key_insights", "common_errors",
    "fragile_points", "likely_shortcuts", "expected_mechanism_terms", "rubric", "expected_findings",
    "gold_evidence_spans"]})
tmp = Path(tempfile.mkdtemp(dir=str(Path(__file__).parent)))
d = T._authorize(tmp / "auth", [gtask])
tr = T.Transport(T.message(T._recording("positive")), T.message(T._recording("positive")), T.message(T._recording("positive")))
with T._session(d, tr) as session:
    prov = live.LiveAuditProvider(session, T.HAIKU, gtask.id, "primary", T.P8)
    res = run_audit(gtask, prov, output_root=tmp / "out", review_state=d / "phase9-state")
print("live run status:", res.status, "| requests sent to mock transport:", len(tr.requests))
for i, rq in enumerate(tr.requests):
    print(" request", i, "url", rq["url"], "keys", sorted(rq["body"]))
    scan(f"live request {i} user", rq["body"]["messages"]); scan(f"live request {i} system", rq["body"]["system"])
print("live user content == build_user_message:", tr.requests[0]["body"]["messages"][0]["content"] == build_user_message(gtask))
