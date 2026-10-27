"""Study forensics checker of the Inspektorium audit runtime.

Evaluates agent responses against study/claim forensic cases.
Checks whether the agent correctly identifies:
- Overall classification (solid, overclaim, mechanism_vs_evidence, correlation_vs_causation)
- Expected findings (evidence_matches_claim, conclusion_exceeds_results, etc.)
- Avoids hallucinating major issues in solid cases

v0.6.1 hardening:
- Negation-aware false-positive detection (no more "no evidence of overclaiming" → FP)
- Flexible pattern families for finding detection (regex + phrase families)
- Hedge-language / decorative uncertainty detection in study context
  (optimistic hedge + null outcome + strong limitations → flag)

Confidence levels: most checks are HEURISTIC or MEDIUM CONFIDENCE.
"""

from __future__ import annotations

import re

from inspektorium.audit.schemas import (
    AgentResponse,
    EvidenceSpan,
    FailureCategory,
    FailureInstance,
    FailureSeverity,
    ForensicFlag,
    Task,
    TaskType,
)


def is_study_forensics_task(task: Task) -> bool:
    return task.task_type == TaskType.STUDY_FORENSICS


# ---------------------------------------------------------------------------
# Negation-aware text matching utilities
# ---------------------------------------------------------------------------

# Common negation prefixes that appear before the keyword in the same
# sentence or short window and flip its meaning.
_NEGATION_WINDOW = 6  # max words between negation cue and keyword start

_NEGATION_CUES = (
    "no ",
    "no evidence",
    "not ",
    "not an ",
    "not a ",
    "don't ",
    "do not ",
    "does not ",
    "doesn't ",
    "isn't ",
    "is not ",
    "without ",
    "absence of ",
    "lack of ",
    "did not find ",
    "found no ",
    "none of the ",
    "there is no ",
    "there are no ",
    "i do not see ",
    "cannot identify ",
    "no sign of ",
    "no indication of ",
    # v0.6.2: anti-claim constructions
    "avoids ",
    "avoid ",
    "avoiding ",
    "refrains from ",
    "refrain from ",
    "refraining from ",
    "stops short of ",
    "stop short of ",
    "stopped short of ",
    "free of ",
    "free from ",
    "steers clear of ",
    "steer clear of ",
)


def _is_negated(text: str, keyword: str) -> bool:
    """Check if a keyword occurrence in text is preceded by a negation cue.

    Looks backwards from the keyword position for a negation cue within
    a short word window. Returns True if the keyword is negated.
    """
    idx = text.find(keyword)
    if idx < 0:
        return False

    # Look at the text window before the keyword
    window_start = max(0, idx - 80)  # generous char window
    before = text[window_start:idx].lower()

    # Check for negation cues at the end of the window (close to keyword)
    for cue in _NEGATION_CUES:
        if before.endswith(cue) or before.endswith(cue.rstrip()):
            return True
        # Also check within the last few words
        before_words = before.split()
        cue_words = cue.strip().split()
        if len(before_words) >= len(cue_words):
            tail = before_words[-_NEGATION_WINDOW:]
            tail_text = " ".join(tail)
            if cue.strip() in tail_text:
                return True

    return False


def _is_analytical_reference(text: str, keyword: str) -> bool:
    """Check if a keyword occurrence in text is preceded by an analytical reference cue.

    Similar to _is_negated but checks for analytical cues like "checked for",
    "looked for", "evidence of" etc.
    """
    low = text.lower()
    idx = low.find(keyword)
    if idx < 0:
        return False

    window_start = max(0, idx - 80)
    before = low[window_start:idx]
    before_words = before.split()
    tail = " ".join(before_words[-_NEGATION_WINDOW:]) if before_words else ""

    return any(cue.strip() in tail for cue in _ANALYTICAL_REFERENCE_CUES)


def _keyword_match_non_negated(text: str, keyword: str) -> bool:
    """Check if keyword appears in text in a non-negated context.

    Returns True only if the keyword is found AND not negated.
    """
    low = text.lower()
    if keyword not in low:
        return False
    # Check all occurrences
    start = 0
    while True:
        idx = low.find(keyword, start)
        if idx < 0:
            return False
        if not _is_negated(low, keyword):
            # Double-check: look at this specific occurrence
            window_start = max(0, idx - 80)
            before = low[window_start:idx]
            negated = any(
                cue.strip() in before.split()[-_NEGATION_WINDOW:]
                if len(before.split()) >= 1
                else False
                for cue in []
            )  # placeholder, use proper check below
            # Use the direct check
            before_text = " ".join(before.split()[-_NEGATION_WINDOW:])
            is_neg = any(cue.strip() in before_text for cue in _NEGATION_CUES)
            if not is_neg:
                return True
        start = idx + len(keyword)
    return False


