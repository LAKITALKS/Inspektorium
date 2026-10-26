# Forensic Dossier: Study Forensics: NAD+ restoration reverses Alzheimer's in mice

**Run ID:** `full27_study-forensics-028_Claude_Opus_6a8e1f`  
**Task:** study-forensics-028 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T08:19:36.330391+00:00  
**Task Family:** mechanism_vs_evidence  
**Trap Type:** animal_to_human_overreach  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Opus
**Winner:** Claude Opus — **70.9/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, unsupported_conclusion, unsupported_intermediate_step, unused_assumption
**Forensic flags:** 2
**Consistency findings:** 8
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Opus | 30.0/30 | 0.0/8 | 4.8/8 | 3.4/6 | 3.3/6 | 4.5/6 | 2.4/8 | 8.0/8 | 4.5/10 | 10.0/10 | **70.9/100** |

## Study Forensics Audit

### Claude Opus

**Classification:** `mechanism_vs_evidence` [+] (gold: `mechanism_vs_evidence`)
**Finding Recall:** 100%
**Matched Findings:** mechanism_not_demonstrated, conclusion_exceeds_results
**Extra Findings:** cautious_scope_control, none_or_minor, unsupported_generalization

## Reasoning Integrity Audit

### Claude Opus
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 5

## Mechanism Analysis

### Claude Opus
| Aspect | Status |
|--------|--------|
| Concept named | :x: none |
| Mechanism described | :white_check_mark: (2 sentence(s)) |
| Grounded to case | :x: (0 sentence(s)) |

