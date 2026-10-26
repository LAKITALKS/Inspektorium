"""Gen 2 Calibrate — calibration proposal engine for agent-arena v0.6.7.

Generates review-ready calibration proposals from journal entries and
insights. Suggests, never mutates. Every proposal includes evidence,
confidence, and recommended action.

Proposal types:
A. fp_reduction      — triggers / phrases that correlate with false positives
B. gold_review       — cases that may need gold label reconsideration
C. category_refinement — categories that are too broad or unstable
D. model_confusion   — stable model label confusions worth documenting
E. data_gap          — categories / shapes that need more cases

Data sources: RunJournalEntry (journal.jsonl), InsightsReport (optional).
"""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone

from agent_arena.confidence_validity import confidence_value_if_valid
from agent_arena.insights import generate_insights, _entropy
from agent_arena.schemas import (
    CalibrationProposal,
    CalibrationReport,
    InsightsReport,
    RunJournalEntry,
)


# ---------------------------------------------------------------------------
# Thresholds (conservative — prefer precision over recall)
# ---------------------------------------------------------------------------

# FP reduction
_FP_MIN_OCCURRENCES = 2           # need >= 2 FP runs to propose
_FP_MIN_FREQUENCY = 0.3           # >= 30% of runs in that family

# Gold review
_GOLD_REVIEW_DISAGREEMENT = 0.4   # entropy >= 0.4 to flag
_GOLD_REVIEW_ALL_WRONG_MIN = 2    # need >= 2 models all wrong

# Category refinement
_CAT_UNSTABLE_CORRECTNESS = 0.5   # correctness < 50%
_CAT_HIGH_DISAGREEMENT = 0.5      # disagreement > 50%
_CAT_MIN_RUNS = 3                 # need >= 3 runs to assess

# Model confusion
_CONFUSION_MIN_COUNT = 2          # need >= 2 to call it stable
_CONFUSION_MIN_RATE = 0.2         # >= 20% of runs for that model+family

# Data gaps
_GAP_MIN_CASES_PER_FAMILY = 3     # fewer = data gap
_GAP_MIN_MODELS_PER_CASE = 2      # fewer = incomplete coverage


# ---------------------------------------------------------------------------
# A. False Positive Reduction Candidates
# ---------------------------------------------------------------------------

