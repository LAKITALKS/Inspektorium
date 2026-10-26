# Forensic Dossier: Study Forensics: AI tutors show moderate gains compared to human tutors

**Run ID:** `full27_study-forensics-035_Claude_Haiku_542412`  
**Task:** study-forensics-035 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T17:09:02.221601+00:00  
**Task Family:** solid  
**Trap Type:** borderline_solid_with_caveats  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **69.3/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, missed_key_insight, named_not_explained, unsupported_conclusion, unsupported_intermediate_step
**Forensic flags:** 5
**Consistency findings:** 8
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 30.0/30 | 0.0/8 | 4.8/8 | 4.8/6 | 3.3/6 | 6.0/6 | 6.4/8 | 4.0/8 | 1.5/10 | 8.5/10 | **69.3/100** |

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

## Claim Verification

### Claude Haiku
Claims checked: 1 | Supported: 0 | Contradicted: 0 | Unresolved: 1

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
  - (+) `steps[2]`: "Assessed bridge: The evidence directly measures human learning outcomes (success rates, topic mastery) in the target pop"
    _Most informative reasoning step_
  - Note: 9 reasoning steps
  - Note: Low step utility: 0/9 steps contribute

**Assumption Discipline:** 4.8/6
  - (+) `assumptions[4]`: "The studies were adequately powered and used appropriate statistical methods (not stated but assumed from peer publicati"
    _Most substantive assumption_
  - Note: 5/5 substantive assumptions

**Uncertainty Handling:** 3.3/6
  - (+) `uncertainties[2]`: "Whether the 76.4% validation rate is a measure of safety/quality or just agreement (could be interpreted either way)"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.82"
    _Stated confidence level_
  - (-) `uncertainties[1]`: "Sample sizes and statistical significance of the reported differences (not provided)"
    _Listed but never addressed in reasoning_
  - (-) `uncertainties[2]`: "Whether the 76.4% validation rate is a measure of safety/quality or just agreement (could be interpreted either way)"
    _Listed but never addressed in reasoning_
  - Note: 5 uncertainties (5 substantive)
  - Note: 2 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 6.0/6
  - (+) `alternative_hypotheses[2]`: "Could classify as mechanism_vs_evidence if the text implied AI would work in all educational contexts or for all learner"
    _Most substantive alternative hypothesis_
  - Note: 3 alternative hypotheses considered
  - Note: 3/3 include rejection reasoning

**Self Monitoring Quality:** 6.4/8
  - (+) `self_check[3]`: "Did I miss confounders? Possibly — tutor training, student motivation, and prior knowledge are not explicitly addressed,"
    _Most substantive self-verification step_
  - Note: 5 self-check items
  - Note: Self-check quality: 1 deep, 4 arithmetic, 0 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 8.5/10
  - Note: Signal density: 0.72, 668 words

**Insight Depth:** 4.0/8
  - (+) `(output text)`: "appropriately position ai as complementary to human tutoring, not a repl"
    _Insight 'complementary' matched (exact)_
  - (?) `(not found)`: "Missing: moderate effect"
    _Insight 'moderate effect' not found_
  - Note: Key insights: 1 full / 2


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
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Sample sizes and statistical significance of the reported di...' is listed but not addressed
  - `uncertainties[1]`: "Sample sizes and statistical significance of the reported differences (not provided)"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether the 76.4% validation rate is a measure of safety/qua...' is listed but not addressed
  - `uncertainties[2]`: "Whether the 76.4% validation rate is a measure of safety/quality or just agreement (could be interpr"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/14 content words)
  - `key_claims[0]`: "AI tutoring systems achieve higher success rates than human tutors in these studies (66% vs 61%), a "
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/16 content words)
  - `key_claims[1]`: "AI-assisted tutoring improves topic mastery, with larger gains for inexperienced tutors (9 points), "
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/10 content words)
  - `key_claims[2]`: "Tutors validate most AI-generated answers (76.4%), indicating reasonable quality control."
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/9 content words)
  - `key_claims[3]`: "The authors appropriately position AI as complementary to human tutoring, not a replacement — this i"
- **[WARN]** `[HEURISTIC]` `claim_step_alignment`: Key claim 3 not well supported in reasoning steps (1/10 content words found)
  - `key_claims[2]`: "Tutors validate most AI-generated answers (76.4%), indicating reasonable quality control."
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 2 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[1]`: "Sample sizes and statistical significance of the reported differences (not provided)"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 3 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[2]`: "Whether the 76.4% validation rate is a measure of safety/quality or just agreement (could be interpr"
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "solid"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 14260ms

**Final Answer:** solid

**Confidence:** 0.82

**Assumptions:**
- Both studies involved actual human learners in educational settings (not simulations or animal models)
- Success rate and topic mastery are appropriate outcome measures for learning effectiveness
- The studies compared AI systems against relevant control conditions (human tutors, written hints)
- The 76.4% validation rate reflects actual tutor assessment of AI quality
- The studies were adequately powered and used appropriate statistical methods (not stated but assumed from peer publication)

