"""Checkpoint (a) on the live path with gold sentinels in every Task gold field (the K11 example task has
none). Throwaway authorization (tests helper), KNOWN_CLOSED={}, MockTransport, api_key='test-key'."""
import json
import shutil
import sys
from pathlib import Path

D = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new"
sys.path[:0] = [D + "/src", D]
OUT = Path("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_p8_p10/P9/verify/live_gold")
assert str(OUT).startswith("/private/tmp/")
shutil.rmtree(OUT, ignore_errors=True)
from agent_arena import phase10_live as live  # noqa: E402
live.KNOWN_CLOSED_AUTHORIZATIONS = {}
import tests.test_phase10_live as T  # noqa: E402
from agent_arena.phase10_bundle import run_audit  # noqa: E402
from agent_arena.providers.anthropic_live import PROFILES  # noqa: E402
from agent_arena.schemas import Task  # noqa: E402

GOLD = {"expected_answer": "GOLD_SENTINEL_EXPECTED", "reference_solution": "GOLD_SENTINEL_REFERENCE",
        "rubric": [{"criterion": "GOLD_SENTINEL_RUBRIC", "points": 1}], "key_insights": ["GOLD_SENTINEL_INSIGHT"],
        "common_errors": ["GOLD_SENTINEL_ERR"], "expected_failure_modes": ["GOLD_SENTINEL_FM"],
        "fragile_points": ["GOLD_SENTINEL_FP"]}
H3 = "claude-haiku-5-5@3"
task, raw = T._conflict_task("aa-verify-gold")
data = task.model_dump()
data.update(GOLD)
task = Task.model_validate(data)
directory = T._authorize(OUT / "auth", [task], profiles=(H3,), ceiling=300_000)
transport = T.Transport(T.message(raw, request_id="req_p"), T.message(raw, request_id="req_c"))
with T._session(directory, transport) as session:
    prov = live.LiveAuditProvider(session, H3, task.id, "primary", PROFILES[H3].prompt_versions[0])
    res = run_audit(task, prov, output_root=OUT / "out", review_state=directory / "phase9-state")
blob = json.dumps([r["body"] for r in transport.requests])
print("requests:", len(transport.requests), "| status:", res.status)
print("GOLD_SENTINEL on the wire:", "GOLD_SENTINEL" in blob)
review = transport.requests[1]["body"]["messages"][0]["content"]
print("review request carries the original claim verbatim:", task.prompt in review,
      "| context verbatim:", (task.context or "") in review)
