"""Verifier: stability-flag semantics with scripted providers (no network, no artifacts)."""
import json
import sys

B = sys.argv[1]
sys.path.insert(0, B + "/src")
from agent_arena import run_library as rl  # noqa: E402
from agent_arena.providers import BaseProvider, ModelResponse  # noqa: E402

OK_SOLID = (json.dumps({"final_answer": "solid", "steps": ["a"], "key_claims": ["b"], "confidence": 0.8}), "stop", None)
TRUNC_OVER = ('{"final_answer":"overclaim","steps":["a"],"key_claims":["b"],"confidence":0.6', "length", None)
NONJSON = ("I think it's overclaim but no JSON", "stop", None)
ERR = ("", "error", "rate limited 429")


class Scripted(BaseProvider):
    name = "scripted"
    model = "scripted-m"

    def __init__(self, seq):
        self.seq, self.i = seq, 0

    def send_prompt(self, t, s):
        raise NotImplementedError

    def generate(self, task, system_prompt):
        text, fr, err = self.seq[self.i % len(self.seq)]
        self.i += 1
        return ModelResponse(text=text, provider="scripted", model="scripted-m", finish_reason=fr,
                             latency_ms=1, error=err, error_type=("rate_limit" if err else None))


cases = rl.discover_cases(case_id="study-forensics-007")
for name, seq in [("mixed", [OK_SOLID, TRUNC_OVER, NONJSON, ERR]), ("err_only", [ERR]),
                  ("ok_plus_errors", [OK_SOLID, ERR]), ("trunc_only_vs_ok", [OK_SOLID, TRUNC_OVER])]:
    s = rl.run_library(Scripted(seq), cases, runs_per_case=4, write_artifacts=False)
    c = s.case_stability[0]
    print(f"[{name}]", {k: v for k, v in c.flags.items() if v}, "| labels", c.unique_labels,
          "consistency", c.label_consistency_rate, "ok", c.successful_runs, "parse_fail", c.parse_failures,
          "trunc", c.truncation_count, "range", c.score_range)
    for r in s.records:
        print("   ", r["run_index"], r["label"], r["parse_ok"], r["finish_reason"], r["truncation_suspected"],
              r["score"], r["error_type"], "p8:", (r["phase8"] or {}).get("technical_status"))
    md = rl.render_summary_md(s)
    print("   md:", [ln for ln in md.splitlines() if ln.startswith("- Parse") or ln.startswith("- Parse-fragile")])
