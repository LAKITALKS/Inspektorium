# Forensic Dossier: Study Forensics: AI coding assistant productivity claims

**Run ID:** `praxis_study-forensics-027_Claude_Opus_5dd40b`  
**Task:** study-forensics-027 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-07T07:54:56.909773+00:00  
**Task Family:** overclaim  
**Trap Type:** survivorship_bias_overclaim  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Opus
**Winner:** Claude Opus — **65.7/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, unsupported_conclusion, unsupported_intermediate_step, unused_assumption
**Forensic flags:** 3
**Consistency findings:** 10
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Opus | 30.0/30 | 0.0/8 | 4.8/8 | 3.4/6 | 3.0/6 | 5.2/6 | 1.2/8 | 8.0/8 | 0.0/10 | 10.0/10 | **65.7/100** |

## Study Forensics Audit

### Claude Opus

**Classification:** `overclaim` [+] (gold: `overclaim`)
**Finding Recall:** 100%
**Matched Findings:** conclusion_exceeds_results, unsupported_generalization
**Extra Findings:** cautious_scope_control, correlation_as_causation

## Reasoning Integrity Audit

### Claude Opus
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 7

## Mechanism Analysis

### Claude Opus
| Aspect | Status |
|--------|--------|
| Concept named | :x: none |
| Mechanism described | :x: (0 sentence(s)) |
| Grounded to case | :x: (0 sentence(s)) |

**Missing:** concept not named, mechanism not described, mechanism not grounded to case data

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


## Evidence Map

### Claude Opus

**Correctness:** 30.0/30
  - (+) `final_answer`: "overclaim"
    _Agent's answer for correctness check_
  - Note: Exact match

**Support Strength:** 0.0/8
  - (-) `final_answer`: "overclaim"
    _Conclusion not supported by steps_
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 7
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[2]`: "Observed strong causal language: 'AI coding assistants fundamentally enhance developer productivity'"
    _Most informative reasoning step_
  - Note: 7 reasoning steps
  - Note: Low step utility: 0/7 steps contribute

**Assumption Discipline:** 3.4/6
  - (+) `assumptions[3]`: "Baseline measurements were taken on the same developers before tool adoption"
    _Most substantive assumption_
  - (-) `assumptions[2]`: "The 22% who stopped using the tool may have had different experiences"
    _Declared but unused in reasoning_
  - Note: 4/4 substantive assumptions
  - Note: 1 unused assumption(s)

**Uncertainty Handling:** 3.0/6
  - (+) `uncertainties[3]`: "If the 'baseline measurements' were truly comparable conditions"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.85"
    _Stated confidence level_
  - (-) `uncertainties[1]`: "What happened with the 22% who stopped using the tool"
    _Listed but never addressed in reasoning_
  - (-) `uncertainties[2]`: "Whether other factors changed during the 3-month period"
    _Listed but never addressed in reasoning_
  - Note: 4 uncertainties (4 substantive)
  - Note: 3 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 5.2/6
  - (+) `alternative_hypotheses[1]`: "correlation_vs_causation - though the temporal sequence suggests some causal inference is reasonable"
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 1/2 include rejection reasoning

**Self Monitoring Quality:** 1.2/8
  - (+) `self_check[3]`: "Ensured I'm not assuming problems that aren't indicated in the text"
    _Most substantive self-verification step_
  - (-) `self_check[0]`: "Verified the text doesn't mention a control group"
    _Fluff self-check_
  - Note: 4 self-check items
  - Note: Self-check quality: 0 deep, 1 arithmetic, 3 fluff

**Mechanism Quality:** 0.0/10
  - Note: Neither names concept nor explains mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.79, 234 words

**Insight Depth:** 4.0/8
  - (+) `(output text)`: "re and after ai tool adoption no control group is mentioned in the text the"
    _Insight 'no control group' matched (exact)_
  - (?) `(not found)`: "Missing: survivorship bias"
    _Insight 'survivorship bias' not found_
  - Note: Key insights: 1 full / 2


## Failure Analysis

### Claude Opus

**MODERATE:**
- **Unsupported Conclusion** `[MEDIUM CONFIDENCE]`: Final answer lacks load-bearing or supporting step grounding
  - `final_answer`: "overclaim"
  - _Impacts: support_strength_
- **Unsupported Intermediate Step** `[MEDIUM CONFIDENCE]`: No reasoning step is load-bearing — final answer lacks traceable derivation
  - `final_answer`: "overclaim"
  - _Impacts: support_strength, structural_reasoning_

**STYLISTIC:**
- **Unused Assumption** `[HEURISTIC]`: Assumption 'The 22% who stopped using the tool may have had different ex...' is declared but not referenced in reasoning
  - `assumptions[2]`: "The 22% who stopped using the tool may have had different experiences"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'What happened with the 22% who stopped using the tool...' is listed but not addressed
  - `uncertainties[1]`: "What happened with the 22% who stopped using the tool"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether other factors changed during the 3-month period...' is listed but not addressed
  - `uncertainties[2]`: "Whether other factors changed during the 3-month period"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'If the 'baseline measurements' were truly comparable conditi...' is listed but not addressed
  - `uncertainties[3]`: "If the 'baseline measurements' were truly comparable conditions"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Opus

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/8 content words)
  - `key_claims[0]`: "Study makes industry-wide predictions from single tool evaluation"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/5 content words)
  - `key_claims[1]`: "Ignores potential confounders in before/after design"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/6 content words)
  - `key_claims[2]`: "Dismisses 22% dropout rate when claiming universal applicability"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/7 content words)
  - `key_claims[3]`: "Recommends immediate enterprise adoption based on limited evidence"
- **[WARN]** `[HEURISTIC]` `claim_step_alignment`: Key claim 4 not well supported in reasoning steps (0/7 content words found)
  - `key_claims[3]`: "Recommends immediate enterprise adoption based on limited evidence"
- **[WARN]** `[HEURISTIC]` `unused_assumption`: Assumption 3 appears unused in reasoning or answer
  - `assumptions[2]`: "The 22% who stopped using the tool may have had different experiences"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 2 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[1]`: "What happened with the 22% who stopped using the tool"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 3 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[2]`: "Whether other factors changed during the 3-month period"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 4 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[3]`: "If the 'baseline measurements' were truly comparable conditions"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 2 is stated without rejection reasoning
  - `alternative_hypotheses[1]`: "correlation_vs_causation - though the temporal sequence suggests some causal inference is reasonable"


