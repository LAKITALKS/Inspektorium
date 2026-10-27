"""Forensic Consistency 2.5 of the Inspektorium audit runtime.

Checks (in priority order):
1. Self-correction detection
2. Final answer <-> key claims alignment
3. Key claims <-> steps alignment
4. Assumptions <-> reasoning consistency
5. Confidence <-> uncertainties coherence
6. Conservative contradiction heuristics
7. Assumption usage audit (v0.4)
8. Uncertainty resolution audit (v0.4)
9. Self-check depth audit (v0.4)
10. Alternative hypothesis quality audit (v0.4)
11. Claim drift detection (v0.4)
12. Mechanism gap detection (v0.4)
13. Numeric-verbal reversal detection (NEW v0.4.1)
14. Failed self-audit detection (NEW v0.4.1)
"""

from __future__ import annotations

from inspektorium.audit.checks.confidence_validity import confidence_value_if_valid
from inspektorium.audit.schemas import (
    CONSISTENCY_CONFIDENCE_MAP,
    AgentResponse,
    ClaimCheckResult,
    ClaimTruthStatus,
    ConsistencyFinding,
    EvidenceSpan,
    Task,
    get_confidence_label,
)


def run_consistency_checks(
    parsed: AgentResponse,
    task: Task,
    claim_check_results: list[ClaimCheckResult] | None = None,
) -> list[ConsistencyFinding]:
    findings: list[ConsistencyFinding] = []
    findings.extend(_check_self_corrections(parsed))
    findings.extend(_check_answer_claims_alignment(parsed))
    findings.extend(_check_claims_steps_alignment(parsed))
    findings.extend(_check_assumptions_reasoning(parsed))
    findings.extend(_check_confidence_uncertainty(parsed, task))
    findings.extend(_check_conservative_contradictions(parsed))
    # v0.4 forensic checks
    findings.extend(_check_assumption_usage(parsed))
    findings.extend(_check_uncertainty_resolution(parsed))
    findings.extend(_check_self_check_depth(parsed))
    findings.extend(_check_alternative_hypothesis_quality(parsed))
    findings.extend(_check_claim_drift(parsed))
    findings.extend(_check_mechanism_gap(parsed, task))
    # v0.4.1 hardening checks
    if claim_check_results:
        findings.extend(_check_numeric_verbal_reversals(claim_check_results))
        findings.extend(_check_failed_self_audit(parsed, claim_check_results))

    # v0.4.2: Assign confidence labels to all findings
    _assign_confidence_labels(findings)
    return findings


# ---------------------------------------------------------------------------
# v0.4.2: Confidence label assignment
# ---------------------------------------------------------------------------
# Uses unified mapping from schemas.CONSISTENCY_CONFIDENCE_MAP.


def _assign_confidence_labels(findings: list[ConsistencyFinding]) -> None:
    """Assign confidence labels to consistency findings based on check type."""
    for f in findings:
        f.confidence = get_confidence_label(f.check_type, CONSISTENCY_CONFIDENCE_MAP)


# ---------------------------------------------------------------------------
# Shared utilities
# ---------------------------------------------------------------------------


def _content_words(text: str, min_len: int = 4) -> set[str]:
    stopwords = {
        "about",
        "which",
        "would",
        "could",
        "should",
        "there",
        "their",
        "these",
        "those",
        "being",
        "where",
        "other",
        "because",
        "since",
        "however",
        "while",
        "though",
        "have",
        "this",
        "that",
        "what",
        "when",
        "than",
        "then",
        "also",
        "just",
        "more",
        "some",
        "very",
        "each",
        "they",
        "been",
        "were",
        "does",
        "only",
    }
    return {w for w in text.lower().split() if len(w) >= min_len and w not in stopwords}


# ---------------------------------------------------------------------------
# 1. Self-correction detection
# ---------------------------------------------------------------------------

