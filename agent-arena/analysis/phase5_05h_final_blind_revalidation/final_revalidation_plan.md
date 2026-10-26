# Phase 5.05h — Final Blind Revalidation Plan (frozen before collection)

**study designation:** final_single_packet_two_family_blind_revalidation
**source checkpoint:** commit `6420303760e8dab37c1feaeb23069b562db3d703` · tag `v0.8.9-biaa013-v3-remediation`
**acceptance criteria version:** 5.05h/1.0

> This design is frozen before any result is observed. No final-revalidation result exists.

## Source and opaque identifier
- **Source packet:** BIAA-013_v3 (approved).
- **Source hash:** `1f6eadad2d28f325244e95be73a3ed153fafd34250ef8afd1536b38e1d6bec29`.
- **Opaque revalidation ID:** **FXR-731** (reveals no BIAA-013, RVAL-001, source case ID, gold
  label, or packet history).

## Pre-specified revalidators (approved before collection)
- **P:** Anthropic / Opus 5 — fresh isolated session.
- **Q:** GLM / GLM 5.2 — fresh isolated session.

## Independence requirements
Fresh isolated sessions; no prior Agent Arena conversation context; no web/retrieval; no
earlier BIAA or RVAL packet; no previous response; no gold label; no internal mapping; no
interaction between P and Q; identical bundle and taxonomy; each result preserved before any
comparison.

## Frozen case-level acceptance criteria (5.05h/1.0)
The packet receives **PASS_CANDIDATE** only if **all** hold:
1. **Both** revalidators assign the existing gold label as **primary**.
2. **Both** mark `source_voice_clear = yes`, `claim_isolated = yes`, `evidence_context_understandable = yes`.
3. **Both** mark `material_packet_defect = no`.
4. **Neither** identifies: multiple materially competing evaluated claims; ambiguous source
   attribution; missing claim isolation; a new serious taxonomy-boundary problem.
5. **No** material-defect or ambiguity note remains unresolved.
6. If **either** revalidator marks `material_packet_defect = yes/uncertain`,
   `source_voice_clear != yes`, `claim_isolated != yes`, `evidence_context_understandable != yes`,
   or `recommended_human_review = yes`, then the automatic status **cannot** be PASS_CANDIDATE
   and **curator review is required**.

**Provisional statuses:** PASS_CANDIDATE · CURATOR_REVIEW_REQUIRED · FAIL.
**These criteria must not be relaxed after collection begins.**

## Standing statements
- Passing **permits later holdout consideration only**; it does **not** select or freeze the case.
- Failure does **not** automatically change the gold label.
- This is **model revalidation, not human IAA**.
- **No kappa statistic will be interpreted for one case** (single-packet design).
