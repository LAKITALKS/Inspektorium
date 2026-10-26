# Forensic Dossier: Study Forensics: Virtual tutoring boosts reading skills

**Run ID:** `val_study-forensics-021_claude_haiku_5f5f77`  
**Task:** study-forensics-021 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-06T14:28:49.759790+00:00  
**Task Family:** solid  
**Trap Type:** overflagging_solid_study  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **40.0/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, missed_key_insight, named_not_explained, overclaiming, unsupported_conclusion, unsupported_intermediate_step, wrong_answer
**Forensic flags:** 5
**Consistency findings:** 6
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 0.0/30 | 0.0/8 | 4.8/8 | 4.2/6 | 3.6/6 | 6.0/6 | 6.4/8 | 5.6/8 | 1.5/10 | 10.0/10 | **40.0/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `overclaim` [x] (gold: `solid`)
**Finding Recall:** 50%
**Matched Findings:** cautious_scope_control
**Missed Findings:** evidence_matches_claim
**Extra Findings:** none_or_minor, conclusion_exceeds_results, unsupported_generalization, decorative_uncertainty, correlation_as_causation
**False Positives:** overclaim, unsupported generalization

## Reasoning Integrity Audit

### Claude Haiku
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 10

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
- **[MINOR]** `study_forensics_overflagging`: Agent raised extra findings in solid case: none_or_minor, conclusion_exceeds_results, unsupported_generalization, decorative_uncertainty, correlation_as_causation


## Evidence Map

### Claude Haiku

**Correctness:** 30.0/30
  - (+) `final_answer`: "solid"
    _Agent's answer for correctness check_
  - Note: Exact match

**Support Strength:** 0.0/8
  - (-) `final_answer`: "solid"
    _Conclusion not supported by steps_
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 10
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[8]`: "Reviewed cost-effectiveness claim: Stated as comparative fact ('lower cost than typical high-dose tutoring'), not as a c"
    _Most informative reasoning step_
  - Note: 10 reasoning steps
  - Note: Low step utility: 0/10 steps contribute

**Assumption Discipline:** 4.2/6
  - (+) `assumptions[3]`: "The 'two additional months' figure is based on standardized effect sizes or growth metrics"
    _Most substantive assumption_
  - Note: 6/6 substantive assumptions
  - Note: Many assumptions (6)

**Uncertainty Handling:** 3.6/6
  - (+) `uncertainties[0]`: "Whether the control group received any intervention (standard instruction vs. no tutoring) — this affects interpretation"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.88"
    _Stated confidence level_
  - (-) `uncertainties[3]`: "The definition of 'consistent participation' and whether it was pre-specified"
    _Listed but never addressed in reasoning_
  - Note: 5 uncertainties (5 substantive)
  - Note: 1 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 6.0/6
  - (+) `alternative_hypotheses[0]`: "Overclaim: Could argue that 'two additional months' is presented without confidence intervals or effect size context, bu"
    _Most substantive alternative hypothesis_
  - Note: 3 alternative hypotheses considered
  - Note: 3/3 include rejection reasoning

**Self Monitoring Quality:** 6.4/8
  - (+) `self_check[3]`: "Are there hidden confounders? Randomization controls for measured and unmeasured confounders at baseline; post-hoc confo"
    _Most substantive self-verification step_
  - Note: 5 self-check items
  - Note: Self-check quality: 1 deep, 4 arithmetic, 0 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.76, 480 words

**Insight Depth:** 8.0/8
  - (+) `(output text)`: "olid identified study design: rct with treatment and control gr"
    _Insight 'RCT' matched (exact)_
  - Note: Key insights: 2 full / 2


## Failure Analysis

### Claude Haiku

**MAJOR:**
- **Wrong Answer** `[HIGH CONFIDENCE]`: Study classification incorrect: expected 'solid', detected 'overclaim'
  - `final_answer`: "solid"
  - _Impacts: correctness_
- **Overclaiming** `[HEURISTIC]`: False positive: agent flagged 'overclaim' in a solid case
  - `final_answer`: "solid"
  - _Impacts: correctness_
- **Overclaiming** `[HEURISTIC]`: False positive: agent flagged 'unsupported generalization' in a solid case
  - `final_answer`: "solid"
  - _Impacts: correctness_

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
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'The definition of 'consistent participation' and whether it ...' is listed but not addressed
  - `uncertainties[3]`: "The definition of 'consistent participation' and whether it was pre-specified"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/9 content words)
  - `key_claims[0]`: "RCT design supports causal inference: virtual tutoring caused reading gains"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/10 content words)
  - `key_claims[1]`: "Effect is dose-dependent: more sessions → larger gains, fewer sessions → modest gains (internally co"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/8 content words)
  - `key_claims[2]`: "Claim is appropriately modest: 'two additional months' is not presented as a cure-all"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/3 content words)
  - `key_claims[3]`: "No mechanism is invoked inappropriately"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 5 has low overlap with final answer (0/5 content words)
  - `key_claims[4]`: "Cost-effectiveness is mentioned but not overstated as a causal finding"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 4 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[3]`: "The definition of 'consistent participation' and whether it was pre-specified"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 11107ms

