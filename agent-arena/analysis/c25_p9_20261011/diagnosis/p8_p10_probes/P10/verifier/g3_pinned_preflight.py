"""Pinned, revoked schema-1.0 authorization (scratch replica of the -002/-003 situation): live preflight text."""
import shutil, sys, json
from pathlib import Path
D = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new"
S = Path("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_p8_p10/P10/verifier/g3")
sys.path.insert(0, D + "/src"); sys.path.insert(0, D)
if S.exists(): shutil.rmtree(S)
S.mkdir(parents=True)
import httpx
from agent_arena import phase10_live as live
live.KNOWN_CLOSED_AUTHORIZATIONS = {}
import tests.test_phase10_live as T
from agent_arena.phase10_bundle import run_audit
pred = T._closed_predecessor(S, "pinned", auth_id="TEST-PINNED")   # 1 primary answered, then REVOKED
T._pin(pred)
task = T._task("positive")
def forbid(request): raise AssertionError("network attempted")
for key in ("test-key", ""):
    with live.LiveSession(Path(pred["directory"]), mode="live", transport=httpx.MockTransport(forbid), api_key=key) as s:
        for kind in ("primary", "counterreview"):
            prov = live.LiveAuditProvider(s, T.HAIKU, task.id, kind, T.PROFILES[T.HAIKU].prompt_versions[0 if kind == "primary" else 1])
            print(f"key={'set' if key else 'missing'} {kind}: preflight ->", prov.preflight(task))
        res = run_audit(task, live.LiveAuditProvider(s, T.HAIKU, task.id, "primary", T.P8), output_root=S / "out", review_state=S / "st")
        print(f"key={'set' if key else 'missing'} run_audit ->", res.status, res.errors[:1])
