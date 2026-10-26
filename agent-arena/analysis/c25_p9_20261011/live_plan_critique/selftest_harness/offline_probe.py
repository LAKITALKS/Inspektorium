"""Offline route probe of the synthetic LR recordings on the dry-run task files (read-only), no provider."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import httpx  # noqa: E402


def _blocked(*_a, **_k):
    raise AssertionError("network")


httpx.HTTPTransport.handle_request = _blocked
import recordings  # noqa: E402
from agent_arena.phase10_bundle import run_audit  # noqa: E402
from agent_arena.phase9_runtime import OfflineReviewProvider  # noqa: E402
from agent_arena.task_loader import load_task  # noqa: E402

SP = Path("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/"
          "cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad")
OUT = SP / "critic_live2/operational/offline_probe"
for case in ("LR-01", "LR-02", "LR-03"):
    task = load_task(SP / "retest_dryrun2/tasks" / f"{case}.json")
    spec = recordings.LR[case]
    assert spec["prompt"] == task.prompt, case
    assert spec["quote"] in task.context, case
    for variant in ("supported", "unsupported_agreed", "conflict_unknown_host", "conflict2"):
        result = run_audit(task, OfflineReviewProvider(recordings.build(case, variant)), output_root=OUT / case / variant)
        row = {"case": case, "variant": variant, "status": result.status, "errors": result.errors[:2]}
        if result.path:
            record = json.loads((Path(result.path) / "record.json").read_text())
            p8 = record["run_record"]["results"][0]["agent_result"].get("phase8") or {}
            p9 = record["run_record"]["metadata"].get("phase9") or {}
            row.update(model=p8.get("model_composite_state"), host=p8.get("host_composite_state"),
                       eff=p8.get("composite_state"), tech=p8.get("technical_status"), route=p9.get("route"),
                       mandatory=p9.get("mandatory"),
                       triggers=sorted({t["code"] for t in p9.get("triggers", [])}),
                       label=(p8.get("original_model_label"), p8.get("derived_label")),
                       host_reasons=[p.get("host_reasons") for p in p8.get("propositions", [])])
        print(json.dumps(row)[:700])
