"""Fix-hypothesis check (in-process monkeypatch only): replay denies a never-executed review slot."""
import runpy, sys
D = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new"
sys.path.insert(0, D + "/src")
from agent_arena import phase10_live as live
orig = live.review_allowance
def patched(session, slot, *, claim=False):
    if session.mode != "live" and not session.authorization.get("review_caps") and slot.split("|")[2] != "primary" \
            and slot not in session.ledger.data["terminal_keys"]:
        return "No live review was executed for this slot; the review stays open"
    return orig(session, slot, claim=claim)
live.review_allowance = patched
sys.argv = ["probe_replay_r1.py", "repair_r1"]
runpy.run_path("probe_replay_r1.py", run_name="__main__")
