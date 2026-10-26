# Forensic Dossier: Study Forensics: AI instruction outperforms human teachers

**Run ID:** `praxis_study-forensics-025_Claude_Opus_1daf11`  
**Task:** study-forensics-025 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-07T07:53:32.949322+00:00  
**Task Family:** overclaim  
**Trap Type:** media_inflated_overclaim  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Opus
**Winner:** Claude Opus — **71.5/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, named_not_explained, unsupported_conclusion, unsupported_intermediate_step, unused_assumption
**Forensic flags:** 4
**Consistency findings:** 10
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Opus | 30.0/30 | 0.0/8 | 4.8/8 | 4.3/6 | 3.6/6 | 4.5/6 | 4.8/8 | 8.0/8 | 1.5/10 | 10.0/10 | **71.5/100** |

## Study Forensics Audit

### Claude Opus

**Classification:** `overclaim` [+] (gold: `overclaim`)
**Finding Recall:** 100%
**Matched Findings:** conclusion_exceeds_results, unsupported_generalization
**Extra Findings:** cautious_scope_control, correlation_as_causation

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
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 6
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[0]`: "First, I identified the key claims: AI systems making teachers obsolete, 65% test score improvements, 2x learning effect"
    _Most informative reasoning step_
  - Note: 6 reasoning steps
  - Note: Low step utility: 0/6 steps contribute

**Assumption Discipline:** 4.3/6
  - (+) `assumptions[1]`: "The '65 percent rise in test scores' and 'two-times learning effect' are being presented as generalizable findings"
    _Most substantive assumption_
  - (-) `assumptions[1]`: "The '65 percent rise in test scores' and 'two-times learning effect' are being presented as generalizable findings"
    _Declared but unused in reasoning_
  - Note: 4/4 substantive assumptions
  - Note: 1 unused assumption(s)

**Uncertainty Handling:** 3.6/6
  - (+) `uncertainties[3]`: "Whether the 65% improvement claim comes from a single study or multiple sources"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.92"
    _Stated confidence level_
  - (-) `uncertainties[1]`: "Whether 'some reports' means peer-reviewed studies or informal observations"
    _Listed but never addressed in reasoning_
  - Note: 4 uncertainties (4 substantive)
  - Note: 1 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 4.5/6
  - (+) `alternative_hypotheses[0]`: "correlation_vs_causation - the article might be confusing correlation between AI use and test scores with causation"
    _Most substantive alternative hypothesis_
  - Note: 3 alternative hypotheses considered
  - Note: 3/3 genuinely diverse alternatives

**Self Monitoring Quality:** 4.8/8
  - (+) `self_check[2]`: "I did not invent problems - the overclaiming is explicit in phrases like 'all subjects' and 'obsolete'"
    _Most substantive self-verification step_
  - Note: 4 self-check items
  - Note: Self-check quality: 0 deep, 4 arithmetic, 0 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.70, 382 words

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
  - `assumptions[1]`: "The '65 percent rise in test scores' and 'two-times learning effect' are being presented as generali"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether 'some reports' means peer-reviewed studies or inform...' is listed but not addressed
  - `uncertainties[1]`: "Whether 'some reports' means peer-reviewed studies or informal observations"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Opus

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/9 content words)
  - `key_claims[0]`: "The article makes sweeping generalizations from pilot programs to all educational contexts"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/10 content words)
  - `key_claims[1]`: "Strong causal claims ('making obsolete', 'dismantling') are made without sufficient evidence"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/10 content words)
  - `key_claims[2]`: "The scope is dramatically expanded from three subjects to 'all subjects' without justification"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/5 content words)
  - `key_claims[3]`: "No limitations, confounders, or contextual factors are acknowledged"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 5 has low overlap with final answer (0/9 content words)
  - `key_claims[4]`: "The phrase 'data-backed reality' overstates the certainty given only pilot program evidence"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 2 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[1]`: "Whether 'some reports' means peer-reviewed studies or informal observations"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "correlation_vs_causation - the article might be confusing correlation between AI use and test scores"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 2 is stated without rejection reasoning
  - `alternative_hypotheses[1]`: "solid - if the pilot programs were comprehensive and the article is accurately reporting their findi"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 3 is stated without rejection reasoning
  - `alternative_hypotheses[2]`: "mechanism_vs_evidence - if the article is extrapolating from how AI works in theory to how it perfor"
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "overclaim"


