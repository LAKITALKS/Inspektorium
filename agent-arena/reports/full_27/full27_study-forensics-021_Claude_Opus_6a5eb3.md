# Forensic Dossier: Study Forensics: Virtual tutoring boosts reading skills

**Run ID:** `full27_study-forensics-021_Claude_Opus_6a5eb3`  
**Task:** study-forensics-021 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T16:59:11.392479+00:00  
**Task Family:** solid  
**Trap Type:** overflagging_solid_study  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Opus
**Winner:** Claude Opus — **64.6/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, missed_key_insight, named_not_explained, unsupported_conclusion, unsupported_intermediate_step, unused_assumption
**Forensic flags:** 5
**Consistency findings:** 12
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Opus | 30.0/30 | 0.0/8 | 4.8/8 | 3.8/6 | 3.3/6 | 6.0/6 | 1.2/8 | 4.0/8 | 1.5/10 | 10.0/10 | **64.6/100** |

## Study Forensics Audit

### Claude Opus

**Classification:** `solid` [+] (gold: `solid`)
**Finding Recall:** 50%
**Matched Findings:** cautious_scope_control
**Missed Findings:** evidence_matches_claim
**Extra Findings:** none_or_minor, conclusion_exceeds_results, unsupported_generalization, correlation_as_causation

## Reasoning Integrity Audit

### Claude Opus
**Classification:** Correct but brittle reasoning
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

- **[MODERATE]** `weak_mechanism`: Correct answer but weak mechanism explanation — answer may not generalize
  - `final_answer`: "solid"
- **[MAJOR]** `unsupported_leap`: Correct answer with weak support chain — final answer may be an unsupported leap
- **[MODERATE]** `unsupported_conclusion_claims`: 1/1 conclusion claims lack step support
  - `final_answer`: "solid"
- **[MODERATE]** `ungrounded_mechanism`: Mechanism named/described but not connected to case-specific data
  - `(mechanism analysis)`: "effect"
- **[MINOR]** `study_forensics_overflagging`: Agent raised extra findings in solid case: none_or_minor, conclusion_exceeds_results, unsupported_generalization, correlation_as_causation


## Evidence Map

### Claude Opus

**Correctness:** 30.0/30
  - (+) `final_answer`: "solid"
    _Agent's answer for correctness check_
  - Note: Exact match

