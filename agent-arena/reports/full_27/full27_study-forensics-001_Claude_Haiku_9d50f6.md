# Forensic Dossier: Study Forensics: Social media use and well-being

**Run ID:** `full27_study-forensics-001_Claude_Haiku_9d50f6`  
**Task:** study-forensics-001 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T08:10:23.241276+00:00  
**Task Family:** solid  
**Trap Type:** overflagging_solid_study  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **69.4/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, missed_key_insight, named_not_explained, unsupported_conclusion, unsupported_intermediate_step, unused_assumption
**Forensic flags:** 5
**Consistency findings:** 14
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 30.0/30 | 0.0/8 | 4.8/8 | 3.2/6 | 3.0/6 | 4.5/6 | 4.4/8 | 8.0/8 | 1.5/10 | 10.0/10 | **69.4/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `solid` [+] (gold: `solid`)
**Finding Recall:** 67%
**Matched Findings:** cautious_scope_control, none_or_minor
**Missed Findings:** evidence_matches_claim
**Extra Findings:** conclusion_exceeds_results, unsupported_generalization, decorative_uncertainty, mechanism_not_demonstrated, correlation_as_causation

## Reasoning Integrity Audit

### Claude Haiku
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 7

## Mechanism Analysis

### Claude Haiku
| Aspect | Status |
|--------|--------|
| Concept named | :white_check_mark: bias |
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
  - `(mechanism analysis)`: "bias"
- **[MINOR]** `study_forensics_overflagging`: Agent raised extra findings in solid case: conclusion_exceeds_results, unsupported_generalization, decorative_uncertainty, mechanism_not_demonstrated, correlation_as_causation


## Evidence Map

### Claude Haiku

**Correctness:** 30.0/30
  - (+) `final_answer`: "solid"
    _Agent's answer for correctness check_
  - Note: Exact match

