"""Core data models for agent-arena v0.5 — forensic reasoning analysis engine."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TaskType(str, Enum):
    CLOSED_WITH_REASONING = "closed_with_reasoning"
    RUBRIC_BASED = "rubric_based"
    FORECASTING_DECISION = "forecasting_decision"  # v0.5
    STUDY_FORENSICS = "study_forensics"  # v0.6: study/claim forensic analysis


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class FailureSeverity(str, Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MODERATE = "moderate"
    MINOR = "minor"
    STYLISTIC = "stylistic"


class FailureCategory(str, Enum):
    # Core reasoning failures
    WRONG_ANSWER = "wrong_answer"
    ARITHMETIC_ERROR = "arithmetic_error"
    LOGIC_ERROR = "logic_error"
    MISSING_KEY_STEP = "missing_key_step"
    UNJUSTIFIED_LEAP = "unjustified_leap"
    UNSUPPORTED_CONCLUSION = "unsupported_conclusion"
    CLAIM_DRIFT = "claim_drift"
    OVERCOMPRESSED_REASONING = "overcompressed_reasoning"

    # Insight / depth failures
    MISSED_KEY_INSIGHT = "missed_key_insight"
    SUPERFICIAL_TREATMENT = "superficial_treatment"
    PATTERN_MATCHING = "pattern_matching"
    MECHANISM_GAP = "mechanism_gap"
    SHALLOW_PATTERN_MATCH = "shallow_pattern_match"

    # Self-monitoring failures
    SELF_CONTRADICTION = "self_contradiction"
    CONFIDENCE_MISMATCH = "confidence_mismatch"
    STEP_ANSWER_MISMATCH = "step_answer_mismatch"
    DECORATIVE_SELF_CHECK = "decorative_self_check"
    WEAK_ALTERNATIVE_HYPOTHESIS = "weak_alternative_hypothesis"

    # Discipline failures
    NO_ASSUMPTIONS_STATED = "no_assumptions_stated"
    UNUSED_ASSUMPTION = "unused_assumption"
    UNSTATED_ASSUMPTION = "unstated_assumption"
    DECORATIVE_UNCERTAINTY = "decorative_uncertainty"
    IGNORED_UNCERTAINTY = "ignored_uncertainty"
    OVERCLAIMING = "overclaiming"

    # Numeric / claim consistency failures (v0.4.1)
    VERBAL_NUMERIC_CONTRADICTION = "verbal_numeric_contradiction"
    LOCAL_FACT_REVERSAL = "local_fact_reversal"
    MISSTATED_COMPARISON = "misstated_comparison"
    UNSUPPORTED_COMPARATIVE_CONCLUSION = "unsupported_comparative_conclusion"
    FAILED_SELF_AUDIT = "failed_self_audit"
    MISSED_OWN_ERROR = "missed_own_error"
    NAMED_NOT_EXPLAINED = "named_not_explained"

    # Reasoning integrity failures (v0.4.3)
    INTERMEDIATE_NUMERIC_ERROR = "intermediate_numeric_error"
    UNSUPPORTED_INTERMEDIATE_STEP = "unsupported_intermediate_step"
    RIGHT_ANSWER_WRONG_REASONING = "right_answer_wrong_reasoning"
    ACCIDENTAL_CORRECTNESS = "accidental_correctness"

    # Forecasting / uncertainty failures (v0.5)
    FALSE_EDGE_DETECTION = "false_edge_detection"
    OVERCONFIDENT_FORECAST = "overconfident_forecast"
    RULE_MISREAD = "rule_misread"
    BASE_RATE_OMISSION = "base_rate_omission"
    WEAK_NO_TRADE_JUSTIFICATION = "weak_no_trade_justification"
    NARRATIVE_OVERREACH = "narrative_overreach"
    INSUFFICIENT_SKEPTICISM = "insufficient_skepticism"
    SHRINKAGE_FAILURE = "shrinkage_failure"
    OPPORTUNITY_MISCLASSIFICATION = "opportunity_misclassification"
    CORRECT_DIRECTION_WEAK_CALIBRATION = "correct_direction_weak_calibration"
    ABSTENTION_WITHOUT_CAUSE = "abstention_without_cause"

    # Communication failures
    REDUNDANT_CONTENT = "redundant_content"
    PADDING = "padding"
    OVERVERBOSE_WITHOUT_GAIN = "oververbose_without_gain"


class EvidenceRole(str, Enum):
    """Classification of how an evidence span relates to the score."""
    SUPPORTING = "supporting"
    WEAKENING = "weakening"
    CONTRADICTORY = "contradictory"
    MISSING_EXPECTED = "missing_expected"


# ---------------------------------------------------------------------------
# v0.4.2: Unified confidence label mapping
# ---------------------------------------------------------------------------
# Single source of truth for confidence classification across the engine.
# Both evaluator (FailureInstance) and consistency (ConsistencyFinding) use this.

# FailureCategory → confidence level
FAILURE_CONFIDENCE_MAP: dict[str, str] = {
    # HIGH CONFIDENCE — deterministic or claim-checker-backed
    FailureCategory.WRONG_ANSWER.value: "HIGH CONFIDENCE",
    FailureCategory.VERBAL_NUMERIC_CONTRADICTION.value: "HIGH CONFIDENCE",
    FailureCategory.FAILED_SELF_AUDIT.value: "HIGH CONFIDENCE",
    FailureCategory.LOCAL_FACT_REVERSAL.value: "HIGH CONFIDENCE",
    FailureCategory.MISSTATED_COMPARISON.value: "HIGH CONFIDENCE",
    FailureCategory.INTERMEDIATE_NUMERIC_ERROR.value: "HIGH CONFIDENCE",
    # MEDIUM CONFIDENCE — grounded heuristic
    FailureCategory.RIGHT_ANSWER_WRONG_REASONING.value: "MEDIUM CONFIDENCE",
    FailureCategory.UNSUPPORTED_INTERMEDIATE_STEP.value: "MEDIUM CONFIDENCE",
    FailureCategory.ACCIDENTAL_CORRECTNESS.value: "MEDIUM CONFIDENCE",
    FailureCategory.NAMED_NOT_EXPLAINED.value: "MEDIUM CONFIDENCE",
    FailureCategory.MECHANISM_GAP.value: "MEDIUM CONFIDENCE",
    FailureCategory.MISSED_KEY_INSIGHT.value: "MEDIUM CONFIDENCE",
    FailureCategory.CONFIDENCE_MISMATCH.value: "MEDIUM CONFIDENCE",
    FailureCategory.SELF_CONTRADICTION.value: "MEDIUM CONFIDENCE",
    FailureCategory.STEP_ANSWER_MISMATCH.value: "MEDIUM CONFIDENCE",
    FailureCategory.UNSUPPORTED_CONCLUSION.value: "MEDIUM CONFIDENCE",
    # v0.5: Forecasting failures — mostly MEDIUM (heuristic-based)
    FailureCategory.OVERCONFIDENT_FORECAST.value: "MEDIUM CONFIDENCE",
    FailureCategory.BASE_RATE_OMISSION.value: "MEDIUM CONFIDENCE",
    FailureCategory.RULE_MISREAD.value: "MEDIUM CONFIDENCE",
    FailureCategory.SHRINKAGE_FAILURE.value: "MEDIUM CONFIDENCE",
    FailureCategory.NARRATIVE_OVERREACH.value: "HEURISTIC",
    FailureCategory.FALSE_EDGE_DETECTION.value: "HEURISTIC",
    FailureCategory.WEAK_NO_TRADE_JUSTIFICATION.value: "MEDIUM CONFIDENCE",
    FailureCategory.INSUFFICIENT_SKEPTICISM.value: "HEURISTIC",
    FailureCategory.ABSTENTION_WITHOUT_CAUSE.value: "MEDIUM CONFIDENCE",
    FailureCategory.OPPORTUNITY_MISCLASSIFICATION.value: "HEURISTIC",
    FailureCategory.CORRECT_DIRECTION_WEAK_CALIBRATION.value: "HEURISTIC",
}
# Everything not listed → HEURISTIC

# ConsistencyFinding check_type → confidence level
CONSISTENCY_CONFIDENCE_MAP: dict[str, str] = {
    # HIGH CONFIDENCE — numeric verification backed
    "numeric_verbal_reversal": "HIGH CONFIDENCE",
    "failed_self_audit": "HIGH CONFIDENCE",
    # MEDIUM CONFIDENCE — grounded heuristic
    "mechanism_gap": "MEDIUM CONFIDENCE",
    "contradiction": "MEDIUM CONFIDENCE",
    "assumption_reasoning": "MEDIUM CONFIDENCE",
    "confidence_uncertainty": "MEDIUM CONFIDENCE",
    "self_correction": "MEDIUM CONFIDENCE",
}
# Everything not listed → HEURISTIC


def get_confidence_label(key: str, mapping: dict[str, str]) -> str:
    """Look up confidence label, defaulting to HEURISTIC."""
    return mapping.get(key, "HEURISTIC")


# ---------------------------------------------------------------------------
# Evidence layer
# ---------------------------------------------------------------------------

class EvidenceSpan(BaseModel):
    """A concrete text passage that supports an evaluation finding."""
    text: str
    source_field: str  # e.g. "steps[2]", "final_answer", "assumptions[1]"
    char_start: int | None = None
    char_end: int | None = None
    claim_type: str | None = None  # "assertion", "correction", "rejection", etc.
    relevance: str = ""  # why this span matters
    role: EvidenceRole = EvidenceRole.SUPPORTING


class FailureInstance(BaseModel):
    """A structured failure finding with evidence."""
    category: str  # FailureCategory value
    severity: str  # FailureSeverity value
    description: str
    evidence: list[EvidenceSpan] = Field(default_factory=list)
    impact_on_score: str = ""  # which dimension(s) affected
    # v0.4.2: confidence label for the finding
    confidence: str = ""  # "HIGH CONFIDENCE", "MEDIUM CONFIDENCE", "HEURISTIC"


class ConsistencyFinding(BaseModel):
    """A consistency check result with evidence."""
    check_type: str
    status: str  # "pass", "warning", "fail"
    description: str
    evidence: list[EvidenceSpan] = Field(default_factory=list)
    # v0.4.2: confidence label for the finding
    confidence: str = ""  # "HIGH CONFIDENCE", "MEDIUM CONFIDENCE", "HEURISTIC"


class ScoredDimension(BaseModel):
    """A single evaluation dimension with score and evidence."""
    dimension: str
    raw_score: float  # 0.0–1.0
    weight: int
    weighted_score: float
    evidence: list[EvidenceSpan] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class ForensicFlag(BaseModel):
    """A latent risk signal detected during forensic analysis."""
    flag_type: str  # e.g. "calibration_gap", "unsupported_leap", "pattern_match_suspect"
    description: str
    evidence: list[EvidenceSpan] = Field(default_factory=list)
    severity: str = "minor"  # critical, major, moderate, minor, stylistic


# ---------------------------------------------------------------------------
# Claim checking models (v0.4.1)
# ---------------------------------------------------------------------------

class ClaimTruthStatus(str, Enum):
    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    UNRESOLVED = "unresolved"


class NumericFact(BaseModel):
    """A numeric fact extracted from text."""
    entity: str  # e.g. "men", "women", "Engineering"
    metric: str  # e.g. "admission_rate", "count"
    value: float
    source_field: str  # where it was found
    context: str = ""  # e.g. "engineering", "arts", "overall" — grouping key


class ComparativeClaim(BaseModel):
    """A comparative verbal claim extracted from text."""
    subject: str  # e.g. "men"
    object: str  # e.g. "women"
    relation: str  # e.g. "higher_than", "lower_than", "favors"
    metric: str  # e.g. "admission rate"
    source_field: str
    source_text: str  # original text


class ClaimCheckResult(BaseModel):
    """Result of checking a comparative claim against numeric facts."""
    claim: ComparativeClaim
    truth_status: ClaimTruthStatus
    explanation: str
    supporting_facts: list[NumericFact] = Field(default_factory=list)
    contradicting_facts: list[NumericFact] = Field(default_factory=list)


class MechanismAnalysis(BaseModel):
    """Analysis of mechanism quality in agent response."""
    concept_named: bool = False
    mechanism_described: bool = False
    mechanism_grounded_to_case: bool = False
    named_concepts: list[str] = Field(default_factory=list)
    mechanism_sentences: list[str] = Field(default_factory=list)
    grounding_sentences: list[str] = Field(default_factory=list)
    missing_elements: list[str] = Field(default_factory=list)


class GroundingAudit(BaseModel):
    """Audit of how well conclusions are grounded in reasoning."""
    total_conclusion_claims: int = 0
    directly_supported: int = 0
    indirectly_supported: int = 0
    unsupported: int = 0
    contradicted: int = 0
    support_paths: list[str] = Field(default_factory=list)  # human-readable descriptions
    unsupported_claims: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Reasoning graph models
# ---------------------------------------------------------------------------

class NormalizedClaim(BaseModel):
    """A single extracted claim from an agent response."""
    text: str
    source_field: str  # "steps[0]", "assumptions[2]", "final_answer", etc.
    claim_role: str  # "assertion", "assumption", "challenge", "conclusion", "check", "claim"
    used: bool = True  # whether this claim is referenced elsewhere
    addressed: bool = True  # whether challenges/uncertainties are later addressed


class ClaimRelation(BaseModel):
    """A relationship between two claims."""
    source_idx: int
    target_idx: int
    relation: str  # "supports", "contradicts", "refines", "assumes", "checks"
    strength: float = 1.0  # 0.0–1.0


class ReasoningGraph(BaseModel):
    """Lightweight reasoning graph extracted from an agent response."""
    claims: list[NormalizedClaim] = Field(default_factory=list)
    relations: list[ClaimRelation] = Field(default_factory=list)

    # Summary metrics
    unused_assumptions: list[int] = Field(default_factory=list)  # indices into claims
    unaddressed_uncertainties: list[int] = Field(default_factory=list)
    unsupported_conclusions: list[int] = Field(default_factory=list)
    fluff_self_checks: list[int] = Field(default_factory=list)
    support_chain_length: int = 0
    conclusion_grounded: bool = False


# ---------------------------------------------------------------------------
# Task schema
# ---------------------------------------------------------------------------

class KeyInsight(BaseModel):
    keyword: str
    variants: list[str] = Field(default_factory=list)
    functional_descriptions: list[str] = Field(default_factory=list)


class RubricItem(BaseModel):
    criterion: str
    points: int
    description: str = ""
    variants: list[str] = Field(default_factory=list)


class EvaluationConfig(BaseModel):
    method: str = "auto"
    answer_match: str = "exact"
    tolerance: float | None = None


class ExpectedFinding(BaseModel):
    """An expected forensic finding for study forensics tasks."""
    finding: str           # e.g. "correlation_as_causation", "evidence_matches_claim"
    severity: str = "moderate"   # minor, moderate, major
    confidence: str = "medium"   # low, medium, high


class GoldEvidenceSpan(BaseModel):
    """A gold-standard evidence span for study forensics validation."""
    span: str
    why_it_matters: str = ""
    supports_finding: str = ""


class Task(BaseModel):
    id: str
    title: str
    domain: str
    difficulty: Difficulty
    task_type: TaskType
    prompt: str
    context: str = ""
    expected_answer: str | None = None
    reference_solution: str | None = None
    rubric: list[RubricItem] = Field(default_factory=list)
    evaluation: EvaluationConfig = Field(default_factory=EvaluationConfig)
    output_schema: str = "structured"
    origin: str | None = None
    # Case lifecycle / intake status (see docs/case_intake_policy.md).
    # Retired cases are kept and remain loadable but are excluded from active
    # discovery/metrics by default. Both optional & defaulted for back-compat.
    status: str | None = None                        # e.g. "retired"
    excluded_from_active_metrics: bool = False
    key_insights: list[str | KeyInsight] = Field(default_factory=list)
    common_errors: list[str] = Field(default_factory=list)
    task_family: str | None = None
    trap_type: str | None = None
    ambiguity_level: str | None = None
    expected_failure_modes: list[str] = Field(default_factory=list)
    discriminative_dimensions: list[str] = Field(default_factory=list)
    # v0.4 diagnostic metadata
    diagnostic_focus: str | None = None
    expected_mechanism_terms: list[str] = Field(default_factory=list)
    fragile_points: list[str] = Field(default_factory=list)
    likely_shortcuts: list[str] = Field(default_factory=list)
    evaluator_notes: str | None = None
    # v0.5: Forecasting task metadata
    base_rate: float | None = None                   # known base rate (0.0–1.0)
    resolution_rule: str | None = None               # how the outcome is determined
    correct_decision: str | None = None              # "forecast", "watch", "no_trade", "abstain"
    expected_probability_range: tuple[float, float] | None = None  # (low, high) plausible range
    # v0.6: Study forensics metadata
    gold_label: str | None = None                    # "solid", "overclaim", etc.
    gold_summary: str | None = None                  # ground truth explanation
    expected_findings: list[ExpectedFinding] = Field(default_factory=list)
    gold_evidence_spans: list[GoldEvidenceSpan] = Field(default_factory=list)
    # v0.6.2: Gold standard calibration fields
    gold_confidence: str | None = None               # "high", "medium", "low" — curator confidence in the gold label
    gold_justification: str | None = None            # explicit reasoning for why this gold label was chosen
    gold_alternative_reading: str | None = None      # plausible alternative label with reasoning
    gold_case_type: str | None = None                # "clear" or "borderline"
    curator_notes: str | None = None                 # free-text notes for dataset maintainers

    def get_key_insights(self) -> list[KeyInsight]:
        out = []
        for item in self.key_insights:
            if isinstance(item, str):
                out.append(KeyInsight(keyword=item))
            else:
                out.append(item)
        return out


# ---------------------------------------------------------------------------
# Agent response schema
# ---------------------------------------------------------------------------

class AgentResponse(BaseModel):
    final_answer: str = ""
    assumptions: list[str] = Field(default_factory=list)
    steps: list[str] = Field(default_factory=list)
    alternative_hypotheses: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    self_check: list[str] = Field(default_factory=list)
    key_claims: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    # v0.5: Forecasting-specific response fields (optional, ignored for non-forecast tasks)
    probability_estimate: float | None = None      # 0.0–1.0
    decision_category: str = ""                     # "forecast", "watch", "no_trade", "abstain"
    base_rate_reference: str = ""                   # stated baseline/reference class
    key_drivers: list[str] = Field(default_factory=list)
    counterarguments: list[str] = Field(default_factory=list)
    edge_justification: str = ""                    # why the agent believes market/base is wrong
    shrinkage_rationale: str = ""                   # why the raw estimate was adjusted


class AgentResult(BaseModel):
    provider: str
    model: str = ""
    raw_output: str = ""
    parsed: AgentResponse | None = None
    parse_ok: bool = False
    error: str | None = None
    latency_ms: int = 0
    # v0.6.3 (Phase 2): provider response metadata. All optional/defaulted for
    # backward compatibility with existing run records and constructors.
    finish_reason: str | None = None
    usage: dict | None = None
    error_type: str | None = None


# ---------------------------------------------------------------------------
# Diagnostic scoring (10 dimensions for v0.4)
# ---------------------------------------------------------------------------

# v0.4.2: correctness raised from 20→30 to make wrong answers harder to mask
# with good structure. Other weights reduced proportionally.
DIAGNOSTIC_WEIGHTS = {
    "correctness": 30,
    "support_strength": 8,
    "structural_reasoning": 8,
    "assumption_discipline": 6,
    "uncertainty_handling": 6,
    "alternative_hypothesis_quality": 6,
    "self_monitoring_quality": 8,
    "insight_depth": 8,
    "mechanism_quality": 10,
    "communication_efficiency": 10,
}


class DiagnosticScores(BaseModel):
    correctness: float = 0.0
    support_strength: float = 0.0
    structural_reasoning: float = 0.0
    assumption_discipline: float = 0.0
    uncertainty_handling: float = 0.0
    alternative_hypothesis_quality: float = 0.0
    self_monitoring_quality: float = 0.0
    insight_depth: float = 0.0
    mechanism_quality: float = 0.0
    communication_efficiency: float = 0.0

    # v0.4.2: hard cap applied when a locally proven contradiction is detected.
    # Set by the evaluator; 0 means no cap.
    _score_cap: float = 0.0

    model_config = {"arbitrary_types_allowed": True}

    @property
    def total(self) -> float:
        s = 0.0
        for dim, weight in DIAGNOSTIC_WEIGHTS.items():
            s += getattr(self, dim) * weight
        raw = round(s, 1)
        if self._score_cap > 0:
            return min(raw, self._score_cap)
        return raw

    def weighted(self, dim: str) -> float:
        return round(getattr(self, dim) * DIAGNOSTIC_WEIGHTS[dim], 1)

    def as_weighted_dict(self) -> dict[str, float]:
        return {dim: self.weighted(dim) for dim in DIAGNOSTIC_WEIGHTS}


ScoreBreakdown = DiagnosticScores


# ---------------------------------------------------------------------------
# LLM Judge result
# ---------------------------------------------------------------------------

class JudgeClaimAudit(BaseModel):
    claim: str
    status: str  # "supported", "unsupported", "contradicted", "incomplete"
    evidence: str = ""
    confidence: float = 0.0


class JudgeResult(BaseModel):
    enabled: bool = False
    dimension_scores: dict[str, float] = Field(default_factory=dict)
    evidence_citations: list[str] = Field(default_factory=list)
    failure_modes: list[str] = Field(default_factory=list)
    claim_audit: list[JudgeClaimAudit] = Field(default_factory=list)
    comparative_note: str = ""
    judge_confidence: float = 0.0
    raw_output: str = ""


# ---------------------------------------------------------------------------
# Evaluated result (v0.4: forensic flags, reasoning graph)
# ---------------------------------------------------------------------------

class EvaluatedResult(BaseModel):
    agent_result: AgentResult
    scores: DiagnosticScores = Field(default_factory=DiagnosticScores)
    scored_dimensions: list[ScoredDimension] = Field(default_factory=list)
    failures: list[FailureInstance] = Field(default_factory=list)
    consistency_findings: list[ConsistencyFinding] = Field(default_factory=list)
    forensic_flags: list[ForensicFlag] = Field(default_factory=list)
    reasoning_graph: ReasoningGraph | None = None
    judge_result: JudgeResult = Field(default_factory=JudgeResult)
    # v0.4.1 forensic hardening
    claim_check_results: list[ClaimCheckResult] = Field(default_factory=list)
    mechanism_analysis: MechanismAnalysis | None = None
    grounding_audit: GroundingAudit | None = None
    # v0.4.3: reasoning integrity
    step_check_results: list[Any] = Field(default_factory=list)  # list[StepCheckResult]
    reasoning_integrity: dict[str, Any] = Field(default_factory=dict)
    # v0.5: forecast integrity
    forecast_integrity: dict[str, Any] = Field(default_factory=dict)
    # v0.6: study forensics results
    study_forensics: dict[str, Any] = Field(default_factory=dict)
    # legacy compat
    failure_modes: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class RunRecord(BaseModel):
    run_id: str
    task: Task
    results: list[EvaluatedResult] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# v0.6: Journal, Outcome, Postmortem, Profile schemas
# ---------------------------------------------------------------------------

class RunJournalEntry(BaseModel):
    """Flat, persistable summary of a single agent's result in a run."""
    run_id: str
    timestamp: str
    task_id: str
    task_family: str = ""
    task_type: str = ""
    agent_id: str              # provider or provider:model
    model: str = ""
    total_score: float = 0.0
    correctness: float = 0.0
    support_strength: float = 0.0
    structural_reasoning: float = 0.0
    insight_depth: float = 0.0
    mechanism_quality: float = 0.0
    self_monitoring_quality: float = 0.0
    failure_categories: list[str] = Field(default_factory=list)
    forensic_flag_types: list[str] = Field(default_factory=list)
    reasoning_integrity_class: str = ""    # well_supported / brittle / accidental
    decision_category: str = ""            # forecast / watch / no_trade / abstain
    probability_estimate: float | None = None
    confidence: float = 0.0
    final_answer: str = ""
    n_contradictions: int = 0
    n_intermediate_errors: int = 0


