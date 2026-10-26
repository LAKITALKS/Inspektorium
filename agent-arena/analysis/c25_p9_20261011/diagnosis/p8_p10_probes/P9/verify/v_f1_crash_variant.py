"""F1 fix-scope probe: a schema-1.1 successor (throwaway, pinned throwaway predecessor, exactly as in
tests/test_phase10_live.py) whose live counterreview is interrupted after the live reservation and before
its capture exists (process kill). Then: live resume and replay. Everything under scratch; MockTransport;
api_key='test-key'; KNOWN_CLOSED_AUTHORIZATIONS starts empty and only gets the throwaway pin."""
import json
import shutil
import sys
from pathlib import Path

D = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new"
sys.path[:0] = [D + "/src", D]
OUT = Path("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_p8_p10/P9/verify/f1_crash")
assert str(OUT).startswith("/private/tmp/")
shutil.rmtree(OUT, ignore_errors=True)
OUT.mkdir(parents=True)

from agent_arena import phase10_live as live  # noqa: E402
live.KNOWN_CLOSED_AUTHORIZATIONS = {}
import tests.test_phase10_live as T  # noqa: E402
import agent_arena.phase10_bundle as B  # noqa: E402
from agent_arena.providers.anthropic_live import PROFILES  # noqa: E402

H3 = "claude-haiku-5-5@3"
R2 = PROFILES[H3].prompt_versions[0]
task, raw = T._conflict_task("aa-verify-crash")
pred = T._closed_predecessor(OUT, "pred")
assert pred["directory"].startswith("/private/tmp/")
T._pin(pred)
directory = T._successor(OUT, [task], [pred], budget=1_000_000, profiles=(H3,))
assert str(directory).startswith("/private/tmp/")


class Killed(BaseException):
    pass


class KillTransport(T.Transport):
    """Second request: a real process kill (BaseException) while the review request is in flight."""
    def __call__(self, request):
        if len(self.requests) == 1:
            self.requests.append({"killed": True})
            raise Killed("process killed while the review request is in flight")
        return super().__call__(request)


transport = KillTransport(T.message(raw, request_id="req_p"))
try:
    with T._session(directory, transport) as session:
        prov = live.LiveAuditProvider(session, H3, task.id, "primary", R2)
        first = B.run_audit(task, prov, output_root=OUT / "live_out", review_state=directory / "phase9-state")
        print("first live run returned (no kill):", first.status, [e[:120] for e in first.errors])
except Killed as exc:
    print("crash:", exc)
led = json.loads((directory / "ledger.json").read_text())
print("live ledger:", [(a["slot_key"].split("|")[2], a["state"]) for a in led["attempts"]],
      "claims:", [c.split("|")[2] for c in led.get("review_cap_claims", [])], "terminal:", [k.split("|")[2] for k in led["terminal_keys"]])
side = next(p for p in (directory / "phase9-state" / H3 / "phase9").glob("p9case*.json") if not p.name.endswith(".ledger.json"))
print("P9 sidecar attempts:", [(a["kind"], a["status"]) for a in json.loads(side.read_text())["metadata"]["phase9"]["attempts"]])

# Supported resumption 1: rerun live (reconcile, then the primary slot is already answered).
with T._session(directory, T.Transport()) as session:
    print("live reopen unresolved:", session.unresolved)
    prov = live.LiveAuditProvider(session, H3, task.id, "primary", R2)
    res = B.run_audit(task, prov, output_root=OUT / "live_out2", review_state=directory / "phase9-state")
print("LIVE RERUN:", res.status, [e[:120] for e in res.errors])

# Supported resumption 2: replay.
captured = {}
orig = B.create_candidate


def cap(record, **kw):
    captured["r"] = record
    return orig(record, **kw)


B.create_candidate = cap
with live.LiveSession(directory, mode="replay") as session:
    prov = live.ReplayProvider(session, H3, task.id, "primary", R2)
    rep = B.run_audit(task, prov, output_root=OUT / "replay_out", review_state=OUT / "replay_state")
print("REPLAY:", rep.status, [e[:200] for e in rep.errors])
p9 = captured["r"].metadata["phase9"]
print("  replay P9:", [(a["kind"], a["status"], a["reason"][:70]) for a in p9["attempts"]], p9["route"])
print("  ledger unchanged by replay:", json.loads((directory / "ledger.json").read_text()) == led)
