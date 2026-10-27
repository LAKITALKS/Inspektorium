"""Tests for Report Engine v1 — client-facing audit reports."""

from __future__ import annotations

import pytest

from inspektorium.audit.reports.reporting import (
    generate_client_report,
    generate_html_report,
    pdf_available,
    _extract_top_findings,
    _extract_recommendations,
    _overall_status,
    _label,
    _section_executive_summary,
    _section_key_findings,
    _section_recommendations,
    _section_method_note,
    _section_technical_appendix,
)
from inspektorium.audit.schemas import (
    AgentResponse,
    AgentResult,
    ClaimCheckResult,
    ClaimTruthStatus,
    ComparativeClaim,
    ConsistencyFinding,
    DiagnosticScores,
    Difficulty,
    EvaluatedResult,
    EvidenceSpan,
    FailureInstance,
    ForensicFlag,
    GroundingAudit,
    MechanismAnalysis,
    RunRecord,
    ScoredDimension,
    Task,
    TaskType,
)


# ---------------------------------------------------------------------------
# Fixtures — reusable test data
# ---------------------------------------------------------------------------

def _make_task(**overrides) -> Task:
    defaults = dict(
        id="test-001",
        title="Test Audit Subject",
        domain="statistics",
        difficulty=Difficulty.MEDIUM,
        task_type=TaskType.CLOSED_WITH_REASONING,
        prompt="Analyze this data.",
        expected_answer="42",
        task_family="solid",
    )
    defaults.update(overrides)
    return Task(**defaults)


def _make_agent_result(**overrides) -> AgentResult:
    defaults = dict(
        provider="TestAgent",
        model="test-model-v1",
        raw_output="raw output text",
        parsed=AgentResponse(
            final_answer="42",
            assumptions=["Data is complete"],
            steps=["Step 1: Read data", "Step 2: Calculate"],
            confidence=0.85,
            confidence_state="VALID",
        ),
        parse_ok=True,
        latency_ms=1500,
    )
    defaults.update(overrides)
    return AgentResult(**defaults)


def _make_scores(**overrides) -> DiagnosticScores:
    defaults = dict(
        correctness=0.9,
        support_strength=0.7,
        structural_reasoning=0.8,
        assumption_discipline=0.6,
        uncertainty_handling=0.5,
        alternative_hypothesis_quality=0.4,
        self_monitoring_quality=0.7,
        insight_depth=0.6,
        mechanism_quality=0.7,
        communication_efficiency=0.8,
    )
    defaults.update(overrides)
    return DiagnosticScores(**defaults)


def _make_failure(
    category: str = "overclaiming",
    severity: str = "moderate",
    description: str = "Test finding",
    confidence: str = "MEDIUM CONFIDENCE",
) -> FailureInstance:
    return FailureInstance(
        category=category,
        severity=severity,
        description=description,
        confidence=confidence,
        evidence=[
            EvidenceSpan(
                text="Some evidence text here",
                source_field="steps[1]",
                role="supporting",
            )
        ],
    )


def _make_evaluated_result(**overrides) -> EvaluatedResult:
    defaults = dict(
        agent_result=_make_agent_result(),
        scores=_make_scores(),
        failures=[],
        consistency_findings=[],
        forensic_flags=[],
    )
    defaults.update(overrides)
    return EvaluatedResult(**defaults)


def _make_run_record(**overrides) -> RunRecord:
    defaults = dict(
        run_id="run_test_001",
        task=_make_task(),
        results=[_make_evaluated_result()],
        timestamp="2026-06-10T10:00:00+00:00",
    )
    defaults.update(overrides)
    return RunRecord(**defaults)


# ---------------------------------------------------------------------------
# 1. Report generation works
# ---------------------------------------------------------------------------

