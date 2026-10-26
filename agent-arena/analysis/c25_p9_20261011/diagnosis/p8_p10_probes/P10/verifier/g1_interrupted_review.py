"""Gap probe G1: schema-1.1 successor (throwaway, scratch only), material conflict -> live counterreview is
interrupted after its ledger claim + reservation and before any capture (hard crash, BaseException).
Then: (A) live resume of the case, (B) replay with a fresh review state (as the CLI does), (C) inspect what the
contract (addendum section 5 / K6 / K7) asks: an open mandatory review -> REVIEW_REQUIRED, human adjudication.
Transport double only; api_key='test-key'; KNOWN_CLOSED_AUTHORIZATIONS replaced by {} before anything else.
"""
import hashlib
import json
import shutil
import sys
from pathlib import Path

D = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new"
S = Path("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_p8_p10/P10/verifier/g1")
sys.path.insert(0, D + "/src")
sys.path.insert(0, D)
if S.exists():
    shutil.rmtree(S)
S.mkdir(parents=True)
import httpx  # noqa: E402
from agent_arena import phase10_live as live  # noqa: E402
assert live.__file__.startswith(D)
live.KNOWN_CLOSED_AUTHORIZATIONS = {}
import tests.test_phase10_live as T  # noqa: E402
T.live.KNOWN_CLOSED_AUTHORIZATIONS = live.KNOWN_CLOSED_AUTHORIZATIONS  # same module object
from agent_arena.phase10_bundle import inspect_bundle, run_audit  # noqa: E402
from agent_arena.providers.anthropic_live import PROFILES  # noqa: E402

H3 = "claude-haiku-5-5@3"
R2 = PROFILES[H3].prompt_versions[0]


class Crash(BaseException):
    pass


class CrashingTransport(T.Transport):
    def __call__(self, request):
        self.requests.append({"body": json.loads(request.content)})
        item = self.responses.pop(0)
        if item == "CRASH":
            raise Crash("process killed while the review request was in flight")
        return item


def forbid_all(request):
    raise AssertionError("network attempted")


task, raw = T._conflict_task("aa-g1-interrupt")
pred = T._closed_predecessor(S, "pred")  # throwaway closed predecessor under scratch
T._pin(pred)
assert all(not str(v).startswith("/Users/") for p in [pred] for v in p.values()), pred
succ = T._successor(S, [task], [pred], budget=2_000_000 - pred["consumed_microusd"], profiles=(H3,))
auth = json.loads((succ / "authorization.json").read_text())
assert auth["canonical_directory"].startswith(str(S)) and all(p["directory"].startswith(str(S)) for p in auth["predecessors"])

tr = CrashingTransport(T.message(raw, request_id="req_p"), "CRASH")
try:
    with T._session(succ, tr) as session:
        prov = live.LiveAuditProvider(session, H3, task.id, "primary", R2)
        run_audit(task, prov, output_root=S / "out", review_state=succ / "phase9-state")
    print("no crash (unexpected)")
except Crash as exc:
    print("live run interrupted:", exc, "| requests sent:", len(tr.requests))
ledger = json.loads((succ / "ledger.json").read_text())
print("ledger after crash:", [(a["slot_key"].split("|")[2], a["state"]) for a in ledger["attempts"]],
      "terminal:", [k.split("|")[2] for k in ledger["terminal_keys"]], "claims:", ledger.get("review_cap_claims"))

# (A) live resume of the same case: no request may leave
with live.LiveSession(succ, mode="live", transport=httpx.MockTransport(forbid_all), api_key="test-key") as session:
    print("resume unresolved:", session.unresolved)
    prov = live.LiveAuditProvider(session, H3, task.id, "primary", R2)
    res = run_audit(task, prov, output_root=S / "out_resume", review_state=succ / "phase9-state")
    print("(A) live resume:", res.status, res.errors[:1], "path:", res.path)

# (B) replay with a fresh review state, exactly like `audit run --replay` (replay-state/<uuid4>)
before = hashlib.sha256((succ / "ledger.json").read_bytes()).hexdigest()
with live.LiveSession(succ, mode="replay") as session:
    prov = live.ReplayProvider(session, H3, task.id, "primary", R2)
    res = run_audit(task, prov, output_root=S / "out_replay", review_state=S / "replay-state-fresh")
    print("(B) replay:", res.status, [e[:260] for e in res.errors[:1]], "path:", res.path)
print("ledger unchanged by replay:", before == hashlib.sha256((succ / "ledger.json").read_bytes()).hexdigest())
case = next((S / "replay-state-fresh").rglob("p9case*.json"))
p9 = json.loads(case.read_text())["metadata"]["phase9"]
print("(B) replay P9 state: route", p9["route"], "mandatory", p9["mandatory"],
      [(a["kind"], a["status"], a.get("reason", "")[:80]) for a in p9["attempts"]])

# (C) replay reusing the live phase9-state (holds the 'begun' attempt)
try:
    with live.LiveSession(succ, mode="replay") as session:
        prov = live.ReplayProvider(session, H3, task.id, "primary", R2)
        res = run_audit(task, prov, output_root=S / "out_replay2", review_state=succ / "phase9-state")
        print("(C) replay on live P9 state:", res.status, [e[:200] for e in res.errors[:1]])
except Exception as exc:
    print("(C) replay on live P9 state raised:", type(exc).__name__, str(exc)[:200])
print("bundles written anywhere:", sorted(p.name for d in ("out", "out_resume", "out_replay", "out_replay2")
                                         if (S / d).exists() for p in (S / d).iterdir()))
