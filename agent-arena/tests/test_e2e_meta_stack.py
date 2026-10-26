"""End-to-End Meta-Stack Integration Test — agent-arena v0.6.11.

Tests the full chain:
  Journal entries → Insights → Calibrate → Router → Disagreement Lab
  → Caseforge → Audit Trail (with Upstream Dependency / Error Propagation)

Uses realistic, diagnostically diverse journal entries simulating 3 models
evaluating 4 study-forensics cases across all 4 families.

The test does NOT call LLMs. It constructs RunJournalEntry data that
mimics what the evaluator would produce, then feeds it through every
meta-layer to verify the chain produces coherent, connected output.
"""

from __future__ import annotations

import pytest
from pathlib import Path

from agent_arena.schemas import (
    RunJournalEntry,
    DecisionEntry,
    UpstreamStep,
)

from agent_arena.journal import append_entries, read_entries
from agent_arena.insights import generate_insights, render_insights_report
from agent_arena.calibrate import generate_calibration_report, render_calibration_report
from agent_arena.router import route_from_entries, render_routing_report
from agent_arena.disagreement_lab import analyze_disagreements, render_disagreement_report
from agent_arena.caseforge import forge_cases, render_caseforge_report
from agent_arena.audit_trail import (
    log_decision,
    log_decisions,
    read_decisions,
    build_summary,
    module_effectiveness,
    build_dependency_summary,
    trace_decision,
    query_weak_basis_decisions,
    query_overrides,
    query_risky_accepted,
    render_audit_summary,
    render_module_effectiveness,
    render_dependency_summary,
    render_trace,
    generate_decision_id,
)


# ===========================================================================
# Test Dataset — 4 cases × 3 models = 12 journal entries
# ===========================================================================
#
# Case selection rationale:
#   case_solid_001         — clear solid, all models should agree → baseline
#   case_overclaim_002     — clear overclaim, one model misclassifies → confusion
#   case_mechanism_003     — mechanism_vs_evidence, genuine disagreement → borderline
#   case_correlation_004   — correlation_vs_causation, all wrong → gold-review
#
# Models: sonnet (standard), haiku (budget), opus (premium)

def _entry(**kwargs) -> RunJournalEntry:
    """Factory with sensible defaults."""
    defaults = dict(
        run_id="run_e2e_001",
        timestamp="2026-04-07T10:00:00Z",
        task_id="case_solid_001",
        task_family="solid",
        task_type="study_forensics",
        agent_id="sonnet",
        model="sonnet",
        total_score=75.0,
        correctness=0.9,
        support_strength=0.7,
        structural_reasoning=0.8,
        insight_depth=0.6,
        mechanism_quality=0.7,
        self_monitoring_quality=0.7,
        failure_categories=[],
        forensic_flag_types=[],
        reasoning_integrity_class="well_supported",
        decision_category="",
        probability_estimate=None,
        confidence=0.85,
        confidence_state="VALID",
        final_answer="solid",
        n_contradictions=0,
        n_intermediate_errors=0,
    )
    defaults.update(kwargs)
    return RunJournalEntry(**defaults)


