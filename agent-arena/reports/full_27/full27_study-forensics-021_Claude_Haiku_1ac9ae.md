# Forensic Dossier: Study Forensics: Virtual tutoring boosts reading skills

**Run ID:** `full27_study-forensics-021_Claude_Haiku_1ac9ae`  
**Task:** study-forensics-021 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T17:55:44.586141+00:00  
**Task Family:** solid  
**Trap Type:** overflagging_solid_study  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **73.8/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, missed_key_insight, named_not_explained, unsupported_conclusion, unsupported_intermediate_step
**Forensic flags:** 5
**Consistency findings:** 7
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 30.0/30 | 0.0/8 | 4.8/8 | 4.8/6 | 3.0/6 | 6.0/6 | 7.2/8 | 8.0/8 | 1.5/10 | 8.5/10 | **73.8/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `solid` [+] (gold: `solid`)
**Finding Recall:** 50%
**Matched Findings:** cautious_scope_control
**Missed Findings:** evidence_matches_claim
**Extra Findings:** none_or_minor, conclusion_exceeds_results, decorative_uncertainty, correlation_as_causation

## Reasoning Integrity Audit

### Claude Haiku
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 8

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
  - `(mechanism analysis)`: "bias, effect"
- **[MINOR]** `study_forensics_overflagging`: Agent raised extra findings in solid case: none_or_minor, conclusion_exceeds_results, decorative_uncertainty, correlation_as_causation


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
  - (+) `steps[3]`: "4. CLAIM ANALYSIS: The text makes three main claims: (a) ~40 sessions → ~2 months additional progress; (b) even lower at"
    _Most informative reasoning step_
  - Note: 8 reasoning steps
  - Note: Low step utility: 0/8 steps contribute

**Assumption Discipline:** 4.8/6
  - (+) `assumptions[2]`: "The 'two additional months' claim is based on standardized effect sizes or growth metrics"
    _Most substantive assumption_
  - Note: 5/5 substantive assumptions

**Uncertainty Handling:** 3.0/6
  - (+) `uncertainties[1]`: "Whether the 'two additional months' is a standardized effect size (e.g., Cohen's d converted to months) or a direct meas"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.92"
    _Stated confidence level_
  - (-) `uncertainties[0]`: "Whether 'reading progress' was measured via standardized tests, curriculum-based measurement, or teacher report—this aff"
    _Listed but never addressed in reasoning_
  - (-) `uncertainties[2]`: "Whether attrition rates and reasons for dropout are reported—the text does not mention this, but it is standard RCT repo"
    _Listed but never addressed in reasoning_
  - Note: 4 uncertainties (4 substantive)
  - Note: 3 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 6.0/6
  - (+) `alternative_hypotheses[0]`: "Could classify as mechanism_vs_evidence if the study measured only proximal reading metrics (e.g., fluency) rather than "
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 2/2 include rejection reasoning

**Self Monitoring Quality:** 7.2/8
  - (+) `self_check[0]`: "Did I assume the RCT was well-conducted? Yes, but the text provides no red flags (e.g., no mention of failed randomizati"
    _Most substantive self-verification step_
  - Note: 6 self-check items
  - Note: Self-check quality: 1 deep, 5 arithmetic, 0 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 8.5/10
  - Note: Signal density: 0.70, 653 words

**Insight Depth:** 8.0/8
  - (+) `(output text)`: "bridge check: the bridge from rct evidence to the conclusion (v"
    _Insight 'RCT' matched (exact)_
  - (+) `(output text)`: "ty: the text uses appropriate cautious language ('roughly,' 'around,' 'modest"
    _Insight 'cautious language' matched (exact)_
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
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Named concept(s) ['bias', 'effect'] but mechanism not described
  - _Impacts: mechanism_quality, insight_depth_
- **Unsupported Intermediate Step** `[MEDIUM CONFIDENCE]`: No reasoning step is load-bearing — final answer lacks traceable derivation
  - `final_answer`: "solid"
  - _Impacts: support_strength, structural_reasoning_
- **Missed Key Insight** `[MEDIUM CONFIDENCE]`: Missed expected finding: evidence_matches_claim
  - `(task expectation)`: "Expected: evidence_matches_claim"
  - _Impacts: insight_depth_

**STYLISTIC:**
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether 'reading progress' was measured via standardized tes...' is listed but not addressed
  - `uncertainties[0]`: "Whether 'reading progress' was measured via standardized tests, curriculum-based measurement, or tea"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether attrition rates and reasons for dropout are reported...' is listed but not addressed
  - `uncertainties[2]`: "Whether attrition rates and reasons for dropout are reported—the text does not mention this, but it "
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'The size of the RCT (sample N) is not stated, which affects ...' is listed but not addressed
  - `uncertainties[3]`: "The size of the RCT (sample N) is not stated, which affects precision of the estimate, but the text "
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/11 content words)
  - `key_claims[0]`: "This is a well-designed RCT with human participants and a real educational outcome, placing it at th"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/14 content words)
  - `key_claims[1]`: "The conclusions (virtual tutoring improves reading, dose-response relationship, cost-effectiveness) "
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/5 content words)
  - `key_claims[2]`: "No causal overclaiming, no mechanism-without-evidence, no correlation-causation confusion."
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/10 content words)
  - `key_claims[3]`: "The text appropriately emphasizes the importance of consistent participation, suggesting nuanced und"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 1 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[0]`: "Whether 'reading progress' was measured via standardized tests, curriculum-based measurement, or tea"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 4 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[3]`: "The size of the RCT (sample N) is not stated, which affects precision of the estimate, but the text "
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "solid"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 14942ms

