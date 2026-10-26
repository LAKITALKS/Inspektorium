# Forensic Dossier: Study Forensics: Vocational training program claims effectiveness without control group

**Run ID:** `full27_study-forensics-040_Claude_Opus_50a306`  
**Task:** study-forensics-040 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T17:12:49.807952+00:00  
**Task Family:** overclaim  
**Trap Type:** missing_counterfactual  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Opus
**Winner:** Claude Opus — **35.7/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, missed_key_insight, named_not_explained, unsupported_conclusion, unused_assumption, wrong_answer
**Forensic flags:** 3
**Consistency findings:** 7
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Opus | 0.0/30 | 0.0/8 | 4.8/8 | 4.3/6 | 3.6/6 | 4.5/6 | 1.6/8 | 5.3/8 | 1.5/10 | 10.0/10 | **35.7/100** |

## Study Forensics Audit

### Claude Opus

**Classification:** `correlation_vs_causation` [x] (gold: `overclaim`)
**Finding Recall:** 67%
**Matched Findings:** conclusion_exceeds_results, correlation_as_causation
**Missed Findings:** unsupported_generalization
**Extra Findings:** cautious_scope_control

## Reasoning Integrity Audit

### Claude Opus
**Classification:** Correct and well-supported
**Load-bearing steps:** 0 / 8

## Mechanism Analysis

### Claude Opus
| Aspect | Status |
|--------|--------|
| Concept named | :white_check_mark: effect |
| Mechanism described | :x: (0 sentence(s)) |
| Grounded to case | :x: (0 sentence(s)) |

**Missing:** mechanism not described, mechanism not grounded to case data

## Grounding Audit

### Claude Opus
Conclusion claims: 1
- Direct support: 0
- Indirect support: 0
- Unsupported: 1
- Contradicted: 0

**Unsupported claims:**
- "correlation_vs_causation"


## Forensic Flags

### Claude Opus

- **[MAJOR]** `well_reasoned_wrong`: Wrong answer but structured reasoning — may have a subtle logic error
  - `final_answer`: "correlation_vs_causation"
- **[MODERATE]** `unsupported_conclusion_claims`: 1/1 conclusion claims lack step support
  - `final_answer`: "correlation_vs_causation"
- **[MODERATE]** `ungrounded_mechanism`: Mechanism named/described but not connected to case-specific data
  - `(mechanism analysis)`: "effect"


## Evidence Map

### Claude Opus

**Correctness:** 0.0/30
  - (+) `final_answer`: "correlation_vs_causation"
    _Agent's answer for correctness check_
  - Note: No match (got: correlation_vs_causation)

**Support Strength:** 0.0/8
  - (-) `final_answer`: "correlation_vs_causation"
    _Conclusion not supported by steps_
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 8
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[3]`: "No control for external factors like economic recovery, seasonal employment, or participant self-selection"
    _Most informative reasoning step_
  - Note: 8 reasoning steps
  - Note: Low step utility: 0/8 steps contribute

**Assumption Discipline:** 4.3/6
  - (+) `assumptions[1]`: "The 34% and 61% figures represent the same cohort of participants"
    _Most substantive assumption_
  - (-) `assumptions[1]`: "The 34% and 61% figures represent the same cohort of participants"
    _Declared but unused in reasoning_
  - Note: 4/4 substantive assumptions
  - Note: 1 unused assumption(s)

**Uncertainty Handling:** 3.6/6
  - (+) `uncertainties[0]`: "Whether any controls or adjustments were made but not mentioned in the summary"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.9"
    _Stated confidence level_
  - (-) `uncertainties[1]`: "The exact nature of the 'evaluation' methodology"
    _Listed but never addressed in reasoning_
  - Note: 2 uncertainties (2 substantive)
  - Note: 1 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 4.5/6
  - (+) `alternative_hypotheses[1]`: "Could be overclaim if the expansion recommendation exceeded the geographic scope of evidence"
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 2/2 genuinely diverse alternatives

**Self Monitoring Quality:** 1.6/8
  - (+) `self_check[1]`: "The issue is causal attribution from observational data, not an evidence tier mismatch"
    _Most substantive self-verification step_
  - (-) `self_check[0]`: "Verified this is correlation vs causation, not mechanism vs evidence"
    _Fluff self-check_
  - Note: 3 self-check items
  - Note: Self-check quality: 0 deep, 1 arithmetic, 2 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.72, 233 words

**Insight Depth:** 5.3/8
  - (+) `(output text)`: "fter observational study with no control group the 34% and 61% figures repre"
    _Insight 'no control group' matched (exact)_
  - (?) `(not found)`: "Missing: secular trends"
    _Insight 'secular trends' not found_
  - Note: Key insights: 2 full / 3


## Failure Analysis

### Claude Opus

**CRITICAL:**
- **Wrong Answer** `[HIGH CONFIDENCE]`: Answer does not match expected 'overclaim'
  - `final_answer`: "correlation_vs_causation"
  - _Impacts: correctness_

**MAJOR:**
- **Wrong Answer** `[HIGH CONFIDENCE]`: Study classification incorrect: expected 'overclaim', detected 'correlation_vs_causation'
  - `final_answer`: "correlation_vs_causation"
  - _Impacts: correctness_
- **Missed Key Insight** `[MEDIUM CONFIDENCE]`: Missed expected finding: unsupported_generalization
  - `(task expectation)`: "Expected: unsupported_generalization"
  - _Impacts: insight_depth_

**MODERATE:**
- **Unsupported Conclusion** `[MEDIUM CONFIDENCE]`: Final answer lacks load-bearing or supporting step grounding
  - `final_answer`: "correlation_vs_causation"
  - _Impacts: support_strength_
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Names the phenomenon but does not explain the causal mechanism
  - `final_answer`: "correlation_vs_causation"
  - _Impacts: mechanism_quality_
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Named concept(s) ['effect'] but mechanism not described
  - _Impacts: mechanism_quality, insight_depth_

**STYLISTIC:**
- **Unused Assumption** `[HEURISTIC]`: Assumption 'The 34% and 61% figures represent the same cohort of partici...' is declared but not referenced in reasoning
  - `assumptions[1]`: "The 34% and 61% figures represent the same cohort of participants"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'The exact nature of the 'evaluation' methodology...' is listed but not addressed
  - `uncertainties[1]`: "The exact nature of the 'evaluation' methodology"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Opus

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/10 content words)
  - `key_claims[0]`: "Classic before-after design without control group being used to make causal claims"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/6 content words)
  - `key_claims[1]`: "The entire employment rate change is attributed to the program"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/8 content words)
  - `key_claims[2]`: "No acknowledgment of potential confounders like economic conditions or selection effects"
- **[WARN]** `[HEURISTIC]` `unused_assumption`: Assumption 2 appears unused in reasoning or answer
  - `assumptions[1]`: "The 34% and 61% figures represent the same cohort of participants"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 2 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[1]`: "The exact nature of the 'evaluation' methodology"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "Could be solid if the text had acknowledged limitations and avoided causal language"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 2 is stated without rejection reasoning
  - `alternative_hypotheses[1]`: "Could be overclaim if the expansion recommendation exceeded the geographic scope of evidence"


