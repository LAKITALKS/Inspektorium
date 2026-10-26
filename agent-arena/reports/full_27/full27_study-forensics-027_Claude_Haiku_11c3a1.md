# Forensic Dossier: Study Forensics: AI coding assistant productivity claims

**Run ID:** `full27_study-forensics-027_Claude_Haiku_11c3a1`  
**Task:** study-forensics-027 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T08:18:38.381763+00:00  
**Task Family:** overclaim  
**Trap Type:** survivorship_bias_overclaim  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **70.1/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, named_not_explained, unsupported_conclusion, unsupported_intermediate_step, unused_assumption
**Forensic flags:** 4
**Consistency findings:** 12
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 30.0/30 | 0.0/8 | 4.8/8 | 3.7/6 | 3.0/6 | 5.0/6 | 5.6/8 | 8.0/8 | 1.5/10 | 8.5/10 | **70.1/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `overclaim` [+] (gold: `overclaim`)
**Finding Recall:** 100%
**Matched Findings:** conclusion_exceeds_results, unsupported_generalization
**Extra Findings:** decorative_uncertainty, correlation_as_causation

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
  - (+) `steps[4]`: "Analyzed the dropout rate: 22% attrition is reframed positively ('78% continued use') without investigating why 1 in 5 s"
    _Most informative reasoning step_
  - Note: 8 reasoning steps
  - Note: Low step utility: 0/8 steps contribute

**Assumption Discipline:** 3.7/6
  - (+) `assumptions[5]`: "Code commits and velocity are treated as direct proxies for meaningful productivity without addressing potential gaming "
    _Most substantive assumption_
  - (-) `assumptions[1]`: "Baseline measurements were taken immediately before tool adoption, potentially capturing a novelty/Hawthorne effect"
    _Declared but unused in reasoning_
  - Note: 6/6 substantive assumptions
  - Note: Many assumptions (6)

**Uncertainty Handling:** 3.0/6
  - (+) `uncertainties[2]`: "Whether the baseline period was truly representative or artificially depressed (e.g., developers were slower before adop"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.82"
    _Stated confidence level_
  - (-) `uncertainties[1]`: "The composition of the 450 developers (company size, domain, experience distribution) and whether results generalize bey"
    _Listed but never addressed in reasoning_
  - (-) `uncertainties[2]`: "Whether the baseline period was truly representative or artificially depressed (e.g., developers were slower before adop"
    _Listed but never addressed in reasoning_
  - Note: 6 uncertainties (6 substantive)
  - Note: 3 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 5.0/6
  - (+) `alternative_hypotheses[5]`: "The study measured speed, not productivity: faster task completion could reflect reduced deliberation or increased techn"
    _Most substantive alternative hypothesis_
  - Note: 6 alternative hypotheses considered
  - Note: 2/6 include rejection reasoning

**Self Monitoring Quality:** 5.6/8
  - (+) `self_check[2]`: "Did I miss positive aspects? The study does track multiple metrics over 3 months with a substantial sample (450), which "
    _Most substantive self-verification step_
  - Note: 5 self-check items
  - Note: Self-check quality: 0 deep, 5 arithmetic, 0 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 8.5/10
  - Note: Signal density: 0.75, 670 words

**Insight Depth:** 8.0/8
  - (+) `(output text)`: "ers assessed for confounders: no control group mentioned; novelty effect, le"
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
- **Unused Assumption** `[HEURISTIC]`: Assumption 'Baseline measurements were taken immediately before tool ado...' is declared but not referenced in reasoning
  - `assumptions[1]`: "Baseline measurements were taken immediately before tool adoption, potentially capturing a novelty/H"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'The composition of the 450 developers (company size, domain,...' is listed but not addressed
  - `uncertainties[1]`: "The composition of the 450 developers (company size, domain, experience distribution) and whether re"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether the baseline period was truly representative or arti...' is listed but not addressed
  - `uncertainties[2]`: "Whether the baseline period was truly representative or artificially depressed (e.g., developers wer"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'The nature of the 22% dropout: were they dissatisfied, did t...' is listed but not addressed
  - `uncertainties[3]`: "The nature of the 22% dropout: were they dissatisfied, did they face technical barriers, or did they"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (1/16 content words)
  - `key_claims[0]`: "The study makes a causal claim ('AI assistants enhance productivity') from a within-subject design w"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (1/11 content words)
  - `key_claims[1]`: "Generalization to 'the industry' is unsupported; results are from a single tool, single company/coho"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/14 content words)
  - `key_claims[2]`: "Quantity metrics (commits, speed) are treated as sufficient evidence of productivity without address"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/10 content words)
  - `key_claims[3]`: "The 22% dropout rate is reframed as evidence of satisfaction rather than investigated as a potential"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 5 has low overlap with final answer (1/13 content words)
  - `key_claims[4]`: "The claim of 'universal applicability' across experience levels is overstated; consistency is noted "
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 3 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[2]`: "Whether the baseline period was truly representative or artificially depressed (e.g., developers wer"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 4 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[3]`: "The nature of the 22% dropout: were they dissatisfied, did they face technical barriers, or did they"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "The productivity gains reflect a Hawthorne effect (being studied) rather than tool efficacy"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 3 is stated without rejection reasoning
  - `alternative_hypotheses[2]`: "Selection bias: the 22% who dropped out may have been less suited to the tool, inflating results for"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 4 is stated without rejection reasoning
  - `alternative_hypotheses[3]`: "Metric gaming: developers may have increased commits/velocity at the expense of code quality or arch"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 5 is stated without rejection reasoning
  - `alternative_hypotheses[4]`: "Confounding variables: concurrent training, team restructuring, or project selection changes during "
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "overclaim"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 17836ms

