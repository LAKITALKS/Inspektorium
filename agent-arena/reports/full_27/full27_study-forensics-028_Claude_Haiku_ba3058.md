# Forensic Dossier: Study Forensics: NAD+ restoration reverses Alzheimer's in mice

**Run ID:** `full27_study-forensics-028_Claude_Haiku_ba3058`  
**Task:** study-forensics-028 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T18:01:02.640725+00:00  
**Task Family:** mechanism_vs_evidence  
**Trap Type:** animal_to_human_overreach  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **69.8/100** (margin: 0.0)
**Failure modes:** unsupported_intermediate_step, unused_assumption
**Forensic flags:** 3
**Consistency findings:** 5
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 30.0/30 | 0.7/8 | 4.8/8 | 3.0/6 | 3.9/6 | 5.2/6 | 5.6/8 | 8.0/8 | 0.0/10 | 8.5/10 | **69.8/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `mechanism_vs_evidence` [+] (gold: `mechanism_vs_evidence`)
**Finding Recall:** 100%
**Matched Findings:** mechanism_not_demonstrated, conclusion_exceeds_results
**Extra Findings:** cautious_scope_control, none_or_minor, unsupported_generalization, decorative_uncertainty, correlation_as_causation

## Reasoning Integrity Audit

### Claude Haiku
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 6

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
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 6
  - Note: Reasoning graph confirms conclusion grounding

**Structural Reasoning:** 4.8/8
  - (+) `steps[3]`: "4. HEDGE ANALYSIS: The text includes cautious language ('suggest,' 'could,' 'clinical trials to see if the approach will"
    _Most informative reasoning step_
  - Note: 6 reasoning steps
  - Note: Low step utility: 0/6 steps contribute

**Assumption Discipline:** 3.0/6
  - (+) `assumptions[4]`: "Genetically engineered mouse models of Alzheimer's do not fully recapitulate human disease complexity, comorbidities, or"
    _Most substantive assumption_
  - (-) `assumptions[1]`: "Memory performance was measured in mice using standard behavioral tests (e.g., Morris water maze), not human cognitive o"
    _Declared but unused in reasoning_
  - (-) `assumptions[2]`: "Brain damage repair was assessed via histology or imaging in mouse brains, not human neuroimaging or autopsy"
    _Declared but unused in reasoning_
  - Note: 6/6 substantive assumptions
  - Note: Many assumptions (6)

**Uncertainty Handling:** 3.9/6
  - (+) `uncertainties[0]`: "Whether the mouse model used is a standard transgenic (e.g., APP/PS1) or a newer model; some newer models may better rec"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.88"
    _Stated confidence level_
  - Note: 4 uncertainties (4 substantive)
  - Note: Confidence 0.88

**Alternative Hypothesis Quality:** 5.2/6
  - (+) `alternative_hypotheses[0]`: "SOLID: If the study included human biomarker data (e.g., CSF NAD+ levels correlating with cognitive decline) or a small "
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 1/2 include rejection reasoning

**Self Monitoring Quality:** 5.6/8
  - (+) `self_check[2]`: "Is the hedging language sufficient? No. Hedges acknowledge uncertainty but do not provide evidence. The text says 'could"
    _Most substantive self-verification step_
  - Note: 5 self-check items
  - Note: Self-check quality: 0 deep, 5 arithmetic, 0 fluff

**Mechanism Quality:** 0.0/10
  - Note: Neither names concept nor explains mechanism

**Communication Efficiency:** 8.5/10
  - Note: Signal density: 0.72, 696 words

**Insight Depth:** 8.0/8
  - (+) `(output text)`: "ke pathology. this is tier 2 (animal models). 2. conclusion tier identif"
    _Insight 'animal model' matched (exact)_
  - Note: Key insights: 2 full / 2


## Failure Analysis

### Claude Haiku

