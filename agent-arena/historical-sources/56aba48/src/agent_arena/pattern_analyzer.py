"""Cross-run pattern detection and agent profiling — agent-arena v0.6.

Analyzes collections of RunJournalEntry records to detect recurring
failure patterns, build agent profiles, and track score trends.
Rule-based, no ML, no external dependencies.
"""

from __future__ import annotations

from collections import Counter, defaultdict

from agent_arena.schemas import (
    AgentProfile,
    FailureCategory,
    PatternCluster,
    RunJournalEntry,
    TrendSnapshot,
    DIAGNOSTIC_WEIGHTS,
)


# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------

_MIN_OCCURRENCES_FOR_PATTERN = 2     # need at least 2 to call it recurring
_MIN_FREQUENCY_FOR_PATTERN = 0.25    # at least 25% of runs


# ---------------------------------------------------------------------------
# Pattern clustering
# ---------------------------------------------------------------------------

def detect_failure_patterns(
    entries: list[RunJournalEntry],
) -> list[PatternCluster]:
    """Detect recurring failure categories across entries."""
    if not entries:
        return []

    total = len(entries)
    counter: Counter[str] = Counter()
    task_map: dict[str, set[str]] = defaultdict(set)

    for e in entries:
        for fc in e.failure_categories:
            counter[fc] += 1
            task_map[fc].add(e.task_id)

    patterns = []
    for category, count in counter.most_common():
        freq = count / total
        if count >= _MIN_OCCURRENCES_FOR_PATTERN and freq >= _MIN_FREQUENCY_FOR_PATTERN:
            patterns.append(PatternCluster(
                pattern_type="recurring_failure",
                category=category,
                occurrences=count,
                total_runs=total,
                frequency=round(freq, 3),
                affected_tasks=sorted(task_map[category]),
                description=f"{category.replace('_', ' ')} in {count}/{total} runs ({freq:.0%})",
            ))

    return patterns


def detect_flag_patterns(
    entries: list[RunJournalEntry],
) -> list[PatternCluster]:
    """Detect recurring forensic flag types across entries."""
    if not entries:
        return []

    total = len(entries)
    counter: Counter[str] = Counter()
    task_map: dict[str, set[str]] = defaultdict(set)

    for e in entries:
        for ft in e.forensic_flag_types:
            counter[ft] += 1
            task_map[ft].add(e.task_id)

    patterns = []
    for flag_type, count in counter.most_common():
        freq = count / total
        if count >= _MIN_OCCURRENCES_FOR_PATTERN and freq >= _MIN_FREQUENCY_FOR_PATTERN:
            patterns.append(PatternCluster(
                pattern_type="recurring_flag",
                category=flag_type,
                occurrences=count,
                total_runs=total,
                frequency=round(freq, 3),
                affected_tasks=sorted(task_map[flag_type]),
                description=f"{flag_type} in {count}/{total} runs ({freq:.0%})",
            ))

    return patterns


