# Forensic Dossier: Study Forensics: Vitamin D supplements and long COVID

**Run ID:** `pilot_9843bc50`  
**Task:** study-forensics-007 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-06T08:18:57.820524+00:00  
**Task Family:** overclaim  
**Trap Type:** small_effect_overinterpretation  
**Ambiguity:** medium  

## Executive Summary

**Agents tested:** synthetic
**Winner:** synthetic — **74.9/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty
**Forensic flags:** 1
**Consistency findings:** 4
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| synthetic | 30.0/30 | 2.2/8 | 7.6/8 | 4.8/6 | 3.6/6 | 3.3/6 | 2.4/8 | 8.0/8 | 3.0/10 | 10.0/10 | **74.9/100** |

## Study Forensics Audit

### synthetic

**Classification:** `overclaim` [+] (gold: `overclaim`)
**Finding Recall:** 100%
**Matched Findings:** conclusion_exceeds_results, decorative_uncertainty
**Extra Findings:** none_or_minor, correlation_as_causation

## Reasoning Integrity Audit

### synthetic
**Classification:** Correct and well-supported
**Load-bearing steps:** 1 / 6

## Mechanism Analysis

### synthetic
| Aspect | Status |
|--------|--------|
| Concept named | :x: none |
| Mechanism described | :white_check_mark: (1 sentence(s)) |
| Grounded to case | :x: (0 sentence(s)) |

**Missing:** concept not named, mechanism not grounded to case data

## Grounding Audit

### synthetic
Conclusion claims: 4
- Direct support: 0
- Indirect support: 4
- Unsupported: 0
- Contradicted: 0


## Forensic Flags

### synthetic

- **[MAJOR]** `unsupported_leap`: Correct answer with weak support chain — final answer may be an unsupported leap


## Evidence Map

### synthetic

**Correctness:** 27.0/30
  - (+) `final_answer`: "This is an overclaim case. The primary outcome (acute infection severity) was null. The secondary finding (4 percentage "
    _Agent's answer for correctness check_
  - Note: Contains expected answer

**Support Strength:** 2.2/8
  - (+) `final_answer`: "This is an overclaim case. The primary outcome (acute infection severity) was null. The secondary finding (4 percentage "
    _Conclusion grounded by reasoning chain_
  - Note: Support classification: 0 load-bearing, 0 supporting, 4 mentioned / 6
  - Note: Steps mention answer words but don't clearly support it

**Structural Reasoning:** 7.6/8
  - (+) `steps[3]`: "The phrase 'larger trials are needed' is decorative uncertainty — it accompanies but does not constrain the optimistic f"
    _Most informative reasoning step_
  - Note: 6 reasoning steps
  - Note: Step utility: 6/6 steps contribute to answer

**Assumption Discipline:** 4.8/6
  - (+) `assumptions[0]`: "The trial was properly conducted despite being remote"
    _Most substantive assumption_
  - Note: 2/2 substantive assumptions

**Uncertainty Handling:** 3.6/6
  - (+) `uncertainties[0]`: "Statistical significance of the 4pp difference is not stated"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.8"
    _Stated confidence level_
  - (-) `uncertainties[1]`: "Remote conduct may introduce unmeasured biases"
    _Listed but never addressed in reasoning_
  - Note: 2 uncertainties (2 substantive)
  - Note: 1 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 3.3/6
  - (+) `alternative_hypotheses[0]`: "Could this be solid? No — the null primary outcome and small secondary effect don't warrant 'promising signal'."
    _Most substantive alternative hypothesis_
  - Note: 1 alternative hypotheses considered

**Self Monitoring Quality:** 2.4/8
  - (+) `self_check[0]`: "Am I being too harsh? The authors do hedge — but the framing is still optimistic beyond the data."
    _Most substantive self-verification step_
  - Note: 1 self-check items
  - Note: Self-check quality: 0 deep, 1 arithmetic, 0 fluff

