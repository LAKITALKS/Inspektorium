"""Forensic evaluation engine for agent-arena v0.5.

Layer 1: Deterministic — correctness, parse quality, numeric matching
Layer 2: Semantic rubric — rubric + insight matching with functional descriptions
Layer 3: Diagnostic — 10-dimension forensic scoring

All findings are evidence-bound. No score without evidence.

# ===========================================================================
# ENGINE SCOPE MANIFEST — v0.5
# ===========================================================================
#
# WHAT THIS ENGINE CAN DO (strong claims):
#   - Deterministic answer matching (exact, contains, numeric with tolerance)
#   - Extract and cross-verify numeric facts (percentages, fractions) in
#     entity-comparison tasks (Simpson's Paradox shape)
#   - Extract probability values from P()-notation chains, decimal/percentage
#     statements, and fractions (base rate neglect + Monty Hall shapes)
#   - Detect directional comparative claims (higher/lower/discriminates)
#   - Detect switch/stay direction claims in decision tasks
#   - Flag numeric contradictions between agent claims and task data
#   - Score cap enforcement: wrong answer → max 40, contradiction → max 45
#   - Structural reasoning scoring based on step utility, coherence, and
#     redundancy (not step count or length)
#   - Support strength with 3 tiers: load-bearing, supporting, mentioned
#   - Grounding audit: DIRECT requires overlap + sub-conclusion marker
#   - 14 consistency checks with confidence labels (HIGH/MEDIUM/HEURISTIC)
#   - v0.4.3: Intermediate step arithmetic verification (sums, differences,
#     products, divisions, fraction-to-percentage)
#   - v0.4.3: Load-bearing step classification (late overlap, number tracing,
#     conclusion markers, transitive dependencies)
#   - v0.4.3: Right-answer-wrong-reasoning detection — classifies reasoning
#     integrity as well_supported / brittle / accidental
#   - v0.4.3: Differential severity for load-bearing vs decorative errors
#
# WHAT IS HEURISTIC (suggestive, not definitive):
#   - Overlap-based claim drift detection
#   - Unused assumption / decorative uncertainty flagging
#   - Information density measurement
#   - Communication efficiency scoring
#   - Insight depth matching (keyword overlap, not semantic)
#   - Mechanism quality scoring
#   - Load-bearing classification (overlap + number heuristics)
#   - "Accidental correctness" classification (conservative — requires
#     verified arithmetic error in a load-bearing step)
#
# v0.5: Forecast integrity checks (forecasting_decision tasks):
#   - Probability-reasoning alignment (overconfident, underjustified)
#   - Base rate usage (omission, baseline-blind)
#   - Rule / resolution integrity (misread, not engaged)
#   - Skeptic coverage (decorative, insufficient)
#   - No-trade integrity (justified vs empty abstention)
#   - Shrinkage discipline (extreme without adjustment)
#   - Narrative edge (rhetorical vs evidence-based)
#   - Decision category validation (forecast/watch/no_trade/abstain)
#
# WHAT THIS ENGINE CANNOT DO (explicit non-claims):
#   - Verify multi-step algebraic derivations (only simple A op B = C)
#   - Detect semantic reasoning errors (flawed logic without arithmetic)
#   - Understand implicit comparisons without directional keywords
#   - Verify semantic equivalence of claims
#   - Judge domain-specific correctness beyond answer matching
#   - Verify WHY a calculation is the right approach (only IF it's computed correctly)
#   - Outcome-based calibration scoring (no historical outcome data)
#   - Market-derived probability comparison (no live market integration)
#
# SUPPORTED TASK SHAPES:
#   1. Simpson's Paradox — entity-comparison with percentages/fractions
#   2. Base Rate Neglect — Bayesian probability with P()-notation
#   3. Monty Hall Variant — conditional probability with switch/stay decisions
#   4. Forecasting Decision — probability estimation under uncertainty (v0.5)
#
# CONFIDENCE LEVELS:
#   HIGH CONFIDENCE   — deterministic checks, verified arithmetic, claim-checker
#   MEDIUM CONFIDENCE — grounded heuristic with structural evidence
#   HEURISTIC         — overlap-based or stylistic pattern matching
#
# See schemas.py for unified confidence mapping (FAILURE_CONFIDENCE_MAP,
# CONSISTENCY_CONFIDENCE_MAP).
# ===========================================================================
"""

from __future__ import annotations

import re

from agent_arena.claim_checker import (
    count_contradictions,
    get_contradictions,
    run_claim_checks,
)
from agent_arena.confidence_validity import confidence_value_if_valid
from agent_arena.forecast_checker import is_forecast_task, run_forecast_checks
from agent_arena.study_forensics_checker import is_study_forensics_task, run_study_forensics_checks
from agent_arena.step_checker import StepCheckResult, verify_all_steps
from agent_arena.consistency import run_consistency_checks
from agent_arena.reasoning_graph import (
    build_mechanism_analysis,
    build_reasoning_graph,
    classify_self_check,
    _build_grounding_audit,
)
from agent_arena.schemas import (
    DIAGNOSTIC_WEIGHTS,
    FAILURE_CONFIDENCE_MAP,
    AgentResponse,
    AgentResult,
    ClaimCheckResult,
    ClaimTruthStatus,
    ConsistencyFinding,
    DiagnosticScores,
    EvaluatedResult,
    EvidenceRole,
    EvidenceSpan,
    FailureCategory,
    FailureInstance,
    FailureSeverity,
    ForensicFlag,
    GroundingAudit,
    KeyInsight,
    MechanismAnalysis,
    ReasoningGraph,
    RubricItem,
    RunRecord,
    ScoredDimension,
    Task,
    TaskType,
    get_confidence_label,
)


# ---------------------------------------------------------------------------
# Shared utilities
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    return text.strip().lower().replace(",", "").replace("%", "")


def _all_text(parsed: AgentResponse) -> str:
    parts = [
        parsed.final_answer,
        *parsed.steps,
        *parsed.assumptions,
        *parsed.alternative_hypotheses,
        *parsed.uncertainties,
        *parsed.self_check,
        *parsed.key_claims,
    ]
    return " ".join(parts).lower()


def _stem(word: str) -> str:
    for suffix in ("ations", "ation", "ting", "ing", "ment", "ness", "edly",
                   "able", "ible", "ive", "ed", "ly", "es", "s"):
        if len(word) > len(suffix) + 3 and word.endswith(suffix):
            return word[: -len(suffix)]
    return word


def _keyword_in_text(kw: str, text: str) -> bool:
    if kw in text:
        return True
    kw_stem = _stem(kw)
    if kw_stem != kw and len(kw_stem) > 3 and kw_stem in text:
        return True
    for part in kw.split("-"):
        if len(part) > 3 and part in text:
            return True
        ps = _stem(part)
        if len(ps) > 3 and ps != part and ps in text:
            return True
    return False


def _signal_density(text: str) -> float:
    words = text.split()
    if not words:
        return 0.0
    filler = {"the", "a", "an", "is", "are", "was", "were", "be", "been",
              "being", "have", "has", "had", "do", "does", "did", "will",
              "would", "could", "should", "may", "might", "shall", "can",
              "this", "that", "these", "those", "it", "its", "of", "in",
              "to", "for", "with", "on", "at", "by", "from", "as", "into",
              "and", "or", "but", "so", "if", "then", "than", "also", "very",
              "just", "we", "i", "you", "he", "she", "they", "our", "my"}
    return sum(1 for w in words if w.lower() not in filler) / len(words)


def _content_words(text: str, min_len: int = 4) -> set[str]:
    stopwords = {"about", "which", "would", "could", "should", "there", "their",
                 "these", "those", "being", "where", "other", "because", "since",
                 "however", "while", "though", "have", "this", "that", "what",
                 "when", "than", "then", "also", "just", "more", "some", "very",
                 "each", "they", "been", "were", "does", "only"}
    return {w for w in text.lower().split()
            if len(w) >= min_len and w not in stopwords}


# ---------------------------------------------------------------------------
# Rubric + insight matching
# ---------------------------------------------------------------------------

def _rubric_item_matches(item: RubricItem, text: str) -> tuple[bool, str | None]:
    for variant in item.variants:
        v = variant.lower()
        if v in text:
            idx = text.index(v)
            return True, text[max(0, idx - 20):idx + len(v) + 20]
    keywords = item.criterion.lower().split()
    for kw in keywords:
        if len(kw) > 3 and _keyword_in_text(kw, text):
            idx = text.find(kw) if kw in text else -1
            snippet = text[max(0, idx - 20):idx + len(kw) + 20] if idx >= 0 else kw
            return True, snippet
    return False, None


def _insight_matches(insight: KeyInsight, text: str) -> bool:
    if insight.keyword.lower() in text:
        return True
    for v in insight.variants:
        if v.lower() in text:
            return True
    return _keyword_in_text(insight.keyword.lower(), text)


