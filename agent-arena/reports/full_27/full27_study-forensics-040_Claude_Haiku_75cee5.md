# Forensic Dossier: Study Forensics: Vocational training program claims effectiveness without control group

**Run ID:** `full27_study-forensics-040_Claude_Haiku_75cee5`  
**Task:** study-forensics-040 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T17:12:34.259332+00:00  
**Task Family:** overclaim  
**Trap Type:** missing_counterfactual  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **40.0/100** (margin: 0.0)
**Failure modes:** named_not_explained, unsupported_conclusion, wrong_answer
**Forensic flags:** 3
**Consistency findings:** 6
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 0.0/30 | 0.0/8 | 4.8/8 | 4.8/6 | 3.9/6 | 5.2/6 | 7.2/8 | 8.0/8 | 1.5/10 | 8.5/10 | **40.0/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `correlation_vs_causation` [x] (gold: `overclaim`)
**Finding Recall:** 100%
**Matched Findings:** unsupported_generalization, conclusion_exceeds_results, correlation_as_causation

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
  - (+) `steps[3]`: "4. CRITICAL CONFOUNDERS NOT ADDRESSED: (a) Economic conditions improved between baseline and 12-month follow-up — genera"
    _Most informative reasoning step_
  - Note: 7 reasoning steps
  - Note: Low step utility: 0/7 steps contribute

**Assumption Discipline:** 4.8/6
  - (+) `assumptions[0]`: "The study tracked the same cohort before and after intervention"
    _Most substantive assumption_
  - Note: 5/5 substantive assumptions

**Uncertainty Handling:** 3.9/6
  - (+) `uncertainties[2]`: "Whether the 12-month period coincided with general labor market improvement (would require external economic data)"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.92"
    _Stated confidence level_
  - Note: 5 uncertainties (5 substantive)
  - Note: Confidence 0.92

**Alternative Hypothesis Quality:** 5.2/6
  - (+) `alternative_hypotheses[1]`: "solid — if the study was actually a randomized trial or matched comparison and the summary simply omitted that detail (u"
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 1/2 include rejection reasoning

**Self Monitoring Quality:** 7.2/8
  - (+) `self_check[4]`: "Is this correlation_vs_causation or mechanism_vs_evidence? This is correlation_vs_causation because the study observes a"
    _Most substantive self-verification step_
  - Note: 6 self-check items
  - Note: Self-check quality: 1 deep, 5 arithmetic, 0 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 8.5/10
  - Note: Signal density: 0.72, 725 words

**Insight Depth:** 8.0/8
  - (+) `(output text)`: "of program participants with no control group. it measures employment rates"
    _Insight 'no control group' matched (exact)_
  - (+) `(output text)`: "in the 27-point increase; (b) selection bias — participants who completed"
    _Insight 'selection bias' matched (exact)_
  - Note: Key insights: 3 full / 3


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

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (1/25 content words)
  - `key_claims[0]`: "The core epistemic problem is CAUSATION FROM CORRELATION: a 27-point employment increase is observed"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/19 content words)
  - `key_claims[1]`: "The text makes strong causal claims ('successfully increased,' 'confirmed effectiveness') without he"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/16 content words)
  - `key_claims[2]`: "Policy expansion is recommended on the basis of limited_human evidence (pre-post observational data)"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/17 content words)
  - `key_claims[3]`: "The program director's statement ('confirmed the effectiveness of skills-based training') overgenera"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "overclaim — if the primary issue is the strength of causal language without hedging, rather than the"
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "correlation_vs_causation"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 15552ms

**Final Answer:** correlation_vs_causation

**Confidence:** 0.92

**Assumptions:**
- The study tracked the same cohort before and after intervention
- Employment was measured consistently at both timepoints
- The 12-month follow-up captured actual employment outcomes
- No selection bias affected who completed the program
- No confounding variables changed between baseline and follow-up

