"""Versioned decision layers over immutable Phase9 positions; no provider calls or IAM."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime
from typing import Literal

from pydantic import Field

from inspektorium.audit.review.models import (
    CONTRACT_VERSION,
    Disagreement,
    ReviewPosition,
    StrictModel,
)
from inspektorium.audit.review.routing import assess_case, case_key
from inspektorium.audit.schemas import Task


def _hash(value):
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        ).encode()
    ).hexdigest()


class AdjudicationRecord(StrictModel):
    adjudication_id: str
    case_id: str
    run_id: str
    claim_id: str
    proposition_ids: list[str]
    position_ids: list[str]
    original_position_ids: list[str]
    conflict_ids: list[str]
    conflict_types: list[str]
    evidence_ids: list[str]
    reviewer_type: Literal["model", "human"]
    reviewer_provenance: str = Field(min_length=1)
    origin: Literal["offline_comparison", "host_human_submission"]
    outcome: Literal["considered", "failed", "resolved", "deferred"]
    selected_position_id: str
    corrected_parent_position_id: str | None = None
    reason: str = Field(min_length=1)
    timestamp: str
    code_version: str = Field(min_length=1)
    contract_version: Literal["AA-P9/1.3"] = CONTRACT_VERSION
    position_fingerprints: dict[str, str]
    original_decisions: list[dict]
    review_decision: dict
    independence: str


def _snapshot(position: ReviewPosition) -> dict:
    return {
        "position_id": position.position_id,
        "raw_sha256": position.raw_sha256,
        "original_model_label": position.phase8.get("original_model_label"),
        "derived_label": position.phase8.get("derived_label"),
        "scientific_state": position.phase8.get("composite_state", "unknown"),
        "technical_status": position.phase8.get("technical_status", "not_executed"),
    }


def _checked(task, data):
    positions = [ReviewPosition.model_validate(p) for p in data.get("positions", [])]
    prior = [
        Disagreement.model_validate(c).model_copy(update={"resolution": "unresolved"})
        for c in data.get("conflicts", [])
    ]
    checked = assess_case(task, positions, prior_conflicts=prior)
    if data.get("case_id") != case_key(task) or not positions:
        raise ValueError("Adjudication lacks bound case/positions")
    if any(t.field == "position.identity" for t in checked.triggers) or any(
        "Prior conflict" in reason for reason in checked.reasons
    ):
        raise ValueError("Invalid identity/history cannot be adjudicated")
    return checked


def _selected(checked, position_id):
    selected = next(
        (p for p in checked.positions if p.position_id == position_id), None
    )
    if selected is None:
        raise ValueError("Selected position is absent from the bound history")
    return selected


_OFFLINE_MODEL_PROVENANCE = "Built-in offline recording via existing runner/parser"


def _review_mode(position) -> str:
    evidence = (position.agent_result or {}).get("execution_evidence") or {}
    current = evidence.get("current_execution")
    if current in {"live_generation", "offline_replay"} and (
        evidence.get("replay_of_unsent_request")
        or (evidence.get("request_sent") is False and not evidence.get("attempt_ids"))
    ):
        return "unsent live" if current == "live_generation" else "replayed unsent live"
    return {"live_generation": "live", "offline_replay": "replayed live"}.get(
        current, "recorded offline"
    )


def _model_review_statements(selected, originals) -> tuple[str, str]:
    """Provenance and independence of a model review, derived from the bound positions.

    Package B (P9-F2, BF1): a live or replayed-live review, a live review request that was never
    sent, and a conflict packet that disclosed both positions are stated as such; the recorded
    offline blind review keeps its historical text.
    """
    mode = _review_mode(selected)
    disclosed = any(p.phase8.get("model_host_conflicts") for p in originals)
    model = (selected.agent_result or {}).get("model") or selected.model
    basis = ", shared source/extraction basis; no empirical model independence or human approval."
    if mode in {"unsent live", "replayed unsent live"}:
        reason = ((selected.agent_result or {}).get("execution_evidence") or {}).get(
            "denial_reason"
        ) or "not stated"
        provenance = (
            "Live review request not sent under AA-P10-LIVE/1.0"
            if mode == "unsent live"
            else "Offline replay of a live review request that was never sent (AA-P10-LIVE/1.0)"
        )
        return (
            f"{provenance} ({model}; {reason}); no review output",
            "No model review output: nothing was generated or supplied; the review stays open.",
        )
    provenance = {
        "recorded offline": _OFFLINE_MODEL_PROVENANCE,
        "live": f"Live model review under AA-P10-LIVE/1.0 ({selected.provider}/{model})",
        "replayed live": f"Offline replay of a recorded live model review under AA-P10-LIVE/1.0 ({model})",
    }[mode]
    if mode == "recorded offline" and not disclosed:
        return provenance, "Recorded offline comparison: first verdict withheld" + basis
    supplied = (
        "model and host positions of the open conflicts supplied as untrusted data"
        if disclosed
        else "first verdict withheld"
    )
    return provenance, f"Host comparison of a {mode} model review: {supplied}" + basis


def _human_candidate(task, selected):
    assessment = assess_case(task, [selected])
    if (
        assessment.technical_status != "completed"
        or assessment.mandatory
        or selected.phase8.get("composite_state") == "unknown"
    ):
        raise ValueError(
            "Human selection cannot waive Phase8 controls or material UNKNOWN"
        )


def _make(
    task,
    data,
    position_id,
    *,
    reviewer_type,
    reviewer_provenance,
    reason,
    timestamp,
    code_version,
    corrected_parent_position_id=None,
):
    checked = _checked(task, data)
    selected = _selected(checked, position_id)
    if (
        not reviewer_provenance.strip()
        or not reason.strip()
        or not code_version.strip()
    ):
        raise ValueError(
            "Explicit reviewer provenance, reason and code version required"
        )
    if datetime.fromisoformat(timestamp).tzinfo is None:
        raise ValueError("Adjudication timestamp must carry a timezone")
    human = reviewer_type == "human"
    if human:
        _human_candidate(task, selected)
        if corrected_parent_position_id is not None:
            _selected(checked, corrected_parent_position_id)
            if (
                selected.origin != "human_correction"
                or corrected_parent_position_id == position_id
            ):
                raise ValueError(
                    "Correction must be a new human layer with an existing parent"
                )
        elif selected.origin == "human_correction":
            raise ValueError("Human correction requires its parent version")
    elif selected.origin not in {"model_review", "stability"}:
        raise ValueError("Model adjudication requires a host-recorded review position")
    originals = [p for p in checked.positions if p.origin == "original"]
    if not human:
        reviewer_provenance, model_independence = _model_review_statements(
            selected, originals
        )
    ids = sorted(p.position_id for p in checked.positions)
    failed = (
        selected.phase8.get("technical_status") != "completed"
        or selected.phase8.get("taxonomy", {}).get("technical_status") == "incomplete"
    )
    evidence_ids = set()
    for position in checked.positions:
        evidence = (position.forensic_record or {}).get("evidence", [])
        if isinstance(evidence, list):
            evidence_ids.update(
                e["evidence_id"]
                for e in evidence
                if isinstance(e, dict) and isinstance(e.get("evidence_id"), str)
            )
    record = AdjudicationRecord(
        adjudication_id="",
        case_id=checked.case_id,
        run_id=selected.run_id,
        claim_id=selected.claim_id
        or next((p.claim_id for p in originals if p.claim_id), checked.case_id),
        proposition_ids=sorted(
            {
                p["proposition_id"]
                for pos in checked.positions
                for p in pos.phase8.get("propositions", [])
            }
        ),
        position_ids=ids,
        original_position_ids=sorted(p.position_id for p in originals),
        conflict_ids=sorted(c.disagreement_id for c in checked.conflicts),
        conflict_types=sorted({c.dimension for c in checked.conflicts}),
        evidence_ids=sorted(evidence_ids),
        reviewer_type=reviewer_type,
        reviewer_provenance=reviewer_provenance,
        origin="host_human_submission" if human else "offline_comparison",
        outcome="resolved" if human else "failed" if failed else "considered",
        selected_position_id=position_id,
        corrected_parent_position_id=corrected_parent_position_id,
        reason=reason,
        timestamp=timestamp,
        code_version=code_version,
        position_fingerprints={
            p.position_id: _hash(p.model_dump(mode="json")) for p in checked.positions
        },
        original_decisions=[
            _snapshot(p) for p in sorted(originals, key=lambda p: p.position_id)
        ],
        review_decision=_snapshot(selected),
        independence=(
            "Explicit host-submitted human adjudication; provenance is not identity authentication."
            if human
            else model_independence
        ),
    )
    record.adjudication_id = "p9decision:" + _hash(record.model_dump(mode="json"))[:24]
    return record


def model_adjudication(
    task: Task,
    data: dict,
    review_position_id: str,
    *,
    timestamp: str,
    code_version: str,
) -> AdjudicationRecord:
    # The provenance text is derived from the bound review position inside _make.
    return _make(
        task,
        data,
        review_position_id,
        reviewer_type="model",
        reviewer_provenance=_OFFLINE_MODEL_PROVENANCE,
        reason="Targeted comparison: "
        + "; ".join(t["reason"] for t in data.get("triggers", [])),
        timestamp=timestamp,
        code_version=code_version,
    )


def human_adjudication(
    task: Task,
    data: dict,
    selected_position_id: str,
    *,
    reviewer_provenance: str,
    reason: str,
    timestamp: str,
    code_version: str,
    corrected_parent_position_id: str | None = None,
) -> AdjudicationRecord:
    return _make(
        task,
        data,
        selected_position_id,
        reviewer_type="human",
        reviewer_provenance=reviewer_provenance,
        reason=reason,
        timestamp=timestamp,
        code_version=code_version,
        corrected_parent_position_id=corrected_parent_position_id,
    )


def apply_adjudications(task: Task, data: dict) -> dict:
    """Revalidate decision bindings on replay. Old human approval cannot cover new positions."""
    result = deepcopy(data)
    result.pop("final_position_id", None)
    result.pop("final_decision", None)
    try:
        checked = _checked(task, data)
        if checked.mandatory and result.get("route") == "AUTO_RESOLVABLE":
            result.update(
                route=checked.route, mandatory=True, review_state=checked.review_state
            )
        positions = {p.position_id: p for p in checked.positions}
        current_ids = set(positions)
        conflicts = {c.disagreement_id: c for c in checked.conflicts}
        resolved_ids = set()
        latest_covering = None
        for raw in data.get("adjudications", []):
            decision = AdjudicationRecord.model_validate(raw)
            if not set(decision.position_ids) <= current_ids:
                raise ValueError("Adjudication references missing historical positions")
            subset = {
                "case_id": checked.case_id,
                "positions": [
                    positions[i].model_dump(mode="json") for i in decision.position_ids
                ],
                "conflicts": [
                    c.model_dump(mode="json")
                    for c in checked.conflicts
                    if set(p.position_id for p in c.positions)
                    <= set(decision.position_ids)
                ],
            }
            expected = _make(
                task,
                subset,
                decision.selected_position_id,
                reviewer_type=decision.reviewer_type,
                reviewer_provenance=decision.reviewer_provenance,
                reason=decision.reason,
                timestamp=decision.timestamp,
                code_version=decision.code_version,
                corrected_parent_position_id=decision.corrected_parent_position_id,
            )
            if expected != decision:
                raise ValueError(
                    "Adjudication content/fingerprints differ from its bound positions"
                )
            if decision.reviewer_type == "human":
                resolved_ids.update(decision.conflict_ids)
                if set(decision.position_ids) == current_ids and set(conflicts) <= set(
                    decision.conflict_ids
                ):
                    latest_covering = decision
        result["conflicts"] = [
            c.model_copy(
                update={
                    "resolution": "adjudicated"
                    if c.disagreement_id in resolved_ids
                    else "unresolved"
                }
            ).model_dump(mode="json")
            for c in checked.conflicts
        ]
        if latest_covering is not None:
            result.update(
                route="AUTO_RESOLVABLE",
                mandatory=False,
                review_state="adjudicated",
                final_position_id=latest_covering.selected_position_id,
                final_decision=latest_covering.review_decision,
            )
        elif result.get("review_state") == "adjudicated":
            result.update(
                route=checked.route,
                mandatory=checked.mandatory,
                review_state=checked.review_state,
            )
    except (ValueError, KeyError, TypeError) as exc:
        result.update(
            route="UNRESOLVED",
            mandatory=True,
            review_state="unresolved",
            history_validation="invalid",
            execution_status="failed",
        )
        result.setdefault("uncertainty", []).append(
            f"Invalid adjudication history: {exc}"
        )
    return result
