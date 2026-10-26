"""Phase9 entry/output wiring. Refresh and replay never invoke a provider."""
from __future__ import annotations

from agent_arena.schemas import AgentResult, RunRecord, Task, TaskType


def initial_assessment(task: Task, result: AgentResult, run_id: str = "initial") -> dict:
    if task.task_type != TaskType.STUDY_FORENSICS:
        return {}
    from agent_arena.phase9_review import assess_case, position_from_result
    return assess_case(task, [position_from_result(task, result, run_id)]).model_dump(mode="json")


def historical_view() -> dict:
    return {"contract_version": "AA-P9/1.0", "technical_status": "not_executed",
            "route": "UNRESOLVED", "execution_status": "not_executed",
            "review_state": "pending", "mandatory": True, "conflicts": [], "triggers": [],
            "uncertainty": ["Historical record: Phase9 was not executed."], "positions": [],
            "adjudications": []}


def assess_run(record: RunRecord) -> dict:
    from agent_arena.phase9_review import assess_case, position_from_result
    positions = [position_from_result(record.task, r.agent_result, record.run_id)
                 for r in record.results]
    return assess_case(record.task, positions).model_dump(mode="json")


def attach_assessment(record: RunRecord, assessment: dict) -> RunRecord:
    """Return a separate output layer; never replace raw/original results."""
    results = [r.model_copy(update={"agent_result": r.agent_result.model_copy(
        update={"phase9": assessment})}) for r in record.results]
    return record.model_copy(update={"results": results,
                                     "metadata": {**record.metadata, "phase9": assessment}})


def refresh_run_phase9(record: RunRecord) -> RunRecord:
    if record.task.task_type != TaskType.STUDY_FORENSICS:
        return record
    cached = record.metadata.get("phase9")
    if cached:
        from agent_arena.phase9_runtime import revalidate_assessment
        assessment = revalidate_assessment(record.task, cached, record)
    elif any(r.agent_result.phase9 for r in record.results):
        histories = [r.agent_result.phase9 for r in record.results
                     if r.agent_result.phase9.get("attempts") or
                     r.agent_result.phase9.get("adjudications")]
        if histories:
            from agent_arena.phase9_runtime import revalidate_assessment
            assessment = revalidate_assessment(record.task, histories[0], record)
        else:
            assessment = assess_run(record)
    else:
        assessment = historical_view()
    from agent_arena.phase9_runtime import _require_covered
    from copy import deepcopy
    try:
        if assessment.get("history_validation") == "invalid":
            raise ValueError("Selected Phase9 history is invalid")
        if assessment.get("positions"):
            _require_covered(record, assessment)
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        # Keep every original carrier in place. Do not attach an older/invalid
        # metadata choice over the result histories that revealed the conflict.
        assessment = deepcopy(assessment)
        assessment.update(technical_status="incomplete", route="UNRESOLVED", mandatory=True,
                          review_state="unresolved", execution_status="failed", history_validation="invalid")
        assessment.setdefault("uncertainty", []).append(f"Invalid Phase9 history: {exc}")
        if assessment.get("final_position_id"):
            assessment["invalidated_final_position_id"] = assessment.pop("final_position_id")
        if assessment.get("final_decision"):
            assessment["invalidated_final_decision"] = assessment.pop("final_decision")
        return record.model_copy(update={"metadata": {**record.metadata, "phase9": assessment}})
    return attach_assessment(record, assessment)


def render_phase9(data: dict | None) -> str:
    data = data or historical_view()
    lines = [f"**Phase 9 review:** `{data.get('route', 'UNRESOLVED')}`; "
             f"analysis `{data.get('technical_status', 'not_executed')}`; "
             f"execution `{data.get('execution_status', 'not_executed')}`; "
             f"review `{data.get('review_state', 'pending')}`; "
             f"mandatory `{data.get('mandatory', True)}`."]
    if data.get("history_validation") == "invalid":
        lines.append("UNVALIDATED HISTORY retained below: no approval or execution claim is accepted.")
    for conflict in data.get("conflicts", []):
        lines.append("Conflict: " + str(conflict))
    for trigger in data.get("triggers", []):
        lines.append("Review trigger: " + str(trigger))
    for decision in data.get("adjudications", []):
        if not isinstance(decision, dict):
            lines.append("Unvalidated adjudication: " + str(decision))
            continue
        lines.append(f"Adjudication `{decision.get('adjudication_id')}`: "
                     f"{decision.get('reviewer_type')} / {decision.get('outcome')}; "
                     f"{decision.get('reason')}")
    for attempt in data.get("attempts", []):
        if not isinstance(attempt, dict):
            lines.append("Unvalidated attempt: " + str(attempt))
            continue
        lines.append(f"Attempt `{attempt.get('kind')}`: {attempt.get('status')}; "
                     f"{attempt.get('reason', '')}")
    if data.get("final_position_id"):
        lines.append(f"Separate adjudicated position: `{data['final_position_id']}`.")
        selected = next((p for p in data.get("positions", [])
                         if p["position_id"] == data["final_position_id"]), None)
        if selected:
            phase8 = selected["phase8"]
            lines.append(f"Final adjudicated scientific state: **{phase8.get('composite_state', 'unknown').upper()}**; "
                         f"technical `{phase8.get('technical_status')}`; derived taxonomy "
                         f"`{phase8.get('derived_label') or 'unknown'}`. Original judgments below remain historical layers.")
    lines.extend("Uncertainty: " + str(s) for s in data.get("uncertainty", []))
    lines.extend(str(s) for s in data.get("reasons", []))
    lines.append("Offline review consistency only; no empirical reviewer-quality or release claim.")
    return "\n\n".join(lines)
