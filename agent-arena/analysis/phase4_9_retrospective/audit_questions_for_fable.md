# Audit Questions for Fable 5 (external benchmark-integrity review)

These are targeted questions for an external auditor. They are deliberately phrased to invite
disagreement; we are not seeking confirmation.

## Methodology & process
1. Is the phase progression from v0.6 to v0.7.7 methodologically sound — small isolated changes,
   tagged rollback points, tests green at each step? Where is the process weakest?
2. Did we handle **case042** correctly by *retiring* it (default-excluded, kept, not label-flipped)
   rather than deleting or flipping it? Is retirement-without-deletion the right primitive?
3. Did we handle **case041** correctly by keeping it active Core while documenting its
   `curated_showcase` origin and `intake_review: passed`? Is "showcase origin but intake-clean" a
   defensible category?

## Taxonomy & adjudication
4. How should **case054** be adjudicated (gold overclaim vs the model's stable mechanism_vs_evidence
   reading), given a co-present in-vitro→clinical tier gap and decorative-hedge equivalence selling?
5. Should **mechanism_vs_evidence override generic overclaim** when both legitimately apply — or the
   reverse? What principle should decide?
6. Should **overclaim** be treated as a residual/generic category (assigned only when no specific
   evidence-gap label fits)?

## Design sufficiency
7. Is the active/retired filtering design sufficient (default-exclude, `--include-retired`, explicit
   `--case-id`, `suite_history`), or does it need a fuller lifecycle model?
8. What should change **before Phase 5B** (the model-panel probe)?
9. What should change **before importing real-world cases** (provenance, citations, verification)?
10. What should change **before scaling to 100–200 cases** (schema, suites, review workflow)?

## Risk & readiness
11. What are the **highest benchmark-integrity risks** right now?
12. What would make this benchmark **publishable or customer-safe**?
13. **Where are we overfitting to one strong model?** Which gold-label corrections look most like
    co-evolution rather than taxonomy fixes?
14. Are we **separating historical vs current active metrics** correctly (Phase-5A frozen; active-set
    metric not yet re-measured)?
15. If you were the external auditor, **what would you prioritize next**?

## Specific artifacts to inspect
- `analysis/phase5a/lib_20260704_134553_55aa66/` (historical single-model diagnostics)
- `docs/case_intake_policy.md`
- `tasks/study_forensics/case040_*, case041_*, case042_*, case054_*`
- `src/agent_arena/run_library.py` (`discover_cases`, `is_retired`) and `schemas.py` (Task fields)
