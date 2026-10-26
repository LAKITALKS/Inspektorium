"""Tests for postmortem.py — causal failure analysis (v0.6)."""

from __future__ import annotations

import pytest

from agent_arena.postmortem import generate_postmortem
from agent_arena.schemas import (
    OutcomeRecord,
    RunJournalEntry,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _entry(**overrides) -> RunJournalEntry:
    defaults = dict(
        run_id="r1",
        timestamp="2024-01-15T10:00:00Z",
        task_id="t1",
        task_family="reasoning",
        task_type="closed_with_reasoning",
        agent_id="agent-a",
        model="gpt-4",
        total_score=65.0,
        correctness=0.8,
        failure_categories=[],
        forensic_flag_types=[],
        reasoning_integrity_class="well_supported",
        n_contradictions=0,
        n_intermediate_errors=0,
    )
    defaults.update(overrides)
    return RunJournalEntry(**defaults)


def _outcome(**overrides) -> OutcomeRecord:
    defaults = dict(
        run_id="r1",
        task_id="t1",
        agent_id="agent-a",
        resolved_outcome="correct",
        was_correct=True,
    )
    defaults.update(overrides)
    return OutcomeRecord(**defaults)


# ---------------------------------------------------------------------------
# Test: Basic postmortem generation
# ---------------------------------------------------------------------------

class TestPostmortemBasic:
    def test_correct_well_supported(self):
        pm = generate_postmortem(_entry(), _outcome())
        assert pm.was_correct is True
        assert pm.verdict == "correct and well-supported"
        assert len(pm.mitigating_factors) > 0  # well_supported is mitigating
        assert pm.reasoning_integrity == "well_supported"

    def test_incorrect_with_wrong_answer(self):
        e = _entry(failure_categories=["wrong_answer"], correctness=0.0)
        o = _outcome(was_correct=False, resolved_outcome="incorrect")
        pm = generate_postmortem(e, o)
        assert pm.was_correct is False
        assert "wrong_answer" in pm.verdict
        assert any(f.category == "wrong_answer" for f in pm.probable_causal_failures)

    def test_outcome_unknown(self):
        o = _outcome(was_correct=None)
        pm = generate_postmortem(_entry(), o)
        assert pm.was_correct is None
        assert "unknown" in pm.verdict


# ---------------------------------------------------------------------------
# Test: Causal failure classification
# ---------------------------------------------------------------------------

class TestCausalClassification:
    def test_critical_failures_are_causal(self):
        critical = ["wrong_answer", "arithmetic_error", "intermediate_numeric_error",
                     "base_rate_omission", "rule_misread"]
        for fc in critical:
            e = _entry(failure_categories=[fc])
            o = _outcome(was_correct=False, resolved_outcome="incorrect")
            pm = generate_postmortem(e, o)
            causal_cats = [f.category for f in pm.probable_causal_failures]
            assert fc in causal_cats, f"{fc} should be causal"

    def test_major_failures_are_contributing(self):
        major = ["logic_error", "self_contradiction", "overconfident_forecast",
                 "narrative_overreach"]
        for fc in major:
            e = _entry(failure_categories=[fc])
            o = _outcome(was_correct=False, resolved_outcome="incorrect")
            pm = generate_postmortem(e, o)
            contributing_cats = [f.category for f in pm.contributing_factors]
            assert fc in contributing_cats, f"{fc} should be contributing"

    def test_minor_failures_are_heuristic(self):
        e = _entry(failure_categories=["padding"])
        o = _outcome()
        pm = generate_postmortem(e, o)
        contributing = [f for f in pm.contributing_factors if f.category == "padding"]
        assert len(contributing) == 1
        assert contributing[0].confidence == "HEURISTIC"


# ---------------------------------------------------------------------------
# Test: Reasoning integrity in postmortem
# ---------------------------------------------------------------------------

class TestReasoningIntegrity:
    def test_accidental_correctness(self):
        e = _entry(reasoning_integrity_class="accidental")
        o = _outcome(was_correct=True)
        pm = generate_postmortem(e, o)
        assert any(
            f.category == "accidental_correctness"
            for f in pm.probable_causal_failures
        )
        assert "accidental" in pm.verdict

    def test_brittle_reasoning(self):
        e = _entry(reasoning_integrity_class="brittle")
        o = _outcome(was_correct=True)
        pm = generate_postmortem(e, o)
        assert any(
            f.category == "brittle_reasoning"
            for f in pm.contributing_factors
        )
        assert "brittle" in pm.verdict

    def test_well_supported_is_mitigating(self):
        e = _entry(reasoning_integrity_class="well_supported")
        o = _outcome(was_correct=True)
        pm = generate_postmortem(e, o)
        assert any(
            f.category == "well_supported_reasoning"
            for f in pm.mitigating_factors
        )


# ---------------------------------------------------------------------------
# Test: Contradictions and intermediate errors
# ---------------------------------------------------------------------------

class TestContradictionsAndErrors:
    def test_contradictions_are_causal(self):
        e = _entry(n_contradictions=2)
        o = _outcome(was_correct=False, resolved_outcome="incorrect")
        pm = generate_postmortem(e, o)
        contra = [f for f in pm.probable_causal_failures if f.category == "contradiction"]
        assert len(contra) == 1
        assert contra[0].severity == "critical"

    def test_single_contradiction_is_major(self):
        e = _entry(n_contradictions=1)
        o = _outcome()
        pm = generate_postmortem(e, o)
        contra = [f for f in pm.probable_causal_failures if f.category == "contradiction"]
        assert contra[0].severity == "major"

    def test_intermediate_errors_are_contributing(self):
        e = _entry(n_intermediate_errors=3)
        o = _outcome()
        pm = generate_postmortem(e, o)
        ie = [f for f in pm.contributing_factors if f.category == "intermediate_errors"]
        assert len(ie) == 1
        assert "3" in ie[0].description


# ---------------------------------------------------------------------------
# Test: Forensic flags
# ---------------------------------------------------------------------------

class TestForensicFlags:
    def test_mitigating_flags(self):
        e = _entry(forensic_flag_types=["calibration_note", "acknowledged_uncertainty"])
        o = _outcome()
        pm = generate_postmortem(e, o)
        assert len(pm.mitigating_factors) >= 2  # flags + well_supported

    def test_non_mitigating_flags_are_contributing(self):
        e = _entry(forensic_flag_types=["pattern_match_suspect"])
        o = _outcome()
        pm = generate_postmortem(e, o)
        flag_contribs = [f for f in pm.contributing_factors if f.category == "pattern_match_suspect"]
        assert len(flag_contribs) == 1


# ---------------------------------------------------------------------------
# Test: Lessons
# ---------------------------------------------------------------------------

class TestLessons:
    def test_wrong_answer_lesson(self):
        e = _entry(failure_categories=["wrong_answer"])
        o = _outcome(was_correct=False, resolved_outcome="incorrect")
        pm = generate_postmortem(e, o)
        assert any("verification" in l.lower() for l in pm.lessons)

    def test_base_rate_lesson(self):
        e = _entry(failure_categories=["base_rate_omission"])
        o = _outcome(was_correct=False, resolved_outcome="incorrect")
        pm = generate_postmortem(e, o)
        assert any("base rate" in l.lower() for l in pm.lessons)

    def test_brittle_lesson(self):
        e = _entry(reasoning_integrity_class="brittle")
        o = _outcome()
        pm = generate_postmortem(e, o)
        assert any("brittle" in l.lower() for l in pm.lessons)

    def test_overconfidence_lesson(self):
        e = _entry(failure_categories=["overconfident_forecast"])
        o = _outcome()
        pm = generate_postmortem(e, o)
        assert any("overconfident" in l.lower() or "calibrate" in l.lower() for l in pm.lessons)


# ---------------------------------------------------------------------------
# Test: Verdict
# ---------------------------------------------------------------------------

class TestVerdict:
    def test_correct_no_issues(self):
        pm = generate_postmortem(_entry(), _outcome())
        assert pm.verdict == "correct and well-supported"

    def test_correct_with_issues(self):
        e = _entry(failure_categories=["wrong_answer"])  # causal present
        o = _outcome(was_correct=True)
        pm = generate_postmortem(e, o)
        assert "correct despite" in pm.verdict

    def test_incorrect_primary_cause(self):
        e = _entry(failure_categories=["arithmetic_error"])
        o = _outcome(was_correct=False, resolved_outcome="incorrect")
        pm = generate_postmortem(e, o)
        assert "incorrect" in pm.verdict
        assert "arithmetic_error" in pm.verdict
