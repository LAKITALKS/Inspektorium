# Forensic Dossier: Study Forensics: Vitamin D supplements and long COVID

**Run ID:** `full27_study-forensics-007_Claude_Haiku_739d08`  
**Task:** study-forensics-007 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T16:56:15.476383+00:00  
**Task Family:** solid  
**Trap Type:** overflagging_decorative_uncertainty  
**Ambiguity:** medium  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **64.7/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, missed_key_insight, named_not_explained, overclaiming, unsupported_conclusion, unsupported_intermediate_step
**Forensic flags:** 6
**Consistency findings:** 6
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 25.5/30 | 0.0/8 | 4.8/8 | 4.8/6 | 3.6/6 | 6.0/6 | 7.2/8 | 2.8/8 | 1.5/10 | 8.5/10 | **64.7/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `solid` [+] (gold: `solid`)
**Finding Recall:** 50%
**Matched Findings:** cautious_scope_control
**Missed Findings:** evidence_matches_claim
**Extra Findings:** none_or_minor, conclusion_exceeds_results, unsupported_generalization, decorative_uncertainty, mechanism_not_demonstrated
**False Positives:** overclaim

## Reasoning Integrity Audit

### Claude Haiku
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 8

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

- **[MODERATE]** `pattern_match_suspect`: Correct answer with shallow insight coverage — possible pattern-match response
  - `final_answer`: "solid"
- **[MODERATE]** `weak_mechanism`: Correct answer but weak mechanism explanation — answer may not generalize
  - `final_answer`: "solid"
- **[MAJOR]** `unsupported_leap`: Correct answer with weak support chain — final answer may be an unsupported leap
- **[MODERATE]** `unsupported_conclusion_claims`: 1/1 conclusion claims lack step support
  - `final_answer`: "solid"
- **[MODERATE]** `ungrounded_mechanism`: Mechanism named/described but not connected to case-specific data
  - `(mechanism analysis)`: "effect"
- **[MINOR]** `study_forensics_overflagging`: Agent raised extra findings in solid case: none_or_minor, conclusion_exceeds_results, unsupported_generalization, decorative_uncertainty, mechanism_not_demonstrated


## Evidence Map

### Claude Haiku

**Correctness:** 30.0/30
  - (+) `final_answer`: "solid"
    _Agent's answer for correctness check_
  - Note: Exact match

**Support Strength:** 0.0/8
  - (-) `final_answer`: "solid"
    _Conclusion not supported by steps_
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 8
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[7]`: "Evaluated overclaim risk: The 'promising signal' language is cautious and paired with explicit call for larger trials; n"
    _Most informative reasoning step_
  - Note: 8 reasoning steps
  - Note: Low step utility: 0/8 steps contribute

**Assumption Discipline:** 4.8/6
  - (+) `assumptions[3]`: "The 4-percentage-point difference (25% vs 21%) in lingering symptoms is being presented as exploratory, not confirmatory"
    _Most substantive assumption_
  - Note: 4/4 substantive assumptions

**Uncertainty Handling:** 3.6/6
  - (+) `uncertainties[3]`: "The clinical significance of a 4-point difference in lingering symptoms (is this meaningful to patients?)"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.82"
    _Stated confidence level_
  - (-) `uncertainties[1]`: "Whether multiple comparisons were conducted and whether correction was applied"
    _Listed but never addressed in reasoning_
  - Note: 5 uncertainties (5 substantive)
  - Note: 1 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 6.0/6
  - (+) `alternative_hypotheses[0]`: "Could classify as overclaim if 'promising signal' is viewed as too strong for a 4-point difference in a secondary endpoi"
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 2/2 include rejection reasoning

**Self Monitoring Quality:** 7.2/8
  - (+) `self_check[5]`: "Is the hedging decorative or substantive? Substantive — the limitations (remote, post-infection) are real constraints on"
    _Most substantive self-verification step_
  - Note: 6 self-check items
  - Note: Self-check quality: 1 deep, 5 arithmetic, 0 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 8.5/10
  - Note: Signal density: 0.70, 527 words

**Insight Depth:** 2.7/8
  - (?) `(not found)`: "Missing: honest reporting"
    _Insight 'honest reporting' not found_
  - Note: Key insights: 1 full / 3


## Failure Analysis

### Claude Haiku

**MAJOR:**
- **Overclaiming** `[HEURISTIC]`: False positive: agent flagged 'overclaim' in a solid case
  - `final_answer`: "solid"
  - _Impacts: correctness_

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
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether multiple comparisons were conducted and whether corr...' is listed but not addressed
  - `uncertainties[1]`: "Whether multiple comparisons were conducted and whether correction was applied"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/9 content words)
  - `key_claims[0]`: "Primary endpoint (acute severity): No effect — this is a negative result for the main hypothesis"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/11 content words)
  - `key_claims[1]`: "Secondary endpoint (lingering symptoms at 8 weeks): 4-percentage-point difference favoring vitamin D"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/10 content words)
  - `key_claims[2]`: "Framing: Described as 'promising signal' but explicitly caveated with call for larger trials"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/9 content words)
  - `key_claims[3]`: "Limitations acknowledged: Remote conduct and post-infection supplementation timing limit interpretat"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 5 has low overlap with final answer (0/10 content words)
  - `key_claims[4]`: "No mechanism claimed: The text does not explain *how* vitamin D might reduce lingering symptoms"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 2 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[1]`: "Whether multiple comparisons were conducted and whether correction was applied"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 13068ms

