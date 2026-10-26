# Forensic Dossier: Study Forensics: Social media use and well-being

**Run ID:** `full27_study-forensics-001_Claude_Haiku_64d177`  
**Task:** study-forensics-001 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T17:51:32.683394+00:00  
**Task Family:** solid  
**Trap Type:** overflagging_solid_study  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **70.9/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, missed_key_insight, named_not_explained, unsupported_conclusion, unsupported_intermediate_step, unused_assumption
**Forensic flags:** 5
**Consistency findings:** 8
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 30.0/30 | 0.0/8 | 4.8/8 | 3.2/6 | 3.3/6 | 6.0/6 | 5.6/8 | 8.0/8 | 1.5/10 | 8.5/10 | **70.9/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `solid` [+] (gold: `solid`)
**Finding Recall:** 67%
**Matched Findings:** cautious_scope_control, none_or_minor
**Missed Findings:** evidence_matches_claim
**Extra Findings:** conclusion_exceeds_results, unsupported_generalization, decorative_uncertainty, correlation_as_causation

## Reasoning Integrity Audit

### Claude Haiku
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 8

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
- **[MINOR]** `study_forensics_overflagging`: Agent raised extra findings in solid case: conclusion_exceeds_results, unsupported_generalization, decorative_uncertainty, correlation_as_causation


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
  - (+) `steps[4]`: "Assessed hedging: The authors explicitly acknowledge scope limitations (college students only, three platforms only, gen"
    _Most informative reasoning step_
  - Note: 8 reasoning steps
  - Note: Low step utility: 0/8 steps contribute

**Assumption Discipline:** 3.2/6
  - (+) `assumptions[2]`: "The three-week timeframe is sufficient to detect meaningful changes in these outcomes"
    _Most substantive assumption_
  - (-) `assumptions[2]`: "The three-week timeframe is sufficient to detect meaningful changes in these outcomes"
    _Declared but unused in reasoning_
  - (-) `assumptions[4]`: "Participants complied with the intervention assignment"
    _Declared but unused in reasoning_
  - Note: 6/6 substantive assumptions
  - Note: Many assumptions (6)

**Uncertainty Handling:** 3.3/6
  - (+) `uncertainties[0]`: "Whether the measured changes in depression/loneliness meet thresholds for clinical significance (not stated in summary)"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.92"
    _Stated confidence level_
  - (-) `uncertainties[1]`: "Whether baseline depression/loneliness severity was balanced between groups (not stated)"
    _Listed but never addressed in reasoning_
  - (-) `uncertainties[4]`: "Long-term durability of effects beyond three weeks"
    _Listed but never addressed in reasoning_
  - Note: 5 uncertainties (5 substantive)
  - Note: 2 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 6.0/6
  - (+) `alternative_hypotheses[0]`: "Could classify as 'limited_human' if the three-week duration is considered too short to establish clinical significance "
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 2/2 include rejection reasoning

**Self Monitoring Quality:** 5.6/8
  - (+) `self_check[1]`: "Did I assume problems not stated in the summary? I checked for confounders, attrition, and measurement validity, but the"
    _Most substantive self-verification step_
  - Note: 5 self-check items
  - Note: Self-check quality: 0 deep, 5 arithmetic, 0 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 8.5/10
  - Note: Signal density: 0.72, 514 words

**Insight Depth:** 8.0/8
  - (+) `(output text)`: "uthors explicitly acknowledge scope limitations (college students only, thre"
    _Insight 'scope limitation' matched (exact)_
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
- **Unused Assumption** `[HEURISTIC]`: Assumption 'The three-week timeframe is sufficient to detect meaningful ...' is declared but not referenced in reasoning
  - `assumptions[2]`: "The three-week timeframe is sufficient to detect meaningful changes in these outcomes"
  - _Impacts: assumption_discipline_
- **Unused Assumption** `[HEURISTIC]`: Assumption 'Participants complied with the intervention assignment...' is declared but not referenced in reasoning
  - `assumptions[4]`: "Participants complied with the intervention assignment"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether baseline depression/loneliness severity was balanced...' is listed but not addressed
  - `uncertainties[1]`: "Whether baseline depression/loneliness severity was balanced between groups (not stated)"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Long-term durability of effects beyond three weeks...' is listed but not addressed
  - `uncertainties[4]`: "Long-term durability of effects beyond three weeks"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/7 content words)
  - `key_claims[0]`: "This is a well-designed RCT with appropriate scope limitations acknowledged by the authors."
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/9 content words)
  - `key_claims[1]`: "The evidence tier (clinical_human) matches the conclusion tier (human_therapeutic benefit in college"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/5 content words)
  - `key_claims[2]`: "The causal claim is justified by the randomized design."
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/9 content words)
  - `key_claims[3]`: "The authors appropriately hedge generalization to other populations and platforms — this is epistemi"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 5 has low overlap with final answer (0/3 content words)
  - `key_claims[4]`: "No overclaim or mechanism-vs-evidence gap is present."
