# Phase 5.1a — Curator Approval

- **Decision date:** 2026-08-02
- **Minimal holdout-pool augmentation approved:** yes
- **Deterministic candidate selection approved:** yes
- **Packets approved:** exactly three
- **correlation_vs_causation additions:** exactly one
- **mechanism_vs_evidence additions:** exactly two
- **Source-YAML changes approved:** no
- **Gold-label changes approved:** no
- **Taxonomy changes approved:** no
- **Model evaluation approved:** no
- **Holdout selection approved in this phase:** no
- **Holdout freeze approved in this phase:** no
- **Phase 5.1 may restart after this checkpoint:** yes

## Statements
- Approval concerns **packet suitability and blind-packet construction only**.
- The three cases are added to the **approved holdout-candidate pool**; they are **not**
  automatically selected for the holdout.
- The original deterministic balanced holdout design (16 cases, four per label) remains **unchanged**.
- Phase 5.1 must **rank the complete eligible pool anew**; **no manual preference** may be given to
  the newly created cases.
- Passing this augmentation **does not evaluate Agent Arena performance**.
- **No further model revalidation is required** unless a specific unresolved packet defect is found.
