"""Run journal — JSONL-based persistence layer for agent-arena v0.6.

Converts RunRecord/EvaluatedResult into flat RunJournalEntry records,
persists them to a local JSONL file, and supports querying by agent,
task, or task family. No external database. No infrastructure.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from agent_arena.confidence_validity import INVALID, MISSING, VALID, classify_confidence
from agent_arena.schemas import (
    EvaluatedResult,
    OutcomeRecord,
    RunJournalEntry,
    RunRecord,
)


# ---------------------------------------------------------------------------
# Default journal location
# ---------------------------------------------------------------------------

_DEFAULT_JOURNAL_DIR = ".agent_arena"
_JOURNAL_FILE = "journal.jsonl"
_OUTCOME_FILE = "outcomes.jsonl"


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _journal_path(base_dir: str | Path | None = None) -> Path:
    base = Path(base_dir) if base_dir else Path(_DEFAULT_JOURNAL_DIR)
    _ensure_dir(base)
    return base / _JOURNAL_FILE


def _outcome_path(base_dir: str | Path | None = None) -> Path:
    base = Path(base_dir) if base_dir else Path(_DEFAULT_JOURNAL_DIR)
    _ensure_dir(base)
    return base / _OUTCOME_FILE


# ---------------------------------------------------------------------------
# RunRecord → RunJournalEntry conversion
# ---------------------------------------------------------------------------

def _extract_entry(
    run_id: str,
    timestamp: str,
    task_id: str,
    task_family: str,
    task_type: str,
    result: EvaluatedResult,
) -> RunJournalEntry:
    """Convert a single EvaluatedResult into a flat journal entry."""
    ar = result.agent_result
    p = ar.parsed
    s = result.scores

    agent_id = ar.provider
    model = ar.model

    # Failure categories
    failure_cats = list({f.category for f in result.failures})

    # Forensic flag types
    flag_types = list({f.flag_type for f in result.forensic_flags})

    # Reasoning integrity class
    ri = result.reasoning_integrity
    ri_class = ri.get("classification", "") if ri else ""

    # Forecast fields
    decision_cat = ""
    prob_est = None
    if p:
        decision_cat = p.decision_category
        prob_est = p.probability_estimate

    if p is None:
        confidence = None
        confidence_state = INVALID
    else:
        confidence = p.confidence
        confidence_state = p.confidence_state
        if confidence_state not in (VALID, MISSING, INVALID):
            # Direct/manual AgentResponse constructors may predate the explicit
            # state field.  Classify their in-memory value before persistence.
            confidence_state = classify_confidence(confidence)

    # Contradiction count
    n_contradictions = sum(
        1 for f in result.consistency_findings if f.status == "fail"
    )

    # Intermediate errors
    n_int_errors = 0
    if ri:
        n_int_errors = ri.get("n_intermediate_errors", 0)

    return RunJournalEntry(
        run_id=run_id,
        timestamp=timestamp,
        task_id=task_id,
        task_family=task_family,
        task_type=task_type,
        agent_id=agent_id,
        model=model,
        total_score=s.total,
        correctness=s.correctness,
        support_strength=s.support_strength,
        structural_reasoning=s.structural_reasoning,
        insight_depth=s.insight_depth,
        mechanism_quality=s.mechanism_quality,
        self_monitoring_quality=s.self_monitoring_quality,
        failure_categories=failure_cats,
        forensic_flag_types=flag_types,
        reasoning_integrity_class=ri_class,
        decision_category=decision_cat,
        probability_estimate=prob_est,
        confidence=confidence,
        confidence_state=confidence_state,
        final_answer=p.final_answer[:200] if p else "",
        n_contradictions=n_contradictions,
        n_intermediate_errors=n_int_errors,
    )


def entries_from_record(record: RunRecord) -> list[RunJournalEntry]:
    """Extract all journal entries from a RunRecord."""
    task = record.task
    entries = []
    for result in record.results:
        entry = _extract_entry(
            run_id=record.run_id,
            timestamp=record.timestamp,
            task_id=task.id,
            task_family=task.task_family or "",
            task_type=task.task_type.value if task.task_type else "",
            result=result,
        )
        entries.append(entry)
    return entries


# ---------------------------------------------------------------------------
# JSONL persistence — journal entries
# ---------------------------------------------------------------------------

def append_entries(
    entries: list[RunJournalEntry],
    base_dir: str | Path | None = None,
) -> Path:
    """Append journal entries to the JSONL file. Returns the file path."""
    path = _journal_path(base_dir)
    with open(path, "a", encoding="utf-8") as f:
        for entry in entries:
            f.write(entry.model_dump_json() + "\n")
    return path


def append_record(
    record: RunRecord,
    base_dir: str | Path | None = None,
) -> Path:
    """Convert a RunRecord to journal entries and append. Returns file path."""
    entries = entries_from_record(record)
    return append_entries(entries, base_dir)


def read_entries(base_dir: str | Path | None = None) -> list[RunJournalEntry]:
    """Read all journal entries from the JSONL file."""
    path = _journal_path(base_dir)
    if not path.exists():
        return []
    entries = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            entries.append(RunJournalEntry(**data))
    return entries


# ---------------------------------------------------------------------------
# Query helpers
# ---------------------------------------------------------------------------

def query_by_agent(
    agent_id: str,
    base_dir: str | Path | None = None,
) -> list[RunJournalEntry]:
    """Return all journal entries for a specific agent."""
    return [e for e in read_entries(base_dir) if e.agent_id == agent_id]


def query_by_task(
    task_id: str,
    base_dir: str | Path | None = None,
) -> list[RunJournalEntry]:
    """Return all journal entries for a specific task."""
    return [e for e in read_entries(base_dir) if e.task_id == task_id]


def query_by_task_family(
    task_family: str,
    base_dir: str | Path | None = None,
) -> list[RunJournalEntry]:
    """Return all journal entries for a specific task family."""
    return [e for e in read_entries(base_dir) if e.task_family == task_family]


def query_by_run(
    run_id: str,
    base_dir: str | Path | None = None,
) -> list[RunJournalEntry]:
    """Return all journal entries for a specific run."""
    return [e for e in read_entries(base_dir) if e.run_id == run_id]


# ---------------------------------------------------------------------------
# JSONL persistence — outcome records
# ---------------------------------------------------------------------------

def append_outcome(
    outcome: OutcomeRecord,
    base_dir: str | Path | None = None,
) -> Path:
    """Append an outcome record to the outcomes JSONL file."""
    path = _outcome_path(base_dir)
    with open(path, "a", encoding="utf-8") as f:
        f.write(outcome.model_dump_json() + "\n")
    return path


def read_outcomes(base_dir: str | Path | None = None) -> list[OutcomeRecord]:
    """Read all outcome records."""
    path = _outcome_path(base_dir)
    if not path.exists():
        return []
    outcomes = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            outcomes.append(OutcomeRecord(**data))
    return outcomes


def find_outcome(
    run_id: str,
    task_id: str,
    agent_id: str,
    base_dir: str | Path | None = None,
) -> OutcomeRecord | None:
    """Find a specific outcome record by run+task+agent."""
    for o in read_outcomes(base_dir):
        if o.run_id == run_id and o.task_id == task_id and o.agent_id == agent_id:
            return o
    return None
