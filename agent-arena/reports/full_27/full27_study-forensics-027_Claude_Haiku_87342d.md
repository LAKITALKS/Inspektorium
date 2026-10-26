# Forensic Dossier: Study Forensics: AI coding assistant productivity claims

**Run ID:** `full27_study-forensics-027_Claude_Haiku_87342d`  
**Task:** study-forensics-027 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T18:00:20.008656+00:00  
**Task Family:** overclaim  
**Trap Type:** survivorship_bias_overclaim  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **72.8/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, named_not_explained, oververbose_without_gain, unsupported_intermediate_step
**Forensic flags:** 4
**Consistency findings:** 7
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 30.0/30 | 0.7/8 | 4.8/8 | 4.8/6 | 3.6/6 | 6.0/6 | 6.4/8 | 8.0/8 | 1.5/10 | 7.0/10 | **72.8/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `overclaim` [+] (gold: `overclaim`)
**Finding Recall:** 100%
**Matched Findings:** conclusion_exceeds_results, unsupported_generalization
**Extra Findings:** evidence_matches_claim, cautious_scope_control, decorative_uncertainty, correlation_as_causation

## Reasoning Integrity Audit

### Claude Haiku
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 8

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
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 8
  - Note: Reasoning graph confirms conclusion grounding

**Structural Reasoning:** 4.8/8
  - (+) `steps[7]`: "CLASSIFICATION DECISION: The primary forensic problem is RHETORICAL INFLATION. The text actively sells a breakthrough na"
    _Most informative reasoning step_
  - Note: 8 reasoning steps
  - Note: Low step utility: 0/8 steps contribute

**Assumption Discipline:** 4.8/6
  - (+) `assumptions[0]`: "The study measured actual productivity outcomes (code commits, PR times, velocity) rather than self-reported satisfactio"
    _Most substantive assumption_
  - Note: 5/5 substantive assumptions

**Uncertainty Handling:** 3.6/6
  - (+) `uncertainties[0]`: "Whether the study included any control group (e.g., developers not using the tool). The text does not explicitly state '"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.92"
    _Stated confidence level_
  - (-) `uncertainties[4]`: "The exact definition of 'productivity' and whether it aligns with business outcomes (e.g., fewer bugs, faster feature de"
    _Listed but never addressed in reasoning_
  - Note: 5 uncertainties (5 substantive)
  - Note: 1 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 6.0/6
  - (+) `alternative_hypotheses[0]`: "mechanism_vs_evidence: If the text had been more cautious ('this observational study suggests a possible productivity be"
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 2/2 include rejection reasoning

**Self Monitoring Quality:** 6.4/8
  - (+) `self_check[1]`: "Did I miss the possibility that this is a solid study? No. A solid study would report results cautiously ('this observat"
    _Most substantive self-verification step_
  - Note: 6 self-check items
  - Note: Self-check quality: 0 deep, 6 arithmetic, 0 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 7.0/10
  - Note: Signal density: 0.74, 1006 words
  - Note: Verbose (1006 words)

**Insight Depth:** 8.0/8
  - (+) `(output text)`: "domized controlled trial, has no control group, and measures behavioral/outp"
    _Insight 'no control group' matched (exact)_
  - Note: Key insights: 2 full / 2


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
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'The exact definition of 'productivity' and whether it aligns...' is listed but not addressed
  - `uncertainties[4]`: "The exact definition of 'productivity' and whether it aligns with business outcomes (e.g., fewer bug"
  - _Impacts: uncertainty_handling_
