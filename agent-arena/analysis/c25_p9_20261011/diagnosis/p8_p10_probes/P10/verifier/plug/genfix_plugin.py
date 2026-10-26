"""In-process fix hypothesis (verifier only): in replay, a review slot without a completed live capture is a
recorded denial (open review) unless live allowed it and never reserved (N-R3 unsent replay keeps its path)."""
from agent_arena import phase10_live as live

_orig = live.review_allowance


def review_allowance(session, slot, *, claim=False):
    if session.mode != "live" and slot.split("|")[2] != "primary":
        d = session.ledger.data
        attempts = [a for a in d["attempts"] if a["slot_key"] == slot]
        if slot not in d["terminal_keys"] and (attempts or not session.authorization.get("review_caps")):
            return "No completed live review exists for this slot; the review stays open"
    return _orig(session, slot, claim=claim)


live.review_allowance = review_allowance