def _propose_fp_reduction(entries: list[RunJournalEntry]) -> list[CalibrationProposal]:
    """Identify triggers/patterns that correlate with false positives.

    FP signals:
    - study_forensics_overflagging flag in solid cases
    - wrong_answer failure in solid cases where model says something other than solid
    - false_positive flag types
    """
    proposals: list[CalibrationProposal] = []

    # Group by task_family
    by_family: dict[str, list[RunJournalEntry]] = defaultdict(list)
    for e in entries:
        by_family[e.task_family].append(e)

    # Solid-case FP analysis
    solid_entries = by_family.get("solid", [])
    if solid_entries:
        total_solid = len(solid_entries)

        # Entries flagged as overflagging or wrong_answer in solid cases
        fp_entries = [
            e for e in solid_entries
            if ("study_forensics_overflagging" in e.forensic_flag_types
                or ("wrong_answer" in e.failure_categories
                    and e.final_answer.strip().lower() != "solid"))
        ]

        if len(fp_entries) >= _FP_MIN_OCCURRENCES:
            freq = len(fp_entries) / total_solid
            if freq >= _FP_MIN_FREQUENCY:
                # Which models produce FPs?
                fp_models = Counter(e.model or e.agent_id for e in fp_entries)
                fp_tasks = sorted(set(e.task_id for e in fp_entries))
                # What answers do they produce instead?
                fp_answers = Counter(
                    e.final_answer.strip().lower()[:50] for e in fp_entries
                )

                proposals.append(CalibrationProposal(
                    proposal_type="fp_reduction",
                    target="solid_case_overflagging",
                    target_kind="category",
                    reason=(
                        f"Solid cases produce false positives in "
                        f"{len(fp_entries)}/{total_solid} runs ({freq:.0%})"
                    ),
                    evidence_summary=(
                        f"FP answers: {dict(fp_answers.most_common(3))}. "
                        f"FP models: {dict(fp_models.most_common(3))}. "
                        f"Affected cases: {', '.join(fp_tasks[:5])}"
                    ),
                    confidence="medium" if freq >= 0.5 else "low",
                    strength=round(freq, 2),
                    recommended_action=(
                        "Review FP-producing cases. Consider adding "
                        "analytical reference cues or weakening cues for "
                        "the misclassified patterns."
                    ),
                    affected_cases=fp_tasks,
                    affected_models=sorted(fp_models.keys()),
                ))

        # Per-model FP analysis within solid
        for model, model_entries in _group_by_model(solid_entries).items():
            n = len(model_entries)
            fp_model = [
                e for e in model_entries
                if e.final_answer.strip().lower() != "solid"
                and "wrong_answer" in e.failure_categories
            ]
            if len(fp_model) >= _FP_MIN_OCCURRENCES and n >= 3:
                rate = len(fp_model) / n
                if rate >= _FP_MIN_FREQUENCY:
                    proposals.append(CalibrationProposal(
                        proposal_type="fp_reduction",
                        target=model,
                        target_kind="model",
                        reason=(
                            f"{model} misclassifies solid cases as something else "
                            f"in {len(fp_model)}/{n} runs ({rate:.0%})"
                        ),
                        evidence_summary=(
                            f"Answers given: "
                            f"{dict(Counter(e.final_answer.strip().lower()[:50] for e in fp_model).most_common(3))}"
                        ),
                        confidence="medium",
                        strength=round(rate, 2),
                        recommended_action=(
                            f"Investigate why {model} overflags solid cases. "
                            f"May need prompt tuning or evaluator adjustment."
                        ),
                        affected_cases=sorted(set(e.task_id for e in fp_model)),
                        affected_models=[model],
                    ))

    # Cross-family: failure categories that appear disproportionately
    # in wrong-answer contexts
    wrong_entries = [e for e in entries if "wrong_answer" in e.failure_categories]
    if len(wrong_entries) >= 3:
        # Which other failure categories co-occur with wrong_answer?
        co_occurring: Counter[str] = Counter()
        for e in wrong_entries:
            for fc in e.failure_categories:
                if fc != "wrong_answer":
                    co_occurring[fc] += 1

        for fc, count in co_occurring.most_common(5):
            rate = count / len(wrong_entries)
            if count >= _FP_MIN_OCCURRENCES and rate >= 0.4:
                proposals.append(CalibrationProposal(
                    proposal_type="fp_reduction",
                    target=fc,
                    target_kind="trigger",
                    reason=(
                        f"Failure '{fc}' co-occurs with wrong_answer in "
                        f"{count}/{len(wrong_entries)} wrong runs ({rate:.0%})"
                    ),
                    evidence_summary=(
                        f"This may indicate the evaluator flag '{fc}' "
                        f"is a symptom, not a cause. Or the trigger is too broad."
                    ),
                    confidence="heuristic",
                    strength=round(rate, 2),
                    recommended_action=(
                        f"Review whether '{fc}' detection is correctly "
                        f"calibrated or too aggressive."
                    ),
                ))

    return proposals


# ---------------------------------------------------------------------------
# B. Gold Review Candidates
# ---------------------------------------------------------------------------

