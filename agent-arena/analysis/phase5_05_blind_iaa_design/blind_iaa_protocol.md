# Phase 5.05 — Blind Inter-Annotator Agreement (IAA) Protocol

*Study design only. **No live model calls, no YAML edits, no label changes.** This
document defines how a second, independent annotator blind-labels a stratified
sample so we can measure whether the gold labels are reproducible beyond the
original curator.*

## Purpose
Measure the **reproducibility of the gold labels**. Every gold label to date
reflects a single curator (taxonomy-first, but one person, who has also seen model
outputs). Blind IAA tests whether an independent annotator, seeing only the claim,
the evidence, and the taxonomy, arrives at the same primary label.

## Why this must precede the Phase 5.1 model panel
A model panel measures how *models* behave against gold. If the gold itself is not
reproducible, panel results are uninterpretable — disagreement could be a model
weakness **or** a soft label. IAA is the credibility gate: establish that the gold
is human-reproducible **before** spending on discrimination measurement, and before
freezing a holdout that bakes in possibly-soft labels.

## What the annotator MAY see
- The evaluated **claim / prompt text** (the isolated claim under judgement).
- The **evidence / source description** contained in the case (context lines,
  design, data type).
- The **taxonomy definitions** and the **precedence rule** (generic vs specific).
- The blank **annotation form**.

## What the annotator MUST NOT see
- The existing **gold label**, `expected_answer`, or `task_family`.
- Any **model prediction** or Phase-5A outcome (accuracy, stable-alternative flags).
- Any **prior adjudication** (e.g. the case040 flip, the case054 no-flip decision).
- `gold_justification`, `gold_alternative_reading`, `curator_notes`,
  `gold_case_type`, `gold_confidence`, `trap_type`, `diagnostic_focus`, or scores.
- Case filenames that leak the label (packets use anonymized IDs).

## Sample size & composition
Target: **~20 active cases** (final plan: 20; see `blind_iaa_sample_plan.csv`).
Composition:
- **All 9 borderline / review-sensitive cases** (007, 022, 031, 037, 043, 045,
  048, **054**, 059).
- **Cases with documented alternative readings** — heavily represented (all 9
  borderline plus several clear cases carry alternatives).
- **A stratified random sample of clear Core cases** covering **all four labels**
  (solid, overclaim, mechanism_vs_evidence, correlation_vs_causation), including
  provenance/discriminator picks (029, 032, 040, public-001).
- **case054** — included (mandatory; the rule-first no-flip adjudication is exactly
  what independent labelling should stress-test).
- **case041** — included (the curated_showcase / intake-passed exemplar).
- **case042 (retired)** — **excluded** from the active IAA sample and **never**
  counted in agreement statistics. It may optionally appear as a **clearly
  separated training example** of a retired task-design failure, marked
  `include_in_blind_packet = optional_training_only` in the sample plan.

Resulting label mix in the 20-case sample: overclaim 9, solid 6, correlation 3,
mechanism 2 (mirrors the library's overclaim skew; per-label agreement will be
reported despite thin specific classes — see `iaa_risk_notes.md`).

## Expected output per case (annotation form)
1. `primary_label` — one of the four taxonomy labels.
2. `secondary_label` — optional second failure mode, if genuinely co-present.
3. `confidence` — annotator's own low/medium/high (uncalibrated, self-report).
4. `rationale` — 1–3 sentences grounding the label in claim/evidence structure.
5. `ambiguity_notes` — what, if anything, made the case hard or debatable.
6. `source_voice_clear` — yes/no: is the claim-maker unambiguous?
7. `claim_isolated` — yes/no: is the evaluated claim isolated (not buried in
   surrounding analysis that critiques it)?
8. `evidence_matches_claim_strength` — yes/no/partial: does the evidence support
   the strength of the claim?

## Process
1. Curator prepares packets from the sample plan using
   `blind_annotation_packet_template.md` (strips all label-bearing fields).
2. Annotator reads `blind_annotator_instructions.md`, then labels each packet
   independently, no discussion.
3. Curator computes agreement per `adjudication_and_kappa_plan.md`.
4. Disagreements go to a **documented curator-review queue** — never a silent
   relabel. Outcomes drive `next_steps_after_iaa.md`.
