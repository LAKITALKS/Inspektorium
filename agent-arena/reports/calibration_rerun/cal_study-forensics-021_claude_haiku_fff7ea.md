# Forensic Dossier: Study Forensics: Virtual tutoring boosts reading skills

**Run ID:** `cal_study-forensics-021_claude_haiku_fff7ea`  
**Task:** study-forensics-021 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-06T14:59:50.445028+00:00  
**Task Family:** solid  
**Trap Type:** overflagging_solid_study  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **71.4/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, named_not_explained, unsupported_conclusion, unsupported_intermediate_step, unused_assumption
**Forensic flags:** 5
**Consistency findings:** 11
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 30.0/30 | 0.0/8 | 4.8/8 | 3.2/6 | 3.0/6 | 6.0/6 | 6.4/8 | 8.0/8 | 1.5/10 | 8.5/10 | **71.4/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `solid` [+] (gold: `solid`)
**Finding Recall:** 100%
**Matched Findings:** evidence_matches_claim, cautious_scope_control
**Extra Findings:** none_or_minor, conclusion_exceeds_results, unsupported_generalization, decorative_uncertainty, correlation_as_causation

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
- **[MINOR]** `study_forensics_overflagging`: Agent raised extra findings in solid case: none_or_minor, conclusion_exceeds_results, unsupported_generalization, decorative_uncertainty, correlation_as_causation


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
  - (+) `steps[2]`: "Checked for overclaim: The text attributes gains to the program and notes dose-response (fewer sessions = modest gains),"
    _Most informative reasoning step_
  - Note: 9 reasoning steps
  - Note: Low step utility: 0/9 steps contribute

**Assumption Discipline:** 3.2/6
  - (+) `assumptions[0]`: "The study used a proper randomized assignment to treatment and control conditions"
    _Most substantive assumption_
  - (-) `assumptions[4]`: "Attrition rates and missing data are reasonably managed"
    _Declared but unused in reasoning_
  - (-) `assumptions[5]`: "The rural school district sample is representative enough for the claims made"
    _Declared but unused in reasoning_
  - Note: 6/6 substantive assumptions
  - Note: Many assumptions (6)

**Uncertainty Handling:** 3.0/6
  - (+) `uncertainties[1]`: "Whether the control group received any intervention or just standard instruction (text says 'control condition' but does"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.88"
    _Stated confidence level_
  - (-) `uncertainties[1]`: "Whether the control group received any intervention or just standard instruction (text says 'control condition' but does"
    _Listed but never addressed in reasoning_
  - (-) `uncertainties[2]`: "Whether attrition or differential dropout between groups is addressed"
    _Listed but never addressed in reasoning_
  - Note: 5 uncertainties (5 substantive)
  - Note: 3 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 6.0/6
  - (+) `alternative_hypotheses[0]`: "correlation_vs_causation — if the study were observational rather than RCT, but the text explicitly states 'randomized c"
    _Most substantive alternative hypothesis_
  - Note: 3 alternative hypotheses considered
  - Note: 3/3 include rejection reasoning

**Self Monitoring Quality:** 6.4/8
  - (+) `self_check[5]`: "Is the study truly solid, or am I being too lenient? The study appears well-designed with appropriate claims; the main l"
    _Most substantive self-verification step_
  - Note: 6 self-check items
  - Note: Self-check quality: 0 deep, 6 arithmetic, 0 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 8.5/10
  - Note: Signal density: 0.72, 558 words

**Insight Depth:** 8.0/8
  - (+) `(output text)`: "olid identified study design: rct with treatment (virtual tutor"
    _Insight 'RCT' matched (exact)_
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
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Named concept(s) ['effect'] but mechanism not described
  - _Impacts: mechanism_quality, insight_depth_
- **Unsupported Intermediate Step** `[MEDIUM CONFIDENCE]`: No reasoning step is load-bearing — final answer lacks traceable derivation
  - `final_answer`: "solid"
  - _Impacts: support_strength, structural_reasoning_

**STYLISTIC:**
- **Unused Assumption** `[HEURISTIC]`: Assumption 'Attrition rates and missing data are reasonably managed...' is declared but not referenced in reasoning
  - `assumptions[4]`: "Attrition rates and missing data are reasonably managed"
  - _Impacts: assumption_discipline_
- **Unused Assumption** `[HEURISTIC]`: Assumption 'The rural school district sample is representative enough fo...' is declared but not referenced in reasoning
  - `assumptions[5]`: "The rural school district sample is representative enough for the claims made"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether the control group received any intervention or just ...' is listed but not addressed
  - `uncertainties[1]`: "Whether the control group received any intervention or just standard instruction (text says 'control"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether attrition or differential dropout between groups is ...' is listed but not addressed
  - `uncertainties[2]`: "Whether attrition or differential dropout between groups is addressed"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether the cost comparison is fair (e.g., does 'typical hig...' is listed but not addressed
  - `uncertainties[4]`: "Whether the cost comparison is fair (e.g., does 'typical high-dose tutoring' include in-person or ot"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/7 content words)
  - `key_claims[0]`: "RCT design is appropriate and supports causal inference about program effectiveness"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/7 content words)
  - `key_claims[1]`: "Quantified outcome (2 months progress for ~40 sessions) is specific and testable"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/13 content words)
  - `key_claims[2]`: "Dose-response pattern (fewer sessions → modest gains) is consistent with causal mechanism and reduce"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/8 content words)
  - `key_claims[3]`: "No unsupported generalizations beyond the rural elementary student population tested"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 5 has low overlap with final answer (0/7 content words)
  - `key_claims[4]`: "Cost-effectiveness claim is reasonable but lacks detail on comparison standard"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 6 has low overlap with final answer (0/5 content words)
  - `key_claims[5]`: "Emphasis on participation consistency is data-driven and appropriate"
