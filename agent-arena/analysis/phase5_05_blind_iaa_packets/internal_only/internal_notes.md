# Internal Notes (CURATOR-ONLY — do NOT share with annotators)

> This file and everything under `internal_only/` are **not** annotator-facing.
> Share only `annotator_facing/` with the model annotators.

## True mapping (curator eyes only)
Full `BIAA-### → real case` mapping is in `blind_case_index.csv`. Highlights:
- **BIAA-001 = case054** (the rule-first no-flip item). Counted in IAA stats; its
  packet hides the label, the prior review outcome, and the alternative reading. The
  blind ID `BIAA-001` encodes no case number, so it is not identifiable from the ID.
- **BIAA-003 = case009**, **BIAA-006 = case041**, **BIAA-013 = case public-001** —
  the three packets that required real-world entity anonymization.
- **TRAIN-042 = case042** — internal only; never annotator-facing; never in stats.

## Validation results (annotator-facing files only)
- **Forbidden project/identity/metadata strings** — checked list: `Agent Arena`,
  `Phase`, `phase5`, `case040/041/042/054`, `study-forensics`, `retired`, `no-flip`,
  `flipped`, `stable`, `adjudication`, `gold_label`, `expected_answer`,
  `task_family`, `suite_history`, `model prediction`, `score:`, `curator`,
  `Phase-5A` → **NONE found**. ✅
- **Label values** (`overclaim`, `solid`, `mechanism_vs_evidence`,
  `correlation_vs_causation`) in per-case packets → **NONE**. Label names appear only
  in `annotator_taxonomy_reference.md` (by design; needed to label at all). ✅
- **Residual original real-world entities** in the 3 anonymized packets — precise
  check for `Structure Therapeutics`, `aleniglipron`, `Eli Lilly`, `Novo Nordisk`,
  `GLP-1`, `Gabrieli`, `UK Biobank`, `Monash`, `University of Sydney`,
  `Central South University`, `European Heart Journal`, `European Society of
  Cardiology`, `ScienceDaily`, `SciTechDaily`, `Jiehua/Minxue/Shen/Stamatakis`,
  `National Natural Science Foundation`, `Reuters`, `orforglipron` → **NONE**. ✅

### Scan false-positives (documented, not leaks)
- The substring "Structure" matches the ordinary word **structure/structural/
  restructure** in the task instructions and in a case about companies restructuring
  workflows — not the company name. Verified in context.
- A broad grep for "Biobank" matches the **placeholder** `[National Biobank Cohort
  A]`, which is the anonymized replacement, not the original.

## Anonymization completeness & residual limitations
- Named people, companies, compounds, institutions, journals, funders, media
  outlets, and societies in BIAA-003/006/013 are replaced with typed placeholders.
- **Preserved on purpose:** numeric values, cohort sizes, follow-up, effect sizes,
  study design, evidence tier, comparison logic, disease lists, and the overclaiming
  **headline wording** in BIAA-013 (the headlines are the forensic object of that
  item). A determined party could still web-search a distinctive headline; the goal
  here is preventing *model prior-memory* recognition of the project/entities, which
  the placeholder substitution achieves for names.
- Clinical trial-phase wording was neutralized to mid-/late-stage descriptors to
  avoid the forbidden project-phase string while preserving evidence maturity.

## Reminder
Distribute per annotator: `README_FOR_ANNOTATOR.md`,
`annotator_taxonomy_reference.md`, `packets/`, and one response sheet each
(A: GLM-5.2, B: Fable 5, C: another strong model). Withhold this directory.
