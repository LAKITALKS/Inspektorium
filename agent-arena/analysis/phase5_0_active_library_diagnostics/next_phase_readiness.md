# Next-Phase Readiness Assessment (post-v0.7.9)

*READY / NOT READY / READY AFTER X, with rationale. Offline assessment; no live
runs were performed.*

## Summary verdicts
| Next step | Verdict |
|---|---|
| Phase 5.05 — Blind IAA design | **READY** |
| Holdout Freeze (planning) | **READY** |
| Phase 5.1 — Small Model Panel Probe | **READY AFTER** holdout freeze + subset selection |
| Schema v2 (secondary labels / suite field) | **READY AFTER** IAA + precedence-rule usage informs the schema |
| Real-world (mass) case intake | **NOT READY** |
| Public benchmark claims | **NOT READY** |
| Customer-facing accuracy numbers | **NOT READY** |

## Detail

### Phase 5.05 — Blind Inter-Annotator Agreement design — **READY**
The taxonomy is documented (`study_forensics_taxonomy.md`), a precedence rule
exists (`taxonomy_precedence.md`), gold labels + alternative readings are present,
and the active/borderline split is known. Enough structure exists to design a blind
second-annotator protocol on a stratified subset. **This is the recommended next step.**

### Holdout Freeze — **READY (to plan)**
The active set is stable (49 cases, clean tests). A holdout slice can be selected
and frozen now to cut co-evolution risk before further label review. Recommend
freezing before Phase 5.1 so the panel probe does not touch the holdout.

### Phase 5.1 — Small Model Panel Probe — **READY AFTER** holdout freeze + subset
Mechanically ready (offline fake provider + `run_library` harness exist). Should
follow the holdout freeze and a stratified subset choice (boundary cases + a
per-label sample) so the panel measures discrimination, not the full set. This is
where a **new live active-set measurement** would occur — none exists yet.

### Schema v2 — **READY AFTER** IAA + precedence signal
Known gaps (single-label limitation, no secondary-label support, no formal `suite`
field, `intake_review`/`origin` not required) argue for a v2 schema — but design it
**after** IAA and precedence-rule usage show what fields are actually needed.

### Real-world mass intake — **NOT READY**
Blocked on: archived-source + citation-verification schema, provenance backfill for
the 27 legacy cases missing `origin`, and the intake policy's source-voice /
claim-isolation checks. Do not import until these exist.

### Public benchmark claims — **NOT READY**
Blockers: single-model ceiling only (no discrimination measurement), no blind IAA,
no frozen holdout, no calibration metrics, class imbalance. "96%" is a frozen
single-model stability figure, not validated benchmark accuracy.

### Customer-facing accuracy numbers — **NOT READY**
The active 49-case set has never been live-measured; the only live numbers are the
frozen 50-case Phase-5A run. Any customer-facing figure would require a fresh
active-set live baseline, per-label reporting, and calibration caveats first.

## Recommended immediate path
1. **Phase 5.05 Blind IAA design** (start here).
2. **Holdout freeze planning** in parallel.
3. Then **Phase 5.1 small panel probe** for the first real discrimination signal.
4. Keep real-world intake, public claims, and customer numbers gated until the above
   land.
