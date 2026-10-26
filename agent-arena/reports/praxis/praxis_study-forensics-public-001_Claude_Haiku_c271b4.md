# Forensic Dossier: Study Forensics: Vigorous Exercise and 8 Major Diseases — Correlation Sold as Intervention

**Run ID:** `praxis_study-forensics-public-001_Claude_Haiku_c271b4`  
**Task:** study-forensics-public-001 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-07T07:58:53.991301+00:00  
**Task Family:** correlation_vs_causation  
**Trap Type:** causal_framing_of_observational_data  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **38.4/100** (margin: 0.0)
**Failure modes:** decorative_uncertainty, missed_key_insight, named_not_explained, oververbose_without_gain, unused_assumption, wrong_answer
**Forensic flags:** 3
**Consistency findings:** 7
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 0.0/30 | 0.7/8 | 4.8/8 | 3.7/6 | 3.6/6 | 5.5/6 | 5.6/8 | 6.0/8 | 1.5/10 | 7.0/10 | **38.4/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `overclaim` [x] (gold: `correlation_vs_causation`)
**Finding Recall:** 50%
**Matched Findings:** correlation_as_causation
**Missed Findings:** unsupported_generalization
**Extra Findings:** cautious_scope_control, none_or_minor, conclusion_exceeds_results, decorative_uncertainty, mechanism_not_demonstrated

## Reasoning Integrity Audit

### Claude Haiku
**Classification:** Correct and well-supported
**Load-bearing steps:** 0 / 9

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

- **[MAJOR]** `well_reasoned_wrong`: Wrong answer but structured reasoning — may have a subtle logic error
  - `final_answer`: "overclaim"
- **[MODERATE]** `unsupported_conclusion_claims`: 1/1 conclusion claims lack step support
  - `final_answer`: "overclaim"
- **[MODERATE]** `ungrounded_mechanism`: Mechanism named/described but not connected to case-specific data
  - `(mechanism analysis)`: "bias, effect"


## Evidence Map

### Claude Haiku

**Correctness:** 0.0/30
  - (+) `final_answer`: "overclaim"
    _Agent's answer for correctness check_
  - Note: No match (got: overclaim)

**Support Strength:** 1.2/8
  - (+) `final_answer`: "overclaim"
    _Conclusion grounded by reasoning chain_
  - Note: Support classification: 0 load-bearing, 0 supporting, 0 mentioned / 9
  - Note: Reasoning graph confirms conclusion grounding

**Structural Reasoning:** 4.8/8
  - (+) `steps[6]`: "7. Examined the 4.5-minute claim: Prof. Stamatakis's quote specifies '4.5 minutes are associated with approximately 35-5"
    _Most informative reasoning step_
  - Note: 9 reasoning steps
  - Note: Low step utility: 0/9 steps contribute

**Assumption Discipline:** 3.7/6
  - (+) `assumptions[2]`: "The study used appropriate statistical methods for observational data (e.g., Cox proportional hazards models with adjust"
    _Most substantive assumption_
  - (-) `assumptions[4]`: "The follow-up period of ~7 years is sufficient to detect incident disease"
    _Declared but unused in reasoning_
  - Note: 6/6 substantive assumptions
  - Note: Many assumptions (6)

**Uncertainty Handling:** 3.6/6
  - (+) `uncertainties[2]`: "The exact wording of author quotes — whether Prof. Shen and Prof. Stamatakis's statements in media are direct quotes or "
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.78"
    _Stated confidence level_
  - (-) `uncertainties[0]`: "Whether the original paper's statistical methods adequately controlled for confounding (e.g., propensity score matching,"
    _Listed but never addressed in reasoning_
  - Note: 5 uncertainties (5 substantive)
  - Note: 1 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 5.5/6
  - (+) `alternative_hypotheses[0]`: "The study could be classified as 'solid' if the media coverage is viewed as appropriately hedged (use of 'may,' 'could,'"
    _Most substantive alternative hypothesis_
  - Note: 3 alternative hypotheses considered
  - Note: 2/3 include rejection reasoning

**Self Monitoring Quality:** 5.6/8
  - (+) `self_check[2]`: "Did I correctly identify the locus of the problem? Yes — the study is methodologically sound but observational. The over"
    _Most substantive self-verification step_
  - Note: 5 self-check items
  - Note: Self-check quality: 0 deep, 5 arithmetic, 0 fluff

**Mechanism Quality:** 1.5/10
  - Note: Names concept but does not describe mechanism

**Communication Efficiency:** 7.0/10
  - Note: Signal density: 0.67, 964 words
  - Note: Verbose (964 words)

**Insight Depth:** 6.0/8
  - (+) `(output text)`: "study is well-designed for an observational study and the authors appropriately"
    _Insight 'observational study' matched (exact)_
  - (+) `(output text)`: "by observational data alone. reverse causation (healthier people do more vig"
    _Insight 'reverse causation' matched (exact)_
  - (?) `(not found)`: "Missing: healthy user bias"
    _Insight 'healthy user bias' not found_
  - Note: Key insights: 3 full / 4


