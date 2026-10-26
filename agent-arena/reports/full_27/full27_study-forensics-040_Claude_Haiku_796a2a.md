# Forensic Dossier: Study Forensics: Vocational training program claims effectiveness without control group

**Run ID:** `full27_study-forensics-040_Claude_Haiku_796a2a`  
**Task:** study-forensics-040 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T08:27:18.178942+00:00  
**Task Family:** overclaim  
**Trap Type:** missing_counterfactual  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **70.4/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, named_not_explained, unsupported_conclusion, unsupported_intermediate_step, unused_assumption
**Forensic flags:** 4
**Consistency findings:** 10
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 30.0/30 | 0.0/8 | 4.8/8 | 3.7/6 | 3.3/6 | 5.0/6 | 5.6/8 | 8.0/8 | 1.5/10 | 8.5/10 | **70.4/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `overclaim` [+] (gold: `overclaim`)
**Finding Recall:** 100%
**Matched Findings:** unsupported_generalization, conclusion_exceeds_results, correlation_as_causation
**Extra Findings:** evidence_matches_claim, cautious_scope_control, none_or_minor, mechanism_not_demonstrated

## Reasoning Integrity Audit

### Claude Haiku
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 8

## Mechanism Analysis

### Claude Haiku
| Aspect | Status |
|--------|--------|
| Concept named | :white_check_mark: bias, effect |
| Mechanism described | :x: (0 sentence(s)) |
| Grounded to case | :x: (0 sentence(s)) |

**Missing:** mechanism not described, mechanism not grounded to case data

## Grounding Audit

### Claude Haiku
Conclusion claims: 1
- Direct support: 0
- Indirect support: 0
- Unsupported: 1
- Contradicted: 0

**Unsupported claims:**
- "overclaim"


## Forensic Flags

### Claude Haiku

- **[MODERATE]** `weak_mechanism`: Correct answer but weak mechanism explanation — answer may not generalize
  - `final_answer`: "overclaim"
- **[MAJOR]** `unsupported_leap`: Correct answer with weak support chain — final answer may be an unsupported leap
- **[MODERATE]** `unsupported_conclusion_claims`: 1/1 conclusion claims lack step support
  - `final_answer`: "overclaim"
- **[MODERATE]** `ungrounded_mechanism`: Mechanism named/described but not connected to case-specific data
  - `(mechanism analysis)`: "bias, effect"


## Evidence Map

### Claude Haiku

**Correctness:** 30.0/30
  - (+) `final_answer`: "overclaim"
    _Agent's answer for correctness check_
  - Note: Exact match