FUNCTIONAL_INDICATORS: dict[str, list[str]] = {
    "simpson": ["aggregate", "overall", "reverse", "individual", "department", "subgroup", "within each"],
    "paradox": ["reverse", "opposite", "counter-intuitive", "misleading", "appears", "actually"],
    "aggregation": ["aggregate", "overall", "combined", "total", "pooled", "grouped"],
    "confounding": ["confound", "lurking", "third variable", "spurious", "driven by", "explained by", "due to"],
    "subgroup": ["within each", "per department", "individual", "separately", "disaggregate", "breakdown"],
    "base rate": ["prevalence", "prior", "1 in 1000", "rare", "how common"],
    "bayes": ["posterior", "prior", "likelihood", "p(a|b)", "conditional"],
    "false positive": ["false alarm", "incorrectly positive", "test positive without"],
    "conditional probability": ["given that", "conditioned on", "p(a|b)", "conditional on"],
    "host behavior": ["host's choice", "host's strategy", "host opens", "host randomly"],
}


def insight_match_score(insight: KeyInsight, text: str) -> tuple[float, str]:
    if _insight_matches(insight, text):
        return 1.0, "exact"
    if _keyword_in_text(insight.keyword.lower(), text):
        return 0.8, "stem"
    func_descs = insight.functional_descriptions
    if func_descs:
        hits = sum(1 for fd in func_descs if fd.lower() in text)
        if hits >= 1:
            return 0.6, "functional"
    indicators = FUNCTIONAL_INDICATORS.get(insight.keyword.lower(), [])
    if indicators:
        hits = sum(1 for ind in indicators if ind in text)
        if hits >= 2:
            return 0.5, "functional_builtin"
    return 0.0, "miss"


# ---------------------------------------------------------------------------
# Main evaluation
# ---------------------------------------------------------------------------

def evaluate_result(task: Task, result: AgentResult) -> EvaluatedResult:
    from agent_arena.phase8_pipeline import assess_agent_result
    result = result.model_copy(update={"phase8": assess_agent_result(task, result)})
    if result.phase9:
        from agent_arena.phase9_runtime import revalidate_assessment
        result = result.model_copy(update={"phase9": revalidate_assessment(task, result.phase9)})
    if not result.parse_ok or result.parsed is None:
        return _empty_result(result)

    p = result.parsed
    text = _all_text(p)

    scored_dims: list[ScoredDimension] = []
    failures: list[FailureInstance] = []
    all_notes: list[str] = []

    # Build reasoning graph
    graph = build_reasoning_graph(p, task)

    # --- Claim checking (v0.4.1) ---
    claim_results = run_claim_checks(task, p)
    n_contradictions = count_contradictions(claim_results)

    # --- Step verification (v0.4.3) ---
    step_checks = verify_all_steps(p.steps) if p.steps else []

    # --- Mechanism analysis (v0.4.1) ---
    mech_analysis = build_mechanism_analysis(p, task)

    # --- Grounding audit (v0.4.1) ---
    grounding = _build_grounding_audit(graph.claims, graph.relations)

    # --- Layer 1: Deterministic ---
    correctness, corr_ev, corr_notes = _eval_correctness(task, p)
    scored_dims.append(_dim("correctness", correctness, corr_ev, corr_notes))
    all_notes.extend(corr_notes)

    if correctness == 0.0 and task.expected_answer:
        failures.append(FailureInstance(
            category=FailureCategory.WRONG_ANSWER.value,
            severity=FailureSeverity.CRITICAL.value,
            description=f"Answer does not match expected '{task.expected_answer}'",
            evidence=[EvidenceSpan(text=p.final_answer[:200], source_field="final_answer",
                                   relevance="Incorrect answer")],
            impact_on_score="correctness",
        ))

    # --- Layer 2: Semantic rubric ---
    rubric_score, rubric_ev, rubric_notes = _eval_rubric(task, p, text, failures)
    insight_score, insight_ev, insight_notes = _eval_insights(task, text)
    all_notes.extend(rubric_notes + insight_notes)

    # --- Layer 3: Diagnostic (10 dimensions) ---

    # Support strength (NEW v0.4)
    support_score, support_ev, support_notes = _eval_support_strength(p, graph, failures)
    scored_dims.append(_dim("support_strength", support_score, support_ev, support_notes))
    all_notes.extend(support_notes)

    # Structural reasoning
    struct_score, struct_ev, struct_notes = _eval_structural_reasoning(p)
    scored_dims.append(_dim("structural_reasoning", struct_score, struct_ev, struct_notes))
    all_notes.extend(struct_notes)

    # Assumption discipline (uses graph)
    assume_score, assume_ev, assume_notes = _eval_assumption_discipline(p, graph, failures)
    scored_dims.append(_dim("assumption_discipline", assume_score, assume_ev, assume_notes))
    all_notes.extend(assume_notes)

    # Uncertainty handling (uses graph)
    uncert_score, uncert_ev, uncert_notes = _eval_uncertainty_handling(p, task, graph, failures)
    scored_dims.append(_dim("uncertainty_handling", uncert_score, uncert_ev, uncert_notes))
    all_notes.extend(uncert_notes)

    # Alternative hypothesis quality
    alt_score, alt_ev, alt_notes = _eval_alt_hypothesis_quality(p, failures)
    scored_dims.append(_dim("alternative_hypothesis_quality", alt_score, alt_ev, alt_notes))
    all_notes.extend(alt_notes)

    # Self-monitoring quality (uses graph)
    self_score, self_ev, self_notes = _eval_self_monitoring(p, task, graph, failures)
    scored_dims.append(_dim("self_monitoring_quality", self_score, self_ev, self_notes))
    all_notes.extend(self_notes)

    # Mechanism quality (v0.4, hardened v0.4.1)
    mech_score, mech_ev, mech_notes = _eval_mechanism_quality(p, task, text, failures, mech_analysis)
    scored_dims.append(_dim("mechanism_quality", mech_score, mech_ev, mech_notes))
    all_notes.extend(mech_notes)

    # Communication efficiency
    comm_score, comm_ev, comm_notes = _eval_communication(p, text, failures)
    scored_dims.append(_dim("communication_efficiency", comm_score, comm_ev, comm_notes))
    all_notes.extend(comm_notes)

    # Insert rubric/insight into scored dims
    if task.task_type == TaskType.RUBRIC_BASED and rubric_score is not None:
        scored_dims = [d for d in scored_dims if d.dimension != "correctness"]
        scored_dims.insert(0, _dim("correctness", rubric_score, rubric_ev, rubric_notes))

    scored_dims.append(_dim("insight_depth", insight_score, insight_ev, insight_notes))

    # --- Consistency engine (v0.4.1: pass claim results) ---
    consistency_findings = run_consistency_checks(p, task, claim_results)

    # Consistency modifier on structural reasoning
    consistency_mod = 1.0
    for f in consistency_findings:
        if f.status == "fail":
            consistency_mod -= 0.15
        elif f.status == "warning" and f.check_type == "self_correction":
            consistency_mod -= 0.08
    consistency_mod = max(0.0, consistency_mod)

    # v0.4.1: Generate failures from claim contradictions
    for cr in get_contradictions(claim_results):
        failures.append(FailureInstance(
            category=FailureCategory.VERBAL_NUMERIC_CONTRADICTION.value,
            severity=FailureSeverity.MAJOR.value,
            description=f"Verbal-numeric contradiction: {cr.explanation}",
            evidence=[EvidenceSpan(
                text=cr.claim.source_text[:200],
                source_field=cr.claim.source_field,
                relevance=cr.explanation,
                role=EvidenceRole.CONTRADICTORY,
            )],
            impact_on_score="correctness, support_strength, structural_reasoning",
        ))

    # v0.4.1: Failed self-audit failure
    has_failed_audit = any(
        f.check_type == "failed_self_audit" and f.status == "fail"
        for f in consistency_findings
    )
    if has_failed_audit:
        failures.append(FailureInstance(
            category=FailureCategory.FAILED_SELF_AUDIT.value,
            severity=FailureSeverity.MODERATE.value,
            description="Self-check claims correctness but claim checker found contradictions",
            evidence=[EvidenceSpan(
                text=p.self_check[0][:150] if p.self_check else "",
                source_field="self_check[0]",
                relevance="Self-check missed real errors",
                role=EvidenceRole.WEAKENING,
            )],
            impact_on_score="self_monitoring_quality",
        ))

    # v0.4.1: Mechanism gap failures from analysis
    if mech_analysis.concept_named and not mech_analysis.mechanism_described:
        # Only add if not already added by mechanism quality eval
        has_mech_gap = any(f.category == FailureCategory.MECHANISM_GAP.value for f in failures)
        if not has_mech_gap:
            failures.append(FailureInstance(
                category=FailureCategory.NAMED_NOT_EXPLAINED.value,
                severity=FailureSeverity.MODERATE.value,
                description=f"Named concept(s) {mech_analysis.named_concepts} but mechanism not described",
                impact_on_score="mechanism_quality, insight_depth",
            ))

    # --- Reasoning integrity (v0.4.3) ---
    eff_correctness = rubric_score if (task.task_type == TaskType.RUBRIC_BASED and rubric_score is not None) else correctness
    reasoning_integrity = _build_reasoning_integrity(
        p, task, eff_correctness, step_checks, failures,
    )

    # --- Forecast integrity (v0.5) ---
    forecast_integrity = run_forecast_checks(task, p)
    if forecast_integrity:
        failures.extend(forecast_integrity.get("failures", []))

    # --- Study forensics (v0.6) ---
    study_forensics = run_study_forensics_checks(task, p)
    if study_forensics.get("is_study_forensics"):
        failures.extend(study_forensics.get("failures", []))

    # --- Forensic flags ---
    flags = _build_forensic_flags(p, task, graph, consistency_findings,
                                   eff_correctness, insight_score, struct_score,
                                   support_score, mech_score, self_score,
                                   claim_results, mech_analysis, grounding,
                                   reasoning_integrity, step_checks)
    if forecast_integrity:
        flags.extend(forecast_integrity.get("flags", []))
    if study_forensics.get("is_study_forensics"):
        flags.extend(study_forensics.get("flags", []))

    # --- Build final scores ---
    eff_structural = min(1.0, struct_score * consistency_mod)

    # v0.4.2: Strengthened contradiction penalty.
    # If the claim checker finds a proven contradiction, the response is
    # demonstrably wrong on at least one factual claim.  We apply both a
    # dimension-level penalty AND a hard cap on the total score so that
    # good structure can never fully mask a wrong answer.
    contradiction_penalty = min(1.0, n_contradictions * 0.30)
    if n_contradictions > 0:
        eff_correctness = max(0.0, eff_correctness - contradiction_penalty)
        support_score = max(0.0, support_score - contradiction_penalty * 0.6)
        eff_structural = max(0.0, eff_structural - contradiction_penalty * 0.4)

    # v0.4.1: Grounding-based support adjustment
    if grounding and grounding.total_conclusion_claims > 0:
        grounding_ratio = (grounding.directly_supported + grounding.indirectly_supported * 0.5) / grounding.total_conclusion_claims
        if grounding_ratio < 0.3:
            support_score = max(0.0, support_score * 0.6)
        if grounding.contradicted > 0:
            support_score = max(0.0, support_score - 0.2)

    # v0.4.1: Mechanism analysis adjustment
    if mech_analysis:
        if mech_analysis.concept_named and mech_analysis.mechanism_described and mech_analysis.mechanism_grounded_to_case:
            mech_score = max(mech_score, 0.7)  # floor for fully grounded mechanism
        elif mech_analysis.concept_named and not mech_analysis.mechanism_described:
            mech_score = min(mech_score, 0.35)  # cap for naming without explaining

    # v0.4.1: Failed self-audit penalty
    if has_failed_audit:
        self_score = max(0.0, self_score - 0.3)

    # v0.4.3: Reasoning integrity penalties
    ri_class = reasoning_integrity.get("classification", "well_supported")
    n_lb_errors = reasoning_integrity.get("n_load_bearing_errors", 0)
    n_int_errors = reasoning_integrity.get("n_intermediate_errors", 0)

    if ri_class == "accidental":
        # Correct answer but broken load-bearing steps
        # Correctness stays high, but support/structure take a hit
        support_score = max(0.0, support_score - 0.25 * n_lb_errors)
        eff_structural = max(0.0, eff_structural - 0.20 * n_lb_errors)
        self_score = max(0.0, self_score - 0.15)  # should have caught own error
    elif ri_class == "brittle":
        # Decorative errors only — light penalty
        eff_structural = max(0.0, eff_structural - 0.08 * n_int_errors)
    # "well_supported" → no penalty

    # v0.6: Study forensics score adjustments
    if study_forensics.get("is_study_forensics"):
        sf_scores = study_forensics.get("scores", {})
        # Use label correctness for the correctness dimension
        sf_label_score = sf_scores.get("label_score", 0.0)
        eff_correctness = sf_label_score
        # Blend finding recall into insight_depth
        sf_recall = sf_scores.get("finding_recall", 0.0)
        insight_score = max(insight_score, sf_recall)
        # Apply false positive penalty for solid cases
        fp_penalty = sf_scores.get("false_positive_penalty", 0.0)
        if fp_penalty > 0:
            eff_correctness = max(0.0, eff_correctness - fp_penalty)
            insight_score = max(0.0, insight_score - fp_penalty)

    scores = DiagnosticScores(
        correctness=eff_correctness,
        support_strength=support_score,
        structural_reasoning=eff_structural,
        assumption_discipline=assume_score,
        uncertainty_handling=uncert_score,
        alternative_hypothesis_quality=alt_score,
        self_monitoring_quality=self_score,
        insight_depth=insight_score,
        mechanism_quality=mech_score,
        communication_efficiency=comm_score,
    )

    # v0.4.2: Assign confidence labels to failures
    _assign_failure_confidence(failures)

    # v0.4.2: Hard score cap when a locally proven contradiction is detected.
    # A response that is demonstrably wrong on a factual claim should never
    # score above 45/100 regardless of how well-structured it is.
    if n_contradictions >= 1:
        scores._score_cap = 45.0

    # v0.4.2: If correctness is zero (answer is wrong), cap at 40/100.
    # This prevents a wrong-but-well-structured answer from scoring high.
    if eff_correctness == 0.0 and task.expected_answer:
        scores._score_cap = min(scores._score_cap or 40.0, 40.0)

    # Serialize study_forensics for storage (strip non-serializable FailureInstance/ForensicFlag)
    study_forensics_stored = {}
    if study_forensics.get("is_study_forensics"):
        study_forensics_stored = {
            k: v for k, v in study_forensics.items()
            if k not in ("failures", "flags")
        }
        study_forensics_stored["phase8"] = result.phase8

    return EvaluatedResult(
        agent_result=result,
        scores=scores,
        scored_dimensions=scored_dims,
        failures=failures,
        consistency_findings=consistency_findings,
        forensic_flags=flags,
        reasoning_graph=graph,
        claim_check_results=claim_results,
        mechanism_analysis=mech_analysis,
        grounding_audit=grounding,
        step_check_results=step_checks,
        reasoning_integrity=reasoning_integrity,
        forecast_integrity=forecast_integrity,
        study_forensics=study_forensics_stored,
        failure_modes=[f.category for f in failures],
        notes=all_notes,
    )