**MODERATE:**
- **Unsupported Intermediate Step** `[MEDIUM CONFIDENCE]`: No reasoning step is load-bearing — final answer lacks traceable derivation
  - `final_answer`: "mechanism_vs_evidence"
  - _Impacts: support_strength, structural_reasoning_

**STYLISTIC:**
- **Unused Assumption** `[HEURISTIC]`: Assumption 'Memory performance was measured in mice using standard behav...' is declared but not referenced in reasoning
  - `assumptions[1]`: "Memory performance was measured in mice using standard behavioral tests (e.g., Morris water maze), n"
  - _Impacts: assumption_discipline_
- **Unused Assumption** `[HEURISTIC]`: Assumption 'Brain damage repair was assessed via histology or imaging in...' is declared but not referenced in reasoning
  - `assumptions[2]`: "Brain damage repair was assessed via histology or imaging in mouse brains, not human neuroimaging or"
  - _Impacts: assumption_discipline_
- **Unused Assumption** `[HEURISTIC]`: Assumption 'The NAD+ restoration compound was tested in mice; its pharma...' is declared but not referenced in reasoning
  - `assumptions[3]`: "The NAD+ restoration compound was tested in mice; its pharmacokinetics, safety, and efficacy in huma"
  - _Impacts: assumption_discipline_
- **Unused Assumption** `[HEURISTIC]`: Assumption 'The text reports the researchers' own framing of the implica...' is declared but not referenced in reasoning
  - `assumptions[5]`: "The text reports the researchers' own framing of the implications, not independent clinical validati"
  - _Impacts: assumption_discipline_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/13 content words)
  - `key_claims[0]`: "The study demonstrates NAD+ depletion and memory loss in mice, and NAD+ restoration reverses both in"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/12 content words)
  - `key_claims[1]`: "The text extrapolates from mouse memory recovery to potential human therapeutic benefit without huma"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/11 content words)
  - `key_claims[2]`: "Cautious language ('suggest,' 'could,' 'clinical trials to see if') is present but does not resolve "
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/12 content words)
  - `key_claims[3]`: "The researchers appropriately call for clinical trials, implicitly acknowledging that animal data ar"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 2 is stated without rejection reasoning
  - `alternative_hypotheses[1]`: "OVERCLAIM: If the text had used language like 'restores memory in Alzheimer's patients' or 'a new cu"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 15963ms

**Final Answer:** mechanism_vs_evidence

**Confidence:** 0.88

**Assumptions:**
- The study used genetically engineered mice with Alzheimer's-like pathology, not human patients
- Memory performance was measured in mice using standard behavioral tests (e.g., Morris water maze), not human cognitive outcomes
- Brain damage repair was assessed via histology or imaging in mouse brains, not human neuroimaging or autopsy
- The NAD+ restoration compound was tested in mice; its pharmacokinetics, safety, and efficacy in humans are unknown
- Genetically engineered mouse models of Alzheimer's do not fully recapitulate human disease complexity, comorbidities, or heterogeneity
- The text reports the researchers' own framing of the implications, not independent clinical validation

