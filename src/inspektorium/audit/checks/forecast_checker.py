"""v0.5: Forecast integrity checker — forensic checks for reasoning under uncertainty.

Checks:
  A. Probability-Reasoning Alignment
  B. Base Rate Usage
  C. Rule / Resolution Integrity
  D. Skeptic Coverage
  E. No-Trade Integrity
  F. Shrinkage Discipline
  G. Narrative Edge

All checks return structured findings with evidence and confidence labels.
Only runs on forecasting_decision tasks.
"""

from __future__ import annotations

from inspektorium.audit.schemas import (
    AgentResponse,
    EvidenceRole,
    EvidenceSpan,
    FailureCategory,
    FailureInstance,
    FailureSeverity,
    ForensicFlag,
    Task,
    TaskType,
)


def is_forecast_task(task: Task) -> bool:
    """Check if this task uses the forecasting evaluation path."""
    return task.task_type == TaskType.FORECASTING_DECISION


def run_forecast_checks(
    task: Task,
    p: AgentResponse,
) -> dict:
    """Run all forecast integrity checks. Returns a structured dict.

    Only meaningful for forecasting_decision tasks.
    """
    if not is_forecast_task(task):
        return {}

    failures: list[FailureInstance] = []
    flags: list[ForensicFlag] = []
    scores: dict[str, float] = {}

    # --- A. Probability-Reasoning Alignment ---
    prob_score = _check_probability_alignment(task, p, failures, flags)
    scores["probability_calibration_quality"] = prob_score

    # --- B. Base Rate Usage ---
    br_score = _check_base_rate_usage(task, p, failures, flags)
    scores["baseline_awareness"] = br_score

    # --- C. Rule / Resolution Integrity ---
    rule_score = _check_rule_integrity(task, p, failures, flags)
    scores["rule_comprehension"] = rule_score

    # --- D. Skeptic Coverage ---
    skeptic_score = _check_skeptic_coverage(task, p, failures, flags)
    scores["skeptic_depth"] = skeptic_score

    # --- E. No-Trade Integrity ---
    notrade_score = _check_no_trade_integrity(task, p, failures, flags)
    scores["no_action_quality"] = notrade_score

    # --- F. Shrinkage Discipline ---
    shrink_score = _check_shrinkage_discipline(task, p, failures, flags)
    scores["uncertainty_honesty"] = shrink_score

    # --- G. Narrative Edge ---
    edge_score = _check_narrative_edge(task, p, failures, flags)

    # Decision category check
    _check_decision_category(task, p, failures)

    return {
        "is_forecast": True,
        "decision_category": p.decision_category,
        "probability_estimate": p.probability_estimate,
        "scores": scores,
        "failures": failures,
        "flags": flags,
    }


# ---------------------------------------------------------------------------
# A. Probability-Reasoning Alignment
# ---------------------------------------------------------------------------


