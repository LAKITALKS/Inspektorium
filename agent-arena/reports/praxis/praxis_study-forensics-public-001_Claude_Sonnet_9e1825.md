# Forensic Dossier: Study Forensics: Vigorous Exercise and 8 Major Diseases — Correlation Sold as Intervention

**Run ID:** `praxis_study-forensics-public-001_Claude_Sonnet_9e1825`  
**Task:** study-forensics-public-001 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-07T07:58:34.110217+00:00  
**Task Family:** correlation_vs_causation  
**Trap Type:** causal_framing_of_observational_data  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Sonnet
**Winner:** Claude Sonnet — **38.3/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, named_not_explained, unsupported_conclusion, unused_assumption, wrong_answer
**Forensic flags:** 3
**Consistency findings:** 9
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Sonnet | 0.0/30 | 0.0/8 | 4.8/8 | 3.8/6 | 3.0/6 | 6.0/6 | 1.2/8 | 8.0/8 | 1.5/10 | 10.0/10 | **38.3/100** |

## Study Forensics Audit

### Claude Sonnet

**Classification:** `solid` [x] (gold: `correlation_vs_causation`)
**Finding Recall:** 100%
**Matched Findings:** correlation_as_causation, unsupported_generalization
**Extra Findings:** cautious_scope_control, none_or_minor, conclusion_exceeds_results

## Reasoning Integrity Audit

### Claude Sonnet
**Classification:** Correct and well-supported
**Load-bearing steps:** 0 / 6

## Mechanism Analysis

### Claude Sonnet
| Aspect | Status |
|--------|--------|
| Concept named | :white_check_mark: effect |
| Mechanism described | :x: (0 sentence(s)) |
| Grounded to case | :x: (0 sentence(s)) |

**Missing:** mechanism not described, mechanism not grounded to case data

## Grounding Audit

### Claude Sonnet
Conclusion claims: 1
- Direct support: 0
- Indirect support: 0
- Unsupported: 1
- Contradicted: 0

**Unsupported claims:**
- "solid"


## Forensic Flags

### Claude Sonnet

- **[MAJOR]** `well_reasoned_wrong`: Wrong answer but structured reasoning — may have a subtle logic error
  - `final_answer`: "solid"
- **[MODERATE]** `unsupported_conclusion_claims`: 1/1 conclusion claims lack step support
  - `final_answer`: "solid"
- **[MODERATE]** `ungrounded_mechanism`: Mechanism named/described but not connected to case-specific data
  - `(mechanism analysis)`: "effect"


## Evidence Map

### Claude Sonnet

**Correctness:** 0.0/30
  - (+) `final_answer`: "solid"
    _Agent's answer for correctness check_
  - Note: No match (got: solid)

