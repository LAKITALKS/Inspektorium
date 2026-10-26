# Forensic Dossier: Study Forensics: Vocational training program claims effectiveness without control group

**Run ID:** `minival_study-forensics-040_Claude_Haiku_5da1ec`  
**Task:** study-forensics-040 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T07:57:58.892736+00:00  
**Task Family:** overclaim  
**Trap Type:** missing_counterfactual  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **72.8/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, missed_key_insight, unsupported_conclusion, unsupported_intermediate_step, unused_assumption
**Forensic flags:** 3
**Consistency findings:** 9
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 30.0/30 | 0.0/8 | 4.8/8 | 3.2/6 | 3.6/6 | 5.1/6 | 5.6/8 | 8.0/8 | 4.0/10 | 8.5/10 | **72.8/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `overclaim` [+] (gold: `overclaim`)
**Finding Recall:** 67%
**Matched Findings:** conclusion_exceeds_results, correlation_as_causation
**Missed Findings:** unsupported_generalization
**Extra Findings:** cautious_scope_control, none_or_minor

## Reasoning Integrity Audit

### Claude Haiku
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 7

## Mechanism Analysis

### Claude Haiku
| Aspect | Status |
|--------|--------|
| Concept named | :white_check_mark: effect |
| Mechanism described | :white_check_mark: (1 sentence(s)) |
| Grounded to case | :x: (0 sentence(s)) |

**Missing:** mechanism not grounded to case data

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

- **[MAJOR]** `unsupported_leap`: Correct answer with weak support chain — final answer may be an unsupported leap
- **[MODERATE]** `unsupported_conclusion_claims`: 1/1 conclusion claims lack step support
  - `final_answer`: "overclaim"
- **[MODERATE]** `ungrounded_mechanism`: Mechanism named/described but not connected to case-specific data
  - `(mechanism analysis)`: "effect"


## Evidence Map

### Claude Haiku

**Correctness:** 30.0/30
  - (+) `final_answer`: "overclaim"
    _Agent's answer for correctness check_
  - Note: Exact match

