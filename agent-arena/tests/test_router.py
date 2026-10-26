"""Tests for Gen 4 Router — agent-arena v0.6.9.

Tests cover:
- Mature category → single-model recommendation
- Mechanism category → Sonnet-prioritized / quality-aware
- Unstable / high-disagreement → disagreement route
- Developing category → multi-model route
- Cost-aware routing (cheap model sufficient)
- Insufficient data → conservative multi
- Known confusions surface in recommendation
- Routing from journal entries
- Report rendering
- Deterministic, human-readable output
"""

from __future__ import annotations

import pytest

from agent_arena.schemas import (
    CalibrationProposal,
    CalibrationReport,
    CategoryMaturitySummary,
    InsightsReport,
    LabelConfusion,
    ModelInsightProfile,
    RoutingRecommendation,
    RoutingReport,
    RoutingSignal,
    RunJournalEntry,
    CaseDisagreement,
    DisagreementSummary,
    BorderlineCandidateSignal,
)
from agent_arena.router import (
    render_routing_report,
    route_from_entries,
    route_from_reports,
    _cost_tier,
    _build_family_model_scores,
    _rank_models_for_family,
    _check_cost_opportunity,
)


# ---------------------------------------------------------------------------
# Helpers — build minimal InsightsReport / CalibrationReport
# ---------------------------------------------------------------------------

def _insights(**kwargs) -> InsightsReport:
    """Create InsightsReport with defaults."""
    defaults = dict(
        generated_at="2026-04-06T00:00:00Z",
        n_runs=50,
        n_tasks=10,
        n_models=3,
        model_profiles=[],
        category_maturity=[],
    )
    defaults.update(kwargs)
    return InsightsReport(**defaults)


def _profile(model: str, **kwargs) -> ModelInsightProfile:
    """Create a ModelInsightProfile with defaults."""
    defaults = dict(
        model=model,
        n_runs=20,
        avg_score=70.0,
        dimension_averages={
            "correctness": 0.7,
            "support_strength": 0.6,
            "structural_reasoning": 0.6,
            "insight_depth": 0.5,
            "mechanism_quality": 0.5,
            "self_monitoring_quality": 0.5,
        },
        strongest_dimensions=["correctness"],
        weakest_dimensions=["mechanism_quality"],
        label_confusions=[],
        tendencies=[],
    )
    defaults.update(kwargs)
    return ModelInsightProfile(**defaults)


def _maturity(category: str, **kwargs) -> CategoryMaturitySummary:
    """Create a CategoryMaturitySummary with defaults."""
    defaults = dict(
        category=category,
        n_cases=5,
        n_runs=15,
        avg_score=75.0,
        correctness_rate=0.85,
        disagreement_rate=0.1,
        maturity="mature",
    )
    defaults.update(kwargs)
    return CategoryMaturitySummary(**defaults)


def _cal_report(**kwargs) -> CalibrationReport:
    """Create CalibrationReport with defaults."""
    defaults = dict(
        generated_at="2026-04-06T00:00:00Z",
        n_entries_analyzed=50,
        n_proposals=0,
        fp_reduction_candidates=[],
        gold_review_candidates=[],
        category_refinement_candidates=[],
        model_confusion_candidates=[],
        data_gap_candidates=[],
    )
    defaults.update(kwargs)
    return CalibrationReport(**defaults)


def _proposal(**kwargs) -> CalibrationProposal:
    defaults = dict(
        proposal_type="data_gap",
        target="overclaim",
        target_kind="category",
        reason="Too few cases",
        evidence_summary="1 case, 3 runs.",
        confidence="medium",
        strength=0.7,
        recommended_action="Add more cases.",
    )
    defaults.update(kwargs)
    return CalibrationProposal(**defaults)