class OutcomeRecord(BaseModel):
    """Outcome attached to a run+task after resolution."""
    run_id: str
    task_id: str
    agent_id: str
    resolved_outcome: str          # "yes", "no", "correct", "incorrect", etc.
    was_correct: bool | None = None
    decision_quality: str = ""     # "good_call", "bad_call", "lucky", "justified_miss"
    notes: str = ""
    resolution_timestamp: str = ""


class PostmortemFinding(BaseModel):
    """A single causal finding from a postmortem."""
    finding_type: str       # "causal_failure", "contributing_factor", "mitigating_factor"
    category: str           # FailureCategory value or forensic flag type
    description: str
    severity: str = "moderate"
    confidence: str = "MEDIUM CONFIDENCE"


class PostmortemReport(BaseModel):
    """Forensic postmortem combining run data with outcome."""
    run_id: str
    task_id: str
    agent_id: str
    outcome: OutcomeRecord
    was_correct: bool | None = None
    reasoning_integrity: str = ""           # well_supported / brittle / accidental
    decision_category: str = ""
    total_score: float = 0.0
    probable_causal_failures: list[PostmortemFinding] = Field(default_factory=list)
    contributing_factors: list[PostmortemFinding] = Field(default_factory=list)
    mitigating_factors: list[PostmortemFinding] = Field(default_factory=list)
    lessons: list[str] = Field(default_factory=list)
    verdict: str = ""   # "correct and well-supported", "correct but brittle", "wrong due to X"


