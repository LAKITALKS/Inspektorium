"""Lightweight reasoning graph extraction of the Inspektorium audit runtime.

Turns an AgentResponse into a structured claim graph without NLP dependencies.
Identifies: repeated claims, support chains, unused assumptions,
unaddressed uncertainties, fluff self-checks, grounding audit,
and mechanism analysis.

v0.4.1 hardening:
- Improved support detection beyond pure word overlap
- Grounding audit with direct/indirect/unsupported classification
- Mechanism analysis (named vs described vs case-grounded)
"""

from __future__ import annotations

import re

from inspektorium.audit.schemas import (
    AgentResponse,
    ClaimRelation,
    GroundingAudit,
    MechanismAnalysis,
    NormalizedClaim,
    ReasoningGraph,
    Task,
)


# ---------------------------------------------------------------------------
# Claim extraction
# ---------------------------------------------------------------------------


def _extract_claims(p: AgentResponse) -> list[NormalizedClaim]:
    """Extract normalized claims from all response fields."""
    claims: list[NormalizedClaim] = []

    # Assumptions
    for i, a in enumerate(p.assumptions):
        claims.append(
            NormalizedClaim(
                text=a,
                source_field=f"assumptions[{i}]",
                claim_role="assumption",
            )
        )

    # Reasoning steps
    for i, s in enumerate(p.steps):
        claims.append(
            NormalizedClaim(
                text=s,
                source_field=f"steps[{i}]",
                claim_role="assertion",
            )
        )

    # Key claims
    for i, c in enumerate(p.key_claims):
        claims.append(
            NormalizedClaim(
                text=c,
                source_field=f"key_claims[{i}]",
                claim_role="claim",
            )
        )

    # Alternative hypotheses
    for i, h in enumerate(p.alternative_hypotheses):
        claims.append(
            NormalizedClaim(
                text=h,
                source_field=f"alternative_hypotheses[{i}]",
                claim_role="challenge",
            )
        )

    # Uncertainties
    for i, u in enumerate(p.uncertainties):
        claims.append(
            NormalizedClaim(
                text=u,
                source_field=f"uncertainties[{i}]",
                claim_role="challenge",
                addressed=False,  # default: unaddressed until proven otherwise
            )
        )

    # Self-checks
    for i, sc in enumerate(p.self_check):
        claims.append(
            NormalizedClaim(
                text=sc,
                source_field=f"self_check[{i}]",
                claim_role="check",
            )
        )

    # Final answer as conclusion
    if p.final_answer:
        claims.append(
            NormalizedClaim(
                text=p.final_answer,
                source_field="final_answer",
                claim_role="conclusion",
            )
        )

    return claims


# ---------------------------------------------------------------------------
# Content word extraction (shared)
# ---------------------------------------------------------------------------


def _content_words(text: str, min_len: int = 4) -> set[str]:
    """Extract meaningful content words from text."""
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
        "after",
        "before",
        "during",
        "between",
        "through",
        "with",
        "from",
        "into",
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


def _overlap_ratio(words_a: set[str], words_b: set[str]) -> float:
    if not words_a:
        return 0.0
    return len(words_a & words_b) / len(words_a)


# ---------------------------------------------------------------------------
# Relation detection
# ---------------------------------------------------------------------------


def _detect_relations(claims: list[NormalizedClaim]) -> list[ClaimRelation]:
    """Detect support/contradiction/refinement relations between claims."""
    relations: list[ClaimRelation] = []

    for i, ci in enumerate(claims):
        words_i = _content_words(ci.text)
        if not words_i:
            continue

        for j, cj in enumerate(claims):
            if i == j:
                continue
            words_j = _content_words(cj.text)
            if not words_j:
                continue

            overlap = _overlap_ratio(words_i, words_j)
            if overlap < 0.25:
                continue

            # Determine relation type based on claim roles
            if ci.claim_role == "assumption" and cj.claim_role == "assertion":
                relations.append(
                    ClaimRelation(
                        source_idx=i,
                        target_idx=j,
                        relation="assumes",
                        strength=overlap,
                    )
                )
            elif ci.claim_role == "assertion" and cj.claim_role == "conclusion":
                relations.append(
                    ClaimRelation(
                        source_idx=i,
                        target_idx=j,
                        relation="supports",
                        strength=overlap,
                    )
                )
            elif ci.claim_role == "check" and cj.claim_role in (
                "assertion",
                "conclusion",
            ):
                relations.append(
                    ClaimRelation(
                        source_idx=i,
                        target_idx=j,
                        relation="checks",
                        strength=overlap,
                    )
                )
            elif ci.claim_role == "claim" and cj.claim_role == "conclusion":
                relations.append(
                    ClaimRelation(
                        source_idx=i,
                        target_idx=j,
                        relation="supports",
                        strength=overlap,
                    )
                )

    return relations


