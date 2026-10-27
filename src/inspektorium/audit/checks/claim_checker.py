"""Numeric / claim consistency engine of the Inspektorium audit runtime.

Extracts numeric facts and comparative claims from task prompts and agent
responses, then cross-checks them for contradictions.

Detects:
- verbal-numeric mismatches (agent says "higher" when numbers say lower)
- local fact reversals (agent reverses direction of a comparison)
- misstated comparisons (agent inverts subgroup ordering)
- unsupported comparative conclusions

v0.4.2 SCOPE — what this module can and cannot do:

RELIABLY EXTRACTED (all 3 task shapes):
  Simpson's Paradox:
    - Percentages with entity context (e.g. "men 30%", "women 40%")
    - Fractions with entity context (e.g. "30/100 men")
    - Entity normalization (male→men, engineering, arts, overall)
    - Context grouping (engineering, arts, overall)
    - Comparative claims: "X have higher rates than Y"
    - Discrimination claims: "discriminates against X"
  Base Rate Neglect:
    - Probability values from "probability is X%", "P(X) = 0.09"
    - P()-notation chains with ≈ (takes final value)
    - Probability fractions ("probability is 2/3")
    - Entity: has_disease, test_positive, false_positive
  Monty Hall:
    - Probability fractions for door entities ("P(Car=2) = 2/3")
    - Direction claims: "should switch", "better to switch"
    - Entity mapping: door_2_switch, door_1_stay, door_3

RELIABLY VERIFIED:
  - Directional comparisons (higher/lower) against numeric facts
  - Equal-to comparisons with tolerance
  - Context-aware verification (engineering vs overall)
  - Probability direction (switch vs stay)

INTENTIONALLY UNSUPPORTED (out of scope for v0.4.2):
  - Complex conditional probability chains (P(A|B) derivations)
  - Multi-step Bayesian reasoning verification
  - Semantic equivalence of probability statements
  - Implicit comparisons without explicit keywords
  - Numeric accuracy of intermediate calculations
  - Non-percentage numeric claims (counts, ratios without %)
  - Tasks outside the 3 supported families

KNOWN BLIND SPOTS:
  - Agent can state the right number but wrong interpretation
  - "P(disease) = 9%" is extracted but not checked against task's 0.09
    unless reference_solution states a percentage
  - Monty Hall: cannot verify the Bayesian derivation, only the final
    probability and switch/stay recommendation
  - Implicit negation ("this is unlikely" ≠ "probability is low")
"""

from __future__ import annotations

import re

from inspektorium.audit.schemas import (
    AgentResponse,
    ClaimCheckResult,
    ClaimTruthStatus,
    ComparativeClaim,
    NumericFact,
    Task,
)


# ---------------------------------------------------------------------------
# Numeric fact extraction
# ---------------------------------------------------------------------------

# Matches patterns like "30%", "82.2%", "30/100", "0.66"
_PCT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*%")
_FRAC_RE = re.compile(r"(\d+)\s*/\s*(\d+)")
_DECIMAL_RE = re.compile(r"\b0\.\d+\b")

# Entity patterns: tries to find what group a number is about
_ENTITY_CONTEXT_RE = re.compile(
    r"(?:(?P<entity>(?:men|women|male|female|man|woman|"
    r"engineering|arts|department\s*\w*|overall|aggregate|total))"
    r"[^.]{0,60}?"
    r"(?P<value>\d+(?:\.\d+)?)\s*%)"
    r"|"
    r"(?:(?P<value2>\d+(?:\.\d+)?)\s*%"
    r"[^.]{0,40}?"
    r"(?P<entity2>men|women|male|female|man|woman))",
    re.IGNORECASE,
)


_CONTEXT_KEYWORDS = {
    "engineering": "engineering",
    "arts": "arts",
    "overall": "overall",
    "aggregate": "overall",
    "total": "overall",
    "combined": "overall",
    "department a": "department_a",
    "department b": "department_b",
}


def _guess_context(text: str) -> str:
    """Guess the context/grouping of a sentence (e.g. 'engineering', 'overall')."""
    text_l = text.lower()
    for kw, ctx in _CONTEXT_KEYWORDS.items():
        if kw in text_l:
            return ctx
    return ""