**Final Answer:** solid

**Confidence:** 0.82

**Assumptions:**
- The RCT was adequately powered for the primary endpoint (acute infection severity)
- The 1,747 participant sample is representative of the population studied
- The remote conduct and post-infection timing are acknowledged limitations rather than fatal flaws
- The 4-percentage-point difference (25% vs 21%) in lingering symptoms is being presented as exploratory, not confirmatory

**Reasoning Steps:**
1. Identified evidence tier: This is a randomized controlled trial in 1,747 adults — a full clinical human study (tier 5)
2. Identified conclusion tier: The text discusses outcomes in the studied human population (COVID-19 patients), not extrapolation to other populations
3. Assessed primary endpoint: Vitamin D did NOT change acute infection severity — a negative primary result
4. Assessed secondary endpoint: A 4-percentage-point difference in lingering symptoms at 8 weeks (25% → 21%) favoring vitamin D
5. Evaluated framing: Senior author calls this a 'promising signal' but explicitly emphasizes need for larger trials
6. Checked for hedging quality: The text acknowledges two key limitations (remote conduct, post-infection start) that constrain interpretation
7. Assessed bridge: The conclusion stays within the evidence tier — human RCT data → human outcomes. No leap to mechanism or animal models
8. Evaluated overclaim risk: The 'promising signal' language is cautious and paired with explicit call for larger trials; not presented as established benefit

**Key Claims:**
- Primary endpoint (acute severity): No effect — this is a negative result for the main hypothesis
- Secondary endpoint (lingering symptoms at 8 weeks): 4-percentage-point difference favoring vitamin D (21% vs 25%)
- Framing: Described as 'promising signal' but explicitly caveated with call for larger trials
- Limitations acknowledged: Remote conduct and post-infection supplementation timing limit interpretation
- No mechanism claimed: The text does not explain *how* vitamin D might reduce lingering symptoms

**Alternative Hypotheses:**
- Could classify as overclaim if 'promising signal' is viewed as too strong for a 4-point difference in a secondary endpoint without multiple-comparison correction — but the explicit caveat about needing larger trials mitigates this
- Could classify as mechanism_vs_evidence if the text implied clinical utility without acknowledging the exploratory nature — but it does not

**Uncertainties:**
- Whether the 4-percentage-point difference is statistically significant (p-value not provided in summary)
- Whether multiple comparisons were conducted and whether correction was applied
- Whether the secondary endpoint was pre-specified or post-hoc
- The clinical significance of a 4-point difference in lingering symptoms (is this meaningful to patients?)
- Whether the remote conduct and post-infection timing are minor or major limitations to generalizability

**Self-Verification:**
- Did I overclassify as solid? No — the study is a proper RCT with appropriate caveats. The primary endpoint was negative, and the secondary finding is presented as exploratory.
- Did I miss an overclaim? The 'promising signal' language is strong but paired with explicit acknowledgment that larger trials are needed. This is appropriate for a secondary finding.
- Did I miss a mechanism_vs_evidence issue? No — the text does not claim a mechanism or extrapolate beyond the human population studied.
- Did I check the evidence tier correctly? Yes — 1,747-person RCT is tier 5 (clinical human).
- Did I verify the bridge? Yes — conclusion stays within the evidence tier (human RCT → human outcomes).
- Is the hedging decorative or substantive? Substantive — the limitations (remote, post-infection) are real constraints on interpretation, and the call for larger trials is appropriate for a secondary endpoint.

**Dimension Scores:**
- Correctness: 25.5/30 `########..`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 4.8/6 `########..`
- Uncertainty Handling: 3.6/6 `######....`
- Alternative Hypothesis Quality: 6.0/6 `##########`
- Self Monitoring Quality: 7.2/8 `#########.`
- Insight Depth: 2.8/8 `###.......`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 8.5/10 `########..`


## Final Verdict

**Solo run: Claude Haiku** scored **64.7/100**.

**Best per dimension:**
- Correctness: Claude Haiku (25.5/30)
- Support Strength: Claude Haiku (0.0/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (4.8/6)
- Uncertainty Handling: Claude Haiku (3.6/6)
- Alternative Hypothesis Quality: Claude Haiku (6.0/6)
- Self Monitoring Quality: Claude Haiku (7.2/8)
- Insight Depth: Claude Haiku (2.8/8)
- Mechanism Quality: Claude Haiku (1.5/10)
- Communication Efficiency: Claude Haiku (8.5/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 13.1s | 64.7/100 | 5.0 |

Failure modes observed: decorative_uncertainty, missed_key_insight, named_not_explained, overclaiming, unsupported_conclusion, unsupported_intermediate_step.
