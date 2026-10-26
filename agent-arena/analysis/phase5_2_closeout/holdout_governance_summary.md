# Phase 5 — Holdout Governance Summary

*(Written from committed public artifacts only; no private holdout file was accessed.)*

- **Prospective internal holdout** — 16 opaque cases (HLD-001…HLD-016), **four per taxonomy label**.
- Selected by the **original deterministic seed + algorithm** (holdout_select_v1); **no manual swaps**.
- **Sealed outside Git:** private HLD→source mapping, per-HLD gold, the private evaluator packet set,
  the bundle/blank sheet, the eligibility ledger, and private rankings.
- **Committed:** only public cryptographic commitments (packet/bundle/sheet hashes + sizes) and
  aggregate label counts (4/4/4/4).
- **No evaluation performed; no results collected.**
- **Not historically untouched** — several selected cases participated in earlier Phase 5 curation/
  revalidation and are protected only from this freeze onward.
- **Statistical precision:** a 16-case holdout has a **6.25-percentage-point** raw accuracy resolution.
- **Membership-inferability limitation:** in the `correlation_vs_causation` and `mechanism_vs_evidence`
  strata **all four eligible cases were selected**, so source membership may be inferable to
  maintainers who know the approved pool; HLD ordering and the HLD→source / HLD→gold mappings
  nonetheless remain private.

## Standing rules (Phase 6–10)
- Selected holdout cases **may not** be used in development.
- **No holdout evaluation** before a **separately committed protocol**.
- Predictions must be **frozen before gold access**.
- **No result-driven replacement**; a material selected-case defect requires **versioned retirement
  and deterministic replacement**.
- Holdout results **cannot** establish universal superiority over every LLM or prompting strategy.