def _check_probability_alignment(
    task: Task,
    p: AgentResponse,
    failures: list[FailureInstance],
    flags: list[ForensicFlag],
) -> float:
    """Check if stated probability matches the strength of reasoning."""
    score = 0.5  # base

    prob = p.probability_estimate
    if prob is None:
        return 0.0  # no probability stated

    n_uncertainties = len(p.uncertainties)
    n_drivers = len(p.key_drivers)
    n_counter = len(p.counterarguments)

    # Overconfident: high probability + many unresolved uncertainties
    if prob >= 0.85 and n_uncertainties >= 3:
        failures.append(
            FailureInstance(
                category=FailureCategory.OVERCONFIDENT_FORECAST.value,
                severity=FailureSeverity.MAJOR.value,
                description=(
                    f"Probability {prob:.0%} despite {n_uncertainties} stated uncertainties"
                ),
                evidence=[
                    EvidenceSpan(
                        text=f"probability: {prob:.0%}, uncertainties: {n_uncertainties}",
                        source_field="probability_estimate",
                        relevance="High probability with many uncertainties",
                        role=EvidenceRole.WEAKENING,
                    )
                ],
                impact_on_score="probability_calibration_quality",
            )
        )
        score -= 0.25

    # Overconfident: extreme probability + weak justification
    if prob >= 0.90 and n_drivers <= 1:
        failures.append(
            FailureInstance(
                category=FailureCategory.OVERCONFIDENT_FORECAST.value,
                severity=FailureSeverity.MAJOR.value,
                description=(
                    f"Probability {prob:.0%} with only {n_drivers} key driver(s) stated"
                ),
                evidence=[
                    EvidenceSpan(
                        text=f"probability: {prob:.0%}",
                        source_field="probability_estimate",
                        relevance="Extreme probability without sufficient drivers",
                    )
                ],
                impact_on_score="probability_calibration_quality",
            )
        )
        score -= 0.20

    # Underconfident: very low probability + strong support + no counterargs
    if prob is not None and prob <= 0.15 and n_drivers >= 3 and n_counter == 0:
        score -= 0.10
        flags.append(
            ForensicFlag(
                flag_type="underconfident_forecast",
                description=f"Probability {prob:.0%} seems low given {n_drivers} drivers and no counterarguments",
                severity="minor",
            )
        )

    # Good alignment signals
    if n_drivers >= 2 and n_counter >= 1 and n_uncertainties >= 1:
        score += 0.30  # shows balanced reasoning
    if n_drivers >= 1:
        score += 0.10

    # In-range check against task's expected range
    if task.expected_probability_range:
        low, high = task.expected_probability_range
        if prob is not None and (prob < low - 0.10 or prob > high + 0.10):
            failures.append(
                FailureInstance(
                    category=FailureCategory.CORRECT_DIRECTION_WEAK_CALIBRATION.value,
                    severity=FailureSeverity.MODERATE.value,
                    description=(
                        f"Probability {prob:.0%} outside plausible range "
                        f"[{low:.0%}–{high:.0%}]"
                    ),
                    evidence=[
                        EvidenceSpan(
                            text=f"estimate: {prob:.0%}, range: [{low:.0%}–{high:.0%}]",
                            source_field="probability_estimate",
                            relevance="Probability outside expected range",
                        )
                    ],
                    impact_on_score="probability_calibration_quality",
                )
            )
            score -= 0.15

    return max(0.0, min(1.0, score))


# ---------------------------------------------------------------------------
# B. Base Rate Usage
# ---------------------------------------------------------------------------


def _check_base_rate_usage(
    task: Task,
    p: AgentResponse,
    failures: list[FailureInstance],
    flags: list[ForensicFlag],
) -> float:
    """Check if base rate / baseline is acknowledged and used."""
    score = 0.0

    has_base_rate_ref = bool(p.base_rate_reference.strip())
    task_has_base_rate = task.base_rate is not None

    # Agent references a baseline
    if has_base_rate_ref:
        score += 0.50
        # Check if the reference seems substantive (not just "I considered the base rate")
        if len(p.base_rate_reference) > 30:
            score += 0.20

    # Agent mentions base rate in steps or key_drivers
    all_text = " ".join([*p.steps, *p.key_drivers, p.edge_justification]).lower()
    base_rate_words = (
        "base rate",
        "baseline",
        "prior probability",
        "historical rate",
        "reference class",
        "base probability",
        "prior",
        "prevalence",
    )
    mentioned_in_reasoning = any(w in all_text for w in base_rate_words)

    if mentioned_in_reasoning:
        score += 0.20

    # Task has a base rate but agent ignores it
    if task_has_base_rate and not has_base_rate_ref and not mentioned_in_reasoning:
        failures.append(
            FailureInstance(
                category=FailureCategory.BASE_RATE_OMISSION.value,
                severity=FailureSeverity.MAJOR.value,
                description=(
                    f"Task provides base rate ({task.base_rate:.0%}) "
                    f"but agent does not reference any baseline"
                ),
                evidence=[
                    EvidenceSpan(
                        text=f"task base_rate: {task.base_rate:.0%}",
                        source_field="task",
                        relevance="Base rate available but ignored",
                    )
                ],
                impact_on_score="baseline_awareness",
            )
        )

    # Even without task base rate, pure narrative without any baseline is weak
    if not has_base_rate_ref and not mentioned_in_reasoning:
        score = max(score, 0.10)  # minimal floor
        flags.append(
            ForensicFlag(
                flag_type="baseline_blind",
                description="No baseline or reference class mentioned — purely narrative reasoning",
                severity="moderate",
            )
        )

    return max(0.0, min(1.0, score))


