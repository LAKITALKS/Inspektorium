# Forensic Dossier: Study Forensics: Rapamycin for human longevity — promise vs proof

**Run ID:** `praxis_study-forensics-031_Claude_Haiku_659cb4`  
**Task:** study-forensics-031 | study_forensics | hard | study_forensics  
**Timestamp:** 2026-04-07T07:57:22.534169+00:00  
**Task Family:** mechanism_vs_evidence  
**Trap Type:** strong_preclinical_weak_human  
**Ambiguity:** medium  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **40.0/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, unsupported_conclusion, unused_assumption, wrong_answer
**Forensic flags:** 3
**Consistency findings:** 5
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 0.0/30 | 0.0/8 | 4.8/8 | 4.3/6 | 3.6/6 | 6.0/6 | 5.6/8 | 8.0/8 | 4.0/10 | 8.5/10 | **40.0/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `solid` [x] (gold: `mechanism_vs_evidence`)
**Finding Recall:** 100%
**Matched Findings:** mechanism_not_demonstrated, decorative_uncertainty
**Extra Findings:** cautious_scope_control, none_or_minor, conclusion_exceeds_results, unsupported_generalization, correlation_as_causation

## Reasoning Integrity Audit

### Claude Haiku
**Classification:** Correct and well-supported
**Load-bearing steps:** 0 / 7

## Mechanism Analysis

### Claude Haiku
| Aspect | Status |
|--------|--------|
| Concept named | :white_check_mark: effect |
| Mechanism described | :white_check_mark: (1 sentence(s)) |
| Grounded to case | :x: (0 sentence(s)) |

**Missing:** mechanism not grounded to case data

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

- **[MAJOR]** `well_reasoned_wrong`: Wrong answer but structured reasoning — may have a subtle logic error
  - `final_answer`: "solid"
- **[MODERATE]** `unsupported_conclusion_claims`: 1/1 conclusion claims lack step support
  - `final_answer`: "solid"
- **[MODERATE]** `ungrounded_mechanism`: Mechanism named/described but not connected to case-specific data
  - `(mechanism analysis)`: "effect"


## Evidence Map

### Claude Haiku

**Correctness:** 0.0/30
  - (+) `final_answer`: "solid"
    _Agent's answer for correctness check_
  - Note: No match (got: solid)

**Support Strength:** 0.0/8
  - (-) `final_answer`: "solid"
    _Conclusion not supported by steps_
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 7
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[4]`: "Checked for decorative uncertainty: The uncertainty language is substantive, not decorative. The text identifies a speci"
    _Most informative reasoning step_
  - Note: 7 reasoning steps
  - Note: Low step utility: 0/7 steps contribute

**Assumption Discipline:** 4.3/6
  - (+) `assumptions[2]`: "The trial's primary endpoint (abdominal fat reduction) and secondary endpoint (lean muscle) are appropriate proxies for "
    _Most substantive assumption_
  - (-) `assumptions[0]`: "The mouse lifespan extension data (10-25%) is accurately reported and represents genuine replication across labs"
    _Declared but unused in reasoning_
  - Note: 5/5 substantive assumptions
  - Note: 1 unused assumption(s)

**Uncertainty Handling:** 3.6/6
  - (+) `uncertainties[0]`: "Whether the human trial's failure to reduce abdominal fat is truly a failure of rapamycin or reflects trial design issue"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.92"
    _Stated confidence level_
  - (-) `uncertainties[1]`: "Whether the 'modest' increase in lean muscle in women is clinically meaningful or just statistically significant — the t"
    _Listed but never addressed in reasoning_
  - Note: 3 uncertainties (3 substantive)
  - Note: 1 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 6.0/6
  - (+) `alternative_hypotheses[0]`: "Could be classified as 'decorative uncertainty' if the expert caution were merely rhetorical window-dressing while the t"
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 2/2 include rejection reasoning

**Self Monitoring Quality:** 5.6/8
  - (+) `self_check[3]`: "Does the text acknowledge the mouse-to-human gap? Yes, explicitly: 'The study did not test whether the drug slows biolog"
    _Most substantive self-verification step_
  - Note: 5 self-check items
  - Note: Self-check quality: 0 deep, 5 arithmetic, 0 fluff

**Mechanism Quality:** 4.0/10
  - (+) `(mechanism analysis)`: "Checked for correlation vs. causation: The text does not claim rapamycin causes aging slowdown in humans. It reports wha"
    _Mechanism description without case grounding_
  - Note: Names concept + describes mechanism (not grounded to case)

**Communication Efficiency:** 8.5/10
  - Note: Signal density: 0.71, 584 words

**Insight Depth:** 8.0/8
  - Note: Key insights: 2 full / 2


## Failure Analysis

### Claude Haiku

**CRITICAL:**
- **Wrong Answer** `[HIGH CONFIDENCE]`: Answer does not match expected 'mechanism_vs_evidence'
  - `final_answer`: "solid"
  - _Impacts: correctness_

**MAJOR:**
- **Wrong Answer** `[HIGH CONFIDENCE]`: Study classification incorrect: expected 'mechanism_vs_evidence', detected 'solid'
  - `final_answer`: "solid"
  - _Impacts: correctness_

**MODERATE:**
- **Unsupported Conclusion** `[MEDIUM CONFIDENCE]`: Final answer lacks load-bearing or supporting step grounding
  - `final_answer`: "solid"
  - _Impacts: support_strength_

**STYLISTIC:**
- **Unused Assumption** `[HEURISTIC]`: Assumption 'The mouse lifespan extension data (10-25%) is accurately rep...' is declared but not referenced in reasoning
  - `assumptions[0]`: "The mouse lifespan extension data (10-25%) is accurately reported and represents genuine replication"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether the 'modest' increase in lean muscle in women is cli...' is listed but not addressed
  - `uncertainties[1]`: "Whether the 'modest' increase in lean muscle in women is clinically meaningful or just statistically"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/13 content words)
  - `key_claims[0]`: "The text correctly distinguishes between animal evidence (reliable lifespan extension) and human evi"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/13 content words)
  - `key_claims[1]`: "The text accurately reports that the human trial's primary endpoint was not met, which is a concrete"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/11 content words)
  - `key_claims[2]`: "The text appropriately cautions against extrapolating from mouse to human without clinical evidence"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/10 content words)
  - `key_claims[3]`: "The text does not claim rapamycin is ineffective in humans; it claims the evidence is insufficient a"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 2 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[1]`: "Whether the 'modest' increase in lean muscle in women is clinically meaningful or just statistically"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 11772ms