def _dim(name: str, raw: float, ev: list[EvidenceSpan], notes: list[str]) -> ScoredDimension:
    return ScoredDimension(
        dimension=name, raw_score=raw, weight=DIAGNOSTIC_WEIGHTS[name],
        weighted_score=round(raw * DIAGNOSTIC_WEIGHTS[name], 1),
        evidence=ev, notes=notes,
    )


def _empty_result(result: AgentResult) -> EvaluatedResult:
    return EvaluatedResult(
        agent_result=result,
        failures=[FailureInstance(
            category=FailureCategory.WRONG_ANSWER.value,
            severity=FailureSeverity.CRITICAL.value,
            description="Output not parseable as structured JSON",
            impact_on_score="all",
        )],
        notes=["Output not parseable"],
    )


# ---------------------------------------------------------------------------
# Layer 1: Correctness
# ---------------------------------------------------------------------------

def _eval_correctness(task: Task, p: AgentResponse) -> tuple[float, list[EvidenceSpan], list[str]]:
    evidence: list[EvidenceSpan] = []
    notes: list[str] = []
    answer = _normalize(p.final_answer)

    if not task.expected_answer:
        notes.append("No expected answer; correctness deferred to rubric")
        return 0.0, evidence, notes

    expected = _normalize(task.expected_answer)
    ev = EvidenceSpan(text=p.final_answer[:200], source_field="final_answer",
                       relevance="Agent's answer for correctness check")
    evidence.append(ev)

    if answer == expected:
        notes.append("Exact match")
        return 1.0, evidence, notes

    if task.evaluation.tolerance is not None:
        try:
            a_val = float(answer)
            e_val = float(expected)
            if abs(a_val - e_val) <= task.evaluation.tolerance:
                notes.append(f"Within tolerance ({task.evaluation.tolerance})")
                return 1.0, evidence, notes
            ratio = max(0.0, 1.0 - abs(a_val - e_val) / max(abs(e_val), 1e-9))
            notes.append(f"Numeric: off by {abs(a_val - e_val):.4f}")
            return ratio, evidence, notes
        except ValueError:
            pass

    if task.evaluation.answer_match == "contains" and expected in answer:
        notes.append("Contains expected answer")
        return 0.9, evidence, notes

    if expected in answer:
        notes.append("Partial match in answer")
        return 0.7, evidence, notes

    notes.append(f"No match (got: {answer[:80]})")
    return 0.0, evidence, notes


# ---------------------------------------------------------------------------
# Layer 2: Rubric
# ---------------------------------------------------------------------------

def _eval_rubric(task: Task, p: AgentResponse, text: str,
                 failures: list[FailureInstance]) -> tuple[float | None, list[EvidenceSpan], list[str]]:
    if not task.rubric:
        return None, [], []

    evidence: list[EvidenceSpan] = []
    notes: list[str] = []
    total_possible = sum(item.points for item in task.rubric)
    earned = 0

    for item in task.rubric:
        matched, snippet = _rubric_item_matches(item, text)
        if matched:
            earned += item.points
            notes.append(f"Rubric hit: {item.criterion}")
            if snippet:
                evidence.append(EvidenceSpan(
                    text=snippet.strip(), source_field="(matched in output)",
                    relevance=f"Rubric criterion: {item.criterion}",
                    role=EvidenceRole.SUPPORTING,
                ))
        else:
            notes.append(f"Rubric miss: {item.criterion}")
            evidence.append(EvidenceSpan(
                text=f"Missing: {item.criterion}", source_field="(not found)",
                relevance=f"Rubric criterion not met: {item.criterion}",
                role=EvidenceRole.MISSING_EXPECTED,
            ))
            failures.append(FailureInstance(
                category=FailureCategory.MISSED_KEY_INSIGHT.value,
                severity=FailureSeverity.MAJOR.value,
                description=f"Rubric criterion not met: {item.criterion}",
                impact_on_score="correctness",
            ))

    ratio = earned / total_possible if total_possible > 0 else 0.0
    return ratio, evidence, notes


