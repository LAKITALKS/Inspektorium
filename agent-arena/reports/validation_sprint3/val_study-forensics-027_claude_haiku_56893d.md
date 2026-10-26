# Forensic Dossier: Study Forensics: AI coding assistant productivity claims

**Run ID:** `val_study-forensics-027_claude_haiku_56893d`  
**Task:** study-forensics-027 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-06T14:33:08.533135+00:00  
**Task Family:** overclaim  
**Trap Type:** survivorship_bias_overclaim  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **70.9/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, named_not_explained, unsupported_conclusion, unsupported_intermediate_step, unused_assumption
**Forensic flags:** 4
**Consistency findings:** 12
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 30.0/30 | 0.0/8 | 4.8/8 | 3.7/6 | 3.0/6 | 5.0/6 | 6.4/8 | 8.0/8 | 1.5/10 | 8.5/10 | **70.9/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `overclaim` [+] (gold: `overclaim`)
**Finding Recall:** 100%
**Matched Findings:** conclusion_exceeds_results, unsupported_generalization
**Extra Findings:** cautious_scope_control, decorative_uncertainty, mechanism_not_demonstrated, correlation_as_causation

## Reasoning Integrity Audit

### Claude Haiku
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 8

## Claim Verification

### Claude Haiku
Claims checked: 1 | Supported: 0 | Contradicted: 0 | Unresolved: 1

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
  - (+) `steps[4]`: "Analyzed the retention statistic: 78% continuation is presented as evidence of satisfaction, but 22% dropout is not expl"
    _Most informative reasoning step_
  - Note: 8 reasoning steps
  - Note: Low step utility: 0/8 steps contribute

**Assumption Discipline:** 3.7/6
  - (+) `assumptions[0]`: "The study measured only quantitative metrics (commits, PR times, velocity) without qualitative assessment of code qualit"
    _Most substantive assumption_
  - (-) `assumptions[1]`: "Baseline measurements were taken immediately before tool adoption, potentially capturing a novelty/Hawthorne effect"
    _Declared but unused in reasoning_
  - Note: 7/7 substantive assumptions
  - Note: Many assumptions (7)

**Uncertainty Handling:** 3.0/6
  - (+) `uncertainties[3]`: "Whether 'consistent across junior and senior developers' means statistically equivalent effect sizes or merely that both"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.82"
    _Stated confidence level_
  - (-) `uncertainties[1]`: "Whether the baseline period was long enough to establish a stable pre-intervention state, or whether it captured a trans"
    _Listed but never addressed in reasoning_
  - (-) `uncertainties[3]`: "Whether 'consistent across junior and senior developers' means statistically equivalent effect sizes or merely that both"
    _Listed but never addressed in reasoning_
  - Note: 6 uncertainties (6 substantive)
  - Note: 4 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 5.0/6
  - (+) `alternative_hypotheses[1]`: "mechanism_vs_evidence: The study measures outputs (commits, speed) but does not measure whether code quality, maintainab"
    _Most substantive alternative hypothesis_
  - Note: 3 alternative hypotheses considered
  - Note: 1/3 include rejection reasoning

**Self Monitoring Quality:** 6.4/8
  - (+) `self_check[4]`: "Should this be 'correlation_vs_causation' instead? Partially—there is no control group, so causation is not established;"
    _Most substantive self-verification step_
  - Note: 5 self-check items
  - Note: Self-check quality: 1 deep, 4 arithmetic, 0 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 8.5/10
  - Note: Signal density: 0.76, 671 words

**Insight Depth:** 8.0/8
  - (+) `(output text)`: "claims evaluated confounders: no control group, no measurement of code quali"
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
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether the baseline period was long enough to establish a s...' is listed but not addressed
  - `uncertainties[1]`: "Whether the baseline period was long enough to establish a stable pre-intervention state, or whether"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether 'consistent across junior and senior developers' mea...' is listed but not addressed
  - `uncertainties[3]`: "Whether 'consistent across junior and senior developers' means statistically equivalent effect sizes"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether the three-month window is sufficient to detect long-...' is listed but not addressed
  - `uncertainties[4]`: "Whether the three-month window is sufficient to detect long-term productivity changes or whether gai"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether the study controlled for concurrent changes (e.g., t...' is listed but not addressed
  - `uncertainties[5]`: "Whether the study controlled for concurrent changes (e.g., team composition, project complexity, oth"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/16 content words)
  - `key_claims[0]`: "The study provides strong evidence for short-term quantitative output increases (commits, task speed"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/19 content words)
  - `key_claims[1]`: "The conclusion that AI assistants 'will reshape software engineering workflows across the industry' "
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (1/14 content words)
  - `key_claims[2]`: "The claim of 'universal applicability' is unsupported—the study shows both groups improved, but does"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/16 content words)
  - `key_claims[3]`: "Code commits and task completion speed are imperfect proxies for productivity; absent quality metric"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 5 has low overlap with final answer (0/15 content words)
  - `key_claims[4]`: "The 22% dropout rate is reframed as evidence of satisfaction (78% retention) without investigating w"
