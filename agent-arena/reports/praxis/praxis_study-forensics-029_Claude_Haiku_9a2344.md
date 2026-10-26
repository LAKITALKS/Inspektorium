# Forensic Dossier: Study Forensics: Amyloid-targeting antibody improves biomarkers without cognitive benefit

**Run ID:** `praxis_study-forensics-029_Claude_Haiku_9a2344`  
**Task:** study-forensics-029 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-07T07:55:58.460166+00:00  
**Task Family:** solid  
**Trap Type:** borderline_solid_with_caveats  
**Ambiguity:** medium  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **70.8/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, missed_key_insight, unsupported_conclusion, unsupported_intermediate_step, unused_assumption
**Forensic flags:** 4
**Consistency findings:** 9
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 30.0/30 | 0.0/8 | 4.8/8 | 4.3/6 | 3.6/6 | 4.5/6 | 5.6/8 | 8.0/8 | 0.0/10 | 10.0/10 | **70.8/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `solid` [+] (gold: `solid`)
**Finding Recall:** 50%
**Matched Findings:** cautious_scope_control
**Missed Findings:** evidence_matches_claim
**Extra Findings:** none_or_minor, conclusion_exceeds_results, decorative_uncertainty, mechanism_not_demonstrated, correlation_as_causation

## Reasoning Integrity Audit

### Claude Haiku
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 7

## Mechanism Analysis

### Claude Haiku
| Aspect | Status |
|--------|--------|
| Concept named | :x: none |
| Mechanism described | :x: (0 sentence(s)) |
| Grounded to case | :x: (0 sentence(s)) |

**Missing:** concept not named, mechanism not described, mechanism not grounded to case data

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
  - (+) `steps[1]`: "Checked for overclaim: The text does NOT claim cognitive benefits occurred. It explicitly states they 'remain unproven' "
    _Most informative reasoning step_
  - Note: 7 reasoning steps
  - Note: Low step utility: 0/7 steps contribute

**Assumption Discipline:** 4.3/6
  - (+) `assumptions[1]`: "The biomarker measurements (amyloid deposits, neurodegeneration markers) were validated and objectively measured"
    _Most substantive assumption_
  - (-) `assumptions[1]`: "The biomarker measurements (amyloid deposits, neurodegeneration markers) were validated and objectively measured"
    _Declared but unused in reasoning_
  - Note: 5/5 substantive assumptions
  - Note: 1 unused assumption(s)

**Uncertainty Handling:** 3.6/6
  - (+) `uncertainties[2]`: "The duration of follow-up and whether longer observation might reveal delayed cognitive benefits"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.88"
    _Stated confidence level_
  - (-) `uncertainties[3]`: "Whether the inherited Alzheimer's population generalizes to sporadic Alzheimer's disease"
    _Listed but never addressed in reasoning_
  - Note: 5 uncertainties (5 substantive)
  - Note: 1 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 4.5/6
  - (+) `alternative_hypotheses[1]`: "Mechanism vs. evidence: if the text had stated that amyloid clearance *causes* cognitive improvement in humans based on "
    _Most substantive alternative hypothesis_
  - Note: 3 alternative hypotheses considered
  - Note: 3/3 genuinely diverse alternatives

**Self Monitoring Quality:** 5.6/8
  - (+) `self_check[4]`: "Could this be a solid study reporting a negative/null result? Yes—Phase 2/3 randomized trials can legitimately fail to s"
    _Most substantive self-verification step_
  - Note: 5 self-check items
  - Note: Self-check quality: 0 deep, 5 arithmetic, 0 fluff

**Mechanism Quality:** 0.0/10
  - Note: Neither names concept nor explains mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.72, 445 words

**Insight Depth:** 8.0/8
  - Note: Key insights: 2 full / 2


## Failure Analysis

### Claude Haiku

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

**STYLISTIC:**
- **Unused Assumption** `[HEURISTIC]`: Assumption 'The biomarker measurements (amyloid deposits, neurodegenerat...' is declared but not referenced in reasoning
  - `assumptions[1]`: "The biomarker measurements (amyloid deposits, neurodegeneration markers) were validated and objectiv"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether the inherited Alzheimer's population generalizes to ...' is listed but not addressed
  - `uncertainties[3]`: "Whether the inherited Alzheimer's population generalizes to sporadic Alzheimer's disease"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/12 content words)
  - `key_claims[0]`: "The study demonstrates a dissociation between biomarker improvement and clinical cognitive outcomes—"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/10 content words)
  - `key_claims[1]`: "Investigators appropriately acknowledge the unproven cognitive benefit rather than overselling bioma"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/8 content words)
  - `key_claims[2]`: "The proposal for open-label extension is reasonable but explicitly framed as exploratory, not confir"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/7 content words)
  - `key_claims[3]`: "No causal claims about biomarkers driving cognition are made in this summary"
