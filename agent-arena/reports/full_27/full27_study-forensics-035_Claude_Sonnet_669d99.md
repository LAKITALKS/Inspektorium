# Forensic Dossier: Study Forensics: AI tutors show moderate gains compared to human tutors

**Run ID:** `full27_study-forensics-035_Claude_Sonnet_669d99`  
**Task:** study-forensics-035 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T08:23:40.151762+00:00  
**Task Family:** solid  
**Trap Type:** borderline_solid_with_caveats  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Sonnet
**Winner:** Claude Sonnet — **62.9/100** (margin: 0.0)
**Failure modes:** decorative_self_check, decorative_uncertainty, missed_key_insight, named_not_explained, unsupported_conclusion, unsupported_intermediate_step
**Forensic flags:** 5
**Consistency findings:** 8
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Sonnet | 30.0/30 | 0.0/8 | 4.8/8 | 4.8/6 | 3.3/6 | 4.5/6 | 0.0/8 | 4.0/8 | 1.5/10 | 10.0/10 | **62.9/100** |

## Study Forensics Audit

### Claude Sonnet

**Classification:** `solid` [+] (gold: `solid`)
**Finding Recall:** 50%
**Matched Findings:** cautious_scope_control
**Missed Findings:** evidence_matches_claim
**Extra Findings:** none_or_minor, conclusion_exceeds_results, mechanism_not_demonstrated, correlation_as_causation

## Reasoning Integrity Audit

### Claude Sonnet
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 6

## Claim Verification

### Claude Sonnet
Claims checked: 1 | Supported: 0 | Contradicted: 0 | Unresolved: 1

## Mechanism Analysis

### Claude Sonnet
| Aspect | Status |
|--------|--------|
| Concept named | :white_check_mark: effect |
| Mechanism described | :x: (0 sentence(s)) |
| Grounded to case | :x: (0 sentence(s)) |

**Missing:** mechanism not described, mechanism not grounded to case data

## Grounding Audit

### Claude Sonnet
Conclusion claims: 1
- Direct support: 0
- Indirect support: 0
- Unsupported: 1
- Contradicted: 0

**Unsupported claims:**
- "solid"


## Forensic Flags

### Claude Sonnet

- **[MODERATE]** `weak_mechanism`: Correct answer but weak mechanism explanation — answer may not generalize
  - `final_answer`: "solid"
- **[MAJOR]** `unsupported_leap`: Correct answer with weak support chain — final answer may be an unsupported leap
- **[MODERATE]** `unsupported_conclusion_claims`: 1/1 conclusion claims lack step support
  - `final_answer`: "solid"
- **[MODERATE]** `ungrounded_mechanism`: Mechanism named/described but not connected to case-specific data
  - `(mechanism analysis)`: "effect"
- **[MINOR]** `study_forensics_overflagging`: Agent raised extra findings in solid case: none_or_minor, conclusion_exceeds_results, mechanism_not_demonstrated, correlation_as_causation


## Evidence Map

### Claude Sonnet

**Correctness:** 30.0/30
  - (+) `final_answer`: "solid"
    _Agent's answer for correctness check_
  - Note: Exact match