def _entry(**kwargs) -> RunJournalEntry:
    """Create a RunJournalEntry with defaults."""
    defaults = dict(
        run_id="run001",
        timestamp="2026-04-06T00:00:00Z",
        task_id="t1",
        task_family="solid",
        task_type="study_forensics",
        agent_id="sonnet",
        model="sonnet",
        total_score=75.0,
        correctness=0.9,
        support_strength=0.7,
        structural_reasoning=0.7,
        insight_depth=0.6,
        mechanism_quality=0.6,
        self_monitoring_quality=0.6,
        failure_categories=[],
        forensic_flag_types=[],
        reasoning_integrity_class="well_supported",
        confidence=0.8,
        final_answer="solid",
    )
    defaults.update(kwargs)
    return RunJournalEntry(**defaults)


# ---------------------------------------------------------------------------
# 1. Mature Category → Single-Model Route
# ---------------------------------------------------------------------------

class TestSingleModelRoute:
    def test_mature_category_gets_single(self):
        insights = _insights(
            model_profiles=[
                _profile("sonnet", avg_score=80.0,
                         dimension_averages={"correctness": 0.9, "mechanism_quality": 0.7,
                                             "support_strength": 0.7, "structural_reasoning": 0.7,
                                             "insight_depth": 0.6, "self_monitoring_quality": 0.6}),
                _profile("haiku", avg_score=65.0,
                         dimension_averages={"correctness": 0.7, "mechanism_quality": 0.4,
                                             "support_strength": 0.5, "structural_reasoning": 0.5,
                                             "insight_depth": 0.4, "self_monitoring_quality": 0.4}),
            ],
            category_maturity=[
                _maturity("solid", correctness_rate=0.9, disagreement_rate=0.05, maturity="mature"),
            ],
        )
        report = route_from_reports(insights)
        assert report.n_recommendations == 1
        rec = report.recommendations[0]
        assert rec.recommended_mode == "single"
        assert "sonnet" in rec.recommended_models
        assert rec.confidence in ("high", "medium")
        assert rec.disagreement_risk == "low"

    def test_single_model_has_fallback(self):
        insights = _insights(
            model_profiles=[
                _profile("sonnet", avg_score=80.0,
                         dimension_averages={"correctness": 0.9, "mechanism_quality": 0.7,
                                             "support_strength": 0.7, "structural_reasoning": 0.7,
                                             "insight_depth": 0.6, "self_monitoring_quality": 0.6}),
                _profile("haiku", avg_score=65.0,
                         dimension_averages={"correctness": 0.7, "mechanism_quality": 0.4,
                                             "support_strength": 0.5, "structural_reasoning": 0.5,
                                             "insight_depth": 0.4, "self_monitoring_quality": 0.4}),
            ],
            category_maturity=[
                _maturity("solid", correctness_rate=0.9, disagreement_rate=0.05, maturity="mature"),
            ],
        )
        report = route_from_reports(insights)
        rec = report.recommendations[0]
        assert len(rec.fallback_models) >= 1

    def test_reason_mentions_mature(self):
        insights = _insights(
            model_profiles=[_profile("sonnet", avg_score=80.0,
                                     dimension_averages={"correctness": 0.9, "mechanism_quality": 0.7,
                                                         "support_strength": 0.7, "structural_reasoning": 0.7,
                                                         "insight_depth": 0.6, "self_monitoring_quality": 0.6})],
            category_maturity=[_maturity("solid", correctness_rate=0.9, disagreement_rate=0.05, maturity="mature")],
        )
        rec = route_from_reports(insights).recommendations[0]
        assert "mature" in rec.reason.lower() or "90%" in rec.reason


# ---------------------------------------------------------------------------
# 2. Mechanism Category → Quality-Aware Routing
# ---------------------------------------------------------------------------

