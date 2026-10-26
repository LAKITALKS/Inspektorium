# Forensic Dossier: Study Forensics: AI instruction outperforms human teachers

**Run ID:** `full27_study-forensics-025_Claude_Haiku_b88dcc`  
**Task:** study-forensics-025 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T08:17:00.864143+00:00  
**Task Family:** overclaim  
**Trap Type:** media_inflated_overclaim  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **73.0/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, named_not_explained, unsupported_intermediate_step
**Forensic flags:** 4
**Consistency findings:** 10
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 30.0/30 | 0.7/8 | 4.8/8 | 4.8/6 | 3.3/6 | 5.0/6 | 6.4/8 | 8.0/8 | 1.5/10 | 8.5/10 | **73.0/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `overclaim` [+] (gold: `overclaim`)
**Finding Recall:** 100%
**Matched Findings:** conclusion_exceeds_results, unsupported_generalization
**Extra Findings:** evidence_matches_claim, cautious_scope_control, none_or_minor, decorative_uncertainty, correlation_as_causation

## Reasoning Integrity Audit

### Claude Haiku
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 7

## Mechanism Analysis

### Claude Haiku
| Aspect | Status |
|--------|--------|
| Concept named | :white_check_mark: bias, effect |
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
- "overclaim"


## Forensic Flags

### Claude Haiku

- **[MODERATE]** `weak_mechanism`: Correct answer but weak mechanism explanation — answer may not generalize
  - `final_answer`: "overclaim"
- **[MAJOR]** `unsupported_leap`: Correct answer with weak support chain — final answer may be an unsupported leap
- **[MODERATE]** `unsupported_conclusion_claims`: 1/1 conclusion claims lack step support
  - `final_answer`: "overclaim"
- **[MODERATE]** `ungrounded_mechanism`: Mechanism named/described but not connected to case-specific data
  - `(mechanism analysis)`: "bias, effect"


## Evidence Map

### Claude Haiku

**Correctness:** 30.0/30
  - (+) `final_answer`: "overclaim"
    _Agent's answer for correctness check_
  - Note: Exact match

**Support Strength:** 1.2/8
  - (+) `final_answer`: "overclaim"
    _Conclusion grounded by reasoning chain_
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 7
  - Note: Reasoning graph confirms conclusion grounding

**Structural Reasoning:** 4.8/8
  - (+) `steps[4]`: "Checked for confounders: pilot programs typically involve selection bias (motivated students/teachers), novelty effects,"
    _Most informative reasoning step_
  - Note: 7 reasoning steps
  - Note: Low step utility: 0/7 steps contribute

**Assumption Discipline:** 4.8/6
  - (+) `assumptions[1]`: "The 65% test score rise and 'two-times learning effect' are real findings from these pilots"
    _Most substantive assumption_
  - Note: 5/5 substantive assumptions

**Uncertainty Handling:** 3.3/6
  - (+) `uncertainties[0]`: "Whether the cited pilot programs actually exist and what their actual methodology was (the article does not cite sources"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.88"
    _Stated confidence level_
  - (-) `uncertainties[1]`: "Whether the 65% figure is absolute gain, relative gain, or cherry-picked from a subset of outcomes"
    _Listed but never addressed in reasoning_
  - (-) `uncertainties[5]`: "What 'active-learning classrooms' means as a comparison group and whether it's a fair baseline"
    _Listed but never addressed in reasoning_
  - Note: 6 uncertainties (6 substantive)
  - Note: 2 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 5.0/6
  - (+) `alternative_hypotheses[0]`: "The study could be solid if pilots were large, randomized, controlled trials with pre-registered outcomes and long-term "
    _Most substantive alternative hypothesis_
  - Note: 3 alternative hypotheses considered
  - Note: 1/3 include rejection reasoning