- **[WARN]** `[HEURISTIC]` `unused_assumption`: Assumption 5 appears unused in reasoning or answer
  - `assumptions[4]`: "Participants complied with the intervention assignment"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 2 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[1]`: "Whether baseline depression/loneliness severity was balanced between groups (not stated)"
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "solid"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 11842ms

**Final Answer:** solid

**Confidence:** 0.92

**Assumptions:**
- The randomization was properly executed and groups were balanced at baseline
- Depression and loneliness were measured with validated instruments
- The three-week timeframe is sufficient to detect meaningful changes in these outcomes
- Phone screenshots provided reliable objective usage data
- Participants complied with the intervention assignment
- No significant attrition or differential dropout between groups

**Reasoning Steps:**
1. Identified evidence tier: This is a randomized controlled trial in humans with objective usage measurement and validated psychological outcomes — clinical_human tier.
2. Identified conclusion tier: The text implies benefit for college students' mental health (depression, loneliness) — human_therapeutic.
3. Checked bridge: The study directly measured the outcome (depression/loneliness) in the target population (college students) via RCT design. The bridge is direct and supported.
4. Evaluated causal claims: The text reports 'students who restricted...reported significant declines' — appropriate causal language for an RCT.
5. Assessed hedging: The authors explicitly acknowledge scope limitations (college students only, three platforms only, generalization uncertain). This is appropriate epistemic humility, not decorative uncertainty.
6. Checked for overclaim: No promotional language ('breakthrough,' 'transforms,' 'confirms effectiveness'). Claims are modest and proportional to the evidence.
7. Checked for mechanism vs. evidence: No gap. The evidence tier matches the conclusion tier. The study measured human outcomes directly.
8. Verified confounders: RCT design controls for most confounders through randomization. No obvious unaddressed confounders mentioned in the summary.

**Key Claims:**
- This is a well-designed RCT with appropriate scope limitations acknowledged by the authors.
- The evidence tier (clinical_human) matches the conclusion tier (human_therapeutic benefit in college students).
- The causal claim is justified by the randomized design.
- The authors appropriately hedge generalization to other populations and platforms — this is epistemic integrity, not evasion.
- No overclaim or mechanism-vs-evidence gap is present.

**Alternative Hypotheses:**
- Could classify as 'limited_human' if the three-week duration is considered too short to establish clinical significance — but RCTs with validated outcome measures at any duration are typically clinical_human tier.
- Could flag as overclaim if 'significant' refers only to statistical significance without clinical meaningfulness — but the text does not specify, and the summary does not make inflated claims about magnitude.

**Uncertainties:**
- Whether the measured changes in depression/loneliness meet thresholds for clinical significance (not stated in summary)
- Whether baseline depression/loneliness severity was balanced between groups (not stated)
- Effect size and confidence intervals (not provided in summary)
- Whether the control group's usage remained stable or drifted (compliance data not mentioned)
- Long-term durability of effects beyond three weeks

**Self-Verification:**
- Did I mistake appropriate hedging for decorative uncertainty? No — the authors are explicitly limiting their claims to the studied population and platforms, which is correct.
- Did I assume problems not stated in the summary? I checked for confounders, attrition, and measurement validity, but the summary does not report these details. I noted them as uncertainties rather than flagging them as problems.
- Is the RCT design sufficient for clinical_human tier? Yes — randomized assignment with objective and subjective outcome measures in humans is the gold standard.
- Did I miss any causal language that overstates the evidence? No — 'reported significant declines' is appropriate for an RCT.
- Is the scope limitation language sufficient? Yes — the authors explicitly note college-only, three-platform-only, and generalization uncertainty. This is good practice.

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 3.2/6 `#####.....`
- Uncertainty Handling: 3.3/6 `#####.....`
- Alternative Hypothesis Quality: 6.0/6 `##########`
- Self Monitoring Quality: 5.6/8 `#######...`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 8.5/10 `########..`


## Final Verdict

**Solo run: Claude Haiku** scored **70.9/100**.

**Best per dimension:**
- Correctness: Claude Haiku (30.0/30)
- Support Strength: Claude Haiku (0.0/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (3.2/6)
- Uncertainty Handling: Claude Haiku (3.3/6)
- Alternative Hypothesis Quality: Claude Haiku (6.0/6)
- Self Monitoring Quality: Claude Haiku (5.6/8)
- Insight Depth: Claude Haiku (8.0/8)
- Mechanism Quality: Claude Haiku (1.5/10)
- Communication Efficiency: Claude Haiku (8.5/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 11.8s | 70.9/100 | 6.0 |

Failure modes observed: decorative_uncertainty, missed_key_insight, named_not_explained, unsupported_conclusion, unsupported_intermediate_step, unused_assumption.