def _propose_gold_review(
    entries: list[RunJournalEntry],
    insights: InsightsReport | None = None,
) -> list[CalibrationProposal]:
    """Identify cases that may need gold label reconsideration."""
    proposals: list[CalibrationProposal] = []

    by_task: dict[str, list[RunJournalEntry]] = defaultdict(list)
    for e in entries:
        by_task[e.task_id].append(e)

    for task_id, task_entries in sorted(by_task.items()):
        models = set(e.model or e.agent_id for e in task_entries)
        if len(models) < 2:
            continue

        family = task_entries[0].task_family

        # Signal 1: High disagreement
        label_dist = Counter(
            e.final_answer.strip().lower()[:100] for e in task_entries
        )
        d_score = _entropy(dict(label_dist))

        if d_score >= _GOLD_REVIEW_DISAGREEMENT:
            labels_str = ", ".join(
                f"{lbl}×{cnt}" for lbl, cnt in label_dist.most_common()
            )
            models_by_label: dict[str, list[str]] = defaultdict(list)
            for e in task_entries:
                m = e.model or e.agent_id
                a = e.final_answer.strip().lower()[:100]
                if m not in models_by_label[a]:
                    models_by_label[a].append(m)

            proposals.append(CalibrationProposal(
                proposal_type="gold_review",
                target=task_id,
                target_kind="case",
                reason="Stable cross-model disagreement on classification",
                evidence_summary=(
                    f"Disagreement entropy: {d_score:.2f}. "
                    f"Labels: {labels_str}. "
                    f"Models: {dict(models_by_label)}"
                ),
                confidence="medium" if d_score >= 0.6 else "low",
                strength=round(d_score, 2),
                recommended_action=(
                    f"Review gold label for {task_id} ({family}). "
                    f"Models disagree — check if the case is genuinely "
                    f"borderline or if the gold label needs adjustment."
                ),
                affected_cases=[task_id],
                affected_models=sorted(models),
            ))

        # Signal 2: All models wrong with high confidence
        all_wrong = all(e.correctness < 0.5 for e in task_entries)
        confidence_values = [
            confidence_value_if_valid(e.confidence, e.confidence_state)
            for e in task_entries
        ]
        valid_confidences = [v for v in confidence_values if v is not None]
        confidence_complete = len(valid_confidences) == len(task_entries)
        high_conf = bool(
            confidence_complete and valid_confidences
            and all(v >= 0.7 for v in valid_confidences)
        )
        n_models = len(models)

        if all_wrong and high_conf and n_models >= _GOLD_REVIEW_ALL_WRONG_MIN:
            answers = sorted(set(
                e.final_answer.strip().lower()[:80] for e in task_entries
            ))
            avg_conf = sum(valid_confidences) / len(valid_confidences)

            # Stronger signal if all models agree on the same wrong answer
            unanimous_wrong = len(set(
                e.final_answer.strip().lower()[:50] for e in task_entries
            )) == 1

            # Don't duplicate if already proposed for disagreement
            if not any(p.target == task_id for p in proposals):
                proposals.append(CalibrationProposal(
                    proposal_type="gold_review",
                    target=task_id,
                    target_kind="case",
                    reason=(
                        "All models incorrect with high confidence"
                        + (" — unanimous wrong answer" if unanimous_wrong else "")
                    ),
                    evidence_summary=(
                        f"{n_models} models, all incorrect. "
                        f"Avg confidence: {avg_conf:.2f} "
                        f"({len(valid_confidences)}/{len(task_entries)} eligible). "
                        f"Answers: {', '.join(answers)}. "
                        f"Family: {family}"
                    ),
                    confidence="high" if unanimous_wrong and n_models >= 3 else "medium",
                    strength=round(avg_conf, 2),
                    recommended_action=(
                        f"Strong gold-review candidate. "
                        f"{'All models agree on the same answer — ' if unanimous_wrong else ''}"
                        f"consider whether {family} is the correct label "
                        f"or if the case should be relabeled."
                    ),
                    affected_cases=[task_id],
                    affected_models=sorted(models),
                ))

        # Signal 3: Strong model correct but weak model pattern
        # (strong model with high score says X, overall label is Y)
        if not all_wrong and len(task_entries) >= 3:
            correct_entries = [e for e in task_entries if e.correctness >= 0.8]
            wrong_entries_task = [e for e in task_entries if e.correctness < 0.5]

            if correct_entries and wrong_entries_task:
                # If wrong entries have high scores in other dimensions,
                # they may have valid reasoning for a different label
                high_quality_wrong = []
                for e in wrong_entries_task:
                    confidence = confidence_value_if_valid(
                        e.confidence, e.confidence_state
                    )
                    if e.total_score >= 60.0 and confidence is not None and confidence >= 0.8:
                        high_quality_wrong.append(e)
                if high_quality_wrong and not any(p.target == task_id for p in proposals):
                    proposals.append(CalibrationProposal(
                        proposal_type="gold_review",
                        target=task_id,
                        target_kind="case",
                        reason="Well-reasoned wrong answer — plausible alternative reading",
                        evidence_summary=(
                            f"{len(high_quality_wrong)} model(s) score >=60 but "
                            f"classify incorrectly with high confidence. "
                            f"May indicate a borderline case."
                        ),
                        confidence="low",
                        strength=0.4,
                        recommended_action=(
                            f"Check if {task_id} is borderline. The wrong-answer "
                            f"models show structured reasoning for their classification."
                        ),
                        affected_cases=[task_id],
                        affected_models=sorted(
                            e.model or e.agent_id for e in high_quality_wrong
                        ),
                    ))

    return proposals


