# Forensic Dossier: Study Forensics: Vocational training program claims effectiveness without control group

**Run ID:** `full27_study-forensics-040_Claude_Opus_06d941`  
**Task:** study-forensics-040 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T08:27:34.348930+00:00  
**Task Family:** overclaim  
**Trap Type:** missing_counterfactual  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Opus
**Winner:** Claude Opus — **36.3/100** (margin: 0.0)
**Failure modes:** missed_key_insight, named_not_explained, unsupported_conclusion, unused_assumption, wrong_answer
**Forensic flags:** 3
**Consistency findings:** 10
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Opus | 0.0/30 | 0.0/8 | 4.8/8 | 3.4/6 | 3.9/6 | 4.5/6 | 2.8/8 | 5.3/8 | 1.5/10 | 10.0/10 | **36.3/100** |

## Study Forensics Audit

### Claude Opus

**Classification:** `correlation_vs_causation` [x] (gold: `overclaim`)
**Finding Recall:** 67%
**Matched Findings:** conclusion_exceeds_results, correlation_as_causation
**Missed Findings:** unsupported_generalization
**Extra Findings:** evidence_matches_claim, cautious_scope_control

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
  - (+) `steps[3]`: "Examined whether confounders are addressed: no discussion of economic conditions, seasonal employment, or participant se"
    _Most informative reasoning step_
  - Note: 6 reasoning steps
  - Note: Low step utility: 0/6 steps contribute

**Assumption Discipline:** 3.4/6
  - (+) `assumptions[3]`: "The measurement periods are different (pre-enrollment vs 12 months post-completion)"
    _Most substantive assumption_
  - (-) `assumptions[3]`: "The measurement periods are different (pre-enrollment vs 12 months post-completion)"
    _Declared but unused in reasoning_
  - Note: 4/4 substantive assumptions
  - Note: 1 unused assumption(s)

**Uncertainty Handling:** 3.9/6
  - (+) `uncertainties[2]`: "The exact nature of the participant population and selection criteria"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.92"
    _Stated confidence level_
  - Note: 3 uncertainties (3 substantive)
  - Note: Confidence 0.92

**Alternative Hypothesis Quality:** 4.5/6
  - (+) `alternative_hypotheses[1]`: "solid - if the text had acknowledged limitations or used more tentative language"
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 2/2 genuinely diverse alternatives

**Self Monitoring Quality:** 2.8/8
  - (+) `self_check[0]`: "Did not overflag - the causal claims are explicit ('successfully increased', 'effectiveness...as an intervention')"
    _Most substantive self-verification step_
  - (-) `self_check[1]`: "The lack of control group is a fundamental design flaw for causal inference"
    _Fluff self-check_
  - Note: 3 self-check items
  - Note: Self-check quality: 0 deep, 2 arithmetic, 1 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.72, 265 words

**Insight Depth:** 5.3/8
  - (+) `(output text)`: "controlling for other factors no control group to establish what would have"
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
- **Unused Assumption** `[HEURISTIC]`: Assumption 'The measurement periods are different (pre-enrollment vs 12 ...' is declared but not referenced in reasoning
  - `assumptions[3]`: "The measurement periods are different (pre-enrollment vs 12 months post-completion)"
  - _Impacts: assumption_discipline_


## Consistency & Grounding Audit

### Claude Opus

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/11 content words)
  - `key_claims[0]`: "Classic correlation-causation error: attributing employment gains solely to the program without cont"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/6 content words)
  - `key_claims[1]`: "No control group to establish what would have happened without the program"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/9 content words)
  - `key_claims[2]`: "Economic conditions, seasonal variations, and participant motivation could all contribute to employm"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/13 content words)
  - `key_claims[3]`: "The 18+ month timeframe (6-month program plus 12 months after) allows many external factors to influ"
