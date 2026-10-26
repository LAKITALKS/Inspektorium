"""Trace 1: offline recorded examples through run_audit -> bundle -> inspect -> review -> release."""
import json, sys, hashlib, shutil
from pathlib import Path
D = Path("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new")
sys.path.insert(0, str(D / "src"))
OUT = Path(__file__).parent / "out_trace1"
shutil.rmtree(OUT, ignore_errors=True); OUT.mkdir()
from agent_arena.schemas import Task, RunRecord
from agent_arena.phase9_runtime import OfflineReviewProvider, execute_review
from agent_arena.phase10_bundle import run_audit, inspect_bundle, release_candidate, review_candidate, create_candidate
from agent_arena.phase10_pipeline import reconstruct, evaluate
from agent_arena.runner import resolve_study_forensics_prompt
import agent_arena.runner as R

versions = {v: hashlib.sha256(resolve_study_forensics_prompt(v).encode()).hexdigest()
            for k, v in vars(R).items() if k.startswith("STUDY_FORENSICS_PROMPT_VERSION") and isinstance(v, str)
            and v.startswith("study_forensics_prompt/v3")}
by_sha = {s: v for v, s in versions.items()}
ex = D / "examples/phase10"
summary = {}
for name, task_name in [("positive", "positive"), ("negative", "negative"), ("unknown", "unknown"),
                        ("conflict", "positive"), ("long-hostile", "long-hostile"), ("optional-unknown", "positive")]:
    task = Task.model_validate_json((ex / f"{task_name}-task.json").read_text())
    raw = (ex / f"{name}-recording.json").read_text()
    prov = OfflineReviewProvider(raw)
    res = run_audit(task, prov, output_root=OUT / name)
    row = {"status": res.status, "errors": res.errors[:4]}
    req = prov.requests[0]
    row["provider_saw_system_prompt"] = by_sha.get(hashlib.sha256(req["system_prompt"].encode()).hexdigest(), "UNKNOWN")
    row["provider_saw_claim_unchanged"] = req["task"]["prompt"] == task.prompt and req["task"]["context"] == task.context
    if res.path:
        p = Path(res.path)
        rec = RunRecord.model_validate(json.loads((p / "record.json").read_text())["run_record"])
        review, sel, ass, forensic = reconstruct(rec)
        ar = rec.results[0].agent_result
        row["p7_parse_ok"] = ar.parse_ok
        row["p8"] = {k: ass.get(k) for k in ("technical_status", "composite_state", "model_composite_state",
                                             "host_composite_state", "derived_label", "original_model_label")}
        row["p8_conflicts"] = [(c.get("scope"), c.get("proposition_id"), c.get("model_state"), c.get("host_state"))
                               for c in ass.get("model_host_conflicts", [])]
        row["p8_props"] = [(q.get("proposition_id"), q.get("reported_verdict"), q.get("host_state"), q.get("derived_state"),
                            q.get("materiality")) for q in ass.get("propositions", [])]
        row["p9"] = {k: review.get(k) for k in ("route", "mandatory", "review_state", "technical_status", "execution_status")}
        row["p9_triggers"] = [(t.get("field"), t.get("kind") or t.get("trigger"), t.get("mandatory")) for t in review.get("triggers", [])]
        dec = json.loads((p / "decision.json").read_text())
        row["p10_failed_controls"] = [c["control_id"] for c in dec["controls"] if c["outcome"] == "fail"]
        row["inspect"] = inspect_bundle(p).model_dump()
        md = (p / "report.md").read_text()
        row["report_mentions_conflict"] = "conflict" in md.lower()
        rel = release_candidate(p, output_root=OUT / name, reviewer="diag", reason="diag trace")
        row["release"] = rel.status
        summary[name] = row
    else:
        summary[name] = row
(Path(__file__).parent / "trace1_summary.json").write_text(json.dumps(summary, indent=1, default=str))
for k, v in summary.items():
    print(k, json.dumps({x: v.get(x) for x in ("status", "provider_saw_system_prompt", "p8", "p8_conflicts", "p9", "p10_failed_controls", "release")}, default=str))