# ---------------------------------------------------------------------------
# C. Category Refinement Candidates
# ---------------------------------------------------------------------------

def _propose_category_refinement(
    entries: list[RunJournalEntry],
    insights: InsightsReport | None = None,
) -> list[CalibrationProposal]:
    """Identify categories that may be too broad or unstable."""
    proposals: list[CalibrationProposal] = []

    by_family: dict[str, list[RunJournalEntry]] = defaultdict(list)
    for e in entries:
        if e.task_family:
            by_family[e.task_family].append(e)

    for family, fam_entries in sorted(by_family.items()):
        n_runs = len(fam_entries)
        if n_runs < _CAT_MIN_RUNS:
            continue

        n_cases = len(set(e.task_id for e in fam_entries))
        correct_count = sum(1 for e in fam_entries if e.correctness >= 0.8)
        correctness_rate = correct_count / n_runs

        # Disagreement analysis within family
        by_task: dict[str, list[RunJournalEntry]] = defaultdict(list)
        for e in fam_entries:
            by_task[e.task_id].append(e)

        disagreement_cases = 0
        multi_model_cases = 0
        label_scatter: Counter[str] = Counter()

        for task_entries in by_task.values():
            models = set(e.model or e.agent_id for e in task_entries)
            for e in task_entries:
                label_scatter[e.final_answer.strip().lower()[:50]] += 1
            if len(models) < 2:
                continue
            multi_model_cases += 1
            answers = set(e.final_answer.strip().lower()[:50] for e in task_entries)
            if len(answers) > 1:
                disagreement_cases += 1

        disagreement_rate = (
            disagreement_cases / multi_model_cases
            if multi_model_cases > 0 else 0.0
        )

        # Signal 1: Low correctness — category may be poorly defined
        if correctness_rate < _CAT_UNSTABLE_CORRECTNESS:
            proposals.append(CalibrationProposal(
                proposal_type="category_refinement",
                target=family,
                target_kind="category",
                reason=f"Low correctness rate ({correctness_rate:.0%}) suggests category instability",
                evidence_summary=(
                    f"{correct_count}/{n_runs} runs correct across {n_cases} cases. "
                    f"Label scatter: {dict(label_scatter.most_common(4))}"
                ),
                confidence="medium" if correctness_rate < 0.3 else "low",
                strength=round(1.0 - correctness_rate, 2),
                recommended_action=(
                    f"Review category '{family}' definition. Cases may be "
                    f"splitting into other labels. Consider narrowing scope "
                    f"or splitting into sub-categories."
                ),
                affected_cases=sorted(set(e.task_id for e in fam_entries)),
                affected_models=sorted(set(e.model or e.agent_id for e in fam_entries)),
            ))

        # Signal 2: High disagreement — category boundary unclear
        if disagreement_rate > _CAT_HIGH_DISAGREEMENT and multi_model_cases >= 2:
            proposals.append(CalibrationProposal(
                proposal_type="category_refinement",
                target=family,
                target_kind="category",
                reason=(
                    f"High disagreement rate ({disagreement_rate:.0%}) in "
                    f"{multi_model_cases} multi-model cases"
                ),
                evidence_summary=(
                    f"{disagreement_cases}/{multi_model_cases} multi-model cases "
                    f"show disagreement. Category boundary may be unclear."
                ),
                confidence="medium",
                strength=round(disagreement_rate, 2),
                recommended_action=(
                    f"Review category '{family}' boundaries. High disagreement "
                    f"suggests models find the distinction ambiguous."
                ),
                affected_cases=sorted(set(e.task_id for e in fam_entries)),
            ))

        # Signal 3: Label scatter — cases in this family produce many different labels
        if len(label_scatter) >= 3 and n_runs >= 5:
            # Significant scatter: the family label isn't dominant
            family_label_count = label_scatter.get(family, 0)
            family_label_rate = family_label_count / n_runs if n_runs > 0 else 0
            if family_label_rate < 0.5:
                proposals.append(CalibrationProposal(
                    proposal_type="category_refinement",
                    target=family,
                    target_kind="category",
                    reason=(
                        f"Label scatter: family label '{family}' appears in only "
                        f"{family_label_rate:.0%} of runs"
                    ),
                    evidence_summary=(
                        f"Labels produced: {dict(label_scatter.most_common(5))}. "
                        f"The family label is not the dominant classification."
                    ),
                    confidence="medium",
                    strength=round(1.0 - family_label_rate, 2),
                    recommended_action=(
                        f"Cases in '{family}' may belong to other categories. "
                        f"Review whether the category scope is too broad."
                    ),
                    affected_cases=sorted(set(e.task_id for e in fam_entries)),
                ))

    return proposals