**Support Strength:** 0.0/8
  - (-) `final_answer`: "solid"
    _Conclusion not supported by steps_
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 6
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[1]`: "Noted specific quantitative outcomes (66% vs 61% vs 56% success rates, 4-9 percentage point improvements)"
    _Most informative reasoning step_
  - Note: 6 reasoning steps
  - Note: Low step utility: 0/6 steps contribute

**Assumption Discipline:** 4.8/6
  - (+) `assumptions[1]`: "Success rates and mastery improvements were measured using valid metrics"
    _Most substantive assumption_
  - Note: 4/4 substantive assumptions

**Uncertainty Handling:** 3.3/6
  - (+) `uncertainties[1]`: "Unknown whether confounding variables were properly controlled"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.75"
    _Stated confidence level_
  - (-) `uncertainties[0]`: "Cannot assess study design quality from this brief summary"
    _Listed but never addressed in reasoning_
  - (-) `uncertainties[1]`: "Unknown whether confounding variables were properly controlled"
    _Listed but never addressed in reasoning_
  - Note: 4 uncertainties (4 substantive)
  - Note: 2 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 4.5/6
  - (+) `alternative_hypotheses[1]`: "Could be correlation_vs_causation if causal language was used inappropriately"
    _Most substantive alternative hypothesis_
  - Note: 3 alternative hypotheses considered
  - Note: 3/3 genuinely diverse alternatives

**Self Monitoring Quality:** 0.0/8
  - (+) `self_check[3]`: "Ensured I'm evaluating the text as presented, not hypothetical issues"
    _Most substantive self-verification step_
  - (-) `self_check[0]`: "Verified I'm not fabricating problems that don't exist in the text"
    _Fluff self-check_
  - Note: 4 self-check items
  - Note: Self-check quality: 0 deep, 0 arithmetic, 4 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.74, 222 words

**Insight Depth:** 4.0/8
  - (?) `(not found)`: "Missing: moderate effect"
    _Insight 'moderate effect' not found_
  - Note: Key insights: 1 full / 2


## Failure Analysis

### Claude Sonnet

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

**MINOR:**
- **Decorative Self Check** `[HEURISTIC]`: All 4 self-checks appear to be fluff — no substantive verification
  - `self_check[0]`: "Verified I'm not fabricating problems that don't exist in the text"
  - _Impacts: self_monitoring_quality_

**STYLISTIC:**
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Cannot assess study design quality from this brief summary...' is listed but not addressed
  - `uncertainties[0]`: "Cannot assess study design quality from this brief summary"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Unknown whether confounding variables were properly controll...' is listed but not addressed
  - `uncertainties[1]`: "Unknown whether confounding variables were properly controlled"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Sonnet

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/8 content words)
  - `key_claims[0]`: "AI tutoring systems can achieve comparable or slightly better outcomes than human tutoring"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/8 content words)
  - `key_claims[1]`: "AI tools can enhance human tutoring effectiveness, especially for inexperienced tutors"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/5 content words)
  - `key_claims[2]`: "AI complements rather than replaces human tutoring"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 1 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[0]`: "Cannot assess study design quality from this brief summary"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 2 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[1]`: "Unknown whether confounding variables were properly controlled"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "Could be overclaim if the studies lacked proper controls"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 2 is stated without rejection reasoning
  - `alternative_hypotheses[1]`: "Could be correlation_vs_causation if causal language was used inappropriately"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 3 is stated without rejection reasoning
  - `alternative_hypotheses[2]`: "Could be mechanism_vs_evidence if animal/lab findings were applied to humans"


## Agent Profiles

### Claude Sonnet (claude-sonnet-4-20250514)
**Parse OK:** True | **Latency:** 10420ms

**Final Answer:** solid

**Confidence:** 0.75

**Assumptions:**
- The studies had appropriate control groups
- Success rates and mastery improvements were measured using valid metrics
- The sample sizes were adequate for the reported comparisons
- The studies controlled for relevant confounding variables

**Reasoning Steps:**
1. Identified two independent studies with clear comparative designs
2. Noted specific quantitative outcomes (66% vs 61% vs 56% success rates, 4-9 percentage point improvements)
3. Observed that claims are appropriately scoped to the evidence presented
4. Confirmed the authors make modest claims about complementing rather than replacing human tutoring
5. Found no evidence of causal overclaims from correlational data
6. Verified that conclusions align with the reported findings

**Key Claims:**
- AI tutoring systems can achieve comparable or slightly better outcomes than human tutoring
- AI tools can enhance human tutoring effectiveness, especially for inexperienced tutors
- AI complements rather than replaces human tutoring

**Alternative Hypotheses:**
- Could be overclaim if the studies lacked proper controls
- Could be correlation_vs_causation if causal language was used inappropriately
- Could be mechanism_vs_evidence if animal/lab findings were applied to humans

**Uncertainties:**
- Cannot assess study design quality from this brief summary
- Unknown whether confounding variables were properly controlled
- Sample sizes and statistical significance not reported
- Duration and context of studies not specified

**Self-Verification:**
- Verified I'm not fabricating problems that don't exist in the text
- Confirmed the claims are modest and evidence-based
- Checked that no causal language exceeds the comparative evidence
- Ensured I'm evaluating the text as presented, not hypothetical issues

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 4.8/6 `########..`
- Uncertainty Handling: 3.3/6 `#####.....`
- Alternative Hypothesis Quality: 4.5/6 `#######...`
- Self Monitoring Quality: 0.0/8 `..........`
- Insight Depth: 4.0/8 `#####.....`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Sonnet** scored **62.9/100**.

**Best per dimension:**
- Correctness: Claude Sonnet (30.0/30)
- Support Strength: Claude Sonnet (0.0/8)
- Structural Reasoning: Claude Sonnet (4.8/8)
- Assumption Discipline: Claude Sonnet (4.8/6)
- Uncertainty Handling: Claude Sonnet (3.3/6)
- Alternative Hypothesis Quality: Claude Sonnet (4.5/6)
- Self Monitoring Quality: Claude Sonnet (0.0/8)
- Insight Depth: Claude Sonnet (4.0/8)
- Mechanism Quality: Claude Sonnet (1.5/10)
- Communication Efficiency: Claude Sonnet (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Sonnet | 10.4s | 62.9/100 | 6.0 |

Failure modes observed: decorative_self_check, decorative_uncertainty, missed_key_insight, named_not_explained, unsupported_conclusion, unsupported_intermediate_step.
