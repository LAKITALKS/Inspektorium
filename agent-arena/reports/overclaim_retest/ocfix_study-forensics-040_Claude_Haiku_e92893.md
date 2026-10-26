# Forensic Dossier: Study Forensics: Vocational training program claims effectiveness without control group

**Run ID:** `ocfix_study-forensics-040_Claude_Haiku_e92893`  
**Task:** study-forensics-040 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T17:29:07.066070+00:00  
**Task Family:** overclaim  
**Trap Type:** missing_counterfactual  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **39.7/100** (margin: 0.0)
**Failure modes:** missed_key_insight, named_not_explained, unsupported_conclusion, wrong_answer
**Forensic flags:** 3
**Consistency findings:** 8
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 0.0/30 | 0.0/8 | 4.8/8 | 4.8/6 | 3.9/6 | 4.5/6 | 6.4/8 | 5.3/8 | 1.5/10 | 8.5/10 | **39.7/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `correlation_vs_causation` [x] (gold: `overclaim`)
**Finding Recall:** 67%
**Matched Findings:** conclusion_exceeds_results, correlation_as_causation
**Missed Findings:** unsupported_generalization
**Extra Findings:** cautious_scope_control, decorative_uncertainty, mechanism_not_demonstrated

## Reasoning Integrity Audit

### Claude Haiku
**Classification:** Correct and well-supported
**Load-bearing steps:** 0 / 7

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
- "correlation_vs_causation"


## Forensic Flags

### Claude Haiku

- **[MAJOR]** `well_reasoned_wrong`: Wrong answer but structured reasoning — may have a subtle logic error
  - `final_answer`: "correlation_vs_causation"
- **[MODERATE]** `unsupported_conclusion_claims`: 1/1 conclusion claims lack step support
  - `final_answer`: "correlation_vs_causation"
- **[MODERATE]** `ungrounded_mechanism`: Mechanism named/described but not connected to case-specific data
  - `(mechanism analysis)`: "bias, effect"


## Evidence Map

### Claude Haiku

**Correctness:** 0.0/30
  - (+) `final_answer`: "correlation_vs_causation"
    _Agent's answer for correctness check_
  - Note: No match (got: correlation_vs_causation)

