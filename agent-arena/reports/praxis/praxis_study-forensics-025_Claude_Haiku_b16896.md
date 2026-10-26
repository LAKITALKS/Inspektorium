# Forensic Dossier: Study Forensics: AI instruction outperforms human teachers

**Run ID:** `praxis_study-forensics-025_Claude_Haiku_b16896`  
**Task:** study-forensics-025 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-07T07:53:11.768558+00:00  
**Task Family:** overclaim  
**Trap Type:** media_inflated_overclaim  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **71.9/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, named_not_explained, unsupported_intermediate_step, unused_assumption
**Forensic flags:** 3
**Consistency findings:** 10
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 30.0/30 | 1.2/8 | 4.8/8 | 3.0/6 | 3.3/6 | 5.2/6 | 6.4/8 | 8.0/8 | 1.5/10 | 8.5/10 | **71.9/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `overclaim` [+] (gold: `overclaim`)
**Finding Recall:** 100%
**Matched Findings:** conclusion_exceeds_results, unsupported_generalization
**Extra Findings:** cautious_scope_control, none_or_minor, mechanism_not_demonstrated, correlation_as_causation

## Reasoning Integrity Audit

### Claude Haiku
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 6

## Mechanism Analysis

### Claude Haiku
| Aspect | Status |
|--------|--------|
| Concept named | :white_check_mark: bias, effect |
| Mechanism described | :x: (0 sentence(s)) |
| Grounded to case | :x: (0 sentence(s)) |

**Missing:** mechanism not described, mechanism not grounded to case data

## Grounding Audit

### Claude Haiku
Conclusion claims: 1
- Direct support: 0
- Indirect support: 1
- Unsupported: 0
- Contradicted: 0


## Forensic Flags

### Claude Haiku

- **[MODERATE]** `weak_mechanism`: Correct answer but weak mechanism explanation — answer may not generalize
  - `final_answer`: "overclaim"
- **[MAJOR]** `unsupported_leap`: Correct answer with weak support chain — final answer may be an unsupported leap
- **[MODERATE]** `ungrounded_mechanism`: Mechanism named/described but not connected to case-specific data
  - `(mechanism analysis)`: "bias, effect"


## Evidence Map

### Claude Haiku

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
  - (+) `steps[3]`: "Observed that the article provides no discussion of confounding variables (e.g., novelty effects, selection of motivated"
    _Most informative reasoning step_
  - Note: 6 reasoning steps
  - Note: Low step utility: 0/6 steps contribute

**Assumption Discipline:** 3.0/6
  - (+) `assumptions[2]`: "The 'two-times learning effect' is attributed to AI tutors without specification of what comparison group was used or wh"
    _Most substantive assumption_
  - (-) `assumptions[1]`: "The 65% test score increase is presented as fact without context about baseline performance, measurement methods, or sta"
    _Declared but unused in reasoning_
  - (-) `assumptions[2]`: "The 'two-times learning effect' is attributed to AI tutors without specification of what comparison group was used or wh"
    _Declared but unused in reasoning_
  - Note: 6/6 substantive assumptions
  - Note: Many assumptions (6)

**Uncertainty Handling:** 3.3/6
  - (+) `uncertainties[1]`: "Whether the 65% figure refers to effect size, absolute gain, or relative improvement, and whether it is statistically si"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.92"
    _Stated confidence level_
  - (-) `uncertainties[1]`: "Whether the 65% figure refers to effect size, absolute gain, or relative improvement, and whether it is statistically si"
    _Listed but never addressed in reasoning_
  - (-) `uncertainties[2]`: "Whether the 'two-times learning effect' controlled for time-on-task or other confounders"
    _Listed but never addressed in reasoning_
  - Note: 5 uncertainties (5 substantive)
  - Note: 2 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 5.2/6
  - (+) `alternative_hypotheses[1]`: "mechanism_vs_evidence: The article describes AI tutoring mechanisms but applies conclusions to human teacher replacement"
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 1/2 include rejection reasoning