- **[WARN]** `[HEURISTIC]` `claim_step_alignment`: Key claim 1 not well supported in reasoning steps (2/11 content words found)
  - `key_claims[0]`: "Classic correlation-causation error: attributing employment gains solely to the program without cont"
- **[WARN]** `[HEURISTIC]` `claim_step_alignment`: Key claim 4 not well supported in reasoning steps (1/13 content words found)
  - `key_claims[3]`: "The 18+ month timeframe (6-month program plus 12 months after) allows many external factors to influ"
- **[WARN]** `[HEURISTIC]` `unused_assumption`: Assumption 4 appears unused in reasoning or answer
  - `assumptions[3]`: "The measurement periods are different (pre-enrollment vs 12 months post-completion)"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "overclaim - the conclusion to expand the program might exceed the evidence"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 2 is stated without rejection reasoning
  - `alternative_hypotheses[1]`: "solid - if the text had acknowledged limitations or used more tentative language"
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "correlation_vs_causation"


## Agent Profiles

### Claude Opus (claude-opus-4-20250514)
**Parse OK:** True | **Latency:** 16149ms

**Final Answer:** correlation_vs_causation

**Confidence:** 0.92

**Assumptions:**
- The text describes a before-after comparison without a control group
- The agency is making causal claims about the program's effectiveness
- No other factors that could influence employment are mentioned or controlled for
- The measurement periods are different (pre-enrollment vs 12 months post-completion)

**Reasoning Steps:**
1. Identified the study design: before-after comparison of employment rates (34% to 61%)
2. Noted the causal claim: 'the program successfully increased employment by approximately 27 percentage points'
3. Checked for control group: none mentioned
4. Examined whether confounders are addressed: no discussion of economic conditions, seasonal employment, or participant self-selection
5. Evaluated the conclusion: agency recommends expansion based on assumed causal effect
6. The director's statement about 'effectiveness of skills-based training as an intervention' implies causation

**Key Claims:**
- Classic correlation-causation error: attributing employment gains solely to the program without controlling for other factors
- No control group to establish what would have happened without the program
- Economic conditions, seasonal variations, and participant motivation could all contribute to employment changes
- The 18+ month timeframe (6-month program plus 12 months after) allows many external factors to influence outcomes

**Alternative Hypotheses:**
- overclaim - the conclusion to expand the program might exceed the evidence
- solid - if the text had acknowledged limitations or used more tentative language

**Uncertainties:**
- Whether the agency collected but didn't report data on confounders
- Whether there were comparison groups not mentioned in this summary
- The exact nature of the participant population and selection criteria

**Self-Verification:**
- Did not overflag - the causal claims are explicit ('successfully increased', 'effectiveness...as an intervention')
- The lack of control group is a fundamental design flaw for causal inference
- The recommendation to expand based on this evidence confirms the correlation-causation issue

**Dimension Scores:**
- Correctness: 0.0/30 `..........`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 3.4/6 `#####.....`
- Uncertainty Handling: 3.9/6 `######....`
- Alternative Hypothesis Quality: 4.5/6 `#######...`
- Self Monitoring Quality: 2.8/8 `###.......`
- Insight Depth: 5.3/8 `######....`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Opus** scored **36.3/100**.

**Best per dimension:**
- Correctness: Claude Opus (0.0/30)
- Support Strength: Claude Opus (0.0/8)
- Structural Reasoning: Claude Opus (4.8/8)
- Assumption Discipline: Claude Opus (3.4/6)
- Uncertainty Handling: Claude Opus (3.9/6)
- Alternative Hypothesis Quality: Claude Opus (4.5/6)
- Self Monitoring Quality: Claude Opus (2.8/8)
- Insight Depth: Claude Opus (5.3/8)
- Mechanism Quality: Claude Opus (1.5/10)
- Communication Efficiency: Claude Opus (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Opus | 16.1s | 36.3/100 | 2.2 |

Failure modes observed: missed_key_insight, named_not_explained, unsupported_conclusion, unused_assumption, wrong_answer.
