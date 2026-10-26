# Forensic Dossier: Study Forensics: AI tutors show moderate gains compared to human tutors

**Run ID:** `full27_study-forensics-035_Claude_Sonnet_b6226b`  
**Task:** study-forensics-035 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T17:08:47.941705+00:00  
**Task Family:** solid  
**Trap Type:** borderline_solid_with_caveats  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Sonnet
**Winner:** Claude Sonnet — **63.6/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, missed_key_insight, named_not_explained, unsupported_conclusion, unsupported_intermediate_step, unused_assumption
**Forensic flags:** 5
**Consistency findings:** 10
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Sonnet | 30.0/30 | 0.0/8 | 4.8/8 | 4.3/6 | 3.3/6 | 4.5/6 | 1.2/8 | 4.0/8 | 1.5/10 | 10.0/10 | **63.6/100** |

## Study Forensics Audit

### Claude Sonnet

**Classification:** `solid` [+] (gold: `solid`)
**Finding Recall:** 50%
**Matched Findings:** cautious_scope_control
**Missed Findings:** evidence_matches_claim
**Extra Findings:** none_or_minor, conclusion_exceeds_results, mechanism_not_demonstrated, correlation_as_causation

## Reasoning Integrity Audit

### Claude Sonnet
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 8

## Mechanism Analysis

### Claude Sonnet
| Aspect | Status |
|--------|--------|
| Concept named | :white_check_mark: effect |
| Mechanism described | :x: (0 sentence(s)) |
| Grounded to case | :x: (0 sentence(s)) |

**Missing:** mechanism not described, mechanism not grounded to case data

## Grounding Audit

### Claude Sonnet
Conclusion claims: 1
- Direct support: 0
- Indirect support: 0
- Unsupported: 1
- Contradicted: 0

**Unsupported claims:**
- "solid"


## Forensic Flags

### Claude Sonnet

- **[MODERATE]** `weak_mechanism`: Correct answer but weak mechanism explanation — answer may not generalize
  - `final_answer`: "solid"
- **[MAJOR]** `unsupported_leap`: Correct answer with weak support chain — final answer may be an unsupported leap
- **[MODERATE]** `unsupported_conclusion_claims`: 1/1 conclusion claims lack step support
  - `final_answer`: "solid"
- **[MODERATE]** `ungrounded_mechanism`: Mechanism named/described but not connected to case-specific data
  - `(mechanism analysis)`: "effect"
- **[MINOR]** `study_forensics_overflagging`: Agent raised extra findings in solid case: none_or_minor, conclusion_exceeds_results, mechanism_not_demonstrated, correlation_as_causation


## Evidence Map

### Claude Sonnet

**Correctness:** 30.0/30
  - (+) `final_answer`: "solid"
    _Agent's answer for correctness check_
  - Note: Exact match

