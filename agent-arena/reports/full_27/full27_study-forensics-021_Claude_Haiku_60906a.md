# Forensic Dossier: Study Forensics: Virtual tutoring boosts reading skills

**Run ID:** `full27_study-forensics-021_Claude_Haiku_60906a`  
**Task:** study-forensics-021 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T08:14:15.412052+00:00  
**Task Family:** solid  
**Trap Type:** overflagging_solid_study  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **73.3/100** (margin: 0.0)
**Failure modes:** missed_key_insight, named_not_explained, unsupported_conclusion, unsupported_intermediate_step
**Forensic flags:** 5
**Consistency findings:** 10
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 30.0/30 | 0.0/8 | 4.8/8 | 4.2/6 | 3.9/6 | 4.5/6 | 6.4/8 | 8.0/8 | 1.5/10 | 10.0/10 | **73.3/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `solid` [+] (gold: `solid`)
**Finding Recall:** 50%
**Matched Findings:** cautious_scope_control
**Missed Findings:** evidence_matches_claim
**Extra Findings:** none_or_minor, conclusion_exceeds_results, correlation_as_causation

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
- **[MINOR]** `study_forensics_overflagging`: Agent raised extra findings in solid case: none_or_minor, conclusion_exceeds_results, correlation_as_causation


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
  - (+) `steps[4]`: "Assessed uncertainty language: The text notes 'even those attending fewer sessions showed modest gains,' acknowledging d"
    _Most informative reasoning step_
  - Note: 9 reasoning steps
  - Note: Low step utility: 0/9 steps contribute

**Assumption Discipline:** 4.2/6
  - (+) `assumptions[3]`: "The control condition received standard instruction (not an alternative intervention)"
    _Most substantive assumption_
  - Note: 6/6 substantive assumptions
  - Note: Many assumptions (6)

**Uncertainty Handling:** 3.9/6
  - (+) `uncertainties[0]`: "Whether 'two additional months of reading progress' is educationally meaningful (effect size in standard deviations not "
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.82"
    _Stated confidence level_
  - Note: 6 uncertainties (6 substantive)
  - Note: Confidence 0.82

**Alternative Hypothesis Quality:** 4.5/6
  - (+) `alternative_hypotheses[0]`: "The study could be overclaimed if effect sizes are modest and statistical significance was driven by large sample size r"
    _Most substantive alternative hypothesis_
  - Note: 3 alternative hypotheses considered
  - Note: 3/3 genuinely diverse alternatives

**Self Monitoring Quality:** 6.4/8
  - (+) `self_check[5]`: "Is the uncertainty language effective? Yes—the text acknowledges dose-response variation and emphasizes the importance o"
    _Most substantive self-verification step_
  - Note: 6 self-check items
  - Note: Self-check quality: 0 deep, 6 arithmetic, 0 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.71, 491 words

**Insight Depth:** 8.0/8
  - (+) `(output text)`: "identified the study design: rct with treatment (virtual tutor"
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


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/7 content words)
  - `key_claims[0]`: "RCT design appropriately supports causal inference about the program's effect"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/13 content words)
  - `key_claims[1]`: "The text avoids overclaiming by noting dose-response effects ('even those attending fewer sessions s"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/7 content words)
  - `key_claims[2]`: "No mechanism claims are made; the study remains descriptive about outcomes"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/5 content words)
  - `key_claims[3]`: "Cost-effectiveness is framed comparatively, not absolutely, which is appropriate"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 5 has low overlap with final answer (0/6 content words)
  - `key_claims[4]`: "The emphasis on 'consistent participation' is evidence-based and appropriately cautious"
- **[WARN]** `[HEURISTIC]` `claim_step_alignment`: Key claim 5 not well supported in reasoning steps (1/6 content words found)
  - `key_claims[4]`: "The emphasis on 'consistent participation' is evidence-based and appropriately cautious"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "The study could be overclaimed if effect sizes are modest and statistical significance was driven by"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 2 is stated without rejection reasoning
  - `alternative_hypotheses[1]`: "The study could have correlation_vs_causation issues if attrition differed between groups in ways th"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 3 is stated without rejection reasoning
  - `alternative_hypotheses[2]`: "The study could be solid if the RCT design, outcome measures, and reporting are all appropriate"
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "solid"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 10881ms

