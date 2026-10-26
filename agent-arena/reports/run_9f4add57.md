# Battle Report: Simpson's Paradox: University Admissions
**Run ID:** `run_9f4add57`  
**Task:** simpsons-paradox-001 (statistics, hard)  
**Type:** rubric_based  
**Timestamp:** 2026-03-31T06:21:26.570071+00:00

## Participating Agents

- Claude Opus (claude-opus-4-20250514)
- Claude Sonnet (claude-sonnet-4-20250514)
- Claude Haiku (claude-haiku-4-5-20251001)

## Winner
**Claude Opus (claude-opus-4-20250514)** with **100.0/100** points

## Scores

| Agent | Correctness | Reasoning | Clarity | Robustness | **Total** |
|-------|-------------|-----------|---------|------------|-----------|
| Claude Opus (claude-opus-4-20250514) | 45.0/45 | 25.0/25 | 15.0/15 | 15.0/15 | **100.0/100** |
| Claude Sonnet (claude-sonnet-4-20250514) | 45.0/45 | 25.0/25 | 15.0/15 | 15.0/15 | **100.0/100** |
| Claude Haiku (claude-haiku-4-5-20251001) | 45.0/45 | 25.0/25 | 15.0/15 | 15.0/15 | **100.0/100** |

## Agent Responses

### Claude Opus (claude-opus-4-20250514)
**Parse OK:** True | **Latency:** 13032ms

**Answer:** No, the claim is not valid. This is an example of Simpson's Paradox. While the overall admission rate for women (82.2%) is higher than for men (66%), women actually have equal or lower admission rates than men in each individual department. The apparent discrimination is due to the fact that women applied disproportionately to the more competitive Engineering department (50/450 = 11.1% of female applicants) while men applied mostly to the less competitive Arts department (400/500 = 80% of male applicants). The data shows no evidence of discrimination against men.

**Confidence:** 0.95

**Assumptions:**
- The provided statistics are accurate
- These are the only two departments at the university
- All applicants applied to exactly one department
- Admission decisions are based on merit within each department

**Steps:**
1. Verified the overall statistics: Men 330/500 = 66%, Women 370/450 = 82.2%
2. Examined department-level admission rates: Engineering - Men 30%, Women 40%; Arts - Men 75%, Women 87.5%
3. Calculated application distribution: Men - 100/500 (20%) to Engineering, 400/500 (80%) to Arts; Women - 50/450 (11.1%) to Engineering, 400/450 (88.9%) to Arts
4. Identified Simpson's Paradox: Women have higher admission rates in both departments individually, but lower overall rate appears due to different application patterns
5. Recognized that women applied more to the competitive Engineering department with lower overall admission rates, while men applied more to Arts with higher admission rates
6. Concluded that the aggregate statistics are misleading and mask the true department-level patterns

**Evaluation Notes:**
- Rubric hit: identifies simpson paradox
- Rubric hit: per-department analysis
- Rubric hit: selection bias in applications
- Rubric hit: concludes claim is invalid or misleading
### Claude Sonnet (claude-sonnet-4-20250514)
**Parse OK:** True | **Latency:** 10531ms

**Answer:** The journalist's claim is not valid. This is a classic example of Simpson's Paradox. While women have a higher overall admission rate (82.2% vs 66%), men actually have higher admission rates within each individual department when we control for department choice. The apparent discrimination against men disappears when we account for the fact that men disproportionately applied to Engineering (which has much lower admission rates) while women applied more evenly across both departments.

**Confidence:** 0.95

**Assumptions:**
- The admission rates provided are accurate
- Department choice is not itself a form of discrimination
- There are no other confounding variables beyond department selection

**Steps:**
1. Calculate admission rates by department and gender: Engineering admits 30% of men vs 40% of women; Arts admits 75% of men vs 87.5% of women
2. Observe that in both departments individually, women have higher admission rates than men
3. Analyze application patterns: Men applied heavily to Engineering (100/500 = 20% to Engineering vs 400/500 = 80% to Arts), while women applied more evenly (50/450 = 11% to Engineering vs 400/450 = 89% to Arts)
4. Recognize this as Simpson's Paradox: the overall statistics are misleading because they don't account for the different application patterns across departments
5. Note that Engineering has much lower admission rates overall (50/150 = 33.3%) compared to Arts (650/800 = 81.25%)
6. Conclude that the lower overall male admission rate is primarily due to men's higher application rate to the more selective Engineering department, not discrimination

**Evaluation Notes:**
- Rubric hit: identifies simpson paradox
- Rubric hit: per-department analysis
- Rubric hit: selection bias in applications
- Rubric hit: concludes claim is invalid or misleading
### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 5086ms

**Answer:** No, the claim is not valid. This is a classic example of Simpson's Paradox. While the overall statistics show women had a higher admission rate (82.2% vs 66%), men actually had higher admission rates in BOTH individual departments (Engineering: 30% vs 40%, Arts: 75% vs 87.5%). The apparent discrimination against men at the aggregate level is entirely due to the different composition of applicants by gender across departments, not actual bias in admissions decisions.

**Confidence:** 0.95

**Assumptions:**
- The admission data provided is accurate and complete
- We are evaluating whether the university's admissions process discriminates based on gender
- Simpson's Paradox is the relevant statistical phenomenon to consider
- The different admission rates across departments reflect legitimate differences in selectivity, not hidden discrimination

**Steps:**
1. Verify the department-level admission rates: Engineering men 30%, women 40%; Arts men 75%, women 87.5%. In both departments, women have higher admission rates.
2. Examine the applicant pool composition: Engineering had 100 male and 50 female applicants (67% male). Arts had 400 male and 400 female applicants (50% male). Men applied disproportionately to Engineering, the more selective department.
3. Recognize Simpson's Paradox: A trend visible in aggregate data can reverse or disappear when data is disaggregated into subgroups. Here, women have higher rates in each department, yet men have a higher overall rate due to compositional differences.
4. Calculate the weighted effect: More men applied to the selective Engineering program (100 men vs 50 women), pulling down the overall male admission rate. More women applied to the less selective Arts program (400 women vs 400 men), pulling up the overall female admission rate.
5. Conclude: The journalist's claim confuses correlation with causation. The lower overall male admission rate reflects application patterns, not discriminatory admissions policies. Each department actually admitted women at higher rates.

**Evaluation Notes:**
- Rubric hit: identifies simpson paradox
- Rubric hit: per-department analysis
- Rubric hit: selection bias in applications
- Rubric hit: concludes claim is invalid or misleading

## Divergence Analysis

Agents diverged:
- **Claude Opus**: No, the claim is not valid. This is an example of Simpson's Paradox. While the overall admission rate for women (82.2%) 
- **Claude Sonnet**: The journalist's claim is not valid. This is a classic example of Simpson's Paradox. While women have a higher overall a
- **Claude Haiku**: No, the claim is not valid. This is a classic example of Simpson's Paradox. While the overall statistics show women had 

## Verdict

Tie between top agents.
