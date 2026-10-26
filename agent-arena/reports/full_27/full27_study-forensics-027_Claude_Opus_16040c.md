# Forensic Dossier: Study Forensics: AI coding assistant productivity claims

**Run ID:** `full27_study-forensics-027_Claude_Opus_16040c`  
**Task:** study-forensics-027 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T17:03:41.967828+00:00  
**Task Family:** overclaim  
**Trap Type:** survivorship_bias_overclaim  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Opus
**Winner:** Claude Opus — **67.2/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, unsupported_conclusion, unsupported_intermediate_step, unused_assumption
**Forensic flags:** 3
**Consistency findings:** 9
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Opus | 30.0/30 | 0.0/8 | 4.8/8 | 3.4/6 | 3.3/6 | 5.2/6 | 2.4/8 | 8.0/8 | 0.0/10 | 10.0/10 | **67.2/100** |

## Study Forensics Audit

### Claude Opus

**Classification:** `overclaim` [+] (gold: `overclaim`)
**Finding Recall:** 100%
**Matched Findings:** conclusion_exceeds_results, unsupported_generalization
**Extra Findings:** cautious_scope_control, none_or_minor, correlation_as_causation

## Reasoning Integrity Audit

### Claude Opus
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 6

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
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 6
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[1]`: "Identified conclusion tier: Claims about 'fundamentally enhancing' productivity and 'reshaping software engineering work"
    _Most informative reasoning step_
  - Note: 6 reasoning steps
  - Note: Low step utility: 0/6 steps contribute

**Assumption Discipline:** 3.4/6
  - (+) `assumptions[0]`: "The study is observational (before/after comparison) rather than a controlled trial"
    _Most substantive assumption_
  - (-) `assumptions[3]`: "Code commits and PR completion times are the primary metrics used"
    _Declared but unused in reasoning_
  - Note: 4/4 substantive assumptions
  - Note: 1 unused assumption(s)

**Uncertainty Handling:** 3.3/6
  - (+) `uncertainties[2]`: "Whether confounders like project type or deadline pressure were controlled for"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.85"
    _Stated confidence level_
  - (-) `uncertainties[1]`: "The specific organizations and contexts studied"
    _Listed but never addressed in reasoning_
  - (-) `uncertainties[2]`: "Whether confounders like project type or deadline pressure were controlled for"
    _Listed but never addressed in reasoning_
  - Note: 3 uncertainties (3 substantive)
  - Note: 2 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 5.2/6
  - (+) `alternative_hypotheses[0]`: "correlation_vs_causation: The causal language from observational data is problematic"
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 1/2 include rejection reasoning

**Self Monitoring Quality:** 2.4/8
  - (+) `self_check[0]`: "Verified that the generalization from one tool to 'AI coding assistants' broadly is unsupported"
    _Most substantive self-verification step_
  - (-) `self_check[2]`: "Checked for control group mention - none found"
    _Fluff self-check_
  - Note: 4 self-check items
  - Note: Self-check quality: 0 deep, 2 arithmetic, 2 fluff

**Mechanism Quality:** 0.0/10
  - Note: Neither names concept nor explains mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.74, 264 words

**Insight Depth:** 4.0/8
  - (+) `(output text)`: "ather than a controlled trial no control group is mentioned, only baseline m"
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
- **Unused Assumption** `[HEURISTIC]`: Assumption 'Code commits and PR completion times are the primary metrics...' is declared but not referenced in reasoning
  - `assumptions[3]`: "Code commits and PR completion times are the primary metrics used"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'The specific organizations and contexts studied...' is listed but not addressed
  - `uncertainties[1]`: "The specific organizations and contexts studied"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether confounders like project type or deadline pressure w...' is listed but not addressed
  - `uncertainties[2]`: "Whether confounders like project type or deadline pressure were controlled for"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Opus

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/8 content words)
  - `key_claims[0]`: "Sweeping industry-wide conclusions from a study of one tool with 450 developers"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/8 content words)
  - `key_claims[1]`: "Causal attribution of productivity gains to AI tool without apparent randomization"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/7 content words)
  - `key_claims[2]`: "Recommendation for 'immediate enterprise adoption' exceeds the evidence scope"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/7 content words)
  - `key_claims[3]`: "No discussion of potential downsides, code quality, or technical debt"
- **[WARN]** `[HEURISTIC]` `claim_step_alignment`: Key claim 3 not well supported in reasoning steps (1/7 content words found)
  - `key_claims[2]`: "Recommendation for 'immediate enterprise adoption' exceeds the evidence scope"
- **[WARN]** `[HEURISTIC]` `claim_step_alignment`: Key claim 4 not well supported in reasoning steps (0/7 content words found)
  - `key_claims[3]`: "No discussion of potential downsides, code quality, or technical debt"
- **[WARN]** `[HEURISTIC]` `unused_assumption`: Assumption 4 appears unused in reasoning or answer
  - `assumptions[3]`: "Code commits and PR completion times are the primary metrics used"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 2 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[1]`: "The specific organizations and contexts studied"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "correlation_vs_causation: The causal language from observational data is problematic"


