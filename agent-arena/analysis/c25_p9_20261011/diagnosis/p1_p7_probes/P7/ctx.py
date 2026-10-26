import sys
B="__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
sys.path.insert(0,B+"/src")
import os; os.chdir(B)
from agent_arena.phase7a_execution import resolve_evaluated_units
from agent_arena import runner
u=resolve_evaluated_units()
print(len(u), "nonempty context:", sum(bool((x.task.context or "").strip()) for x in u))
import inspect
print([n for n in dir(runner) if "prompt" in n.lower()][:20])
by={x.unit_id:x for x in u}
withc=[x for x in u if (x.task.context or "").strip()]
x=withc[0]; print(x.unit_id, x.unit_type, "| prompt:", x.task.prompt[:160], "| context:", x.task.context[:300])
v=[y for y in u if y.unit_type=="perturbation_variant" and (by[y.base_case_id].task.context or "").strip()]
print("variants whose base has context:", len(v), "of", sum(y.unit_type=="perturbation_variant" for y in u))
y=v[0]; print(y.unit_id, "base", y.base_case_id, "| variant prompt:", y.task.prompt[:200])
from collections import Counter
print(Counter(x.unit_type for x in withc))
