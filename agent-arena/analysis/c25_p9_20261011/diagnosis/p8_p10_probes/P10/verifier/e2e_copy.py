"""E2E: throwaway schema-1.0 authorization (pinned history disabled in-process), transport double,
conflict case with sentinel gold fields -> live run -> inspect -> release attempt -> human review ->
release -> inspect -> CLI replay (same dir) -> replay from copied dir (K1) -> tamper checks."""
import sys, json, shutil, os
D = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new"
S = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_p8_p10/P10/verifier/e2e"
sys.path.insert(0, D + "/src"); sys.path.insert(0, D)
from pathlib import Path
if Path(S).exists(): shutil.rmtree(S)
Path(S).mkdir(parents=True)
os.environ.pop("ANTHROPIC_API_KEY", None)
from agent_arena import phase10_live as live
live.KNOWN_CLOSED_AUTHORIZATIONS = {}
import tests.test_phase10_live as T
from agent_arena.phase10_bundle import run_audit, inspect_bundle, release_candidate, review_candidate
from agent_arena.providers.anthropic_live import PROFILES
from agent_arena.schemas import RubricItem
H3 = "claude-haiku-5-5@3"
task, raw = T._conflict_task()
SENT = "GOLDSENTINEL"
task = task.model_copy(update={"expected_answer": SENT + "-expected", "reference_solution": SENT + "-ref",
    "key_insights": [SENT + "-insight"], "common_errors": [SENT + "-err"], "expected_failure_modes": [SENT + "-fm"],
    "trap_type": SENT + "-trap", "expected_mechanism_terms": [SENT + "-mech"]})
tp = Path(S) / "task.json"; tp.write_text(task.model_dump_json())
auth = T._authorize(Path(S) / "auth", [task], profiles=(H3,), ceiling=300_000)
tr = T.Transport(T.message(raw, request_id="req_p"), T.message(raw, request_id="req_c"))
with T._session(auth, tr) as session:
    prov = live.LiveAuditProvider(session, H3, task.id, "primary", PROFILES[H3].prompt_versions[0])
    res = run_audit(task, prov, output_root=Path(S) / "out", review_state=auth / "phase9-state")
    summ = session.summary()
print("live:", res.status, "requests:", len(tr.requests), "ledger:", summ)
blob = json.dumps([r["body"] for r in tr.requests])
print("gold sentinel in any request body:", SENT in blob)
print("claim/context verbatim in primary:", task.prompt in tr.requests[0]["body"]["messages"][0]["content"], task.context in tr.requests[0]["body"]["messages"][0]["content"])
print("systems:", [r["body"]["system"][:0] or len(r["body"]["system"]) for r in tr.requests])
rec = json.loads((Path(res.path) / "record.json").read_text())
p9 = rec["run_record"]["metadata"]["phase9"]
print("p9:", p9["route"], p9["mandatory"], [(a["kind"], a["status"]) for a in p9["attempts"]], "mode", rec["execution_mode"])
print("inspect:", inspect_bundle(Path(res.path)))
print("release:", release_candidate(Path(res.path), output_root=Path(S)/"rel", reviewer="diag", reason="diag").status)
orig = [p for p in p9["positions"] if p["origin"] == "original"][0]["position_id"]
# human selection of conflicting original -> must be rejected
r1 = review_candidate(Path(res.path), output_root=Path(S)/"rev", state_dir=Path(S)/"hstate1", selected_position_id=orig, reviewer="diag", reason="select original")
print("human select conflicting original:", r1.status, r1.errors[:1])
r2 = review_candidate(Path(res.path), output_root=Path(S)/"rev", state_dir=Path(S)/"hstate2", selected_position_id=orig, reviewer="diag", reason="correction", corrected_raw_output=T._recording("positive"))
print("human correction:", r2.status, r2.errors[:1])
if r2.path:
    rel = release_candidate(Path(r2.path), output_root=Path(S)/"rel", reviewer="diag", reason="diag release")
    print("release after correction:", rel.status, inspect_bundle(Path(rel.path)).valid if rel.path else None)
    md = (Path(rel.path) / "report.md").read_text()
    print("report mentions live notice:", "LIVE MODEL GENERATION" in md, "human" in md.lower())
# replay same dir via CLI
from click.testing import CliRunner
from agent_arena.cli import cli
rr = CliRunner().invoke(cli, ["audit", "run", "--replay", "--task", str(tp), "--authorization-dir", str(auth), "--profile", H3, "--output-root", str(Path(S)/"replay")])
print("CLI replay same dir: exit", rr.exit_code, json.loads(rr.output)["status"] if rr.output.strip().startswith("{") else rr.output[:300])
print("replay wrote into authorization dir:", sorted(p.name for p in auth.iterdir()))
# K1: copied directory
cp = Path(S) / "auth_copy"; shutil.copytree(auth, cp)
rr = CliRunner().invoke(cli, ["audit", "run", "--replay", "--task", str(tp), "--authorization-dir", str(cp), "--profile", H3, "--output-root", str(Path(S)/"replay2")])
print("CLI replay copied dir: exit", rr.exit_code, rr.output[:300])
# inspect of the original live bundle after authorization dir was moved away (bundles self-contained?)
mv = Path(S) / "auth_moved"; shutil.move(str(auth), str(mv))
print("inspect live bundle after authorization dir moved:", inspect_bundle(Path(res.path)).valid)
