# Forensic Dossier: Study Forensics: AI instruction outperforms human teachers

**Run ID:** `val_study-forensics-025_claude_haiku_d18a43`  
**Task:** study-forensics-025 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-06T14:31:38.116711+00:00  
**Task Family:** overclaim  
**Trap Type:** media_inflated_overclaim  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **72.3/100** (margin: 0.0)
**Failure modes:** named_not_explained, unsupported_intermediate_step
**Forensic flags:** 3
**Consistency findings:** 8
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 30.0/30 | 1.2/8 | 4.8/8 | 3.3/6 | 3.9/6 | 5.5/6 | 5.6/8 | 8.0/8 | 1.5/10 | 8.5/10 | **72.3/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `overclaim` [+] (gold: `overclaim`)
**Finding Recall:** 100%
**Matched Findings:** conclusion_exceeds_results, unsupported_generalization
**Extra Findings:** cautious_scope_control, none_or_minor, decorative_uncertainty, correlation_as_causation

## Reasoning Integrity Audit

### Claude Haiku
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 8

## Mechanism Analysis

### Claude Haiku
| Aspect | Status |
|--------|--------|
| Concept named | :white_check_mark: bias, effect, principle |
| Mechanism described | :x: (0 sentence(s)) |
| Grounded to case | :x: (0 sentence(s)) |

**Missing:** mechanism not described, mechanism not grounded to case data

## Grounding Audit

### Claude Haiku
Conclusion claims: 1
- Direct support: 0
- Indirect support: 1
- Unsupported: 0
- Contradicted: 0


## Forensic Flags

### Claude Haiku

- **[MODERATE]** `weak_mechanism`: Correct answer but weak mechanism explanation — answer may not generalize
  - `final_answer`: "overclaim"
- **[MAJOR]** `unsupported_leap`: Correct answer with weak support chain — final answer may be an unsupported leap
- **[MODERATE]** `ungrounded_mechanism`: Mechanism named/described but not connected to case-specific data
  - `(mechanism analysis)`: "bias, effect, principle"


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
  - (+) `steps[4]`: "Analyzed the 'two-times learning effect' claim: described as a general principle but likely derived from specific studie"
    _Most informative reasoning step_
  - Note: 8 reasoning steps
  - Note: Low step utility: 0/8 steps contribute

**Assumption Discipline:** 3.3/6
  - (+) `assumptions[5]`: "The article assumes AI tutoring effects are causal rather than potentially confounded by selection bias, novelty effects"
    _Most substantive assumption_
  - Note: 6/6 substantive assumptions
  - Note: Many assumptions (6)

**Uncertainty Handling:** 3.9/6
  - (+) `uncertainties[3]`: "The baseline performance of comparison groups is unknown—a 65% increase from a very low baseline is different from a 65%"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.88"
    _Stated confidence level_
  - Note: 5 uncertainties (5 substantive)
  - Note: Confidence 0.88

**Alternative Hypothesis Quality:** 5.5/6
  - (+) `alternative_hypotheses[1]`: "Correlation vs. causation: Improvements could reflect selection effects (motivated students), novelty effects, or better"
    _Most substantive alternative hypothesis_
  - Note: 3 alternative hypotheses considered
  - Note: 2/3 include rejection reasoning

**Self Monitoring Quality:** 5.6/8
  - (+) `self_check[1]`: "Did I miss potential strengths? The article does cite specific programs and quantified results, which is better than pur"
    _Most substantive self-verification step_
  - Note: 5 self-check items
  - Note: Self-check quality: 0 deep, 5 arithmetic, 0 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 8.5/10
  - Note: Signal density: 0.72, 615 words

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
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Named concept(s) ['bias', 'effect', 'principle'] but mechanism not described
  - _Impacts: mechanism_quality, insight_depth_
- **Unsupported Intermediate Step** `[MEDIUM CONFIDENCE]`: No reasoning step is load-bearing — final answer lacks traceable derivation
  - `final_answer`: "overclaim"
  - _Impacts: support_strength, structural_reasoning_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (1/13 content words)
  - `key_claims[0]`: "The article makes a causal claim ('AI outperform peers') from what are likely correlational or quasi"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (1/11 content words)
  - `key_claims[1]`: "Evidence from three subjects is generalized to 'all subjects' without justification—a clear overclai"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/13 content words)
  - `key_claims[2]`: "Quantified claims (65% increase, two-times effect) lack context and appear decontextualized from the"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/11 content words)
  - `key_claims[3]`: "The conclusion that educators' roles are 'being dismantled' is a dramatic extrapolation from limited"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 5 has low overlap with final answer (0/12 content words)
  - `key_claims[4]`: "The phrase 'data-backed reality for all subjects' contradicts the actual evidence base (pilots in sp"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 6 has low overlap with final answer (0/14 content words)
  - `key_claims[5]`: "No discussion of confounders (selection bias, novelty effects, measurement differences, teacher qual"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 2 is stated without rejection reasoning
  - `alternative_hypotheses[1]`: "Correlation vs. causation: Improvements could reflect selection effects (motivated students), novelt"
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "overclaim"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 15340ms

