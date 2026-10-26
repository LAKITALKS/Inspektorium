"""Postmortem engine — causal failure analysis for agent-arena v0.6.

Combines run data (RunJournalEntry) with outcome data (OutcomeRecord)
to produce a PostmortemReport with causal findings, contributing factors,
mitigating factors, lessons, and a verdict.
"""

from __future__ import annotations

from agent_arena.schemas import (
    FailureCategory,
    OutcomeRecord,
    PostmortemFinding,
    PostmortemReport,
    RunJournalEntry,
)


# ---------------------------------------------------------------------------
# Severity mapping for failure categories
# ---------------------------------------------------------------------------

_CRITICAL_FAILURES = {
    FailureCategory.WRONG_ANSWER.value,
    FailureCategory.ARITHMETIC_ERROR.value,
    FailureCategory.INTERMEDIATE_NUMERIC_ERROR.value,
    FailureCategory.BASE_RATE_OMISSION.value,
    FailureCategory.RULE_MISREAD.value,
}

_MAJOR_FAILURES = {
    FailureCategory.LOGIC_ERROR.value,
    FailureCategory.SELF_CONTRADICTION.value,
    FailureCategory.OVERCONFIDENT_FORECAST.value,
    FailureCategory.SHRINKAGE_FAILURE.value,
    FailureCategory.NARRATIVE_OVERREACH.value,
    FailureCategory.RIGHT_ANSWER_WRONG_REASONING.value,
    FailureCategory.ACCIDENTAL_CORRECTNESS.value,
    FailureCategory.STEP_ANSWER_MISMATCH.value,
    FailureCategory.VERBAL_NUMERIC_CONTRADICTION.value,
}

_MITIGATING_FLAGS = {
    "calibration_note",
    "acknowledged_uncertainty",
    "substantive_self_check",
}


# ---------------------------------------------------------------------------
# Postmortem generation
# ---------------------------------------------------------------------------

