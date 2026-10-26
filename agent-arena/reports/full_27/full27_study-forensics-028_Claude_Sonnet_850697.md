# Forensic Dossier: Study Forensics: NAD+ restoration reverses Alzheimer's in mice

**Run ID:** `full27_study-forensics-028_Claude_Sonnet_850697`  
**Task:** study-forensics-028 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T18:00:46.659919+00:00  
**Task Family:** mechanism_vs_evidence  
**Trap Type:** animal_to_human_overreach  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Sonnet
**Winner:** Claude Sonnet — **71.1/100** (margin: 0.0)
**Failure modes:** decorative_self_check, decorative_uncertainty, unused_assumption
**Forensic flags:** 1
**Consistency findings:** 7
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Sonnet | 30.0/30 | 2.4/8 | 5.3/8 | 4.3/6 | 3.6/6 | 4.5/6 | 0.0/8 | 8.0/8 | 3.0/10 | 10.0/10 | **71.1/100** |

## Study Forensics Audit

### Claude Sonnet

**Classification:** `mechanism_vs_evidence` [+] (gold: `mechanism_vs_evidence`)
**Finding Recall:** 100%
**Matched Findings:** mechanism_not_demonstrated, conclusion_exceeds_results
**Extra Findings:** evidence_matches_claim

## Reasoning Integrity Audit

### Claude Sonnet
**Classification:** Correct and well-supported
**Load-bearing steps:** 1 / 6

## Mechanism Analysis

### Claude Sonnet
| Aspect | Status |
|--------|--------|
| Concept named | :x: none |
| Mechanism described | :white_check_mark: (1 sentence(s)) |
| Grounded to case | :x: (0 sentence(s)) |

**Missing:** concept not named, mechanism not grounded to case data

## Grounding Audit

### Claude Sonnet
Conclusion claims: 1
- Direct support: 0
- Indirect support: 1
- Unsupported: 0
- Contradicted: 0


## Forensic Flags

### Claude Sonnet

- **[STYLISTIC]** `unnamed_mechanism`: Describes mechanism without naming the concept — under-explicit
  - `steps[5]`: "Classified as mechanism_vs_evidence due to unsupported leap from mouse to human therapeutic context"


## Evidence Map

### Claude Sonnet

**Correctness:** 30.0/30
  - (+) `final_answer`: "mechanism_vs_evidence"
    _Agent's answer for correctness check_
  - Note: Exact match

**Support Strength:** 2.4/8
  - (+) `final_answer`: "mechanism_vs_evidence"
    _Conclusion grounded by reasoning chain_
  - Note: Support classification: 0 load-bearing, 1 supporting, 0 mentioned / 6
  - Note: Reasoning graph confirms conclusion grounding

**Structural Reasoning:** 5.3/8
  - (+) `steps[1]`: "Identified conclusion tier: human therapeutic benefit implied by 'move Alzheimer's therapy beyond slowing decline toward"
    _Most informative reasoning step_
  - Note: 6 reasoning steps
  - Note: Low step utility: 1/6 steps contribute

**Assumption Discipline:** 4.3/6
  - (+) `assumptions[0]`: "The study was conducted in genetically engineered mouse models of Alzheimer's"
    _Most substantive assumption_
  - (-) `assumptions[1]`: "The treatment showed memory restoration in these mice"
    _Declared but unused in reasoning_
  - Note: 4/4 substantive assumptions
  - Note: 1 unused assumption(s)

**Uncertainty Handling:** 3.6/6
  - (+) `uncertainties[1]`: "Whether 'meaningful recovery' language constitutes promotional tone"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.9"
    _Stated confidence level_
  - (-) `uncertainties[0]`: "Exact wording of scientists' quotes could affect classification"
    _Listed but never addressed in reasoning_
  - Note: 2 uncertainties (2 substantive)
  - Note: 1 decorative uncertainty(ies)

**Alternative Hypothesis Quality:** 4.5/6
  - (+) `alternative_hypotheses[1]`: "Could be 'overclaim' if language was more promotional about human benefits"
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 2/2 genuinely diverse alternatives

**Self Monitoring Quality:** 0.0/8
  - (+) `self_check[2]`: "Verified this is tier mismatch rather than overclaim - language is cautious"
    _Most substantive self-verification step_
  - (-) `self_check[0]`: "Confirmed evidence tier is animal, not human"
    _Fluff self-check_
  - Note: 4 self-check items
  - Note: Self-check quality: 0 deep, 0 arithmetic, 4 fluff

**Mechanism Quality:** 3.0/10
  - (+) `(mechanism analysis)`: "Classified as mechanism_vs_evidence due to unsupported leap from mouse to human therapeutic context"
    _Mechanism description_
  - Note: Describes mechanism but does not name concept

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.79, 211 words

**Insight Depth:** 8.0/8
  - (+) `(output text)`: "if conclusions stayed within animal model context could be 'overclaim'"
    _Insight 'animal model' matched (exact)_
  - Note: Key insights: 2 full / 2


## Failure Analysis

### Claude Sonnet

