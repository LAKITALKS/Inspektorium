# Forensic Dossier: Simpson's Paradox: University Admissions

**Run ID:** `run_d634d3cf`  
**Task:** simpsons-paradox-001 | statistics | hard | rubric_based  
**Timestamp:** 2026-03-31T08:23:09.917516+00:00  
**Task Family:** statistical_paradox  
**Trap Type:** aggregation_reversal  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Opus, Claude Sonnet, Claude Haiku
**Winner:** Claude Sonnet — **90.5/100** (margin: 1.7)
**Failure modes detected:** confidence_mismatch
**Answer convergence:** agents diverge (3 distinct answers)
**Consistency findings:** 3 total (0 failures)

## Score Matrix

| Agent | Correctness | Structural Reaso | Assumption Disci | Uncertainty Cali | Alternative Hypo | Self Verificatio | Insight Depth | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Opus | 25.0/25 | 12.0/15 | 10.0/10 | 6.5/10 | 10.0/10 | 6.0/10 | 8.0/10 | 8.5/10 | **86.0/100** |
| Claude Sonnet | 25.0/25 | 12.0/15 | 10.0/10 | 9.0/10 | 10.0/10 | 6.0/10 | 10.0/10 | 8.5/10 | **90.5/100** |
| Claude Haiku | 25.0/25 | 12.8/15 | 10.0/10 | 7.5/10 | 10.0/10 | 6.0/10 | 9.0/10 | 8.5/10 | **88.8/100** |

## Evidence Map

Each score is bound to concrete evidence from the agent's output.

### Claude Opus

**Correctness:** 25.0/25
  - `(matched in output)`: "66%, this is due to simpson's paradox. women actually hav"
    _Rubric criterion: identifies simpson paradox_
  - `(matched in output)`: "women now examining department-level admission rates: en"
    _Rubric criterion: per-department analysis_
  - `(matched in output)`: "than men analyzing application patterns: 20% (100/500) of"
    _Rubric criterion: selection bias in applications_
  - Note: Rubric hit: identifies simpson paradox
  - Note: Rubric hit: per-department analysis

**Structural Reasoning:** 12.0/15
  - `steps[8]`: "This is Simpson's Paradox: aggregated data shows opposite trend from disaggregated data because of different distributio"
    _Most detailed reasoning step_
  - `steps[5]`: "In both departments, women have higher admission rates than men"
    _Briefest reasoning step_
  - Note: 10 reasoning steps
  - Note: Steps are detailed (avg 106 chars)

**Assumption Discipline:** 10.0/10
  - `assumptions[3]`: "Admission decisions within each department use consistent criteria"
    _Most substantive assumption_
  - Note: 5/5 substantive assumptions

**Uncertainty Calibration:** 6.5/10
  - `uncertainties[1]`: "There could be other factors affecting admission decisions not captured in these statistics"
    _Most substantive uncertainty_
  - `confidence`: "confidence: 0.95"
    _Stated confidence level_
  - Note: 5 uncertainties (5 substantive)
  - Note: Confidence 0.95 — very high

**Alternative Hypothesis Awareness:** 10.0/10
  - `alternative_hypotheses[2]`: "The departments might have different standards that inadvertently favor women - rejected because both departments indepe"
    _Most substantive alternative hypothesis_
  - Note: 4 alternative hypotheses considered
  - Note: 4/4 include rejection reasoning

**Self Verification Quality:** 6.0/10
  - `self_check[1]`: "Confirmed this is indeed Simpson's Paradox by checking that both departments favor women while overall appears to favor "
    _Most substantive self-verification step_
  - Note: 5 self-check items

**Communication Efficiency:** 8.5/10
  - Note: Signal density: 0.77, 582 words

**Insight Depth:** 8.0/10
  - `(output text)`: "vs men at 66%, this is due to simpson's paradox. women actually hav"
    _Insight 'simpson' matched (exact)_
  - `(output text)`: "66%, this is due to simpson's paradox. women actually have equal or"
    _Insight 'paradox' matched (exact)_
  - Note: Key insights: 4 full / 5

### Claude Sonnet

**Correctness:** 25.0/25
  - `(matched in output)`: "classic example of simpson's paradox. while women have a"
    _Rubric criterion: identifies simpson paradox_
  - `(matched in output)`: "titive rates within each department the data is flawed"
    _Rubric criterion: per-department analysis_
  - `(matched in output)`: "ly due to different application patterns rather than discri"
    _Rubric criterion: selection bias in applications_
  - Note: Rubric hit: identifies simpson paradox
  - Note: Rubric hit: per-department analysis