## Agent Profiles

### Claude Opus (claude-opus-4-20250514)
**Parse OK:** True | **Latency:** 14468ms

**Final Answer:** overclaim

**Confidence:** 0.85

**Assumptions:**
- The study measured productivity before and after AI tool adoption
- No control group is mentioned in the text
- The 22% who stopped using the tool may have had different experiences
- Baseline measurements were taken on the same developers before tool adoption

**Reasoning Steps:**
1. Identified the study design: before/after comparison with 450 developers
2. Noted specific metrics: code commits, PR completion times, feature velocity
3. Observed strong causal language: 'AI coding assistants fundamentally enhance developer productivity'
4. Checked for control group: none mentioned
5. Evaluated the scope of conclusions: study of one tool extended to entire industry
6. Examined retention data: 22% dropout rate not addressed in conclusions
7. Assessed generalization: single tool study used to recommend all 'AI coding assistants'

**Key Claims:**
- Study makes industry-wide predictions from single tool evaluation
- Ignores potential confounders in before/after design
- Dismisses 22% dropout rate when claiming universal applicability
- Recommends immediate enterprise adoption based on limited evidence

**Alternative Hypotheses:**
- solid - if there were proper controls not mentioned in the summary
- correlation_vs_causation - though the temporal sequence suggests some causal inference is reasonable

**Uncertainties:**
- Whether a control group existed but wasn't mentioned
- What happened with the 22% who stopped using the tool
- Whether other factors changed during the 3-month period
- If the 'baseline measurements' were truly comparable conditions

**Self-Verification:**
- Verified the text doesn't mention a control group
- Confirmed the causal language is explicit
- Checked if caveats were present - none found
- Ensured I'm not assuming problems that aren't indicated in the text

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 3.4/6 `#####.....`
- Uncertainty Handling: 3.0/6 `####......`
- Alternative Hypothesis Quality: 5.2/6 `########..`
- Self Monitoring Quality: 1.2/8 `#.........`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 0.0/10 `..........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Opus** scored **65.7/100**.

**Best per dimension:**
- Correctness: Claude Opus (30.0/30)
- Support Strength: Claude Opus (0.0/8)
- Structural Reasoning: Claude Opus (4.8/8)
- Assumption Discipline: Claude Opus (3.4/6)
- Uncertainty Handling: Claude Opus (3.0/6)
- Alternative Hypothesis Quality: Claude Opus (5.2/6)
- Self Monitoring Quality: Claude Opus (1.2/8)
- Insight Depth: Claude Opus (8.0/8)
- Mechanism Quality: Claude Opus (0.0/10)
- Communication Efficiency: Claude Opus (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Opus | 14.5s | 65.7/100 | 4.5 |

Failure modes observed: decorative_uncertainty, unsupported_conclusion, unsupported_intermediate_step, unused_assumption.
