# Forensic Dossier: Study Forensics: AI instruction outperforms human teachers

**Run ID:** `full27_study-forensics-025_Claude_Opus_abfe99`  
**Task:** study-forensics-025 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T17:59:03.845016+00:00  
**Task Family:** overclaim  
**Trap Type:** media_inflated_overclaim  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Opus
**Winner:** Claude Opus — **71.5/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, named_not_explained, unsupported_conclusion, unsupported_intermediate_step, unused_assumption
**Forensic flags:** 4
**Consistency findings:** 6
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Opus | 30.0/30 | 0.0/8 | 4.1/8 | 4.3/6 | 3.6/6 | 5.2/6 | 4.8/8 | 8.0/8 | 1.5/10 | 10.0/10 | **71.5/100** |

## Study Forensics Audit

### Claude Opus

**Classification:** `overclaim` [+] (gold: `overclaim`)
**Finding Recall:** 100%
**Matched Findings:** conclusion_exceeds_results, unsupported_generalization
**Extra Findings:** cautious_scope_control

## Reasoning Integrity Audit

### Claude Opus
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 5

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
- "overclaim"


## Forensic Flags

### Claude Opus

- **[MODERATE]** `weak_mechanism`: Correct answer but weak mechanism explanation — answer may not generalize
  - `final_answer`: "overclaim"
- **[MAJOR]** `unsupported_leap`: Correct answer with weak support chain — final answer may be an unsupported leap
- **[MODERATE]** `unsupported_conclusion_claims`: 1/1 conclusion claims lack step support
  - `final_answer`: "overclaim"
- **[MODERATE]** `ungrounded_mechanism`: Mechanism named/described but not connected to case-specific data
  - `(mechanism analysis)`: "effect"


## Evidence Map

### Claude Opus

**Correctness:** 30.0/30
  - (+) `final_answer`: "overclaim"
    _Agent's answer for correctness check_
  - Note: Exact match

**Support Strength:** 0.0/8
  - (-) `final_answer`: "overclaim"
    _Conclusion not supported by steps_
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 5
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[0]`: "Identified evidence tier: pilot programs suggest limited human trials, not comprehensive educational research"
    _Most informative reasoning step_
  - Note: 5 reasoning steps
  - Note: Low step utility: 0/5 steps contribute

**Assumption Discipline:** 4.3/6
  - (+) `assumptions[1]`: "The '65 percent rise in test scores' and 'two-times learning effect' are based on selective or preliminary data"
    _Most substantive assumption_
  - (-) `assumptions[1]`: "The '65 percent rise in test scores' and 'two-times learning effect' are based on selective or preliminary data"
    _Declared but unused in reasoning_
  - Note: 3/3 substantive assumptions
  - Note: 1 unused assumption(s)

**Uncertainty Handling:** 3.6/6
  - (+) `uncertainties[1]`: "Whether '65 percent rise' refers to a cherry-picked metric or representative outcome"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.9"
    _Stated confidence level_
  - (-) `uncertainties[1]`: "Whether '65 percent rise' refers to a cherry-picked metric or representative outcome"
    _Listed but never addressed in reasoning_
  - Note: 3 uncertainties (3 substantive)
  - Note: 1 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 5.2/6
  - (+) `alternative_hypotheses[1]`: "However, the promotional certainty and sweeping claims ('all subjects,' 'obsolete,' 'dismantled') indicate rhetorical in"
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 1/2 include rejection reasoning

**Self Monitoring Quality:** 4.8/8
  - (+) `self_check[2]`: "The claims about 'all subjects' and teacher obsolescence go beyond any reasonable interpretation of pilot data"
    _Most substantive self-verification step_
  - Note: 3 self-check items
  - Note: Self-check quality: 1 deep, 2 arithmetic, 0 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.77, 248 words

**Insight Depth:** 4.0/8
  - (?) `(not found)`: "Missing: no methodology"
    _Insight 'no methodology' not found_
  - Note: Key insights: 1 full / 2


## Failure Analysis

### Claude Opus

**MODERATE:**
- **Unsupported Conclusion** `[MEDIUM CONFIDENCE]`: Final answer lacks load-bearing or supporting step grounding
  - `final_answer`: "overclaim"
  - _Impacts: support_strength_
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Names the phenomenon but does not explain the causal mechanism
  - `final_answer`: "overclaim"
  - _Impacts: mechanism_quality_
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Named concept(s) ['effect'] but mechanism not described
  - _Impacts: mechanism_quality, insight_depth_
- **Unsupported Intermediate Step** `[MEDIUM CONFIDENCE]`: No reasoning step is load-bearing — final answer lacks traceable derivation
  - `final_answer`: "overclaim"
  - _Impacts: support_strength, structural_reasoning_

**STYLISTIC:**
- **Unused Assumption** `[HEURISTIC]`: Assumption 'The '65 percent rise in test scores' and 'two-times learning...' is declared but not referenced in reasoning
  - `assumptions[1]`: "The '65 percent rise in test scores' and 'two-times learning effect' are based on selective or preli"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether '65 percent rise' refers to a cherry-picked metric o...' is listed but not addressed
  - `uncertainties[1]`: "Whether '65 percent rise' refers to a cherry-picked metric or representative outcome"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Opus

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/9 content words)
  - `key_claims[0]`: "Text extrapolates from limited pilots to declare the obsolescence of an entire profession"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/10 content words)
  - `key_claims[1]`: "Selective metrics (test scores) are used to make claims about comprehensive educational effectivenes"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/8 content words)
  - `key_claims[2]`: "The certainty of language ('data-backed reality') far exceeds what pilot programs can establish"
- **[FAIL]** `[MEDIUM CONFIDENCE]` `assumption_reasoning`: Assumption 3 may be contradicted by step 1
  - `assumptions[2]`: "The studies likely measured short-term test performance rather than comprehensive educational outcom"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 2 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[1]`: "Whether '65 percent rise' refers to a cherry-picked metric or representative outcome"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "mechanism_vs_evidence was considered due to the tier gap between pilots and system-wide conclusions"


