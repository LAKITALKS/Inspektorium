# Forensic Dossier: Study Forensics: Vocational training program claims effectiveness without control group

**Run ID:** `ocfix_study-forensics-040_Claude_Opus_14464a`  
**Task:** study-forensics-040 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T17:29:25.311176+00:00  
**Task Family:** overclaim  
**Trap Type:** missing_counterfactual  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Opus
**Winner:** Claude Opus — **39.7/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, missed_key_insight, named_not_explained, unsupported_conclusion, wrong_answer
**Forensic flags:** 3
**Consistency findings:** 6
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Opus | 0.0/30 | 0.0/8 | 4.8/8 | 4.8/6 | 3.3/6 | 6.0/6 | 4.0/8 | 5.3/8 | 1.5/10 | 10.0/10 | **39.7/100** |

## Study Forensics Audit

### Claude Opus

**Classification:** `correlation_vs_causation` [x] (gold: `overclaim`)
**Finding Recall:** 67%
**Matched Findings:** conclusion_exceeds_results, correlation_as_causation
**Missed Findings:** unsupported_generalization

## Reasoning Integrity Audit

### Claude Opus
**Classification:** Correct and well-supported
**Load-bearing steps:** 0 / 6

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
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 6
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[0]`: "Identified study design: pre-post comparison without control group"
    _Most informative reasoning step_
  - Note: 6 reasoning steps
  - Note: Low step utility: 0/6 steps contribute

**Assumption Discipline:** 4.8/6
  - (+) `assumptions[3]`: "The agency is making policy recommendations based on this data"
    _Most substantive assumption_
  - Note: 4/4 substantive assumptions

**Uncertainty Handling:** 3.3/6
  - (+) `uncertainties[0]`: "Whether the agency collected any data on non-participants as informal control"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.9"
    _Stated confidence level_
  - (-) `uncertainties[0]`: "Whether the agency collected any data on non-participants as informal control"
    _Listed but never addressed in reasoning_
  - (-) `uncertainties[1]`: "Whether other analyses were performed but not mentioned"
    _Listed but never addressed in reasoning_
  - Note: 3 uncertainties (3 substantive)
  - Note: 2 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 6.0/6
  - (+) `alternative_hypotheses[0]`: "overclaim - considered because of strong effectiveness claims, but the core issue is causal inference from non-causal de"
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 2/2 include rejection reasoning

**Self Monitoring Quality:** 4.0/8
  - (+) `self_check[2]`: "Not overclaim because the numbers themselves appear accurate - it's the causal interpretation that's problematic"
    _Most substantive self-verification step_
  - Note: 3 self-check items
  - Note: Self-check quality: 0 deep, 3 arithmetic, 0 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.76, 243 words

**Insight Depth:** 5.3/8
  - (+) `(output text)`: "vational with pre-post design no control group is mentioned the 27 percentag"
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
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether the agency collected any data on non-participants as...' is listed but not addressed
  - `uncertainties[0]`: "Whether the agency collected any data on non-participants as informal control"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether other analyses were performed but not mentioned...' is listed but not addressed
  - `uncertainties[1]`: "Whether other analyses were performed but not mentioned"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Opus

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/11 content words)
  - `key_claims[0]`: "The study attributes the 27 percentage point employment increase to the program without controlling "
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/9 content words)
  - `key_claims[1]`: "Economic recovery, seasonal employment patterns, or participant self-selection could explain the res"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/7 content words)
  - `key_claims[2]`: "The conclusion of program 'effectiveness' requires comparison to a control group"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/6 content words)
  - `key_claims[3]`: "Policy expansion is recommended based on correlational evidence"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 2 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[1]`: "Whether other analyses were performed but not mentioned"
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "correlation_vs_causation"


## Agent Profiles

### Claude Opus (claude-opus-4-20250514)
**Parse OK:** True | **Latency:** 18227ms

**Final Answer:** correlation_vs_causation

**Confidence:** 0.9

**Assumptions:**
- The study is observational with pre-post design
- No control group is mentioned
- The 27 percentage point increase is calculated as 61% - 34%
- The agency is making policy recommendations based on this data

**Reasoning Steps:**
1. Identified study design: pre-post comparison without control group
2. Noted the conclusion: program 'successfully increased employment' - causal language
3. Observed policy recommendation: expanding to additional districts
4. Checked for confounders: no mention of economic conditions, seasonal employment, or other factors
5. The director's statement about 'effectiveness' implies causation from correlational data
6. Evidence tier is limited_human (observational study), conclusion tier is human_policy (expansion recommendation)

**Key Claims:**
- The study attributes the 27 percentage point employment increase to the program without controlling for external factors
- Economic recovery, seasonal employment patterns, or participant self-selection could explain the results
- The conclusion of program 'effectiveness' requires comparison to a control group
- Policy expansion is recommended based on correlational evidence

**Alternative Hypotheses:**
- overclaim - considered because of strong effectiveness claims, but the core issue is causal inference from non-causal design
- solid - rejected because the study lacks a control group yet makes causal claims

**Uncertainties:**
- Whether the agency collected any data on non-participants as informal control
- Whether other analyses were performed but not mentioned
- The specific nature of the vocational training program

**Self-Verification:**
- Confirmed this is correlation vs causation, not mechanism vs evidence - the study is human-level
- The causal claim ('successfully increased') from pre-post data is the central issue
- Not overclaim because the numbers themselves appear accurate - it's the causal interpretation that's problematic

**Dimension Scores:**
- Correctness: 0.0/30 `..........`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 4.8/6 `########..`
- Uncertainty Handling: 3.3/6 `#####.....`
- Alternative Hypothesis Quality: 6.0/6 `##########`
- Self Monitoring Quality: 4.0/8 `#####.....`
- Insight Depth: 5.3/8 `######....`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Opus** scored **39.7/100**.

**Best per dimension:**
- Correctness: Claude Opus (0.0/30)
- Support Strength: Claude Opus (0.0/8)
- Structural Reasoning: Claude Opus (4.8/8)
- Assumption Discipline: Claude Opus (4.8/6)
- Uncertainty Handling: Claude Opus (3.3/6)
- Alternative Hypothesis Quality: Claude Opus (6.0/6)
- Self Monitoring Quality: Claude Opus (4.0/8)
- Insight Depth: Claude Opus (5.3/8)
- Mechanism Quality: Claude Opus (1.5/10)
- Communication Efficiency: Claude Opus (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Opus | 18.2s | 39.7/100 | 2.2 |

Failure modes observed: decorative_uncertainty, missed_key_insight, named_not_explained, unsupported_conclusion, wrong_answer.