**Reasoning Steps:**
1. Identified evidence tier: Both studies involve human learners in real educational contexts comparing AI tutoring systems to human tutors and other controls. This is clinical human evidence.
2. Identified conclusion tier: The text draws conclusions about learning effectiveness for students using AI systems — a human educational outcome.
3. Assessed bridge: The evidence directly measures human learning outcomes (success rates, topic mastery) in the target population (students). No inferential leap from animals to humans or from biomarkers to clinical benefit is required.
4. Evaluated claims: Study 1 reports specific comparative success rates (66% AI vs 61% human vs 56% written). Study 2 reports mastery gains (4 points overall, 9 points for inexperienced tutors). These are direct measurements, not surrogate endpoints.
5. Checked for overclaim: The text reports effect sizes without exaggeration. The 5-percentage-point advantage in Study 1 is modest and presented as such. Study 2's 4–9 point gains are contextualized by tutor experience.
6. Checked for mechanism vs. evidence: The text does not claim to explain *why* AI works or extrapolate to untested populations. It reports what was measured.
7. Evaluated hedging: The final sentence ('AI does not replace human tutoring but complements it') is appropriate and supported by the data showing AI as an adjunct, not a replacement. This is not decorative uncertainty; it reflects the study design.
8. Checked for confounders: No obvious confounders are ignored. The studies compare AI to human tutors and written hints, controlling for the tutoring modality. Tutor experience is explicitly analyzed in Study 2.
9. Checked for correlation vs. causation: The studies appear to use comparative designs (AI vs. control), not purely observational. The causal framing is appropriate for this design.

**Key Claims:**
- AI tutoring systems achieve higher success rates than human tutors in these studies (66% vs 61%), a modest but measurable advantage.
- AI-assisted tutoring improves topic mastery, with larger gains for inexperienced tutors (9 points), suggesting AI may reduce tutor skill variance.
- Tutors validate most AI-generated answers (76.4%), indicating reasonable quality control.
- The authors appropriately position AI as complementary to human tutoring, not a replacement — this is supported by the data.

**Alternative Hypotheses:**
- Could classify as overclaim if the 5-percentage-point difference in Study 1 is clinically trivial — but the text presents it as a modest finding, not a breakthrough.
- Could flag decorative uncertainty if the final sentence were present but the body made stronger claims — but the body is appropriately cautious.
- Could classify as mechanism_vs_evidence if the text implied AI would work in all educational contexts or for all learners — but it reports specific outcomes in specific studies.

**Uncertainties:**
- Whether the studies are RCTs or quasi-experimental designs (not specified in the summary)
- Sample sizes and statistical significance of the reported differences (not provided)
- Whether the 76.4% validation rate is a measure of safety/quality or just agreement (could be interpreted either way)
- Whether 'topic mastery' is a validated measure or a study-specific outcome
- Whether the studies controlled for confounders like student prior knowledge, motivation, or tutor training quality

**Self-Verification:**
- Did I overclassify as solid? No — the studies directly measure human learning outcomes in real educational settings with appropriate controls. This is legitimate clinical evidence.
- Did I miss a mechanism vs. evidence problem? No — the text does not extrapolate beyond what was measured or claim to explain mechanisms.
- Did I miss an overclaim? No — the effect sizes are modest and presented without exaggeration.
- Did I miss confounders? Possibly — tutor training, student motivation, and prior knowledge are not explicitly addressed, but this is a limitation of the summary, not the text itself.
- Is the hedging appropriate? Yes — the final sentence reflects the study design and findings, not decorative uncertainty.

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 4.8/6 `########..`
- Uncertainty Handling: 3.3/6 `#####.....`
- Alternative Hypothesis Quality: 6.0/6 `##########`
- Self Monitoring Quality: 6.4/8 `########..`
- Insight Depth: 4.0/8 `#####.....`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 8.5/10 `########..`


## Final Verdict

**Solo run: Claude Haiku** scored **69.3/100**.

**Best per dimension:**
- Correctness: Claude Haiku (30.0/30)
- Support Strength: Claude Haiku (0.0/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (4.8/6)
- Uncertainty Handling: Claude Haiku (3.3/6)
- Alternative Hypothesis Quality: Claude Haiku (6.0/6)
- Self Monitoring Quality: Claude Haiku (6.4/8)
- Insight Depth: Claude Haiku (4.0/8)
- Mechanism Quality: Claude Haiku (1.5/10)
- Communication Efficiency: Claude Haiku (8.5/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 14.3s | 69.3/100 | 4.9 |

Failure modes observed: decorative_uncertainty, missed_key_insight, named_not_explained, unsupported_conclusion, unsupported_intermediate_step.