## Agent Profiles

### Claude Opus (claude-opus-4-20250514)
**Parse OK:** True | **Latency:** 21166ms

**Final Answer:** overclaim

**Confidence:** 0.92

**Assumptions:**
- The article is accurately representing the claims about AI tutoring systems
- The '65 percent rise in test scores' and 'two-times learning effect' are being presented as generalizable findings
- The pilot programs mentioned are real but their scope and methodology are not detailed
- The article is making broad claims about AI replacing teachers based on limited evidence

**Reasoning Steps:**
1. First, I identified the key claims: AI systems making teachers obsolete, 65% test score improvements, 2x learning effectiveness, and dismantling of educators' role
2. Second, I noted the evidence base: only 'pilot programs' in US and UK are cited, with no details on sample size, duration, or methodology
3. Third, I observed the scope of claims: the article generalizes from specific subjects (physics, math, literacy) to 'all subjects'
4. Fourth, I analyzed the causal language: 'making teachers obsolete' and 'dismantling the role of educators' are strong causal claims
5. Fifth, I noted the lack of caveats: no mention of limitations, confounders, or contexts where AI might not work
6. Finally, I identified the mismatch between limited pilot data and sweeping conclusions about educational transformation

**Key Claims:**
- The article makes sweeping generalizations from pilot programs to all educational contexts
- Strong causal claims ('making obsolete', 'dismantling') are made without sufficient evidence
- The scope is dramatically expanded from three subjects to 'all subjects' without justification
- No limitations, confounders, or contextual factors are acknowledged
- The phrase 'data-backed reality' overstates the certainty given only pilot program evidence

**Alternative Hypotheses:**
- correlation_vs_causation - the article might be confusing correlation between AI use and test scores with causation
- solid - if the pilot programs were comprehensive and the article is accurately reporting their findings
- mechanism_vs_evidence - if the article is extrapolating from how AI works in theory to how it performs in practice

**Uncertainties:**
- The actual methodology and scope of the pilot programs referenced
- Whether 'some reports' means peer-reviewed studies or informal observations
- The specific contexts and conditions under which these results were obtained
- Whether the 65% improvement claim comes from a single study or multiple sources

**Self-Verification:**
- I verified that the text does make broad claims about obsolescence based on limited pilot data
- I confirmed there are no mentioned caveats or limitations in the summary
- I did not invent problems - the overclaiming is explicit in phrases like 'all subjects' and 'obsolete'
- The mismatch between evidence (pilots) and conclusions (dismantling education) is clear

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 4.3/6 `#######...`
- Uncertainty Handling: 3.6/6 `######....`
- Alternative Hypothesis Quality: 4.5/6 `#######...`
- Self Monitoring Quality: 4.8/8 `######....`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Opus** scored **71.5/100**.

**Best per dimension:**
- Correctness: Claude Opus (30.0/30)
- Support Strength: Claude Opus (0.0/8)
- Structural Reasoning: Claude Opus (4.8/8)
- Assumption Discipline: Claude Opus (4.3/6)
- Uncertainty Handling: Claude Opus (3.6/6)
- Alternative Hypothesis Quality: Claude Opus (4.5/6)
- Self Monitoring Quality: Claude Opus (4.8/8)
- Insight Depth: Claude Opus (8.0/8)
- Mechanism Quality: Claude Opus (1.5/10)
- Communication Efficiency: Claude Opus (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Opus | 21.2s | 71.5/100 | 3.4 |

Failure modes observed: decorative_uncertainty, named_not_explained, unsupported_conclusion, unsupported_intermediate_step, unused_assumption.
