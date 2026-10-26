# Post-v0.7.9 Open Risks

*Carried forward from the Phase 4.9 dossier and updated for the v0.7.9 state.
**[FACT]** observed / **[RISK]** what could go wrong / **[REC]** proposed.*

## 1. Single-curator gold — unresolved [RISK]
- [FACT] All gold labels reflect a single curator's judgement (taxonomy-first, but
  one curator).
- [RISK] No independent check that the labels are reproducible by another annotator.
- [REC] Phase 5.05 blind inter-annotator agreement (IAA) design.

## 2. Blind inter-annotator agreement — missing [RISK]
- [FACT] No blind second-annotator pass has been run on any subset.
- [RISK] Gold quality is asserted, not measured. Borderline cases (9 active) are
  most exposed.
- [REC] Blind-label a stratified subset (clear + borderline + all 4 labels); report
  Cohen's/Krippendorff agreement before any accuracy claim.

## 3. Holdout — not frozen [RISK]
- [FACT] No holdout set is frozen; every case is visible to gold tuning.
- [RISK] Co-evolution / overfitting: labels could drift toward one model over time.
- [REC] Freeze a never-tuned holdout slice before further label review.

## 4. Small model panel — not run [RISK]
- [FACT] All measurement to date is one strong model (Opus 4.5). No weak/mid/strong
  panel exists.
- [RISK] "96%" is a single-model **ceiling/stability** figure, not demonstrated
  discrimination power.
- [REC] Phase 5.1 small heterogeneous panel on a candidate subset (~15–20 cases).

## 5. Active metrics after retirement — not live-remeasured [RISK]
- [FACT] The 49-case active set has **never** been measured in a fresh live run.
  The only live numbers are the frozen 50-case Phase-5A run.
- [RISK] Treating the derived 97.96% (exclude-case042) as an active benchmark would
  be wrong — it is arithmetic on old records, not a new run.
- [REC] Run a fresh active-set baseline (Phase 5.1+) and publish as a new artifact.

## 6. Historical vs active separation — must hold [FACT/REC]
- [FACT] Phase-5A (50-case) reports are frozen; this Phase-5.0 bundle is separate
  and clearly labelled offline/derived.
- [REC] Never silently recalculate or overwrite the frozen reports; always emit
  forward-looking metrics as new artifacts.

## 7. Calibration metrics — not implemented [RISK]
- [FACT] `confidence` is the model's uncalibrated self-report; no reliability
  diagram / ECE is computed.
- [RISK] Readers may misread confidence as a calibrated probability.
- [REC] Add calibration metrics (or keep the uncalibrated caveat prominent) before
  any external reporting.

## 8. Real-world intake — postponed [FACT]
- [FACT] The active library is entirely synthetic fixtures + 1 curated_showcase
  (041) + 1 public-prefixed case. No real-world mass import has been done.
- [REC] Do not import real-world cases until archived-source + provenance schema and
  citation verification are ready.

## 9. Metadata provenance gaps [RISK]
- [FACT] 27 active cases lack `origin`; 48 active cases lack `intake_review` (only
  case041 has both).
- [RISK] Provenance is undocumented for the legacy hand-curated block; latent
  demo-origin/task-design issues (the case042 failure mode) may exist un-audited.
- [REC] Retrospective intake audit + provenance backfill for the legacy cases.

## 10. Analysis generators — partly outside repo [RISK]
- [FACT] The Phase-5A generator lived out-of-repo; this Phase-5.0 bundle was
  produced by an offline scratchpad generator (outputs committed, generator not).
- [RISK] Reports are not fully reproducible from the repo alone.
- [REC] Commit versioned, official generator scripts for Phase-5A / active-set /
  Phase-5.0 diagnostics.

## 11. Class balance [RISK]
- [FACT] Active labels are imbalanced: overclaim 23 (46.9%) vs mechanism 6 and
  correlation 6 (12.2% each).
- [RISK] A headline accuracy is dominated by the overclaim class; thin specific
  categories (6 cases each) give noisy per-label estimates.
- [REC] Report per-label metrics, not just a headline; grow the thin categories
  before any discrimination claim.