# ---------------------------------------------------------------------------
# Layer 2: Insights
# ---------------------------------------------------------------------------

def _eval_insights(task: Task, text: str) -> tuple[float, list[EvidenceSpan], list[str]]:
    insights = task.get_key_insights()
    if not insights:
        return 0.0, [], ["No key insights defined"]

    evidence: list[EvidenceSpan] = []
    notes: list[str] = []
    total = 0.0
    full = partial = 0

    for ins in insights:
        score, level = insight_match_score(ins, text)
        total += score
        if score >= 0.8:
            full += 1
        elif score > 0:
            partial += 1
        if score > 0:
            kw = ins.keyword.lower()
            idx = text.find(kw)
            if idx >= 0:
                snippet = text[max(0, idx - 30):idx + len(kw) + 30]
                evidence.append(EvidenceSpan(
                    text=snippet.strip(), source_field="(output text)",
                    relevance=f"Insight '{ins.keyword}' matched ({level})",
                    role=EvidenceRole.SUPPORTING,
                ))
        else:
            evidence.append(EvidenceSpan(
                text=f"Missing: {ins.keyword}", source_field="(not found)",
                relevance=f"Insight '{ins.keyword}' not found",
                role=EvidenceRole.MISSING_EXPECTED,
            ))

    ratio = total / len(insights)
    parts = [f"{full} full"]
    if partial:
        parts.append(f"{partial} partial")
    notes.append(f"Key insights: {' + '.join(parts)} / {len(insights)}")
    return ratio, evidence, notes


# ---------------------------------------------------------------------------
# Support strength (NEW v0.4)
# ---------------------------------------------------------------------------

def _eval_support_strength(p: AgentResponse, graph: ReasoningGraph,
                           failures: list[FailureInstance]) -> tuple[float, list[EvidenceSpan], list[str]]:
    """Evaluate how well the final answer is grounded in reasoning steps.

    v0.4.2 hardening: distinguish three support levels:
    - load-bearing: step reaches a sub-conclusion that appears in the answer
    - supporting: step shares topic + direction with the answer
    - mentioned: step shares words but doesn't advance toward the answer

    Only load-bearing and supporting steps earn full credit.
    Pure lexical overlap ("mentioned") earns reduced credit.
    """
    evidence: list[EvidenceSpan] = []
    notes: list[str] = []

    if not p.steps or not p.final_answer:
        notes.append("No steps to evaluate support strength")
        return 0.0, evidence, notes

    score = 0.0
    answer_words = _content_words(p.final_answer, min_len=4)

    # --- 1. Classify each step's support level ---
    # Sub-conclusion indicators: words that signal a step reaches a result
    _CONCLUSION_MARKERS = (
        "therefore", "thus", "hence", "so ", "this means", "which means",
        "we can conclude", "this shows", "this proves", "this indicates",
        "the result is", "in conclusion", "consequently",
    )

    load_bearing = 0
    supporting = 0
    mentioned = 0
    best_lb_idx = -1
    best_lb_overlap = 0.0

    for i, step in enumerate(p.steps):
        step_lower = step.lower()
        step_words = _content_words(step, min_len=4)
        if not step_words or not answer_words:
            continue

        overlap_count = len(step_words & answer_words)
        overlap_ratio = overlap_count / len(answer_words)

        # Load-bearing: step contains a sub-conclusion marker AND shares
        # substantial content with the answer (the step drives the answer).
        has_conclusion = any(m in step_lower for m in _CONCLUSION_MARKERS)
        if has_conclusion and overlap_ratio >= 0.15:
            load_bearing += 1
            if overlap_ratio > best_lb_overlap:
                best_lb_overlap = overlap_ratio
                best_lb_idx = i
        elif overlap_ratio >= 0.20:
            # Supporting: shares topic direction with answer without being
            # a mere word-match (requires a minimum overlap bar).
            supporting += 1
        elif overlap_ratio >= 0.08:
            # Mentioned: shares some words but doesn't clearly support.
            mentioned += 1

    total = len(p.steps)
    notes.append(f"Support classification: {load_bearing} load-bearing, "
                 f"{supporting} supporting, {mentioned} mentioned / {total}")

    # --- 2. Score based on support mix ---
    # Load-bearing steps are the strongest signal (0.40 max)
    if load_bearing >= 2:
        score += 0.40
    elif load_bearing == 1:
        score += 0.25
    # Supporting steps add moderate credit (0.25 max)
    if supporting >= 2:
        score += 0.25
    elif supporting >= 1:
        score += 0.15
    # Mentioned-only steps get minimal credit (0.05 max)
    if mentioned > 0 and load_bearing == 0 and supporting == 0:
        score += 0.05
        notes.append("Steps mention answer words but don't clearly support it")

    # --- 3. Conclusion grounding from reasoning graph (0.15 max) ---
    if graph.conclusion_grounded:
        score += 0.15
        notes.append("Reasoning graph confirms conclusion grounding")
        evidence.append(EvidenceSpan(
            text=p.final_answer[:120], source_field="final_answer",
            relevance="Conclusion grounded by reasoning chain",
            role=EvidenceRole.SUPPORTING,
        ))
    else:
        notes.append("Reasoning graph: conclusion not well grounded")
        if load_bearing == 0 and supporting == 0:
            evidence.append(EvidenceSpan(
                text=p.final_answer[:120], source_field="final_answer",
                relevance="Conclusion not supported by steps",
                role=EvidenceRole.WEAKENING,
            ))
            failures.append(FailureInstance(
                category=FailureCategory.UNSUPPORTED_CONCLUSION.value,
                severity=FailureSeverity.MODERATE.value,
                description="Final answer lacks load-bearing or supporting step grounding",
                evidence=[EvidenceSpan(text=p.final_answer[:150], source_field="final_answer",
                                       relevance="Weakly grounded conclusion")],
                impact_on_score="support_strength",
            ))

    # --- 4. Support chain length (0.15 max, reduced from 0.30) ---
    chain = graph.support_chain_length
    if chain >= 3:
        score += 0.15
        notes.append(f"Support chain length: {chain}")
    elif chain >= 1:
        score += 0.08

    # --- Evidence ---
    if best_lb_idx >= 0:
        evidence.append(EvidenceSpan(
            text=p.steps[best_lb_idx][:150], source_field=f"steps[{best_lb_idx}]",
            relevance="Load-bearing step (reaches sub-conclusion used in answer)",
            role=EvidenceRole.SUPPORTING,
        ))

    return max(0.0, min(1.0, score)), evidence, notes


# ---------------------------------------------------------------------------
# Structural reasoning
# ---------------------------------------------------------------------------

