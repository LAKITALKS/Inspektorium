"""Which step refuses the production 5B path at HEAD? No provider can be built (stubs), no writes expected."""
import sys
B = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
sys.path.insert(0, B + "/src")
from pathlib import Path
from agent_arena import condition_contract as cc, full_replication_contract as frc
from agent_arena.phase7a_real_run import _run_registered_condition

calls = {"source": 0, "cred": 0, "provider": 0}


def src(_root):
    calls["source"] += 1
    raise RuntimeError("source inspector reached (unexpected)")


def cred():
    calls["cred"] += 1
    return {"available": False, "reason": "verifier stub"}


def prov(_k):
    calls["provider"] += 1
    raise RuntimeError("provider construction reached (unexpected)")


for prof in (frc.HAIKU, frc.SONNET):
    lease = Path(B) / prof.artifact_namespace / prof.model_key / frc.LEASE_FILENAME
    doc = cc.resolve_registered_plan(prof.plan_id, Path(B))
    try:
        _run_registered_condition(prof.plan_id, prof.arm_id, prof.model_key, repo_root=B,
                                  _source_inspector=src, _credential_checker=cred, _provider_builder=prov)
        print(prof.model_key, "NO REFUSAL (unexpected)")
    except Exception as e:
        print(prof.model_key, "refused:", type(e).__name__, str(e)[:110])
    print("   lease tracked+present:", lease.exists(), "| production_authorization_errors:", cc.production_authorization_errors(doc, Path(B))[:2])
print("stub calls:", calls)
