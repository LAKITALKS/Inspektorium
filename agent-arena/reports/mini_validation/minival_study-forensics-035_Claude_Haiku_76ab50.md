# Forensic Dossier: Study Forensics: AI tutors show moderate gains compared to human tutors

**Run ID:** `minival_study-forensics-035_Claude_Haiku_76ab50`  
**Task:** study-forensics-035 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T07:54:32.904559+00:00  
**Task Family:** solid  
**Trap Type:** borderline_solid_with_caveats  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **70.3/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, unsupported_conclusion, unsupported_intermediate_step, unused_assumption
**Forensic flags:** 4
**Consistency findings:** 7
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 30.0/30 | 0.0/8 | 4.8/8 | 3.8/6 | 3.6/6 | 5.2/6 | 4.8/8 | 8.0/8 | 0.0/10 | 10.0/10 | **70.3/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `solid` [+] (gold: `solid`)
**Finding Recall:** 100%
**Matched Findings:** evidence_matches_claim, cautious_scope_control
**Extra Findings:** none_or_minor, conclusion_exceeds_results, decorative_uncertainty, correlation_as_causation

## Reasoning Integrity Audit

### Claude Haiku
**Classification:** Correct but brittle reasoning
**Load-bearing steps:** 0 / 7

## Claim Verification

### Claude Haiku
Claims checked: 1 | Supported: 0 | Contradicted: 0 | Unresolved: 1

## Mechanism Analysis

### Claude Haiku
| Aspect | Status |
|--------|--------|
| Concept named | :x: none |
| Mechanism described | :x: (0 sentence(s)) |
| Grounded to case | :x: (0 sentence(s)) |

**Missing:** concept not named, mechanism not described, mechanism not grounded to case data

## Grounding Audit

### Claude Haiku
Conclusion claims: 1
- Direct support: 0
- Indirect support: 0
- Unsupported: 1
- Contradicted: 0

**Unsupported claims:**
- "solid"


## Forensic Flags

### Claude Haiku

- **[MODERATE]** `weak_mechanism`: Correct answer but weak mechanism explanation — answer may not generalize
  - `final_answer`: "solid"
- **[MAJOR]** `unsupported_leap`: Correct answer with weak support chain — final answer may be an unsupported leap
- **[MODERATE]** `unsupported_conclusion_claims`: 1/1 conclusion claims lack step support
  - `final_answer`: "solid"
- **[MINOR]** `study_forensics_overflagging`: Agent raised extra findings in solid case: none_or_minor, conclusion_exceeds_results, decorative_uncertainty, correlation_as_causation


## Evidence Map

### Claude Haiku

**Correctness:** 30.0/30
  - (+) `final_answer`: "solid"
    _Agent's answer for correctness check_
  - Note: Exact match

**Support Strength:** 0.0/8
  - (-) `final_answer`: "solid"
    _Conclusion not supported by steps_
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 7
  - Note: Reasoning graph: conclusion not well grounded

**Structural Reasoning:** 4.8/8
  - (+) `steps[4]`: "Examined uncertainty language: The text appropriately qualifies findings (e.g., 'increased by 4 percentage points' is sp"
    _Most informative reasoning step_
  - Note: 7 reasoning steps
  - Note: Low step utility: 0/7 steps contribute

**Assumption Discipline:** 3.8/6
  - (+) `assumptions[4]`: "The inexperienced tutor subgroup analysis was pre-specified or appropriately corrected for multiple comparisons"
    _Most substantive assumption_
  - (-) `assumptions[1]`: "Success rate and topic mastery are valid outcome measures for the respective studies"
    _Declared but unused in reasoning_
  - (-) `assumptions[3]`: "The studies measured short-term outcomes; long-term effects are not addressed"
    _Declared but unused in reasoning_
  - Note: 5/5 substantive assumptions
  - Note: 2 unused assumption(s)

**Uncertainty Handling:** 3.6/6
  - (+) `uncertainties[0]`: "Statistical significance of the 5-percentage-point difference (66% vs 61%) is not reported in the summary"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.78"
    _Stated confidence level_
  - (-) `uncertainties[1]`: "Sample sizes, study duration, and student demographics are not provided"
    _Listed but never addressed in reasoning_
  - Note: 5 uncertainties (5 substantive)
  - Note: 1 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 5.2/6
  - (+) `alternative_hypotheses[1]`: "The study could have confounding variables (e.g., student motivation, prior knowledge) that favor AI conditions, though "
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 1/2 include rejection reasoning

**Self Monitoring Quality:** 4.8/8
  - (+) `self_check[2]`: "Is the complementary framing justified? Yes—AI outperforms human tutoring slightly but the emphasis on complementarity i"
    _Most substantive self-verification step_
  - Note: 4 self-check items
  - Note: Self-check quality: 0 deep, 4 arithmetic, 0 fluff

**Mechanism Quality:** 0.0/10
  - Note: Neither names concept nor explains mechanism

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.74, 472 words

**Insight Depth:** 8.0/8
  - (+) `(output text)`: ", not the study itself is the complementary framing justified? yes—ai out"
    _Insight 'complementary' matched (exact)_
  - Note: Key insights: 2 full / 2


## Failure Analysis

### Claude Haiku

**MODERATE:**
- **Unsupported Conclusion** `[MEDIUM CONFIDENCE]`: Final answer lacks load-bearing or supporting step grounding
  - `final_answer`: "solid"
  - _Impacts: support_strength_
- **Unsupported Intermediate Step** `[MEDIUM CONFIDENCE]`: No reasoning step is load-bearing — final answer lacks traceable derivation
  - `final_answer`: "solid"
  - _Impacts: support_strength, structural_reasoning_

