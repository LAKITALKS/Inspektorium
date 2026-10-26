import sys, json
D = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new"
sys.path[:0] = [D + "/src", D]
OUT = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_p8_p10/P9"
from tests.test_phase8_9_conflict import case, set_host, set_model, raw_output, position
from agent_arena.schemas import Task
GOLD = {"expected_answer": "GOLD_SENTINEL_EXPECTED", "reference_solution": "GOLD_SENTINEL_REFERENCE",
        "rubric": [{"criterion": "GOLD_SENTINEL_RUBRIC", "points": 1}],
        "key_insights": ["GOLD_SENTINEL_INSIGHT"], "common_errors": ["GOLD_SENTINEL_ERR"],
        "expected_failure_modes": ["GOLD_SENTINEL_FM"], "fragile_points": ["GOLD_SENTINEL_FP"]}
def gold_case(host, model):
    task, payload = case(host, model)
    d = task.model_dump(); d.update(GOLD)
    return Task.model_validate(d), payload
