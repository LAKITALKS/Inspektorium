# Forensic Dossier: Study Forensics: Social media use and well-being

**Run ID:** `pilot_86f1a5b8`  
**Task:** study-forensics-001 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-06T08:18:57.805370+00:00  
**Task Family:** solid  
**Trap Type:** overflagging_solid_study  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** synthetic
**Winner:** synthetic — **71.8/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, named_not_explained, unsupported_intermediate_step
**Forensic flags:** 5
**Consistency findings:** 3
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| synthetic | 30.0/30 | 1.2/8 | 5.9/8 | 4.8/6 | 3.6/6 | 4.8/6 | 2.0/8 | 8.0/8 | 1.5/10 | 10.0/10 | **71.8/100** |

## Study Forensics Audit

### synthetic

**Classification:** `solid` [+] (gold: `solid`)
**Finding Recall:** 100%
**Matched Findings:** evidence_matches_claim, cautious_scope_control, none_or_minor
**Extra Findings:** unsupported_generalization, correlation_as_causation

## Reasoning Integrity Audit

### synthetic
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 5

## Mechanism Analysis

### synthetic
| Aspect | Status |
|--------|--------|
| Concept named | :white_check_mark: effect |
| Mechanism described | :x: (0 sentence(s)) |
| Grounded to case | :x: (0 sentence(s)) |

**Missing:** mechanism not described, mechanism not grounded to case data

## Grounding Audit

### synthetic
Conclusion claims: 3
- Direct support: 0
- Indirect support: 3
- Unsupported: 0
- Contradicted: 0


## Forensic Flags

### synthetic

- **[MODERATE]** `weak_mechanism`: Correct answer but weak mechanism explanation — answer may not generalize
  - `final_answer`: "This is a solid study. The randomised experimental design supports causal inference. The authors are"
- **[MAJOR]** `unsupported_leap`: Correct answer with weak support chain — final answer may be an unsupported leap
- **[MINOR]** `blind_spot`: Strong reasoning but weak self-monitoring — may miss own errors
- **[MODERATE]** `ungrounded_mechanism`: Mechanism named/described but not connected to case-specific data
  - `(mechanism analysis)`: "effect"
- **[MINOR]** `study_forensics_overflagging`: Agent raised extra findings in solid case: unsupported_generalization, correlation_as_causation


## Evidence Map

### synthetic

**Correctness:** 27.0/30
  - (+) `final_answer`: "This is a solid study. The randomised experimental design supports causal inference. The authors are careful not to over"
    _Agent's answer for correctness check_
  - Note: Contains expected answer

**Support Strength:** 1.2/8
  - (+) `final_answer`: "This is a solid study. The randomised experimental design supports causal inference. The authors are careful not to over"
    _Conclusion grounded by reasoning chain_
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 5
  - Note: Reasoning graph confirms conclusion grounding

**Structural Reasoning:** 5.9/8
  - (+) `steps[3]`: "The authors show cautious scope control by noting the study only covers college students and three platforms."
    _Most informative reasoning step_
  - Note: 5 reasoning steps
  - Note: Low step utility: 2/5 steps contribute

**Assumption Discipline:** 4.8/6
  - (+) `assumptions[1]`: "Self-report measures are adequate for depression and loneliness"
    _Most substantive assumption_
  - Note: 2/2 substantive assumptions

**Uncertainty Handling:** 3.6/6
  - (+) `uncertainties[0]`: "Self-report measures may be subject to social desirability bias"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.88"
    _Stated confidence level_
  - (-) `uncertainties[1]`: "Three-week timeframe may not capture long-term effects"
    _Listed but never addressed in reasoning_
  - Note: 2 uncertainties (2 substantive)
  - Note: 1 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 4.8/6
  - (+) `alternative_hypotheses[0]`: "Could there be a demand effect? Unlikely given objective usage data from screenshots."
    _Most substantive alternative hypothesis_
  - Note: 1 alternative hypotheses considered
  - Note: 1/1 include rejection reasoning

