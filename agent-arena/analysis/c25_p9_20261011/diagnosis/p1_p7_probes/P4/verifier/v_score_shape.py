"""Verifier: does the response *shape* each prompt asks for change the P4 score for the same label?

Same case, same final_answer 'solid'. (a) historical-prompt field set; (b) only the fields the
v3-phase8 prompt asks for (final_answer, confidence, steps/uncertainties, forensic_record stub).
No network: run_agent with in-process providers returning fixed text.
"""
import json
import sys

B = sys.argv[1]
sys.path.insert(0, B + "/src")
from agent_arena import run_library as rl  # noqa: E402
from agent_arena.providers import BaseProvider  # noqa: E402

HIST = {
    "final_answer": "solid", "evidence_tier": "clinical_human", "conclusion_tier": "same as evidence",
    "bridge_supported": True,
    "assumptions": ["The trial was randomised as described."],
    "steps": ["Human RCT; secondary outcome 21% vs 25%; author hedges and calls for larger trials."],
    "alternative_hypotheses": ["overclaim: 'promising signal' after a null primary outcome."],
    "uncertainties": ["Secondary endpoint; remote conduct; post-infection start."],
    "key_claims": ["Conclusion stays within the human-RCT evidence tier."],
    "self_check": ["Did not overflag decorative caution."],
    "confidence": 0.7,
}
P8 = {
    "final_answer": "solid", "confidence": 0.7,
    "steps": ["Human RCT; secondary outcome 21% vs 25%; author hedges and calls for larger trials."],
    "uncertainties": ["Secondary endpoint; remote conduct; post-infection start."],
    "forensic_record": {"record_id": "r1"},
}


class Fixed(BaseProvider):
    name = "fixed"
    model = "fixed-m"

    def __init__(self, payload):
        self.payload = payload

    def send_prompt(self, task, system_prompt):
        return json.dumps(self.payload)


case = rl.discover_cases(case_id="study-forensics-007")
P8_NO_FR = {k: v for k, v in P8.items() if k != "forensic_record"}  # control: P8 status not_executed
for name, payload in [("historical-shape", HIST), ("phase8-shape", P8), ("phase8-shape-no-fr", P8_NO_FR)]:
    rec = rl.run_single(Fixed(payload), case[0][0], case[0][1], 0, "verify")
    print(f"{name}: label={rec['label']} correct={rec['label_correct']} score={rec['score']} "
          f"parse_ok={rec['parse_ok']} p8={rec['phase8'].get('technical_status')}")