def detect_forecast_bias_patterns(
    entries: list[RunJournalEntry],
) -> list[PatternCluster]:
    """Detect forecast-specific biases (overconfidence, base rate neglect, etc.)."""
    forecast_entries = [e for e in entries if e.decision_category]
    if not forecast_entries:
        return []

    total = len(forecast_entries)
    patterns = []

    # Overconfidence rate
    overconfident = [
        e for e in forecast_entries
        if FailureCategory.OVERCONFIDENT_FORECAST.value in e.failure_categories
    ]
    if len(overconfident) >= _MIN_OCCURRENCES_FOR_PATTERN:
        freq = len(overconfident) / total
        if freq >= _MIN_FREQUENCY_FOR_PATTERN:
            patterns.append(PatternCluster(
                pattern_type="forecast_bias",
                category="overconfidence",
                occurrences=len(overconfident),
                total_runs=total,
                frequency=round(freq, 3),
                affected_tasks=sorted({e.task_id for e in overconfident}),
                description=f"Overconfident forecasts in {len(overconfident)}/{total} forecast runs ({freq:.0%})",
            ))

    # Base rate neglect
    br_neglect = [
        e for e in forecast_entries
        if FailureCategory.BASE_RATE_OMISSION.value in e.failure_categories
    ]
    if len(br_neglect) >= _MIN_OCCURRENCES_FOR_PATTERN:
        freq = len(br_neglect) / total
        if freq >= _MIN_FREQUENCY_FOR_PATTERN:
            patterns.append(PatternCluster(
                pattern_type="forecast_bias",
                category="base_rate_neglect",
                occurrences=len(br_neglect),
                total_runs=total,
                frequency=round(freq, 3),
                affected_tasks=sorted({e.task_id for e in br_neglect}),
                description=f"Base rate neglect in {len(br_neglect)}/{total} forecast runs ({freq:.0%})",
            ))

    # Narrative overreach
    narrative = [
        e for e in forecast_entries
        if FailureCategory.NARRATIVE_OVERREACH.value in e.failure_categories
    ]
    if len(narrative) >= _MIN_OCCURRENCES_FOR_PATTERN:
        freq = len(narrative) / total
        if freq >= _MIN_FREQUENCY_FOR_PATTERN:
            patterns.append(PatternCluster(
                pattern_type="forecast_bias",
                category="narrative_overreach",
                occurrences=len(narrative),
                total_runs=total,
                frequency=round(freq, 3),
                affected_tasks=sorted({e.task_id for e in narrative}),
                description=f"Narrative overreach in {len(narrative)}/{total} forecast runs ({freq:.0%})",
            ))

    return patterns


# ---------------------------------------------------------------------------
# Agent profile
# ---------------------------------------------------------------------------

_DIMENSIONS = [
    "correctness", "support_strength", "structural_reasoning",
    "insight_depth", "mechanism_quality", "self_monitoring_quality",
]


def build_agent_profile(
    agent_id: str,
    entries: list[RunJournalEntry],
) -> AgentProfile:
    """Build an aggregated forensic profile from journal entries for one agent."""
    agent_entries = [e for e in entries if e.agent_id == agent_id]
    if not agent_entries:
        return AgentProfile(agent_id=agent_id)

    n = len(agent_entries)
    model = agent_entries[-1].model  # latest model

    # Average total score
    avg_score = sum(e.total_score for e in agent_entries) / n

    # Dimension averages
    dim_avgs: dict[str, float] = {}
    for dim in _DIMENSIONS:
        dim_avgs[dim] = sum(getattr(e, dim) for e in agent_entries) / n

    strongest = max(dim_avgs, key=dim_avgs.get)  # type: ignore[arg-type]
    weakest = min(dim_avgs, key=dim_avgs.get)  # type: ignore[arg-type]

    # Recurring patterns
    recurring_failures = detect_failure_patterns(agent_entries)
    recurring_flags = detect_flag_patterns(agent_entries)

    # Forecast-specific metrics
    forecast_entries = [e for e in agent_entries if e.decision_category]
    avg_prob = None
    overconfidence_rate = 0.0
    no_trade_quality = ""
    base_rate_awareness = ""

    if forecast_entries:
        probs = [e.probability_estimate for e in forecast_entries if e.probability_estimate is not None]
        if probs:
            avg_prob = sum(probs) / len(probs)

        overconfident = sum(
            1 for e in forecast_entries
            if FailureCategory.OVERCONFIDENT_FORECAST.value in e.failure_categories
        )
        overconfidence_rate = overconfident / len(forecast_entries)

        # No-trade quality
        no_trade_entries = [e for e in forecast_entries if e.decision_category == "no_trade"]
        if no_trade_entries:
            weak_nt = sum(
                1 for e in no_trade_entries
                if FailureCategory.WEAK_NO_TRADE_JUSTIFICATION.value in e.failure_categories
            )
            ratio = weak_nt / len(no_trade_entries)
            if ratio > 0.5:
                no_trade_quality = "mostly_weak"
            elif ratio > 0:
                no_trade_quality = "mixed"
            else:
                no_trade_quality = "mostly_justified"

        # Base rate awareness
        br_omissions = sum(
            1 for e in forecast_entries
            if FailureCategory.BASE_RATE_OMISSION.value in e.failure_categories
        )
        br_ratio = br_omissions / len(forecast_entries)
        if br_ratio > 0.5:
            base_rate_awareness = "ignores"
        elif br_ratio > 0:
            base_rate_awareness = "sometimes_ignores"
        else:
            base_rate_awareness = "consistently_uses"

    # Integrity rates
    accidental_rate = sum(
        1 for e in agent_entries if e.reasoning_integrity_class == "accidental"
    ) / n
    brittle_rate = sum(
        1 for e in agent_entries if e.reasoning_integrity_class == "brittle"
    ) / n
    contradiction_rate = sum(
        1 for e in agent_entries if e.n_contradictions > 0
    ) / n

    return AgentProfile(
        agent_id=agent_id,
        model=model,
        n_runs=n,
        avg_total_score=round(avg_score, 1),
        strongest_dimension=strongest,
        weakest_dimension=weakest,
        recurring_failures=recurring_failures,
        recurring_flags=recurring_flags,
        avg_probability_estimate=round(avg_prob, 3) if avg_prob is not None else None,
        overconfidence_rate=round(overconfidence_rate, 3),
        no_trade_quality=no_trade_quality,
        base_rate_awareness=base_rate_awareness,
        accidental_correctness_rate=round(accidental_rate, 3),
        brittleness_rate=round(brittle_rate, 3),
        contradiction_rate=round(contradiction_rate, 3),
    )


