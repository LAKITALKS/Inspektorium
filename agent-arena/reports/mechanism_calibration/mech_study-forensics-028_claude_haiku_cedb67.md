# Forensic Dossier: Study Forensics: NAD+ restoration reverses Alzheimer's in mice

**Run ID:** `mech_study-forensics-028_claude_haiku_cedb67`  
**Task:** study-forensics-028 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-06T15:43:31.792087+00:00  
**Task Family:** mechanism_vs_evidence  
**Trap Type:** animal_to_human_overreach  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **68.9/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, unsupported_intermediate_step, unused_assumption
**Forensic flags:** 3
**Consistency findings:** 8
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 30.0/30 | 0.7/8 | 4.8/8 | 4.3/6 | 3.3/6 | 4.5/6 | 4.8/8 | 8.0/8 | 0.0/10 | 8.5/10 | **68.9/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `mechanism_vs_evidence` [+] (gold: `mechanism_vs_evidence`)
**Finding Recall:** 100%
**Matched Findings:** mechanism_not_demonstrated, conclusion_exceeds_results
**Extra Findings:** cautious_scope_control, none_or_minor, unsupported_generalization, correlation_as_causation

## Reasoning Integrity Audit

### Claude Haiku
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 7

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
- "mechanism_vs_evidence"


## Forensic Flags

### Claude Haiku

- **[MODERATE]** `weak_mechanism`: Correct answer but weak mechanism explanation — answer may not generalize
  - `final_answer`: "mechanism_vs_evidence"
- **[MAJOR]** `unsupported_leap`: Correct answer with weak support chain — final answer may be an unsupported leap
- **[MODERATE]** `unsupported_conclusion_claims`: 1/1 conclusion claims lack step support
  - `final_answer`: "mechanism_vs_evidence"


## Evidence Map

### Claude Haiku

**Correctness:** 30.0/30
  - (+) `final_answer`: "mechanism_vs_evidence"
    _Agent's answer for correctness check_
  - Note: Exact match

**Support Strength:** 1.2/8
  - (+) `final_answer`: "mechanism_vs_evidence"
    _Conclusion grounded by reasoning chain_
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 7
  - Note: Reasoning graph confirms conclusion grounding

**Structural Reasoning:** 4.8/8
  - (+) `steps[5]`: "Examined the language: 'suggest' and 'call for clinical trials' indicate awareness that translation is uncertain, but th"
    _Most informative reasoning step_
  - Note: 7 reasoning steps
  - Note: Low step utility: 0/7 steps contribute

**Assumption Discipline:** 4.3/6
  - (+) `assumptions[0]`: "The study was conducted in genetically engineered mouse models of Alzheimer's disease"
    _Most substantive assumption_
  - (-) `assumptions[2]`: "Memory performance was measured using standard behavioral tests in mice"
    _Declared but unused in reasoning_
  - Note: 5/5 substantive assumptions
  - Note: 1 unused assumption(s)

**Uncertainty Handling:** 3.3/6
  - (+) `uncertainties[0]`: "Whether the genetically engineered mice fully recapitulate human Alzheimer's pathology (a known limitation of mouse mode"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.78"
    _Stated confidence level_
  - (-) `uncertainties[1]`: "Whether 'repaired brain damage' refers to structural imaging, histology, or functional recovery—each has different impli"
    _Listed but never addressed in reasoning_
  - (-) `uncertainties[4]`: "Whether confounders (e.g., off-target effects of the NAD+-boosting compound) were controlled"
    _Listed but never addressed in reasoning_
  - Note: 5 uncertainties (5 substantive)
  - Note: 2 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 4.5/6
  - (+) `alternative_hypotheses[0]`: "Solid study: If the mouse work is rigorous and the researchers appropriately frame it as preclinical evidence warranting"
    _Most substantive alternative hypothesis_
  - Note: 3 alternative hypotheses considered
  - Note: 3/3 genuinely diverse alternatives

**Self Monitoring Quality:** 4.8/8
  - (+) `self_check[2]`: "Is this really mechanism_vs_evidence or just normal preclinical-to-clinical translation? The distinction is subtle: mech"
    _Most substantive self-verification step_
  - Note: 4 self-check items
  - Note: Self-check quality: 0 deep, 4 arithmetic, 0 fluff

**Mechanism Quality:** 0.0/10
  - Note: Neither names concept nor explains mechanism

**Communication Efficiency:** 8.5/10
  - Note: Signal density: 0.68, 579 words

**Insight Depth:** 8.0/8
  - Note: Key insights: 2 full / 2


## Failure Analysis

### Claude Haiku

**MODERATE:**
- **Unsupported Intermediate Step** `[MEDIUM CONFIDENCE]`: No reasoning step is load-bearing — final answer lacks traceable derivation
  - `final_answer`: "mechanism_vs_evidence"
  - _Impacts: support_strength, structural_reasoning_

