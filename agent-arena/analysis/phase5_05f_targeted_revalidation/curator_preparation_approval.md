# Phase 5.05f — Curator Preparation Approval

- **Decision date:** 2026-08-02
- **Phase 5.05f preparation approved:** yes
- **Annotation collection approved after this checkpoint:** yes
- **Acceptance criteria frozen:** yes
- **Acceptance criteria version:** 5.05f/1.0
- **Gold-label changes approved:** no
- **Taxonomy changes approved:** no
- **Holdout freeze approved:** no
- **Human review executed:** no
- **Live model calls already performed:** no

## Approved future collection design
- **Revalidator X:** first independent model family.
- **Revalidator Y:** second independent model family.
- **Revalidator Z:** third independent model family.
- Identical annotator-facing bundle for every revalidator.
- Fresh, isolated sessions.
- No web retrieval.
- No prior responses.
- No internal mapping.
- Raw results preserved before any comparison.

## Explicit statements
- **This commit freezes the design before any result is observed.**
- **The acceptance criteria may not be relaxed after collection begins.**
- **No revalidator may be excluded because of an unfavorable result.**
- **Model revalidation is not human IAA** and is not a substitute for human review.
- **BIAA-007 remains outside the holdout** (active borderline/development case; human review
  deferred).
- **BIAA-019 remains retired.**
- **No holdout selection begins during targeted revalidation.**

*This repository-facing record contains no gold labels and no internal RVAL→case mapping;
those remain only under `model_revalidation/internal_only/`.*