# ---------------------------------------------------------------------------
# D. Model Confusion Candidates
# ---------------------------------------------------------------------------

def _propose_model_confusion(
    entries: list[RunJournalEntry],
) -> list[CalibrationProposal]:
    """Identify stable label confusions per model."""
    proposals: list[CalibrationProposal] = []

    # Only study_forensics entries have meaningful label comparison
    sf_entries = [e for e in entries if e.task_type == "study_forensics"]
    if not sf_entries:
        return proposals

    by_model: dict[str, list[RunJournalEntry]] = defaultdict(list)
    for e in sf_entries:
        by_model[e.model or e.agent_id].append(e)

    for model, model_entries in sorted(by_model.items()):
        n = len(model_entries)
        if n < 3:
            continue

        # Count confusions: task_family (gold proxy) vs final_answer (detected)
        confusion_ctr: Counter[tuple[str, str]] = Counter()
        confusion_tasks: dict[tuple[str, str], list[str]] = defaultdict(list)

        for e in model_entries:
            gold = e.task_family
            detected = e.final_answer.strip().lower()[:50]
            if gold and detected and detected != gold:
                pair = (gold, detected)
                confusion_ctr[pair] += 1
                if e.task_id not in confusion_tasks[pair]:
                    confusion_tasks[pair].append(e.task_id)

        for (gold, detected), count in confusion_ctr.most_common(5):
            # Count runs in this gold family for this model
            family_runs = sum(1 for e in model_entries if e.task_family == gold)
            rate = count / family_runs if family_runs > 0 else 0

            if count >= _CONFUSION_MIN_COUNT and rate >= _CONFUSION_MIN_RATE:
                proposals.append(CalibrationProposal(
                    proposal_type="model_confusion",
                    target=model,
                    target_kind="model",
                    reason=(
                        f"{model} confuses '{gold}' with '{detected}' "
                        f"in {count}/{family_runs} runs ({rate:.0%})"
                    ),
                    evidence_summary=(
                        f"Stable confusion pattern: {gold} → {detected}. "
                        f"Affected tasks: {', '.join(confusion_tasks[(gold, detected)][:5])}"
                    ),
                    confidence="medium" if count >= 3 else "low",
                    strength=round(rate, 2),
                    recommended_action=(
                        f"Document this confusion pattern for {model}. "
                        f"Check if the confusion indicates a prompt issue, "
                        f"a genuine category boundary problem, or model limitation."
                    ),
                    affected_cases=confusion_tasks[(gold, detected)],
                    affected_models=[model],
                ))

    # Cross-model confusion: same confusion across multiple models
    all_confusions: dict[tuple[str, str], list[str]] = defaultdict(list)
    for p in proposals:
        if p.proposal_type == "model_confusion":
            # Extract gold->detected from reason
            for model, model_entries in by_model.items():
                for e in model_entries:
                    gold = e.task_family
                    detected = e.final_answer.strip().lower()[:50]
                    if gold and detected and detected != gold:
                        if model not in all_confusions[(gold, detected)]:
                            all_confusions[(gold, detected)].append(model)

    for (gold, detected), models in all_confusions.items():
        if len(models) >= 2:
            # Check if not already covered
            if not any(
                p.target == f"cross_model_{gold}_{detected}"
                for p in proposals
            ):
                proposals.append(CalibrationProposal(
                    proposal_type="model_confusion",
                    target=f"cross_model_{gold}_{detected}",
                    target_kind="category",
                    reason=(
                        f"Multiple models ({len(models)}) confuse "
                        f"'{gold}' with '{detected}'"
                    ),
                    evidence_summary=(
                        f"Models: {', '.join(sorted(models))}. "
                        f"Cross-model confusion may indicate a category "
                        f"boundary problem rather than individual model weakness."
                    ),
                    confidence="medium",
                    strength=round(len(models) / len(by_model), 2),
                    recommended_action=(
                        f"Cross-model confusion {gold}→{detected} suggests "
                        f"the category boundary may be unclear. "
                        f"Consider reviewing the distinction."
                    ),
                    affected_models=sorted(models),
                ))

    return proposals