class PatternCluster(BaseModel):
    """A recurring pattern detected across multiple runs."""
    pattern_type: str        # "recurring_failure", "recurring_flag", "forecast_bias", etc.
    category: str            # the specific failure/flag/dimension
    occurrences: int
    total_runs: int
    frequency: float         # occurrences / total_runs
    affected_tasks: list[str] = Field(default_factory=list)
    description: str = ""


class AgentProfile(BaseModel):
    """Aggregated forensic profile for an agent across runs."""
    agent_id: str
    model: str = ""
    n_runs: int = 0
    avg_total_score: float = 0.0
    strongest_dimension: str = ""
    weakest_dimension: str = ""
    recurring_failures: list[PatternCluster] = Field(default_factory=list)
    recurring_flags: list[PatternCluster] = Field(default_factory=list)
    # Forecast-specific
    avg_probability_estimate: float | None = None
    overconfidence_rate: float = 0.0       # fraction of runs with OVERCONFIDENT_FORECAST
    no_trade_quality: str = ""             # "mostly_justified" / "mostly_weak" / "mixed"
    base_rate_awareness: str = ""          # "consistently_uses" / "sometimes_ignores" / "ignores"
    # Integrity
    accidental_correctness_rate: float = 0.0
    brittleness_rate: float = 0.0
    contradiction_rate: float = 0.0