# ---------------------------------------------------------------------------
# v0.6.1: Flexible pattern families for finding detection
# ---------------------------------------------------------------------------
# Each finding type has:
#   - keywords: simple substring matches (fast, broad)
#   - patterns: compiled regex patterns (flexible, precise)
# Both are checked; either can trigger a match.

_FINDING_PATTERNS: dict[str, dict] = {
    # --- Solid-case signals ---
    "evidence_matches_claim": {
        "keywords": [
            "evidence supports",
            "evidence matches",
            "claim is supported",
            "well-supported",
            "well supported",
            "findings support",
            "data supports",
            "results support",
            "consistent with",
            "appropriately supported",
            "adequate evidence",
            "evidence aligns",
            "claims are justified",
            "findings are consistent",
            "data back",
            "empirically supported",
            "conclusions follow from",
        ],
        "patterns": [
            re.compile(
                r"evidence\s+(?:clearly\s+)?(?:supports?|backs?|confirms?|matches)",
                re.I,
            ),
            re.compile(
                r"(?:claim|conclusion)s?\s+(?:is|are)\s+(?:well[- ])?supported", re.I
            ),
            re.compile(
                r"results?\s+(?:support|justify|back)\s+(?:the\s+)?(?:claim|conclusion)",
                re.I,
            ),
            re.compile(
                r"(?:data|findings?)\s+(?:support|confirm|match)\s+(?:the\s+)?(?:claim|conclusion)",
                re.I,
            ),
        ],
    },
    "cautious_scope_control": {
        "keywords": [
            "limitation",
            "acknowledge",
            "caveat",
            "scope",
            "restrict",
            "careful",
            "appropriate uncertainty",
            "honest",
            "transparent",
            "qualified",
            "appropriate caution",
            "properly qualified",
            "limit their conclusions",
            "appropriate caveats",
            "do not overgenerali",
            "appropriately hedged",
        ],
        "patterns": [
            re.compile(
                r"(?:author|researcher|study)s?\s+(?:appropriately\s+)?(?:acknowledge|note|caution|limit|qualify)",
                re.I,
            ),
            re.compile(
                r"(?:caution|limitation|caveat)s?\s+(?:are\s+)?(?:noted|acknowledged|stated|appropriate)",
                re.I,
            ),
            re.compile(
                r"(?:scope|generali[sz]ability)\s+(?:is\s+)?(?:limited|restricted|narrow|appropriately)",
                re.I,
            ),
            re.compile(
                r"(?:honest|transparent|careful)\s+(?:about|regarding|in)\s+(?:limitation|uncertainty)",
                re.I,
            ),
        ],
    },
    "none_or_minor": {
        "keywords": [
            "no major",
            "no significant",
            "no substantive",
            "minor issue",
            "well-designed",
            "well designed",
            "appropriate",
            "no epistemic",
            "no serious",
            "no fundamental",
            "no critical flaw",
            "methodologically sound",
        ],
        "patterns": [
            re.compile(
                r"no\s+(?:major|significant|serious|substantive|fundamental|critical)\s+(?:flaw|issue|problem|error|weakness)",
                re.I,
            ),
            re.compile(
                r"(?:study|trial|research)\s+(?:is|appears?)\s+(?:well[- ]designed|sound|solid|rigorous)",
                re.I,
            ),
        ],
    },
    # --- Overclaim signals ---
    "conclusion_exceeds_results": {
        "keywords": [
            "exceeds",
            "beyond the data",
            "beyond the evidence",
            "overstated",
            "overinterpret",
            "exaggerat",
            "not warranted",
            "not supported by",
            "goes beyond",
            "stronger than",
            "disproportionate",
            "inflated",
            "beyond what the",
            "overreach",
            "unwarranted",
            "unjustified conclusion",
            "claim is stronger than",
            "more than the data",
        ],
        "patterns": [
            re.compile(
                r"conclusion\s+(?:goes?\s+)?(?:beyond|exceeds?|overreach)", re.I
            ),
            re.compile(
                r"(?:claim|conclusion|interpretation)s?\s+(?:is|are)\s+(?:not\s+)?(?:supported|warranted|justified)\s+by",
                re.I,
            ),
            re.compile(
                r"(?:results?|data|evidence|findings?)\s+(?:do\s+not\s+|don'?t\s+)?(?:support|justify|warrant)\s+(?:the\s+)?(?:claim|conclusion)",
                re.I,
            ),
            re.compile(r"(?:over(?:stat|interpret|claim|reach|sell))", re.I),
            re.compile(
                r"(?:goes?|went)\s+beyond\s+(?:the\s+)?(?:data|evidence|results?|findings?)",
                re.I,
            ),
            re.compile(
                r"stronger\s+(?:claim|conclusion)\s+than\s+(?:the\s+)?(?:data|evidence|results?)",
                re.I,
            ),
        ],
    },
    "unsupported_generalization": {
        "keywords": [
            "all ages",
            "all people",
            "everyone",
            "overgenerali",
            "extrapolat",
            "beyond the sample",
            "broader population",
            "universal",
            "sweeping",
            "beyond the study population",
            "beyond the studied",
            "unjustified extension",
            "unwarranted generali",
        ],
        "patterns": [
            re.compile(
                r"generali[sz](?:e|es|ed|ation|ations?)\s+(?:beyond|to\s+(?:all|other|broader|wider))",
                re.I,
            ),
            re.compile(r"(?:unsupported|unwarranted|unjustified)\s+generali[sz]", re.I),
            re.compile(r"extrapolat(?:e|es|ed|ion|ions?)\s+(?:beyond|from|to)", re.I),
            re.compile(
                r"(?:extends?|applied|applies)\s+(?:the\s+)?(?:findings?|results?|conclusions?)\s+(?:to\s+)?(?:all|broader|wider|other|general)",
                re.I,
            ),
            re.compile(
                r"(?:beyond|outside)\s+(?:the\s+)?(?:study|sample|studied)\s+(?:population|group|sample)",
                re.I,
            ),
            re.compile(
                r"(?:claim|suggest)s?\s+(?:it\s+)?(?:could|might|may)\s+(?:help|benefit|work\s+for)\s+(?:all|everyone|people\s+of\s+all)",
                re.I,
            ),
        ],
    },
    "decorative_uncertainty": {
        "keywords": [
            "decorative",
            "performative",
            "token",
            "lip service",
            "hedge",
            "nominal",
            "surface-level caveat",
            "pro forma",
            "formulaic caveat",
            "caveat does not constrain",
            "hedge without substance",
        ],
        "patterns": [
            re.compile(
                r"(?:decorative|performative|token|nominal|formulaic)\s+(?:uncertainty|caveat|hedge|caution|qualification)",
                re.I,
            ),
            re.compile(
                r"(?:caveat|hedge|caution)\s+(?:is|appears?|seems?)\s+(?:decorative|performative|token|nominal|cosmetic|superficial)",
                re.I,
            ),
            re.compile(
                r"(?:further|more)\s+research\s+(?:is\s+)?needed.*(?:but|yet|however|while|despite)",
                re.I,
            ),
            re.compile(
                r"(?:caveat|hedge)s?\s+(?:do\s+not|doesn'?t|does\s+not)\s+(?:constrain|limit|qualify)",
                re.I,
            ),
        ],
    },
    # --- Mechanism vs evidence signals ---
    "mechanism_not_demonstrated": {
        "keywords": [
            "not demonstrated",
            "not proven in human",
            "animal model",
            "mice",
            "rodent",
            "preclinical",
            "translation gap",
            "unproven",
            "not established",
            "not shown in human",
            "not demonstrated in human",
            "preclinical to clinical",
            "mouse to human",
            "animal to human",
            "rodent model",
            "in vitro",
            "not yet established in",
        ],
        "patterns": [
            re.compile(
                r"mechanism\s+(?:is\s+)?(?:not|hasn'?t\s+been)\s+(?:demonstrated|established|proven|shown|confirmed)",
                re.I,
            ),
            re.compile(
                r"(?:causal|mechanistic)\s+(?:pathway|link|chain|relationship)\s+(?:is\s+)?(?:not|hasn'?t\s+been)\s+(?:demonstrated|established|proven)",
                re.I,
            ),
            re.compile(
                r"(?:only|exclusively)\s+(?:shown|demonstrated|tested|proven)\s+in\s+(?:mice|rodents?|animals?|vitro)",
                re.I,
            ),
            re.compile(
                r"(?:translat|transfer|extend)(?:e|es|ed|ion)\s+(?:from\s+)?(?:animal|mice|rodent|preclinical)\s+(?:to\s+)?human",
                re.I,
            ),
            re.compile(
                r"(?:no|lack\s+of|without)\s+(?:human\s+)?(?:clinical\s+)?(?:evidence|data|trials?|studies)",
                re.I,
            ),
            re.compile(
                r"(?:evidence|data)\s+(?:is\s+)?(?:limited\s+to|restricted\s+to|only\s+from)\s+(?:animal|mice|rodent|preclinical)",
                re.I,
            ),
            re.compile(
                r"(?:does\s+not|cannot|can'?t)\s+(?:justify|support)\s+(?:a\s+)?(?:causal|mechanistic)\s+(?:claim|interpretation)",
                re.I,
            ),
        ],
    },
    # --- Correlation vs causation signals ---
    "correlation_as_causation": {
        "keywords": [
            "correlation",
            "causation",
            "correlat",
            "causal",
            "cross-sectional",
            "observational",
            "confound",
            "not causal",
            "does not prove",
            "association",
            "reverse causation",
            "third variable",
            "causal claim from correlat",
            "spurious",
            "cannot infer causation",
            "does not establish causation",
        ],
        "patterns": [
            re.compile(
                r"correlation\s+(?:is\s+)?(?:not|doesn'?t|does\s+not)\s+(?:imply|prove|mean|equal|establish)\s+causation",
                re.I,
            ),
            re.compile(
                r"(?:causal|causation)\s+(?:claim|inference|conclusion|interpretation)\s+(?:from|based\s+on)\s+(?:correlat|observat|cross-sectional|survey)",
                re.I,
            ),
            re.compile(
                r"(?:treat|present|interpret|equat)(?:s|ed|ing)?\s+(?:a\s+)?(?:correlation|association|observat)\s+(?:as|like)\s+(?:causation|causal)",
                re.I,
            ),
            re.compile(
                r"(?:confound|confounder|confounding)\s+(?:variable|factor)s?\s+(?:are\s+)?(?:not\s+)?(?:controlled|accounted|addressed|considered)",
                re.I,
            ),
            re.compile(
                r"(?:cross-sectional|observational|survey)\s+(?:data|design|study|evidence)\s+(?:cannot|does\s+not|can'?t)\s+(?:prove|establish|demonstrate)\s+(?:caus)",
                re.I,
            ),
            re.compile(
                r"(?:implies?|suggests?|assumes?)\s+causation\s+(?:from|without|despite)\s+(?:only\s+)?(?:correlat|associat|observat)",
                re.I,
            ),
        ],
    },
}