**Self Monitoring Quality:** 6.4/8
  - (+) `self_check[4]`: "Is this truly an overclaim or could it be solid reporting of solid research? The article's language ('being dismantled,'"
    _Most substantive self-verification step_
  - Note: 5 self-check items
  - Note: Self-check quality: 1 deep, 4 arithmetic, 0 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 8.5/10
  - Note: Signal density: 0.73, 602 words

**Insight Depth:** 4.0/8
  - (?) `(not found)`: "Missing: no methodology"
    _Insight 'no methodology' not found_
  - Note: Key insights: 1 full / 2


## Failure Analysis

### Claude Haiku

**MODERATE:**
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Names the phenomenon but does not explain the causal mechanism
  - `final_answer`: "overclaim"
  - _Impacts: mechanism_quality_
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Named concept(s) ['bias', 'effect'] but mechanism not described
  - _Impacts: mechanism_quality, insight_depth_
- **Unsupported Intermediate Step** `[MEDIUM CONFIDENCE]`: No reasoning step is load-bearing — final answer lacks traceable derivation
  - `final_answer`: "overclaim"
  - _Impacts: support_strength, structural_reasoning_

**STYLISTIC:**
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether the 65% figure is absolute gain, relative gain, or c...' is listed but not addressed
  - `uncertainties[1]`: "Whether the 65% figure is absolute gain, relative gain, or cherry-picked from a subset of outcomes"
  - _Impacts: uncertainty_handling_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'What 'active-learning classrooms' means as a comparison grou...' is listed but not addressed
  - `uncertainties[5]`: "What 'active-learning classrooms' means as a comparison group and whether it's a fair baseline"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/15 content words)
  - `key_claims[0]`: "OVERCLAIM: Generalizing from pilot programs to 'all subjects' and claiming educators' role is 'being"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/16 content words)
  - `key_claims[1]`: "OVERCLAIM: Describing findings as 'data-backed reality' when pilots are inherently limited in genera"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/15 content words)
  - `key_claims[2]`: "OVERCLAIM: The 65% score rise and 2x learning effect are presented as established facts without cave"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/15 content words)
  - `key_claims[3]`: "CONFOUNDING: No mention of whether gains reflect AI efficacy or pilot-specific factors (motivated pa"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 5 has low overlap with final answer (0/16 content words)
  - `key_claims[4]`: "DECORATIVE UNCERTAINTY: Article makes absolute claims without hedging language ('is being dismantled"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 2 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[1]`: "Whether the 65% figure is absolute gain, relative gain, or cherry-picked from a subset of outcomes"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 6 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[5]`: "What 'active-learning classrooms' means as a comparison group and whether it's a fair baseline"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 2 is stated without rejection reasoning
  - `alternative_hypotheses[1]`: "The claims could be correlation_vs_causation if the 65% gains reflect selection bias or novelty effe"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 3 is stated without rejection reasoning
  - `alternative_hypotheses[2]`: "The article could be mechanism_vs_evidence if it applies findings from controlled pilots (mechanism)"
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "overclaim"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 14425ms

**Final Answer:** overclaim

**Confidence:** 0.88

**Assumptions:**
- The article is reporting on actual pilot programs with published results
- The 65% test score rise and 'two-times learning effect' are real findings from these pilots
- The article is making generalizable claims about all education based on limited pilot data
- No distinction is made between effect sizes in controlled pilots vs. real-world scalability
- The article treats pilot success as predictive of system-wide outcomes

**Reasoning Steps:**
1. Identified the core claim: AI systems are making human teachers obsolete and represent a 'data-backed reality for all subjects'
2. Examined the evidence base: pilot programs in US and UK with reported performance gains (65% score rise, 2x learning effect)
3. Assessed scope of evidence: pilots are inherently limited in scale, duration, student population, and context
4. Evaluated generalization: article claims 'all subjects' and 'primary source of knowledge is being dismantled' based on pilots in specific subjects (physics, math, literacy)
5. Checked for confounders: pilot programs typically involve selection bias (motivated students/teachers), novelty effects, intensive support, and controlled conditions not present in scaled deployment
6. Assessed mechanism claims: article asserts AI is 'twice as effective' without explaining why or addressing whether this persists outside pilot conditions
7. Evaluated certainty language: conclusion is stated as established fact ('data-backed reality') despite pilot-stage evidence