# ---------------------------------------------------------------------------
# Trend tracking
# ---------------------------------------------------------------------------

def compute_trend(
    agent_id: str,
    entries: list[RunJournalEntry],
    dimension: str = "total_score",
) -> TrendSnapshot:
    """Compute score trend over time for one agent and dimension."""
    agent_entries = sorted(
        [e for e in entries if e.agent_id == agent_id],
        key=lambda e: e.timestamp,
    )

    if not agent_entries:
        return TrendSnapshot(
            agent_id=agent_id,
            dimension=dimension,
            trend_direction="insufficient_data",
        )

    timestamps = [e.timestamp for e in agent_entries]

    if dimension == "total_score":
        values = [e.total_score for e in agent_entries]
    elif hasattr(agent_entries[0], dimension):
        values = [getattr(e, dimension) for e in agent_entries]
    else:
        return TrendSnapshot(
            agent_id=agent_id,
            dimension=dimension,
            trend_direction="insufficient_data",
        )

    if len(values) < 2:
        return TrendSnapshot(
            agent_id=agent_id,
            dimension=dimension,
            timestamps=timestamps,
            values=values,
            trend_direction="insufficient_data",
            delta=0.0,
        )

    delta = values[-1] - values[0]
    # Use simple windowed comparison: average of last half vs first half
    mid = len(values) // 2
    first_half_avg = sum(values[:mid]) / mid if mid > 0 else values[0]
    second_half_avg = sum(values[mid:]) / (len(values) - mid)

    if second_half_avg > first_half_avg + 0.05:
        direction = "improving"
    elif second_half_avg < first_half_avg - 0.05:
        direction = "declining"
    else:
        direction = "stable"

    return TrendSnapshot(
        agent_id=agent_id,
        dimension=dimension,
        timestamps=timestamps,
        values=[round(v, 3) for v in values],
        trend_direction=direction,
        delta=round(delta, 3),
    )


def compute_all_trends(
    agent_id: str,
    entries: list[RunJournalEntry],
) -> list[TrendSnapshot]:
    """Compute trends for all dimensions plus total_score."""
    dims = ["total_score"] + list(_DIMENSIONS)
    return [compute_trend(agent_id, entries, d) for d in dims]