# ---------------------------------------------------------------------------
# C. Rule / Resolution Integrity
# ---------------------------------------------------------------------------


def _check_rule_integrity(
    task: Task,
    p: AgentResponse,
    failures: list[FailureInstance],
    flags: list[ForensicFlag],
) -> float:
    """Check if the resolution rule was correctly understood."""
    score = 0.5  # base — we can't deeply verify, but we check signals

    if not task.resolution_rule:
        return 0.5  # no rule to check against

    rule_lower = task.resolution_rule.lower()
    all_text = " ".join([p.final_answer, *p.steps, *p.key_claims]).lower()

    # Extract key terms from the resolution rule
    rule_words = {w for w in rule_lower.split() if len(w) >= 4}
    text_words = {w for w in all_text.split() if len(w) >= 4}
    overlap = len(rule_words & text_words)
    total_rule_words = len(rule_words) if rule_words else 1

    coverage = overlap / total_rule_words

    if coverage >= 0.3:
        score += 0.30
    elif coverage >= 0.15:
        score += 0.15
    else:
        # Agent doesn't engage with the resolution rule at all
        failures.append(
            FailureInstance(
                category=FailureCategory.RULE_MISREAD.value,
                severity=FailureSeverity.MODERATE.value,
                description="Agent does not engage with the resolution/decision rule",
                evidence=[
                    EvidenceSpan(
                        text=task.resolution_rule[:200],
                        source_field="task.resolution_rule",
                        relevance="Resolution rule not referenced in reasoning",
                    )
                ],
                impact_on_score="rule_comprehension",
            )
        )
        score -= 0.20

    return max(0.0, min(1.0, score))


# ---------------------------------------------------------------------------
# D. Skeptic Coverage
# ---------------------------------------------------------------------------


def _check_skeptic_coverage(
    task: Task,
    p: AgentResponse,
    failures: list[FailureInstance],
    flags: list[ForensicFlag],
) -> float:
    """Check if counterarguments are treated seriously, not decoratively."""
    score = 0.0

    n_counter = len(p.counterarguments)
    n_alt = len(p.alternative_hypotheses)

    if n_counter == 0 and n_alt == 0:
        failures.append(
            FailureInstance(
                category=FailureCategory.INSUFFICIENT_SKEPTICISM.value,
                severity=FailureSeverity.MODERATE.value,
                description="No counterarguments or alternative hypotheses considered",
                impact_on_score="skeptic_depth",
            )
        )
        return 0.0

    # Count substantive counterarguments (>40 chars, contain reasoning words)
    reasoning_words = (
        "because",
        "since",
        "however",
        "but",
        "although",
        "despite",
        "unlikely",
        "possible",
        "risk",
        "could",
        "might",
        "if",
    )
    substantive_counter = 0
    for c in p.counterarguments:
        if len(c) > 40 and any(w in c.lower() for w in reasoning_words):
            substantive_counter += 1

    if substantive_counter >= 2:
        score += 0.60
    elif substantive_counter >= 1:
        score += 0.40
    elif n_counter >= 1:
        score += 0.15
        flags.append(
            ForensicFlag(
                flag_type="decorative_skepticism",
                description="Counterarguments listed but appear superficial (short, no reasoning)",
                severity="minor",
            )
        )

    # Alternative hypotheses add value
    substantive_alt = sum(1 for h in p.alternative_hypotheses if len(h) > 40)
    if substantive_alt >= 1:
        score += 0.25

    # Bonus: uncertainty + counterargument together
    if p.uncertainties and n_counter >= 1:
        score += 0.15

    return max(0.0, min(1.0, score))