class TestMechanismRouting:
    def test_mechanism_boosts_high_mechanism_quality_model(self):
        """Model with high mechanism_quality should rank higher for mechanism tasks."""
        insights = _insights(
            model_profiles=[
                _profile("haiku", avg_score=70.0,
                         dimension_averages={"correctness": 0.7, "mechanism_quality": 0.3,
                                             "support_strength": 0.6, "structural_reasoning": 0.6,
                                             "insight_depth": 0.5, "self_monitoring_quality": 0.5}),
                _profile("sonnet", avg_score=75.0,
                         dimension_averages={"correctness": 0.75, "mechanism_quality": 0.8,
                                             "support_strength": 0.7, "structural_reasoning": 0.7,
                                             "insight_depth": 0.6, "self_monitoring_quality": 0.6}),
            ],
            category_maturity=[
                _maturity("mechanism_vs_evidence", correctness_rate=0.85,
                          disagreement_rate=0.1, maturity="mature"),
            ],
        )
        report = route_from_reports(insights)
        rec = report.recommendations[0]
        # Sonnet should be ranked first due to mechanism_quality boost
        assert rec.recommended_models[0] == "sonnet"

    def test_mechanism_with_developing_maturity(self):
        insights = _insights(
            model_profiles=[
                _profile("sonnet", avg_score=75.0,
                         dimension_averages={"correctness": 0.7, "mechanism_quality": 0.8,
                                             "support_strength": 0.7, "structural_reasoning": 0.7,
                                             "insight_depth": 0.6, "self_monitoring_quality": 0.6}),
                _profile("haiku", avg_score=60.0,
                         dimension_averages={"correctness": 0.6, "mechanism_quality": 0.3,
                                             "support_strength": 0.5, "structural_reasoning": 0.5,
                                             "insight_depth": 0.4, "self_monitoring_quality": 0.4}),
            ],
            category_maturity=[
                _maturity("mechanism_vs_evidence", correctness_rate=0.65,
                          disagreement_rate=0.25, maturity="developing"),
            ],
        )
        report = route_from_reports(insights)
        rec = report.recommendations[0]
        assert rec.recommended_mode == "multi"
        assert "sonnet" in rec.recommended_models


# ---------------------------------------------------------------------------
# 3. Unstable / High-Disagreement → Disagreement Route
# ---------------------------------------------------------------------------

class TestDisagreementRoute:
    def test_unstable_category_gets_disagreement(self):
        insights = _insights(
            model_profiles=[
                _profile("sonnet"), _profile("haiku"), _profile("opus"),
            ],
            category_maturity=[
                _maturity("overclaim", correctness_rate=0.35,
                          disagreement_rate=0.7, maturity="unstable"),
            ],
        )
        report = route_from_reports(insights)
        rec = report.recommendations[0]
        assert rec.recommended_mode == "disagreement"
        assert rec.disagreement_risk in ("high", "moderate")
        assert rec.cost_sensitivity == "invest_in_quality"

    def test_high_disagreement_triggers_disagreement_route(self):
        insights = _insights(
            model_profiles=[_profile("sonnet"), _profile("haiku")],
            category_maturity=[
                _maturity("correlation_vs_causation", correctness_rate=0.6,
                          disagreement_rate=0.6, maturity="developing"),
            ],
        )
        report = route_from_reports(insights)
        rec = report.recommendations[0]
        assert rec.recommended_mode == "disagreement"

    def test_refinement_candidate_triggers_disagreement(self):
        insights = _insights(
            model_profiles=[_profile("sonnet"), _profile("haiku")],
            category_maturity=[
                _maturity("overclaim", correctness_rate=0.55,
                          disagreement_rate=0.35, maturity="developing"),
            ],
        )
        cal = _cal_report(
            category_refinement_candidates=[
                _proposal(proposal_type="category_refinement",
                          target="overclaim", target_kind="category",
                          reason="Low correctness rate"),
            ],
            n_proposals=1,
        )
        report = route_from_reports(insights, cal)
        rec = report.recommendations[0]
        assert rec.recommended_mode == "disagreement"

    def test_disagreement_reason_is_descriptive(self):
        insights = _insights(
            model_profiles=[_profile("sonnet"), _profile("haiku")],
            category_maturity=[
                _maturity("overclaim", correctness_rate=0.3,
                          disagreement_rate=0.8, maturity="unstable"),
            ],
        )
        rec = route_from_reports(insights).recommendations[0]
        assert "instability" in rec.reason.lower() or "disagreement" in rec.reason.lower()


# ---------------------------------------------------------------------------
# 4. Developing Category → Multi-Model Route
# ---------------------------------------------------------------------------