# ---------------------------------------------------------------------------
# Assumption usage audit
# ---------------------------------------------------------------------------


def _audit_assumption_usage(claims: list[NormalizedClaim]) -> list[int]:
    """Return indices of assumptions that are never referenced in steps."""
    unused = []
    step_text = " ".join(
        c.text.lower() for c in claims if c.claim_role in ("assertion", "conclusion")
    )

    for i, c in enumerate(claims):
        if c.claim_role != "assumption":
            continue
        words = _content_words(c.text, min_len=5)
        if not words:
            continue
        hits = sum(1 for w in words if w in step_text)
        if hits == 0 or (len(words) >= 3 and hits / len(words) < 0.15):
            c.used = False
            unused.append(i)

    return unused


# ---------------------------------------------------------------------------
# Uncertainty resolution audit
# ---------------------------------------------------------------------------


def _audit_uncertainty_resolution(claims: list[NormalizedClaim]) -> list[int]:
    """Return indices of uncertainties that are never addressed in later reasoning."""
    unaddressed = []
    reasoning_text = " ".join(
        c.text.lower()
        for c in claims
        if c.claim_role in ("assertion", "conclusion", "check")
    )

    for i, c in enumerate(claims):
        if c.claim_role != "challenge" or c.source_field.startswith("alternative"):
            continue
        words = _content_words(c.text, min_len=5)
        if not words:
            continue
        hits = sum(1 for w in words if w in reasoning_text)
        if hits == 0 or (len(words) >= 3 and hits / len(words) < 0.2):
            c.addressed = False
            unaddressed.append(i)

    return unaddressed


# ---------------------------------------------------------------------------
# Self-check depth audit
# ---------------------------------------------------------------------------

_FLUFF_INDICATORS = (
    "i checked",
    "i verified",
    "double-check",
    "confirmed correct",
    "looks right",
    "seems correct",
    "appears correct",
    "is correct",
    "this is right",
    "verified my",
    "checked my work",
)

_ARITHMETIC_INDICATORS = (
    "arithmetic",
    "calculation",
    "sum",
    "total",
    "equals",
    "computed",
    "multiplied",
    "divided",
    "added",
    "subtracted",
)

_DEEP_CHECK_INDICATORS = (
    "what if",
    "could this be wrong",
    "alternative",
    "edge case",
    "counterexample",
    "fails when",
    "breaks if",
    "assuming the opposite",
    "trap",
    "common error",
    "pitfall",
    "fallacy",
    "bias",
)


def classify_self_check(text: str) -> str:
    """Classify a self-check as: deep, arithmetic, fluff."""
    low = text.lower()
    if any(ind in low for ind in _DEEP_CHECK_INDICATORS):
        return "deep"
    if any(ind in low for ind in _ARITHMETIC_INDICATORS):
        return "arithmetic"
    if any(ind in low for ind in _FLUFF_INDICATORS) and len(text) < 60:
        return "fluff"
    # Substantive if long enough and not matching fluff
    if len(text) > 80:
        return "arithmetic"  # at least doing something
    return "fluff"


def _audit_self_checks(claims: list[NormalizedClaim]) -> list[int]:
    """Return indices of self-checks classified as fluff."""
    fluff_indices = []
    for i, c in enumerate(claims):
        if c.claim_role != "check":
            continue
        if classify_self_check(c.text) == "fluff":
            fluff_indices.append(i)
    return fluff_indices


# ---------------------------------------------------------------------------
# Conclusion grounding check
# ---------------------------------------------------------------------------


