# Forensic Dossier: Study Forensics: AI instruction outperforms human teachers

**Run ID:** `full27_study-forensics-025_Claude_Haiku_3af080`  
**Task:** study-forensics-025 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T17:01:52.113732+00:00  
**Task Family:** overclaim  
**Trap Type:** media_inflated_overclaim  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **72.5/100** (margin: 0.0)
**Failure modes:** named_not_explained, unsupported_conclusion, unsupported_intermediate_step
**Forensic flags:** 4
**Consistency findings:** 6
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 30.0/30 | 0.0/8 | 4.8/8 | 4.2/6 | 3.9/6 | 6.0/6 | 5.6/8 | 8.0/8 | 1.5/10 | 8.5/10 | **72.5/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `overclaim` [+] (gold: `overclaim`)
**Finding Recall:** 100%
**Matched Findings:** conclusion_exceeds_results, unsupported_generalization
**Extra Findings:** cautious_scope_control, decorative_uncertainty, mechanism_not_demonstrated, correlation_as_causation

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

**Support Strength:** 0.0/8
  - (-) `final_answer`: "overclaim"
    _Conclusion not supported by steps_
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 8
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[3]`: "4. CONFOUNDERS NOT ADDRESSED: Pilot participants are self-selected (motivation bias). Novelty effect (Hawthorne effect) "
    _Most informative reasoning step_
  - Note: 8 reasoning steps
  - Note: Low step utility: 0/8 steps contribute

**Assumption Discipline:** 4.2/6
  - (+) `assumptions[4]`: "No mention of confounders: selection bias (motivated students in pilots), Hawthorne effect (novelty of AI), teacher qual"
    _Most substantive assumption_
  - Note: 6/6 substantive assumptions
  - Note: Many assumptions (6)

**Uncertainty Handling:** 3.9/6
  - (+) `uncertainties[4]`: "Whether 'active-learning classrooms' in the comparison were well-implemented or strawmanned"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.92"
    _Stated confidence level_
  - Note: 5 uncertainties (5 substantive)
  - Note: Confidence 0.92

**Alternative Hypothesis Quality:** 6.0/6
  - (+) `alternative_hypotheses[0]`: "mechanism_vs_evidence: If the text were framed as 'early evidence suggests AI tutoring *could* improve learning in some "
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 2/2 include rejection reasoning

**Self Monitoring Quality:** 5.6/8
  - (+) `self_check[2]`: "Is this truly an overclaim, or is it mechanism_vs_evidence? It is overclaim because the text does not hedge its policy c"
    _Most substantive self-verification step_
  - Note: 5 self-check items
  - Note: Self-check quality: 0 deep, 5 arithmetic, 0 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 8.5/10
  - Note: Signal density: 0.71, 746 words

**Insight Depth:** 4.0/8
  - (?) `(not found)`: "Missing: no methodology"
    _Insight 'no methodology' not found_
  - Note: Key insights: 1 full / 2


## Failure Analysis

### Claude Haiku

**MODERATE:**
- **Unsupported Conclusion** `[MEDIUM CONFIDENCE]`: Final answer lacks load-bearing or supporting step grounding
  - `final_answer`: "overclaim"
  - _Impacts: support_strength_
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Names the phenomenon but does not explain the causal mechanism
  - `final_answer`: "overclaim"
  - _Impacts: mechanism_quality_
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Named concept(s) ['bias', 'effect'] but mechanism not described
  - _Impacts: mechanism_quality, insight_depth_
- **Unsupported Intermediate Step** `[MEDIUM CONFIDENCE]`: No reasoning step is load-bearing — final answer lacks traceable derivation
  - `final_answer`: "overclaim"
  - _Impacts: support_strength, structural_reasoning_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (1/15 content words)
  - `key_claims[0]`: "The article makes a policy-level claim (educators are becoming obsolete) based on limited_human evid"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/19 content words)
  - `key_claims[1]`: "The 65% test score rise lacks context and is presented without statistical rigor, making it impossib"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (1/15 content words)
  - `key_claims[2]`: "The claim that AI is 'data-backed' for 'all subjects' overgeneralizes from three domains and ignores"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/14 content words)
  - `key_claims[3]`: "Confounders (selection bias, novelty effect, teacher quality variation) are not acknowledged, making"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 5 has low overlap with final answer (0/12 content words)
  - `key_claims[4]`: "The article uses hedging language ('purportedly,' 'some reports') but does not let that hedging cons"
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "overclaim"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 17399ms

**Final Answer:** overclaim

**Confidence:** 0.92

**Assumptions:**
- The 'pilot programs' referenced are small-scale, non-randomized studies without control groups or blinding
- The 65% test score rise is reported without context on baseline performance, sample size, or statistical significance
- The 'two-times learning effect' claim is presented as a general finding but likely derives from a single pilot or cherry-picked comparison
- The article treats pilot results as generalizable to 'all subjects' and all student populations
- No mention of confounders: selection bias (motivated students in pilots), Hawthorne effect (novelty of AI), teacher quality variation, or curriculum differences
- The article does not distinguish between short-term pilot outcomes and sustained, long-term educational impact

**Reasoning Steps:**
1. 1. EVIDENCE TIER: The text cites 'pilot programs' in two countries. Pilot programs are small, often non-randomized, proof-of-concept studies. This is limited_human evidence at best.
2. 2. CONCLUSION TIER: The article makes sweeping policy claims ('role of educators is being dismantled,' 'data-backed reality for all subjects'). This is human_policy tier — affecting educational systems globally.
3. 3. BRIDGE GAP: The text jumps from small pilots to universal claims without acknowledging the gap. Phrases like 'some reports suggest' and 'purportedly' add hedging but do not close the evidence-tier mismatch.
4. 4. CONFOUNDERS NOT ADDRESSED: Pilot participants are self-selected (motivation bias). Novelty effect (Hawthorne effect) inflates short-term gains. No mention of whether AI was compared to best-practice human teaching or to baseline instruction.
5. 5. SPECIFICITY PROBLEM: The 65% rise is cited without context — rise from what baseline? Over what timeframe? With what sample size? Statistical significance unknown.
6. 6. OVERGENERALIZATION: The article claims results hold for 'all subjects' based on evidence from physics, mathematics, and literacy — three domains. No evidence for history, art, social-emotional learning, or other areas.
7. 7. MECHANISM CLAIM WITHOUT EVIDENCE: The 'two-times learning effect' is presented as fact but is likely a single comparison or a best-case scenario from a pilot, not a replicated finding.
8. 8. DECORATIVE UNCERTAINTY: Words like 'purportedly' and 'some reports' acknowledge uncertainty but do not prevent the article from making strong policy conclusions.

**Key Claims:**
- The article makes a policy-level claim (educators are becoming obsolete) based on limited_human evidence (small pilots). This is a classic evidence-tier mismatch.
- The 65% test score rise lacks context and is presented without statistical rigor, making it impossible to assess whether it reflects real learning gains or measurement artifacts.
- The claim that AI is 'data-backed' for 'all subjects' overgeneralizes from three domains and ignores domains where human mentorship, creativity, and social-emotional guidance are critical.
- Confounders (selection bias, novelty effect, teacher quality variation) are not acknowledged, making it impossible to attribute gains to AI itself.
- The article uses hedging language ('purportedly,' 'some reports') but does not let that hedging constrain its conclusions, creating decorative uncertainty.

**Alternative Hypotheses:**
- mechanism_vs_evidence: If the text were framed as 'early evidence suggests AI tutoring *could* improve learning in some contexts, pending larger trials,' it would be mechanism_vs_evidence rather than overclaim. But the text makes definitive policy claims.
- correlation_vs_causation: The article does not establish causation (AI caused the improvement) vs. confounding (selection bias, novelty, or better instruction caused it). This is a secondary issue underlying the overclaim.

**Uncertainties:**
- Whether the cited pilot programs included control groups or were purely observational
- Whether the 65% figure is a real statistic or a paraphrase/misreporting
- Whether the article is reporting on a single study or aggregating multiple pilots
- The actual sample sizes and demographic characteristics of pilot participants
- Whether 'active-learning classrooms' in the comparison were well-implemented or strawmanned

**Self-Verification:**
- Did I overstate the problems? No — the evidence-tier mismatch is real and severe. Pilot programs are not sufficient to support policy claims about dismantling the teaching profession.
- Did I miss a solid aspect? The article does cite empirical studies (pilots), which is better than pure speculation. However, the leap from pilots to policy is unjustified.
- Is this truly an overclaim, or is it mechanism_vs_evidence? It is overclaim because the text does not hedge its policy conclusions. It states as fact that 'the role of educators is being dismantled' and that AI represents a 'data-backed reality.' A mechanism_vs_evidence classification would apply if the text said 'early evidence suggests AI *could* one day replace human teachers in some contexts.' Instead, it asserts the outcome as present reality.
- Did I correctly identify the evidence tier? Yes — pilot programs are limited_human evidence. They are human studies but small, non-randomized, and not designed to answer the broad policy question being posed.
- Did I correctly identify the conclusion tier? Yes — the article makes claims about educational policy and the future of the teaching profession, which is human_policy tier.

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 4.2/6 `#######...`
- Uncertainty Handling: 3.9/6 `######....`
- Alternative Hypothesis Quality: 6.0/6 `##########`
- Self Monitoring Quality: 5.6/8 `#######...`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 8.5/10 `########..`


## Final Verdict

**Solo run: Claude Haiku** scored **72.5/100**.

**Best per dimension:**
- Correctness: Claude Haiku (30.0/30)
- Support Strength: Claude Haiku (0.0/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (4.2/6)
- Uncertainty Handling: Claude Haiku (3.9/6)
- Alternative Hypothesis Quality: Claude Haiku (6.0/6)
- Self Monitoring Quality: Claude Haiku (5.6/8)
- Insight Depth: Claude Haiku (8.0/8)
- Mechanism Quality: Claude Haiku (1.5/10)
- Communication Efficiency: Claude Haiku (8.5/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 17.4s | 72.5/100 | 4.2 |

Failure modes observed: named_not_explained, unsupported_conclusion, unsupported_intermediate_step.
