# Forensic Dossier: Study Forensics: NAD+ restoration reverses Alzheimer's in mice

**Run ID:** `full27_study-forensics-028_Claude_Opus_c4276a`  
**Task:** study-forensics-028 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T18:01:17.507487+00:00  
**Task Family:** mechanism_vs_evidence  
**Trap Type:** animal_to_human_overreach  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Opus
**Winner:** Claude Opus — **63.5/100** (margin: 0.0)
**Failure modes:** decorative_self_check, decorative_uncertainty, unsupported_conclusion, unsupported_intermediate_step, unused_assumption
**Forensic flags:** 3
**Consistency findings:** 9
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Opus | 30.0/30 | 0.0/8 | 4.8/8 | 2.9/6 | 3.3/6 | 4.5/6 | 0.0/8 | 8.0/8 | 0.0/10 | 10.0/10 | **63.5/100** |

## Study Forensics Audit

### Claude Opus

**Classification:** `mechanism_vs_evidence` [+] (gold: `mechanism_vs_evidence`)
**Finding Recall:** 100%
**Matched Findings:** mechanism_not_demonstrated, conclusion_exceeds_results
**Extra Findings:** cautious_scope_control, none_or_minor

## Reasoning Integrity Audit

### Claude Opus
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 6

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
- "mechanism_vs_evidence"


## Forensic Flags

### Claude Opus

- **[MODERATE]** `weak_mechanism`: Correct answer but weak mechanism explanation — answer may not generalize
  - `final_answer`: "mechanism_vs_evidence"
- **[MAJOR]** `unsupported_leap`: Correct answer with weak support chain — final answer may be an unsupported leap
- **[MODERATE]** `unsupported_conclusion_claims`: 1/1 conclusion claims lack step support
  - `final_answer`: "mechanism_vs_evidence"


## Evidence Map

### Claude Opus

**Correctness:** 30.0/30
  - (+) `final_answer`: "mechanism_vs_evidence"
    _Agent's answer for correctness check_
  - Note: Exact match