**Structural Reasoning:** 12.0/15
  - `steps[1]`: "I noticed that in both individual departments, the gender gap is relatively small (10-12.5 percentage points), but the o"
    _Most detailed reasoning step_
  - `steps[4]`: "Engineering has much lower admission rates overall (33.3%) compared to Arts (81.25%)"
    _Briefest reasoning step_
  - Note: 7 reasoning steps
  - Note: Steps are detailed (avg 129 chars)

**Assumption Discipline:** 10.0/10
  - `assumptions[2]`: "Department choice is a relevant factor to consider when evaluating discrimination"
    _Most substantive assumption_
  - Note: 4/4 substantive assumptions

**Uncertainty Calibration:** 9.0/10
  - `uncertainties[0]`: "Whether there are other departments not mentioned that could affect the analysis"
    _Most substantive uncertainty_
  - `confidence`: "confidence: 0.3"
    _Stated confidence level_
  - Note: 4 uncertainties (4 substantive)
  - Note: Confidence 0.3 — appropriately cautious for hard task

**Alternative Hypothesis Awareness:** 10.0/10
  - `alternative_hypotheses[0]`: "The university does discriminate against men - rejected because men actually have competitive rates within each departme"
    _Most substantive alternative hypothesis_
  - Note: 4 alternative hypotheses considered
  - Note: 4/4 include rejection reasoning

**Self Verification Quality:** 6.0/10
  - `self_check[4]`: "Let me reconsider: if women outperform men in both departments AND overall, this suggests possible discrimination agains"
    _Most substantive self-verification step_
  - Note: 5 self-check items

**Communication Efficiency:** 8.5/10
  - Note: Signal density: 0.74, 521 words

**Insight Depth:** 10.0/10
  - `(output text)`: "this is a classic example of simpson's paradox. while women have a"
    _Insight 'simpson' matched (exact)_
  - `(output text)`: "classic example of simpson's paradox. while women have a higher ov"
    _Insight 'paradox' matched (exact)_
  - `(output text)`: "rejected because this ignores confounding variables whether there are o"
    _Insight 'confounding' matched (exact)_
  - Note: Key insights: 5 full / 5

### Claude Haiku

**Correctness:** 25.0/25
  - `(matched in output)`: "classic example of simpson's paradox. while the overall"
    _Rubric criterion: identifies simpson paradox_
  - `(matched in output)`: "tell us whether the department-level disparities (women"
    _Rubric criterion: per-department analysis_
  - `(matched in output)`: "lained by different application patterns across departments"
    _Rubric criterion: selection bias in applications_
  - Note: Rubric hit: identifies simpson paradox
  - Note: Rubric hit: per-department analysis

**Structural Reasoning:** 12.8/15
  - `steps[5]`: "6. Calculate expected rates if composition were equal: Men applied more heavily to the harder department (Engineering, 3"
    _Most detailed reasoning step_
  - `steps[2]`: "3. Examine admission rates within Arts: Men 300/400 = 75%, Women 350/400 = 87.5%. Women admitted at HIGHER rate."
    _Briefest reasoning step_
  - Note: 7 reasoning steps
  - Note: Steps are detailed (avg 145 chars)

**Assumption Discipline:** 10.0/10
  - `assumptions[3]`: "Applicant qualifications are roughly comparable within each department (we're not told otherwise)"
    _Most substantive assumption_
  - Note: 5/5 substantive assumptions

**Uncertainty Calibration:** 7.5/10
  - `uncertainties[1]`: "We don't have information about applicant qualifications, GPA, test scores, etc. — if women applicants were systematical"
    _Most substantive uncertainty_
  - `confidence`: "confidence: 0.92"
    _Stated confidence level_
  - Note: 4 uncertainties (4 substantive)
  - Note: Confidence 0.92

**Alternative Hypothesis Awareness:** 10.0/10
  - `alternative_hypotheses[2]`: "Women are more qualified applicants: POSSIBLE but irrelevant to the journalist's claim. The claim is about discriminatio"
    _Most substantive alternative hypothesis_
  - Note: 3 alternative hypotheses considered
  - Note: 3/3 include rejection reasoning

**Self Verification Quality:** 6.0/10
  - `self_check[0]`: "Verified arithmetic: 30/100=30%, 20/50=40%, 300/400=75%, 350/400=87.5%, 330/500=66%, 370/450=82.2% ✓"
    _Most substantive self-verification step_
  - Note: 6 self-check items

