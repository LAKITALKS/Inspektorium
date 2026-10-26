# Forensic Dossier: Study Forensics: AI tutors show moderate gains compared to human tutors

**Run ID:** `full27_study-forensics-035_Claude_Sonnet_661039`  
**Task:** study-forensics-035 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T18:05:52.125847+00:00  
**Task Family:** solid  
**Trap Type:** borderline_solid_with_caveats  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Sonnet
**Winner:** Claude Sonnet — **66.7/100** (margin: 0.0)
**Failure modes:** decorative_self_check, decorative_uncertainty, named_not_explained, unsupported_conclusion, unsupported_intermediate_step, unused_assumption
**Forensic flags:** 5
**Consistency findings:** 6
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Sonnet | 30.0/30 | 0.0/8 | 4.8/8 | 4.3/6 | 3.6/6 | 4.5/6 | 0.0/8 | 8.0/8 | 1.5/10 | 10.0/10 | **66.7/100** |

## Study Forensics Audit

### Claude Sonnet

**Classification:** `solid` [+] (gold: `solid`)
**Finding Recall:** 100%
**Matched Findings:** evidence_matches_claim, cautious_scope_control
**Extra Findings:** none_or_minor, conclusion_exceeds_results, unsupported_generalization, mechanism_not_demonstrated, correlation_as_causation

## Reasoning Integrity Audit

### Claude Sonnet
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 7

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
- **[MINOR]** `study_forensics_overflagging`: Agent raised extra findings in solid case: none_or_minor, conclusion_exceeds_results, unsupported_generalization, mechanism_not_demonstrated, correlation_as_causation


## Evidence Map

### Claude Sonnet

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
  - (+) `steps[0]`: "Identified evidence tier: Human students were directly studied in educational contexts"
    _Most informative reasoning step_
  - Note: 7 reasoning steps
  - Note: Low step utility: 0/7 steps contribute

**Assumption Discipline:** 4.3/6
  - (+) `assumptions[3]`: "The studies were conducted with sufficient sample sizes for meaningful comparison"
    _Most substantive assumption_
  - (-) `assumptions[3]`: "The studies were conducted with sufficient sample sizes for meaningful comparison"
    _Declared but unused in reasoning_
  - Note: 4/4 substantive assumptions
  - Note: 1 unused assumption(s)

**Uncertainty Handling:** 3.6/6
  - (+) `uncertainties[2]`: "Whether these were randomized controlled trials or observational studies"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.9"
    _Stated confidence level_
  - (-) `uncertainties[2]`: "Whether these were randomized controlled trials or observational studies"
    _Listed but never addressed in reasoning_
  - Note: 3 uncertainties (3 substantive)
  - Note: 1 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 4.5/6
  - (+) `alternative_hypotheses[0]`: "mechanism_vs_evidence - if this were preliminary or pilot data being overgeneralized"
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 2/2 genuinely diverse alternatives

**Self Monitoring Quality:** 0.0/8
  - (+) `self_check[3]`: "Ensured I'm evaluating the text as written, not hypothetical issues"
    _Most substantive self-verification step_
  - (-) `self_check[0]`: "Confirmed no evidence-tier mismatch exists"
    _Fluff self-check_
  - Note: 4 self-check items
  - Note: Self-check quality: 0 deep, 0 arithmetic, 4 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.80, 222 words

**Insight Depth:** 4.0/8
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

**MINOR:**
- **Decorative Self Check** `[HEURISTIC]`: All 4 self-checks appear to be fluff — no substantive verification
  - `self_check[0]`: "Confirmed no evidence-tier mismatch exists"
  - _Impacts: self_monitoring_quality_

**STYLISTIC:**
- **Unused Assumption** `[HEURISTIC]`: Assumption 'The studies were conducted with sufficient sample sizes for ...' is declared but not referenced in reasoning
  - `assumptions[3]`: "The studies were conducted with sufficient sample sizes for meaningful comparison"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether these were randomized controlled trials or observati...' is listed but not addressed
  - `uncertainties[2]`: "Whether these were randomized controlled trials or observational studies"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Sonnet

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/7 content words)
  - `key_claims[0]`: "Direct human evidence supports conclusions about human educational outcomes"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/4 content words)
  - `key_claims[1]`: "Claims are appropriately scoped to the evidence"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/7 content words)
  - `key_claims[2]`: "Proper acknowledgment that AI complements rather than replaces human instruction"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "mechanism_vs_evidence - if this were preliminary or pilot data being overgeneralized"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 2 is stated without rejection reasoning
  - `alternative_hypotheses[1]`: "overclaim - if the benefits were being oversold beyond what the data shows"
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "solid"


## Agent Profiles

### Claude Sonnet (claude-sonnet-4-20250514)
**Parse OK:** True | **Latency:** 13575ms

**Final Answer:** solid

**Confidence:** 0.9

**Assumptions:**
- The studies involved actual students in educational settings
- Success rates and mastery improvements were measured with appropriate metrics
- The comparison groups were properly controlled
- The studies were conducted with sufficient sample sizes for meaningful comparison

**Reasoning Steps:**
1. Identified evidence tier: Human students were directly studied in educational contexts
2. Identified conclusion tier: Claims are about educational effectiveness in human learning contexts
3. Checked for bridge step: No evidence-tier mismatch - conclusions match the population studied
4. Examined claims: Specific, measured outcomes (66% vs 61% vs 56%, 4-9 percentage point improvements)
5. Assessed hedging: Appropriate caveats present (AI complements rather than replaces tutors)
6. Checked for overclaiming: Results presented as measured findings, not inflated promises
7. Verified study design: Comparative studies with control groups and validation measures

**Key Claims:**
- Direct human evidence supports conclusions about human educational outcomes
- Claims are appropriately scoped to the evidence
- Proper acknowledgment that AI complements rather than replaces human instruction

**Alternative Hypotheses:**
- mechanism_vs_evidence - if this were preliminary or pilot data being overgeneralized
- overclaim - if the benefits were being oversold beyond what the data shows

**Uncertainties:**
- Sample sizes and study duration not specified
- Specific methodological details not provided
- Whether these were randomized controlled trials or observational studies

**Self-Verification:**
- Confirmed no evidence-tier mismatch exists
- Verified claims stay within bounds of measured outcomes
- Checked that I'm not fabricating problems where none exist
- Ensured I'm evaluating the text as written, not hypothetical issues

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 4.3/6 `#######...`
- Uncertainty Handling: 3.6/6 `######....`
- Alternative Hypothesis Quality: 4.5/6 `#######...`
- Self Monitoring Quality: 0.0/8 `..........`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Sonnet** scored **66.7/100**.

**Best per dimension:**
- Correctness: Claude Sonnet (30.0/30)
- Support Strength: Claude Sonnet (0.0/8)
- Structural Reasoning: Claude Sonnet (4.8/8)
- Assumption Discipline: Claude Sonnet (4.3/6)
- Uncertainty Handling: Claude Sonnet (3.6/6)
- Alternative Hypothesis Quality: Claude Sonnet (4.5/6)
- Self Monitoring Quality: Claude Sonnet (0.0/8)
- Insight Depth: Claude Sonnet (8.0/8)
- Mechanism Quality: Claude Sonnet (1.5/10)
- Communication Efficiency: Claude Sonnet (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Sonnet | 13.6s | 66.7/100 | 4.9 |

Failure modes observed: decorative_self_check, decorative_uncertainty, named_not_explained, unsupported_conclusion, unsupported_intermediate_step, unused_assumption.