**Final Answer:** overclaim

**Confidence:** 0.88

**Assumptions:**
- The article cites real pilot programs but may misrepresent their scope, duration, or findings
- The 65% test score increase figure is presented as a general finding rather than context-specific
- The 'two-times learning effect' is treated as a universal principle rather than a specific measurement from limited studies
- The article conflates evidence from specific subjects (physics, mathematics, literacy) with 'all subjects'
- Pilot programs are assumed to be representative of broader educational outcomes
- The article assumes AI tutoring effects are causal rather than potentially confounded by selection bias, novelty effects, or measurement artifacts

**Reasoning Steps:**
1. Identified the core claim: AI systems are making human teachers obsolete across all subjects, with quantified performance gains
2. Examined the evidence base: pilot programs in two countries with reported improvements in three specific subjects
3. Assessed generalization: the article moves from limited pilot data to sweeping conclusions about 'all subjects' and the dismantling of educator roles
4. Evaluated the 65% figure: presented without context (baseline, sample size, duration, control conditions, or whether this is an outlier)
5. Analyzed the 'two-times learning effect' claim: described as a general principle but likely derived from specific studies with unknown methodological rigor
6. Checked for confounders: no mention of selection bias (who participated?), novelty effects (students excited by new technology), teacher quality variation, or measurement differences
7. Assessed causal language: 'outperform' and 'taught' imply causation, but pilot programs are typically correlational or quasi-experimental
8. Evaluated scope creep: evidence from three subjects generalized to 'all subjects' without justification

**Key Claims:**
- The article makes a causal claim ('AI outperform peers') from what are likely correlational or quasi-experimental pilot data
- Evidence from three subjects is generalized to 'all subjects' without justification—a clear overclaim
- Quantified claims (65% increase, two-times effect) lack context and appear decontextualized from their original studies
- The conclusion that educators' roles are 'being dismantled' is a dramatic extrapolation from limited pilot evidence
- The phrase 'data-backed reality for all subjects' contradicts the actual evidence base (pilots in specific subjects only)
- No discussion of confounders (selection bias, novelty effects, measurement differences, teacher quality variation) despite their obvious relevance

**Alternative Hypotheses:**
- The study is solid but the article misrepresents it: The underlying research may be methodologically sound, but the article overstates findings and scope
- Correlation vs. causation: Improvements could reflect selection effects (motivated students), novelty effects, or better measurement rather than AI superiority
- Mechanism vs. evidence: The 'two-times learning effect' may describe a specific context (e.g., one-on-one tutoring in mathematics) but is applied universally

**Uncertainties:**
- Without access to the original pilot studies, I cannot verify whether the 65% figure or 'two-times effect' are accurately reported or cherry-picked
- The article may cite legitimate research but frame it misleadingly; the underlying studies could be solid while the article's interpretation is not
- It is unclear whether 'pilot programs' involved rigorous RCTs, quasi-experimental designs, or informal comparisons
- The baseline performance of comparison groups is unknown—a 65% increase from a very low baseline is different from a 65% increase from a high baseline
- Duration of pilots is not specified; short-term novelty effects could inflate results

**Self-Verification:**
- Did I overstate the problems? No—the article explicitly claims 'all subjects' and 'dismantling' of educator roles, which are clear overclaims given pilot-level evidence
- Did I miss potential strengths? The article does cite specific programs and quantified results, which is better than pure speculation, but the generalization is still unjustified
- Is this a correlation vs. causation issue? Yes, partially—pilots likely lack rigorous causal designs, but the primary issue is overclaim and scope creep
- Should I flag decorative uncertainty? The article shows no meaningful uncertainty language; it presents speculative conclusions as established facts
- Did I assume facts not in evidence? I noted that I cannot verify the studies without seeing them, but the article's own framing (pilot programs → universal claims) is the problem

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 1.2/8 `#.........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 3.3/6 `#####.....`
- Uncertainty Handling: 3.9/6 `######....`
- Alternative Hypothesis Quality: 5.5/6 `#########.`
- Self Monitoring Quality: 5.6/8 `#######...`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 8.5/10 `########..`


## Final Verdict

**Solo run: Claude Haiku** scored **72.3/100**.

**Best per dimension:**
- Correctness: Claude Haiku (30.0/30)
- Support Strength: Claude Haiku (1.2/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (3.3/6)
- Uncertainty Handling: Claude Haiku (3.9/6)
- Alternative Hypothesis Quality: Claude Haiku (5.5/6)
- Self Monitoring Quality: Claude Haiku (5.6/8)
- Insight Depth: Claude Haiku (8.0/8)
- Mechanism Quality: Claude Haiku (1.5/10)
- Communication Efficiency: Claude Haiku (8.5/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 15.3s | 72.3/100 | 4.7 |

Failure modes observed: named_not_explained, unsupported_intermediate_step.