class TrendSnapshot(BaseModel):
    """Score trend for an agent over time."""
    agent_id: str
    dimension: str           # "total_score" or a specific dimension name
    timestamps: list[str] = Field(default_factory=list)
    values: list[float] = Field(default_factory=list)
    trend_direction: str = ""  # "improving", "declining", "stable", "insufficient_data"
    delta: float = 0.0         # latest - earliest (or windowed)


# ---------------------------------------------------------------------------
# v0.6.6: Gen 1 Insights schemas — meta-analysis layer
# ---------------------------------------------------------------------------

class CountedItem(BaseModel):
    """A category/type with occurrence count and frequency."""
    name: str
    count: int
    total: int
    frequency: float          # count / total


class FailureSummary(BaseModel):
    """Aggregated failure mode analysis across runs."""
    top_overall: list[CountedItem] = Field(default_factory=list)
    by_family: dict[str, list[CountedItem]] = Field(default_factory=dict)
    by_model: dict[str, list[CountedItem]] = Field(default_factory=dict)


class FlagSummary(BaseModel):
    """Aggregated forensic flag analysis across runs."""
    top_overall: list[CountedItem] = Field(default_factory=list)
    by_family: dict[str, list[CountedItem]] = Field(default_factory=dict)
    by_model: dict[str, list[CountedItem]] = Field(default_factory=dict)


