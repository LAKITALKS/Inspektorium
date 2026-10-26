# Forensic Dossier: Study Forensics: AI instruction outperforms human teachers

**Run ID:** `full27_study-forensics-025_Claude_Opus_401107`  
**Task:** study-forensics-025 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T17:02:10.437077+00:00  
**Task Family:** overclaim  
**Trap Type:** media_inflated_overclaim  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Opus
**Winner:** Claude Opus — **68.7/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, unsupported_intermediate_step, unused_assumption
**Forensic flags:** 3
**Consistency findings:** 9
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Opus | 30.0/30 | 0.7/8 | 4.8/8 | 3.4/6 | 3.3/6 | 4.5/6 | 4.0/8 | 8.0/8 | 0.0/10 | 10.0/10 | **68.7/100** |

## Study Forensics Audit

### Claude Opus

**Classification:** `overclaim` [+] (gold: `overclaim`)
**Finding Recall:** 100%
**Matched Findings:** conclusion_exceeds_results, unsupported_generalization
**Extra Findings:** cautious_scope_control

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

**Support Strength:** 1.2/8
  - (+) `final_answer`: "overclaim"
    _Conclusion grounded by reasoning chain_
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 6
  - Note: Reasoning graph confirms conclusion grounding

**Structural Reasoning:** 4.8/8
  - (+) `steps[1]`: "Identified conclusion tier: claims about AI making teachers obsolete across 'all subjects' and representing 'data-backed"
    _Most informative reasoning step_
  - Note: 6 reasoning steps
  - Note: Low step utility: 0/6 steps contribute

**Assumption Discipline:** 3.4/6
  - (+) `assumptions[2]`: "The pilot programs were limited in scope (specific subjects, specific contexts) rather than comprehensive educational im"
    _Most substantive assumption_
  - (-) `assumptions[1]`: "The '65 percent rise in test scores' and 'two-times learning effect' are actual reported metrics from these pilots"
    _Declared but unused in reasoning_
  - Note: 3/3 substantive assumptions
  - Note: 1 unused assumption(s)

**Uncertainty Handling:** 3.3/6
  - (+) `uncertainties[1]`: "Whether '65 percent rise' is a maximum outlier or average result"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.9"
    _Stated confidence level_
  - (-) `uncertainties[1]`: "Whether '65 percent rise' is a maximum outlier or average result"
    _Listed but never addressed in reasoning_
  - (-) `uncertainties[2]`: "Duration and sustainability of the reported effects"
    _Listed but never addressed in reasoning_
  - Note: 4 uncertainties (4 substantive)
  - Note: 2 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 4.5/6
  - (+) `alternative_hypotheses[1]`: "solid if the article had stayed within the bounds of what the pilots actually showed"
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 2/2 genuinely diverse alternatives

**Self Monitoring Quality:** 4.0/8
  - (+) `self_check[1]`: "Confirmed the bridge step is unsupported - pilot success in limited contexts doesn't justify claims about dismantling en"
    _Most substantive self-verification step_
  - Note: 3 self-check items
  - Note: Self-check quality: 0 deep, 3 arithmetic, 0 fluff

**Mechanism Quality:** 0.0/10
  - Note: Neither names concept nor explains mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.79, 281 words

**Insight Depth:** 4.0/8
  - (?) `(not found)`: "Missing: no methodology"
    _Insight 'no methodology' not found_
  - Note: Key insights: 1 full / 2


## Failure Analysis

### Claude Opus

**MODERATE:**
- **Unsupported Intermediate Step** `[MEDIUM CONFIDENCE]`: No reasoning step is load-bearing — final answer lacks traceable derivation
  - `final_answer`: "overclaim"
  - _Impacts: support_strength, structural_reasoning_

**STYLISTIC:**
- **Unused Assumption** `[HEURISTIC]`: Assumption 'The '65 percent rise in test scores' and 'two-times learning...' is declared but not referenced in reasoning
  - `assumptions[1]`: "The '65 percent rise in test scores' and 'two-times learning effect' are actual reported metrics fro"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether '65 percent rise' is a maximum outlier or average re...' is listed but not addressed
  - `uncertainties[1]`: "Whether '65 percent rise' is a maximum outlier or average result"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Duration and sustainability of the reported effects...' is listed but not addressed
  - `uncertainties[2]`: "Duration and sustainability of the reported effects"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Opus

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/10 content words)
  - `key_claims[0]`: "Article makes sweeping claims about teacher obsolescence based on limited pilot data"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/8 content words)
  - `key_claims[1]`: "Generalizes from specific subjects (physics, math, literacy) to all education"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/7 content words)
  - `key_claims[2]`: "Presents preliminary pilot results as established 'data-backed reality'"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/8 content words)
  - `key_claims[3]`: "Ignores the gap between controlled pilot performance and system-wide educational transformation"
