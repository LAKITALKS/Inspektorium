"""P1/P7 parser -> P8 -> P10 transition: an answer holding a draft analysis and a self-correction.

Offline canonical path only (exact OfflineReviewProvider), no network. Recording = positive analysis (supported),
then prose, then the negative analysis of the same task shape. Which object reaches P8/P10, and is the ambiguity
visible anywhere?"""
import json, shutil, sys
from pathlib import Path
D = Path("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new")
sys.path.insert(0, str(D / "src")); sys.path.insert(0, str(D))
import agent_arena
assert str(D) in agent_arena.__file__
X = Path(__file__).parent
W = X / "out_v5"; shutil.rmtree(W, ignore_errors=True); W.mkdir()
from agent_arena.output_contract import parse_structured_output
from agent_arena.phase10_bundle import run_audit, inspect_bundle, release_candidate
from agent_arena.phase9_runtime import OfflineReviewProvider
from agent_arena.task_loader import load_task

task = load_task(D / "examples/phase10/positive-task.json")
pos = (D / "examples/phase10/positive-recording.json").read_text().strip()
from tests.test_phase8_9_conflict import set_model
neg = json.loads(pos)
set_model(neg["forensic_record"], "unsupported")
neg["final_answer"] = "overclaim"
out = {"negative_final_answer": neg.get("final_answer")}
cases = {
    "draft_then_correction": pos + "\n\nWait, I made an error. Corrected analysis:\n" + json.dumps(neg),
    "two_fenced_blocks": "```json\n" + pos + "\n```\nCorrection:\n```json\n" + json.dumps(neg) + "\n```",
}
for name, raw in cases.items():
    parsed, diag = parse_structured_output(raw, "stop")
    res = run_audit(task, OfflineReviewProvider(raw), output_root=W / name)
    row = {"parser_ok": diag.ok, "strategy": diag.strategy, "repaired": diag.repaired,
           "truncation_suspected": diag.truncation_suspected,
           "diag_fields": sorted(diag.as_dict()),
           "parsed_final_answer": parsed.final_answer if parsed else None,
           "status": res.status, "errors": res.errors[:2]}
    if res.path:
        rec = json.loads((Path(res.path) / "record.json").read_text())
        p8 = rec["run_record"]["results"][0]["agent_result"]["phase8"]
        row["p8"] = {k: p8.get(k) for k in ("technical_status", "composite_state", "original_model_label", "derived_label")}
        row["inspect_valid"] = inspect_bundle(Path(res.path)).valid
        if res.status == "READY_FOR_RELEASE":
            rel = release_candidate(Path(res.path), output_root=W / name, reviewer="diag", reason="probe")
            row["release"] = rel.status
        md = (Path(res.path) / "report.md").read_text()
        row["report_mentions_second_object_or_ambiguity"] = any(s in md.lower() for s in ("multiple", "ambiguous", "second analysis", "correction"))
    out[name] = row
print(json.dumps(out, indent=1, default=str))
(X / "v5_summary.json").write_text(json.dumps(out, indent=1, default=str))
