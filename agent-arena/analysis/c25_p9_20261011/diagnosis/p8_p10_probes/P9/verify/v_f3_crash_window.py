"""Verifier probe for P9-F3 without deleting any file: crash between the durable ledger reservation
(phase9_runtime.py:478) and the 'begun' sidecar save (:480), then resume. Offline only."""
import json
import shutil
import sys
from pathlib import Path

D = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new"
sys.path[:0] = [D + "/src", D]
OUT = Path("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_p8_p10/P9/verify/f3")
assert str(OUT).startswith("/private/tmp/")
shutil.rmtree(OUT, ignore_errors=True)

import agent_arena.phase9_runtime as rt  # noqa: E402
from agent_arena.evaluator import evaluate_run  # noqa: E402
from agent_arena.phase10_bundle import create_candidate  # noqa: E402
from agent_arena.phase9_review import case_key  # noqa: E402
from agent_arena.phase9_runtime import OfflineReviewProvider, execute_review  # noqa: E402
from agent_arena.runner import run_agent  # noqa: E402
from tests.test_phase8_9_conflict import example, set_model  # noqa: E402

task, raw = example("positive", "unsupported")
record = evaluate_run(task, "run1", [run_agent(OfflineReviewProvider(raw), task)])
agree = json.loads(raw)
set_model(agree["forensic_record"], "supported")

real_save = rt._save


class Killed(BaseException):
    pass


def crash_on_begun(base, path, result):
    attempts = result.metadata["phase9"].get("attempts", [])
    if attempts and attempts[-1].get("status") == "begun":
        raise Killed("process killed after ledger.reserve, before the begun sidecar")
    return real_save(base, path, result)


rt._save = crash_on_begun
try:
    execute_review(record, OfflineReviewProvider(json.dumps(agree)), base_dir=OUT, authorized=True, budget_calls=2)
except Killed as exc:
    print("crash:", exc)
rt._save = real_save
side = OUT / "phase9" / f"{case_key(task)}.json"
ledger = json.loads((OUT / "phase9" / f"{case_key(task)}.ledger.json").read_text())
print("sidecar exists after crash:", side.exists(), "| ledger attempts:", [(a["slot_key"], a["state"]) for a in ledger["attempts"]])
resumed = execute_review(record, OfflineReviewProvider(json.dumps(agree)), base_dir=OUT, authorized=True, budget_calls=2)
d = resumed.metadata["phase9"]
print("resume:", [(a["kind"], a["status"], a["reason"]) for a in d["attempts"]], d["route"],
      "execution_status=", d.get("execution_status"))
out = create_candidate(resumed, output_root=OUT / "bundle")
rep = (Path(out.path) / "report.md").read_text()
print("bundle:", out.status, "| report row:", [ln.strip()[:80] for ln in rep.splitlines() if "review execution" in ln.lower()][:1])