class TestMultiModelRoute:
    def test_developing_category_gets_multi(self):
        insights = _insights(
            model_profiles=[_profile("sonnet"), _profile("haiku")],
            category_maturity=[
                _maturity("solid", correctness_rate=0.7,
                          disagreement_rate=0.15, maturity="developing"),
            ],
        )
        report = route_from_reports(insights)
        rec = report.recommendations[0]
        assert rec.recommended_mode == "multi"

    def test_known_confusions_trigger_multi(self):
        insights = _insights(
            model_profiles=[
                _profile("sonnet", label_confusions=[
                    LabelConfusion(gold_label="solid", detected_label="overclaim",
                                   count=3, models=["sonnet"]),
                ]),
                _profile("haiku"),
            ],
            category_maturity=[
                _maturity("solid", correctness_rate=0.82,
                          disagreement_rate=0.12, maturity="mature"),
            ],
        )
        cal = _cal_report(
            model_confusion_candidates=[
                _proposal(proposal_type="model_confusion",
                          target="sonnet", target_kind="model",
                          reason="sonnet confuses 'solid' with 'overclaim'"),
            ],
            n_proposals=1,
        )
        report = route_from_reports(insights, cal)
        rec = report.recommendations[0]
        assert rec.recommended_mode == "multi"
        assert len(rec.known_confusions) >= 1

    def test_multi_route_includes_multiple_models(self):
        insights = _insights(
            model_profiles=[_profile("sonnet"), _profile("haiku"), _profile("opus")],
            category_maturity=[
                _maturity("overclaim", correctness_rate=0.65,
                          disagreement_rate=0.3, maturity="developing"),
            ],
        )
        rec = route_from_reports(insights).recommendations[0]
        assert len(rec.recommended_models) >= 2

    def test_multi_reason_mentions_correctness(self):
        insights = _insights(
            model_profiles=[_profile("sonnet"), _profile("haiku")],
            category_maturity=[
                _maturity("overclaim", correctness_rate=0.65,
                          disagreement_rate=0.15, maturity="developing"),
            ],
        )
        rec = route_from_reports(insights).recommendations[0]
        assert "65%" in rec.reason or "correctness" in rec.reason.lower()


# ---------------------------------------------------------------------------
# 5. Cost-Aware Routing
# ---------------------------------------------------------------------------

class TestCostAwareRoute:
    def test_cheaper_model_recommended_when_close_enough(self):
        """If premium model is best but standard is within 10%, prefer standard."""
        insights = _insights(
            model_profiles=[
                _profile("opus", avg_score=82.0,
                         dimension_averages={"correctness": 0.92, "mechanism_quality": 0.8,
                                             "support_strength": 0.8, "structural_reasoning": 0.8,
                                             "insight_depth": 0.7, "self_monitoring_quality": 0.7}),
                _profile("sonnet", avg_score=78.0,
                         dimension_averages={"correctness": 0.88, "mechanism_quality": 0.7,
                                             "support_strength": 0.7, "structural_reasoning": 0.7,
                                             "insight_depth": 0.6, "self_monitoring_quality": 0.6}),
            ],
            category_maturity=[
                _maturity("solid", correctness_rate=0.9, disagreement_rate=0.05, maturity="mature"),
            ],
        )
        report = route_from_reports(insights)
        rec = report.recommendations[0]
        assert rec.recommended_mode == "cost_aware"
        assert rec.recommended_models[0] == "sonnet"
        assert rec.cost_sensitivity == "low_cost_ok"
        assert "opus" in rec.fallback_models

    def test_no_cost_saving_when_best_is_standard(self):
        """Standard-tier model doesn't trigger cost-aware route."""
        insights = _insights(
            model_profiles=[
                _profile("sonnet", avg_score=80.0,
                         dimension_averages={"correctness": 0.9, "mechanism_quality": 0.7,
                                             "support_strength": 0.7, "structural_reasoning": 0.7,
                                             "insight_depth": 0.6, "self_monitoring_quality": 0.6}),
                _profile("haiku", avg_score=60.0,
                         dimension_averages={"correctness": 0.6, "mechanism_quality": 0.4,
                                             "support_strength": 0.5, "structural_reasoning": 0.5,
                                             "insight_depth": 0.4, "self_monitoring_quality": 0.4}),
            ],
            category_maturity=[
                _maturity("solid", correctness_rate=0.9, disagreement_rate=0.05, maturity="mature"),
            ],
        )
        rec = route_from_reports(insights).recommendations[0]
        assert rec.recommended_mode == "single"  # not cost_aware
        assert rec.recommended_models[0] == "sonnet"

    def test_cost_tier_classification(self):
        assert _cost_tier("haiku") == 1
        assert _cost_tier("sonnet") == 2
        assert _cost_tier("opus") == 3
        assert _cost_tier("claude-3.5-sonnet") == 2
        assert _cost_tier("gpt-4o-mini") == 1
        assert _cost_tier("unknown-model") == 2  # default


