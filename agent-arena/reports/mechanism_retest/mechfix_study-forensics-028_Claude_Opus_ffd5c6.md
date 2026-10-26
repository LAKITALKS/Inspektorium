# Forensic Dossier: Study Forensics: NAD+ restoration reverses Alzheimer's in mice

**Run ID:** `mechfix_study-forensics-028_Claude_Opus_ffd5c6`  
**Task:** study-forensics-028 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T16:42:11.001112+00:00  
**Task Family:** mechanism_vs_evidence  
**Trap Type:** animal_to_human_overreach  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Opus
**Winner:** Claude Opus — **69.3/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, unsupported_conclusion, unsupported_intermediate_step, unused_assumption
**Forensic flags:** 3
**Consistency findings:** 4
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Opus | 30.0/30 | 0.0/8 | 4.8/8 | 3.4/6 | 3.6/6 | 5.5/6 | 4.0/8 | 8.0/8 | 0.0/10 | 10.0/10 | **69.3/100** |

## Study Forensics Audit

### Claude Opus

**Classification:** `mechanism_vs_evidence` [+] (gold: `mechanism_vs_evidence`)
**Finding Recall:** 100%
**Matched Findings:** mechanism_not_demonstrated, conclusion_exceeds_results
**Extra Findings:** cautious_scope_control, none_or_minor, unsupported_generalization, decorative_uncertainty, correlation_as_causation

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
  - (+) `steps[4]`: "Checked for bridge support: the call for clinical trials acknowledges the gap but doesn't provide evidence that mouse NA"
    _Most informative reasoning step_
  - Note: 6 reasoning steps
  - Note: Low step utility: 0/6 steps contribute

**Assumption Discipline:** 3.4/6
  - (+) `assumptions[0]`: "The study used genetically engineered mice with Alzheimer's-like pathology"
    _Most substantive assumption_
  - (-) `assumptions[2]`: "Memory performance was measured through standard rodent behavioral tests"
    _Declared but unused in reasoning_
  - Note: 4/4 substantive assumptions
  - Note: 1 unused assumption(s)

**Uncertainty Handling:** 3.6/6
  - (+) `uncertainties[2]`: "Whether any preliminary human data exists that wasn't mentioned"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.9"
    _Stated confidence level_
  - (-) `uncertainties[2]`: "Whether any preliminary human data exists that wasn't mentioned"
    _Listed but never addressed in reasoning_
  - Note: 3 uncertainties (3 substantive)
  - Note: 1 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 5.5/6
  - (+) `alternative_hypotheses[0]`: "Could be classified as solid if the text had limited conclusions to mouse models only"
    _Most substantive alternative hypothesis_
  - Note: 3 alternative hypotheses considered
  - Note: 2/3 include rejection reasoning

**Self Monitoring Quality:** 4.0/8
  - (+) `self_check[1]`: "The call for clinical trials is appropriate scientific caution but doesn't bridge the evidence gap"
    _Most substantive self-verification step_
  - Note: 3 self-check items
  - Note: Self-check quality: 0 deep, 3 arithmetic, 0 fluff

**Mechanism Quality:** 0.0/10
  - Note: Neither names concept nor explains mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.72, 265 words

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
- **Unused Assumption** `[HEURISTIC]`: Assumption 'Memory performance was measured through standard rodent beha...' is declared but not referenced in reasoning
  - `assumptions[2]`: "Memory performance was measured through standard rodent behavioral tests"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether any preliminary human data exists that wasn't mentio...' is listed but not addressed
  - `uncertainties[2]`: "Whether any preliminary human data exists that wasn't mentioned"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Opus

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/13 content words)
  - `key_claims[0]`: "Mouse study showing NAD+ restoration improves Alzheimer's symptoms is being extrapolated to suggest "
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/9 content words)
  - `key_claims[1]`: "The hedge 'called for clinical trials' acknowledges but doesn't resolve the evidence-tier mismatch"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (1/9 content words)
  - `key_claims[2]`: "The phrase 'meaningful recovery' implies human benefit despite only animal evidence"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "Could be classified as solid if the text had limited conclusions to mouse models only"


## Agent Profiles

### Claude Opus (claude-opus-4-20250514)
**Parse OK:** True | **Latency:** 16154ms

**Final Answer:** mechanism_vs_evidence

**Confidence:** 0.9

**Assumptions:**
- The study used genetically engineered mice with Alzheimer's-like pathology
- NAD+ restoration was achieved through some compound administration
- Memory performance was measured through standard rodent behavioral tests
- The mice had 'advanced Alzheimer's' as modeled in the animal system

**Reasoning Steps:**
1. Identified that this is an animal study using genetically engineered mice
2. Noted the intervention: restoring NAD+ levels with a compound
3. Observed the reported outcomes: repaired brain damage and restored memory in mice
4. Analyzed the conclusion: scientists suggest this could lead to meaningful recovery in human Alzheimer's patients
5. Checked for bridge support: the call for clinical trials acknowledges the gap but doesn't provide evidence that mouse NAD+ findings will translate to humans
6. The text implies therapeutic potential for human patients based solely on mouse data

**Key Claims:**
- Mouse study showing NAD+ restoration improves Alzheimer's symptoms is being extrapolated to suggest human therapeutic potential
- The hedge 'called for clinical trials' acknowledges but doesn't resolve the evidence-tier mismatch
- The phrase 'meaningful recovery' implies human benefit despite only animal evidence

**Alternative Hypotheses:**
- Could be classified as solid if the text had limited conclusions to mouse models only
- Not overclaim because the scientists do acknowledge need for clinical trials
- Not correlation vs causation as this appears to be an intervention study

**Uncertainties:**
- Exact nature of the 'compound' used to restore NAD+
- Specific memory tests used in mice
- Whether any preliminary human data exists that wasn't mentioned

**Self-Verification:**
- Confirmed this is animal evidence being used to suggest human therapeutic potential
- The call for clinical trials is appropriate scientific caution but doesn't bridge the evidence gap
- Not overflagging - the text clearly implies human therapeutic benefit from mouse data alone

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 3.4/6 `#####.....`
- Uncertainty Handling: 3.6/6 `######....`
- Alternative Hypothesis Quality: 5.5/6 `#########.`
- Self Monitoring Quality: 4.0/8 `#####.....`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 0.0/10 `..........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Opus** scored **69.3/100**.

**Best per dimension:**
- Correctness: Claude Opus (30.0/30)
- Support Strength: Claude Opus (0.0/8)
- Structural Reasoning: Claude Opus (4.8/8)
- Assumption Discipline: Claude Opus (3.4/6)
- Uncertainty Handling: Claude Opus (3.6/6)
- Alternative Hypothesis Quality: Claude Opus (5.5/6)
- Self Monitoring Quality: Claude Opus (4.0/8)
- Insight Depth: Claude Opus (8.0/8)
- Mechanism Quality: Claude Opus (0.0/10)
- Communication Efficiency: Claude Opus (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Opus | 16.2s | 69.3/100 | 4.3 |

Failure modes observed: decorative_uncertainty, unsupported_conclusion, unsupported_intermediate_step, unused_assumption.