class LabelConfusion(BaseModel):
    """Confusion matrix entry for label detection."""
    gold_label: str
    detected_label: str
    count: int
    models: list[str] = Field(default_factory=list)


class ModelInsightProfile(BaseModel):
    """Per-model forensic insight profile."""
    model: str
    n_runs: int = 0
    avg_score: float = 0.0
    dimension_averages: dict[str, float] = Field(default_factory=dict)
    strongest_dimensions: list[str] = Field(default_factory=list)
    weakest_dimensions: list[str] = Field(default_factory=list)
    top_failures: list[CountedItem] = Field(default_factory=list)
    top_flags: list[CountedItem] = Field(default_factory=list)
    label_confusions: list[LabelConfusion] = Field(default_factory=list)
    tendencies: list[str] = Field(default_factory=list)
    integrity_rates: dict[str, float] = Field(default_factory=dict)


class CaseDisagreement(BaseModel):
    """A case where models disagree on classification."""
    task_id: str
    task_family: str = ""
    n_runs: int = 0
    labels_produced: dict[str, int] = Field(default_factory=dict)
    models_by_label: dict[str, list[str]] = Field(default_factory=dict)
    disagreement_score: float = 0.0  # 0 = unanimous, 1 = max entropy
    is_borderline_candidate: bool = False


class DisagreementSummary(BaseModel):
    """Cross-model disagreement analysis."""
    cases: list[CaseDisagreement] = Field(default_factory=list)
    most_contentious_families: list[CountedItem] = Field(default_factory=list)


class CategoryMaturitySummary(BaseModel):
    """Stability and readiness assessment for a task category."""
    category: str
    n_cases: int = 0
    n_runs: int = 0
    avg_score: float = 0.0
    correctness_rate: float = 0.0
    disagreement_rate: float = 0.0
    maturity: str = ""        # "mature", "developing", "unstable"


class BorderlineCandidateSignal(BaseModel):
    """Signal that a case may need gold label review."""
    task_id: str
    task_family: str = ""
    reason: str = ""
    confidence: str = ""      # "high", "medium", "low"
    evidence: list[str] = Field(default_factory=list)


class InsightsReport(BaseModel):
    """Top-level Gen 1 Insights report — transparent meta-analysis."""
    generated_at: str = ""
    n_runs: int = 0
    n_tasks: int = 0
    n_models: int = 0
    failure_summary: FailureSummary = Field(default_factory=FailureSummary)
    flag_summary: FlagSummary = Field(default_factory=FlagSummary)
    model_profiles: list[ModelInsightProfile] = Field(default_factory=list)
    disagreement_summary: DisagreementSummary = Field(default_factory=DisagreementSummary)
    category_maturity: list[CategoryMaturitySummary] = Field(default_factory=list)
    borderline_candidates: list[BorderlineCandidateSignal] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# v0.6.7: Gen 2 Calibrate schemas — proposal layer
# ---------------------------------------------------------------------------

class CalibrationProposal(BaseModel):
    """A single calibration suggestion. Suggest, don't mutate."""
    proposal_type: str         # fp_reduction | gold_review | category_refinement
                               # | model_confusion | data_gap
    target: str                # what this proposal is about (case id, category, phrase, model)
    target_kind: str = ""      # "case" | "category" | "trigger" | "model" | "threshold"
    reason: str = ""
    evidence_summary: str = ""
    confidence: str = ""       # "high" | "medium" | "low" | "heuristic"
    strength: float = 0.0      # 0.0-1.0, how strong the signal is
    recommended_action: str = ""
    affected_cases: list[str] = Field(default_factory=list)
    affected_models: list[str] = Field(default_factory=list)


class CalibrationReport(BaseModel):
    """Top-level Gen 2 Calibrate report — proposals only, no mutations."""
    generated_at: str = ""
    n_entries_analyzed: int = 0
    n_proposals: int = 0
    fp_reduction_candidates: list[CalibrationProposal] = Field(default_factory=list)
    gold_review_candidates: list[CalibrationProposal] = Field(default_factory=list)
    category_refinement_candidates: list[CalibrationProposal] = Field(default_factory=list)
    model_confusion_candidates: list[CalibrationProposal] = Field(default_factory=list)
    data_gap_candidates: list[CalibrationProposal] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# v0.6.8: Gen 3 Caseforge schemas — case candidate generation
# ---------------------------------------------------------------------------

class ProposedFinding(BaseModel):
    """Proposed expected finding for a case candidate."""
    finding: str
    severity: str = "moderate"    # major / moderate / minor
    confidence: str = "medium"    # high / medium / low


class ProposedEvidenceSpan(BaseModel):
    """Proposed evidence span for a case candidate."""
    span: str
    why_it_matters: str = ""
    supports_finding: str = ""


class CaseCandidate(BaseModel):
    """A draft case generated by Caseforge. Pending human review."""

    # --- Identity ---
    candidate_id: str
    review_status: str = "pending_human_review"

    # --- Steering axes ---
    generation_mode: str = ""     # explicit_request / data_gap / calibration_signal
                                  # / confusion_probe / borderline_probe
    category_gap: str = ""        # which category is underrepresented
    shape_gap: str = ""           # which sub-shape is targeted
    borderline_need: str = ""     # "clear" or "borderline"
    model_confusion_target: str = ""  # e.g. "sonnet confuses corr with solid"

    # --- Task metadata ---
    target_family: str = ""
    target_shape: str = ""
    domain: str = "study_forensics"
    difficulty: str = "medium"
    trap_type: str = ""
    ambiguity_level: str = "low"

    # --- Input ---
    title: str = ""
    input_text: str = ""

    # --- Proposed gold layer ---
    proposed_gold_label: str = ""
    proposed_gold_confidence: str = "medium"
    proposed_gold_case_type: str = "clear"
    proposed_gold_summary: str = ""
    proposed_gold_justification: str = ""
    proposed_gold_alternative_reading: str = ""

    # --- Proposed findings & evidence ---
    proposed_expected_findings: list[ProposedFinding] = Field(default_factory=list)
    proposed_evidence_spans: list[ProposedEvidenceSpan] = Field(default_factory=list)

    # --- Rationale ---
    why_this_candidate_exists: str = ""
    which_gap_it_addresses: str = ""
    why_diagnostically_useful: str = ""
    curator_notes: str = ""


class CaseforgeReport(BaseModel):
    """Top-level Caseforge output — draft candidates, not final cases."""
    generated_at: str = ""
    n_candidates: int = 0
    candidates: list[CaseCandidate] = Field(default_factory=list)
    gaps_addressed: list[str] = Field(default_factory=list)
    review_summary: str = ""


# ---------------------------------------------------------------------------
# v0.6.9: Gen 4 Router schemas — routing recommendation layer
# ---------------------------------------------------------------------------

