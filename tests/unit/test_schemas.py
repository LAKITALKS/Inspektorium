"""Tests of the Inspektorium audit runtime schemas."""

from inspektorium.audit.schemas import (
    DIAGNOSTIC_WEIGHTS,
    DiagnosticScores,
    EvidenceRole,
    EvidenceSpan,
    FailureCategory,
    FailureSeverity,
    ForensicFlag,
    NormalizedClaim,
    ReasoningGraph,
    Task,
    TaskType,
    Difficulty,
)


def test_evidence_span_with_role():
    ev = EvidenceSpan(
        text="hello", source_field="steps[0]", role=EvidenceRole.SUPPORTING
    )
    assert ev.role == EvidenceRole.SUPPORTING


def test_evidence_span_default_role():
    ev = EvidenceSpan(text="hello", source_field="steps[0]")
    assert ev.role == EvidenceRole.SUPPORTING


def test_evidence_roles():
    assert EvidenceRole.SUPPORTING.value == "supporting"
    assert EvidenceRole.WEAKENING.value == "weakening"
    assert EvidenceRole.CONTRADICTORY.value == "contradictory"
    assert EvidenceRole.MISSING_EXPECTED.value == "missing_expected"


def test_failure_severity_moderate():
    assert FailureSeverity.MODERATE.value == "moderate"


def test_new_failure_categories():
    assert FailureCategory.UNUSED_ASSUMPTION.value == "unused_assumption"
    assert FailureCategory.UNSTATED_ASSUMPTION.value == "unstated_assumption"
    assert FailureCategory.DECORATIVE_UNCERTAINTY.value == "decorative_uncertainty"
    assert FailureCategory.DECORATIVE_SELF_CHECK.value == "decorative_self_check"
    assert FailureCategory.MECHANISM_GAP.value == "mechanism_gap"
    assert FailureCategory.CLAIM_DRIFT.value == "claim_drift"
    assert (
        FailureCategory.WEAK_ALTERNATIVE_HYPOTHESIS.value
        == "weak_alternative_hypothesis"
    )
    assert FailureCategory.UNSUPPORTED_CONCLUSION.value == "unsupported_conclusion"
    assert FailureCategory.OVERVERBOSE_WITHOUT_GAIN.value == "oververbose_without_gain"
    assert FailureCategory.SHALLOW_PATTERN_MATCH.value == "shallow_pattern_match"


def test_forensic_flag():
    ff = ForensicFlag(
        flag_type="calibration_gap",
        description="High confidence with unresolved uncertainty",
        evidence=[EvidenceSpan(text="confidence: 0.95", source_field="confidence")],
        severity="minor",
    )
    assert ff.flag_type == "calibration_gap"
    assert len(ff.evidence) == 1


def test_normalized_claim():
    nc = NormalizedClaim(
        text="The rate is 30%",
        source_field="steps[0]",
        claim_role="assertion",
        used=True,
        addressed=True,
    )
    assert nc.claim_role == "assertion"


def test_reasoning_graph():
    rg = ReasoningGraph(
        unused_assumptions=[0],
        unaddressed_uncertainties=[1],
        conclusion_grounded=True,
        support_chain_length=3,
    )
    assert rg.conclusion_grounded
    assert len(rg.unused_assumptions) == 1


def test_diagnostic_weights_sum_100():
    assert sum(DIAGNOSTIC_WEIGHTS.values()) == 100


def test_diagnostic_scores_10_dimensions():
    scores = DiagnosticScores(
        correctness=1.0,
        support_strength=1.0,
        structural_reasoning=1.0,
        assumption_discipline=1.0,
        uncertainty_handling=1.0,
        alternative_hypothesis_quality=1.0,
        self_monitoring_quality=1.0,
        insight_depth=1.0,
        mechanism_quality=1.0,
        communication_efficiency=1.0,
    )
    assert scores.total == 100.0


def test_diagnostic_scores_zero():
    scores = DiagnosticScores()
    assert scores.total == 0.0


def test_task_new_fields():
    task = Task(
        id="t1",
        title="Test",
        domain="test",
        difficulty=Difficulty.HARD,
        task_type=TaskType.CLOSED_WITH_REASONING,
        prompt="test",
        diagnostic_focus="Can the agent do X?",
        expected_mechanism_terms=["term1", "term2"],
        fragile_points=["may miss Y"],
        likely_shortcuts=["pattern match"],
        evaluator_notes="Notes here",
    )
    assert task.diagnostic_focus == "Can the agent do X?"
    assert len(task.expected_mechanism_terms) == 2


def test_evaluated_result_has_forensic_fields():
    from inspektorium.audit.schemas import EvaluatedResult, AgentResult

    er = EvaluatedResult(
        agent_result=AgentResult(provider="test"),
        forensic_flags=[ForensicFlag(flag_type="test", description="test")],
        reasoning_graph=ReasoningGraph(),
    )
    assert len(er.forensic_flags) == 1
    assert er.reasoning_graph is not None
