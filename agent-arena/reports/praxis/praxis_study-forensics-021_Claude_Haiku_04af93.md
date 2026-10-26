# Forensic Dossier: Study Forensics: Virtual tutoring boosts reading skills

**Run ID:** `praxis_study-forensics-021_Claude_Haiku_04af93`  
**Task:** study-forensics-021 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-07T07:50:30.424226+00:00  
**Task Family:** solid  
**Trap Type:** overflagging_solid_study  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **71.9/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, missed_key_insight, named_not_explained, unsupported_conclusion, unsupported_intermediate_step, unused_assumption
**Forensic flags:** 5
**Consistency findings:** 8
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 30.0/30 | 0.0/8 | 4.8/8 | 3.7/6 | 3.6/6 | 5.5/6 | 4.8/8 | 8.0/8 | 1.5/10 | 10.0/10 | **71.9/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `solid` [+] (gold: `solid`)
**Finding Recall:** 50%
**Matched Findings:** cautious_scope_control
**Missed Findings:** evidence_matches_claim
**Extra Findings:** none_or_minor, conclusion_exceeds_results, unsupported_generalization, decorative_uncertainty, mechanism_not_demonstrated, correlation_as_causation

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
- **[MINOR]** `study_forensics_overflagging`: Agent raised extra findings in solid case: none_or_minor, conclusion_exceeds_results, unsupported_generalization, decorative_uncertainty, mechanism_not_demonstrated, correlation_as_causation


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
  - (+) `steps[7]`: "Assessed scope of claims: Results are presented for this specific program in this context; no inappropriate generalizati"
    _Most informative reasoning step_
  - Note: 9 reasoning steps
  - Note: Low step utility: 0/9 steps contribute

**Assumption Discipline:** 3.7/6
  - (+) `assumptions[0]`: "The study used a proper randomized assignment to treatment and control conditions"
    _Most substantive assumption_
  - (-) `assumptions[4]`: "Attrition rates and missing data are not problematic enough to invalidate results"
    _Declared but unused in reasoning_
  - Note: 6/6 substantive assumptions
  - Note: Many assumptions (6)

**Uncertainty Handling:** 3.6/6
  - (+) `uncertainties[0]`: "Whether the 'two months of reading progress' is educationally meaningful (effect size not provided in text)"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.88"
    _Stated confidence level_
  - (-) `uncertainties[3]`: "Whether the 'modest gains' for lower-attendance students are statistically significant"
    _Listed but never addressed in reasoning_
  - Note: 6 uncertainties (6 substantive)
  - Note: 1 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 5.5/6
  - (+) `alternative_hypotheses[1]`: "Mechanism_vs_evidence: If the text had explained *why* virtual tutoring works (e.g., 'because of personalized attention'"
    _Most substantive alternative hypothesis_
  - Note: 3 alternative hypotheses considered
  - Note: 2/3 include rejection reasoning

**Self Monitoring Quality:** 4.8/8
  - (+) `self_check[1]`: "Did I miss red flags? Checked for: overclaim (none found), causation without RCT (not present), mechanism without eviden"
    _Most substantive self-verification step_
  - Note: 4 self-check items
  - Note: Self-check quality: 0 deep, 4 arithmetic, 0 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.73, 475 words

**Insight Depth:** 8.0/8
  - (+) `(output text)`: "olid identified study design: rct with random assignment — this"
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
- **Missed Key Insight** `[MEDIUM CONFIDENCE]`: Missed expected finding: evidence_matches_claim
  - `(task expectation)`: "Expected: evidence_matches_claim"
  - _Impacts: insight_depth_