**STYLISTIC:**
- **Unused Assumption** `[HEURISTIC]`: Assumption 'Memory performance was measured using standard behavioral te...' is declared but not referenced in reasoning
  - `assumptions[2]`: "Memory performance was measured using standard behavioral tests in mice"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether 'repaired brain damage' refers to structural imaging...' is listed but not addressed
  - `uncertainties[1]`: "Whether 'repaired brain damage' refers to structural imaging, histology, or functional recovery—each"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether confounders (e.g., off-target effects of the NAD+-bo...' is listed but not addressed
  - `uncertainties[4]`: "Whether confounders (e.g., off-target effects of the NAD+-boosting compound) were controlled"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (2/20 content words)
  - `key_claims[0]`: "The primary epistemic issue is mechanism_vs_evidence: a mechanism (NAD+ restoration) and a treatment"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/13 content words)
  - `key_claims[1]`: "The text does include appropriate hedging language ('suggest,' 'call for clinical trials'), which pa"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/20 content words)
  - `key_claims[2]`: "However, the framing—'repaired brain damage and regained normal memory'—is presented as a strong pos"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/17 content words)
  - `key_claims[3]`: "The claim that this moves therapy 'beyond slowing decline toward meaningful recovery' is aspirationa"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 5 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[4]`: "Whether confounders (e.g., off-target effects of the NAD+-boosting compound) were controlled"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "Solid study: If the mouse work is rigorous and the researchers appropriately frame it as preclinical"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 2 is stated without rejection reasoning
  - `alternative_hypotheses[1]`: "Overclaim: If the text overstates the certainty that NAD+ restoration will work in humans or minimiz"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 3 is stated without rejection reasoning
  - `alternative_hypotheses[2]`: "Correlation vs. causation: If NAD+ changes are correlational rather than causal in the mouse model i"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 13857ms

**Final Answer:** mechanism_vs_evidence

**Confidence:** 0.78

**Assumptions:**
- The study was conducted in genetically engineered mouse models of Alzheimer's disease
- The treatment successfully restored NAD+ levels in treated mice
- Memory performance was measured using standard behavioral tests in mice
- The text represents an accurate summary of the study's findings and claims
- No human clinical data are presented in this summary

**Reasoning Steps:**
1. Identified the core claim: NAD+ restoration in mice with advanced Alzheimer's led to repair of brain damage and recovery of normal memory
2. Recognized that the study was conducted in genetically engineered mice, not humans
3. Noted the extrapolation: researchers claim these results 'suggest' the approach could work in patients and call for clinical trials
4. Evaluated whether mouse findings directly support human therapeutic claims
5. Assessed the mechanism transfer: the NAD+ disruption mechanism was demonstrated in mice; the claim extends this to human Alzheimer's therapy
6. Examined the language: 'suggest' and 'call for clinical trials' indicate awareness that translation is uncertain, but the framing still presents mouse recovery as evidence for human potential
7. Identified that while the caveats are present, the core epistemic problem is applying a mouse model mechanism/treatment outcome to humans without human data

**Key Claims:**
- The primary epistemic issue is mechanism_vs_evidence: a mechanism (NAD+ restoration) and a treatment outcome (memory recovery) demonstrated in mice are presented as evidence for human therapeutic potential without human data
- The text does include appropriate hedging language ('suggest,' 'call for clinical trials'), which partially mitigates the overclaim risk
- However, the framing—'repaired brain damage and regained normal memory'—is presented as a strong positive result that justifies moving toward human trials, which is a moderate extrapolation from mouse to human
- The claim that this moves therapy 'beyond slowing decline toward meaningful recovery' is aspirational language that goes beyond what the mouse data alone can support

**Alternative Hypotheses:**
- Solid study: If the mouse work is rigorous and the researchers appropriately frame it as preclinical evidence warranting trials, this could be acceptable science communication
- Overclaim: If the text overstates the certainty that NAD+ restoration will work in humans or minimizes the gap between mouse models and human disease
- Correlation vs. causation: If NAD+ changes are correlational rather than causal in the mouse model itself (though the text suggests causation was tested)

**Uncertainties:**
- Whether the genetically engineered mice fully recapitulate human Alzheimer's pathology (a known limitation of mouse models not addressed in the summary)
- Whether 'repaired brain damage' refers to structural imaging, histology, or functional recovery—each has different implications
- Whether the treatment was preventive, halting, or truly reversing damage in already-advanced disease
- The magnitude of effect size and whether it was statistically significant
- Whether confounders (e.g., off-target effects of the NAD+-boosting compound) were controlled

**Self-Verification:**
- Did I overstate the problem? The researchers do acknowledge uncertainty by calling for trials, so this is not a severe overclaim. The mechanism_vs_evidence label is appropriate because the core issue is translating mouse findings to humans.
- Did I miss a solid study interpretation? The mouse work itself may be rigorous, but the summary does not provide enough detail to evaluate that. The epistemic problem is at the translation level, not necessarily the mouse study design.
- Is this really mechanism_vs_evidence or just normal preclinical-to-clinical translation? The distinction is subtle: mechanism_vs_evidence applies when a mechanism shown in one context (mice) is used to justify claims in another (humans) without direct evidence in the second context. That fits here.
- Should this be 'overclaim' instead? Possibly, if the framing is too confident about human potential. But the presence of 'suggest' and 'call for trials' suggests appropriate caution, making mechanism_vs_evidence the better fit.

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.7/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 4.3/6 `#######...`
- Uncertainty Handling: 3.3/6 `#####.....`
- Alternative Hypothesis Quality: 4.5/6 `#######...`
- Self Monitoring Quality: 4.8/8 `######....`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 0.0/10 `..........`
- Communication Efficiency: 8.5/10 `########..`


## Final Verdict

**Solo run: Claude Haiku** scored **68.9/100**.

**Best per dimension:**
- Correctness: Claude Haiku (30.0/30)
- Support Strength: Claude Haiku (0.7/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (4.3/6)
- Uncertainty Handling: Claude Haiku (3.3/6)
- Alternative Hypothesis Quality: Claude Haiku (4.5/6)
- Self Monitoring Quality: Claude Haiku (4.8/8)
- Insight Depth: Claude Haiku (8.0/8)
- Mechanism Quality: Claude Haiku (0.0/10)
- Communication Efficiency: Claude Haiku (8.5/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 13.9s | 68.9/100 | 5.0 |

Failure modes observed: decorative_uncertainty, unsupported_intermediate_step, unused_assumption.
