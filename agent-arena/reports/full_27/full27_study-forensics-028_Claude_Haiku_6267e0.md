# Forensic Dossier: Study Forensics: NAD+ restoration reverses Alzheimer's in mice

**Run ID:** `full27_study-forensics-028_Claude_Haiku_6267e0`  
**Task:** study-forensics-028 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T17:04:05.613013+00:00  
**Task Family:** mechanism_vs_evidence  
**Trap Type:** animal_to_human_overreach  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **73.5/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty
**Forensic flags:** 1
**Consistency findings:** 5
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 30.0/30 | 2.4/8 | 5.4/8 | 4.8/6 | 3.6/6 | 6.0/6 | 4.8/8 | 8.0/8 | 0.0/10 | 8.5/10 | **73.5/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `mechanism_vs_evidence` [+] (gold: `mechanism_vs_evidence`)
**Finding Recall:** 100%
**Matched Findings:** mechanism_not_demonstrated, conclusion_exceeds_results
**Extra Findings:** cautious_scope_control, none_or_minor, unsupported_generalization, decorative_uncertainty, correlation_as_causation

## Reasoning Integrity Audit

### Claude Haiku
**Classification:** Correct and well-supported
**Load-bearing steps:** 1 / 5

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
- Indirect support: 1
- Unsupported: 0
- Contradicted: 0


## Forensic Flags

### Claude Haiku

- **[MODERATE]** `weak_mechanism`: Correct answer but weak mechanism explanation — answer may not generalize
  - `final_answer`: "mechanism_vs_evidence"


## Evidence Map

### Claude Haiku

**Correctness:** 30.0/30
  - (+) `final_answer`: "mechanism_vs_evidence"
    _Agent's answer for correctness check_
  - Note: Exact match

**Support Strength:** 2.4/8
  - (+) `final_answer`: "mechanism_vs_evidence"
    _Conclusion grounded by reasoning chain_
  - Note: Support classification: 0 load-bearing, 1 supporting, 0 mentioned / 5
  - Note: Reasoning graph confirms conclusion grounding

**Structural Reasoning:** 5.4/8
  - (+) `steps[4]`: "5. MECHANISM VS. EVIDENCE CLASSIFICATION: The text describes a mechanistic finding (NAD+ restoration repairs brain damag"
    _Most informative reasoning step_
  - Note: 5 reasoning steps
  - Note: Low step utility: 1/5 steps contribute

**Assumption Discipline:** 4.8/6
  - (+) `assumptions[0]`: "The study was conducted in genetically engineered mice with Alzheimer's-like pathology"
    _Most substantive assumption_
  - Note: 5/5 substantive assumptions

**Uncertainty Handling:** 3.6/6
  - (+) `uncertainties[0]`: "Whether the genetically engineered mice fully recapitulate human Alzheimer's pathology (a known limitation of mouse mode"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.92"
    _Stated confidence level_
  - (-) `uncertainties[3]`: "The specific nature of 'brain damage repair' — whether this is structural, functional, or biomarker-based"
    _Listed but never addressed in reasoning_
  - Note: 4 uncertainties (4 substantive)
  - Note: 1 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 6.0/6
  - (+) `alternative_hypotheses[0]`: "Could classify as 'solid' if the text were framed as 'mouse study suggests mechanism; human trials needed' without imply"
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 2/2 include rejection reasoning

**Self Monitoring Quality:** 4.8/8
  - (+) `self_check[1]`: "Is the hedging language sufficient to make this 'solid'? No — hedging acknowledges the gap but does not close it. A soli"
    _Most substantive self-verification step_
  - Note: 4 self-check items
  - Note: Self-check quality: 0 deep, 4 arithmetic, 0 fluff

**Mechanism Quality:** 0.0/10
  - Note: Neither names concept nor explains mechanism

**Communication Efficiency:** 8.5/10
  - Note: Signal density: 0.71, 526 words

**Insight Depth:** 8.0/8
  - (+) `(output text)`: "on: the study is conducted in animal models (genetically engineered mice"
    _Insight 'animal model' matched (exact)_
  - Note: Key insights: 2 full / 2


## Failure Analysis

### Claude Haiku

