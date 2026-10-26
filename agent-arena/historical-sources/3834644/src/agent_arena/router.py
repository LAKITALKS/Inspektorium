"""Gen 4 Router — transparent routing recommendation layer for agent-arena v0.6.9.

Recommends run strategies (which models, single vs multi, disagreement path)
based on observed evidence from Insights and Calibrate. Does NOT execute runs,
modify scores, or change gold labels.

Answers:
- Which model is strongest for this category?
- Is a single-model run sufficient or is multi-model needed?
- Should this case enter a disagreement / borderline path?
- Where is a cheaper model adequate?
- Where are known confusions relevant?

Data sources: InsightsReport, CalibrationReport, RunJournalEntry.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

from agent_arena.schemas import (
    CalibrationReport,
    CategoryMaturitySummary,
    InsightsReport,
    ModelInsightProfile,
    RoutingRecommendation,
    RoutingReport,
    RoutingSignal,
    RunJournalEntry,
)


# ---------------------------------------------------------------------------
# Model cost tiers (heuristic — can be overridden)
# ---------------------------------------------------------------------------

# Lower tier = cheaper.  Tier 1 = budget, Tier 2 = standard, Tier 3 = premium
_DEFAULT_COST_TIERS: dict[str, int] = {
    "haiku": 1,
    "claude-3-haiku": 1,
    "claude-3.5-haiku": 1,
    "gpt-4o-mini": 1,
    "sonnet": 2,
    "claude-3-sonnet": 2,
    "claude-3.5-sonnet": 2,
    "claude-sonnet-4": 2,
    "gpt-4o": 2,
    "opus": 3,
    "claude-3-opus": 3,
    "claude-opus-4": 3,
    "gpt-4": 3,
    "o1": 3,
    "o3": 3,
}

_TIER_LABELS = {1: "budget", 2: "standard", 3: "premium"}


def _cost_tier(model: str) -> int:
    """Return the cost tier for a model name (best-effort fuzzy match)."""
    ml = model.lower().strip()
    if ml in _DEFAULT_COST_TIERS:
        return _DEFAULT_COST_TIERS[ml]
    # Fuzzy: check if any key is a substring
    for key, tier in _DEFAULT_COST_TIERS.items():
        if key in ml or ml in key:
            return tier
    return 2  # default to standard


# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------

_MATURE_CORRECTNESS = 0.8       # category correctness >= 80% = mature enough for single
_UNSTABLE_CORRECTNESS = 0.5     # category correctness < 50% = unstable
_LOW_DISAGREEMENT = 0.2         # disagreement rate <= 20% = low
_HIGH_DISAGREEMENT = 0.5        # disagreement rate > 50% = high
_STRONG_MODEL_THRESHOLD = 0.75  # model correctness >= 75% in category = strong
_MIN_RUNS_FOR_ROUTING = 3       # need >= 3 runs to give confident recommendations
_CONFUSION_RELEVANCE = 0.2      # confusion rate >= 20% = relevant to routing


# ---------------------------------------------------------------------------
# Core: build routing recommendations from Insights + Calibrate
# ---------------------------------------------------------------------------

def route_from_reports(
    insights: InsightsReport,
    calibration: CalibrationReport | None = None,
    families: list[str] | None = None,
) -> RoutingReport:
    """Generate routing recommendations from pre-computed reports.

    Pure analysis — no side effects, no mutations.

    Args:
        insights: Gen 1 Insights report (required).
        calibration: Gen 2 Calibration report (optional, enriches recommendations).
        families: Restrict to specific families. None = all observed families.

    Returns:
        RoutingReport with per-family recommendations.
    """
    recommendations: list[RoutingRecommendation] = []

    # Build lookup structures
    maturity_map = {cm.category: cm for cm in insights.category_maturity}
    profile_map = {p.model: p for p in insights.model_profiles}

    # Per-family model performance from journal-derived profiles
    family_model_scores = _build_family_model_scores(insights)

    # Calibration signals
    confusion_signals = _extract_confusion_signals(calibration) if calibration else {}
    gap_families = _extract_gap_families(calibration) if calibration else set()
    refinement_families = _extract_refinement_families(calibration) if calibration else set()

    # Borderline / disagreement signals from insights
    borderline_tasks = {bc.task_id: bc for bc in insights.borderline_candidates}
    disagreement_families = _extract_disagreement_families(insights)

    # Determine which families to route
    target_families = families if families else sorted(maturity_map.keys())

    for family in target_families:
        maturity = maturity_map.get(family)
        fms = family_model_scores.get(family, {})
        confusions = confusion_signals.get(family, [])
        is_gap = family in gap_families
        is_refinement = family in refinement_families
        dis_rate = disagreement_families.get(family, 0.0)

        rec = _route_family(
            family=family,
            maturity=maturity,
            family_model_scores=fms,
            profile_map=profile_map,
            confusions=confusions,
            is_data_gap=is_gap,
            is_refinement_candidate=is_refinement,
            disagreement_rate=dis_rate,
            borderline_tasks=borderline_tasks,
        )
        recommendations.append(rec)

    # Data quality note
    total_runs = insights.n_runs
    if total_runs < 10:
        dq = f"Low data volume ({total_runs} runs). Recommendations are tentative."
    elif total_runs < 30:
        dq = f"Moderate data volume ({total_runs} runs). Recommendations are reasonable but may shift with more data."
    else:
        dq = f"Good data volume ({total_runs} runs). Recommendations are well-grounded."

    # Summary
    modes = defaultdict(int)
    for r in recommendations:
        modes[r.recommended_mode] += 1
    mode_parts = [f"{count} {mode}" for mode, count in sorted(modes.items())]
    summary = f"{len(recommendations)} routing recommendations: {', '.join(mode_parts)}."

    return RoutingReport(
        generated_at=datetime.now(timezone.utc).isoformat(),
        n_recommendations=len(recommendations),
        recommendations=recommendations,
        summary=summary,
        data_quality_note=dq,
    )


def route_from_entries(
    entries: list[RunJournalEntry],
    families: list[str] | None = None,
) -> RoutingReport:
    """Generate routing recommendations directly from journal entries.

    Convenience wrapper: computes Insights + Calibrate internally.
    """
    from agent_arena.insights import generate_insights
    from agent_arena.calibrate import generate_calibration_report

    if not entries:
        return RoutingReport(
            generated_at=datetime.now(timezone.utc).isoformat(),
            summary="No journal entries — no routing recommendations.",
            data_quality_note="No data available.",
        )

    insights = generate_insights(entries)
    calibration = generate_calibration_report(entries, insights)
    return route_from_reports(insights, calibration, families)


# ---------------------------------------------------------------------------
# Per-family routing decision
# ---------------------------------------------------------------------------

def _route_family(
    family: str,
    maturity: CategoryMaturitySummary | None,
    family_model_scores: dict[str, dict],
    profile_map: dict[str, ModelInsightProfile],
    confusions: list[str],
    is_data_gap: bool,
    is_refinement_candidate: bool,
    disagreement_rate: float,
    borderline_tasks: dict,
) -> RoutingRecommendation:
    """Decide routing for a single family based on all available signals."""

    signals: list[RoutingSignal] = []
    notes: list[str] = []
    known_confusions: list[str] = confusions[:]

    # --- Gather signals ---

    correctness_rate = 0.0
    n_runs = 0

    if maturity:
        correctness_rate = maturity.correctness_rate
        n_runs = maturity.n_runs
        signals.append(RoutingSignal(
            signal_type="maturity",
            source="insights:category_maturity",
            description=f"Category '{family}': maturity={maturity.maturity}, "
                        f"correctness={correctness_rate:.0%}, "
                        f"disagreement={maturity.disagreement_rate:.0%}",
            strength=correctness_rate,
        ))

    if is_data_gap:
        signals.append(RoutingSignal(
            signal_type="data_gap",
            source="calibrate:data_gap",
            description=f"Category '{family}' flagged as data gap",
            strength=0.6,
        ))
        notes.append(f"Data gap: '{family}' needs more cases for reliable routing.")

    if is_refinement_candidate:
        signals.append(RoutingSignal(
            signal_type="confusion",
            source="calibrate:category_refinement",
            description=f"Category '{family}' flagged for refinement",
            strength=0.7,
        ))

    if confusions:
        signals.append(RoutingSignal(
            signal_type="confusion",
            source="calibrate:model_confusion",
            description=f"{len(confusions)} known confusion pattern(s)",
            strength=min(0.3 * len(confusions), 1.0),
        ))

    if disagreement_rate > 0:
        signals.append(RoutingSignal(
            signal_type="disagreement",
            source="insights:disagreement_summary",
            description=f"Disagreement rate: {disagreement_rate:.0%}",
            strength=disagreement_rate,
        ))

    # --- Rank models for this family ---
    ranked_models = _rank_models_for_family(family_model_scores, profile_map)

    # --- Insufficient data → conservative multi-model ---
    if n_runs < _MIN_RUNS_FOR_ROUTING:
        return RoutingRecommendation(
            target=family,
            target_kind="family",
            recommended_mode="multi",
            recommended_models=[m for m, _ in ranked_models[:3]],
            reason=f"Insufficient data ({n_runs} runs) — defaulting to multi-model for observation.",
            confidence="low",
            expected_value="Gather baseline data across models for future routing.",
            cost_sensitivity="standard",
            notes=notes + [f"Only {n_runs} runs available. Need >= {_MIN_RUNS_FOR_ROUTING} for confident routing."],
            based_on_signals=signals,
            known_confusions=known_confusions,
            disagreement_risk="unknown",
            borderline_risk="unknown",
        )

    # --- Decision logic ---

    # DISAGREEMENT / BORDERLINE route
    if (disagreement_rate > _HIGH_DISAGREEMENT
            or is_refinement_candidate
            or (maturity and maturity.maturity == "unstable")):
        dis_risk = "high" if disagreement_rate > _HIGH_DISAGREEMENT else "moderate"
        bl_risk = "high" if is_refinement_candidate else "moderate"

        return RoutingRecommendation(
            target=family,
            target_kind="family",
            recommended_mode="disagreement",
            recommended_models=[m for m, _ in ranked_models[:3]],
            reason=_disagreement_reason(family, maturity, disagreement_rate, is_refinement_candidate),
            confidence="medium",
            expected_value="Detect cross-model disagreement patterns. Surface borderline cases.",
            cost_sensitivity="invest_in_quality",
            notes=notes + ["Run all available models. Compare outputs for calibration value."],
            based_on_signals=signals,
            known_confusions=known_confusions,
            disagreement_risk=dis_risk,
            borderline_risk=bl_risk,
        )

    # MULTI-MODEL route
    if (correctness_rate < _MATURE_CORRECTNESS
            or disagreement_rate > _LOW_DISAGREEMENT
            or confusions
            or (maturity and maturity.maturity == "developing")):

        # Determine how many models
        if confusions or disagreement_rate > 0.3:
            n_models = min(3, len(ranked_models))
            reason = _multi_reason(family, correctness_rate, disagreement_rate, confusions)
        else:
            n_models = 2
            reason = f"Category '{family}' is developing (correctness {correctness_rate:.0%}). " \
                     f"Two models provide useful comparison."

        return RoutingRecommendation(
            target=family,
            target_kind="family",
            recommended_mode="multi",
            recommended_models=[m for m, _ in ranked_models[:n_models]],
            fallback_models=[m for m, _ in ranked_models[n_models:n_models + 1]],
            reason=reason,
            confidence="medium",
            expected_value="Cross-validate classifications. Detect emerging disagreement patterns.",
            cost_sensitivity="standard",
            notes=notes,
            based_on_signals=signals,
            known_confusions=known_confusions,
            disagreement_risk="moderate" if disagreement_rate > _LOW_DISAGREEMENT else "low",
            borderline_risk="moderate" if is_data_gap else "low",
        )

    # SINGLE-MODEL route (mature category, strong model, low disagreement)
    if ranked_models:
        best_model, best_info = ranked_models[0]
        best_correctness = best_info.get("correctness", 0.0)

        # Cost-aware: if best model is premium and a cheaper one is close enough,
        # recommend cost-aware route instead
        cost_rec = _check_cost_opportunity(ranked_models)
        if cost_rec:
            return RoutingRecommendation(
                target=family,
                target_kind="family",
                recommended_mode="cost_aware",
                recommended_models=[cost_rec["model"]],
                fallback_models=[best_model] if cost_rec["model"] != best_model else [],
                reason=cost_rec["reason"],
                confidence="medium",
                expected_value=f"Comparable quality at lower cost. "
                               f"Fallback to {best_model} if quality drops.",
                cost_sensitivity="low_cost_ok",
                notes=notes + [cost_rec["note"]],
                based_on_signals=signals + [RoutingSignal(
                    signal_type="cost",
                    source="router:cost_analysis",
                    description=cost_rec["note"],
                    strength=cost_rec["saving"],
                )],
                known_confusions=known_confusions,
                disagreement_risk="low",
                borderline_risk="low",
            )

        signals.append(RoutingSignal(
            signal_type="model_strength",
            source="insights:model_profiles",
            description=f"Best model for '{family}': {best_model} "
                        f"(correctness {best_correctness:.0%})",
            strength=best_correctness,
        ))

        return RoutingRecommendation(
            target=family,
            target_kind="family",
            recommended_mode="single",
            recommended_models=[best_model],
            fallback_models=[m for m, _ in ranked_models[1:2]],
            reason=f"Category '{family}' is mature (correctness {correctness_rate:.0%}, "
                   f"disagreement {disagreement_rate:.0%}). "
                   f"{best_model} is strongest (correctness {best_correctness:.0%}).",
            confidence="high" if best_correctness >= 0.9 else "medium",
            expected_value=f"Reliable single-model classification. "
                          f"Additional models add marginal value.",
            cost_sensitivity="low_cost_ok" if _cost_tier(best_model) <= 1 else "standard",
            notes=notes,
            based_on_signals=signals,
            known_confusions=known_confusions,
            disagreement_risk="low",
            borderline_risk="low",
        )

    # Fallback: no model data at all
    return RoutingRecommendation(
        target=family,
        target_kind="family",
        recommended_mode="multi",
        recommended_models=[],
        reason=f"No model performance data for '{family}'. Defaulting to multi-model.",
        confidence="low",
        expected_value="Establish baseline model performance data.",
        cost_sensitivity="standard",
        notes=notes + ["No model-level data available."],
        based_on_signals=signals,
        known_confusions=known_confusions,
        disagreement_risk="unknown",
        borderline_risk="unknown",
    )


# ---------------------------------------------------------------------------
# Reason builders
# ---------------------------------------------------------------------------

def _disagreement_reason(
    family: str,
    maturity: CategoryMaturitySummary | None,
    disagreement_rate: float,
    is_refinement: bool,
) -> str:
    parts = [f"Category '{family}' has high instability:"]
    if maturity and maturity.maturity == "unstable":
        parts.append(f"maturity=unstable (correctness {maturity.correctness_rate:.0%})")
    if disagreement_rate > _HIGH_DISAGREEMENT:
        parts.append(f"disagreement rate {disagreement_rate:.0%}")
    if is_refinement:
        parts.append("flagged for category refinement")
    parts.append("Disagreement path recommended to surface calibration-relevant patterns.")
    return " ".join(parts)


def _multi_reason(
    family: str,
    correctness_rate: float,
    disagreement_rate: float,
    confusions: list[str],
) -> str:
    parts = [f"Category '{family}' needs multi-model validation:"]
    if correctness_rate < _MATURE_CORRECTNESS:
        parts.append(f"correctness {correctness_rate:.0%} (below {_MATURE_CORRECTNESS:.0%} threshold)")
    if disagreement_rate > _LOW_DISAGREEMENT:
        parts.append(f"disagreement rate {disagreement_rate:.0%}")
    if confusions:
        parts.append(f"{len(confusions)} known confusion pattern(s)")
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Model ranking helpers
# ---------------------------------------------------------------------------

def _build_family_model_scores(
    insights: InsightsReport,
) -> dict[str, dict[str, dict]]:
    """Build per-family per-model score summaries from model profiles.

    Returns: {family: {model: {"correctness": float, "avg_score": float, "n_runs": int}}}

    Uses label confusions and dimension averages as proxies for per-family
    model strength. This is approximate — direct per-family breakdowns
    would need raw journal entries.
    """
    result: dict[str, dict[str, dict]] = defaultdict(dict)

    for profile in insights.model_profiles:
        model = profile.model

        # Base metrics
        base_correctness = profile.dimension_averages.get("correctness", 0.5)
        base_score = profile.avg_score
        n_runs = profile.n_runs

        # All observed families (from category maturity)
        for cm in insights.category_maturity:
            family = cm.category

            # Start with global model metrics
            model_correctness = base_correctness
            model_score = base_score

            # Penalize for known confusions in this family
            for lc in profile.label_confusions:
                if lc.gold_label == family:
                    # This model confuses this family with something else
                    penalty = min(lc.count * 0.1, 0.3)
                    model_correctness = max(0.0, model_correctness - penalty)

            # Boost models with known strengths for mechanism tasks
            if family == "mechanism_vs_evidence":
                mech_quality = profile.dimension_averages.get("mechanism_quality", 0.5)
                if mech_quality > 0.7:
                    model_correctness = min(1.0, model_correctness + 0.1)

            result[family][model] = {
                "correctness": round(model_correctness, 3),
                "avg_score": round(model_score, 1),
                "n_runs": n_runs,
                "cost_tier": _cost_tier(model),
            }

    return dict(result)


def _rank_models_for_family(
    family_model_scores: dict[str, dict],
    profile_map: dict[str, ModelInsightProfile],
) -> list[tuple[str, dict]]:
    """Rank models by suitability for a family.

    Primary sort: correctness (desc), secondary: avg_score (desc).
    If no family-level data, fall back to global model profiles.
    """
    if family_model_scores:
        return sorted(
            family_model_scores.items(),
            key=lambda x: (x[1].get("correctness", 0), x[1].get("avg_score", 0)),
            reverse=True,
        )

    # Fallback: rank by global avg_score
    if profile_map:
        return [
            (model, {
                "correctness": p.dimension_averages.get("correctness", 0.5),
                "avg_score": p.avg_score,
                "n_runs": p.n_runs,
                "cost_tier": _cost_tier(model),
            })
            for model, p in sorted(
                profile_map.items(),
                key=lambda x: x[1].avg_score,
                reverse=True,
            )
        ]

    return []


def _check_cost_opportunity(
    ranked_models: list[tuple[str, dict]],
) -> dict | None:
    """Check if a cheaper model can substitute the best model.

    Returns a cost recommendation dict or None if no opportunity.
    """
    if len(ranked_models) < 2:
        return None

    best_model, best_info = ranked_models[0]
    best_tier = best_info.get("cost_tier", 2)
    best_correctness = best_info.get("correctness", 0.0)

    # Only recommend cost savings if best model is premium
    if best_tier < 3:
        return None

    # Look for a cheaper model with close enough performance
    for model, info in ranked_models[1:]:
        tier = info.get("cost_tier", 2)
        correctness = info.get("correctness", 0.0)

        if tier < best_tier and correctness >= best_correctness - 0.1:
            saving = round((best_tier - tier) / best_tier, 2)
            gap = round(best_correctness - correctness, 3)
            return {
                "model": model,
                "reason": f"'{model}' (tier {tier}) performs within {gap:.0%} of "
                          f"'{best_model}' (tier {best_tier}) at lower cost.",
                "note": f"Cost saving: tier {best_tier}→{tier}. "
                        f"Correctness gap: {gap:.1%}. "
                        f"Acceptable for mature categories.",
                "saving": saving,
            }

    return None


# ---------------------------------------------------------------------------
# Signal extraction from CalibrationReport
# ---------------------------------------------------------------------------

def _extract_confusion_signals(
    calibration: CalibrationReport,
) -> dict[str, list[str]]:
    """Extract per-family confusion descriptions from calibration report."""
    result: dict[str, list[str]] = defaultdict(list)
    for p in calibration.model_confusion_candidates:
        # Extract family from the reason text or target
        desc = f"{p.target}: {p.reason}"
        # Try to associate with family via affected_cases or target
        if p.target_kind == "category":
            # Cross-model confusion targets look like "cross_model_X_Y"
            parts = p.target.split("_")
            if len(parts) >= 3 and parts[0] == "cross":
                # cross_model_GOLD_DETECTED
                family = "_".join(parts[2:-1]) if len(parts) > 3 else parts[2]
                result[family].append(desc)
            else:
                result[p.target].append(desc)
        elif p.target_kind == "model":
            # Per-model confusion — parse family from reason
            for word in ["solid", "overclaim", "correlation_vs_causation",
                         "mechanism_vs_evidence"]:
                if word in p.reason.lower():
                    result[word].append(desc)
    return dict(result)


def _extract_gap_families(calibration: CalibrationReport) -> set[str]:
    """Extract families flagged as data gaps."""
    return {
        p.target for p in calibration.data_gap_candidates
        if p.target_kind == "category"
    }


def _extract_refinement_families(calibration: CalibrationReport) -> set[str]:
    """Extract families flagged for category refinement."""
    return {
        p.target for p in calibration.category_refinement_candidates
        if p.target_kind == "category"
    }


def _extract_disagreement_families(
    insights: InsightsReport,
) -> dict[str, float]:
    """Extract per-family disagreement rates from insights."""
    return {
        cm.category: cm.disagreement_rate
        for cm in insights.category_maturity
    }


# ---------------------------------------------------------------------------
# Report rendering — Markdown
# ---------------------------------------------------------------------------

def render_routing_report(report: RoutingReport) -> str:
    """Render RoutingReport as nüchtern, operative Markdown."""
    lines: list[str] = []

    def _h1(t: str) -> None:
        lines.append(f"# {t}")
        lines.append("")

    def _h2(t: str) -> None:
        lines.append(f"## {t}")
        lines.append("")

    def _h3(t: str) -> None:
        lines.append(f"### {t}")
        lines.append("")

    def _p(t: str) -> None:
        lines.append(t)
        lines.append("")

    _h1("Agent Arena — Gen 4 Routing Report")
    _p(f"**Generated:** {report.generated_at}  ")
    _p(f"**Recommendations:** {report.n_recommendations}")
    _p(f"**Data quality:** {report.data_quality_note}")

    if report.n_recommendations == 0:
        _p("_No routing recommendations. Run evaluations first to generate data._")
        return "\n".join(lines)

    _p(f"**Summary:** {report.summary}")

    # Overview table
    _h2("Routing Overview")
    lines.append("| Family | Mode | Models | Confidence | Disagreement Risk | Cost |")
    lines.append("|--------|------|--------|------------|-------------------|------|")
    for r in report.recommendations:
        models = ", ".join(r.recommended_models[:3]) if r.recommended_models else "—"
        lines.append(
            f"| {r.target} | **{r.recommended_mode}** | {models} | "
            f"{r.confidence} | {r.disagreement_risk} | {r.cost_sensitivity} |"
        )
    lines.append("")

    # Detail sections
    _h2("Recommendation Details")
    for r in report.recommendations:
        _h3(f"{r.target} ({r.target_kind})")
        _p(f"**Mode:** {r.recommended_mode}")
        _p(f"**Recommended models:** {', '.join(r.recommended_models) if r.recommended_models else 'none specified'}")
        if r.fallback_models:
            _p(f"**Fallback models:** {', '.join(r.fallback_models)}")
        _p(f"**Reason:** {r.reason}")
        _p(f"**Confidence:** {r.confidence}")
        _p(f"**Expected value:** {r.expected_value}")
        _p(f"**Cost sensitivity:** {r.cost_sensitivity}")

        if r.known_confusions:
            _p("**Known confusions:**")
            for c in r.known_confusions:
                lines.append(f"- {c}")
            lines.append("")

        _p(f"**Disagreement risk:** {r.disagreement_risk}")
        _p(f"**Borderline risk:** {r.borderline_risk}")

        if r.notes:
            _p("**Notes:**")
            for n in r.notes:
                lines.append(f"- {n}")
            lines.append("")

        if r.based_on_signals:
            _p("**Signals:**")
            for s in r.based_on_signals:
                lines.append(f"- [{s.signal_type}] {s.description} (strength: {s.strength:.2f})")
            lines.append("")

        lines.append("---")
        lines.append("")

    # Footer
    _p("*Gen 4 Router — recommendations only. No automatic execution, "
       "score changes, or gold label modifications.*")

    return "\n".join(lines)