# ---------------------------------------------------------------------------
# v0.6.1: Hedge-language / decorative uncertainty in study context
# ---------------------------------------------------------------------------

# Optimistic hedge phrases that may mask weak evidence
_OPTIMISTIC_HEDGE_PHRASES = [
    "promising signal",
    "promising finding",
    "promising result",
    "encouraging trend",
    "encouraging result",
    "encouraging finding",
    "suggestive result",
    "suggestive finding",
    "suggestive evidence",
    "may help",
    "may benefit",
    "may improve",
    "may protect",
    "potentially beneficial",
    "potentially effective",
    "potentially helpful",
    "could help",
    "could benefit",
    "could improve",
    "appears to help",
    "appears to benefit",
    "appears to improve",
    "hopeful",
    "reason for optimism",
    "grounds for hope",
]

# Markers indicating the primary/main outcome was null or weak
_NULL_OUTCOME_MARKERS = [
    "did not change",
    "did not affect",
    "did not improve",
    "no effect on",
    "no significant effect",
    "no statistically significant",
    "null result",
    "null finding",
    "null primary",
    "primary outcome was null",
    "primary outcome showed no",
    "failed to show",
    "failed to demonstrate",
    "failed to reach",
    "no difference in the primary",
    "no significant difference in primary",
    "primary endpoint was not met",
    "did not meet the primary",
]

