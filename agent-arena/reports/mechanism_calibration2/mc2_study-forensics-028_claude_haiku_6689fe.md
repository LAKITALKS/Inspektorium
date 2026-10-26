# Forensic Dossier: Study Forensics: NAD+ restoration reverses Alzheimer's in mice

**Run ID:** `mc2_study-forensics-028_claude_haiku_6689fe`  
**Task:** study-forensics-028 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-06T16:22:43.371175+00:00  
**Task Family:** mechanism_vs_evidence  
**Trap Type:** animal_to_human_overreach  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **72.0/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, named_not_explained, unsupported_conclusion, unsupported_intermediate_step, unused_assumption
**Forensic flags:** 4
**Consistency findings:** 7
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 30.0/30 | 0.0/8 | 4.8/8 | 4.3/6 | 3.6/6 | 5.0/6 | 4.8/8 | 8.0/8 | 1.5/10 | 10.0/10 | **72.0/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `mechanism_vs_evidence` [+] (gold: `mechanism_vs_evidence`)
**Finding Recall:** 100%
**Matched Findings:** mechanism_not_demonstrated, conclusion_exceeds_results
**Extra Findings:** cautious_scope_control, none_or_minor, decorative_uncertainty, correlation_as_causation

## Reasoning Integrity Audit

### Claude Haiku
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 6

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
- "mechanism_vs_evidence"


## Forensic Flags

### Claude Haiku

- **[MODERATE]** `weak_mechanism`: Correct answer but weak mechanism explanation — answer may not generalize
  - `final_answer`: "mechanism_vs_evidence"
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
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 6
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[3]`: "Evaluated whether mouse brain physiology and disease mechanisms are sufficiently similar to human Alzheimer's to warrant"
    _Most informative reasoning step_
  - Note: 6 reasoning steps
  - Note: Low step utility: 0/6 steps contribute

**Assumption Discipline:** 4.3/6
  - (+) `assumptions[0]`: "The study was conducted in genetically engineered mouse models of Alzheimer's disease"
    _Most substantive assumption_
  - (-) `assumptions[2]`: "Memory performance was measured using standard behavioral tests in mice"
    _Declared but unused in reasoning_
  - Note: 5/5 substantive assumptions
  - Note: 1 unused assumption(s)

**Uncertainty Handling:** 3.6/6
  - (+) `uncertainties[4]`: "The exact wording of the original study and whether this summary accurately represents the scientists' actual claims abo"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.78"
    _Stated confidence level_
  - (-) `uncertainties[3]`: "Whether confounding variables (e.g., stress from treatment, non-specific effects) were controlled"
    _Listed but never addressed in reasoning_
  - Note: 5 uncertainties (5 substantive)
  - Note: 1 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 5.0/6
  - (+) `alternative_hypotheses[0]`: "Solid study: If the mouse model is well-validated, the findings are clearly presented as preclinical, and the call for t"
    _Most substantive alternative hypothesis_
  - Note: 3 alternative hypotheses considered
  - Note: 1/3 include rejection reasoning

**Self Monitoring Quality:** 4.8/8
  - (+) `self_check[0]`: "Did I overstate the problem? The text does call for clinical trials, which is appropriate. However, the framing ('sugges"
    _Most substantive self-verification step_
  - Note: 4 self-check items
  - Note: Self-check quality: 0 deep, 4 arithmetic, 0 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.69, 478 words

**Insight Depth:** 8.0/8
  - Note: Key insights: 2 full / 2


## Failure Analysis

### Claude Haiku

**MODERATE:**
- **Unsupported Conclusion** `[MEDIUM CONFIDENCE]`: Final answer lacks load-bearing or supporting step grounding
  - `final_answer`: "mechanism_vs_evidence"
  - _Impacts: support_strength_
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Names the phenomenon but does not explain the causal mechanism
  - `final_answer`: "mechanism_vs_evidence"
  - _Impacts: mechanism_quality_
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Named concept(s) ['effect'] but mechanism not described
  - _Impacts: mechanism_quality, insight_depth_
- **Unsupported Intermediate Step** `[MEDIUM CONFIDENCE]`: No reasoning step is load-bearing — final answer lacks traceable derivation
  - `final_answer`: "mechanism_vs_evidence"
  - _Impacts: support_strength, structural_reasoning_

**STYLISTIC:**
- **Unused Assumption** `[HEURISTIC]`: Assumption 'Memory performance was measured using standard behavioral te...' is declared but not referenced in reasoning
  - `assumptions[2]`: "Memory performance was measured using standard behavioral tests in mice"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether confounding variables (e.g., stress from treatment, ...' is listed but not addressed
  - `uncertainties[3]`: "Whether confounding variables (e.g., stress from treatment, non-specific effects) were controlled"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/16 content words)
  - `key_claims[0]`: "The primary mechanism-vs-evidence issue: Findings in genetically engineered mice are presented as su"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/14 content words)
  - `key_claims[1]`: "The phrase 'suggest that boosting NAD+ could move Alzheimer's therapy' makes a human therapeutic cla"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/12 content words)
  - `key_claims[2]`: "The call for clinical trials is appropriate, but it follows confident claims about recovery potentia"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/11 content words)
  - `key_claims[3]`: "No mention of limitations of mouse models, genetic engineering effects, or why this mouse finding sh"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 4 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[3]`: "Whether confounding variables (e.g., stress from treatment, non-specific effects) were controlled"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "Solid study: If the mouse model is well-validated, the findings are clearly presented as preclinical"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 2 is stated without rejection reasoning
  - `alternative_hypotheses[1]`: "Overclaim: If the text overstates the certainty of human applicability without acknowledging model l"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 10250ms