**Final Answer:** solid

**Confidence:** 0.92

**Assumptions:**
- The RCT was properly randomized and controlled
- Reading progress was measured with a validated instrument
- The 'two additional months' claim is based on standardized effect sizes or growth metrics
- Attrition and compliance were adequately reported
- The rural school district sample is representative enough for the claims made

**Reasoning Steps:**
1. 1. EVIDENCE TIER: This is a randomized controlled trial with human participants (elementary students) measuring a real educational outcome (reading progress). This is clinical_human tier evidence.
2. 2. CONCLUSION TIER: The text implies benefit for struggling readers in rural settings receiving virtual tutoring—a human therapeutic/educational outcome.
3. 3. BRIDGE CHECK: The bridge from RCT evidence to the conclusion (virtual tutoring improves reading) is direct and supported. The study directly tested this intervention in the target population.
4. 4. CLAIM ANALYSIS: The text makes three main claims: (a) ~40 sessions → ~2 months additional progress; (b) even lower attendance shows modest gains; (c) cost-effective vs. high-dose tutoring. All three stay within the evidence tier.
5. 5. HEDGING QUALITY: The text uses appropriate cautious language ('roughly,' 'around,' 'modest gains,' 'emphasized that consistent participation was critical'). These are not decorative—they reflect genuine uncertainty in effect sizes and dose-response.
6. 6. CONFOUNDERS: No obvious confounders are ignored. The RCT design controls for selection bias. The mention of 'consistent participation' as critical suggests the researchers considered compliance as a moderator, not a confounder.
7. 7. COST CLAIM: The cost-effectiveness claim is stated as a finding ('delivered results at lower cost'), not as a causal mechanism. This is appropriate for an RCT that measured outcomes and presumably tracked costs.
8. 8. GENERALIZATION SCOPE: The text does not overclaim generalizability. It specifies 'rural school district' and 'struggling elementary students'—appropriate boundaries.

**Key Claims:**
- This is a well-designed RCT with human participants and a real educational outcome, placing it at the highest evidence tier.
- The conclusions (virtual tutoring improves reading, dose-response relationship, cost-effectiveness) all stay within the evidence tier and are appropriately hedged.
- No causal overclaiming, no mechanism-without-evidence, no correlation-causation confusion.
- The text appropriately emphasizes the importance of consistent participation, suggesting nuanced understanding of the intervention.

**Alternative Hypotheses:**
- Could classify as mechanism_vs_evidence if the study measured only proximal reading metrics (e.g., fluency) rather than comprehensive reading achievement, but the text says 'reading progress' without specifying, so I assume validated outcome measures.
- Could flag the cost-effectiveness claim as unsupported if the study did not formally measure implementation costs, but the text says 'delivered results at lower cost,' implying cost data were collected.

**Uncertainties:**
- Whether 'reading progress' was measured via standardized tests, curriculum-based measurement, or teacher report—this affects confidence in the magnitude of the effect.
- Whether the 'two additional months' is a standardized effect size (e.g., Cohen's d converted to months) or a direct measurement—the text does not specify, but this is a minor reporting gap, not a methodological flaw.
- Whether attrition rates and reasons for dropout are reported—the text does not mention this, but it is standard RCT reporting and likely present in the full paper.
- The size of the RCT (sample N) is not stated, which affects precision of the estimate, but the text does not overclaim certainty, so this is not a major issue.

**Self-Verification:**
- Did I assume the RCT was well-conducted? Yes, but the text provides no red flags (e.g., no mention of failed randomization, high attrition, or measurement issues), so this is a reasonable baseline assumption.
- Did I miss any overclaiming? No. The text does not use promotional language like 'breakthrough,' 'transforms,' or 'confirms effectiveness.' It reports findings in measured terms.
- Did I miss any mechanism-vs-evidence issues? No. The evidence tier (RCT) directly supports the conclusion tier (human educational benefit).
- Did I flag confounders that don't exist? No. The RCT design controls for the main confounders (selection bias, regression to the mean).
- Is the cost-effectiveness claim problematic? No. It is stated as a finding, not a causal mechanism, and is appropriate for an RCT that measured both outcomes and costs.
- Did I over-hedge? No. The text uses appropriate uncertainty language without undermining the findings.

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 4.8/6 `########..`
- Uncertainty Handling: 3.0/6 `####......`
- Alternative Hypothesis Quality: 6.0/6 `##########`
- Self Monitoring Quality: 7.2/8 `#########.`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 8.5/10 `########..`


## Final Verdict

**Solo run: Claude Haiku** scored **73.8/100**.

**Best per dimension:**
- Correctness: Claude Haiku (30.0/30)
- Support Strength: Claude Haiku (0.0/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (4.8/6)
- Uncertainty Handling: Claude Haiku (3.0/6)
- Alternative Hypothesis Quality: Claude Haiku (6.0/6)
- Self Monitoring Quality: Claude Haiku (7.2/8)
- Insight Depth: Claude Haiku (8.0/8)
- Mechanism Quality: Claude Haiku (1.5/10)
- Communication Efficiency: Claude Haiku (8.5/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 14.9s | 73.8/100 | 4.9 |

Failure modes observed: decorative_uncertainty, missed_key_insight, named_not_explained, unsupported_conclusion, unsupported_intermediate_step.
