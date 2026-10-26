# Forensic Dossier: Study Forensics: NAD+ restoration reverses Alzheimer's in mice

**Run ID:** `mechfix_study-forensics-028_Claude_Haiku_47b017`  
**Task:** study-forensics-028 | study_forensics | medium | study_forensics  
**Timestamp:** 2026-04-08T16:41:54.837064+00:00  
**Task Family:** mechanism_vs_evidence  
**Trap Type:** animal_to_human_overreach  
**Ambiguity:** low  

## Executive Summary

**Agents tested:** Claude Haiku
**Winner:** Claude Haiku — **79.1/100** (margin: 0.0)
**Failure modes:** none
**Forensic flags:** 0
**Consistency findings:** 5
**Answer convergence:** all agents agree

## Score Matrix

| Agent | Correctness | Support Strength | Structural Reaso | Assumption Disci | Uncertainty Hand | Alternative Hypo | Self Monitoring  | Insight Depth | Mechanism Qualit | Communication Ef | **Total** |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Claude Haiku | 30.0/30 | 2.4/8 | 5.4/8 | 4.8/6 | 3.9/6 | 6.0/6 | 5.6/8 | 8.0/8 | 3.0/10 | 10.0/10 | **79.1/100** |

## Study Forensics Audit

### Claude Haiku

**Classification:** `mechanism_vs_evidence` [+] (gold: `mechanism_vs_evidence`)
**Finding Recall:** 100%
**Matched Findings:** mechanism_not_demonstrated, conclusion_exceeds_results
**Extra Findings:** cautious_scope_control, none_or_minor, unsupported_generalization, decorative_uncertainty

## Reasoning Integrity Audit

### Claude Haiku
**Classification:** Correct and well-supported
**Load-bearing steps:** 1 / 5

## Mechanism Analysis

### Claude Haiku
| Aspect | Status |
|--------|--------|
| Concept named | :x: none |
| Mechanism described | :white_check_mark: (1 sentence(s)) |
| Grounded to case | :x: (0 sentence(s)) |

**Missing:** concept not named, mechanism not grounded to case data

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
  - (+) `final_answer`: "mechanism_vs_evidence"
    _Agent's answer for correctness check_
  - Note: Exact match

**Support Strength:** 2.4/8
  - (+) `final_answer`: "mechanism_vs_evidence"
    _Conclusion grounded by reasoning chain_
  - Note: Support classification: 0 load-bearing, 1 supporting, 0 mentioned / 5
  - Note: Reasoning graph confirms conclusion grounding

**Structural Reasoning:** 5.4/8
  - (+) `steps[4]`: "5. MECHANISM VS. EVIDENCE CLASSIFICATION: The text makes a mechanistic claim (NAD+ restoration repairs brain damage and "
    _Most informative reasoning step_
  - Note: 5 reasoning steps
  - Note: Low step utility: 1/5 steps contribute

**Assumption Discipline:** 4.8/6
  - (+) `assumptions[0]`: "The study was conducted in genetically engineered mice with Alzheimer's-like pathology"
    _Most substantive assumption_
  - Note: 4/4 substantive assumptions

**Uncertainty Handling:** 3.9/6
  - (+) `uncertainties[0]`: "Whether the genetically engineered mice fully recapitulate human Alzheimer's pathology (a known limitation of mouse mode"
    _Most substantive uncertainty_
  - (+) `confidence`: "confidence: 0.92"
    _Stated confidence level_
  - Note: 4 uncertainties (4 substantive)
  - Note: Confidence 0.92

**Alternative Hypothesis Quality:** 6.0/6
  - (+) `alternative_hypotheses[1]`: "Could classify as 'overclaim' if the language were more assertive (e.g., 'will cure Alzheimer's'), but the text uses app"
    _Most substantive alternative hypothesis_
  - Note: 2 alternative hypotheses considered
  - Note: 2/2 include rejection reasoning

**Self Monitoring Quality:** 5.6/8
  - (+) `self_check[2]`: "Is the cautious language sufficient to make this 'solid'? No — cautious wording does not close an evidence-tier gap. A w"
    _Most substantive self-verification step_
  - Note: 4 self-check items
  - Note: Self-check quality: 1 deep, 3 arithmetic, 0 fluff

**Mechanism Quality:** 3.0/10
  - (+) `(mechanism analysis)`: "5. MECHANISM VS. EVIDENCE CLASSIFICATION: The text makes a mechanistic claim (NAD+ restoration repairs brain damage and "
    _Mechanism description_
  - Note: Describes mechanism but does not name concept

**Communication Efficiency:** 10.0/10
  - Note: Signal density: 0.69, 496 words

**Insight Depth:** 8.0/8
  - (+) `(output text)`: "e study is conducted in mice (animal model), not humans. this is tier 2"
    _Insight 'animal model' matched (exact)_
  - Note: Key insights: 2 full / 2


## Consistency & Grounding Audit

### Claude Haiku

- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 1 has low overlap with final answer (1/14 content words)
  - `key_claims[0]`: "The core epistemic problem: animal evidence (mice) is being used to support a human therapeutic clai"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 2 has low overlap with final answer (0/12 content words)
  - `key_claims[1]`: "The hedge language ('suggest,' 'could,' 'clinical trials pending') acknowledges uncertainty but does"
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 3 has low overlap with final answer (0/13 content words)
  - `key_claims[2]`: "The claim of 'meaningful recovery' (not just slowing decline) is particularly strong given it rests "