def extract_numeric_facts(text: str, source_field: str) -> list[NumericFact]:
    """Extract numeric facts with entity context from text."""
    facts: list[NumericFact] = []
    seen: set[tuple[str, float, str]] = set()

    # Strategy 1: sentence-level extraction (avoid splitting on decimal points)
    sentences = re.split(r"(?<!\d)\.(?!\d)|\n", text)
    for sent in sentences:
        sent_lower = sent.lower().strip()
        if not sent_lower:
            continue

        # Find percentages in this sentence
        pcts = _PCT_RE.findall(sent)
        fracs = _FRAC_RE.findall(sent)

        # Determine entity and context from sentence
        entity = _guess_entity(sent_lower)
        context = _guess_context(sent_lower)
        if not entity and not pcts and not fracs:
            continue

        for pct_str in pcts:
            val = float(pct_str)
            # Always use proximity-based entity detection for each number
            ent = _guess_entity_near_number(sent_lower, pct_str + "%")
            if not ent:
                ent = _guess_entity_near_number(sent_lower, pct_str)
            if not ent:
                ent = entity
            if ent:
                key = (_normalize_entity(ent), val, context)
                if key not in seen:
                    seen.add(key)
                    facts.append(
                        NumericFact(
                            entity=_normalize_entity(ent),
                            metric="rate",
                            value=val,
                            source_field=source_field,
                            context=context,
                        )
                    )

        for num_str, den_str in fracs:
            if float(den_str) == 0:
                continue
            val = round(float(num_str) / float(den_str) * 100, 1)
            ent = _guess_entity_near_number(sent_lower, num_str + "/" + den_str)
            if not ent:
                ent = _guess_entity_near_number(sent_lower, num_str)
            if not ent:
                ent = entity
            if ent:
                key = (_normalize_entity(ent), val, context)
                if key not in seen:
                    seen.add(key)
                    facts.append(
                        NumericFact(
                            entity=_normalize_entity(ent),
                            metric="rate",
                            value=val,
                            source_field=source_field,
                            context=context,
                        )
                    )

    return facts


def _normalize_entity(entity: str) -> str:
    """Normalize entity names to canonical form."""
    e = entity.lower().strip()
    if e in ("male", "man", "males", "mans"):
        return "men"
    if e in ("female", "woman", "females", "womans"):
        return "women"
    if "engineering" in e:
        return "engineering"
    if "arts" in e:
        return "arts"
    if e in ("overall", "aggregate", "total", "combined"):
        return "overall"
    return e


_ENTITY_KEYWORDS = [
    "men",
    "women",
    "male",
    "female",
    "man",
    "woman",
    "engineering",
    "arts",
    "overall",
    "aggregate",
    "total",
]


def _guess_entity(text: str) -> str:
    """Guess the primary entity a sentence is about."""
    text_l = text.lower()
    for kw in _ENTITY_KEYWORDS:
        if kw in text_l:
            return kw
    return ""


def _guess_entity_near_number(text: str, number_str: str) -> str:
    """Find entity keyword closest to a number in text.

    Strategy: find the clause (segment between delimiters like 'and', ',', 'vs')
    that contains the number, then find the entity within that clause.
    Falls back to proximity-based matching.
    """
    idx = text.find(number_str)
    if idx < 0:
        return ""

    # Try clause-based matching first
    # Split text into segments around common delimiters
    clause_ent = _find_entity_in_clause(text, idx)
    if clause_ent:
        return clause_ent

    # Fallback: pure proximity
    best_dist = 999
    best_ent = ""

    for kw in _ENTITY_KEYWORDS:
        for kw_idx in _find_all_entity(text, kw):
            dist = abs(kw_idx - idx)
            if dist < best_dist:
                best_dist = dist
                best_ent = kw

    return best_ent if best_dist < 80 else ""


def _find_entity_in_clause(text: str, number_idx: int) -> str:
    """Find the entity in the same clause as a number.

    A clause is a segment between delimiters like ' and ', ', ', ' vs ', ' — '.
    """
    delimiters = [" and ", ", ", " vs ", " vs. ", " versus ", " — ", " – ", "; "]

    # Find clause boundaries
    clause_start = 0
    clause_end = len(text)
    for delim in delimiters:
        pos = 0
        while True:
            d_idx = text.find(delim, pos)
            if d_idx < 0:
                break
            if d_idx < number_idx and d_idx + len(delim) > clause_start:
                clause_start = d_idx + len(delim)
            if d_idx >= number_idx and d_idx < clause_end:
                clause_end = d_idx
            pos = d_idx + len(delim)

    clause = text[clause_start:clause_end]

    # Find entity in clause
    for kw in _ENTITY_KEYWORDS:
        for kw_idx in _find_all_entity(clause, kw):
            return kw

    return ""


def _find_all_entity(text: str, kw: str) -> list[int]:
    """Find all positions of an entity keyword, avoiding false matches."""
    positions = []
    start = 0
    while True:
        kw_idx = text.find(kw, start)
        if kw_idx < 0:
            break
        # Avoid matching "men" inside "women"
        if (
            kw in ("men", "man")
            and kw_idx > 0
            and text[kw_idx - 1 : kw_idx].lower() in ("o",)
        ):
            start = kw_idx + len(kw)
            continue
        positions.append(kw_idx)
        start = kw_idx + len(kw)
    return positions


# ---------------------------------------------------------------------------
# Comparative claim extraction
# ---------------------------------------------------------------------------

