# Forensic Dossier: Study Forensics: AI instruction outperforms human teachers

**Run ID:** `full27_study-forensics-025_Claude_Sonnet_e5e861`  
**Task:** study-forensics-025 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T17:01:34.683469+00:00  
**Task Family:** overclaim  
**Trap Type:** media_inflated_overclaim  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Sonnet
**Winner:** Claude Sonnet — **69.4/100** (margin: 0.0)
**Failure modes:** named_not_explained, unsupported_intermediate_step
**Forensic flags:** 4
**Consistency findings:** 8
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Sonnet | 30.0/30 | 0.7/8 | 4.8/8 | 3.9/6 | 3.9/6 | 5.0/6 | 1.6/8 | 8.0/8 | 1.5/10 | 10.0/10 | **69.4/100** |

## Study Forensics Audit

### Claude Sonnet

**Classification:** `overclaim` [+] (gold: `overclaim`)
**Finding Recall:** 100%
**Matched Findings:** conclusion_exceeds_results, unsupported_generalization
**Extra Findings:** cautious_scope_control, correlation_as_causation

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

**Support Strength:** 1.2/8
  - (+) `final_answer`: "overclaim"
    _Conclusion grounded by reasoning chain_
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 5
  - Note: Reasoning graph confirms conclusion grounding

**Structural Reasoning:** 4.8/8
  - (+) `steps[1]`: "Noted conclusion implies broad educational policy changes ('making human teachers obsolete', 'data-backed reality for al"
    _Most informative reasoning step_
  - Note: 5 reasoning steps
  - Note: Low step utility: 0/5 steps contribute

**Assumption Discipline:** 3.9/6
  - (+) `assumptions[1]`: "The 65% test score improvement and 2x learning effect claims are from limited trials"
    _Most substantive assumption_
  - Note: 3/3 substantive assumptions

**Uncertainty Handling:** 3.9/6
  - (+) `uncertainties[0]`: "Exact methodology and sample sizes of the pilot programs"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.92"
    _Stated confidence level_
  - Note: 3 uncertainties (3 substantive)
  - Note: Confidence 0.92

**Alternative Hypothesis Quality:** 5.0/6
  - (+) `alternative_hypotheses[1]`: "Could be correlation_vs_causation if emphasizing test score improvements"
    _Most substantive alternative hypothesis_
  - Note: 3 alternative hypotheses considered
  - Note: 1/3 include rejection reasoning

**Self Monitoring Quality:** 1.6/8
  - (+) `self_check[0]`: "Confirmed this is overclaim rather than mechanism_vs_evidence - the issue is scope of conclusions not evidence tier mism"
    _Most substantive self-verification step_
  - (-) `self_check[1]`: "Verified I'm not overflagging - the language is genuinely overreaching"
    _Fluff self-check_
  - Note: 3 self-check items
  - Note: Self-check quality: 0 deep, 1 arithmetic, 2 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.79, 217 words

**Insight Depth:** 4.0/8
  - (?) `(not found)`: "Missing: no methodology"
    _Insight 'no methodology' not found_
  - Note: Key insights: 1 full / 2


## Failure Analysis

### Claude Sonnet

**MODERATE:**
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
  - `key_claims[0]`: "Pilot studies show promise but cannot support claims of universal teacher obsolescence"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/8 content words)
  - `key_claims[1]`: "Specific performance metrics (65%, 2x) lack proper context and caveats"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/7 content words)
  - `key_claims[2]`: "Generalization from limited subjects/contexts to 'all subjects' is unsupported"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/8 content words)
  - `key_claims[3]`: "Strong causal claims about educational transformation exceed evidence base"
- **[WARN]** `[HEURISTIC]` `claim_step_alignment`: Key claim 2 not well supported in reasoning steps (1/8 content words found)
  - `key_claims[1]`: "Specific performance metrics (65%, 2x) lack proper context and caveats"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "Could be mechanism_vs_evidence if focusing on AI technology development"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 2 is stated without rejection reasoning
  - `alternative_hypotheses[1]`: "Could be correlation_vs_causation if emphasizing test score improvements"
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "overclaim"


## Agent Profiles

### Claude Sonnet (claude-sonnet-4-20250514)
**Parse OK:** True | **Latency:** 11965ms

**Final Answer:** overclaim

**Confidence:** 0.92

**Assumptions:**
- The pilot programs mentioned are small-scale studies
- The 65% test score improvement and 2x learning effect claims are from limited trials
- The article is making broad policy/implementation claims based on early evidence

**Reasoning Steps:**
1. Identified evidence as pilot programs (limited human studies)
2. Noted conclusion implies broad educational policy changes ('making human teachers obsolete', 'data-backed reality for all subjects')
3. Found multiple overclaims: 65% improvement without context, 2x effectiveness claim, generalization across all subjects
4. Detected unsupported leap from limited pilots to universal educational transformation
5. Recognized strong causal language ('dismantled', 'obsolete') exceeding pilot study evidence

**Key Claims:**
- Pilot studies show promise but cannot support claims of universal teacher obsolescence
- Specific performance metrics (65%, 2x) lack proper context and caveats
- Generalization from limited subjects/contexts to 'all subjects' is unsupported
- Strong causal claims about educational transformation exceed evidence base

**Alternative Hypotheses:**
- Could be mechanism_vs_evidence if focusing on AI technology development
- Could be correlation_vs_causation if emphasizing test score improvements
- Considered solid but rejected due to sweeping generalizations

**Uncertainties:**
- Exact methodology and sample sizes of the pilot programs
- Whether the 65% and 2x claims are accurately reported
- Scope and duration of the cited studies

**Self-Verification:**
- Confirmed this is overclaim rather than mechanism_vs_evidence - the issue is scope of conclusions not evidence tier mismatch
- Verified I'm not overflagging - the language is genuinely overreaching
- Double-checked that pilot programs constitute limited human evidence

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.7/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 3.9/6 `######....`
- Uncertainty Handling: 3.9/6 `######....`
- Alternative Hypothesis Quality: 5.0/6 `########..`
- Self Monitoring Quality: 1.6/8 `##........`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Sonnet** scored **69.4/100**.

**Best per dimension:**
- Correctness: Claude Sonnet (30.0/30)
- Support Strength: Claude Sonnet (0.7/8)
- Structural Reasoning: Claude Sonnet (4.8/8)
- Assumption Discipline: Claude Sonnet (3.9/6)
- Uncertainty Handling: Claude Sonnet (3.9/6)
- Alternative Hypothesis Quality: Claude Sonnet (5.0/6)
- Self Monitoring Quality: Claude Sonnet (1.6/8)
- Insight Depth: Claude Sonnet (8.0/8)
- Mechanism Quality: Claude Sonnet (1.5/10)
- Communication Efficiency: Claude Sonnet (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Sonnet | 12.0s | 69.4/100 | 5.8 |

Failure modes observed: named_not_explained, unsupported_intermediate_step.
