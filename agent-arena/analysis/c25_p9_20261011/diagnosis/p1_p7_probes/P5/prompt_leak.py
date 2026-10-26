import sys, json, re, shutil
B="__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
sys.path.insert(0, B+"/src"); sys.path.insert(0, B+"/tests")
from pathlib import Path
import hashlib
import test_full_replication_contract as t
from agent_arena import full_replication_contract as frc
seen=[]
class Cap(t._CountingProvider):
    def generate(self, task, system_prompt):
        seen.append((task.id, hashlib.sha256(system_prompt.encode()).hexdigest(), task.prompt))
        return super().generate(task, system_prompt)
class Bld(t._ProviderBuilder):
    def __call__(self, mk):
        self.constructions+=1; p=Cap(t.cc.rc.MODELS[mk]["exact_model_id"]); self.providers.append(p); return p
out=Path(sys.argv[1]); shutil.rmtree(out, ignore_errors=True)
t._run_synthetic(out, t._synthetic_document(), Bld())
print("requests", len(seen), "system sha set", {s for _,s,_ in seen}, "expected", frc.EXPECTED_PROMPT_SHA256)
from agent_arena import phase7a_execution as p7
units={u.unit_id:u for u in p7.resolve_evaluated_units(B)}
bad=[]
for tid,_,prompt in seen:
    low=prompt.lower()
    for pat in ("gold","expected_answer","expected answer","rubric","curator","competing_label","difficulty_tier","hld-","holdout"):
        if pat in low: bad.append((tid,pat))
print("leak-pattern hits", len(bad), bad[:5])
# task object fields beyond prompt
u=next(iter(units.values())); print("task attrs", sorted(k for k in vars(u.task)))
# verify full prompt reaches provider unchanged
mism=[tid for tid,_,p in seen if p!=units[tid.split('#')[0]].task.prompt] if all(tid.split('#')[0] in units for tid,_,_ in seen) else "ids differ"
print("prompt unchanged mismatches", mism if isinstance(mism,str) else len(mism), "example id", seen[0][0])
