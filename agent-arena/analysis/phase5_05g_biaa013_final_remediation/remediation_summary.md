# Phase 5.05g — Remediation Summary (BIAA-013_v3)

- **Original unresolved issue:** insufficiently explicit claim isolation in BIAA-013_v2 — the
  study finding, three media headlines, and two author quotations were presented together
  with no designated single evaluated public claim (Phase 5.05f Revalidator-X flag).
- **Selected exact claim (verbatim, single speaker):** "Our findings suggest that making some
  of your physical activity vigorous can provide substantial health benefits. This doesn't
  require going to the gym. Adding short bursts of activity that make you slightly breathless
  into daily life can make a real difference."
- **Source voice:** the study's lead author ([Author B]).
- **Files created:** `remediation_plan.md`, `candidate_claim_audit.md`, `remediation_summary.md`,
  `source_change_manifest.json`; `revised_packet/annotator_facing/BIAA-013_v3.md`;
  `revised_packet/internal_only/{claim_selection_record.md, semantic_diff_v2_to_v3.md,
  contamination_audit.md, revision_manifest.json}`.
- **Source YAML changed:** no.
- **Gold changed:** no (`correlation_vs_causation` before and after).
- **Taxonomy changed:** no.
- **Evidence changed:** no (all study findings, limitations, headlines, and the co-author
  quote preserved verbatim; nothing added or removed).
- **BIAA-013_v2 changed:** no (byte-identical; sha 17b3aeb…, matches approved).
- **v3 ready for revalidation:** yes — pending a fresh blind revalidation under a new opaque
  identifier and fresh isolated sessions.
- **Unresolved curator questions:**
  1. Approve BIAA-013_v3 and authorize the final fresh blind revalidation (new opaque id)?
  2. Confirm the lead-author quotation is the intended authoritative evaluated claim (vs. a
     media headline), given all three revalidators already reproduced the gold label on v2.

BIAA-013_v3 remains **holdout-ineligible** until that revalidation passes. No revalidation was
begun; no holdout was created; no live model calls were made.