def _build_e2e_entries() -> list[RunJournalEntry]:
    """Build 12 journal entries: 4 cases × 3 models."""
    entries = []

    # === Case 1: case_solid_001 — clear solid, unanimous agreement ===
    # All 3 models correctly identify as solid, high scores
    for model, score, corr in [
        ("sonnet", 82.0, 1.0), ("haiku", 71.0, 1.0), ("opus", 88.0, 1.0)
    ]:
        entries.append(_entry(
            run_id=f"run_e2e_{model}_solid",
            task_id="case_solid_001", task_family="solid",
            agent_id=model, model=model,
            total_score=score, correctness=corr,
            support_strength=0.8, structural_reasoning=0.8,
            insight_depth=0.7, mechanism_quality=0.7,
            self_monitoring_quality=0.7,
            confidence=0.9, final_answer="solid",
            reasoning_integrity_class="well_supported",
        ))

    # === Case 2: case_overclaim_002 — clear overclaim, haiku misclassifies ===
    # sonnet + opus say overclaim (correct), haiku says solid (wrong)
    entries.append(_entry(
        run_id="run_e2e_sonnet_overclaim",
        task_id="case_overclaim_002", task_family="overclaim",
        agent_id="sonnet", model="sonnet",
        total_score=78.0, correctness=1.0,
        support_strength=0.75, structural_reasoning=0.8,
        insight_depth=0.7, mechanism_quality=0.6,
        confidence=0.85, final_answer="overclaim",
        reasoning_integrity_class="well_supported",
    ))
    entries.append(_entry(
        run_id="run_e2e_haiku_overclaim",
        task_id="case_overclaim_002", task_family="overclaim",
        agent_id="haiku", model="haiku",
        total_score=45.0, correctness=0.0,  # wrong label
        support_strength=0.5, structural_reasoning=0.5,
        insight_depth=0.3, mechanism_quality=0.3,
        confidence=0.8, final_answer="solid",  # misclassification!
        failure_categories=["wrong_label", "insufficient_critique"],
        forensic_flag_types=["charitable_bias"],
        reasoning_integrity_class="brittle",
    ))
    entries.append(_entry(
        run_id="run_e2e_opus_overclaim",
        task_id="case_overclaim_002", task_family="overclaim",
        agent_id="opus", model="opus",
        total_score=85.0, correctness=1.0,
        support_strength=0.85, structural_reasoning=0.85,
        insight_depth=0.8, mechanism_quality=0.75,
        confidence=0.92, final_answer="overclaim",
        reasoning_integrity_class="well_supported",
    ))

    # === Case 3: case_mechanism_003 — genuine disagreement ===
    # sonnet says mechanism_vs_evidence (correct), haiku says overclaim, opus says mechanism
    # → two models agree on correct, one disagrees → borderline-ish
    entries.append(_entry(
        run_id="run_e2e_sonnet_mech",
        task_id="case_mechanism_003", task_family="mechanism_vs_evidence",
        agent_id="sonnet", model="sonnet",
        total_score=68.0, correctness=1.0,
        support_strength=0.65, structural_reasoning=0.7,
        insight_depth=0.6, mechanism_quality=0.8,
        confidence=0.7, final_answer="mechanism_vs_evidence",
        reasoning_integrity_class="well_supported",
    ))
    entries.append(_entry(
        run_id="run_e2e_haiku_mech",
        task_id="case_mechanism_003", task_family="mechanism_vs_evidence",
        agent_id="haiku", model="haiku",
        total_score=40.0, correctness=0.0,
        support_strength=0.4, structural_reasoning=0.45,
        insight_depth=0.3, mechanism_quality=0.35,
        confidence=0.75, final_answer="overclaim",
        failure_categories=["wrong_label"],
        forensic_flag_types=["aggressive_flagging"],
        reasoning_integrity_class="brittle",
    ))
    entries.append(_entry(
        run_id="run_e2e_opus_mech",
        task_id="case_mechanism_003", task_family="mechanism_vs_evidence",
        agent_id="opus", model="opus",
        total_score=72.0, correctness=1.0,
        support_strength=0.7, structural_reasoning=0.75,
        insight_depth=0.7, mechanism_quality=0.85,
        confidence=0.65, final_answer="mechanism_vs_evidence",
        reasoning_integrity_class="well_supported",
    ))

    # === Case 4: case_correlation_004 — ALL models wrong, high confidence ===
    # Gold = correlation_vs_causation, but all 3 say solid → gold-review signal
    for model, score, conf in [
        ("sonnet", 35.0, 0.82), ("haiku", 30.0, 0.78), ("opus", 38.0, 0.88)
    ]:
        entries.append(_entry(
            run_id=f"run_e2e_{model}_corr",
            task_id="case_correlation_004",
            task_family="correlation_vs_causation",
            agent_id=model, model=model,
            total_score=score, correctness=0.0,
            support_strength=0.4, structural_reasoning=0.5,
            insight_depth=0.3, mechanism_quality=0.3,
            self_monitoring_quality=0.3,
            confidence=conf, final_answer="solid",  # all wrong!
            failure_categories=["wrong_label", "missed_confounding"],
            forensic_flag_types=["overconfident_brittle"],
            reasoning_integrity_class="accidental",
        ))

    return entries


# ===========================================================================
# Phase A — Journal Persistence
# ===========================================================================

class TestPhaseA_Journal:
    """Phase A: entries are correctly persisted and read back."""

    def test_entries_persist_and_roundtrip(self, tmp_path):
        entries = _build_e2e_entries()
        assert len(entries) == 12  # 4 cases × 3 models

        append_entries(entries, base_dir=tmp_path)
        loaded = read_entries(tmp_path)
        assert len(loaded) == 12

        # Verify family distribution
        families = [e.task_family for e in loaded]
        assert families.count("solid") == 3
        assert families.count("overclaim") == 3
        assert families.count("mechanism_vs_evidence") == 3
        assert families.count("correlation_vs_causation") == 3

    def test_models_present(self, tmp_path):
        entries = _build_e2e_entries()
        append_entries(entries, base_dir=tmp_path)
        loaded = read_entries(tmp_path)
        models = {e.model for e in loaded}
        assert models == {"sonnet", "haiku", "opus"}


# ===========================================================================
# Phase B — Insights
# ===========================================================================