**Support Strength:** 0.0/8
  - (-) `final_answer`: "overclaim"
    _Conclusion not supported by steps_
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 7
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[4]`: "Identified confounders: general economic recovery, labor market tightening, seasonal hiring cycles, participant motivati"
    _Most informative reasoning step_
  - Note: 7 reasoning steps
  - Note: Low step utility: 0/7 steps contribute

**Assumption Discipline:** 3.2/6
  - (+) `assumptions[1]`: "The 12-month follow-up period includes 6 months of program participation plus 6 months post-completion"
    _Most substantive assumption_
  - (-) `assumptions[1]`: "The 12-month follow-up period includes 6 months of program participation plus 6 months post-completion"
    _Declared but unused in reasoning_
  - (-) `assumptions[2]`: "No information is provided about selection bias, attrition, or confounding variables"
    _Declared but unused in reasoning_
  - Note: 6/6 substantive assumptions
  - Note: Many assumptions (6)

**Uncertainty Handling:** 3.6/6
  - (+) `uncertainties[0]`: "Whether the agency collected data on a comparison group (unemployed individuals who did not participate)"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.92"
    _Stated confidence level_
  - (-) `uncertainties[5]`: "Whether the 61% figure includes part-time, temporary, or underemployment, or only full-time positions"
    _Listed but never addressed in reasoning_
  - Note: 6 uncertainties (6 substantive)
  - Note: 1 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 5.1/6
  - (+) `alternative_hypotheses[1]`: "Participants were self-selected individuals already motivated to find work; the program accelerated an inevitable outcom"
    _Most substantive alternative hypothesis_
  - Note: 5 alternative hypotheses considered
  - Note: 2/5 include rejection reasoning

**Self Monitoring Quality:** 5.6/8
  - (+) `self_check[4]`: "Is the overclaim classification appropriate? Yes—the conclusion (program caused the increase) exceeds the evidence (pre-"
    _Most substantive self-verification step_
  - Note: 5 self-check items
  - Note: Self-check quality: 0 deep, 5 arithmetic, 0 fluff

**Mechanism Quality:** 4.0/10
  - (+) `(mechanism analysis)`: "Assessed whether the improvement could be explained by factors other than the program"
    _Mechanism description without case grounding_
  - Note: Names concept + describes mechanism (not grounded to case)

**Communication Efficiency:** 8.5/10
  - Note: Signal density: 0.70, 513 words

**Insight Depth:** 8.0/8
  - (+) `(output text)`: "information is provided about selection bias, attrition, or confounding va"
    _Insight 'selection bias' matched (exact)_
  - Note: Key insights: 3 full / 3


## Failure Analysis

### Claude Haiku

**MAJOR:**
- **Missed Key Insight** `[MEDIUM CONFIDENCE]`: Missed expected finding: unsupported_generalization
  - `(task expectation)`: "Expected: unsupported_generalization"
  - _Impacts: insight_depth_

**MODERATE:**
- **Unsupported Conclusion** `[MEDIUM CONFIDENCE]`: Final answer lacks load-bearing or supporting step grounding
  - `final_answer`: "overclaim"
  - _Impacts: support_strength_
- **Unsupported Intermediate Step** `[MEDIUM CONFIDENCE]`: No reasoning step is load-bearing — final answer lacks traceable derivation
  - `final_answer`: "overclaim"
  - _Impacts: support_strength, structural_reasoning_

**STYLISTIC:**
- **Unused Assumption** `[HEURISTIC]`: Assumption 'The 12-month follow-up period includes 6 months of program p...' is declared but not referenced in reasoning
  - `assumptions[1]`: "The 12-month follow-up period includes 6 months of program participation plus 6 months post-completi"
  - _Impacts: assumption_discipline_
- **Unused Assumption** `[HEURISTIC]`: Assumption 'No information is provided about selection bias, attrition, ...' is declared but not referenced in reasoning
  - `assumptions[2]`: "No information is provided about selection bias, attrition, or confounding variables"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether the 61% figure includes part-time, temporary, or und...' is listed but not addressed
  - `uncertainties[5]`: "Whether the 61% figure includes part-time, temporary, or underemployment, or only full-time position"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (1/18 content words)
  - `key_claims[0]`: "The study makes a causal claim ('program successfully increased employment') from a pre-post design "
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/17 content words)
  - `key_claims[1]`: "The 27 percentage point improvement is presented as evidence of program effectiveness, but multiple "
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/11 content words)
  - `key_claims[2]`: "The recommendation to expand the program is based on an uncontrolled comparison, which does not meet"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/14 content words)
  - `key_claims[3]`: "The program director's statement that results 'confirmed the effectiveness of skills-based training'"
- **[WARN]** `[HEURISTIC]` `claim_step_alignment`: Key claim 3 not well supported in reasoning steps (2/11 content words found)
  - `key_claims[2]`: "The recommendation to expand the program is based on an uncontrolled comparison, which does not meet"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 6 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[5]`: "Whether the 61% figure includes part-time, temporary, or underemployment, or only full-time position"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 2 is stated without rejection reasoning
  - `alternative_hypotheses[1]`: "Participants were self-selected individuals already motivated to find work; the program accelerated "
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 3 is stated without rejection reasoning
  - `alternative_hypotheses[2]`: "Seasonal employment patterns or labor market tightening drove the increase independent of training"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 4 is stated without rejection reasoning
  - `alternative_hypotheses[3]`: "Attrition bias: participants who dropped out may have had worse employment outcomes, inflating the r"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 11965ms

**Final Answer:** overclaim

**Confidence:** 0.92