_HIGHER_PATTERNS = [
    r"(?P<subj>\w+)\s+(?:have|has|had|show|shows|get|gets)\s+(?:a\s+)?higher\s+(?P<metric>\w+(?:\s+\w+)?)\s+than\s+(?P<obj>\w+)",
    r"(?P<subj>\w+)\s+(?:are|were|is|was)\s+admitted\s+(?:at\s+)?(?:a\s+)?higher\s+rate\s+than\s+(?P<obj>\w+)",
    r"(?P<subj>\w+)\s+(?:are|were)\s+(?:more\s+likely|favou?red)\b.*?(?:than|over|compared\s+to)\s+(?P<obj>\w+)",
    r"(?P<metric>rate|percentage|proportion)\s+(?:for|of)\s+(?P<subj>\w+)\s+(?:is|was|are|were)\s+higher\s+than\s+(?:for|of)\s+(?P<obj>\w+)",
]

_LOWER_PATTERNS = [
    r"(?P<subj>\w+)\s+(?:have|has|had|show|shows|get|gets)\s+(?:a\s+)?lower\s+(?P<metric>\w+(?:\s+\w+)?)\s+than\s+(?P<obj>\w+)",
    r"(?P<subj>\w+)\s+(?:are|were|is|was)\s+admitted\s+(?:at\s+)?(?:a\s+)?lower\s+rate\s+than\s+(?P<obj>\w+)",
    r"(?P<subj>\w+)\s+(?:are|were)\s+(?:less\s+likely|disfavou?red)\b.*?(?:than|compared\s+to)\s+(?P<obj>\w+)",
]

_DISCRIMINATION_PATTERNS = [
    r"discriminat(?:es|ion|ing)\s+against\s+(?P<obj>\w+)",
    r"bias(?:ed)?\s+against\s+(?P<obj>\w+)",
    r"(?P<obj>\w+)\s+(?:are|were)\s+disadvantaged",
    r"favou?rs?\s+(?P<subj>\w+)\s+over\s+(?P<obj>\w+)",
]

_BETTER_WORSE_PATTERNS = [
    r"(?P<subj>\w+)\s+(?:perform|do|fare|score)\w*\s+better\s+(?:than|in\s+both|in\s+each|in\s+every)",
    r"(?P<subj>\w+)\s+(?:perform|do|fare|score)\w*\s+worse\s+(?:than|in\s+both|in\s+each|in\s+every)",
    r"(?P<subj>\w+)\s+(?:have|has)\s+(?:a\s+)?(?:better|worse)\s+(?:rate|outcome|result)",
]


def extract_comparative_claims(text: str, source_field: str) -> list[ComparativeClaim]:
    """Extract comparative claims from text."""
    claims: list[ComparativeClaim] = []

    # Sentence-level scanning (avoid splitting on decimal points)
    sentences = re.split(r"(?<!\d)\.(?!\d)|\n|!|\?", text)
    for sent in sentences:
        sent_l = sent.lower().strip()
        if not sent_l:
            continue

        # Higher-than patterns
        for pat in _HIGHER_PATTERNS:
            m = re.search(pat, sent_l)
            if m:
                groups = m.groupdict()
                claims.append(
                    ComparativeClaim(
                        subject=_normalize_entity(groups.get("subj", "")),
                        object=_normalize_entity(groups.get("obj", "")),
                        relation="higher_than",
                        metric=groups.get("metric", "rate"),
                        source_field=source_field,
                        source_text=sent.strip(),
                    )
                )

        # Lower-than patterns
        for pat in _LOWER_PATTERNS:
            m = re.search(pat, sent_l)
            if m:
                groups = m.groupdict()
                claims.append(
                    ComparativeClaim(
                        subject=_normalize_entity(groups.get("subj", "")),
                        object=_normalize_entity(groups.get("obj", "")),
                        relation="lower_than",
                        metric=groups.get("metric", "rate"),
                        source_field=source_field,
                        source_text=sent.strip(),
                    )
                )

        # Discrimination patterns
        for pat in _DISCRIMINATION_PATTERNS:
            m = re.search(pat, sent_l)
            if m:
                groups = m.groupdict()
                obj = _normalize_entity(groups.get("obj", ""))
                subj = (
                    _normalize_entity(groups.get("subj", ""))
                    if "subj" in groups
                    else ""
                )
                if obj:
                    claims.append(
                        ComparativeClaim(
                            subject=subj or "(system)",
                            object=obj,
                            relation="discriminates_against",
                            metric="treatment",
                            source_field=source_field,
                            source_text=sent.strip(),
                        )
                    )

            # Keyword-based heuristic extraction for simpler patterns
        _extract_keyword_claims(sent_l, sent.strip(), source_field, claims)

        # Context-based directional claims (v0.4.1)
        _extract_contextual_direction_claims(sent_l, sent.strip(), source_field, claims)

    return claims


