"""Close the retest authorization -004 after the run (also after PARTIAL or BLOCKED), as -003 was closed.

Usage (repository root, immediately after the runner has ended; no model call, no key needed):
  .venv/bin/python analysis/c25_p9_20261011/live_retest/scripts/close_retest.py
Direct ledger revoke with an ORDER_COMPLETE reason under the lease; unresolved reservations stay bound; an
already REVOKED ledger counts as closed and is not rewritten. After expires_at no live session opens, so an
ACTIVE ledger is then revoked under the lease file without a live session. While a live process still holds
the lease nothing is written. evidence/closure.json is written once; later checks are appended to
evidence/closure_checks.jsonl.
"""
import fcntl
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from agent_arena import phase10_live as live

RETEST = Path("analysis/c25_p9_20261011/live_retest")
EVIDENCE = RETEST / "evidence"
CLAIM = Path("analysis/live_smoke_20261011/repair_r1/successor_claim.json")
REASON = ("ORDER_COMPLETE: C25/P9 live retest under the order of 11.10.2026 finished; the remaining budget is not "
          "carried over and no further execution is authorized. Replay of the captures stays possible.")
LEASE_HELD = "a live process still holds the lease of -004; wait until it has ended; nothing was written"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def revoke_live():
    try:
        session = live.LiveSession(RETEST, mode="live")
    except ValueError as exc:
        if "Another process holds" in str(exc):
            sys.exit(LEASE_HELD)
        raise
    # No ledger yet (nothing was run): opening the live session creates it (and the successor claim) and
    # the revoke below leaves no executable remainder. An ACTIVE ledger is revoked the same way.
    with session:
        unresolved = list(session.unresolved)
        if session.ledger.data["state"] != "ACTIVE":
            return f"already {session.ledger.data['state']}"
        session.ledger.revoke(REASON + (f" Unresolved reservations kept bound: {unresolved}." if unresolved else ""))
        return "revoked"


def revoke_after_expiry():
    lease = (RETEST / ".live-lease").open("a+")
    try:
        fcntl.flock(lease.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        lease.close()
        sys.exit(LEASE_HELD)
    try:
        with live.LiveSession(RETEST, mode="replay") as session:
            unresolved = [a["attempt_id"] for a in session.ledger.data["attempts"]
                          if a["state"] == "RESERVED_POSSIBLY_BILLABLE"]
            session.ledger.revoke(REASON + " Closed after expires_at under the lease file." +
                                  (f" Unresolved reservations kept bound: {unresolved}." if unresolved else ""))
        return "revoked after expiry"
    finally:
        fcntl.flock(lease.fileno(), fcntl.LOCK_UN)
        lease.close()


def main():
    path = RETEST / "ledger.json"
    authorization = json.loads((RETEST / "authorization.json").read_text())
    before = json.loads(path.read_text())["state"] if path.exists() else None
    expired = None  # decided by the product's own live check, not by a separate clock
    if before not in (None, "ACTIVE"):
        action = f"already {before}"
    else:
        try:
            action = revoke_live()
            expired = False
        except ValueError as exc:
            if "authorization expired" not in str(exc):
                raise
            expired = True
            action = (revoke_after_expiry() if before == "ACTIVE" else
                      "expired without a ledger: nothing ran, and no live session can open any more")
    data = json.loads(path.read_text()) if path.exists() else {}
    attempts = data.get("attempts", [])
    closure = {
        "authorization_id": authorization["authorization_id"], "checked_at": datetime.now(timezone.utc).isoformat(),
        "action": action, "authorization_expired": expired, "ledger_state": data.get("state"),
        "revocation_reason": data.get("revocation_reason"),
        "executable_remaining_microusd": data.get("executable_remaining_microusd"),
        "reserved_or_confirmed_microusd": data.get("reserved_microusd"), "attempts": len(attempts),
        "technical_retries": sum(1 for a in attempts if a.get("retry_of")),
        "unresolved_attempts": [a["attempt_id"] for a in attempts if a["state"] == "RESERVED_POSSIBLY_BILLABLE"],
        "unknown_billing_attempts": [a["attempt_id"] for a in attempts if a.get("billing") == "unknown_reservation_kept"],
        "ledger_sha256": sha(path), "successor_claim": {"path": str(CLAIM), "sha256": sha(CLAIM)},
        "replay_possible": path.exists()}
    EVIDENCE.mkdir(exist_ok=True)
    text = json.dumps(closure, indent=2, ensure_ascii=False) + "\n"
    try:
        fd = os.open(EVIDENCE / "closure.json", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        with os.fdopen(fd, "w") as handle:
            handle.write(text)
    except FileExistsError:
        with (EVIDENCE / "closure_checks.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(closure, ensure_ascii=False) + "\n")
    print(text)
    closed = closure["ledger_state"] == "REVOKED" and closure["executable_remaining_microusd"] == 0
    if not closed and not (expired and not path.exists()):
        sys.exit("authorization -004 is NOT closed")
    return 0


if __name__ == "__main__":
    if not (Path.cwd() / ".git").exists() or not RETEST.exists():
        sys.exit("run from the repository root")
    sys.exit(main())
