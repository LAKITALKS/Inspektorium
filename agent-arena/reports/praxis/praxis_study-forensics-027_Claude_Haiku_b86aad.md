# Forensic Dossier: Study Forensics: AI coding assistant productivity claims

**Run ID:** `praxis_study-forensics-027_Claude_Haiku_b86aad`  
**Task:** study-forensics-027 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-07T07:54:42.422090+00:00  
**Task Family:** overclaim  
**Trap Type:** survivorship_bias_overclaim  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **71.2/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, named_not_explained, unsupported_conclusion, unsupported_intermediate_step
**Forensic flags:** 4
**Consistency findings:** 12
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 30.0/30 | 0.0/8 | 4.8/8 | 4.2/6 | 3.3/6 | 5.2/6 | 5.6/8 | 8.0/8 | 1.5/10 | 8.5/10 | **71.2/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `overclaim` [+] (gold: `overclaim`)
**Finding Recall:** 100%
**Matched Findings:** conclusion_exceeds_results, unsupported_generalization
**Extra Findings:** cautious_scope_control, correlation_as_causation

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
  - (+) `steps[6]`: "Examined causal language: 'AI coding assistants fundamentally enhance' treats correlation as causation without ruling ou"
    _Most informative reasoning step_
  - Note: 8 reasoning steps
  - Note: Low step utility: 0/8 steps contribute

**Assumption Discipline:** 4.2/6
  - (+) `assumptions[0]`: "The study measured only quantitative metrics (commits, PR times, velocity) without qualitative assessment of code qualit"
    _Most substantive assumption_
  - Note: 6/6 substantive assumptions
  - Note: Many assumptions (6)

**Uncertainty Handling:** 3.3/6
  - (+) `uncertainties[1]`: "What the baseline period was and whether it was comparable to the intervention period (e.g., same sprint cycle, team com"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.82"
    _Stated confidence level_
  - (-) `uncertainties[1]`: "What the baseline period was and whether it was comparable to the intervention period (e.g., same sprint cycle, team com"
    _Listed but never addressed in reasoning_
  - (-) `uncertainties[4]`: "How 'completion times' and 'velocity' were operationalized and whether they account for task complexity"
    _Listed but never addressed in reasoning_
  - Note: 6 uncertainties (6 substantive)
  - Note: 2 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 5.2/6
  - (+) `alternative_hypotheses[5]`: "The tool is beneficial for some developer profiles but not others, and the 'universal applicability' claim is unfounded"
    _Most substantive alternative hypothesis_
  - Note: 6 alternative hypotheses considered
  - Note: 3/6 include rejection reasoning

**Self Monitoring Quality:** 5.6/8
  - (+) `self_check[4]`: "Should I have flagged correlation vs. causation instead? Overclaim is more precise because the core issue is not just ca"
    _Most substantive self-verification step_
  - Note: 5 self-check items
  - Note: Self-check quality: 0 deep, 5 arithmetic, 0 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 8.5/10
  - Note: Signal density: 0.75, 661 words

**Insight Depth:** 8.0/8
  - (+) `(output text)`: "hin-subject before/after with no control group—this is vulnerable to multipl"
    _Insight 'no control group' matched (exact)_
  - Note: Key insights: 2 full / 2


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
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'What the baseline period was and whether it was comparable t...' is listed but not addressed
  - `uncertainties[1]`: "What the baseline period was and whether it was comparable to the intervention period (e.g., same sp"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'How 'completion times' and 'velocity' were operationalized a...' is listed but not addressed
  - `uncertainties[4]`: "How 'completion times' and 'velocity' were operationalized and whether they account for task complex"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/20 content words)
  - `key_claims[0]`: "The study uses a within-subject before/after design with no control group, making it vulnerable to c"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/14 content words)
  - `key_claims[1]`: "Productivity is measured only via easily-gamed quantitative metrics (commits, PR times) with no asse"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/12 content words)
  - `key_claims[2]`: "The conclusion 'fundamentally enhance' and 'reshape the industry' vastly exceeds the evidence from a"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (1/18 content words)
  - `key_claims[3]`: "The claim of 'universal applicability' is unsupported; the study shows consistency across junior/sen"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 5 has low overlap with final answer (0/11 content words)
  - `key_claims[4]`: "The 22% dropout rate is reframed as evidence of satisfaction without investigation, potentially mask"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 6 has low overlap with final answer (0/10 content words)
  - `key_claims[5]`: "No uncertainty language is present despite significant methodological limitations; recommendations a"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 2 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[1]`: "What the baseline period was and whether it was comparable to the intervention period (e.g., same sp"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 5 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[4]`: "How 'completion times' and 'velocity' were operationalized and whether they account for task complex"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "The productivity gains reflect a novelty effect that will diminish after the initial adoption period"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 2 is stated without rejection reasoning
  - `alternative_hypotheses[1]`: "Developers changed their behavior in response to being measured (Hawthorne effect), independent of t"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 3 is stated without rejection reasoning
  - `alternative_hypotheses[2]`: "The 22% who dropped out were less productive users, biasing the remaining sample toward higher perfo"
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "overclaim"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 15722ms

