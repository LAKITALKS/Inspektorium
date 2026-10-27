"""Tests for Gen 6 Audit Trail of the Inspektorium audit runtime.

Tests cover:
- Decision entry persistence (write / read)
- All decision types
- All decision outcomes (accepted / rejected / deferred / partially_accepted)
- Query helpers (by type, target, source, decision, reviewer)
- Summary generation
- Module effectiveness analysis
- Label change history
- Deferred decisions tracking
- Report rendering
- Edge cases (empty, single entry)
"""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from inspektorium.audit.schemas import (
    AuditSummary,
    DecisionEntry,
    DependencySummary,
    UpstreamStep,
)
from inspektorium.audit.integrity.audit_trail import (
    log_decision,
    log_decisions,
    read_decisions,
    query_by_type,
    query_by_target,
    query_by_source,
    query_by_decision,
    query_by_reviewer,
    query_recent,
    build_summary,
    module_effectiveness,
    label_change_history,
    deferred_decisions,
    generate_decision_id,
    render_audit_summary,
    render_module_effectiveness,
    build_dependency_summary,
    trace_decision,
    query_weak_basis_decisions,
    query_overrides,
    query_risky_accepted,
    render_dependency_summary,
    render_trace,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _decision(**kwargs) -> DecisionEntry:
    """Create a DecisionEntry with defaults."""
    defaults = dict(
        decision_id="dec_test_001",
        timestamp="2026-04-06T00:00:00Z",
        decision_type="gold_review_decision",
        target="case031",
        target_kind="case",
        source_module="calibrate",
        decision="accepted",
        reason="Gold label appears incorrect based on cross-model disagreement",
        evidence_summary="3/3 models say solid, gold says overclaim",
        reviewer="alice",
        notes="Clear case",
        related_cases=["case031"],
        related_models=["sonnet", "haiku"],
    )
    defaults.update(kwargs)
    return DecisionEntry(**defaults)


# ---------------------------------------------------------------------------
# 1. Persistence — Write and Read
# ---------------------------------------------------------------------------

class TestPersistence:
    def test_write_and_read_single(self, tmp_path):
        entry = _decision()
        log_decision(entry, base_dir=tmp_path)
        decisions = read_decisions(tmp_path)
        assert len(decisions) == 1
        assert decisions[0].decision_id == "dec_test_001"
        assert decisions[0].target == "case031"

    def test_write_and_read_multiple(self, tmp_path):
        entries = [
            _decision(decision_id="dec_001", target="case001"),
            _decision(decision_id="dec_002", target="case002"),
            _decision(decision_id="dec_003", target="case003"),
        ]
        log_decisions(entries, base_dir=tmp_path)
        decisions = read_decisions(tmp_path)
        assert len(decisions) == 3
        assert {d.target for d in decisions} == {"case001", "case002", "case003"}

    def test_append_preserves_existing(self, tmp_path):
        log_decision(_decision(decision_id="dec_001"), base_dir=tmp_path)
        log_decision(_decision(decision_id="dec_002"), base_dir=tmp_path)
        decisions = read_decisions(tmp_path)
        assert len(decisions) == 2

    def test_read_empty_dir(self, tmp_path):
        decisions = read_decisions(tmp_path)
        assert decisions == []

    def test_auto_fills_timestamp(self, tmp_path):
        entry = _decision(timestamp="")
        log_decision(entry, base_dir=tmp_path)
        decisions = read_decisions(tmp_path)
        assert decisions[0].timestamp != ""

    def test_auto_fills_decision_id(self, tmp_path):
        entry = _decision(decision_id="")
        log_decision(entry, base_dir=tmp_path)
        decisions = read_decisions(tmp_path)
        assert decisions[0].decision_id.startswith("dec_")

    def test_jsonl_format(self, tmp_path):
        log_decision(_decision(), base_dir=tmp_path)
        path = tmp_path / "decisions.jsonl"
        content = path.read_text()
        lines = [l for l in content.strip().split("\n") if l.strip()]
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["decision_id"] == "dec_test_001"


# ---------------------------------------------------------------------------
# 2. All Decision Types
# ---------------------------------------------------------------------------

class TestDecisionTypes:
    @pytest.mark.parametrize("dtype", [
        "gold_review_decision",
        "category_refinement_decision",
        "routing_decision",
        "case_candidate_review",
        "calibration_proposal_decision",
        "disagreement_resolution",
        "workflow_note",
    ])
    def test_each_type_persists(self, tmp_path, dtype):
        entry = _decision(decision_type=dtype, decision_id=f"dec_{dtype}")
        log_decision(entry, base_dir=tmp_path)
        decisions = read_decisions(tmp_path)
        assert len(decisions) == 1
        assert decisions[0].decision_type == dtype


# ---------------------------------------------------------------------------
# 3. All Decision Outcomes
# ---------------------------------------------------------------------------

class TestDecisionOutcomes:
    @pytest.mark.parametrize("outcome", [
        "accepted", "rejected", "deferred", "partially_accepted",
    ])
    def test_each_outcome_persists(self, tmp_path, outcome):
        entry = _decision(decision=outcome, decision_id=f"dec_{outcome}")
        log_decision(entry, base_dir=tmp_path)
        decisions = read_decisions(tmp_path)
        assert decisions[0].decision == outcome


# ---------------------------------------------------------------------------
# 4. Query Helpers
# ---------------------------------------------------------------------------

class TestQueries:
    def _populate(self, tmp_path) -> None:
        entries = [
            _decision(decision_id="d1", decision_type="gold_review_decision",
                      target="case001", source_module="calibrate",
                      decision="accepted", reviewer="alice"),
            _decision(decision_id="d2", decision_type="category_refinement_decision",
                      target="overclaim", source_module="calibrate",
                      decision="rejected", reviewer="bob"),
            _decision(decision_id="d3", decision_type="case_candidate_review",
                      target="candidate_001", source_module="caseforge",
                      decision="accepted", reviewer="alice"),
            _decision(decision_id="d4", decision_type="routing_decision",
                      target="solid", source_module="router",
                      decision="deferred", reviewer="bob"),
            _decision(decision_id="d5", decision_type="disagreement_resolution",
                      target="case031", source_module="disagreement_lab",
                      decision="accepted", reviewer="alice"),
        ]
        log_decisions(entries, base_dir=tmp_path)

    def test_query_by_type(self, tmp_path):
        self._populate(tmp_path)
        results = query_by_type("gold_review_decision", tmp_path)
        assert len(results) == 1
        assert results[0].decision_id == "d1"

    def test_query_by_target(self, tmp_path):
        self._populate(tmp_path)
        results = query_by_target("case031", tmp_path)
        assert len(results) == 1
        assert results[0].decision_type == "disagreement_resolution"

    def test_query_by_source(self, tmp_path):
        self._populate(tmp_path)
        results = query_by_source("calibrate", tmp_path)
        assert len(results) == 2

    def test_query_by_decision(self, tmp_path):
        self._populate(tmp_path)
        results = query_by_decision("accepted", tmp_path)
        assert len(results) == 3

    def test_query_by_reviewer(self, tmp_path):
        self._populate(tmp_path)
        results = query_by_reviewer("alice", tmp_path)
        assert len(results) == 3
        results_bob = query_by_reviewer("bob", tmp_path)
        assert len(results_bob) == 2

    def test_query_recent(self, tmp_path):
        self._populate(tmp_path)
        results = query_recent(2, tmp_path)
        assert len(results) == 2
        assert results[-1].decision_id == "d5"  # last logged

    def test_query_recent_all(self, tmp_path):
        self._populate(tmp_path)
        results = query_recent(100, tmp_path)
        assert len(results) == 5


# ---------------------------------------------------------------------------
# 5. Summary Generation
# ---------------------------------------------------------------------------

class TestSummary:
    def _make_decisions(self) -> list[DecisionEntry]:
        return [
            _decision(decision_id="d1", decision_type="gold_review_decision",
                      decision="accepted", source_module="calibrate", target="case001"),
            _decision(decision_id="d2", decision_type="gold_review_decision",
                      decision="rejected", source_module="calibrate", target="case002"),
            _decision(decision_id="d3", decision_type="case_candidate_review",
                      decision="accepted", source_module="caseforge", target="cand001"),
            _decision(decision_id="d4", decision_type="routing_decision",
                      decision="deferred", source_module="router", target="solid"),
            _decision(decision_id="d5", decision_type="calibration_proposal_decision",
                      decision="partially_accepted", source_module="calibrate",
                      target="overclaim"),
        ]

    def test_summary_totals(self):
        summary = build_summary(self._make_decisions())
        assert summary.total_decisions == 5
        assert summary.by_type["gold_review_decision"] == 2
        assert summary.by_type["case_candidate_review"] == 1

    def test_summary_outcomes(self):
        summary = build_summary(self._make_decisions())
        assert summary.by_decision["accepted"] == 2
        assert summary.by_decision["rejected"] == 1
        assert summary.by_decision["deferred"] == 1
        assert summary.by_decision["partially_accepted"] == 1

    def test_acceptance_rate(self):
        summary = build_summary(self._make_decisions())
        # accepted=2, partially_accepted=1, rejected=1 → 3/4 = 0.75
        assert summary.acceptance_rate == pytest.approx(0.75, abs=0.01)

    def test_deferred_count(self):
        summary = build_summary(self._make_decisions())
        assert summary.deferred_count == 1

    def test_by_source_module(self):
        summary = build_summary(self._make_decisions())
        assert summary.by_source_module["calibrate"] == 3
        assert summary.by_source_module["caseforge"] == 1
        assert summary.by_source_module["router"] == 1

    def test_most_active_targets(self):
        summary = build_summary(self._make_decisions())
        assert len(summary.most_active_targets) >= 1

    def test_recent_decisions_included(self):
        summary = build_summary(self._make_decisions(), recent_n=3)
        assert len(summary.recent_decisions) == 3

    def test_empty_summary(self):
        summary = build_summary([])
        assert summary.total_decisions == 0
        assert summary.acceptance_rate == 0.0

    def test_summary_from_disk(self, tmp_path):
        log_decisions(self._make_decisions(), base_dir=tmp_path)
        summary = build_summary(base_dir=tmp_path)
        assert summary.total_decisions == 5


# ---------------------------------------------------------------------------
# 6. Module Effectiveness
# ---------------------------------------------------------------------------

class TestModuleEffectiveness:
    def test_effectiveness_per_module(self):
        decisions = [
            _decision(decision_id="d1", source_module="calibrate", decision="accepted"),
            _decision(decision_id="d2", source_module="calibrate", decision="accepted"),
            _decision(decision_id="d3", source_module="calibrate", decision="rejected"),
            _decision(decision_id="d4", source_module="caseforge", decision="accepted"),
            _decision(decision_id="d5", source_module="caseforge", decision="deferred"),
        ]
        eff = module_effectiveness(decisions)
        assert eff["calibrate"]["total"] == 3
        assert eff["calibrate"]["accepted"] == 2
        assert eff["calibrate"]["rejected"] == 1
        assert eff["calibrate"]["acceptance_rate"] == pytest.approx(0.667, abs=0.01)
        assert eff["caseforge"]["total"] == 2
        assert eff["caseforge"]["accepted"] == 1
        assert eff["caseforge"]["deferred"] == 1

    def test_empty_effectiveness(self):
        eff = module_effectiveness([])
        assert eff == {}

    def test_partially_accepted_counts_as_accepted(self):
        decisions = [
            _decision(decision_id="d1", source_module="calibrate",
                      decision="partially_accepted"),
        ]
        eff = module_effectiveness(decisions)
        assert eff["calibrate"]["accepted"] == 1
        assert eff["calibrate"]["acceptance_rate"] == 1.0


# ---------------------------------------------------------------------------
# 7. Label Change History
# ---------------------------------------------------------------------------

class TestLabelChangeHistory:
    def test_changes_detected(self):
        decisions = [
            _decision(decision_id="d1",
                      before_state="gold_label=overclaim",
                      after_state="gold_label=correlation_vs_causation"),
            _decision(decision_id="d2",
                      before_state="", after_state=""),  # no change
            _decision(decision_id="d3",
                      before_state="routing_mode=single",
                      after_state="routing_mode=multi"),
        ]
        changes = label_change_history(decisions)
        assert len(changes) == 2
        assert changes[0].decision_id == "d1"
        assert changes[1].decision_id == "d3"

    def test_same_state_not_a_change(self):
        decisions = [
            _decision(before_state="gold_label=solid",
                      after_state="gold_label=solid"),
        ]
        changes = label_change_history(decisions)
        assert len(changes) == 0

    def test_empty_states_not_a_change(self):
        decisions = [_decision(before_state="", after_state="")]
        changes = label_change_history(decisions)
        assert len(changes) == 0


# ---------------------------------------------------------------------------
# 8. Deferred Decisions
# ---------------------------------------------------------------------------

class TestDeferredDecisions:
    def test_deferred_found(self):
        decisions = [
            _decision(decision_id="d1", decision="accepted"),
            _decision(decision_id="d2", decision="deferred"),
            _decision(decision_id="d3", decision="deferred"),
            _decision(decision_id="d4", decision="rejected"),
        ]
        deferred = deferred_decisions(decisions)
        assert len(deferred) == 2
        assert all(d.decision == "deferred" for d in deferred)

    def test_no_deferred(self):
        decisions = [
            _decision(decision="accepted"),
            _decision(decision="rejected"),
        ]
        deferred = deferred_decisions(decisions)
        assert len(deferred) == 0


# ---------------------------------------------------------------------------
# 9. Related Cases / Models
# ---------------------------------------------------------------------------

class TestRelatedFields:
    def test_related_cases_preserved(self, tmp_path):
        entry = _decision(related_cases=["case001", "case002", "case003"])
        log_decision(entry, base_dir=tmp_path)
        decisions = read_decisions(tmp_path)
        assert decisions[0].related_cases == ["case001", "case002", "case003"]

    def test_related_models_preserved(self, tmp_path):
        entry = _decision(related_models=["sonnet", "haiku", "opus"])
        log_decision(entry, base_dir=tmp_path)
        decisions = read_decisions(tmp_path)
        assert decisions[0].related_models == ["sonnet", "haiku", "opus"]


# ---------------------------------------------------------------------------
# 10. Decision ID Generation
# ---------------------------------------------------------------------------

class TestDecisionId:
    def test_unique_ids(self):
        id1 = generate_decision_id()
        id2 = generate_decision_id()
        assert id1 != id2

    def test_id_format(self):
        did = generate_decision_id()
        assert did.startswith("dec_")
        assert len(did) > 10


# ---------------------------------------------------------------------------
# 11. Report Rendering
# ---------------------------------------------------------------------------

class TestRenderReport:
    def test_empty_summary(self):
        summary = AuditSummary(
            generated_at="2026-04-06T00:00:00Z",
        )
        md = render_audit_summary(summary)
        assert "Gen 6 Audit Trail" in md
        assert "No decisions recorded" in md

    def test_full_summary_has_sections(self):
        decisions = [
            _decision(decision_id="d1", decision="accepted",
                      source_module="calibrate"),
            _decision(decision_id="d2", decision="rejected",
                      source_module="caseforge"),
            _decision(decision_id="d3", decision="deferred",
                      source_module="router"),
        ]
        summary = build_summary(decisions)
        md = render_audit_summary(summary)
        assert "## Decision Outcomes" in md
        assert "## Decision Types" in md
        assert "## Source Modules" in md
        assert "## Recent Decisions" in md
        assert "accepted" in md

    def test_footer(self):
        decisions = [_decision()]
        summary = build_summary(decisions)
        md = render_audit_summary(summary)
        assert "decision records only" in md

    def test_module_effectiveness_render(self):
        decisions = [
            _decision(decision_id="d1", source_module="calibrate",
                      decision="accepted"),
            _decision(decision_id="d2", source_module="calibrate",
                      decision="rejected"),
        ]
        eff = module_effectiveness(decisions)
        md = render_module_effectiveness(eff)
        assert "## Module Effectiveness" in md
        assert "calibrate" in md

    def test_empty_effectiveness_render(self):
        md = render_module_effectiveness({})
        assert "No module-level data" in md


# ---------------------------------------------------------------------------
# 12. State Tracking
# ---------------------------------------------------------------------------

class TestStateTracking:
    def test_before_after_preserved(self, tmp_path):
        entry = _decision(
            before_state="gold_label=overclaim",
            after_state="gold_label=correlation_vs_causation",
            follow_up_action="Re-run all models on case031",
        )
        log_decision(entry, base_dir=tmp_path)
        decisions = read_decisions(tmp_path)
        d = decisions[0]
        assert d.before_state == "gold_label=overclaim"
        assert d.after_state == "gold_label=correlation_vs_causation"
        assert d.follow_up_action == "Re-run all models on case031"


# ===========================================================================
# Gen 6.1: Upstream Dependency / Error Propagation Hardening Tests
# ===========================================================================


def _upstream_decision(**kwargs) -> DecisionEntry:
    """Create a DecisionEntry with upstream dependency fields filled."""
    defaults = dict(
        decision_id="dec_up_001",
        timestamp="2026-04-07T00:00:00Z",
        decision_type="gold_review_decision",
        target="case031",
        target_kind="case",
        source_module="calibrate",
        decision="accepted",
        reason="Gold label appears incorrect",
        evidence_summary="3/3 models disagree",
        reviewer="alice",
        upstream_module="disagreement_lab",
        upstream_reference="dis_case031_report",
        upstream_dependency_summary="Disagreement lab flagged case031 as gold-review candidate",
        dependency_confidence="high",
        dependency_risk_note="",
        upstream_chain=[
            UpstreamStep(
                module="insights",
                reference="insights_2026_04",
                description="Identified case031 as unstable",
                confidence="high",
            ),
            UpstreamStep(
                module="disagreement_lab",
                reference="dis_case031",
                description="Flagged gold-review signal",
                confidence="high",
            ),
        ],
        propagation_risk_level="low",
        review_override=False,
    )
    defaults.update(kwargs)
    return DecisionEntry(**defaults)


# ---------------------------------------------------------------------------
# 13. Upstream Fields Persistence
# ---------------------------------------------------------------------------

class TestUpstreamPersistence:
    def test_upstream_fields_roundtrip(self, tmp_path):
        entry = _upstream_decision()
        log_decision(entry, base_dir=tmp_path)
        decisions = read_decisions(tmp_path)
        d = decisions[0]
        assert d.upstream_module == "disagreement_lab"
        assert d.upstream_reference == "dis_case031_report"
        assert d.upstream_dependency_summary.startswith("Disagreement lab")
        assert d.dependency_confidence == "high"
        assert d.propagation_risk_level == "low"
        assert d.review_override is False

    def test_upstream_chain_roundtrip(self, tmp_path):
        entry = _upstream_decision()
        log_decision(entry, base_dir=tmp_path)
        decisions = read_decisions(tmp_path)
        chain = decisions[0].upstream_chain
        assert len(chain) == 2
        assert chain[0].module == "insights"
        assert chain[1].module == "disagreement_lab"
        assert chain[0].confidence == "high"

    def test_empty_upstream_compatible(self, tmp_path):
        """Decisions without upstream fields remain fully compatible."""
        entry = _decision()
        log_decision(entry, base_dir=tmp_path)
        decisions = read_decisions(tmp_path)
        d = decisions[0]
        assert d.upstream_module == ""
        assert d.upstream_chain == []
        assert d.review_override is False
        assert d.propagation_risk_level == ""

    def test_mixed_entries_roundtrip(self, tmp_path):
        """Mixing upstream and non-upstream entries in same file."""
        log_decision(_decision(decision_id="plain_01"), base_dir=tmp_path)
        log_decision(_upstream_decision(decision_id="up_01"), base_dir=tmp_path)
        log_decision(_decision(decision_id="plain_02"), base_dir=tmp_path)
        decisions = read_decisions(tmp_path)
        assert len(decisions) == 3
        assert decisions[0].upstream_module == ""
        assert decisions[1].upstream_module == "disagreement_lab"
        assert decisions[2].upstream_module == ""

    def test_review_override_persists(self, tmp_path):
        entry = _upstream_decision(review_override=True)
        log_decision(entry, base_dir=tmp_path)
        decisions = read_decisions(tmp_path)
        assert decisions[0].review_override is True


# ---------------------------------------------------------------------------
# 14. Dependency Summary
# ---------------------------------------------------------------------------

class TestDependencySummary:
    def _make_decisions(self) -> list[DecisionEntry]:
        return [
            _upstream_decision(
                decision_id="d1", upstream_module="disagreement_lab",
                dependency_confidence="high", propagation_risk_level="low",
                decision="accepted",
            ),
            _upstream_decision(
                decision_id="d2", upstream_module="calibrate",
                dependency_confidence="low", propagation_risk_level="high",
                decision="accepted", review_override=True,
            ),
            _upstream_decision(
                decision_id="d3", upstream_module="calibrate",
                dependency_confidence="heuristic", propagation_risk_level="medium",
                decision="rejected",
            ),
            _decision(decision_id="d4"),  # no upstream
            _upstream_decision(
                decision_id="d5", upstream_module="router",
                dependency_confidence="medium", propagation_risk_level="low",
                decision="deferred",
            ),
        ]

    def test_total_counts(self):
        summary = build_dependency_summary(self._make_decisions())
        assert summary.total_decisions == 5
        assert summary.decisions_with_upstream == 4  # d4 has no upstream

    def test_by_upstream_module(self):
        summary = build_dependency_summary(self._make_decisions())
        assert summary.by_upstream_module["calibrate"] == 2
        assert summary.by_upstream_module["disagreement_lab"] == 1
        assert summary.by_upstream_module["router"] == 1

    def test_by_confidence(self):
        summary = build_dependency_summary(self._make_decisions())
        assert summary.by_dependency_confidence["high"] == 1
        assert summary.by_dependency_confidence["low"] == 1
        assert summary.by_dependency_confidence["heuristic"] == 1
        assert summary.by_dependency_confidence["medium"] == 1

    def test_by_propagation_risk(self):
        summary = build_dependency_summary(self._make_decisions())
        assert summary.by_propagation_risk["low"] == 2
        assert summary.by_propagation_risk["high"] == 1
        assert summary.by_propagation_risk["medium"] == 1

    def test_override_count_and_rate(self):
        summary = build_dependency_summary(self._make_decisions())
        assert summary.override_count == 1
        assert summary.override_rate == pytest.approx(0.25, abs=0.01)

    def test_weak_basis_accepted(self):
        summary = build_dependency_summary(self._make_decisions())
        # d2: low confidence + accepted, d3: heuristic + rejected (not counted)
        assert summary.weak_basis_accepted == 1

    def test_risky_acceptances(self):
        summary = build_dependency_summary(self._make_decisions())
        assert len(summary.risky_acceptances) == 1
        assert summary.risky_acceptances[0].decision_id == "d2"

    def test_rejected_upstream_patterns(self):
        summary = build_dependency_summary(self._make_decisions())
        assert summary.rejected_upstream_patterns["calibrate"] == 1

    def test_empty_summary(self):
        summary = build_dependency_summary([])
        assert summary.total_decisions == 0
        assert summary.decisions_with_upstream == 0
        assert summary.override_rate == 0.0

    def test_summary_from_disk(self, tmp_path):
        for d in self._make_decisions():
            log_decision(d, base_dir=tmp_path)
        summary = build_dependency_summary(base_dir=tmp_path)
        assert summary.total_decisions == 5
        assert summary.decisions_with_upstream == 4


# ---------------------------------------------------------------------------
# 15. Propagation Chain Detection
# ---------------------------------------------------------------------------

class TestPropagationChains:
    def test_chain_detected(self):
        """Two decisions on same target from different modules → chain."""
        decisions = [
            _upstream_decision(
                decision_id="d1", target="case031",
                source_module="calibrate", upstream_module="insights",
                decision="accepted", propagation_risk_level="medium",
            ),
            _upstream_decision(
                decision_id="d2", target="case031",
                source_module="disagreement_lab", upstream_module="calibrate",
                decision="accepted", propagation_risk_level="low",
            ),
        ]
        summary = build_dependency_summary(decisions)
        assert len(summary.propagation_chains) == 1
        chain = summary.propagation_chains[0]
        assert chain["target"] == "case031"
        assert chain["n_decisions"] == 2
        assert len(chain["modules_involved"]) >= 2

    def test_no_chain_single_module(self):
        """Same target, same module → no chain."""
        decisions = [
            _decision(decision_id="d1", target="case001",
                      source_module="calibrate", decision="accepted"),
            _decision(decision_id="d2", target="case001",
                      source_module="calibrate", decision="rejected"),
        ]
        summary = build_dependency_summary(decisions)
        assert len(summary.propagation_chains) == 0

    def test_no_chain_no_acceptance(self):
        """Same target, different modules, but all rejected → no chain."""
        decisions = [
            _upstream_decision(
                decision_id="d1", target="case099",
                source_module="calibrate", upstream_module="insights",
                decision="rejected",
            ),
            _upstream_decision(
                decision_id="d2", target="case099",
                source_module="router", upstream_module="calibrate",
                decision="rejected",
            ),
        ]
        summary = build_dependency_summary(decisions)
        assert len(summary.propagation_chains) == 0

    def test_chain_with_weak_links(self):
        decisions = [
            _upstream_decision(
                decision_id="d1", target="case055",
                source_module="calibrate", upstream_module="insights",
                decision="accepted", dependency_confidence="low",
            ),
            _upstream_decision(
                decision_id="d2", target="case055",
                source_module="router", upstream_module="calibrate",
                decision="accepted", dependency_confidence="high",
            ),
        ]
        summary = build_dependency_summary(decisions)
        assert len(summary.propagation_chains) == 1
        assert summary.propagation_chains[0]["n_weak_links"] == 1

    def test_chain_risk_signal(self):
        decisions = [
            _upstream_decision(
                decision_id="d1", target="case077",
                source_module="calibrate", upstream_module="insights",
                decision="accepted", propagation_risk_level="high",
            ),
            _upstream_decision(
                decision_id="d2", target="case077",
                source_module="router", upstream_module="calibrate",
                decision="accepted", propagation_risk_level="low",
            ),
        ]
        summary = build_dependency_summary(decisions)
        chain = summary.propagation_chains[0]
        assert chain["has_risk_signal"] is True


# ---------------------------------------------------------------------------
# 16. Decision Trace
# ---------------------------------------------------------------------------

class TestDecisionTrace:
    def _make_decisions(self) -> list[DecisionEntry]:
        return [
            _upstream_decision(
                decision_id="traced_01", target="case031",
                upstream_module="disagreement_lab",
                dependency_confidence="low",
                propagation_risk_level="high",
                review_override=True,
                dependency_risk_note="Based on heuristic only",
            ),
            _decision(decision_id="related_01", target="case031",
                      source_module="calibrate"),
            _decision(decision_id="unrelated_01", target="case099"),
        ]

    def test_trace_found(self):
        decisions = self._make_decisions()
        trace = trace_decision("traced_01", decisions)
        assert trace is not None
        assert trace["decision"].decision_id == "traced_01"

    def test_trace_not_found(self):
        trace = trace_decision("nonexistent", self._make_decisions())
        assert trace is None

    def test_trace_has_upstream(self):
        trace = trace_decision("traced_01", self._make_decisions())
        assert trace["has_upstream"] is True

    def test_trace_upstream_chain(self):
        trace = trace_decision("traced_01", self._make_decisions())
        assert len(trace["upstream_chain"]) == 2
        assert trace["upstream_chain"][0]["module"] == "insights"

    def test_trace_related_decisions(self):
        trace = trace_decision("traced_01", self._make_decisions())
        assert trace["n_related"] == 1
        assert trace["related_decisions"][0].decision_id == "related_01"

    def test_trace_risk_factors(self):
        trace = trace_decision("traced_01", self._make_decisions())
        factors = trace["risk_factors"]
        assert len(factors) >= 3  # low confidence, high risk, override, risk note
        assert any("low" in f for f in factors)
        assert any("high" in f.lower() or "Propagation" in f for f in factors)
        assert any("overr" in f.lower() for f in factors)

    def test_trace_is_override(self):
        trace = trace_decision("traced_01", self._make_decisions())
        assert trace["is_override"] is True

    def test_trace_no_upstream(self):
        trace = trace_decision("related_01", self._make_decisions())
        assert trace["has_upstream"] is False
        assert trace["upstream_chain"] == []
        assert trace["risk_factors"] == []

    def test_trace_from_disk(self, tmp_path):
        for d in self._make_decisions():
            log_decision(d, base_dir=tmp_path)
        trace = trace_decision("traced_01", base_dir=tmp_path)
        assert trace is not None
        assert trace["decision"].decision_id == "traced_01"


# ---------------------------------------------------------------------------
# 17. Query Helpers — Upstream
# ---------------------------------------------------------------------------

class TestUpstreamQueries:
    def _make_decisions(self) -> list[DecisionEntry]:
        return [
            _upstream_decision(
                decision_id="w1", dependency_confidence="low",
                decision="accepted", review_override=False,
                propagation_risk_level="low",
            ),
            _upstream_decision(
                decision_id="w2", dependency_confidence="heuristic",
                decision="rejected", review_override=True,
                propagation_risk_level="medium",
            ),
            _upstream_decision(
                decision_id="w3", dependency_confidence="high",
                decision="accepted", review_override=True,
                propagation_risk_level="high",
            ),
            _decision(decision_id="w4"),  # no upstream fields
        ]

    def test_query_weak_basis(self):
        results = query_weak_basis_decisions(self._make_decisions())
        assert len(results) == 2
        ids = {d.decision_id for d in results}
        assert ids == {"w1", "w2"}

    def test_query_overrides(self):
        results = query_overrides(self._make_decisions())
        assert len(results) == 2
        ids = {d.decision_id for d in results}
        assert ids == {"w2", "w3"}

    def test_query_risky_accepted(self):
        results = query_risky_accepted(self._make_decisions())
        assert len(results) == 1
        assert results[0].decision_id == "w3"

    def test_risky_rejected_not_included(self):
        """Rejected high-risk decisions are NOT risky acceptances."""
        decisions = [
            _upstream_decision(
                decision_id="r1", propagation_risk_level="high",
                decision="rejected",
            ),
        ]
        assert query_risky_accepted(decisions) == []

    def test_weak_basis_from_disk(self, tmp_path):
        for d in self._make_decisions():
            log_decision(d, base_dir=tmp_path)
        results = query_weak_basis_decisions(base_dir=tmp_path)
        assert len(results) == 2

    def test_overrides_from_disk(self, tmp_path):
        for d in self._make_decisions():
            log_decision(d, base_dir=tmp_path)
        results = query_overrides(base_dir=tmp_path)
        assert len(results) == 2


# ---------------------------------------------------------------------------
# 18. Dependency Summary Rendering
# ---------------------------------------------------------------------------

class TestDependencyRendering:
    def test_render_dependency_summary(self):
        decisions = [
            _upstream_decision(
                decision_id="d1", upstream_module="calibrate",
                dependency_confidence="high", propagation_risk_level="low",
                decision="accepted",
            ),
            _upstream_decision(
                decision_id="d2", upstream_module="router",
                dependency_confidence="low", propagation_risk_level="high",
                decision="accepted", review_override=True,
            ),
        ]
        summary = build_dependency_summary(decisions)
        md = render_dependency_summary(summary)
        assert "## Upstream Dependency Summary" in md
        assert "Total decisions" in md
        assert "With upstream dependency" in md
        assert "Override rate" in md

    def test_render_empty_dependency_summary(self):
        summary = build_dependency_summary([])
        md = render_dependency_summary(summary)
        assert "No decisions recorded" in md

    def test_render_trace(self):
        decisions = [
            _upstream_decision(
                decision_id="tr_01", target="case031",
                dependency_confidence="low",
                propagation_risk_level="high",
                review_override=True,
            ),
        ]
        trace = trace_decision("tr_01", decisions)
        md = render_trace(trace)
        assert "## Decision Trace: tr_01" in md
        assert "### Upstream Dependency" in md
        assert "### Risk Factors" in md
        assert "### Upstream Chain" in md

    def test_render_trace_no_upstream(self):
        decisions = [_decision(decision_id="plain_01")]
        trace = trace_decision("plain_01", decisions)
        md = render_trace(trace)
        assert "## Decision Trace: plain_01" in md
        assert "### Upstream Dependency" not in md

    def test_render_dependency_has_confidence_table(self):
        decisions = [
            _upstream_decision(
                decision_id="d1", dependency_confidence="high",
            ),
            _upstream_decision(
                decision_id="d2", dependency_confidence="low",
            ),
        ]
        summary = build_dependency_summary(decisions)
        md = render_dependency_summary(summary)
        assert "Dependency Confidence Distribution" in md
        assert "high" in md
        assert "low" in md

    def test_render_dependency_has_risk_table(self):
        decisions = [
            _upstream_decision(
                decision_id="d1", propagation_risk_level="low",
            ),
            _upstream_decision(
                decision_id="d2", propagation_risk_level="high",
            ),
        ]
        summary = build_dependency_summary(decisions)
        md = render_dependency_summary(summary)
        assert "Propagation Risk Distribution" in md