# Markers indicating strong study limitations
_STRONG_LIMITATION_MARKERS = [
    "small sample",
    "limited sample",
    "modest sample",
    "conducted remotely",
    "remote conduct",
    "self-report",
    "after onset",
    "after infection",
    "after diagnosis",
    "short follow-up",
    "short duration",
    "brief follow-up",
    "no blinding",
    "unblinded",
    "open-label",
    "wait-list control",
    "waitlist control",
    "single site",
    "single center",
    "single centre",
    "percentage point",
    "4 percentage",
    "small absolute",
    "clinically marginal",
    "clinically modest",
]

# Compiled regex for small effect sizes mentioned with optimism
_SMALL_EFFECT_PATTERN = re.compile(
    r"(\d{1,2})\s*(?:percentage\s+points?|pp|percent)\s*"
    r"(?:difference|improvement|reduction|benefit|advantage)",
    re.I,
)


def _detect_hedge_overclaim(task: Task, p: AgentResponse) -> dict:
    """Detect study-context decorative uncertainty / hedge overclaim.

    Checks for the combination of:
    1. Optimistic hedge language in the input text (task prompt)
    2. Null/weak primary outcome markers in the input text
    3. Strong limitation markers in the input text

    Returns a dict with detection result and evidence.
    """
    input_text = task.prompt.lower()
    agent_text = " ".join(
        [
            p.final_answer,
            *p.steps,
            *p.key_claims,
        ]
    ).lower()

    # Score each dimension
    hedge_hits = [ph for ph in _OPTIMISTIC_HEDGE_PHRASES if ph in input_text]
    null_hits = [m for m in _NULL_OUTCOME_MARKERS if m in input_text]
    limit_hits = [m for m in _STRONG_LIMITATION_MARKERS if m in input_text]

    # Small effect size detection
    small_effect = False
    for m in _SMALL_EFFECT_PATTERN.finditer(input_text):
        val = int(m.group(1))
        if val <= 10:  # 10 percentage points or less = small effect
            small_effect = True

    has_hedge = len(hedge_hits) > 0
    has_null = len(null_hits) > 0
    has_limits = len(limit_hits) >= 2 or (len(limit_hits) >= 1 and small_effect)

    # The agent should flag this pattern — did it?
    agent_flagged = any(
        phrase in agent_text
        for phrase in [
            "decorative",
            "overclaim",
            "overstated",
            "exceeds",
            "beyond the data",
            "beyond the evidence",
            "weak finding",
            "null primary",
            "small effect",
            "marginal",
            "not warranted",
            "disproportionate",
            "inflated",
        ]
    )

    # Combination trigger: hedge + (null OR strong limits) = suspicious
    is_suspicious = has_hedge and (has_null or has_limits)

    return {
        "is_suspicious": is_suspicious,
        "hedge_phrases": hedge_hits,
        "null_outcome_markers": null_hits,
        "limitation_markers": limit_hits,
        "small_effect_detected": small_effect,
        "agent_flagged": agent_flagged,
    }


