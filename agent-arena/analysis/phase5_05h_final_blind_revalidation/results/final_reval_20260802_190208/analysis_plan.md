# Phase 5.05h — Final Blind Revalidation Result-Analysis Plan (frozen before mapping/gold)

**run_id:** final_reval_20260802_190208  ·  **written_at (UTC):** 2026-08-02T19:02:08Z
**repository_commit:** 2aa15fbf7980ba8e90d55aba5f33d2a8fcfb6852 · **repository_tag:** v0.8.10-final-revalidation-prep
**study_designation:** final_single_packet_two_family_blind_revalidation
**acceptance_criteria_version:** 5.05h/1.0

> Written **before** the internal FXR→BIAA mapping, the source-packet identity, or the gold
> label is accessed, and before any comparison or result is computed. Fresh run; no aborted or
> previous directory reused. This is a targeted two-family blind **model** revalidation of one
> claim-isolated packet — **not** human IAA.

## Scope
- opaque_case_count: 1 (FXR-731) · revalidator_count: 2 · model_family_count: 2.
- No kappa / inferential agreement statistic for a single case (descriptive one-case evidence only).
- No result-driven exclusion · no gold or taxonomy modification · no holdout selection or freeze
  · no live model calls · no commit in this step.

## Verified inputs (structurally validated and preserved BEFORE comparison; neither excluded)
| revalidator | model | verified canonical sha256 |
|-------------|-------|---------------------------|
| P | Anthropic / Opus 5 | 4b6f503721134abdcb806de200e0fae7cdc6483674dc92ecacc56498bc6df836 |
| Q | GLM / GLM 5.2 (pasted_output) | db1ca2e103dd81406b721de07af348310b4a8b0e7fb2c7f59d5ad4113fd76f98 |

**Frozen bundle hash:** 2a4e360a4c8321829bc0cd8b632bdbf10666fef76042fe0695f7e225b6c27324

## Planned descriptive analyses (STEP 5)
Per-field P-vs-Q comparison: primary/secondary label, confidence, source_voice_clear,
claim_isolated, evidence_context_understandable, multiple_competing_claims_present,
material_packet_defect (+notes), recommended_human_review, ambiguity_notes, freeform_notes,
rationale summary; P-vs-gold and Q-vs-gold primary; gold-primary vote count; soft/serious
disagreement count.

## Frozen acceptance criteria (copied verbatim from committed final_revalidation_plan.md — not relaxed, reinterpreted, or added to)
The packet receives **PASS_CANDIDATE** only if **all** hold:
1. **Both** revalidators assign the existing gold label as **primary**.
2. **Both** mark `source_voice_clear = yes`, `claim_isolated = yes`, `evidence_context_understandable = yes`.
3. **Both** mark `material_packet_defect = no`.
4. **Neither** identifies: multiple materially competing evaluated claims; ambiguous source attribution; missing claim isolation; a new serious taxonomy-boundary problem.
5. **No** material-defect or ambiguity note remains unresolved.
6. If **either** revalidator marks `material_packet_defect = yes/uncertain`, `source_voice_clear != yes`, `claim_isolated != yes`, `evidence_context_understandable != yes`, or `recommended_human_review = yes`, then the automatic status **cannot** be PASS_CANDIDATE and **curator review is required**.

**Provisional statuses:** PASS_CANDIDATE · CURATOR_REVIEW_REQUIRED · FAIL. Not relaxed after collection.

## Confirmation
This plan was written **before** any FXR→BIAA mapping or gold-label access. It contains no gold
label, no mapping, no predicted result, and neither revalidator's substantive answer.