**Final Answer:** solid

**Confidence:** 0.92

**Assumptions:**
- The mouse lifespan extension data (10-25%) is accurately reported and represents genuine replication across labs
- The human trial described is indeed 'well-designed' as stated
- The trial's primary endpoint (abdominal fat reduction) and secondary endpoint (lean muscle) are appropriate proxies for aging effects
- The text accurately represents expert consensus on current evidence
- Off-label use of rapamycin does carry the risks mentioned for the populations cited

**Reasoning Steps:**
1. Identified the core claim structure: mouse data → human enthusiasm → human trial results → expert caution
2. Checked for mechanism vs. evidence issues: The text does NOT claim the mouse mechanism (mTOR inhibition) directly translates to humans. It acknowledges the gap by noting the human trial 'did not test whether the drug slows biological aging'
3. Checked for correlation vs. causation: The text does not claim rapamycin causes aging slowdown in humans. It reports what the trial found (or didn't find) and what experts say
4. Checked for overclaim: The text explicitly states 'no clinical evidence yet shows rapamycin slows aging in people' — this is appropriately cautious and contradicts the enthusiasts' behavior
5. Checked for decorative uncertainty: The uncertainty language is substantive, not decorative. The text identifies a specific gap (no test of biological aging in humans) and reports actual trial results (failed primary endpoint, modest secondary effect)
6. Checked for confounders: The text does not make causal claims about why the human trial failed, so confounder analysis is not applicable here
7. Verified the logical structure: Mouse data → human enthusiasm (described as off-label use) → human trial failure → expert warning. This is a coherent narrative that does NOT overclaim

**Key Claims:**
- The text correctly distinguishes between animal evidence (reliable lifespan extension) and human evidence (no aging slowdown demonstrated)
- The text accurately reports that the human trial's primary endpoint was not met, which is a concrete negative result, not a null finding
- The text appropriately cautions against extrapolating from mouse to human without clinical evidence
- The text does not claim rapamycin is ineffective in humans; it claims the evidence is insufficient and risks are real

**Alternative Hypotheses:**
- Could be classified as 'decorative uncertainty' if the expert caution were merely rhetorical window-dressing while the text still implied rapamycin works in humans — but it doesn't; the trial failure is concrete
- Could be classified as 'mechanism_vs_evidence' if the text claimed mouse mTOR effects should work in humans — but it explicitly does not make this claim

**Uncertainties:**
- Whether the human trial's failure to reduce abdominal fat is truly a failure of rapamycin or reflects trial design issues (dose, duration, population selection, etc.) — the text does not address this
- Whether the 'modest' increase in lean muscle in women is clinically meaningful or just statistically significant — the text does not quantify this
- The specific risks of off-label rapamycin use beyond those mentioned (active cancer) — the text says 'especially' but does not enumerate all risks

**Self-Verification:**
- Did I overidentify problems? No. The text is epistemically careful. It does not commit the mechanism-vs-evidence error or overclaim.
- Did I miss a correlation-vs-causation issue? No. The text reports trial results, not correlational associations.
- Is the expert caution substantive or decorative? Substantive — it is grounded in the trial's failure to meet its primary endpoint and the absence of aging biomarker testing.
- Does the text acknowledge the mouse-to-human gap? Yes, explicitly: 'The study did not test whether the drug slows biological aging' and 'no clinical evidence yet shows rapamycin slows aging in people.'
- Are there unsupported generalizations? No. The text is careful to distinguish mouse data, human enthusiasm, trial results, and expert opinion.

**Dimension Scores:**
- Correctness: 0.0/30 `..........`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 4.3/6 `#######...`
- Uncertainty Handling: 3.6/6 `######....`
- Alternative Hypothesis Quality: 6.0/6 `##########`
- Self Monitoring Quality: 5.6/8 `#######...`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 4.0/10 `####......`
- Communication Efficiency: 8.5/10 `########..`


## Final Verdict

**Solo run: Claude Haiku** scored **40.0/100**.

**Best per dimension:**
- Correctness: Claude Haiku (0.0/30)
- Support Strength: Claude Haiku (0.0/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (4.3/6)
- Uncertainty Handling: Claude Haiku (3.6/6)
- Alternative Hypothesis Quality: Claude Haiku (6.0/6)
- Self Monitoring Quality: Claude Haiku (5.6/8)
- Insight Depth: Claude Haiku (8.0/8)
- Mechanism Quality: Claude Haiku (4.0/10)
- Communication Efficiency: Claude Haiku (8.5/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 11.8s | 40.0/100 | 3.4 |

Failure modes observed: decorative_uncertainty, unsupported_conclusion, unused_assumption, wrong_answer.