class RoutingSignal(BaseModel):
    """A single evidence signal that contributed to a routing decision."""
    signal_type: str           # "maturity", "confusion", "disagreement",
                               # "model_strength", "data_gap", "borderline",
                               # "cost", "correctness_rate"
    source: str = ""           # e.g. "insights:category_maturity", "calibrate:model_confusion"
    description: str = ""
    strength: float = 0.0      # 0.0-1.0


class RoutingRecommendation(BaseModel):
    """A single routing recommendation for a target (family, task, label)."""

    # --- Target ---
    target: str                # family name, task_id, or label
    target_kind: str = ""      # "family" | "task" | "label"

    # --- Recommendation ---
    recommended_mode: str = ""         # "single" | "multi" | "disagreement" | "cost_aware"
    recommended_models: list[str] = Field(default_factory=list)
    fallback_models: list[str] = Field(default_factory=list)

    # --- Rationale ---
    reason: str = ""
    confidence: str = ""               # "high" | "medium" | "low"
    expected_value: str = ""           # what running this way should yield
    cost_sensitivity: str = ""         # "low_cost_ok" | "standard" | "invest_in_quality"
    notes: list[str] = Field(default_factory=list)

    # --- Evidence ---
    based_on_signals: list[RoutingSignal] = Field(default_factory=list)

    # --- Known risks ---
    known_confusions: list[str] = Field(default_factory=list)
    disagreement_risk: str = ""        # "low" | "moderate" | "high"
    borderline_risk: str = ""          # "low" | "moderate" | "high"


class RoutingReport(BaseModel):
    """Top-level Gen 4 Router output — recommendations only."""
    generated_at: str = ""
    n_recommendations: int = 0
    recommendations: list[RoutingRecommendation] = Field(default_factory=list)
    summary: str = ""
    data_quality_note: str = ""        # how much data the recommendations are based on


# ---------------------------------------------------------------------------
# v0.6.10: Gen 5 Disagreement Lab schemas — forensic divergence layer
# ---------------------------------------------------------------------------

class ModelPosition(BaseModel):
    """A single model's position on a case."""
    model: str
    label: str = ""                    # final_answer (normalized)
    confidence: float = 0.0
    total_score: float = 0.0
    correctness: float = 0.0
    reasoning_integrity: str = ""      # well_supported / brittle / accidental
    key_failures: list[str] = Field(default_factory=list)
    key_flags: list[str] = Field(default_factory=list)


class AlternativeReading(BaseModel):
    """A plausible alternative interpretation of a case."""
    reading_label: str                 # e.g. "charitable_reading", "overclaim_reading"
    description: str = ""
    supporting_models: list[str] = Field(default_factory=list)
    plausibility: str = ""             # "high" | "medium" | "low"
    evidence: list[str] = Field(default_factory=list)


class DisagreementCaseReport(BaseModel):
    """Forensic analysis of disagreement on a single case."""

    # --- Identity ---
    task_id: str
    task_family: str = ""

    # --- Label distribution ---
    n_models: int = 0
    model_positions: list[ModelPosition] = Field(default_factory=list)
    label_distribution: dict[str, int] = Field(default_factory=dict)
    disagreement_score: float = 0.0    # Shannon entropy, 0-1

    # --- Confidence analysis ---
    avg_confidence: float = 0.0
    confidence_spread: float = 0.0     # max - min confidence
    all_high_confidence: bool = False   # all models confident but disagree

    # --- Alternative readings ---
    plausible_readings: list[AlternativeReading] = Field(default_factory=list)

    # --- Signals ---
    likely_borderline: bool = False
    likely_gold_review: bool = False
    likely_root_issue: str = ""        # "gold_label" | "model_limitation" |
                                       # "case_design" | "category_boundary" |
                                       # "evaluator" | "insufficient_data"
    root_issue_confidence: str = ""    # "high" | "medium" | "low" | "heuristic"
    root_issue_evidence: list[str] = Field(default_factory=list)

    # --- Model character notes ---
    model_character_notes: list[str] = Field(default_factory=list)

    # --- Verdict ---
    epistemic_value: str = ""          # "high" | "medium" | "low" | "noise"
    review_recommendation: str = ""


class DisagreementLabReport(BaseModel):
    """Top-level Gen 5 Disagreement Lab report."""
    generated_at: str = ""
    n_cases_analyzed: int = 0
    n_disagreement_cases: int = 0
    n_borderline_signals: int = 0
    n_gold_review_signals: int = 0
    cases: list[DisagreementCaseReport] = Field(default_factory=list)
    family_summary: dict[str, dict] = Field(default_factory=dict)
    model_character_summary: dict[str, list[str]] = Field(default_factory=dict)
    summary: str = ""


# ---------------------------------------------------------------------------
# v0.6.11: Gen 6 Audit Trail schemas — decision governance layer
# ---------------------------------------------------------------------------

class UpstreamStep(BaseModel):
    """A single step in an upstream dependency chain."""
    module: str = ""                   # "insights" | "calibrate" | "caseforge" | etc.
    reference: str = ""                # report id, proposal id, candidate id, etc.
    description: str = ""              # what this step contributed
    confidence: str = ""               # "high" | "medium" | "low" | "heuristic"


class DecisionEntry(BaseModel):
    """A single human decision on a pipeline recommendation or finding."""

    # --- Identity ---
    decision_id: str
    timestamp: str = ""

    # --- Classification ---
    decision_type: str = ""            # "gold_review_decision" | "category_refinement_decision"
                                       # | "routing_decision" | "case_candidate_review"
                                       # | "calibration_proposal_decision"
                                       # | "disagreement_resolution" | "workflow_note"
    target: str = ""                   # case id, category, model, route, proposal id
    target_kind: str = ""              # "case" | "category" | "model" | "route"
                                       # | "proposal" | "candidate" | "workflow"
    source_module: str = ""            # "calibrate" | "caseforge" | "router"
                                       # | "disagreement_lab" | "insights" | "manual"

    # --- Decision ---
    decision: str = ""                 # "accepted" | "rejected" | "deferred"
                                       # | "partially_accepted"
    reason: str = ""
    evidence_summary: str = ""

    # --- Context ---
    reviewer: str = ""                 # who made the decision
    notes: str = ""
    related_cases: list[str] = Field(default_factory=list)
    related_models: list[str] = Field(default_factory=list)

    # --- Optional state tracking ---
    before_state: str = ""             # e.g. "gold_label=overclaim"
    after_state: str = ""              # e.g. "gold_label=correlation_vs_causation"
    follow_up_action: str = ""         # e.g. "re-run all models on case031"

    # --- v0.6.11.1: Upstream dependency / error propagation (Gen 6.1) ---
    upstream_module: str = ""          # which module produced the signal that led here
    upstream_reference: str = ""       # ID of the upstream artifact (proposal, candidate, etc.)
    upstream_dependency_summary: str = ""  # human-readable description of the upstream basis
    dependency_confidence: str = ""    # "high" | "medium" | "low" | "heuristic"
    dependency_risk_note: str = ""     # optional: known risk, fragile assumption, etc.
    upstream_chain: list[UpstreamStep] = Field(default_factory=list)  # full provenance chain
    propagation_risk_level: str = ""   # "low" | "medium" | "high"
    review_override: bool = False      # True if reviewer decided against upstream recommendation