def _extract_contextual_direction_claims(
    sent_l: str, sent_orig: str, source_field: str, claims: list[ComparativeClaim]
) -> None:
    """Extract directional claims from context like 'X have higher rates in Y'."""
    # Pattern: "[entity] have/has higher/lower rates"
    # Without an explicit "than", we infer the other entity from known pairs
    _direction_patterns = [
        (
            r"(\w+)\s+(?:have|has|had)\s+(?:a\s+)?higher\s+(?:rate|rates|percentage)",
            "higher_than",
        ),
        (r"(\w+)\s+(?:are|is|were)\s+(?:more\s+)?favou?red", "higher_than"),
        (
            r"(\w+)\s+(?:have|has|had)\s+(?:a\s+)?lower\s+(?:rate|rates|percentage)",
            "lower_than",
        ),
        (r"(\w+)\s+(?:are|is|were)\s+(?:less\s+)?favou?red", "lower_than"),
        (
            r"(\w+)\s+(?:have|has|had)\s+(?:a\s+)?(?:better|superior)\s+(?:rate|outcome)",
            "higher_than",
        ),
        (
            r"(\w+)\s+(?:have|has|had)\s+(?:a\s+)?(?:worse|inferior)\s+(?:rate|outcome)",
            "lower_than",
        ),
    ]
    _entity_pairs = {
        "men": "women",
        "women": "men",
        "male": "female",
        "female": "male",
    }

    for pat, relation in _direction_patterns:
        m = re.search(pat, sent_l)
        if m:
            subj = _normalize_entity(m.group(1))
            obj = _entity_pairs.get(subj, "")
            if subj and obj:
                # Check this isn't already captured
                already = any(
                    c.subject == subj and c.object == obj and c.relation == relation
                    for c in claims
                )
                if not already:
                    claims.append(
                        ComparativeClaim(
                            subject=subj,
                            object=obj,
                            relation=relation,
                            metric="rate",
                            source_field=source_field,
                            source_text=sent_orig,
                        )
                    )


def _extract_keyword_claims(
    sent_l: str, sent_orig: str, source_field: str, claims: list[ComparativeClaim]
) -> None:
    """Extract claims from keyword patterns that don't fit regex well."""
    # "X% of men vs Y% of women" style
    m = re.search(
        r"(\d+(?:\.\d+)?)\s*%\s*(?:of\s+)?(\w+).*?(?:vs\.?|versus|compared\s+to|while|but)\s+"
        r"(\d+(?:\.\d+)?)\s*%\s*(?:of\s+)?(\w+)",
        sent_l,
    )
    if m:
        val1, ent1, val2, ent2 = (
            float(m.group(1)),
            m.group(2),
            float(m.group(3)),
            m.group(4),
        )
        ent1_n = _normalize_entity(ent1)
        ent2_n = _normalize_entity(ent2)
        if ent1_n and ent2_n and ent1_n != ent2_n:
            rel = (
                "higher_than"
                if val1 > val2
                else "lower_than"
                if val1 < val2
                else "equal_to"
            )
            claims.append(
                ComparativeClaim(
                    subject=ent1_n,
                    object=ent2_n,
                    relation=rel,
                    metric="rate",
                    source_field=source_field,
                    source_text=sent_orig,
                )
            )

    # "only X% ... admitted" pattern indicating criticism
    if "only" in sent_l and "%" in sent_l:
        for kw in _ENTITY_KEYWORDS[:6]:  # men/women/male/female/man/woman
            if kw in sent_l:
                claims.append(
                    ComparativeClaim(
                        subject="(system)",
                        object=_normalize_entity(kw),
                        relation="disadvantages",
                        metric="rate",
                        source_field=source_field,
                        source_text=sent_orig,
                    )
                )
                break


# ---------------------------------------------------------------------------
# Claim verification
# ---------------------------------------------------------------------------


def _invert_relation(rel: str) -> str:
    """Get the inverse of a relation."""
    inversions = {
        "higher_than": "lower_than",
        "lower_than": "higher_than",
        "discriminates_against": "favors",
        "favors": "discriminates_against",
        "disadvantages": "advantages",
        "advantages": "disadvantages",
    }
    return inversions.get(rel, rel)