def _eval_structural_reasoning(p: AgentResponse) -> tuple[float, list[EvidenceSpan], list[str]]:
    """Evaluate reasoning structure.

    v0.4.2 hardening: reduced dependence on raw step count and text length.
    Now emphasises:
    - Step utility: does each step contribute content toward the conclusion?
    - Redundancy penalty: heavily repeated steps are penalized.
    - Step coherence: each step should introduce new information.
    - Information density over raw length.
    Short, precise reasoning can now score as well as long reasoning.
    """
    evidence: list[EvidenceSpan] = []
    notes: list[str] = []
    if not p.steps:
        notes.append("No reasoning steps")
        return 0.0, evidence, notes

    score = 0.0
    n = len(p.steps)
    notes.append(f"{n} reasoning steps")

    # --- 1. Minimum structure (0.15 max, down from 0.4) ---
    # At least 2 steps required; beyond 3, no extra credit for count alone.
    if n >= 2:
        score += 0.15
    elif n == 1:
        score += 0.05

    # --- 2. Step utility: fraction of steps that contribute content
    #     words to the final answer (0.35 max) ---
    answer_words = _content_words(p.final_answer, min_len=4)
    if answer_words:
        contributing = 0
        for step in p.steps:
            step_words = _content_words(step, min_len=4)
            if step_words and len(step_words & answer_words) >= 1:
                contributing += 1
        utility_ratio = contributing / n
        score += utility_ratio * 0.35
        if utility_ratio >= 0.5:
            notes.append(f"Step utility: {contributing}/{n} steps contribute to answer")
        else:
            notes.append(f"Low step utility: {contributing}/{n} steps contribute")

    # --- 3. Step coherence / information gain (0.25 max) ---
    # Each step should introduce new content words not seen in prior steps.
    if n >= 2:
        seen_words: set[str] = set()
        novel_steps = 0
        for step in p.steps:
            step_words = _content_words(step, min_len=5)
            new_words = step_words - seen_words
            # Step is novel if it introduces at least 2 new content words
            if len(new_words) >= 2:
                novel_steps += 1
            seen_words.update(step_words)
        coherence_ratio = novel_steps / n
        score += coherence_ratio * 0.25
        if coherence_ratio >= 0.7:
            notes.append("Steps introduce new information consistently")
        elif coherence_ratio < 0.4:
            notes.append(f"Low coherence: {novel_steps}/{n} steps introduce new content")

    # --- 4. Redundancy penalty (up to -0.15) ---
    # Penalise steps that are near-duplicates of each other.
    redundant_count = 0
    for i in range(n):
        wi = _content_words(p.steps[i], min_len=5)
        if not wi:
            continue
        for j in range(i + 1, n):
            wj = _content_words(p.steps[j], min_len=5)
            if not wj:
                continue
            overlap = len(wi & wj) / min(len(wi), len(wj)) if min(len(wi), len(wj)) > 0 else 0
            if overlap > 0.7:
                redundant_count += 1
    if redundant_count > 0:
        penalty = min(0.15, redundant_count * 0.06)
        score -= penalty
        notes.append(f"Redundancy: {redundant_count} near-duplicate step pair(s)")

    # --- 5. Information density bonus (0.20 max) ---
    # Rewards concise, signal-dense steps over verbose padding.
    step_densities = [_signal_density(s) for s in p.steps]
    avg_density = sum(step_densities) / n if n else 0
    if avg_density > 0.55:
        score += 0.20
        notes.append(f"High step density ({avg_density:.2f})")
    elif avg_density > 0.45:
        score += 0.12
    else:
        score += 0.05
        notes.append(f"Low step density ({avg_density:.2f})")

    # --- Evidence ---
    if p.steps:
        # Most informative step (most novel content words)
        best_idx = max(range(n), key=lambda i: len(_content_words(p.steps[i], min_len=5)))
        evidence.append(EvidenceSpan(
            text=p.steps[best_idx][:150], source_field=f"steps[{best_idx}]",
            relevance="Most informative reasoning step",
            role=EvidenceRole.SUPPORTING,
        ))
        if redundant_count > 0 and n >= 2:
            # Show a redundant step as weakening evidence
            for i in range(n):
                wi = _content_words(p.steps[i], min_len=5)
                for j in range(i + 1, n):
                    wj = _content_words(p.steps[j], min_len=5)
                    if wi and wj and len(wi & wj) / min(len(wi), len(wj)) > 0.7:
                        evidence.append(EvidenceSpan(
                            text=p.steps[j][:150], source_field=f"steps[{j}]",
                            relevance="Redundant step (near-duplicate)",
                            role=EvidenceRole.WEAKENING,
                        ))
                        break
                else:
                    continue
                break

    return max(0.0, min(1.0, score)), evidence, notes


# ---------------------------------------------------------------------------
# Assumption discipline (v0.4: graph-aware)
# ---------------------------------------------------------------------------

def _eval_assumption_discipline(p: AgentResponse, graph: ReasoningGraph,
                                failures: list[FailureInstance]) -> tuple[float, list[EvidenceSpan], list[str]]:
    evidence: list[EvidenceSpan] = []
    notes: list[str] = []
    if not p.assumptions:
        notes.append("No assumptions listed")
        failures.append(FailureInstance(
            category=FailureCategory.NO_ASSUMPTIONS_STATED.value,
            severity=FailureSeverity.MINOR.value,
            description="No assumptions stated",
            impact_on_score="assumption_discipline",
        ))
        return 0.0, evidence, notes

    score = 0.3  # base
    n = len(p.assumptions)
    substantive = sum(1 for a in p.assumptions if len(a) > 20)
    if substantive >= 2:
        score += 0.2
        notes.append(f"{substantive}/{n} substantive assumptions")
    elif substantive >= 1:
        score += 0.1

    if 2 <= n <= 5:
        score += 0.15
    elif n > 5:
        score += 0.05
        notes.append(f"Many assumptions ({n})")

    # Domain relevance
    task_words = {"data", "statistic", "number", "rate", "probability", "sample",
                  "population", "independent", "random", "accurate", "complete"}
    domain_relevant = sum(1 for a in p.assumptions if any(tw in a.lower() for tw in task_words))
    if domain_relevant > 0:
        score += 0.15

    # v0.4: Penalize unused assumptions from graph
    n_unused = len(graph.unused_assumptions)
    if n_unused > 0:
        penalty = min(0.2, n_unused * 0.08)
        score -= penalty
        notes.append(f"{n_unused} unused assumption(s)")
        for idx in graph.unused_assumptions:
            claim = graph.claims[idx]
            evidence.append(EvidenceSpan(
                text=claim.text, source_field=claim.source_field,
                relevance="Declared but unused in reasoning",
                role=EvidenceRole.WEAKENING,
            ))
            failures.append(FailureInstance(
                category=FailureCategory.UNUSED_ASSUMPTION.value,
                severity=FailureSeverity.STYLISTIC.value,
                description=f"Assumption '{claim.text[:60]}...' is declared but not referenced in reasoning",
                evidence=[EvidenceSpan(text=claim.text, source_field=claim.source_field,
                                       relevance="Unused assumption")],
                impact_on_score="assumption_discipline",
            ))

    # Evidence: most substantive assumption
    if p.assumptions:
        best = max(p.assumptions, key=len)
        idx = p.assumptions.index(best)
        evidence.append(EvidenceSpan(
            text=best, source_field=f"assumptions[{idx}]",
            relevance="Most substantive assumption",
            role=EvidenceRole.SUPPORTING,
        ))

    return max(0.0, min(1.0, score)), evidence, notes


# ---------------------------------------------------------------------------
# Uncertainty handling (v0.4: graph-aware)
# ---------------------------------------------------------------------------

def _eval_uncertainty_handling(p: AgentResponse, task: Task, graph: ReasoningGraph,
                               failures: list[FailureInstance]) -> tuple[float, list[EvidenceSpan], list[str]]:
    evidence: list[EvidenceSpan] = []
    notes: list[str] = []
    score = 0.0

    if p.uncertainties:
        score += 0.3
        n = len(p.uncertainties)
        substantive = sum(1 for u in p.uncertainties if len(u) > 15)
        notes.append(f"{n} uncertainties ({substantive} substantive)")
        if substantive >= 1:
            score += 0.15
            best = max(p.uncertainties, key=len)
            idx = p.uncertainties.index(best)
            evidence.append(EvidenceSpan(
                text=best, source_field=f"uncertainties[{idx}]",
                relevance="Most substantive uncertainty",
                role=EvidenceRole.SUPPORTING,
            ))

        # v0.4: Penalize decorative uncertainties
        n_unaddressed = len(graph.unaddressed_uncertainties)
        if n_unaddressed > 0:
            penalty = min(0.15, n_unaddressed * 0.05)
            score -= penalty
            notes.append(f"{n_unaddressed} decorative uncertainty(ies)")
            for claim_idx in graph.unaddressed_uncertainties:
                claim = graph.claims[claim_idx]
                evidence.append(EvidenceSpan(
                    text=claim.text, source_field=claim.source_field,
                    relevance="Listed but never addressed in reasoning",
                    role=EvidenceRole.WEAKENING,
                ))
                failures.append(FailureInstance(
                    category=FailureCategory.DECORATIVE_UNCERTAINTY.value,
                    severity=FailureSeverity.STYLISTIC.value,
                    description=f"Uncertainty '{claim.text[:60]}...' is listed but not addressed",
                    evidence=[EvidenceSpan(text=claim.text, source_field=claim.source_field,
                                           relevance="Decorative uncertainty")],
                    impact_on_score="uncertainty_handling",
                ))
    else:
        notes.append("No uncertainties listed")
        failures.append(FailureInstance(
            category=FailureCategory.IGNORED_UNCERTAINTY.value,
            severity=FailureSeverity.MINOR.value,
            description="No uncertainties listed",
            impact_on_score="uncertainty_handling",
        ))

    # Confidence calibration
    confidence = confidence_value_if_valid(p.confidence, p.confidence_state)
    if confidence is not None and 0 < confidence < 1:
        evidence.append(EvidenceSpan(
            text=f"confidence: {confidence}", source_field="confidence",
            relevance="Stated confidence level",
        ))
        if task.difficulty.value == "hard" and confidence < 0.85:
            score += 0.35
            notes.append(f"Confidence {confidence} — appropriately cautious for hard task")
        elif confidence >= 0.95:
            score += 0.05
            notes.append(f"Confidence {confidence} — very high")
            failures.append(FailureInstance(
                category=FailureCategory.CONFIDENCE_MISMATCH.value,
                severity=FailureSeverity.MINOR.value,
                description=f"Very high confidence ({confidence}) on {task.difficulty.value} task",
                evidence=[EvidenceSpan(text=f"confidence: {confidence}", source_field="confidence",
                                        relevance="High confidence value")],
                impact_on_score="uncertainty_handling",
            ))
        else:
            score += 0.2
            notes.append(f"Confidence {confidence}")

    return max(0.0, min(1.0, score)), evidence, notes


# ---------------------------------------------------------------------------
# Alternative hypothesis quality
# ---------------------------------------------------------------------------

