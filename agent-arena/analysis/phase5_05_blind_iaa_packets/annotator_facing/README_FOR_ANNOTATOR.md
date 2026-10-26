# Read Me — Independent Blind Annotator

You are an **independent blind annotator for a claim-forensics taxonomy task**.
Your job is to read short items — each presenting a scientific or commercial claim
together with the evidence available for it — and classify how the claim relates to
its evidence, using a fixed four-label taxonomy.

## What you have
- `annotator_taxonomy_reference.md` — the label definitions and the precedence rule.
- `packets/` — the items to annotate (`BIAA-001` … `BIAA-020`).
- Your assigned response sheet in `response_sheets/` (or the blank one).

## How to work
1. Read `annotator_taxonomy_reference.md` once.
2. For each packet `BIAA-###`, read the material and decide the labels and fields.
3. Record your answers on the matching row of your response sheet — **one row per
   `BIAA-###`**.
4. Complete every item.

## Ground rules
- **Work only from the packet content and the taxonomy reference.** Nothing else is
  needed or provided.
- **Do not infer an "intended" answer** from formatting, wording, topic, ordering,
  or placeholder names. Some proper names have been replaced with neutral
  placeholders such as `[Researcher A]`, `[Journal A]`, `[Investigational Drug A]`
  — treat these as opaque; they carry no hidden meaning.
- **Do not try to find, search for, or reconstruct the original source** of any
  item. Judge only the material in front of you.
- **Do not ask for the correct answers.** There is no answer key to request; your
  independent judgement is the measurement.
- **Work alone.** No collaboration or comparison with other annotators.
- Low-confidence, honest splits are useful. Use `secondary_label`,
  `ambiguity_notes`, and `recommended_human_review` freely.

## The response fields (per item)
`primary_label`, `secondary_label` (optional), `confidence` (0–1), `rationale`,
`ambiguity_notes`, `source_voice_clear`, `claim_isolated`,
`evidence_matches_claim_strength`, `missing_evidence_notes`,
`recommended_human_review`, `freeform_notes`.

When your sheet is complete, return it to the study team.
