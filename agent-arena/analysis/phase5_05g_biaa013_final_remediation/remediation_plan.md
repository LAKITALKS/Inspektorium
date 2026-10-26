# Phase 5.05g — BIAA-013 Final Claim-Isolation Remediation Plan (written before v3)

**source checkpoint:** commit `31c6310ad01d3be061f81a4a13ae2e86210ee46c` · tag `v0.8.8-targeted-revalidation-results`
**written_at (UTC):** 2026-08-02T15:50:09Z
**acceptance criteria version:** 5.05f/1.0

> This plan is written **before** BIAA-013_v3 is created. This is a narrow, versioned
> remediation loop following the archived Phase 5.05f curator decision — not a reopening of
> the full Phase 5.05 study.

## Existing revision under remediation
- **BIAA-013_v2 path:** `analysis/phase5_05e_targeted_curation/revised_packets/annotator_facing/packets/BIAA-013_v2.md`
- **BIAA-013_v2 SHA-256:** `17b3aebdd3d4291e598a2c08fac229bc64b91e0b872c2417cab0da935c089680` (immutable)
- **Current gold label:** `correlation_vs_causation` (unchanged; internal target study-forensics-public-001)
- **Taxonomy reference SHA-256:** `c8c9f5c35da6d62e4a9dcffcb6b0c0b3c1604fc66b0e94795832b7f792bc872e` (four-label taxonomy, unchanged)

## Exact curator-authorized problem
Insufficiently explicit **claim isolation**: BIAA-013_v2 presents the study finding, three
media headlines, and two author quotations together without designating **one** exact
evaluated public claim, making the evaluated target reading-dependent (Revalidator-X flag in
Phase 5.05f).

## Authorized change
Isolate **one exact existing public claim** (verbatim, single speaker) as the evaluated
claim; reposition the remaining material as clearly-labelled evidence/additional context.

## Prohibited changes
- No gold-label change · no taxonomy change · no new/removed evidence · no change to the
  source meaning or evidence tier · no modification of BIAA-013_v1 or BIAA-013_v2 (historical
  packet versions remain immutable) · no synthesis of multiple speakers into one claim.

## Statements
- **BIAA-013_v3 requires a fresh blind revalidation** (a new opaque identifier, fresh isolated
  sessions) before any holdout consideration.
- **BIAA-013_v3 remains holdout-ineligible** until that revalidation passes.
- **No source case / YAML change is assumed necessary**; if selection turns out to require one,
  that is escalated rather than performed silently.

## Fail-stop
If no single existing candidate satisfies all eight STEP-5 conditions, BIAA-013_v3 is **not**
created; the case is reported structurally unsuitable (retirement or development-only
retention), and the phase stops for curator decision. No solution is manufactured.