def _eval_alt_hypothesis_quality(p: AgentResponse,
                                 failures: list[FailureInstance]) -> tuple[float, list[EvidenceSpan], list[str]]:
    evidence: list[EvidenceSpan] = []
    notes: list[str] = []
    if not p.alternative_hypotheses:
        notes.append("No alternative hypotheses")
        return 0.0, evidence, notes

    score = 0.3
    n = len(p.alternative_hypotheses)
    notes.append(f"{n} alternative hypotheses considered")

    # Quality: rejection reasoning
    rejection_words = ("because", "since", "however", "but", "reject", "unlikely",
                       "incorrect", "wrong", "doesn't", "does not", "fails", "not")
    reasoned = sum(1 for h in p.alternative_hypotheses
                   if any(w in h.lower() for w in rejection_words))
    if reasoned > 0:
        score += 0.25 * min(1.0, reasoned / max(n, 1))
        notes.append(f"{reasoned}/{n} include rejection reasoning")

    # Substantive alternatives
    substantive = [h for h in p.alternative_hypotheses if len(h) > 40]
    if substantive:
        score += 0.25
        best = max(substantive, key=len)
        idx = p.alternative_hypotheses.index(best)
        evidence.append(EvidenceSpan(
            text=best[:200], source_field=f"alternative_hypotheses[{idx}]",
            relevance="Most substantive alternative hypothesis",
            role=EvidenceRole.SUPPORTING,
        ))

    # Penalize weak/short alternatives
    weak = sum(1 for h in p.alternative_hypotheses if len(h) < 30)
    if weak > 0:
        score -= weak * 0.05
        notes.append(f"{weak} weak/short alternative(s)")
        for i, h in enumerate(p.alternative_hypotheses):
            if len(h) < 30:
                failures.append(FailureInstance(
                    category=FailureCategory.WEAK_ALTERNATIVE_HYPOTHESIS.value,
                    severity=FailureSeverity.STYLISTIC.value,
                    description=f"Alternative hypothesis {i+1} is too brief ({len(h)} chars)",
                    evidence=[EvidenceSpan(text=h, source_field=f"alternative_hypotheses[{i}]",
                                           relevance="Brief alternative")],
                    impact_on_score="alternative_hypothesis_quality",
                ))

    # Genuine diversity
    if n >= 2:
        answer_words = _content_words(p.final_answer)
        diverse = 0
        for h in p.alternative_hypotheses:
            h_words = _content_words(h)
            if h_words and answer_words:
                overlap = len(h_words & answer_words) / len(h_words)
                if overlap < 0.5:
                    diverse += 1
        if diverse >= 2:
            score += 0.2
            notes.append(f"{diverse}/{n} genuinely diverse alternatives")

    return max(0.0, min(1.0, score)), evidence, notes


# ---------------------------------------------------------------------------
# Self-monitoring quality (v0.4: graph-aware)
# ---------------------------------------------------------------------------

def _eval_self_monitoring(p: AgentResponse, task: Task, graph: ReasoningGraph,
                          failures: list[FailureInstance]) -> tuple[float, list[EvidenceSpan], list[str]]:
    evidence: list[EvidenceSpan] = []
    notes: list[str] = []
    if not p.self_check:
        notes.append("No self-verification")
        return 0.0, evidence, notes

    score = 0.2
    n = len(p.self_check)
    notes.append(f"{n} self-check items")

    # Classify each self-check
    deep_count = 0
    arith_count = 0
    fluff_count = 0
    for sc in p.self_check:
        cat = classify_self_check(sc)
        if cat == "deep":
            deep_count += 1
        elif cat == "arithmetic":
            arith_count += 1
        else:
            fluff_count += 1

    notes.append(f"Self-check quality: {deep_count} deep, {arith_count} arithmetic, {fluff_count} fluff")

    # Score based on quality
    score += deep_count * 0.2
    score += arith_count * 0.1
    score -= fluff_count * 0.05

    if fluff_count > 0 and deep_count == 0 and arith_count == 0:
        failures.append(FailureInstance(
            category=FailureCategory.DECORATIVE_SELF_CHECK.value,
            severity=FailureSeverity.MINOR.value,
            description=f"All {n} self-checks appear to be fluff — no substantive verification",
            evidence=[EvidenceSpan(text=p.self_check[0], source_field="self_check[0]",
                                   relevance="Example fluff self-check")],
            impact_on_score="self_monitoring_quality",
        ))

    # Trap awareness
    check_text = " ".join(p.self_check).lower()
    if task.common_errors:
        trap_hits = sum(1 for err in task.common_errors if err.lower() in check_text)
        if trap_hits > 0:
            score += 0.3
            notes.append(f"Self-check addresses {trap_hits} known traps")

    # Evidence: best self-check
    substantive = [s for s in p.self_check if len(s) > 25]
    if substantive:
        best = max(substantive, key=len)
        idx = p.self_check.index(best)
        evidence.append(EvidenceSpan(
            text=best[:200], source_field=f"self_check[{idx}]",
            relevance="Most substantive self-verification step",
            role=EvidenceRole.SUPPORTING,
        ))

    # Fluff evidence
    if fluff_count > 0:
        for i, sc in enumerate(p.self_check):
            if classify_self_check(sc) == "fluff":
                evidence.append(EvidenceSpan(
                    text=sc, source_field=f"self_check[{i}]",
                    relevance="Fluff self-check",
                    role=EvidenceRole.WEAKENING,
                ))
                break

    return max(0.0, min(1.0, score)), evidence, notes


# ---------------------------------------------------------------------------
# Mechanism quality (NEW v0.4)
# ---------------------------------------------------------------------------

_MECHANISM_WORDS = ("because", "causes", "leads to", "results in", "driven by",
                    "explained by", "due to", "reason is", "mechanism is",
                    "this happens when", "this occurs because")

_CONCEPT_NAMES = ("paradox", "fallacy", "bias", "effect", "theorem",
                  "principle", "law", "heuristic", "phenomenon")


def _eval_mechanism_quality(p: AgentResponse, task: Task, text: str,
                            failures: list[FailureInstance],
                            mech_analysis: MechanismAnalysis | None = None,
                            ) -> tuple[float, list[EvidenceSpan], list[str]]:
    """Evaluate whether the agent explains the causal mechanism, not just names the concept.

    v0.4.1: Uses MechanismAnalysis for 3-level distinction:
    - naming a concept
    - describing a mechanism
    - grounding the mechanism to the specific case
    """
    evidence: list[EvidenceSpan] = []
    notes: list[str] = []

    if not p.steps:
        notes.append("No steps to evaluate mechanism")
        return 0.0, evidence, notes

    score = 0.0
    combined = text

    # Use MechanismAnalysis if available (v0.4.1)
    if mech_analysis:
        named = mech_analysis.concept_named
        described = mech_analysis.mechanism_described
        grounded = mech_analysis.mechanism_grounded_to_case
    else:
        named = any(ind in combined for ind in _CONCEPT_NAMES)
        described = any(ind in combined for ind in _MECHANISM_WORDS)
        grounded = False

    # 3-level scoring (v0.4.1)
    if named and described and grounded:
        score += 0.6
        notes.append("Names concept + describes mechanism + grounds to case")
        if mech_analysis and mech_analysis.grounding_sentences:
            evidence.append(EvidenceSpan(
                text=mech_analysis.grounding_sentences[0][:150],
                source_field="(mechanism analysis)",
                relevance="Case-grounded mechanism explanation",
                role=EvidenceRole.SUPPORTING,
            ))
    elif named and described:
        score += 0.4
        notes.append("Names concept + describes mechanism (not grounded to case)")
        if mech_analysis and mech_analysis.mechanism_sentences:
            evidence.append(EvidenceSpan(
                text=mech_analysis.mechanism_sentences[0][:150],
                source_field="(mechanism analysis)",
                relevance="Mechanism description without case grounding",
                role=EvidenceRole.SUPPORTING,
            ))
    elif named and not described:
        score += 0.15
        notes.append("Names concept but does not describe mechanism")
        failures.append(FailureInstance(
            category=FailureCategory.NAMED_NOT_EXPLAINED.value,
            severity=FailureSeverity.MODERATE.value,
            description="Names the phenomenon but does not explain the causal mechanism",
            evidence=[EvidenceSpan(text=p.final_answer[:150], source_field="final_answer",
                                   relevance="Names concept without mechanism")],
            impact_on_score="mechanism_quality",
        ))
    elif described and not named:
        score += 0.3
        notes.append("Describes mechanism but does not name concept")
        if mech_analysis and mech_analysis.mechanism_sentences:
            evidence.append(EvidenceSpan(
                text=mech_analysis.mechanism_sentences[0][:150],
                source_field="(mechanism analysis)",
                relevance="Mechanism description",
                role=EvidenceRole.SUPPORTING,
            ))
    else:
        notes.append("Neither names concept nor explains mechanism")

    # Task-specific mechanism terms
    if task.expected_mechanism_terms:
        found = sum(1 for t in task.expected_mechanism_terms if t.lower() in combined)
        total = len(task.expected_mechanism_terms)
        ratio = found / total
        score += ratio * 0.25
        notes.append(f"Mechanism terms: {found}/{total}")

    # Depth: does explanation go beyond one sentence?
    if mech_analysis:
        n_mech_sents = len(mech_analysis.mechanism_sentences)
        if n_mech_sents >= 2:
            score += 0.15
            notes.append(f"Multi-step mechanism ({n_mech_sents} sentences)")
    else:
        mechanism_steps = [s for s in p.steps if any(w in s.lower() for w in _MECHANISM_WORDS)]
        if len(mechanism_steps) >= 2:
            score += 0.15
            notes.append("Multi-step mechanism explanation")

    return min(1.0, score), evidence, notes