**MINOR:**
- **Decorative Self Check** `[HEURISTIC]`: All 4 self-checks appear to be fluff — no substantive verification
  - `self_check[0]`: "Confirmed evidence tier is animal, not human"
  - _Impacts: self_monitoring_quality_

**STYLISTIC:**
- **Unused Assumption** `[HEURISTIC]`: Assumption 'The treatment showed memory restoration in these mice...' is declared but not referenced in reasoning
  - `assumptions[1]`: "The treatment showed memory restoration in these mice"
  - _Impacts: assumption_discipline_
- **Decorative Uncertainty** `[HEURISTIC]`: Uncertainty 'Exact wording of scientists' quotes could affect classificat...' is listed but not addressed
  - `uncertainties[0]`: "Exact wording of scientists' quotes could affect classification"
  - _Impacts: uncertainty_handling_


## Consistency & Grounding Audit

### Claude Sonnet

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (1/12 content words)
  - `key_claims[0]`: "Animal evidence shows NAD+ restoration can repair brain damage and restore memory in mouse models"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/6 content words)
  - `key_claims[1]`: "Text implies this could translate to human therapeutic benefit"
- **[WARN]** `[HEURISTIC]` `unused_assumption`: Assumption 2 appears unused in reasoning or answer
  - `assumptions[1]`: "The treatment showed memory restoration in these mice"
- **[WARN]** `[HEURISTIC]` `decorative_uncertainty`: Uncertainty 1 appears decorative — not addressed in reasoning or self-check
  - `uncertainties[0]`: "Exact wording of scientists' quotes could affect classification"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 1 is stated without rejection reasoning
  - `alternative_hypotheses[0]`: "Could be 'solid' if conclusions stayed within animal model context"
- **[NOTE]** `[HEURISTIC]` `weak_alternative`: Alternative hypothesis 2 is stated without rejection reasoning
  - `alternative_hypotheses[1]`: "Could be 'overclaim' if language was more promotional about human benefits"
- **[NOTE]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Causal mechanism described but underlying concept not named
  - `final_answer`: "mechanism_vs_evidence"


## Agent Profiles

### Claude Sonnet (claude-sonnet-4-20250514)
**Parse OK:** True | **Latency:** 10325ms

**Final Answer:** mechanism_vs_evidence

**Confidence:** 0.9

**Assumptions:**
- The study was conducted in genetically engineered mouse models of Alzheimer's
- The treatment showed memory restoration in these mice
- No human clinical data is presented
- The text implies therapeutic potential for human patients

**Reasoning Steps:**
1. Identified evidence tier: animal studies in genetically engineered mice
2. Identified conclusion tier: human therapeutic benefit implied by 'move Alzheimer's therapy beyond slowing decline toward meaningful recovery'
3. Checked for bridge support: only hedging language ('suggest', 'could', call for trials) but no direct human evidence
4. Evaluated language: cautious/analytical rather than promotional
5. Applied priority rule: tier gap is primary issue, not rhetorical inflation
6. Classified as mechanism_vs_evidence due to unsupported leap from mouse to human therapeutic context

**Key Claims:**
- Animal evidence shows NAD+ restoration can repair brain damage and restore memory in mouse models
- Text implies this could translate to human therapeutic benefit
- No direct human evidence supports the therapeutic implication

**Alternative Hypotheses:**
- Could be 'solid' if conclusions stayed within animal model context
- Could be 'overclaim' if language was more promotional about human benefits

**Uncertainties:**
- Exact wording of scientists' quotes could affect classification
- Whether 'meaningful recovery' language constitutes promotional tone

**Self-Verification:**
- Confirmed evidence tier is animal, not human
- Confirmed conclusion implies human benefit despite hedging
- Verified this is tier mismatch rather than overclaim - language is cautious
- Did not fabricate problems - the tier gap genuinely exists

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 2.4/8 `###.......`
- Structural Reasoning: 5.3/8 `######....`
- Assumption Discipline: 4.3/6 `#######...`
- Uncertainty Handling: 3.6/6 `######....`
- Alternative Hypothesis Quality: 4.5/6 `#######...`
- Self Monitoring Quality: 0.0/8 `..........`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 3.0/10 `###.......`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Sonnet** scored **71.1/100**.

**Best per dimension:**
- Correctness: Claude Sonnet (30.0/30)
- Support Strength: Claude Sonnet (2.4/8)
- Structural Reasoning: Claude Sonnet (5.3/8)
- Assumption Discipline: Claude Sonnet (4.3/6)
- Uncertainty Handling: Claude Sonnet (3.6/6)
- Alternative Hypothesis Quality: Claude Sonnet (4.5/6)
- Self Monitoring Quality: Claude Sonnet (0.0/8)
- Insight Depth: Claude Sonnet (8.0/8)
- Mechanism Quality: Claude Sonnet (3.0/10)
- Communication Efficiency: Claude Sonnet (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Sonnet | 10.3s | 71.1/100 | 6.9 |

Failure modes observed: decorative_self_check, decorative_uncertainty, unused_assumption.
