import sys, os, json, re
B="__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
sys.path.insert(0, B+"/src"); os.chdir(B)
from pathlib import Path
from collections import Counter
import yaml
from agent_arena.task_loader import load_task
from agent_arena.schemas import Task
from agent_arena.run_library import discover_cases, is_retired
from agent_arena.providers.anthropic_live import build_user_message
import agent_arena
print("module from:", agent_arena.__file__)
LABELS={"solid","overclaim","mechanism_vs_evidence","correlation_vs_causation"}
files=sorted(Path("tasks/study_forensics").glob("*.yaml"))
ids=Counter(); labs=Counter(); bad=[]; extras=[]
known=set(Task.model_fields)
tasks=[]
for f in files:
    raw=yaml.safe_load(open(f)); t=load_task(f); tasks.append((f,t))
    ids[t.id]+=1; labs[t.gold_label]+=1
    if t.gold_label not in LABELS: bad.append((f.name,t.gold_label))
    unk=set(raw)-known
    if unk: extras.append((f.name,sorted(unk)))
print("files",len(files),"unique ids",len(ids),"dupes",[k for k,v in ids.items() if v>1])
print("labels",dict(labs),"bad",bad)
print("unknown top-level keys (silently dropped by Task):",extras[:10], "n=",len(extras))
act=discover_cases(); allc=discover_cases(include_retired=True)
print("active",len(act),"all",len(allc),"retired",[t.id for _,t in allc if is_retired(t)])
print("explicit 042:",[t.id for _,t in discover_cases(case_id="study-forensics-042")])
print("active labels",dict(Counter(t.gold_label for _,t in act)))
q=sorted(Path("tasks/study_forensics/quarantine").glob("*.yaml")); print("quarantine (not globbed):",[p.name for p in q])
# context leakage: label tokens / curator words in context
pat={"solid":r"\bsolid\b","overclaim":r"\boverclaim","mechanism_vs_evidence":r"mechanism_vs_evidence","correlation_vs_causation":r"correlation_vs_causation"}
leak=[]; goldinctx=[]
for f,t in act:
    ctx=t.context or ""
    hits=[l for l,p in pat.items() if re.search(p,ctx,re.I)]
    if hits: leak.append((t.id,t.gold_label,hits))
    if t.gold_label and re.search(pat[t.gold_label],ctx,re.I): goldinctx.append(t.id)
print("active cases w/ label token in context:",len(leak)," gold label itself named in context:",len(goldinctx))
for x in leak[:8]: print("  ",x)
# what each builder sends for one leaking case
t=[t for _,t in act if t.id=="study-forensics-044"][0]
u=build_user_message(t)
print("live builder contains 'mechanism_vs_evidence':", "mechanism_vs_evidence" in u, " len", len(u))
print("legacy builder content == task.prompt only; contains label:", "mechanism_vs_evidence" in t.prompt)
json.dump({"leak":leak,"goldinctx":goldinctx},open(sys.argv[1],"w"),indent=1)