# ---------------------------------------------------------------------------
# Communication efficiency
# ---------------------------------------------------------------------------

def _eval_communication(p: AgentResponse, text: str,
                        failures: list[FailureInstance]) -> tuple[float, list[EvidenceSpan], list[str]]:
    evidence: list[EvidenceSpan] = []
    notes: list[str] = []
    if not text.strip():
        return 0.0, evidence, notes

    score = 0.0
    density = _signal_density(text)
    words = len(text.split())
    notes.append(f"Signal density: {density:.2f}, {words} words")

    if density > 0.55:
        score += 0.5
    elif density > 0.45:
        score += 0.3
    else:
        score += 0.1

    if 100 <= words <= 500:
        score += 0.4
    elif words <= 800:
        score += 0.25
    else:
        score += 0.1
        notes.append(f"Verbose ({words} words)")
        failures.append(FailureInstance(
            category=FailureCategory.OVERVERBOSE_WITHOUT_GAIN.value,
            severity=FailureSeverity.STYLISTIC.value,
            description=f"Output is verbose ({words} words, density {density:.2f})",
            evidence=[EvidenceSpan(text=f"{words} words, density {density:.2f}",
                                    source_field="(computed)", relevance="Length/density metrics")],
            impact_on_score="communication_efficiency",
        ))

    if all([p.final_answer, p.assumptions, p.steps]):
        score += 0.1

    return min(1.0, score), evidence, notes


# ---------------------------------------------------------------------------
# v0.4.3: Load-bearing step analysis
# ---------------------------------------------------------------------------

def _classify_load_bearing_steps(
    steps: list[str], final_answer: str,
) -> list[bool]:
    """Classify each step as load-bearing or decorative.

    A step is load-bearing if:
    - It appears late in the chain AND has high overlap with the final answer, OR
    - It introduces a key number that appears in the final answer, OR
    - A later step references content from this step (forward dependency).

    Returns a list of booleans, one per step.
    """
    n = len(steps)
    if not n or not final_answer:
        return [False] * n

    answer_words = _content_words(final_answer, min_len=4)
    # Extract numbers from the final answer for numeric tracing
    answer_numbers = set(re.findall(r"\d+(?:\.\d+)?", final_answer))

    is_lb = [False] * n

    for i, step in enumerate(steps):
        step_words = _content_words(step, min_len=4)
        step_numbers = set(re.findall(r"\d+(?:\.\d+)?", step))

        # Criterion 1: Late step (last 60%) with substantial overlap to answer
        if answer_words and step_words:
            overlap = len(step_words & answer_words) / len(answer_words)
            is_late = i >= n * 0.4
            if is_late and overlap >= 0.15:
                is_lb[i] = True

        # Criterion 2: Introduces a number that appears in the final answer
        # (and the number wasn't in an earlier step — this step is the source)
        if answer_numbers and step_numbers:
            shared = step_numbers & answer_numbers
            for num in shared:
                # Check if this is the FIRST step introducing this number
                earlier_has_it = any(
                    num in re.findall(r"\d+(?:\.\d+)?", steps[j])
                    for j in range(i)
                )
                if not earlier_has_it:
                    is_lb[i] = True
                    break

        # Criterion 3: Has a conclusion marker pointing toward the answer
        step_lower = step.lower()
        _CONCLUSION_MARKERS = (
            "therefore", "thus", "hence", "this means", "which means",
            "we can conclude", "this shows", "consequently",
        )
        if any(m in step_lower for m in _CONCLUSION_MARKERS):
            if answer_words and step_words and len(step_words & answer_words) >= 1:
                is_lb[i] = True

    # Criterion 4 (transitive): If a later load-bearing step uses a number
    # introduced by this step, then this step is also load-bearing.
    # One backward pass is enough for direct dependencies.
    for i in range(n):
        if is_lb[i]:
            continue
        step_numbers = set(re.findall(r"\d+(?:\.\d+)?", steps[i]))
        if not step_numbers:
            continue
        for j in range(i + 1, n):
            if not is_lb[j]:
                continue
            later_numbers = set(re.findall(r"\d+(?:\.\d+)?", steps[j]))
            # If a later LB step uses a number from this step (and it's
            # non-trivial — not single digits that appear everywhere)
            shared = step_numbers & later_numbers
            significant = {num for num in shared if len(num) >= 2 or float(num) >= 10}
            if significant:
                is_lb[i] = True
                break

    return is_lb


def _build_reasoning_integrity(
    p: AgentResponse,
    task: Task,
    correctness: float,
    step_checks: list[StepCheckResult],
    failures: list[FailureInstance],
) -> dict:
    """v0.4.3: Assess reasoning integrity — detect right-answer-wrong-reasoning.

    Returns a dict with:
      - classification: "well_supported" | "brittle" | "accidental"
      - load_bearing_mask: list[bool] per step
      - failed_load_bearing: list of (step_index, explanation) for broken LB steps
      - n_intermediate_errors: int
      - n_load_bearing_errors: int
    """
    steps = p.steps
    result = {
        "classification": "well_supported",
        "load_bearing_mask": [],
        "failed_load_bearing": [],
        "n_intermediate_errors": 0,
        "n_load_bearing_errors": 0,
    }

    if not steps:
        return result

    lb_mask = _classify_load_bearing_steps(steps, p.final_answer)
    result["load_bearing_mask"] = lb_mask

    # Count intermediate errors and which are load-bearing
    failed_checks = [c for c in step_checks if not c.is_correct]
    result["n_intermediate_errors"] = len(failed_checks)

    for check in failed_checks:
        is_lb = lb_mask[check.step_index] if check.step_index < len(lb_mask) else False

        # Always generate a failure for intermediate errors
        failures.append(FailureInstance(
            category=FailureCategory.INTERMEDIATE_NUMERIC_ERROR.value,
            severity=FailureSeverity.MAJOR.value if is_lb else FailureSeverity.MINOR.value,
            description=(
                f"Intermediate calculation error in step {check.step_index}: "
                f"{check.explanation}"
                + (" (LOAD-BEARING)" if is_lb else " (decorative)")
            ),
            evidence=check.evidence,
            impact_on_score="structural_reasoning, support_strength",
        ))

        if is_lb:
            result["failed_load_bearing"].append(
                (check.step_index, check.explanation)
            )
            result["n_load_bearing_errors"] += 1

    # Classify reasoning integrity
    answer_is_correct = correctness >= 0.7

    if answer_is_correct and result["n_load_bearing_errors"] >= 1:
        # Correct answer but a load-bearing step is numerically wrong
        result["classification"] = "accidental"
        failures.append(FailureInstance(
            category=FailureCategory.RIGHT_ANSWER_WRONG_REASONING.value,
            severity=FailureSeverity.MAJOR.value,
            description=(
                f"Final answer is correct, but {result['n_load_bearing_errors']} "
                f"load-bearing step(s) contain verified arithmetic errors"
            ),
            evidence=[EvidenceSpan(
                text=result["failed_load_bearing"][0][1],
                source_field=f"steps[{result['failed_load_bearing'][0][0]}]",
                relevance="Load-bearing step with arithmetic error",
                role=EvidenceRole.CONTRADICTORY,
            )],
            impact_on_score="support_strength, structural_reasoning, self_monitoring_quality",
        ))
        failures.append(FailureInstance(
            category=FailureCategory.ACCIDENTAL_CORRECTNESS.value,
            severity=FailureSeverity.MODERATE.value,
            description="Correct final answer likely reached despite flawed reasoning path",
            evidence=[EvidenceSpan(
                text=p.final_answer[:150],
                source_field="final_answer",
                relevance="Correct answer with unreliable derivation",
            )],
            impact_on_score="support_strength",
        ))
    elif answer_is_correct and result["n_intermediate_errors"] >= 1 and result["n_load_bearing_errors"] == 0:
        # Correct answer, errors only in decorative steps
        result["classification"] = "brittle"
    # else: well_supported (no errors found)

    # Check for unsupported load-bearing steps (no numeric error, but no task data backing)
    if answer_is_correct and task.expected_answer:
        n_lb = sum(lb_mask)
        if n_lb == 0 and len(steps) >= 2:
            # No load-bearing steps at all — answer comes from nowhere
            result["classification"] = "brittle"
            failures.append(FailureInstance(
                category=FailureCategory.UNSUPPORTED_INTERMEDIATE_STEP.value,
                severity=FailureSeverity.MODERATE.value,
                description="No reasoning step is load-bearing — final answer lacks traceable derivation",
                evidence=[EvidenceSpan(
                    text=p.final_answer[:150],
                    source_field="final_answer",
                    relevance="Answer without load-bearing support",
                )],
                impact_on_score="support_strength, structural_reasoning",
            ))

    return result


# ---------------------------------------------------------------------------
# Forensic flags (evolved from hidden_weaknesses)
# ---------------------------------------------------------------------------

