"""AA-P10-LIVE/1.0: authorization, live budget ledger, live/replay providers, provenance checks.

Every provider call reserves its conservative maximum exposure in a durable ledger before the
request leaves the process. Raw responses are persisted before interpretation. Recorded hashes
and identities are integrity checks; they do not authenticate a person or the provider.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from inspektorium.audit.budget_ledger import BudgetLedger, MissionError, atomic, read
from inspektorium.audit.providers import BaseProvider
from inspektorium.audit.providers.anthropic_live import (
    CONTRACT_R2_PROMPT_BINDING, EVIDENCE_SCHEMA, LIVE_ENDPOINT, MESSAGES_URL, PROFILES, TRANSIENT_ERRORS,
    USER_MESSAGE_VERSION,
    LiveModelResponse, build_user_message, canonical_json, cost_microusd, input_token_bound,
    max_exposure_microusd, response_from_capture, send_request, sha256_text,
)
from inspektorium.audit.schemas import Task

ADDENDUM = "AA-P10-LIVE/1.0"
AUTH_SCHEMA = "aa-p10-live-authorization/1.0"
# Successor schema: verified binding to every closed predecessor ledger and per-profile review caps.
AUTH_SCHEMA_SUCCESSOR = "aa-p10-live-authorization/1.1"
LEDGER_SCHEMA = "aa-p10-live-ledger/1.0"
CAPTURE_SCHEMA = "aa-p10-live-capture/1.0"
KINDS = ("primary", "counterreview", "stability")
CEILING_TOTAL_MICROUSD = 2_000_000
CEILING_ATTEMPTS = 40
CEILING_RETRIES = 4
LIVE_MODES = ("live_generation", "offline_replay_of_live")
# Closed live history, pinned by the SHA-256 of each closed ledger and of its authorization file
# (which fixes its canonical directory). While it is non-empty, a new live budget must be a schema-1.1
# successor that lists every entry with exactly these bytes; a pinned id never opens a fresh ledger.
KNOWN_CLOSED_AUTHORIZATIONS = {
    "AA-P10-LIVE-SMOKE-20261011-002": {
        "ledger_sha256": "e6ef0f5aff3b6bdd3c841fc0a5982449a83eecac004f73e42f9a19a66b0c64b5",
        "authorization_sha256": "a331a4cb55cbbc83c155d7ad7abc978503cb6aab3e25880e0af4db39cd115824",
    },
    "AA-P10-LIVE-SMOKE-20261011-003": {
        "ledger_sha256": "124ffab09ad94b9c751b50fe2888e48a2e585d41f16a6e21d2062d99e69497da",
        "authorization_sha256": "b93edacd76b3726024494e7f493fb67896481c413ca38459c0bb739bba6357ae",
    },
}
# Written once (O_EXCL) into the directory of the latest predecessor when a successor opens its
# fresh ledger: a predecessor carries at most one successor, so no parallel budget can exist.
SUCCESSOR_CLAIM = "successor_claim.json"
SUCCESSOR_CLAIM_SCHEMA = "aa-p10-live-successor-claim/1.0"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def task_sha256(task: Task) -> str:
    return sha256_text(canonical_json(task.model_dump(mode="json")))


def slot_key(task_id: str, profile_id: str, kind: str) -> str:
    if kind not in KINDS:
        raise ValueError("Unknown live slot kind")
    return f"{task_id}|{profile_id}|{kind}"


# ---------------------------------------------------------------------------
# Authorization
# ---------------------------------------------------------------------------

def load_authorization(directory: Path, *, now: datetime | None = None, mode: str = "live") -> tuple[dict, str]:
    """Validate the work-order-bound authorization; any defect blocks before sending."""
    if mode not in {"live", "replay"}:
        raise ValueError("Authorization mode must be live or replay")
    path = Path(directory) / "authorization.json"
    raw = path.read_bytes()
    auth = json.loads(raw)
    errors = []
    expected = {"schema", "authorization_id", "work_order", "issued_at", "expires_at", "status",
                "canonical_directory", "endpoint", "total_budget_microusd", "max_generation_attempts",
                "max_technical_retries", "max_attempts_per_request", "per_call_ceiling_microusd",
                "allowed_profiles", "task_bindings", "slots", "supersedes"}
    successor = isinstance(auth, dict) and auth.get("schema") == AUTH_SCHEMA_SUCCESSOR
    if successor:
        expected = expected | {"predecessors", "review_caps"}
    if not isinstance(auth, dict) or set(auth) != expected:
        raise ValueError("Live authorization is partial or has unknown fields")
    if auth["schema"] not in {AUTH_SCHEMA, AUTH_SCHEMA_SUCCESSOR}:
        errors.append("unsupported authorization schema")
    if auth["status"] != "ACTIVE":
        errors.append("authorization is not ACTIVE")
    if mode == "live" and auth["canonical_directory"] != str(Path(directory).resolve()):
        # A copied authorization would otherwise open a second, fresh ledger and multiply the cap.
        # Replay never generates and never writes the ledger, so recorded live answers stay
        # reviewable from any clone or copy (Package B, K1); the ledger binding still applies.
        errors.append("authorization is bound to another directory; copies are not executable")
    if auth["endpoint"] != LIVE_ENDPOINT:
        errors.append("authorization endpoint is not the direct Anthropic API")
    if type(auth["total_budget_microusd"]) is not int or not 0 < auth["total_budget_microusd"] <= CEILING_TOTAL_MICROUSD:
        errors.append("total budget outside the AA-P10-LIVE/1.0 ceiling")
    if type(auth["max_generation_attempts"]) is not int or not 0 < auth["max_generation_attempts"] <= CEILING_ATTEMPTS:
        errors.append("attempt limit outside the ceiling")
    if type(auth["max_technical_retries"]) is not int or not 0 <= auth["max_technical_retries"] <= CEILING_RETRIES:
        errors.append("retry limit outside the ceiling")
    if auth["max_attempts_per_request"] != 2:
        errors.append("exactly one technical retry per failed request is the registered policy")
    ceiling = auth["per_call_ceiling_microusd"]
    if type(ceiling) is not int or not 0 < ceiling <= auth["total_budget_microusd"]:
        errors.append("invalid per-call ceiling")
    profiles = auth["allowed_profiles"]
    if not isinstance(profiles, dict) or not profiles:
        errors.append("no allowed profiles")
    else:
        for profile_id, fingerprint in profiles.items():
            if profile_id not in PROFILES or PROFILES[profile_id].fingerprint() != fingerprint:
                errors.append(f"profile {profile_id} is not the registered configuration revision")
    tasks = auth["task_bindings"]
    if not isinstance(tasks, dict) or not tasks or not all(
            isinstance(k, str) and isinstance(v, str) and len(v) == 64 for k, v in tasks.items()):
        errors.append("task bindings missing or malformed")
    slots = auth["slots"]
    if not isinstance(slots, list) or len(set(slots)) != len(slots) or not slots:
        errors.append("slot list missing or duplicated")
    else:
        for slot in slots:
            parts = slot.split("|") if isinstance(slot, str) else []
            if len(parts) != 3 or parts[0] not in (tasks or {}) or parts[1] not in (profiles or {}) or parts[2] not in KINDS:
                errors.append(f"slot outside the authorization: {slot}")
    if successor:
        errors.extend(_successor_errors(auth, live=mode == "live", fingerprint=_sha_bytes(raw)))
    elif mode == "live" and KNOWN_CLOSED_AUTHORIZATIONS:
        # Schema 1.0 has no predecessor binding; accepting it would open a budget outside the
        # cumulative ceilings. It stays valid for replay. A pinned closed authorization opens live only
        # as itself (unchanged file, existing closed ledger), so it can never get a fresh ledger.
        pinned = KNOWN_CLOSED_AUTHORIZATIONS.get(auth.get("authorization_id"))
        ledger_path = Path(directory) / "ledger.json"
        if pinned is None:
            errors.append("a new live budget must be a schema-1.1 successor bound to the closed live history")
        elif (_sha_bytes(raw) != pinned["authorization_sha256"] or not ledger_path.exists()
              or _sha_bytes(ledger_path.read_bytes()) != pinned["ledger_sha256"]):
            errors.append("a pinned closed authorization opens only with its unchanged file and closed ledger")
    if mode == "replay" and auth.get("authorization_id") in KNOWN_CLOSED_AUTHORIZATIONS:
        # Replay is location-free (K1), so the pinned history is bound by bytes instead (Package B, BF3).
        pinned = KNOWN_CLOSED_AUTHORIZATIONS[auth["authorization_id"]]
        ledger_path = Path(directory) / "ledger.json"
        if (_sha_bytes(raw) != pinned["authorization_sha256"] or not ledger_path.exists()
                or _sha_bytes(ledger_path.read_bytes()) != pinned["ledger_sha256"]):
            errors.append("a pinned closed authorization replays only from its unchanged file and closed ledger")
    try:
        expiry = datetime.fromisoformat(auth["expires_at"])
        # Expiry limits spending. Replay never generates, so recorded live output stays reviewable.
        if mode == "live" and (now or datetime.now(timezone.utc)) >= expiry:
            errors.append("authorization expired")
    except (TypeError, ValueError):
        errors.append("invalid expiry")
    if errors:
        raise ValueError("Live authorization rejected: " + "; ".join(errors))
    return auth, _sha_bytes(raw)


def _successor_errors(auth: dict, *, live: bool, fingerprint: str) -> list[str]:
    """Bind a successor to the complete closed predecessor history, so the cumulative caps hold.

    Structure is always checked. For live spending additionally: each predecessor is read from its
    own canonical directory (no copy), revoked, unchanged since closure (SHA-256), free of unresolved
    or unknown billing, and its consumed amount, attempts and retries match the ledger. The list is
    closed under every predecessor's own supersedes record and contains the pinned closed history.
    The latest predecessor carries no other successor. The successor's own limits plus everything
    consumed before may not exceed the AA-P10-LIVE ceilings. Replay never spends, so it does not
    re-read predecessor ledgers.
    """
    errors, consumed, attempts, retries, seen = [], 0, 0, 0, set()
    predecessors = auth.get("predecessors")
    if not isinstance(predecessors, list) or not predecessors:
        return ["successor authorization lists no predecessors"]
    keys = {"authorization_id", "directory", "ledger_sha256", "consumed_microusd", "attempts", "technical_retries"}
    caps = auth.get("review_caps")
    profiles = auth.get("allowed_profiles") or {}
    if not isinstance(caps, dict) or set(caps) != set(profiles) or any(
            not isinstance(c, dict) or set(c) != {"counterreview", "stability"}
            or any(type(v) is not int or v not in {0, 1} for v in c.values()) for c in caps.values()):
        errors.append("review caps must give counterreview/stability limits of 0 or 1 for every allowed profile")
    for profile_id in profiles:
        if profile_id in PROFILES and PROFILES[profile_id].prompt_versions != CONTRACT_R2_PROMPT_BINDING:
            errors.append(f"profile {profile_id} does not bind the AA-P8/1.1 prompts; successors use r2 profiles")
    listed, superseded = {}, {}
    for item in predecessors:
        if not isinstance(item, dict) or set(item) != keys:
            errors.append("malformed predecessor record")
            continue
        if item["authorization_id"] in seen or item["authorization_id"] == auth["authorization_id"]:
            errors.append(f"duplicate predecessor {item['authorization_id']}")
        seen.add(item["authorization_id"])
        listed[item["authorization_id"]] = item
    if not live or errors:
        return errors
    for pid, item in listed.items():
        directory = Path(item["directory"])
        try:
            raw = (directory / "ledger.json").read_bytes()
            ledger = json.loads(raw)
            auth_raw = (directory / "authorization.json").read_bytes()
            prior_auth = json.loads(auth_raw)
        except (OSError, ValueError) as exc:
            errors.append(f"predecessor {pid} unreadable: {exc}")
            continue
        if ledger.get("binding", {}).get("authorization_fingerprint") != _sha_bytes(auth_raw):
            errors.append(f"predecessor {pid} ledger is not bound to this authorization file")
        pinned = KNOWN_CLOSED_AUTHORIZATIONS.get(pid)
        if pinned is not None:
            if _sha_bytes(auth_raw) != pinned["authorization_sha256"]:
                errors.append(f"predecessor {pid} authorization differs from the pinned closed authorization")
        elif prior_auth.get("schema") != AUTH_SCHEMA_SUCCESSOR:
            errors.append(f"predecessor {pid} is neither pinned closed history nor a schema-1.1 successor")
        elif not _recorded_successor(prior_auth, _sha_bytes(auth_raw)):
            errors.append(f"predecessor {pid} is not the successor recorded by its own predecessor")
        found_retries = sum(1 for a in ledger["attempts"] if a.get("retry_of"))
        open_billing = [a["attempt_id"] for a in ledger["attempts"]
                        if a["state"] == "RESERVED_POSSIBLY_BILLABLE" or a.get("billing") != "confirmed_from_usage"]
        if prior_auth.get("authorization_id") != pid or ledger.get("binding", {}).get("authorization_id") != pid:
            errors.append(f"predecessor {pid} identity does not match its ledger")
        if str(directory.resolve()) != prior_auth.get("canonical_directory"):
            errors.append(f"predecessor {pid} is not read from its canonical directory; copies bind nothing")
        if _sha_bytes(raw) != item["ledger_sha256"]:
            errors.append(f"predecessor {pid} ledger changed since closure")
        if ledger.get("state") != "REVOKED" or ledger.get("executable_remaining_microusd") != 0:
            errors.append(f"predecessor {pid} is still executable")
        if open_billing:
            errors.append(f"predecessor {pid} has unresolved or unknown billing: {open_billing}")
        if (ledger.get("reserved_microusd") != item["consumed_microusd"] or len(ledger["attempts"]) != item["attempts"]
                or found_retries != item["technical_retries"]):
            errors.append(f"predecessor {pid} totals differ from its ledger")
        # Every authorization a predecessor itself superseded belongs to the history as well.
        earlier = prior_auth.get("supersedes") or {}
        chain = [(earlier["prior_authorization_id"], earlier.get("prior_ledger_sha256_after_closure"))] \
            if isinstance(earlier, dict) and earlier.get("prior_authorization_id") else []
        chain += [(p.get("authorization_id"), p.get("ledger_sha256")) for p in prior_auth.get("predecessors") or []
                  if isinstance(p, dict)]
        for earlier_id, earlier_sha in chain:
            superseded[earlier_id] = pid
            if earlier_id not in listed:
                errors.append(f"predecessor {pid} supersedes {earlier_id}, which the successor omits")
            elif earlier_sha is not None and listed[earlier_id]["ledger_sha256"] != earlier_sha:
                errors.append(f"predecessor {earlier_id} ledger hash differs from the hash recorded at its closure")
        consumed += ledger.get("reserved_microusd", 0)
        attempts += len(ledger["attempts"])
        retries += found_retries
    for pid, pinned in KNOWN_CLOSED_AUTHORIZATIONS.items():
        if pid not in listed:
            errors.append(f"closed authorization {pid} is missing from the predecessor history")
        elif listed[pid]["ledger_sha256"] != pinned["ledger_sha256"]:
            errors.append(f"closed authorization {pid} does not match its pinned closed ledger")
    heads = [pid for pid in listed if pid not in superseded]
    if len(heads) != 1:
        errors.append(f"predecessor history must be one chain with a single latest authorization, found {sorted(heads)}")
    else:
        claim = _read_claim(Path(listed[heads[0]]["directory"]))
        if claim is not None and claim != _claim_body(auth, fingerprint, heads[0]):
            errors.append(f"predecessor {heads[0]} already carries another successor; no parallel budget")
    if consumed + auth["total_budget_microusd"] > CEILING_TOTAL_MICROUSD:
        errors.append("successor budget plus predecessor consumption exceeds the total ceiling")
    if attempts + auth["max_generation_attempts"] > CEILING_ATTEMPTS:
        errors.append("successor attempts plus predecessor attempts exceed the ceiling")
    if retries + auth["max_technical_retries"] > CEILING_RETRIES:
        errors.append("successor retries plus predecessor retries exceed the ceiling")
    return errors


def _successor_head(auth: dict) -> str:
    """The latest predecessor: the one no other listed predecessor supersedes."""
    listed = {p["authorization_id"]: p for p in auth["predecessors"]}
    superseded = set()
    for item in listed.values():
        prior = json.loads((Path(item["directory"]) / "authorization.json").read_bytes())
        earlier = prior.get("supersedes") or {}
        if isinstance(earlier, dict) and earlier.get("prior_authorization_id"):
            superseded.add(earlier["prior_authorization_id"])
        superseded.update(p.get("authorization_id") for p in prior.get("predecessors") or [] if isinstance(p, dict))
    (head,) = [pid for pid in listed if pid not in superseded]
    return head


def _recorded_successor(prior_auth: dict, fingerprint: str) -> bool:
    """A non-pinned predecessor counts only as the successor its own latest predecessor recorded."""
    try:
        head = _successor_head(prior_auth)
        directory = Path(next(p["directory"] for p in prior_auth["predecessors"] if p["authorization_id"] == head))
    except (KeyError, OSError, ValueError, TypeError, StopIteration):
        return False
    return _read_claim(directory) == _claim_body(prior_auth, fingerprint, head)


def _claim_body(auth: dict, fingerprint: str, head: str) -> dict:
    return {"schema": SUCCESSOR_CLAIM_SCHEMA, "predecessor_authorization_id": head,
            "successor_authorization_id": auth["authorization_id"],
            "successor_canonical_directory": auth["canonical_directory"],
            "successor_authorization_sha256": fingerprint}


def _read_claim(directory: Path) -> dict | None:
    path = directory / SUCCESSOR_CLAIM
    if not path.exists():
        return None
    try:
        claim = json.loads(path.read_bytes())
    except ValueError:
        return {"unreadable": True}
    return {k: claim.get(k) for k in ("schema", "predecessor_authorization_id", "successor_authorization_id",
                                      "successor_canonical_directory", "successor_authorization_sha256")}


def claim_succession(auth: dict, fingerprint: str) -> None:
    """Record, exactly once, that the latest predecessor is succeeded by this authorization.

    Created with O_EXCL before the successor's fresh ledger exists. A second successor of the same
    predecessor finds the claim and is refused, so two executable budgets cannot coexist.
    """
    head = _successor_head(auth)
    directory = Path(next(p["directory"] for p in auth["predecessors"] if p["authorization_id"] == head))
    body = _claim_body(auth, fingerprint, head)
    try:
        fd = os.open(directory / SUCCESSOR_CLAIM, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        if _read_claim(directory) != body:
            raise MissionError(f"predecessor {head} already carries another successor; no parallel budget")
        return
    with os.fdopen(fd, "w") as handle:
        handle.write(json.dumps({**body, "claimed_at": _now()}, indent=2) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def review_allowance(session, slot: str, *, claim: bool = False) -> str | None:
    """Per-profile cap on review slots of a successor authorization; returns a denial reason.

    The live decision is recorded in the ledger (``review_cap_claims``) before any request, so the
    cap counts decisions, not reservations, and replay reproduces the recorded decision exactly.
    ``claim`` records an allowed live decision; replay and preflight only read.

    Replay (Package B, P10-F1/G1): replay never generates, so a review slot is replayed only from a
    completed live capture, or as the recorded unsent request of a claimed slot that live never
    reserved. Every other review slot (no live review, an interrupted or unresolved request, a
    capped or unrecorded allowance) is denied before the reviewer runs; the review stays open.
    """
    _, profile_id, kind = slot.split("|")
    if kind == "primary":
        return None
    caps = session.authorization.get("review_caps")
    data = session.ledger.data
    claims = data.get("review_cap_claims", [])
    limit = (caps or {}).get(profile_id, {}).get(kind, 0)
    # Claims only grow, so an unclaimed slot with the cap used up was denied by the cap.
    capped = bool(caps) and sum(1 for key in claims if key.split("|")[1:] == [profile_id, kind]) >= limit
    denied = (f"Review cap for this model reached ({limit} {kind} per profile under "
              f"{session.authorization['authorization_id']}); the review stays open")
    if session.mode != "live":
        if slot in data["terminal_keys"]:
            return None
        if any(a["slot_key"] == slot for a in data["attempts"]):
            return ("The live review request for this slot was interrupted or is unresolved (no completed capture); "
                    "replay never generates, the review stays open")
        if slot in claims:
            return None  # allowed live, never reserved: replayed as the recorded unsent request
        if caps:
            return denied if capped else "No live review allowance was recorded for this slot; the review stays open"
        return (f"No live review was executed for this slot under {session.authorization['authorization_id']}; "
                "replay never generates, the review stays open")
    if not caps:
        return None
    if slot in claims:
        return None
    if data["state"] != "ACTIVE":
        return "Live ledger is not ACTIVE; the review stays open"
    if capped:
        return denied
    if claim:
        session.ledger.claim_review(slot)
    return None


# ---------------------------------------------------------------------------
# Ledger: extension of the existing atomic BudgetLedger
# ---------------------------------------------------------------------------

class LiveBudgetLedger(BudgetLedger):
    """Per-call maximum-exposure reservation on the existing atomic ledger.

    Differences from the mission ledger, all explicit: the reservation amount is computed per
    call (bounded by ``attempt_microusd``); slots are a declared set, not a frozen order; known
    provider usage settles a reservation down to its confirmed cost, while unknown billing
    stays fully bound. A slot with an unresolved reservation is never resent.
    """

    def _fresh(self) -> dict:
        data = read(self.path)
        if data != self.data:
            raise MissionError("ledger changed outside its lease owner")
        return data

    def reserve(self, key, payload_hash, wire_hash, *, microusd=None, retry_of=None):
        d = self._fresh()
        if microusd is None:
            raise MissionError("live ledger requires an explicit per-call reservation")
        if d["state"] != "ACTIVE":
            raise MissionError("ledger is not ACTIVE")
        if key not in d["planned_keys"] or key in d["terminal_keys"]:
            raise MissionError("slot is not executable")
        prior = [a for a in d["attempts"] if a["slot_key"] == key]
        if any(a["state"] == "RESERVED_POSSIBLY_BILLABLE" for a in prior):
            raise MissionError("slot has an unresolved reservation; no blind resend")
        if prior:
            last = prior[-1]
            if retry_of != last["attempt_id"] or last["state"] != "FAILED_TRANSIENT":
                raise MissionError("retry is only permitted once after a technical failure")
            if sum(1 for a in d["attempts"] if a.get("retry_of")) >= self.binding["max_technical_retries"]:
                raise MissionError("technical retry cap reached")
        elif retry_of is not None:
            raise MissionError("retry without a failed attempt")
        if len(prior) >= self.policy["per_slot"] or len(d["attempts"]) >= self.policy["max_attempts"]:
            raise MissionError("attempt cap reached")
        if type(microusd) is not int or microusd <= 0 or microusd > self.policy["attempt_microusd"]:
            raise MissionError("maximal exposure exceeds the per-call ceiling")
        bound = d["reserved_microusd"] + microusd
        if bound > self.policy["total_microusd"]:
            raise MissionError("dollar cap: maximal exposure would exceed the remaining budget")
        attempt = {"attempt_id": f"attempt-{len(d['attempts']) + 1:03}", "slot_key": key,
                   "payload_sha256": payload_hash, "wire_sha256": wire_hash,
                   "reserved_microusd": microusd, "bound_microusd": microusd,
                   "state": "RESERVED_POSSIBLY_BILLABLE", "usage": None,
                   "confirmed_token_cost_microusd": None, "retry_of": retry_of, "reserved_at": _now()}
        d["attempts"].append(attempt)
        d["reserved_microusd"] = bound
        d["executable_remaining_microusd"] = self.policy["total_microusd"] - bound
        atomic(self.path, d)
        self.data = d
        return attempt["attempt_id"]

    def settle(self, aid, *, state, confirmed_microusd=None, **facts):
        d = self._fresh()
        attempt = next((a for a in d["attempts"] if a["attempt_id"] == aid), None)
        if attempt is None or attempt["state"] != "RESERVED_POSSIBLY_BILLABLE":
            raise MissionError("attempt is unknown or already settled")
        if state not in {"COMPLETED", "FAILED_TRANSIENT", "FAILED_PERMANENT"}:
            raise MissionError("invalid settlement state")
        if confirmed_microusd is not None:
            if type(confirmed_microusd) is not int or confirmed_microusd < 0:
                raise MissionError("invalid confirmed cost")
            delta = confirmed_microusd - attempt["bound_microusd"]
            if delta > 0:
                attempt["overrun_microusd"] = delta
            attempt["bound_microusd"] = confirmed_microusd
            attempt["confirmed_token_cost_microusd"] = confirmed_microusd
            d["reserved_microusd"] += delta
            attempt["billing"] = "confirmed_from_usage"
        else:
            attempt["billing"] = "unknown_reservation_kept"
        attempt.update(state=state, settled_at=_now(), **facts)
        total = self.policy["total_microusd"]
        d["executable_remaining_microusd"] = max(total - d["reserved_microusd"], 0)
        if d["reserved_microusd"] > total:
            d.update(state="REVOKED", revocation_reason="confirmed cost exceeded the authorized total")
        atomic(self.path, d)
        self.data = d

    def claim_review(self, key):
        """Durably record an allowed review decision before its request (see review_allowance)."""
        d = self._fresh()
        if d["state"] != "ACTIVE" or key not in d["planned_keys"]:
            raise MissionError("review allowance outside an ACTIVE ledger slot")
        claims = d.setdefault("review_cap_claims", [])
        if key not in claims:
            claims.append(key)
            atomic(self.path, d)
            self.data = d

    def terminal(self, key, raw_record_sha256):
        d = self._fresh()
        if key not in d["planned_keys"] or key in d["terminal_keys"]:
            raise MissionError("terminal duplicate or unknown slot")
        prior = [a for a in d["attempts"] if a["slot_key"] == key]
        if not prior or any(a["state"] == "RESERVED_POSSIBLY_BILLABLE" for a in prior):
            raise MissionError("terminal without settled attempt")
        d["terminal_keys"].append(key)
        d.setdefault("terminal_record_hashes", {})[key] = raw_record_sha256
        atomic(self.path, d)
        self.data = d


# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------

class LiveSession:
    """One authorization directory: authorization, ledger, captures and an exclusive lease."""

    def __init__(self, directory: Path, *, mode: str, transport=None, api_key: str | None = None,
                 now: datetime | None = None):
        if mode not in {"live", "replay"}:
            raise ValueError("Live session mode must be live or replay")
        self.directory = Path(directory).resolve()
        self.mode = mode
        self.transport = transport
        self.api_key = api_key
        self.authorization, self.fingerprint = load_authorization(self.directory, now=now, mode=mode)
        self.binding = {"schema": LEDGER_SCHEMA, "addendum": ADDENDUM,
                        "authorization_id": self.authorization["authorization_id"],
                        "authorization_fingerprint": self.fingerprint,
                        "max_technical_retries": self.authorization["max_technical_retries"],
                        "endpoint": MESSAGES_URL}
        self.policy = {"max_attempts": self.authorization["max_generation_attempts"],
                       "per_slot": self.authorization["max_attempts_per_request"],
                       "attempt_microusd": self.authorization["per_call_ceiling_microusd"],
                       "total_microusd": self.authorization["total_budget_microusd"]}
        self.captures = self.directory / "captures"
        self._lease = None
        self.unresolved: list[str] = []
        ledger_path = self.directory / "ledger.json"
        slots = [{"slot_key": s} for s in self.authorization["slots"]]
        if mode == "live":
            self._lease = (self.directory / ".live-lease").open("a+")
            try:
                fcntl.flock(self._lease.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                self._lease.close()
                self._lease = None
                raise ValueError("Another process holds this live authorization; parallel execution refused") from exc
            fresh = not ledger_path.exists()
            if fresh and self.captures.exists() and any(self.captures.iterdir()):
                self.close()
                raise MissionError("captures exist without their ledger; a fresh budget is never created")
            if self.authorization["schema"] == AUTH_SCHEMA_SUCCESSOR:
                try:
                    claim_succession(self.authorization, self.fingerprint)
                except MissionError:
                    self.close()
                    raise
            self.ledger = LiveBudgetLedger(ledger_path, self.binding, slots, policy=self.policy, create=fresh)
            self.reconcile()
        else:
            if not ledger_path.exists():
                raise ValueError("Replay requires the live ledger of the original execution")
            self.ledger = LiveBudgetLedger(ledger_path, self.binding, slots, policy=self.policy)

    def close(self):
        if self._lease is not None:
            fcntl.flock(self._lease.fileno(), fcntl.LOCK_UN)
            self._lease.close()
            self._lease = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def capture_path(self, attempt_id: str) -> Path:
        return self.captures / f"{attempt_id}.json"

    def reconcile(self) -> None:
        """Settle reservations whose raw capture was persisted before an interruption."""
        for attempt in list(self.ledger.data["attempts"]):
            if attempt["state"] != "RESERVED_POSSIBLY_BILLABLE":
                continue
            path = self.capture_path(attempt["attempt_id"])
            if not path.exists():
                self.unresolved.append(attempt["attempt_id"])
                continue
            capture = json.loads(path.read_bytes())
            if (capture.get("attempt_id") != attempt["attempt_id"] or capture.get("slot_key") != attempt["slot_key"]
                    or capture.get("authorization_id") != self.authorization["authorization_id"]
                    or capture.get("profile_id") not in PROFILES):
                self.unresolved.append(attempt["attempt_id"])  # foreign capture: reservation stays bound
                continue
            profile = PROFILES[capture["profile_id"]]
            confirmed = _confirmed(profile, capture["call"])
            self.ledger.settle(attempt["attempt_id"], state=_call_state(capture["call"]),
                               confirmed_microusd=confirmed, capture_sha256=_sha_bytes(path.read_bytes()),
                               request_id=capture["call"].get("request_id"),
                               http_status=capture["call"].get("http_status"), reconciled_after_interruption=True)
        # A crash between settlement and the terminal step must not leave an answered slot open.
        d = self.ledger.data
        for key in d["planned_keys"]:
            attempts = [a for a in d["attempts"] if a["slot_key"] == key]
            if not attempts or key in d["terminal_keys"] or any(
                    a["state"] == "RESERVED_POSSIBLY_BILLABLE" for a in attempts):
                continue
            last = attempts[-1]
            if last["state"] in {"COMPLETED", "FAILED_PERMANENT"} or last.get("retry_of"):
                capture = self.capture_path(last["attempt_id"])
                text = ""
                if capture.exists():
                    text = (json.loads(capture.read_bytes()).get("interpretation") or {}).get("final_text", "")
                self.ledger.terminal(key, sha256_text(text))
                d = self.ledger.data

    def summary(self) -> dict:
        d = self.ledger.data
        return {"authorization_id": self.authorization["authorization_id"],
                "authorization_fingerprint": self.fingerprint, "ledger_state": d["state"],
                "attempts": len(d["attempts"]), "reserved_or_confirmed_microusd": d["reserved_microusd"],
                "executable_remaining_microusd": d["executable_remaining_microusd"],
                "unresolved_attempts": list(self.unresolved)}


def close_for_successor(directory: Path, *, successor_id: str, reason: str) -> dict:
    """Make one authorization non-executable before a successor carries its remaining budget.

    Reuses the existing ledger revocation (state REVOKED, executable remainder 0), so the two
    authorizations never hold parallel executable budgets. Replay of the recorded captures
    stays possible. Refused while any reservation is unresolved, because its cost is unknown.
    """
    with LiveSession(directory, mode="live") as session:
        if session.unresolved:
            raise MissionError("unresolved reservations; the closing ledger cannot be carried over")
        if session.ledger.data["state"] != "ACTIVE":
            raise MissionError("ledger is not ACTIVE; nothing to close")
        session.ledger.revoke(f"CLOSED_SUPERSEDED by {successor_id}: {reason}")
        summary = session.summary()
        attempts = session.ledger.data["attempts"]
        # Hashed while the lease is still held, so the recorded bytes are the closed ledger.
        ledger_sha256 = _sha_bytes((session.directory / "ledger.json").read_bytes())
    summary.update(
        technical_retries=sum(1 for a in attempts if a.get("retry_of")),
        unknown_billing_attempts=[a["attempt_id"] for a in attempts
                                  if a.get("billing") == "unknown_reservation_kept"],
        ledger_sha256=ledger_sha256,
    )
    return summary


def _confirmed(profile, call: dict) -> int | None:
    if call.get("request_sent") is False:
        return 0  # nothing left the process (e.g. credential missing): nothing can be billed
    body = call.get("response_body")
    if call.get("http_status") == 200 and isinstance(body, dict) and isinstance(body.get("usage"), dict):
        try:
            return cost_microusd(profile, body["usage"])
        except ValueError:
            return None
    return None


def _call_state(call: dict) -> str:
    if call.get("http_status") == 200:
        return "COMPLETED"
    return "FAILED_TRANSIENT" if call.get("error_type") in TRANSIENT_ERRORS else "FAILED_PERMANENT"


# ---------------------------------------------------------------------------
# Providers
# ---------------------------------------------------------------------------

class _BoundProvider(BaseProvider):
    def __init__(self, session: LiveSession, profile_id: str, task_id: str, kind: str, prompt_version: str):
        from inspektorium.audit.runner import resolve_study_forensics_prompt
        if profile_id not in self._allowed(session):
            raise ValueError("Profile is not allowed by this live authorization")
        self.session = session
        self.profile = PROFILES[profile_id]
        self.model = self.profile.model_id
        self.task_id = task_id
        self.kind = kind
        self.slot = slot_key(task_id, profile_id, kind)
        if self.slot not in session.authorization["slots"]:
            raise ValueError("Slot is not part of this live authorization")
        if prompt_version != self.profile.prompt_versions[0 if kind == "primary" else 1]:
            raise ValueError("Prompt version is not the one bound to this profile revision and slot kind")
        self.prompt_version = prompt_version
        self.system_sha256 = sha256_text(resolve_study_forensics_prompt(prompt_version))

    @staticmethod
    def _allowed(session):
        return session.authorization["allowed_profiles"]

    def _credential_available(self) -> bool:
        return bool(self.session.api_key if self.session.api_key is not None else os.environ.get("ANTHROPIC_API_KEY"))

    def preflight(self, task: Task) -> str | None:
        """Refuse before any network access: binding, answered/unclear slot, budget."""
        from inspektorium.audit.runner import resolve_study_forensics_prompt
        system = resolve_study_forensics_prompt(self.prompt_version)
        try:
            user = self._check(task, system)
        except ValueError as exc:
            return str(exc)
        d = self.session.ledger.data
        attempts = [a for a in d["attempts"] if a["slot_key"] == self.slot]
        if self.session.mode == "replay":
            return None if self.slot in d["terminal_keys"] and attempts else \
                "No completed live capture exists for this slot; replay cannot generate"
        if not self._credential_available():
            return "ANTHROPIC_API_KEY is not available; nothing reserved or sent"
        if self.slot in d["terminal_keys"]:
            return "Slot already answered; a completed live slot is never resent"
        if any(a["state"] == "RESERVED_POSSIBLY_BILLABLE" for a in attempts):
            return "Slot has an unresolved reservation from an interrupted request; not resent"
        if d["state"] != "ACTIVE":
            return "Live ledger is not ACTIVE"
        denied = review_allowance(self.session, self.slot)
        if denied:
            return denied
        exposure, _ = max_exposure_microusd(self.profile, system, user)
        policy = self.session.policy
        if exposure > policy["attempt_microusd"] or d["reserved_microusd"] + exposure > policy["total_microusd"]:
            return (f"Insufficient remaining budget: maximal exposure {exposure} microUSD, "
                    f"remaining {policy['total_microusd'] - d['reserved_microusd']} microUSD")
        if len(d["attempts"]) >= policy["max_attempts"]:
            return "Generation attempt limit reached"
        return None

    def send_prompt(self, task: Task, system_prompt: str) -> str:
        response = self.generate(task, system_prompt)
        if response.error:
            raise RuntimeError(response.error)
        return response.text

    def _check(self, task: Task, system_prompt: str) -> str:
        if task.id != self.task_id:
            raise ValueError("Task does not belong to this live slot")
        if self.kind == "primary":
            binding = self.session.authorization["task_bindings"].get(task.id)
            if binding != task_sha256(task):
                raise ValueError("Task bytes differ from the authorized case binding")
        if sha256_text(system_prompt) != self.system_sha256:
            raise ValueError("System prompt is not the registered prompt version for this slot")
        return build_user_message(task)

    def _evidence(self, task, system_prompt, user, *, current, capture, capture_sha, info, attempts, extra=None,
                  delivered_text=None):
        call = capture["call"] if capture else {}
        usage = info.get("usage") or {}
        bound = input_token_bound(system_prompt, user) if user is not None else None
        prompt_tokens = sum(v for v in (usage.get("input_tokens"), usage.get("cache_creation_input_tokens"),
                                        usage.get("cache_read_input_tokens")) if type(v) is int)
        final = attempts[-1] if attempts else None
        evidence = {
            "schema": EVIDENCE_SCHEMA, "addendum": ADDENDUM, "origin": "live_generation",
            "current_execution": current, "provider": "anthropic", "endpoint": MESSAGES_URL,
            "authorization_id": self.session.authorization["authorization_id"],
            "authorization_fingerprint": self.session.fingerprint,
            "slot_key": self.slot, "slot_kind": self.kind, "task_id": task.id,
            "request_task_sha256": task_sha256(task),
            "profile_id": self.profile.profile_id, "profile_fingerprint": self.profile.fingerprint(),
            "requested_model": self.profile.model_id, "returned_model": info.get("returned_model"),
            "request_sent": bool(call.get("request_sent")), "http_status": call.get("http_status"),
            "request_id": call.get("request_id"), "message_id": info.get("message_id"),
            "system_prompt_version": self.prompt_version, "system_prompt_sha256": sha256_text(system_prompt),
            "user_message_version": USER_MESSAGE_VERSION,
            "user_message_sha256": sha256_text(user) if user is not None else None,
            "request_sha256": call.get("request_sha256"),
            "stop_reason": info.get("stop_reason"), "completion_state": info.get("completion_state"),
            "content_block_types": info.get("content_block_types", []),
            "thinking_block_count": info.get("thinking_block_count", 0),
            "text_block_count": info.get("text_block_count", 0),
            "usage": usage, "billing": call.get("billing", "none"),
            "reserved_microusd": final["reserved_microusd"] if final else 0,
            "confirmed_cost_microusd": final.get("confirmed_token_cost_microusd") if final else None,
            "attempt_ids": [a["attempt_id"] for a in attempts], "final_attempt_id": final["attempt_id"] if final else None,
            "latency_ms": call.get("latency_ms"), "started_at": call.get("started_at"),
            "completed_at": call.get("completed_at"),
            "final_text_sha256": sha256_text(info.get("final_text", "") if delivered_text is None else delivered_text),
            "capture_final_text_sha256": sha256_text(info.get("final_text", "")),
            "capture_sha256": capture_sha,
            "input_token_bound": bound,
            "input_bound_respected": None if not prompt_tokens else (bound is not None and prompt_tokens <= bound),
        }
        evidence.update(extra or {})
        return evidence

    def _denied(self, task, system_prompt, user, reason, attempts, current, extra=None):
        info = {"final_text": "", "completion_state": "not_sent", "usage": {}}
        evidence = self._evidence(task, system_prompt, user, current=current, capture=None, capture_sha=None,
                                  info=info, attempts=attempts, extra={"denial_reason": reason, **(extra or {})})
        return LiveModelResponse(text="", provider="anthropic-live", model=self.profile.model_id,
                                 finish_reason="error", error=f"Live request not sent: {reason}",
                                 error_type="live_denied", execution_evidence=evidence)


class LiveAuditProvider(_BoundProvider):
    """Exact live provider type accepted by the canonical audit path in live mode."""
    name = "anthropic-live"
    label = "anthropic-live"

    def __init__(self, session: LiveSession, profile_id: str, task_id: str, kind: str, prompt_version: str):
        if session.mode != "live":
            raise ValueError("Live provider requires a live session")
        super().__init__(session, profile_id, task_id, kind, prompt_version)
        self.network_attempts = 0

    def generate(self, task: Task, system_prompt: str) -> LiveModelResponse:
        user = None
        try:
            user = self._check(task, system_prompt)
        except ValueError as exc:
            return self._denied(task, system_prompt, user, str(exc), [], "live_generation")
        if not self._credential_available():
            return self._denied(task, system_prompt, user, "ANTHROPIC_API_KEY is not available", [],
                                "live_generation")
        ledger = self.session.ledger
        denied = review_allowance(self.session, self.slot, claim=True)
        if denied:
            return self._denied(task, system_prompt, user, denied, [], "live_generation")
        exposure, basis = max_exposure_microusd(self.profile, system_prompt, user)
        request_sha = sha256_text(canonical_json(self.profile.request_body(system_prompt, user)))
        prior = [a for a in ledger.data["attempts"] if a["slot_key"] == self.slot]
        # After an interruption between a technical failure and its retry, the single permitted
        # retry is resumed instead of leaving the slot stuck; nothing else is ever resent.
        pending_retry = prior[-1]["attempt_id"] if prior and prior[-1]["state"] == "FAILED_TRANSIENT" and \
            not prior[-1].get("retry_of") else None
        try:
            aid = ledger.reserve(self.slot, request_sha, request_sha, microusd=exposure, retry_of=pending_retry)
        except MissionError as exc:
            attempts = [a for a in ledger.data["attempts"] if a["slot_key"] == self.slot]
            return self._denied(task, system_prompt, user, f"budget/authorization: {exc}", attempts,
                                "live_generation")
        retry_denied = None
        while True:
            if self.session.capture_path(aid).exists():
                # Checked before sending: an existing file means the ledger was rolled back externally.
                raise MissionError(f"capture {aid} already exists; earlier raw evidence is never overwritten")
            self.network_attempts += 1
            call = send_request(self.profile, system_prompt, user, transport=self.session.transport,
                                api_key=self.session.api_key)
            info, response = response_from_capture(self.profile, call)
            capture = {"schema": CAPTURE_SCHEMA, "addendum": ADDENDUM,
                       "authorization_id": self.session.authorization["authorization_id"],
                       "attempt_id": aid, "slot_key": self.slot, "profile_id": self.profile.profile_id,
                       "profile_fingerprint": self.profile.fingerprint(), "task_id": task.id,
                       "task_sha256": task_sha256(task), "system_prompt_version": self.prompt_version,
                       "user_message_version": USER_MESSAGE_VERSION, "exposure_basis": basis,
                       "reserved_microusd": exposure, "call": call, "interpretation": info}
            path = self.session.capture_path(aid)
            atomic(path, capture)  # raw response persisted before any interpretation is used
            capture_sha = _sha_bytes(path.read_bytes())
            state = _call_state(call)
            ledger.settle(aid, state=state, confirmed_microusd=_confirmed(self.profile, call),
                          capture_sha256=capture_sha, request_id=call.get("request_id"),
                          http_status=call.get("http_status"), usage=info.get("usage") or None)
            if state == "FAILED_TRANSIENT" and retry_denied is None and pending_retry is None and \
                    not any(a.get("retry_of") == aid for a in ledger.data["attempts"]) and \
                    not next(a for a in ledger.data["attempts"] if a["attempt_id"] == aid).get("retry_of"):
                previous = aid
                try:
                    # One technical retry, reserved separately before it is sent.
                    aid = ledger.reserve(self.slot, request_sha, request_sha, microusd=exposure, retry_of=previous)
                    continue
                except MissionError as exc:
                    retry_denied = str(exc)
            break
        ledger.terminal(self.slot, sha256_text(info.get("final_text", "")))
        attempts = [a for a in ledger.data["attempts"] if a["slot_key"] == self.slot]
        evidence = self._evidence(task, system_prompt, user, current="live_generation", capture=capture,
                                  capture_sha=capture_sha, info=info, attempts=attempts,
                                  extra={"retry_denied": retry_denied} if retry_denied else None,
                                  delivered_text=response.text)
        return LiveModelResponse(text=response.text, provider="anthropic-live",
                                 model=response.model or self.profile.model_id,
                                 finish_reason=response.finish_reason, usage=response.usage,
                                 latency_ms=response.latency_ms, error=response.error,
                                 error_type=response.error_type, execution_evidence=evidence)


class ReplayProvider(_BoundProvider):
    """Offline replay of a captured live response. Never imports a network client."""
    name = "anthropic-live-replay"
    label = "anthropic-live-replay"

    def __init__(self, session: LiveSession, profile_id: str, task_id: str, kind: str, prompt_version: str):
        if session.mode != "replay":
            raise ValueError("Replay provider requires a replay session")
        super().__init__(session, profile_id, task_id, kind, prompt_version)
        self.network_attempts = 0

    def generate(self, task: Task, system_prompt: str) -> LiveModelResponse:
        user = None
        try:
            user = self._check(task, system_prompt)
        except ValueError as exc:
            return self._denied(task, system_prompt, user, str(exc), [], "offline_replay")
        data = self.session.ledger.data
        attempts = [a for a in data["attempts"] if a["slot_key"] == self.slot]
        ledger_sha = _sha_bytes(self.session.ledger.path.read_bytes())
        if not attempts and self.kind != "primary" and self.slot in data.get("review_cap_claims", []):
            # Live allowed this review but never sent it (refused before any reservation, e.g. by
            # the per-call ceiling or the remaining budget). Replay reproduces that unsent request.
            return self._denied(task, system_prompt, user, "no live request was sent for this review slot", [],
                                "offline_replay", extra={"new_generation": False, "replay_of_unsent_request": True,
                                                         "replay_ledger_sha256": ledger_sha})
        if self.slot not in data["terminal_keys"] or not attempts:
            return self._denied(task, system_prompt, user, "no completed live capture for this slot", attempts,
                                "offline_replay")
        final = attempts[-1]
        path = self.session.capture_path(final["attempt_id"])
        try:
            raw = path.read_bytes()
        except OSError:
            return self._denied(task, system_prompt, user, "live capture missing", attempts, "offline_replay")
        capture_sha = _sha_bytes(raw)
        capture = json.loads(raw)
        current_request = sha256_text(canonical_json(self.profile.request_body(system_prompt, user)))
        info, response = response_from_capture(self.profile, capture["call"])
        extra = {"replayed_at": _now(), "replay_ledger_sha256": ledger_sha,
                 "replay_capture_verified": capture_sha == final.get("capture_sha256"),
                 "replay_request_identical": current_request == capture["call"].get("request_sha256"),
                 "new_generation": False}
        evidence = self._evidence(task, system_prompt, user, current="offline_replay", capture=capture,
                                  capture_sha=capture_sha, info=info, attempts=attempts, extra=extra,
                                  delivered_text=response.text)
        if not (extra["replay_capture_verified"] and extra["replay_request_identical"]):
            return LiveModelResponse(text="", provider="anthropic-live-replay", model=self.profile.model_id,
                                     finish_reason="error", error="Replay capture or request binding mismatch",
                                     error_type="replay_mismatch", execution_evidence=evidence)
        return LiveModelResponse(text=response.text, provider="anthropic-live-replay",
                                 model=response.model or self.profile.model_id,
                                 finish_reason=response.finish_reason, usage=response.usage,
                                 latency_ms=response.latency_ms, error=response.error,
                                 error_type=response.error_type, execution_evidence=evidence)


def review_mode(provider) -> str | None:
    """Exact provider types only; subclasses or look-alikes are not accepted."""
    if type(provider) is LiveAuditProvider:
        return "live"
    if type(provider) is ReplayProvider:
        return "live_replay"
    return None


# ---------------------------------------------------------------------------
# Provenance validation (used by the mandatory provenance control)
# ---------------------------------------------------------------------------

OFFLINE_MODEL = "offline-recording-no-live-model"


def carrier_kind(carrier: dict) -> str:
    """Classify one AgentResult-shaped dict: offline, live, replay or invalid."""
    evidence = carrier.get("execution_evidence")
    if evidence is None:
        if carrier.get("model") == OFFLINE_MODEL and carrier.get("provider") == OFFLINE_MODEL:
            return "offline"
        return "invalid"
    if not isinstance(evidence, dict) or evidence.get("schema") != EVIDENCE_SCHEMA:
        return "invalid"
    return {"live_generation": "live", "offline_replay": "replay"}.get(evidence.get("current_execution"), "invalid")


def validate_live_carrier(carrier: dict, *, expected_kind: str, task: Task | None = None) -> list[str]:
    errors = []
    ev = carrier.get("execution_evidence") or {}
    profile = PROFILES.get(ev.get("profile_id"))
    if ev.get("addendum") != ADDENDUM or ev.get("origin") != "live_generation":
        errors.append("evidence schema/origin")
    if profile is None or ev.get("profile_fingerprint") != profile.fingerprint():
        errors.append("unregistered profile or configuration revision")
    elif ev.get("requested_model") != profile.model_id or carrier.get("model") != profile.model_id:
        errors.append("requested model differs from the registered profile")
    if ev.get("endpoint") != MESSAGES_URL or ev.get("provider") != "anthropic":
        errors.append("endpoint/provider")
    if ev.get("slot_kind") != expected_kind:
        errors.append("slot kind does not match the carrier role")
    if profile is not None and expected_kind in KINDS:
        from inspektorium.audit.runner import resolve_study_forensics_prompt
        version = profile.prompt_versions[0 if expected_kind == "primary" else 1]
        if ev.get("system_prompt_version") != version or \
                ev.get("system_prompt_sha256") != sha256_text(resolve_study_forensics_prompt(version)):
            errors.append("system prompt is not the version bound to this profile revision")
    if ev.get("final_text_sha256") != sha256_text(carrier.get("raw_output") or ""):
        errors.append("final text hash differs from the stored raw output")
    if not isinstance(ev.get("authorization_id"), str) or not ev.get("authorization_id"):
        errors.append("authorization identity missing")
    if not isinstance(ev.get("attempt_ids"), list):
        errors.append("attempt identities missing")
    if ev.get("request_sent"):
        if ev.get("http_status") == 200:
            if ev.get("returned_model") != ev.get("requested_model"):
                errors.append("returned model differs from requested model")
            if not isinstance(ev.get("request_id"), str) or not ev["request_id"]:
                errors.append("provider request ID missing")
            usage = ev.get("usage") or {}
            if type(usage.get("input_tokens")) is not int or type(usage.get("output_tokens")) is not int:
                errors.append("provider usage missing")
            if ev.get("input_bound_respected") is False:
                errors.append("actual input exceeded the reserved bound")
            if not ev.get("capture_sha256"):
                errors.append("raw capture hash missing")
    elif not ev.get("denial_reason") and not ev.get("attempt_ids"):
        errors.append("unsent request lacks a recorded denial reason or attempt")
    unsent_review = (ev.get("replay_of_unsent_request") is True and expected_kind in {"counterreview", "stability"}
                     and ev.get("request_sent") is False and ev.get("attempt_ids") == [] and ev.get("denial_reason")
                     and not carrier.get("raw_output"))
    if ev.get("current_execution") == "offline_replay" and ev.get("new_generation") is not False:
        errors.append("replay is not bound to the verified original capture and identical request")
    elif ev.get("current_execution") == "offline_replay" and not unsent_review and not (
            ev.get("replay_capture_verified") and ev.get("replay_request_identical")):
        errors.append("replay is not bound to the verified original capture and identical request")
    if task is not None and expected_kind == "primary":
        if ev.get("task_id") != task.id or ev.get("request_task_sha256") != task_sha256(task):
            errors.append("primary evidence is not bound to this case")
    return errors


def execution_mode(record, review: dict) -> tuple[str | None, list[str]]:
    """Derive the single bundle mode from every result and Phase9 carrier."""
    carriers = [("primary", r.agent_result.model_dump(mode="json")) for r in record.results]
    for position in review.get("positions", []):
        origin = position.get("origin")
        if origin == "original" or origin == "human_correction":
            continue  # originals are the results above; human corrections are mode-neutral
        kind = {"model_review": "counterreview", "stability": "stability"}.get(origin)
        carriers.append((kind or "invalid", position.get("agent_result") or {}))
    if not carriers:
        return "recorded_offline", []  # legacy empty population: input_preflight blocks it
    kinds = {carrier_kind(c) for _, c in carriers}
    if kinds == {"offline"}:
        return "recorded_offline", []
    if kinds not in ({"live"}, {"replay"}):
        return None, ["mixed, unknown or unbound execution carriers: " + ",".join(sorted(kinds))]
    errors = []
    auth_ids, attempt_ids, profiles, slots = set(), [], set(), []
    for role, carrier in carriers:
        problems = validate_live_carrier(carrier, expected_kind=role, task=record.task if role == "primary" else None)
        errors += [f"{role}: {p}" for p in problems]
        ev = carrier.get("execution_evidence") or {}
        # Every carrier, including Phase9 reviews, is bound to this case and its own slot.
        if ev.get("task_id") != record.task.id:
            errors.append(f"{role}: evidence belongs to another case")
        try:
            expected_slot = slot_key(record.task.id, str(ev.get("profile_id")), role)
        except ValueError:
            expected_slot = None
        if ev.get("slot_key") != expected_slot:
            errors.append(f"{role}: evidence slot is not this case's {role} slot")
        auth_ids.add(ev.get("authorization_id"))
        profiles.add(ev.get("profile_id"))
        slots.append(ev.get("slot_key"))
        attempt_ids += ev.get("attempt_ids") or []
    if len(auth_ids) != 1:
        errors.append("carriers reference more than one authorization")
    if len(profiles) != 1:
        errors.append("carriers mix model profiles")
    if len(slots) != len(set(slots)):
        errors.append("a slot is bound to more than one carrier")
    if len(attempt_ids) != len(set(attempt_ids)):
        errors.append("an attempt identity is bound to more than one carrier")
    mode = "live_generation" if kinds == {"live"} else "offline_replay_of_live"
    return (mode if not errors else None), errors
