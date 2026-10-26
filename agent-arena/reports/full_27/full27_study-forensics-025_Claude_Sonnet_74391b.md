# Forensic Dossier: Study Forensics: AI instruction outperforms human teachers

**Run ID:** `full27_study-forensics-025_Claude_Sonnet_74391b`  
**Task:** study-forensics-025 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T17:58:31.450818+00:00  
**Task Family:** overclaim  
**Trap Type:** media_inflated_overclaim  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Sonnet
**Winner:** Claude Sonnet — **70.1/100** (margin: 0.0)
**Failure modes:** named_not_explained, unsupported_conclusion, unsupported_intermediate_step
**Forensic flags:** 4
**Consistency findings:** 6
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Sonnet | 30.0/30 | 0.0/8 | 4.8/8 | 3.9/6 | 3.9/6 | 5.2/6 | 2.8/8 | 8.0/8 | 1.5/10 | 10.0/10 | **70.1/100** |

## Study Forensics Audit

### Claude Sonnet

**Classification:** `overclaim` [+] (gold: `overclaim`)
**Finding Recall:** 100%
**Matched Findings:** conclusion_exceeds_results, unsupported_generalization

## Reasoning Integrity Audit

### Claude Sonnet
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 5

## Mechanism Analysis

### Claude Sonnet
| Aspect | Status |
|--------|--------|
| Concept named | :white_check_mark: effect |
| Mechanism described | :x: (0 sentence(s)) |
| Grounded to case | :x: (0 sentence(s)) |

**Missing:** mechanism not described, mechanism not grounded to case data

## Grounding Audit

### Claude Sonnet
Conclusion claims: 1
- Direct support: 0
- Indirect support: 0
- Unsupported: 1
- Contradicted: 0

**Unsupported claims:**
- "overclaim"


## Forensic Flags

### Claude Sonnet

- **[MODERATE]** `weak_mechanism`: Correct answer but weak mechanism explanation — answer may not generalize
  - `final_answer`: "overclaim"
- **[MAJOR]** `unsupported_leap`: Correct answer with weak support chain — final answer may be an unsupported leap
- **[MODERATE]** `unsupported_conclusion_claims`: 1/1 conclusion claims lack step support
  - `final_answer`: "overclaim"
- **[MODERATE]** `ungrounded_mechanism`: Mechanism named/described but not connected to case-specific data
  - `(mechanism analysis)`: "effect"


## Evidence Map

### Claude Sonnet

**Correctness:** 30.0/30
  - (+) `final_answer`: "overclaim"
    _Agent's answer for correctness check_
  - Note: Exact match

