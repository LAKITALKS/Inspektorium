# Read Me — Targeted Revalidation (Revised Packets)

These are **versioned revised packets** (`packet_version: 2`) produced by targeted curation.

- They are **not** the packets used in the original blind run. Do not treat them as the
  originals, and **do not mix them with the original response sheets**.
- Only the listed revised cases are in scope for this revalidation:
  - `BIAA-013_v2.md` (packet construction normalized)
  - `BIAA-016_v2.md` (evaluated claim isolated)
- Each revised packet preserves its original `blind_case_id`, states `packet_version: 2`,
  and contains no real case identifier, no expected answer, no prior annotator result, and
  no model identity.
- Classify each revised packet independently using `annotator_taxonomy_reference.md`, the
  same four-label taxonomy as the original run. Record answers on a **fresh** revalidation
  response sheet, one row per `blind_case_id`.
- Annotators receive only this annotator-facing folder and the taxonomy reference — never
  any internal curation records, mappings, or manifests.

Cases handled separately and **not** part of this revalidation packet set: BIAA-003 and
BIAA-007 (internal rationale/designation only), and BIAA-019 (handled separately).