class AuditSummary(BaseModel):
    """Aggregated view of decision history."""
    generated_at: str = ""
    total_decisions: int = 0
    by_type: dict[str, int] = Field(default_factory=dict)
    by_decision: dict[str, int] = Field(default_factory=dict)
    by_source_module: dict[str, int] = Field(default_factory=dict)
    acceptance_rate: float = 0.0       # accepted / (accepted + rejected)
    most_active_targets: list[str] = Field(default_factory=list)
    deferred_count: int = 0
    recent_decisions: list[DecisionEntry] = Field(default_factory=list)


class DependencySummary(BaseModel):
    """Aggregated view of upstream dependency patterns across decisions."""
    generated_at: str = ""
    total_decisions: int = 0
    decisions_with_upstream: int = 0
    by_upstream_module: dict[str, int] = Field(default_factory=dict)
    by_dependency_confidence: dict[str, int] = Field(default_factory=dict)
    by_propagation_risk: dict[str, int] = Field(default_factory=dict)
    override_count: int = 0            # how many times reviewer overrode upstream
    override_rate: float = 0.0         # override_count / decisions_with_upstream
    weak_basis_accepted: int = 0       # accepted decisions with low/heuristic confidence
    risky_acceptances: list[DecisionEntry] = Field(default_factory=list)
    propagation_chains: list[dict] = Field(default_factory=list)  # detected multi-step chains
    rejected_upstream_patterns: dict[str, int] = Field(default_factory=dict)  # module→reject count


# ---------------------------------------------------------------------------
# Phase 7B — Forensic record / artifact-binding chain (representation robustness)
# ---------------------------------------------------------------------------
# A separate, additive contract for the CLAIM → PROVENANCE → EVIDENCE → INTERNAL
# FINDING → CLIENT FINDING chain and its deterministic QA gates. It does NOT modify
# the frozen forensic_report 6.3.0 output schema (which stays byte-compatible). The
# four-label claim taxonomy is unchanged; pipeline-QA codes live in a SEPARATE
# namespace (see agent_arena.artifact_binding) and are never claim labels.

FORENSIC_RECORD_SCHEMA_VERSION = "0.1.0"

# Provenance state of a captured public-style claim. A modelled/estimated value and
# a published literature value are DISTINCT states and must not be conflated.
PROVENANCE_STATES = (
    "archived_snapshot",     # a frozen copy of a page as retrieved
    "current_live",          # the page as it is live now (a different state)
    "modelled",              # an internally computed/estimated value
    "published_literature",  # a value stated in a cited publication
)

# Minimal, ordered summary-strength lattice (weak → strong assertion). Monotonicity
# invariant: a client summary may not assert a stronger status than its parent
# finding allows. Evidence strength and search completeness are separate dimensions;
# this lattice models evidential-conclusion strength only.
SUMMARY_STRENGTH_ORDER = (
    "not_assessed",              # 0 — no evidential conclusion asserted
    "mixed",                     # 1 — evidence genuinely points both ways
    "not_directly_established",  # 2 — the claim is not established on this evidence
    "limited_support",           # 3 — a qualified, bounded conclusion
    "not_supported",             # 4 — a definite negative conclusion
    "contradicted",              # 5 — evidence runs against the claim
    "disproven",                 # 6 — strongest negative; requires strong basis
)

# Value origin — a dimension SEPARATE from evidence strength, claim provenance,
# source provenance and search scope (Phase-7B slice 2). It answers: did the SOURCE
# report this quantitative/evidential value, or did Agent Arena DERIVE it (compute /
# model / estimate / aggregate)? A system-derived value must never silently become a
# source-reported (literature) fact downstream.
#
# FAIL-CLOSED (curator hardening): the two values below are the ONLY *resolved* origins.
# A missing origin is represented as ``None`` (unresolved) and must NEVER be treated as
# source_reported — absence of provenance metadata is not evidence of source provenance.
VALUE_ORIGIN_SOURCE_REPORTED = "source_reported"   # the cited source states this value
VALUE_ORIGIN_SYSTEM_DERIVED = "system_derived"     # Agent Arena produced it from inputs
VALUE_ORIGINS = (VALUE_ORIGIN_SOURCE_REPORTED, VALUE_ORIGIN_SYSTEM_DERIVED)

# What origin a CLIENT representation may assert. "unspecified" means the client makes
# NO positive origin claim (loss of attribution detail); it is always allowed and NEVER
# alters the internal record. Value origin is CATEGORICAL provenance — NOT a strength,
# confidence, or certainty scale. ``source_reported`` and ``system_derived`` are DISTINCT
# categories and neither may be rewritten into the other downstream (that would be a
# total order, which is wrong here). Provenance may be OMITTED (→ unspecified) but never
# REWRITTEN into a different origin.
CLIENT_ORIGIN_UNSPECIFIED = "unspecified"
CLIENT_ORIGIN_CLAIMS = (
    VALUE_ORIGIN_SOURCE_REPORTED,
    VALUE_ORIGIN_SYSTEM_DERIVED,
    CLIENT_ORIGIN_UNSPECIFIED,
)

# Categorical compatibility (NOT a ranking): which client-origin claims are compatible
# with each resolved internal origin — the same category, or a drop to unspecified. Any
# cross-category claim is a provenance falsification and is release-blocking.
ALLOWED_CLIENT_ORIGINS = {
    VALUE_ORIGIN_SOURCE_REPORTED: frozenset({VALUE_ORIGIN_SOURCE_REPORTED, CLIENT_ORIGIN_UNSPECIFIED}),
    VALUE_ORIGIN_SYSTEM_DERIVED: frozenset({VALUE_ORIGIN_SYSTEM_DERIVED, CLIENT_ORIGIN_UNSPECIFIED}),
}

# Search scope (Phase-7B slice 3) — a dimension SEPARATE from evidence strength,
# confidence, claim provenance and value origin. It answers: what universe of material
# was actually searched/reviewed before making a NEGATIVE evidence assertion?
# NOT FOUND ≠ DOES NOT EXIST: the breadth of a negative claim may not exceed its basis.
SCOPE_SOURCE_LOCAL = "source_local"              # the cited source itself lacks X (direct inspection)
SCOPE_REVIEWED_SET = "reviewed_set"              # X not identified in a defined reviewed source set
SCOPE_DOCUMENTED_SEARCH = "documented_search"    # X not identified in a documented structured search
SCOPE_GLOBAL_NONEXISTENCE = "global_nonexistence"  # X does not exist (a world claim)

# What a SearchScope object may document (source_local is a direct-inspection basis, not
# a search, so it is NOT a SearchScope.scope_type).
SEARCH_SCOPE_TYPES = (SCOPE_REVIEWED_SET, SCOPE_DOCUMENTED_SEARCH)
# Scopes an assertion (internal or client-facing) may declare.
ASSERTION_SCOPES = (SCOPE_SOURCE_LOCAL, SCOPE_REVIEWED_SET, SCOPE_DOCUMENTED_SEARCH,
                    SCOPE_GLOBAL_NONEXISTENCE)
# Modest completeness labels only — no "complete"/"exhaustive" (no false certainty).
SEARCH_COMPLETENESS_VALUES = ("targeted", "structured")