**STYLISTIC:**
- **Unused Assumption** `[HEURISTIC]`: Assumption 'Success rate and topic mastery are valid outcome measures fo...' is declared but not referenced in reasoning
  - `assumptions[1]`: "Success rate and topic mastery are valid outcome measures for the respective studies"
  - _Impacts: assumption_discipline_
- **Unused Assumption** `[HEURISTIC]`: Assumption 'The studies measured short-term outcomes; long-term effects ...' is declared but not referenced in reasoning
  - `assumptions[3]`: "The studies measured short-term outcomes; long-term effects are not addressed"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Sample sizes, study duration, and student demographics are n...' is listed but not addressed
  - `uncertainties[1]`: "Sample sizes, study duration, and student demographics are not provided"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/9 content words)
  - `key_claims[0]`: "AI tutoring achieved 66% success vs 61% for human tutoring and 56% for written hints—a modest advant"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/10 content words)
  - `key_claims[1]`: "Tutors confirmed 76.4% of AI answers without major corrections—suggests reasonable quality but not p"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/13 content words)
  - `key_claims[2]`: "AI support improved topic mastery by 4 points overall, 9 points for inexperienced tutors—indicates c"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/11 content words)
  - `key_claims[3]`: "Authors explicitly state AI complements rather than replaces human tutoring—appropriate framing give"
- **[WARN]** `[HEURISTIC]` `unused_assumption`: Assumption 4 appears unused in reasoning or answer
  - `assumptions[3]`: "The studies measured short-term outcomes; long-term effects are not addressed"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 2 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[1]`: "Sample sizes, study duration, and student demographics are not provided"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 2 is stated without rejection reasoning
  - `alternative_hypotheses[1]`: "The study could have confounding variables (e.g., student motivation, prior knowledge) that favor AI"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 15656ms

**Final Answer:** solid

**Confidence:** 0.78

**Assumptions:**
- Both studies used appropriate control groups and comparable student populations
- Success rate and topic mastery are valid outcome measures for the respective studies
- The 76.4% confirmation rate reflects actual tutor assessment rather than selection bias
- The studies measured short-term outcomes; long-term effects are not addressed
- The inexperienced tutor subgroup analysis was pre-specified or appropriately corrected for multiple comparisons

**Reasoning Steps:**
1. Examined whether causal claims are made: The text describes comparative outcomes (66% vs 61% vs 56%) without claiming causation; it presents results as comparisons between conditions
2. Checked for overclaiming: The conclusion that AI 'complements' rather than 'replaces' human tutoring is explicitly stated as a caveat and is consistent with the data (AI alone at 66% vs human at 61%)
3. Evaluated mechanism claims: No mechanistic explanations are offered; the text reports empirical outcomes only
4. Assessed confounders: The text does not discuss potential confounders, but this is typical for a summary; the study design (comparison groups) suggests awareness of this issue
5. Examined uncertainty language: The text appropriately qualifies findings (e.g., 'increased by 4 percentage points' is specific; the subgroup finding for inexperienced tutors is presented as a separate observation)
6. Checked for decorative uncertainty: No false hedging detected; claims are proportionate to evidence presented
7. Verified correlation vs. causation: The comparative design (AI vs. human vs. written hints) supports causal inference about the intervention, not merely correlation

**Key Claims:**
- AI tutoring achieved 66% success vs 61% for human tutoring and 56% for written hints—a modest advantage over human tutoring
- Tutors confirmed 76.4% of AI answers without major corrections—suggests reasonable quality but not perfection
- AI support improved topic mastery by 4 points overall, 9 points for inexperienced tutors—indicates complementary role, especially for less-skilled tutors
- Authors explicitly state AI complements rather than replaces human tutoring—appropriate framing given the data

**Alternative Hypotheses:**
- The study could be overclaiming if the 66% vs 61% difference is not statistically significant (not stated in summary)
- The study could have confounding variables (e.g., student motivation, prior knowledge) that favor AI conditions, though the comparative design mitigates this

**Uncertainties:**
- Statistical significance of the 5-percentage-point difference (66% vs 61%) is not reported in the summary
- Sample sizes, study duration, and student demographics are not provided
- Whether the 76.4% confirmation rate reflects high quality or merely agreement with AI outputs
- Whether the 4-point and 9-point improvements in the second study are statistically significant
- Whether the inexperienced tutor subgroup analysis was pre-registered or represents post-hoc exploration

**Self-Verification:**
- Did I overidentify problems? No—the text is appropriately cautious and does not make unsupported causal claims
- Did I miss red flags? The lack of statistical significance reporting is a limitation of the summary, not the study itself
- Is the complementary framing justified? Yes—AI outperforms human tutoring slightly but the emphasis on complementarity is reasonable given modest margins
- Are the subgroup findings concerning? The 9-point advantage for inexperienced tutors is interesting but not overclaimed; it's presented as an observation

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 0.0/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 3.8/6 `######....`
- Uncertainty Handling: 3.6/6 `######....`
- Alternative Hypothesis Quality: 5.2/6 `########..`
- Self Monitoring Quality: 4.8/8 `######....`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 0.0/10 `..........`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Haiku** scored **70.3/100**.

**Best per dimension:**
- Correctness: Claude Haiku (30.0/30)
- Support Strength: Claude Haiku (0.0/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (3.8/6)
- Uncertainty Handling: Claude Haiku (3.6/6)
- Alternative Hypothesis Quality: Claude Haiku (5.2/6)
- Self Monitoring Quality: Claude Haiku (4.8/8)
- Insight Depth: Claude Haiku (8.0/8)
- Mechanism Quality: Claude Haiku (0.0/10)
- Communication Efficiency: Claude Haiku (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 15.7s | 70.3/100 | 4.5 |

Failure modes observed: decorative_uncertainty, unsupported_conclusion, unsupported_intermediate_step, unused_assumption.