## Failure Analysis

### Claude Haiku

**CRITICAL:**
- **Wrong Answer** `[HIGH CONFIDENCE]`: Answer does not match expected 'correlation_vs_causation'
  - `final_answer`: "overclaim"
  - _Impacts: correctness_

**MAJOR:**
- **Wrong Answer** `[HIGH CONFIDENCE]`: Study classification incorrect: expected 'correlation_vs_causation', detected 'overclaim'
  - `final_answer`: "overclaim"
  - _Impacts: correctness_

**MODERATE:**
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Names the phenomenon but does not explain the causal mechanism
  - `final_answer`: "overclaim"
  - _Impacts: mechanism_quality_
- **Named Not Explained** `[MEDIUM CONFIDENCE]`: Named concept(s) ['bias', 'effect'] but mechanism not described
  - _Impacts: mechanism_quality, insight_depth_
- **Missed Key Insight** `[MEDIUM CONFIDENCE]`: Missed expected finding: unsupported_generalization
  - `(task expectation)`: "Expected: unsupported_generalization"
  - _Impacts: insight_depth_

**STYLISTIC:**
- **Unused Assumption** `[HEURISTIC]`: Assumption 'The follow-up period of ~7 years is sufficient to detect inc...' is declared but not referenced in reasoning
  - `assumptions[4]`: "The follow-up period of ~7 years is sufficient to detect incident disease"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Whether the original paper's statistical methods adequately ...' is listed but not addressed
  - `uncertainties[0]`: "Whether the original paper's statistical methods adequately controlled for confounding (e.g., propen"
  - _Impacts: uncertainty_handling_
- **Oververbose Without Gain** `[HEURISTIC]`: Output is verbose (964 words, density 0.67)
  - `(computed)`: "964 words, density 0.67"
  - _Impacts: communication_efficiency_


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (0/11 content words)
  - `key_claims[0]`: "The study is observational and cannot prove causation — this is correctly stated in the paper but un"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/18 content words)
  - `key_claims[1]`: "The associations are substantial (29-63% lower risk) but are relative risk reductions in a populatio"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (1/23 content words)
  - `key_claims[2]`: "The claim that '4.5 minutes per day' or '15-20 minutes per week' of vigorous activity is sufficient "
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/16 content words)
  - `key_claims[3]`: "Media headlines emphasize simplicity and magnitude ('just a few minutes,' 'slash your risk') in ways"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 5 has low overlap with final answer (0/13 content words)
  - `key_claims[4]`: "The paper's stated limitations are appropriate but the media coverage and author quotes do not propo"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 2 is stated without rejection reasoning
  - `alternative_hypotheses[1]`: "The study could be 'correlation_vs_causation' if the focus is on the media's implicit causal framing"
- **[WARN]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Phenomenon is named but causal mechanism is not explained
  - `final_answer`: "overclaim"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 19851ms

**Final Answer:** overclaim

**Confidence:** 0.78

**Assumptions:**
- The study is a legitimate prospective cohort study published in a peer-reviewed journal with stated limitations
- The media headlines and quotes are accurately representing or paraphrasing the study findings
- The study used appropriate statistical methods for observational data (e.g., Cox proportional hazards models with adjustments)
- The 'vigorous activity' definition is operationally clear in the original paper
- The follow-up period of ~7 years is sufficient to detect incident disease
- The stated limitations in the paper are genuine acknowledgments by the authors

**Reasoning Steps:**
1. 1. Identified the study design: prospective observational cohort with two data sources (accelerometer n~96k, self-report n~376k). This is appropriate for generating hypotheses but cannot establish causation.
2. 2. Examined the key claims: 29-63% lower risk of 8 diseases associated with >4% vigorous activity. These are relative risk reductions from observational data.
3. 3. Checked stated limitations: Authors explicitly acknowledge observational design cannot prove causation, UK Biobank selection bias, 7-day accelerometer capture may not reflect habitual patterns, and residual confounding.
4. 4. Analyzed media framing: Headlines use language like 'could lower,' 'may slash,' and 'could lower' — these contain appropriate hedging. However, the framing emphasizes the magnitude of benefit and simplicity ('just a few minutes') in ways that may overstate the causal certainty.
5. 5. Evaluated the mechanism gap: The study shows associations between vigorous activity intensity and disease risk. Media coverage and author quotes imply a causal mechanism ('adding short bursts... can make a real difference') without acknowledging the observational limitation.
6. 6. Assessed confounding risk: Vigorous activity is strongly correlated with overall fitness, health consciousness, socioeconomic status, diet, sleep, stress, and baseline health status. Even with statistical adjustment, residual confounding is plausible. The paper acknowledges this but media does not.
7. 7. Examined the 4.5-minute claim: Prof. Stamatakis's quote specifies '4.5 minutes are associated with approximately 35-50% lower risk for cardiovascular disease.' This is a precise quantification of an association, not a causal effect. The phrasing 'are associated with' is technically correct but in media context implies actionability.
8. 8. Checked for decorative uncertainty: The paper states limitations but then the media and author quotes proceed to make actionable recommendations ('adding short bursts... can make a real difference') without proportional emphasis on the observational nature and confounding risk.
9. 9. Identified the core overclaim: The leap from 'vigorous activity is associated with lower disease risk' to 'doing vigorous activity will lower your disease risk' is not supported by observational data alone. Reverse causation (healthier people do more vigorous activity) and confounding are not ruled out.