**Support Strength:** 0.0/8
  - (-) `final_answer`: "mechanism_vs_evidence"
    _Conclusion not supported by steps_
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 6
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[1]`: "Identified conclusion tier: implies human therapeutic potential ('translate to patients')"
    _Most informative reasoning step_
  - Note: 6 reasoning steps
  - Note: Low step utility: 0/6 steps contribute

**Assumption Discipline:** 2.9/6
  - (+) `assumptions[2]`: "Memory performance was measured through standard rodent behavioral tests"
    _Most substantive assumption_
  - (-) `assumptions[1]`: "NAD+ restoration was achieved through some compound"
    _Declared but unused in reasoning_
  - (-) `assumptions[2]`: "Memory performance was measured through standard rodent behavioral tests"
    _Declared but unused in reasoning_
  - Note: 4/4 substantive assumptions
  - Note: 2 unused assumption(s)

**Uncertainty Handling:** 3.3/6
  - (+) `uncertainties[3]`: "Whether any human data exists for NAD+ in neurodegeneration"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.9"
    _Stated confidence level_
  - (-) `uncertainties[0]`: "What specific compound was used for NAD+ restoration"
    _Listed but never addressed in reasoning_
  - (-) `uncertainties[2]`: "What 'normal memory performance' means in mice"
    _Listed but never addressed in reasoning_
  - Note: 4 uncertainties (4 substantive)
  - Note: 2 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 4.5/6
  - (+) `alternative_hypotheses[0]`: "solid - if we accept that calling for trials is appropriate"
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 2/2 genuinely diverse alternatives

**Self Monitoring Quality:** 0.0/8
  - (+) `self_check[1]`: "Verified the text does imply human benefit despite hedging"
    _Most substantive self-verification step_
  - (-) `self_check[0]`: "Confirmed this is animal evidence, not human"
    _Fluff self-check_
  - Note: 4 self-check items
  - Note: Self-check quality: 0 deep, 0 arithmetic, 4 fluff

**Mechanism Quality:** 0.0/10
  - Note: Neither names concept nor explains mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.76, 222 words

**Insight Depth:** 8.0/8
  - Note: Key insights: 2 full / 2


## Failure Analysis

### Claude Opus

**MODERATE:**
- **Unsupported Conclusion** `[MEDIUM CONFIDENCE]`: Final answer lacks load-bearing or supporting step grounding
  - `final_answer`: "mechanism_vs_evidence"
  - _Impacts: support_strength_
- **Unsupported Intermediate Step** `[MEDIUM CONFIDENCE]`: No reasoning step is load-bearing — final answer lacks traceable derivation
  - `final_answer`: "mechanism_vs_evidence"
  - _Impacts: support_strength, structural_reasoning_

**MINOR:**
- **Decorative Self Check** `[HEURISTIC]`: All 4 self-checks appear to be fluff — no substantive verification
  - `self_check[0]`: "Confirmed this is animal evidence, not human"
  - _Impacts: self_monitoring_quality_

**STYLISTIC:**
- **Unused Assumption** `[HEURISTIC]`: Assumption 'NAD+ restoration was achieved through some compound...' is declared but not referenced in reasoning
  - `assumptions[1]`: "NAD+ restoration was achieved through some compound"
  - _Impacts: assumption_discipline_
- **Unused Assumption** `[HEURISTIC]`: Assumption 'Memory performance was measured through standard rodent beha...' is declared but not referenced in reasoning
  - `assumptions[2]`: "Memory performance was measured through standard rodent behavioral tests"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'What specific compound was used for NAD+ restoration...' is listed but not addressed
  - `uncertainties[0]`: "What specific compound was used for NAD+ restoration"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'What 'normal memory performance' means in mice...' is listed but not addressed
  - `uncertainties[2]`: "What 'normal memory performance' means in mice"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Opus

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/7 content words)
  - `key_claims[0]`: "Mouse study results are being bridged to human therapeutic implications"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/9 content words)
  - `key_claims[1]`: "The text acknowledges the gap with 'translate to patients' but still implies therapeutic relevance"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/9 content words)
  - `key_claims[2]`: "The cautious framing ('could move', 'called for trials') does not resolve the tier mismatch"
- **[WARN]** `[HEURISTIC]` `unused_assumption`: Assumption 2 appears unused in reasoning or answer
  - `assumptions[1]`: "NAD+ restoration was achieved through some compound"
- **[WARN]** `[HEURISTIC]` `unused_assumption`: Assumption 3 appears unused in reasoning or answer
  - `assumptions[2]`: "Memory performance was measured through standard rodent behavioral tests"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 1 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[0]`: "What specific compound was used for NAD+ restoration"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 3 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[2]`: "What 'normal memory performance' means in mice"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "solid - if we accept that calling for trials is appropriate"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 2 is stated without rejection reasoning
  - `alternative_hypotheses[1]`: "overclaim - if 'meaningful recovery' is seen as too strong"


## Agent Profiles

### Claude Opus (claude-opus-4-20250514)
**Parse OK:** True | **Latency:** 14843ms

**Final Answer:** mechanism_vs_evidence

**Confidence:** 0.9

**Assumptions:**
- The study used genetically engineered mice as Alzheimer's models
- NAD+ restoration was achieved through some compound
- Memory performance was measured through standard rodent behavioral tests
- The mice had 'advanced Alzheimer's' as defined by the mouse model

**Reasoning Steps:**
1. Identified evidence tier: genetically engineered mice with Alzheimer's model
2. Identified conclusion tier: implies human therapeutic potential ('translate to patients')
3. Detected bridge step: from mouse model to human therapy
4. Evaluated bridge support: only supported by call for future trials, not existing evidence
5. Checked for rhetorical inflation: language is analytical, not promotional
6. Applied priority rule: no active selling, just tier mismatch

**Key Claims:**
- Mouse study results are being bridged to human therapeutic implications
- The text acknowledges the gap with 'translate to patients' but still implies therapeutic relevance
- The cautious framing ('could move', 'called for trials') does not resolve the tier mismatch

**Alternative Hypotheses:**
- solid - if we accept that calling for trials is appropriate
- overclaim - if 'meaningful recovery' is seen as too strong

**Uncertainties:**
- What specific compound was used for NAD+ restoration
- How 'advanced Alzheimer's' was defined in the mouse model
- What 'normal memory performance' means in mice
- Whether any human data exists for NAD+ in neurodegeneration

**Self-Verification:**
- Confirmed this is animal evidence, not human
- Verified the text does imply human benefit despite hedging
- Checked for promotional language - found analytical tone
- Ensured I'm not overflagging - the tier gap is real

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 2.9/6 `####......`
- Uncertainty Handling: 3.3/6 `#####.....`
- Alternative Hypothesis Quality: 4.5/6 `#######...`
- Self Monitoring Quality: 0.0/8 `..........`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 0.0/10 `..........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Opus** scored **63.5/100**.

**Best per dimension:**
- Correctness: Claude Opus (30.0/30)
- Support Strength: Claude Opus (0.0/8)
- Structural Reasoning: Claude Opus (4.8/8)
- Assumption Discipline: Claude Opus (2.9/6)
- Uncertainty Handling: Claude Opus (3.3/6)
- Alternative Hypothesis Quality: Claude Opus (4.5/6)
- Self Monitoring Quality: Claude Opus (0.0/8)
- Insight Depth: Claude Opus (8.0/8)
- Mechanism Quality: Claude Opus (0.0/10)
- Communication Efficiency: Claude Opus (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Opus | 14.8s | 63.5/100 | 4.3 |

Failure modes observed: decorative_self_check, decorative_uncertainty, unsupported_conclusion, unsupported_intermediate_step, unused_assumption.
