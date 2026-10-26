# Forensic Dossier: Study Forensics: AI instruction outperforms human teachers

**Run ID:** `full27_study-forensics-025_Claude_Haiku_47ac49`  
**Task:** study-forensics-025 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T17:58:46.879033+00:00  
**Task Family:** overclaim  
**Trap Type:** media_inflated_overclaim  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **72.1/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, named_not_explained, unsupported_intermediate_step
**Forensic flags:** 4
**Consistency findings:** 7
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 30.0/30 | 0.7/8 | 4.8/8 | 4.2/6 | 3.6/6 | 6.0/6 | 4.8/8 | 8.0/8 | 1.5/10 | 8.5/10 | **72.1/100** |

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

**Support Strength:** 1.2/8
  - (+) `final_answer`: "overclaim"
    _Conclusion grounded by reasoning chain_
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 8
  - Note: Reasoning graph confirms conclusion grounding

**Structural Reasoning:** 4.8/8
  - (+) `steps[7]`: "8. CLASSIFICATION DECISION: The primary problem is not an evidence-tier mismatch alone (which would be mechanism_vs_evid"
    _Most informative reasoning step_
  - Note: 8 reasoning steps
  - Note: Low step utility: 0/8 steps contribute

**Assumption Discipline:** 4.2/6
  - (+) `assumptions[2]`: "The 'two-times learning effect' is a single metric from a limited sample, not replicated across independent studies"
    _Most substantive assumption_
  - Note: 7/7 substantive assumptions
  - Note: Many assumptions (7)

**Uncertainty Handling:** 3.6/6
  - (+) `uncertainties[3]`: "Whether the article is reporting on a single study or aggregating results across multiple pilots (the vague 'some report"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.92"
    _Stated confidence level_
  - (-) `uncertainties[2]`: "Whether the 65% and 'two-times' figures are from peer-reviewed sources or promotional materials from AI vendors."
    _Listed but never addressed in reasoning_
  - Note: 4 uncertainties (4 substantive)
  - Note: 1 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 6.0/6
  - (+) `alternative_hypotheses[0]`: "mechanism_vs_evidence: If the article had been more cautious in tone ('early evidence suggests AI tutoring may improve o"
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 2/2 include rejection reasoning

