import sys
B="__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
sys.path.insert(0, B+"/src")
from agent_arena import phase7a_execution as p7
us=p7.resolve_evaluated_units(B)
nonempty=[(u.unit_id, len(str(u.task.context))) for u in us if u.task.context]
print("units with non-empty task.context:", len(nonempty), nonempty[:5])
print("min/max prompt len", min(len(u.task.prompt) for u in us), max(len(u.task.prompt) for u in us))
inprompt=sum(1 for u in us if u.task.context and str(u.task.context).strip()[:60] in u.task.prompt)
print("context contained in prompt:", inprompt)
u=[x for x in us if x.unit_id=="P7A-BND-001"][0]
print("CONTEXT:", str(u.task.context)[:466]); print("PROMPT:", u.task.prompt[:700])