**Key Claims:**
- OVERCLAIM: Generalizing from pilot programs to 'all subjects' and claiming educators' role is 'being dismantled' vastly exceeds pilot evidence
- OVERCLAIM: Describing findings as 'data-backed reality' when pilots are inherently limited in generalizability and subject to confounders (selection bias, novelty, intensive support)
- OVERCLAIM: The 65% score rise and 2x learning effect are presented as established facts without caveats about pilot limitations, effect persistence, or real-world scalability
- CONFOUNDING: No mention of whether gains reflect AI efficacy or pilot-specific factors (motivated participants, intensive support, novelty, teacher selection)
- DECORATIVE UNCERTAINTY: Article makes absolute claims without hedging language ('is being dismantled,' 'data-backed reality') despite pilot-stage evidence

**Alternative Hypotheses:**
- The study could be solid if pilots were large, randomized, controlled trials with pre-registered outcomes and long-term follow-up—but the article does not describe this rigor
- The claims could be correlation_vs_causation if the 65% gains reflect selection bias or novelty effects rather than AI efficacy itself
- The article could be mechanism_vs_evidence if it applies findings from controlled pilots (mechanism) to uncontrolled real-world deployment (evidence needed)

**Uncertainties:**
- Whether the cited pilot programs actually exist and what their actual methodology was (the article does not cite sources)
- Whether the 65% figure is absolute gain, relative gain, or cherry-picked from a subset of outcomes
- Whether the 'two-times learning effect' is a peer-reviewed finding or promotional language from AI vendors
- How long the pilots ran and whether gains persisted over time
- Whether pilots controlled for teacher quality, student motivation, or novelty effects
- What 'active-learning classrooms' means as a comparison group and whether it's a fair baseline

**Self-Verification:**
- Did I assume the pilots were poorly designed? No—I noted that the article does not describe their design, so I cannot assume rigor or lack thereof. The overclaim is about generalization, not study quality.
- Did I conflate 'pilot programs exist' with 'pilots prove the claim'? No—pilots are appropriate for early testing but insufficient for claims about system-wide obsolescence.
- Did I miss that the article might be reporting on peer-reviewed research? Possibly—but the article does not cite sources, uses promotional language ('data-backed reality'), and makes sweeping claims inconsistent with cautious research communication.
- Did I overweight the confounding concern? No—selection bias and novelty effects are standard concerns in pilot-to-scale transitions and are not addressed in the article.
- Is this truly an overclaim or could it be solid reporting of solid research? The article's language ('being dismantled,' 'all subjects,' 'data-backed reality') goes beyond what pilot evidence can support, even if the pilots themselves were well-designed.

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.7/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 4.8/6 `########..`
- Uncertainty Handling: 3.3/6 `#####.....`
- Alternative Hypothesis Quality: 5.0/6 `########..`
- Self Monitoring Quality: 6.4/8 `########..`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 8.5/10 `########..`


## Final Verdict

**Solo run: Claude Haiku** scored **73.0/100**.

**Best per dimension:**
- Correctness: Claude Haiku (30.0/30)
- Support Strength: Claude Haiku (0.7/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (4.8/6)
- Uncertainty Handling: Claude Haiku (3.3/6)
- Alternative Hypothesis Quality: Claude Haiku (5.0/6)
- Self Monitoring Quality: Claude Haiku (6.4/8)
- Insight Depth: Claude Haiku (8.0/8)
- Mechanism Quality: Claude Haiku (1.5/10)
- Communication Efficiency: Claude Haiku (8.5/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 14.4s | 73.0/100 | 5.1 |

Failure modes observed: decorative_uncertainty, named_not_explained, unsupported_intermediate_step.
