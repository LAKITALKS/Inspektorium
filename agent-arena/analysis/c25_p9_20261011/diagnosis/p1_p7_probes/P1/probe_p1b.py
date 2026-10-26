import sys, json
from pathlib import Path
B="__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
sys.path[:0]=[B+"/src", B]
from tests.phase8_case_factory import raw_record
from agent_arena.providers import BaseProvider
from agent_arena.providers.response import ModelResponse
from agent_arena.run_library import run_single
from agent_arena.phase7a_execution import is_classification_valid
from agent_arena.schemas import Task
class Fake(BaseProvider):
    name="offline"; model="fake"
    def __init__(s, text, fr): s.text=text; s.fr=fr
    def send_prompt(s,t,sp): return s.text
    def generate(s, task, sp): return ModelResponse(text=s.text, provider="offline", model="fake", finish_reason=s.fr)
claim, context, payload = raw_record()
task = Task(id="probe", title="t", domain="study_forensics", difficulty="medium", task_type="study_forensics",
            prompt=claim, context=context, gold_label="solid")
resp = {"forensic_record": payload, "final_answer": "solid", "confidence": 0.9, "steps": ["s"],
        "self_check": ["check one", "check two"]}
full = json.dumps(resp); trunc = full[:-12]
for name, text in (("full", full), ("repaired", trunc)):
    row = run_single(Fake(text, None), Path("fake.yaml"), task, 0, "offline")
    print(name, {k: row[k] for k in ("parse_ok","truncation_suspected","label","label_correct","score")},
          "phase8", row["phase8"]["technical_status"], "phase9", row["phase9"].get("technical_status"), row["phase9"].get("route"),
          "fr_stored", row["forensic_record"] is not None, "class_valid", is_classification_valid(row))