- **[WARN]** `[HEURISTIC]` `claim_step_alignment`: Key claim 4 not well supported in reasoning steps (1/8 content words found)
  - `key_claims[3]`: "Ignores the gap between controlled pilot performance and system-wide educational transformation"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 2 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[1]`: "Whether '65 percent rise' is a maximum outlier or average result"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 3 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[2]`: "Duration and sustainability of the reported effects"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "mechanism_vs_evidence if the pilots were very early-stage or proof-of-concept"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 2 is stated without rejection reasoning
  - `alternative_hypotheses[1]`: "solid if the article had stayed within the bounds of what the pilots actually showed"


## Agent Profiles

### Claude Opus (claude-opus-4-20250514)
**Parse OK:** True | **Latency:** 18309ms

**Final Answer:** overclaim

**Confidence:** 0.9

**Assumptions:**
- The article references real pilot programs rather than hypothetical ones
- The '65 percent rise in test scores' and 'two-times learning effect' are actual reported metrics from these pilots
- The pilot programs were limited in scope (specific subjects, specific contexts) rather than comprehensive educational implementations

**Reasoning Steps:**
1. Identified evidence tier: pilot programs in US/UK constitute limited human evidence
2. Identified conclusion tier: claims about AI making teachers obsolete across 'all subjects' and representing 'data-backed reality' for entire education system
3. Detected bridge step: from limited pilot data in specific subjects (physics, math, literacy) to sweeping claims about all education
4. Evaluated specific overclaims: 'rapidly making human teachers obsolete' and 'dismantled' role of educators exceed pilot program evidence
5. Noted cherry-picking: article cites only positive metrics without mentioning limitations, sample sizes, or negative outcomes
6. Identified generalization: from three specific subjects to 'all subjects'

**Key Claims:**
- Article makes sweeping claims about teacher obsolescence based on limited pilot data
- Generalizes from specific subjects (physics, math, literacy) to all education
- Presents preliminary pilot results as established 'data-backed reality'
- Ignores the gap between controlled pilot performance and system-wide educational transformation

**Alternative Hypotheses:**
- mechanism_vs_evidence if the pilots were very early-stage or proof-of-concept
- solid if the article had stayed within the bounds of what the pilots actually showed

**Uncertainties:**
- Actual scope and quality of the pilot programs referenced
- Whether '65 percent rise' is a maximum outlier or average result
- Duration and sustainability of the reported effects
- Whether negative results from pilots were omitted

**Self-Verification:**
- Verified this is overclaim rather than mechanism_vs_evidence because actual human pilot data exists
- Confirmed the bridge step is unsupported - pilot success in limited contexts doesn't justify claims about dismantling entire profession
- Did not fabricate problems - the text genuinely makes claims beyond its evidence base

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.7/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 3.4/6 `#####.....`
- Uncertainty Handling: 3.3/6 `#####.....`
- Alternative Hypothesis Quality: 4.5/6 `#######...`
- Self Monitoring Quality: 4.0/8 `#####.....`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 0.0/10 `..........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Opus** scored **68.7/100**.

**Best per dimension:**
- Correctness: Claude Opus (30.0/30)
- Support Strength: Claude Opus (0.7/8)
- Structural Reasoning: Claude Opus (4.8/8)
- Assumption Discipline: Claude Opus (3.4/6)
- Uncertainty Handling: Claude Opus (3.3/6)
- Alternative Hypothesis Quality: Claude Opus (4.5/6)
- Self Monitoring Quality: Claude Opus (4.0/8)
- Insight Depth: Claude Opus (8.0/8)
- Mechanism Quality: Claude Opus (0.0/10)
- Communication Efficiency: Claude Opus (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Opus | 18.3s | 68.7/100 | 3.8 |

Failure modes observed: decorative_uncertainty, unsupported_intermediate_step, unused_assumption.
