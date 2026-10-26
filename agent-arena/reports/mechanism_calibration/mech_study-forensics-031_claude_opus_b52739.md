# Forensic Dossier: Study Forensics: Rapamycin for human longevity — promise vs proof

**Run ID:** `mech_study-forensics-031_claude_opus_b52739`  
**Task:** study-forensics-031 | study_forensics | hard | study_forensics  
**Timestamp:** 2026-04-06T15:45:57.395658+00:00  
**Task Family:** mechanism_vs_evidence  
**Trap Type:** strong_preclinical_weak_human  
**Ambiguity:** medium  

## Executive Summary

**Agents tested:** Claude Opus
**Winner:** Claude Opus — **36.7/100** (margin: 0.0)
**Failure modes:** decorative_self_check, decorative_uncertainty, missed_key_insight, unsupported_conclusion, unused_assumption, wrong_answer
**Forensic flags:** 2
**Consistency findings:** 6
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Opus | 0.0/30 | 0.0/8 | 4.8/8 | 4.3/6 | 3.6/6 | 6.0/6 | 0.0/8 | 8.0/8 | 0.0/10 | 10.0/10 | **36.7/100** |

## Study Forensics Audit

### Claude Opus

**Classification:** `solid` [x] (gold: `mechanism_vs_evidence`)
**Finding Recall:** 50%
**Matched Findings:** mechanism_not_demonstrated
**Missed Findings:** decorative_uncertainty
**Extra Findings:** cautious_scope_control, none_or_minor, conclusion_exceeds_results, unsupported_generalization, correlation_as_causation

## Reasoning Integrity Audit

### Claude Opus
**Classification:** Correct and well-supported
**Load-bearing steps:** 0 / 7

## Mechanism Analysis

### Claude Opus
| Aspect | Status |
|--------|--------|
| Concept named | :x: none |
| Mechanism described | :x: (0 sentence(s)) |
| Grounded to case | :x: (0 sentence(s)) |

**Missing:** concept not named, mechanism not described, mechanism not grounded to case data

## Grounding Audit

### Claude Opus
Conclusion claims: 1
- Direct support: 0
- Indirect support: 0
- Unsupported: 1
- Contradicted: 0

**Unsupported claims:**
- "solid"


## Forensic Flags

### Claude Opus

- **[MAJOR]** `well_reasoned_wrong`: Wrong answer but structured reasoning — may have a subtle logic error
  - `final_answer`: "solid"
- **[MODERATE]** `unsupported_conclusion_claims`: 1/1 conclusion claims lack step support
  - `final_answer`: "solid"


## Evidence Map

### Claude Opus

**Correctness:** 0.0/30
  - (+) `final_answer`: "solid"
    _Agent's answer for correctness check_
  - Note: No match (got: solid)

**Support Strength:** 0.0/8
  - (-) `final_answer`: "solid"
    _Conclusion not supported by steps_
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 7
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[2]`: "Observed that human evidence is limited to one trial testing specific endpoints (fat/muscle), not aging"
    _Most informative reasoning step_
  - Note: 7 reasoning steps
  - Note: Low step utility: 0/7 steps contribute

**Assumption Discipline:** 4.3/6
  - (+) `assumptions[1]`: "The human trial mentioned was appropriately powered for its endpoints"
    _Most substantive assumption_
  - (-) `assumptions[2]`: "The experts quoted are qualified in aging/longevity research"
    _Declared but unused in reasoning_
  - Note: 4/4 substantive assumptions
  - Note: 1 unused assumption(s)

**Uncertainty Handling:** 3.6/6
  - (+) `uncertainties[0]`: "Whether the 'enthusiasts' taking it off-label are making their own epistemic errors"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.9"
    _Stated confidence level_
  - (-) `uncertainties[0]`: "Whether the 'enthusiasts' taking it off-label are making their own epistemic errors"
    _Listed but never addressed in reasoning_
  - Note: 3 uncertainties (3 substantive)
  - Note: 1 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 6.0/6
  - (+) `alternative_hypotheses[0]`: "Could be classified as mechanism_vs_evidence if the text implied mouse longevity mechanisms apply to humans, but it does"
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 2/2 include rejection reasoning

**Self Monitoring Quality:** 0.0/8
  - (+) `self_check[3]`: "Confirmed no unsupported generalizations about human aging - correct"
    _Most substantive self-verification step_
  - (-) `self_check[0]`: "Re-read for any subtle overclaims - found none"
    _Fluff self-check_
  - Note: 4 self-check items
  - Note: Self-check quality: 0 deep, 0 arithmetic, 4 fluff

**Mechanism Quality:** 0.0/10
  - Note: Neither names concept nor explains mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.73, 243 words

**Insight Depth:** 8.0/8
  - Note: Key insights: 2 full / 2


## Failure Analysis

### Claude Opus

**CRITICAL:**
- **Wrong Answer** `[HIGH CONFIDENCE]`: Answer does not match expected 'mechanism_vs_evidence'
  - `final_answer`: "solid"
  - _Impacts: correctness_

**MAJOR:**
- **Wrong Answer** `[HIGH CONFIDENCE]`: Study classification incorrect: expected 'mechanism_vs_evidence', detected 'solid'
  - `final_answer`: "solid"
  - _Impacts: correctness_

**MODERATE:**
- **Unsupported Conclusion** `[MEDIUM CONFIDENCE]`: Final answer lacks load-bearing or supporting step grounding
  - `final_answer`: "solid"
  - _Impacts: support_strength_
- **Missed Key Insight** `[MEDIUM CONFIDENCE]`: Missed expected finding: decorative_uncertainty
  - `(task expectation)`: "Expected: decorative_uncertainty"
  - _Impacts: insight_depth_

**MINOR:**
- **Decorative Self Check** `[HEURISTIC]`: All 4 self-checks appear to be fluff — no substantive verification
  - `self_check[0]`: "Re-read for any subtle overclaims - found none"
  - _Impacts: self_monitoring_quality_

**STYLISTIC:**
- **Unused Assumption** `[HEURISTIC]`: Assumption 'The experts quoted are qualified in aging/longevity research...' is declared but not referenced in reasoning
  - `assumptions[2]`: "The experts quoted are qualified in aging/longevity research"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether the 'enthusiasts' taking it off-label are making the...' is listed but not addressed
  - `uncertainties[0]`: "Whether the 'enthusiasts' taking it off-label are making their own epistemic errors"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Opus

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/7 content words)
  - `key_claims[0]`: "Text maintains clear epistemic boundaries between species"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/8 content words)
  - `key_claims[1]`: "Acknowledges replication in mice while noting absence of human aging evidence"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/5 content words)
  - `key_claims[2]`: "Includes appropriate expert warnings about off-label use"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/5 content words)
  - `key_claims[3]`: "Does not extrapolate from mechanism to human outcomes"
- **[WARN]** `[HEURISTIC]` `unused_assumption`: Assumption 3 appears unused in reasoning or answer
  - `assumptions[2]`: "The experts quoted are qualified in aging/longevity research"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 1 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[0]`: "Whether the 'enthusiasts' taking it off-label are making their own epistemic errors"