**Support Strength:** 0.0/8
  - (-) `final_answer`: "overclaim"
    _Conclusion not supported by steps_
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 5
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[2]`: "Detected promotional language: 'rapidly making obsolete', 'data-backed reality for all subjects'"
    _Most informative reasoning step_
  - Note: 5 reasoning steps
  - Note: Low step utility: 0/5 steps contribute

**Assumption Discipline:** 3.9/6
  - (+) `assumptions[1]`: "The 65% test score improvement and 2x learning effect claims lack proper controls"
    _Most substantive assumption_
  - Note: 3/3 substantive assumptions

**Uncertainty Handling:** 3.9/6
  - (+) `uncertainties[1]`: "Whether the quantitative claims have any empirical basis"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.9"
    _Stated confidence level_
  - Note: 3 uncertainties (3 substantive)
  - Note: Confidence 0.9

**Alternative Hypothesis Quality:** 5.2/6
  - (+) `alternative_hypotheses[0]`: "mechanism_vs_evidence - if the text were more cautious but still implied broad applicability"
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 1/2 include rejection reasoning

**Self Monitoring Quality:** 2.8/8
  - (+) `self_check[0]`: "Confirmed this is overclaim rather than mechanism_vs_evidence because the text actively sells educational transformation"
    _Most substantive self-verification step_
  - (-) `self_check[1]`: "Verified the promotional language exceeds what pilot programs can support"
    _Fluff self-check_
  - Note: 3 self-check items
  - Note: Self-check quality: 0 deep, 2 arithmetic, 1 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.79, 212 words

**Insight Depth:** 4.0/8
  - (?) `(not found)`: "Missing: no methodology"
    _Insight 'no methodology' not found_
  - Note: Key insights: 1 full / 2


## Failure Analysis

### Claude Sonnet

**MODERATE:**
- **Unsupported Conclusion** `[MEDIUM CONFIDENCE]`: Final answer lacks load-bearing or supporting step grounding
  - `final_answer`: "overclaim"
  - _Impacts: support_strength_
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Names the phenomenon but does not explain the causal mechanism
  - `final_answer`: "overclaim"
  - _Impacts: mechanism_quality_
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Named concept(s) ['effect'] but mechanism not described
  - _Impacts: mechanism_quality, insight_depth_
- **Unsupported Intermediate Step** `[MEDIUM CONFIDENCE]`: No reasoning step is load-bearing — final answer lacks traceable derivation
  - `final_answer`: "overclaim"
  - _Impacts: support_strength, structural_reasoning_


## Consistency & Grounding Audit

### Claude Sonnet

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/10 content words)
  - `key_claims[0]`: "Text actively promotes AI as making teachers 'obsolete' based on limited pilot data"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/7 content words)
  - `key_claims[1]`: "Presents specific performance metrics (65%, 2x) as established facts"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/7 content words)
  - `key_claims[2]`: "Concludes AI instruction is 'data-backed reality for all subjects' - a sweeping generalization"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/10 content words)
  - `key_claims[3]`: "Uses promotional language that inflates pilot results into transformative educational policy"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 2 is stated without rejection reasoning
  - `alternative_hypotheses[1]`: "solid - if claims were limited to pilot program results only"
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "overclaim"


## Agent Profiles

### Claude Sonnet (claude-sonnet-4-20250514)
**Parse OK:** True | **Latency:** 10883ms

**Final Answer:** overclaim

**Confidence:** 0.9

**Assumptions:**
- The pilot programs mentioned are small-scale studies
- The 65% test score improvement and 2x learning effect claims lack proper controls
- The article is making broad policy conclusions from limited evidence

**Reasoning Steps:**
1. Identified evidence as pilot programs (limited human studies)
2. Found conclusion tier implies broad educational policy changes
3. Detected promotional language: 'rapidly making obsolete', 'data-backed reality for all subjects'
4. Noted specific quantitative claims (65%, 2x effect) presented as established facts
5. Recognized this as active selling of educational transformation beyond what pilot data can support

**Key Claims:**
- Text actively promotes AI as making teachers 'obsolete' based on limited pilot data
- Presents specific performance metrics (65%, 2x) as established facts
- Concludes AI instruction is 'data-backed reality for all subjects' - a sweeping generalization
- Uses promotional language that inflates pilot results into transformative educational policy

**Alternative Hypotheses:**
- mechanism_vs_evidence - if the text were more cautious but still implied broad applicability
- solid - if claims were limited to pilot program results only

**Uncertainties:**
- Exact methodology of the cited pilot programs
- Whether the quantitative claims have any empirical basis
- Scale and duration of the studies referenced

**Self-Verification:**
- Confirmed this is overclaim rather than mechanism_vs_evidence because the text actively sells educational transformation
- Verified the promotional language exceeds what pilot programs can support
- Did not overflag - the text makes genuinely inflated claims about educational policy

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 3.9/6 `######....`
- Uncertainty Handling: 3.9/6 `######....`
- Alternative Hypothesis Quality: 5.2/6 `########..`
- Self Monitoring Quality: 2.8/8 `###.......`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Sonnet** scored **70.1/100**.

**Best per dimension:**
- Correctness: Claude Sonnet (30.0/30)
- Support Strength: Claude Sonnet (0.0/8)
- Structural Reasoning: Claude Sonnet (4.8/8)
- Assumption Discipline: Claude Sonnet (3.9/6)
- Uncertainty Handling: Claude Sonnet (3.9/6)
- Alternative Hypothesis Quality: Claude Sonnet (5.2/6)
- Self Monitoring Quality: Claude Sonnet (2.8/8)
- Insight Depth: Claude Sonnet (8.0/8)
- Mechanism Quality: Claude Sonnet (1.5/10)
- Communication Efficiency: Claude Sonnet (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Sonnet | 10.9s | 70.1/100 | 6.4 |

Failure modes observed: named_not_explained, unsupported_conclusion, unsupported_intermediate_step.