# ---------------------------------------------------------------------------
# False positive detection — v0.6.1 negation-aware
# ---------------------------------------------------------------------------

_SOLID_FALSE_POSITIVE_KEYWORDS = [
    "overclaim",
    "conclusion exceeds",
    "unsupported generalization",
    "correlation as causation",
    "mechanism not demonstrated",
    "major flaw",
    "serious error",
    "fundamental problem",
    "fabricat",
    "fraud",
    "p-hack",
]

# v0.6.3: Analytical reference cues — when the agent mentions a keyword
# as part of its analysis process ("checked for X", "looked for X"),
# this is NOT a positive finding of X.
_ANALYTICAL_REFERENCE_CUES = (
    "checked for ",
    "check for ",
    "checking for ",
    "looked for ",
    "look for ",
    "looking for ",
    "searched for ",
    "search for ",
    "searching for ",
    "tested whether ",
    "test whether ",
    "testing whether ",
    "assessed whether ",
    "assess whether ",
    "assessing whether ",
    "evaluated whether ",
    "evaluate whether ",
    "evaluating whether ",
    "examined for ",
    "examine for ",
    "examining for ",
    "screened for ",
    "screen for ",
    "screening for ",
    "inspected for ",
    "inspect for ",
    "inspecting for ",
    "investigated whether ",
    "investigate whether ",
    "considered whether ",
    "consider whether ",
    "ruled out ",
    "rule out ",
    "ruling out ",
    "signs of ",
    "sign of ",
    "evidence of ",
    "indication of ",
    "indications of ",
)

# v0.6.3: Criticism-direction cues — phrases that WEAKEN a claim rather
# than asserting it. When these appear near an FP keyword, they indicate
# the agent is noting limitations (positive analytical behaviour), not
# asserting that the study has the flaw.
_WEAKENING_CUES = (
    "limited sample",
    "small sample",
    "modest sample",
    "cautious interpretation",
    "interpreted cautiously",
    "interpret with caution",
    "further research needed",
    "further research is needed",
    "more research is needed",
    "additional research needed",
    "preliminary evidence",
    "preliminary findings",
    "preliminary results",
    "does not establish causality",
    "does not establish causation",
    "does not prove causation",
    "cannot establish causation",
    "should be interpreted carefully",
    "interpret carefully",
    "results are suggestive only",
    "suggestive but not conclusive",
    "tentative conclusion",
    "tentative finding",
    "acknowledges limitation",
    "acknowledge limitation",
    "within appropriate scope",
    "appropriately scoped",
    "honest about limitation",
    "transparent about limitation",
)


