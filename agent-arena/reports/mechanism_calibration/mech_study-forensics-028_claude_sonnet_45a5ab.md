# Forensic Dossier: Study Forensics: NAD+ restoration reverses Alzheimer's in mice

**Run ID:** `mech_study-forensics-028_claude_sonnet_45a5ab`  
**Task:** study-forensics-028 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-06T15:43:44.513711+00:00  
**Task Family:** mechanism_vs_evidence  
**Trap Type:** animal_to_human_overreach  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Sonnet
**Winner:** Claude Sonnet — **68.6/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, unsupported_conclusion, unsupported_intermediate_step, unused_assumption
**Forensic flags:** 3
**Consistency findings:** 8
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Sonnet | 30.0/30 | 0.0/8 | 4.8/8 | 2.9/6 | 3.6/6 | 4.5/6 | 4.8/8 | 8.0/8 | 0.0/10 | 10.0/10 | **68.6/100** |

## Study Forensics Audit

### Claude Sonnet

**Classification:** `mechanism_vs_evidence` [+] (gold: `mechanism_vs_evidence`)
**Finding Recall:** 100%
**Matched Findings:** mechanism_not_demonstrated, conclusion_exceeds_results
**Extra Findings:** cautious_scope_control, none_or_minor

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
  - (+) `steps[2]`: "Observed that researchers make claims about potential human therapy ('boosting NAD+ could move Alzheimer's therapy beyon"
    _Most informative reasoning step_
  - Note: 5 reasoning steps
  - Note: Low step utility: 0/5 steps contribute

**Assumption Discipline:** 2.9/6
  - (+) `assumptions[0]`: "The study was conducted in genetically engineered mice with Alzheimer's disease"
    _Most substantive assumption_
  - (-) `assumptions[1]`: "NAD+ restoration was achieved through a specific compound"
    _Declared but unused in reasoning_
  - (-) `assumptions[2]`: "Memory performance was measured using standard behavioral tests"
    _Declared but unused in reasoning_
  - Note: 4/4 substantive assumptions
  - Note: 2 unused assumption(s)

**Uncertainty Handling:** 3.6/6
  - (+) `uncertainties[0]`: "Whether the researchers made more cautious statements in the original paper that weren't included in this summary"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.82"
    _Stated confidence level_
  - (-) `uncertainties[0]`: "Whether the researchers made more cautious statements in the original paper that weren't included in this summary"
    _Listed but never addressed in reasoning_
  - Note: 3 uncertainties (3 substantive)
  - Note: 1 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 4.5/6
  - (+) `alternative_hypotheses[1]`: "overclaim - the therapeutic claims might be considered too strong given animal-only evidence"
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 2/2 genuinely diverse alternatives

**Self Monitoring Quality:** 4.8/8
  - (+) `self_check[3]`: "The key issue is the confident therapeutic framing ('could move therapy beyond slowing decline') based on animal evidenc"
    _Most substantive self-verification step_
  - Note: 4 self-check items
  - Note: Self-check quality: 0 deep, 4 arithmetic, 0 fluff

**Mechanism Quality:** 0.0/10
  - Note: Neither names concept nor explains mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.75, 279 words

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

**STYLISTIC:**
- **Unused Assumption** `[HEURISTIC]`: Assumption 'NAD+ restoration was achieved through a specific compound...' is declared but not referenced in reasoning
  - `assumptions[1]`: "NAD+ restoration was achieved through a specific compound"
  - _Impacts: assumption_discipline_
- **Unused Assumption** `[HEURISTIC]`: Assumption 'Memory performance was measured using standard behavioral te...' is declared but not referenced in reasoning
  - `assumptions[2]`: "Memory performance was measured using standard behavioral tests"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether the researchers made more cautious statements in the...' is listed but not addressed
  - `uncertainties[0]`: "Whether the researchers made more cautious statements in the original paper that weren't included in"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Sonnet

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/12 content words)
  - `key_claims[0]`: "Animal study shows NAD+ restoration can repair brain damage and restore memory in Alzheimer's mice"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/6 content words)
  - `key_claims[1]`: "Researchers suggest this could lead to recovery-focused human therapies"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (1/7 content words)
  - `key_claims[2]`: "The mechanism identified in mice is being proposed as relevant to human treatment"