**Final Answer:** solid

**Confidence:** 0.82

**Assumptions:**
- The study used a proper randomized assignment to treatment and control conditions
- Reading progress was measured with a validated, standardized assessment
- The 'two additional months of reading progress' represents a meaningful effect size
- The control condition received standard instruction (not an alternative intervention)
- Attrition and compliance were tracked and reported appropriately
- The rural school district context is representative enough to warrant the claims made

**Reasoning Steps:**
1. Identified the study design: RCT with treatment (virtual tutoring) and control conditions
2. Examined the primary outcome: reading progress measured in months gained
3. Checked for causal claims: The text attributes gains to the program via the RCT design, which is appropriate
4. Evaluated scope of claims: Results are presented as specific to this program, in this context, with this population
5. Assessed uncertainty language: The text notes 'even those attending fewer sessions showed modest gains,' acknowledging dose-response variation
6. Reviewed for confounders: RCT design controls for most baseline confounders; no obvious unaddressed confounders mentioned
7. Checked mechanism claims: No mechanistic claims are made; the text stays descriptive
8. Evaluated generalizability: Claims are appropriately bounded to the program tested in a rural district
9. Assessed cost-effectiveness claim: Stated as comparative ('lower cost than typical high-dose tutoring'), which is reasonable given the context

**Key Claims:**
- RCT design appropriately supports causal inference about the program's effect
- The text avoids overclaiming by noting dose-response effects ('even those attending fewer sessions showed modest gains')
- No mechanism claims are made; the study remains descriptive about outcomes
- Cost-effectiveness is framed comparatively, not absolutely, which is appropriate
- The emphasis on 'consistent participation' is evidence-based and appropriately cautious

**Alternative Hypotheses:**
- The study could be overclaimed if effect sizes are modest and statistical significance was driven by large sample size rather than practical significance
- The study could have correlation_vs_causation issues if attrition differed between groups in ways that biased results
- The study could be solid if the RCT design, outcome measures, and reporting are all appropriate

**Uncertainties:**
- Whether 'two additional months of reading progress' is educationally meaningful (effect size in standard deviations not provided in the summary)
- Whether the control group received any intervention or just standard instruction
- The actual attrition rate and whether it differed between conditions
- Whether the 'forty tutoring sessions' represents completion or is an average, and how much variation existed
- The specific reading assessment used and whether it is sensitive to the types of gains expected
- Whether the rural context limits generalizability to urban or suburban settings

**Self-Verification:**
- Did I assume problems that aren't stated? No—I found no explicit red flags in the text
- Did I miss any overclaiming? The text is appropriately bounded to the program tested; no wild generalizations detected
- Did I verify the RCT design supports causation? Yes—randomization is the gold standard for causal inference
- Did I check for mechanism vs. evidence issues? No such issues present; no mechanism is claimed
- Did I assess confounders? RCT design controls for baseline confounders; no obvious unaddressed confounders mentioned
- Is the uncertainty language effective? Yes—the text acknowledges dose-response variation and emphasizes the importance of participation

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 4.2/6 `#######...`
- Uncertainty Handling: 3.9/6 `######....`
- Alternative Hypothesis Quality: 4.5/6 `#######...`
- Self Monitoring Quality: 6.4/8 `########..`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Haiku** scored **73.3/100**.

**Best per dimension:**
- Correctness: Claude Haiku (30.0/30)
- Support Strength: Claude Haiku (0.0/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (4.2/6)
- Uncertainty Handling: Claude Haiku (3.9/6)
- Alternative Hypothesis Quality: Claude Haiku (4.5/6)
- Self Monitoring Quality: Claude Haiku (6.4/8)
- Insight Depth: Claude Haiku (8.0/8)
- Mechanism Quality: Claude Haiku (1.5/10)
- Communication Efficiency: Claude Haiku (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 10.9s | 73.3/100 | 6.7 |

Failure modes observed: missed_key_insight, named_not_explained, unsupported_conclusion, unsupported_intermediate_step.