def generate_postmortem(
    entry: RunJournalEntry,
    outcome: OutcomeRecord,
) -> PostmortemReport:
    """Generate a forensic postmortem from a journal entry and outcome."""

    causal: list[PostmortemFinding] = []
    contributing: list[PostmortemFinding] = []
    mitigating: list[PostmortemFinding] = []
    lessons: list[str] = []

    was_correct = outcome.was_correct

    # --- Classify failures by causal role ---
    for fc in entry.failure_categories:
        if fc in _CRITICAL_FAILURES:
            causal.append(PostmortemFinding(
                finding_type="causal_failure",
                category=fc,
                description=_failure_description(fc, was_correct),
                severity="critical",
                confidence="HIGH CONFIDENCE",
            ))
        elif fc in _MAJOR_FAILURES:
            contributing.append(PostmortemFinding(
                finding_type="contributing_factor",
                category=fc,
                description=_failure_description(fc, was_correct),
                severity="major",
                confidence="MEDIUM CONFIDENCE",
            ))
        else:
            contributing.append(PostmortemFinding(
                finding_type="contributing_factor",
                category=fc,
                description=_failure_description(fc, was_correct),
                severity="moderate",
                confidence="HEURISTIC",
            ))

    # --- Forensic flags as contributing or mitigating ---
    for ft in entry.forensic_flag_types:
        if ft in _MITIGATING_FLAGS:
            mitigating.append(PostmortemFinding(
                finding_type="mitigating_factor",
                category=ft,
                description=f"Forensic flag '{ft}' indicates partial self-awareness",
                severity="minor",
                confidence="HEURISTIC",
            ))
        else:
            contributing.append(PostmortemFinding(
                finding_type="contributing_factor",
                category=ft,
                description=f"Forensic flag '{ft}' may have contributed to outcome",
                severity="minor",
                confidence="HEURISTIC",
            ))

    # --- Reasoning integrity findings ---
    ri_class = entry.reasoning_integrity_class
    if ri_class == "accidental" and was_correct:
        causal.append(PostmortemFinding(
            finding_type="causal_failure",
            category="accidental_correctness",
            description="Correct answer but reasoning is unreliable — accidental",
            severity="major",
            confidence="MEDIUM CONFIDENCE",
        ))
    elif ri_class == "brittle" and was_correct:
        contributing.append(PostmortemFinding(
            finding_type="contributing_factor",
            category="brittle_reasoning",
            description="Correct answer but reasoning has fragile steps",
            severity="moderate",
            confidence="MEDIUM CONFIDENCE",
        ))
    elif ri_class == "well_supported" and was_correct:
        mitigating.append(PostmortemFinding(
            finding_type="mitigating_factor",
            category="well_supported_reasoning",
            description="Reasoning integrity is solid and well-supported",
            severity="minor",
            confidence="HIGH CONFIDENCE",
        ))

    # --- Contradiction analysis ---
    if entry.n_contradictions > 0:
        sev = "critical" if entry.n_contradictions >= 2 else "major"
        causal.append(PostmortemFinding(
            finding_type="causal_failure",
            category="contradiction",
            description=f"{entry.n_contradictions} internal contradiction(s) detected",
            severity=sev,
            confidence="HIGH CONFIDENCE",
        ))

    # --- Intermediate errors ---
    if entry.n_intermediate_errors > 0:
        contributing.append(PostmortemFinding(
            finding_type="contributing_factor",
            category="intermediate_errors",
            description=f"{entry.n_intermediate_errors} intermediate arithmetic error(s)",
            severity="major",
            confidence="HIGH CONFIDENCE",
        ))

    # --- Lessons ---
    lessons = _derive_lessons(entry, outcome, causal, contributing)

    # --- Verdict ---
    verdict = _build_verdict(entry, outcome, causal, contributing, mitigating)

    return PostmortemReport(
        run_id=entry.run_id,
        task_id=entry.task_id,
        agent_id=entry.agent_id,
        outcome=outcome,
        was_correct=was_correct,
        reasoning_integrity=ri_class,
        decision_category=entry.decision_category,
        total_score=entry.total_score,
        probable_causal_failures=causal,
        contributing_factors=contributing,
        mitigating_factors=mitigating,
        lessons=lessons,
        verdict=verdict,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _failure_description(fc: str, was_correct: bool | None) -> str:
    """Generate a concise failure description for a postmortem."""
    label = fc.replace("_", " ")
    if was_correct is False:
        return f"{label} — contributed to incorrect outcome"
    elif was_correct is True:
        return f"{label} — present despite correct outcome"
    return f"{label} — outcome unknown"


def _derive_lessons(
    entry: RunJournalEntry,
    outcome: OutcomeRecord,
    causal: list[PostmortemFinding],
    contributing: list[PostmortemFinding],
) -> list[str]:
    """Derive actionable lessons from postmortem findings."""
    lessons = []

    # Lesson from causal failures
    causal_cats = {f.category for f in causal}
    if "wrong_answer" in causal_cats:
        lessons.append("Answer verification failed — check deterministic correctness first")
    if "base_rate_omission" in causal_cats:
        lessons.append("Base rate was ignored — always anchor on prior probability")
    if "arithmetic_error" in causal_cats or "intermediate_numeric_error" in causal_cats:
        lessons.append("Arithmetic errors in reasoning chain — verify calculations step by step")
    if "rule_misread" in causal_cats:
        lessons.append("Resolution rule was misread — parse task rules carefully")
    if "contradiction" in causal_cats:
        lessons.append("Internal contradictions detected — improve self-consistency checking")
    if "accidental_correctness" in causal_cats:
        lessons.append("Correct answer was accidental — reasoning does not support conclusion")

    # Lesson from reasoning integrity
    if entry.reasoning_integrity_class == "brittle":
        lessons.append("Reasoning is brittle — strengthen intermediate steps")

    # Forecast-specific lessons
    contributing_cats = {f.category for f in contributing}
    if "overconfident_forecast" in causal_cats or "overconfident_forecast" in contributing_cats:
        lessons.append("Overconfident forecast — calibrate probability estimates more carefully")
    if "narrative_overreach" in contributing_cats:
        lessons.append("Narrative drove the estimate — separate evidence from storytelling")
    if "shrinkage_failure" in contributing_cats:
        lessons.append("Extreme probability without shrinkage — apply base rate anchoring")

    return lessons


def _build_verdict(
    entry: RunJournalEntry,
    outcome: OutcomeRecord,
    causal: list[PostmortemFinding],
    contributing: list[PostmortemFinding],
    mitigating: list[PostmortemFinding],
) -> str:
    """Build a concise verdict string."""
    was_correct = outcome.was_correct
    ri = entry.reasoning_integrity_class
    n_causal = len(causal)
    n_mitigating = len(mitigating)

    if was_correct is True:
        if ri == "well_supported" and n_causal == 0:
            return "correct and well-supported"
        elif ri == "accidental":
            return "correct but accidental — reasoning does not support conclusion"
        elif ri == "brittle":
            return "correct but brittle — reasoning has fragile dependencies"
        elif n_causal > 0:
            cats = ", ".join(f.category for f in causal[:3])
            return f"correct despite issues: {cats}"
        return "correct with minor concerns"
    elif was_correct is False:
        if n_causal > 0:
            primary = causal[0].category
            return f"incorrect — primary cause: {primary}"
        return "incorrect — no clear causal failure identified"
    else:
        if n_causal > 0:
            return f"outcome unknown — {n_causal} causal concern(s) identified"
        return "outcome unknown — insufficient data for verdict"
