# Forensic Dossier: Study Forensics: AI tutors show moderate gains compared to human tutors

**Run ID:** `full27_study-forensics-035_Claude_Haiku_5c013a`  
**Task:** study-forensics-035 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T08:23:52.286900+00:00  
**Task Family:** solid  
**Trap Type:** borderline_solid_with_caveats  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **71.3/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, named_not_explained, unsupported_conclusion, unsupported_intermediate_step, unused_assumption
**Forensic flags:** 5
**Consistency findings:** 8
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 30.0/30 | 0.0/8 | 4.8/8 | 3.6/6 | 3.3/6 | 6.0/6 | 5.6/8 | 8.0/8 | 1.5/10 | 8.5/10 | **71.3/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `solid` [+] (gold: `solid`)
**Finding Recall:** 100%
**Matched Findings:** evidence_matches_claim, cautious_scope_control
**Extra Findings:** none_or_minor, conclusion_exceeds_results, decorative_uncertainty, mechanism_not_demonstrated, correlation_as_causation

## Reasoning Integrity Audit

### Claude Haiku
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 7

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
- **[MINOR]** `study_forensics_overflagging`: Agent raised extra findings in solid case: none_or_minor, conclusion_exceeds_results, decorative_uncertainty, mechanism_not_demonstrated, correlation_as_causation


## Evidence Map

### Claude Haiku

**Correctness:** 30.0/30
  - (+) `final_answer`: "solid"
    _Agent's answer for correctness check_
  - Note: Exact match

