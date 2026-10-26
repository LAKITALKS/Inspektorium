# Phase 7 — Scientific Handoff (robustness focus; proposal only)

This handoff **proposes** Phase 7 work. It implements nothing, runs no model, and authorizes
**no** holdout access. Phase 7 is a **robustness** phase on development material, entered under
the guardrails in `phase6_go_no_go_review.md`. It builds on the Phase 6 signals: an unproven
abstention rule, ceiling effects for strong models, and a recurring **overclaim → over-specific**
boundary difficulty (hypothesis, `phase6_integrated_findings.md` Part C).

Each priority states its objective and its **pre-registration** requirement — the metric,
aggregation, and decision rule must be frozen before results (Level-2 discipline).

## 1. Boundary-case robustness

- Targeted cases probing **overclaim vs `correlation_vs_causation`** and **overclaim vs
  `mechanism_vs_evidence`**, plus cases with **multiple plausible failure modes**.
- **Explicit primary-label prioritization tests**: when several labels could fit, is the
  single most-specific-yet-correct label chosen per the frozen taxonomy precedence?
- *Pre-register*: expected label + acceptable alternates per case, before any run.

## 2. Perturbation robustness (label-preserving)

- Paraphrases; claim reordering; irrelevant distractor evidence; added weak hedges;
  source-format changes; evidence-order changes; small wording changes that **should not**
  alter the label.
- Objective: measure label **stability** under transformations that must not change the gold
  label.
- *Pre-register*: the perturbation families and the "label must not change" invariant.

## 3. Adversarial robustness

- Persuasive marketing language; citation decoration; benchmark exaggeration; unsupported
  superiority wording; mechanistic language engineered to resemble human evidence; causal
  verbs grafted onto correlational evidence.
- Objective: does the classifier hold the correct label when the *surface* pushes toward a
  wrong one?
- *Pre-register*: adversarial families mapped to the label they attack.

## 4. Replication and stability

- **Freeze a replication count before execution** (consider **3–5** where justified).
- Measure **label stability** and **confidence variability** across replications.
- Define **deterministic aggregation** and **disagreement reporting** before results.
- **Do not** reinterpret replication frequency directly as a calibrated correctness
  probability.

## 5. Difficulty and ceiling management

- **Preserve all existing cases**; **do not** remove easy cases because models solved them.
- **Add / nominate harder diagnostic cases separately**, with their own provenance.
- Distinguish **evaluation coverage** from **discriminative difficulty**.
- **No result-driven retirement or relabeling** (Level 3; curator-only, separate decision).

## 6. Governance efficiency

- Reduce redundant narrative artifacts. Prefer a compact per-operation set:
  (a) one machine-readable report; (b) one concise human report; (c) one audit manifest;
  (d) one deterministic generator.
- Preserve rigor (frozen prep/result checkpoints, hashed contracts, leakage scans) while
  cutting documentation overhead. Phase 6 accreted many docs; Phase 7 should consolidate.

## 7. Optional Phase 7b — independent expert / human validation

- If pursued: **define the human-validation objective before data collection**.
- **Do not** relabel model revalidation as human inter-annotator agreement.
- Keep it a **separate, pre-registered** track; it does not, by itself, authorize holdout
  access.

## Carry-forward hypotheses (test, do not assume)

- **Overclaim-boundary weakness** (recurs across Sonnet-6.2 and prompt-only-6.4 on DEV-0011,
  DEV-0013): boundary ambiguity vs prioritization-scaffold gap vs phrasing artifact —
  distinguish with §1 boundary cases and §3 adversarial causal/mechanistic decoys.
- **Package advantage durability**: does the Phase 6.4 Agent-Arena advantage persist under
  §4 replication and §5 harder cases, or is it a small-sample/ceiling artifact?
- **Abstention**: is any confidence-threshold rule reliable under §2 perturbations, or does it
  stay development-selected only?

## Hard boundaries (unchanged)

Holdout stays sealed; taxonomy/gold/status/thresholds/costs stay frozen; no production or
universal-superiority claim; no pooling of paired predictions. Any Level-3 action (holdout,
gold, taxonomy, public claim) requires a separate explicit curator decision.