class TestReportGeneration:
    def test_basic_generation(self):
        record = _make_run_record()
        report = generate_client_report(record)
        assert isinstance(report, str)
        assert len(report) > 100

    def test_report_has_all_sections(self):
        record = _make_run_record()
        report = generate_client_report(record)
        assert "## 1. Executive Summary" in report
        assert "## 2. Key Findings" in report
        assert "## 3. What To Change" in report
        assert "## 4. Method Note" in report
        assert "## 5. Technical Appendix" in report

    def test_report_contains_run_id(self):
        record = _make_run_record(run_id="run_unique_abc")
        report = generate_client_report(record)
        assert "run_unique_abc" in report

    def test_report_contains_task_info(self):
        record = _make_run_record()
        report = generate_client_report(record)
        assert "Test Audit Subject" in report
        assert "statistics" in report

    def test_report_contains_footer(self):
        record = _make_run_record()
        report = generate_client_report(record)
        assert "Inspektorium" in report

    def test_multi_agent_report(self):
        r1 = _make_evaluated_result(
            agent_result=_make_agent_result(provider="AgentA", model="model-a")
        )
        r2 = _make_evaluated_result(
            agent_result=_make_agent_result(provider="AgentB", model="model-b")
        )
        record = _make_run_record(results=[r1, r2])
        report = generate_client_report(record)
        assert "AgentA" in report
        assert "AgentB" in report

    def test_empty_results(self):
        record = _make_run_record(results=[])
        report = generate_client_report(record)
        assert isinstance(report, str)
        assert "Executive Summary" in report


# ---------------------------------------------------------------------------
# 2. Executive summary quality
# ---------------------------------------------------------------------------

class TestExecutiveSummary:
    def test_summary_generated(self):
        record = _make_run_record()
        summary = _section_executive_summary(record)
        assert "Executive Summary" in summary
        assert "Overall Assessment" in summary

    def test_key_findings_visible(self):
        failures = [
            _make_failure("wrong_answer", "critical", "Answer is incorrect"),
            _make_failure("overclaiming", "major", "Claims exceed evidence"),
        ]
        result = _make_evaluated_result(failures=failures)
        record = _make_run_record(results=[result])
        summary = _section_executive_summary(record)
        assert "Key Findings" in summary

    def test_no_raw_json_in_summary(self):
        record = _make_run_record()
        summary = _section_executive_summary(record)
        assert "{" not in summary or "{{" in summary  # Allow template braces
        assert "dict(" not in summary
        assert "EvaluatedResult" not in summary

    def test_status_indicator_present(self):
        record = _make_run_record()
        summary = _section_executive_summary(record)
        assert any(s in summary for s in ["PASS", "CAUTION", "CRITICAL", "ISSUES"])

    def test_recommendation_present(self):
        failures = [_make_failure("wrong_answer", "critical", "Wrong")]
        result = _make_evaluated_result(failures=failures)
        record = _make_run_record(results=[result])
        summary = _section_executive_summary(record)
        assert "Recommendation" in summary

    def test_study_forensics_classification_shown(self):
        result = _make_evaluated_result(
            study_forensics={
                "is_study_forensics": True,
                "detected_label": "overclaim",
                "gold_label": "overclaim",
                "label_correct": True,
            }
        )
        record = _make_run_record(results=[result])
        summary = _section_executive_summary(record)
        assert "Overclaim" in summary or "overclaim" in summary.lower()


# ---------------------------------------------------------------------------
# 3. Format rendering
# ---------------------------------------------------------------------------

class TestFormatRendering:
    def test_markdown_is_valid(self):
        record = _make_run_record()
        md = generate_client_report(record)
        assert md.startswith("> **DIAGNOSTIC / NON-RELEASE ARTIFACT")
        assert "official_release_authorized=false" in md
        assert "# Audit Report" in md
        assert "---" in md
        heading_count = md.count("\n## ")
        assert heading_count >= 4

    def test_html_is_valid(self):
        record = _make_run_record()
        html = generate_html_report(record)
        assert "<!DOCTYPE html>" in html
        assert "<html" in html
        assert "</html>" in html
        assert "<style>" in html
        assert "Audit Report" in html

    def test_html_contains_sections(self):
        record = _make_run_record()
        html = generate_html_report(record)
        assert "<h2>" in html
        assert "Executive Summary" in html
        assert "Key Findings" in html
        assert "Technical Appendix" in html

    def test_html_tables_rendered(self):
        record = _make_run_record()
        html = generate_html_report(record)
        assert "<table>" in html
        assert "<th>" in html

    def test_html_no_raw_markdown(self):
        record = _make_run_record()
        html = generate_html_report(record)
        lines = html.split("\n")
        body_start = next(i for i, l in enumerate(lines) if "<body>" in l)
        body_end = next(i for i, l in enumerate(lines) if "</body>" in l)
        body = "\n".join(lines[body_start:body_end])
        # Markdown headings should not appear raw in HTML body
        assert "\n# " not in body
        assert "\n## " not in body

    def test_pdf_availability_check(self):
        result = pdf_available()
        assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# 4. Missing fields / degraded input