**Support Strength:** 0.0/8
  - (-) `final_answer`: "solid"
    _Conclusion not supported by steps_
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 7
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[0]`: "Identified study design: randomized controlled trial with objective usage monitoring—this is a strong design for causal "
    _Most informative reasoning step_
  - Note: 7 reasoning steps
  - Note: Low step utility: 0/7 steps contribute

**Assumption Discipline:** 3.2/6
  - (+) `assumptions[5]`: "The reported 'significant declines' refer to statistical significance with appropriate effect sizes"
    _Most substantive assumption_
  - (-) `assumptions[3]`: "The three-week timeframe is sufficient to detect meaningful changes in these outcomes"
    _Declared but unused in reasoning_
  - (-) `assumptions[4]`: "Participants complied with their assigned conditions"
    _Declared but unused in reasoning_
  - Note: 6/6 substantive assumptions
  - Note: Many assumptions (6)

**Uncertainty Handling:** 3.0/6
  - (+) `uncertainties[0]`: "Whether baseline depression/loneliness levels were balanced between groups (not stated in summary)"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.82"
    _Stated confidence level_
  - (-) `uncertainties[1]`: "Whether the 10-minute limit was chosen based on prior evidence or was arbitrary"
    _Listed but never addressed in reasoning_
  - (-) `uncertainties[2]`: "Whether there were differential dropout rates or compliance issues between groups"
    _Listed but never addressed in reasoning_
  - Note: 5 uncertainties (5 substantive)
  - Note: 4 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 4.5/6
  - (+) `alternative_hypotheses[0]`: "Overclaim: if the text had claimed effects generalize to all populations or all social media platforms"
    _Most substantive alternative hypothesis_
  - Note: 3 alternative hypotheses considered
  - Note: 3/3 genuinely diverse alternatives

**Self Monitoring Quality:** 4.4/8
  - (+) `self_check[3]`: "Could confounding explain the results? Unlikely given randomization, though baseline balance not confirmed in summary"
    _Most substantive self-verification step_
  - (-) `self_check[1]`: "Is random assignment actually present? Yes, explicitly stated"
    _Fluff self-check_
  - Note: 5 self-check items
  - Note: Self-check quality: 0 deep, 4 arithmetic, 1 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.77, 365 words

**Insight Depth:** 8.0/8
  - (+) `(output text)`: "upporting causality evaluated scope limitations: authors explicitly acknowle"
    _Insight 'scope limitation' matched (exact)_
  - Note: Key insights: 2 full / 2


## Failure Analysis

### Claude Haiku

**MODERATE:**
- **Unsupported Conclusion** `[MEDIUM CONFIDENCE]`: Final answer lacks load-bearing or supporting step grounding
  - `final_answer`: "solid"
  - _Impacts: support_strength_
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Names the phenomenon but does not explain the causal mechanism
  - `final_answer`: "solid"
  - _Impacts: mechanism_quality_
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Named concept(s) ['bias'] but mechanism not described
  - _Impacts: mechanism_quality, insight_depth_
- **Unsupported Intermediate Step** `[MEDIUM CONFIDENCE]`: No reasoning step is load-bearing — final answer lacks traceable derivation
  - `final_answer`: "solid"
  - _Impacts: support_strength, structural_reasoning_
- **Missed Key Insight** `[MEDIUM CONFIDENCE]`: Missed expected finding: evidence_matches_claim
  - `(task expectation)`: "Expected: evidence_matches_claim"
  - _Impacts: insight_depth_

**STYLISTIC:**
- **Unused Assumption** `[HEURISTIC]`: Assumption 'The three-week timeframe is sufficient to detect meaningful ...' is declared but not referenced in reasoning
  - `assumptions[3]`: "The three-week timeframe is sufficient to detect meaningful changes in these outcomes"
  - _Impacts: assumption_discipline_
- **Unused Assumption** `[HEURISTIC]`: Assumption 'Participants complied with their assigned conditions...' is declared but not referenced in reasoning
  - `assumptions[4]`: "Participants complied with their assigned conditions"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether the 10-minute limit was chosen based on prior eviden...' is listed but not addressed
  - `uncertainties[1]`: "Whether the 10-minute limit was chosen based on prior evidence or was arbitrary"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether there were differential dropout rates or compliance ...' is listed but not addressed
  - `uncertainties[2]`: "Whether there were differential dropout rates or compliance issues between groups"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'The magnitude of effect sizes (described as 'significant' bu...' is listed but not addressed
  - `uncertainties[3]`: "The magnitude of effect sizes (described as 'significant' but no numbers provided)"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether multiple comparisons were corrected for...' is listed but not addressed
  - `uncertainties[4]`: "Whether multiple comparisons were corrected for"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/8 content words)
  - `key_claims[0]`: "Random assignment supports causal inference: restriction → reduced depression/loneliness"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/8 content words)
  - `key_claims[1]`: "Authors appropriately limit claims to college students and three platforms"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/4 content words)
  - `key_claims[2]`: "No unsupported mechanism claims are made"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/10 content words)
  - `key_claims[3]`: "Objective usage data (screenshots) strengthens the study by reducing self-report bias on the exposur"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 5 has low overlap with final answer (0/7 content words)
  - `key_claims[4]`: "The caveats are substantive and address real limitations rather than performative"
- **[WARN]** `[HEURISTIC]` `unused_assumption`: Assumption 5 appears unused in reasoning or answer
  - `assumptions[4]`: "Participants complied with their assigned conditions"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 2 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[1]`: "Whether the 10-minute limit was chosen based on prior evidence or was arbitrary"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 3 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[2]`: "Whether there were differential dropout rates or compliance issues between groups"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 4 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[3]`: "The magnitude of effect sizes (described as 'significant' but no numbers provided)"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 5 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[4]`: "Whether multiple comparisons were corrected for"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "Overclaim: if the text had claimed effects generalize to all populations or all social media platfor"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 2 is stated without rejection reasoning
  - `alternative_hypotheses[1]`: "Correlation_vs_causation: if the study were observational rather than randomized"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 3 is stated without rejection reasoning
  - `alternative_hypotheses[2]`: "Mechanism_vs_evidence: if authors claimed specific psychological mechanisms without evidence"
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "solid"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 9278ms

**Final Answer:** solid

**Confidence:** 0.82

**Assumptions:**
- The random assignment was properly executed and groups were balanced at baseline
- The objective usage data (phone screenshots) reliably captured actual social media use
- Depression and loneliness were measured with validated instruments
- The three-week timeframe is sufficient to detect meaningful changes in these outcomes
- Participants complied with their assigned conditions
- The reported 'significant declines' refer to statistical significance with appropriate effect sizes

**Reasoning Steps:**
1. Identified study design: randomized controlled trial with objective usage monitoring—this is a strong design for causal inference
2. Checked for causal claims: the text states students 'who restricted' use 'reported' declines, with random assignment supporting causality
3. Evaluated scope limitations: authors explicitly acknowledge college-only sample and three specific platforms
4. Assessed generalization claims: the authors appropriately caution against overgeneralization rather than claiming broad applicability
5. Checked for confounders: random assignment mitigates selection bias; no obvious unmeasured confounders mentioned as unaddressed
6. Evaluated mechanism claims: the text reports outcomes (depression, loneliness) without speculating about mechanisms—appropriately restrained
7. Assessed uncertainty language: caveats are substantive (not decorative) and directly address real limitations

**Key Claims:**
- Random assignment supports causal inference: restriction → reduced depression/loneliness
- Authors appropriately limit claims to college students and three platforms
- No unsupported mechanism claims are made
- Objective usage data (screenshots) strengthens the study by reducing self-report bias on the exposure
- The caveats are substantive and address real limitations rather than performative

**Alternative Hypotheses:**
- Overclaim: if the text had claimed effects generalize to all populations or all social media platforms
- Correlation_vs_causation: if the study were observational rather than randomized
- Mechanism_vs_evidence: if authors claimed specific psychological mechanisms without evidence

**Uncertainties:**
- Whether baseline depression/loneliness levels were balanced between groups (not stated in summary)
- Whether the 10-minute limit was chosen based on prior evidence or was arbitrary
- Whether there were differential dropout rates or compliance issues between groups
- The magnitude of effect sizes (described as 'significant' but no numbers provided)
- Whether multiple comparisons were corrected for

**Self-Verification:**
- Did I assume problems that aren't stated? No—I focused on what the text says
- Is random assignment actually present? Yes, explicitly stated
- Are the caveats genuine limitations or decorative? Genuine—they identify real scope constraints
- Could confounding explain the results? Unlikely given randomization, though baseline balance not confirmed in summary
- Did I miss any overclaims? No—the text is appropriately cautious about generalization

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 3.2/6 `#####.....`
- Uncertainty Handling: 3.0/6 `####......`
- Alternative Hypothesis Quality: 4.5/6 `#######...`
- Self Monitoring Quality: 4.4/8 `#####.....`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Haiku** scored **69.4/100**.

**Best per dimension:**
- Correctness: Claude Haiku (30.0/30)
- Support Strength: Claude Haiku (0.0/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (3.2/6)
- Uncertainty Handling: Claude Haiku (3.0/6)
- Alternative Hypothesis Quality: Claude Haiku (4.5/6)
- Self Monitoring Quality: Claude Haiku (4.4/8)
- Insight Depth: Claude Haiku (8.0/8)
- Mechanism Quality: Claude Haiku (1.5/10)
- Communication Efficiency: Claude Haiku (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 9.3s | 69.4/100 | 7.5 |

Failure modes observed: decorative_uncertainty, missed_key_insight, named_not_explained, unsupported_conclusion, unsupported_intermediate_step, unused_assumption.
