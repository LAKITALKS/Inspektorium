# Forensic Dossier: Study Forensics: Social media use and well-being

**Run ID:** `praxis_study-forensics-001_Claude_Opus_4c1193`  
**Task:** study-forensics-001 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-07T07:46:52.251695+00:00  
**Task Family:** solid  
**Trap Type:** overflagging_solid_study  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Opus
**Winner:** Claude Opus — **70.5/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, missed_key_insight, named_not_explained, unsupported_conclusion, unsupported_intermediate_step
**Forensic flags:** 5
**Consistency findings:** 6
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Opus | 30.0/30 | 0.0/8 | 4.8/8 | 4.8/6 | 3.3/6 | 6.0/6 | 4.8/8 | 5.3/8 | 1.5/10 | 10.0/10 | **70.5/100** |

## Study Forensics Audit

### Claude Opus

**Classification:** `solid` [+] (gold: `solid`)
**Finding Recall:** 67%
**Matched Findings:** cautious_scope_control, none_or_minor
**Missed Findings:** evidence_matches_claim
**Extra Findings:** conclusion_exceeds_results, correlation_as_causation

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
- **[MINOR]** `study_forensics_overflagging`: Agent raised extra findings in solid case: conclusion_exceeds_results, correlation_as_causation


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
  - (+) `steps[0]`: "1. Identified key study design elements: random assignment, control group, objective usage data collection"
    _Most informative reasoning step_
  - Note: 6 reasoning steps
  - Note: Low step utility: 0/6 steps contribute

**Assumption Discipline:** 4.8/6
  - (+) `assumptions[1]`: "The researchers actually measured what they claim to measure (depression and loneliness)"
    _Most substantive assumption_
  - Note: 4/4 substantive assumptions

**Uncertainty Handling:** 3.3/6
  - (+) `uncertainties[2]`: "Whether there was proper blinding or if demand characteristics could have influenced results"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.85"
    _Stated confidence level_
  - (-) `uncertainties[1]`: "The magnitude of the effects is not stated"
    _Listed but never addressed in reasoning_
  - (-) `uncertainties[3]`: "The baseline characteristics of the groups"
    _Listed but never addressed in reasoning_
  - Note: 4 uncertainties (4 substantive)
  - Note: 2 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 6.0/6
  - (+) `alternative_hypotheses[1]`: "correlation_vs_causation - but this is an RCT with random assignment, so causal inference is appropriate"
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 2/2 include rejection reasoning

**Self Monitoring Quality:** 4.8/8
  - (+) `self_check[2]`: "Am I being too lenient? No - the presence of random assignment, control group, and explicit limitations suggests good pr"
    _Most substantive self-verification step_
  - Note: 3 self-check items
  - Note: Self-check quality: 1 deep, 2 arithmetic, 0 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.71, 278 words

**Insight Depth:** 4.0/8
  - (?) `(not found)`: "Missing: scope limitation"
    _Insight 'scope limitation' not found_
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
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'The magnitude of the effects is not stated...' is listed but not addressed
  - `uncertainties[1]`: "The magnitude of the effects is not stated"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'The baseline characteristics of the groups...' is listed but not addressed
  - `uncertainties[3]`: "The baseline characteristics of the groups"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Opus

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/5 content words)
  - `key_claims[0]`: "This appears to be a well-designed RCT with appropriate caveats"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/6 content words)
  - `key_claims[1]`: "The use of random assignment justifies the causal language about effects"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/5 content words)
  - `key_claims[2]`: "The authors appropriately limit generalizability claims"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/9 content words)
  - `key_claims[3]`: "The study collected objective usage data rather than relying solely on self-report"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 2 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[1]`: "The magnitude of the effects is not stated"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 4 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[3]`: "The baseline characteristics of the groups"


## Agent Profiles

### Claude Opus (claude-opus-4-20250514)
**Parse OK:** True | **Latency:** 17696ms

**Final Answer:** solid

**Confidence:** 0.85

**Assumptions:**
- The study used random assignment as stated
- The researchers actually measured what they claim to measure (depression and loneliness)
- The control group continued normal usage without other interventions
- The objective usage data from screenshots was reliable

**Reasoning Steps:**
1. 1. Identified key study design elements: random assignment, control group, objective usage data collection
2. 2. Noted the intervention: limiting social media to 10 minutes per day per platform
3. 3. Examined the reported results: significant declines in depression and loneliness in the restricted group
4. 4. Checked for causal language: 'reported significant declines' is appropriate for an RCT
5. 5. Looked for caveats: authors explicitly note limitations about generalizability
6. 6. Assessed whether claims match evidence: the conclusions are limited to what was actually studied

**Key Claims:**
- This appears to be a well-designed RCT with appropriate caveats
- The use of random assignment justifies the causal language about effects
- The authors appropriately limit generalizability claims
- The study collected objective usage data rather than relying solely on self-report

**Alternative Hypotheses:**
- overclaim - but the authors explicitly limit their claims to the studied population
- correlation_vs_causation - but this is an RCT with random assignment, so causal inference is appropriate

**Uncertainties:**
- The specific measures used for depression and loneliness are not described
- The magnitude of the effects is not stated
- Whether there was proper blinding or if demand characteristics could have influenced results
- The baseline characteristics of the groups

**Self-Verification:**
- Did I look for problems that aren't there? No - I considered alternatives but found the study description solid
- Did I miss any red flags? The text is brief but doesn't contain obvious epistemic issues
- Am I being too lenient? No - the presence of random assignment, control group, and explicit limitations suggests good practice

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 4.8/6 `########..`
- Uncertainty Handling: 3.3/6 `#####.....`
- Alternative Hypothesis Quality: 6.0/6 `##########`
- Self Monitoring Quality: 4.8/8 `######....`
- Insight Depth: 5.3/8 `######....`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Opus** scored **70.5/100**.

**Best per dimension:**
- Correctness: Claude Opus (30.0/30)
- Support Strength: Claude Opus (0.0/8)
- Structural Reasoning: Claude Opus (4.8/8)
- Assumption Discipline: Claude Opus (4.8/6)
- Uncertainty Handling: Claude Opus (3.3/6)
- Alternative Hypothesis Quality: Claude Opus (6.0/6)
- Self Monitoring Quality: Claude Opus (4.8/8)
- Insight Depth: Claude Opus (5.3/8)
- Mechanism Quality: Claude Opus (1.5/10)
- Communication Efficiency: Claude Opus (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Opus | 17.7s | 70.5/100 | 4.0 |

Failure modes observed: decorative_uncertainty, missed_key_insight, named_not_explained, unsupported_conclusion, unsupported_intermediate_step.