# ---------------------------------------------------------------------------

class TestDegradedInput:
    def test_no_failures(self):
        result = _make_evaluated_result(failures=[])
        record = _make_run_record(results=[result])
        report = generate_client_report(record)
        assert "No significant findings" in report

    def test_no_parsed_response(self):
        ar = _make_agent_result(parsed=None, parse_ok=False)
        result = _make_evaluated_result(agent_result=ar)
        record = _make_run_record(results=[result])
        report = generate_client_report(record)
        assert isinstance(report, str)
        assert len(report) > 100

    def test_missing_task_family(self):
        task = _make_task(task_family=None)
        record = _make_run_record(task=task)
        report = generate_client_report(record)
        assert isinstance(report, str)

    def test_missing_gold_label(self):
        task = _make_task(gold_label=None, gold_confidence=None)
        record = _make_run_record(task=task)
        report = generate_client_report(record)
        assert isinstance(report, str)

    def test_empty_evidence(self):
        failure = FailureInstance(
            category="overclaiming",
            severity="moderate",
            description="No evidence provided",
            evidence=[],
        )
        result = _make_evaluated_result(failures=[failure])
        record = _make_run_record(results=[result])
        report = generate_client_report(record)
        assert "No evidence provided" in report

    def test_no_consistency_findings(self):
        result = _make_evaluated_result(consistency_findings=[])
        record = _make_run_record(results=[result])
        report = generate_client_report(record)
        assert isinstance(report, str)

    def test_no_forensic_flags(self):
        result = _make_evaluated_result(forensic_flags=[])
        record = _make_run_record(results=[result])
        report = generate_client_report(record)
        assert isinstance(report, str)

    def test_no_mechanism_analysis(self):
        result = _make_evaluated_result()
        result.mechanism_analysis = None
        record = _make_run_record(results=[result])
        report = generate_client_report(record)
        assert isinstance(report, str)

    def test_no_reasoning_integrity(self):
        result = _make_evaluated_result()
        result.reasoning_integrity = {}
        record = _make_run_record(results=[result])
        report = generate_client_report(record)
        assert isinstance(report, str)

    def test_no_study_forensics(self):
        result = _make_evaluated_result()
        result.study_forensics = {}
        record = _make_run_record(results=[result])
        report = generate_client_report(record)
        assert isinstance(report, str)

    def test_minimal_scores(self):
        scores = DiagnosticScores()
        result = _make_evaluated_result(scores=scores)
        record = _make_run_record(results=[result])
        report = generate_client_report(record)
        assert isinstance(report, str)


# ---------------------------------------------------------------------------
# 5. Confidence marking
# ---------------------------------------------------------------------------

class TestConfidenceMarking:
    def test_confidence_marked_unkalibriert(self):
        result = _make_evaluated_result()
        record = _make_run_record(results=[result])
        report = generate_client_report(record)
        # Agent confidence should show UNKALIBRIERT tag
        if "Agent confidence" in report or "confidence" in report.lower():
            assert "UNKALIBRIERT" in report

    def test_failure_confidence_preserved(self):
        failure = _make_failure(confidence="HIGH CONFIDENCE")
        result = _make_evaluated_result(failures=[failure])
        record = _make_run_record(results=[result])
        report = generate_client_report(record)
        assert "HIGH CONFIDENCE" in report

    def test_heuristic_confidence_shown(self):
        failure = _make_failure(confidence="HEURISTIC")
        result = _make_evaluated_result(failures=[failure])
        record = _make_run_record(results=[result])
        report = generate_client_report(record)
        assert "HEURISTIC" in report

    def test_confidence_not_promoted(self):
        """Confidence should not appear as a quality indicator in executive section."""
        result = _make_evaluated_result()
        record = _make_run_record(results=[result])
        summary = _section_executive_summary(record)
        assert "confidence: 0.85" not in summary.lower()
        assert "85%" not in summary


