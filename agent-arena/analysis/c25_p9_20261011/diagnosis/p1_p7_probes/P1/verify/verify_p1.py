"""Independent verifier probe for the P1 row (read-only over the checkout; offline fakes only)."""
import sys, json, copy, collections
B = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
sys.path[:0] = [B + "/src", B]
import agent_arena
assert agent_arena.__file__.startswith(B), agent_arena.__file__
from pathlib import Path
from tests.phase8_case_factory import raw_record
from agent_arena.providers import BaseProvider
from agent_arena.providers.response import ModelResponse
from agent_arena.runner import run_agent
from agent_arena.run_library import run_single
from agent_arena.phase7a_execution import is_classification_valid
from agent_arena.schemas import Task, AgentResult
from agent_arena.output_contract import parse_structured_output
from agent_arena.phase8_pipeline import assess_agent_result, refresh_run_phase8
from agent_arena.evaluator import evaluate_run
from agent_arena.phase10_pipeline import reconstruct


class Fake(BaseProvider):
    name = "offline"; model = "fake"

    def __init__(self, text, fr):
        self.text, self.fr = text, fr

    def send_prompt(self, t, sp):
        return self.text

    def generate(self, task, sp):
        return ModelResponse(text=self.text, provider="offline", model="fake", finish_reason=self.fr)


claim, context, payload = raw_record()
task = Task(id="vprobe", title="t", domain="study_forensics", difficulty="medium",
            task_type="study_forensics", prompt=claim, context=context, gold_label="solid")

final = {"final_answer": "solid", "confidence": 0.9, "steps": ["s"], "assumptions": [],
         "alternative_hypotheses": [], "uncertainties": [], "key_claims": ["k"],
         "self_check": ["c"], "forensic_record": payload}
# Draft: different label AND a different evidence reading (contradict instead of support)
dpay = copy.deepcopy(payload)
for p in dpay["phase8"]["propositions"]:
    for b in p["evidence_bindings"]:
        b["observation"] = "contradict"
    p["reported_verdict"] = "contradicted"
draft = dict(final, final_answer="overclaim", confidence=0.6, forensic_record=dpay)


def full_path(name, text, fr="stop"):
    r = run_agent(Fake(text, fr), task)
    _, d = parse_structured_output(text, fr)
    row = run_single(Fake(text, fr), Path("x.yaml"), task, 0, "verify")
    rec = evaluate_run(task, "verify-run", [r])
    _, sel, assessment, forensic = reconstruct(rec)
    fr_comp = None
    if forensic is not None:
        fr_comp = forensic.model_dump(mode="json")["phase8"]["propositions"][0]["evidence_bindings"][0]["observation"]
    print(f"{name}: strategy={d.strategy} ok={d.ok} trunc={d.truncation_suspected} "
          f"label={r.parsed.final_answer if r.parsed else None} p8={r.phase8.get('technical_status')}/"
          f"{r.phase8.get('composite_state')} p9={r.phase9.get('technical_status')}/{r.phase9.get('route')} "
          f"row_label={row['label']} class_valid={is_classification_valid(row)} "
          f"p10_forensic_binding={fr_comp}")


j = json.dumps
print("== F1 counter-cases (draft first, corrected final second) ==")
full_path("SINGLE_FINAL", "```json\n" + j(final) + "\n```")
full_path("TWO_FENCES", "```json\n" + j(draft) + "\n```\n\n**CORRECTED RESPONSE:**\n\n```json\n" + j(final) + "\n```")
full_path("TWO_RAW", j(draft) + "\n\nCorrection after self-check:\n" + j(final))
print("== precedence: bare fence first, ```json second ==")
full_path("BARE_THEN_JSON", "```\n" + j(final) + "\n```\nAlt:\n```json\n" + j(draft) + "\n```")
print("== first fenced block is not an analysis ==")
full_path("META_THEN_ANALYSIS", "Input summary:\n```json\n" + j({"claim": claim}) + "\n```\n\n```json\n" + j(final) + "\n```")
print("== hidden truncation: complete draft, truncated second object ==")
tf = "```json\n" + j(draft) + "\n```\n\n**CORRECTED RESPONSE:**\n\n```json\n" + j(final)[: len(j(final)) // 2]
for fr in (None, "unknown", "stop", "length"):
    full_path(f"TRUNC_SECOND fr={fr}", tf, fr)
tr = j(draft) + "\n\nCorrection:\n" + j(final)[: len(j(final)) // 2]
full_path("TRUNC_SECOND_RAW fr=None", tr, None)
print("== duplicate top-level key (inline self-correction) ==")
dup = j(final)[:-1] + ', "final_answer": "overclaim"}'
_, d = parse_structured_output(dup)
pr, _ = parse_structured_output(dup)
print("DUP_KEY:", d.strategy, d.ok, pr.final_answer, "unexpected/missing:", d.unexpected_fields, d.missing_fields)

print("== F2: empty raw_output with parsed + finish_reason=length ==")
parsed, _ = parse_structured_output(j(final))
lr = AgentResult(provider="x", raw_output="", parsed=parsed, parse_ok=True, finish_reason="length")
a = assess_agent_result(task, lr)
print("F2 direct:", a.get("technical_status"), a.get("composite_state"), a["raw_response_sha256"][:12])
rec = evaluate_run(task, "f2", [AgentResult(provider="x", raw_output=j(final), parsed=parsed, parse_ok=True,
                                             finish_reason="length")])
print("F2 baseline with raw (length):", rec.results[0].agent_result.phase8.get("technical_status"))
stripped = rec.model_copy(deep=True)
stripped.results[0].agent_result.raw_output = ""
ref = refresh_run_phase8(stripped)
print("F2 via refresh_run_phase8 after stripping raw:", ref.results[0].agent_result.phase8.get("technical_status"))
# JSON round trip without raw_output key (loaded legacy-style record)
dumped = json.loads(rec.model_dump_json())
dumped["results"][0]["agent_result"].pop("raw_output")
from agent_arena.schemas import RunRecord
loaded = RunRecord.model_validate(dumped)
print("F2 loaded w/o raw_output key -> refresh:", refresh_run_phase8(loaded).results[0].agent_result.phase8.get("technical_status"))
_, _, a10, f10 = reconstruct(loaded)
print("F2 P10 reconstruct on that record: phase8", a10.get("technical_status"), "forensic", f10 is not None)