def _build_forensic_flags(
    p: AgentResponse, task: Task, graph: ReasoningGraph,
    consistency_findings: list[ConsistencyFinding],
    correctness: float, insight_score: float,
    structural_score: float, support_score: float,
    mechanism_score: float, self_monitoring_score: float,
    claim_results: list[ClaimCheckResult] | None = None,
    mech_analysis: MechanismAnalysis | None = None,
    grounding: GroundingAudit | None = None,
    reasoning_integrity: dict | None = None,
    step_checks: list[StepCheckResult] | None = None,
) -> list[ForensicFlag]:
    flags: list[ForensicFlag] = []

    # From consistency findings
    for f in consistency_findings:
        if f.status in ("warning", "fail") and f.check_type == "self_correction":
            flags.append(ForensicFlag(
                flag_type="reasoning_slip",
                description=f"Reasoning slip: {f.description}",
                evidence=f.evidence, severity="minor",
            ))
        elif f.status == "fail" and f.check_type == "contradiction":
            flags.append(ForensicFlag(
                flag_type="internal_contradiction",
                description=f"Internal contradiction: {f.description}",
                evidence=f.evidence, severity="major",
            ))
        elif f.check_type == "confidence_uncertainty" and f.status == "warning":
            flags.append(ForensicFlag(
                flag_type="calibration_gap",
                description=f.description,
                evidence=f.evidence, severity="minor",
            ))

    # Correct but shallow
    if correctness > 0.8 and insight_score < 0.5:
        flags.append(ForensicFlag(
            flag_type="pattern_match_suspect",
            description="Correct answer with shallow insight coverage — possible pattern-match response",
            evidence=[EvidenceSpan(
                text=p.final_answer[:100], source_field="final_answer",
                relevance="Correct but shallow",
            )],
            severity="moderate",
        ))

    # Correct but brittle
    if correctness > 0.8 and structural_score < 0.4:
        flags.append(ForensicFlag(
            flag_type="brittle_correctness",
            description="Right answer with weak reasoning chain — fragile under perturbation",
            severity="major",
        ))

    # Correct but weak mechanism
    if correctness > 0.8 and mechanism_score < 0.3:
        flags.append(ForensicFlag(
            flag_type="weak_mechanism",
            description="Correct answer but weak mechanism explanation — answer may not generalize",
            evidence=[EvidenceSpan(
                text=p.final_answer[:100], source_field="final_answer",
                relevance="Correct without mechanism",
            )],
            severity="moderate",
        ))

    # Correct but unsupported leap
    if correctness > 0.8 and support_score < 0.3:
        flags.append(ForensicFlag(
            flag_type="unsupported_leap",
            description="Correct answer with weak support chain — final answer may be an unsupported leap",
            severity="major",
        ))

    # Strong reasoning but weak self-audit
    if structural_score > 0.7 and self_monitoring_score < 0.3:
        flags.append(ForensicFlag(
            flag_type="blind_spot",
            description="Strong reasoning but weak self-monitoring — may miss own errors",
            severity="minor",
        ))

    # Wrong but high-quality reasoning
    if correctness < 0.3 and structural_score > 0.6:
        flags.append(ForensicFlag(
            flag_type="well_reasoned_wrong",
            description="Wrong answer but structured reasoning — may have a subtle logic error",
            evidence=[EvidenceSpan(
                text=p.final_answer[:100], source_field="final_answer",
                relevance="Wrong despite good reasoning",
            )],
            severity="major",
        ))

    # Mechanism naming gap
    if p.steps:
        step_text = " ".join(p.steps).lower()
        has_mechanism = any(w in step_text for w in _MECHANISM_WORDS)
        has_names = any(w in step_text for w in _CONCEPT_NAMES)
        if has_mechanism and not has_names:
            for i, s in enumerate(p.steps):
                if any(w in s.lower() for w in ("because", "due to", "explained by")):
                    flags.append(ForensicFlag(
                        flag_type="unnamed_mechanism",
                        description="Describes mechanism without naming the concept — under-explicit",
                        evidence=[EvidenceSpan(
                            text=s[:150], source_field=f"steps[{i}]",
                            relevance="Functional description without concept name",
                        )],
                        severity="stylistic",
                    ))
                    break

    # Easy task robustness caveat
    if task.difficulty.value == "easy" and correctness > 0.9:
        flags.append(ForensicFlag(
            flag_type="easy_task_caveat",
            description="Answer robust only because task is easy — performance on harder tasks may differ",
            severity="stylistic",
        ))

    # v0.4.1: Claim contradiction flags
    if claim_results:
        contradictions = [cr for cr in claim_results if cr.truth_status == ClaimTruthStatus.CONTRADICTED]
        if contradictions:
            flags.append(ForensicFlag(
                flag_type="numeric_verbal_contradiction",
                description=f"{len(contradictions)} verbal claim(s) contradict numeric facts — local truth failure",
                evidence=[EvidenceSpan(
                    text=contradictions[0].explanation[:150],
                    source_field=contradictions[0].claim.source_field,
                    relevance="First contradiction found",
                    role=EvidenceRole.CONTRADICTORY,
                )],
                severity="critical" if len(contradictions) >= 2 else "major",
            ))

    # v0.4.1: Grounding weakness flags
    if grounding and grounding.total_conclusion_claims > 0:
        if grounding.unsupported > 0:
            flags.append(ForensicFlag(
                flag_type="unsupported_conclusion_claims",
                description=f"{grounding.unsupported}/{grounding.total_conclusion_claims} conclusion claims lack step support",
                evidence=[EvidenceSpan(
                    text=grounding.unsupported_claims[0][:150] if grounding.unsupported_claims else "",
                    source_field="final_answer",
                    relevance="Unsupported conclusion claim",
                    role=EvidenceRole.WEAKENING,
                )],
                severity="moderate",
            ))
        if grounding.contradicted > 0:
            flags.append(ForensicFlag(
                flag_type="self_contradicting_conclusion",
                description=f"{grounding.contradicted} conclusion claim(s) contradicted by own reasoning steps",
                severity="major",
            ))

    # v0.4.1: Mechanism completeness flag
    if mech_analysis:
        if mech_analysis.concept_named and not mech_analysis.mechanism_grounded_to_case:
            flags.append(ForensicFlag(
                flag_type="ungrounded_mechanism",
                description="Mechanism named/described but not connected to case-specific data",
                evidence=[EvidenceSpan(
                    text=", ".join(mech_analysis.named_concepts),
                    source_field="(mechanism analysis)",
                    relevance="Named but not grounded to case",
                )],
                severity="moderate",
            ))

    # v0.4.1: Failed self-audit flag
    has_failed_audit = any(
        f.check_type == "failed_self_audit" and f.status == "fail"
        for f in consistency_findings
    )
    if has_failed_audit:
        flags.append(ForensicFlag(
            flag_type="failed_self_audit",
            description="Self-check affirms correctness despite detectable contradictions — self-monitoring blind spot",
            severity="major",
        ))

    # v0.4.3: Reasoning integrity flags
    if reasoning_integrity:
        classification = reasoning_integrity.get("classification", "well_supported")
        n_lb_errors = reasoning_integrity.get("n_load_bearing_errors", 0)
        n_int_errors = reasoning_integrity.get("n_intermediate_errors", 0)

        if classification == "accidental":
            flags.append(ForensicFlag(
                flag_type="accidental_correctness",
                description=(
                    f"Correct answer reached despite {n_lb_errors} arithmetic error(s) "
                    f"in load-bearing step(s) — likely accidental"
                ),
                severity="major",
            ))
        elif classification == "brittle" and n_int_errors > 0:
            flags.append(ForensicFlag(
                flag_type="brittle_reasoning_path",
                description=(
                    f"{n_int_errors} intermediate arithmetic error(s) in decorative steps — "
                    f"reasoning path is fragile but load-bearing steps are intact"
                ),
                severity="moderate",
            ))

    if step_checks:
        failed = [c for c in step_checks if not c.is_correct]
        if failed:
            flags.append(ForensicFlag(
                flag_type="intermediate_calculation_errors",
                description=f"{len(failed)} verified intermediate calculation error(s) found",
                evidence=[EvidenceSpan(
                    text=failed[0].claim_text,
                    source_field=failed[0].source_field,
                    relevance=failed[0].explanation,
                    role=EvidenceRole.CONTRADICTORY,
                )],
                severity="major" if len(failed) >= 2 else "moderate",
            ))

    return flags


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# v0.4.2: Confidence label assignment for failures
# ---------------------------------------------------------------------------
# Uses unified mapping from schemas.FAILURE_CONFIDENCE_MAP.


def _assign_failure_confidence(failures: list[FailureInstance]) -> None:
    """Assign confidence labels to failure instances."""
    for f in failures:
        f.confidence = get_confidence_label(f.category, FAILURE_CONFIDENCE_MAP)


def evaluate_run(task: Task, run_id: str, results: list[AgentResult]) -> RunRecord:
    evaluated = [evaluate_result(task, r) for r in results]
    record = RunRecord(run_id=run_id, task=task, results=evaluated)
    if task.task_type == TaskType.STUDY_FORENSICS:
        from agent_arena.phase9_pipeline import refresh_run_phase9
        record = refresh_run_phase9(record)
    return record