## Agent Profiles

### Claude Opus (claude-opus-4-20250514)
**Parse OK:** True | **Latency:** 18712ms

**Final Answer:** overclaim

**Confidence:** 0.85

**Assumptions:**
- The study is observational (before/after comparison) rather than a controlled trial
- No control group is mentioned, only baseline measurements
- The 450 developers likely come from a limited set of organizations
- Code commits and PR completion times are the primary metrics used

**Reasoning Steps:**
1. Identified evidence tier: 450 developers over 3 months is substantial but appears to be a single-arm observational study
2. Identified conclusion tier: Claims about 'fundamentally enhancing' productivity and 'reshaping software engineering workflows across the industry'
3. Examined methodology: Before/after comparison without apparent control group
4. Evaluated generalization: Study of one AI tool extrapolated to all AI coding assistants and entire industry
5. Assessed causal claims: 'AI assistant showed' and 'gains' imply causation from observational data
6. Checked for confounders: No mention of other factors that could affect productivity over 3 months

**Key Claims:**
- Sweeping industry-wide conclusions from a study of one tool with 450 developers
- Causal attribution of productivity gains to AI tool without apparent randomization
- Recommendation for 'immediate enterprise adoption' exceeds the evidence scope
- No discussion of potential downsides, code quality, or technical debt

**Alternative Hypotheses:**
- correlation_vs_causation: The causal language from observational data is problematic
- solid: If the study had appropriate controls not mentioned in the summary

**Uncertainties:**
- Whether the study had a control group not mentioned in this summary
- The specific organizations and contexts studied
- Whether confounders like project type or deadline pressure were controlled for

**Self-Verification:**
- Verified that the generalization from one tool to 'AI coding assistants' broadly is unsupported
- Confirmed the leap from observational study to industry-wide transformation claims
- Checked for control group mention - none found
- The 78% retention rate is positive but doesn't validate the broader claims

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 3.4/6 `#####.....`
- Uncertainty Handling: 3.3/6 `#####.....`
- Alternative Hypothesis Quality: 5.2/6 `########..`
- Self Monitoring Quality: 2.4/8 `###.......`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 0.0/10 `..........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Opus** scored **67.2/100**.

**Best per dimension:**
- Correctness: Claude Opus (30.0/30)
- Support Strength: Claude Opus (0.0/8)
- Structural Reasoning: Claude Opus (4.8/8)
- Assumption Discipline: Claude Opus (3.4/6)
- Uncertainty Handling: Claude Opus (3.3/6)
- Alternative Hypothesis Quality: Claude Opus (5.2/6)
- Self Monitoring Quality: Claude Opus (2.4/8)
- Insight Depth: Claude Opus (8.0/8)
- Mechanism Quality: Claude Opus (0.0/10)
- Communication Efficiency: Claude Opus (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Opus | 18.7s | 67.2/100 | 3.6 |

Failure modes observed: decorative_uncertainty, unsupported_conclusion, unsupported_intermediate_step, unused_assumption.
