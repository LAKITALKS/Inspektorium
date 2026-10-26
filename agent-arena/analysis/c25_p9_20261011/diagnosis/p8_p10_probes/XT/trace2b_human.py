"""Trace 2b: human resolution of the live conflict bundle from trace 2 (throwaway state only)."""
import json, sys
from pathlib import Path
D = Path("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new")
sys.path.insert(0, str(D / "src")); sys.path.insert(0, str(D))
X = Path(__file__).parent; W = X / "out_trace2"
from agent_arena.phase10_bundle import review_candidate, release_candidate, inspect_bundle
from agent_arena.phase10_pipeline import reconstruct
from agent_arena.schemas import RunRecord
live_out = W / "live_out"
bundle = next(p for p in live_out.iterdir() if p.is_dir() and not p.name.startswith("."))
rec = RunRecord.model_validate(json.loads((bundle / "record.json").read_text())["run_record"])
positions = rec.metadata["phase9"]["positions"]
state = W / "auth" / "phase9-state" / "claude-haiku-5-5@3"
out = {}
for p in positions:
    r = review_candidate(bundle, output_root=W / "human", state_dir=state, selected_position_id=p["position_id"],
                         reviewer="diag human", reason="select")
    out[f"select_{p['origin']}"] = (r.status, r.errors[:1])
# correction: the unmodified positive recording (model == host == supported)
raw = (D / "examples/phase10/positive-recording.json").read_text()
r = review_candidate(bundle, output_root=W / "human", state_dir=state, selected_position_id=positions[0]["position_id"],
                     reviewer="diag human", reason="correct", corrected_raw_output=raw)
out["correction"] = (r.status, r.errors[:2])
if r.path:
    rr = RunRecord.model_validate(json.loads((Path(r.path) / "record.json").read_text())["run_record"])
    review, sel, ass, _ = reconstruct(rr)
    out["after_correction"] = {"route": review.get("route"), "review_state": review.get("review_state"),
                               "mandatory": review.get("mandatory"), "composite": ass.get("composite_state"),
                               "selected_origin": sel["origin"], "mode": json.loads((Path(r.path) / "record.json").read_text())["execution_mode"],
                               "inspect": inspect_bundle(Path(r.path)).valid}
    md = (Path(r.path) / "report.md").read_text()
    out["conflict_row"] = [l[:200] for l in md.splitlines() if l.startswith("| model/host conflicts")]
    rel = release_candidate(Path(r.path), output_root=W / "human", reviewer="diag", reason="release after human")
    out["release"] = (rel.status, rel.errors[:1])
print(json.dumps(out, indent=1, default=str))
(X / "trace2b_summary.json").write_text(json.dumps(out, indent=1, default=str))