- **[WARN]** `[HEURISTIC]` `unused_assumption`: Assumption 2 appears unused in reasoning or answer
  - `assumptions[1]`: "Baseline measurements were taken immediately before tool adoption, potentially capturing a novelty/H"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 4 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[3]`: "Whether 'consistent across junior and senior developers' means statistically equivalent effect sizes"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 5 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[4]`: "Whether the three-month window is sufficient to detect long-term productivity changes or whether gai"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 6 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[5]`: "Whether the study controlled for concurrent changes (e.g., team composition, project complexity, oth"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "correlation_vs_causation: The productivity gains could reflect novelty effects, Hawthorne effect (be"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 3 is stated without rejection reasoning
  - `alternative_hypotheses[2]`: "confounders: Developers may have shifted task selection toward simpler, AI-friendly tasks; may have "
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "overclaim"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 15899ms

**Final Answer:** overclaim

**Confidence:** 0.82

**Assumptions:**
- The study measured only quantitative metrics (commits, PR times, velocity) without qualitative assessment of code quality
- Baseline measurements were taken immediately before tool adoption, potentially capturing a novelty/Hawthorne effect
- The 22% dropout rate is treated as evidence of satisfaction rather than investigated as a potential confounder
- No control group existed (comparison is within-subject before/after)
- The three-month timeframe is sufficient to assess 'sustained utility' and long-term productivity
- Code commits and velocity are valid proxies for actual productivity and business value
- The study population (450 developers) is representative of 'the industry'

**Reasoning Steps:**
1. Identified the core claim: AI assistants 'fundamentally enhance developer productivity' and 'will reshape software engineering workflows across the industry'
2. Examined the evidence: within-subject metrics (commits +35%, task completion +42%) over 3 months with 78% retention
3. Assessed scope mismatch: study measured narrow quantitative outputs; conclusion makes broad causal and industry-wide claims
4. Evaluated confounders: no control group, no measurement of code quality, no assessment of technical debt, no measurement of bug rates or maintenance burden
5. Analyzed the retention statistic: 78% continuation is presented as evidence of satisfaction, but 22% dropout is not explained and could indicate selection bias (remaining users are self-selected enthusiasts)
6. Checked for mechanism clarity: the study does not explain *why* productivity increased (learning curve? reduced cognitive load? task selection bias?)
7. Evaluated generalizability claims: 'universal applicability regardless of experience level' is stated but not substantiated with interaction analysis or stratified results
8. Identified decorative uncertainty: no caveats, limitations, or 'more research needed' language despite making sweeping industry-level recommendations

**Key Claims:**
- The study provides strong evidence for short-term quantitative output increases (commits, task speed) but weak evidence for the causal mechanism or long-term sustainability
- The conclusion that AI assistants 'will reshape software engineering workflows across the industry' vastly exceeds the scope of a single 3-month study of 450 developers with no control group
- The claim of 'universal applicability' is unsupported—the study shows both groups improved, but does not demonstrate equivalent effect sizes or mechanisms
- Code commits and task completion speed are imperfect proxies for productivity; absent quality metrics, the gains could reflect faster but lower-quality work
- The 22% dropout rate is reframed as evidence of satisfaction (78% retention) without investigating why developers left or whether they represent a different population

**Alternative Hypotheses:**
- correlation_vs_causation: The productivity gains could reflect novelty effects, Hawthorne effect (being observed), or selection bias (enthusiasts self-selected into continued use) rather than genuine tool efficacy
- mechanism_vs_evidence: The study measures outputs (commits, speed) but does not measure whether code quality, maintainability, or actual business value improved—a critical gap when extrapolating to industry-wide claims
- confounders: Developers may have shifted task selection toward simpler, AI-friendly tasks; may have reduced code review rigor; or may have accumulated technical debt that will manifest later

**Uncertainties:**
- Whether the study included any measurement of code quality, defect rates, or post-deployment issues
- Whether the baseline period was long enough to establish a stable pre-intervention state, or whether it captured a transient low point
- Whether the 78% retention rate is actually high (no comparison to typical tool adoption curves provided)
- Whether 'consistent across junior and senior developers' means statistically equivalent effect sizes or merely that both groups showed improvement
- Whether the three-month window is sufficient to detect long-term productivity changes or whether gains plateau/reverse after novelty wears off
- Whether the study controlled for concurrent changes (e.g., team composition, project complexity, other tools adopted)

**Self-Verification:**
- Did I overstate the problems? No—the lack of control group, quality metrics, and mechanism explanation are genuine methodological gaps, not invented issues
- Did I miss positive aspects? The study does show consistent quantitative improvements across a reasonably large sample over a defined period, which is non-trivial
- Did I conflate study quality with conclusion validity? Yes, partially—the study may be well-executed, but the conclusions drawn are disproportionate to the evidence
- Is the overclaim classification justified? Yes—the text explicitly claims industry-wide reshaping and immediate enterprise adoption based on a single-arm 3-month study
- Should this be 'correlation_vs_causation' instead? Partially—there is no control group, so causation is not established; however, the primary issue is overclaim (extrapolating beyond scope) rather than confusing correlation with causation per se

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 3.7/6 `######....`
- Uncertainty Handling: 3.0/6 `####......`
- Alternative Hypothesis Quality: 5.0/6 `########..`
- Self Monitoring Quality: 6.4/8 `########..`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 8.5/10 `########..`


## Final Verdict

**Solo run: Claude Haiku** scored **70.9/100**.

**Best per dimension:**
- Correctness: Claude Haiku (30.0/30)
- Support Strength: Claude Haiku (0.0/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (3.7/6)
- Uncertainty Handling: Claude Haiku (3.0/6)
- Alternative Hypothesis Quality: Claude Haiku (5.0/6)
- Self Monitoring Quality: Claude Haiku (6.4/8)
- Insight Depth: Claude Haiku (8.0/8)
- Mechanism Quality: Claude Haiku (1.5/10)
- Communication Efficiency: Claude Haiku (8.5/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 15.9s | 70.9/100 | 4.5 |

Failure modes observed: decorative_uncertainty, named_not_explained, unsupported_conclusion, unsupported_intermediate_step, unused_assumption.
