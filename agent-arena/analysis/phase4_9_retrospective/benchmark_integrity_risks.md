# Benchmark Integrity Risks (as of v0.7.7)

*Each item: **[FACT]** (observed), **[INTERPRETATION]** (our reading), **[RISK]** (what could go
wrong), **[MITIGATION/REC]** (proposed, not yet implemented unless stated).*

## 1. Single strong model ceiling
- [FACT] All measurement to date is against one strong model (Opus 4.5). Phase-5A: 96% accuracy,
  0 unstable, 0 high-variance.
- [RISK] "96%" reads as validity but is a ceiling/stability figure. A benchmark that one strong
  model finds trivial has undemonstrated discrimination power.
- [REC] Phase 5B heterogeneous model panel (weak/mid/strong) on a candidate subset.

## 2. Gold-label co-evolution / overfitting to one model
- [FACT] Several gold labels were reviewed after live probes (043/044/045/048/040).
- [INTERPRETATION] Each change was justified on **taxonomy grounds first**, with model agreement
  as corroboration — not by matching the model.
- [RISK] Repeatedly "correcting" gold toward one model's behavior silently overfits the benchmark
  to that model.
- [MITIGATION] Documented policy: do not flip labels solely because a model disagrees; require an
  independent taxonomy justification. [REC] Add a holdout set never used for gold tuning.

## 3. One-model disagreement handling
- [FACT] case042/case054 were flagged (stable-alternative) but not auto-flipped.
- [REC] Keep the rule explicit: single-model disagreement → human review queue, never automatic
  relabel.

## 4. Single-label taxonomy limitation
- [FACT] Exactly one `gold_label` per case from a 4-value set.
- [RISK] Cases with two legitimate failure modes (e.g., tier gap **and** rhetorical inflation)
  cannot be represented; forces an artificial single answer.
- [OPEN] Whether to add secondary-label support or a precedence rule.

## 5. Generic `overclaim` vs specific failure-mode ambiguity + missing precedence rule
- [FACT] case054: gold overclaim; model stably reads mechanism_vs_evidence (a real in-vitro→clinical
  tier gap co-exists with decorative hedging).
- [OPEN] No taxonomy precedence rule exists (e.g., "specific evidence-gap label outranks generic
  overclaim when both apply," or the reverse).
- [RISK] Without a rule, several borderline cases will remain permanent stable-alternative misses.

## 6. Boundary-case handling
- [FACT] 10 cases are `gold_case_type: borderline`. In Phase-5A, 8/10 were stable-correct; 2
  (042/054) stable-alternative.
- [REC] Formal Core/Boundary suite split so boundary cases are reported separately and don't
  distort a headline accuracy.

## 7. Retired-case handling
- [FACT] case042 retired via real filtering (default-excluded, not deleted, not flipped).
- [RISK] If future reports don't respect the active/retired split, retired cases could re-enter
  metrics or be lost from the audit trail.
- [MITIGATION] `docs/case_intake_policy.md` + `suite_history`; tests enforce default exclusion.

## 8. Stable-alternative handling
- [FACT] Defined and detected (042/054). [OPEN] No adjudication policy yet for what to do when a
  strong model is stably on a documented alternative reading.

## 9. Demo-origin contamination
- [FACT] case041 and case042 both came from the same early "showcase" template (source placeholder
  + subclaims + single central claim).
- [INTERPRETATION] case041 passed intake (unambiguous promotional source voice; isolated claim);
  case042 failed (claim embedded in an analytical paper that critiques it; ambiguous voice).
- [RISK] Other library cases may have latent demo-origin/task-design issues not yet audited.
- [REC] Retrospective intake audit of the remaining 49 active cases.

## 10. Source-voice ambiguity & claim-isolation
- [FACT] The intake policy now requires an isolated exact claim and a clear claim-maker.
- [RISK] Cases that bury the evaluated claim inside surrounding analysis measure task
  interpretation, not claim forensics (the case042 failure mode).

## 11. Real-world case verification
- [FACT] Current active library is entirely synthetic fixtures + 1 curated_showcase (041).
- [REC] Do not import real-world cases until schema/policy for archived sources, citations, and
  provenance is finalized; verify sources; avoid fabricated citations.

## 12. Confidence is uncalibrated self-report
- [FACT] `confidence` is the model's own number; the harness treats it as uncalibrated and does not
  convert it to a probability. Phase-5A explicitly labels it so.
- [RISK] Readers may misread confidence as calibrated. Keep the caveat prominent.

## 13. Historical vs active metrics separation
- [FACT] Phase-5A metrics were computed over all 50 (pre-retirement).
- [RISK] Silently recalculating or filtering old reports would corrupt the audit trail.
- [MITIGATION] Policy: historical reports are frozen; regenerate forward-looking metrics against
  the active set as a **new** artifact.

## 14. Reproducibility of analysis
- [FACT] The Phase-5A generator lives in an out-of-repo scratchpad; only its outputs are committed.
- [RISK] Reports are not reproducible from the repo alone.
- [REC] Commit official, versioned analysis generator scripts.
