# Forensic Dossier: Study Forensics: AI tutors show moderate gains compared to human tutors

**Run ID:** `full27_study-forensics-035_Claude_Opus_b9d5e0`  
**Task:** study-forensics-035 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T18:06:23.050342+00:00  
**Task Family:** solid  
**Trap Type:** borderline_solid_with_caveats  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Opus
**Winner:** Claude Opus — **61.8/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, missed_key_insight, unsupported_conclusion, unsupported_intermediate_step, unused_assumption
**Forensic flags:** 4
**Consistency findings:** 12
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Opus | 30.0/30 | 0.0/8 | 4.8/8 | 4.3/6 | 3.0/6 | 4.5/6 | 1.2/8 | 4.0/8 | 0.0/10 | 10.0/10 | **61.8/100** |

## Study Forensics Audit

### Claude Opus

**Classification:** `solid` [+] (gold: `solid`)
**Finding Recall:** 50%
**Matched Findings:** cautious_scope_control
**Missed Findings:** evidence_matches_claim
**Extra Findings:** none_or_minor, conclusion_exceeds_results, unsupported_generalization, mechanism_not_demonstrated, correlation_as_causation

## Reasoning Integrity Audit

### Claude Opus
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 6

## Claim Verification

### Claude Opus
Claims checked: 1 | Supported: 0 | Contradicted: 0 | Unresolved: 1

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
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 6
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[0]`: "Identified two independent human studies comparing AI-assisted learning with traditional methods"
    _Most informative reasoning step_
  - Note: 6 reasoning steps
  - Note: Low step utility: 0/6 steps contribute

**Assumption Discipline:** 4.3/6
  - (+) `assumptions[1]`: "Success rates and topic mastery are valid educational outcome measures"
    _Most substantive assumption_
  - (-) `assumptions[2]`: "The sample sizes were adequate for the reported effects"
    _Declared but unused in reasoning_
  - Note: 4/4 substantive assumptions
  - Note: 1 unused assumption(s)

**Uncertainty Handling:** 3.0/6
  - (+) `uncertainties[0]`: "Whether the studies were randomized controlled trials or observational"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.85"
    _Stated confidence level_
  - (-) `uncertainties[0]`: "Whether the studies were randomized controlled trials or observational"
    _Listed but never addressed in reasoning_
  - (-) `uncertainties[1]`: "Statistical significance and confidence intervals not reported"
    _Listed but never addressed in reasoning_
  - Note: 4 uncertainties (4 substantive)
  - Note: 4 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 4.5/6
  - (+) `alternative_hypotheses[1]`: "Could be correlation_vs_causation if these were observational rather than experimental studies"
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 2/2 genuinely diverse alternatives

**Self Monitoring Quality:** 1.2/8
  - (+) `self_check[0]`: "Verified no tier mismatch - human studies supporting conclusions about human learning"
    _Most substantive self-verification step_
  - (-) `self_check[1]`: "Checked for promotional language - none found"
    _Fluff self-check_
  - Note: 4 self-check items
  - Note: Self-check quality: 0 deep, 1 arithmetic, 3 fluff

**Mechanism Quality:** 0.0/10
  - Note: Neither names concept nor explains mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.80, 227 words

**Insight Depth:** 4.0/8
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

**STYLISTIC:**
- **Unused Assumption** `[HEURISTIC]`: Assumption 'The sample sizes were adequate for the reported effects...' is declared but not referenced in reasoning
  - `assumptions[2]`: "The sample sizes were adequate for the reported effects"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether the studies were randomized controlled trials or obs...' is listed but not addressed
  - `uncertainties[0]`: "Whether the studies were randomized controlled trials or observational"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Statistical significance and confidence intervals not report...' is listed but not addressed
  - `uncertainties[1]`: "Statistical significance and confidence intervals not reported"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Generalizability to other educational contexts not discussed...' is listed but not addressed
  - `uncertainties[2]`: "Generalizability to other educational contexts not discussed"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Long-term retention effects unknown...' is listed but not addressed
  - `uncertainties[3]`: "Long-term retention effects unknown"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Opus

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/5 content words)
  - `key_claims[0]`: "The text reports human-level evidence for human-level conclusions"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/6 content words)
  - `key_claims[1]`: "Quantitative results are presented without rhetorical inflation"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/8 content words)
  - `key_claims[2]`: "Authors appropriately scope their claims to complementing rather than replacing tutors"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/4 content words)
  - `key_claims[3]`: "No mechanism-only speculation about how AI might work"
- **[WARN]** `[HEURISTIC]` `claim_step_alignment`: Key claim 2 not well supported in reasoning steps (1/6 content words found)
  - `key_claims[1]`: "Quantitative results are presented without rhetorical inflation"
- **[WARN]** `[HEURISTIC]` `claim_step_alignment`: Key claim 4 not well supported in reasoning steps (0/4 content words found)
  - `key_claims[3]`: "No mechanism-only speculation about how AI might work"
- **[WARN]** `[HEURISTIC]` `unused_assumption`: Assumption 3 appears unused in reasoning or answer
  - `assumptions[2]`: "The sample sizes were adequate for the reported effects"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 2 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[1]`: "Statistical significance and confidence intervals not reported"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 3 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[2]`: "Generalizability to other educational contexts not discussed"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 4 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[3]`: "Long-term retention effects unknown"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "Could be overclaim if the effect sizes are presented without appropriate statistical context"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 2 is stated without rejection reasoning
  - `alternative_hypotheses[1]`: "Could be correlation_vs_causation if these were observational rather than experimental studies"