_STRONG_MARKERS = (
    "let me recalculate",
    "let me re-check",
    "wait,",
    "wait -",
    "i was wrong",
    "that's incorrect",
    "this is wrong",
    "not correct",
    "oops",
    "scratch that",
    "correction:",
    "i made a mistake",
    "let me redo",
    "that was wrong",
)


def _check_self_corrections(p: AgentResponse) -> list[ConsistencyFinding]:
    findings = []
    for i, step in enumerate(p.steps):
        low = step.lower()
        for marker in _STRONG_MARKERS:
            if marker in low:
                findings.append(
                    ConsistencyFinding(
                        check_type="self_correction",
                        status="warning",
                        description=f"Self-correction detected in step {i + 1}: agent backtracks using '{marker.strip(',- ')}'",
                        evidence=[
                            EvidenceSpan(
                                text=step,
                                source_field=f"steps[{i}]",
                                claim_type="correction",
                                relevance=f"Contains self-correction marker '{marker.strip(',- ')}'",
                            )
                        ],
                    )
                )
                break
    return findings


# ---------------------------------------------------------------------------
# 2. Final answer <-> key claims alignment
# ---------------------------------------------------------------------------


def _check_answer_claims_alignment(p: AgentResponse) -> list[ConsistencyFinding]:
    if not p.key_claims:
        return []

    findings = []
    answer_low = p.final_answer.lower()

    for i, claim in enumerate(p.key_claims):
        content = _content_words(claim)
        if len(content) < 3:
            continue

        overlap = sum(1 for w in content if w in answer_low)
        ratio = overlap / len(content)

        if ratio < 0.15:
            findings.append(
                ConsistencyFinding(
                    check_type="answer_claim_alignment",
                    status="warning",
                    description=f"Key claim {i + 1} has low overlap with final answer ({overlap}/{len(content)} content words)",
                    evidence=[
                        EvidenceSpan(
                            text=claim,
                            source_field=f"key_claims[{i}]",
                            claim_type="assertion",
                            relevance="Claim not reflected in answer",
                        ),
                        EvidenceSpan(
                            text=p.final_answer[:200],
                            source_field="final_answer",
                            relevance="Answer text for comparison",
                        ),
                    ],
                )
            )

    return findings


# ---------------------------------------------------------------------------
# 3. Key claims <-> steps alignment
# ---------------------------------------------------------------------------


def _check_claims_steps_alignment(p: AgentResponse) -> list[ConsistencyFinding]:
    if not p.key_claims or not p.steps:
        return []

    findings = []
    all_steps_text = " ".join(p.steps).lower()

    for i, claim in enumerate(p.key_claims):
        content = _content_words(claim)
        if len(content) < 3:
            continue

        overlap = sum(1 for w in content if w in all_steps_text)
        ratio = overlap / len(content)

        if ratio < 0.2:
            findings.append(
                ConsistencyFinding(
                    check_type="claim_step_alignment",
                    status="warning",
                    description=f"Key claim {i + 1} not well supported in reasoning steps ({overlap}/{len(content)} content words found)",
                    evidence=[
                        EvidenceSpan(
                            text=claim,
                            source_field=f"key_claims[{i}]",
                            claim_type="assertion",
                            relevance="Claim lacks step support",
                        ),
                    ],
                )
            )

    return findings


# ---------------------------------------------------------------------------
# 4. Assumptions <-> reasoning consistency
# ---------------------------------------------------------------------------


