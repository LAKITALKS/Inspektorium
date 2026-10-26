# Phase 5.05f — Targeted Blind Model-Revalidation Plan (frozen before packet exposure)

**Study designation:** `targeted_versioned_blind_model_revalidation`
**Source checkpoint:** commit `4da78d5b09526516eb837ed7cb846519c6eb9b32` · tag
`v0.8.6-targeted-curation`.
**acceptance_criteria_version:** `5.05f/1.0`

> This plan is frozen **before** any annotator-facing packet is exposed. The acceptance
> criteria below are pre-specified and must not be relaxed or changed after observing
> results. This is preparation only — no live model calls, no response collection.

## Targets and opaque identifiers
- **RVAL-001** maps internally to **BIAA-013_v2** (packet-construction remediation).
- **RVAL-002** maps internally to **BIAA-016_v2** (claim-isolation remediation).

Fresh opaque `RVAL-###` identifiers are used so external revalidators cannot connect the
packets to the original Phase 5.05c blind IDs. The RVAL→BIAA mapping lives only in
`model_revalidation/internal_only/revalidation_id_map.csv`.

## Planned independent revalidators
- **Revalidator X** — one model family.
- **Revalidator Y** — a second model family.
- **Revalidator Z** — a third model family, where practical.

## Collection requirements
- Fresh sessions; no previous Agent Arena conversation context.
- No web retrieval; no original v1 packets; no previous responses; no gold labels; no
  internal mapping; no model-to-model discussion.
- Identical annotator-facing bundle for every revalidator.
- Independent completion of response sheets.
- Raw responses preserved before any comparison.

## Two evaluated dimensions
**A. Taxonomy outcome:** primary label, optional secondary label, confidence, rationale.
**B. Packet-remediation quality:** source_voice_clear, claim_isolated,
evidence_context_understandable, multiple_competing_claims_present, material_packet_defect,
recommended_human_review, ambiguity_notes.

## Pre-specified case-level acceptance criteria (frozen)
A revised packet passes targeted revalidation only if **all** hold:
1. At least **two of three** independent revalidators assign the existing gold label as
   their **primary** label.
2. **No majority** assigns a different primary label.
3. At least **two of three** mark `source_voice_clear = yes`, `claim_isolated = yes`, and
   `evidence_context_understandable = yes`.
4. **No majority** identifies `material_packet_defect = yes`.
5. **No individual** material-defect report remains unresolved after curator inspection.
6. **No serious disagreement** reveals a new taxonomy-boundary problem.
7. Any remaining disagreement is explicitly documented and curator-reviewed.

### If only two independent revalidators are ultimately collected
- **Both** must assign the existing gold label as primary;
- **both** must mark source voice, claim isolation, and evidence context as clear;
- **neither** may identify a material packet defect;
- otherwise the packet does **not** pass and requires either a third revalidator or further
  curation.

**These criteria must not be relaxed or changed after observing results.**

## Holdout rules
- **BIAA-007:** excluded (deferred; active development case).
- **BIAA-019:** excluded (retired).
- **BIAA-013_v2 (RVAL-001):** eligible for later holdout consideration **only after**
  passing targeted revalidation.
- **BIAA-016_v2 (RVAL-002):** eligible for later holdout consideration **only after**
  passing targeted revalidation.

**No holdout selection or freeze occurs in this phase.**
