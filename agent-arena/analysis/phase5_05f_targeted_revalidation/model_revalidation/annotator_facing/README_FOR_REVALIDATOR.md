# Read Me — Independent Revalidator

You are an **independent revalidator** for a claim-forensics taxonomy task. Evaluate
**exactly two packets** (`RVAL-001` and `RVAL-002`) and record your answers on your assigned
response sheet.

## How to work
- Apply **only** the supplied four-label taxonomy in `annotator_taxonomy_reference.md`.
- Make an **independent** judgment from the packet content and the taxonomy alone.
- **Do not use the web.**
- **Do not** try to identify the original source, study, product, or case.
- **Do not** search for or reuse any previous Agent Arena material.
- **Do not** consult another model, and do not reuse or look for any earlier answers.
- **Complete every field** on your response sheet, using **only the permitted values**.
- **Preserve the `RVAL-###` identifiers** exactly; one row per packet.
- **Do not alter the packet text.**
- Return a **valid CSV** file matching the provided header.
- **Do not** provide benchmark scores, comparisons, or an overall verdict.

## What to record per packet
- `primary_label` (one of the four taxonomy labels), optional `secondary_label`
  (a different label or `none`), `confidence` (0–1), and a short `rationale`.
- Packet-quality fields: `source_voice_clear`, `claim_isolated`,
  `evidence_context_understandable`, `multiple_competing_claims_present`,
  `material_packet_defect` (+ notes if yes), `recommended_human_review`, `ambiguity_notes`,
  and any `freeform_notes`.

Your independent reading is the measurement. There is no answer key to request, and no
"expected" label. Judge only the claim/evidence structure in front of you.