## Agent Profiles

### Claude Opus (claude-opus-4-20250514)
**Parse OK:** True | **Latency:** 16395ms

**Final Answer:** solid

**Confidence:** 0.85

**Assumptions:**
- The studies involved actual human students in real learning contexts
- Success rates and topic mastery are valid educational outcome measures
- The sample sizes were adequate for the reported effects
- The studies were properly controlled

**Reasoning Steps:**
1. Identified two independent human studies comparing AI-assisted learning with traditional methods
2. Noted specific quantitative outcomes: 66% vs 61% vs 56% success rates in study 1
3. Noted 4-9 percentage point improvements in topic mastery in study 2
4. Observed that conclusions stay within the evidence tier - no extrapolation beyond what was studied
5. Authors explicitly limit claims: AI complements rather than replaces human tutoring
6. No evidence of causal language beyond what the experimental design supports

**Key Claims:**
- The text reports human-level evidence for human-level conclusions
- Quantitative results are presented without rhetorical inflation
- Authors appropriately scope their claims to complementing rather than replacing tutors
- No mechanism-only speculation about how AI might work

**Alternative Hypotheses:**
- Could be overclaim if the effect sizes are presented without appropriate statistical context
- Could be correlation_vs_causation if these were observational rather than experimental studies

**Uncertainties:**
- Whether the studies were randomized controlled trials or observational
- Statistical significance and confidence intervals not reported
- Generalizability to other educational contexts not discussed
- Long-term retention effects unknown

**Self-Verification:**
- Verified no tier mismatch - human studies supporting conclusions about human learning
- Checked for promotional language - none found
- Confirmed modest claims match modest evidence
- No red flags for correlation/causation confusion in experimental context

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 4.3/6 `#######...`
- Uncertainty Handling: 3.0/6 `####......`
- Alternative Hypothesis Quality: 4.5/6 `#######...`
- Self Monitoring Quality: 1.2/8 `#.........`
- Insight Depth: 4.0/8 `#####.....`
- Mechanism Quality: 0.0/10 `..........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Opus** scored **61.8/100**.

**Best per dimension:**
- Correctness: Claude Opus (30.0/30)
- Support Strength: Claude Opus (0.0/8)
- Structural Reasoning: Claude Opus (4.8/8)
- Assumption Discipline: Claude Opus (4.3/6)
- Uncertainty Handling: Claude Opus (3.0/6)
- Alternative Hypothesis Quality: Claude Opus (4.5/6)
- Self Monitoring Quality: Claude Opus (1.2/8)
- Insight Depth: Claude Opus (4.0/8)
- Mechanism Quality: Claude Opus (0.0/10)
- Communication Efficiency: Claude Opus (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Opus | 16.4s | 61.8/100 | 3.8 |

Failure modes observed: decorative_uncertainty, missed_key_insight, unsupported_conclusion, unsupported_intermediate_step, unused_assumption.