def _check_assumptions_reasoning(p: AgentResponse) -> list[ConsistencyFinding]:
    if not p.assumptions or not p.steps:
        return []

    findings = []
    all_steps_text = " ".join(p.steps).lower()

    for i, assumption in enumerate(p.assumptions):
        a_low = assumption.lower()
        negation_patterns = [
            (f"not {phrase}", phrase)
            for phrase in _extract_short_phrases(a_low)
            if len(phrase) > 8
        ]

        for negated, original in negation_patterns:
            if negated in all_steps_text and original in a_low:
                for j, step in enumerate(p.steps):
                    if negated in step.lower():
                        findings.append(
                            ConsistencyFinding(
                                check_type="assumption_reasoning",
                                status="fail",
                                description=f"Assumption {i + 1} may be contradicted by step {j + 1}",
                                evidence=[
                                    EvidenceSpan(
                                        text=assumption,
                                        source_field=f"assumptions[{i}]",
                                        claim_type="assumption",
                                        relevance="Assumed condition",
                                    ),
                                    EvidenceSpan(
                                        text=step,
                                        source_field=f"steps[{j}]",
                                        claim_type="assertion",
                                        relevance="Potentially contradicting step",
                                    ),
                                ],
                            )
                        )
                        break

    return findings


def _extract_short_phrases(text: str) -> list[str]:
    words = text.split()
    phrases = []
    for length in (3, 2):
        for i in range(len(words) - length + 1):
            phrase = " ".join(words[i : i + length])
            if all(len(w) > 2 for w in words[i : i + length]):
                phrases.append(phrase)
    return phrases


# ---------------------------------------------------------------------------
# 5. Confidence <-> uncertainties coherence
# ---------------------------------------------------------------------------


def _check_confidence_uncertainty(
    p: AgentResponse, task: Task
) -> list[ConsistencyFinding]:
    findings = []
    confidence = confidence_value_if_valid(p.confidence, p.confidence_state)

    if (
        confidence is not None
        and confidence >= 0.95
        and p.uncertainties
        and len(p.uncertainties) >= 3
    ):
        findings.append(
            ConsistencyFinding(
                check_type="confidence_uncertainty",
                status="warning",
                description=(
                    f"Confidence {confidence} is very high despite listing "
                    f"{len(p.uncertainties)} uncertainties — possible performative calibration"
                ),
                evidence=[
                    EvidenceSpan(
                        text=f"confidence: {confidence}",
                        source_field="confidence",
                        relevance="High confidence value",
                    ),
                    *[
                        EvidenceSpan(
                            text=u,
                            source_field=f"uncertainties[{i}]",
                            relevance="Listed uncertainty",
                        )
                        for i, u in enumerate(p.uncertainties[:3])
                    ],
                ],
            )
        )

    if confidence is not None and confidence >= 0.95 and not p.uncertainties:
        findings.append(
            ConsistencyFinding(
                check_type="confidence_uncertainty",
                status="warning",
                description=f"Confidence {confidence} with zero uncertainties listed — no epistemic humility",
                evidence=[
                    EvidenceSpan(
                        text=f"confidence: {confidence}",
                        source_field="confidence",
                        relevance="High confidence with no uncertainties",
                    ),
                ],
            )
        )

    if (
        task.difficulty.value == "hard"
        and confidence is not None
        and confidence >= 0.95
    ):
        findings.append(
            ConsistencyFinding(
                check_type="confidence_uncertainty",
                status="minor",
                description=f"Confidence {confidence} on a hard task — may indicate miscalibration",
                evidence=[
                    EvidenceSpan(
                        text=f"confidence: {confidence}",
                        source_field="confidence",
                        relevance="High confidence on hard task",
                    ),
                ],
            )
        )

    return findings


# ---------------------------------------------------------------------------
# 6. Conservative contradiction heuristics
# ---------------------------------------------------------------------------