**Final Answer:** mechanism_vs_evidence

**Confidence:** 0.78

**Assumptions:**
- The study was conducted in genetically engineered mouse models of Alzheimer's disease
- The treatment successfully restored NAD+ levels in treated mice
- Memory performance was measured using standard behavioral tests in mice
- The text represents an accurate summary of the study's findings and claims
- No human clinical data are presented in this summary

**Reasoning Steps:**
1. Identified the core claim: NAD+ restoration repaired brain damage and restored memory in mice with advanced Alzheimer's
2. Recognized that the study was conducted in mice, not humans
3. Noted the leap from mouse findings to human therapeutic potential ('suggest that boosting NAD+ could move Alzheimer's therapy')
4. Evaluated whether mouse brain physiology and disease mechanisms are sufficiently similar to human Alzheimer's to warrant the therapeutic claims
5. Assessed the call for clinical trials as appropriate scientific next step, but noted it follows strong claims about therapeutic potential
6. Examined whether the text acknowledges the translational gap between mouse models and human disease

**Key Claims:**
- The primary mechanism-vs-evidence issue: Findings in genetically engineered mice are presented as suggesting therapeutic potential in humans without explicit acknowledgment of the translational gap
- The phrase 'suggest that boosting NAD+ could move Alzheimer's therapy' makes a human therapeutic claim based on mouse data
- The call for clinical trials is appropriate, but it follows confident claims about recovery potential rather than being framed as exploratory
- No mention of limitations of mouse models, genetic engineering effects, or why this mouse finding should translate to human disease

**Alternative Hypotheses:**
- Solid study: If the mouse model is well-validated, the findings are clearly presented as preclinical, and the call for trials is appropriately cautious
- Overclaim: If the text overstates the certainty of human applicability without acknowledging model limitations
- Correlation vs. causation: If NAD+ restoration is correlated with recovery but causation isn't established (less likely given experimental design)

**Uncertainties:**
- Whether the mouse model used is a validated, translatable model of human Alzheimer's pathology
- Whether 'repaired brain damage' refers to structural imaging, histology, or functional recovery only
- The magnitude of memory recovery and whether it was complete or partial
- Whether confounding variables (e.g., stress from treatment, non-specific effects) were controlled
- The exact wording of the original study and whether this summary accurately represents the scientists' actual claims about clinical translation

**Self-Verification:**
- Did I overstate the problem? The text does call for clinical trials, which is appropriate. However, the framing ('suggest that boosting NAD+ could move Alzheimer's therapy') treats mouse recovery as evidence for human therapeutic potential without caveats.
- Did I miss that the text is appropriately cautious? The word 'suggest' is present, but it's weak uncertainty language paired with strong mechanistic claims. This is decorative uncertainty.
- Is this truly mechanism-vs-evidence? Yes: the mechanism (NAD+ restoration → recovery) is demonstrated in mice, but the evidence is applied to humans without acknowledging the translational gap.
- Could this be overclaim instead? Possibly, but the core issue is the unjustified leap from mouse to human mechanism, making mechanism-vs-evidence the more precise classification.

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 4.3/6 `#######...`
- Uncertainty Handling: 3.6/6 `######....`
- Alternative Hypothesis Quality: 5.0/6 `########..`
- Self Monitoring Quality: 4.8/8 `######....`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Haiku** scored **72.0/100**.

**Best per dimension:**
- Correctness: Claude Haiku (30.0/30)
- Support Strength: Claude Haiku (0.0/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (4.3/6)
- Uncertainty Handling: Claude Haiku (3.6/6)
- Alternative Hypothesis Quality: Claude Haiku (5.0/6)
- Self Monitoring Quality: Claude Haiku (4.8/8)
- Insight Depth: Claude Haiku (8.0/8)
- Mechanism Quality: Claude Haiku (1.5/10)
- Communication Efficiency: Claude Haiku (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 10.2s | 72.0/100 | 7.0 |

Failure modes observed: decorative_uncertainty, named_not_explained, unsupported_conclusion, unsupported_intermediate_step, unused_assumption.
