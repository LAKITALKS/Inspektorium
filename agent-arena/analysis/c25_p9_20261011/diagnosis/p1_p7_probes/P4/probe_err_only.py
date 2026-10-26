import sys, json
B, S = sys.argv[1], sys.argv[2]; sys.path.insert(0, B+"/src")
from pathlib import Path
from agent_arena import run_library as rl
from agent_arena.providers import BaseProvider, ModelResponse
SEQ = [("", "error", "rate limited 429")]
class P(BaseProvider):
    name="probe"; model="probe-m"
    def __init__(self): self.i=0
    def send_prompt(self,t,s): raise NotImplementedError
    def generate(self, task, system_prompt):
        text, fr, err = SEQ[self.i % len(SEQ)]; self.i+=1
        return ModelResponse(text=text, provider="probe", model="probe-m", finish_reason=fr, usage=None, latency_ms=1, error=err, error_type=("rate_limit" if err else None))
cases = rl.discover_cases(case_id="study-forensics-007", task_dir=Path(B+"/tasks/study_forensics"))
s = rl.run_library(P(), cases, runs_per_case=4, out_dir=Path(S+"/err_only_run"))
c = s.case_stability[0]
print("flags", c.flags); print("unique", c.unique_labels, "consistency", c.label_consistency_rate, "succ", c.successful_runs, "parse_fail", c.parse_failures, "trunc", c.truncation_count, "score_range", c.score_range)
for l in open(S+"/err_only_run/results.jsonl"):
    r=json.loads(l); print(r["run_index"], r["label"], r["parse_ok"], r["finish_reason"], r["truncation_suspected"], r["score"], r["error_type"])