**Self Monitoring Quality:** 6.4/8
  - (+) `self_check[2]`: "Is this a solid study being misreported, or is the article itself making unsupported claims? The article itself is makin"
    _Most substantive self-verification step_
  - Note: 5 self-check items
  - Note: Self-check quality: 1 deep, 4 arithmetic, 0 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 8.5/10
  - Note: Signal density: 0.73, 594 words

**Insight Depth:** 4.0/8
  - (?) `(not found)`: "Missing: no methodology"
    _Insight 'no methodology' not found_
  - Note: Key insights: 1 full / 2


## Failure Analysis

### Claude Haiku

**MODERATE:**
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Names the phenomenon but does not explain the causal mechanism
  - `final_answer`: "overclaim"
  - _Impacts: mechanism_quality_
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Named concept(s) ['bias', 'effect'] but mechanism not described
  - _Impacts: mechanism_quality, insight_depth_
- **Unsupported Intermediate Step** `[MEDIUM CONFIDENCE]`: No reasoning step is load-bearing — final answer lacks traceable derivation
  - `final_answer`: "overclaim"
  - _Impacts: support_strength, structural_reasoning_

**STYLISTIC:**
- **Unused Assumption** `[HEURISTIC]`: Assumption 'The 65% test score increase is presented as fact without con...' is declared but not referenced in reasoning
  - `assumptions[1]`: "The 65% test score increase is presented as fact without context about baseline performance, measure"
  - _Impacts: assumption_discipline_
- **Unused Assumption** `[HEURISTIC]`: Assumption 'The 'two-times learning effect' is attributed to AI tutors w...' is declared but not referenced in reasoning
  - `assumptions[2]`: "The 'two-times learning effect' is attributed to AI tutors without specification of what comparison "
  - _Impacts: assumption_discipline_
- **Unused Assumption** `[HEURISTIC]`: Assumption 'No information is provided about study duration, student dem...' is declared but not referenced in reasoning
  - `assumptions[4]`: "No information is provided about study duration, student demographics, or whether results replicated"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether the 65% figure refers to effect size, absolute gain,...' is listed but not addressed
  - `uncertainties[1]`: "Whether the 65% figure refers to effect size, absolute gain, or relative improvement, and whether it"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether the 'two-times learning effect' controlled for time-...' is listed but not addressed
  - `uncertainties[2]`: "Whether the 'two-times learning effect' controlled for time-on-task or other confounders"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (1/20 content words)
  - `key_claims[0]`: "The article makes strong causal claims ('AI outperform', 'taught twice as effectively') from pilot p"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/13 content words)
  - `key_claims[1]`: "Quantitative claims (65% rise, two-times effect) lack citations and context, making them impossible "
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/16 content words)
  - `key_claims[2]`: "The generalization from three subject areas to 'all subjects' and from pilots to broad conclusions a"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/14 content words)
  - `key_claims[3]`: "No discussion of confounders (novelty, selection bias, implementation quality, time effects) that co"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 5 has low overlap with final answer (1/18 content words)
  - `key_claims[4]`: "The article conflates AI tutoring effectiveness in specific domains with the broader claim that huma"
- **[WARN]** `[HEURISTIC]` `unused_assumption`: Assumption 2 appears unused in reasoning or answer
  - `assumptions[1]`: "The 65% test score increase is presented as fact without context about baseline performance, measure"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 2 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[1]`: "Whether the 65% figure refers to effect size, absolute gain, or relative improvement, and whether it"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 3 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[2]`: "Whether the 'two-times learning effect' controlled for time-on-task or other confounders"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "correlation_vs_causation: The performance gains could reflect novelty effects, selection bias (motiv"
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "overclaim"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 12083ms

**Final Answer:** overclaim

**Confidence:** 0.92

**Assumptions:**
- The article cites 'pilot programs' but provides no specific study names, sample sizes, control conditions, or peer-review status
- The 65% test score increase is presented as fact without context about baseline performance, measurement methods, or statistical significance
- The 'two-times learning effect' is attributed to AI tutors without specification of what comparison group was used or whether confounders were controlled
- The article generalizes from limited domains (physics, mathematics, literacy) to 'all subjects'
- No information is provided about study duration, student demographics, or whether results replicated across different contexts
- The article treats pilot program findings as generalizable to broad populations without acknowledging selection bias or implementation fidelity issues

