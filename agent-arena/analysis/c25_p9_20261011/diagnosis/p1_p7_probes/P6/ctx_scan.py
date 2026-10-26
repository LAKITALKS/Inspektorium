import sys, glob, collections
B=sys.argv[1]
sys.path.insert(0,B+"/src")
from agent_arena.task_loader import load_task
c=collections.Counter(); ex=[]
for p in sorted(glob.glob(B+"/tasks/**/*.yaml",recursive=True)):
    try: t=load_task(p)
    except Exception as e: c["loadfail"]+=1; continue
    k=(t.task_type.value, bool(t.context.strip()))
    c[k]+=1
    if t.task_type.value=="study_forensics" and t.context.strip() and len(ex)<3: ex.append((p.replace(B+"/",""), len(t.context)))
print(c); print(ex)