**Support Strength:** 0.0/8
  - (-) `final_answer`: "correlation_vs_causation"
    _Conclusion not supported by steps_
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 7
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[3]`: "CONFOUNDERS PRESENT: (1) Economic conditions improved between baseline and 12-month follow-up — regional employment may "
    _Most informative reasoning step_
  - Note: 7 reasoning steps
  - Note: Low step utility: 0/7 steps contribute

**Assumption Discipline:** 4.8/6
  - (+) `assumptions[0]`: "The 34% pre-enrollment employment rate and 61% post-completion rate are accurately measured"
    _Most substantive assumption_
  - Note: 5/5 substantive assumptions

**Uncertainty Handling:** 3.9/6
  - (+) `uncertainties[3]`: "Whether the text represents the full study report or a summary that omits methodological details (e.g., a control group "
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.88"
    _Stated confidence level_
  - Note: 4 uncertainties (4 substantive)
  - Note: Confidence 0.88

**Alternative Hypothesis Quality:** 4.5/6
  - (+) `alternative_hypotheses[1]`: "solid — if the study had included a matched control group or quasi-experimental design (e.g., regression discontinuity, "
    _Most substantive alternative hypothesis_
  - Note: 3 alternative hypotheses considered
  - Note: 3/3 genuinely diverse alternatives

**Self Monitoring Quality:** 6.4/8
  - (+) `self_check[3]`: "Did I confuse 'lack of hedging' with 'overclaim'? No. The text is confident but not using promotional language. The issu"
    _Most substantive self-verification step_
  - Note: 6 self-check items
  - Note: Self-check quality: 0 deep, 6 arithmetic, 0 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 8.5/10
  - Note: Signal density: 0.70, 645 words

**Insight Depth:** 5.3/8
  - (+) `(output text)`: "rt with pre/post measurement. no control group, no randomization, no compari"
    _Insight 'no control group' matched (exact)_
  - (+) `(output text)`: "ve risen for all workers. (2) selection bias — participants who completed"
    _Insight 'selection bias' matched (exact)_
  - (?) `(not found)`: "Missing: secular trends"
    _Insight 'secular trends' not found_
  - Note: Key insights: 2 full / 3


## Failure Analysis

### Claude Haiku

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
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Named concept(s) ['bias', 'effect'] but mechanism not described
  - _Impacts: mechanism_quality, insight_depth_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/7 content words)
  - `key_claims[0]`: "Employment rose from 34% to 61% — this is an observed correlation, not a causal effect."
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/9 content words)
  - `key_claims[1]`: "The program 'successfully increased employment' — this is a causal claim unsupported by the study de"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/10 content words)
  - `key_claims[2]`: "The results 'confirmed the effectiveness of skills-based training' — this overstates what a single-a"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/9 content words)
  - `key_claims[3]`: "Recommendation to expand is premature without evidence that the program, not confounders, drove the "
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "overclaim — if the text were using promotional language like 'breakthrough' or 'transforms outcomes,"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 2 is stated without rejection reasoning
  - `alternative_hypotheses[1]`: "solid — if the study had included a matched control group or quasi-experimental design (e.g., regres"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 3 is stated without rejection reasoning
  - `alternative_hypotheses[2]`: "mechanism_vs_evidence — if the text were making claims about *why* the program works (e.g., 'improve"
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "correlation_vs_causation"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 14328ms

**Final Answer:** correlation_vs_causation

**Confidence:** 0.88

**Assumptions:**
- The 34% pre-enrollment employment rate and 61% post-completion rate are accurately measured
- The same cohort was tracked before and after (not different populations)
- Employment status was measured consistently at both time points
- The 12-month follow-up period is sufficient to observe stable outcomes
- No selection bias affected who completed the program

**Reasoning Steps:**
1. EVIDENCE TIER: This is observational data from a single cohort with pre/post measurement. No control group, no randomization, no comparison to a counterfactual. This is limited human observation (tier 4).
2. CONCLUSION TIER: The text implies the program caused employment gains and recommends policy expansion. This is a causal human therapeutic claim (tier 5).
3. BRIDGE GAP: The evidence is a simple before-after comparison. The 27-percentage-point rise is observed, but causation is not established.
4. CONFOUNDERS PRESENT: (1) Economic conditions improved between baseline and 12-month follow-up — regional employment may have risen for all workers. (2) Selection bias — participants who completed the program may differ from those who enrolled (motivation, education, health). (3) Time passage — 12 months of job search, networking, and maturation independent of training. (4) Regression to the mean — those at 34% employment may naturally drift upward. (5) Survivor bias — only those who completed are measured; dropouts are excluded.
5. CAUSAL LANGUAGE: The text states the program 'successfully increased employment' and 'confirmed the effectiveness' — these are causal claims. The director attributes the outcome to 'skills-based training as an intervention.' No alternative explanations are considered.
6. LACK OF CONTROL: No comparison group (e.g., similar unemployed individuals who did not enroll, or a waitlist control). Without a control, the 27-point rise cannot be attributed to the program.
7. CLASSIFICATION: The core problem is not overclaim of certainty (the text does not hedge with 'may' or 'could'), but rather a causal inference drawn from correlational data. The employment rise is real, but its cause is unknown.

**Key Claims:**
- Employment rose from 34% to 61% — this is an observed correlation, not a causal effect.
- The program 'successfully increased employment' — this is a causal claim unsupported by the study design.
- The results 'confirmed the effectiveness of skills-based training' — this overstates what a single-arm pre-post design can confirm.
- Recommendation to expand is premature without evidence that the program, not confounders, drove the gain.

**Alternative Hypotheses:**
- overclaim — if the text were using promotional language like 'breakthrough' or 'transforms outcomes,' the primary issue would be rhetorical inflation rather than causal inference
- solid — if the study had included a matched control group or quasi-experimental design (e.g., regression discontinuity, difference-in-differences), the causal claim would be supported
- mechanism_vs_evidence — if the text were making claims about *why* the program works (e.g., 'improves soft skills') without measuring those mechanisms, that would be the primary issue

**Uncertainties:**
- Whether the agency collected data on regional employment trends during the same period (would help rule out economic confounding)
- Whether dropout rates or program completion rates are reported (affects selection bias assessment)
- Whether the 34% baseline is representative of the target population or reflects selection into the program
- Whether the text represents the full study report or a summary that omits methodological details (e.g., a control group may exist but not be mentioned)

**Self-Verification:**
- Did I correctly identify the evidence tier? Yes — single cohort, pre-post measurement, no control group = limited human observation.
- Did I correctly identify the conclusion tier? Yes — the text implies causal program effect on employment outcomes.
- Is the bridge gap real? Yes — a 27-point rise is observed, but causation requires ruling out confounders, which this design does not do.
- Did I confuse 'lack of hedging' with 'overclaim'? No. The text is confident but not using promotional language. The issue is causal inference, not rhetorical excess.
- Did I miss a control group? I checked the text carefully. No control group is mentioned.
- Is this a solid study? No — the absence of a control group is a fundamental design limitation, not a minor caveat.

**Dimension Scores:**
- Correctness: 0.0/30 `..........`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 4.8/6 `########..`
- Uncertainty Handling: 3.9/6 `######....`
- Alternative Hypothesis Quality: 4.5/6 `#######...`
- Self Monitoring Quality: 6.4/8 `########..`
- Insight Depth: 5.3/8 `######....`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 8.5/10 `########..`


## Final Verdict

**Solo run: Claude Haiku** scored **39.7/100**.

**Best per dimension:**
- Correctness: Claude Haiku (0.0/30)
- Support Strength: Claude Haiku (0.0/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (4.8/6)
- Uncertainty Handling: Claude Haiku (3.9/6)
- Alternative Hypothesis Quality: Claude Haiku (4.5/6)
- Self Monitoring Quality: Claude Haiku (6.4/8)
- Insight Depth: Claude Haiku (5.3/8)
- Mechanism Quality: Claude Haiku (1.5/10)
- Communication Efficiency: Claude Haiku (8.5/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 14.3s | 39.7/100 | 2.8 |

Failure modes observed: missed_key_insight, named_not_explained, unsupported_conclusion, wrong_answer.