## Agent Profiles

### Claude Opus (claude-opus-4-20250514)
**Parse OK:** True | **Latency:** 15536ms

**Final Answer:** correlation_vs_causation

**Confidence:** 0.9

**Assumptions:**
- This is a before-after observational study with no control group
- The 34% and 61% figures represent the same cohort of participants
- The evaluation measured employment status at two time points
- No randomization or comparison group is mentioned

**Reasoning Steps:**
1. Identified study design: pre-post comparison without control group
2. Noted the claim: program 'successfully increased employment by 27 percentage points'
3. This is a causal claim ('increased') based on temporal association alone
4. No control for external factors like economic recovery, seasonal employment, or participant self-selection
5. The conclusion attributes the entire 27pp change to the program intervention
6. Evidence tier is limited_human (observational study, no controls)
7. Conclusion tier matches evidence tier (discussing same population)
8. No bridge step issue - they're concluding about the population they studied

**Key Claims:**
- Classic before-after design without control group being used to make causal claims
- The entire employment rate change is attributed to the program
- No acknowledgment of potential confounders like economic conditions or selection effects

**Alternative Hypotheses:**
- Could be solid if the text had acknowledged limitations and avoided causal language
- Could be overclaim if the expansion recommendation exceeded the geographic scope of evidence

**Uncertainties:**
- Whether any controls or adjustments were made but not mentioned in the summary
- The exact nature of the 'evaluation' methodology

**Self-Verification:**
- Verified this is correlation vs causation, not mechanism vs evidence
- The issue is causal attribution from observational data, not an evidence tier mismatch
- The recommendation to expand stays within reasonable bounds of the evidence

**Dimension Scores:**
- Correctness: 0.0/30 `..........`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 4.3/6 `#######...`
- Uncertainty Handling: 3.6/6 `######....`
- Alternative Hypothesis Quality: 4.5/6 `#######...`
- Self Monitoring Quality: 1.6/8 `##........`
- Insight Depth: 5.3/8 `######....`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Opus** scored **35.7/100**.

**Best per dimension:**
- Correctness: Claude Opus (0.0/30)
- Support Strength: Claude Opus (0.0/8)
- Structural Reasoning: Claude Opus (4.8/8)
- Assumption Discipline: Claude Opus (4.3/6)
- Uncertainty Handling: Claude Opus (3.6/6)
- Alternative Hypothesis Quality: Claude Opus (4.5/6)
- Self Monitoring Quality: Claude Opus (1.6/8)
- Insight Depth: Claude Opus (5.3/8)
- Mechanism Quality: Claude Opus (1.5/10)
- Communication Efficiency: Claude Opus (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Opus | 15.5s | 35.7/100 | 2.3 |

Failure modes observed: decorative_uncertainty, missed_key_insight, named_not_explained, unsupported_conclusion, unused_assumption, wrong_answer.
