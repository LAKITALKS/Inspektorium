# Forensic Dossier: Study Forensics: Rapamycin for human longevity — promise vs proof

**Run ID:** `praxis_study-forensics-031_Claude_Opus_be9688`  
**Task:** study-forensics-031 | study_forensics | hard | study_forensics  
**Timestamp:** 2026-04-07T07:57:38.809818+00:00  
**Task Family:** mechanism_vs_evidence  
**Trap Type:** strong_preclinical_weak_human  
**Ambiguity:** medium  

## Executive Summary

**Agents tested:** Claude Opus
**Winner:** Claude Opus — **39.4/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, named_not_explained, unsupported_conclusion, unused_assumption, wrong_answer
**Forensic flags:** 3
**Consistency findings:** 9
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Opus | 0.0/30 | 0.0/8 | 4.8/8 | 4.3/6 | 3.6/6 | 6.0/6 | 1.2/8 | 8.0/8 | 1.5/10 | 10.0/10 | **39.4/100** |

## Study Forensics Audit

### Claude Opus

**Classification:** `solid` [x] (gold: `mechanism_vs_evidence`)
**Finding Recall:** 100%
**Matched Findings:** mechanism_not_demonstrated, decorative_uncertainty
**Extra Findings:** cautious_scope_control, none_or_minor, conclusion_exceeds_results, correlation_as_causation

## Reasoning Integrity Audit

### Claude Opus
**Classification:** Correct and well-supported
**Load-bearing steps:** 0 / 6

## Mechanism Analysis

### Claude Opus
| Aspect | Status |
|--------|--------|
| Concept named | :white_check_mark: effect |
| Mechanism described | :x: (0 sentence(s)) |
| Grounded to case | :x: (0 sentence(s)) |

**Missing:** mechanism not described, mechanism not grounded to case data

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

- **[MAJOR]** `well_reasoned_wrong`: Wrong answer but structured reasoning — may have a subtle logic error
  - `final_answer`: "solid"
- **[MODERATE]** `unsupported_conclusion_claims`: 1/1 conclusion claims lack step support
  - `final_answer`: "solid"
- **[MODERATE]** `ungrounded_mechanism`: Mechanism named/described but not connected to case-specific data
  - `(mechanism analysis)`: "effect"


## Evidence Map

### Claude Opus

**Correctness:** 0.0/30
  - (+) `final_answer`: "solid"
    _Agent's answer for correctness check_
  - Note: No match (got: solid)

**Support Strength:** 0.0/8
  - (-) `final_answer`: "solid"
    _Conclusion not supported by steps_
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 6
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[4]`: "5. Assessed uncertainty language - effectively used throughout (failed to meet primary goal, no clinical evidence yet, c"
    _Most informative reasoning step_
  - Note: 6 reasoning steps
  - Note: Low step utility: 0/6 steps contribute

**Assumption Discipline:** 4.3/6
  - (+) `assumptions[1]`: "The human trial mentioned was appropriately powered for its endpoints"
    _Most substantive assumption_
  - (-) `assumptions[2]`: "The experts quoted are qualified in aging/longevity research"
    _Declared but unused in reasoning_
  - Note: 3/3 substantive assumptions
  - Note: 1 unused assumption(s)

**Uncertainty Handling:** 3.6/6
  - (+) `uncertainties[2]`: "Whether 'enthusiasts' taking it off-label represents a significant population"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.9"
    _Stated confidence level_
  - (-) `uncertainties[2]`: "Whether 'enthusiasts' taking it off-label represents a significant population"
    _Listed but never addressed in reasoning_
  - Note: 3 uncertainties (3 substantive)
  - Note: 1 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 6.0/6
  - (+) `alternative_hypotheses[0]`: "Could be classified as 'mechanism_vs_evidence' if the text implied mouse results translate to humans, but it explicitly "
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 2/2 include rejection reasoning

**Self Monitoring Quality:** 1.2/8
  - (+) `self_check[2]`: "Confirmed that uncertainty is substantive, not decorative"
    _Most substantive self-verification step_
  - (-) `self_check[0]`: "Re-read for any subtle overclaiming - found none"
    _Fluff self-check_
  - Note: 4 self-check items
  - Note: Self-check quality: 0 deep, 1 arithmetic, 3 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.75, 240 words

**Insight Depth:** 8.0/8
  - Note: Key insights: 2 full / 2


## Failure Analysis

### Claude Opus

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
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Names the phenomenon but does not explain the causal mechanism
  - `final_answer`: "solid"
  - _Impacts: mechanism_quality_
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Named concept(s) ['effect'] but mechanism not described
  - _Impacts: mechanism_quality, insight_depth_

**STYLISTIC:**
- **Unused Assumption** `[HEURISTIC]`: Assumption 'The experts quoted are qualified in aging/longevity research...' is declared but not referenced in reasoning
  - `assumptions[2]`: "The experts quoted are qualified in aging/longevity research"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether 'enthusiasts' taking it off-label represents a signi...' is listed but not addressed
  - `uncertainties[2]`: "Whether 'enthusiasts' taking it off-label represents a significant population"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Opus

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/7 content words)
  - `key_claims[0]`: "Text maintains clear epistemic boundaries between species"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/8 content words)
  - `key_claims[1]`: "Acknowledges replication in mice while emphasizing absence of human aging evidence"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/6 content words)
  - `key_claims[2]`: "Presents both enthusiasm and expert caution appropriately"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/7 content words)
  - `key_claims[3]`: "Does not conflate surrogate endpoints (fat, muscle) with aging"
- **[WARN]** `[HEURISTIC]` `claim_step_alignment`: Key claim 3 not well supported in reasoning steps (0/6 content words found)
  - `key_claims[2]`: "Presents both enthusiasm and expert caution appropriately"
- **[WARN]** `[HEURISTIC]` `claim_step_alignment`: Key claim 4 not well supported in reasoning steps (1/7 content words found)
  - `key_claims[3]`: "Does not conflate surrogate endpoints (fat, muscle) with aging"
- **[WARN]** `[HEURISTIC]` `unused_assumption`: Assumption 3 appears unused in reasoning or answer
  - `assumptions[2]`: "The experts quoted are qualified in aging/longevity research"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 3 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[2]`: "Whether 'enthusiasts' taking it off-label represents a significant population"
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "solid"