# ---------------------------------------------------------------------------
# 6. No raw dump
# ---------------------------------------------------------------------------

class TestNoRawDump:
    def test_no_dict_repr(self):
        record = _make_run_record()
        report = generate_client_report(record)
        assert "{'category'" not in report
        assert '"category":' not in report
        assert "FailureInstance(" not in report
        assert "EvaluatedResult(" not in report

    def test_no_pydantic_dump(self):
        record = _make_run_record()
        report = generate_client_report(record)
        assert "model_dump" not in report
        assert "model_fields" not in report

    def test_categories_are_readable(self):
        failure = _make_failure("verbal_numeric_contradiction", "critical", "Numbers disagree")
        result = _make_evaluated_result(failures=[failure])
        record = _make_run_record(results=[result])
        report = generate_client_report(record)
        assert "Verbal claims contradict numeric data" in report

    def test_executive_is_readable(self):
        record = _make_run_record()
        summary = _section_executive_summary(record)
        # Should not contain internal field names
        assert "correctness:" not in summary
        assert "support_strength" not in summary
        assert "scored_dimensions" not in summary


# ---------------------------------------------------------------------------
# 7. Overall status logic
# ---------------------------------------------------------------------------

class TestOverallStatus:
    def test_good_status(self):
        scores = _make_scores(correctness=1.0, support_strength=0.9, structural_reasoning=0.9,
                              mechanism_quality=0.9, communication_efficiency=0.9)
        result = _make_evaluated_result(failures=[], scores=scores)
        status, _ = _overall_status([result])
        assert status == "good"

    def test_critical_status(self):
        failure = _make_failure("wrong_answer", "critical", "Wrong")
        result = _make_evaluated_result(failures=[failure])
        status, _ = _overall_status([result])
        assert status == "critical"

    def test_poor_status(self):
        scores = DiagnosticScores(correctness=0.2, support_strength=0.2)
        result = _make_evaluated_result(scores=scores, failures=[])
        status, _ = _overall_status([result])
        assert status == "poor"

    def test_empty_results(self):
        status, _ = _overall_status([])
        assert status == "unknown"


# ---------------------------------------------------------------------------
# 8. Category label translation
# ---------------------------------------------------------------------------

class TestCategoryLabels:
    def test_known_labels(self):
        assert "overclaim" not in _label("overclaim").lower() or "Overclaim" in _label("overclaim")
        assert _label("solid") != "solid"
        assert _label("correlation_vs_causation") != "correlation_vs_causation"

    def test_unknown_label_fallback(self):
        result = _label("some_unknown_category")
        assert result == "Some Unknown Category"

    def test_mechanism_vs_evidence_readable(self):
        label = _label("mechanism_vs_evidence")
        assert "evidence" in label.lower()


# ---------------------------------------------------------------------------
# 9. Rich report content
# ---------------------------------------------------------------------------

