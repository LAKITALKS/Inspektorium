# Forensic Dossier: Study Forensics: NAD+ restoration reverses Alzheimer's in mice

**Run ID:** `mechfix_study-forensics-028_Claude_Sonnet_0cf11c`  
**Task:** study-forensics-028 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T16:41:42.201176+00:00  
**Task Family:** mechanism_vs_evidence  
**Trap Type:** animal_to_human_overreach  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Sonnet
**Winner:** Claude Sonnet — **66.5/100** (margin: 0.0)
**Failure modes:** decorative_self_check, decorative_uncertainty, unsupported_conclusion, unsupported_intermediate_step
**Forensic flags:** 3
**Consistency findings:** 4
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Sonnet | 30.0/30 | 0.0/8 | 4.8/8 | 4.8/6 | 3.3/6 | 5.2/6 | 0.4/8 | 8.0/8 | 0.0/10 | 10.0/10 | **66.5/100** |

## Study Forensics Audit

### Claude Sonnet

**Classification:** `mechanism_vs_evidence` [+] (gold: `mechanism_vs_evidence`)
**Finding Recall:** 100%
**Matched Findings:** mechanism_not_demonstrated, conclusion_exceeds_results
**Extra Findings:** cautious_scope_control

## Reasoning Integrity Audit

### Claude Sonnet
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 5

## Mechanism Analysis

### Claude Sonnet
| Aspect | Status |
|--------|--------|
| Concept named | :x: none |
| Mechanism described | :x: (0 sentence(s)) |
| Grounded to case | :x: (0 sentence(s)) |

**Missing:** concept not named, mechanism not described, mechanism not grounded to case data

## Grounding Audit

### Claude Sonnet
Conclusion claims: 1
- Direct support: 0
- Indirect support: 0
- Unsupported: 1
- Contradicted: 0

**Unsupported claims:**
- "mechanism_vs_evidence"


## Forensic Flags

### Claude Sonnet

- **[MODERATE]** `weak_mechanism`: Correct answer but weak mechanism explanation — answer may not generalize
  - `final_answer`: "mechanism_vs_evidence"
- **[MAJOR]** `unsupported_leap`: Correct answer with weak support chain — final answer may be an unsupported leap
- **[MODERATE]** `unsupported_conclusion_claims`: 1/1 conclusion claims lack step support
  - `final_answer`: "mechanism_vs_evidence"


## Evidence Map

### Claude Sonnet

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
  - (+) `steps[1]`: "Identified conclusion tier: text implies human therapeutic potential ('boosting NAD+ could move Alzheimer's therapy beyo"
    _Most informative reasoning step_
  - Note: 5 reasoning steps
  - Note: Low step utility: 0/5 steps contribute

**Assumption Discipline:** 4.8/6
  - (+) `assumptions[0]`: "The study was conducted in genetically engineered mouse models of Alzheimer's disease"
    _Most substantive assumption_
  - Note: 3/3 substantive assumptions

**Uncertainty Handling:** 3.3/6
  - (+) `uncertainties[1]`: "Whether additional human data exists that wasn't mentioned"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.9"
    _Stated confidence level_
  - (-) `uncertainties[0]`: "Exact wording of original research paper vs. this summary"
    _Listed but never addressed in reasoning_
  - (-) `uncertainties[1]`: "Whether additional human data exists that wasn't mentioned"
    _Listed but never addressed in reasoning_
  - Note: 2 uncertainties (2 substantive)
  - Note: 2 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 5.2/6
  - (+) `alternative_hypotheses[0]`: "Could be classified as 'solid' if focusing only on the mouse study results themselves"
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 1/2 include rejection reasoning

**Self Monitoring Quality:** 0.4/8
  - (+) `self_check[1]`: "Verified that hedging language doesn't resolve the evidence tier mismatch"
    _Most substantive self-verification step_
  - (-) `self_check[0]`: "Confirmed this is animal-to-human bridge without supporting human data"
    _Fluff self-check_
  - Note: 3 self-check items
  - Note: Self-check quality: 0 deep, 0 arithmetic, 3 fluff

**Mechanism Quality:** 0.0/10
  - Note: Neither names concept nor explains mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.76, 220 words

**Insight Depth:** 8.0/8
  - Note: Key insights: 2 full / 2


## Failure Analysis

### Claude Sonnet

