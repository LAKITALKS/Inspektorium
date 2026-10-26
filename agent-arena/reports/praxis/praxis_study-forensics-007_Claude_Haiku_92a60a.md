# Forensic Dossier: Study Forensics: Vitamin D supplements and long COVID

**Run ID:** `praxis_study-forensics-007_Claude_Haiku_92a60a`  
**Task:** study-forensics-007 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-07T07:47:55.290502+00:00  
**Task Family:** overclaim  
**Trap Type:** small_effect_overinterpretation  
**Ambiguity:** medium  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **40.0/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, missed_key_insight, unsupported_conclusion, wrong_answer
**Forensic flags:** 3
**Consistency findings:** 6
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 0.0/30 | 0.0/8 | 4.8/8 | 4.8/6 | 3.6/6 | 6.0/6 | 4.0/8 | 5.3/8 | 4.0/10 | 10.0/10 | **40.0/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `solid` [x] (gold: `overclaim`)
**Finding Recall:** 50%
**Matched Findings:** conclusion_exceeds_results
**Missed Findings:** decorative_uncertainty
**Extra Findings:** cautious_scope_control, none_or_minor, correlation_as_causation

## Reasoning Integrity Audit

### Claude Haiku
**Classification:** Correct and well-supported
**Load-bearing steps:** 0 / 9

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
- "solid"


## Forensic Flags

### Claude Haiku

- **[MAJOR]** `well_reasoned_wrong`: Wrong answer but structured reasoning — may have a subtle logic error
  - `final_answer`: "solid"
- **[MODERATE]** `unsupported_conclusion_claims`: 1/1 conclusion claims lack step support
  - `final_answer`: "solid"
- **[MODERATE]** `ungrounded_mechanism`: Mechanism named/described but not connected to case-specific data
  - `(mechanism analysis)`: "effect"


## Evidence Map

### Claude Haiku

**Correctness:** 0.0/30
  - (+) `final_answer`: "solid"
    _Agent's answer for correctness check_
  - Note: No match (got: solid)

**Support Strength:** 0.0/8
  - (-) `final_answer`: "solid"
    _Conclusion not supported by steps_
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 9
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[1]`: "Examined primary outcome claim: 'did not change severity of acute infection'—this is a null finding presented straightfo"
    _Most informative reasoning step_
  - Note: 9 reasoning steps
  - Note: Low step utility: 0/9 steps contribute

**Assumption Discipline:** 4.8/6
  - (+) `assumptions[0]`: "The study was a properly randomized controlled trial with appropriate blinding and allocation concealment (standard for "
    _Most substantive assumption_
  - Note: 5/5 substantive assumptions

**Uncertainty Handling:** 3.6/6
  - (+) `uncertainties[0]`: "Whether the 4-percentage-point difference is statistically significant (confidence interval not provided in summary)"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.88"
    _Stated confidence level_
  - (-) `uncertainties[3]`: "Whether there were multiple comparisons that might inflate false positive risk"
    _Listed but never addressed in reasoning_
  - Note: 4 uncertainties (4 substantive)
  - Note: 1 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 6.0/6
  - (+) `alternative_hypotheses[0]`: "Overclaim: Could argue that calling a 4-point difference a 'promising signal' overstates a modest effect, but the langua"
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 2/2 include rejection reasoning

**Self Monitoring Quality:** 4.0/8
  - (+) `self_check[1]`: "Is the 'promising signal' language actually an overclaim? No—it's qualified, and the author emphasizes need for larger t"
    _Most substantive self-verification step_
  - (-) `self_check[3]`: "Is the null primary outcome being hidden? No—it's stated clearly upfront"
    _Fluff self-check_
  - Note: 6 self-check items
  - Note: Self-check quality: 0 deep, 4 arithmetic, 2 fluff

**Mechanism Quality:** 4.0/10
  - (+) `(mechanism analysis)`: "Checked for mechanism claims: No mechanism is proposed; only outcomes are reported"
    _Mechanism description without case grounding_
  - Note: Names concept + describes mechanism (not grounded to case)

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.74, 452 words

**Insight Depth:** 5.3/8
  - (+) `(output text)`: "so i cannot assume it is the null primary outcome being hidden? no—it's stated"
    _Insight 'null primary outcome' matched (exact)_
  - (?) `(not found)`: "Missing: small absolute difference"
    _Insight 'small absolute difference' not found_
  - Note: Key insights: 2 full / 3


## Failure Analysis

### Claude Haiku

**CRITICAL:**
- **Wrong Answer** `[HIGH CONFIDENCE]`: Answer does not match expected 'overclaim'
  - `final_answer`: "solid"
  - _Impacts: correctness_

**MAJOR:**
- **Wrong Answer** `[HIGH CONFIDENCE]`: Study classification incorrect: expected 'overclaim', detected 'solid'
  - `final_answer`: "solid"
  - _Impacts: correctness_

**MODERATE:**
- **Unsupported Conclusion** `[MEDIUM CONFIDENCE]`: Final answer lacks load-bearing or supporting step grounding
  - `final_answer`: "solid"
  - _Impacts: support_strength_
- **Missed Key Insight** `[MEDIUM CONFIDENCE]`: Missed expected finding: decorative_uncertainty
  - `(task expectation)`: "Expected: decorative_uncertainty"
  - _Impacts: insight_depth_

**STYLISTIC:**
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether there were multiple comparisons that might inflate f...' is listed but not addressed
  - `uncertainties[3]`: "Whether there were multiple comparisons that might inflate false positive risk"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/10 content words)
  - `key_claims[0]`: "Primary outcome (acute severity): null finding, appropriately reported without overclaim"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/14 content words)
  - `key_claims[1]`: "Secondary outcome (lingering symptoms): 4-point difference favoring vitamin D, described as 'promisi"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/9 content words)
  - `key_claims[2]`: "Limitations are explicitly acknowledged: remote conduct and post-infection timing limit interpretati"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/8 content words)
  - `key_claims[3]`: "Call for larger trials is appropriate given the modest secondary finding"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 5 has low overlap with final answer (0/8 content words)
  - `key_claims[4]`: "No causal overclaim is made; the RCT design supports causal inference for the measured outcomes"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 4 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[3]`: "Whether there were multiple comparisons that might inflate false positive risk"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 9982ms