- **[WARN]** `[HEURISTIC]` `claim_step_alignment`: Key claim 4 not well supported in reasoning steps (1/7 content words found)
  - `key_claims[3]`: "No causal claims about biomarkers driving cognition are made in this summary"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 4 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[3]`: "Whether the inherited Alzheimer's population generalizes to sporadic Alzheimer's disease"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "Overclaim: if the text had claimed cognitive benefits were likely or imminent based on biomarkers al"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 2 is stated without rejection reasoning
  - `alternative_hypotheses[1]`: "Mechanism vs. evidence: if the text had stated that amyloid clearance *causes* cognitive improvement"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 3 is stated without rejection reasoning
  - `alternative_hypotheses[2]`: "Correlation vs. causation: if the text had implied biomarker reduction necessarily causes cognitive "


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 10128ms

**Final Answer:** solid

**Confidence:** 0.88

**Assumptions:**
- This is a genuine Phase 2/3 randomized trial with appropriate controls for the biomarker phase
- The biomarker measurements (amyloid deposits, neurodegeneration markers) were validated and objectively measured
- Cognitive decline was measured using standard clinical instruments
- The trial was adequately powered to detect cognitive effects if they existed
- The summary accurately represents what the investigators reported

**Reasoning Steps:**
1. Identified the core claim: drug reduced biomarkers but failed to slow cognitive decline
2. Checked for overclaim: The text does NOT claim cognitive benefits occurred. It explicitly states they 'remain unproven' and the trial 'failed to show' slowing of decline
3. Checked for mechanism vs. evidence: The investigators propose biomarker improvement as mechanistically relevant but do NOT claim this proves cognitive benefit will follow
4. Checked for correlation vs. causation: The text describes associations (biomarker reduction) without claiming causation of cognitive outcomes
5. Checked for decorative uncertainty: The acknowledgment that 'cognitive benefits remain unproven' is substantive, not decorative—it directly contradicts the biomarker success
6. Checked for confounders: The randomized design controls for most confounders; the failure to show cognitive benefit despite biomarker success is itself the key finding
7. Evaluated the open-label extension proposal: This is reasonable given biomarker success, though appropriately cautious given cognitive failure

**Key Claims:**
- The study demonstrates a dissociation between biomarker improvement and clinical cognitive outcomes—a critical negative finding
- Investigators appropriately acknowledge the unproven cognitive benefit rather than overselling biomarker success
- The proposal for open-label extension is reasonable but explicitly framed as exploratory, not confirmatory
- No causal claims about biomarkers driving cognition are made in this summary

**Alternative Hypotheses:**
- Overclaim: if the text had claimed cognitive benefits were likely or imminent based on biomarkers alone
- Mechanism vs. evidence: if the text had stated that amyloid clearance *causes* cognitive improvement in humans based on animal or biomarker data
- Correlation vs. causation: if the text had implied biomarker reduction necessarily causes cognitive benefit

**Uncertainties:**
- Whether the trial was adequately powered for cognitive endpoints (not stated in summary)
- The specific cognitive measures used and their sensitivity
- The duration of follow-up and whether longer observation might reveal delayed cognitive benefits
- Whether the inherited Alzheimer's population generalizes to sporadic Alzheimer's disease
- The clinical significance of the biomarker improvements (magnitude not specified)

**Self-Verification:**
- Did I flag problems that don't exist? No—the dissociation between biomarkers and cognition is a genuine and important finding, not a methodological flaw
- Did I miss overclaiming? No—the text explicitly states cognitive benefits are unproven
- Did I miss mechanism vs. evidence problems? No—no unsupported mechanistic claims are made
- Is the acknowledgment of uncertainty genuine? Yes—it directly contradicts the biomarker success, making it substantive rather than decorative
- Could this be a solid study reporting a negative/null result? Yes—Phase 2/3 randomized trials can legitimately fail to show clinical benefit despite biomarker changes

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 4.3/6 `#######...`
- Uncertainty Handling: 3.6/6 `######....`
- Alternative Hypothesis Quality: 4.5/6 `#######...`
- Self Monitoring Quality: 5.6/8 `#######...`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 0.0/10 `..........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Haiku** scored **70.8/100**.

**Best per dimension:**
- Correctness: Claude Haiku (30.0/30)
- Support Strength: Claude Haiku (0.0/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (4.3/6)
- Uncertainty Handling: Claude Haiku (3.6/6)
- Alternative Hypothesis Quality: Claude Haiku (4.5/6)
- Self Monitoring Quality: Claude Haiku (5.6/8)
- Insight Depth: Claude Haiku (8.0/8)
- Mechanism Quality: Claude Haiku (0.0/10)
- Communication Efficiency: Claude Haiku (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 10.1s | 70.8/100 | 7.0 |

Failure modes observed: decorative_uncertainty, missed_key_insight, unsupported_conclusion, unsupported_intermediate_step, unused_assumption.
