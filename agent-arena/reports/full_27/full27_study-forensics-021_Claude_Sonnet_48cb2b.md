# Forensic Dossier: Study Forensics: Virtual tutoring boosts reading skills

**Run ID:** `full27_study-forensics-021_Claude_Sonnet_48cb2b`  
**Task:** study-forensics-021 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T17:55:29.627907+00:00  
**Task Family:** solid  
**Trap Type:** overflagging_solid_study  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Sonnet
**Winner:** Claude Sonnet — **58.9/100** (margin: 0.0)
**Failure modes:** decorative_self_check, decorative_uncertainty, missed_key_insight, overclaiming, unsupported_conclusion, unsupported_intermediate_step, unused_assumption
**Forensic flags:** 4
**Consistency findings:** 8
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Sonnet | 25.5/30 | 0.0/8 | 4.8/8 | 4.3/6 | 3.0/6 | 4.5/6 | 0.0/8 | 6.8/8 | 0.0/10 | 10.0/10 | **58.9/100** |

## Study Forensics Audit

### Claude Sonnet

**Classification:** `solid` [+] (gold: `solid`)
**Finding Recall:** 50%
**Matched Findings:** cautious_scope_control
**Missed Findings:** evidence_matches_claim
**Extra Findings:** none_or_minor, conclusion_exceeds_results, unsupported_generalization, mechanism_not_demonstrated, correlation_as_causation
**False Positives:** overclaim

## Reasoning Integrity Audit

### Claude Sonnet
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 6

## Mechanism Analysis

### Claude Sonnet
| Aspect | Status |
|--------|--------|
| Concept named | :x: none |
| Mechanism described | :x: (0 sentence(s)) |
| Grounded to case | :x: (0 sentence(s)) |

