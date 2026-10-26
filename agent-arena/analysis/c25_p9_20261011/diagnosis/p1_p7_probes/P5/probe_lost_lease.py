"""Counter-case: one-shot lease is the only second-invocation guard while the tracked plan is authorized."""
import sys, json, shutil
B="__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
sys.path.insert(0, B+"/src"); sys.path.insert(0, B+"/tests")
from pathlib import Path
import test_full_replication_contract as t
from agent_arena import full_replication_contract as frc
from agent_arena.phase7a_real_run import ConditionAuthorizationError
out = Path(sys.argv[1]); shutil.rmtree(out, ignore_errors=True); out.mkdir(parents=True)
doc = t._synthetic_document()

def run(d, builder):
    try:
        r = t._run_synthetic(d, doc, builder)
        reqs = sum(p.requests for p in builder.providers)
        return f"RAN constructions={builder.constructions} provider_requests={reqs} terminal={r['freeze']['terminal_attempts']} abort={r['batch_abort']}"
    except Exception as e:
        return f"REFUSED {type(e).__name__}: {str(e)[:100]} constructions={builder.constructions}"

# Case A: complete run, lease file lost, rerun
a = out/"A"; print("A1", run(a, t._ProviderBuilder()))
lease_a1 = json.loads((a/frc.LEASE_FILENAME).read_text())["lease_fingerprint"]
print("A2 (lease present)", run(a, t._ProviderBuilder()))
(a/frc.LEASE_FILENAME).unlink()
print("A3 (lease deleted)", run(a, t._ProviderBuilder()))
ev = json.loads((a/"execution_evidence.json").read_text())
print("   execution_evidence lease fp now", ev["one_shot_lease"]["lease_fingerprint"][:12], "original", lease_a1[:12], "-> overwritten:", ev["one_shot_lease"]["lease_fingerprint"]!=lease_a1)

# Case B: aborted (auth_error) run leaves PARTIAL_INCOMPLETE; lease lost; rerun with healthy provider
b = out/"B"; print("B1", run(b, t._AuthErrorBuilder()))
(b/frc.LEASE_FILENAME).unlink()
print("B2 (lease deleted, second guarded pass)", run(b, t._ProviderBuilder()))

# Case C: whole run namespace lost while plan still authorized
c = out/"C"; print("C1", run(c, t._ProviderBuilder()))
shutil.rmtree(c)
print("C2 (namespace deleted)", run(c, t._ProviderBuilder()))