**MODERATE:**
- **Unsupported Conclusion** `[MEDIUM CONFIDENCE]`: Final answer lacks load-bearing or supporting step grounding
  - `final_answer`: "mechanism_vs_evidence"
  - _Impacts: support_strength_
- **Unsupported Intermediate Step** `[MEDIUM CONFIDENCE]`: No reasoning step is load-bearing — final answer lacks traceable derivation
  - `final_answer`: "mechanism_vs_evidence"
  - _Impacts: support_strength, structural_reasoning_

**MINOR:**
- **Decorative Self Check** `[HEURISTIC]`: All 3 self-checks appear to be fluff — no substantive verification
  - `self_check[0]`: "Confirmed this is animal-to-human bridge without supporting human data"
  - _Impacts: self_monitoring_quality_

**STYLISTIC:**
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Exact wording of original research paper vs. this summary...' is listed but not addressed
  - `uncertainties[0]`: "Exact wording of original research paper vs. this summary"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether additional human data exists that wasn't mentioned...' is listed but not addressed
  - `uncertainties[1]`: "Whether additional human data exists that wasn't mentioned"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Sonnet

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/9 content words)
  - `key_claims[0]`: "Animal study shows NAD+ restoration can reverse Alzheimer's symptoms in mice"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/6 content words)
  - `key_claims[1]`: "Text implies this could translate to meaningful human therapy"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (1/7 content words)
  - `key_claims[2]`: "No direct human evidence is presented to support therapeutic claims"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "Could be classified as 'solid' if focusing only on the mouse study results themselves"


## Agent Profiles

### Claude Sonnet (claude-sonnet-4-20250514)
**Parse OK:** True | **Latency:** 10910ms

**Final Answer:** mechanism_vs_evidence

**Confidence:** 0.9

**Assumptions:**
- The study was conducted in genetically engineered mouse models of Alzheimer's disease
- The treatment showed efficacy in reversing cognitive deficits in these mice
- The researchers are proposing human clinical applications based on animal data

**Reasoning Steps:**
1. Identified evidence tier: animal studies in genetically engineered mice
2. Identified conclusion tier: text implies human therapeutic potential ('boosting NAD+ could move Alzheimer's therapy beyond slowing decline toward meaningful recovery')
3. Checked for bridge support: while researchers call for clinical trials (acknowledging the gap), the text still implies therapeutic potential for humans based solely on mouse data
4. Evaluated hedging: phrases like 'could' and 'suggest' acknowledge uncertainty but don't eliminate the evidence-tier mismatch
5. The leap from mouse efficacy to human therapeutic implications represents a classic mechanism vs evidence issue

**Key Claims:**
- Animal study shows NAD+ restoration can reverse Alzheimer's symptoms in mice
- Text implies this could translate to meaningful human therapy
- No direct human evidence is presented to support therapeutic claims

**Alternative Hypotheses:**
- Could be classified as 'solid' if focusing only on the mouse study results themselves
- Might be 'overclaim' but the hedging language prevents this classification

**Uncertainties:**
- Exact wording of original research paper vs. this summary
- Whether additional human data exists that wasn't mentioned

**Self-Verification:**
- Confirmed this is animal-to-human bridge without supporting human data
- Verified that hedging language doesn't resolve the evidence tier mismatch
- Double-checked that I'm not overflagging a legitimately cautious report

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 4.8/6 `########..`
- Uncertainty Handling: 3.3/6 `#####.....`
- Alternative Hypothesis Quality: 5.2/6 `########..`
- Self Monitoring Quality: 0.4/8 `..........`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 0.0/10 `..........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Sonnet** scored **66.5/100**.

**Best per dimension:**
- Correctness: Claude Sonnet (30.0/30)
- Support Strength: Claude Sonnet (0.0/8)
- Structural Reasoning: Claude Sonnet (4.8/8)
- Assumption Discipline: Claude Sonnet (4.8/6)
- Uncertainty Handling: Claude Sonnet (3.3/6)
- Alternative Hypothesis Quality: Claude Sonnet (5.2/6)
- Self Monitoring Quality: Claude Sonnet (0.4/8)
- Insight Depth: Claude Sonnet (8.0/8)
- Mechanism Quality: Claude Sonnet (0.0/10)
- Communication Efficiency: Claude Sonnet (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Sonnet | 10.9s | 66.5/100 | 6.1 |

Failure modes observed: decorative_self_check, decorative_uncertainty, unsupported_conclusion, unsupported_intermediate_step.
