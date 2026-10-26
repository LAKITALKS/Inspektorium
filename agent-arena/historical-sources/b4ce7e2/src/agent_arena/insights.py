"""Gen 1 Insights — transparent meta-analysis layer for agent-arena v0.6.6.

Observes, aggregates, and surfaces patterns across stored runs.
Does NOT modify gold labels, evaluator rules, or scores.

Answers:
- Which failure modes are most frequent?
- Which model is weak in which category?
- Which cases produce stable disagreement?
- Which categories are mature vs unstable?
- Which cases are borderline / gold-review candidates?

Data sources: RunJournalEntry records (journal.jsonl).
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from datetime import datetime, timezone

from agent_arena.schemas import (
    BorderlineCandidateSignal,
    CaseDisagreement,
    CategoryMaturitySummary,
    CountedItem,
    DisagreementSummary,
    FailureSummary,
    FlagSummary,
    InsightsReport,
    LabelConfusion,
    ModelInsightProfile,
    RunJournalEntry,
    DIAGNOSTIC_WEIGHTS,
)


# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------

_TOP_N = 10                         # max items in top-N lists
_DISAGREEMENT_THRESHOLD = 0.3       # disagreement_score above this = notable
_BORDERLINE_DISAGREEMENT = 0.4      # above this = borderline candidate
_MATURITY_MIN_RUNS = 3              # need at least 3 runs to assess maturity
_MATURITY_STABLE_THRESHOLD = 0.8    # correctness >= 80% = mature
_MATURITY_UNSTABLE_THRESHOLD = 0.5  # correctness < 50% = unstable

# Dimension names tracked in journal entries
_DIMENSIONS = [
    "correctness", "support_strength", "structural_reasoning",
    "insight_depth", "mechanism_quality", "self_monitoring_quality",
]


# ---------------------------------------------------------------------------
# Helper: count → CountedItem list
# ---------------------------------------------------------------------------

def _counter_to_items(counter: Counter, total: int, top_n: int = _TOP_N) -> list[CountedItem]:
    """Convert a Counter to a sorted list of CountedItem."""
    return [
        CountedItem(
            name=name,
            count=count,
            total=total,
            frequency=round(count / total, 3) if total > 0 else 0.0,
        )
        for name, count in counter.most_common(top_n)
        if count > 0
    ]


# ---------------------------------------------------------------------------
# A. Failure Summary
# ---------------------------------------------------------------------------

def _build_failure_summary(entries: list[RunJournalEntry]) -> FailureSummary:
    """Aggregate failure categories: overall, by family, by model."""
    overall: Counter[str] = Counter()
    by_family: dict[str, Counter[str]] = defaultdict(Counter)
    by_model: dict[str, Counter[str]] = defaultdict(Counter)

    family_totals: Counter[str] = Counter()
    model_totals: Counter[str] = Counter()

    for e in entries:
        model_totals[e.model or e.agent_id] += 1
        family_totals[e.task_family] += 1
        for fc in e.failure_categories:
            overall[fc] += 1
            by_family[e.task_family][fc] += 1
            by_model[e.model or e.agent_id][fc] += 1

    total = len(entries)
    return FailureSummary(
        top_overall=_counter_to_items(overall, total),
        by_family={
            fam: _counter_to_items(ctr, family_totals[fam])
            for fam, ctr in sorted(by_family.items())
        },
        by_model={
            mdl: _counter_to_items(ctr, model_totals[mdl])
            for mdl, ctr in sorted(by_model.items())
        },
    )


# ---------------------------------------------------------------------------
# B. Flag Summary
# ---------------------------------------------------------------------------

def _build_flag_summary(entries: list[RunJournalEntry]) -> FlagSummary:
    """Aggregate forensic flags: overall, by family, by model."""
    overall: Counter[str] = Counter()
    by_family: dict[str, Counter[str]] = defaultdict(Counter)
    by_model: dict[str, Counter[str]] = defaultdict(Counter)

    family_totals: Counter[str] = Counter()
    model_totals: Counter[str] = Counter()

    for e in entries:
        model_totals[e.model or e.agent_id] += 1
        family_totals[e.task_family] += 1
        for ft in e.forensic_flag_types:
            overall[ft] += 1
            by_family[e.task_family][ft] += 1
            by_model[e.model or e.agent_id][ft] += 1

    total = len(entries)
    return FlagSummary(
        top_overall=_counter_to_items(overall, total),
        by_family={
            fam: _counter_to_items(ctr, family_totals[fam])
            for fam, ctr in sorted(by_family.items())
        },
        by_model={
            mdl: _counter_to_items(ctr, model_totals[mdl])
            for mdl, ctr in sorted(by_model.items())
        },
    )


# ---------------------------------------------------------------------------
# C. Model Insight Profiles
# ---------------------------------------------------------------------------

def _detect_tendencies(
    entries: list[RunJournalEntry],
    dim_avgs: dict[str, float],
    top_failures: list[CountedItem],
) -> list[str]:
    """Derive human-readable tendency labels from entry patterns."""
    tendencies: list[str] = []
    n = len(entries)
    if n == 0:
        return tendencies

    # Overclaim tendency
    overclaim_count = sum(
        1 for e in entries
        if any("overclaim" in fc.lower() for fc in e.failure_categories)
    )
    if overclaim_count / n >= 0.25:
        tendencies.append(f"overclaim_tendency ({overclaim_count}/{n})")

    # False positive tendency (hallucinating issues in solid cases)
    fp_count = sum(
        1 for e in entries
        if any("false_positive" in ft or "overflagging" in ft
               for ft in e.forensic_flag_types)
    )
    if fp_count / n >= 0.2:
        tendencies.append(f"false_positive_tendency ({fp_count}/{n})")

    # Charitable reading (tends to say "solid" when it shouldn't)
    charitable_count = sum(
        1 for e in entries
        if e.final_answer.strip().lower() in ("solid", "no major issues")
        and e.correctness < 0.5
    )
    if charitable_count >= 2:
        tendencies.append(f"charitable_reading ({charitable_count}/{n})")

    # Brittle reasoning
    brittle_count = sum(
        1 for e in entries if e.reasoning_integrity_class == "brittle"
    )
    if brittle_count / n >= 0.25:
        tendencies.append(f"brittle_reasoning ({brittle_count}/{n})")

    # Accidental correctness
    accidental_count = sum(
        1 for e in entries if e.reasoning_integrity_class == "accidental"
    )
    if accidental_count / n >= 0.2:
        tendencies.append(f"accidental_correctness ({accidental_count}/{n})")

    # Weak self-monitoring
    if dim_avgs.get("self_monitoring_quality", 1.0) < 0.3:
        tendencies.append("weak_self_monitoring")

    # Weak mechanism quality
    if dim_avgs.get("mechanism_quality", 1.0) < 0.3:
        tendencies.append("weak_mechanism_quality")

    # Contradiction tendency
    contradiction_count = sum(1 for e in entries if e.n_contradictions > 0)
    if contradiction_count / n >= 0.25:
        tendencies.append(f"contradiction_tendency ({contradiction_count}/{n})")

    return tendencies


def _build_model_profiles(entries: list[RunJournalEntry]) -> list[ModelInsightProfile]:
    """Build forensic insight profile for each model."""
    # Group by model
    by_model: dict[str, list[RunJournalEntry]] = defaultdict(list)
    for e in entries:
        key = e.model or e.agent_id
        by_model[key].append(e)

    profiles = []
    for model, model_entries in sorted(by_model.items()):
        n = len(model_entries)

        # Dimension averages
        dim_avgs: dict[str, float] = {}
        for dim in _DIMENSIONS:
            dim_avgs[dim] = round(
                sum(getattr(e, dim) for e in model_entries) / n, 3
            )

        # Sort by average to find strongest/weakest
        sorted_dims = sorted(dim_avgs.items(), key=lambda x: x[1], reverse=True)
        strongest = [d[0] for d in sorted_dims[:3]]
        weakest = [d[0] for d in sorted_dims[-3:]]

        # Top failures
        failure_ctr: Counter[str] = Counter()
        for e in model_entries:
            for fc in e.failure_categories:
                failure_ctr[fc] += 1
        top_failures = _counter_to_items(failure_ctr, n, top_n=5)

        # Top flags
        flag_ctr: Counter[str] = Counter()
        for e in model_entries:
            for ft in e.forensic_flag_types:
                flag_ctr[ft] += 1
        top_flags = _counter_to_items(flag_ctr, n, top_n=5)

        # Label confusions (study forensics specific)
        confusions = _detect_label_confusions(model_entries, model)

        # Tendencies
        tendencies = _detect_tendencies(model_entries, dim_avgs, top_failures)

        # Integrity rates
        integrity = {
            "accidental": round(
                sum(1 for e in model_entries if e.reasoning_integrity_class == "accidental") / n, 3
            ),
            "brittle": round(
                sum(1 for e in model_entries if e.reasoning_integrity_class == "brittle") / n, 3
            ),
            "well_supported": round(
                sum(1 for e in model_entries if e.reasoning_integrity_class == "well_supported") / n, 3
            ),
            "contradiction_rate": round(
                sum(1 for e in model_entries if e.n_contradictions > 0) / n, 3
            ),
        }

        avg_score = round(sum(e.total_score for e in model_entries) / n, 1)

        profiles.append(ModelInsightProfile(
            model=model,
            n_runs=n,
            avg_score=avg_score,
            dimension_averages=dim_avgs,
            strongest_dimensions=strongest,
            weakest_dimensions=weakest,
            top_failures=top_failures,
            top_flags=top_flags,
            label_confusions=confusions,
            tendencies=tendencies,
            integrity_rates=integrity,
        ))

    return profiles


def _detect_label_confusions(
    entries: list[RunJournalEntry],
    model: str,
) -> list[LabelConfusion]:
    """Detect label confusion patterns from study forensics entries.

    Uses task_family as proxy for gold label and final_answer as detected label.
    """
    sf_entries = [e for e in entries if e.task_type == "study_forensics"]
    if not sf_entries:
        return []

    confusion_ctr: Counter[tuple[str, str]] = Counter()
    for e in sf_entries:
        gold = e.task_family
        detected = e.final_answer.strip().lower()
        if gold and detected and detected != gold:
            confusion_ctr[(gold, detected)] += 1

    return [
        LabelConfusion(
            gold_label=gold,
            detected_label=detected,
            count=count,
            models=[model],
        )
        for (gold, detected), count in confusion_ctr.most_common(10)
    ]


# ---------------------------------------------------------------------------
# D. Disagreement / Instability Summary
# ---------------------------------------------------------------------------

def _entropy(distribution: dict[str, int]) -> float:
    """Shannon entropy of a label distribution, normalized to [0, 1]."""
    total = sum(distribution.values())
    if total == 0:
        return 0.0
    n_labels = len(distribution)
    if n_labels <= 1:
        return 0.0

    entropy = 0.0
    for count in distribution.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)

    max_entropy = math.log2(n_labels)
    return round(entropy / max_entropy, 3) if max_entropy > 0 else 0.0


def _build_disagreement_summary(entries: list[RunJournalEntry]) -> DisagreementSummary:
    """Find cases where different models disagree on the answer."""
    # Group entries by task_id
    by_task: dict[str, list[RunJournalEntry]] = defaultdict(list)
    for e in entries:
        by_task[e.task_id].append(e)

    cases: list[CaseDisagreement] = []
    family_disagreement_ctr: Counter[str] = Counter()
    family_total_ctr: Counter[str] = Counter()

    for task_id, task_entries in sorted(by_task.items()):
        # Need multiple distinct models to measure disagreement
        models_seen = set()
        label_dist: Counter[str] = Counter()
        models_by_label: dict[str, list[str]] = defaultdict(list)

        for e in task_entries:
            model = e.model or e.agent_id
            answer = e.final_answer.strip().lower()[:100]
            if not answer:
                answer = "(empty)"
            models_seen.add(model)
            label_dist[answer] += 1
            if model not in models_by_label[answer]:
                models_by_label[answer].append(model)

        if len(models_seen) < 2:
            continue  # Can't measure disagreement with one model

        family = task_entries[0].task_family or ""
        family_total_ctr[family] += 1

        d_score = _entropy(dict(label_dist))

        if d_score > _DISAGREEMENT_THRESHOLD:
            family_disagreement_ctr[family] += 1

        is_borderline = d_score >= _BORDERLINE_DISAGREEMENT

        if d_score > 0:
            cases.append(CaseDisagreement(
                task_id=task_id,
                task_family=family,
                n_runs=len(task_entries),
                labels_produced=dict(label_dist),
                models_by_label=dict(models_by_label),
                disagreement_score=d_score,
                is_borderline_candidate=is_borderline,
            ))

    # Sort by disagreement score descending
    cases.sort(key=lambda c: c.disagreement_score, reverse=True)

    # Most contentious families
    contentious = Counter()
    for fam, dis_count in family_disagreement_ctr.items():
        total = family_total_ctr[fam]
        if total > 0:
            contentious[fam] = dis_count

    return DisagreementSummary(
        cases=cases,
        most_contentious_families=_counter_to_items(
            contentious, sum(family_total_ctr.values())
        ),
    )


# ---------------------------------------------------------------------------
# E. Category Maturity Summary
# ---------------------------------------------------------------------------

def _build_category_maturity(entries: list[RunJournalEntry]) -> list[CategoryMaturitySummary]:
    """Assess stability and readiness per task family."""
    by_family: dict[str, list[RunJournalEntry]] = defaultdict(list)
    for e in entries:
        if e.task_family:
            by_family[e.task_family].append(e)

    summaries = []
    for family, fam_entries in sorted(by_family.items()):
        n_runs = len(fam_entries)
        n_cases = len(set(e.task_id for e in fam_entries))
        avg_score = round(sum(e.total_score for e in fam_entries) / n_runs, 1)

        # Correctness rate: fraction with high correctness dimension
        correct_count = sum(1 for e in fam_entries if e.correctness >= 0.8)
        correctness_rate = round(correct_count / n_runs, 3)

        # Disagreement rate: what fraction of multi-model cases have disagreement?
        by_task: dict[str, list[RunJournalEntry]] = defaultdict(list)
        for e in fam_entries:
            by_task[e.task_id].append(e)

        disagreement_cases = 0
        multi_model_cases = 0
        for task_entries in by_task.values():
            models = set(e.model or e.agent_id for e in task_entries)
            if len(models) < 2:
                continue
            multi_model_cases += 1
            answers = set(e.final_answer.strip().lower()[:100] for e in task_entries)
            if len(answers) > 1:
                disagreement_cases += 1

        disagreement_rate = (
            round(disagreement_cases / multi_model_cases, 3)
            if multi_model_cases > 0 else 0.0
        )

        # Maturity classification
        if n_runs < _MATURITY_MIN_RUNS:
            maturity = "insufficient_data"
        elif correctness_rate >= _MATURITY_STABLE_THRESHOLD and disagreement_rate <= 0.3:
            maturity = "mature"
        elif correctness_rate < _MATURITY_UNSTABLE_THRESHOLD or disagreement_rate > 0.6:
            maturity = "unstable"
        else:
            maturity = "developing"

        summaries.append(CategoryMaturitySummary(
            category=family,
            n_cases=n_cases,
            n_runs=n_runs,
            avg_score=avg_score,
            correctness_rate=correctness_rate,
            disagreement_rate=disagreement_rate,
            maturity=maturity,
        ))

    return summaries


# ---------------------------------------------------------------------------
# F. Borderline Candidate Signals
# ---------------------------------------------------------------------------

def _detect_borderline_candidates(
    entries: list[RunJournalEntry],
    disagreement: DisagreementSummary,
) -> list[BorderlineCandidateSignal]:
    """Identify cases that may need gold label review. Observe only."""
    signals: list[BorderlineCandidateSignal] = []

    # Signal 1: High disagreement cases from disagreement analysis
    for case in disagreement.cases:
        if case.is_borderline_candidate:
            labels_str = ", ".join(
                f"{lbl}×{cnt}" for lbl, cnt in case.labels_produced.items()
            )
            signals.append(BorderlineCandidateSignal(
                task_id=case.task_id,
                task_family=case.task_family,
                reason="High cross-model disagreement on classification",
                confidence="medium",
                evidence=[
                    f"Disagreement score: {case.disagreement_score}",
                    f"Labels produced: {labels_str}",
                    f"N runs: {case.n_runs}",
                ],
            ))

    # Signal 2: Cases where all models disagree with expected correctness
    by_task: dict[str, list[RunJournalEntry]] = defaultdict(list)
    for e in entries:
        by_task[e.task_id].append(e)

    for task_id, task_entries in by_task.items():
        if len(task_entries) < 2:
            continue
        # All incorrect with high confidence = possible gold label issue
        all_incorrect = all(e.correctness < 0.5 for e in task_entries)
        high_confidence = all(e.confidence >= 0.7 for e in task_entries)

        if all_incorrect and high_confidence:
            # Check if not already in signals
            if not any(s.task_id == task_id for s in signals):
                answers = set(e.final_answer.strip().lower()[:80] for e in task_entries)
                signals.append(BorderlineCandidateSignal(
                    task_id=task_id,
                    task_family=task_entries[0].task_family,
                    reason="All models incorrect with high confidence — possible gold label issue",
                    confidence="high" if len(task_entries) >= 3 else "medium",
                    evidence=[
                        f"N runs: {len(task_entries)}, all incorrect",
                        f"Answers produced: {', '.join(sorted(answers))}",
                        f"Avg confidence: {sum(e.confidence for e in task_entries) / len(task_entries):.2f}",
                    ],
                ))

    # Signal 3: Cases with consistently low scores across all models
    for task_id, task_entries in by_task.items():
        if len(task_entries) < 2:
            continue
        avg_score = sum(e.total_score for e in task_entries) / len(task_entries)
        if avg_score < 40.0 and not any(s.task_id == task_id for s in signals):
            signals.append(BorderlineCandidateSignal(
                task_id=task_id,
                task_family=task_entries[0].task_family,
                reason="Consistently low scores across all models",
                confidence="low",
                evidence=[
                    f"Avg score: {avg_score:.1f}/100",
                    f"N runs: {len(task_entries)}",
                ],
            ))

    return signals


# ---------------------------------------------------------------------------
# Main: generate_insights
# ---------------------------------------------------------------------------

def generate_insights(entries: list[RunJournalEntry]) -> InsightsReport:
    """Generate a complete Gen 1 Insights report from journal entries.

    Pure observation — no side effects, no modifications.
    """
    if not entries:
        return InsightsReport(
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    n_runs = len(entries)
    n_tasks = len(set(e.task_id for e in entries))
    n_models = len(set(e.model or e.agent_id for e in entries))

    failure_summary = _build_failure_summary(entries)
    flag_summary = _build_flag_summary(entries)
    model_profiles = _build_model_profiles(entries)
    disagreement = _build_disagreement_summary(entries)
    category_maturity = _build_category_maturity(entries)
    borderline = _detect_borderline_candidates(entries, disagreement)

    return InsightsReport(
        generated_at=datetime.now(timezone.utc).isoformat(),
        n_runs=n_runs,
        n_tasks=n_tasks,
        n_models=n_models,
        failure_summary=failure_summary,
        flag_summary=flag_summary,
        model_profiles=model_profiles,
        disagreement_summary=disagreement,
        category_maturity=category_maturity,
        borderline_candidates=borderline,
    )


# ---------------------------------------------------------------------------
# Report rendering — Markdown
# ---------------------------------------------------------------------------

def render_insights_report(report: InsightsReport) -> str:
    """Render InsightsReport as a nüchtern, forensic Markdown report."""
    lines: list[str] = []

    def _h1(text: str) -> None:
        lines.append(f"# {text}")
        lines.append("")

    def _h2(text: str) -> None:
        lines.append(f"## {text}")
        lines.append("")

    def _h3(text: str) -> None:
        lines.append(f"### {text}")
        lines.append("")

    def _p(text: str) -> None:
        lines.append(text)
        lines.append("")

    def _items_table(items: list[CountedItem], label: str = "Category") -> None:
        if not items:
            lines.append("_No data._")
            lines.append("")
            return
        lines.append(f"| {label} | Count | Frequency |")
        lines.append("|--------|-------|-----------|")
        for item in items:
            lines.append(f"| {item.name} | {item.count}/{item.total} | {item.frequency:.0%} |")
        lines.append("")

    # Header
    _h1("Agent Arena — Gen 1 Insights Report")
    _p(f"**Generated:** {report.generated_at}  ")
    _p(f"**Scope:** {report.n_runs} runs, {report.n_tasks} tasks, {report.n_models} models")

    if report.n_runs == 0:
        _p("_No journal entries found. Run evaluations first._")
        return "\n".join(lines)

    # A. Failure Summary
    _h2("A. Failure Summary")
    _h3("Overall")
    _items_table(report.failure_summary.top_overall, "Failure Mode")

    if report.failure_summary.by_model:
        _h3("By Model")
        for model, items in report.failure_summary.by_model.items():
            _p(f"**{model}:**")
            _items_table(items, "Failure Mode")

    if report.failure_summary.by_family:
        _h3("By Task Family")
        for family, items in report.failure_summary.by_family.items():
            if items:
                _p(f"**{family}:**")
                _items_table(items, "Failure Mode")

    # B. Flag Summary
    _h2("B. Flag Summary")
    _h3("Overall")
    _items_table(report.flag_summary.top_overall, "Flag")

    if report.flag_summary.by_model:
        _h3("By Model")
        for model, items in report.flag_summary.by_model.items():
            if items:
                _p(f"**{model}:**")
                _items_table(items, "Flag")

    # C. Model Profiles
    _h2("C. Model Profiles")
    for profile in report.model_profiles:
        _h3(f"{profile.model}")
        _p(f"**Runs:** {profile.n_runs} | **Avg Score:** {profile.avg_score}/100")

        # Dimension averages table
        if profile.dimension_averages:
            lines.append("| Dimension | Avg Score |")
            lines.append("|-----------|-----------|")
            for dim, avg in sorted(
                profile.dimension_averages.items(),
                key=lambda x: x[1],
                reverse=True,
            ):
                marker = ""
                if dim in profile.strongest_dimensions[:1]:
                    marker = " **[strongest]**"
                elif dim in profile.weakest_dimensions[:1]:
                    marker = " **[weakest]**"
                lines.append(f"| {dim} | {avg:.3f}{marker} |")
            lines.append("")

        # Tendencies
        if profile.tendencies:
            _p("**Tendencies:** " + ", ".join(profile.tendencies))

        # Integrity rates
        if profile.integrity_rates:
            rates = profile.integrity_rates
            _p(
                f"**Integrity:** "
                f"well_supported={rates.get('well_supported', 0):.0%}, "
                f"brittle={rates.get('brittle', 0):.0%}, "
                f"accidental={rates.get('accidental', 0):.0%}, "
                f"contradictions={rates.get('contradiction_rate', 0):.0%}"
            )

        # Label confusions
        if profile.label_confusions:
            _p("**Label Confusions:**")
            for lc in profile.label_confusions:
                _p(f"- {lc.gold_label} misclassified as **{lc.detected_label}** ({lc.count}x)")

        # Top failures
        if profile.top_failures:
            _p("**Top Failures:**")
            for f in profile.top_failures[:5]:
                _p(f"- {f.name} ({f.count}/{f.total}, {f.frequency:.0%})")

    # D. Disagreement Summary
    _h2("D. Disagreement Summary")
    if report.disagreement_summary.cases:
        lines.append("| Task | Family | Disagreement | Labels | Borderline? |")
        lines.append("|------|--------|-------------|--------|-------------|")
        for case in report.disagreement_summary.cases[:15]:
            labels = ", ".join(
                f"{lbl}×{cnt}" for lbl, cnt in case.labels_produced.items()
            )
            bl = "yes" if case.is_borderline_candidate else ""
            lines.append(
                f"| {case.task_id} | {case.task_family} | "
                f"{case.disagreement_score:.2f} | {labels} | {bl} |"
            )
        lines.append("")

        if report.disagreement_summary.most_contentious_families:
            _p("**Most contentious families:**")
            for item in report.disagreement_summary.most_contentious_families:
                _p(f"- {item.name}: {item.count} contentious cases")
    else:
        _p("_No cross-model disagreement detected._")

    # E. Category Maturity
    _h2("E. Category Maturity")
    if report.category_maturity:
        lines.append("| Category | Cases | Runs | Avg Score | Correctness | Disagreement | Maturity |")
        lines.append("|----------|-------|------|-----------|-------------|-------------|----------|")
        for cm in report.category_maturity:
            lines.append(
                f"| {cm.category} | {cm.n_cases} | {cm.n_runs} | "
                f"{cm.avg_score} | {cm.correctness_rate:.0%} | "
                f"{cm.disagreement_rate:.0%} | **{cm.maturity}** |"
            )
        lines.append("")
    else:
        _p("_No category data._")

    # F. Borderline Candidates
    _h2("F. Borderline / Gold-Review Candidates")
    if report.borderline_candidates:
        for bc in report.borderline_candidates:
            _p(f"**{bc.task_id}** ({bc.task_family}) — Confidence: {bc.confidence}")
            _p(f"Reason: {bc.reason}")
            for ev in bc.evidence:
                _p(f"- {ev}")
    else:
        _p("_No borderline candidates detected._")

    # Footer
    lines.append("---")
    _p("*Gen 1 Insights — observation only. No automatic changes to gold labels, "
       "evaluator rules, or scores.*")

    return "\n".join(lines)
