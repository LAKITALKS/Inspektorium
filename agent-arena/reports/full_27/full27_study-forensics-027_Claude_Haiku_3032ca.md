# Forensic Dossier: Study Forensics: AI coding assistant productivity claims

**Run ID:** `full27_study-forensics-027_Claude_Haiku_3032ca`  
**Task:** study-forensics-027 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T17:03:23.245591+00:00  
**Task Family:** overclaim  
**Trap Type:** survivorship_bias_overclaim  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **78.5/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, oververbose_without_gain
**Forensic flags:** 0
**Consistency findings:** 8
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 30.0/30 | 2.4/8 | 5.2/8 | 4.8/6 | 3.6/6 | 5.0/6 | 5.6/8 | 8.0/8 | 7.0/10 | 7.0/10 | **78.5/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `overclaim` [+] (gold: `overclaim`)
**Finding Recall:** 100%
**Matched Findings:** conclusion_exceeds_results, unsupported_generalization
**Extra Findings:** cautious_scope_control, decorative_uncertainty, correlation_as_causation

## Reasoning Integrity Audit

### Claude Haiku
**Classification:** Correct and well-supported
**Load-bearing steps:** 1 / 8

## Mechanism Analysis

### Claude Haiku
| Aspect | Status |
|--------|--------|
| Concept named | :white_check_mark: bias, effect |
| Mechanism described | :white_check_mark: (1 sentence(s)) |
| Grounded to case | :white_check_mark: (1 sentence(s)) |

## Grounding Audit

### Claude Haiku
Conclusion claims: 1
- Direct support: 0
- Indirect support: 1
- Unsupported: 0
- Contradicted: 0


## Evidence Map

### Claude Haiku

**Correctness:** 30.0/30
  - (+) `final_answer`: "overclaim"
    _Agent's answer for correctness check_
  - Note: Exact match

**Support Strength:** 2.4/8
  - (+) `final_answer`: "overclaim"
    _Conclusion grounded by reasoning chain_
  - Note: Support classification: 0 load-bearing, 1 supporting, 0 mentioned / 8
  - Note: Reasoning graph confirms conclusion grounding

**Structural Reasoning:** 5.2/8
  - (+) `steps[3]`: "CONFOUNDING VARIABLES NOT ADDRESSED: (1) Hawthorne effect — developers may work harder when being studied; (2) selection"
    _Most informative reasoning step_
  - Note: 8 reasoning steps
  - Note: Low step utility: 1/8 steps contribute

**Assumption Discipline:** 4.8/6
  - (+) `assumptions[0]`: "The study measured actual productivity outcomes (code commits, PR times, feature velocity) rather than self-reported sat"
    _Most substantive assumption_
  - Note: 5/5 substantive assumptions

**Uncertainty Handling:** 3.6/6
  - (+) `uncertainties[0]`: "Whether the study included any control group (text does not explicitly state this, but 'baseline measurements taken befo"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.88"
    _Stated confidence level_
  - (-) `uncertainties[2]`: "Whether the 22% dropout rate was analyzed for systematic differences (selection bias risk)."
    _Listed but never addressed in reasoning_
  - Note: 5 uncertainties (5 substantive)
  - Note: 1 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 5.0/6
  - (+) `alternative_hypotheses[1]`: "mechanism_vs_evidence: If the study were framed as 'preliminary evidence suggesting AI assistants may improve coding spe"
    _Most substantive alternative hypothesis_
  - Note: 3 alternative hypotheses considered
  - Note: 1/3 include rejection reasoning

**Self Monitoring Quality:** 5.6/8
  - (+) `self_check[3]`: "Did I miss any strengths? The study is reasonably large (n=450) and measured objective behavioral metrics rather than se"
    _Most substantive self-verification step_
  - Note: 5 self-check items
  - Note: Self-check quality: 0 deep, 5 arithmetic, 0 fluff

**Mechanism Quality:** 6.0/10
  - (+) `(mechanism analysis)`: "RETENTION RATE INTERPRETATION: The 78% continuation is presented as evidence of 'high satisfaction and sustained utility"
    _Case-grounded mechanism explanation_
  - Note: Names concept + describes mechanism + grounds to case

**Communication Efficiency:** 7.0/10
  - Note: Signal density: 0.74, 852 words
  - Note: Verbose (852 words)