**STYLISTIC:**
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'The specific nature of 'brain damage repair' — whether this ...' is listed but not addressed
  - `uncertainties[3]`: "The specific nature of 'brain damage repair' — whether this is structural, functional, or biomarker-"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/11 content words)
  - `key_claims[0]`: "Mouse study shows NAD+ restoration can reverse cognitive decline in advanced Alzheimer's-like diseas"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/8 content words)
  - `key_claims[1]`: "Text implies this could translate to human therapeutic recovery, not just slowing decline"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (1/11 content words)
  - `key_claims[2]`: "No human evidence is presented; the bridge from animal to human is acknowledged as needing clinical "
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/10 content words)
  - `key_claims[3]`: "The hedging language ('suggest,' 'could,' 'clinical trials needed') is appropriate but does not reso"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 4 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[3]`: "The specific nature of 'brain damage repair' — whether this is structural, functional, or biomarker-"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 11963ms

**Final Answer:** mechanism_vs_evidence

**Confidence:** 0.92

**Assumptions:**
- The study was conducted in genetically engineered mice with Alzheimer's-like pathology
- The mice showed measurable cognitive recovery after NAD+ restoration
- The text implies this could translate to human therapeutic benefit
- No human clinical data are presented or referenced
- The call for clinical trials acknowledges the gap but does not close it

**Reasoning Steps:**
1. 1. EVIDENCE TIER IDENTIFICATION: The study is conducted in animal models (genetically engineered mice). This is Tier 2 evidence.
2. 2. CONCLUSION TIER IDENTIFICATION: The text implies human therapeutic benefit ('move Alzheimer's therapy beyond slowing decline toward meaningful recovery') and calls for clinical trials in patients. This is Tier 5 (human therapeutic) language.
3. 3. BRIDGE STEP DETECTION: There is a substantial gap between animal models and human clinical application. The text does not present human data, biomarker studies, or mechanistic evidence that would bridge this gap.
4. 4. HEDGE ANALYSIS: The phrase 'suggest that' and 'called for clinical trials to see if the approach will translate' acknowledges uncertainty about human applicability. However, these hedges do not constitute evidence that the mechanism works in humans. They are decorative uncertainty—they acknowledge the gap without closing it.
5. 5. MECHANISM VS. EVIDENCE CLASSIFICATION: The text describes a mechanistic finding (NAD+ restoration repairs brain damage in mice) and extrapolates to human therapeutic potential without direct human evidence. This is a classic mechanism_vs_evidence pattern: strong animal data, weak bridge to humans.

**Key Claims:**
- Mouse study shows NAD+ restoration can reverse cognitive decline in advanced Alzheimer's-like disease
- Text implies this could translate to human therapeutic recovery, not just slowing decline
- No human evidence is presented; the bridge from animal to human is acknowledged as needing clinical trials but not yet supported
- The hedging language ('suggest,' 'could,' 'clinical trials needed') is appropriate but does not resolve the evidence-tier gap

**Alternative Hypotheses:**
- Could classify as 'solid' if the text were framed as 'mouse study suggests mechanism; human trials needed' without implying therapeutic benefit. However, the language 'move Alzheimer's therapy toward meaningful recovery' implies human benefit, which exceeds the evidence tier.
- Could classify as 'overclaim' if the text made stronger certainty claims (e.g., 'will work in humans'). However, the hedging language prevents this classification; the issue is the tier mismatch, not false certainty.

**Uncertainties:**
- Whether the genetically engineered mice fully recapitulate human Alzheimer's pathology (a known limitation of mouse models not addressed in the text)
- Whether NAD+ depletion is a primary driver or secondary consequence of Alzheimer's in humans
- Whether the compound used is safe and bioavailable in humans
- The specific nature of 'brain damage repair' — whether this is structural, functional, or biomarker-based

**Self-Verification:**
- Did I overclassify this as mechanism_vs_evidence? No — the text explicitly moves from animal findings to human therapeutic implications without human data. This is the definition of mechanism_vs_evidence.
- Is the hedging language sufficient to make this 'solid'? No — hedging acknowledges the gap but does not close it. A solid study would either (a) present human data, or (b) frame the finding as 'mechanism in mice; human translation unknown.'
- Did I miss any human data? Re-read: no human trials, biomarkers, or observational studies are mentioned.
- Is this an unfair classification? No — the text's own call for clinical trials confirms that human evidence is absent and needed.

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 2.4/8 `###.......`
- Structural Reasoning: 5.4/8 `######....`
- Assumption Discipline: 4.8/6 `########..`
- Uncertainty Handling: 3.6/6 `######....`
- Alternative Hypothesis Quality: 6.0/6 `##########`
- Self Monitoring Quality: 4.8/8 `######....`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 0.0/10 `..........`
- Communication Efficiency: 8.5/10 `########..`


## Final Verdict

**Solo run: Claude Haiku** scored **73.5/100**.

**Best per dimension:**
- Correctness: Claude Haiku (30.0/30)
- Support Strength: Claude Haiku (2.4/8)
- Structural Reasoning: Claude Haiku (5.4/8)
- Assumption Discipline: Claude Haiku (4.8/6)
- Uncertainty Handling: Claude Haiku (3.6/6)
- Alternative Hypothesis Quality: Claude Haiku (6.0/6)
- Self Monitoring Quality: Claude Haiku (4.8/8)
- Insight Depth: Claude Haiku (8.0/8)
- Mechanism Quality: Claude Haiku (0.0/10)
- Communication Efficiency: Claude Haiku (8.5/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 12.0s | 73.5/100 | 6.1 |

Failure modes observed: decorative_uncertainty.