- **[WARN]** `[HEURISTIC]` `claim_step_alignment`: Key claim 4 not well supported in reasoning steps (0/8 content words found)
  - `key_claims[3]`: "No unsupported generalizations beyond the rural elementary student population tested"
- **[WARN]** `[HEURISTIC]` `unused_assumption`: Assumption 5 appears unused in reasoning or answer
  - `assumptions[4]`: "Attrition rates and missing data are reasonably managed"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 3 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[2]`: "Whether attrition or differential dropout between groups is addressed"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 5 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[4]`: "Whether the cost comparison is fair (e.g., does 'typical high-dose tutoring' include in-person or ot"
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "solid"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 10901ms

**Final Answer:** solid

**Confidence:** 0.88

**Assumptions:**
- The study used a proper randomized assignment to treatment and control conditions
- Reading progress was measured with a validated, standardized assessment
- The ten-week timeframe and session counts are accurately reported
- The control condition received no tutoring or standard instruction only
- Attrition rates and missing data are reasonably managed
- The rural school district sample is representative enough for the claims made

**Reasoning Steps:**
1. Identified study design: RCT with treatment (virtual tutoring) and control groups — this is a strong design for causal inference
2. Examined the primary outcome claim: ~2 months reading progress gain for ~40 sessions — this is a specific, quantified result
3. Checked for overclaim: The text attributes gains to the program and notes dose-response (fewer sessions = modest gains), which is consistent with causal language appropriate for RCT data
4. Evaluated mechanism claims: No mechanistic explanation is offered; the text simply reports outcomes
5. Assessed correlation vs. causation: RCT design supports causal claims; the text appropriately uses causal language ('gained,' 'delivered results')
6. Examined confounders: RCT randomization controls for most baseline confounders; no obvious uncontrolled confounders mentioned
7. Checked for decorative uncertainty: The text does NOT use weak hedging while making strong claims; it presents findings directly without false caveats
8. Evaluated practical claims: Cost-effectiveness claim is reasonable given the outcome and design, though cost comparison details are not provided
9. Assessed emphasis on participation: The note that 'consistent participation was critical' is appropriate and supported by the dose-response pattern (fewer sessions = modest gains)

**Key Claims:**
- RCT design is appropriate and supports causal inference about program effectiveness
- Quantified outcome (2 months progress for ~40 sessions) is specific and testable
- Dose-response pattern (fewer sessions → modest gains) is consistent with causal mechanism and reduces reverse-causality concerns
- No unsupported generalizations beyond the rural elementary student population tested
- Cost-effectiveness claim is reasonable but lacks detail on comparison standard
- Emphasis on participation consistency is data-driven and appropriate

**Alternative Hypotheses:**
- correlation_vs_causation — if the study were observational rather than RCT, but the text explicitly states 'randomized controlled trial'
- overclaim — if the text generalized beyond rural elementary students or made claims about long-term retention, but it does not
- mechanism_vs_evidence — if the text explained *why* the program works, but it only reports outcomes

**Uncertainties:**
- Whether the 'two additional months of reading progress' is educationally meaningful (effect size not provided in text)
- Whether the control group received any intervention or just standard instruction (text says 'control condition' but doesn't specify)
- Whether attrition or differential dropout between groups is addressed
- The specific reading assessment used and whether it is sensitive to the gains claimed
- Whether the cost comparison is fair (e.g., does 'typical high-dose tutoring' include in-person or other formats?)

**Self-Verification:**
- Did I assume the RCT was well-executed? Yes, but the text explicitly states it is an RCT; I should not assume hidden flaws
- Did I miss any overclaims? No — the text is cautious about generalization and does not claim long-term effects or universal applicability
- Did I flag correlation-as-causation incorrectly? No — RCT design justifies causal language
- Did I invent confounders? No — I noted that randomization controls for baseline confounders
- Did I miss decorative uncertainty? No — the text does not use weak hedging inappropriately
- Is the study truly solid, or am I being too lenient? The study appears well-designed with appropriate claims; the main limitation is lack of detail on implementation and long-term follow-up, which is not a flaw in the summary itself

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 3.2/6 `#####.....`
- Uncertainty Handling: 3.0/6 `####......`
- Alternative Hypothesis Quality: 6.0/6 `##########`
- Self Monitoring Quality: 6.4/8 `########..`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 8.5/10 `########..`


## Final Verdict

**Solo run: Claude Haiku** scored **71.4/100**.

**Best per dimension:**
- Correctness: Claude Haiku (30.0/30)
- Support Strength: Claude Haiku (0.0/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (3.2/6)
- Uncertainty Handling: Claude Haiku (3.0/6)
- Alternative Hypothesis Quality: Claude Haiku (6.0/6)
- Self Monitoring Quality: Claude Haiku (6.4/8)
- Insight Depth: Claude Haiku (8.0/8)
- Mechanism Quality: Claude Haiku (1.5/10)
- Communication Efficiency: Claude Haiku (8.5/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 10.9s | 71.4/100 | 6.5 |

Failure modes observed: decorative_uncertainty, named_not_explained, unsupported_conclusion, unsupported_intermediate_step, unused_assumption.
