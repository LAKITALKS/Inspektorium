# Forensic Dossier: Study Forensics: AI tutors show moderate gains compared to human tutors

**Run ID:** `minival_study-forensics-035_Claude_Opus_e1810e`  
**Task:** study-forensics-035 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T07:54:48.759061+00:00  
**Task Family:** solid  
**Trap Type:** borderline_solid_with_caveats  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Opus
**Winner:** Claude Opus — **62.1/100** (margin: 0.0)
**Failure modes:** decorative_self_check, decorative_uncertainty, missed_key_insight, unsupported_conclusion, unsupported_intermediate_step, unused_assumption
**Forensic flags:** 4
**Consistency findings:** 9
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Opus | 30.0/30 | 0.0/8 | 4.8/8 | 4.3/6 | 3.0/6 | 6.0/6 | 0.0/8 | 4.0/8 | 0.0/10 | 10.0/10 | **62.1/100** |

## Study Forensics Audit

### Claude Opus

**Classification:** `solid` [+] (gold: `solid`)
**Finding Recall:** 0%
**Missed Findings:** evidence_matches_claim, cautious_scope_control
**Extra Findings:** none_or_minor, conclusion_exceeds_results, unsupported_generalization, mechanism_not_demonstrated, correlation_as_causation

## Reasoning Integrity Audit

### Claude Opus
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 7

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
- "solid"


## Forensic Flags

### Claude Opus

- **[MODERATE]** `weak_mechanism`: Correct answer but weak mechanism explanation — answer may not generalize
  - `final_answer`: "solid"
- **[MAJOR]** `unsupported_leap`: Correct answer with weak support chain — final answer may be an unsupported leap
- **[MODERATE]** `unsupported_conclusion_claims`: 1/1 conclusion claims lack step support
  - `final_answer`: "solid"
- **[MINOR]** `study_forensics_overflagging`: Agent raised extra findings in solid case: none_or_minor, conclusion_exceeds_results, unsupported_generalization, mechanism_not_demonstrated, correlation_as_causation


## Evidence Map

### Claude Opus

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
  - (+) `steps[1]`: "First study shows modest improvements: AI (66%) vs human tutoring (61%) vs written hints (56%)"
    _Most informative reasoning step_
  - Note: 7 reasoning steps
  - Note: Low step utility: 0/7 steps contribute

**Assumption Discipline:** 4.3/6
  - (+) `assumptions[3]`: "Success rate and topic mastery are valid measures of learning effectiveness"
    _Most substantive assumption_
  - (-) `assumptions[3]`: "Success rate and topic mastery are valid measures of learning effectiveness"
    _Declared but unused in reasoning_
  - Note: 4/4 substantive assumptions
  - Note: 1 unused assumption(s)

**Uncertainty Handling:** 3.0/6
  - (+) `uncertainties[0]`: "Statistical significance of the reported differences"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.75"
    _Stated confidence level_
  - (-) `uncertainties[0]`: "Statistical significance of the reported differences"
    _Listed but never addressed in reasoning_
  - (-) `uncertainties[2]`: "How 'success rate' and 'topic mastery' were measured"
    _Listed but never addressed in reasoning_
  - Note: 5 uncertainties (5 substantive)
  - Note: 4 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 6.0/6
  - (+) `alternative_hypotheses[1]`: "Could be correlation vs causation if other factors explain the differences, but the controlled comparison design suggest"
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 2/2 include rejection reasoning

**Self Monitoring Quality:** 0.0/8
  - (+) `self_check[1]`: "Checked for causation claims - comparative results presented appropriately"
    _Most substantive self-verification step_
  - (-) `self_check[0]`: "Reviewed for overclaiming - none found, improvements are modest"
    _Fluff self-check_
  - Note: 5 self-check items
  - Note: Self-check quality: 0 deep, 0 arithmetic, 5 fluff

**Mechanism Quality:** 0.0/10
  - Note: Neither names concept nor explains mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.79, 251 words

**Insight Depth:** 4.0/8
  - (+) `(output text)`: "ided without exaggeration the complementary rather than replacement frami"
    _Insight 'complementary' matched (exact)_
  - (?) `(not found)`: "Missing: moderate effect"
    _Insight 'moderate effect' not found_
  - Note: Key insights: 1 full / 2


## Failure Analysis

### Claude Opus

**MODERATE:**
- **Unsupported Conclusion** `[MEDIUM CONFIDENCE]`: Final answer lacks load-bearing or supporting step grounding
  - `final_answer`: "solid"
  - _Impacts: support_strength_
- **Unsupported Intermediate Step** `[MEDIUM CONFIDENCE]`: No reasoning step is load-bearing — final answer lacks traceable derivation
  - `final_answer`: "solid"
  - _Impacts: support_strength, structural_reasoning_
- **Missed Key Insight** `[MEDIUM CONFIDENCE]`: Missed expected finding: evidence_matches_claim
  - `(task expectation)`: "Expected: evidence_matches_claim"
  - _Impacts: insight_depth_
