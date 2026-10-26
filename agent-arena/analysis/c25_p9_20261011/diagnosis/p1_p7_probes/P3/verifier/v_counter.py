"""Verifier counter-cases for F1/F2 (offline; no provider/network call)."""
import sys, os, re, json
from pathlib import Path
from collections import Counter

B, D = sys.argv[1], sys.argv[2]
sys.path.insert(0, B + "/src")
os.chdir(B)
import yaml
from agent_arena.task_loader import load_task
from agent_arena.phase10_pipeline import preflight
from agent_arena.providers.anthropic_live import build_user_message
from agent_arena.packet_integrity import (build_model_facing_packet, check_contamination,
                                          ModelFacingPacket, check_task)
from agent_arena.run_library import discover_cases, is_retired

# --- F1: whole active library through P10 input gate + live builder + P6.0 check ---------
act = discover_cases()
stats = Counter(); flagged_live = []; own_tok = []
for f, t in act:
    errs = preflight(t)
    stats["preflight_ok" if not errs else "preflight_blocked"] += 1
    try:
        u = build_user_message(t)
    except ValueError as e:
        stats["builder_refused"] += 1
        continue
    stats["ctx_in_msg" if (t.context or "").strip() and t.context.strip() in u else "ctx_not_in_msg"] += 1
    if re.search(r"\b" + re.escape(t.gold_label) + r"\b", u, re.I):
        own_tok.append(t.id)
    live_pkt = ModelFacingPacket(case_id=t.id, task_type="study_forensics",
                                 system=build_model_facing_packet(t).system, user=u)
    r_live = check_contamination(t, live_pkt, f.name)
    r_real = check_task(t, f.name)  # the actual P6.0 per-case entry point
    stats["p60_real_passed" if r_real.contamination.passed else "p60_real_failed"] += 1
    if not r_live.passed:
        flagged_live.append((t.id, sorted({x.code for x in r_live.findings})))
print("F1 active-library stats:", dict(stats))
print("F1 gold label word (\\b...\\b) present in live user message:", len(own_tok))
print("F1 check_contamination would flag the LIVE packet for", len(flagged_live), "of", len(act), ":", flagged_live)

# case001 detail
t = load_task("tasks/study_forensics/case001_social_media.yaml")
u = build_user_message(t)
print("case001 live msg tail:", repr(u[-150:]))
print("case001 contamination(live):", check_contamination(t, ModelFacingPacket(t.id, "study_forensics", build_model_facing_packet(t).system, u)).passed)

# CLI-level: `agent-arena audit validate --task <library yaml>` (no provider call)
from click.testing import CliRunner
from agent_arena.phase10_cli import audit
res = CliRunner().invoke(audit, ["validate", "--task", "tasks/study_forensics/case001_social_media.yaml"])
print("CLI audit validate case001: exit", res.exit_code, "out", res.output.strip())
res = CliRunner().invoke(audit, ["validate", "--task", "tasks/study_forensics/case042_edge_ai_energy_blind_spot.yaml"])
print("CLI audit validate RETIRED case042: exit", res.exit_code, "out", res.output.strip())

# --- F2: retirement marker variants ------------------------------------------------------
src = yaml.safe_load(open("tasks/study_forensics/case001_social_media.yaml"))
cc = Path(D) / "cc_tasks"; cc.mkdir(parents=True, exist_ok=True)
for p in cc.glob("*.yaml"):
    p.unlink()
variants = {
    "v_ok": {"status": "retired"},
    "v_cap": {"status": "Retired"},
    "v_upper": {"status": "RETIRED"},
    "v_space": {"status": "retired "},
    "v_typo_key": {"excluded_from_active_metric": True},
    "v_str_yes": {"excluded_from_active_metrics": "yes"},
    "v_str_false_but_status": {"excluded_from_active_metrics": "false", "status": "retired"},
    "v_intake_only": {"intake_review": "retired_after_review"},
}
for name, patch in variants.items():
    d = dict(src); d.update(patch); d["id"] = "cc-" + name
    yaml.safe_dump(d, open(cc / f"{name}.yaml", "w"))
active = sorted(t.id for _, t in discover_cases(task_dir=cc))
print("F2 active after variants:", active)