**Self Monitoring Quality:** 4.8/8
  - (+) `self_check[3]`: "Is this overclaim or mechanism_vs_evidence? Overclaim, because the text actively sells a breakthrough ('dismantled,' 'da"
    _Most substantive self-verification step_
  - Note: 4 self-check items
  - Note: Self-check quality: 0 deep, 4 arithmetic, 0 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 8.5/10
  - Note: Signal density: 0.75, 644 words

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
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether the 65% and 'two-times' figures are from peer-review...' is listed but not addressed
  - `uncertainties[2]`: "Whether the 65% and 'two-times' figures are from peer-reviewed sources or promotional materials from"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (1/15 content words)
  - `key_claims[0]`: "The article makes a causal claim ('AI is making teachers obsolete') based on correlational pilot dat"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/11 content words)
  - `key_claims[1]`: "Preliminary findings from small, non-representative samples are presented as 'data-backed reality' a"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/13 content words)
  - `key_claims[2]`: "Specific metrics (65% rise, two-times effect) are cited without source, confidence intervals, or rep"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/7 content words)
  - `key_claims[3]`: "Novelty effects, selection bias, and teacher-quality confounds are not acknowledged."
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 5 has low overlap with final answer (0/12 content words)
  - `key_claims[4]`: "The scope of the conclusion (all subjects, all contexts) far exceeds the scope of the evidence (two "
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 3 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[2]`: "Whether the 65% and 'two-times' figures are from peer-reviewed sources or promotional materials from"
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "overclaim"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 15407ms

**Final Answer:** overclaim

**Confidence:** 0.92

**Assumptions:**
- The 'pilot programs' referenced are small-scale, non-randomized trials without control groups or blinding
- The 65% test score rise is reported without context (baseline performance, selection bias, measurement timing)
- The 'two-times learning effect' is a single metric from a limited sample, not replicated across independent studies
- No mention of effect sizes, confidence intervals, or statistical significance testing
- No discussion of which student populations benefited (selection bias likely present in pilot adoption)
- No accounting for novelty effects, Hawthorne effects, or teacher quality confounds
- The article treats pilot results as generalizable to 'all subjects' without evidence

**Reasoning Steps:**
1. 1. EVIDENCE TIER: Pilot programs in two countries = limited human observation (small trials, non-representative samples). This is tier 4 at best.
2. 2. CONCLUSION TIER: The article claims AI is 'rapidly making human teachers obsolete' and represents a 'data-backed reality for all subjects' — this is a sweeping policy/societal claim (tier: human_policy).
3. 3. BRIDGE GAP: Pilot data from two countries cannot support a universal claim about teacher obsolescence across all subjects and contexts.
4. 4. RHETORICAL INFLATION: The text uses promotional language ('dismantled,' 'data-backed reality,' 'rapidly making obsolete') to describe preliminary findings. It presents speculative conclusions as established fact.
5. 5. CONFOUNDERS IGNORED: No mention of (a) selection bias in pilot adoption, (b) novelty/Hawthorne effects, (c) teacher quality variation, (d) measurement timing, (e) student demographic differences.
6. 6. SPECIFICITY PROBLEM: The 65% rise and 'two-times learning effect' are cited without source attribution, confidence intervals, or replication status. These numbers carry false precision.
7. 7. SCOPE CREEP: Pilots in physics, mathematics, and literacy are generalized to 'all subjects' without evidence.
8. 8. CLASSIFICATION DECISION: The primary problem is not an evidence-tier mismatch alone (which would be mechanism_vs_evidence) but active rhetorical selling of a breakthrough claim ('dismantled,' 'data-backed reality') based on preliminary, limited data. This is overclaim.

**Key Claims:**
- The article makes a causal claim ('AI is making teachers obsolete') based on correlational pilot data without control groups.
- Preliminary findings from small, non-representative samples are presented as 'data-backed reality' applicable to all subjects.
- Specific metrics (65% rise, two-times effect) are cited without source, confidence intervals, or replication evidence.
- Novelty effects, selection bias, and teacher-quality confounds are not acknowledged.
- The scope of the conclusion (all subjects, all contexts) far exceeds the scope of the evidence (two countries, three subjects, pilot stage).

**Alternative Hypotheses:**
- mechanism_vs_evidence: If the article had been more cautious in tone ('early evidence suggests AI tutoring may improve outcomes in some contexts; more research needed'), the classification would shift to mechanism_vs_evidence. However, the promotional language and sweeping conclusions push this into overclaim territory.
- correlation_vs_causation: The article does not establish causation (no control groups mentioned), but this is subsumed under the broader overclaim problem.

**Uncertainties:**
- Whether the pilot programs included randomized controls or matched comparison groups (the article does not specify; I am assuming they did not, which is typical for early-stage pilots).
- The actual sample sizes, demographic composition, and dropout rates of the pilots (not provided).
- Whether the 65% and 'two-times' figures are from peer-reviewed sources or promotional materials from AI vendors.
- Whether the article is reporting on a single study or aggregating results across multiple pilots (the vague 'some reports' language suggests the latter, which increases heterogeneity and reduces reliability).

**Self-Verification:**
- Did I overstate the problems? No. The article explicitly claims teacher roles are being 'dismantled' and AI represents a 'data-backed reality' — these are strong causal and universal claims unsupported by pilot data.
- Did I miss a solid study? No. The article cites 'pilot programs' without methodological detail, which is a red flag for limited-stage research.
- Did I conflate tone with evidence? No. I classified based on the gap between evidence tier (limited human pilots) and conclusion tier (universal policy claim), plus the promotional language that actively sells the conclusion.
- Is this overclaim or mechanism_vs_evidence? Overclaim, because the text actively sells a breakthrough ('dismantled,' 'data-backed reality') rather than cautiously exploring a mechanism. The rhetorical inflation is the primary forensic finding.

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.7/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 4.2/6 `#######...`
- Uncertainty Handling: 3.6/6 `######....`
- Alternative Hypothesis Quality: 6.0/6 `##########`
- Self Monitoring Quality: 4.8/8 `######....`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 8.5/10 `########..`


## Final Verdict

**Solo run: Claude Haiku** scored **72.1/100**.

**Best per dimension:**
- Correctness: Claude Haiku (30.0/30)
- Support Strength: Claude Haiku (0.7/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (4.2/6)
- Uncertainty Handling: Claude Haiku (3.6/6)
- Alternative Hypothesis Quality: Claude Haiku (6.0/6)
- Self Monitoring Quality: Claude Haiku (4.8/8)
- Insight Depth: Claude Haiku (8.0/8)
- Mechanism Quality: Claude Haiku (1.5/10)
- Communication Efficiency: Claude Haiku (8.5/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 15.4s | 72.1/100 | 4.7 |

Failure modes observed: decorative_uncertainty, named_not_explained, unsupported_intermediate_step.