**STYLISTIC:**
- **Unused Assumption** `[HEURISTIC]`: Assumption 'Attrition rates and missing data are not problematic enough ...' is declared but not referenced in reasoning
  - `assumptions[4]`: "Attrition rates and missing data are not problematic enough to invalidate results"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether the 'modest gains' for lower-attendance students are...' is listed but not addressed
  - `uncertainties[3]`: "Whether the 'modest gains' for lower-attendance students are statistically significant"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/9 content words)
  - `key_claims[0]`: "RCT design provides strong causal evidence that the program caused reading gains"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/8 content words)
  - `key_claims[1]`: "Effect size is modest but concrete (two months progress) and dose-dependent"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/8 content words)
  - `key_claims[2]`: "The text appropriately emphasizes participation as critical without overstating certainty"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/6 content words)
  - `key_claims[3]`: "No unsupported mechanism claims or inappropriate generalizations detected"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 5 has low overlap with final answer (0/5 content words)
  - `key_claims[4]`: "Cost-effectiveness claim is stated but not detailed in this summary"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 4 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[3]`: "Whether the 'modest gains' for lower-attendance students are statistically significant"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "Overclaim: If the text had claimed this works for all struggling readers or all contexts, that would"
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "solid"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 10188ms

**Final Answer:** solid

**Confidence:** 0.88

**Assumptions:**
- The study used a proper randomized assignment to treatment and control conditions
- Reading progress was measured with a validated, standardized assessment
- The ten-week timeframe and session counts are accurately reported
- The control condition received no tutoring or standard instruction only
- Attrition rates and missing data are not problematic enough to invalidate results
- The rural school district context is representative enough for the claims made

**Reasoning Steps:**
1. Identified study design: RCT with random assignment — this is the gold standard for causal inference
2. Examined the main claim: ~40 sessions → ~2 months additional reading progress vs. control
3. Assessed whether this is a causal claim: Yes, but justified by RCT design, not just correlation
4. Checked for overclaiming: The text makes modest, specific claims (two months, lower cost) without sweeping generalizations
5. Evaluated mechanism claims: None presented; the text describes what happened, not why
6. Examined uncertainty language: Researchers 'emphasized' importance of participation; this is appropriate framing, not decorative
7. Checked for confounders: RCT design controls for most baseline confounders through randomization
8. Assessed scope of claims: Results are presented for this specific program in this context; no inappropriate generalization to all tutoring or all populations detected
9. Reviewed cost-effectiveness claim: Stated as comparative fact ('lower cost than typical high-dose tutoring') — reasonable if true, though not detailed here

**Key Claims:**
- RCT design provides strong causal evidence that the program caused reading gains
- Effect size is modest but concrete (two months progress) and dose-dependent
- The text appropriately emphasizes participation as critical without overstating certainty
- No unsupported mechanism claims or inappropriate generalizations detected
- Cost-effectiveness claim is stated but not detailed in this summary

**Alternative Hypotheses:**
- Overclaim: If the text had claimed this works for all struggling readers or all contexts, that would be overclaiming
- Mechanism_vs_evidence: If the text had explained *why* virtual tutoring works (e.g., 'because of personalized attention') without evidence, that would be problematic
- Correlation_vs_causation: If this were observational data, the causal claim would be unjustified — but RCT design supports causation

**Uncertainties:**
- Whether the 'two months of reading progress' is educationally meaningful (effect size not provided in text)
- What the control condition actually received (standard instruction? no intervention? waitlist?)
- Attrition rates and whether they differed between groups
- Whether the 'modest gains' for lower-attendance students are statistically significant
- Generalizability beyond rural elementary students to other populations or settings
- Whether the cost comparison to 'typical high-dose tutoring' is based on actual data or assumption

**Self-Verification:**
- Did I assume problems that aren't stated? No — I focused on what the text actually says
- Did I miss red flags? Checked for: overclaim (none found), causation without RCT (not present), mechanism without evidence (not present), confounders (RCT controls for these)
- Is 'solid' the right call? Yes — this is a well-designed study with appropriate caveats and modest, specific claims
- Did I conflate 'uncertainty exists' with 'study is flawed'? No — uncertainty about generalizability is normal and expected, not a flaw in the study itself

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 3.7/6 `######....`
- Uncertainty Handling: 3.6/6 `######....`
- Alternative Hypothesis Quality: 5.5/6 `#########.`
- Self Monitoring Quality: 4.8/8 `######....`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Haiku** scored **71.9/100**.

**Best per dimension:**
- Correctness: Claude Haiku (30.0/30)
- Support Strength: Claude Haiku (0.0/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (3.7/6)
- Uncertainty Handling: Claude Haiku (3.6/6)
- Alternative Hypothesis Quality: Claude Haiku (5.5/6)
- Self Monitoring Quality: Claude Haiku (4.8/8)
- Insight Depth: Claude Haiku (8.0/8)
- Mechanism Quality: Claude Haiku (1.5/10)
- Communication Efficiency: Claude Haiku (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 10.2s | 71.9/100 | 7.1 |

Failure modes observed: decorative_uncertainty, missed_key_insight, named_not_explained, unsupported_conclusion, unsupported_intermediate_step, unused_assumption.
