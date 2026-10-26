"""Tests for journal.py — run persistence layer (v0.6)."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from agent_arena.confidence_validity import INVALID, MISSING, VALID
from agent_arena.evaluator import evaluate_result
from agent_arena.journal import (
    append_entries,
    append_outcome,
    append_record,
    entries_from_record,
    find_outcome,
    query_by_agent,
    query_by_run,
    query_by_task,
    query_by_task_family,
    read_entries,
    read_outcomes,
)
from agent_arena.output_contract import parse_structured_output
from agent_arena.schemas import (
    AgentResponse,
    AgentResult,
    DiagnosticScores,
    EvaluatedResult,
    FailureInstance,
    ForensicFlag,
    OutcomeRecord,
    RunJournalEntry,
    RunRecord,
    Task,
    TaskType,
    Difficulty,
    ConsistencyFinding,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_parsed(**overrides) -> AgentResponse:
    defaults = dict(
        final_answer="42",
        steps=["step 1", "step 2"],
        confidence=0.8,
    )
    defaults.update(overrides)
    return AgentResponse(**defaults)


def _make_result(provider="agent-a", model="gpt-4", **parsed_kw) -> AgentResult:
    return AgentResult(
        provider=provider,
        model=model,
        parsed=_make_parsed(**parsed_kw),
        parse_ok=True,
    )


def _make_evaluated(
    provider="agent-a",
    model="gpt-4",
    correctness=0.8,
    failures=None,
    flags=None,
    consistency_findings=None,
    reasoning_integrity=None,
    **parsed_kw,
) -> EvaluatedResult:
    scores = DiagnosticScores(
        correctness=correctness,
        support_strength=0.6,
        structural_reasoning=0.7,
        insight_depth=0.5,
        mechanism_quality=0.4,
        self_monitoring_quality=0.5,
    )
    return EvaluatedResult(
        agent_result=_make_result(provider, model, **parsed_kw),
        scores=scores,
        failures=failures or [],
        forensic_flags=flags or [],
        consistency_findings=consistency_findings or [],
        reasoning_integrity=reasoning_integrity or {},
    )


def _make_task(task_id="task-001", task_family="reasoning", task_type=TaskType.CLOSED_WITH_REASONING) -> Task:
    return Task(
        id=task_id,
        title="Test Task",
        domain="test",
        difficulty=Difficulty.MEDIUM,
        task_type=task_type,
        prompt="What is 6x7?",
        task_family=task_family,
    )


def _make_record(
    run_id="run-001",
    task_id="task-001",
    task_family="reasoning",
    results=None,
) -> RunRecord:
    task = _make_task(task_id=task_id, task_family=task_family)
    return RunRecord(
        run_id=run_id,
        task=task,
        results=results or [_make_evaluated()],
        timestamp="2024-01-15T10:00:00Z",
    )


def _journal_entry_from_raw(raw: str) -> tuple[RunJournalEntry, object]:
    parsed, diag = parse_structured_output(raw)
    agent_result = AgentResult(
        provider="offline", model="fake", raw_output=raw,
        parsed=parsed, parse_ok=diag.ok,
    )
    task = _make_task(task_family="solid", task_type=TaskType.STUDY_FORENSICS)
    evaluated = evaluate_result(task, agent_result)
    record = _make_record(task_family="solid", results=[evaluated])
    return entries_from_record(record)[0], diag


# ---------------------------------------------------------------------------
# Test: entries_from_record
# ---------------------------------------------------------------------------

class TestEntriesFromRecord:
    def test_basic_extraction(self):
        record = _make_record()
        entries = entries_from_record(record)
        assert len(entries) == 1
        e = entries[0]
        assert e.run_id == "run-001"
        assert e.task_id == "task-001"
        assert e.task_family == "reasoning"
        assert e.agent_id == "agent-a"
        assert e.model == "gpt-4"
        assert e.correctness == 0.8
        assert e.final_answer == "42"

    def test_multiple_results(self):
        results = [
            _make_evaluated(provider="agent-a"),
            _make_evaluated(provider="agent-b", model="claude-3"),
        ]
        record = _make_record(results=results)
        entries = entries_from_record(record)
        assert len(entries) == 2
        assert entries[0].agent_id == "agent-a"
        assert entries[1].agent_id == "agent-b"

    def test_failure_categories_extracted(self):
        failures = [
            FailureInstance(category="wrong_answer", severity="critical", description="wrong"),
            FailureInstance(category="logic_error", severity="major", description="bad logic"),
        ]
        record = _make_record(results=[_make_evaluated(failures=failures)])
        entries = entries_from_record(record)
        assert "wrong_answer" in entries[0].failure_categories
        assert "logic_error" in entries[0].failure_categories

    def test_forensic_flags_extracted(self):
        flags = [
            ForensicFlag(flag_type="calibration_gap", description="gap"),
        ]
        record = _make_record(results=[_make_evaluated(flags=flags)])
        entries = entries_from_record(record)
        assert "calibration_gap" in entries[0].forensic_flag_types

    def test_reasoning_integrity_class(self):
        ri = {"classification": "brittle", "n_intermediate_errors": 2}
        record = _make_record(results=[_make_evaluated(reasoning_integrity=ri)])
        entries = entries_from_record(record)
        assert entries[0].reasoning_integrity_class == "brittle"
        assert entries[0].n_intermediate_errors == 2

    def test_forecast_fields(self):
        record = _make_record(
            task_family="forecasting_decision",
            results=[_make_evaluated(
                probability_estimate=0.45,
                decision_category="no_trade",
            )],
        )
        entries = entries_from_record(record)
        assert entries[0].probability_estimate == 0.45
        assert entries[0].decision_category == "no_trade"

    def test_contradiction_count(self):
        findings = [
            ConsistencyFinding(check_type="test", status="fail", description="bad"),
            ConsistencyFinding(check_type="test2", status="fail", description="bad2"),
            ConsistencyFinding(check_type="test3", status="pass", description="ok"),
        ]
        record = _make_record(results=[_make_evaluated(consistency_findings=findings)])
        entries = entries_from_record(record)
        assert entries[0].n_contradictions == 2

    @pytest.mark.parametrize(
        ("raw_confidence", "expected_state", "expected_confidence"),
        [
            (95, INVALID, None),
            ("95", INVALID, None),
            ("0.85", INVALID, None),
            (True, INVALID, None),
            (False, INVALID, None),
            (float("nan"), INVALID, None),
            (float("inf"), INVALID, None),
            (float("-inf"), INVALID, None),
            (-0.1, INVALID, None),
            (1.5, INVALID, None),
            (0.0, VALID, 0.0),
            (0.85, VALID, 0.85),
        ],
    )
    def test_confidence_contract_survives_parser_to_journal(
        self, raw_confidence, expected_state, expected_confidence
    ):
        raw = json.dumps({"final_answer": "solid", "confidence": raw_confidence})
        entry, diag = _journal_entry_from_raw(raw)

        assert diag.confidence_state == expected_state
        assert entry.confidence_state == expected_state
        assert entry.confidence == expected_confidence

    def test_parser_failure_is_not_numeric_zero(self):
        entry, diag = _journal_entry_from_raw("not json")

        assert diag.ok is False
        assert entry.confidence is None
        assert entry.confidence_state == INVALID


# ---------------------------------------------------------------------------
# Test: JSONL persistence
# ---------------------------------------------------------------------------

class TestJournalPersistence:
    def test_append_and_read(self, tmp_path):
        entry = RunJournalEntry(
            run_id="r1", timestamp="2024-01-01T00:00:00Z",
            task_id="t1", agent_id="a1",
        )
        append_entries([entry], base_dir=tmp_path)
        loaded = read_entries(base_dir=tmp_path)
        assert len(loaded) == 1
        assert loaded[0].run_id == "r1"
        assert loaded[0].task_id == "t1"

    def test_append_is_additive(self, tmp_path):
        e1 = RunJournalEntry(run_id="r1", timestamp="t1", task_id="t1", agent_id="a1")
        e2 = RunJournalEntry(run_id="r2", timestamp="t2", task_id="t2", agent_id="a2")
        append_entries([e1], base_dir=tmp_path)
        append_entries([e2], base_dir=tmp_path)
        loaded = read_entries(base_dir=tmp_path)
        assert len(loaded) == 2

    def test_read_empty_file(self, tmp_path):
        loaded = read_entries(base_dir=tmp_path)
        assert loaded == []

    def test_append_record_integration(self, tmp_path):
        record = _make_record()
        path = append_record(record, base_dir=tmp_path)
        assert path.exists()
        loaded = read_entries(base_dir=tmp_path)
        assert len(loaded) == 1
        assert loaded[0].run_id == "run-001"

    def test_preserves_all_fields(self, tmp_path):
        entry = RunJournalEntry(
            run_id="r1", timestamp="2024-01-01T00:00:00Z",
            task_id="t1", task_family="forecasting",
            task_type="forecasting_decision",
            agent_id="a1", model="gpt-4",
            total_score=65.3, correctness=0.8,
            failure_categories=["wrong_answer", "logic_error"],
            forensic_flag_types=["calibration_gap"],
            reasoning_integrity_class="brittle",
            decision_category="forecast",
            probability_estimate=0.75,
            confidence=0.9,
            confidence_state=VALID,
            final_answer="Yes",
            n_contradictions=1,
            n_intermediate_errors=2,
        )
        append_entries([entry], base_dir=tmp_path)
        loaded = read_entries(base_dir=tmp_path)[0]
        assert loaded.total_score == 65.3
        assert loaded.failure_categories == ["wrong_answer", "logic_error"]
        assert loaded.probability_estimate == 0.75
        assert loaded.n_contradictions == 1

    def test_new_validity_aware_roundtrip_preserves_zero_and_valid_value(self, tmp_path):
        entries = [
            RunJournalEntry(
                run_id="zero", timestamp="t", task_id="t0", agent_id="a",
                confidence=0.0, confidence_state=VALID,
            ),
            RunJournalEntry(
                run_id="valid", timestamp="t", task_id="t1", agent_id="a",
                confidence=0.85, confidence_state=VALID,
            ),
        ]
        append_entries(entries, base_dir=tmp_path)

        loaded = read_entries(base_dir=tmp_path)
        assert (loaded[0].confidence, loaded[0].confidence_state) == (0.0, VALID)
        assert (loaded[1].confidence, loaded[1].confidence_state) == (0.85, VALID)

    def test_legacy_absent_confidence_does_not_deserialize_as_zero(self, tmp_path):
        payload = {
            "run_id": "legacy", "timestamp": "t", "task_id": "t", "agent_id": "a"
        }
        (tmp_path / "journal.jsonl").write_text(json.dumps(payload) + "\n")

        loaded = read_entries(base_dir=tmp_path)[0]
        assert loaded.confidence is None
        assert loaded.confidence_state == MISSING

    @pytest.mark.parametrize("legacy_confidence", [0.0, 0.85])
    def test_legacy_numeric_without_state_fails_closed(self, tmp_path, legacy_confidence):
        payload = {
            "run_id": "legacy-value", "timestamp": "t", "task_id": "t", "agent_id": "a",
            "confidence": legacy_confidence,
        }
        (tmp_path / "journal.jsonl").write_text(json.dumps(payload) + "\n")

        loaded = read_entries(base_dir=tmp_path)[0]
        assert loaded.confidence is None
        assert loaded.confidence_state == INVALID

    @pytest.mark.parametrize("stored_state", ["UNKNOWN", "valid", "", None, 7])
    def test_malformed_stored_confidence_state_fails_closed(self, stored_state):
        entry = RunJournalEntry(
            run_id="bad", timestamp="t", task_id="t", agent_id="a",
            confidence=0.85, confidence_state=stored_state,
        )
        assert entry.confidence is None
        assert entry.confidence_state == INVALID


# ---------------------------------------------------------------------------
# Test: Query helpers
# ---------------------------------------------------------------------------

class TestQueryHelpers:
    def _seed(self, tmp_path):
        entries = [
            RunJournalEntry(run_id="r1", timestamp="t1", task_id="t1", task_family="reasoning", agent_id="a1"),
            RunJournalEntry(run_id="r1", timestamp="t1", task_id="t2", task_family="forecasting", agent_id="a2"),
            RunJournalEntry(run_id="r2", timestamp="t2", task_id="t1", task_family="reasoning", agent_id="a1"),
            RunJournalEntry(run_id="r2", timestamp="t2", task_id="t3", task_family="reasoning", agent_id="a1"),
        ]
        append_entries(entries, base_dir=tmp_path)

    def test_query_by_agent(self, tmp_path):
        self._seed(tmp_path)
        result = query_by_agent("a1", base_dir=tmp_path)
        assert len(result) == 3
        assert all(e.agent_id == "a1" for e in result)

    def test_query_by_task(self, tmp_path):
        self._seed(tmp_path)
        result = query_by_task("t1", base_dir=tmp_path)
        assert len(result) == 2

    def test_query_by_task_family(self, tmp_path):
        self._seed(tmp_path)
        result = query_by_task_family("reasoning", base_dir=tmp_path)
        assert len(result) == 3

    def test_query_by_run(self, tmp_path):
        self._seed(tmp_path)
        result = query_by_run("r1", base_dir=tmp_path)
        assert len(result) == 2

    def test_query_nonexistent_agent(self, tmp_path):
        self._seed(tmp_path)
        result = query_by_agent("unknown", base_dir=tmp_path)
        assert result == []


# ---------------------------------------------------------------------------
# Test: Outcome persistence
# ---------------------------------------------------------------------------

class TestOutcomePersistence:
    def test_append_and_read_outcome(self, tmp_path):
        outcome = OutcomeRecord(
            run_id="r1", task_id="t1", agent_id="a1",
            resolved_outcome="correct", was_correct=True,
            decision_quality="good_call",
        )
        append_outcome(outcome, base_dir=tmp_path)
        loaded = read_outcomes(base_dir=tmp_path)
        assert len(loaded) == 1
        assert loaded[0].was_correct is True
        assert loaded[0].decision_quality == "good_call"

    def test_find_outcome(self, tmp_path):
        o1 = OutcomeRecord(run_id="r1", task_id="t1", agent_id="a1", resolved_outcome="correct")
        o2 = OutcomeRecord(run_id="r1", task_id="t2", agent_id="a1", resolved_outcome="incorrect")
        append_outcome(o1, base_dir=tmp_path)
        append_outcome(o2, base_dir=tmp_path)
        found = find_outcome("r1", "t1", "a1", base_dir=tmp_path)
        assert found is not None
        assert found.resolved_outcome == "correct"

    def test_find_outcome_missing(self, tmp_path):
        found = find_outcome("r1", "t1", "a1", base_dir=tmp_path)
        assert found is None