- **[WARN]** `[HEURISTIC]` `unused_assumption`: Assumption 2 appears unused in reasoning or answer
  - `assumptions[1]`: "NAD+ restoration was achieved through a specific compound"
- **[WARN]** `[HEURISTIC]` `unused_assumption`: Assumption 3 appears unused in reasoning or answer
  - `assumptions[2]`: "Memory performance was measured using standard behavioral tests"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 1 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[0]`: "Whether the researchers made more cautious statements in the original paper that weren't included in"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "solid - researchers do call for clinical trials showing appropriate caution"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 2 is stated without rejection reasoning
  - `alternative_hypotheses[1]`: "overclaim - the therapeutic claims might be considered too strong given animal-only evidence"


## Agent Profiles

### Claude Sonnet (claude-sonnet-4-20250514)
**Parse OK:** True | **Latency:** 12710ms

**Final Answer:** mechanism_vs_evidence

**Confidence:** 0.82

**Assumptions:**
- The study was conducted in genetically engineered mice with Alzheimer's disease
- NAD+ restoration was achieved through a specific compound
- Memory performance was measured using standard behavioral tests
- The researchers are proposing translation to human clinical trials

**Reasoning Steps:**
1. Identified that the core findings come from mouse studies with genetically engineered Alzheimer's models
2. Noted that the text describes a clear mechanism (NAD+ disruption affecting brain energy balance)
3. Observed that researchers make claims about potential human therapy ('boosting NAD+ could move Alzheimer's therapy beyond slowing decline toward meaningful recovery')
4. Recognized that the leap from mouse model success to human therapeutic potential represents mechanism vs. evidence issue
5. Confirmed that while researchers appropriately call for clinical trials, they still make forward-looking therapeutic claims based solely on animal evidence

**Key Claims:**
- Animal study shows NAD+ restoration can repair brain damage and restore memory in Alzheimer's mice
- Researchers suggest this could lead to recovery-focused human therapies
- The mechanism identified in mice is being proposed as relevant to human treatment

**Alternative Hypotheses:**
- solid - researchers do call for clinical trials showing appropriate caution
- overclaim - the therapeutic claims might be considered too strong given animal-only evidence

**Uncertainties:**
- Whether the researchers made more cautious statements in the original paper that weren't included in this summary
- The exact strength of the therapeutic claims in the original context
- Whether this represents standard scientific communication for preclinical research

**Self-Verification:**
- Verified that the issue is specifically about applying animal mechanisms to human therapeutic potential
- Confirmed that while clinical trials are mentioned, therapeutic claims are still made
- Checked that I'm not overflagging normal scientific progression from animal to human studies
- The key issue is the confident therapeutic framing ('could move therapy beyond slowing decline') based on animal evidence alone

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 2.9/6 `####......`
- Uncertainty Handling: 3.6/6 `######....`
- Alternative Hypothesis Quality: 4.5/6 `#######...`
- Self Monitoring Quality: 4.8/8 `######....`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 0.0/10 `..........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Sonnet** scored **68.6/100**.

**Best per dimension:**
- Correctness: Claude Sonnet (30.0/30)
- Support Strength: Claude Sonnet (0.0/8)
- Structural Reasoning: Claude Sonnet (4.8/8)
- Assumption Discipline: Claude Sonnet (2.9/6)
- Uncertainty Handling: Claude Sonnet (3.6/6)
- Alternative Hypothesis Quality: Claude Sonnet (4.5/6)
- Self Monitoring Quality: Claude Sonnet (4.8/8)
- Insight Depth: Claude Sonnet (8.0/8)
- Mechanism Quality: Claude Sonnet (0.0/10)
- Communication Efficiency: Claude Sonnet (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Sonnet | 12.7s | 68.6/100 | 5.4 |

Failure modes observed: decorative_uncertainty, unsupported_conclusion, unsupported_intermediate_step, unused_assumption.