**Final Answer:** solid

**Confidence:** 0.88

**Assumptions:**
- The study was a properly randomized controlled trial with appropriate blinding and allocation concealment (standard for RCTs)
- The 1,747 sample size is adequate for detecting the primary outcome (acute severity)
- The 4-percentage-point difference (25% vs 21%) in lingering symptoms is the actual observed effect
- The remote conduct and post-infection timing are acknowledged limitations rather than hidden methodological flaws
- The senior author's 'promising signal' language reflects appropriate caution given the secondary nature of this finding

**Reasoning Steps:**
1. Identified the study design: RCT with 1,747 participants—a reasonably large, well-controlled design
2. Examined primary outcome claim: 'did not change severity of acute infection'—this is a null finding presented straightforwardly without overclaim
3. Examined secondary outcome: 21% vs 25% lingering symptoms at 8 weeks—a 4-percentage-point difference
4. Evaluated the language used: 'promising signal' is appropriately cautious language for a secondary outcome with modest effect size
5. Checked for causal claims: The text does not claim causation; it reports an association from an RCT (which can support causal inference for primary outcomes)
6. Assessed confounding: RCT design controls for confounders by randomization
7. Evaluated caveats: The text explicitly acknowledges limitations (remote conduct, post-infection start) and calls for larger trials
8. Checked for mechanism claims: No mechanism is proposed; only outcomes are reported
9. Assessed correlation vs causation: Not applicable—this is an RCT, not observational data

**Key Claims:**
- Primary outcome (acute severity): null finding, appropriately reported without overclaim
- Secondary outcome (lingering symptoms): 4-point difference favoring vitamin D, described as 'promising signal' with appropriate caveats
- Limitations are explicitly acknowledged: remote conduct and post-infection timing limit interpretation
- Call for larger trials is appropriate given the modest secondary finding
- No causal overclaim is made; the RCT design supports causal inference for the measured outcomes

**Alternative Hypotheses:**
- Overclaim: Could argue that calling a 4-point difference a 'promising signal' overstates a modest effect, but the language is qualified and the author explicitly notes larger trials are needed
- Confounders: Could question whether remote conduct introduced unmeasured confounding, but randomization should balance these across groups

**Uncertainties:**
- Whether the 4-percentage-point difference is statistically significant (confidence interval not provided in summary)
- Whether this was a pre-specified secondary outcome or post-hoc analysis (affects interpretation of the 'signal')
- The actual effect size and power calculation for the lingering symptoms outcome
- Whether there were multiple comparisons that might inflate false positive risk

**Self-Verification:**
- Did I assume problems that aren't stated? No—the text itself acknowledges limitations
- Is the 'promising signal' language actually an overclaim? No—it's qualified, and the author emphasizes need for larger trials
- Should I flag the secondary outcome as post-hoc analysis? The text doesn't indicate this, so I cannot assume it
- Is the null primary outcome being hidden? No—it's stated clearly upfront
- Did I miss any mechanism claims? No—only outcomes are reported
- Is there a correlation vs causation problem? No—RCT design supports causal inference

**Dimension Scores:**
- Correctness: 0.0/30 `..........`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 4.8/6 `########..`
- Uncertainty Handling: 3.6/6 `######....`
- Alternative Hypothesis Quality: 6.0/6 `##########`
- Self Monitoring Quality: 4.0/8 `#####.....`
- Insight Depth: 5.3/8 `######....`
- Mechanism Quality: 4.0/10 `####......`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Haiku** scored **40.0/100**.

**Best per dimension:**
- Correctness: Claude Haiku (0.0/30)
- Support Strength: Claude Haiku (0.0/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (4.8/6)
- Uncertainty Handling: Claude Haiku (3.6/6)
- Alternative Hypothesis Quality: Claude Haiku (6.0/6)
- Self Monitoring Quality: Claude Haiku (4.0/8)
- Insight Depth: Claude Haiku (5.3/8)
- Mechanism Quality: Claude Haiku (4.0/10)
- Communication Efficiency: Claude Haiku (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 10.0s | 40.0/100 | 4.0 |

Failure modes observed: decorative_uncertainty, missed_key_insight, unsupported_conclusion, wrong_answer.