def _detect_false_positives(p: AgentResponse) -> list[str]:
    """Detect if the agent hallucinated major issues.

    v0.6.1: Negation-aware — phrases like "no evidence of overclaiming"
    or "this is not a correlation-as-causation problem" no longer match.
    """
    all_text = " ".join(
        [
            p.final_answer,
            *p.steps,
            *p.key_claims,
        ]
    ).lower()

    found = []
    for kw in _SOLID_FALSE_POSITIVE_KEYWORDS:
        if kw not in all_text:
            continue

        # Check ALL occurrences of this keyword
        has_non_negated = False
        search_text = all_text
        offset = 0
        while True:
            idx = search_text.find(kw, offset)
            if idx < 0:
                break

            # Look at the window before this occurrence
            window_start = max(0, idx - 80)
            before = search_text[window_start:idx]

            # Split on sentence boundaries to avoid cross-sentence negation
            # Only consider text after the last sentence break
            for sep in (".", ",", ";", "!", "?"):
                last_sep = before.rfind(sep)
                if last_sep >= 0:
                    before = before[last_sep + 1 :]

            before_words = before.split()
            # Check the last few words for negation cues
            tail = " ".join(before_words[-_NEGATION_WINDOW:]) if before_words else ""

            is_negated = any(cue.strip() in tail for cue in _NEGATION_CUES)

            # v0.6.3: Check for analytical reference cues
            is_analytical = any(
                cue.strip() in tail for cue in _ANALYTICAL_REFERENCE_CUES
            )

            # v0.6.3: Check for weakening/criticism-direction cues in the
            # surrounding sentence. If the keyword appears in a context where
            # the agent is noting limitations (weakening direction), it's not
            # asserting the flaw — it's praising honest reporting.
            # Look at a wider window (the sentence containing the keyword)
            sent_start = max(
                search_text.rfind(".", 0, idx),
                search_text.rfind("!", 0, idx),
                search_text.rfind("?", 0, idx),
            )
            sent_start = sent_start + 1 if sent_start >= 0 else max(0, idx - 200)
            sent_end_candidates = [
                search_text.find(".", idx + len(kw)),
                search_text.find("!", idx + len(kw)),
                search_text.find("?", idx + len(kw)),
            ]
            sent_end = min(
                (c for c in sent_end_candidates if c >= 0), default=len(search_text)
            )
            sentence = search_text[sent_start:sent_end].lower()
            is_weakening = any(wc in sentence for wc in _WEAKENING_CUES)

            if not is_negated and not is_analytical and not is_weakening:
                has_non_negated = True
                break

            offset = idx + len(kw)

        if has_non_negated:
            found.append(kw)

    return found


# ---------------------------------------------------------------------------
# Label detection
# ---------------------------------------------------------------------------


