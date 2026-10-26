# Packet Generation Audit (CURATOR-INTERNAL — do NOT share with annotators)

> **Not annotator-facing.** This file, `blind_case_index.csv`, and
> `optional_training_examples/` must never be given to any (human or model)
> annotator. They contain the true case mapping and anonymization keys.

*Offline generation; no live model calls; no case YAMLs modified.*

## Structure produced
```
analysis/phase5_05_blind_iaa_packets/
  annotator_facing/                 <- safe to share
    README_FOR_ANNOTATOR.md
    annotator_taxonomy_reference.md
    packets/BIAA-001.md ... BIAA-020.md
    response_sheets/{annotator_A,annotator_B,annotator_C,blank}_response_sheet.csv
  internal_only/                    <- WITHHELD from annotators
    blind_case_index.csv
    packet_generation_audit.md      (this file)
    internal_notes.md
    optional_training_examples/TRAIN-042.md
```

## Counts
- **20 annotator-facing scored packets** (`BIAA-001` … `BIAA-020`); all 20 counted
  in IAA statistics.
- 1 internal-only training example (`TRAIN-042`); **never** in agreement statistics
  and **not** annotator-facing.

## Blindness / anonymization policy
Annotator-facing packets contain only the anonymized claim + evidence and the
annotation fields. Never included: any gold label, expected answer, `task_family`,
justification, alternative reading, case-type, confidence-of-gold, findings,
evidence spans, notes, prior review/adjudication history, or run outcomes.
Blind IDs (`BIAA-###`) carry no case-number or label signal; packet order was
deterministically shuffled (seed 505). The true `BIAA-### → case` mapping lives only
in `blind_case_index.csv`.

## Content transformations applied at the packet level (YAML prompts NOT edited)
1. **HTML source-placeholder comments removed** (`<!-- ... -->`).
2. **Trailing embedded task-scaffolding removed** (`"For each subclaim provide: …
   Required analysis dimensions: …"`) — leftover instruction text carrying
   label-priming terms.
3. **`context` field excluded wholesale** — it is analytic commentary and in several
   cases literally contains the answer word.
4. **Clinical trial-phase wording neutralized** — `Phase 2 / Phase 3` →
   `mid-stage / late-stage clinical study`. Applied to BIAA-004, BIAA-006, BIAA-014,
   BIAA-018. This is purely to avoid collision with the forbidden project-phase
   string; the evidence-maturity meaning (mid-/late-stage) is preserved.

## Entity anonymization (the 3 identifiable real-world packets)
Real proper nouns replaced with typed neutral placeholders; numeric values, study
design, evidence tier, comparison logic, and claim/evidence mismatch preserved.

### BIAA-003 (internal: case009)
- named researcher → `[Researcher A]`.

### BIAA-006 (internal: case041)
- company → `[Biotech Company A]`; investigational compound → `[Investigational Drug A]`;
  two named competitors → `[Large Pharma Company B]` / `[Large Pharma Company C]`;
  specific drug-class phrasing ("oral/injectable GLP-1 …") → generic
  "oral/injectable weight-loss drug(s)/treatments". Numbers (16.3%, 44 weeks, 2026)
  kept.

### BIAA-013 (internal: case public-001)
- journal + publication date → `[Journal A]`; author list + institutions →
  `[Author A]/[Author B]/[Author D]` and `[University Lab A/B/C]`; national biobank →
  `[National Biobank Cohort A]`; funder → `[National Science Funder A]`; media outlets
  + society → `[News Outlet A/B/C]` / `[Professional Society A]`. All cohort sizes,
  follow-up, risk percentages, disease list, and the overclaiming headline wording
  (the forensic object) preserved.

The exact regex → replacement list is reproducible from the offline generator; the
per-packet transform log was verified after generation (no residual original
entities; see `internal_notes.md`).

## Key confirmations
- **case054 is included** (internal: `BIAA-001`), counted in IAA stats; its packet
  shows only the neutral claim + evidence — the prior no-flip review, gold label,
  alternative reading, and model reading are all hidden, and the blind ID does not
  encode the case number.
- **case042 is NOT annotator-facing** — it appears only as the internal-only
  `TRAIN-042` and is excluded from IAA statistics.
- **All 20 active packets are included in IAA stats.**

## Validation (annotator-facing files only)
- Forbidden project/identity/metadata strings → NONE (see `internal_notes.md` for the
  full string list and result).
- Label values in per-case packets → NONE. Label names appear only in
  `annotator_taxonomy_reference.md` (by design; the annotator needs the definitions).
- Residual real-world proper-noun scan of the 3 anonymized packets → NONE.

## Next step
Share **only** `annotator_facing/` with each independent model annotator
(A: GLM-5.2, B: Fable 5, C: another strong model). Give each its own response sheet.
Withhold `internal_only/`. Score agreement per
`../phase5_05_blind_iaa_design/adjudication_and_kappa_plan.md`; do not silently
relabel.