# ---------------------------------------------------------------------------
# E. No-Trade Integrity
# ---------------------------------------------------------------------------


def _check_no_trade_integrity(
    task: Task,
    p: AgentResponse,
    failures: list[FailureInstance],
    flags: list[ForensicFlag],
) -> float:
    """Check quality of no-trade / abstain / watch decisions."""
    cat = p.decision_category.lower().strip()

    if cat not in ("no_trade", "abstain", "watch"):
        # Not a no-trade decision — return neutral
        return 0.5

    score = 0.3  # base for any no-action decision

    # Justification quality
    all_text = " ".join(
        [p.final_answer, *p.steps, p.edge_justification, p.shrinkage_rationale]
    ).lower()

    # Look for substantive justification
    justification_words = (
        "insufficient",
        "unclear",
        "ambiguous",
        "uncertain",
        "not enough",
        "lack of",
        "conflicting",
        "cannot determine",
        "no clear edge",
        "too close",
        "balanced",
        "indeterminate",
        "information",
        "evidence",
        "data",
    )
    n_just_words = sum(1 for w in justification_words if w in all_text)

    if n_just_words >= 3:
        score += 0.40
    elif n_just_words >= 1:
        score += 0.20
    else:
        # No-trade without any reasoning
        failures.append(
            FailureInstance(
                category=FailureCategory.WEAK_NO_TRADE_JUSTIFICATION.value,
                severity=FailureSeverity.MODERATE.value,
                description=f"Decision is '{cat}' but lacks substantive justification",
                evidence=[
                    EvidenceSpan(
                        text=p.final_answer[:200],
                        source_field="final_answer",
                        relevance="No-action decision without reasoning",
                    )
                ],
                impact_on_score="no_action_quality",
            )
        )

    # Check for empty abstention (no reasoning at all)
    if cat in ("abstain", "no_trade") and len(p.steps) == 0:
        failures.append(
            FailureInstance(
                category=FailureCategory.ABSTENTION_WITHOUT_CAUSE.value,
                severity=FailureSeverity.MAJOR.value,
                description="Abstention with zero reasoning steps — empty non-decision",
                impact_on_score="no_action_quality, structural_reasoning",
            )
        )
        score -= 0.20

    # Counterarguments strengthens no-trade
    if p.counterarguments and len(p.counterarguments) >= 1:
        score += 0.15

    # Check if correct decision IS no_trade
    if task.correct_decision and task.correct_decision.lower() in (
        "no_trade",
        "abstain",
        "watch",
    ):
        if cat in ("no_trade", "abstain", "watch"):
            score += 0.15  # got the right call

    return max(0.0, min(1.0, score))


# ---------------------------------------------------------------------------
# F. Shrinkage Discipline
# ---------------------------------------------------------------------------


def _check_shrinkage_discipline(
    task: Task,
    p: AgentResponse,
    failures: list[FailureInstance],
    flags: list[ForensicFlag],
) -> float:
    """Check if raw forecast was appropriately adjusted toward base rate."""
    score = 0.5  # base

    prob = p.probability_estimate
    if prob is None:
        return 0.3

    has_shrinkage = bool(p.shrinkage_rationale.strip())
    has_base_ref = bool(p.base_rate_reference.strip())

    # Extreme probability without shrinkage rationale
    if (prob >= 0.90 or prob <= 0.10) and not has_shrinkage:
        failures.append(
            FailureInstance(
                category=FailureCategory.SHRINKAGE_FAILURE.value,
                severity=FailureSeverity.MODERATE.value,
                description=(
                    f"Extreme probability ({prob:.0%}) without shrinkage/adjustment rationale"
                ),
                evidence=[
                    EvidenceSpan(
                        text=f"probability: {prob:.0%}",
                        source_field="probability_estimate",
                        relevance="Extreme estimate without acknowledged adjustment",
                    )
                ],
                impact_on_score="uncertainty_honesty",
            )
        )
        score -= 0.25

    # Has shrinkage rationale — positive signal
    if has_shrinkage:
        score += 0.20
        if len(p.shrinkage_rationale) > 40:
            score += 0.10  # substantive explanation

    # Shrinkage toward base rate is strongest signal
    if has_shrinkage and has_base_ref:
        score += 0.15

    return max(0.0, min(1.0, score))