def _check_conservative_contradictions(p: AgentResponse) -> list[ConsistencyFinding]:
    if not p.steps or not p.final_answer:
        return []

    findings = []
    answer_low = p.final_answer.lower()

    answer_affirms = any(
        phrase in answer_low
        for phrase in ("is valid", "claim is correct", "is true", "yes,")
    )
    answer_denies = any(
        phrase in answer_low
        for phrase in (
            "not valid",
            "invalid",
            "is not",
            "claim is misleading",
            "does not hold",
            "incorrect",
        )
    )

    if not answer_affirms and not answer_denies:
        return findings

    for i, step in enumerate(p.steps):
        low = step.lower()
        step_affirms = any(
            phrase in low
            for phrase in (
                "therefore the claim is valid",
                "the claim is correct",
                "this proves the claim",
                "the journalist is right",
            )
        )
        step_denies = any(
            phrase in low
            for phrase in (
                "therefore the claim is not valid",
                "the claim is invalid",
                "the journalist is wrong",
                "this disproves the claim",
            )
        )

        if answer_denies and step_affirms:
            findings.append(
                ConsistencyFinding(
                    check_type="contradiction",
                    status="fail",
                    description=f"Step {i + 1} explicitly affirms what the final answer denies",
                    evidence=[
                        EvidenceSpan(
                            text=step,
                            source_field=f"steps[{i}]",
                            claim_type="assertion",
                            relevance="Contradicts answer direction",
                        ),
                        EvidenceSpan(
                            text=p.final_answer[:200],
                            source_field="final_answer",
                            relevance="Answer takes opposite position",
                        ),
                    ],
                )
            )
        if answer_affirms and step_denies:
            findings.append(
                ConsistencyFinding(
                    check_type="contradiction",
                    status="fail",
                    description=f"Step {i + 1} explicitly denies what the final answer affirms",
                    evidence=[
                        EvidenceSpan(
                            text=step,
                            source_field=f"steps[{i}]",
                            claim_type="assertion",
                            relevance="Contradicts answer direction",
                        ),
                        EvidenceSpan(
                            text=p.final_answer[:200],
                            source_field="final_answer",
                            relevance="Answer takes opposite position",
                        ),
                    ],
                )
            )

    return findings


# ---------------------------------------------------------------------------
# 7. Assumption usage audit (v0.4)
# ---------------------------------------------------------------------------


def _check_assumption_usage(p: AgentResponse) -> list[ConsistencyFinding]:
    """Detect assumptions that are declared but never referenced in reasoning."""
    if not p.assumptions or not p.steps:
        return []

    findings = []
    step_text = " ".join(p.steps).lower()
    answer_text = p.final_answer.lower()
    combined = step_text + " " + answer_text

    for i, assumption in enumerate(p.assumptions):
        words = _content_words(assumption, min_len=5)
        if len(words) < 2:
            continue

        hits = sum(1 for w in words if w in combined)
        if hits == 0:
            findings.append(
                ConsistencyFinding(
                    check_type="unused_assumption",
                    status="warning",
                    description=f"Assumption {i + 1} appears unused in reasoning or answer",
                    evidence=[
                        EvidenceSpan(
                            text=assumption,
                            source_field=f"assumptions[{i}]",
                            claim_type="assumption",
                            relevance="Declared but not referenced in steps or answer",
                            role="missing_expected",
                        ),
                    ],
                )
            )

    return findings


# ---------------------------------------------------------------------------
# 8. Uncertainty resolution audit (v0.4)
# ---------------------------------------------------------------------------


def _check_uncertainty_resolution(p: AgentResponse) -> list[ConsistencyFinding]:
    """Detect uncertainties that are listed but never addressed in reasoning."""
    if not p.uncertainties or not p.steps:
        return []

    findings = []
    reasoning_text = " ".join(p.steps).lower() + " " + " ".join(p.self_check).lower()

    for i, uncertainty in enumerate(p.uncertainties):
        words = _content_words(uncertainty, min_len=5)
        if len(words) < 2:
            continue

        hits = sum(1 for w in words if w in reasoning_text)
        ratio = hits / len(words) if words else 0

        if ratio < 0.15:
            findings.append(
                ConsistencyFinding(
                    check_type="decorative_uncertainty",
                    status="warning",
                    description=f"Uncertainty {i + 1} appears decorative — not addressed in reasoning or self-check",
                    evidence=[
                        EvidenceSpan(
                            text=uncertainty,
                            source_field=f"uncertainties[{i}]",
                            relevance="Listed but not addressed in reasoning",
                            role="missing_expected",
                        ),
                    ],
                )
            )

    return findings