def _compare_claim_pairs(
    claim: ComparativeClaim,
    subj_vals: list[NumericFact],
    obj_vals: list[NumericFact],
) -> ClaimCheckResult:
    """Compare a claim against all available fact pairs and return the best result.

    Strategy:
    - If claim source text mentions a specific context (e.g. "engineering"),
      prefer facts from that context.
    - Otherwise, check all pairs. If ALL pairs agree on direction, use that.
    - If pairs disagree (some support, some contradict), return the strongest signal.
    """
    source_lower = claim.source_text.lower()

    # Determine claim context
    claim_context = _guess_context(source_lower)

    # Build pairs to check: prefer same-context pairs
    pairs: list[tuple[NumericFact, NumericFact]] = []

    # 1. If claim mentions a specific context, use facts from that context
    if claim_context:
        ctx_subj = [f for f in subj_vals if f.context == claim_context]
        ctx_obj = [f for f in obj_vals if f.context == claim_context]
        for sf in ctx_subj:
            for of in ctx_obj:
                pairs.append((sf, of))

    # 2. If claim says "overall" or no specific context, prefer "overall" facts
    if not pairs and (claim_context == "overall" or not claim_context):
        overall_subj = [f for f in subj_vals if f.context == "overall"]
        overall_obj = [f for f in obj_vals if f.context == "overall"]
        for sf in overall_subj:
            for of in overall_obj:
                pairs.append((sf, of))

    # 3. Fall back to same-context pairs
    if not pairs:
        for sf in subj_vals:
            for of in obj_vals:
                if sf.context == of.context and sf.context:
                    pairs.append((sf, of))

    # 4. Last resort: first pair
    if not pairs:
        pairs = [(subj_vals[0], obj_vals[0])]

    # Check each pair
    supported_count = 0
    contradicted_count = 0
    best_expl = ""
    best_s_facts: list[NumericFact] = []
    best_c_facts: list[NumericFact] = []

    for sf, of in pairs:
        status, expl = _check_direction(
            claim.relation, sf.value, of.value, claim.subject, claim.object
        )
        if status == ClaimTruthStatus.SUPPORTED:
            supported_count += 1
            if not best_expl or "CONTRADICTION" not in best_expl:
                best_expl = expl
                best_s_facts = [sf, of]
        elif status == ClaimTruthStatus.CONTRADICTED:
            contradicted_count += 1
            best_expl = expl
            best_c_facts = [sf, of]

    # Decision: if any pair contradicts and none supports, it's contradicted
    # If mixed, still flag as contradicted (conservative)
    if contradicted_count > 0:
        return ClaimCheckResult(
            claim=claim,
            truth_status=ClaimTruthStatus.CONTRADICTED,
            explanation=best_expl,
            contradicting_facts=best_c_facts,
        )
    elif supported_count > 0:
        return ClaimCheckResult(
            claim=claim,
            truth_status=ClaimTruthStatus.SUPPORTED,
            explanation=best_expl,
            supporting_facts=best_s_facts,
        )
    else:
        return ClaimCheckResult(
            claim=claim,
            truth_status=ClaimTruthStatus.UNRESOLVED,
            explanation=f"Cannot determine direction for relation '{claim.relation}'",
        )


def _check_direction(
    relation: str, subj_val: float, obj_val: float, subj_name: str, obj_name: str
) -> tuple[ClaimTruthStatus, str]:
    """Check a single directional comparison."""
    if relation == "higher_than":
        if subj_val > obj_val:
            return (
                ClaimTruthStatus.SUPPORTED,
                f"{subj_name} ({subj_val}%) > {obj_name} ({obj_val}%)",
            )
        elif subj_val < obj_val:
            return (
                ClaimTruthStatus.CONTRADICTED,
                f"CONTRADICTION: {subj_name} ({subj_val}%) < {obj_name} ({obj_val}%) — claim says higher",
            )
        else:
            return (
                ClaimTruthStatus.CONTRADICTED,
                f"Values equal ({subj_val}%) — claim says higher",
            )
    elif relation == "lower_than":
        if subj_val < obj_val:
            return (
                ClaimTruthStatus.SUPPORTED,
                f"{subj_name} ({subj_val}%) < {obj_name} ({obj_val}%)",
            )
        elif subj_val > obj_val:
            return (
                ClaimTruthStatus.CONTRADICTED,
                f"CONTRADICTION: {subj_name} ({subj_val}%) > {obj_name} ({obj_val}%) — claim says lower",
            )
        else:
            return (
                ClaimTruthStatus.CONTRADICTED,
                f"Values equal ({subj_val}%) — claim says lower",
            )
    elif relation == "equal_to":
        if abs(subj_val - obj_val) < 0.5:
            return (
                ClaimTruthStatus.SUPPORTED,
                f"Values approximately equal: {subj_val}% ≈ {obj_val}%",
            )
        else:
            return (
                ClaimTruthStatus.CONTRADICTED,
                f"Values differ: {subj_val}% vs {obj_val}%",
            )
    return ClaimTruthStatus.UNRESOLVED, f"Cannot verify relation '{relation}'"