**Final Answer:** overclaim

**Confidence:** 0.82

**Assumptions:**
- The study measured only quantitative metrics (commits, PR times, velocity) without qualitative assessment of code quality
- Baseline measurements were taken immediately before tool adoption, potentially capturing a novelty/Hawthorne effect
- The 22% dropout rate is treated as evidence of satisfaction rather than investigated as a potential confounder
- No control group existed (comparison is within-subject before/after)
- The study duration (3 months) is assumed sufficient to detect sustained effects vs. temporary productivity boosts
- Code commits and velocity are treated as direct proxies for meaningful productivity without addressing potential gaming or quality trade-offs

**Reasoning Steps:**
1. Identified the core claim: AI assistants 'fundamentally enhance developer productivity' and 'will reshape software engineering workflows across the industry'
2. Examined the evidence: within-subject metrics (42% faster task completion, 35% more commits) over 3 months with 450 developers
3. Assessed for confounders: no control group mentioned; novelty effect, learning curve, and Hawthorne effect (being observed) are plausible alternatives to tool efficacy
4. Evaluated generalization: conclusion claims industry-wide applicability ('across the industry') from a single tool study with unknown selection bias
5. Analyzed the dropout rate: 22% attrition is reframed positively ('78% continued use') without investigating why 1 in 5 stopped—could indicate dissatisfaction, technical issues, or workload changes
6. Checked for quality assessment: no mention of code quality, bug rates, technical debt, or maintainability—only quantity metrics
7. Examined the 'universal applicability' claim: consistency across junior/senior developers is noted but doesn't address domain variation, team structure, or task type differences
8. Identified decorative uncertainty: 'notably' and 'indicating' language suggests confidence without acknowledging alternative explanations

**Key Claims:**
- The study makes a causal claim ('AI assistants enhance productivity') from a within-subject design with no control group, vulnerable to confounding
- Generalization to 'the industry' is unsupported; results are from a single tool, single company/cohort, over 3 months
- Quantity metrics (commits, speed) are treated as sufficient evidence of productivity without addressing code quality or long-term sustainability
- The 22% dropout rate is reframed as evidence of satisfaction rather than investigated as a potential signal of problems
- The claim of 'universal applicability' across experience levels is overstated; consistency is noted but not rigorously tested across diverse contexts

**Alternative Hypotheses:**
- The productivity gains reflect a Hawthorne effect (being studied) rather than tool efficacy
- Novelty effect: developers were more engaged in the first 3 months; gains may not persist
- Selection bias: the 22% who dropped out may have been less suited to the tool, inflating results for completers
- Metric gaming: developers may have increased commits/velocity at the expense of code quality or architectural soundness
- Confounding variables: concurrent training, team restructuring, or project selection changes during the study period
- The study measured speed, not productivity: faster task completion could reflect reduced deliberation or increased technical debt

**Uncertainties:**
- Whether code quality metrics (bugs, rework, maintainability) were measured but not reported, or genuinely not assessed
- The composition of the 450 developers (company size, domain, experience distribution) and whether results generalize beyond this population
- Whether the baseline period was truly representative or artificially depressed (e.g., developers were slower before adoption for unrelated reasons)
- The nature of the 22% dropout: were they dissatisfied, did they face technical barriers, or did they leave the company?
- Whether the 3-month window is sufficient to distinguish sustained productivity gains from temporary novelty effects
- How 'consistent across junior and senior developers' was measured—were effect sizes truly equivalent, or just directionally similar?

**Self-Verification:**
- Did I assume problems that aren't stated? No—the text explicitly lacks a control group, quality metrics, and investigation of dropouts. These are genuine gaps.
- Did I conflate 'could be confounded' with 'is confounded'? No—I identified plausible confounders (Hawthorne, novelty) without claiming they definitely explain the results.
- Did I miss positive aspects? The study does track multiple metrics over 3 months with a substantial sample (450), which is methodologically stronger than many tech reports. However, the design flaws and overclaimed conclusions remain.
- Is the overclaim classification justified? Yes—the text moves from 'faster task completion in 3 months' to 'will reshape the industry' without addressing confounds, quality, or long-term effects.
- Did I fairly assess the dropout rate? Yes—78% continuation is presented as evidence of utility, but 22% attrition deserves investigation rather than dismissal.

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 3.7/6 `######....`
- Uncertainty Handling: 3.0/6 `####......`
- Alternative Hypothesis Quality: 5.0/6 `########..`
- Self Monitoring Quality: 5.6/8 `#######...`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 8.5/10 `########..`


## Final Verdict

**Solo run: Claude Haiku** scored **70.1/100**.

**Best per dimension:**
- Correctness: Claude Haiku (30.0/30)
- Support Strength: Claude Haiku (0.0/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (3.7/6)
- Uncertainty Handling: Claude Haiku (3.0/6)
- Alternative Hypothesis Quality: Claude Haiku (5.0/6)
- Self Monitoring Quality: Claude Haiku (5.6/8)
- Insight Depth: Claude Haiku (8.0/8)
- Mechanism Quality: Claude Haiku (1.5/10)
- Communication Efficiency: Claude Haiku (8.5/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 17.8s | 70.1/100 | 3.9 |

Failure modes observed: decorative_uncertainty, named_not_explained, unsupported_conclusion, unsupported_intermediate_step, unused_assumption.