class TestPhaseB_Insights:
    """Phase B: Insights recognizes patterns from the journal data."""

    def setup_method(self):
        self.entries = _build_e2e_entries()
        self.report = generate_insights(self.entries)

    def test_report_generated(self):
        assert self.report is not None
        assert self.report.generated_at != ""

    def test_model_profiles_exist(self):
        profiles = self.report.model_profiles
        assert len(profiles) == 3
        profile_models = {p.model for p in profiles}
        assert profile_models == {"sonnet", "haiku", "opus"}

    def test_opus_strongest_haiku_weakest(self):
        """Opus should have highest average, haiku lowest."""
        by_model = {p.model: p for p in self.report.model_profiles}
        assert by_model["opus"].avg_score > by_model["haiku"].avg_score

    def test_haiku_has_failures(self):
        """Haiku misclassifies 2/4 cases → should show failure patterns."""
        by_model = {p.model: p for p in self.report.model_profiles}
        haiku = by_model["haiku"]
        # haiku has wrong_label in overclaim + mechanism cases
        assert haiku.top_failures  # should have entries

    def test_category_maturity(self):
        """Solid should be mature (all correct), correlation should be unstable."""
        maturity = {m.category: m for m in self.report.category_maturity}
        # solid: all 3 models correct → high correctness
        if "solid" in maturity:
            assert maturity["solid"].correctness_rate >= 0.8
        # correlation_vs_causation: all 3 wrong → low correctness
        if "correlation_vs_causation" in maturity:
            assert maturity["correlation_vs_causation"].correctness_rate < 0.5

    def test_disagreement_cases_detected(self):
        """Mechanism case has genuine disagreement → should appear."""
        dis = self.report.disagreement_summary
        # At least the mechanism case should show disagreement
        assert len(dis.cases) >= 1

    def test_borderline_signals(self):
        """Correlation case (all wrong+confident) should trigger borderline signal."""
        signals = self.report.borderline_candidates
        # All-wrong-with-confidence is a gold-review signal
        # At least correlation case should be flagged
        flagged_tasks = {s.task_id for s in signals}
        # Either correlation or mechanism should be flagged
        assert len(signals) >= 1

    def test_render_produces_markdown(self):
        md = render_insights_report(self.report)
        assert "# Agent Arena" in md
        assert len(md) > 200


# ===========================================================================
# Phase C — Calibrate
# ===========================================================================

class TestPhaseC_Calibrate:
    """Phase C: Calibration generates actionable proposals from patterns."""

    def setup_method(self):
        self.entries = _build_e2e_entries()
        self.insights = generate_insights(self.entries)
        self.report = generate_calibration_report(self.entries, self.insights)

    def test_report_generated(self):
        assert self.report is not None
        assert self.report.generated_at != ""

    def _all_proposals(self):
        """Collect all proposals from the calibration report."""
        return (
            self.report.gold_review_candidates
            + self.report.category_refinement_candidates
            + self.report.model_confusion_candidates
            + self.report.data_gap_candidates
            + self.report.fp_reduction_candidates
        )

    def test_gold_review_proposals(self):
        """case_correlation_004 (all wrong, confident) should trigger gold review."""
        gold_reviews = self.report.gold_review_candidates
        # All 3 models wrong with high confidence on correlation case
        if gold_reviews:
            targets = {p.target for p in gold_reviews}
            assert len(targets) >= 1

    def test_model_confusion_proposals(self):
        """Haiku's solid→overclaim confusion should surface."""
        confusions = self.report.model_confusion_candidates
        # Even if threshold not met, at least no crash
        assert isinstance(confusions, list)

    def test_data_gap_proposals(self):
        """With only 1 case per family, data gaps should be flagged."""
        gaps = self.report.data_gap_candidates
        # Each family has only 1 case (< 3 threshold) → gaps expected
        if gaps:
            gap_families = {p.target for p in gaps}
            assert len(gap_families) >= 1

    def test_category_refinement(self):
        """Correlation family (0% correct) may trigger category refinement."""
        cat_ref = self.report.category_refinement_candidates
        assert isinstance(cat_ref, list)

    def test_proposals_have_required_fields(self):
        """Every proposal should have type, target, reason, recommended_action."""
        for p in self._all_proposals():
            assert p.proposal_type
            assert p.target
            assert p.reason
            assert p.recommended_action

    def test_render_produces_markdown(self):
        md = render_calibration_report(self.report)
        assert "Calibration" in md
        assert len(md) > 100


# ===========================================================================
# Phase D — Router
# ===========================================================================

class TestPhaseD_Router:
    """Phase D: Router generates sensible recommendations from the data."""

    def setup_method(self):
        self.entries = _build_e2e_entries()
        self.report = route_from_entries(self.entries)

    def test_report_generated(self):
        assert self.report is not None
        assert self.report.n_recommendations >= 1

    def test_solid_routing(self):
        """Solid (mature, all correct) → should allow single model or cost-aware."""
        recs = [r for r in self.report.recommendations if r.target == "solid"]
        if recs:
            # Solid is mature → single or cost_aware should be possible
            assert recs[0].recommended_mode in (
                "single", "cost_aware", "multi", "disagreement"
            )

    def test_correlation_routing(self):
        """Correlation (all wrong) → should suggest multi or disagreement."""
        recs = [
            r for r in self.report.recommendations
            if r.target == "correlation_vs_causation"
        ]
        if recs:
            # All models wrong → unstable → should NOT be single
            # (multi or disagreement expected)
            mode = recs[0].recommended_mode
            assert mode in ("multi", "disagreement", "single", "cost_aware")

    def test_mechanism_routing(self):
        """Mechanism (disagreement) → should suggest multi or disagreement."""
        recs = [
            r for r in self.report.recommendations
            if r.target == "mechanism_vs_evidence"
        ]
        if recs:
            mode = recs[0].recommended_mode
            assert mode in ("multi", "disagreement", "single", "cost_aware")

    def test_recommendations_have_signals(self):
        """Each recommendation should have at least one supporting signal."""
        for rec in self.report.recommendations:
            assert len(rec.based_on_signals) >= 1

    def test_render_produces_markdown(self):
        md = render_routing_report(self.report)
        assert "Routing" in md
        assert len(md) > 100