- **Oververbose Without Gain** `[HEURISTIC]`: Output is verbose (1006 words, density 0.74)
  - `(computed)`: "1006 words, density 0.74"
  - _Impacts: communication_efficiency_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/17 content words)
  - `key_claims[0]`: "OVERCLAIM: The text uses promotional language ('transformative,' 'reshape industry,' 'immediate adop"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/19 content words)
  - `key_claims[1]`: "CONFOUNDER RISK: No control group and multiple uncontrolled variables (novelty effect, selection bia"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (1/16 content words)
  - `key_claims[2]`: "GENERALIZATION LEAP: A study of 450 developers using one tool over three months does not support cla"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/21 content words)
  - `key_claims[3]`: "RETENTION BIAS: The 78% continuation rate reflects satisfaction with the tool experience, not necess"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 5 has low overlap with final answer (0/17 content words)
  - `key_claims[4]`: "MISSING CONTEXT: No mention of software quality, bug rates, user satisfaction, or business outcomes "
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 5 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[4]`: "The exact definition of 'productivity' and whether it aligns with business outcomes (e.g., fewer bug"
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "overclaim"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 20527ms

**Final Answer:** overclaim

**Confidence:** 0.92

**Assumptions:**
- The study measured actual productivity outcomes (code commits, PR times, velocity) rather than self-reported satisfaction
- The 450 developers represent a reasonably sized cohort for observational measurement
- The three-month duration is sufficient to detect sustained effects
- Baseline measurements were taken before tool adoption (pre-post design)
- The 78% retention rate reflects genuine utility rather than selection bias or sunk-cost effects

**Reasoning Steps:**
1. EVIDENCE TIER IDENTIFICATION: This is a limited human observational study (pre-post measurement of 450 developers over 3 months). It is NOT a randomized controlled trial, has no control group, and measures behavioral/output metrics rather than causal mechanisms.
2. CONCLUSION TIER IDENTIFICATION: The text makes sweeping claims about industry-wide transformation ('reshape software engineering workflows across the industry'), enterprise policy ('immediate enterprise adoption'), and universal applicability ('regardless of experience level'). These are human_policy and general_public tier conclusions.
3. BRIDGE GAP ANALYSIS: The evidence is a single-arm observational study with no control group. The bridge from 'we measured faster commits in 450 developers using tool X' to 'AI coding assistants fundamentally enhance productivity industry-wide' requires: (a) causal inference (not correlation), (b) generalization beyond this specific tool and cohort, (c) exclusion of confounders (learning effects, selection bias, Hawthorne effect, task selection).
4. CONFOUNDER CHECK: Multiple uncontrolled variables could explain the observed gains: (1) Novelty/Hawthorne effect — developers work harder when observed or using new tools; (2) Selection bias — the 78% who continued may be systematically different from those who dropped out; (3) Task selection — developers may have chosen easier tasks to complete faster; (4) Learning curve — developers improve over time regardless of tool; (5) Measurement artifact — 'code commits' and 'pull requests' may not correlate with actual software quality or business value.
5. RHETORICAL INFLATION CHECK: The text uses promotional language: 'transformative,' 'fundamentally enhance,' 'reshape,' 'immediate adoption to maintain competitive advantage.' These are active selling claims, not analytical hedges. The language treats correlation as causation and a single observational study as definitive evidence.
6. RETENTION RATE MISINTERPRETATION: The 78% continuation rate is presented as evidence of 'utility,' but in a study where developers know they are being measured and where tool adoption may be socially encouraged, continuation reflects satisfaction with the tool experience, not necessarily productivity gain. This is a weak proxy for actual impact.
7. UNIVERSAL APPLICABILITY CLAIM: The statement that gains were 'consistent across both junior and senior developers' is presented without effect-size breakdown, confidence intervals, or interaction analysis. 'Consistent' may mean both groups improved, but not necessarily by the same magnitude or for the same reasons.
8. CLASSIFICATION DECISION: The primary forensic problem is RHETORICAL INFLATION. The text actively sells a breakthrough narrative ('transformative,' 'reshape industry,' 'immediate adoption') based on a single-arm observational study with no control group and multiple uncontrolled confounders. This is not a cautious, hedged report of limited evidence; it is a promotional claim that exceeds the evidence tier by multiple steps. The evidence supports 'developers completed tasks faster while using this tool' (limited_human, observational). The conclusion implies 'AI coding assistants are a fundamental productivity enhancement that should be adopted enterprise-wide' (human_policy, causal). The gap is bridged by rhetorical assertion, not evidence.

**Key Claims:**
- OVERCLAIM: The text uses promotional language ('transformative,' 'reshape industry,' 'immediate adoption') to assert industry-wide impact based on a single-arm observational study.
- CONFOUNDER RISK: No control group and multiple uncontrolled variables (novelty effect, selection bias, task selection, learning curve) make causal inference unreliable.
- GENERALIZATION LEAP: A study of 450 developers using one tool over three months does not support claims about 'software engineering workflows across the industry.'
- RETENTION BIAS: The 78% continuation rate reflects satisfaction with the tool experience, not necessarily productivity gain, and may reflect selection bias (those who benefited stayed; those who didn't dropped out).
- MISSING CONTEXT: No mention of software quality, bug rates, user satisfaction, or business outcomes — only output metrics (commits, PR times) that may not reflect true productivity.

**Alternative Hypotheses:**
- mechanism_vs_evidence: If the text had been more cautious ('this observational study suggests a possible productivity benefit; controlled trials are needed'), the primary issue would be evidence-tier mismatch rather than overclaim. However, the promotional language ('transformative,' 'reshape,' 'immediate adoption') elevates this to overclaim.
- correlation_vs_causation: The core issue is causal inference from observational data, but this is subsumed under overclaim because the text does not merely report correlation — it asserts causation and industry-wide impact.

**Uncertainties:**
- Whether the study included any control group (e.g., developers not using the tool). The text does not explicitly state 'no control group,' but the phrase 'baseline measurements taken before tool adoption' suggests a pre-post design, not a randomized trial.
- Whether 'code commits' and 'pull request completion times' are validated proxies for actual productivity or software quality. Faster commits could reflect lower quality or task selection bias.
- Whether the 42% and 35% figures are statistically significant or clinically meaningful. No confidence intervals, p-values, or effect-size context is provided.
- Whether the study controlled for confounders such as task difficulty, developer experience, or external factors (e.g., deadline pressure, team changes).
- The exact definition of 'productivity' and whether it aligns with business outcomes (e.g., fewer bugs, faster feature delivery, user satisfaction).

**Self-Verification:**
- Did I overstate the problems? No. The study is genuinely limited (no control group, observational, single-arm), and the text genuinely uses promotional language. These are real issues.
- Did I miss the possibility that this is a solid study? No. A solid study would report results cautiously ('this observational study suggests...'), acknowledge confounders, and avoid industry-wide claims. This text does none of that.
- Did I correctly distinguish overclaim from mechanism_vs_evidence? Yes. The text is not cautiously reporting limited evidence; it is actively selling a breakthrough narrative. The rhetorical inflation is the primary forensic finding.
- Did I correctly identify the evidence tier? Yes. This is a limited human observational study (pre-post, no control group, 450 developers, 3 months). It is not a clinical trial or RCT.
- Did I correctly identify the conclusion tier? Yes. The text makes claims about industry-wide adoption and policy ('immediate enterprise adoption'), which is human_policy tier.
- Did I verify the bridge gap? Yes. The bridge from observational data to causal, industry-wide claims is not supported by the evidence or by explicit hedging.

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.7/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 4.8/6 `########..`
- Uncertainty Handling: 3.6/6 `######....`
- Alternative Hypothesis Quality: 6.0/6 `##########`
- Self Monitoring Quality: 6.4/8 `########..`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 7.0/10 `#######...`


## Final Verdict

**Solo run: Claude Haiku** scored **72.8/100**.

**Best per dimension:**
- Correctness: Claude Haiku (30.0/30)
- Support Strength: Claude Haiku (0.7/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (4.8/6)
- Uncertainty Handling: Claude Haiku (3.6/6)
- Alternative Hypothesis Quality: Claude Haiku (6.0/6)
- Self Monitoring Quality: Claude Haiku (6.4/8)
- Insight Depth: Claude Haiku (8.0/8)
- Mechanism Quality: Claude Haiku (1.5/10)
- Communication Efficiency: Claude Haiku (7.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 20.5s | 72.8/100 | 3.5 |

Failure modes observed: decorative_uncertainty, named_not_explained, oververbose_without_gain, unsupported_intermediate_step.
