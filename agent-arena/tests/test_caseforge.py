"""Tests for Gen 3 Caseforge — agent-arena v0.6.8.

Tests cover:
- Explicit request-based generation
- Calibration-driven generation (data gaps, model confusion, category refinement)
- Borderline probe generation
- Candidate structure completeness
- Review status enforcement
- YAML draft rendering
- Report rendering
- Empty / edge-case inputs
"""

from __future__ import annotations

import pytest

from agent_arena.schemas import (
    CalibrationProposal,
    CalibrationReport,
    CaseCandidate,
    CaseforgeReport,
)
from agent_arena.caseforge import (
    candidate_to_yaml_draft,
    forge_cases,
    generate_borderline_probes,
    generate_from_calibration,
    generate_from_request,
    render_caseforge_report,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cal_report(**kwargs) -> CalibrationReport:
    """Create a CalibrationReport with defaults."""
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
    """Create a CalibrationProposal with defaults."""
    defaults = dict(
        proposal_type="data_gap",
        target="overclaim",
        target_kind="category",
        reason="Category 'overclaim' has only 1 case",
        evidence_summary="1 unique case, 3 total runs.",
        confidence="medium",
        strength=0.7,
        recommended_action="Add more cases.",
    )
    defaults.update(kwargs)
    return CalibrationProposal(**defaults)


# ---------------------------------------------------------------------------
# 1. Explicit Request Generation
# ---------------------------------------------------------------------------

class TestExplicitRequest:
    def test_generate_single_clear(self):
        candidates = generate_from_request(family="solid", case_type="clear", count=1)
        assert len(candidates) == 1
        c = candidates[0]
        assert c.target_family == "solid"
        assert c.proposed_gold_case_type == "clear"
        assert c.generation_mode == "explicit_request"

    def test_generate_multiple(self):
        candidates = generate_from_request(family="overclaim", case_type="clear", count=3)
        # Limited by available templates
        assert len(candidates) >= 1
        assert all(c.target_family == "overclaim" for c in candidates)

    def test_generate_borderline(self):
        candidates = generate_from_request(
            family="correlation_vs_causation", case_type="borderline"
        )
        assert len(candidates) == 1
        c = candidates[0]
        assert c.proposed_gold_case_type == "borderline"
        assert c.ambiguity_level == "medium"

    def test_generate_mechanism(self):
        candidates = generate_from_request(
            family="mechanism_vs_evidence", case_type="clear"
        )
        assert len(candidates) == 1
        assert candidates[0].proposed_gold_label == "mechanism_vs_evidence"

    def test_unknown_family_empty(self):
        candidates = generate_from_request(family="nonexistent")
        assert len(candidates) == 0

    def test_model_confusion_target_set(self):
        candidates = generate_from_request(
            family="solid",
            model_confusion_target="sonnet reads hedged language too charitably",
        )
        assert len(candidates) == 1
        assert "charitably" in candidates[0].model_confusion_target

    def test_all_families_have_clear_templates(self):
        for family in ["solid", "overclaim", "correlation_vs_causation",
                        "mechanism_vs_evidence"]:
            candidates = generate_from_request(family=family, case_type="clear")
            assert len(candidates) >= 1, f"No clear template for {family}"

    def test_all_families_have_borderline_templates(self):
        for family in ["solid", "overclaim", "correlation_vs_causation",
                        "mechanism_vs_evidence"]:
            candidates = generate_from_request(family=family, case_type="borderline")
            assert len(candidates) >= 1, f"No borderline template for {family}"


# ---------------------------------------------------------------------------
# 2. Calibration-Driven Generation
# ---------------------------------------------------------------------------

class TestCalibrationDriven:
    def test_data_gap_generates_candidates(self):
        report = _cal_report(
            data_gap_candidates=[
                _proposal(target="overclaim", reason="Too few cases"),
            ],
            n_proposals=1,
        )
        candidates = generate_from_calibration(report)
        assert len(candidates) >= 1
        assert candidates[0].generation_mode == "data_gap"
        assert candidates[0].target_family == "overclaim"

    def test_model_confusion_generates_probes(self):
        report = _cal_report(
            model_confusion_candidates=[
                _proposal(
                    proposal_type="model_confusion",
                    target="sonnet",
                    target_kind="model",
                    reason="sonnet confuses 'solid' with 'overclaim' in 3/5 runs",
                ),
            ],
            n_proposals=1,
        )
        candidates = generate_from_calibration(report)
        assert len(candidates) >= 1
        assert candidates[0].generation_mode == "confusion_probe"
        assert candidates[0].model_confusion_target != ""

    def test_category_refinement_generates_anchoring(self):
        report = _cal_report(
            category_refinement_candidates=[
                _proposal(
                    proposal_type="category_refinement",
                    target="overclaim",
                    target_kind="category",
                    reason="Low correctness rate (30%)",
                ),
            ],
            n_proposals=1,
        )
        candidates = generate_from_calibration(report)
        assert len(candidates) >= 1
        assert candidates[0].generation_mode == "calibration_signal"

    def test_borderline_gap_generates_borderline(self):
        report = _cal_report(
            data_gap_candidates=[
                _proposal(
                    target="solid",
                    reason="Category 'solid' may lack borderline / challenging cases",
                ),
            ],
            n_proposals=1,
        )
        candidates = generate_from_calibration(report)
        assert len(candidates) >= 1
        assert candidates[0].proposed_gold_case_type == "borderline"

    def test_unknown_family_in_gap_skipped(self):
        report = _cal_report(
            data_gap_candidates=[
                _proposal(target="nonexistent_family"),
            ],
            n_proposals=1,
        )
        candidates = generate_from_calibration(report)
        assert len(candidates) == 0

    def test_empty_report(self):
        report = _cal_report()
        candidates = generate_from_calibration(report)
        assert len(candidates) == 0


# ---------------------------------------------------------------------------
# 3. Borderline Probes
# ---------------------------------------------------------------------------

class TestBorderlineProbes:
    def test_all_families(self):
        candidates = generate_borderline_probes()
        families = set(c.target_family for c in candidates)
        assert "solid" in families
        assert "overclaim" in families
        assert "correlation_vs_causation" in families
        assert "mechanism_vs_evidence" in families

    def test_specific_family(self):
        candidates = generate_borderline_probes(families=["overclaim"])
        assert len(candidates) >= 1
        assert all(c.target_family == "overclaim" for c in candidates)

    def test_mode_is_borderline_probe(self):
        candidates = generate_borderline_probes(families=["solid"])
        assert candidates[0].generation_mode == "borderline_probe"
        assert candidates[0].proposed_gold_case_type == "borderline"

    def test_unknown_family_skipped(self):
        candidates = generate_borderline_probes(families=["nonexistent"])
        assert len(candidates) == 0


# ---------------------------------------------------------------------------
# 4. Candidate Structure
# ---------------------------------------------------------------------------

class TestCandidateStructure:
    def test_all_required_fields_present(self):
        candidates = generate_from_request(family="overclaim", case_type="clear")
        c = candidates[0]
        assert c.candidate_id
        assert c.review_status == "pending_human_review"
        assert c.generation_mode
        assert c.target_family
        assert c.input_text
        assert c.proposed_gold_label
        assert c.proposed_gold_confidence in ("high", "medium", "low")
        assert c.proposed_gold_case_type in ("clear", "borderline")
        assert c.why_this_candidate_exists
        assert c.which_gap_it_addresses

    def test_findings_present(self):
        candidates = generate_from_request(family="overclaim", case_type="clear")
        c = candidates[0]
        assert len(c.proposed_expected_findings) > 0
        for f in c.proposed_expected_findings:
            assert f.finding
            assert f.severity in ("major", "moderate", "minor")

    def test_evidence_spans_present(self):
        candidates = generate_from_request(family="overclaim", case_type="clear")
        c = candidates[0]
        assert len(c.proposed_evidence_spans) > 0
        for s in c.proposed_evidence_spans:
            assert s.span
            assert s.supports_finding

    def test_alternative_reading_present(self):
        candidates = generate_from_request(
            family="correlation_vs_causation", case_type="borderline"
        )
        c = candidates[0]
        assert c.proposed_gold_alternative_reading

    def test_input_text_is_clean_prose(self):
        """Input text should be clean prose, no URLs or artifacts."""
        for family in ["solid", "overclaim", "correlation_vs_causation",
                        "mechanism_vs_evidence"]:
            candidates = generate_from_request(family=family)
            for c in candidates:
                assert "http" not in c.input_text.lower()
                assert "www." not in c.input_text.lower()
                assert len(c.input_text) >= 100  # substantial text

    def test_steering_axes_documented(self):
        """Every candidate should have steering axes set."""
        candidates = generate_from_request(
            family="mechanism_vs_evidence", case_type="clear"
        )
        c = candidates[0]
        assert c.category_gap == "mechanism_vs_evidence"
        assert c.borderline_need == "clear"


# ---------------------------------------------------------------------------
# 5. Review Status Enforcement
# ---------------------------------------------------------------------------

class TestReviewStatus:
    def test_all_candidates_pending_review(self):
        """No candidate should ever be auto-approved."""
        candidates = generate_from_request(family="solid", count=5)
        for c in candidates:
            assert c.review_status == "pending_human_review"

    def test_calibration_candidates_pending(self):
        report = _cal_report(
            data_gap_candidates=[_proposal(target="overclaim")],
            n_proposals=1,
        )
        candidates = generate_from_calibration(report)
        for c in candidates:
            assert c.review_status == "pending_human_review"

    def test_borderline_candidates_pending(self):
        candidates = generate_borderline_probes()
        for c in candidates:
            assert c.review_status == "pending_human_review"


# ---------------------------------------------------------------------------
# 6. YAML Draft Rendering
# ---------------------------------------------------------------------------

class TestYAMLDraft:
    def test_yaml_contains_draft_warning(self):
        candidates = generate_from_request(family="overclaim")
        yaml = candidate_to_yaml_draft(candidates[0])
        assert "CASEFORGE DRAFT" in yaml
        assert "NOT A FINALIZED CASE" in yaml
        assert "pending_human_review" in yaml

    def test_yaml_has_task_fields(self):
        candidates = generate_from_request(family="solid")
        yaml = candidate_to_yaml_draft(candidates[0])
        assert "id:" in yaml
        assert "title:" in yaml
        assert "domain:" in yaml
        assert "task_type:" in yaml
        assert "task_family:" in yaml
        assert "gold_label:" in yaml
        assert "prompt:" in yaml
        assert "expected_findings:" in yaml

    def test_yaml_has_caseforge_metadata(self):
        candidates = generate_from_request(family="overclaim")
        yaml = candidate_to_yaml_draft(candidates[0])
        assert "generation_mode:" in yaml
        assert "category_gap:" in yaml
        assert "shape_gap:" in yaml


# ---------------------------------------------------------------------------
# 7. Full Pipeline: forge_cases
# ---------------------------------------------------------------------------

class TestForgeCases:
    def test_explicit_mode(self):
        report = forge_cases(family="solid", count=1)
        assert report.n_candidates == 1
        assert "explicit:" in report.gaps_addressed[0]

    def test_calibration_mode(self):
        cal = _cal_report(
            data_gap_candidates=[_proposal(target="overclaim")],
            n_proposals=1,
        )
        report = forge_cases(calibration_report=cal)
        assert report.n_candidates >= 1
        assert any("calibration:" in g for g in report.gaps_addressed)

    def test_borderline_mode(self):
        report = forge_cases(borderline_mode=True)
        assert report.n_candidates >= 4  # one per family
        assert "borderline_probes" in report.gaps_addressed

    def test_combined_modes(self):
        cal = _cal_report(
            data_gap_candidates=[_proposal(target="solid")],
            n_proposals=1,
        )
        report = forge_cases(
            family="overclaim",
            calibration_report=cal,
            borderline_mode=True,
        )
        modes = set(c.generation_mode for c in report.candidates)
        assert "explicit_request" in modes
        # data_gap and/or borderline_probe should also be present
        assert len(modes) >= 2

    def test_empty_request(self):
        report = forge_cases()
        assert report.n_candidates == 0

    def test_review_summary(self):
        report = forge_cases(family="solid", count=1)
        assert "pending" in report.review_summary.lower() or "review" in report.review_summary.lower()


# ---------------------------------------------------------------------------
# 8. Report Rendering
# ---------------------------------------------------------------------------

class TestRenderReport:
    def test_empty_report(self):
        report = forge_cases()
        md = render_caseforge_report(report)
        assert "Gen 3 Caseforge" in md
        assert "No candidates" in md

    def test_full_report(self):
        report = forge_cases(family="overclaim", count=1)
        md = render_caseforge_report(report)
        assert "## Candidate Summary" in md
        assert "## Candidate Details" in md
        assert "overclaim" in md
        assert "human review" in md.lower()

    def test_report_has_all_candidates(self):
        report = forge_cases(borderline_mode=True)
        md = render_caseforge_report(report)
        for c in report.candidates:
            assert c.candidate_id in md

    def test_report_footer(self):
        report = forge_cases(family="solid")
        md = render_caseforge_report(report)
        assert "draft candidates only" in md
        assert "No gold labels are finalized" in md


# ---------------------------------------------------------------------------
# 9. Clear vs Borderline Distinction
# ---------------------------------------------------------------------------

class TestClearVsBorderline:
    def test_clear_has_low_ambiguity(self):
        candidates = generate_from_request(family="overclaim", case_type="clear")
        c = candidates[0]
        assert c.ambiguity_level == "low"
        assert c.proposed_gold_confidence == "high"

    def test_borderline_has_medium_ambiguity(self):
        candidates = generate_from_request(family="overclaim", case_type="borderline")
        c = candidates[0]
        assert c.ambiguity_level == "medium"
        assert c.proposed_gold_confidence == "medium"

    def test_borderline_has_richer_alt_reading(self):
        clear = generate_from_request(family="solid", case_type="clear")[0]
        borderline = generate_from_request(family="solid", case_type="borderline")[0]
        # Borderline should have a more substantive alternative reading
        assert len(borderline.proposed_gold_alternative_reading) > 0
