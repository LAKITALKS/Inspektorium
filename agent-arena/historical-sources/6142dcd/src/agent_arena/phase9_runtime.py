"""Bounded offline review adapter over the existing runner, ledger and decision log.

No live provider is accepted. Host submission is provenance, not authenticated IAM.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from agent_arena.providers import BaseProvider
from agent_arena.schemas import AgentResult, DecisionEntry, RunRecord, Task


def _hash(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode()).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def code_version() -> str:
    root = Path(__file__).parent
    return _hash({p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in sorted(root.glob("phase9_*.py"))})


class OfflineReviewProvider(BaseProvider):
    """Recorded bytes or a single simulated error; no callbacks, retries or network."""
    name = "phase9_offline_recording"
    model = "offline-recording-no-live-model"

    def __init__(self, raw_output: str = "", *, error: str | None = None):
        if type(raw_output) is not str or (error is not None and type(error) is not str):
            raise TypeError("Only recorded text and static errors are accepted")
        self.raw_output = raw_output
        self.error = error
        self.requests: list[dict] = []

    def send_prompt(self, task: Task, system_prompt: str) -> str:
        self.requests.append({"task": task.model_dump(mode="json"), "system_prompt": system_prompt})
        if self.error:
            raise RuntimeError(self.error)
        return self.raw_output


def build_challenge(task: Task, position, additional_positions=()) -> dict:
    """Keep original source prose and all captured evidence, exclude interpretation."""
    record = position.forensic_record or {}
    ledger = record.get("phase8") or {}
    if not isinstance(ledger, dict) or not isinstance(ledger.get("propositions"), list) or \
            not isinstance(record.get("evidence"), list) or not all(
                isinstance(item, dict) for item in ledger["propositions"] + record["evidence"]):
        raise ValueError("Complete bound challenge unavailable: malformed original extraction")
    packet = {
        "original_claim": task.prompt, "original_context": task.context,
        "claim_id": ledger.get("claim_id"),
        "propositions": [{k: p.get(k) for k in ("proposition_id", "original_span")}
                         for p in ledger.get("propositions", [])],
        "evidence": [{k: e.get(k) for k in ("evidence_id", "source_id", "text", "exact_reference")}
                     for e in record.get("evidence", [])],
    }
    for other in additional_positions:
        other_packet = build_challenge(task, other)
        for field in ("propositions", "evidence"):
            for item in other_packet[field]:
                if item not in packet[field]:
                    packet[field].append(item)
    return packet


def stability_variant(packet: dict) -> dict:
    variant = json.loads(json.dumps(packet))
    variant["evidence"] = list(reversed(variant["evidence"]))
    return variant


def _same_typed_content(left, right) -> bool:
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(
            type(key) is str and _same_typed_content(value, right[key]) for key, value in left.items())
    if isinstance(left, list):
        return len(left) == len(right) and all(_same_typed_content(a, b) for a, b in zip(left, right))
    return left == right


def validate_variant(packet: dict, variant: dict) -> str | None:
    if not _same_typed_content(variant, stability_variant(packet)):
        return "Rejected: only exact reversal of the complete evidence ordering is permitted."
    if _same_typed_content(variant, packet):
        return "Rejected: evidence reversal is a no-op; no replacement variant is sampled."
    return None


def _challenge_task(task: Task, packet: dict) -> Task:
    # Reconstruct, do not copy Task's gold/rubric/reference/expected-answer fields.
    return Task(id=task.id, title="Independent bound evidence review", domain=task.domain,
                difficulty=task.difficulty, task_type=task.task_type, prompt=task.prompt,
                context=(task.context or "") + "\n\nBound evidence packet:\n" +
                json.dumps(packet, ensure_ascii=False))


def _rebuild(task: Task, data: dict) -> dict:
    from agent_arena.phase9_review import assess_case, case_key, position_from_result
    from agent_arena.phase9_models import CONTRACT_VERSION, ReviewPosition
    if data.get("case_id") != case_key(task) or data.get("contract_version") != CONTRACT_VERSION:
        raise ValueError("Phase9 case/contract binding changed")
    positions = []
    for old in data.get("positions", []):
        pos = position_from_result(task, AgentResult.model_validate(old["agent_result"]),
                                   old["run_id"], old["origin"])
        if pos != ReviewPosition.model_validate(old):
            raise ValueError("Phase9 position content or binding changed")
        positions.append(pos)
    from agent_arena.phase9_models import Disagreement
    prior = [Disagreement.model_validate(c).model_copy(update={"resolution": "unresolved"})
             for c in data.get("conflicts", [])]
    fresh = assess_case(task, positions, prior_conflicts=prior).model_dump(mode="json")
    if any(t["field"] == "position.identity" for t in fresh["triggers"]) or any(
        "Prior conflict" in reason for reason in fresh["reasons"]
    ):
        raise ValueError("Phase9 position/conflict history is inconsistent")
    fresh.update({k: data[k] for k in ("attempts", "adjudications", "final_position_id") if k in data})
    # A completed countercheck is an executed comparison, never a majority verdict.
    attempts = list({a["kind"]: a for a in fresh.get("attempts", [])}.values())
    if any(a.get("status") == "completed" for a in attempts):
        fresh["execution_status"] = "completed"
        if fresh.get("mandatory") and fresh["route"] == "REVIEW_RECOMMENDED":
            fresh.update(route="HUMAN_REVIEW_REQUIRED", review_state="pending")
            fresh["reasons"].append("Material uncertainty remains after the bounded countercheck.")
    if any(a.get("status") in {"failed", "begun"} for a in attempts):
        fresh["execution_status"] = "failed"
    if fresh.get("mandatory") and any(a.get("status") in {
        "denied", "failed", "begun", "rejected"} for a in attempts):
        fresh.update(route="UNRESOLVED", review_state="unresolved")
    return fresh


def _validate_execution_history(data: dict) -> None:
    positions = {p["position_id"]: p for p in data.get("positions", [])}
    consumed = set()
    for attempt in data.get("attempts", []):
        kind, status = attempt.get("kind"), attempt.get("status")
        if kind not in {"counterreview", "stability"} or status not in {
            "denied", "rejected", "begun", "completed", "failed"
        }:
            raise ValueError("Invalid execution receipt")
        if status == "denied":
            continue
        if kind in consumed:
            raise ValueError("More than one consumed attempt/variant for a case slot")
        consumed.add(kind)
        if status in {"rejected", "begun"}:
            continue
        position = positions.get(attempt.get("position_id"))
        expected_origin = "model_review" if kind == "counterreview" else "stability"
        if not position or position["origin"] != expected_origin or not attempt.get("attempt_id"):
            raise ValueError("Completed/failed execution lacks its bound review position/attempt")
        decisions = [d for d in data.get("adjudications", []) if
                     d.get("selected_position_id") == position["position_id"] and
                     d.get("reviewer_type") == "model" and d.get("origin") == "offline_comparison"]
        if not decisions or any((d.get("outcome") == "failed") != (status == "failed") for d in decisions):
            raise ValueError("Execution receipt lacks a matching recorded model adjudication")


def _require_covered(incoming: RunRecord, stored_data: dict) -> None:
    """Every supplied carrier must be an unchanged part of the selected history.

    Derived routing can be recomputed; recorded positions, receipts and decisions
    cannot be replaced by matching hashes/IDs with different content. This is a
    coverage check, not a merge or a timestamp-based choice of authority.
    """
    from agent_arena.phase9_review import case_key, position_from_result
    if stored_data.get("case_id") != case_key(incoming.task):
        raise ValueError("Different bound case; both histories retained unchanged")
    originals = [p["agent_result"] for p in stored_data["positions"] if p["origin"] == "original"]
    if any(position_from_result(incoming.task, r.agent_result, incoming.run_id).agent_result not in originals
           for r in incoming.results):
        raise ValueError("Different original analysis for existing case; both histories retained unchanged")

    def indexed(data, field, key):
        result = {}
        for item in data.get(field, []):
            value = dict(item)
            if field == "conflicts":
                value["resolution"] = "unresolved"  # Reapplied from validated human decisions.
            identity = value[key]
            if identity in result:
                raise ValueError(f"Duplicate {field} identity in review history")
            result[identity] = value
        return result

    def ordered_subset(submitted, stored):
        remaining = iter(stored)
        return all(any(item == candidate for candidate in remaining) for item in submitted)

    carriers = [incoming.metadata["phase9"]] if incoming.metadata.get("phase9") else []
    carriers.extend(r.agent_result.phase9 for r in incoming.results if r.agent_result.phase9)
    for submitted in carriers:
        checked = revalidate_assessment(incoming.task, submitted)
        if checked.get("history_validation") == "invalid":
            raise ValueError("Submitted Phase9 history is invalid; no replacement performed")
        # Runner positions are created before a RunRecord has its real run ID.
        # Only this receipt/decision/conflict-free bootstrap may acquire that ID;
        # compare every remaining field, not merely its raw hash.
        bootstrap = not any(checked.get(k) for k in ("attempts", "adjudications", "conflicts")) and all(
            p["origin"] == "original" and p["run_id"] == "initial" for p in checked["positions"])
        if bootstrap:
            checked = deepcopy(checked)
            for p in checked["positions"]:
                content = {k: v for k, v in p.items() if k not in {"position_id", "run_id"}}
                match = next((other for other in stored_data["positions"] if
                              {k: v for k, v in other.items() if k not in {"position_id", "run_id"}} == content), None)
                if match is not None:
                    p.update(position_id=match["position_id"], run_id=match["run_id"])
        for field, key in (("positions", "position_id"), ("conflicts", "disagreement_id"),
                           ("adjudications", "adjudication_id")):
            stored = indexed(stored_data, field, key)
            if any(stored.get(identity) != value for identity, value in indexed(checked, field, key).items()):
                raise ValueError(f"Submitted review history differs in {field}; both retained unchanged")
        # Receipts lack universal IDs (e.g. denied requests). Preserve their exact
        # content, order and multiplicity, as well as the order of decisions.
        for field in ("attempts", "adjudications"):
            if not ordered_subset(checked.get(field, []), stored_data.get(field, [])):
                raise ValueError(f"Submitted review history differs in {field}; both retained unchanged")


def revalidate_assessment(task: Task, data: dict, record: RunRecord | None = None) -> dict:
    """Fail closed on stale payloads, without execution or manufacturing decisions."""
    from agent_arena.phase9_review import position_from_result
    try:
        if not isinstance(data, dict):
            raise TypeError("Phase9 history is not an object")
        if data.get("history_validation") == "invalid":
            raise ValueError("Previously invalidated history remains retained and non-authoritative")
        fresh = _rebuild(task, data)
        _validate_execution_history(fresh)
        if record is not None:
            raw_hashes = {p["raw_sha256"] for p in fresh["positions"] if p["origin"] == "original"}
            for evaluated in record.results:
                pos = position_from_result(task, evaluated.agent_result, record.run_id)
                if pos.raw_sha256 not in raw_hashes:
                    raise ValueError("Current original analysis is absent from Phase9 history")
        # Human records are separately validated below; model text has no authority.
        if fresh.get("adjudications"):
            from agent_arena.phase9_adjudication import apply_adjudications
            fresh = apply_adjudications(task, fresh)
            if fresh.get("history_validation") == "invalid":
                raise ValueError("Adjudication proof failed validation; execution is unverified")
        return fresh
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        fresh = deepcopy(data) if isinstance(data, dict) else {"unvalidated_history": deepcopy(data)}
        fresh.update(technical_status="incomplete", route="UNRESOLVED", mandatory=True,
                     review_state="unresolved", execution_status="failed", history_validation="invalid")
        fresh.setdefault("uncertainty", []).append(f"Invalid Phase9 history: {exc}; execution is unverified.")
        if fresh.get("final_position_id"):
            fresh["invalidated_final_position_id"] = fresh.pop("final_position_id")
        if fresh.get("final_decision"):
            fresh["invalidated_final_decision"] = fresh.pop("final_decision")
        return fresh


@contextmanager
def _case_lease(base: Path, case_id: str):
    directory = base / "phase9"
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / f"{case_id}.lock").open("a") as lease:
        try:
            fcntl.flock(lease, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError("Case already leased; no concurrent review") from exc
        try:
            yield directory
        finally:
            fcntl.flock(lease, fcntl.LOCK_UN)


def _save(base: Path, path: Path, record: RunRecord) -> None:
    from agent_arena.audit_trail import log_decision, read_decisions
    from agent_arena.bounded_harness_mission import atomic
    atomic(path, record.model_dump(mode="json"))
    known = {d.decision_id for d in read_decisions(base)}
    for decision in record.metadata["phase9"].get("adjudications", []):
        if decision["adjudication_id"] not in known:
            log_decision(DecisionEntry(
                decision_id=decision["adjudication_id"], timestamp=decision["timestamp"],
                decision_type="disagreement_resolution", source_module="disagreement_lab",
                target=record.metadata["phase9"]["case_id"], target_kind="case",
                decision="accepted" if decision["outcome"] == "resolved" else "deferred",
                reason=decision["reason"], reviewer=decision["reviewer_provenance"],
                evidence_summary=json.dumps(decision, sort_keys=True),
                before_state="Original positions retained", after_state=decision["outcome"],
            ), base)


def replay_review(task: Task, *, base_dir: Path) -> RunRecord:
    from agent_arena.phase9_review import case_key
    path = Path(base_dir) / "phase9" / f"{case_key(task)}.json"
    record = RunRecord.model_validate_json(path.read_text())
    from agent_arena.phase9_pipeline import refresh_run_phase9
    if case_key(record.task) != case_key(task):
        raise ValueError("Stored replay belongs to a different case")
    return refresh_run_phase9(record)


def execute_review(record: RunRecord, provider: OfflineReviewProvider | None = None, *,
                   base_dir: Path, authorized: bool = False, budget_calls: int = 0,
                   kind: str = "counterreview", variant: dict | None = None) -> RunRecord:
    """Explicit bounded request. Defaults deny; replay is a separate read-only API."""
    from agent_arena.bounded_harness_mission import BudgetLedger, atomic
    from agent_arena.phase9_pipeline import assess_run, attach_assessment, refresh_run_phase9
    from agent_arena.phase9_review import case_key, position_from_result
    from agent_arena.runner import STUDY_FORENSICS_PROMPT_VERSION_PHASE9, run_agent
    if kind not in {"counterreview", "stability"}:
        raise ValueError("Unknown review kind")
    if type(budget_calls) is not int or not 0 <= budget_calls <= 2:
        raise ValueError("Offline grant must be between zero and two calls")
    # AA-P10-LIVE/1.0: exact live/replay reviewer types run under their own ledger binding mode;
    # every other provider keeps the historical offline rules and texts unchanged.
    from agent_arena.phase10_live import review_mode
    live_mode = review_mode(provider)
    base = Path(base_dir)
    case_id = case_key(record.task)
    with _case_lease(base, case_id) as directory:
        path = directory / f"{case_id}.json"
        if path.exists():
            saved = RunRecord.model_validate_json(path.read_text())
            data = revalidate_assessment(record.task, saved.metadata["phase9"], saved)
            if data.get("history_validation") == "invalid" or not data.get("positions"):
                raise ValueError("Invalid stored case; no fresh budget")
            _require_covered(saved, data)
            _require_covered(record, data)
            record = saved
        else:
            # RunRecord is already the persistence format; a missing sidecar is no reset.
            if record.metadata.get("phase9") or any(r.agent_result.phase9 for r in record.results):
                data = refresh_run_phase9(record).metadata["phase9"]
            else:
                data = assess_run(record)
            if data.get("history_validation") == "invalid":
                raise ValueError("Invalid submitted history retained unchanged; no execution")
            _require_covered(record, data)
        attempts = data.setdefault("attempts", [])
        ledger_path = directory / f"{case_id}.ledger.json"
        binding = {"case_id": case_id, "contract_version": "AA-P9/1.0", "mode": live_mode or "offline"}
        policy = {"max_attempts": 2, "per_slot": 1, "attempt_microusd": 0, "total_microusd": 0}
        slots = [{"slot_key": "counterreview"}, {"slot_key": "stability"}]
        ledger = BudgetLedger(ledger_path, binding, slots, policy=policy) if ledger_path.exists() else None
        executed_history = any(a["status"] in {"begun", "completed", "failed"} for a in attempts)
        existing_rejections = [a for a in attempts if a["status"] == "rejected"]
        if existing_rejections:
            # Older checkpoints recorded rejection only in the outcome sidecar.
            # Preserve every validated rejection before *any* early return, also
            # when reopening the counterreview or importing without a sidecar.
            if ledger is None and executed_history:
                raise ValueError("Governance ledger missing for executed history; rejected variant cannot be resumed")
            ledger = ledger or BudgetLedger(ledger_path, binding, slots, create=True, policy=policy)
            durable = deepcopy(ledger.data)
            rejected_variants = durable.setdefault("rejected_variants", {})
            for receipt in existing_rejections:
                previous = rejected_variants.get(receipt["kind"])
                if previous is not None and previous != receipt:
                    raise ValueError("Rejected variant differs from durable governance history")
                rejected_variants[receipt["kind"]] = deepcopy(receipt)
            if durable != ledger.data:
                atomic(ledger_path, durable)
                ledger.data = durable
        if any(a["kind"] == kind and a["status"] in {"begun", "completed", "failed", "rejected"}
               for a in attempts):
            result = attach_assessment(record, data)
            if not path.exists():
                _save(base, path, result)
            return result
        if data["route"] == "AUTO_RESOLVABLE" or not record.results:
            result = attach_assessment(record, data)
            _save(base, path, result)
            return result
        original_positions = [position_from_result(record.task, r.agent_result, record.run_id)
                              for r in record.results]
        reason = None
        try:
            packet = build_challenge(record.task, original_positions[0], original_positions[1:])
        except ValueError as exc:
            reason = str(exc)
            packet = {"original_claim": record.task.prompt, "original_context": record.task.context}
        if kind == "stability" and reason is None:
            proposed = stability_variant(packet) if variant is None else variant
            reason = validate_variant(packet, proposed)
            packet = proposed
        rejected = ledger.data.get("rejected_variants", {}).get(kind) if ledger else None
        if rejected is not None:
            # A rejected variant consumes the variant choice, not a provider call.
            # Recover that exact receipt if the outcome sidecar was lost.
            attempts.append(deepcopy(rejected))
            data = revalidate_assessment(record.task, data, record)
            result = attach_assessment(record, data)
            _save(base, path, result)
            return result
        if ledger is None and executed_history:
            reason = "Governance ledger missing for executed history; no fresh allowance created."
        if reason is None and (authorized is not True or budget_calls == 0):
            reason = ("No live review authorization/remaining case allowance." if live_mode else
                      "No offline authorization/remaining call budget; live API budget is zero.")
        if reason is None and live_mode is None and type(provider) is not OfflineReviewProvider:
            reason = "Missing recorded offline reviewer; live/arbitrary providers are not authorized."
        if reason is None:
            ledger = ledger or BudgetLedger(ledger_path, binding, slots, create=True, policy=policy)
            if any(a["slot_key"] == kind for a in ledger.data["attempts"]):
                reason = "Attempt already reserved in durable ledger; missing outcome remains unresolved."
            elif len(ledger.data["attempts"]) >= budget_calls:
                reason = "Offline grant exhausted."
            elif kind == "stability" and "counterreview" not in ledger.data["terminal_keys"]:
                reason = "Counterreview must be attempted before the single stability variant."
        attempt = {"kind": kind, "status": "rejected" if kind == "stability" and reason
                   and reason.startswith("Rejected:") else "denied", "reason": reason or "",
                   "timestamp": _now(), "packet_sha256": _hash(packet),
                   "code_version": code_version(), "contract_version": "AA-P9/1.0"}
        attempts.append(attempt)
        if attempt["status"] == "rejected":
            ledger = ledger or BudgetLedger(ledger_path, binding, slots, create=True, policy=policy)
            # Same lease and atomic JSON mechanism as reservations; persist before
            # the sidecar so interruption cannot allow a replacement variant.
            durable = deepcopy(ledger.data)
            durable.setdefault("rejected_variants", {})[kind] = deepcopy(attempt)
            atomic(ledger_path, durable)
        if reason:
            data.update(route="UNRESOLVED", review_state="unresolved")
            result = attach_assessment(record, data)
            _save(base, path, result)
            return result
        review_task = _challenge_task(record.task, packet)
        request_hash = _hash(review_task.model_dump(mode="json"))
        # Atomic pessimistic reservation before runner/provider, including crash paths.
        aid = ledger.reserve(kind, request_hash, request_hash)
        attempt.update(status="begun", attempt_id=aid)
        _save(base, path, attach_assessment(record, data))
        # A live/replay reviewer carries the review prompt bound to its profile revision.
        response = run_agent(provider, review_task, prompt_version=provider.prompt_version if live_mode
                             else STUDY_FORENSICS_PROMPT_VERSION_PHASE9)
        origin = "model_review" if kind == "counterreview" else "stability"
        position = position_from_result(record.task, response, f"{record.run_id}:{kind}", origin)
        data["positions"].append(position.model_dump(mode="json"))
        failed = bool(response.error or not response.parse_ok or
                      position.phase8.get("technical_status") != "completed" or
                      position.phase8.get("taxonomy", {}).get("technical_status") == "incomplete")
        attempt.update(status="failed" if failed else "completed",
                       reason=response.error or ("Incomplete Phase8 review" if failed else ""),
                       position_id=position.position_id,
                       independence="First verdict withheld; shared original sources and extraction IDs. " +
                       ("Live output of the same model profile under AA-P10-LIVE/1.0; no empirical model "
                        "independence established." if live_mode == "live" else
                        "Offline replay of an earlier live output; no new generation and no empirical model "
                        "independence established." if live_mode == "live_replay" else
                        "Recorded offline output; no empirical model independence established."))
        ledger.observe(aid, state=attempt["status"], raw_response_sha256=position.raw_sha256)
        ledger.terminal(kind, position.raw_sha256)
        data = _rebuild(record.task, data)
        from agent_arena.phase9_adjudication import model_adjudication, apply_adjudications
        decision = model_adjudication(record.task, data, position.position_id,
                                      timestamp=_now(), code_version=code_version())
        data.setdefault("adjudications", []).append(decision.model_dump(mode="json"))
        data = apply_adjudications(record.task, data)
        result = attach_assessment(record, data)
        _save(base, path, result)
        return result


def submit_human_review(record: RunRecord, *, base_dir: Path, selected_position_id: str,
                        reviewer_provenance: str, reason: str,
                        corrected_raw_output: str | None = None) -> RunRecord:
    """Explicit host submission; never inferred from model JSON or free-text approval."""
    from agent_arena.output_contract import parse_structured_output
    from agent_arena.phase9_pipeline import attach_assessment, refresh_run_phase9
    from agent_arena.phase9_review import case_key, position_from_result
    from agent_arena.phase9_adjudication import apply_adjudications, human_adjudication
    base = Path(base_dir)
    with _case_lease(base, case_key(record.task)) as directory:
        path = directory / f"{case_key(record.task)}.json"
        if path.exists():
            saved = RunRecord.model_validate_json(path.read_text())
            stored = revalidate_assessment(saved.task, saved.metadata["phase9"], saved)
            if stored.get("history_validation") == "invalid":
                raise ValueError("Stored history is invalid; human review cannot waive it")
            _require_covered(saved, stored)
            _require_covered(record, stored)
            record = saved
        data = refresh_run_phase9(record).metadata["phase9"]
        if data.get("history_validation") == "invalid":
            raise ValueError("Invalid history cannot be adjudicated")
        parent_id = None
        if corrected_raw_output is not None:
            if not any(p["position_id"] == selected_position_id for p in data["positions"]):
                raise ValueError("Correction parent is not an existing position")
            parsed, diagnostic = parse_structured_output(corrected_raw_output)
            response = AgentResult(provider="host_human_submission", raw_output=corrected_raw_output,
                                   parsed=parsed, parse_ok=diagnostic.ok)
            position = position_from_result(record.task, response,
                                            f"{record.run_id}:correction:{len(data['positions'])}",
                                            "human_correction")
            parent_id = selected_position_id
            selected_position_id = position.position_id
            data["positions"].append(position.model_dump(mode="json"))
            data = _rebuild(record.task, data)
        decision = human_adjudication(
            record.task, data, selected_position_id, reviewer_provenance=reviewer_provenance,
            reason=reason, timestamp=_now(), code_version=code_version(),
            corrected_parent_position_id=parent_id,
        )
        data.setdefault("adjudications", []).append(decision.model_dump(mode="json"))
        data = apply_adjudications(record.task, data)
        result = attach_assessment(record, data)
        _save(base, path, result)
        return result
