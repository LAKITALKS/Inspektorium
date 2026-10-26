import sys, os, json, yaml, re
B, D = sys.argv[1], sys.argv[2]
sys.path.insert(0, B+"/src")
from pathlib import Path
from agent_arena.task_loader import load_task
from agent_arena.phase10_pipeline import preflight
from agent_arena.providers.anthropic_live import build_user_message
from agent_arena.packet_integrity import build_model_facing_packet
from agent_arena.run_library import discover_cases, is_retired
# Counter-case A: unmodified library case fed to the canonical P10 audit input gate + live message builder
for name in ["case001_social_media.yaml","case044_mice_memory_dementia.yaml","case043_cell_study_cancer_cure.yaml"]:
    t=load_task(Path(B)/"tasks/study_forensics"/name)
    u=build_user_message(t); pkt=build_model_facing_packet(t)
    m=re.search(r"(solid|overclaim|mechanism_vs_evidence|correlation_vs_causation)",t.context)
    print(name,"| p10 preflight errors:",preflight(t),"| gold:",t.gold_label,
          "| live msg has gold token:",t.gold_label in u, "| phase6 packet (prompt-only) has gold token:",t.gold_label in pkt.user,
          "| ctx snippet:",repr(t.context.strip()[:90]))
# Counter-case B: retirement marker variants written in scratch
src=yaml.safe_load(open(Path(B)/"tasks/study_forensics/case001_social_media.yaml"))
variants={"cc_ok.yaml":{"status":"retired"},"cc_case.yaml":{"status":"Retired"},
          "cc_typo.yaml":{"excluded_from_active_metric":True},"cc_strbool.yaml":{"excluded_from_active_metrics":"false","status":"retired"}}
for fn,patch in variants.items():
    d=dict(src); d.update(patch); d["id"]="cc-"+fn[:-5]; yaml.safe_dump(d,open(Path(D)/"cc_tasks"/fn,"w"))
act=[t.id for _,t in discover_cases(task_dir=Path(D)/"cc_tasks")]
print("active after variants:",sorted(act))