def _detect_label(p: AgentResponse) -> str | None:
    """Attempt to detect what label the agent assigned.

    v0.6.3: Restructured to strongly prioritize final_answer over analysis body.
    v0.6.6: Added "solid" to step 1 exact label check. Removed ambiguous
    "not causal" keyword from correlation_vs_causation (matched approving
    contexts like "presented as associations, not causal effects").

    Priority order:
    1. Exact label string in final_answer (strongest) — all 4 labels checked
    2. Keyword scoring in final_answer ONLY (strong)
    3. Keyword scoring in key_claims as fallback (weak, 0.5x weight)
    """
    fa = p.final_answer.lower()

    # 1. Exact label mention in final_answer (strongest signal)
    # Compound labels first (unambiguous)
    if "mechanism_vs_evidence" in fa or "mechanism vs evidence" in fa:
        return "mechanism_vs_evidence"
    if "correlation_vs_causation" in fa or "correlation vs causation" in fa:
        return "correlation_vs_causation"

    # Single-word labels need negation + analytical reference checks
    if "overclaim" in fa or "over-claim" in fa:
        if (
            not _is_negated(fa, "overclaim")
            and not _is_negated(fa, "over-claim")
            and not _is_analytical_reference(fa, "overclaim")
            and not _is_analytical_reference(fa, "over-claim")
        ):
            return "overclaim"

    # v0.6.6: "solid" in final_answer — strongest signal for solid classification
    if "solid" in fa and not _is_negated(fa, "solid"):
        return "solid"

    # 2. Keyword scoring — final_answer gets full weight, key_claims get 0.5x
    label_keywords = {
        "solid": [
            "well-designed",
            "well designed",
            "no major issue",
            "no significant flaw",
            "sound methodology",
            "methodologically sound",
            "solid study",
            "solid reporting",
        ],
        "overclaim": [
            "overstated",
            "exaggerat",
            "goes beyond",
            "exceeds the evidence",
            "inflated",
            "overreach",
            "unwarranted conclusion",
        ],
        "mechanism_vs_evidence": [
            "mechanism vs",
            "mechanism versus",
            "animal model",
            "preclinical",
            "translation gap",
            "mechanism not demonstrated",
            "not proven in human",
            "not demonstrated in humans",
        ],
        "correlation_vs_causation": [
            "correlation treated as",
            "correlation as causation",
            "correlation is treated as",
            "correlation mistaken for",
            "does not establish causation",
            "cannot prove causation",
            "causal claim from",
            "cross-sectional",
            "merely correlational",
            "only correlational",
            "associational not causal",
        ],
    }

    # Score final_answer (full weight = 2 per hit)
    scores: dict[str, float] = {}
    for label, kws in label_keywords.items():
        scores[label] = sum(2 for kw in kws if kw in fa)

    # Score key_claims (half weight = 1 per hit) — only as fallback signal
    claims_text = " ".join(p.key_claims).lower()
    for label, kws in label_keywords.items():
        scores[label] += sum(1 for kw in kws if kw in claims_text)

    # If final_answer alone has a clear winner, use it (ignore body noise)
    fa_scores: dict[str, float] = {}
    for label, kws in label_keywords.items():
        fa_scores[label] = sum(1 for kw in kws if kw in fa)

    fa_best = max(fa_scores.values()) if fa_scores else 0
    if fa_best > 0:
        fa_candidates = [k for k, v in fa_scores.items() if v == fa_best]
        if len(fa_candidates) == 1:
            return fa_candidates[0]
        # If tied in final_answer, prefer specific over solid
        if "solid" in fa_candidates and len(fa_candidates) > 1:
            fa_candidates.remove("solid")
        if len(fa_candidates) == 1:
            return fa_candidates[0]

    # Fall back to combined scoring
    if not any(scores.values()):
        if "solid" in fa:
            return "solid"
        return None

    best_score = max(scores.values())
    candidates = [k for k, v in scores.items() if v == best_score]
    if len(candidates) > 1 and "solid" in candidates:
        candidates.remove("solid")
    return candidates[0]


# ---------------------------------------------------------------------------
# Finding detection — v0.6.1 with pattern families
# ---------------------------------------------------------------------------


def _detect_findings(p: AgentResponse) -> list[str]:
    """Detect which finding types the agent's response mentions.

    v0.6.1: Uses both keyword and regex pattern matching for each finding
    type. Either a keyword hit or a pattern match triggers detection.
    """
    all_text = " ".join(
        [
            p.final_answer,
            *p.steps,
            *p.key_claims,
            *p.assumptions,
            *p.alternative_hypotheses,
            *p.uncertainties,
            *p.self_check,
        ]
    ).lower()

    detected = []
    for finding_type, config in _FINDING_PATTERNS.items():
        # Check keywords
        keywords = config.get("keywords", [])
        if any(kw in all_text for kw in keywords):
            detected.append(finding_type)
            continue

        # Check regex patterns
        patterns = config.get("patterns", [])
        if any(pat.search(all_text) for pat in patterns):
            detected.append(finding_type)

    return detected


# ---------------------------------------------------------------------------
# Main checker
# ---------------------------------------------------------------------------