**Reasoning Steps:**
1. 1. EVIDENCE TIER IDENTIFICATION: This is a pre-post observational study of program participants with no control group. It measures employment rates in a real human population but lacks a comparison group. This is limited_human evidence (tier 4).
2. 2. CONCLUSION TIER IDENTIFICATION: The text recommends policy expansion ('expanding the program to additional districts') and claims causal effectiveness ('successfully increased employment'). This is human_policy tier.
3. 3. BRIDGE CHECK: The text claims the program 'successfully increased employment' and 'confirmed the effectiveness of skills-based training.' These are causal claims. The evidence is a pre-post comparison without a control group.
4. 4. CRITICAL CONFOUNDERS NOT ADDRESSED: (a) Economic conditions improved between baseline and 12-month follow-up — general labor market recovery could explain the 27-point increase; (b) Selection bias — participants who completed the program may differ systematically from those who enrolled (motivation, baseline skills, health status); (c) Regression to the mean — the 34% baseline may have been artificially depressed (e.g., measured during economic downturn); (d) Time passage — 12 months of job search, networking, and maturation independent of training could drive employment gains; (e) Attrition — if only employed participants were successfully followed up, the denominator changes.
5. 5. ABSENCE OF CONTROL GROUP: Without a comparison group (e.g., similar unemployed individuals not receiving training, or a waitlist control), the 27-point increase cannot be attributed to the program. It could reflect secular labor market improvement.
6. 6. HEDGING LANGUAGE CHECK: The text contains no uncertainty language ('could,' 'may,' 'suggests'). It uses definitive causal language ('successfully increased,' 'confirmed the effectiveness'). This strengthens the overclaim.
7. 7. POLICY RECOMMENDATION MISMATCH: The agency recommends expansion based on a pre-post design. This is a significant leap from observational evidence to policy without causal evidence.

**Key Claims:**
- The core epistemic problem is CAUSATION FROM CORRELATION: a 27-point employment increase is observed, but without a control group, this cannot be attributed to the program rather than confounding factors (economic recovery, selection bias, time passage).
- The text makes strong causal claims ('successfully increased,' 'confirmed effectiveness') without hedging, despite relying on a pre-post design that cannot isolate program effects.
- Policy expansion is recommended on the basis of limited_human evidence (pre-post observational data) without addressing obvious confounders or the absence of a control group.
- The program director's statement ('confirmed the effectiveness of skills-based training') overgeneralizes from a single program's pre-post data to a broad claim about the intervention class.

**Alternative Hypotheses:**
- overclaim — if the primary issue is the strength of causal language without hedging, rather than the absence of a control group
- solid — if the study was actually a randomized trial or matched comparison and the summary simply omitted that detail (unlikely given the text)

**Uncertainties:**
- Whether the study included any control group or comparison cohort not mentioned in the summary
- Whether employment was measured identically at baseline and follow-up (same definition, same data source)
- Whether the 12-month period coincided with general labor market improvement (would require external economic data)
- Whether attrition or loss-to-follow-up was differential by employment status
- Whether the program had selection criteria that would bias the sample toward more employable individuals

**Self-Verification:**
- Did I correctly identify the evidence tier? Yes — this is a real human population study but lacks a control group, making it limited_human (tier 4), not clinical_human (tier 5).
- Did I correctly identify the conclusion tier? Yes — the text recommends policy expansion and makes causal claims about program effectiveness, which is human_policy.
- Is the bridge supported? No — the text jumps from pre-post correlation to causal attribution without addressing confounders or using a control group.
- Did I fabricate problems? No — the absence of a control group and the presence of obvious confounders (economic conditions, selection bias, time passage) are real methodological gaps, not invented ones.
- Is this correlation_vs_causation or mechanism_vs_evidence? This is correlation_vs_causation because the study observes a correlation (employment increased after training) and infers causation (the program caused the increase) without ruling out confounders. It is not mechanism_vs_evidence because the evidence is in humans, not animals or cells.
- Should I flag overclaim as well? The strong causal language without hedging is part of the overclaim, but the root problem is the causal inference from a pre-post design.

**Dimension Scores:**
- Correctness: 0.0/30 `..........`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 4.8/6 `########..`
- Uncertainty Handling: 3.9/6 `######....`
- Alternative Hypothesis Quality: 5.2/6 `########..`
- Self Monitoring Quality: 7.2/8 `#########.`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 8.5/10 `########..`


## Final Verdict

**Solo run: Claude Haiku** scored **40.0/100**.

**Best per dimension:**
- Correctness: Claude Haiku (0.0/30)
- Support Strength: Claude Haiku (0.0/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (4.8/6)
- Uncertainty Handling: Claude Haiku (3.9/6)
- Alternative Hypothesis Quality: Claude Haiku (5.2/6)
- Self Monitoring Quality: Claude Haiku (7.2/8)
- Insight Depth: Claude Haiku (8.0/8)
- Mechanism Quality: Claude Haiku (1.5/10)
- Communication Efficiency: Claude Haiku (8.5/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 15.6s | 40.0/100 | 2.6 |

Failure modes observed: named_not_explained, unsupported_conclusion, wrong_answer.
