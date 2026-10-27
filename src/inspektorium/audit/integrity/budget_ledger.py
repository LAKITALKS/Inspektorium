"""Atomic, pessimistic budget ledger shared by the audit workflow.

Extracted verbatim from the bounded-harness mission module so that the audit
workflow no longer imports the historical study harness. Reservation, settlement
and revocation semantics are unchanged.
"""

from __future__ import annotations
import json, os
from pathlib import Path

MAX_ATTEMPT_MICROUSD = 26480
MAX_TOTAL_MICROUSD = 8000000


class MissionError(RuntimeError):
    pass


def read(path):
    return json.loads(Path(path).read_text())


def atomic(path, v):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w") as f:
        f.write(json.dumps(v, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    fd = os.open(path.parent, os.O_RDONLY)
    os.fsync(fd)
    os.close(fd)


class BudgetLedger:
    """Atomic pessimistic reservation. Unknown billing is never returned to budget.

    A one-shot exclusive lease gives one owner. The ledger retains each full maximum
    even after actual token usage is known; this deliberately over-reserves. Resume
    and terminal replacement are unsupported, including after interruption.
    """

    def __init__(self, path, binding, slots, *, create=False, policy=None):
        self.path = Path(path)
        self.binding = binding
        self.slots = slots
        # Explicit policy reuses the same reservation engine; legacy serialization and
        # defaults remain unchanged. Phase9 uses zero-dollar offline reservations.
        self.policy = (
            dict(policy)
            if policy is not None
            else {
                "max_attempts": 192,
                "per_slot": 3,
                "attempt_microusd": MAX_ATTEMPT_MICROUSD,
                "total_microusd": MAX_TOTAL_MICROUSD,
            }
        )
        if set(self.policy) != {
            "max_attempts",
            "per_slot",
            "attempt_microusd",
            "total_microusd",
        } or any(type(v) is not int or v < 0 for v in self.policy.values()):
            raise MissionError("invalid ledger policy")
        if create:
            if self.path.exists():
                raise MissionError("ledger exists; no fresh identity/restart")
            self.data = {
                "binding": binding,
                "state": "ACTIVE",
                "attempts": [],
                "terminal_keys": [],
                "planned_keys": [s["slot_key"] for s in slots],
                "reserved_microusd": 0,
                "executable_remaining_microusd": self.policy["total_microusd"],
            }
            if policy is not None:
                self.data["policy"] = dict(policy)
            atomic(self.path, self.data)
        else:
            self.data = read(self.path)
        if self.data["binding"] != binding:
            raise MissionError("ledger binding mismatch")
        if self.data.get("policy") != policy:
            raise MissionError("ledger policy mismatch")

    def reserve(self, key, payload_hash, wire_hash):
        d = read(self.path)
        if d != self.data:
            raise MissionError("ledger changed outside its lease owner")
        if (
            d["state"] != "ACTIVE"
            or key not in d["planned_keys"]
            or key in d["terminal_keys"]
        ):
            raise MissionError("non-executable or terminal slot")
        position = len(d["terminal_keys"])
        if key != d["planned_keys"][position]:
            raise MissionError("frozen schedule violation")
        if (
            len(d["attempts"]) >= self.policy["max_attempts"]
            or sum(a["slot_key"] == key for a in d["attempts"])
            >= self.policy["per_slot"]
        ):
            raise MissionError("attempt cap")
        reserved = d["reserved_microusd"] + self.policy["attempt_microusd"]
        if reserved > self.policy["total_microusd"]:
            raise MissionError("dollar cap")
        a = {
            "attempt_id": f"attempt-{len(d['attempts']) + 1:03}",
            "slot_key": key,
            "payload_sha256": payload_hash,
            "wire_sha256": wire_hash,
            "reserved_microusd": self.policy["attempt_microusd"],
            "state": "RESERVED_POSSIBLY_BILLABLE",
            "usage": None,
            "confirmed_token_cost_microusd": None,
        }
        d["attempts"].append(a)
        d["reserved_microusd"] = reserved
        d["executable_remaining_microusd"] = self.policy["total_microusd"] - reserved
        atomic(self.path, d)
        self.data = d
        return a["attempt_id"]

    def observe(self, aid, **changes):
        d = read(self.path)
        if d != self.data:
            raise MissionError("external ledger modification")
        next(a for a in d["attempts"] if a["attempt_id"] == aid).update(changes)
        atomic(self.path, d)
        self.data = d

    def terminal(self, key, raw_record_sha256):
        d = read(self.path)
        if d != self.data or d["state"] != "ACTIVE" or key in d["terminal_keys"]:
            raise MissionError("terminal duplicate/state mismatch")
        if key != d["planned_keys"][len(d["terminal_keys"])]:
            raise MissionError("terminal schedule mismatch")
        if not any(a["slot_key"] == key for a in d["attempts"]):
            raise MissionError("terminal without reserved attempt")
        d["terminal_keys"].append(key)
        d.setdefault("terminal_record_hashes", {})[key] = raw_record_sha256
        atomic(self.path, d)
        self.data = d

    def revoke(self, reason):
        d = read(self.path)
        if d != self.data:
            raise MissionError("ledger externally altered before revoke")
        d.update(
            state="REVOKED", executable_remaining_microusd=0, revocation_reason=reason
        )
        atomic(self.path, d)
        self.data = d