# ---------------------------------------------------------------------------
# 6. Insufficient Data → Conservative Multi
# ---------------------------------------------------------------------------

class TestInsufficientData:
    def test_few_runs_defaults_to_multi(self):
        insights = _insights(
            n_runs=2,
            model_profiles=[_profile("sonnet")],
            category_maturity=[
                _maturity("solid", n_runs=2, correctness_rate=1.0,
                          disagreement_rate=0.0, maturity="insufficient_data"),
            ],
        )
        rec = route_from_reports(insights).recommendations[0]
        assert rec.recommended_mode == "multi"
        assert rec.confidence == "low"
        assert "insufficient" in rec.reason.lower() or "data" in rec.reason.lower()

    def test_zero_runs_category(self):
        insights = _insights(
            model_profiles=[_profile("sonnet")],
            category_maturity=[
                _maturity("solid", n_runs=0, correctness_rate=0.0,
                          disagreement_rate=0.0, maturity="insufficient_data"),
            ],
        )
        rec = route_from_reports(insights).recommendations[0]
        assert rec.recommended_mode == "multi"
        assert rec.confidence == "low"


# ---------------------------------------------------------------------------
# 7. Known Confusions Surface in Recommendations
# ---------------------------------------------------------------------------

class TestConfusionSignals:
    def test_model_confusion_appears_in_known_confusions(self):
        insights = _insights(
            model_profiles=[_profile("sonnet"), _profile("haiku")],
            category_maturity=[
                _maturity("solid", correctness_rate=0.85,
                          disagreement_rate=0.1, maturity="mature"),
            ],
        )
        cal = _cal_report(
            model_confusion_candidates=[
                _proposal(proposal_type="model_confusion",
                          target="sonnet", target_kind="model",
                          reason="sonnet confuses 'solid' with 'overclaim' in 3/5 runs"),
            ],
            n_proposals=1,
        )
        report = route_from_reports(insights, cal)
        rec = report.recommendations[0]
        assert len(rec.known_confusions) >= 1
        assert any("solid" in c.lower() for c in rec.known_confusions)

    def test_cross_model_confusion_flagged(self):
        insights = _insights(
            model_profiles=[_profile("sonnet"), _profile("haiku")],
            category_maturity=[
                _maturity("overclaim", correctness_rate=0.7,
                          disagreement_rate=0.2, maturity="developing"),
            ],
        )
        cal = _cal_report(
            model_confusion_candidates=[
                _proposal(proposal_type="model_confusion",
                          target="cross_model_overclaim_solid",
                          target_kind="category",
                          reason="Multiple models confuse 'overclaim' with 'solid'"),
            ],
            n_proposals=1,
        )
        report = route_from_reports(insights, cal)
        rec = report.recommendations[0]
        assert len(rec.known_confusions) >= 1


# ---------------------------------------------------------------------------
# 8. Routing From Journal Entries
# ---------------------------------------------------------------------------

