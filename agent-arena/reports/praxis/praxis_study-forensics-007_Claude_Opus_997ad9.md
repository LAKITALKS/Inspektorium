# Forensic Dossier: Study Forensics: Vitamin D supplements and long COVID

**Run ID:** `praxis_study-forensics-007_Claude_Opus_997ad9`  
**Task:** study-forensics-007 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-07T07:48:11.800753+00:00  
**Task Family:** overclaim  
**Trap Type:** small_effect_overinterpretation  
**Ambiguity:** medium  

## Executive Summary

**Agents tested:** Claude Opus
**Winner:** Claude Opus — **40.0/100** (margin: 0.0)
**Failure modes:** named_not_explained, unsupported_conclusion, wrong_answer
**Forensic flags:** 3
**Consistency findings:** 5
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Opus | 0.0/30 | 0.0/8 | 4.8/8 | 3.9/6 | 3.9/6 | 6.0/6 | 3.6/8 | 8.0/8 | 1.5/10 | 10.0/10 | **40.0/100** |

## Study Forensics Audit

### Claude Opus

**Classification:** `solid` [x] (gold: `overclaim`)
**Finding Recall:** 100%
**Matched Findings:** conclusion_exceeds_results, decorative_uncertainty
**Extra Findings:** cautious_scope_control, none_or_minor, correlation_as_causation

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
- "solid"


## Forensic Flags

### Claude Opus

- **[MAJOR]** `well_reasoned_wrong`: Wrong answer but structured reasoning — may have a subtle logic error
  - `final_answer`: "solid"
- **[MODERATE]** `unsupported_conclusion_claims`: 1/1 conclusion claims lack step support
  - `final_answer`: "solid"
- **[MODERATE]** `ungrounded_mechanism`: Mechanism named/described but not connected to case-specific data
  - `(mechanism analysis)`: "effect"


## Evidence Map

### Claude Opus

**Correctness:** 0.0/30
  - (+) `final_answer`: "solid"
    _Agent's answer for correctness check_
  - Note: No match (got: solid)