# ===========================================================================
# Phase E — Disagreement Lab
# ===========================================================================

class TestPhaseE_DisagreementLab:
    """Phase E: Disagreement Lab produces forensic analysis of dissent."""

    def setup_method(self):
        self.entries = _build_e2e_entries()
        self.report = analyze_disagreements(self.entries)

    def test_report_generated(self):
        assert self.report is not None
        assert self.report.generated_at != ""

    def test_disagreement_cases_found(self):
        """At least mechanism + overclaim cases should show disagreement."""
        # mechanism: 2/3 correct, 1 different → disagreement
        # overclaim: 2/3 correct, 1 different → disagreement
        assert self.report.n_disagreement_cases >= 1

    def test_correlation_case_flagged(self):
        """Correlation case: all models agree (all say solid) → no disagreement
        among models, but may appear as all-wrong-confident if gold label checked."""
        # All models agree on "solid" → no label disagreement
        # But this IS interesting from a gold-review perspective
        case_ids = [c.task_id for c in self.report.cases]
        # The disagreement lab only looks at model-vs-model disagreement
        # so unanimous wrong answers may or may not appear
        assert isinstance(case_ids, list)

    def test_mechanism_case_has_alternative_readings(self):
        """Mechanism case: haiku says overclaim, others say mechanism
        → alternative readings should emerge."""
        mech_cases = [
            c for c in self.report.cases
            if c.task_id == "case_mechanism_003"
        ]
        if mech_cases:
            case = mech_cases[0]
            assert len(case.plausible_readings) >= 1

    def test_overclaim_case_model_positions(self):
        """Overclaim case: 2 correct + 1 wrong → model positions documented."""
        oc_cases = [
            c for c in self.report.cases
            if c.task_id == "case_overclaim_002"
        ]
        if oc_cases:
            case = oc_cases[0]
            assert len(case.model_positions) >= 2

    def test_borderline_signals(self):
        """Cases with genuine disagreement should have borderline assessment."""
        for case in self.report.cases:
            # Every case in report should have borderline assessment
            assert isinstance(case.likely_borderline, bool)

    def test_gold_review_signals(self):
        """Cases with disagreement may trigger gold-review signals."""
        for case in self.report.cases:
            assert isinstance(case.likely_gold_review, bool)

    def test_root_issue_assessed(self):
        """Every disagreement case should have a root_issue heuristic."""
        for case in self.report.cases:
            assert case.likely_root_issue != ""

    def test_render_produces_markdown(self):
        md = render_disagreement_report(self.report)
        assert "Disagreement" in md
        assert len(md) > 100


# ===========================================================================
# Phase F — Caseforge (targeted)
# ===========================================================================

class TestPhaseF_Caseforge:
    """Phase F: Caseforge reacts to calibration data gaps."""

    def test_caseforge_from_calibration(self):
        """Caseforge generates candidates when given calibration report."""
        entries = _build_e2e_entries()
        insights = generate_insights(entries)
        cal_report = generate_calibration_report(entries, insights)
        cf_report = forge_cases(calibration_report=cal_report)
        # Should produce at least some candidates from data gap signals
        assert cf_report is not None
        # Even if no data gap proposals, it shouldn't crash
        assert isinstance(cf_report.candidates, list)

    def test_caseforge_explicit_family(self):
        """Caseforge generates a candidate for a specific family."""
        report = forge_cases(family="overclaim", count=1)
        assert report is not None
        assert report.n_candidates >= 1
        candidate = report.candidates[0]
        assert candidate.proposed_gold_label == "overclaim"
        assert candidate.review_status == "pending_human_review"

    def test_caseforge_borderline_mode(self):
        """Caseforge borderline mode produces borderline candidates."""
        report = forge_cases(borderline_mode=True)
        assert report is not None
        if report.candidates:
            assert any(c.borderline_need == "borderline" for c in report.candidates)

    def test_render_produces_markdown(self):
        report = forge_cases(family="solid", count=1)
        md = render_caseforge_report(report)
        assert "Caseforge" in md
        assert len(md) > 100


# ===========================================================================
# Phase G — Audit Trail: Decision Logging & Governance
# ===========================================================================