**Mechanism Quality:** 3.0/10
  - (+) `(mechanism analysis)`: "Overall: mild overclaim driven by framing a weak secondary result as promising."
    _Mechanism description_
  - Note: Describes mechanism but does not name concept

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.71, 203 words

**Insight Depth:** 8.0/8
  - (+) `(output text)`: "could this be solid? no — the null primary outcome and small secondary effect do"
    _Insight 'null primary outcome' matched (exact)_
  - (+) `(output text)`: "entage point difference. this small absolute difference is described as a 'promising"
    _Insight 'small absolute difference' matched (exact)_
  - Note: Key insights: 3 full / 3


## Failure Analysis

### synthetic

**STYLISTIC:**
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Remote conduct may introduce unmeasured biases...' is listed but not addressed
  - `uncertainties[1]`: "Remote conduct may introduce unmeasured biases"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### synthetic

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/3 content words)
  - `key_claims[1]`: "The conclusion exceeds the results"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 2 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[1]`: "Remote conduct may introduce unmeasured biases"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "Could this be solid? No — the null primary outcome and small secondary effect don't warrant 'promisi"
- **[NOTE]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Causal mechanism described but underlying concept not named
  - `final_answer`: "This is an overclaim case. The primary outcome (acute infection severity) was null. The secondary fi"


## Agent Profiles

### synthetic (synthetic-pilot-v1)
**Parse OK:** True | **Latency:** 0ms

**Final Answer:** This is an overclaim case. The primary outcome (acute infection severity) was null. The secondary finding (4 percentage points difference in lingering symptoms) is very small and framed with misleading optimism. The uncertainty language is decorative.

**Confidence:** 0.8

**Assumptions:**
- The trial was properly conducted despite being remote
- 21% vs 25% is the accurate reported difference

**Reasoning Steps:**
1. Primary outcome was null: vitamin D did not change acute infection severity.
2. Secondary outcome: 21% vs 25% — a 4 percentage point difference.
3. This small absolute difference is described as a 'promising signal' — this conclusion exceeds the results.
4. The phrase 'larger trials are needed' is decorative uncertainty — it accompanies but does not constrain the optimistic framing.
5. Study started supplementation after infection onset, limiting causal interpretation.
6. Overall: mild overclaim driven by framing a weak secondary result as promising.

**Key Claims:**
- Primary outcome was null — acute COVID-19 severity unchanged
- The conclusion exceeds the results
- Uncertainty language is decorative, not constraining

**Alternative Hypotheses:**
- Could this be solid? No — the null primary outcome and small secondary effect don't warrant 'promising signal'.

**Uncertainties:**
- Statistical significance of the 4pp difference is not stated
- Remote conduct may introduce unmeasured biases

**Self-Verification:**
- Am I being too harsh? The authors do hedge — but the framing is still optimistic beyond the data.

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 2.2/8 `##........`
- Structural Reasoning: 7.6/8 `#########.`
- Assumption Discipline: 4.8/6 `########..`
- Uncertainty Handling: 3.6/6 `######....`
- Alternative Hypothesis Quality: 3.3/6 `#####.....`
- Self Monitoring Quality: 2.4/8 `###.......`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 3.0/10 `###.......`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: synthetic** scored **74.9/100**.

**Best per dimension:**
- Correctness: synthetic (30.0/30)
- Support Strength: synthetic (2.2/8)
- Structural Reasoning: synthetic (7.6/8)
- Assumption Discipline: synthetic (4.8/6)
- Uncertainty Handling: synthetic (3.6/6)
- Alternative Hypothesis Quality: synthetic (3.3/6)
- Self Monitoring Quality: synthetic (2.4/8)
- Insight Depth: synthetic (8.0/8)
- Mechanism Quality: synthetic (3.0/10)
- Communication Efficiency: synthetic (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| synthetic | 0.0s | 74.9/100 | 0.0 |

Failure modes observed: decorative_uncertainty.