**Final Answer:** solid

**Confidence:** 0.88

**Assumptions:**
- The study is genuinely randomized (no information contradicts this)
- Reading progress was measured with a validated instrument
- The control condition received no tutoring or standard instruction
- The 'two additional months' figure is based on standardized effect sizes or growth metrics
- The sample size was adequate (not stated, but RCT design suggests reasonable rigor)
- Attrition and compliance were tracked appropriately

**Reasoning Steps:**
1. Identified study design: RCT with treatment and control groups — this is the gold standard for causal inference
2. Examined the main claim: ~40 sessions → ~2 months additional reading progress vs. control
3. Assessed causality: RCT design supports causal inference; randomization controls for confounders
4. Checked for overclaim: The claim is modest and specific (two months, not transformative); acknowledges dose-response (fewer sessions = modest gains)
5. Evaluated mechanism claims: None presented; no mechanism is invoked inappropriately
6. Examined correlation vs. causation: Not an issue; RCT design justifies causal language
7. Checked for decorative uncertainty: The text does NOT say 'more research needed' while making strong claims; it presents findings straightforwardly
8. Assessed confounders: Randomization addresses selection bias; no obvious uncontrolled confounders mentioned
9. Reviewed cost-effectiveness claim: Stated as comparative fact ('lower cost than typical high-dose tutoring'), not as a causal finding; reasonable contextual claim
10. Checked for unsupported generalizations: Claims are limited to the tested population (rural elementary students, struggling readers); no overgeneralization to other groups

**Key Claims:**
- RCT design supports causal inference: virtual tutoring caused reading gains
- Effect is dose-dependent: more sessions → larger gains, fewer sessions → modest gains (internally consistent)
- Claim is appropriately modest: 'two additional months' is not presented as a cure-all
- No mechanism is invoked inappropriately
- Cost-effectiveness is mentioned but not overstated as a causal finding

**Alternative Hypotheses:**
- Overclaim: Could argue that 'two additional months' is presented without confidence intervals or effect size context, but the text is actually quite measured
- Confounders: Could argue that motivation or parental involvement differ between groups, but RCT design mitigates this
- Mechanism vs. evidence: Not applicable; no mechanism is claimed

**Uncertainties:**
- Whether the control group received any intervention (standard instruction vs. no tutoring) — this affects interpretation but doesn't invalidate the finding
- The actual effect size (Cohen's d or similar) — 'two months' is interpretable but context-dependent
- Whether attrition differed between groups and how it was handled
- The definition of 'consistent participation' and whether it was pre-specified
- Whether the cost comparison is based on actual data or assumption

**Self-Verification:**
- Did I flag problems that don't exist? No. The study is well-designed and the text is appropriately cautious.
- Did I miss red flags? No obvious ones. The dose-response relationship actually strengthens confidence in causality.
- Is the RCT design sufficient to justify causal claims? Yes, assuming proper randomization and no major attrition bias.
- Are there hidden confounders? Randomization controls for measured and unmeasured confounders at baseline; post-hoc confounders (e.g., differential motivation) are possible but not evident from the text.
- Is the cost claim problematic? No; it's presented as comparative context, not as a causal mechanism.

**Dimension Scores:**
- Correctness: 0.0/30 `..........`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 4.2/6 `#######...`
- Uncertainty Handling: 3.6/6 `######....`
- Alternative Hypothesis Quality: 6.0/6 `##########`
- Self Monitoring Quality: 6.4/8 `########..`
- Insight Depth: 5.6/8 `#######...`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Haiku** scored **40.0/100**.

**Best per dimension:**
- Correctness: Claude Haiku (0.0/30)
- Support Strength: Claude Haiku (0.0/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (4.2/6)
- Uncertainty Handling: Claude Haiku (3.6/6)
- Alternative Hypothesis Quality: Claude Haiku (6.0/6)
- Self Monitoring Quality: Claude Haiku (6.4/8)
- Insight Depth: Claude Haiku (5.6/8)
- Mechanism Quality: Claude Haiku (1.5/10)
- Communication Efficiency: Claude Haiku (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 11.1s | 40.0/100 | 3.6 |

Failure modes observed: decorative_uncertainty, missed_key_insight, named_not_explained, overclaiming, unsupported_conclusion, unsupported_intermediate_step, wrong_answer.