## Agent Profiles

### Claude Opus (claude-opus-4-20250514)
**Parse OK:** True | **Latency:** 16263ms

**Final Answer:** solid

**Confidence:** 0.9

**Assumptions:**
- The text accurately represents the state of rapamycin research
- The human trial mentioned was appropriately powered for its endpoints
- The experts quoted are qualified in aging/longevity research

**Reasoning Steps:**
1. 1. Examined claims about mouse studies - presented as reliable with replication across labs
2. 2. Checked for overclaiming - text explicitly states human evidence is lacking
3. 3. Analyzed mechanism vs evidence - clear distinction made between mouse and human data
4. 4. Evaluated causation claims - mouse lifespan extension is presented as established, human effects as unknown
5. 5. Assessed uncertainty language - effectively used throughout (failed to meet primary goal, no clinical evidence yet, carries risks)
6. 6. Looked for ignored confounders - text acknowledges complexity with cancer risk mention

**Key Claims:**
- Text maintains clear epistemic boundaries between species
- Acknowledges replication in mice while emphasizing absence of human aging evidence
- Presents both enthusiasm and expert caution appropriately
- Does not conflate surrogate endpoints (fat, muscle) with aging

**Alternative Hypotheses:**
- Could be classified as 'mechanism_vs_evidence' if the text implied mouse results translate to humans, but it explicitly avoids this
- Could be 'overclaim' if it promoted off-label use, but it presents risks and lack of evidence

**Uncertainties:**
- Details of the human trial design and power
- Specific mechanisms of lifespan extension in mice
- Whether 'enthusiasts' taking it off-label represents a significant population

**Self-Verification:**
- Re-read for any subtle overclaiming - found none
- Verified that mouse-to-human translation is not assumed
- Confirmed that uncertainty is substantive, not decorative
- Checked if correlation/causation is confused - it is not

**Dimension Scores:**
- Correctness: 0.0/30 `..........`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 4.3/6 `#######...`
- Uncertainty Handling: 3.6/6 `######....`
- Alternative Hypothesis Quality: 6.0/6 `##########`
- Self Monitoring Quality: 1.2/8 `#.........`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Opus** scored **39.4/100**.

**Best per dimension:**
- Correctness: Claude Opus (0.0/30)
- Support Strength: Claude Opus (0.0/8)
- Structural Reasoning: Claude Opus (4.8/8)
- Assumption Discipline: Claude Opus (4.3/6)
- Uncertainty Handling: Claude Opus (3.6/6)
- Alternative Hypothesis Quality: Claude Opus (6.0/6)
- Self Monitoring Quality: Claude Opus (1.2/8)
- Insight Depth: Claude Opus (8.0/8)
- Mechanism Quality: Claude Opus (1.5/10)
- Communication Efficiency: Claude Opus (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Opus | 16.3s | 39.4/100 | 2.4 |

Failure modes observed: decorative_uncertainty, named_not_explained, unsupported_conclusion, unused_assumption, wrong_answer.