def _check_conclusion_grounding(
    claims: list[NormalizedClaim],
) -> tuple[bool, list[int]]:
    """Check whether the final answer is supported by reasoning steps.
    Returns (grounded, list_of_unsupported_conclusion_indices)."""
    conclusions = [(i, c) for i, c in enumerate(claims) if c.claim_role == "conclusion"]
    steps = [c for c in claims if c.claim_role in ("assertion", "claim")]

    if not conclusions or not steps:
        return False, [i for i, _ in conclusions]

    step_text = " ".join(s.text.lower() for s in steps)
    unsupported = []

    for i, conc in conclusions:
        words = _content_words(conc.text, min_len=5)
        if not words:
            continue
        hits = sum(1 for w in words if w in step_text)
        ratio = hits / len(words)
        if ratio < 0.2:
            unsupported.append(i)

    grounded = len(unsupported) == 0
    return grounded, unsupported


# ---------------------------------------------------------------------------
# v0.4.1: Enhanced grounding audit
# ---------------------------------------------------------------------------


def _build_grounding_audit(
    claims: list[NormalizedClaim], relations: list[ClaimRelation]
) -> GroundingAudit:
    """Build a detailed grounding audit for conclusion claims.

    Classifies each conclusion sub-claim as:
    - directly supported: >=30% content word overlap with a step
    - indirectly supported: step shares key phrases but < direct threshold
    - unsupported: no meaningful step support
    - contradicted: step negates the claim direction
    """
    conclusions = [(i, c) for i, c in enumerate(claims) if c.claim_role == "conclusion"]
    steps = [
        (i, c) for i, c in enumerate(claims) if c.claim_role in ("assertion", "claim")
    ]

    if not conclusions:
        return GroundingAudit()

    # Split conclusion text into sub-claims (sentence-level)
    all_sub_claims: list[str] = []
    for _, conc in conclusions:
        sents = re.split(r"[.;!\n]", conc.text)
        all_sub_claims.extend(s.strip() for s in sents if len(s.strip()) > 10)

    if not all_sub_claims:
        all_sub_claims = [c.text for _, c in conclusions]

    direct = 0
    indirect = 0
    unsupported_claims: list[str] = []
    contradicted = 0
    support_paths: list[str] = []

    # v0.4.2: Stricter grounding — require both word overlap AND
    # directional alignment.  Pure lexical overlap (topic words shared
    # without a conclusion/sub-conclusion marker) counts as indirect only.
    _SUB_CONCLUSION_MARKERS = (
        "therefore",
        "thus",
        "hence",
        "so ",
        "this means",
        "which means",
        "this shows",
        "this proves",
        "this indicates",
        "consequently",
        "the result",
        "we conclude",
        "we can see",
    )

    for sub in all_sub_claims:
        sub_words = _content_words(sub, min_len=4)
        if not sub_words:
            continue

        best_overlap = 0.0
        best_step_idx = -1
        best_step_has_conclusion = False
        has_negation_conflict = False

        for si, step in steps:
            step_words = _content_words(step.text, min_len=4)
            if not step_words:
                continue
            overlap = len(sub_words & step_words) / len(sub_words)
            if overlap > best_overlap:
                best_overlap = overlap
                best_step_idx = si
                step_lower = step.text.lower()
                best_step_has_conclusion = any(
                    m in step_lower for m in _SUB_CONCLUSION_MARKERS
                )

            # Check for negation conflict
            if overlap > 0.15 and _has_negation_conflict(sub, step.text):
                has_negation_conflict = True

        if has_negation_conflict:
            contradicted += 1
            support_paths.append(f"CONTRADICTED: '{sub[:60]}...'")
        elif best_overlap >= 0.3 and best_step_has_conclusion:
            # v0.4.2: DIRECT requires both high overlap AND a sub-conclusion
            direct += 1
            support_paths.append(f"DIRECT: '{sub[:60]}...' <- step {best_step_idx}")
        elif best_overlap >= 0.25:
            # High overlap without conclusion marker → still good but indirect
            indirect += 1
            support_paths.append(
                f"INDIRECT: '{sub[:60]}...' <- step {best_step_idx} (no conclusion marker)"
            )
        elif best_overlap >= 0.12:
            indirect += 1
            support_paths.append(
                f"INDIRECT: '{sub[:60]}...' <- step {best_step_idx} (weak)"
            )
        else:
            unsupported_claims.append(sub[:100])
            support_paths.append(f"UNSUPPORTED: '{sub[:60]}...'")

    return GroundingAudit(
        total_conclusion_claims=len(all_sub_claims),
        directly_supported=direct,
        indirectly_supported=indirect,
        unsupported=len(unsupported_claims),
        contradicted=contradicted,
        support_paths=support_paths,
        unsupported_claims=unsupported_claims,
    )


