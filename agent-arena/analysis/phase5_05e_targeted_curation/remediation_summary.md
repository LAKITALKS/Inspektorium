# Phase 5.05e — Remediation Summary

Source checkpoint: commit `a4027d7` · tag `v0.8.5-proxy-iaa-curator-review`. All actions
are the ones approved in the immutable Phase 5.05d curator decision (disposition **B**).
Nothing was staged or committed. No live model calls. No metrics computed.

## Per-case

### BIAA-003
- **Original problem:** clear/anchor designation over-optimistic for a case a capable rater read as `solid`.
- **Approved action:** retain gold · re-designate borderline · clarify gold rationale.
- **Files changed:** `tasks/study_forensics/case009_mindfulness_autism.yaml`.
- **Exact remediation:** `gold_case_type` clear→borderline; `ambiguity_level` medium→high; appended precedence clarification to `gold_justification`; recorded re-designation in `curator_notes`.
- **Gold changed:** no · **Taxonomy changed:** no · **Revised packet created:** no.
- **Holdout eligibility:** eligible (no packet defect). **Targeted revalidation required:** no.
- **Unresolved curator decision:** none.

### BIAA-007
- **Original problem:** genuine mechanism-vs-overclaim boundary; needs explicit precedence + independent human check.
- **Approved action:** retain gold · add precedence explanation · request independent human review.
- **Files changed:** `tasks/study_forensics/case043_cell_study_cancer_cure.yaml`; new `human_review/BIAA-007_independent_human_review_request.md`.
- **Exact remediation:** appended explicit precedence explanation to `gold_justification`; recorded holdout-ineligibility (pending review, not yet performed) in `curator_notes`; created a blind human-review request (no gold, no model votes, no model names).
- **Gold changed:** no · **Taxonomy changed:** no · **Revised packet created:** no.
- **Holdout eligibility:** ineligible until independent human review completed. **Targeted revalidation required:** independent human review.
- **Unresolved curator decision:** independent human review outcome.

### BIAA-013
- **Original problem:** packet embedded an analysis instruction naming all four taxonomy terms; non-standard headings; ~4× mean length.
- **Approved action:** revise packet construction · remove embedded instruction · normalize · exclude from holdout.
- **Files changed:** new `revised_packets/annotator_facing/packets/BIAA-013_v2.md` (original packet untouched).
- **Exact remediation:** removed the instruction line; normalized to the 3-heading template (Study/Media as inline bold); preserved all claim and evidence verbatim; no evidence shortened.
- **Gold changed:** no · **Taxonomy changed:** no · **Revised packet created:** yes (`BIAA-013_v2.md`).
- **Holdout eligibility:** ineligible until revalidated. **Targeted revalidation required:** yes.
- **Unresolved curator decision:** none (mechanical fix); revalidation pending.

### BIAA-016
- **Original problem:** company claim and university critique interleaved; three raters flagged claim-isolation.
- **Approved action:** isolate exact evaluated claim · mark borderline · revise packet · revalidate.
- **Files changed:** `tasks/study_forensics/case037_mindfulness_app.yaml`; new `revised_packets/annotator_facing/packets/BIAA-016_v2.md`.
- **Exact remediation:** v2 packet separates evidence context from the single verbatim company claim (caveats flagged as context); YAML `ambiguity_level` medium→high, `curator_notes` records isolation. No paraphrase strengthened/weakened the claim; no evidence added.
- **Gold changed:** no · **Taxonomy changed:** no · **Revised packet created:** yes (`BIAA-016_v2.md`).
- **Holdout eligibility:** ineligible until revalidated. **Targeted revalidation required:** yes.
- **Unresolved curator decision:** none (revalidation pending).

### BIAA-019
- **Original problem:** materially ambiguous source voice; no single claim-maker for one evaluated claim.
- **Approved action:** clarify source voice · decide revision-vs-retirement · exclude from holdout.
- **Proposed → approved → executed:** retirement proposed (Phase 5.05e), **approved** by curator (v0.8.6), and **executed**.
- **Files changed:** `tasks/study_forensics/case031_rapamycin_longevity.yaml` (retirement flags + reason); `case_decisions/BIAA-019.md`.
- **Exact remediation:** set `status: retired` + `excluded_from_active_metrics: true` (case042 precedent); retirement reason recorded in `curator_notes`. No revised packet. Library counts 49/1 → **48 active / 2 retired** (total 50).
- **Gold changed:** no (`solid`) · **Taxonomy changed:** no · **Revised packet created:** no.
- **Retirement:** approved: yes · executed: yes · deleted: no · historical packet retained: yes.
- **Holdout eligibility:** ineligible (retired). **Targeted revalidation required:** no.
- **Unresolved curator decision:** none (retirement executed).

## Action-status matrix (proposed / approved / executed / pending)
| case | proposed | approved | executed | still pending |
|------|----------|----------|----------|---------------|
| BIAA-003 | metadata+rationale | yes | yes | — |
| BIAA-007 | precedence note + human-review request | yes | precedence note yes | **independent human review** |
| BIAA-013 | v2 packet | yes | v2 packet yes | **targeted blind revalidation** |
| BIAA-016 | v2 packet + borderline | yes | yes | **targeted blind revalidation** |
| BIAA-019 | retirement | yes | **retirement executed** | — |

Also pending: **holdout selection and freeze** (Phase 5.05f), which must not begin until the
above pending items are resolved.

## Invariants
- Gold-label invariance: **PASS** (all five identical before/after).
- Taxonomy invariance: **PASS**.
- Historical-artifact invariance (5.05c, 5.05d, original packets, blind index): **PASS**.
- Tests: focused 157 passed; full unit suite 1008 passed (no live model calls).
- Contamination scan of revised annotator-facing material: clean.

## Open items requiring curator approval
1. BIAA-019 retirement (or scoped retention).
2. BIAA-007 independent human review (then holdout eligibility).
3. Targeted blind revalidation of `BIAA-013_v2` and `BIAA-016_v2`.
4. Whether to apply the BIAA-003/007/016 source-YAML metadata edits (currently unstaged, working-tree only).