**Support Strength:** 0.0/8
  - (-) `final_answer`: "solid"
    _Conclusion not supported by steps_
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 6
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[4]`: "Verified claims stay within studied population (struggling elementary readers in rural district)"
    _Most informative reasoning step_
  - Note: 6 reasoning steps
  - Note: Low step utility: 0/6 steps contribute

**Assumption Discipline:** 3.8/6
  - (+) `assumptions[3]`: "The rural school district context is representative enough for the claims made"
    _Most substantive assumption_
  - (-) `assumptions[0]`: "The control condition was properly randomized"
    _Declared but unused in reasoning_
  - (-) `assumptions[2]`: "The sample size was adequate for statistical power"
    _Declared but unused in reasoning_
  - Note: 4/4 substantive assumptions
  - Note: 2 unused assumption(s)

**Uncertainty Handling:** 3.3/6
  - (+) `uncertainties[1]`: "Definition of 'reading progress' metric not detailed"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.85"
    _Stated confidence level_
  - (-) `uncertainties[0]`: "Exact sample size not specified"
    _Listed but never addressed in reasoning_
  - (-) `uncertainties[1]`: "Definition of 'reading progress' metric not detailed"
    _Listed but never addressed in reasoning_
  - Note: 4 uncertainties (4 substantive)
  - Note: 2 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 6.0/6
  - (+) `alternative_hypotheses[0]`: "Could be overclaim if 'two months progress' metric is poorly defined, but text presents it as measured outcome"
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 2/2 include rejection reasoning

**Self Monitoring Quality:** 1.2/8
  - (+) `self_check[1]`: "Claims about cost-effectiveness appear data-based not speculative"
    _Most substantive self-verification step_
  - (-) `self_check[0]`: "Did not overflag - RCT design supports causal language used"
    _Fluff self-check_
  - Note: 4 self-check items
  - Note: Self-check quality: 0 deep, 1 arithmetic, 3 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.80, 215 words

**Insight Depth:** 4.0/8
  - (+) `(output text)`: "solid identified this as an rct with human participants (elem"
    _Insight 'RCT' matched (exact)_
  - (?) `(not found)`: "Missing: cautious language"
    _Insight 'cautious language' not found_
  - Note: Key insights: 1 full / 2


## Failure Analysis

### Claude Opus

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
- **Unused Assumption** `[HEURISTIC]`: Assumption 'The control condition was properly randomized...' is declared but not referenced in reasoning
  - `assumptions[0]`: "The control condition was properly randomized"
  - _Impacts: assumption_discipline_
- **Unused Assumption** `[HEURISTIC]`: Assumption 'The sample size was adequate for statistical power...' is declared but not referenced in reasoning
  - `assumptions[2]`: "The sample size was adequate for statistical power"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Exact sample size not specified...' is listed but not addressed
  - `uncertainties[0]`: "Exact sample size not specified"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Definition of 'reading progress' metric not detailed...' is listed but not addressed
  - `uncertainties[1]`: "Definition of 'reading progress' metric not detailed"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Opus

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/7 content words)
  - `key_claims[0]`: "Study design is appropriate (RCT) for causal claims made"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/3 content words)
  - `key_claims[1]`: "Results are specific and quantified"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/5 content words)
  - `key_claims[2]`: "Conclusions remain within studied population"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/6 content words)
  - `key_claims[3]`: "Appropriate caveats included (need for consistent participation)"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 5 has low overlap with final answer (0/5 content words)
  - `key_claims[4]`: "No extrapolation beyond elementary students to other age groups"
- **[WARN]** `[HEURISTIC]` `claim_step_alignment`: Key claim 1 not well supported in reasoning steps (1/7 content words found)
  - `key_claims[0]`: "Study design is appropriate (RCT) for causal claims made"
- **[WARN]** `[HEURISTIC]` `claim_step_alignment`: Key claim 4 not well supported in reasoning steps (0/6 content words found)
  - `key_claims[3]`: "Appropriate caveats included (need for consistent participation)"
- **[WARN]** `[HEURISTIC]` `unused_assumption`: Assumption 1 appears unused in reasoning or answer
  - `assumptions[0]`: "The control condition was properly randomized"
- **[WARN]** `[HEURISTIC]` `unused_assumption`: Assumption 3 appears unused in reasoning or answer
  - `assumptions[2]`: "The sample size was adequate for statistical power"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 1 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[0]`: "Exact sample size not specified"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 2 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[1]`: "Definition of 'reading progress' metric not detailed"
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "solid"


## Agent Profiles

### Claude Opus (claude-opus-4-20250514)
**Parse OK:** True | **Latency:** 20239ms

**Final Answer:** solid

**Confidence:** 0.85

**Assumptions:**
- The control condition was properly randomized
- Reading progress was measured using validated assessment tools
- The sample size was adequate for statistical power
- The rural school district context is representative enough for the claims made

**Reasoning Steps:**
1. Identified this as an RCT with human participants (elementary students)
2. Noted specific quantitative outcomes (two months reading progress gain)
3. Observed dose-response relationship (more sessions = better outcomes)
4. Checked if conclusions exceeded evidence - they do not
5. Verified claims stay within studied population (struggling elementary readers in rural district)
6. Confirmed cost-effectiveness claim appears to be based on actual program data

**Key Claims:**
- Study design is appropriate (RCT) for causal claims made
- Results are specific and quantified
- Conclusions remain within studied population
- Appropriate caveats included (need for consistent participation)
- No extrapolation beyond elementary students to other age groups

**Alternative Hypotheses:**
- Could be overclaim if 'two months progress' metric is poorly defined, but text presents it as measured outcome
- Could flag as needing more context about control condition, but RCT design implies proper controls

**Uncertainties:**
- Exact sample size not specified
- Definition of 'reading progress' metric not detailed
- Specific cost comparisons not provided
- Duration of effect persistence unknown

**Self-Verification:**
- Did not overflag - RCT design supports causal language used
- Claims about cost-effectiveness appear data-based not speculative
- No red flags for p-hacking or cherry-picking evident in summary
- Dose-response finding strengthens credibility

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 3.8/6 `######....`
- Uncertainty Handling: 3.3/6 `#####.....`
- Alternative Hypothesis Quality: 6.0/6 `##########`
- Self Monitoring Quality: 1.2/8 `#.........`
- Insight Depth: 4.0/8 `#####.....`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Opus** scored **64.6/100**.

**Best per dimension:**
- Correctness: Claude Opus (30.0/30)
- Support Strength: Claude Opus (0.0/8)
- Structural Reasoning: Claude Opus (4.8/8)
- Assumption Discipline: Claude Opus (3.8/6)
- Uncertainty Handling: Claude Opus (3.3/6)
- Alternative Hypothesis Quality: Claude Opus (6.0/6)
- Self Monitoring Quality: Claude Opus (1.2/8)
- Insight Depth: Claude Opus (4.0/8)
- Mechanism Quality: Claude Opus (1.5/10)
- Communication Efficiency: Claude Opus (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Opus | 20.2s | 64.6/100 | 3.2 |

Failure modes observed: decorative_uncertainty, missed_key_insight, named_not_explained, unsupported_conclusion, unsupported_intermediate_step, unused_assumption.
