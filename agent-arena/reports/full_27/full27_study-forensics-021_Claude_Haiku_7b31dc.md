# Forensic Dossier: Study Forensics: Virtual tutoring boosts reading skills

**Run ID:** `full27_study-forensics-021_Claude_Haiku_7b31dc`  
**Task:** study-forensics-021 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T16:58:51.142859+00:00  
**Task Family:** solid  
**Trap Type:** overflagging_solid_study  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **70.8/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, missed_key_insight, unsupported_conclusion, unsupported_intermediate_step, unused_assumption
**Forensic flags:** 4
**Consistency findings:** 6
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 30.0/30 | 0.0/8 | 4.8/8 | 3.8/6 | 3.3/6 | 6.0/6 | 6.4/8 | 8.0/8 | 0.0/10 | 8.5/10 | **70.8/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `solid` [+] (gold: `solid`)
**Finding Recall:** 50%
**Matched Findings:** cautious_scope_control
**Missed Findings:** evidence_matches_claim
**Extra Findings:** none_or_minor, conclusion_exceeds_results, unsupported_generalization, decorative_uncertainty, correlation_as_causation

## Reasoning Integrity Audit

### Claude Haiku
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 9

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
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 9
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[6]`: "Checked for overclaim: The text does not claim universal efficacy, does not extrapolate beyond the tested population, an"
    _Most informative reasoning step_
  - Note: 9 reasoning steps
  - Note: Low step utility: 0/9 steps contribute

**Assumption Discipline:** 3.8/6
  - (+) `assumptions[2]`: "The 'two additional months' claim refers to standardized effect sizes or grade-level equivalents"
    _Most substantive assumption_
  - (-) `assumptions[2]`: "The 'two additional months' claim refers to standardized effect sizes or grade-level equivalents"
    _Declared but unused in reasoning_
  - (-) `assumptions[4]`: "No major attrition bias or differential dropout between arms"
    _Declared but unused in reasoning_
  - Note: 5/5 substantive assumptions
  - Note: 2 unused assumption(s)

**Uncertainty Handling:** 3.3/6
  - (+) `uncertainties[0]`: "Whether 'two additional months of reading progress' is a clinically meaningful effect size (e.g., Cohen's d, percentile "
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.88"
    _Stated confidence level_
  - (-) `uncertainties[0]`: "Whether 'two additional months of reading progress' is a clinically meaningful effect size (e.g., Cohen's d, percentile "
    _Listed but never addressed in reasoning_
  - (-) `uncertainties[1]`: "Whether the control condition was active (e.g., standard tutoring) or passive (no intervention) — this affects interpret"
    _Listed but never addressed in reasoning_
  - Note: 4 uncertainties (4 substantive)
  - Note: 2 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 6.0/6
  - (+) `alternative_hypotheses[1]`: "Could flag 'correlation_vs_causation' if the RCT design were weak — but RCTs are the gold standard for causal inference "
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 2/2 include rejection reasoning

**Self Monitoring Quality:** 6.4/8
  - (+) `self_check[2]`: "Did I miss any overclaims? No — the text is appropriately scoped to the tested population and does not claim universal e"
    _Most substantive self-verification step_
  - Note: 6 self-check items
  - Note: Self-check quality: 0 deep, 6 arithmetic, 0 fluff

**Mechanism Quality:** 0.0/10
  - Note: Neither names concept nor explains mechanism

**Communication Efficiency:** 8.5/10
  - Note: Signal density: 0.71, 513 words

**Insight Depth:** 8.0/8
  - (+) `(output text)`: "direct human evidence from an rct — the strongest tier for effi"
    _Insight 'RCT' matched (exact)_
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
- **Unused Assumption** `[HEURISTIC]`: Assumption 'The 'two additional months' claim refers to standardized eff...' is declared but not referenced in reasoning
  - `assumptions[2]`: "The 'two additional months' claim refers to standardized effect sizes or grade-level equivalents"
  - _Impacts: assumption_discipline_
- **Unused Assumption** `[HEURISTIC]`: Assumption 'No major attrition bias or differential dropout between arms...' is declared but not referenced in reasoning
  - `assumptions[4]`: "No major attrition bias or differential dropout between arms"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether 'two additional months of reading progress' is a cli...' is listed but not addressed
  - `uncertainties[0]`: "Whether 'two additional months of reading progress' is a clinically meaningful effect size (e.g., Co"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether the control condition was active (e.g., standard tut...' is listed but not addressed
  - `uncertainties[1]`: "Whether the control condition was active (e.g., standard tutoring) or passive (no intervention) — th"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/9 content words)
  - `key_claims[0]`: "An RCT directly tested a virtual tutoring program in a real-world setting (rural schools)"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/9 content words)
  - `key_claims[1]`: "The primary outcome (reading progress) was measured in human participants, not proxies or biomarkers"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/10 content words)
  - `key_claims[2]`: "The conclusion (program improves reading) stays within the evidence tier (RCT results)"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/9 content words)
  - `key_claims[3]`: "Appropriate caveats are included: dose-response relationship, emphasis on participation, cost contex"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 5 has low overlap with final answer (0/5 content words)
  - `key_claims[4]`: "No mechanistic claims or unsupported generalizations are made"
- **[WARN]** `[HEURISTIC]` `unused_assumption`: Assumption 5 appears unused in reasoning or answer
  - `assumptions[4]`: "No major attrition bias or differential dropout between arms"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 11856ms

**Final Answer:** solid

**Confidence:** 0.88

**Assumptions:**
- The RCT was properly randomized and controlled
- Reading progress was measured with validated instruments
- The 'two additional months' claim refers to standardized effect sizes or grade-level equivalents
- The rural school district sample is representative enough for the claims being made
- No major attrition bias or differential dropout between arms

**Reasoning Steps:**
1. Identified study design: randomized controlled trial with treatment and control groups
2. Identified evidence tier: This is direct human evidence from an RCT — the strongest tier for efficacy claims
3. Identified conclusion tier: The text claims therapeutic benefit (reading progress) for struggling elementary students
4. Checked bridge: The evidence (RCT results) directly supports the conclusion (program improves reading outcomes in this population)
5. Assessed hedging: The text appropriately notes that 'consistent participation was critical' — a realistic caveat, not decorative
6. Assessed generalizability: The text specifies 'rural school district' and 'elementary students,' appropriately scoping claims
7. Checked for overclaim: The text does not claim universal efficacy, does not extrapolate beyond the tested population, and acknowledges dose-response (fewer sessions = modest gains)
8. Checked for mechanism vs. evidence: No mechanistic claims are made; the text reports observed outcomes, not proposed biological pathways
9. Assessed cost claim: The cost comparison is presented as a practical finding, not as a causal mechanism

**Key Claims:**
- An RCT directly tested a virtual tutoring program in a real-world setting (rural schools)
- The primary outcome (reading progress) was measured in human participants, not proxies or biomarkers
- The conclusion (program improves reading) stays within the evidence tier (RCT results)
- Appropriate caveats are included: dose-response relationship, emphasis on participation, cost context
- No mechanistic claims or unsupported generalizations are made

**Alternative Hypotheses:**
- Could classify as 'overclaim' if the rural sample is too narrow to generalize — but the text does not claim broad generalizability, so this is not supported
- Could flag 'correlation_vs_causation' if the RCT design were weak — but RCTs are the gold standard for causal inference in human studies, so this does not apply

**Uncertainties:**
- Whether 'two additional months of reading progress' is a clinically meaningful effect size (e.g., Cohen's d, percentile gains) — the text does not specify, but this is a reporting issue, not an epistemic flaw in the study itself
- Whether the control condition was active (e.g., standard tutoring) or passive (no intervention) — this affects interpretation but does not invalidate the finding
- Long-term follow-up: The text does not mention whether gains persisted after the ten-week program ended
- Attrition and compliance: The text mentions 'consistent participation was critical' but does not report dropout rates or intent-to-treat analysis

**Self-Verification:**
- Did I correctly identify this as an RCT? Yes — 'randomized controlled trial' is explicit.
- Did I correctly place it at the clinical_human tier? Yes — direct measurement of reading outcomes in children.
- Did I miss any overclaims? No — the text is appropriately scoped to the tested population and does not claim universal efficacy.
- Did I miss any mechanism-vs-evidence issues? No — the text reports outcomes, not proposed mechanisms.
- Did I flag decorative uncertainty? No — the caveats (participation, cost context) are substantive, not decorative.
- Did I overflag? Possibly — the text is well-written and appropriately cautious. I should not invent problems.

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 3.8/6 `######....`
- Uncertainty Handling: 3.3/6 `#####.....`
- Alternative Hypothesis Quality: 6.0/6 `##########`
- Self Monitoring Quality: 6.4/8 `########..`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 0.0/10 `..........`
- Communication Efficiency: 8.5/10 `########..`


## Final Verdict

**Solo run: Claude Haiku** scored **70.8/100**.

**Best per dimension:**
- Correctness: Claude Haiku (30.0/30)
- Support Strength: Claude Haiku (0.0/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (3.8/6)
- Uncertainty Handling: Claude Haiku (3.3/6)
- Alternative Hypothesis Quality: Claude Haiku (6.0/6)
- Self Monitoring Quality: Claude Haiku (6.4/8)
- Insight Depth: Claude Haiku (8.0/8)
- Mechanism Quality: Claude Haiku (0.0/10)
- Communication Efficiency: Claude Haiku (8.5/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 11.9s | 70.8/100 | 6.0 |

Failure modes observed: decorative_uncertainty, missed_key_insight, unsupported_conclusion, unsupported_intermediate_step, unused_assumption.
