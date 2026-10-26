# Curator Review Queue — Phase 5.05h final revalidation

Provisional case status: **CURATOR_REVIEW_REQUIRED**. No adjudication performed; no label changed; no holdout action.

## Taxonomy-label outcome — PASS
Both P and Q assigned the existing gold label (`correlation_vs_causation`) as primary, with
`overclaim` as secondary. Unanimous; soft 0, serious 0.

## Unresolved packet-quality item (frozen criterion 5)
- **Source:** Revalidator P (Opus 5), freeform_notes.
- **Verified concern:** the FXR-731 (and upstream BIAA-013_v3) packet's `## Your annotation`
  section still lists the **original blind-packet field names** — `evidence_matches_claim_strength`
  and `missing_evidence_notes` — which **do not match** the 5.05h response-sheet schema
  (`evidence_context_understandable`, `multiple_competing_claims_present`, `material_packet_defect`,
  `material_packet_defect_notes`). Confirmed by inspection.
- P marked `material_packet_defect = no` and stated the discrepancy "did not impede evaluation";
  the frozen auto-gate (criterion 6) therefore did **not** trigger. This is a residual
  packet-construction inconsistency, not a taxonomy or claim-isolation failure.
- **Curator question:** should the packet's embedded `## Your annotation` field list be updated
  to match the revalidation response-sheet schema (a cosmetic v4 / template fix) before the case
  is considered fully clean and holdout-eligible? The claim-isolation objective (the reason for v3)
  is corroborated as met by both revalidators.

## Not blocking
- Both revalidators' `ambiguity_notes` document a self-resolved "borderline vs solid" reading
  (the 'suggest' hedge) that both resolved toward the gold — consistent with the documented
  secondary reading; not a new taxonomy-boundary problem.