## Agent Profiles

### Claude Opus (claude-opus-4-20250514)
**Parse OK:** True | **Latency:** 16960ms

**Final Answer:** overclaim

**Confidence:** 0.9

**Assumptions:**
- The pilot programs mentioned are real but likely small-scale and limited in scope
- The '65 percent rise in test scores' and 'two-times learning effect' are based on selective or preliminary data
- The studies likely measured short-term test performance rather than comprehensive educational outcomes

**Reasoning Steps:**
1. Identified evidence tier: pilot programs suggest limited human trials, not comprehensive educational research
2. Identified conclusion tier: sweeping claims about AI replacing all human teachers across all subjects
3. Detected promotional language: 'rapidly making obsolete,' 'dismantled,' 'data-backed reality'
4. Applied priority rule: active selling of transformative outcomes exceeds the evidence base
5. The text makes definitive claims about educational transformation based on limited pilot data

**Key Claims:**
- Text extrapolates from limited pilots to declare the obsolescence of an entire profession
- Selective metrics (test scores) are used to make claims about comprehensive educational effectiveness
- The certainty of language ('data-backed reality') far exceeds what pilot programs can establish

**Alternative Hypotheses:**
- mechanism_vs_evidence was considered due to the tier gap between pilots and system-wide conclusions
- However, the promotional certainty and sweeping claims ('all subjects,' 'obsolete,' 'dismantled') indicate rhetorical inflation beyond what any pilot could support

**Uncertainties:**
- The actual scope and methodology of the cited pilot programs
- Whether '65 percent rise' refers to a cherry-picked metric or representative outcome
- The duration and comprehensiveness of the studies behind these claims

**Self-Verification:**
- Confirmed the text makes sweeping, definitive claims not just cautious extrapolation
- The promotional language and certainty distinguish this from a mere evidence-tier mismatch
- The claims about 'all subjects' and teacher obsolescence go beyond any reasonable interpretation of pilot data

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.1/8 `#####.....`
- Assumption Discipline: 4.3/6 `#######...`
- Uncertainty Handling: 3.6/6 `######....`
- Alternative Hypothesis Quality: 5.2/6 `########..`
- Self Monitoring Quality: 4.8/8 `######....`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Opus** scored **71.5/100**.

**Best per dimension:**
- Correctness: Claude Opus (30.0/30)
- Support Strength: Claude Opus (0.0/8)
- Structural Reasoning: Claude Opus (4.1/8)
- Assumption Discipline: Claude Opus (4.3/6)
- Uncertainty Handling: Claude Opus (3.6/6)
- Alternative Hypothesis Quality: Claude Opus (5.2/6)
- Self Monitoring Quality: Claude Opus (4.8/8)
- Insight Depth: Claude Opus (8.0/8)
- Mechanism Quality: Claude Opus (1.5/10)
- Communication Efficiency: Claude Opus (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Opus | 17.0s | 71.5/100 | 4.2 |

Failure modes observed: decorative_uncertainty, named_not_explained, unsupported_conclusion, unsupported_intermediate_step, unused_assumption.