**Reasoning Steps:**
1. Identified that the article makes strong causal claims ('AI outperform peers', 'taught twice as effectively') from what appear to be pilot studies with unspecified methodology
2. Noted that specific quantitative claims (65% rise, two-times effect) lack supporting citations or methodological transparency
3. Recognized that pilot programs are inherently limited in scope and generalizability, yet the article extrapolates to 'all subjects' and positions this as dismantling the teaching profession
4. Observed that the article provides no discussion of confounding variables (e.g., novelty effects, selection of motivated students, additional instructional time, teacher quality variation)
5. Noted the absence of comparison to other evidence-based interventions or meta-analyses of educational technology
6. Identified that the conclusion ('role of educators as primary source of knowledge is being dismantled') far exceeds what pilot data can support

**Key Claims:**
- The article makes strong causal claims ('AI outperform', 'taught twice as effectively') from pilot programs with no methodological transparency—this is a classic overclaim from limited evidence
- Quantitative claims (65% rise, two-times effect) lack citations and context, making them impossible to evaluate
- The generalization from three subject areas to 'all subjects' and from pilots to broad conclusions about teacher obsolescence vastly exceeds the evidence base
- No discussion of confounders (novelty, selection bias, implementation quality, time effects) that commonly inflate pilot program results
- The article conflates AI tutoring effectiveness in specific domains with the broader claim that human teachers are becoming obsolete—a logical leap unsupported by the evidence presented

**Alternative Hypotheses:**
- correlation_vs_causation: The performance gains could reflect novelty effects, selection bias (motivated students volunteering for pilots), or confounding variables rather than AI superiority
- mechanism_vs_evidence: The article describes AI tutoring mechanisms but applies conclusions to human teacher replacement without evidence that AI can replicate all teaching functions (motivation, mentorship, social-emotional learning)

**Uncertainties:**
- Whether the cited pilot programs actually exist and what their actual findings were (the article provides no citations)
- Whether the 65% figure refers to effect size, absolute gain, or relative improvement, and whether it is statistically significant
- Whether the 'two-times learning effect' controlled for time-on-task or other confounders
- Whether the article is reporting on peer-reviewed studies or promotional materials from AI vendors
- The actual sample sizes and demographic representativeness of the pilot programs

**Self-Verification:**
- Did I assume problems that aren't stated? No—the article genuinely lacks citations, methodological detail, and appropriate caveats for pilot findings
- Did I miss any hedging language? The article uses 'some reports suggest' for the 65% claim but then treats the two-times effect and obsolescence conclusion as established facts
- Is this a solid study being misreported, or is the article itself making unsupported claims? The article itself is making the overclaims; it is not reporting a specific study with appropriate caveats
- Could pilot programs legitimately show these effects? Yes, but the article presents them as proof of broad claims without acknowledging limitations, selection bias, or the need for replication
- Did I correctly identify the primary issue? Yes—this is overclaim: strong conclusions about teacher obsolescence and universal AI superiority drawn from limited, unspecified pilot data

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 1.2/8 `#.........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 3.0/6 `#####.....`
- Uncertainty Handling: 3.3/6 `#####.....`
- Alternative Hypothesis Quality: 5.2/6 `########..`
- Self Monitoring Quality: 6.4/8 `########..`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 8.5/10 `########..`


## Final Verdict

**Solo run: Claude Haiku** scored **71.9/100**.

**Best per dimension:**
- Correctness: Claude Haiku (30.0/30)
- Support Strength: Claude Haiku (1.2/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (3.0/6)
- Uncertainty Handling: Claude Haiku (3.3/6)
- Alternative Hypothesis Quality: Claude Haiku (5.2/6)
- Self Monitoring Quality: Claude Haiku (6.4/8)
- Insight Depth: Claude Haiku (8.0/8)
- Mechanism Quality: Claude Haiku (1.5/10)
- Communication Efficiency: Claude Haiku (8.5/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 12.1s | 71.9/100 | 6.0 |

Failure modes observed: decorative_uncertainty, named_not_explained, unsupported_intermediate_step, unused_assumption.