# Categorical containment (NOT a numeric rank): which client assertion scopes a given
# documented BASIS breadth supports. A client may keep or NARROW scope, never broaden it.
# global_nonexistence is supported by NO basis by default (fail closed) — a documented
# search does not prove global absence.
ALLOWED_CLIENT_SCOPES = {
    SCOPE_SOURCE_LOCAL: frozenset({SCOPE_SOURCE_LOCAL}),
    SCOPE_REVIEWED_SET: frozenset({SCOPE_SOURCE_LOCAL, SCOPE_REVIEWED_SET}),
    SCOPE_DOCUMENTED_SEARCH: frozenset({SCOPE_SOURCE_LOCAL, SCOPE_REVIEWED_SET,
                                        SCOPE_DOCUMENTED_SEARCH}),
}


class ClaimProvenance(BaseModel):
    """Frozen provenance of one captured public-style claim (immutable at capture).

    Downstream representations must REFERENCE this object by ``provenance_id``; a
    renderer/summary may not freely reconstruct the claim's origin.
    """
    provenance_id: str
    exact_claim_text: str
    source_id: str                              # identity of the page/source captured from
    provenance_state: str = "archived_snapshot"  # one of PROVENANCE_STATES
    canonical_url: str | None = None
    page_title: str | None = None
    retrieved_at: str | None = None             # ISO-8601 passthrough (never wall-clock)
    content_fingerprint: str | None = None       # recomputable SHA-256 (see artifact_binding)
    context_before: str | None = None
    context_after: str | None = None


class QAEvidenceItem(BaseModel):
    """One stable-identified evidence item participating in the QA path.

    ``role`` reuses the existing :class:`EvidenceRole` (no second direction enum).
    ``value_origin`` (Phase-7B slice 2) records whether the cited source reported the
    value or Agent Arena derived it; a derived item carries its derivation lineage.
    """
    evidence_id: str
    source_id: str
    role: EvidenceRole = EvidenceRole.SUPPORTING
    endpoint: str = ""                          # what was measured / outcome type
    material: bool = True                       # materially relevant to the interpretation
    exact_reference: str | None = None          # span / table / figure where available
    text: str = ""
    reported_value: str | None = None           # the quantitative value, if any (e.g. "≈ 60%")
    # --- value origin + derivation lineage (FAIL-CLOSED: default None = unresolved) ---
    # None means "origin not established" and must never be treated as source_reported.
    value_origin: str | None = None             # one of VALUE_ORIGINS, or None (unresolved)
    derivation_method: str | None = None        # identifier of the model/method, if derived
    input_evidence_ids: list[str] = Field(default_factory=list)  # source inputs a derived value used
    derivation_note: str | None = None          # human-readable note on how it was derived


class InternalFinding(BaseModel):
    """An internally validated finding bound to frozen provenance and evidence ids."""
    finding_id: str
    provenance_id: str                          # references the frozen ClaimProvenance
    proposition: str
    verdict_summary: str = ""
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    contrary_evidence_ids: list[str] = Field(default_factory=list)
    allowed_summary_strength: str = "not_assessed"   # ceiling for any client summary
    confidence_status: str = ""                 # optional VALID/MISSING/INVALID passthrough
    predicted_label: str | None = None          # frozen claim taxonomy (optional, unchanged)


class ClientValueClaim(BaseModel):
    """A client representation's explicit origin assertion about one evidence value.

    Binds a referenced ``evidence_id`` to the origin the client asserts for it and any
    sources the client attributes it to. Enforced deterministically against the parent
    evidence's ``value_origin`` and derivation lineage (no NLP classification).
    """
    evidence_id: str
    claimed_origin: str = CLIENT_ORIGIN_UNSPECIFIED   # one of CLIENT_ORIGIN_CLAIMS
    claimed_source_ids: list[str] = Field(default_factory=list)


class SearchScope(BaseModel):
    """Documents what universe of material was actually searched/reviewed.

    A ``source_local`` basis is direct inspection of frozen source evidence, NOT a
    search — so it is not represented here; only ``reviewed_set`` / ``documented_search``.
    A ``documented_search`` must carry positive machine-readable evidence that a search
    occurred (see the gate); an empty search record fails closed.
    """
    search_scope_id: str
    scope_type: str                             # one of SEARCH_SCOPE_TYPES
    reviewed_source_ids: list[str] = Field(default_factory=list)
    resources: list[str] = Field(default_factory=list)   # named databases / resources
    query_terms: list[str] = Field(default_factory=list)
    date_cutoff: str | None = None
    search_completeness: str | None = None      # one of SEARCH_COMPLETENESS_VALUES


class NegativeEvidenceAssertion(BaseModel):
    """An internal 'X was not found' assertion, bound to a finding and its search basis.

    Its actual basis breadth is derived from support (a resolved ``search_scope_id``, or
    resolvable ``source_local_evidence_ids``), not from a self-declared label.
    """
    assertion_id: str
    finding_id: str
    proposition: str = ""                        # what is asserted to be absent
    assertion_scope: str = SCOPE_SOURCE_LOCAL    # one of ASSERTION_SCOPES (documentation)
    search_scope_id: str | None = None           # basis when a search was performed
    source_local_evidence_ids: list[str] = Field(default_factory=list)  # direct-inspection basis


class ClientNegativeAssertion(BaseModel):
    """A client-facing negative assertion; declares the epistemic scope it claims."""
    assertion_id: str                            # references a NegativeEvidenceAssertion
    client_scope: str = SCOPE_SOURCE_LOCAL       # one of ASSERTION_SCOPES


class ClientFinding(BaseModel):
    """A client-facing finding; must bind to a parent finding and frozen provenance.

    Invariant: NO CLIENT SUMMARY WITHOUT FINDING BINDING.
    """
    client_finding_id: str
    parent_finding_id: str
    display_claim: str
    client_explanation: str = ""
    client_strength: str = "not_assessed"       # must be <= parent allowed_summary_strength
    referenced_evidence_ids: list[str] = Field(default_factory=list)
    provenance_id: str                          # must resolve to the parent's frozen provenance
    value_claims: list[ClientValueClaim] = Field(default_factory=list)  # per-value origin assertions
    client_negative_assertions: list[ClientNegativeAssertion] = Field(default_factory=list)


class ForensicRecord(BaseModel):
    """The structured intermediate representation the artifact-binding gate operates on.

    A serialized ForensicRecord is a PIPELINE-QA fixture (data class C), never a case
    library / evaluation / benchmark / holdout artifact.
    """
    record_schema_version: str = FORENSIC_RECORD_SCHEMA_VERSION
    record_id: str
    synthetic_fixture: bool = True
    fixture_class: str = "pipeline_qa"          # explicit data-class C marker
    provenance: list[ClaimProvenance] = Field(default_factory=list)
    evidence: list[QAEvidenceItem] = Field(default_factory=list)
    findings: list[InternalFinding] = Field(default_factory=list)
    client_findings: list[ClientFinding] = Field(default_factory=list)
    search_scopes: list[SearchScope] = Field(default_factory=list)
    negative_assertions: list[NegativeEvidenceAssertion] = Field(default_factory=list)