_NEGATION_PAIRS = [
    ("valid", "not valid"),
    ("valid", "invalid"),
    ("valid", "misleading"),
    ("correct", "incorrect"),
    ("correct", "not correct"),
    ("correct", "wrong"),
    ("true", "not true"),
    ("true", "false"),
    ("higher", "lower"),
    ("lower", "higher"),
    ("more", "less"),
    ("less", "more"),
    ("favors", "discriminates"),
    ("discrimination", "no discrimination"),
    ("increases", "decreases"),
    ("decreases", "increases"),
]


def _has_negation_conflict(text_a: str, text_b: str) -> bool:
    """Check if two texts express opposite directions on the same topic.

    v0.4.2: Made more conservative to avoid false positives.
    Design choice: prefer false negatives over false positives.

    A correct answer that discusses both a claim and its rebuttal (e.g.
    "the claim says X is valid, but actually it is not valid") must NOT be
    flagged.  We only flag when:
    1. text_a contains the positive form but NOT the negative form, AND
    2. text_b contains the negative form but NOT the positive form
       (or vice-versa).
    This ensures that a single text discussing both sides is not treated
    as half of a contradiction.
    """
    a_low = text_a.lower()
    b_low = text_b.lower()
    for pos, neg in _NEGATION_PAIRS:
        # Check if the polarity is split across the two texts,
        # not present in both (which indicates discussion/rebuttal).
        a_has_pos = pos in a_low
        a_has_neg = neg in a_low
        b_has_pos = pos in b_low
        b_has_neg = neg in b_low

        # Skip if either text contains BOTH polarities — that's a
        # discussion pattern, not a contradiction signal.
        if a_has_pos and a_has_neg:
            continue
        if b_has_pos and b_has_neg:
            continue

        # True split: one text has pos-only, the other has neg-only
        split = (a_has_pos and b_has_neg) or (a_has_neg and b_has_pos)
        if not split:
            continue

        # Require meaningful topic overlap (raised threshold for safety)
        a_words = _content_words(a_low, min_len=5)
        b_words = _content_words(b_low, min_len=5)
        if len(a_words & b_words) >= 3:
            return True
    return False


# ---------------------------------------------------------------------------
# v0.4.1: Mechanism analysis
# ---------------------------------------------------------------------------

_CONCEPT_NAMES = (
    "paradox",
    "fallacy",
    "bias",
    "effect",
    "theorem",
    "principle",
    "law",
    "heuristic",
    "phenomenon",
    "simpson",
    "monty hall",
    "bayes",
    "base rate",
)

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
    "the reason",
    "this is why",
    "which means",
    "as a result",
)

_CASE_GROUNDING_INDICATORS = (
    "in this case",
    "in our case",
    "here,",
    "specifically,",
    "the data shows",
    "the numbers show",
    "looking at the",
    "for this university",
    "in this problem",
    "in this scenario",
    "the department",
    "the engineering",
    "the arts",
    "men applied",
    "women applied",
    "30%",
    "40%",
    "75%",
    "87",
)