def check_claims_against_facts(
    claims: list[ComparativeClaim],
    facts: list[NumericFact],
) -> list[ClaimCheckResult]:
    """Check each comparative claim against available numeric facts."""
    results: list[ClaimCheckResult] = []
    if not claims:
        return results
    if not facts:
        for claim in claims:
            results.append(
                ClaimCheckResult(
                    claim=claim,
                    truth_status=ClaimTruthStatus.UNRESOLVED,
                    explanation="No numeric facts available for verification",
                )
            )
        return results

    # Build fact lookup: entity -> list of NumericFact
    fact_map: dict[str, list[NumericFact]] = {}
    for f in facts:
        fact_map.setdefault(f.entity, []).append(f)

    for claim in claims:
        subj_facts = fact_map.get(claim.subject, [])
        obj_facts = fact_map.get(claim.object, [])

        if not subj_facts and not obj_facts:
            results.append(
                ClaimCheckResult(
                    claim=claim,
                    truth_status=ClaimTruthStatus.UNRESOLVED,
                    explanation=f"No numeric facts found for '{claim.subject}' or '{claim.object}'",
                )
            )
            continue

        # Find matching facts (same or compatible metric type)
        def _metric_compatible(fact_metric: str, claim_metric: str) -> bool:
            if fact_metric == claim_metric:
                return True
            # "rate" facts are compatible with any rate-like claim metric
            rate_words = (
                "rate",
                "rates",
                "treatment",
                "admission",
                "percentage",
                "proportion",
            )
            return fact_metric in rate_words or any(
                w in claim_metric for w in rate_words
            )

        subj_vals = [
            f for f in subj_facts if _metric_compatible(f.metric, claim.metric)
        ]
        obj_vals = [f for f in obj_facts if _metric_compatible(f.metric, claim.metric)]

        if not subj_vals or not obj_vals:
            # Special case for discrimination claims: check if object entity has facts
            if (
                claim.relation in ("discriminates_against", "disadvantages")
                and obj_vals
            ):
                results.append(
                    ClaimCheckResult(
                        claim=claim,
                        truth_status=ClaimTruthStatus.UNRESOLVED,
                        explanation=f"Found facts for '{claim.object}' but cannot verify discrimination claim without comparison",
                        supporting_facts=obj_vals,
                    )
                )
            else:
                results.append(
                    ClaimCheckResult(
                        claim=claim,
                        truth_status=ClaimTruthStatus.UNRESOLVED,
                        explanation=f"Insufficient facts to verify: subj={len(subj_vals)}, obj={len(obj_vals)}",
                    )
                )
            continue

        # Compare: check ALL pairs and pick the strongest signal.
        # If the claim source mentions a specific context (e.g. "engineering"),
        # try to use facts from that context. Otherwise use overall/first pair.
        best_result = _compare_claim_pairs(claim, subj_vals, obj_vals)
        results.append(best_result)

    return results


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def run_claim_checks(task: Task, parsed: AgentResponse) -> list[ClaimCheckResult]:
    """Extract facts and claims from task and response, then cross-check.

    Strategy:
    1. Extract numeric facts from task prompt (ground truth)
    2. Extract numeric facts from agent steps (agent's computed facts)
    3. Extract comparative claims from agent final answer + steps
    4. Check agent claims against task facts
    5. Check agent claims against agent's own computed facts
    """
    # Ground truth facts from task
    task_facts = extract_numeric_facts(task.prompt, "task_prompt")
    if task.reference_solution:
        task_facts.extend(
            extract_numeric_facts(task.reference_solution, "reference_solution")
        )

    # v0.4.2: Also extract probability facts from task prompt and reference
    task_facts.extend(extract_probability_facts(task.prompt, "task_prompt"))
    if task.reference_solution:
        task_facts.extend(
            extract_probability_facts(task.reference_solution, "reference_solution")
        )

    # Agent-computed facts from steps
    agent_facts: list[NumericFact] = []
    for i, step in enumerate(parsed.steps):
        agent_facts.extend(extract_numeric_facts(step, f"steps[{i}]"))
        agent_facts.extend(extract_probability_facts(step, f"steps[{i}]"))

    # All available facts (task has priority)
    all_facts = task_facts + agent_facts

    # Extract comparative claims from agent output
    claims: list[ComparativeClaim] = []
    claims.extend(extract_comparative_claims(parsed.final_answer, "final_answer"))
    for i, step in enumerate(parsed.steps):
        claims.extend(extract_comparative_claims(step, f"steps[{i}]"))
    for i, kc in enumerate(parsed.key_claims):
        claims.extend(extract_comparative_claims(kc, f"key_claims[{i}]"))

    # v0.4.2: probability direction claims (Monty Hall, etc.)
    claims.extend(
        extract_probability_direction_claims(parsed.final_answer, "final_answer")
    )
    for i, step in enumerate(parsed.steps):
        claims.extend(extract_probability_direction_claims(step, f"steps[{i}]"))

    # Deduplicate claims
    claims = _deduplicate_claims(claims)

    # Check claims against all available facts
    results = check_claims_against_facts(claims, all_facts)

    return results


# ---------------------------------------------------------------------------
# v0.4.2: Probability fact extraction (base rate & Monty Hall support)
# ---------------------------------------------------------------------------
# Supports:
#   - "the probability is 9%", "P(disease|positive) = 0.09"
#   - "2/3 probability", "probability of 1/3"
#   - "X% chance", "likelihood of 0.67"
# Does NOT attempt a full probabilistic parser — just pragmatic coverage
# for obvious decimal/fraction/probability-direction claims.