**Missing:** concept not named, mechanism not grounded to case data

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
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 5
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[1]`: "2. Noted that the treatment showed positive results in mice: repaired brain damage and restored memory"
    _Most informative reasoning step_
  - Note: 5 reasoning steps
  - Note: Low step utility: 0/5 steps contribute

**Assumption Discipline:** 3.4/6
  - (+) `assumptions[3]`: "The researchers are proposing human trials based on these results"
    _Most substantive assumption_
  - (-) `assumptions[1]`: "The mice had some form of induced Alzheimer's-like pathology"
    _Declared but unused in reasoning_
  - Note: 4/4 substantive assumptions
  - Note: 1 unused assumption(s)

**Uncertainty Handling:** 3.3/6
  - (+) `uncertainties[2]`: "The specific mouse model used and how well it recapitulates human Alzheimer's"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.85"
    _Stated confidence level_
  - (-) `uncertainties[0]`: "The exact wording of the researchers' statements about human translation"
    _Listed but never addressed in reasoning_
  - (-) `uncertainties[1]`: "Whether any preliminary human data exists that wasn't mentioned"
    _Listed but never addressed in reasoning_
  - Note: 3 uncertainties (3 substantive)
  - Note: 2 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 4.5/6
  - (+) `alternative_hypotheses[1]`: "solid - if the researchers appropriately caveated their claims about translation"
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 2/2 genuinely diverse alternatives

**Self Monitoring Quality:** 2.4/8
  - (+) `self_check[1]`: "The issue is not that mouse studies are invalid, but that human therapeutic claims are made without human data"
    _Most substantive self-verification step_
  - (-) `self_check[0]`: "Did not overflag - there is a clear mechanism-to-evidence gap"
    _Fluff self-check_
  - Note: 4 self-check items
  - Note: Self-check quality: 0 deep, 2 arithmetic, 2 fluff

**Mechanism Quality:** 4.5/10
  - (+) `(mechanism analysis)`: "2. Noted that the treatment showed positive results in mice: repaired brain damage and restored memory"
    _Mechanism description_
  - Note: Describes mechanism but does not name concept
  - Note: Multi-step mechanism (2 sentences)

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.72, 261 words

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

**STYLISTIC:**
- **Unused Assumption** `[HEURISTIC]`: Assumption 'The mice had some form of induced Alzheimer's-like pathology...' is declared but not referenced in reasoning
  - `assumptions[1]`: "The mice had some form of induced Alzheimer's-like pathology"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'The exact wording of the researchers' statements about human...' is listed but not addressed
  - `uncertainties[0]`: "The exact wording of the researchers' statements about human translation"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether any preliminary human data exists that wasn't mentio...' is listed but not addressed
  - `uncertainties[1]`: "Whether any preliminary human data exists that wasn't mentioned"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Opus

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/7 content words)
  - `key_claims[0]`: "NAD+ drops disrupt brain energy in Alzheimer's mice"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/7 content words)
  - `key_claims[1]`: "NAD+ restoration reversed damage and memory loss in mice"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (1/7 content words)
  - `key_claims[2]`: "Researchers suggest this could work in humans without human evidence"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (1/8 content words)
  - `key_claims[3]`: "The text presents mouse mechanism as basis for human therapeutic optimism"
- **[WARN]** `[HEURISTIC]` `unused_assumption`: Assumption 2 appears unused in reasoning or answer
  - `assumptions[1]`: "The mice had some form of induced Alzheimer's-like pathology"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "overclaim - the jump from mouse to human could be seen as exceeding evidence"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 2 is stated without rejection reasoning
  - `alternative_hypotheses[1]`: "solid - if the researchers appropriately caveated their claims about translation"
- **[NOTE]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Causal mechanism described but underlying concept not named
  - `final_answer`: "mechanism_vs_evidence"


## Agent Profiles

### Claude Opus (claude-opus-4-20250514)
**Parse OK:** True | **Latency:** 16129ms

**Final Answer:** mechanism_vs_evidence

**Confidence:** 0.85

**Assumptions:**
- The study was conducted entirely in genetically engineered mice
- The mice had some form of induced Alzheimer's-like pathology
- NAD+ restoration showed benefits in these mouse models
- The researchers are proposing human trials based on these results

**Reasoning Steps:**
1. 1. Identified that the entire study was conducted in genetically engineered mice
2. 2. Noted that the treatment showed positive results in mice: repaired brain damage and restored memory
3. 3. Observed that scientists are extrapolating from mouse results to suggest human therapeutic potential
4. 4. Recognized the leap from 'results in engineered mice' to 'could enable meaningful recovery in human patients'
5. 5. The mechanism (NAD+ restoration) is demonstrated in mice but applied to human therapeutic context without human evidence

**Key Claims:**
- NAD+ drops disrupt brain energy in Alzheimer's mice
- NAD+ restoration reversed damage and memory loss in mice
- Researchers suggest this could work in humans without human evidence
- The text presents mouse mechanism as basis for human therapeutic optimism

**Alternative Hypotheses:**
- overclaim - the jump from mouse to human could be seen as exceeding evidence
- solid - if the researchers appropriately caveated their claims about translation

**Uncertainties:**
- The exact wording of the researchers' statements about human translation
- Whether any preliminary human data exists that wasn't mentioned
- The specific mouse model used and how well it recapitulates human Alzheimer's

**Self-Verification:**
- Did not overflag - there is a clear mechanism-to-evidence gap
- The issue is not that mouse studies are invalid, but that human therapeutic claims are made without human data
- The researchers do call for clinical trials, showing some appropriate caution
- The overall framing still suggests likely human benefit based solely on mouse data

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 3.4/6 `#####.....`
- Uncertainty Handling: 3.3/6 `#####.....`
- Alternative Hypothesis Quality: 4.5/6 `#######...`
- Self Monitoring Quality: 2.4/8 `###.......`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 4.5/10 `####......`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Opus** scored **70.9/100**.

**Best per dimension:**
- Correctness: Claude Opus (30.0/30)
- Support Strength: Claude Opus (0.0/8)
- Structural Reasoning: Claude Opus (4.8/8)
- Assumption Discipline: Claude Opus (3.4/6)
- Uncertainty Handling: Claude Opus (3.3/6)
- Alternative Hypothesis Quality: Claude Opus (4.5/6)
- Self Monitoring Quality: Claude Opus (2.4/8)
- Insight Depth: Claude Opus (8.0/8)
- Mechanism Quality: Claude Opus (4.5/10)
- Communication Efficiency: Claude Opus (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Opus | 16.1s | 70.9/100 | 4.4 |

Failure modes observed: decorative_uncertainty, unsupported_conclusion, unsupported_intermediate_step, unused_assumption.