# ---------------------------------------------------------------------------
# E. Data Gap Candidates
# ---------------------------------------------------------------------------

def _propose_data_gaps(
    entries: list[RunJournalEntry],
) -> list[CalibrationProposal]:
    """Identify categories / shapes that need more cases."""
    proposals: list[CalibrationProposal] = []

    by_family: dict[str, list[RunJournalEntry]] = defaultdict(list)
    for e in entries:
        if e.task_family:
            by_family[e.task_family].append(e)

    all_families = set(by_family.keys())

    for family, fam_entries in sorted(by_family.items()):
        n_cases = len(set(e.task_id for e in fam_entries))
        n_runs = len(fam_entries)

        # Signal 1: Too few cases in family
        if n_cases < _GAP_MIN_CASES_PER_FAMILY:
            proposals.append(CalibrationProposal(
                proposal_type="data_gap",
                target=family,
                target_kind="category",
                reason=(
                    f"Category '{family}' has only {n_cases} case(s) — "
                    f"insufficient for reliable calibration"
                ),
                evidence_summary=(
                    f"{n_cases} unique cases, {n_runs} total runs. "
                    f"Minimum recommended: {_GAP_MIN_CASES_PER_FAMILY} cases."
                ),
                confidence="high" if n_cases <= 1 else "medium",
                strength=round(1.0 - (n_cases / _GAP_MIN_CASES_PER_FAMILY), 2),
                recommended_action=(
                    f"Add more cases to '{family}'. Current coverage "
                    f"is too thin for reliable pattern detection."
                ),
                affected_cases=sorted(set(e.task_id for e in fam_entries)),
            ))

        # Signal 2: Cases with only single-model coverage
        by_task: dict[str, list[RunJournalEntry]] = defaultdict(list)
        for e in fam_entries:
            by_task[e.task_id].append(e)

        single_coverage = [
            tid for tid, tes in by_task.items()
            if len(set(e.model or e.agent_id for e in tes)) < _GAP_MIN_MODELS_PER_CASE
        ]

        if single_coverage and len(single_coverage) >= 2:
            proposals.append(CalibrationProposal(
                proposal_type="data_gap",
                target=family,
                target_kind="category",
                reason=(
                    f"{len(single_coverage)} case(s) in '{family}' have "
                    f"single-model coverage only"
                ),
                evidence_summary=(
                    f"Cases: {', '.join(single_coverage[:5])}. "
                    f"Multi-model runs needed for disagreement analysis."
                ),
                confidence="low",
                strength=round(len(single_coverage) / len(by_task), 2),
                recommended_action=(
                    f"Run additional models on single-coverage cases "
                    f"in '{family}' to enable cross-model analysis."
                ),
                affected_cases=single_coverage,
            ))

    # Signal 3: Borderline cases missing
    # If a family has only clear cases (all high correctness), it may lack
    # borderline calibration data
    for family, fam_entries in sorted(by_family.items()):
        n_cases = len(set(e.task_id for e in fam_entries))
        if n_cases < 3:
            continue
        all_correct = all(e.correctness >= 0.8 for e in fam_entries)
        if all_correct and len(fam_entries) >= 5:
            proposals.append(CalibrationProposal(
                proposal_type="data_gap",
                target=family,
                target_kind="category",
                reason=(
                    f"Category '{family}' has 100% correctness — "
                    f"may lack borderline / challenging cases"
                ),
                evidence_summary=(
                    f"All {len(fam_entries)} runs are correct. "
                    f"No edge cases are testing the category boundary."
                ),
                confidence="heuristic",
                strength=0.3,
                recommended_action=(
                    f"Consider adding borderline cases to '{family}' "
                    f"to stress-test category boundaries."
                ),
                affected_cases=sorted(set(e.task_id for e in fam_entries)),
            ))

    return proposals


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _group_by_model(
    entries: list[RunJournalEntry],
) -> dict[str, list[RunJournalEntry]]:
    """Group entries by model name."""
    by_model: dict[str, list[RunJournalEntry]] = defaultdict(list)
    for e in entries:
        by_model[e.model or e.agent_id].append(e)
    return by_model