_PROB_ENTITY_KEYWORDS = [
    "disease",
    "positive",
    "car",
    "switch",
    "stay",
    "door",
    "door 1",
    "door 2",
    "door 3",
]

# Matches "probability is 9%", "probability ... is approximately 9%",
# "≈ 9%", etc.  Allows intervening words between keyword and value.
_PROB_DECIMAL_RE = re.compile(
    r"(?:probability|chance|likelihood)"
    r"(?:\s+\w+){0,8}\s+"  # up to 8 intervening words
    r"(?:is|=|:)\s*"
    r"(?:approximately?\s*|about\s*|roughly\s*|≈\s*)?"
    r"(\d+(?:\.\d+)?)\s*(%)?",
    re.IGNORECASE,
)

# Matches "P(Disease|Positive) = ..." then captures the LAST value in the chain
# e.g. "P(X) = 0.00099 / 0.01098 ≈ 0.09 ≈ 9%" → we want 9%
# Uses greedy match to end of string/sentence-ending period (not decimal points).
_P_NOTATION_RE = re.compile(
    r"P\(([^)]+)\)\s*=\s*(.+?)(?:(?<!\d)\.(?!\d)|(?=\s*P\()|$)",
    re.IGNORECASE,
)

_PROB_FRACTION_RE = re.compile(
    r"(?:probability|chance|likelihood)"
    r"(?:\s+\w+){0,8}\s+"
    r"(?:is|=|:)\s*"
    r"(?:approximately?\s*|about\s*|roughly\s*|≈\s*)?"
    r"(\d+)\s*/\s*(\d+)",
    re.IGNORECASE,
)

_STANDALONE_FRACTION_RE = re.compile(
    r"(\d+)\s*/\s*(\d+)\s*(?:probability|chance|likelihood)",
    re.IGNORECASE,
)

# Matches standalone "≈ 9%" or "≈ 0.09" (common in derivations)
_APPROX_VALUE_RE = re.compile(
    r"≈\s*(\d+(?:\.\d+)?)\s*(%)?",
)


def extract_probability_facts(text: str, source_field: str) -> list[NumericFact]:
    """Extract probability-related numeric facts from text.

    v0.4.2: Supports base-rate-neglect and Monty-Hall-style tasks.
    """
    facts: list[NumericFact] = []
    seen: set[tuple[str, float]] = set()

    def _add_fact(entity: str, val: float) -> None:
        key = (entity, round(val, 2))
        if key not in seen:
            seen.add(key)
            facts.append(
                NumericFact(
                    entity=entity,
                    metric="probability",
                    value=round(val, 2),
                    source_field=source_field,
                    context="probability",
                )
            )

    sentences = re.split(r"(?<!\d)\.(?!\d)|\n", text)
    for sent in sentences:
        sent_l = sent.lower().strip()
        if not sent_l:
            continue

        entity = _guess_probability_entity(sent_l)
        if not entity:
            continue

        # Strategy 1: P(X) = ... chains — take the LAST meaningful value
        # e.g. "P(D|P) = 0.00099 / 0.01098 ≈ 0.09 ≈ 9%" → 9%
        # Uses finditer to handle multiple P()-expressions in one sentence
        # (e.g. "P(Car=2|...) = 2/3. P(Car=1|...) = 1/3" when not split)
        p_matches = list(_P_NOTATION_RE.finditer(sent))
        if p_matches:
            for p_match in p_matches:
                p_expr = p_match.group(1)  # content inside P(...)
                chain = p_match.group(2)  # the value chain after =
                # Derive entity from P()-expression if possible
                p_entity = _guess_probability_entity(p_expr.lower()) or entity
                # Find last percentage in chain
                pcts = _PCT_RE.findall(chain)
                if pcts:
                    _add_fact(p_entity, float(pcts[-1]))
                    continue
                # Find last ≈ value
                approxes = _APPROX_VALUE_RE.findall(chain)
                if approxes:
                    val_str, pct_sign = approxes[-1]
                    val = float(val_str)
                    if not pct_sign and val < 1.0:
                        val = val * 100
                    _add_fact(p_entity, val)
                    continue
                # Check for fraction in the chain (e.g. "= 1/3")
                frac_matches = _FRAC_RE.findall(chain)
                if frac_matches:
                    num, den = float(frac_matches[-1][0]), float(frac_matches[-1][1])
                    if den > 0:
                        _add_fact(p_entity, round(num / den * 100, 2))
                    continue
                # Fall back to last decimal in chain
                decimals = re.findall(r"(\d+(?:\.\d+)?)", chain)
                if decimals:
                    val = float(decimals[-1])
                    if val < 1.0:
                        val = val * 100
                    _add_fact(p_entity, val)
            continue

        # Strategy 2: fractions FIRST — "probability is 2/3", "2/3 probability"
        # (must run before decimal to avoid matching numerator as standalone)
        found_fraction = False
        for m in _PROB_FRACTION_RE.finditer(sent_l):
            num, den = float(m.group(1)), float(m.group(2))
            if den > 0:
                _add_fact(entity, round(num / den * 100, 2))
                found_fraction = True
        for m in _STANDALONE_FRACTION_RE.finditer(sent_l):
            num, den = float(m.group(1)), float(m.group(2))
            if den > 0:
                _add_fact(entity, round(num / den * 100, 2))
                found_fraction = True

        # Strategy 3: decimal/percentage — "probability is 9%", "probability ... is 0.09"
        # Skip if we already found a fraction (avoids double-counting numerator)
        if not found_fraction:
            for m in _PROB_DECIMAL_RE.finditer(sent_l):
                val = float(m.group(1))
                has_pct = m.group(2) == "%"
                if val < 1.0 and not has_pct:
                    val = val * 100
                _add_fact(entity, val)

    return facts


