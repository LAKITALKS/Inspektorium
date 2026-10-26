# BIAA-013 — Case Decision

**Approved actions:** revise packet construction · remove embedded analysis instruction ·
normalize packet structure · exclude from holdout until revalidated.

**Defect (original packet).** The case-material section opened with an embedded analysis
instruction — "Analyze the following study summary and media coverage for epistemological
integrity. Identify any overclaims, unsupported causal inferences, mechanism gaps, or
correlation-as-causation issues." — which names all four taxonomy categories verbatim, and
used non-standard `## Study` / `## Media Coverage` sub-headings; the packet was also ~4×
the corpus mean length.

**Implemented — revised packet `BIAA-013_v2.md`:**
- Removed the embedded analysis instruction (the only curator-facing/taxonomy-naming text).
- Normalized to the standard three-heading template (Task / Case material / Your
  annotation); the study and media blocks are retained as inline **bold** labels, not `##`
  headings.
- Preserved the public claim and all evidence verbatim (study title, design, findings,
  stated limitations, funding, all three media headlines, both author quotes).
- No evidence was shortened to equalize length; only the non-evidence instruction and the
  divergent heading markup were changed.

**Not changed:** gold_label (`correlation_vs_causation`), source YAML (`prompt`/`context`
left as historical source), taxonomy, original packet (byte-identical).

**Holdout eligibility:** ineligible until targeted blind revalidation of `BIAA-013_v2.md`.