**Communication Efficiency:** 8.5/10
  - Note: Signal density: 0.76, 621 words

**Insight Depth:** 9.0/10
  - `(output text)`: "this is a classic example of simpson's paradox. while the overall"
    _Insight 'simpson' matched (exact)_
  - `(output text)`: "classic example of simpson's paradox. while the overall statistics"
    _Insight 'paradox' matched (exact)_
  - Note: Key insights: 4 full + 1 partial / 5


## Reasoning Profiles

### Claude Opus (claude-opus-4-20250514)
**Parse OK:** True | **Latency:** 30864ms

**Final Answer:** No, the claim is not valid. While the overall admission rates show women at 82.2% vs men at 66%, this is due to Simpson's Paradox. Women actually have equal or lower admission rates than men in each individual department (Engineering: 40% vs 30% favoring women; Arts: 87.5% vs 75% favoring women). The overall difference occurs because men disproportionately applied to the more competitive Engineering department (100/500 = 20% of male applicants) while women disproportionately applied to the less competitive Arts department (400/450 = 89% of female applicants). The data actually suggests possible discrimination in favor of women within departments, not against men.

**Confidence:** 0.95

**Assumptions:**
- The provided numbers are accurate and complete
- These are the only two departments at the university
- All applicants applied to exactly one department
- Admission decisions within each department use consistent criteria
- The sample sizes are representative of typical admission patterns

**Reasoning Steps:**
1. First, I'll verify the given numbers add up correctly: Engineering (30+20=50 admitted out of 150 total), Arts (300+350=650 admitted out of 800 total)
2. Total men: 100 (Eng) + 400 (Arts) = 500; Total women: 50 (Eng) + 400 (Arts) = 450
3. Total admitted men: 30 + 300 = 330; Total admitted women: 20 + 350 = 370
4. Overall rates check out: 330/500 = 66% for men, 370/450 = 82.2% for women
5. Now examining department-level admission rates: Engineering admits 30% of men vs 40% of women; Arts admits 75% of men vs 87.5% of women
6. In both departments, women have higher admission rates than men
7. Analyzing application patterns: 20% (100/500) of men applied to Engineering vs only 11% (50/450) of women
8. Engineering has much lower admission rates (33.3% overall) compared to Arts (81.25% overall)
9. This is Simpson's Paradox: aggregated data shows opposite trend from disaggregated data because of different distribution of applicants across departments
10. The apparent discrimination against men in overall numbers is actually due to men's higher tendency to apply to the more selective department

**Key Claims:**
- Women have higher admission rates than men in both individual departments
- Men applied to Engineering at nearly twice the rate of women (20% vs 11%)
- Engineering has a much lower overall admission rate than Arts (33.3% vs 81.25%)
- Simpson's Paradox explains why aggregate data shows opposite pattern from department-level data
- The data suggests possible favoritism toward women at the department level, not discrimination against men

**Alternative Hypotheses:**
- The journalist's claim could be valid if we only look at overall numbers without context - rejected because this ignores the crucial department-level data
- There might be discrimination against men in application encouragement - possible but not supported by the admission data itself
- The departments might have different standards that inadvertently favor women - rejected because both departments independently show higher admission rates for women
- This could be random variation - unlikely given the consistent pattern across both departments

**Uncertainties:**
- We don't know why men disproportionately applied to Engineering
- There could be other factors affecting admission decisions not captured in these statistics
- We don't know if these patterns are consistent across years
- The quality or qualifications of applicants in each pool is unknown
- There might be other departments not included in this data

**Self-Verification:**
- Verified all arithmetic: 30+20=50, 300+350=650, 100+400=500, 50+400=450
- Confirmed this is indeed Simpson's Paradox by checking that both departments favor women while overall appears to favor men
- Double-checked the application distribution calculation: 100/500 = 0.2 for men to Engineering, 50/450 = 0.111 for women
- Verified that the reversal is due to different application patterns, not calculation errors
- Confirmed that my conclusion addresses the specific claim about discrimination against men

**Dimension Scores:**
- Correctness: 25.0/25 `##########`
- Structural Reasoning: 12.0/15 `#######...`
- Assumption Discipline: 10.0/10 `##########`
- Uncertainty Calibration: 6.5/10 `######....`
- Alternative Hypothesis Awareness: 10.0/10 `##########`
- Self Verification Quality: 6.0/10 `######....`
- Insight Depth: 8.0/10 `########..`
- Communication Efficiency: 8.5/10 `########..`