def _guess_probability_entity(text: str) -> str:
    """Guess what probability entity a sentence is about."""
    text_l = text.lower()
    # Monty Hall entities — match "door 2", "car=2", "switch", etc.
    if (
        "door 2" in text_l
        or "car=2" in text_l
        or "car = 2" in text_l
        or "switch" in text_l
    ):
        return "door_2_switch"
    if (
        "door 1" in text_l
        or "car=1" in text_l
        or "car = 1" in text_l
        or "stay" in text_l
    ):
        return "door_1_stay"
    if "door 3" in text_l or "car=3" in text_l or "car = 3" in text_l:
        return "door_3"
    # Base rate entities
    if "disease" in text_l or "has the disease" in text_l or "actually has" in text_l:
        return "has_disease"
    if "positive" in text_l and ("false" in text_l or "not have" in text_l):
        return "false_positive"
    if "positive" in text_l:
        return "test_positive"
    # Generic probability context — if sentence mentions probability but no entity
    if any(w in text_l for w in ("probability", "chance", "likelihood")):
        return "generic_probability"
    return ""


# ---------------------------------------------------------------------------
# v0.4.2: Probability-direction claim extraction
# ---------------------------------------------------------------------------

_PROB_HIGHER_PATTERNS = [
    r"(?:should|better\s+to)\s+switch",
    r"switch(?:ing)?\s+(?:is|gives|has)\s+(?:a\s+)?(?:higher|better|greater)",
    r"(?:probability|chance)\s+(?:of\s+)?(?:winning|car)\s+(?:is\s+)?(?:higher|greater|better)\s+(?:if|when|by)\s+switch",
    r"(?:more\s+likely|better\s+off)\s+(?:to\s+)?switch",
]

_PROB_EQUAL_PATTERNS = [
    r"(?:probability|chance)\s+(?:is\s+)?(?:the\s+same|equal|50|1/2)\s+(?:whether|regardless|either)",
    r"(?:doesn't|does\s+not)\s+matter\s+(?:whether|if)\s+(?:you\s+)?switch",
]


def extract_probability_direction_claims(
    text: str,
    source_field: str,
) -> list[ComparativeClaim]:
    """Extract directional probability claims (switch vs stay, etc.).

    v0.4.2: Supports Monty Hall and similar conditional probability tasks.
    """
    claims: list[ComparativeClaim] = []
    text_l = text.lower()

    for pat in _PROB_HIGHER_PATTERNS:
        if re.search(pat, text_l):
            claims.append(
                ComparativeClaim(
                    subject="door_2_switch",
                    object="door_1_stay",
                    relation="higher_than",
                    metric="probability",
                    source_field=source_field,
                    source_text=text[:200],
                )
            )
            break

    for pat in _PROB_EQUAL_PATTERNS:
        if re.search(pat, text_l):
            claims.append(
                ComparativeClaim(
                    subject="door_2_switch",
                    object="door_1_stay",
                    relation="equal_to",
                    metric="probability",
                    source_field=source_field,
                    source_text=text[:200],
                )
            )
            break

    return claims


def _deduplicate_claims(claims: list[ComparativeClaim]) -> list[ComparativeClaim]:
    """Remove duplicate claims (same subject/object/relation)."""
    seen: set[tuple[str, str, str]] = set()
    unique: list[ComparativeClaim] = []
    for c in claims:
        key = (c.subject, c.object, c.relation)
        if key not in seen:
            seen.add(key)
            unique.append(c)
    return unique


def count_contradictions(results: list[ClaimCheckResult]) -> int:
    """Count the number of contradicted claims."""
    return sum(1 for r in results if r.truth_status == ClaimTruthStatus.CONTRADICTED)


def get_contradictions(results: list[ClaimCheckResult]) -> list[ClaimCheckResult]:
    """Return only contradicted claim check results."""
    return [r for r in results if r.truth_status == ClaimTruthStatus.CONTRADICTED]