**Support Strength:** 0.0/8
  - (-) `final_answer`: "solid"
    _Conclusion not supported by steps_
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 7
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[4]`: "Examined uncertainty language: The text appropriately qualifies findings (e.g., 'increased by 4 percentage points' is sp"
    _Most informative reasoning step_
  - Note: 7 reasoning steps
  - Note: Low step utility: 0/7 steps contribute

**Assumption Discipline:** 3.6/6
  - (+) `assumptions[4]`: "The inexperienced tutor subgroup analysis was pre-specified or appropriately corrected for multiple comparisons"
    _Most substantive assumption_
  - (-) `assumptions[0]`: "Both studies used appropriate control groups and comparable student populations"
    _Declared but unused in reasoning_
  - (-) `assumptions[1]`: "Success rate and topic mastery are valid outcome measures for the respective studies"
    _Declared but unused in reasoning_
  - Note: 5/5 substantive assumptions
  - Note: 3 unused assumption(s)

**Uncertainty Handling:** 3.3/6
  - (+) `uncertainties[3]`: "The subgroup analysis for inexperienced tutors (9-point advantage) could reflect regression to the mean or selection eff"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.78"
    _Stated confidence level_
  - (-) `uncertainties[1]`: "No information on sample sizes, statistical significance, or confidence intervals is provided"
    _Listed but never addressed in reasoning_
  - (-) `uncertainties[2]`: "The definition of 'success rate' and 'topic mastery' is not given; these could be measured differently across studies"
    _Listed but never addressed in reasoning_
  - Note: 5 uncertainties (5 substantive)
  - Note: 2 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 6.0/6
  - (+) `alternative_hypotheses[0]`: "correlation_vs_causation: Could be flagged if the studies were purely observational, but the text describes 'compared' s"
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 2/2 include rejection reasoning

**Self Monitoring Quality:** 5.6/8
  - (+) `self_check[1]`: "Did I miss red flags? The lack of methodological detail (sample size, significance tests, design) is a limitation of the"
    _Most substantive self-verification step_
  - Note: 5 self-check items
  - Note: Self-check quality: 0 deep, 5 arithmetic, 0 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 8.5/10
  - Note: Signal density: 0.71, 519 words

**Insight Depth:** 8.0/8
  - (+) `(output text)`: "the studies themselves is the complementary framing justified? yes—the da"
    _Insight 'complementary' matched (exact)_
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
- **Unused Assumption** `[HEURISTIC]`: Assumption 'Both studies used appropriate control groups and comparable ...' is declared but not referenced in reasoning
  - `assumptions[0]`: "Both studies used appropriate control groups and comparable student populations"
  - _Impacts: assumption_discipline_
- **Unused Assumption** `[HEURISTIC]`: Assumption 'Success rate and topic mastery are valid outcome measures fo...' is declared but not referenced in reasoning
  - `assumptions[1]`: "Success rate and topic mastery are valid outcome measures for the respective studies"
  - _Impacts: assumption_discipline_
- **Unused Assumption** `[HEURISTIC]`: Assumption 'The studies measured short-term outcomes; long-term effects ...' is declared but not referenced in reasoning
  - `assumptions[3]`: "The studies measured short-term outcomes; long-term effects are not addressed"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'No information on sample sizes, statistical significance, or...' is listed but not addressed
  - `uncertainties[1]`: "No information on sample sizes, statistical significance, or confidence intervals is provided"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'The definition of 'success rate' and 'topic mastery' is not ...' is listed but not addressed
  - `uncertainties[2]`: "The definition of 'success rate' and 'topic mastery' is not given; these could be measured different"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/15 content words)
  - `key_claims[0]`: "AI tutoring systems achieve modestly higher success rates than human tutoring alone (66% vs 61%) and"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/10 content words)
  - `key_claims[1]`: "Human tutors validate most AI-generated answers (76.4%), suggesting reasonable quality"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/14 content words)
  - `key_claims[2]`: "AI tools supporting human tutors improve outcomes, with larger gains for less experienced tutors (9 "
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/9 content words)
  - `key_claims[3]`: "The authors appropriately frame AI as complementary rather than replacement, which is consistent wit"
- **[WARN]** `[HEURISTIC]` `unused_assumption`: Assumption 4 appears unused in reasoning or answer
  - `assumptions[3]`: "The studies measured short-term outcomes; long-term effects are not addressed"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 2 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[1]`: "No information on sample sizes, statistical significance, or confidence intervals is provided"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 3 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[2]`: "The definition of 'success rate' and 'topic mastery' is not given; these could be measured different"
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "solid"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 12121ms

**Final Answer:** solid

**Confidence:** 0.78

**Assumptions:**
- Both studies used appropriate control groups and comparable student populations
- Success rate and topic mastery are valid outcome measures for the respective studies
- The 76.4% confirmation rate reflects actual tutor assessment rather than selection bias
- The studies measured short-term outcomes; long-term effects are not addressed
- The inexperienced tutor subgroup analysis was pre-specified or appropriately corrected for multiple comparisons

**Reasoning Steps:**
1. Examined whether causal claims are made: The text describes comparative outcomes (66% vs 61% vs 56%) without claiming causation; it presents results as comparisons between conditions
2. Checked for overclaiming: The conclusion that AI 'complements' rather than 'replaces' human tutoring is explicitly stated as a caveat and is consistent with the data (AI alone at 66% vs human at 61%)
3. Evaluated mechanism claims: No mechanistic explanations are offered; the text reports empirical outcomes only
4. Assessed confounders: The text does not discuss potential confounders, but this is a limitation of the summary rather than evidence of poor study design
5. Examined uncertainty language: The text appropriately qualifies findings (e.g., 'increased by 4 percentage points' is specific; the subgroup finding for inexperienced tutors is presented as a separate observation)
6. Checked for decorative uncertainty: No false hedging detected; claims are proportionate to reported results
7. Verified effect sizes: The differences reported (5 percentage points in study 1; 4–9 points in study 2) are modest but non-trivial and appropriately presented

**Key Claims:**
- AI tutoring systems achieve modestly higher success rates than human tutoring alone (66% vs 61%) and substantially higher than written hints (56%)
- Human tutors validate most AI-generated answers (76.4%), suggesting reasonable quality
- AI tools supporting human tutors improve outcomes, with larger gains for less experienced tutors (9 vs 4 percentage points overall)
- The authors appropriately frame AI as complementary rather than replacement, which is consistent with the data

**Alternative Hypotheses:**
- correlation_vs_causation: Could be flagged if the studies were purely observational, but the text describes 'compared' studies suggesting experimental or quasi-experimental design
- overclaim: Could be flagged if the 76.4% confirmation rate were interpreted as proof of AI superiority, but the text presents it as one metric among several

**Uncertainties:**
- The text does not specify study design (RCT, quasi-experimental, observational); this limits assessment of internal validity
- No information on sample sizes, statistical significance, or confidence intervals is provided
- The definition of 'success rate' and 'topic mastery' is not given; these could be measured differently across studies
- The subgroup analysis for inexperienced tutors (9-point advantage) could reflect regression to the mean or selection effects if not properly controlled
- Whether the two studies are truly independent or share overlapping samples is unclear

**Self-Verification:**
- Did I overidentify problems? No—the text is cautious and does not make unsupported causal claims
- Did I miss red flags? The lack of methodological detail (sample size, significance tests, design) is a limitation of the summary, not necessarily the studies themselves
- Is the complementary framing justified? Yes—the data show AI performs slightly better in isolation but is presented as a support tool for human tutors
- Are the effect sizes reasonable? Yes—5–9 percentage point improvements are modest but meaningful in educational contexts
- Did I assume the studies are well-designed? I noted uncertainty about design, but the text provides no evidence of poor design

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 3.6/6 `######....`
- Uncertainty Handling: 3.3/6 `#####.....`
- Alternative Hypothesis Quality: 6.0/6 `##########`
- Self Monitoring Quality: 5.6/8 `#######...`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 8.5/10 `########..`


## Final Verdict

**Solo run: Claude Haiku** scored **71.3/100**.

**Best per dimension:**
- Correctness: Claude Haiku (30.0/30)
- Support Strength: Claude Haiku (0.0/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (3.6/6)
- Uncertainty Handling: Claude Haiku (3.3/6)
- Alternative Hypothesis Quality: Claude Haiku (6.0/6)
- Self Monitoring Quality: Claude Haiku (5.6/8)
- Insight Depth: Claude Haiku (8.0/8)
- Mechanism Quality: Claude Haiku (1.5/10)
- Communication Efficiency: Claude Haiku (8.5/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 12.1s | 71.3/100 | 5.9 |

Failure modes observed: decorative_uncertainty, named_not_explained, unsupported_conclusion, unsupported_intermediate_step, unused_assumption.