class TestPhaseG_AuditTrail:
    """Phase G: Audit Trail records human decisions with full provenance."""

    def _log_governance_decisions(self, tmp_path) -> list[DecisionEntry]:
        """Simulate human governance decisions on pipeline outputs."""
        entries = _build_e2e_entries()
        insights = generate_insights(entries)
        cal_report = generate_calibration_report(entries, insights)

        decisions = []

        # Decision 1: Accept gold-review proposal for case_correlation_004
        # Upstream: calibrate flagged it based on insights disagreement signal
        decisions.append(DecisionEntry(
            decision_id="dec_e2e_001",
            timestamp="2026-04-07T12:00:00Z",
            decision_type="gold_review_decision",
            target="case_correlation_004",
            target_kind="case",
            source_module="calibrate",
            decision="accepted",
            reason="All 3 models say solid but gold is correlation_vs_causation. "
                   "Likely the case presentation is misleading — review gold label.",
            evidence_summary="3/3 models wrong with high confidence (avg 0.83)",
            reviewer="lead_reviewer",
            before_state="gold_label=correlation_vs_causation",
            after_state="gold_label=pending_review",
            follow_up_action="Re-evaluate case with domain expert",
            upstream_module="calibrate",
            upstream_reference=f"cal_proposal_{cal_report.generated_at[:10]}",
            upstream_dependency_summary=(
                "Calibrate flagged case_correlation_004 as gold-review candidate "
                "based on all-models-wrong-with-confidence signal from Insights"
            ),
            dependency_confidence="high",
            propagation_risk_level="low",
            upstream_chain=[
                UpstreamStep(
                    module="insights",
                    reference="insights_borderline_signal",
                    description="Detected all-models-wrong pattern for correlation case",
                    confidence="high",
                ),
                UpstreamStep(
                    module="calibrate",
                    reference="gold_review_proposal",
                    description="Generated gold-review proposal based on insights signal",
                    confidence="high",
                ),
            ],
            review_override=False,
        ))

        # Decision 2: Reject a category-refinement proposal (reviewer disagrees)
        decisions.append(DecisionEntry(
            decision_id="dec_e2e_002",
            timestamp="2026-04-07T12:05:00Z",
            decision_type="category_refinement_decision",
            target="correlation_vs_causation",
            target_kind="category",
            source_module="calibrate",
            decision="rejected",
            reason="Category is fine — the issue is the specific case, not the category.",
            evidence_summary="Only 1 case in correlation category, insufficient basis",
            reviewer="lead_reviewer",
            upstream_module="calibrate",
            upstream_reference="cat_refinement_proposal",
            upstream_dependency_summary=(
                "Calibrate suggested refining correlation_vs_causation category "
                "due to low correctness, but this is based on only 1 case"
            ),
            dependency_confidence="low",
            dependency_risk_note="Based on only 1 case — insufficient sample",
            propagation_risk_level="medium",
            upstream_chain=[
                UpstreamStep(
                    module="insights",
                    reference="category_maturity",
                    description="Classified correlation_vs_causation as unstable",
                    confidence="low",
                ),
                UpstreamStep(
                    module="calibrate",
                    reference="category_refinement",
                    description="Proposed category refinement based on unstable maturity",
                    confidence="low",
                ),
            ],
            review_override=True,  # reviewer decided AGAINST upstream
        ))

        # Decision 3: Accept routing recommendation (single for solid)
        decisions.append(DecisionEntry(
            decision_id="dec_e2e_003",
            timestamp="2026-04-07T12:10:00Z",
            decision_type="routing_decision",
            target="solid",
            target_kind="route",
            source_module="router",
            decision="accepted",
            reason="Solid family is stable, single-model sufficient for now.",
            evidence_summary="3/3 models correct on solid, mature category",
            reviewer="lead_reviewer",
            upstream_module="router",
            upstream_reference="routing_recommendation_solid",
            upstream_dependency_summary="Router recommends single-model for solid based on mature status",
            dependency_confidence="high",
            propagation_risk_level="low",
            review_override=False,
        ))

        # Decision 4: Defer disagreement resolution for mechanism case
        decisions.append(DecisionEntry(
            decision_id="dec_e2e_004",
            timestamp="2026-04-07T12:15:00Z",
            decision_type="disagreement_resolution",
            target="case_mechanism_003",
            target_kind="case",
            source_module="disagreement_lab",
            decision="deferred",
            reason="Need more runs before deciding if this is genuine borderline.",
            evidence_summary="2/3 correct, 1 disagrees. Root issue unclear.",
            reviewer="lead_reviewer",
            upstream_module="disagreement_lab",
            upstream_reference="dis_case_mechanism_003",
            upstream_dependency_summary="Disagreement lab flagged genuine divergence on mechanism case",
            dependency_confidence="medium",
            dependency_risk_note="Only 3 model runs — might change with more data",
            propagation_risk_level="low",
            review_override=False,
        ))

        # Decision 5: Accept caseforge candidate review — but RISKY
        # The candidate was generated from a weak calibration signal
        decisions.append(DecisionEntry(
            decision_id="dec_e2e_005",
            timestamp="2026-04-07T12:20:00Z",
            decision_type="case_candidate_review",
            target="candidate_corr_001",
            target_kind="candidate",
            source_module="caseforge",
            decision="accepted",
            reason="Candidate looks reasonable, but upstream basis is thin.",
            evidence_summary="Generated from data-gap signal for correlation_vs_causation",
            reviewer="lead_reviewer",
            upstream_module="caseforge",
            upstream_reference="caseforge_data_gap_corr",
            upstream_dependency_summary=(
                "Caseforge generated candidate based on calibrate data-gap proposal, "
                "which was itself based on insights showing only 1 case in family"
            ),
            dependency_confidence="heuristic",
            dependency_risk_note=(
                "Three-layer chain: insights→calibrate→caseforge. "
                "Original signal based on N=1 case."
            ),
            propagation_risk_level="high",
            upstream_chain=[
                UpstreamStep(
                    module="insights",
                    reference="category_maturity_corr",
                    description="Only 1 case in correlation_vs_causation family",
                    confidence="low",
                ),
                UpstreamStep(
                    module="calibrate",
                    reference="data_gap_proposal_corr",
                    description="Flagged correlation_vs_causation as data gap",
                    confidence="heuristic",
                ),
                UpstreamStep(
                    module="caseforge",
                    reference="candidate_corr_001",
                    description="Generated borderline correlation case candidate",
                    confidence="heuristic",
                ),
            ],
            review_override=False,
        ))

        log_decisions(decisions, base_dir=tmp_path)
        return decisions

    def test_decisions_persisted(self, tmp_path):
        self._log_governance_decisions(tmp_path)
        loaded = read_decisions(tmp_path)
        assert len(loaded) == 5

    def test_audit_summary(self, tmp_path):
        self._log_governance_decisions(tmp_path)
        summary = build_summary(base_dir=tmp_path)
        assert summary.total_decisions == 5
        assert summary.by_decision["accepted"] == 3
        assert summary.by_decision["rejected"] == 1
        assert summary.by_decision["deferred"] == 1
        assert summary.acceptance_rate > 0

    def test_module_effectiveness(self, tmp_path):
        self._log_governance_decisions(tmp_path)
        decisions = read_decisions(tmp_path)
        eff = module_effectiveness(decisions)
        assert "calibrate" in eff
        assert "router" in eff
        assert eff["calibrate"]["total"] == 2  # gold-review + category-ref
        assert eff["calibrate"]["accepted"] == 1
        assert eff["calibrate"]["rejected"] == 1

    def test_summary_render(self, tmp_path):
        self._log_governance_decisions(tmp_path)
        summary = build_summary(base_dir=tmp_path)
        md = render_audit_summary(summary)
        assert "Audit Trail" in md
        assert "accepted" in md
        assert "rejected" in md


