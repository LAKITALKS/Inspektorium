"""Verifier: are completed runs persisted if the batch is interrupted mid-run? (no network)"""
import json
import os
import sys
from pathlib import Path

B, S = sys.argv[1], sys.argv[2]
sys.path.insert(0, B + "/src")
from agent_arena import run_library as rl  # noqa: E402
from agent_arena.providers import BaseProvider  # noqa: E402


class InterruptOnThird(BaseProvider):
    name = "interrupt"
    model = "interrupt-m"

    def __init__(self):
        self.n = 0

    def send_prompt(self, task, system_prompt):
        self.n += 1
        if self.n == 3:
            raise KeyboardInterrupt  # stands in for Ctrl-C / SIGINT during call 3
        return json.dumps({"final_answer": "solid", "confidence": 0.7})


out = Path(S) / "interrupt_run"
p = InterruptOnThird()
try:
    rl.run_library(p, rl.discover_cases(limit=3), runs_per_case=1, out_dir=out)
except KeyboardInterrupt:
    print("interrupted after", p.n, "provider calls (2 completed)")
print("out_dir exists:", out.exists(), "| files:", sorted(os.listdir(out)) if out.exists() else [])