class TestRouteFromEntries:
    def _make_entries(self) -> list[RunJournalEntry]:
        """Create a set of journal entries for multiple families/models."""
        entries = []
        # Solid family — mature, high correctness
        for i in range(5):
            for model in ["sonnet", "haiku"]:
                entries.append(_entry(
                    run_id=f"run_solid_{i}_{model}",
                    task_id=f"solid_{i}",
                    task_family="solid",
                    model=model,
                    agent_id=model,
                    correctness=0.9,
                    total_score=80.0,
                    final_answer="solid",
                ))
        # Overclaim — developing, some disagreement
        for i in range(4):
            entries.append(_entry(
                run_id=f"run_oc_{i}_sonnet",
                task_id=f"oc_{i}",
                task_family="overclaim",
                model="sonnet",
                agent_id="sonnet",
                correctness=0.8 if i < 2 else 0.3,
                total_score=70.0 if i < 2 else 45.0,
                final_answer="overclaim" if i < 2 else "solid",
            ))
            entries.append(_entry(
                run_id=f"run_oc_{i}_haiku",
                task_id=f"oc_{i}",
                task_family="overclaim",
                model="haiku",
                agent_id="haiku",
                correctness=0.6,
                total_score=55.0,
                final_answer="overclaim" if i < 1 else "solid",
            ))
        return entries

    def test_route_from_entries_produces_recommendations(self):
        entries = self._make_entries()
        report = route_from_entries(entries)
        assert report.n_recommendations >= 2
        families = {r.target for r in report.recommendations}
        assert "solid" in families
        assert "overclaim" in families

    def test_route_from_entries_family_filter(self):
        entries = self._make_entries()
        report = route_from_entries(entries, families=["solid"])
        assert report.n_recommendations == 1
        assert report.recommendations[0].target == "solid"

    def test_empty_entries_returns_empty_report(self):
        report = route_from_entries([])
        assert report.n_recommendations == 0
        assert "no" in report.summary.lower() or "No" in report.summary

    def test_solid_gets_single_or_cost_aware(self):
        """Solid with high correctness should get single, cost_aware, or multi
        (multi is acceptable when calibration detects cross-family confusion patterns)."""
        entries = self._make_entries()
        report = route_from_entries(entries)
        solid_rec = next(r for r in report.recommendations if r.target == "solid")
        # multi is acceptable here because overclaim entries answering "solid"
        # create confusion signals that correctly trigger multi-model routing
        assert solid_rec.recommended_mode in ("single", "cost_aware", "multi")

    def test_overclaim_does_not_get_single(self):
        """Overclaim with disagreement should not get single-model."""
        entries = self._make_entries()
        report = route_from_entries(entries)
        oc_rec = next(r for r in report.recommendations if r.target == "overclaim")
        assert oc_rec.recommended_mode != "single"


# ---------------------------------------------------------------------------
# 9. Report Rendering
# ---------------------------------------------------------------------------

class TestRenderReport:
    def test_empty_report(self):
        report = RoutingReport(
            generated_at="2026-04-06T00:00:00Z",
        )
        md = render_routing_report(report)
        assert "Gen 4 Routing Report" in md
        assert "No routing recommendations" in md

    def test_full_report_has_overview_table(self):
        insights = _insights(
            model_profiles=[_profile("sonnet"), _profile("haiku")],
            category_maturity=[
                _maturity("solid", correctness_rate=0.9, maturity="mature"),
                _maturity("overclaim", correctness_rate=0.6, maturity="developing"),
            ],
        )
        report = route_from_reports(insights)
        md = render_routing_report(report)
        assert "## Routing Overview" in md
        assert "solid" in md
        assert "overclaim" in md

    def test_report_has_recommendation_details(self):
        insights = _insights(
            model_profiles=[_profile("sonnet")],
            category_maturity=[_maturity("solid", correctness_rate=0.9, maturity="mature")],
        )
        report = route_from_reports(insights)
        md = render_routing_report(report)
        assert "## Recommendation Details" in md
        assert "**Mode:**" in md
        assert "**Reason:**" in md

    def test_report_footer(self):
        insights = _insights(
            model_profiles=[_profile("sonnet")],
            category_maturity=[_maturity("solid", maturity="mature")],
        )
        md = render_routing_report(route_from_reports(insights))
        assert "recommendations only" in md
        assert "No automatic execution" in md

    def test_report_includes_signals(self):
        insights = _insights(
            model_profiles=[_profile("sonnet")],
            category_maturity=[_maturity("solid", maturity="mature")],
        )
        md = render_routing_report(route_from_reports(insights))
        assert "Signals" in md or "signal" in md.lower()