**Key Claims:**
- The study is observational and cannot prove causation — this is correctly stated in the paper but underemphasized in media coverage.
- The associations are substantial (29-63% lower risk) but are relative risk reductions in a population with relatively low baseline disease incidence. Absolute risk reduction is not reported in the summary.
- The claim that '4.5 minutes per day' or '15-20 minutes per week' of vigorous activity is sufficient is based on observational associations, not randomized evidence. Reverse causation (healthier people exercise more) is a plausible alternative explanation.
- Media headlines emphasize simplicity and magnitude ('just a few minutes,' 'slash your risk') in ways that may overstate the causal certainty and actionability of the findings.
- The paper's stated limitations are appropriate but the media coverage and author quotes do not proportionally emphasize the observational design's limitations.

**Alternative Hypotheses:**
- The study could be classified as 'solid' if the media coverage is viewed as appropriately hedged (use of 'may,' 'could,' 'associated with') and the paper's limitations are considered sufficient disclosure. However, the gap between observational evidence and causal implication in media framing argues against this.
- The study could be 'correlation_vs_causation' if the focus is on the media's implicit causal framing of correlational findings. This is a subset of the overclaim category.
- The study could be 'mechanism_vs_evidence' if the mechanism (vigorous activity → lower disease risk) is assumed without evidence of the pathway. However, the study does not propose a specific mechanism, so this is less applicable than overclaim.

**Uncertainties:**
- Whether the original paper's statistical methods adequately controlled for confounding (e.g., propensity score matching, instrumental variables). The summary does not detail this.
- Whether the 7-day accelerometer capture is actually a major limitation or whether it correlates well with habitual activity (this is an empirical question the authors may have addressed).
- The exact wording of author quotes — whether Prof. Shen and Prof. Stamatakis's statements in media are direct quotes or paraphrases, and whether they included caveats that were edited out.
- Whether the UK Biobank selection bias is severe enough to invalidate the findings for the general population. The paper may have addressed this.
- The magnitude of residual confounding — it could be small or large relative to the observed associations.

**Self-Verification:**
- Did I overstate the problems? The study is well-designed for an observational study and the authors appropriately acknowledge limitations. However, the gap between observational evidence and causal claims in media framing is real and significant.
- Did I miss the fact that the study is solid? The study design is appropriate for its scope, but the media coverage and author quotes make causal claims that exceed the evidence. The overclaim is primarily in the communication, not the study itself.
- Did I correctly identify the locus of the problem? Yes — the study is methodologically sound but observational. The overclaim occurs in the translation to media and in author quotes that imply actionability without sufficient emphasis on confounding and reverse causation.
- Is the overclaim classification correct? Yes. The media headlines and author quotes imply that vigorous activity causes lower disease risk, when the evidence only shows association. This is an overclaim relative to the evidence.
- Did I account for appropriate hedging language? Yes — 'may,' 'could,' and 'associated with' are present, but they are insufficient given the magnitude of the causal claim implied by the context (e.g., 'adding short bursts... can make a real difference').

**Dimension Scores:**
- Correctness: 0.0/30 `..........`
- Support Strength: 0.7/8 `..........`
- Structural Reasoning: 4.8/8 `######....`
- Assumption Discipline: 3.7/6 `######....`
- Uncertainty Handling: 3.6/6 `######....`
- Alternative Hypothesis Quality: 5.5/6 `#########.`
- Self Monitoring Quality: 5.6/8 `#######...`
- Insight Depth: 6.0/8 `#######...`
- Mechanism Quality: 1.5/10 `#.........`
- Communication Efficiency: 7.0/10 `#######...`


## Final Verdict

**Solo run: Claude Haiku** scored **38.4/100**.

**Best per dimension:**
- Correctness: Claude Haiku (0.0/30)
- Support Strength: Claude Haiku (0.7/8)
- Structural Reasoning: Claude Haiku (4.8/8)
- Assumption Discipline: Claude Haiku (3.7/6)
- Uncertainty Handling: Claude Haiku (3.6/6)
- Alternative Hypothesis Quality: Claude Haiku (5.5/6)
- Self Monitoring Quality: Claude Haiku (5.6/8)
- Insight Depth: Claude Haiku (6.0/8)
- Mechanism Quality: Claude Haiku (1.5/10)
- Communication Efficiency: Claude Haiku (7.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 19.9s | 38.4/100 | 1.9 |

Failure modes observed: decorative_uncertainty, missed_key_insight, named_not_explained, oververbose_without_gain, unused_assumption, wrong_answer.