**Support Strength:** 0.0/8
  - (-) `final_answer`: "solid"
    _Conclusion not supported by steps_
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 6
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[3]`: "Fourth, I evaluated how this finding was presented: senior author called it a 'promising signal' not a definitive result"
    _Most informative reasoning step_
  - Note: 6 reasoning steps
  - Note: Low step utility: 0/6 steps contribute

**Assumption Discipline:** 3.9/6
  - (+) `assumptions[2]`: "The 21% vs 25% difference in lingering symptoms was observed but not claimed as definitive"
    _Most substantive assumption_
  - Note: 4/4 substantive assumptions

**Uncertainty Handling:** 3.9/6
  - (+) `uncertainties[1]`: "Whether lingering symptoms was a pre-specified secondary outcome or post-hoc analysis"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.9"
    _Stated confidence level_
  - Note: 3 uncertainties (3 substantive)
  - Note: Confidence 0.9

**Alternative Hypothesis Quality:** 6.0/6
  - (+) `alternative_hypotheses[1]`: "decorative uncertainty - but the uncertainty appears genuine given explicit mention of study limitations and need for la"
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 2/2 include rejection reasoning

**Self Monitoring Quality:** 3.6/8
  - (+) `self_check[1]`: "Is 'promising signal' an overclaim? No, it's appropriate for a secondary finding that needs replication"
    _Most substantive self-verification step_
  - (-) `self_check[0]`: "Did I look for problems that aren't there? The text is careful about claims"
    _Fluff self-check_
  - Note: 4 self-check items
  - Note: Self-check quality: 0 deep, 3 arithmetic, 1 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.70, 293 words

**Insight Depth:** 5.3/8
  - (+) `(output text)`: "e given the secondary outcome decorative uncertainty - but the uncertainty appears"
    _Insight 'decorative uncertainty' matched (exact)_
  - (?) `(not found)`: "Missing: small absolute difference"
    _Insight 'small absolute difference' not found_
  - Note: Key insights: 2 full / 3


## Failure Analysis

### Claude Opus

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
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Names the phenomenon but does not explain the causal mechanism
  - `final_answer`: "solid"
  - _Impacts: mechanism_quality_
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Named concept(s) ['effect'] but mechanism not described
  - _Impacts: mechanism_quality, insight_depth_


## Consistency & Grounding Audit

### Claude Opus

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/7 content words)
  - `key_claims[0]`: "The study appropriately reports a null result for the primary outcome"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/6 content words)
  - `key_claims[1]`: "The secondary finding is presented with appropriate uncertainty"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/4 content words)
  - `key_claims[2]`: "Study limitations are explicitly acknowledged"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/4 content words)
  - `key_claims[3]`: "No overclaiming of results is evident in the text"
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "solid"


## Agent Profiles

### Claude Opus (claude-opus-4-20250514)
**Parse OK:** True | **Latency:** 16503ms

**Final Answer:** solid

**Confidence:** 0.9

**Assumptions:**
- This was an RCT with 1,747 participants
- The study measured both acute infection severity and lingering symptoms at 8 weeks
- The 21% vs 25% difference in lingering symptoms was observed but not claimed as definitive
- The study was conducted remotely with supplementation starting after infection onset

**Reasoning Steps:**
1. First, I identified the study design: RCT with substantial sample size (1,747)
2. Second, I noted the primary finding: no effect on acute infection severity
3. Third, I examined the secondary finding: 21% vs 25% difference in lingering symptoms
4. Fourth, I evaluated how this finding was presented: senior author called it a 'promising signal' not a definitive result
5. Fifth, I checked for appropriate caveats: the text explicitly mentions need for larger trials and study limitations
6. Sixth, I verified no causal claims were made beyond what the RCT design supports

**Key Claims:**
- The study appropriately reports a null result for the primary outcome
- The secondary finding is presented with appropriate uncertainty
- Study limitations are explicitly acknowledged
- No overclaiming of results is evident in the text

**Alternative Hypotheses:**
- overclaim - but the 'promising signal' language is appropriately tentative given the secondary outcome
- decorative uncertainty - but the uncertainty appears genuine given explicit mention of study limitations and need for larger trials

**Uncertainties:**
- Whether the 21% vs 25% difference was statistically significant is not stated
- Whether lingering symptoms was a pre-specified secondary outcome or post-hoc analysis
- The exact nature of the remote conduct and how it might affect results

**Self-Verification:**
- Did I look for problems that aren't there? The text is careful about claims
- Is 'promising signal' an overclaim? No, it's appropriate for a secondary finding that needs replication
- Are the limitations real or decorative? They appear substantive (remote conduct, post-infection start)
- Did I miss any red flags? No causal claims beyond RCT warrant, no mechanism speculation

**Dimension Scores:**
- Correctness: 0.0/30 `..........`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 3.9/6 `######....`
- Uncertainty Handling: 3.9/6 `######....`
- Alternative Hypothesis Quality: 6.0/6 `##########`
- Self Monitoring Quality: 3.6/8 `####......`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Opus** scored **40.0/100**.

**Best per dimension:**
- Correctness: Claude Opus (0.0/30)
- Support Strength: Claude Opus (0.0/8)
- Structural Reasoning: Claude Opus (4.8/8)
- Assumption Discipline: Claude Opus (3.9/6)
- Uncertainty Handling: Claude Opus (3.9/6)
- Alternative Hypothesis Quality: Claude Opus (6.0/6)
- Self Monitoring Quality: Claude Opus (3.6/8)
- Insight Depth: Claude Opus (8.0/8)
- Mechanism Quality: Claude Opus (1.5/10)
- Communication Efficiency: Claude Opus (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Opus | 16.5s | 40.0/100 | 2.4 |

Failure modes observed: named_not_explained, unsupported_conclusion, wrong_answer.