**Reasoning Steps:**
1. 1. EVIDENCE TIER IDENTIFICATION: The study is conducted in genetically engineered mice with Alzheimer's-like pathology. This is Tier 2 (animal models).
2. 2. CONCLUSION TIER IDENTIFICATION: The text implies human therapeutic benefit ('boosting NAD+ could move Alzheimer's therapy beyond slowing decline toward meaningful recovery') and calls for clinical trials. This is Tier 5 (human therapeutic).
3. 3. BRIDGE STEP DETECTION: A large gap exists between animal evidence and human therapeutic claims. The text does not present human data, biomarker studies, or mechanistic evidence that would bridge this gap.
4. 4. HEDGE ANALYSIS: The text includes cautious language ('suggest,' 'could,' 'clinical trials to see if the approach will translate'). However, these hedges acknowledge the gap without closing it. The core claim—that NAD+ restoration offers therapeutic potential for human Alzheimer's—remains unsupported by human evidence.
5. 5. RHETORICAL TONE: The language is analytical rather than promotional. Terms like 'suggest' and 'could' indicate tentativeness. There is no use of 'breakthrough,' 'confirms,' or 'reduces risk' as fact. The researchers are appropriately calling for further work.
6. 6. CLASSIFICATION DECISION: The primary problem is not inflated rhetoric but an evidence-tier mismatch. The text makes a modest, hedged claim about human therapeutic potential based solely on animal data. This is mechanism_vs_evidence, not overclaim.

**Key Claims:**
- The study demonstrates NAD+ depletion and memory loss in mice, and NAD+ restoration reverses both in the same animal model.
- The text extrapolates from mouse memory recovery to potential human therapeutic benefit without human evidence.
- Cautious language ('suggest,' 'could,' 'clinical trials to see if') is present but does not resolve the evidence-tier gap.
- The researchers appropriately call for clinical trials, implicitly acknowledging that animal data are insufficient for human claims.

**Alternative Hypotheses:**
- SOLID: If the study included human biomarker data (e.g., CSF NAD+ levels correlating with cognitive decline) or a small human pilot trial, the evidence tier would be higher and the conclusion more defensible. The text does not mention such data.
- OVERCLAIM: If the text had used language like 'restores memory in Alzheimer's patients' or 'a new cure for Alzheimer's,' the primary issue would be rhetorical inflation. The actual language is more cautious.

**Uncertainties:**
- Whether the mouse model used is a standard transgenic (e.g., APP/PS1) or a newer model; some newer models may better recapitulate human pathology, but this does not change the fundamental tier gap.
- Whether the study measured only behavioral recovery or also assessed underlying neuropathology (amyloid, tau, neuroinflammation); either way, mouse data do not translate directly to human benefit.
- Whether the researchers' call for clinical trials reflects genuine optimism or standard scientific practice; either way, the current evidence does not support human therapeutic claims.
- The specific NAD+ restoration compound used; if it is a known drug with prior human safety data, the translational risk is lower, but efficacy in humans remains untested.

**Self-Verification:**
- Did I overstate the problem? No. The evidence is genuinely from animals, and the conclusion is genuinely about human therapy. This is a real tier mismatch.
- Did I miss a bridge? I checked for human biomarker data, pilot trials, or mechanistic evidence linking NAD+ to human Alzheimer's. The text does not mention any. The bridge is absent.
- Is the hedging language sufficient? No. Hedges acknowledge uncertainty but do not provide evidence. The text says 'could' and 'suggest,' which is appropriate, but it still implies human benefit without human data.
- Is this overclaim or mechanism_vs_evidence? The text is analytical and cautious, not promotional. The primary issue is the evidence tier, not rhetorical inflation. Mechanism_vs_evidence is correct.
- Did I assume the mouse model is poor? No. I noted that even good mouse models do not fully recapitulate human disease. This is a standard limitation, not an assumption I imposed.

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.7/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 3.0/6 `#####.....`
- Uncertainty Handling: 3.9/6 `######....`
- Alternative Hypothesis Quality: 5.2/6 `########..`
- Self Monitoring Quality: 5.6/8 `#######...`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 0.0/10 `..........`
- Communication Efficiency: 8.5/10 `########..`


## Final Verdict

**Solo run: Claude Haiku** scored **69.8/100**.

**Best per dimension:**
- Correctness: Claude Haiku (30.0/30)
- Support Strength: Claude Haiku (0.7/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (3.0/6)
- Uncertainty Handling: Claude Haiku (3.9/6)
- Alternative Hypothesis Quality: Claude Haiku (5.2/6)
- Self Monitoring Quality: Claude Haiku (5.6/8)
- Insight Depth: Claude Haiku (8.0/8)
- Mechanism Quality: Claude Haiku (0.0/10)
- Communication Efficiency: Claude Haiku (8.5/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 16.0s | 69.8/100 | 4.4 |

Failure modes observed: unsupported_intermediate_step, unused_assumption.
