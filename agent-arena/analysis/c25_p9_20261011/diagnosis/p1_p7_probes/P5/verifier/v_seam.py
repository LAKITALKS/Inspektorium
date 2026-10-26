"""Docstring check: are the private seams of _run_registered_condition really 'accepted solely with synthetic
authorization'? Production mode (_synthetic_test=False) + injected _plan_resolver returning an in-memory AUTH_REAL
copy of the untouched NOT_AUTHORIZED Phase-5A paired plan. A sentinel source inspector stops the run before
QA/credentials/provider; nothing is written."""
import sys, copy
B = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
sys.path.insert(0, B + "/src")
from pathlib import Path
import agent_arena
from agent_arena import condition_contract as cc
from agent_arena.phase7a_real_run import _run_registered_condition
assert agent_arena.__file__.startswith(B)
root = Path(B)
real = cc.resolve_registered_plan(cc.PAIRED_PLAN_ID, root)
print("tracked paired plan:", real["authorization"]["status"], "| production_authorization_errors:", cc.production_authorization_errors(real, root)[:1])
forged = copy.deepcopy(real)
forged["authorization"] = {"status": cc.AUTH_REAL, "specification_fingerprint": real["specification"]["specification_fingerprint"],
                           "authorization_source": "tracked_governance_approval",
                           "authorized_budget_calls": real["specification"]["expected_calls_total"]}
print("forged in-memory doc production_authorization_errors:", cc.production_authorization_errors(forged, root))


class Reached(Exception):
    pass


def sentinel(_root):
    raise Reached("source inspection reached: authorization gate accepted injected AUTH_REAL document")


arm_id = real["specification"]["arms"][0]["arm_id"]
try:
    _run_registered_condition(cc.PAIRED_PLAN_ID, arm_id, "haiku", repo_root=B, _synthetic_test=False,
                              _plan_resolver=lambda _p, _r: copy.deepcopy(forged), _source_inspector=sentinel,
                              _credential_checker=lambda: {"available": False}, _provider_builder=lambda _k: (_ for _ in ()).throw(RuntimeError("provider")))
except Reached as e:
    print("RESULT:", e)
except Exception as e:
    print("RESULT: refused", type(e).__name__, str(e)[:120])