class TestRichContent:
    def test_consistency_in_appendix(self):
        finding = ConsistencyFinding(
            check_type="numeric_verbal_reversal",
            status="fail",
            description="Numbers disagree with text",
            confidence="HIGH CONFIDENCE",
        )
        result = _make_evaluated_result(consistency_findings=[finding])
        record = _make_run_record(results=[result])
        appendix = _section_technical_appendix(record)
        assert "Consistency" in appendix
        assert "Numbers disagree" in appendix

    def test_forensic_flags_in_appendix(self):
        flag = ForensicFlag(
            flag_type="calibration_gap",
            description="Confidence doesn't match reasoning quality",
            severity="moderate",
        )
        result = _make_evaluated_result(forensic_flags=[flag])
        record = _make_run_record(results=[result])
        appendix = _section_technical_appendix(record)
        assert "Forensic Flags" in appendix
        assert "calibration_gap" in appendix

    def test_score_matrix_in_appendix(self):
        record = _make_run_record()
        appendix = _section_technical_appendix(record)
        assert "Score Matrix" in appendix
        assert "Correctness" in appendix
        assert "/100" in appendix or "Total" in appendix

    def test_method_note_explains_coverage(self):
        record = _make_run_record()
        method = _section_method_note(record)
        assert "What This Audit Covers" in method
        assert "What This Audit Does Not Cover" in method
        assert "Confidence Levels" in method

    def test_reasoning_integrity_in_appendix(self):
        result = _make_evaluated_result()
        result.reasoning_integrity = {
            "classification": "brittle",
            "n_intermediate_errors": 2,
            "n_load_bearing_errors": 1,
            "load_bearing_mask": [True, True, False],
            "failed_load_bearing": [(0, "Calculation error")],
        }
        record = _make_run_record(results=[result])
        appendix = _section_technical_appendix(record)
        assert "Reasoning Integrity" in appendix
        assert "brittle" in appendix

    def test_study_forensics_detail(self):
        result = _make_evaluated_result(
            failures=[_make_failure("overclaiming", "major", "Claims exceed evidence")],
            study_forensics={
                "is_study_forensics": True,
                "detected_label": "overclaim",
                "gold_label": "overclaim",
                "label_correct": True,
                "matched_findings": ["overclaiming_language"],
                "missed_findings": [],
                "extra_findings": ["hedge_weakness"],
            }
        )
        record = _make_run_record(results=[result])
        findings = _section_key_findings(record)
        assert "Study Forensics" in findings

    def test_mechanism_analysis_in_appendix(self):
        result = _make_evaluated_result()
        result.mechanism_analysis = MechanismAnalysis(
            concept_named=True,
            mechanism_described=True,
            mechanism_grounded_to_case=False,
            named_concepts=["Simpson's paradox"],
            missing_elements=["case-specific grounding"],
        )
        record = _make_run_record(results=[result])
        appendix = _section_technical_appendix(record)
        assert "concept named" in appendix
        assert "case-specific grounding" in appendix

    def test_grounding_audit_in_appendix(self):
        result = _make_evaluated_result()
        result.grounding_audit = GroundingAudit(
            total_conclusion_claims=5,
            directly_supported=3,
            indirectly_supported=1,
            unsupported=1,
            contradicted=0,
        )
        record = _make_run_record(results=[result])
        appendix = _section_technical_appendix(record)
        assert "3 direct" in appendix
        assert "1 unsupported" in appendix


# ---------------------------------------------------------------------------
# 10. HTML-specific tests
# ---------------------------------------------------------------------------

class TestHTMLSpecific:
    def test_html_escapes_special_chars(self):
        task = _make_task(title="Test <script>alert('xss')</script>")
        record = _make_run_record(task=task)
        html = generate_html_report(record)
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_html_has_print_styles(self):
        record = _make_run_record()
        html = generate_html_report(record)
        assert "@media print" in html
        assert "@page" in html

    def test_html_responsive(self):
        record = _make_run_record()
        html = generate_html_report(record)
        assert "viewport" in html

    def test_html_with_failures(self):
        failures = [
            _make_failure("wrong_answer", "critical", "Answer incorrect"),
            _make_failure("overclaiming", "major", "Claims exceed evidence"),
        ]
        result = _make_evaluated_result(failures=failures)
        record = _make_run_record(results=[result])
        html = generate_html_report(record)
        assert "Answer incorrect" in html or "Incorrect answer" in html


# ---------------------------------------------------------------------------
# 11. Real run file integration test
# ---------------------------------------------------------------------------

class TestRealRunIntegration:
    """Exercise JSON roundtrip integration with tracked synthetic builders only."""

    @pytest.fixture
    def serialized_synthetic_run(self):
        return _make_run_record().model_dump_json()

    def test_serialized_synthetic_run_generates_report(self, serialized_synthetic_run):
        record = RunRecord.model_validate_json(serialized_synthetic_run)
        report = generate_client_report(record)
        assert isinstance(report, str)
        assert len(report) > 200
        assert "Executive Summary" in report

    def test_serialized_synthetic_run_generates_html(self, serialized_synthetic_run):
        record = RunRecord.model_validate_json(serialized_synthetic_run)
        html = generate_html_report(record)
        assert "<!DOCTYPE html>" in html
        assert len(html) > 500