**Support Strength:** 0.0/8
  - (-) `final_answer`: "overclaim"
    _Conclusion not supported by steps_
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 8
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[7]`: "Checked for alternative explanations: general economic improvement, self-selection of motivated individuals, regression "
    _Most informative reasoning step_
  - Note: 8 reasoning steps
  - Note: Low step utility: 0/8 steps contribute

**Assumption Discipline:** 3.7/6
  - (+) `assumptions[1]`: "The 12-month follow-up period includes 6 months of program participation plus 6 months post-completion"
    _Most substantive assumption_
  - (-) `assumptions[2]`: "No information is provided about selection bias, attrition, or confounding variables"
    _Declared but unused in reasoning_
  - Note: 6/6 substantive assumptions
  - Note: Many assumptions (6)

**Uncertainty Handling:** 3.3/6
  - (+) `uncertainties[3]`: "Whether the 34% baseline employment rate was measured at the same point in the employment cycle as the 61% follow-up"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.88"
    _Stated confidence level_
  - (-) `uncertainties[2]`: "Whether attrition analysis was conducted (did lower-performing participants drop out?)"
    _Listed but never addressed in reasoning_
  - (-) `uncertainties[4]`: "Whether participants were self-selected volunteers (high motivation) vs. randomly assigned"
    _Listed but never addressed in reasoning_
  - Note: 5 uncertainties (5 substantive)
  - Note: 2 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 5.0/6
  - (+) `alternative_hypotheses[0]`: "correlation_vs_causation: The employment gain may reflect general labor market improvement, seasonal hiring, or self-sel"
    _Most substantive alternative hypothesis_
  - Note: 3 alternative hypotheses considered
  - Note: 1/3 include rejection reasoning

**Self Monitoring Quality:** 5.6/8
  - (+) `self_check[4]`: "Could this be a solid study? Only if the summary omits critical methodological details (e.g., a control group), but I mu"
    _Most substantive self-verification step_
  - Note: 5 self-check items
  - Note: Self-check quality: 0 deep, 5 arithmetic, 0 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 8.5/10
  - Note: Signal density: 0.72, 523 words

**Insight Depth:** 8.0/8
  - (+) `(output text)`: "fects, participant motivation/selection bias evaluated the causal language"
    _Insight 'selection bias' matched (exact)_
  - Note: Key insights: 3 full / 3


## Failure Analysis

### Claude Haiku

**MODERATE:**
- **Unsupported Conclusion** `[MEDIUM CONFIDENCE]`: Final answer lacks load-bearing or supporting step grounding
  - `final_answer`: "overclaim"
  - _Impacts: support_strength_
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Names the phenomenon but does not explain the causal mechanism
  - `final_answer`: "overclaim"
  - _Impacts: mechanism_quality_
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Named concept(s) ['bias', 'effect'] but mechanism not described
  - _Impacts: mechanism_quality, insight_depth_
- **Unsupported Intermediate Step** `[MEDIUM CONFIDENCE]`: No reasoning step is load-bearing — final answer lacks traceable derivation
  - `final_answer`: "overclaim"
  - _Impacts: support_strength, structural_reasoning_

**STYLISTIC:**
- **Unused Assumption** `[HEURISTIC]`: Assumption 'No information is provided about selection bias, attrition, ...' is declared but not referenced in reasoning
  - `assumptions[2]`: "No information is provided about selection bias, attrition, or confounding variables"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether attrition analysis was conducted (did lower-performi...' is listed but not addressed
  - `uncertainties[2]`: "Whether attrition analysis was conducted (did lower-performing participants drop out?)"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether participants were self-selected volunteers (high mot...' is listed but not addressed
  - `uncertainties[4]`: "Whether participants were self-selected volunteers (high motivation) vs. randomly assigned"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (1/17 content words)
  - `key_claims[0]`: "The text makes a causal claim ('successfully increased employment') based on pre-post data without a"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/13 content words)
  - `key_claims[1]`: "The 27 percentage point increase is substantial, but without knowing the counterfactual (what would "
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (1/16 content words)
  - `key_claims[2]`: "The program director's conclusion that 'results confirmed the effectiveness of skills-based training"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/13 content words)
  - `key_claims[3]`: "No mention of confounders (economic conditions, labor market trends, participant selection effects) "
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 5 has low overlap with final answer (0/8 content words)
  - `key_claims[4]`: "The recommendation to expand the program is premature without evidence of causal impact"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 3 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[2]`: "Whether attrition analysis was conducted (did lower-performing participants drop out?)"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 5 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[4]`: "Whether participants were self-selected volunteers (high motivation) vs. randomly assigned"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "correlation_vs_causation: The employment gain may reflect general labor market improvement, seasonal"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 2 is stated without rejection reasoning
  - `alternative_hypotheses[1]`: "confounders: Unmeasured variables (economic growth, participant age/education, prior job search inte"
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "overclaim"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 12386ms

**Final Answer:** overclaim

**Confidence:** 0.88

**Assumptions:**
- The study design is a simple pre-post comparison without a control group
- The 12-month follow-up period includes 6 months of program participation plus 6 months post-completion
- No information is provided about selection bias, attrition, or confounding variables
- The text does not mention whether participants were randomly assigned or self-selected
- Economic conditions, labor market changes, and seasonal employment trends are not discussed
- No comparison group exists to establish what employment rate would have been without the program

**Reasoning Steps:**
1. Identified the study design: pre-post comparison (34% → 61%) without control group
2. Recognized that a 27 percentage point increase is substantial and noteworthy
3. Assessed whether this increase can be attributed to the program itself
4. Noted the absence of a control or comparison group—critical for causal inference
5. Identified major confounders: economic conditions, labor market tightness, seasonal effects, participant motivation/selection bias
6. Evaluated the causal language: 'successfully increased employment' and 'effectiveness of skills-based training' make causal claims
7. Determined that the evidence supports correlation (program participation correlates with employment gain) but not causation
8. Checked for alternative explanations: general economic improvement, self-selection of motivated individuals, regression to the mean, time passage effects

**Key Claims:**
- The text makes a causal claim ('successfully increased employment') based on pre-post data without a control group—this is a classic correlation vs. causation error
- The 27 percentage point increase is substantial, but without knowing the counterfactual (what would have happened without the program), causality cannot be established
- The program director's conclusion that 'results confirmed the effectiveness of skills-based training' overgeneralizes from a single-arm study to a broad claim about an intervention type
- No mention of confounders (economic conditions, labor market trends, participant selection effects) despite their obvious relevance
- The recommendation to expand the program is premature without evidence of causal impact

**Alternative Hypotheses:**
- correlation_vs_causation: The employment gain may reflect general labor market improvement, seasonal hiring, or self-selection of motivated participants rather than program effectiveness
- confounders: Unmeasured variables (economic growth, participant age/education, prior job search intensity) could explain the improvement
- solid: If the study included a matched control group or accounted for economic conditions, the causal claim would be more defensible (but text provides no evidence of this)

**Uncertainties:**
- Whether the study actually included a control group that is simply not mentioned in this summary
- The specific economic conditions during the 12-month period (labor market expansion vs. contraction)
- Whether attrition analysis was conducted (did lower-performing participants drop out?)
- Whether the 34% baseline employment rate was measured at the same point in the employment cycle as the 61% follow-up
- Whether participants were self-selected volunteers (high motivation) vs. randomly assigned

**Self-Verification:**
- Did I correctly identify the study design? Yes—it is explicitly a before-after comparison with no mention of a control group
- Did I overstate the problem? No—the absence of a control group is a fundamental limitation for causal claims, not a minor issue
- Did I miss any evidence of causal design? I reviewed the text carefully; no randomization, matching, or control group is mentioned
- Is the overclaim label justified? Yes—the text uses causal language ('successfully increased,' 'effectiveness') for correlational data
- Could this be a solid study? Only if the summary omits critical methodological details (e.g., a control group), but I must evaluate the text as presented

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 3.7/6 `######....`
- Uncertainty Handling: 3.3/6 `#####.....`
- Alternative Hypothesis Quality: 5.0/6 `########..`
- Self Monitoring Quality: 5.6/8 `#######...`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 8.5/10 `########..`


## Final Verdict

**Solo run: Claude Haiku** scored **70.4/100**.

**Best per dimension:**
- Correctness: Claude Haiku (30.0/30)
- Support Strength: Claude Haiku (0.0/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (3.7/6)
- Uncertainty Handling: Claude Haiku (3.3/6)
- Alternative Hypothesis Quality: Claude Haiku (5.0/6)
- Self Monitoring Quality: Claude Haiku (5.6/8)
- Insight Depth: Claude Haiku (8.0/8)
- Mechanism Quality: Claude Haiku (1.5/10)
- Communication Efficiency: Claude Haiku (8.5/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 12.4s | 70.4/100 | 5.7 |

Failure modes observed: decorative_uncertainty, named_not_explained, unsupported_conclusion, unsupported_intermediate_step, unused_assumption.