def build_mechanism_analysis(
    p: AgentResponse, task: Task | None = None
) -> MechanismAnalysis:
    """Analyze whether the agent names, describes, and grounds a mechanism."""
    all_text = " ".join([p.final_answer] + p.steps + p.key_claims).lower()

    # 1. Concept naming
    named_concepts: list[str] = []
    for name in _CONCEPT_NAMES:
        if name in all_text:
            named_concepts.append(name)
    concept_named = len(named_concepts) > 0

    # 2. Mechanism description (causal language beyond just naming)
    mechanism_sents: list[str] = []
    for step in p.steps:
        step_l = step.lower()
        if any(ind in step_l for ind in _MECHANISM_INDICATORS):
            # Must be more than just "because X" — needs some substance
            words = step_l.split()
            mech_idx = -1
            for ind in _MECHANISM_INDICATORS:
                if ind in step_l:
                    mech_idx = step_l.find(ind)
                    break
            if mech_idx >= 0:
                after_mech = step_l[mech_idx:]
                after_words = [w for w in after_mech.split() if len(w) > 3]
                if (
                    len(after_words) >= 4
                ):  # at least 4 content words after the mechanism indicator
                    mechanism_sents.append(step[:150])
    # Also check final answer
    fa_l = p.final_answer.lower()
    if any(ind in fa_l for ind in _MECHANISM_INDICATORS):
        after_words = [w for w in fa_l.split() if len(w) > 3]
        if len(after_words) >= 6:
            mechanism_sents.append(p.final_answer[:150])

    mechanism_described = len(mechanism_sents) > 0

    # 3. Case grounding (connects mechanism to specific case data)
    grounding_sents: list[str] = []
    for step in p.steps:
        step_l = step.lower()
        if any(ind in step_l for ind in _CASE_GROUNDING_INDICATORS):
            # Must also have some mechanism/causal language nearby
            if any(ind in step_l for ind in _MECHANISM_INDICATORS) or any(
                c in step_l for c in named_concepts
            ):
                grounding_sents.append(step[:150])
    if not grounding_sents:
        # Weaker check: does any step mention both a specific number AND a causal word?
        for step in p.steps:
            step_l = step.lower()
            has_number = bool(re.search(r"\d+%|\d+/\d+", step))
            has_causal = any(ind in step_l for ind in _MECHANISM_INDICATORS[:6])
            if has_number and has_causal:
                grounding_sents.append(step[:150])

    mechanism_grounded = len(grounding_sents) > 0

    # 4. Missing elements
    missing: list[str] = []
    if not concept_named:
        missing.append("concept not named")
    if not mechanism_described:
        missing.append("mechanism not described")
    if not mechanism_grounded:
        missing.append("mechanism not grounded to case data")

    # Check expected mechanism terms from task
    if task and task.expected_mechanism_terms:
        for term in task.expected_mechanism_terms:
            if term.lower() not in all_text:
                missing.append(f"expected term missing: {term}")

    return MechanismAnalysis(
        concept_named=concept_named,
        mechanism_described=mechanism_described,
        mechanism_grounded_to_case=mechanism_grounded,
        named_concepts=named_concepts,
        mechanism_sentences=mechanism_sents,
        grounding_sentences=grounding_sents,
        missing_elements=missing,
    )


# ---------------------------------------------------------------------------
# Support chain length
# ---------------------------------------------------------------------------


def _compute_support_chain(
    claims: list[NormalizedClaim], relations: list[ClaimRelation]
) -> int:
    """Compute longest chain of supporting relations."""
    if not relations:
        return 0

    # Build adjacency for "supports" relations
    adj: dict[int, list[int]] = {}
    for r in relations:
        if r.relation == "supports":
            adj.setdefault(r.source_idx, []).append(r.target_idx)

    def _dfs(node: int, visited: set[int]) -> int:
        if node in visited:
            return 0
        visited.add(node)
        best = 0
        for nxt in adj.get(node, []):
            best = max(best, 1 + _dfs(nxt, visited))
        return best

    return max((_dfs(start, set()) for start in adj), default=0)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def build_reasoning_graph(p: AgentResponse, task: Task | None = None) -> ReasoningGraph:
    """Build a lightweight reasoning graph from an agent response."""
    claims = _extract_claims(p)
    relations = _detect_relations(claims)

    unused = _audit_assumption_usage(claims)
    unaddressed = _audit_uncertainty_resolution(claims)
    fluff = _audit_self_checks(claims)
    grounded, unsupported = _check_conclusion_grounding(claims)
    chain_len = _compute_support_chain(claims, relations)

    return ReasoningGraph(
        claims=claims,
        relations=relations,
        unused_assumptions=unused,
        unaddressed_uncertainties=unaddressed,
        unsupported_conclusions=unsupported,
        fluff_self_checks=fluff,
        support_chain_length=chain_len,
        conclusion_grounded=grounded,
    )
