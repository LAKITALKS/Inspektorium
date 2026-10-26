"""(1) F6 on schema 1.1: crash after the terminal primary, before the review claim -> replay status.
(2) Row fix part 2 alone: new_generation=False on the ReplayProvider denial, without the review_allowance change,
    on a faithful copy of the tracked -003 history (one REVIEW_RECOMMENDED slot)."""
import json
import json as _json
import shutil
import sys
from pathlib import Path

D = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new"
S = Path("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_p8_p10/P10/verifier/g2")
sys.path.insert(0, D + "/src")
sys.path.insert(0, D)
if S.exists():
    shutil.rmtree(S)
S.mkdir(parents=True)
import httpx  # noqa: E402
from agent_arena import phase10_live as live  # noqa: E402
REAL_PINS = dict(live.KNOWN_CLOSED_AUTHORIZATIONS)
live.KNOWN_CLOSED_AUTHORIZATIONS = {}
import tests.test_phase10_live as T  # noqa: E402
from agent_arena.phase10_bundle import inspect_bundle, run_audit  # noqa: E402
from agent_arena.providers.anthropic_live import PROFILES  # noqa: E402
from agent_arena.task_loader import load_task  # noqa: E402

H3 = "claude-haiku-5-5@3"
R2 = PROFILES[H3].prompt_versions[0]


class Crash(BaseException):
    pass


# ---- (1) F6
task, raw = T._conflict_task("aa-g2-f6")
pred = T._closed_predecessor(S, "pred")
T._pin(pred)
succ = T._successor(S, [task], [pred], budget=2_000_000 - pred["consumed_microusd"], profiles=(H3,))
orig_claim = live.LiveBudgetLedger.claim_review


def crash_claim(self, key):
    raise Crash("killed between terminal primary and review claim")


live.LiveBudgetLedger.claim_review = crash_claim
tr = T.Transport(T.message(raw, request_id="req_p"))
try:
    with T._session(succ, tr) as session:
        run_audit(task, live.LiveAuditProvider(session, H3, task.id, "primary", R2), output_root=S / "out",
                  review_state=succ / "phase9-state")
except Crash as exc:
    print("(1) interrupted:", exc, "| requests:", len(tr.requests))
live.LiveBudgetLedger.claim_review = orig_claim
ledger = json.loads((succ / "ledger.json").read_text())
print("(1) ledger:", [(a["slot_key"].split("|")[2], a["state"]) for a in ledger["attempts"]], "claims:",
      ledger.get("review_cap_claims"))
with live.LiveSession(succ, mode="replay") as session:
    res = run_audit(task, live.ReplayProvider(session, H3, task.id, "primary", R2), output_root=S / "replay",
                    review_state=S / "rs1")
p9 = json.loads((Path(res.path) / "record.json").read_text())["run_record"]["metadata"]["phase9"] if res.path else {}
print("(1) F6 replay (1.1):", res.status, p9.get("route"), [(a["kind"], a["status"], a["reason"][:70]) for a in p9.get("attempts", [])],
      "inspect:", inspect_bundle(Path(res.path)).valid if res.path else None)

# ---- (2) fix part 2 alone on the faithful -003 copy
src = Path(D) / "analysis/live_smoke_20261011/repair_r1"
copy = S / "r1"
copy.mkdir()
for name in ("authorization.json", "ledger.json"):
    shutil.copy2(src / name, copy / name)
shutil.copytree(src / "captures", copy / "captures")
real = _json.loads((src / "authorization.json").read_bytes())["canonical_directory"]


class Shim:
    def __getattr__(self, name):
        return getattr(_json, name)

    def loads(self, raw_, *a, **k):
        value = _json.loads(raw_, *a, **k)
        if isinstance(value, dict) and value.get("canonical_directory") == real:
            value = dict(value, canonical_directory=str(copy.resolve()))
        return value


live.json = Shim()
live.KNOWN_CLOSED_AUTHORIZATIONS = REAL_PINS  # replay ignores pins; restored for realism
orig_denied = live.ReplayProvider._denied


def denied_with_flag(self, task_, system_prompt, user, reason, attempts, current, extra=None):
    if current == "offline_replay":
        extra = {"new_generation": False, **(extra or {})}
    return orig_denied(self, task_, system_prompt, user, reason, attempts, current, extra)


live.ReplayProvider._denied = denied_with_flag
httpx.Client.send = lambda *a, **k: (_ for _ in ()).throw(AssertionError("network attempted"))
t02 = load_task(Path(D) / "analysis/live_smoke_20261011/live_run/tasks/LS-02.json")
profile = "claude-haiku-5-5@2"
with live.LiveSession(copy, mode="replay") as session:
    res = run_audit(t02, live.ReplayProvider(session, profile, t02.id, "primary", PROFILES[profile].prompt_versions[0]),
                    output_root=S / "r1_out", review_state=S / "r1_state")
print("(2) -003 LS-02 haiku with new_generation=False only:", res.status, [e[:230] for e in res.errors[:1]])