def run_study_forensics_checks(
    task: Task,
    parsed: AgentResponse,
) -> dict:
    """Run study forensics evaluation.

    Returns a dict with:
    - is_study_forensics: bool
    - gold_label: str
    - detected_label: str | None
    - label_correct: bool
    - expected_findings: list of expected finding types
    - detected_findings: list of detected finding types
    - matched_findings: list of findings both expected and detected
    - missed_findings: list of expected but not detected
    - extra_findings: list of detected but not expected
    - false_positives: list (only for solid cases)
    - finding_recall: float (0-1)
    - hedge_overclaim: dict (v0.6.1 hedge analysis)
    - failures: list[FailureInstance]
    - flags: list[ForensicFlag]
    - scores: dict with label_score, finding_recall, false_positive_penalty
    """
    if not is_study_forensics_task(task):
        return {"is_study_forensics": False}

    gold_label = task.gold_label or task.expected_answer or ""
    expected_finding_types = [ef.finding for ef in task.expected_findings]

    detected_label = _detect_label(parsed)
    detected_findings = _detect_findings(parsed)

    matched = [f for f in expected_finding_types if f in detected_findings]
    missed = [f for f in expected_finding_types if f not in detected_findings]
    extra = [f for f in detected_findings if f not in expected_finding_types]

    finding_recall = (
        len(matched) / len(expected_finding_types) if expected_finding_types else 1.0
    )

    # Label correctness
    label_correct = (detected_label == gold_label) if detected_label else False

    # False positive check (only for solid cases)
    false_positives: list[str] = []
    if gold_label == "solid":
        false_positives = _detect_false_positives(parsed)

    # v0.6.1: Hedge-language / decorative uncertainty analysis
    hedge_result = _detect_hedge_overclaim(task, parsed)

    # Build failures and flags
    failures: list[FailureInstance] = []
    flags: list[ForensicFlag] = []

    if not label_correct:
        failures.append(
            FailureInstance(
                category=FailureCategory.WRONG_ANSWER.value,
                severity=FailureSeverity.MAJOR.value,
                description=(
                    f"Study classification incorrect: expected '{gold_label}', "
                    f"detected '{detected_label or 'unknown'}'"
                ),
                evidence=[
                    EvidenceSpan(
                        text=parsed.final_answer[:200],
                        source_field="final_answer",
                        relevance="Agent's classification",
                    )
                ],
                impact_on_score="correctness",
                confidence="MEDIUM CONFIDENCE",
            )
        )

    for m in missed:
        severity = FailureSeverity.MODERATE.value
        for ef in task.expected_findings:
            if ef.finding == m and ef.severity == "major":
                severity = FailureSeverity.MAJOR.value
                break

        failures.append(
            FailureInstance(
                category=FailureCategory.MISSED_KEY_INSIGHT.value,
                severity=severity,
                description=f"Missed expected finding: {m}",
                evidence=[
                    EvidenceSpan(
                        text=f"Expected: {m}",
                        source_field="(task expectation)",
                        relevance=f"Finding '{m}' not detected in agent response",
                    )
                ],
                impact_on_score="insight_depth",
                confidence="HEURISTIC",
            )
        )

    for fp in false_positives:
        failures.append(
            FailureInstance(
                category=FailureCategory.OVERCLAIMING.value,
                severity=FailureSeverity.MAJOR.value,
                description=f"False positive: agent flagged '{fp}' in a solid case",
                evidence=[
                    EvidenceSpan(
                        text=parsed.final_answer[:200],
                        source_field="final_answer",
                        relevance="Agent hallucinated a major issue in a solid study",
                    )
                ],
                impact_on_score="correctness",
                confidence="MEDIUM CONFIDENCE",
            )
        )

    if extra and gold_label == "solid":
        flags.append(
            ForensicFlag(
                flag_type="study_forensics_overflagging",
                description=f"Agent raised extra findings in solid case: {', '.join(extra)}",
                severity="minor",
            )
        )

    # v0.6.1: Hedge-overclaim flag
    if hedge_result["is_suspicious"] and not hedge_result["agent_flagged"]:
        flags.append(
            ForensicFlag(
                flag_type="hedge_overclaim_undetected",
                description=(
                    f"Input text contains optimistic hedge language "
                    f"({', '.join(hedge_result['hedge_phrases'][:2])}) "
                    f"combined with "
                    f"{'null outcome markers' if hedge_result['null_outcome_markers'] else 'strong limitations'}"
                    f", but agent did not flag this as overclaim or decorative uncertainty"
                ),
                evidence=[
                    EvidenceSpan(
                        text=task.prompt[:200],
                        source_field="(task prompt)",
                        relevance="Hedge + null/weak evidence pattern in input",
                    )
                ],
                severity="moderate",
            )
        )

    # Scores
    label_score = 1.0 if label_correct else 0.0
    fp_penalty = min(len(false_positives) * 0.15, 0.5)

    return {
        "is_study_forensics": True,
        "gold_label": gold_label,
        "detected_label": detected_label,
        "label_correct": label_correct,
        "expected_findings": expected_finding_types,
        "detected_findings": detected_findings,
        "matched_findings": matched,
        "missed_findings": missed,
        "extra_findings": extra,
        "false_positives": false_positives,
        "finding_recall": round(finding_recall, 3),
        "hedge_overclaim": hedge_result,
        "failures": failures,
        "flags": flags,
        "scores": {
            "label_score": label_score,
            "finding_recall": round(finding_recall, 3),
            "false_positive_penalty": round(fp_penalty, 3),
        },
    }
