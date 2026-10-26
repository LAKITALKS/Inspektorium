"""AA-P10-LIVE/1.0: authorization, live budget ledger, live/replay providers, provenance checks.

Every provider call reserves its conservative maximum exposure in a durable ledger before the
request leaves the process. Raw responses are persisted before interpretation. Recorded hashes
and identities are integrity checks; they do not authenticate a person or the provider.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from agent_arena.bounded_harness_mission import BudgetLedger, MissionError, atomic, read
from agent_arena.providers import BaseProvider
from agent_arena.providers.anthropic_live import (
    EVIDENCE_SCHEMA, LIVE_ENDPOINT, MESSAGES_URL, PROFILES, TRANSIENT_ERRORS, USER_MESSAGE_VERSION,
    LiveModelResponse, build_user_message, canonical_json, cost_microusd, input_token_bound,
    max_exposure_microusd, response_from_capture, send_request, sha256_text,
)
from agent_arena.schemas import Task

ADDENDUM = "AA-P10-LIVE/1.0"
AUTH_SCHEMA = "aa-p10-live-authorization/1.0"
LEDGER_SCHEMA = "aa-p10-live-ledger/1.0"
CAPTURE_SCHEMA = "aa-p10-live-capture/1.0"
KINDS = ("primary", "counterreview", "stability")
CEILING_TOTAL_MICROUSD = 2_000_000
CEILING_ATTEMPTS = 40
CEILING_RETRIES = 4
LIVE_MODES = ("live_generation", "offline_replay_of_live")


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

def load_authorization(directory: Path, *, now: datetime | None = None) -> tuple[dict, str]:
    """Validate the work-order-bound authorization; any defect blocks before sending."""
    path = Path(directory) / "authorization.json"
    raw = path.read_bytes()
    auth = json.loads(raw)
    errors = []
    expected = {"schema", "authorization_id", "work_order", "issued_at", "expires_at", "status",
                "canonical_directory", "endpoint", "total_budget_microusd", "max_generation_attempts",
                "max_technical_retries", "max_attempts_per_request", "per_call_ceiling_microusd",
                "allowed_profiles", "task_bindings", "slots", "supersedes"}
    if not isinstance(auth, dict) or set(auth) != expected:
        raise ValueError("Live authorization is partial or has unknown fields")
    if auth["schema"] != AUTH_SCHEMA:
        errors.append("unsupported authorization schema")
    if auth["status"] != "ACTIVE":
        errors.append("authorization is not ACTIVE")
    if auth["canonical_directory"] != str(Path(directory).resolve()):
        # A copied authorization would otherwise open a second, fresh ledger and multiply the cap.
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
    try:
        expiry = datetime.fromisoformat(auth["expires_at"])
        if (now or datetime.now(timezone.utc)) >= expiry:
            errors.append("authorization expired")
    except (TypeError, ValueError):
        errors.append("invalid expiry")
    if errors:
        raise ValueError("Live authorization rejected: " + "; ".join(errors))
    return auth, _sha_bytes(raw)


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
        self.authorization, self.fingerprint = load_authorization(self.directory, now=now)
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
        from agent_arena.runner import resolve_study_forensics_prompt
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
        self.prompt_version = prompt_version
        self.system_sha256 = sha256_text(resolve_study_forensics_prompt(prompt_version))

    @staticmethod
    def _allowed(session):
        return session.authorization["allowed_profiles"]

    def _credential_available(self) -> bool:
        import os
        return bool(self.session.api_key if self.session.api_key is not None else os.environ.get("ANTHROPIC_API_KEY"))

    def preflight(self, task: Task) -> str | None:
        """Refuse before any network access: binding, answered/unclear slot, budget."""
        from agent_arena.runner import resolve_study_forensics_prompt
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

    def _denied(self, task, system_prompt, user, reason, attempts, current):
        info = {"final_text": "", "completion_state": "not_sent", "usage": {}}
        evidence = self._evidence(task, system_prompt, user, current=current, capture=None, capture_sha=None,
                                  info=info, attempts=attempts, extra={"denial_reason": reason})
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
        extra = {"replayed_at": _now(), "replay_capture_verified": capture_sha == final.get("capture_sha256"),
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
    if ev.get("current_execution") == "offline_replay" and not (
            ev.get("replay_capture_verified") and ev.get("replay_request_identical") and ev.get("new_generation") is False):
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