**Self Monitoring Quality:** 2.0/8
  - (+) `self_check[0]`: "Am I overflagging? No — the study design is genuinely strong and authors are cautious."
    _Most substantive self-verification step_
  - (-) `self_check[1]`: "Could I be missing a subtle issue? The sample size is modest but acknowledged."
    _Fluff self-check_
  - Note: 2 self-check items
  - Note: Self-check quality: 0 deep, 1 arithmetic, 1 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.68, 184 words

**Insight Depth:** 4.0/8
  - (+) `(output text)`: "this is a solid study. the randomised experimental design supports"
    _Insight 'randomised' matched (exact)_
  - (?) `(not found)`: "Missing: scope limitation"
    _Insight 'scope limitation' not found_
  - Note: Key insights: 1 full / 2


## Failure Analysis

### synthetic

**MODERATE:**
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Names the phenomenon but does not explain the causal mechanism
  - `final_answer`: "This is a solid study. The randomised experimental design supports causal inference. The authors are"
  - _Impacts: mechanism_quality_
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Named concept(s) ['effect'] but mechanism not described
  - _Impacts: mechanism_quality, insight_depth_
- **Unsupported Intermediate Step** `[MEDIUM CONFIDENCE]`: No reasoning step is load-bearing — final answer lacks traceable derivation
  - `final_answer`: "This is a solid study. The randomised experimental design supports causal inference. The authors are"
  - _Impacts: support_strength, structural_reasoning_

**STYLISTIC:**
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Three-week timeframe may not capture long-term effects...' is listed but not addressed
  - `uncertainties[1]`: "Three-week timeframe may not capture long-term effects"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### synthetic

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/3 content words)
  - `key_claims[2]`: "No major epistemic failures"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 2 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[1]`: "Three-week timeframe may not capture long-term effects"
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "This is a solid study. The randomised experimental design supports causal inference. The authors are"


## Agent Profiles

### synthetic (synthetic-pilot-v1)
**Parse OK:** True | **Latency:** 0ms

**Final Answer:** This is a solid study. The randomised experimental design supports causal inference. The authors are careful not to overgeneralise and openly acknowledge limitations.

**Confidence:** 0.88

**Assumptions:**
- The study was conducted rigorously with proper randomisation
- Self-report measures are adequate for depression and loneliness

**Reasoning Steps:**
1. The study uses random assignment — this is a true experiment, not observational.
2. 143 participants is modest but sufficient for detecting effect sizes in within-subject designs.
3. The evidence supports the claim: restricting social media use reduced depression and loneliness.
4. The authors show cautious scope control by noting the study only covers college students and three platforms.
5. No major epistemic failures detected. The conclusion matches the evidence.

**Key Claims:**
- This is a solid, well-designed study with appropriate caveats
- Evidence matches the claim made by the authors
- No major epistemic failures

**Alternative Hypotheses:**
- Could there be a demand effect? Unlikely given objective usage data from screenshots.

**Uncertainties:**
- Self-report measures may be subject to social desirability bias
- Three-week timeframe may not capture long-term effects

**Self-Verification:**
- Am I overflagging? No — the study design is genuinely strong and authors are cautious.
- Could I be missing a subtle issue? The sample size is modest but acknowledged.

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 1.2/8 `#.........`
- Structural Reasoning: 5.9/8 `#######...`
- Assumption Discipline: 4.8/6 `########..`
- Uncertainty Handling: 3.6/6 `######....`
- Alternative Hypothesis Quality: 4.8/6 `########..`
- Self Monitoring Quality: 2.0/8 `##........`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: synthetic** scored **71.8/100**.

**Best per dimension:**
- Correctness: synthetic (30.0/30)
- Support Strength: synthetic (1.2/8)
- Structural Reasoning: synthetic (5.9/8)
- Assumption Discipline: synthetic (4.8/6)
- Uncertainty Handling: synthetic (3.6/6)
- Alternative Hypothesis Quality: synthetic (4.8/6)
- Self Monitoring Quality: synthetic (2.0/8)
- Insight Depth: synthetic (8.0/8)
- Mechanism Quality: synthetic (1.5/10)
- Communication Efficiency: synthetic (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| synthetic | 0.0s | 71.8/100 | 0.0 |

Failure modes observed: decorative_uncertainty, named_not_explained, unsupported_intermediate_step.