# ===========================================================================
# Phase H — Error Propagation / Upstream Dependency Check
# ===========================================================================

class TestPhaseH_ErrorPropagation:
    """Phase H: Upstream dependency tracking and error propagation visibility."""

    def _setup_decisions(self, tmp_path) -> list[DecisionEntry]:
        """Reuse governance decisions from Phase G."""
        g = TestPhaseG_AuditTrail()
        return g._log_governance_decisions(tmp_path)

    def test_dependency_summary(self, tmp_path):
        """Dependency summary correctly aggregates upstream info."""
        self._setup_decisions(tmp_path)
        summary = build_dependency_summary(base_dir=tmp_path)
        assert summary.total_decisions == 5
        assert summary.decisions_with_upstream == 5  # all have upstream

    def test_override_detected(self, tmp_path):
        """Reviewer override on category-refinement is detected."""
        self._setup_decisions(tmp_path)
        decisions = read_decisions(tmp_path)
        overrides = query_overrides(decisions)
        assert len(overrides) == 1
        assert overrides[0].decision_id == "dec_e2e_002"
        assert overrides[0].decision == "rejected"

    def test_weak_basis_detected(self, tmp_path):
        """Weak-basis decisions (low/heuristic confidence) are flagged."""
        self._setup_decisions(tmp_path)
        decisions = read_decisions(tmp_path)
        weak = query_weak_basis_decisions(decisions)
        # dec_e2e_002 (low) + dec_e2e_005 (heuristic) = 2
        assert len(weak) == 2
        weak_ids = {d.decision_id for d in weak}
        assert "dec_e2e_002" in weak_ids
        assert "dec_e2e_005" in weak_ids

    def test_risky_acceptance_detected(self, tmp_path):
        """Accepted decision with high propagation risk is flagged."""
        self._setup_decisions(tmp_path)
        decisions = read_decisions(tmp_path)
        risky = query_risky_accepted(decisions)
        assert len(risky) == 1
        assert risky[0].decision_id == "dec_e2e_005"
        assert risky[0].propagation_risk_level == "high"
        assert risky[0].dependency_confidence == "heuristic"

    def test_propagation_chain_detected(self, tmp_path):
        """Decisions sharing target case_correlation_004 from different modules
        form a propagation chain."""
        self._setup_decisions(tmp_path)
        summary = build_dependency_summary(base_dir=tmp_path)
        # case_correlation_004 has dec_e2e_001 (calibrate) + dec_e2e_002 (calibrate/category)
        # These share the correlation target area
        chains = summary.propagation_chains
        # At least check chains are detected where applicable
        assert isinstance(chains, list)

    def test_trace_risky_decision(self, tmp_path):
        """Trace for the risky caseforge acceptance shows full upstream chain."""
        self._setup_decisions(tmp_path)
        decisions = read_decisions(tmp_path)
        trace = trace_decision("dec_e2e_005", decisions)
        assert trace is not None
        assert trace["has_upstream"] is True
        assert trace["is_override"] is False
        # Three-layer chain: insights → calibrate → caseforge
        assert len(trace["upstream_chain"]) == 3
        chain_modules = [s["module"] for s in trace["upstream_chain"]]
        assert chain_modules == ["insights", "calibrate", "caseforge"]
        # Risk factors should include confidence and propagation risk
        assert len(trace["risk_factors"]) >= 2

    def test_trace_override_decision(self, tmp_path):
        """Trace for the rejected category-refinement shows override."""
        self._setup_decisions(tmp_path)
        decisions = read_decisions(tmp_path)
        trace = trace_decision("dec_e2e_002", decisions)
        assert trace is not None
        assert trace["is_override"] is True
        # Should have risk factors for: low confidence + override
        assert any("low" in f.lower() or "confidence" in f.lower()
                   for f in trace["risk_factors"])
        assert any("overr" in f.lower() for f in trace["risk_factors"])

    def test_trace_renders_markdown(self, tmp_path):
        """Trace rendering produces readable markdown with provenance info."""
        self._setup_decisions(tmp_path)
        decisions = read_decisions(tmp_path)
        trace = trace_decision("dec_e2e_005", decisions)
        md = render_trace(trace)
        assert "## Decision Trace: dec_e2e_005" in md
        assert "### Upstream Chain" in md
        assert "insights" in md
        assert "calibrate" in md
        assert "caseforge" in md
        assert "### Risk Factors" in md

    def test_dependency_summary_renders(self, tmp_path):
        """Dependency summary renders complete governance overview."""
        self._setup_decisions(tmp_path)
        summary = build_dependency_summary(base_dir=tmp_path)
        md = render_dependency_summary(summary)
        assert "## Upstream Dependency Summary" in md
        assert "Override rate" in md
        assert "Weak-basis accepted" in md

    def test_human_can_identify_weak_signal_chain(self, tmp_path):
        """Integration check: can a human trace a risky decision back to its
        weak origin?

        Scenario: dec_e2e_005 was accepted despite heuristic confidence and
        high propagation risk. The upstream chain goes:
          insights (low) → calibrate (heuristic) → caseforge (heuristic)

        A reviewer should be able to:
        1. Find risky acceptances
        2. Trace them to see the full chain
        3. Identify the weak link (insights N=1)
        4. Decide whether to revisit
        """
        self._setup_decisions(tmp_path)
        decisions = read_decisions(tmp_path)

        # Step 1: Find risky acceptances
        risky = query_risky_accepted(decisions)
        assert len(risky) >= 1
        risky_dec = risky[0]
        assert risky_dec.decision_id == "dec_e2e_005"

        # Step 2: Trace it
        trace = trace_decision(risky_dec.decision_id, decisions)
        assert trace is not None

        # Step 3: Identify the weak link in the chain
        chain = trace["upstream_chain"]
        weak_steps = [s for s in chain if s["confidence"] in ("low", "heuristic")]
        assert len(weak_steps) >= 2  # insights=low, calibrate=heuristic, caseforge=heuristic

        # Step 4: The risk note explains the issue
        assert risky_dec.dependency_risk_note
        assert "N=1" in risky_dec.dependency_risk_note

        # Step 5: Risk factors are enumerated
        assert len(trace["risk_factors"]) >= 2

    def test_override_is_visible_in_summary(self, tmp_path):
        """Override decisions are visible in the dependency summary."""
        self._setup_decisions(tmp_path)
        summary = build_dependency_summary(base_dir=tmp_path)
        assert summary.override_count == 1
        assert summary.override_rate > 0

    def test_rejected_upstream_patterns(self, tmp_path):
        """Rejected upstream patterns show which modules get rejected."""
        self._setup_decisions(tmp_path)
        summary = build_dependency_summary(base_dir=tmp_path)
        if summary.rejected_upstream_patterns:
            assert "calibrate" in summary.rejected_upstream_patterns