## Agent Profiles

### Claude Opus (claude-opus-4-20250514)
**Parse OK:** True | **Latency:** 16548ms

**Final Answer:** solid

**Confidence:** 0.9

**Assumptions:**
- The text accurately represents the state of rapamycin research
- The human trial mentioned was appropriately powered for its endpoints
- The experts quoted are qualified in aging/longevity research
- The mouse studies were conducted with appropriate controls

**Reasoning Steps:**
1. Identified clear distinction between mouse and human evidence
2. Noted that mouse results are described as 'reliable' and 'replicated across multiple laboratories'
3. Observed that human evidence is limited to one trial testing specific endpoints (fat/muscle), not aging
4. Text explicitly states 'no clinical evidence yet shows rapamycin slows aging in people'
5. Appropriate caveats about off-label use and risks are included
6. No causal claims made from correlational data
7. No overclaiming from the available evidence

**Key Claims:**
- Text maintains clear epistemic boundaries between species
- Acknowledges replication in mice while noting absence of human aging evidence
- Includes appropriate expert warnings about off-label use
- Does not extrapolate from mechanism to human outcomes

**Alternative Hypotheses:**
- Could be classified as mechanism_vs_evidence if the text implied mouse longevity mechanisms apply to humans, but it doesn't
- Could be overclaim if it suggested the drug works in humans based on mouse data, but it explicitly states the opposite

**Uncertainties:**
- Whether the 'enthusiasts' taking it off-label are making their own epistemic errors
- The quality of the specific human trial mentioned
- Whether there are other human studies not mentioned

**Self-Verification:**
- Re-read for any subtle overclaims - found none
- Checked if mouse-to-human leap was made - it wasn't
- Verified that uncertainties and risks were acknowledged - they were
- Confirmed no unsupported generalizations about human aging - correct

**Dimension Scores:**
- Correctness: 0.0/30 `..........`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 4.3/6 `#######...`
- Uncertainty Handling: 3.6/6 `######....`
- Alternative Hypothesis Quality: 6.0/6 `##########`
- Self Monitoring Quality: 0.0/8 `..........`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 0.0/10 `..........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Opus** scored **36.7/100**.

**Best per dimension:**
- Correctness: Claude Opus (0.0/30)
- Support Strength: Claude Opus (0.0/8)
- Structural Reasoning: Claude Opus (4.8/8)
- Assumption Discipline: Claude Opus (4.3/6)
- Uncertainty Handling: Claude Opus (3.6/6)
- Alternative Hypothesis Quality: Claude Opus (6.0/6)
- Self Monitoring Quality: Claude Opus (0.0/8)
- Insight Depth: Claude Opus (8.0/8)
- Mechanism Quality: Claude Opus (0.0/10)
- Communication Efficiency: Claude Opus (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Opus | 16.5s | 36.7/100 | 2.2 |

Failure modes observed: decorative_self_check, decorative_uncertainty, missed_key_insight, unsupported_conclusion, unused_assumption, wrong_answer.
