# Forensic Dossier: Study Forensics: AI tutors show moderate gains compared to human tutors

**Run ID:** `full27_study-forensics-035_Claude_Haiku_f0c74f`  
**Task:** study-forensics-035 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T18:06:06.644283+00:00  
**Task Family:** solid  
**Trap Type:** borderline_solid_with_caveats  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **73.3/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, missed_key_insight, named_not_explained, unsupported_conclusion, unsupported_intermediate_step
**Forensic flags:** 5
**Consistency findings:** 8
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 30.0/30 | 0.0/8 | 4.8/8 | 4.8/6 | 3.3/6 | 6.0/6 | 6.4/8 | 8.0/8 | 1.5/10 | 8.5/10 | **73.3/100** |

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
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 7
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[0]`: "Identified evidence tier: Both studies involve human learners in real educational settings with measured learning outcom"
    _Most informative reasoning step_
  - Note: 7 reasoning steps
  - Note: Low step utility: 0/7 steps contribute

**Assumption Discipline:** 4.8/6
  - (+) `assumptions[0]`: "Both studies involved actual human learners in educational settings (not simulations or animal models)"
    _Most substantive assumption_
  - Note: 5/5 substantive assumptions

**Uncertainty Handling:** 3.3/6
  - (+) `uncertainties[0]`: "Sample sizes are not reported; if studies were very small (n<30 per group), confidence in the results would be lower."
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.82"
    _Stated confidence level_
  - (-) `uncertainties[1]`: "Randomization and blinding procedures are not described; this affects internal validity."
    _Listed but never addressed in reasoning_
  - (-) `uncertainties[2]`: "The 'success rate' and 'topic mastery' metrics are not defined in detail; unclear if these are standardized measures."
    _Listed but never addressed in reasoning_
  - Note: 6 uncertainties (6 substantive)
  - Note: 2 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 6.0/6
  - (+) `alternative_hypotheses[0]`: "Could classify as mechanism_vs_evidence if the studies were small pilots with weak designs — but the text provides speci"
    _Most substantive alternative hypothesis_
  - Note: 3 alternative hypotheses considered
  - Note: 3/3 include rejection reasoning

**Self Monitoring Quality:** 6.4/8
  - (+) `self_check[3]`: "Did I miss confounders? Possibly — student motivation, prior knowledge, and tutor experience could differ between groups"
    _Most substantive self-verification step_
  - Note: 6 self-check items
  - Note: Self-check quality: 0 deep, 6 arithmetic, 0 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 8.5/10
  - Note: Signal density: 0.75, 661 words

**Insight Depth:** 8.0/8
  - (+) `(output text)`: "e text carefully frames ai as complementary, not superior. could flag cor"
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
- **Missed Key Insight** `[MEDIUM CONFIDENCE]`: Missed expected finding: evidence_matches_claim
  - `(task expectation)`: "Expected: evidence_matches_claim"
  - _Impacts: insight_depth_

**STYLISTIC:**
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Randomization and blinding procedures are not described; thi...' is listed but not addressed
  - `uncertainties[1]`: "Randomization and blinding procedures are not described; this affects internal validity."
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'The 'success rate' and 'topic mastery' metrics are not defin...' is listed but not addressed
  - `uncertainties[2]`: "The 'success rate' and 'topic mastery' metrics are not defined in detail; unclear if these are stand"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/11 content words)
  - `key_claims[0]`: "AI-assisted learning achieved 66% success vs. 61% for human tutoring and 56% for written hints — a m"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/15 content words)
  - `key_claims[1]`: "AI tool improved topic mastery by 4 percentage points overall, 9 points for inexperienced tutors — s"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/11 content words)
  - `key_claims[2]`: "Tutors validated 76.4% of AI answers without major corrections — indicates reasonable quality but no"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/11 content words)
  - `key_claims[3]`: "Authors frame AI as complementary to human tutoring, not a replacement — this is a substantive and a"
- **[WARN]** `[HEURISTIC]` `claim_step_alignment`: Key claim 3 not well supported in reasoning steps (2/11 content words found)
  - `key_claims[2]`: "Tutors validated 76.4% of AI answers without major corrections — indicates reasonable quality but no"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 2 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[1]`: "Randomization and blinding procedures are not described; this affects internal validity."
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 3 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[2]`: "The 'success rate' and 'topic mastery' metrics are not defined in detail; unclear if these are stand"
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "solid"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 14500ms

**Final Answer:** solid

**Confidence:** 0.82

**Assumptions:**
- Both studies involved actual human learners in educational settings (not simulations or animal models)
- Success rate and topic mastery are appropriate outcome measures for the educational context
- The studies were conducted with reasonable sample sizes and controls (baseline comparisons provided)
- The 76.4% tutor confirmation rate reflects actual quality assessment by domain experts
- The studies measured short-term learning outcomes, not long-term retention or transfer

**Reasoning Steps:**
1. Identified evidence tier: Both studies involve human learners in real educational settings with measured learning outcomes (success rates, mastery gains). This is limited human evidence — not large-scale RCTs or meta-analyses, but genuine human trials with control comparisons.
2. Identified conclusion tier: The text implies benefits for human learners in tutoring contexts (improved success rates, mastery gains).
3. Assessed bridge: The evidence directly measures human learning outcomes. The bridge from evidence to conclusion is direct — no extrapolation from animals or cells to humans is required.
4. Evaluated claims: The text reports specific numerical results (66% vs 61% vs 56%; 4-9 percentage point gains) without inflated language. No claims of 'breakthrough,' 'transformation,' or 'replacement' are made.
5. Checked for hedging quality: The authors explicitly state AI 'complements' rather than 'replaces' human tutoring. This is a substantive claim about the role of AI, not decorative uncertainty.
6. Assessed confounders: The studies include control conditions (human tutoring, written hints), which partially address confounding. No obvious confounders are ignored in the reported comparisons.
7. Checked for correlation vs. causation: The studies compare conditions (AI vs. human vs. written), which supports causal inference about the effect of the tutoring modality, though causality is not definitively established without randomization details.

**Key Claims:**
- AI-assisted learning achieved 66% success vs. 61% for human tutoring and 56% for written hints — a modest but consistent advantage.
- AI tool improved topic mastery by 4 percentage points overall, 9 points for inexperienced tutors — suggests AI may be most valuable as a support for less-skilled tutors.
- Tutors validated 76.4% of AI answers without major corrections — indicates reasonable quality but not perfection.
- Authors frame AI as complementary to human tutoring, not a replacement — this is a substantive and appropriate claim given the evidence.

**Alternative Hypotheses:**
- Could classify as mechanism_vs_evidence if the studies were small pilots with weak designs — but the text provides specific success rates and tutor validation, suggesting reasonable rigor.
- Could flag overclaim if the text had used language like 'AI tutors outperform humans' — but the text carefully frames AI as complementary, not superior.
- Could flag correlation_vs_causation if the text had not included control conditions — but comparisons to human tutoring and written hints support causal inference about modality.

**Uncertainties:**
- Sample sizes are not reported; if studies were very small (n<30 per group), confidence in the results would be lower.
- Randomization and blinding procedures are not described; this affects internal validity.
- The 'success rate' and 'topic mastery' metrics are not defined in detail; unclear if these are standardized measures.
- Duration of studies is not specified; unclear if gains persist or are short-term.
- The second study's 4–9 percentage point gains are modest; statistical significance is not reported.
- Tutor confirmation rate (76.4%) is high but does not directly measure student learning; it is a proxy for AI quality.

**Self-Verification:**
- Did I overstate the evidence tier? No — the studies involve human learners with measured outcomes; this is limited human evidence, not animal or cell studies.
- Did I miss an overclaim? No — the text avoids promotional language and acknowledges AI's complementary role.
- Did I miss a mechanism_vs_evidence problem? No — the conclusions (AI supports learning, especially for inexperienced tutors) stay within the evidence tier.
- Did I miss confounders? Possibly — student motivation, prior knowledge, and tutor experience could differ between groups, but the text does not ignore these; the second study explicitly examines tutor experience.
- Did I miss correlation_vs_causation? No — the studies compare conditions, which supports causal inference about modality effects.
- Is the study solid? Yes — it reports human learning outcomes with control conditions, provides specific numbers, and makes appropriately cautious claims about AI's role.

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 4.8/6 `########..`
- Uncertainty Handling: 3.3/6 `#####.....`
- Alternative Hypothesis Quality: 6.0/6 `##########`
- Self Monitoring Quality: 6.4/8 `########..`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 8.5/10 `########..`


## Final Verdict

**Solo run: Claude Haiku** scored **73.3/100**.

**Best per dimension:**
- Correctness: Claude Haiku (30.0/30)
- Support Strength: Claude Haiku (0.0/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (4.8/6)
- Uncertainty Handling: Claude Haiku (3.3/6)
- Alternative Hypothesis Quality: Claude Haiku (6.0/6)
- Self Monitoring Quality: Claude Haiku (6.4/8)
- Insight Depth: Claude Haiku (8.0/8)
- Mechanism Quality: Claude Haiku (1.5/10)
- Communication Efficiency: Claude Haiku (8.5/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 14.5s | 73.3/100 | 5.1 |

Failure modes observed: decorative_uncertainty, missed_key_insight, named_not_explained, unsupported_conclusion, unsupported_intermediate_step.
