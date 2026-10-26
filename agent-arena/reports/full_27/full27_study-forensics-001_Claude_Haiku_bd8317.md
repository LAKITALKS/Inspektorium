# Forensic Dossier: Study Forensics: Social media use and well-being

**Run ID:** `full27_study-forensics-001_Claude_Haiku_bd8317`  
**Task:** study-forensics-001 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T16:54:52.645258+00:00  
**Task Family:** solid  
**Trap Type:** overflagging_solid_study  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **67.7/100** (margin: 0.0)
**Failure modes:** missed_key_insight, named_not_explained, unsupported_conclusion, unsupported_intermediate_step, unused_assumption
**Forensic flags:** 5
**Consistency findings:** 5
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 30.0/30 | 0.0/8 | 4.8/8 | 3.2/6 | 3.9/6 | 6.0/6 | 4.4/8 | 5.3/8 | 1.5/10 | 8.5/10 | **67.7/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `solid` [+] (gold: `solid`)
**Finding Recall:** 67%
**Matched Findings:** cautious_scope_control, none_or_minor
**Missed Findings:** evidence_matches_claim
**Extra Findings:** conclusion_exceeds_results, unsupported_generalization, correlation_as_causation

## Reasoning Integrity Audit

### Claude Haiku
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 9

## Mechanism Analysis

### Claude Haiku
| Aspect | Status |
|--------|--------|
| Concept named | :white_check_mark: effect |
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
- "solid"


## Forensic Flags

### Claude Haiku

- **[MODERATE]** `weak_mechanism`: Correct answer but weak mechanism explanation — answer may not generalize
  - `final_answer`: "solid"
- **[MAJOR]** `unsupported_leap`: Correct answer with weak support chain — final answer may be an unsupported leap
- **[MODERATE]** `unsupported_conclusion_claims`: 1/1 conclusion claims lack step support
  - `final_answer`: "solid"
- **[MODERATE]** `ungrounded_mechanism`: Mechanism named/described but not connected to case-specific data
  - `(mechanism analysis)`: "effect"
- **[MINOR]** `study_forensics_overflagging`: Agent raised extra findings in solid case: conclusion_exceeds_results, unsupported_generalization, correlation_as_causation


## Evidence Map

### Claude Haiku

**Correctness:** 30.0/30
  - (+) `final_answer`: "solid"
    _Agent's answer for correctness check_
  - Note: Exact match