**Final Answer:** overclaim

**Confidence:** 0.82

**Assumptions:**
- The study measured only quantitative metrics (commits, PR times, velocity) without qualitative assessment of code quality
- Baseline measurements were taken immediately before tool adoption, potentially capturing a novelty/Hawthorne effect
- The 22% dropout rate is treated as evidence of satisfaction rather than investigated as a potential confounder
- No control group existed (comparison is within-subject before/after)
- The three-month timeframe is sufficient to assess 'transformative' and 'reshape the industry' claims
- Code commits and velocity are valid proxies for actual productivity and business value

**Reasoning Steps:**
1. Identified the core claims: 42% faster completion, 35% more commits, 'fundamentally enhance', 'reshape industry', 'universal applicability'
2. Examined the study design: within-subject before/after with no control group—this is vulnerable to multiple confounds
3. Assessed the dropout rate: 22% attrition is non-trivial but framed as evidence of satisfaction without investigation of reasons
4. Evaluated metric validity: commits and PR times are easily gamed (more commits ≠ better code); no mention of code quality, bugs, technical debt, or maintainability
5. Checked for novelty/Hawthorne effects: new tool adoption often produces temporary productivity spikes; three months is insufficient to distinguish sustained improvement from novelty
6. Analyzed generalization claims: 'universal applicability' and 'reshape the industry' are sweeping claims from a single 3-month study with no control group
7. Examined causal language: 'AI coding assistants fundamentally enhance' treats correlation as causation without ruling out confounds (e.g., developer motivation, selection bias, seasonal effects)
8. Reviewed uncertainty language: none present; recommendations are stated as imperative despite methodological limitations

**Key Claims:**
- The study uses a within-subject before/after design with no control group, making it vulnerable to confounds (novelty, Hawthorne effect, seasonal variation, selection bias from 22% dropout)
- Productivity is measured only via easily-gamed quantitative metrics (commits, PR times) with no assessment of code quality, maintainability, or business outcomes
- The conclusion 'fundamentally enhance' and 'reshape the industry' vastly exceeds the evidence from a single 3-month study
- The claim of 'universal applicability' is unsupported; the study shows consistency across junior/senior levels but does not test other relevant dimensions (domain, team size, codebase maturity)
- The 22% dropout rate is reframed as evidence of satisfaction without investigation, potentially masking selection bias
- No uncertainty language is present despite significant methodological limitations; recommendations are stated as imperative

**Alternative Hypotheses:**
- The productivity gains reflect a novelty effect that will diminish after the initial adoption period
- Developers changed their behavior in response to being measured (Hawthorne effect), independent of tool quality
- The 22% who dropped out were less productive users, biasing the remaining sample toward higher performers
- Increased commits reflect lower code quality or more fragmented changes, not genuine productivity
- Seasonal or organizational factors (e.g., sprint cycles, team composition changes) drove the gains, not the tool
- The tool is beneficial for some developer profiles but not others, and the 'universal applicability' claim is unfounded

**Uncertainties:**
- Whether code quality metrics (bugs, test coverage, refactoring needs) were measured—the summary does not mention them
- What the baseline period was and whether it was comparable to the intervention period (e.g., same sprint cycle, team composition)
- Why 22% of developers stopped using the tool and whether this represents dissatisfaction, technical issues, or other factors
- Whether the study included a control group of developers not using the tool during the same period
- How 'completion times' and 'velocity' were operationalized and whether they account for task complexity
- Whether the gains persisted beyond three months or if they represent a temporary spike

**Self-Verification:**
- Did I overstate the problems? No—the lack of a control group and quality metrics are genuine methodological gaps, not invented issues
- Did I miss positive aspects? The study does track multiple metrics over time and includes a reasonably large sample (450 developers), which are strengths
- Did I conflate study design with study quality? No—I focused on specific design choices (no control, no quality metrics) that limit causal inference
- Is the overclaim classification justified? Yes—the gap between 'faster commits in 3 months' and 'reshape the industry' is substantial and unsupported
- Should I have flagged correlation vs. causation instead? Overclaim is more precise because the core issue is not just causality but also generalization and metric validity

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 4.2/6 `#######...`
- Uncertainty Handling: 3.3/6 `#####.....`
- Alternative Hypothesis Quality: 5.2/6 `########..`
- Self Monitoring Quality: 5.6/8 `#######...`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 8.5/10 `########..`


## Final Verdict

**Solo run: Claude Haiku** scored **71.2/100**.

**Best per dimension:**
- Correctness: Claude Haiku (30.0/30)
- Support Strength: Claude Haiku (0.0/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (4.2/6)
- Uncertainty Handling: Claude Haiku (3.3/6)
- Alternative Hypothesis Quality: Claude Haiku (5.2/6)
- Self Monitoring Quality: Claude Haiku (5.6/8)
- Insight Depth: Claude Haiku (8.0/8)
- Mechanism Quality: Claude Haiku (1.5/10)
- Communication Efficiency: Claude Haiku (8.5/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 15.7s | 71.2/100 | 4.5 |

Failure modes observed: decorative_uncertainty, named_not_explained, unsupported_conclusion, unsupported_intermediate_step.
