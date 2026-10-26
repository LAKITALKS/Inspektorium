"""Verifier re-probe of P5-F1 via the private synthetic seam (same lease/claim code as production)."""
import sys, json, shutil, hashlib
B = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
sys.path.insert(0, B + "/src"); sys.path.insert(0, B + "/tests")
from pathlib import Path
import agent_arena
import test_full_replication_contract as t
from agent_arena import full_replication_contract as frc

assert agent_arena.__file__.startswith(B), agent_arena.__file__
out = Path(sys.argv[1]); shutil.rmtree(out, ignore_errors=True); out.mkdir(parents=True)
doc = t._synthetic_document()


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()[:10] if Path(p).exists() else None


def run(d, builder):
    try:
        r = t._run_synthetic(d, doc, builder)
        return (f"RAN constructions={builder.constructions} requests={sum(p.requests for p in builder.providers)} "
                f"terminal={r['freeze']['terminal_attempts']} abort={r['batch_abort']}")
    except Exception as e:
        return f"REFUSED {type(e).__name__}: {str(e)[:80]} constructions={builder.constructions}"


raw = lambda d: d / "raw" / "haiku_raw_records.jsonl"
# A: complete run -> lease lost -> rerun
a = out / "A"; print("A1", run(a, t._ProviderBuilder()))
l1 = json.loads((a / frc.LEASE_FILENAME).read_text())["lease_fingerprint"]; pe1 = sha(a / "preflight_evidence.json"); r1 = sha(raw(a))
print("A2 lease present:", run(a, t._ProviderBuilder()))
(a / frc.LEASE_FILENAME).unlink()
print("A3 lease deleted:", run(a, t._ProviderBuilder()))
l2 = json.loads((a / frc.LEASE_FILENAME).read_text())["lease_fingerprint"]
print("   lease replaced:", l1[:8], "->", l2[:8], "| preflight_evidence replaced:", pe1 != sha(a / "preflight_evidence.json"), "| raw records bytes changed:", r1 != sha(raw(a)))
# B: aborted run (auth_error) -> lease lost -> rerun with healthy provider
b = out / "B"; print("B1", run(b, t._AuthErrorBuilder()))
print("   B1 records after abort:", len(raw(b).read_text().splitlines()))
print("B1b lease present, healthy provider:", run(b, t._ProviderBuilder()))
(b / frc.LEASE_FILENAME).unlink()
print("B2 lease deleted:", run(b, t._ProviderBuilder()))
# C: complete run -> namespace lost -> rerun
c = out / "C"; print("C1", run(c, t._ProviderBuilder())); shutil.rmtree(c)
print("C2 namespace deleted:", run(c, t._ProviderBuilder()))
# D: lease file replaced by an empty file of the same name (still blocks: existence-only check)
d = out / "D"; print("D1", run(d, t._ProviderBuilder()))
(d / frc.LEASE_FILENAME).write_text("")
print("D2 lease emptied (not deleted):", run(d, t._ProviderBuilder()))