### Claude Sonnet (claude-sonnet-4-20250514)
**Parse OK:** True | **Latency:** 21209ms

**Final Answer:** The journalist's claim is not valid. This is a classic example of Simpson's Paradox. While women have a higher overall admission rate (82.2% vs 66%), men actually have higher admission rates within each individual department when we control for department choice. The apparent discrimination against men disappears when we account for the fact that men disproportionately applied to Engineering (which has much lower admission rates) while women applied more evenly across departments.

**Confidence:** 0.3

**Assumptions:**
- The data provided is accurate and complete
- There are only these two departments at the university
- Department choice is a relevant factor to consider when evaluating discrimination
- Simpson's Paradox principles apply to this scenario

**Reasoning Steps:**
1. First, I verified the given statistics: Engineering admits 30% of men vs 40% of women; Arts admits 75% of men vs 87.5% of women; Overall: 66% of men vs 82.2% of women
2. I noticed that in both individual departments, the gender gap is relatively small (10-12.5 percentage points), but the overall gap is much larger (16.2 percentage points)
3. I calculated the application distribution: Men applied 100 to Engineering + 400 to Arts = 500 total; Women applied 50 to Engineering + 400 to Arts = 450 total
4. I observed that men applied to Engineering at twice the rate of women (20% vs 11.1% of their respective totals)
5. Engineering has much lower admission rates overall (33.3%) compared to Arts (81.25%)
6. The overall disparity is explained by men's higher application rate to the more selective Engineering department
7. This is a textbook case of Simpson's Paradox where aggregate data reverses the trend seen in subgroups

**Key Claims:**
- Men have higher admission rates than women in Engineering (30% vs 40% - actually women are higher here, I need to recheck)
- Actually: Women have higher rates in both departments (40% vs 30% in Engineering, 87.5% vs 75% in Arts)
- Men applied disproportionately to the more selective Engineering department
- The overall disparity is primarily due to different application patterns rather than discrimination
- This demonstrates Simpson's Paradox

**Alternative Hypotheses:**
- The university does discriminate against men - rejected because men actually have competitive rates within each department
- The data is flawed or incomplete - possible but we must work with given information
- There are other unmeasured factors causing the disparity - possible but department choice alone explains the paradox
- The journalist's claim is valid because overall rates matter most - rejected because this ignores confounding variables

**Uncertainties:**
- Whether there are other departments not mentioned that could affect the analysis
- Whether department choice itself might reflect some form of institutional bias
- Whether there are other confounding variables not captured in this data
- The temporal aspect - whether these patterns hold over time

**Self-Verification:**
- Rechecked all calculations: Engineering 30/100 men (30%), 20/50 women (40%); Arts 300/400 men (75%), 350/400 women (87.5%)
- Verified that women actually have higher admission rates in BOTH departments, not men as I initially stated
- Confirmed the paradox: women do better in each department individually AND overall
- Wait - this means the journalist's claim about discrimination against men is actually supported by the departmental data too
- Let me reconsider: if women outperform men in both departments AND overall, this suggests possible discrimination against men, not a statistical artifact

**Dimension Scores:**
- Correctness: 25.0/25 `##########`
- Structural Reasoning: 12.0/15 `#######...`
- Assumption Discipline: 10.0/10 `##########`
- Uncertainty Calibration: 9.0/10 `#########.`
- Alternative Hypothesis Awareness: 10.0/10 `##########`
- Self Verification Quality: 6.0/10 `######....`
- Insight Depth: 10.0/10 `##########`
- Communication Efficiency: 8.5/10 `########..`

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 14511ms

**Final Answer:** The journalist's claim is NOT valid. This is a classic example of Simpson's Paradox. While the overall statistics show women had a higher admission rate (82.2% vs 66%), men were actually admitted at higher rates in BOTH departments individually (Engineering: 30% vs 40%, Arts: 75% vs 87.5%). The overall disparity is caused by the different composition of applicants across departments, not discrimination. Women applied disproportionately to Arts (a high-acceptance department), while men applied disproportionately to Engineering (a low-acceptance department).

**Confidence:** 0.92