# ---------------------------------------------------------------------------
# 9. Self-check depth audit (v0.4)
# ---------------------------------------------------------------------------

_FLUFF_INDICATORS = (
    "i checked",
    "i verified",
    "double-check",
    "confirmed correct",
    "looks right",
    "seems correct",
    "appears correct",
    "this is right",
    "verified my",
    "checked my work",
)


def _check_self_check_depth(p: AgentResponse) -> list[ConsistencyFinding]:
    """Classify self-checks as deep, arithmetic, or fluff."""
    if not p.self_check:
        return []

    findings = []
    fluff_count = 0
    total = len(p.self_check)

    for i, check in enumerate(p.self_check):
        low = check.lower()
        is_fluff = (
            any(ind in low for ind in _FLUFF_INDICATORS) and len(check) < 60
        ) or len(check) < 25

        if is_fluff:
            fluff_count += 1
            findings.append(
                ConsistencyFinding(
                    check_type="self_check_depth",
                    status="minor",
                    description=f"Self-check {i + 1} appears to be generic fluff rather than substantive verification",
                    evidence=[
                        EvidenceSpan(
                            text=check,
                            source_field=f"self_check[{i}]",
                            relevance="Short or generic self-check",
                            role="weakening",
                        ),
                    ],
                )
            )

    if fluff_count > 0 and fluff_count == total:
        findings.append(
            ConsistencyFinding(
                check_type="self_check_depth",
                status="warning",
                description=f"All {total} self-checks appear to be fluff — no substantive verification detected",
                evidence=[
                    EvidenceSpan(
                        text=p.self_check[0],
                        source_field="self_check[0]",
                        relevance="Example of fluff self-check",
                        role="weakening",
                    ),
                ],
            )
        )

    return findings


# ---------------------------------------------------------------------------
# 10. Alternative hypothesis quality audit (v0.4)
# ---------------------------------------------------------------------------


def _check_alternative_hypothesis_quality(p: AgentResponse) -> list[ConsistencyFinding]:
    """Detect weak or strawman alternative hypotheses."""
    if not p.alternative_hypotheses:
        return []

    findings = []
    answer_words = _content_words(p.final_answer)

    for i, hyp in enumerate(p.alternative_hypotheses):
        low = hyp.lower()

        # Strawman: very short or trivially dismissed
        if len(hyp) < 30:
            findings.append(
                ConsistencyFinding(
                    check_type="weak_alternative",
                    status="minor",
                    description=f"Alternative hypothesis {i + 1} is too brief to represent genuine consideration",
                    evidence=[
                        EvidenceSpan(
                            text=hyp,
                            source_field=f"alternative_hypotheses[{i}]",
                            relevance="Very brief alternative",
                            role="weakening",
                        ),
                    ],
                )
            )
            continue

        # Trivial restatement: high overlap with final answer
        hyp_words = _content_words(hyp)
        if hyp_words and answer_words:
            overlap = len(hyp_words & answer_words) / len(hyp_words)
            if overlap > 0.6:
                findings.append(
                    ConsistencyFinding(
                        check_type="weak_alternative",
                        status="minor",
                        description=f"Alternative hypothesis {i + 1} closely restates the final answer rather than offering a genuine alternative",
                        evidence=[
                            EvidenceSpan(
                                text=hyp,
                                source_field=f"alternative_hypotheses[{i}]",
                                relevance="High overlap with final answer",
                                role="weakening",
                            ),
                        ],
                    )
                )
                continue

        # No rejection reasoning
        rejection_words = (
            "because",
            "since",
            "however",
            "but",
            "reject",
            "unlikely",
            "incorrect",
            "wrong",
            "doesn't",
            "not",
        )
        has_reasoning = any(w in low for w in rejection_words)
        if not has_reasoning:
            findings.append(
                ConsistencyFinding(
                    check_type="weak_alternative",
                    status="minor",
                    description=f"Alternative hypothesis {i + 1} is stated without rejection reasoning",
                    evidence=[
                        EvidenceSpan(
                            text=hyp,
                            source_field=f"alternative_hypotheses[{i}]",
                            relevance="No explanation for why rejected",
                            role="weakening",
                        ),
                    ],
                )
            )

    return findings


