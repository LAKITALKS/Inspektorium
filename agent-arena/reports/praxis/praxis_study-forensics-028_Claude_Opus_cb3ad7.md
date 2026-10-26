# Forensic Dossier: Study Forensics: NAD+ restoration reverses Alzheimer's in mice

**Run ID:** `praxis_study-forensics-028_Claude_Opus_cb3ad7`  
**Task:** study-forensics-028 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-07T07:55:37.262403+00:00  
**Task Family:** mechanism_vs_evidence  
**Trap Type:** animal_to_human_overreach  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Opus
**Winner:** Claude Opus — **70.6/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, unsupported_conclusion, unsupported_intermediate_step, unused_assumption
**Forensic flags:** 2
**Consistency findings:** 8
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Opus | 30.0/30 | 0.0/8 | 4.8/8 | 3.4/6 | 3.3/6 | 4.5/6 | 3.6/8 | 8.0/8 | 3.0/10 | 10.0/10 | **70.6/100** |

## Study Forensics Audit

### Claude Opus

**Classification:** `mechanism_vs_evidence` [+] (gold: `mechanism_vs_evidence`)
**Finding Recall:** 100%
**Matched Findings:** mechanism_not_demonstrated, conclusion_exceeds_results
**Extra Findings:** none_or_minor, unsupported_generalization

## Reasoning Integrity Audit

### Claude Opus
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 5

## Mechanism Analysis

### Claude Opus
| Aspect | Status |
|--------|--------|
| Concept named | :x: none |
| Mechanism described | :white_check_mark: (1 sentence(s)) |
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
  - (+) `uncertainties[2]`: "The specific language used by the researchers vs. the summary author"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.9"
    _Stated confidence level_
  - (-) `uncertainties[0]`: "The exact nature of the Alzheimer's model in the mice"
    _Listed but never addressed in reasoning_
  - (-) `uncertainties[1]`: "Whether any preliminary human data exists that wasn't mentioned"
    _Listed but never addressed in reasoning_
  - Note: 3 uncertainties (3 substantive)
  - Note: 2 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 4.5/6
  - (+) `alternative_hypotheses[1]`: "overclaim - there is an element of overclaiming in suggesting human therapeutic potential"
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 2/2 genuinely diverse alternatives

**Self Monitoring Quality:** 3.6/8
  - (+) `self_check[0]`: "Confirmed this is mechanism vs. evidence rather than overclaim because a mechanism (NAD+ restoration) is demonstrated in"
    _Most substantive self-verification step_
  - (-) `self_check[2]`: "Did not fabricate problems - the text clearly makes the mouse-to-human leap"
    _Fluff self-check_
  - Note: 3 self-check items
  - Note: Self-check quality: 1 deep, 1 arithmetic, 1 fluff

**Mechanism Quality:** 3.0/10
  - (+) `(mechanism analysis)`: "2. Noted that the treatment showed positive results in mice: repaired brain damage and restored memory"
    _Mechanism description_
  - Note: Describes mechanism but does not name concept

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.67, 279 words

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
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'The exact nature of the Alzheimer's model in the mice...' is listed but not addressed
  - `uncertainties[0]`: "The exact nature of the Alzheimer's model in the mice"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether any preliminary human data exists that wasn't mentio...' is listed but not addressed
  - `uncertainties[1]`: "Whether any preliminary human data exists that wasn't mentioned"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Opus

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (1/10 content words)
  - `key_claims[0]`: "Mouse model results are being used to suggest human therapeutic potential without human evidence"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/12 content words)
  - `key_claims[1]`: "The leap from 'mice regained normal memory' to suggesting 'meaningful recovery' in human patients is"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (1/8 content words)
  - `key_claims[2]`: "While calling for clinical trials is appropriate, the optimistic framing exceeds the evidence"
- **[WARN]** `[HEURISTIC]` `unused_assumption`: Assumption 2 appears unused in reasoning or answer
  - `assumptions[1]`: "The mice had some form of induced Alzheimer's-like pathology"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 1 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[0]`: "The exact nature of the Alzheimer's model in the mice"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "solid - if the researchers had been more cautious about human applicability"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 2 is stated without rejection reasoning
  - `alternative_hypotheses[1]`: "overclaim - there is an element of overclaiming in suggesting human therapeutic potential"
- **[NOTE]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Causal mechanism described but underlying concept not named
  - `final_answer`: "mechanism_vs_evidence"


## Agent Profiles

### Claude Opus (claude-opus-4-20250514)
**Parse OK:** True | **Latency:** 16052ms

**Final Answer:** mechanism_vs_evidence

**Confidence:** 0.9

**Assumptions:**
- The study was conducted entirely in genetically engineered mice
- The mice had some form of induced Alzheimer's-like pathology
- NAD+ restoration showed benefits in these mouse models
- The researchers are proposing human trials based on these results

**Reasoning Steps:**
1. 1. Identified that the entire study was conducted in genetically engineered mice, not humans
2. 2. Noted that the treatment showed positive results in mice: repaired brain damage and restored memory
3. 3. Observed that researchers are extrapolating from mouse results to suggest human therapeutic potential
4. 4. Recognized the classic pattern of mechanism demonstrated in animals being applied to humans without human evidence
5. 5. The call for clinical trials is appropriate, but the suggestion of 'meaningful recovery' in humans based solely on mouse data is premature

**Key Claims:**
- Mouse model results are being used to suggest human therapeutic potential without human evidence
- The leap from 'mice regained normal memory' to suggesting 'meaningful recovery' in human patients is unsupported
- While calling for clinical trials is appropriate, the optimistic framing exceeds the evidence

**Alternative Hypotheses:**
- solid - if the researchers had been more cautious about human applicability
- overclaim - there is an element of overclaiming in suggesting human therapeutic potential

**Uncertainties:**
- The exact nature of the Alzheimer's model in the mice
- Whether any preliminary human data exists that wasn't mentioned
- The specific language used by the researchers vs. the summary author

**Self-Verification:**
- Confirmed this is mechanism vs. evidence rather than overclaim because a mechanism (NAD+ restoration) is demonstrated in one context (mice) and applied to another (humans)
- The study itself may be solid for what it is - a mouse study - but the extrapolation to humans is the issue
- Did not fabricate problems - the text clearly makes the mouse-to-human leap

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 3.4/6 `#####.....`
- Uncertainty Handling: 3.3/6 `#####.....`
- Alternative Hypothesis Quality: 4.5/6 `#######...`
- Self Monitoring Quality: 3.6/8 `####......`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 3.0/10 `###.......`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Opus** scored **70.6/100**.

**Best per dimension:**
- Correctness: Claude Opus (30.0/30)
- Support Strength: Claude Opus (0.0/8)
- Structural Reasoning: Claude Opus (4.8/8)
- Assumption Discipline: Claude Opus (3.4/6)
- Uncertainty Handling: Claude Opus (3.3/6)
- Alternative Hypothesis Quality: Claude Opus (4.5/6)
- Self Monitoring Quality: Claude Opus (3.6/8)
- Insight Depth: Claude Opus (8.0/8)
- Mechanism Quality: Claude Opus (3.0/10)
- Communication Efficiency: Claude Opus (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Opus | 16.1s | 70.6/100 | 4.4 |

Failure modes observed: decorative_uncertainty, unsupported_conclusion, unsupported_intermediate_step, unused_assumption.
