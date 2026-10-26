# Forensic Dossier: Study Forensics: NAD+ restoration reverses Alzheimer's in mice

**Run ID:** `praxis_study-forensics-028_Claude_Haiku_b96650`  
**Task:** study-forensics-028 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-07T07:55:21.202104+00:00  
**Task Family:** mechanism_vs_evidence  
**Trap Type:** animal_to_human_overreach  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **73.2/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, unsupported_conclusion, unsupported_intermediate_step, unused_assumption
**Forensic flags:** 3
**Consistency findings:** 8
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 30.0/30 | 0.0/8 | 4.8/8 | 3.7/6 | 3.6/6 | 5.0/6 | 5.6/8 | 8.0/8 | 4.0/10 | 8.5/10 | **73.2/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `mechanism_vs_evidence` [+] (gold: `mechanism_vs_evidence`)
**Finding Recall:** 100%
**Matched Findings:** mechanism_not_demonstrated, conclusion_exceeds_results
**Extra Findings:** cautious_scope_control, none_or_minor, correlation_as_causation

## Reasoning Integrity Audit

### Claude Haiku
**Classification:** Correct but brittle reasoning
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
- "mechanism_vs_evidence"


## Forensic Flags

### Claude Haiku

- **[MAJOR]** `unsupported_leap`: Correct answer with weak support chain — final answer may be an unsupported leap
- **[MODERATE]** `unsupported_conclusion_claims`: 1/1 conclusion claims lack step support
  - `final_answer`: "mechanism_vs_evidence"
- **[MODERATE]** `ungrounded_mechanism`: Mechanism named/described but not connected to case-specific data
  - `(mechanism analysis)`: "effect"


## Evidence Map

### Claude Haiku

**Correctness:** 30.0/30
  - (+) `final_answer`: "mechanism_vs_evidence"
    _Agent's answer for correctness check_
  - Note: Exact match

**Support Strength:** 0.0/8
  - (-) `final_answer`: "mechanism_vs_evidence"
    _Conclusion not supported by steps_
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 7
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[3]`: "Assessed the specificity of the claim: 'moving beyond slowing decline toward meaningful recovery' is presented as a pros"
    _Most informative reasoning step_
  - Note: 7 reasoning steps
  - Note: Low step utility: 0/7 steps contribute

**Assumption Discipline:** 3.7/6
  - (+) `assumptions[0]`: "The study was conducted in genetically engineered mouse models of Alzheimer's disease"
    _Most substantive assumption_
  - (-) `assumptions[2]`: "Memory performance was measured using standard behavioral tests in mice"
    _Declared but unused in reasoning_
  - Note: 6/6 substantive assumptions
  - Note: Many assumptions (6)

**Uncertainty Handling:** 3.6/6
  - (+) `uncertainties[3]`: "Whether the researchers themselves made the clinical translation claims or if this is editorial interpretation"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.72"
    _Stated confidence level_
  - (-) `uncertainties[4]`: "The timeline of treatment relative to disease progression (early vs. late intervention)"
    _Listed but never addressed in reasoning_
  - Note: 6 uncertainties (6 substantive)
  - Note: 1 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 5.0/6
  - (+) `alternative_hypotheses[0]`: "solid — if the study is well-designed and the researchers appropriately frame mouse results as preliminary"
    _Most substantive alternative hypothesis_
  - Note: 3 alternative hypotheses considered
  - Note: 1/3 include rejection reasoning

**Self Monitoring Quality:** 5.6/8
  - (+) `self_check[2]`: "Is this truly mechanism_vs_evidence? Yes — the mechanism (NAD+ restoration) is demonstrated in one context (mice) and ap"
    _Most substantive self-verification step_
  - Note: 5 self-check items
  - Note: Self-check quality: 0 deep, 5 arithmetic, 0 fluff

**Mechanism Quality:** 4.0/10
  - (+) `(mechanism analysis)`: "Evaluated the translation claim: results in mice are presented as suggesting human therapeutic potential"
    _Mechanism description without case grounding_
  - Note: Names concept + describes mechanism (not grounded to case)

**Communication Efficiency:** 8.5/10
  - Note: Signal density: 0.70, 569 words

**Insight Depth:** 8.0/8
  - Note: Key insights: 2 full / 2


## Failure Analysis

### Claude Haiku

**MODERATE:**
- **Unsupported Conclusion** `[MEDIUM CONFIDENCE]`: Final answer lacks load-bearing or supporting step grounding
  - `final_answer`: "mechanism_vs_evidence"
  - _Impacts: support_strength_
- **Unsupported Intermediate Step** `[MEDIUM CONFIDENCE]`: No reasoning step is load-bearing — final answer lacks traceable derivation
  - `final_answer`: "mechanism_vs_evidence"
  - _Impacts: support_strength, structural_reasoning_

**STYLISTIC:**
- **Unused Assumption** `[HEURISTIC]`: Assumption 'Memory performance was measured using standard behavioral te...' is declared but not referenced in reasoning
  - `assumptions[2]`: "Memory performance was measured using standard behavioral tests in mice"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'The timeline of treatment relative to disease progression (e...' is listed but not addressed
  - `uncertainties[4]`: "The timeline of treatment relative to disease progression (early vs. late intervention)"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (1/18 content words)
  - `key_claims[0]`: "The primary mechanism claim (NAD+ depletion → energy imbalance → Alzheimer's pathology) is demonstra"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (1/16 content words)
  - `key_claims[1]`: "The treatment effect (memory recovery in mice) is presented as evidence for human therapeutic potent"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/20 content words)
  - `key_claims[2]`: "The framing 'move beyond slowing decline toward meaningful recovery' is aspirational language based "
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/18 content words)
  - `key_claims[3]`: "The call for clinical trials is reasonable given positive mouse data, but the text does not acknowle"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 5 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[4]`: "The timeline of treatment relative to disease progression (early vs. late intervention)"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "solid — if the study is well-designed and the researchers appropriately frame mouse results as preli"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 2 is stated without rejection reasoning
  - `alternative_hypotheses[1]`: "overclaim — if the language overstates what mouse models can tell us about human disease"