**Assumptions:**
- The admission decisions within each department are independent of the overall statistics
- We are evaluating discrimination based on admission rates within comparable groups (departments)
- The data provided is accurate and complete
- Applicant qualifications are roughly comparable within each department (we're not told otherwise)
- The departments have different acceptance standards/selectivity

**Reasoning Steps:**
1. 1. Verify the overall statistics: (30+300)/(100+400) = 330/500 = 66% for men ✓; (20+350)/(50+400) = 370/450 = 82.2% for women ✓
2. 2. Examine admission rates within Engineering: Men 30/100 = 30%, Women 20/50 = 40%. Women admitted at HIGHER rate.
3. 3. Examine admission rates within Arts: Men 300/400 = 75%, Women 350/400 = 87.5%. Women admitted at HIGHER rate.
4. 4. Recognize the paradox: Women have higher rates in both departments, yet lower overall rate for men. This seems contradictory.
5. 5. Analyze the composition: Men: 100 to Engineering, 400 to Arts (20% to low-acceptance dept). Women: 50 to Engineering, 400 to Arts (11.1% to low-acceptance dept).
6. 6. Calculate expected rates if composition were equal: Men applied more heavily to the harder department (Engineering, 30% acceptance). Women applied more heavily to the easier department (Arts, 87.5% acceptance).
7. 7. Conclude: The overall disparity is entirely explained by different application patterns across departments, not by differential treatment within departments.

**Key Claims:**
- Simpson's Paradox: A trend can reverse when data is aggregated vs. disaggregated
- Men have higher admission rates in Engineering (30% vs 40% is actually lower — correction: women have 40% vs men's 30%, so women higher)
- Men have higher admission rates in Arts (75% vs 87.5% is actually lower — women have 87.5% vs men's 75%, so women higher)
- The overall disparity is caused by compositional differences: men applied more to the harder department
- Within-department analysis is the appropriate way to detect discrimination, not overall statistics

**Alternative Hypotheses:**
- The journalist is correct and the university discriminates against men: REJECTED because men have higher admission rates in both departments individually. The overall statistic is misleading due to compositional differences.
- There is genuine discrimination but it's hidden in the data: REJECTED because we can see the mechanism clearly — it's Simpson's Paradox, not hidden bias. The within-department rates are transparent.
- Women are more qualified applicants: POSSIBLE but irrelevant to the journalist's claim. The claim is about discrimination in the admission process itself, not about applicant quality. Even if true, it wouldn't validate the journalist's reasoning.

**Uncertainties:**
- We don't know if applicants were self-selected into departments based on expected acceptance rates, which could indicate prior discrimination
- We don't have information about applicant qualifications, GPA, test scores, etc. — if women applicants were systematically more qualified, that could explain the pattern legitimately
- We don't know if the departments have different admission standards or if one is more selective than the other by design
- The data doesn't tell us whether the department-level disparities (women favored in both) represent actual discrimination or reflect legitimate differences in qualifications

**Self-Verification:**
- Verified arithmetic: 30/100=30%, 20/50=40%, 300/400=75%, 350/400=87.5%, 330/500=66%, 370/450=82.2% ✓
- Confirmed women have higher rates in BOTH departments ✓
- Confirmed men have lower overall rate despite higher rates in both departments ✓
- Identified the mechanism: compositional difference (men 80% to Arts, women 88.9% to Arts) ✓
- Checked for logical consistency: Simpson's Paradox is a well-known statistical phenomenon ✓
- Verified this is not about absolute numbers but rates within comparable groups ✓

**Dimension Scores:**
- Correctness: 25.0/25 `##########`
- Structural Reasoning: 12.8/15 `########..`
- Assumption Discipline: 10.0/10 `##########`
- Uncertainty Calibration: 7.5/10 `#######...`
- Alternative Hypothesis Awareness: 10.0/10 `##########`
- Self Verification Quality: 6.0/10 `######....`
- Insight Depth: 9.0/10 `#########.`
- Communication Efficiency: 8.5/10 `########..`


## Failure Analysis

### Claude Opus

**MINOR:**
- **Confidence Mismatch**: Very high confidence (0.95) on hard task
  - `confidence`: "confidence: 0.95"
  - _Impacts: uncertainty_calibration_

**Failure Mode Summary:**
- Confidence Mismatch: Claude Opus


## Consistency Report

### Claude Opus

- **[WARN]** `confidence_uncertainty`: Confidence 0.95 is very high despite listing 5 uncertainties — possible performative calibration
  - `confidence`: "confidence: 0.95"
  - `uncertainties[0]`: "We don't know why men disproportionately applied to Engineering"
- **[NOTE]** `confidence_uncertainty`: Confidence 0.95 on a hard task — may indicate miscalibration
  - `confidence`: "confidence: 0.95"

### Claude Haiku

- **[WARN]** `claim_step_alignment`: Key claim 1 not well supported in reasoning steps (1/6 content words found)
  - `key_claims[0]`: "Simpson's Paradox: A trend can reverse when data is aggregated vs. disaggregated"


## Divergence Analysis

### Answer Divergence
- **Claude Opus:** No, the claim is not valid. While the overall admission rates show women at 82.2% vs men at 66%, this is due to Simpson's Paradox. Women actually have equal or lower admission rates than men in each individual department (Engineering: 40% vs 30% favoring women; Arts: 87.5% vs 75% favoring women). The overall difference occurs because men disproportionately applied to the more competitive Engineering department (100/500 = 20% of male applicants) while women disproportionately applied to the less competitive Arts department (400/450 = 89% of female applicants). The data actually suggests possible discrimination in favor of women within departments, not against men.
- **Claude Sonnet:** The journalist's claim is not valid. This is a classic example of Simpson's Paradox. While women have a higher overall admission rate (82.2% vs 66%), men actually have higher admission rates within each individual department when we control for department choice. The apparent discrimination against men disappears when we account for the fact that men disproportionately applied to Engineering (which has much lower admission rates) while women applied more evenly across departments.
- **Claude Haiku:** The journalist's claim is NOT valid. This is a classic example of Simpson's Paradox. While the overall statistics show women had a higher admission rate (82.2% vs 66%), men were actually admitted at higher rates in BOTH departments individually (Engineering: 30% vs 40%, Arts: 75% vs 87.5%). The overall disparity is caused by the different composition of applicants across departments, not discrimination. Women applied disproportionately to Arts (a high-acceptance department), while men applied disproportionately to Engineering (a low-acceptance department).

### Reasoning Approach Comparison

**Claude Opus** — 10 steps, 5 assumptions, 4 alternatives, 5 uncertainties, 5 self-checks, 5 key claims
**Claude Sonnet** — 7 steps, 4 assumptions, 4 alternatives, 4 uncertainties, 5 self-checks, 5 key claims
**Claude Haiku** — 7 steps, 5 assumptions, 3 alternatives, 4 uncertainties, 6 self-checks, 5 key claims

### Key Insight Coverage

| Insight | Claude Opus | Claude Sonnet | Claude Haiku |
|-------|-------|-------|-------|
| simpson | Y | Y | Y |
| paradox | Y | Y | Y |
| aggregation | Y | Y | Y |
| confounding | - | Y | - |
| subgroup | Y | Y | Y |

### Assumption Comparison

**Claude Opus:**
- The provided numbers are accurate and complete
- These are the only two departments at the university
- All applicants applied to exactly one department
- Admission decisions within each department use consistent criteria
- The sample sizes are representative of typical admission patterns

**Claude Sonnet:**
- The data provided is accurate and complete
- There are only these two departments at the university
- Department choice is a relevant factor to consider when evaluating discrimination
- Simpson's Paradox principles apply to this scenario

**Claude Haiku:**
- The admission decisions within each department are independent of the overall statistics
- We are evaluating discrimination based on admission rates within comparable groups (departments)
- The data provided is accurate and complete
- Applicant qualifications are roughly comparable within each department (we're not told otherwise)
- The departments have different acceptance standards/selectivity


## Hidden Weaknesses

**Claude Opus:**
- Confidence 0.95 is very high despite listing 5 uncertainties — possible performative calibration [minor]
  - `confidence`: "confidence: 0.95"
  - `uncertainties[0]`: "We don't know why men disproportionately applied to Engineering"


## Latency vs Quality

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Opus | 30.9s | 86.0/100 | 2.8 |
| Claude Sonnet | 21.2s | 90.5/100 | 4.3 |
| Claude Haiku | 14.5s | 88.8/100 | 6.1 |


## Final Verdict

**Winner: Claude Sonnet** with **90.5/100** (+1.7 over Claude Haiku).

**Best per dimension:**
- Correctness: Claude Opus (25.0/25)
- Structural Reasoning: Claude Haiku (12.8/15)
- Assumption Discipline: Claude Opus (10.0/10)
- Uncertainty Calibration: Claude Sonnet (9.0/10)
- Alternative Hypothesis Awareness: Claude Opus (10.0/10)
- Self Verification Quality: Claude Opus (6.0/10)
- Insight Depth: Claude Sonnet (10.0/10)
- Communication Efficiency: Claude Opus (8.5/10)

Failure modes observed: confidence_mismatch.