- **[WARN]** `[HEURISTIC]` `answer_claim_alignment`: Key claim 4 has low overlap with final answer (0/16 content words)
  - `key_claims[3]`: "The call for clinical trials is appropriate and indicates awareness of the gap, but the framing stil"
- **[NOTE]** `[MEDIUM CONFIDENCE]` `mechanism_gap`: Causal mechanism described but underlying concept not named
  - `final_answer`: "mechanism_vs_evidence"


## Agent Profiles

### Claude Haiku (claude-haiku-4-5-20251001)
**Parse OK:** True | **Latency:** 12620ms

**Final Answer:** mechanism_vs_evidence

**Confidence:** 0.92

**Assumptions:**
- The study was conducted in genetically engineered mice with Alzheimer's-like pathology
- The mice showed measurable cognitive recovery after NAD+ restoration
- The text implies this could translate to human therapeutic benefit
- No human clinical data are presented or referenced

**Reasoning Steps:**
1. 1. EVIDENCE TIER IDENTIFICATION: The study is conducted in mice (animal model), not humans. This is tier 2 evidence.
2. 2. CONCLUSION TIER IDENTIFICATION: The text states results 'suggest that boosting NAD+ could move Alzheimer's therapy' and calls for clinical trials. This implies human therapeutic potential (tier 5 conclusion).
3. 3. BRIDGE GAP DETECTION: There is a 3-tier gap between animal evidence (tier 2) and human therapeutic claims (tier 5).
4. 4. BRIDGE SUPPORT ANALYSIS: The text acknowledges the gap by calling for clinical trials ('to see if the approach will translate to patients'), but this acknowledgment does not close the gap. The hedge 'could' and 'suggest' are present but do not constitute direct evidence of human benefit.
5. 5. MECHANISM VS. EVIDENCE CLASSIFICATION: The text makes a mechanistic claim (NAD+ restoration repairs brain damage and restores memory) based on animal data, then extrapolates to human therapeutic potential. This is a classic mechanism_vs_evidence pattern: the mechanism is demonstrated in mice, but human efficacy is not established.

**Key Claims:**
- The core epistemic problem: animal evidence (mice) is being used to support a human therapeutic claim without intermediate human data.
- The hedge language ('suggest,' 'could,' 'clinical trials pending') acknowledges uncertainty but does not resolve the evidence-tier gap.
- The claim of 'meaningful recovery' (not just slowing decline) is particularly strong given it rests on animal data alone.
- The call for clinical trials is appropriate and indicates awareness of the gap, but the framing still implies human benefit is plausible based on mouse results.

**Alternative Hypotheses:**
- Could classify as 'solid' if the study is actually a human RCT — but the text explicitly states 'mice' and 'genetically engineered mice,' ruling this out.
- Could classify as 'overclaim' if the language were more assertive (e.g., 'will cure Alzheimer's'), but the text uses appropriately cautious language ('suggest,' 'could'), making mechanism_vs_evidence the more precise fit.

**Uncertainties:**
- Whether the genetically engineered mice fully recapitulate human Alzheimer's pathology (a known limitation of mouse models not addressed in the text)
- Whether the NAD+ restoration approach addresses the primary pathogenic mechanisms in human Alzheimer's or only secondary energy deficits
- Whether the 'normal memory performance' in mice translates to clinically meaningful cognitive recovery in humans
- The specific compound used and whether it is bioavailable or safe in humans

**Self-Verification:**
- Did I overclassify this as mechanism_vs_evidence? No — the text explicitly extrapolates from mice to human therapy. This is the definition of mechanism_vs_evidence.
- Did I miss that this is actually human data? No — the text clearly states 'mice' and 'genetically engineered mice.'
- Is the cautious language sufficient to make this 'solid'? No — cautious wording does not close an evidence-tier gap. A well-hedged mouse study implying human benefit is still mechanism_vs_evidence.
- Should I have flagged this as 'overclaim'? The language is appropriately cautious, so mechanism_vs_evidence is more precise than overclaim.

**Dimension Scores:**
- Correctness: 30.0/30 `##########`
- Support Strength: 2.4/8 `###.......`
- Structural Reasoning: 5.4/8 `######....`
- Assumption Discipline: 4.8/6 `########..`
- Uncertainty Handling: 3.9/6 `######....`
- Alternative Hypothesis Quality: 6.0/6 `##########`
- Self Monitoring Quality: 5.6/8 `#######...`
- Insight Depth: 8.0/8 `##########`
- Mechanism Quality: 3.0/10 `###.......`
- Communication Efficiency: 10.0/10 `##########`


## Final Verdict

**Solo run: Claude Haiku** scored **79.1/100**.

**Best per dimension:**
- Correctness: Claude Haiku (30.0/30)
- Support Strength: Claude Haiku (2.4/8)
- Structural Reasoning: Claude Haiku (5.4/8)
- Assumption Discipline: Claude Haiku (4.8/6)
- Uncertainty Handling: Claude Haiku (3.9/6)
- Alternative Hypothesis Quality: Claude Haiku (6.0/6)
- Self Monitoring Quality: Claude Haiku (5.6/8)
- Insight Depth: Claude Haiku (8.0/8)
- Mechanism Quality: Claude Haiku (3.0/10)
- Communication Efficiency: Claude Haiku (10.0/10)

**Latency vs Quality:**

| Agent | Latency | Score | Points/sec |
|-------|---------|-------|------------|
| Claude Haiku | 12.6s | 79.1/100 | 6.3 |

All agents completed without critical failure modes.