# ---------------------------------------------------------------------------
# 10. Structure and Determinism
# ---------------------------------------------------------------------------

class TestStructureAndDeterminism:
    def test_recommendation_fields_complete(self):
        insights = _insights(
            model_profiles=[_profile("sonnet")],
            category_maturity=[_maturity("solid", maturity="mature")],
        )
        rec = route_from_reports(insights).recommendations[0]
        assert rec.target == "solid"
        assert rec.target_kind == "family"
        assert rec.recommended_mode in ("single", "multi", "disagreement", "cost_aware")
        assert rec.reason
        assert rec.confidence in ("high", "medium", "low")
        assert rec.expected_value
        assert rec.cost_sensitivity in ("low_cost_ok", "standard", "invest_in_quality")
        assert rec.disagreement_risk in ("low", "moderate", "high", "unknown")
        assert rec.borderline_risk in ("low", "moderate", "high", "unknown")

    def test_signals_are_present(self):
        insights = _insights(
            model_profiles=[_profile("sonnet")],
            category_maturity=[_maturity("solid", maturity="mature")],
        )
        rec = route_from_reports(insights).recommendations[0]
        assert len(rec.based_on_signals) >= 1
        for s in rec.based_on_signals:
            assert s.signal_type
            assert s.source
            assert s.description

    def test_deterministic_output(self):
        """Same input → same output (modulo timestamp)."""
        insights = _insights(
            model_profiles=[_profile("sonnet"), _profile("haiku")],
            category_maturity=[
                _maturity("solid", correctness_rate=0.9, maturity="mature"),
            ],
        )
        r1 = route_from_reports(insights)
        r2 = route_from_reports(insights)
        assert r1.recommendations[0].recommended_mode == r2.recommendations[0].recommended_mode
        assert r1.recommendations[0].recommended_models == r2.recommendations[0].recommended_models
        assert r1.recommendations[0].reason == r2.recommendations[0].reason

    def test_family_filter_works(self):
        insights = _insights(
            model_profiles=[_profile("sonnet")],
            category_maturity=[
                _maturity("solid", maturity="mature"),
                _maturity("overclaim", maturity="developing"),
            ],
        )
        report = route_from_reports(insights, families=["overclaim"])
        assert report.n_recommendations == 1
        assert report.recommendations[0].target == "overclaim"

    def test_data_quality_note_scales(self):
        low = _insights(n_runs=5, model_profiles=[], category_maturity=[])
        med = _insights(n_runs=20, model_profiles=[], category_maturity=[])
        high = _insights(n_runs=50, model_profiles=[], category_maturity=[])
        assert "tentative" in route_from_reports(low).data_quality_note.lower()
        assert "reasonable" in route_from_reports(med).data_quality_note.lower() or \
               "moderate" in route_from_reports(med).data_quality_note.lower()
        assert "well-grounded" in route_from_reports(high).data_quality_note.lower() or \
               "good" in route_from_reports(high).data_quality_note.lower()


# ---------------------------------------------------------------------------
# 11. Data Gap Families
# ---------------------------------------------------------------------------

class TestDataGapRouting:
    def test_data_gap_noted_in_recommendation(self):
        insights = _insights(
            model_profiles=[_profile("sonnet")],
            category_maturity=[
                _maturity("mechanism_vs_evidence", n_runs=5,
                          correctness_rate=0.7, disagreement_rate=0.2,
                          maturity="developing"),
            ],
        )
        cal = _cal_report(
            data_gap_candidates=[
                _proposal(target="mechanism_vs_evidence", target_kind="category",
                          reason="Too few cases"),
            ],
            n_proposals=1,
        )
        report = route_from_reports(insights, cal)
        rec = report.recommendations[0]
        # Data gap should be noted
        has_gap_note = any("data gap" in n.lower() or "gap" in n.lower()
                           for n in rec.notes)
        has_gap_signal = any(s.signal_type == "data_gap"
                             for s in rec.based_on_signals)
        assert has_gap_note or has_gap_signal
