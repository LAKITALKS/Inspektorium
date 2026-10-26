"""F3: bundle made in the git checkout vs inspection under byte-identical installed copy without git.
Usage: f3_cross_install.py <make|inspect> <code_root> <out_or_bundle>"""
import json
import sys
from pathlib import Path

mode, code_root, target = sys.argv[1:4]
sys.path.insert(0, code_root)
import agent_arena  # noqa: E402
assert agent_arena.__file__.startswith(code_root), agent_arena.__file__
from agent_arena.phase10_bundle import inspect_bundle, release_candidate, run_audit  # noqa: E402
from agent_arena.phase9_runtime import OfflineReviewProvider  # noqa: E402
from agent_arena.task_loader import load_task  # noqa: E402

EX = Path("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new/examples/phase10")
if mode == "make":
    task = load_task(EX / "positive-task.json")
    res = run_audit(task, OfflineReviewProvider((EX / "positive-recording.json").read_text()), output_root=Path(target) / "cand")
    rel = release_candidate(Path(res.path), output_root=Path(target) / "rel", reviewer="verifier", reason="F3 probe")
    for p in (res.path, rel.path):
        code = json.loads((Path(p) / "record.json").read_text())["provenance"]["code"]
        print("made", json.loads((Path(p) / "record.json").read_text())["status"], p.split("/")[-2],
              "claim:", code["verified_source_commit"], "| fingerprint:", code["code_fingerprint"][:16])
else:
    for p in sorted(Path(target).glob("*/*")):
        v = inspect_bundle(p)
        print("inspect", p.parent.name, v.valid, v.status, [e[:150] for e in v.errors[:1]])