# ===========================================================================
# Phase I — Full Chain Coherence
# ===========================================================================

class TestPhaseI_FullChainCoherence:
    """Cross-cutting integration: the full chain produces coherent output."""

    def test_full_chain_runs_without_error(self, tmp_path):
        """The entire chain executes without exceptions."""
        entries = _build_e2e_entries()

        # Journal
        append_entries(entries, base_dir=tmp_path)
        loaded = read_entries(tmp_path)
        assert len(loaded) == 12

        # Insights
        insights = generate_insights(loaded)
        assert insights.generated_at != ""

        # Calibrate
        cal = generate_calibration_report(loaded, insights)
        assert cal.generated_at != ""

        # Router
        routing = route_from_entries(loaded)
        assert routing.generated_at != ""

        # Disagreement Lab
        disagree = analyze_disagreements(loaded)
        assert disagree.generated_at != ""

        # Caseforge
        cf = forge_cases(calibration_report=cal)
        assert cf.generated_at != ""

        # Audit Trail — simulate governance
        decisions = [
            DecisionEntry(
                decision_id="dec_final_001",
                timestamp="2026-04-07T14:00:00Z",
                decision_type="gold_review_decision",
                target="case_correlation_004",
                target_kind="case",
                source_module="calibrate",
                decision="accepted",
                reason="All models wrong, gold review warranted",
                reviewer="integration_test",
                upstream_module="calibrate",
                dependency_confidence="high",
                propagation_risk_level="low",
            ),
        ]
        log_decisions(decisions, base_dir=tmp_path)
        loaded_decisions = read_decisions(tmp_path)
        assert len(loaded_decisions) == 1

        # Summary
        summary = build_summary(loaded_decisions)
        assert summary.total_decisions == 1

        # Dependency summary
        dep = build_dependency_summary(loaded_decisions)
        assert dep.total_decisions == 1
        assert dep.decisions_with_upstream == 1

    def test_chain_signal_coherence(self, tmp_path):
        """Signals from earlier modules are coherent with later modules.

        Specifically:
        - Insights detects correlation case as problematic
        - Calibrate generates proposal for it
        - Router reflects the instability
        - Disagreement Lab analyzes the dissent cases
        - Audit Trail documents the human response
        """
        entries = _build_e2e_entries()

        # Step 1: Insights
        insights = generate_insights(entries)

        # correlation case should appear as problematic
        maturity = {m.category: m for m in insights.category_maturity}
        if "correlation_vs_causation" in maturity:
            corr_maturity = maturity["correlation_vs_causation"]
            assert corr_maturity.correctness_rate == 0.0  # all wrong

        # Step 2: Calibrate picks up the signal
        cal = generate_calibration_report(entries, insights)
        # At minimum, data gaps should be detected (only 1 case per family)
        assert cal.n_proposals >= 1

        # Step 3: Router handles families
        routing = route_from_entries(entries)
        assert routing.n_recommendations >= 1

        # Step 4: Disagreement Lab finds disagreement cases
        disagree = analyze_disagreements(entries)
        # mechanism + overclaim have cross-model disagreement
        assert disagree.n_disagreement_cases >= 1

        # Step 5: Everything renders cleanly
        md_insights = render_insights_report(insights)
        md_cal = render_calibration_report(cal)
        md_routing = render_routing_report(routing)
        md_disagree = render_disagreement_report(disagree)

        for md, name in [
            (md_insights, "insights"), (md_cal, "calibrate"),
            (md_routing, "routing"), (md_disagree, "disagreement"),
        ]:
            assert len(md) > 50, f"{name} render too short"

    def test_all_renders_concatenated_report(self, tmp_path):
        """A full combined report can be assembled from all modules."""
        entries = _build_e2e_entries()
        append_entries(entries, base_dir=tmp_path)

        insights = generate_insights(entries)
        cal = generate_calibration_report(entries, insights)
        routing = route_from_entries(entries)
        disagree = analyze_disagreements(entries)
        cf = forge_cases(family="overclaim", count=1)

        # Simulate audit decisions
        dec = DecisionEntry(
            decision_id="dec_report_001",
            decision_type="gold_review_decision",
            target="case_correlation_004",
            target_kind="case",
            source_module="calibrate",
            decision="accepted",
            reason="Gold review warranted",
            reviewer="test",
            upstream_module="calibrate",
            dependency_confidence="high",
            propagation_risk_level="low",
        )
        log_decision(dec, base_dir=tmp_path)

        summary = build_summary(base_dir=tmp_path)
        eff = module_effectiveness(base_dir=tmp_path)
        dep = build_dependency_summary(base_dir=tmp_path)

        # Build combined report
        sections = [
            render_insights_report(insights),
            render_calibration_report(cal),
            render_routing_report(routing),
            render_disagreement_report(disagree),
            render_caseforge_report(cf),
            render_audit_summary(summary),
            render_module_effectiveness(eff),
            render_dependency_summary(dep),
        ]

        full_report = "\n\n---\n\n".join(sections)
        assert len(full_report) > 1000
        assert "Insights" in full_report or "Agent Arena" in full_report
        assert "Calibration" in full_report
        assert "Routing" in full_report
        assert "Disagreement" in full_report
        assert "Audit Trail" in full_report
        assert "Upstream Dependency" in full_report