# ---------------------------------------------------------------------------
# Main: generate_calibration_report
# ---------------------------------------------------------------------------

def generate_calibration_report(
    entries: list[RunJournalEntry],
    insights: InsightsReport | None = None,
) -> CalibrationReport:
    """Generate a complete calibration proposal report.

    Pure observation — no side effects, no mutations.
    Optionally accepts a pre-computed InsightsReport for enrichment.
    """
    if not entries:
        return CalibrationReport(
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    # Compute insights if not provided
    if insights is None:
        insights = generate_insights(entries)

    confidence_values = [
        confidence_value_if_valid(e.confidence, e.confidence_state) for e in entries
    ]
    n_confidence_eligible = sum(v is not None for v in confidence_values)

    fp_proposals = _propose_fp_reduction(entries)
    gold_proposals = _propose_gold_review(entries, insights)
    cat_proposals = _propose_category_refinement(entries, insights)
    confusion_proposals = _propose_model_confusion(entries)
    gap_proposals = _propose_data_gaps(entries)

    all_proposals = (
        fp_proposals + gold_proposals + cat_proposals
        + confusion_proposals + gap_proposals
    )

    return CalibrationReport(
        generated_at=datetime.now(timezone.utc).isoformat(),
        n_entries_analyzed=len(entries),
        n_confidence_observations=len(entries),
        n_confidence_eligible=n_confidence_eligible,
        n_confidence_ineligible=len(entries) - n_confidence_eligible,
        n_proposals=len(all_proposals),
        fp_reduction_candidates=fp_proposals,
        gold_review_candidates=gold_proposals,
        category_refinement_candidates=cat_proposals,
        model_confusion_candidates=confusion_proposals,
        data_gap_candidates=gap_proposals,
    )


# ---------------------------------------------------------------------------
# Report rendering — Markdown
# ---------------------------------------------------------------------------

def render_calibration_report(report: CalibrationReport) -> str:
    """Render CalibrationReport as a nüchtern, forensic Markdown report."""
    lines: list[str] = []

    def _h1(t: str) -> None:
        lines.append(f"# {t}")
        lines.append("")

    def _h2(t: str) -> None:
        lines.append(f"## {t}")
        lines.append("")

    def _p(t: str) -> None:
        lines.append(t)
        lines.append("")

    def _proposals_section(proposals: list[CalibrationProposal], title: str) -> None:
        _h2(title)
        if not proposals:
            _p("_No candidates detected._")
            return

        for i, p in enumerate(proposals, 1):
            lines.append(
                f"### {i}. {p.target} "
                f"({p.target_kind}) — Confidence: {p.confidence}"
            )
            lines.append("")
            _p(f"**Reason:** {p.reason}")
            _p(f"**Evidence:** {p.evidence_summary}")
            _p(f"**Strength:** {p.strength:.2f}")
            _p(f"**Recommended action:** {p.recommended_action}")
            if p.affected_cases:
                _p(f"**Affected cases:** {', '.join(p.affected_cases[:8])}")
            if p.affected_models:
                _p(f"**Affected models:** {', '.join(p.affected_models)}")
            lines.append("---")
            lines.append("")

    # Header
    _h1("Agent Arena — Gen 2 Calibration Report")
    _p(f"**Generated:** {report.generated_at}  ")
    _p(
        f"**Scope:** {report.n_entries_analyzed} journal entries analyzed, "
        f"{report.n_proposals} proposals generated"
    )
    _p(
        f"**Confidence coverage:** {report.n_confidence_eligible}/"
        f"{report.n_confidence_observations} eligible; "
        f"{report.n_confidence_ineligible} ineligible"
    )

    if report.n_entries_analyzed == 0:
        _p("_No journal entries found. Run evaluations first._")
        return "\n".join(lines)

    if report.n_proposals == 0:
        _p("_No calibration proposals generated. System appears well-calibrated._")
        return "\n".join(lines)

    # Summary table
    _h2("Proposal Summary")
    lines.append("| Type | Count |")
    lines.append("|------|-------|")
    lines.append(f"| FP Reduction | {len(report.fp_reduction_candidates)} |")
    lines.append(f"| Gold Review | {len(report.gold_review_candidates)} |")
    lines.append(f"| Category Refinement | {len(report.category_refinement_candidates)} |")
    lines.append(f"| Model Confusion | {len(report.model_confusion_candidates)} |")
    lines.append(f"| Data Gap | {len(report.data_gap_candidates)} |")
    lines.append(f"| **Total** | **{report.n_proposals}** |")
    lines.append("")

    # Sections
    _proposals_section(report.fp_reduction_candidates, "A. False Positive Reduction Candidates")
    _proposals_section(report.gold_review_candidates, "B. Gold Review Candidates")
    _proposals_section(report.category_refinement_candidates, "C. Category Refinement Candidates")
    _proposals_section(report.model_confusion_candidates, "D. Model Confusion Candidates")
    _proposals_section(report.data_gap_candidates, "E. Data Gap Candidates")

    # Recommended next actions
    _h2("F. Recommended Next Actions")
    actions: list[str] = []

    # Prioritize by confidence
    high_conf = [
        p for p in (
            report.gold_review_candidates
            + report.fp_reduction_candidates
            + report.category_refinement_candidates
        )
        if p.confidence == "high"
    ]
    medium_conf = [
        p for p in (
            report.gold_review_candidates
            + report.fp_reduction_candidates
            + report.category_refinement_candidates
        )
        if p.confidence == "medium"
    ]

    if high_conf:
        actions.append(
            f"1. **Urgent:** {len(high_conf)} high-confidence proposal(s) — "
            f"review immediately"
        )
    if medium_conf:
        actions.append(
            f"2. **Next sprint:** {len(medium_conf)} medium-confidence proposal(s) — "
            f"review in next calibration cycle"
        )
    if report.data_gap_candidates:
        actions.append(
            f"3. **Data generation:** {len(report.data_gap_candidates)} data gap(s) — "
            f"new cases needed"
        )
    if report.model_confusion_candidates:
        actions.append(
            f"4. **Documentation:** {len(report.model_confusion_candidates)} model "
            f"confusion pattern(s) to document"
        )

    if not actions:
        _p("_No prioritized actions at this time._")
    else:
        for a in actions:
            _p(a)

    # Footer
    lines.append("---")
    _p(
        "*Gen 2 Calibrate — proposals only. No automatic changes to gold labels, "
        "evaluator rules, or scores. Human review required.*"
    )

    return "\n".join(lines)