# ---------------------------------------------------------------------------
# 11. Claim drift detection (v0.4)
# ---------------------------------------------------------------------------


def _check_claim_drift(p: AgentResponse) -> list[ConsistencyFinding]:
    """Detect when the semantic center shifts between steps and final answer."""
    if not p.steps or not p.final_answer:
        return []

    findings = []
    answer_words = _content_words(p.final_answer, min_len=5)
    if len(answer_words) < 3:
        return findings

    # Check early steps vs final answer
    if len(p.steps) >= 3:
        early_text = " ".join(p.steps[: len(p.steps) // 2]).lower()
        late_text = " ".join(p.steps[len(p.steps) // 2 :]).lower()
        early_words = _content_words(early_text, min_len=5)
        late_words = _content_words(late_text, min_len=5)

        if early_words and late_words:
            early_overlap = len(answer_words & early_words) / len(answer_words)
            late_overlap = len(answer_words & late_words) / len(answer_words)

            # Answer much closer to late steps than early = potential drift
            if early_overlap < 0.15 and late_overlap > 0.4:
                findings.append(
                    ConsistencyFinding(
                        check_type="claim_drift",
                        status="warning",
                        description="Answer content appears disconnected from early reasoning steps — possible claim drift",
                        evidence=[
                            EvidenceSpan(
                                text=p.steps[0][:120],
                                source_field="steps[0]",
                                relevance=f"Early step ({early_overlap:.0%} answer overlap)",
                                role="weakening",
                            ),
                            EvidenceSpan(
                                text=p.final_answer[:120],
                                source_field="final_answer",
                                relevance=f"Late overlap: {late_overlap:.0%}",
                                role="supporting",
                            ),
                        ],
                    )
                )

    return findings


# ---------------------------------------------------------------------------
# 12. Mechanism gap detection (v0.4)
# ---------------------------------------------------------------------------

_MECHANISM_INDICATORS = (
    "because",
    "causes",
    "leads to",
    "results in",
    "driven by",
    "explained by",
    "due to",
    "reason is",
    "mechanism is",
    "this happens when",
    "this occurs because",
)

_NAMING_INDICATORS = (
    "paradox",
    "fallacy",
    "bias",
    "effect",
    "theorem",
    "principle",
    "law",
    "heuristic",
    "phenomenon",
)


def _check_mechanism_gap(p: AgentResponse, task: Task) -> list[ConsistencyFinding]:
    """Detect when a phenomenon is named but not mechanistically explained, or vice versa."""
    if not p.steps:
        return []

    findings = []
    step_text = " ".join(p.steps).lower()
    answer_text = p.final_answer.lower()
    combined = step_text + " " + answer_text

    has_naming = any(ind in combined for ind in _NAMING_INDICATORS)
    has_mechanism = any(ind in combined for ind in _MECHANISM_INDICATORS)

    # Named but not explained
    if has_naming and not has_mechanism:
        findings.append(
            ConsistencyFinding(
                check_type="mechanism_gap",
                status="warning",
                description="Phenomenon is named but causal mechanism is not explained",
                evidence=[
                    EvidenceSpan(
                        text=p.final_answer[:150],
                        source_field="final_answer",
                        relevance="Names concept without mechanism explanation",
                        role="weakening",
                    ),
                ],
            )
        )

    # Mechanism described but not named
    if has_mechanism and not has_naming:
        findings.append(
            ConsistencyFinding(
                check_type="mechanism_gap",
                status="minor",
                description="Causal mechanism described but underlying concept not named",
                evidence=[
                    EvidenceSpan(
                        text=p.final_answer[:150],
                        source_field="final_answer",
                        relevance="Describes mechanism without naming concept",
                        role="weakening",
                    ),
                ],
            )
        )

    # Check task-specific expected mechanism terms
    if task.expected_mechanism_terms:
        missing = [
            t for t in task.expected_mechanism_terms if t.lower() not in combined
        ]
        if missing:
            findings.append(
                ConsistencyFinding(
                    check_type="mechanism_gap",
                    status="warning",
                    description=f"Expected mechanism terms missing: {', '.join(missing)}",
                    evidence=[
                        EvidenceSpan(
                            text=f"Missing: {', '.join(missing)}",
                            source_field="(task expectation)",
                            relevance="Task expects these mechanism terms",
                            role="missing_expected",
                        ),
                    ],
                )
            )

    return findings


# ---------------------------------------------------------------------------
# 13. Numeric-verbal reversal detection (v0.4.1)
# ---------------------------------------------------------------------------


def _check_numeric_verbal_reversals(
    claim_results: list[ClaimCheckResult],
) -> list[ConsistencyFinding]:
    """Flag claim check results where verbal claims contradict numeric facts."""
    findings = []
    for cr in claim_results:
        if cr.truth_status == ClaimTruthStatus.CONTRADICTED:
            findings.append(
                ConsistencyFinding(
                    check_type="numeric_verbal_reversal",
                    status="fail",
                    description=(
                        f"Verbal claim contradicts numeric facts: "
                        f"'{cr.claim.source_text[:100]}' — {cr.explanation}"
                    ),
                    evidence=[
                        EvidenceSpan(
                            text=cr.claim.source_text[:200],
                            source_field=cr.claim.source_field,
                            relevance=f"Claims {cr.claim.subject} {cr.claim.relation} {cr.claim.object}",
                            role="contradictory",
                        ),
                        *[
                            EvidenceSpan(
                                text=f"{f.entity}: {f.value}%",
                                source_field=f.source_field,
                                relevance="Contradicting numeric fact",
                                role="contradictory",
                            )
                            for f in cr.contradicting_facts[:3]
                        ],
                    ],
                )
            )
    return findings


# ---------------------------------------------------------------------------
# 14. Failed self-audit detection (v0.4.1)
# ---------------------------------------------------------------------------


def _check_failed_self_audit(
    parsed: AgentResponse,
    claim_results: list[ClaimCheckResult],
) -> list[ConsistencyFinding]:
    """Detect when self-check claims correctness but claim checker finds contradictions."""
    if not parsed.self_check:
        return []

    contradictions = [
        cr for cr in claim_results if cr.truth_status == ClaimTruthStatus.CONTRADICTED
    ]
    if not contradictions:
        return []

    findings = []
    check_text = " ".join(parsed.self_check).lower()

    # Self-check says things are correct
    affirm_markers = (
        "correct",
        "verified",
        "confirmed",
        "consistent",
        "checks out",
        "no errors",
        "no mistakes",
        "everything checks",
        "valid",
        "arithmetic is right",
        "numbers match",
        "calculations are",
    )
    self_affirms = any(m in check_text for m in affirm_markers)

    if self_affirms and contradictions:
        findings.append(
            ConsistencyFinding(
                check_type="failed_self_audit",
                status="fail",
                description=(
                    f"Self-check affirms correctness but {len(contradictions)} "
                    f"numeric-verbal contradiction(s) found — self-audit missed real errors"
                ),
                evidence=[
                    EvidenceSpan(
                        text=parsed.self_check[0][:150],
                        source_field="self_check[0]",
                        relevance="Self-check affirms correctness",
                        role="weakening",
                    ),
                    EvidenceSpan(
                        text=contradictions[0].explanation[:150],
                        source_field=contradictions[0].claim.source_field,
                        relevance="Contradiction missed by self-check",
                        role="contradictory",
                    ),
                ],
            )
        )

    return findings
