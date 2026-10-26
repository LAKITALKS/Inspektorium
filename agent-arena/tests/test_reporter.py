"""Tests for agent-arena v0.4 reporter — forensic dossier."""

from agent_arena.reporter import generate_report
from agent_arena.schemas import (
    AgentResponse,
    AgentResult,
    ConsistencyFinding,
    DiagnosticScores,
    Difficulty,
    EvaluatedResult,
    EvidenceRole,
    EvidenceSpan,
    FailureCategory,
    FailureInstance,
    FailureSeverity,
    ForensicFlag,
    ReasoningGraph,
    RunRecord,
    ScoredDimension,
    Task,
    TaskType,
)


def _make_task() -> Task:
    return Task(
        id="test-001", title="Test Task", domain="test",
        difficulty=Difficulty.MEDIUM, task_type=TaskType.CLOSED_WITH_REASONING,
        prompt="test",
    )


def _make_evaluated_result(provider: str = "TestAgent", total_frac: float = 0.75) -> EvaluatedResult:
    parsed = AgentResponse(
        final_answer="The answer is 42",
        steps=["Step 1", "Step 2"],
        assumptions=["Assumption 1"],
        key_claims=["Claim 1"],
        confidence=0.85,
        uncertainties=["Some uncertainty"],
        alternative_hypotheses=["Alternative — rejected because X"],
        self_check=["Verified arithmetic: 2+2=4"],
    )
    result = AgentResult(
        provider=provider, model="test-model",
        raw_output="", parsed=parsed, parse_ok=True, latency_ms=5000,
    )
    scores = DiagnosticScores(
        correctness=total_frac, support_strength=total_frac,
        structural_reasoning=total_frac, assumption_discipline=total_frac,
        uncertainty_handling=total_frac, alternative_hypothesis_quality=total_frac,
        self_monitoring_quality=total_frac, insight_depth=total_frac,
        mechanism_quality=total_frac, communication_efficiency=total_frac,
    )
    return EvaluatedResult(
        agent_result=result, scores=scores,
        scored_dimensions=[
            ScoredDimension(
                dimension="correctness", raw_score=total_frac, weight=20,
                weighted_score=total_frac * 20,
                evidence=[
                    EvidenceSpan(text="The answer is 42", source_field="final_answer",
                                 role=EvidenceRole.SUPPORTING),
                ],
            ),
            ScoredDimension(
                dimension="support_strength", raw_score=total_frac, weight=10,
                weighted_score=total_frac * 10,
                evidence=[
                    EvidenceSpan(text="Step 1", source_field="steps[0]",
                                 role=EvidenceRole.SUPPORTING),
                    EvidenceSpan(text="Missing link", source_field="(gap)",
                                 role=EvidenceRole.MISSING_EXPECTED,
                                 relevance="Expected grounding not found"),
                ],
            ),
        ],
        consistency_findings=[
            ConsistencyFinding(
                check_type="confidence_uncertainty", status="warning",
                description="High confidence with uncertainties",
                evidence=[EvidenceSpan(text="confidence: 0.85", source_field="confidence")],
            ),
        ],
        failures=[
            FailureInstance(
                category=FailureCategory.CONFIDENCE_MISMATCH.value,
                severity=FailureSeverity.MINOR.value,
                description="Minor confidence issue",
            ),
        ],
        forensic_flags=[
            ForensicFlag(
                flag_type="calibration_gap",
                description="Calibration gap detected",
                evidence=[EvidenceSpan(text="0.85", source_field="confidence")],
                severity="minor",
            ),
        ],
        reasoning_graph=ReasoningGraph(),
    )


class TestReporter:
    def test_generates_report(self):
        record = RunRecord(
            run_id="test-run", task=_make_task(),
            results=[_make_evaluated_result("Agent1", 0.8), _make_evaluated_result("Agent2", 0.7)],
        )
        report = generate_report(record)
        assert "# Forensic Dossier" in report
        assert "Agent1" in report

    def test_report_has_v04_sections(self):
        record = RunRecord(
            run_id="test-run", task=_make_task(),
            results=[_make_evaluated_result("A1", 0.8), _make_evaluated_result("A2", 0.7)],
        )
        report = generate_report(record)
        assert "## Forensic Flags" in report
        assert "## Evidence Map" in report
        assert "## Comparative Forensics" in report

    def test_evidence_roles_in_report(self):
        record = RunRecord(
            run_id="test-run", task=_make_task(),
            results=[_make_evaluated_result()],
        )
        report = generate_report(record)
        assert "(+)" in report  # supporting evidence
        assert "(?)" in report  # missing expected evidence

    def test_forensic_flags_content(self):
        record = RunRecord(
            run_id="test-run", task=_make_task(),
            results=[_make_evaluated_result()],
        )
        report = generate_report(record)
        assert "calibration_gap" in report

    def test_single_agent_no_crash(self):
        record = RunRecord(
            run_id="test-run", task=_make_task(),
            results=[_make_evaluated_result()],
        )
        report = generate_report(record)
        assert "## Final Verdict" in report

    def test_empty_results_no_crash(self):
        record = RunRecord(
            run_id="test-run", task=_make_task(), results=[],
        )
        report = generate_report(record)
        assert "Forensic Dossier" in report

    def test_comparative_forensics_needs_two_agents(self):
        record = RunRecord(
            run_id="test-run", task=_make_task(),
            results=[_make_evaluated_result()],
        )
        report = generate_report(record)
        assert "## Comparative Forensics" not in report

    def test_omits_empty_sections(self):
        """Sections with no content should be omitted."""
        er = _make_evaluated_result()
        er.failures = []
        er.consistency_findings = []
        er.forensic_flags = []
        record = RunRecord(
            run_id="test-run", task=_make_task(), results=[er],
        )
        report = generate_report(record)
        assert "## Failure Analysis" not in report