- **Missed Key Insight** `[MEDIUM CONFIDENCE]`: Missed expected finding: cautious_scope_control
  - `(task expectation)`: "Expected: cautious_scope_control"
  - _Impacts: insight_depth_

**MINOR:**
- **Decorative Self Check** `[HEURISTIC]`: All 5 self-checks appear to be fluff — no substantive verification
  - `self_check[0]`: "Reviewed for overclaiming - none found, improvements are modest"
  - _Impacts: self_monitoring_quality_

**STYLISTIC:**
- **Unused Assumption** `[HEURISTIC]`: Assumption 'Success rate and topic mastery are valid measures of learnin...' is declared but not referenced in reasoning
  - `assumptions[3]`: "Success rate and topic mastery are valid measures of learning effectiveness"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Statistical significance of the reported differences...' is listed but not addressed
  - `uncertainties[0]`: "Statistical significance of the reported differences"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'How 'success rate' and 'topic mastery' were measured...' is listed but not addressed
  - `uncertainties[2]`: "How 'success rate' and 'topic mastery' were measured"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether randomization was used...' is listed but not addressed
  - `uncertainties[3]`: "Whether randomization was used"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Potential selection bias in who used which system...' is listed but not addressed
  - `uncertainties[4]`: "Potential selection bias in who used which system"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Opus

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/6 content words)
  - `key_claims[0]`: "The text makes appropriately modest claims about AI performance"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/6 content words)
  - `key_claims[1]`: "Specific quantitative results are provided without exaggeration"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/6 content words)
  - `key_claims[2]`: "The complementary rather than replacement framing is epistemically appropriate"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/5 content words)
  - `key_claims[3]`: "No unsupported generalizations beyond the study contexts"
- **[WARN]** `[HEURISTIC]` `unused_assumption`: Assumption 4 appears unused in reasoning or answer
  - `assumptions[3]`: "Success rate and topic mastery are valid measures of learning effectiveness"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 1 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[0]`: "Statistical significance of the reported differences"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 3 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[2]`: "How 'success rate' and 'topic mastery' were measured"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 4 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[3]`: "Whether randomization was used"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 5 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[4]`: "Potential selection bias in who used which system"


## Agent Profiles

### Claude Opus (claude-opus-4-20250514)
**Parse OK:** True | **Latency:** 15840ms

**Final Answer:** solid

**Confidence:** 0.75

**Assumptions:**
- The studies measured actual learning outcomes, not just satisfaction
- The percentage differences reported are statistically significant
- The studies had appropriate sample sizes and controls
- Success rate and topic mastery are valid measures of learning effectiveness

**Reasoning Steps:**
1. Identified two independent studies with specific quantitative results
2. First study shows modest improvements: AI (66%) vs human tutoring (61%) vs written hints (56%)
3. Second study shows 4 percentage point improvement overall, 9 points for inexperienced tutors
4. Authors explicitly state AI complements rather than replaces human tutoring
5. No causal language used inappropriately - results are presented as comparative outcomes
6. No mechanism claims made without evidence
7. No overclaiming detected - improvements are modest and specific

**Key Claims:**
- The text makes appropriately modest claims about AI performance
- Specific quantitative results are provided without exaggeration
- The complementary rather than replacement framing is epistemically appropriate
- No unsupported generalizations beyond the study contexts

**Alternative Hypotheses:**
- Could be overclaim if the differences aren't statistically significant, but text doesn't make claims beyond the data
- Could be correlation vs causation if other factors explain the differences, but the controlled comparison design suggests this is addressed

**Uncertainties:**
- Statistical significance of the reported differences
- Sample sizes and study duration
- How 'success rate' and 'topic mastery' were measured
- Whether randomization was used
- Potential selection bias in who used which system

**Self-Verification:**
- Reviewed for overclaiming - none found, improvements are modest
- Checked for causation claims - comparative results presented appropriately
- Looked for mechanism claims - none made
- Verified the authors' conclusion matches the data - it does
- Did not fabricate problems where none exist

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 4.3/6 `#######...`
- Uncertainty Handling: 3.0/6 `####......`
- Alternative Hypothesis Quality: 6.0/6 `##########`
- Self Monitoring Quality: 0.0/8 `..........`
- Insight Depth: 4.0/8 `#####.....`
- Mechanism Quality: 0.0/10 `..........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Opus** scored **62.1/100**.

**Best per dimension:**
- Correctness: Claude Opus (30.0/30)
- Support Strength: Claude Opus (0.0/8)
- Structural Reasoning: Claude Opus (4.8/8)
- Assumption Discipline: Claude Opus (4.3/6)
- Uncertainty Handling: Claude Opus (3.0/6)
- Alternative Hypothesis Quality: Claude Opus (6.0/6)
- Self Monitoring Quality: Claude Opus (0.0/8)
- Insight Depth: Claude Opus (4.0/8)
- Mechanism Quality: Claude Opus (0.0/10)
- Communication Efficiency: Claude Opus (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Opus | 15.8s | 62.1/100 | 3.9 |

Failure modes observed: decorative_self_check, decorative_uncertainty, missed_key_insight, unsupported_conclusion, unsupported_intermediate_step, unused_assumption.
