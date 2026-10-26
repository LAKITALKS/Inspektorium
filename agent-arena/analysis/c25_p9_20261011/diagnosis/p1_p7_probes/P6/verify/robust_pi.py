import sys
from pathlib import Path
B = sys.argv[1]; sys.path.insert(0, B + "/src")
from agent_arena.task_loader import load_task
from agent_arena.packet_integrity import check_task, check_contamination, ModelFacingPacket
from agent_arena.providers.anthropic_live import build_user_message
from agent_arena.runner import resolve_study_forensics_prompt
from agent_arena.phase10_pipeline import preflight
n = ok = pre_ok = live_flag = own = 0
for f in sorted(Path(B, "tasks/study_forensics_robustness").glob("P7A-*.yaml")):
    t = load_task(str(f)); n += 1
    ok += check_task(t, case_file=f.name).ok
    pre_ok += not preflight(t)
    g = (t.gold_label or "").lower(); ctx = " ".join(t.context.split()).lower()
    own += bool(g and (g in ctx or g.replace("_", " ") in ctx))
    pkt = ModelFacingPacket(t.id, "study_forensics", resolve_study_forensics_prompt("study_forensics_prompt/v3-phase8"), build_user_message(t))
    live_flag += not check_contamination(t, pkt, case_file=f.name).passed
print(f"robustness P7A tasks: {n}; P6 check_task ok: {ok}; P10 preflight ok: {pre_ok}; own gold label in context: {own}; existing rules would flag the LIVE packet: {live_flag}")