# ---------------------------------------------------------------------------
# G. Narrative Edge
# ---------------------------------------------------------------------------


def _check_narrative_edge(
    task: Task,
    p: AgentResponse,
    failures: list[FailureInstance],
    flags: list[ForensicFlag],
) -> float:
    """Check if claimed edge is substantiated or just rhetorical."""
    score = 0.5

    edge = p.edge_justification.strip()
    cat = p.decision_category.lower().strip()

    # No edge claimed — fine for no_trade/abstain, weak for forecast
    if not edge:
        if cat in ("forecast",):
            failures.append(
                FailureInstance(
                    category=FailureCategory.FALSE_EDGE_DETECTION.value,
                    severity=FailureSeverity.MODERATE.value,
                    description="Forecasting decision without stated edge justification",
                    impact_on_score="support_strength",
                )
            )
            score -= 0.20
        return max(0.0, min(1.0, score))

    # Check if edge is substantive
    edge_lower = edge.lower()

    # Narrative-only signals (rhetorical without evidence)
    narrative_words = (
        "clearly",
        "obviously",
        "market is wrong",
        "everyone knows",
        "it's clear that",
        "no doubt",
        "inevitable",
        "certain",
        "definitely",
        "surely",
        "undoubtedly",
    )
    n_narrative = sum(1 for w in narrative_words if w in edge_lower)

    # Evidence-based signals
    evidence_words = (
        "data shows",
        "historically",
        "evidence",
        "base rate",
        "statistics",
        "prior",
        "research",
        "study",
        "analysis",
        "because",
        "specifically",
        "according to",
    )
    n_evidence = sum(1 for w in evidence_words if w in edge_lower)

    if n_narrative >= 2 and n_evidence == 0:
        failures.append(
            FailureInstance(
                category=FailureCategory.NARRATIVE_OVERREACH.value,
                severity=FailureSeverity.MODERATE.value,
                description="Edge justification is rhetorical — no evidence-based reasoning",
                evidence=[
                    EvidenceSpan(
                        text=edge[:200],
                        source_field="edge_justification",
                        relevance="Narrative without evidence",
                        role=EvidenceRole.WEAKENING,
                    )
                ],
                impact_on_score="support_strength",
            )
        )
        score -= 0.25

    if n_evidence >= 2:
        score += 0.25
    elif n_evidence >= 1:
        score += 0.15

    # Length as very rough quality proxy
    if len(edge) > 100:
        score += 0.10

    return max(0.0, min(1.0, score))


# ---------------------------------------------------------------------------
# Decision Category Check
# ---------------------------------------------------------------------------


def _check_decision_category(
    task: Task,
    p: AgentResponse,
    failures: list[FailureInstance],
) -> None:
    """Check if the chosen decision category matches the correct one."""
    if not task.correct_decision:
        return

    cat = p.decision_category.lower().strip()
    expected = task.correct_decision.lower().strip()

    if not cat:
        return  # no decision stated

    # Map equivalent terms
    equiv = {
        "no_trade": {"no_trade", "abstain"},
        "abstain": {"no_trade", "abstain"},
        "watch": {"watch"},
        "forecast": {"forecast"},
    }

    cat_set = equiv.get(cat, {cat})
    expected_set = equiv.get(expected, {expected})

    if not cat_set & expected_set:
        failures.append(
            FailureInstance(
                category=FailureCategory.OPPORTUNITY_MISCLASSIFICATION.value,
                severity=FailureSeverity.MAJOR.value,
                description=(
                    f"Decision category '{cat}' does not match expected '{expected}'"
                ),
                evidence=[
                    EvidenceSpan(
                        text=f"agent: {cat}, expected: {expected}",
                        source_field="decision_category",
                        relevance="Wrong decision category",
                    )
                ],
                impact_on_score="correctness",
            )
        )
