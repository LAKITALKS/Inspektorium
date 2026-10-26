"""P6 probe: does the Phase-6.0 packet-integrity leakage control see what the current live builder sends?
No network: build_user_message is a pure string builder; nothing is sent."""
import sys, re
from pathlib import Path
B = sys.argv[1]; sys.path.insert(0, B + "/src")
from agent_arena.task_loader import load_task
from agent_arena.packet_integrity import check_task, check_contamination, ModelFacingPacket, build_model_facing_packet
from agent_arena.providers.anthropic_live import build_user_message
from agent_arena.runner import _select_system_prompt, STUDY_FORENSICS_PROMPT_VERSION_PHASE8

LABELS = ("solid", "overclaim", "correlation_vs_causation", "mechanism_vs_evidence",
          "correlation vs causation", "mechanism vs evidence")
GUIDANCE = re.compile(r"\b(the agent|agents?) (should|must|may)\b|\bexpected\b|\bgold\b|\btrap\b", re.I)

p = Path(B) / "tasks/study_forensics/case004_multivitamin.yaml"
t = load_task(str(p))
rep = check_task(t, case_file=p.name)
print("case004 gold:", t.gold_label, "| packet_integrity ok:", rep.ok)
print("  reconstructed user == task.prompt only:", build_model_facing_packet(t).user == t.prompt)
print("  reconstructed system version: historical; executed default:", STUDY_FORENSICS_PROMPT_VERSION_PHASE8,
      "| same bytes:", build_model_facing_packet(t).system == _select_system_prompt(t, STUDY_FORENSICS_PROMPT_VERSION_PHASE8))
live_user = build_user_message(t)
print("  live user message contains context:", t.context.strip() in live_user)
print("  live context text:", t.context.strip().replace("\n", " "))
live_pkt = ModelFacingPacket(case_id=t.id, task_type="study_forensics",
                             system=_select_system_prompt(t, STUDY_FORENSICS_PROMPT_VERSION_PHASE8), user=live_user)
c = check_contamination(t, live_pkt, case_file=p.name)
print("  check_contamination on LIVE packet passed:", c.passed, "| checked fields:", c.diagnostics["checked_blob_fields"])

# library-wide census
n = n_ok = n_label = n_gold_word = n_guid = 0; ex = []
for f in sorted((Path(B) / "tasks/study_forensics").glob("*.yaml")):
    try: t = load_task(str(f))
    except Exception: continue
    if not t.context.strip(): continue
    n += 1
    if check_task(t, case_file=f.name).ok: n_ok += 1
    ctx = t.context.lower()
    g = (t.gold_label or "").lower()
    if any(l in ctx for l in LABELS): n_label += 1
    if g and (g in ctx or g.replace("_", " ") in ctx):
        n_gold_word += 1
        if len(ex) < 4: ex.append((f.name, g, t.context.strip().replace("\n", " ")[:140]))
    if GUIDANCE.search(t.context): n_guid += 1
print(f"\nstudy_forensics tasks with nonempty context: {n}; packet_integrity ok: {n_ok}")
print(f"  context contains any label token: {n_label}; contains the case's OWN gold label: {n_gold_word}; curator-guidance phrasing: {n_guid}")
for e in ex: print("  e.g.", e)
