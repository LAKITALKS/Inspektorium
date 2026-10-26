# Signal Strength vs. Evidence Integrity

**A Small Agent Arena Probe on a GLP-1 Market Claim**

---

Draft briefing for Dr. Peter Walde / MAPEGY | June 2026 | Early proof-of-concept

---

## 1. Why This Matters

Technology and innovation intelligence systems are built to detect strong signals: emerging drugs, breakthrough claims, patent filings, analyst enthusiasm. But a strong signal is not always a strongly supported signal. The language surrounding a clinical result can extend well beyond what the underlying evidence actually establishes. Agent Arena explores a complementary layer: evaluating the evidential integrity of the claims behind signals, not just their strength.

## 2. Case Tested

**Claim source:** Reuters-based secondary report (March 16, 2026), paraphrased and structured. Not a full clinical publication.

**Drug:** Aleniglipron (Structure Therapeutics), an oral GLP-1 receptor agonist for obesity.

**Central claim:** The drug showed up to 16.3% weight loss after 44 weeks in a Phase 2 trial and is being positioned as having potential best-in-class efficacy among oral GLP-1 drugs, with efficacy potentially comparable to injectable GLP-1 treatments.

**Four subclaims were isolated for forensic evaluation:**

- A. Highest efficacy among oral GLP-1 therapies
- B. Potentially comparable to injectable GLP-1 drugs
- C. Potential best-in-class oral obesity drug
- D. No observed weight-loss plateau at 44 weeks

## 3. Multi-Agent Result

Three evaluator agents using different Claude model families evaluated the claim in parallel. All three converged on the same classification.

| Agent | Model | Score | Classification |
|-------|-------|------:|----------------|
| Claude Opus | claude-opus-4-5 | 71.3 / 100 | overclaim |
| Claude Sonnet | claude-sonnet-4-5 | 73.5 / 100 | overclaim |
| Claude Haiku | claude-haiku-4-5-20251001 | 80.5 / 100 | overclaim |

**Gold label:** overclaim | **Consensus:** unanimous across all three agents

## 4. Subclaim Analysis

| Subclaim | Evidence Issue | Agent Arena Verdict | Why It Matters |
|----------|---------------|---------------------|----------------|
| **A.** Highest efficacy among oral GLP-1 therapies | Based on indirect cross-trial comparison (16.3% vs. ~12% orforglipron), not head-to-head evidence | Unsupported | Cross-trial numerical comparison is not clinical evidence of superiority |
| **B.** Potentially comparable to injectable GLP-1 drugs | Compares Phase 2 oral data to Phase 3 injectable data without direct comparator trial | Overclaimed | Phase and formulation mismatch; hedge word "potentially" does not resolve the evidential gap |
| **C.** Potential best-in-class | Best-in-class positioning applied to Phase 2 data, which cannot establish class leadership | Overclaimed | Phase-maturity mismatch: best-in-class requires Phase 3 confirmation |
| **D.** No observed weight-loss plateau | Factual observation at 44 weeks, but framed as an advantage rather than an open question | Partially supported, framing overclaimed | Absence of plateau does not confirm durability; final effect size remains unknown |

## 5. Key Finding

The underlying clinical data point — 16.3% weight loss at 44 weeks for an oral GLP-1 drug — may represent a genuinely strong Phase 2 signal. However, the market-facing communication extends beyond the evidence tier in several ways: indirect cross-trial comparisons are presented as competitive evidence, best-in-class positioning is applied to mid-stage data, and hedge language ("potentially") is present but insufficient to constrain the overall promotional framing. The signal is real; the positioning outpaces the evidence.

## 6. Relevance to Technology Intelligence

When large-scale technology intelligence systems ingest market reports, patents, scientific papers, startup claims, and analyst language, signal strength can be amplified by weakly supported claims. A promising Phase 2 result, filtered through analyst enthusiasm and promotional framing, can appear in an intelligence system as a near-confirmed breakthrough — even when the evidence remains preliminary.

Agent Arena addresses this gap. It does not replace signal detection; it adds a forensic layer that evaluates whether the reasoning and evidence behind a signal are as strong as the signal itself. For technology intelligence at scale, this distinction between signal strength and evidence integrity is operationally relevant.

## 7. Caveats

- This is an early probe and proof-of-concept, not a finished product or validated diagnostic tool.
- The source material is a Reuters-based secondary report, not the full clinical trial publication.
- Full clinical validation of any drug claim would require the trial publication, protocol details, endpoint definitions, sample sizes, and ideally head-to-head comparator trials or Phase 3 confirmation.
- The result demonstrates a claim-forensics capability. It is not a final medical judgment, regulatory assessment, or investment recommendation.
- Agent Arena's evaluation rubric is under active development; scores reflect the current evaluation framework.

## 8. Takeaway

> "Agent Arena does not ask only whether a signal is strong; it asks whether the reasoning behind the signal is evidentially strong."
