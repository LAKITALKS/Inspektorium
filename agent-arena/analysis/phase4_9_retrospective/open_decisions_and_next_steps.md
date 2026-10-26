# Open Decisions & Next Steps (prioritized)

*All items are **[OPEN]** decisions or **[RECOMMENDATION]** actions. None are implemented here.*

## Case adjudication history (context) [FACT]
- **case040** — was overclaim (later borderline); **flipped to correlation_vs_causation** (clear/high)
  after curator review. Reason: the specific structural failure is causal inference from an
  uncontrolled pre/post design, not generic rhetorical overclaim. overclaim kept as alternative.
- **case041** — GLP-1 / aleniglipron weight-loss-pill showcase. Audited for demo-origin contamination;
  **kept active Core**. Reason: despite showcase origin, the claim is sufficiently isolated and the
  source voice (company + analysts, promotional) is unambiguous. Added `origin: curated_showcase`,
  `intake_review: passed`. Prompt unchanged.
- **case042** — Edge-AI readiness. **Retired from active metrics**. Reason: demo-derived exploratory
  origin + task-design confound (target claim embedded in an analytical paper that qualifies/critiques
  it; ambiguous source voice). Not hard-deleted, not label-flipped; default discovery excludes it.
- **case054** — **UNRESOLVED**. Current primary label overclaim; strong model stably reads
  mechanism_vs_evidence. Likely a granularity / taxonomy-precedence issue. Do not auto-flip.

## Prioritized action list

1. **case054 adjudication** [OPEN]. Decide primary label given a co-present in-vitro→clinical tier
   gap (mechanism) and decorative-hedge equivalence selling (overclaim). Options: keep overclaim +
   document; light rewrite to remove the tier-gap confound; or flip if a precedence rule says so.
   Do not flip solely on model behavior.
2. **Taxonomy precedence rule** [OPEN]. Decide, in general, whether a specific evidence-gap label
   (mechanism_vs_evidence / correlation_vs_causation) outranks generic `overclaim` when both apply,
   or vice versa. Document as an explicit rule and apply consistently.
3. **Regenerate active metrics** [REC]. After retirement (and any case054 change), produce a fresh
   active-set summary (49 cases) as a **new** artifact; leave Phase-5A historical reports frozen.
4. **Retrospective intake audit of the 49 active cases** [REC]. Apply the intake checklist
   (isolated claim, clear source voice, archived source, provenance) to catch other latent
   demo-origin/task-design issues.
5. **Phase 4.9 external audit with Fable 5** [REC]. Use this dossier as the input package.
6. **Phase 5B small model-panel probe** [REC]. Weak/mid/strong panel on a candidate subset
   (~15–20 cases: the boundary cases + a stratified sample), not a full expensive run; measure
   cross-model disagreement + weak-model error rate.
7. **Real-world case intake** [REC]. Only after schema/policy for archived sources + provenance is
   ready; verify sources; no fabricated citations.
8. **Replacement for case042** [REC]. Author a clean Edge-AI readiness overclaim case with a **new
   case_id**, isolated claim, unambiguous source voice; link via `superseded_by` / `supersedes`.
9. **Official analysis generator scripts** [REC]. Commit versioned, reproducible generators for the
   Phase-5A / active-set reports (currently out-of-repo scratchpad).
10. **Customer/public report safety review** [REC]. Before any external/customer output, review for
    source-safety (no full third-party article reproduction), calibration caveats, and clear
    historical-vs-active labelling.

## Explicitly not-yet-decided [OPEN]
- Whether `overclaim` should be treated as a residual/generic category.
- Whether to add secondary-label support to the schema.
- Whether to introduce a formal Core/Boundary/Retired/Quarantine suite split.
- Whether to add a holdout set to reduce co-evolution risk.

---

## Current update as of v0.8.2 [FACT]

*Appended 2026-07-10. The list above is the **v0.7.7 snapshot** and is preserved as
history. Progress since then (tags v0.8.0 → v0.8.2):*
- **case054 adjudication** — RESOLVED rule-first (no flip; primary stays `overclaim`);
  taxonomy precedence rule added (`docs/taxonomy_precedence.md`). (v0.7.9)
- **Taxonomy precedence rule** — DONE (v0.7.9).
- **Active-set diagnostics** — DONE as a new offline artifact
  (`analysis/phase5_0_active_library_diagnostics/`); Phase-5A left frozen. (v0.8.0)
- **Blind IAA** — design (v0.8.1) and strongly anonymized multi-annotator packets
  (v0.8.2) DONE.

### Corrected next-step ordering
1. **Phase 5.05c — ACTIVE NEXT STEP:** import blind annotator responses and compute
   agreement (`../phase5_05_blind_iaa_design/next_steps_after_iaa.md`). Not yet started.
2. IAA disposition → **Holdout Freeze**.
3. **Small Model Panel (5B / 5.1)** — gated behind 5.05c + holdout freeze.
4. **Three-case adversarial challenge** — small gated experiment, **after** holdout
   freeze and **before** the panel, **non-holdout cases only** (see the architecture
   ledger's "Current update as of v0.8.2").
5. Real-world intake — still deferred.

Historical Phase-5A metrics remain **frozen**. Forward roadmap detail, the greenfield
correction (calibrate/disagreement/audit-trail already exist), report-engine
extensions, duplicate-prevention notes, and the parked backlog live in
`architecture_ledger.md` → "Current update as of v0.8.2 — Claim Novelty Auditor
deduplication integration". No new roadmap file was created.