**Missing:** concept not named, mechanism not described, mechanism not grounded to case data

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
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 6
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[2]`: "Examined claims for overclaim: results are reported modestly (two months additional progress, modest gains for partial p"
    _Most informative reasoning step_
  - Note: 6 reasoning steps
  - Note: Low step utility: 0/6 steps contribute

**Assumption Discipline:** 4.3/6
  - (+) `assumptions[0]`: "This was a properly conducted RCT with appropriate control group"
    _Most substantive assumption_
  - (-) `assumptions[2]`: "The cost comparison was based on actual data"
    _Declared but unused in reasoning_
  - Note: 4/4 substantive assumptions
  - Note: 1 unused assumption(s)

**Uncertainty Handling:** 3.0/6
  - (+) `uncertainties[1]`: "Unclear if the rural context limits generalizability claims"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.9"
    _Stated confidence level_
  - (-) `uncertainties[0]`: "Don't know the exact sample size or effect size statistics"
    _Listed but never addressed in reasoning_
  - (-) `uncertainties[1]`: "Unclear if the rural context limits generalizability claims"
    _Listed but never addressed in reasoning_
  - Note: 3 uncertainties (3 substantive)
  - Note: 3 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 4.5/6
  - (+) `alternative_hypotheses[1]`: "Could be mechanism_vs_evidence if generalizing beyond the studied context"
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 2/2 genuinely diverse alternatives

**Self Monitoring Quality:** 0.0/8
  - (+) `self_check[3]`: "The study tests what it claims to test in the population it claims to benefit"
    _Most substantive self-verification step_
  - (-) `self_check[0]`: "Verified no evidence-tier mismatch exists"
    _Fluff self-check_
  - Note: 4 self-check items
  - Note: Self-check quality: 0 deep, 0 arithmetic, 4 fluff

**Mechanism Quality:** 0.0/10
  - Note: Neither names concept nor explains mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.69, 209 words

**Insight Depth:** 8.0/8
  - (+) `(output text)`: "id identified this as a human rct testing an educational interv"
    _Insight 'RCT' matched (exact)_
  - Note: Key insights: 2 full / 2


## Failure Analysis

### Claude Sonnet

**MAJOR:**
- **Overclaiming** `[HEURISTIC]`: False positive: agent flagged 'overclaim' in a solid case
  - `final_answer`: "solid"
  - _Impacts: correctness_

**MODERATE:**
- **Unsupported Conclusion** `[MEDIUM CONFIDENCE]`: Final answer lacks load-bearing or supporting step grounding
  - `final_answer`: "solid"
  - _Impacts: support_strength_
- **Unsupported Intermediate Step** `[MEDIUM CONFIDENCE]`: No reasoning step is load-bearing — final answer lacks traceable derivation
  - `final_answer`: "solid"
  - _Impacts: support_strength, structural_reasoning_
- **Missed Key Insight** `[MEDIUM CONFIDENCE]`: Missed expected finding: evidence_matches_claim
  - `(task expectation)`: "Expected: evidence_matches_claim"
  - _Impacts: insight_depth_

**MINOR:**
- **Decorative Self Check** `[HEURISTIC]`: All 4 self-checks appear to be fluff — no substantive verification
  - `self_check[0]`: "Verified no evidence-tier mismatch exists"
  - _Impacts: self_monitoring_quality_

**STYLISTIC:**
- **Unused Assumption** `[HEURISTIC]`: Assumption 'The cost comparison was based on actual data...' is declared but not referenced in reasoning
  - `assumptions[2]`: "The cost comparison was based on actual data"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Don't know the exact sample size or effect size statistics...' is listed but not addressed
  - `uncertainties[0]`: "Don't know the exact sample size or effect size statistics"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Unclear if the rural context limits generalizability claims...' is listed but not addressed
  - `uncertainties[1]`: "Unclear if the rural context limits generalizability claims"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Don't know if cost analysis was rigorous...' is listed but not addressed
  - `uncertainties[2]`: "Don't know if cost analysis was rigorous"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Sonnet

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/7 content words)
  - `key_claims[0]`: "This appears to be a well-conducted and appropriately reported educational intervention study"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/4 content words)
  - `key_claims[1]`: "Claims are proportionate to the evidence from the RCT"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/5 content words)
  - `key_claims[2]`: "Appropriate caveats about participation consistency are included"
- **[WARN]** `[HEURISTIC]` `unused_assumption`: Assumption 3 appears unused in reasoning or answer
  - `assumptions[2]`: "The cost comparison was based on actual data"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 1 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[0]`: "Don't know the exact sample size or effect size statistics"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 3 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[2]`: "Don't know if cost analysis was rigorous"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "Could be overclaim if the cost claims were unsupported"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 2 is stated without rejection reasoning
  - `alternative_hypotheses[1]`: "Could be mechanism_vs_evidence if generalizing beyond the studied context"


## Agent Profiles

### Claude Sonnet (claude-sonnet-4-20250514)
**Parse OK:** True | **Latency:** 10943ms

**Final Answer:** solid

**Confidence:** 0.9

**Assumptions:**
- This was a properly conducted RCT with appropriate control group
- The reading progress measurements were valid and reliable
- The cost comparison was based on actual data
- The study population was elementary students in a rural district

**Reasoning Steps:**
1. Identified this as a human RCT testing an educational intervention
2. Checked for evidence-tier mismatch: conclusions stay within the studied population (elementary students)
3. Examined claims for overclaim: results are reported modestly (two months additional progress, modest gains for partial participation)
4. Looked for causal language: appropriate given RCT design
5. Assessed uncertainty handling: researchers appropriately emphasized importance of consistent participation
6. Checked for obvious confounders: none ignored in the reporting

**Key Claims:**
- This appears to be a well-conducted and appropriately reported educational intervention study
- Claims are proportionate to the evidence from the RCT
- Appropriate caveats about participation consistency are included

**Alternative Hypotheses:**
- Could be overclaim if the cost claims were unsupported
- Could be mechanism_vs_evidence if generalizing beyond the studied context

**Uncertainties:**
- Don't know the exact sample size or effect size statistics
- Unclear if the rural context limits generalizability claims
- Don't know if cost analysis was rigorous

**Self-Verification:**
- Verified no evidence-tier mismatch exists
- Confirmed claims are modest and supported
- Checked that I'm not fabricating problems where none exist
- The study tests what it claims to test in the population it claims to benefit

**Dimension Scores:**
- Correctness: 25.5/30 `########..`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 4.3/6 `#######...`
- Uncertainty Handling: 3.0/6 `####......`
- Alternative Hypothesis Quality: 4.5/6 `#######...`
- Self Monitoring Quality: 0.0/8 `..........`
- Insight Depth: 6.8/8 `########..`
- Mechanism Quality: 0.0/10 `..........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Sonnet** scored **58.9/100**.

**Best per dimension:**
- Correctness: Claude Sonnet (25.5/30)
- Support Strength: Claude Sonnet (0.0/8)
- Structural Reasoning: Claude Sonnet (4.8/8)
- Assumption Discipline: Claude Sonnet (4.3/6)
- Uncertainty Handling: Claude Sonnet (3.0/6)
- Alternative Hypothesis Quality: Claude Sonnet (4.5/6)
- Self Monitoring Quality: Claude Sonnet (0.0/8)
- Insight Depth: Claude Sonnet (6.8/8)
- Mechanism Quality: Claude Sonnet (0.0/10)
- Communication Efficiency: Claude Sonnet (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Sonnet | 10.9s | 58.9/100 | 5.4 |

Failure modes observed: decorative_self_check, decorative_uncertainty, missed_key_insight, overclaiming, unsupported_conclusion, unsupported_intermediate_step, unused_assumption.