**Support Strength:** 0.0/8
  - (-) `final_answer`: "solid"
    _Conclusion not supported by steps_
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 8
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[1]`: "Evidence tier: Clinical human - actual students using these systems in educational contexts"
    _Most informative reasoning step_
  - Note: 8 reasoning steps
  - Note: Low step utility: 0/8 steps contribute

**Assumption Discipline:** 4.3/6
  - (+) `assumptions[3]`: "The studies were conducted with sufficient sample sizes for meaningful results"
    _Most substantive assumption_
  - (-) `assumptions[2]`: "The comparison groups were properly controlled"
    _Declared but unused in reasoning_
  - Note: 4/4 substantive assumptions
  - Note: 1 unused assumption(s)

**Uncertainty Handling:** 3.3/6
  - (+) `uncertainties[1]`: "Statistical significance of reported differences not mentioned"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.82"
    _Stated confidence level_
  - (-) `uncertainties[1]`: "Statistical significance of reported differences not mentioned"
    _Listed but never addressed in reasoning_
  - (-) `uncertainties[3]`: "Whether randomization was used in group assignment"
    _Listed but never addressed in reasoning_
  - Note: 4 uncertainties (4 substantive)
  - Note: 2 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 4.5/6
  - (+) `alternative_hypotheses[0]`: "Could be mechanism_vs_evidence if these were pilot studies with very small samples"
    _Most substantive alternative hypothesis_
  - Note: 3 alternative hypotheses considered
  - Note: 3/3 genuinely diverse alternatives

**Self Monitoring Quality:** 1.2/8
  - (+) `self_check[2]`: "Checked for overclaims - the modest framing and specific numbers suggest appropriate restraint"
    _Most substantive self-verification step_
  - (-) `self_check[0]`: "Verified this involves human students, not just theoretical or animal models"
    _Fluff self-check_
  - Note: 4 self-check items
  - Note: Self-check quality: 0 deep, 1 arithmetic, 3 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.77, 263 words

**Insight Depth:** 4.0/8
  - (+) `(output text)`: "ors appropriately frame ai as complementary rather than replacement techn"
    _Insight 'complementary' matched (exact)_
  - (?) `(not found)`: "Missing: moderate effect"
    _Insight 'moderate effect' not found_
  - Note: Key insights: 1 full / 2


## Failure Analysis

### Claude Sonnet

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
- **Unused Assumption** `[HEURISTIC]`: Assumption 'The comparison groups were properly controlled...' is declared but not referenced in reasoning
  - `assumptions[2]`: "The comparison groups were properly controlled"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Statistical significance of reported differences not mention...' is listed but not addressed
  - `uncertainties[1]`: "Statistical significance of reported differences not mentioned"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether randomization was used in group assignment...' is listed but not addressed
  - `uncertainties[3]`: "Whether randomization was used in group assignment"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Sonnet

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/7 content words)
  - `key_claims[0]`: "Two independent studies provide human evidence for AI tutoring effectiveness"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/7 content words)
  - `key_claims[1]`: "Results show modest but measurable improvements in educational outcomes"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/7 content words)
  - `key_claims[2]`: "Authors appropriately frame AI as complementary rather than replacement technology"
- **[WARN]** `[HEURISTIC]` `unused_assumption`: Assumption 3 appears unused in reasoning or answer
  - `assumptions[2]`: "The comparison groups were properly controlled"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 2 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[1]`: "Statistical significance of reported differences not mentioned"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 4 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[3]`: "Whether randomization was used in group assignment"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "Could be mechanism_vs_evidence if these were pilot studies with very small samples"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 2 is stated without rejection reasoning
  - `alternative_hypotheses[1]`: "Could be overclaim if the numerical differences weren't statistically significant"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 3 is stated without rejection reasoning
  - `alternative_hypotheses[2]`: "Could have confounding issues if student populations weren't matched"
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "solid"


## Agent Profiles

### Claude Sonnet (claude-sonnet-4-20250514)
**Parse OK:** True | **Latency:** 12984ms

**Final Answer:** solid

**Confidence:** 0.82

**Assumptions:**
- The studies involved actual students in educational settings
- Success rates and mastery improvements were measured with appropriate metrics
- The comparison groups were properly controlled
- The studies were conducted with sufficient sample sizes for meaningful results

**Reasoning Steps:**
1. Identified two independent human studies comparing AI learning support with human tutoring
2. Evidence tier: Clinical human - actual students using these systems in educational contexts
3. Conclusion tier: Same as evidence - conclusions about educational effectiveness for students
4. No bridge step exists - conclusions match the evidence level
5. Claims are appropriately modest: AI 'complements' rather than 'replaces' human tutoring
6. Specific numerical results provided (66% vs 61% vs 56%, 76.4% confirmation rate, 4-9 point improvements)
7. No causal overclaims - results presented as comparative performance data
8. No obvious confounders ignored - studies appear to control for tutoring method

**Key Claims:**
- Two independent studies provide human evidence for AI tutoring effectiveness
- Results show modest but measurable improvements in educational outcomes
- Authors appropriately frame AI as complementary rather than replacement technology

**Alternative Hypotheses:**
- Could be mechanism_vs_evidence if these were pilot studies with very small samples
- Could be overclaim if the numerical differences weren't statistically significant
- Could have confounding issues if student populations weren't matched

**Uncertainties:**
- Sample sizes of the studies not specified
- Statistical significance of reported differences not mentioned
- Duration and scope of the studies unclear
- Whether randomization was used in group assignment

**Self-Verification:**
- Verified this involves human students, not just theoretical or animal models
- Confirmed conclusions stay within the evidence tier
- Checked for overclaims - the modest framing and specific numbers suggest appropriate restraint
- Looked for obvious red flags - none present in the text as written

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 4.3/6 `#######...`
- Uncertainty Handling: 3.3/6 `#####.....`
- Alternative Hypothesis Quality: 4.5/6 `#######...`
- Self Monitoring Quality: 1.2/8 `#.........`
- Insight Depth: 4.0/8 `#####.....`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Sonnet** scored **63.6/100**.

**Best per dimension:**
- Correctness: Claude Sonnet (30.0/30)
- Support Strength: Claude Sonnet (0.0/8)
- Structural Reasoning: Claude Sonnet (4.8/8)
- Assumption Discipline: Claude Sonnet (4.3/6)
- Uncertainty Handling: Claude Sonnet (3.3/6)
- Alternative Hypothesis Quality: Claude Sonnet (4.5/6)
- Self Monitoring Quality: Claude Sonnet (1.2/8)
- Insight Depth: Claude Sonnet (4.0/8)
- Mechanism Quality: Claude Sonnet (1.5/10)
- Communication Efficiency: Claude Sonnet (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Sonnet | 13.0s | 63.6/100 | 4.9 |

Failure modes observed: decorative_uncertainty, missed_key_insight, named_not_explained, unsupported_conclusion, unsupported_intermediate_step, unused_assumption.