**Assumptions:**
- The study design is a simple pre-post comparison without a control group
- The 12-month follow-up period includes 6 months of program participation plus 6 months post-completion
- No information is provided about selection bias, attrition, or confounding variables
- The text does not mention whether participants were randomly assigned or self-selected
- Economic conditions, labor market changes, and seasonal employment trends are not discussed
- No comparison group exists to establish what employment rate would have been without the program

**Reasoning Steps:**
1. Identified the study design: pre-post comparison (34% → 61% employment)
2. Noted the absence of a control or comparison group
3. Recognized that a 27 percentage point increase is substantial but cannot be attributed to the program without a counterfactual
4. Examined the causal language: 'concluded that the program successfully increased employment' and 'confirmed the effectiveness'
5. Identified confounders: general economic recovery, labor market tightening, seasonal hiring cycles, participant motivation/selection effects, and time passage itself
6. Assessed whether the improvement could be explained by factors other than the program
7. Evaluated the strength of evidence for the causal claim versus the strength of the conclusion

**Key Claims:**
- The study makes a causal claim ('program successfully increased employment') from a pre-post design without a control group—this is a classic correlation vs. causation problem
- The 27 percentage point improvement is presented as evidence of program effectiveness, but multiple confounders (economic conditions, time passage, selection effects) could explain the gain
- The recommendation to expand the program is based on an uncontrolled comparison, which does not meet the evidentiary standard for causal inference
- The program director's statement that results 'confirmed the effectiveness of skills-based training' overstates the evidence; the design cannot confirm causation

**Alternative Hypotheses:**
- The employment increase reflects general economic improvement during the 12-month period, not program effectiveness
- Participants were self-selected individuals already motivated to find work; the program accelerated an inevitable outcome
- Seasonal employment patterns or labor market tightening drove the increase independent of training
- Attrition bias: participants who dropped out may have had worse employment outcomes, inflating the reported success rate
- The program had modest effect, but confounders account for most of the 27 percentage point gain

**Uncertainties:**
- Whether the agency collected data on a comparison group (unemployed individuals who did not participate)
- Whether employment was measured consistently at both time points (same definition, same methodology)
- What the baseline employment rate would have been for similar individuals without the program
- Whether economic conditions improved, worsened, or remained stable during the 12-month period
- The composition of the participant group and whether selection bias is present
- Whether the 61% figure includes part-time, temporary, or underemployment, or only full-time positions

**Self-Verification:**
- Did I correctly identify the absence of a control group? Yes—the text describes only a pre-post comparison.
- Did I overstate the problems? No—the lack of a control group is a fundamental limitation for causal claims.
- Did I consider that the study might still be useful? Yes—pre-post data can be informative, but the causal claim is not justified.
- Did I miss any evidence of controls or confounding adjustments? No—the text provides no mention of these.
- Is the overclaim classification appropriate? Yes—the conclusion (program caused the increase) exceeds the evidence (pre-post comparison only).

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 3.2/6 `#####.....`
- Uncertainty Handling: 3.6/6 `######....`
- Alternative Hypothesis Quality: 5.1/6 `########..`
- Self Monitoring Quality: 5.6/8 `#######...`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 4.0/10 `####......`
- Communication Efficiency: 8.5/10 `########..`


## Final Verdict

**Solo run: Claude Haiku** scored **72.8/100**.

**Best per dimension:**
- Correctness: Claude Haiku (30.0/30)
- Support Strength: Claude Haiku (0.0/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (3.2/6)
- Uncertainty Handling: Claude Haiku (3.6/6)
- Alternative Hypothesis Quality: Claude Haiku (5.1/6)
- Self Monitoring Quality: Claude Haiku (5.6/8)
- Insight Depth: Claude Haiku (8.0/8)
- Mechanism Quality: Claude Haiku (4.0/10)
- Communication Efficiency: Claude Haiku (8.5/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 12.0s | 72.8/100 | 6.1 |

Failure modes observed: decorative_uncertainty, missed_key_insight, unsupported_conclusion, unsupported_intermediate_step, unused_assumption.