**Insight Depth:** 8.0/8
  - (+) `(output text)`: "domized controlled trial, has no control group mentioned, and measures behav"
    _Insight 'no control group' matched (exact)_
  - Note: Key insights: 2 full / 2


## Failure Analysis

### Claude Haiku

**STYLISTIC:**
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether the 22% dropout rate was analyzed for systematic dif...' is listed but not addressed
  - `uncertainties[2]`: "Whether the 22% dropout rate was analyzed for systematic differences (selection bias risk)."
  - _Impacts: uncertainty_handling_
- **Oververbose Without Gain** `[HEURISTIC]`: Output is verbose (852 words, density 0.74)
  - `(computed)`: "852 words, density 0.74"
  - _Impacts: communication_efficiency_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/17 content words)
  - `key_claims[0]`: "OVERCLAIM: Recommending 'immediate enterprise adoption' based on a single 3-month observational stud"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/14 content words)
  - `key_claims[1]`: "CONFOUNDING: No control group means the 42% and 35% improvements cannot be attributed to the tool; H"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/16 content words)
  - `key_claims[2]`: "METRIC GAMING RISK: Optimizing for commits and PR completion time may not reflect genuine productivi"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/13 content words)
  - `key_claims[3]`: "GENERALIZATION OVERREACH: Claiming 'universal applicability' and 'reshape the industry' from a singl"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 5 has low overlap with final answer (0/12 content words)
  - `key_claims[4]`: "RETENTION ≠ EFFICACY: 78% continuation is presented as evidence of utility, but it only shows user s"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 3 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[2]`: "Whether the 22% dropout rate was analyzed for systematic differences (selection bias risk)."
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "correlation_vs_causation: The productivity gains could reflect Hawthorne effect, selection bias (hig"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 3 is stated without rejection reasoning
  - `alternative_hypotheses[2]`: "solid: If the text had stated 'In a 3-month observational study, developers reported faster task com"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 19546ms

**Final Answer:** overclaim

**Confidence:** 0.88

**Assumptions:**
- The study measured actual productivity outcomes (code commits, PR times, feature velocity) rather than self-reported satisfaction
- The 450 developers represent a reasonably sized cohort for observational research
- The three-month duration is sufficient to detect sustained effects
- Baseline measurements were taken before tool adoption (pre-post design)
- The 78% retention rate reflects genuine utility rather than selection bias

**Reasoning Steps:**
1. EVIDENCE TIER IDENTIFICATION: This is a limited human observational study (n=450, 3-month duration, pre-post measurement). It is NOT a randomized controlled trial, has no control group mentioned, and measures behavioral/output metrics rather than clinical outcomes. This places it at limited_human tier.
2. CONCLUSION TIER IDENTIFICATION: The text makes claims about 'transformative productivity gains,' 'reshape software engineering workflows across the industry,' and recommends 'immediate enterprise adoption.' These are industry-wide policy/adoption claims, placing conclusion tier at human_policy.
3. BRIDGE GAP ANALYSIS: The evidence (observational pre-post study) does not support the conclusion (industry-wide transformative impact and adoption recommendations). There is a substantial gap.
4. CONFOUNDING VARIABLES NOT ADDRESSED: (1) Hawthorne effect — developers may work harder when being studied; (2) selection bias — the 78% who continued may be systematically different from the 22% who dropped out; (3) learning curve — developers may have improved naturally over 3 months regardless of tool; (4) no control group — no comparison to developers NOT using the tool during the same period; (5) metric gaming — developers may optimize for 'commits' and 'PR completion time' without improving actual code quality or feature value.
5. OVERCLAIM DETECTION: The phrase 'fundamentally enhance' and 'reshape software engineering workflows across the industry' vastly exceeds what a single 3-month observational study can support. The recommendation for 'immediate enterprise adoption' is a policy claim that requires evidence of sustained benefit, cost-effectiveness, and absence of negative externalities — none of which are demonstrated.
6. RETENTION RATE INTERPRETATION: The 78% continuation is presented as evidence of 'high satisfaction and sustained utility,' but this conflates user satisfaction with actual productivity benefit. Users may continue because the tool is convenient or novel, not because it genuinely improves outcomes. This is decorative uncertainty — the retention statistic is used to reinforce the conclusion without addressing confounders.
7. GENERALIZATION CLAIM: 'Consistent across both junior and senior developers' suggests universal applicability, but a single study with no control group cannot establish this. Subgroup consistency within a biased sample does not prove generalizability.
8. MISSING ELEMENTS: No mention of code quality metrics, bug rates, technical debt, or long-term maintenance costs. No control group. No blinding. No adjustment for confounders. No discussion of potential negative effects (e.g., reduced learning, over-reliance on suggestions, security risks).

**Key Claims:**
- OVERCLAIM: Recommending 'immediate enterprise adoption' based on a single 3-month observational study without control group or quality metrics is premature and unsupported.
- CONFOUNDING: No control group means the 42% and 35% improvements cannot be attributed to the tool; Hawthorne effect and selection bias are plausible alternatives.
- METRIC GAMING RISK: Optimizing for commits and PR completion time may not reflect genuine productivity or code quality; these are output metrics, not outcome metrics.
- GENERALIZATION OVERREACH: Claiming 'universal applicability' and 'reshape the industry' from a single cohort study is a classic overclaim.
- RETENTION ≠ EFFICACY: 78% continuation is presented as evidence of utility, but it only shows user satisfaction, not causal productivity benefit.

**Alternative Hypotheses:**
- correlation_vs_causation: The productivity gains could reflect Hawthorne effect, selection bias (high performers retained), or natural learning curve rather than tool efficacy.
- mechanism_vs_evidence: If the study were framed as 'preliminary evidence suggesting AI assistants may improve coding speed' with caveats about need for RCTs, it would be mechanism_vs_evidence. But the text makes definitive policy claims, elevating it to overclaim.
- solid: If the text had stated 'In a 3-month observational study, developers reported faster task completion and higher commit rates; further controlled research is needed to establish causation and long-term impact,' it would be solid.

**Uncertainties:**
- Whether the study included any control group (text does not explicitly state this, but 'baseline measurements taken before tool adoption' suggests pre-post design without concurrent control).
- Whether code quality, bug rates, or technical debt were measured (text only mentions commits, PR times, and velocity).
- Whether the 22% dropout rate was analyzed for systematic differences (selection bias risk).
- Whether the three-month period is sufficient to detect regression to the mean or novelty effects wearing off.
- Whether 'feature delivery velocity' is a validated productivity metric or a proxy that may not reflect actual business value.

**Self-Verification:**
- Did I correctly identify the evidence tier? Yes — this is observational human data (limited_human), not a clinical RCT or animal study.
- Did I correctly identify the conclusion tier? Yes — the text makes industry-wide policy recommendations ('immediate enterprise adoption'), which is human_policy tier.
- Did I overstate the problems? No — the absence of a control group is a fundamental design flaw for causal claims, and the text explicitly makes causal claims ('enhance developer productivity').
- Did I miss any strengths? The study is reasonably large (n=450) and measured objective behavioral metrics rather than self-report alone. However, size and objectivity do not overcome the lack of a control group.
- Is the classification justified? Yes — the text makes strong causal and policy claims that exceed the evidence tier. This is the definition of overclaim.

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 2.4/8 `###.......`
- Structural Reasoning: 5.2/8 `######....`
- Assumption Discipline: 4.8/6 `########..`
- Uncertainty Handling: 3.6/6 `######....`
- Alternative Hypothesis Quality: 5.0/6 `########..`
- Self Monitoring Quality: 5.6/8 `#######...`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 7.0/10 `#######...`
- Communication Efficiency: 7.0/10 `#######...`


## Final Verdict

**Solo run: Claude Haiku** scored **78.5/100**.

**Best per dimension:**
- Correctness: Claude Haiku (30.0/30)
- Support Strength: Claude Haiku (2.4/8)
- Structural Reasoning: Claude Haiku (5.2/8)
- Assumption Discipline: Claude Haiku (4.8/6)
- Uncertainty Handling: Claude Haiku (3.6/6)
- Alternative Hypothesis Quality: Claude Haiku (5.0/6)
- Self Monitoring Quality: Claude Haiku (5.6/8)
- Insight Depth: Claude Haiku (8.0/8)
- Mechanism Quality: Claude Haiku (7.0/10)
- Communication Efficiency: Claude Haiku (7.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 19.5s | 78.5/100 | 4.0 |

Failure modes observed: decorative_uncertainty, oververbose_without_gain.