**Support Strength:** 0.0/8
  - (-) `final_answer`: "solid"
    _Conclusion not supported by steps_
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 6
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[0]`: "Examined claims for causal language - authors and media appropriately use associational language ('associated with', 'li"
    _Most informative reasoning step_
  - Note: 6 reasoning steps
  - Note: Low step utility: 0/6 steps contribute

**Assumption Discipline:** 3.8/6
  - (+) `assumptions[2]`: "The UK Biobank represents a reasonably large and well-characterized cohort"
    _Most substantive assumption_
  - (-) `assumptions[1]`: "The 7-year follow-up period is sufficient for chronic disease outcomes"
    _Declared but unused in reasoning_
  - (-) `assumptions[2]`: "The UK Biobank represents a reasonably large and well-characterized cohort"
    _Declared but unused in reasoning_
  - Note: 4/4 substantive assumptions
  - Note: 2 unused assumption(s)

**Uncertainty Handling:** 3.0/6
  - (+) `uncertainties[1]`: "How representative the 7-day accelerometer period is of long-term activity patterns"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.88"
    _Stated confidence level_
  - (-) `uncertainties[0]`: "Whether all relevant confounders were adequately controlled"
    _Listed but never addressed in reasoning_
  - (-) `uncertainties[1]`: "How representative the 7-day accelerometer period is of long-term activity patterns"
    _Listed but never addressed in reasoning_
  - Note: 3 uncertainties (3 substantive)
  - Note: 3 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 6.0/6
  - (+) `alternative_hypotheses[2]`: "Could be mechanism gap, but no mechanistic claims are being inappropriately applied"
    _Most substantive alternative hypothesis_
  - Note: 3 alternative hypotheses considered
  - Note: 3/3 include rejection reasoning

**Self Monitoring Quality:** 1.2/8
  - (+) `self_check[3]`: "Ensured I'm not fabricating problems where none exist - this appears to be responsible reporting of observational resear"
    _Most substantive self-verification step_
  - (-) `self_check[0]`: "Verified that no causal language is used inappropriately"
    _Fluff self-check_
  - Note: 4 self-check items
  - Note: Self-check quality: 0 deep, 1 arithmetic, 3 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.79, 258 words

**Insight Depth:** 4.0/8
  - (?) `(not found)`: "Missing: healthy user bias"
    _Insight 'healthy user bias' not found_
  - Note: Key insights: 2 full / 4


## Failure Analysis

### Claude Sonnet

**CRITICAL:**
- **Wrong Answer** `[HIGH CONFIDENCE]`: Answer does not match expected 'correlation_vs_causation'
  - `final_answer`: "solid"
  - _Impacts: correctness_

**MAJOR:**
- **Wrong Answer** `[HIGH CONFIDENCE]`: Study classification incorrect: expected 'correlation_vs_causation', detected 'solid'
  - `final_answer`: "solid"
  - _Impacts: correctness_

**MODERATE:**
- **Unsupported Conclusion** `[MEDIUM CONFIDENCE]`: Final answer lacks load-bearing or supporting step grounding
  - `final_answer`: "solid"
  - _Impacts: support_strength_
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Names the phenomenon but does not explain the causal mechanism
  - `final_answer`: "solid"
  - _Impacts: mechanism_quality_
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Named concept(s) ['effect'] but mechanism not described
  - _Impacts: mechanism_quality, insight_depth_

**STYLISTIC:**
- **Unused Assumption** `[HEURISTIC]`: Assumption 'The 7-year follow-up period is sufficient for chronic diseas...' is declared but not referenced in reasoning
  - `assumptions[1]`: "The 7-year follow-up period is sufficient for chronic disease outcomes"
  - _Impacts: assumption_discipline_
- **Unused Assumption** `[HEURISTIC]`: Assumption 'The UK Biobank represents a reasonably large and well-charac...' is declared but not referenced in reasoning
  - `assumptions[2]`: "The UK Biobank represents a reasonably large and well-characterized cohort"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether all relevant confounders were adequately controlled...' is listed but not addressed
  - `uncertainties[0]`: "Whether all relevant confounders were adequately controlled"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'How representative the 7-day accelerometer period is of long...' is listed but not addressed
  - `uncertainties[1]`: "How representative the 7-day accelerometer period is of long-term activity patterns"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether the UK Biobank population limits generalizability si...' is listed but not addressed
  - `uncertainties[2]`: "Whether the UK Biobank population limits generalizability significantly"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Sonnet

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/8 content words)
  - `key_claims[0]`: "Study appropriately presents observational associations without claiming causation"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/10 content words)
  - `key_claims[1]`: "Media coverage uses appropriate hedging language ('may', 'could', 'associated with')"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/8 content words)
  - `key_claims[2]`: "Authors clearly acknowledge study limitations including observational design"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/6 content words)
  - `key_claims[3]`: "Effect sizes are presented as associations, not causal effects"
- **[WARN]** `[HEURISTIC]` `unused_assumption`: Assumption 2 appears unused in reasoning or answer
  - `assumptions[1]`: "The 7-year follow-up period is sufficient for chronic disease outcomes"
- **[WARN]** `[HEURISTIC]` `unused_assumption`: Assumption 3 appears unused in reasoning or answer
  - `assumptions[2]`: "The UK Biobank represents a reasonably large and well-characterized cohort"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 1 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[0]`: "Whether all relevant confounders were adequately controlled"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 2 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[1]`: "How representative the 7-day accelerometer period is of long-term activity patterns"
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "solid"


## Agent Profiles

### Claude Sonnet (claude-sonnet-4-20250514)
**Parse OK:** True | **Latency:** 12675ms

**Final Answer:** solid

**Confidence:** 0.88

**Assumptions:**
- The study used appropriate statistical methods for observational data
- The 7-year follow-up period is sufficient for chronic disease outcomes
- The UK Biobank represents a reasonably large and well-characterized cohort
- The authors properly adjusted for major confounding variables

**Reasoning Steps:**
1. Examined claims for causal language - authors and media appropriately use associational language ('associated with', 'linked to')
2. Checked for mechanism overreach - no inappropriate extrapolation from animal studies or different contexts
3. Evaluated uncertainty handling - study clearly states observational limitations and cannot prove causation
4. Assessed generalizability claims - media coverage stays within bounds of the evidence
5. Reviewed confounding discussion - authors acknowledge residual confounding as a limitation
6. Analyzed effect size reporting - percentages are clearly presented as relative risk reductions from observational data

**Key Claims:**
- Study appropriately presents observational associations without claiming causation
- Media coverage uses appropriate hedging language ('may', 'could', 'associated with')
- Authors clearly acknowledge study limitations including observational design
- Effect sizes are presented as associations, not causal effects

**Alternative Hypotheses:**
- Could be overclaim due to observational nature, but limitations are clearly stated
- Could be correlation vs causation issue, but no direct causal claims are made
- Could be mechanism gap, but no mechanistic claims are being inappropriately applied

**Uncertainties:**
- Whether all relevant confounders were adequately controlled
- How representative the 7-day accelerometer period is of long-term activity patterns
- Whether the UK Biobank population limits generalizability significantly

**Self-Verification:**
- Verified that no causal language is used inappropriately
- Confirmed that limitations are clearly stated
- Checked that media coverage doesn't overstate findings
- Ensured I'm not fabricating problems where none exist - this appears to be responsible reporting of observational research

**Dimension Scores:**
- Correctness: 0.0/30 `..........`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 3.8/6 `######....`
- Uncertainty Handling: 3.0/6 `####......`
- Alternative Hypothesis Quality: 6.0/6 `##########`
- Self Monitoring Quality: 1.2/8 `#.........`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Sonnet** scored **38.3/100**.

**Best per dimension:**
- Correctness: Claude Sonnet (0.0/30)
- Support Strength: Claude Sonnet (0.0/8)
- Structural Reasoning: Claude Sonnet (4.8/8)
- Assumption Discipline: Claude Sonnet (3.8/6)
- Uncertainty Handling: Claude Sonnet (3.0/6)
- Alternative Hypothesis Quality: Claude Sonnet (6.0/6)
- Self Monitoring Quality: Claude Sonnet (1.2/8)
- Insight Depth: Claude Sonnet (8.0/8)
- Mechanism Quality: Claude Sonnet (1.5/10)
- Communication Efficiency: Claude Sonnet (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Sonnet | 12.7s | 38.3/100 | 3.0 |

Failure modes observed: decorative_uncertainty, named_not_explained, unsupported_conclusion, unused_assumption, wrong_answer.