**Support Strength:** 0.0/8
  - (-) `final_answer`: "solid"
    _Conclusion not supported by steps_
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 9
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[5]`: "Assessed appropriate caveats: The authors explicitly acknowledge limitations (college students only, three platforms onl"
    _Most informative reasoning step_
  - Note: 9 reasoning steps
  - Note: Low step utility: 0/9 steps contribute

**Assumption Discipline:** 3.2/6
  - (+) `assumptions[5]`: "The reported 'significant declines' refer to statistical significance with appropriate multiple-comparison corrections"
    _Most substantive assumption_
  - (-) `assumptions[2]`: "The three-week timeframe is sufficient to detect meaningful changes in these outcomes"
    _Declared but unused in reasoning_
  - (-) `assumptions[5]`: "The reported 'significant declines' refer to statistical significance with appropriate multiple-comparison corrections"
    _Declared but unused in reasoning_
  - Note: 6/6 substantive assumptions
  - Note: Many assumptions (6)

**Uncertainty Handling:** 3.9/6
  - (+) `uncertainties[1]`: "Whether the control group truly continued 'usual' use or whether awareness of the study altered their behavior (Hawthorn"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.88"
    _Stated confidence level_
  - Note: 4 uncertainties (4 substantive)
  - Note: Confidence 0.88

**Alternative Hypothesis Quality:** 6.0/6
  - (+) `alternative_hypotheses[0]`: "Could classify as 'limited_human' if the three-week duration is considered too short to establish clinical significance "
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 2/2 include rejection reasoning

**Self Monitoring Quality:** 4.4/8
  - (+) `self_check[1]`: "Did I miss a mechanism vs. evidence problem? No — the study is human RCT evidence, and the conclusion is about human out"
    _Most substantive self-verification step_
  - (-) `self_check[3]`: "Did I miss an overclaim? No — the authors explicitly limit generalization."
    _Fluff self-check_
  - Note: 5 self-check items
  - Note: Self-check quality: 0 deep, 4 arithmetic, 1 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 8.5/10
  - Note: Signal density: 0.71, 526 words

**Insight Depth:** 4.0/8
  - (?) `(not found)`: "Missing: scope limitation"
    _Insight 'scope limitation' not found_
  - Note: Key insights: 1 full / 2


## Failure Analysis

### Claude Haiku

**MODERATE:**
- **Unsupported Conclusion** `[MEDIUM CONFIDENCE]`: Final answer lacks load-bearing or supporting step grounding
  - `final_answer`: "solid"
  - _Impacts: support_strength_
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Names the phenomenon but does not explain the causal mechanism
  - `final_answer`: "solid"
  - _Impacts: mechanism_quality_
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Named concept(s) ['effect'] but mechanism not described
  - _Impacts: mechanism_quality, insight_depth_
- **Unsupported Intermediate Step** `[MEDIUM CONFIDENCE]`: No reasoning step is load-bearing — final answer lacks traceable derivation
  - `final_answer`: "solid"
  - _Impacts: support_strength, structural_reasoning_
- **Missed Key Insight** `[MEDIUM CONFIDENCE]`: Missed expected finding: evidence_matches_claim
  - `(task expectation)`: "Expected: evidence_matches_claim"
  - _Impacts: insight_depth_

**STYLISTIC:**
- **Unused Assumption** `[HEURISTIC]`: Assumption 'The three-week timeframe is sufficient to detect meaningful ...' is declared but not referenced in reasoning
  - `assumptions[2]`: "The three-week timeframe is sufficient to detect meaningful changes in these outcomes"
  - _Impacts: assumption_discipline_
- **Unused Assumption** `[HEURISTIC]`: Assumption 'The reported 'significant declines' refer to statistical sig...' is declared but not referenced in reasoning
  - `assumptions[5]`: "The reported 'significant declines' refer to statistical significance with appropriate multiple-comp"
  - _Impacts: assumption_discipline_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/6 content words)
  - `key_claims[0]`: "This is a well-designed RCT with appropriate scope and honest caveats."
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/12 content words)
  - `key_claims[1]`: "The conclusion (reduced depression/loneliness in college students restricting social-media use) stay"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/11 content words)
  - `key_claims[2]`: "The authors appropriately acknowledge that results may not generalize beyond college students and th"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/5 content words)
  - `key_claims[3]`: "No unsupported mechanistic or population-level claims are made."
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "solid"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 12963ms

**Final Answer:** solid

**Confidence:** 0.88

**Assumptions:**
- The randomization was properly executed and groups were balanced at baseline
- Depression and loneliness were measured with validated instruments
- The three-week timeframe is sufficient to detect meaningful changes in these outcomes
- Objective usage data from screenshots reliably captured compliance with the intervention
- Participants were not differentially lost to follow-up between groups
- The reported 'significant declines' refer to statistical significance with appropriate multiple-comparison corrections

**Reasoning Steps:**
1. Identified study design: randomized controlled trial (RCT) with 143 college students
2. Identified evidence tier: This is a human RCT with objective behavioral measurement (phone screenshots) and validated psychological outcomes (depression, loneliness). This is clinical_human evidence.
3. Identified conclusion tier: The text reports therapeutic outcomes (reduced depression and loneliness) in the studied population (college students on three platforms).
4. Assessed bridge: The conclusion stays within the evidence tier — the study measured college students, and the conclusion is about college students. No extrapolation to other populations is claimed in the main finding.
5. Evaluated causal claim: The randomized design supports a causal inference about the effect of social-media restriction on depression/loneliness within this population.
6. Assessed appropriate caveats: The authors explicitly acknowledge limitations (college students only, three platforms only, generalization uncertain). These caveats are proportionate and honest.
7. Checked for overclaim: The text does not claim effects on other populations, age groups, or platforms. The main claim is narrowly scoped to the studied sample.
8. Checked for mechanism vs. evidence: No mechanistic claims are made. The study reports outcomes, not proposed biological pathways.
9. Checked for correlation vs. causation: The randomized design rules out this concern for the primary finding.

**Key Claims:**
- This is a well-designed RCT with appropriate scope and honest caveats.
- The conclusion (reduced depression/loneliness in college students restricting social-media use) stays within the evidence tier.
- The authors appropriately acknowledge that results may not generalize beyond college students and the three platforms studied.
- No unsupported mechanistic or population-level claims are made.

**Alternative Hypotheses:**
- Could classify as 'limited_human' if the three-week duration is considered too short to establish clinical significance — but the text reports 'significant declines,' implying statistical significance was achieved, and three weeks is a reasonable timeframe for mood changes.
- Could flag as 'overclaim' if the text implied benefits for all social-media users — but it does not; it explicitly limits claims to college students and the three platforms studied.

**Uncertainties:**
- Whether 'significant' refers to statistical or clinical significance (the text does not specify effect sizes)
- Whether the control group truly continued 'usual' use or whether awareness of the study altered their behavior (Hawthorne effect)
- Whether depression and loneliness were the only outcomes measured, or whether selective reporting of positive results occurred
- The specific validated instruments used for depression and loneliness measurement (not stated in the summary)

**Self-Verification:**
- Did I overread the text? No — the text makes only the claims stated, with appropriate hedging.
- Did I miss a mechanism vs. evidence problem? No — the study is human RCT evidence, and the conclusion is about human outcomes in the same population.
- Did I miss a correlation vs. causation problem? No — randomization supports causality.
- Did I miss an overclaim? No — the authors explicitly limit generalization.
- Is this actually a solid study? Yes — RCT design, objective measurement, validated outcomes, appropriate caveats.

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 3.2/6 `#####.....`
- Uncertainty Handling: 3.9/6 `######....`
- Alternative Hypothesis Quality: 6.0/6 `##########`
- Self Monitoring Quality: 4.4/8 `#####.....`
- Insight Depth: 5.3/8 `######....`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 8.5/10 `########..`


## Final Verdict

**Solo run: Claude Haiku** scored **67.7/100**.

**Best per dimension:**
- Correctness: Claude Haiku (30.0/30)
- Support Strength: Claude Haiku (0.0/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (3.2/6)
- Uncertainty Handling: Claude Haiku (3.9/6)
- Alternative Hypothesis Quality: Claude Haiku (6.0/6)
- Self Monitoring Quality: Claude Haiku (4.4/8)
- Insight Depth: Claude Haiku (5.3/8)
- Mechanism Quality: Claude Haiku (1.5/10)
- Communication Efficiency: Claude Haiku (8.5/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 13.0s | 67.7/100 | 5.2 |

Failure modes observed: missed_key_insight, named_not_explained, unsupported_conclusion, unsupported_intermediate_step, unused_assumption.