- **[NOTE]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Causal mechanism described but underlying concept not named
  - `final_answer`: "mechanism_vs_evidence"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 11574ms

**Final Answer:** mechanism_vs_evidence

**Confidence:** 0.72

**Assumptions:**
- The study was conducted in genetically engineered mouse models of Alzheimer's disease
- The treatment successfully restored NAD+ levels in treated mice
- Memory performance was measured using standard behavioral tests in mice
- The text represents an accurate summary of the study's findings and claims
- Mouse models of Alzheimer's share relevant pathophysiology with human disease
- The researchers made the quoted statements about clinical translation

**Reasoning Steps:**
1. Identified the core mechanism claim: NAD+ depletion disrupts brain energy balance in Alzheimer's
2. Identified the evidence base: mouse model study with treatment intervention
3. Evaluated the translation claim: results in mice are presented as suggesting human therapeutic potential
4. Assessed the specificity of the claim: 'moving beyond slowing decline toward meaningful recovery' is presented as a prospect based on mouse data
5. Examined the causal language: 'repaired brain damage' and 'regained normal memory' are stated as outcomes in mice
6. Evaluated whether mouse findings directly support human clinical claims
7. Checked for appropriate caveats about translational gap

**Key Claims:**
- The primary mechanism claim (NAD+ depletion → energy imbalance → Alzheimer's pathology) is demonstrated in mice but the text does not establish whether this mechanism is causal or correlational in the disease process
- The treatment effect (memory recovery in mice) is presented as evidence for human therapeutic potential, but this represents a significant translational leap without human data
- The framing 'move beyond slowing decline toward meaningful recovery' is aspirational language based on mouse outcomes; it is unclear whether this reflects the researchers' claims or editorial interpretation
- The call for clinical trials is reasonable given positive mouse data, but the text does not acknowledge the well-known challenges of translating Alzheimer's treatments from mice to humans

**Alternative Hypotheses:**
- solid — if the study is well-designed and the researchers appropriately frame mouse results as preliminary
- overclaim — if the language overstates what mouse models can tell us about human disease
- correlation_vs_causation — if NAD+ restoration is correlated with recovery but causation isn't established

**Uncertainties:**
- Whether the original study included appropriate controls (vehicle-treated mice, sham treatment groups)
- Whether the memory recovery was complete or partial, and how it was measured
- The specific nature of 'brain damage repair' — whether this is structural, functional, or both
- Whether the researchers themselves made the clinical translation claims or if this is editorial interpretation
- The timeline of treatment relative to disease progression (early vs. late intervention)
- Whether confounders like off-target effects of the NAD+-boosting compound were adequately controlled

**Self-Verification:**
- Did I overstate the problems? The study itself may be solid; the issue is the translation claim. The text does present mouse findings as suggesting human therapeutic potential without adequate caveats about the translational gap.
- Did I miss that this is actually solid? The researchers appropriately called for clinical trials rather than claiming human efficacy. However, the language 'suggest that boosting NAD+ could move Alzheimer's therapy' does imply human relevance based on mouse data alone.
- Is this truly mechanism_vs_evidence? Yes — the mechanism (NAD+ restoration) is demonstrated in one context (mice) and applied to another (human patients) without human evidence. The call for trials is appropriate, but the framing suggests the mouse mechanism will translate.
- Should this be overclaim instead? Possibly — the language about 'meaningful recovery' and moving 'beyond slowing decline' may exceed what mouse data alone supports. However, the explicit call for clinical trials suggests appropriate epistemic humility.
- The core issue: The text presents mouse findings as a basis for human therapeutic optimism without adequately flagging the translational gap. This is a classic mechanism_vs_evidence problem.

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 3.7/6 `######....`
- Uncertainty Handling: 3.6/6 `######....`
- Alternative Hypothesis Quality: 5.0/6 `########..`
- Self Monitoring Quality: 5.6/8 `#######...`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 4.0/10 `####......`
- Communication Efficiency: 8.5/10 `########..`


## Final Verdict

**Solo run: Claude Haiku** scored **73.2/100**.

**Best per dimension:**
- Correctness: Claude Haiku (30.0/30)
- Support Strength: Claude Haiku (0.0/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (3.7/6)
- Uncertainty Handling: Claude Haiku (3.6/6)
- Alternative Hypothesis Quality: Claude Haiku (5.0/6)
- Self Monitoring Quality: Claude Haiku (5.6/8)
- Insight Depth: Claude Haiku (8.0/8)
- Mechanism Quality: Claude Haiku (4.0/10)
- Communication Efficiency: Claude Haiku (8.5/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 11.6s | 73.2/100 | 6.3 |

Failure modes observed: decorative_uncertainty, unsupported_conclusion, unsupported_intermediate_step, unused_assumption.
