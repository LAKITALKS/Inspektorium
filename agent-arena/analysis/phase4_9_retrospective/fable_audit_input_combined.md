# Agent Arena — Combined Fable 5 Audit Input

> **Instructions for Fable 5 (external benchmark-integrity auditor)**
>
> You are being asked to review the benchmark integrity of **Agent Arena**, a claim-forensics
> evaluation library, at tag **v0.7.7-retire-case042**. This single file bundles the five
> dossier documents you need; no repo access is required to form an initial opinion (deeper
> inspection artifacts are listed at the end of Section 1).
>
> Please read critically and adversarially — we are seeking disagreement, not confirmation.
> As you read, note that statements are labelled **[FACT]** (observed), **[INTERPRETATION]**
> (our reading), **[RISK]**, **[RECOMMENDATION]/[REC]**, or **[OPEN]** (undecided). Treat
> `[INTERPRETATION]` and `[REC]` as claims to challenge, not established truths.
>
> **What we most want you to answer:**
> 1. Is retiring (not deleting or label-flipping) **case042** the correct primitive?
> 2. How should **case054** be adjudicated — and should a specific evidence-gap label
>    (`mechanism_vs_evidence`) outrank the generic `overclaim` label when both apply?
> 3. Where are we overfitting to a single strong model, and what would you prioritize next?
>
> The full 15-question list is in Section 2. A short written verdict plus prioritized
> recommendations would be the ideal output.
>
> **Key caveat we are NOT hiding:** the "96% accuracy" figure is a *single strong model
> ceiling/stability* result, not a demonstration of benchmark validity or discrimination power.

**Document set / tag:** v0.7.7-retire-case042 (commit `19aa295`)
**Sections below:** (1) Audit Brief · (2) Audit Questions · (3) Benchmark Integrity Risks ·
(4) Current State Snapshot · (5) Open Decisions & Next Steps

---

# Section 1 — Fable 5 Audit Brief

*A compact briefing for an external benchmark-integrity auditor. Written neutrally; it does not
claim benchmark validity from a single-model run. Facts, interpretations, and open questions are
labelled.*

## What Agent Arena is [FACT]
A local-first evaluation engine for **claim-forensics**: given a short text making a scientific or
commercial claim, an agent must classify the epistemic failure mode and support it with evidence.
The primary task family is `study_forensics`. Each case has a curator gold label, a justification,
a documented alternative reading, expected findings, and evidence spans. The engine scores an
agent's structured response across diagnostic dimensions; an optional LLM judge is a separate path.

## Current repo state [FACT]
- Tag: **v0.7.7-retire-case042** (commit `19aa295`).
- Library: **49 active cases + 1 retired** (case042). 50 case files on disk.
- Tests: **988 passed**. No live model run after v0.7.7.
- Taxonomy: 4 gold labels — `solid`, `overclaim`, `mechanism_vs_evidence`,
  `correlation_vs_causation` (single label per case).

## What has been built [FACT]
- Hardened structured-output parser (shared by agent + judge) that never crashes on malformed/
  truncated/fenced JSON.
- Normalized provider contract (`ModelResponse`: finish_reason, usage, latency, error_type).
- Curated case library expanded 29 → 50 (mostly synthetic fixtures, no fabricated citations).
- A multi-run stability harness (`run_library`) with a deterministic offline fake provider.
- A real **case-retirement mechanism**: retired cases are excluded from default active discovery
  but kept and reachable for audit.
- A Phase-5A single-model diagnostic bundle and an intake policy (`docs/case_intake_policy.md`).

## What was validated [FACT]
- Engine behavior: 988 unit/integration tests (fixtures/fakes; no live keys).
- One live single-model baseline (Opus 4.5, 50×3 = 150 runs): 150/150 successful, 0 parse/
  truncation/provider errors, **96% accuracy**, 0 unstable cases.
- [INTERPRETATION] This establishes internal consistency and a **single strong model ceiling** — it
  does **not** establish discrimination power or benchmark validity.

## Problems found (and how handled) [FACT]
- **case040** (uncontrolled pre/post vocational-training claim): mislabeled generic overclaim →
  **flipped to correlation_vs_causation** on taxonomy grounds (the specific causal-inference gap);
  overclaim kept as alternative.
- **case041** (GLP-1 / aleniglipron weight-loss pill, showcase-derived): audited for demo-origin
  contamination; **kept active Core** because the claim is isolated and the source voice
  (company/analysts, promotional) is unambiguous; annotated `curated_showcase` / intake passed;
  prompt unchanged.
- **case042** (Edge-AI readiness, showcase-derived): **retired from active metrics** because the
  target claim is embedded in an analytical paper that critiques it (ambiguous source voice,
  non-isolated claim) — a task-design confound. Not deleted, not label-flipped.
- Four synthetic mechanism fixtures (043/044/045/048) had been written with selling language and
  were relabeled/reworded so the mechanism-vs-overclaim boundary is clean.

## What remains unresolved — case054 [OPEN]
Current gold `overclaim`; a strong model stably reads `mechanism_vs_evidence`. Both are defensible:
decorative-hedge equivalence selling (overclaim) vs an in-vitro→clinical tier gap (mechanism). This
is a **taxonomy-precedence** question, not a clear error. We have deliberately **not** auto-flipped
it. A general rule (specific evidence-gap label vs generic overclaim) is undecided.

## Current risks [INTERPRETATION]
1. Single-model ceiling (no discrimination measurement yet).
2. Co-evolution risk if gold labels track one model (mitigated by taxonomy-first rule; no holdout
   set yet).
3. Single-label taxonomy can't represent dual failure modes; no precedence rule.
4. Latent demo-origin/task-design issues may exist in un-audited active cases.
5. Confidence is uncalibrated self-report.
6. Analysis generators are out-of-repo (reproducibility gap).

## Concrete questions for Fable 5
See Section 2 (15 questions). The three we most want challenged:
- Is retiring (not deleting/flipping) case042 the right call?
- How should case054 be adjudicated, and should specific labels outrank generic overclaim?
- Where are we overfitting to one strong model, and what would you prioritize next?

## Reviewer package [FACT]
`analysis/phase4_9_retrospective/` (this dossier) + `analysis/phase5a/...` (historical metrics) +
`docs/case_intake_policy.md` + the four cited case YAMLs + `run_library.py`/`schemas.py`.

---

# Section 2 — Audit Questions for Fable 5

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

---

# Section 3 — Benchmark Integrity Risks (as of v0.7.7)

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

---

# Section 4 — Current State Snapshot (v0.7.7-retire-case042)

## Repo/tag state [FACT]
- Current tag: **v0.7.7-retire-case042** (commit `19aa295`).
- Full tag chain intact from `v0.6-agent-arena-baseline` (3327605) to `v0.7.7` (19aa295).
- Working tree clean except 21 known untracked cruft entries.
- Tests: **988 passed** (`pytest -q`).

## Active vs retired library [FACT]
- Case **files** on disk: 50.
- **Active cases (default discovery): 49.**
- **Retired cases: 1 — case042** (`study-forensics-042`).
- case042: not hard-deleted, not label-flipped, prompt byte-identical; excluded from default
  active discovery; reachable via `--include-retired` or explicit `--case-id`.

## Historical metrics — Phase 5A at v0.7.6 [FACT]
Single-model run `lib_20260704_134553_55aa66` (Opus 4.5, 50×3). **These are historical and were
computed over all 50 cases including case042, before retirement. They should NOT be silently
recalculated; regenerate against the active set for any forward-looking metric.**

- 50 cases, 150 total runs, **150/150 successful**
- 0 parse failures, 0 truncations, 0 provider errors
- Per-run accuracy: **144/150 = 96.0%**
- Case-majority accuracy: **48/50 = 96.0%**
- All 50 cases label-consistent (0 unstable)
- Stable-correct: **48**
- Stable-alternative: **2 — case042 and case054**
- High-score-variance cases: **0**
- `solid_as_problem_rate` (gold solid, predicted non-solid): **0/42 = 0%**
- `problem_as_solid_rate` (gold non-solid, predicted solid): **3/108 = 2.78%**, entirely case042
- Per-label accuracy: solid 100%, correlation_vs_causation 100%, mechanism_vs_evidence 100%,
  overclaim 66/72 = 92% (the 6 misses = case042 ×3 + case054 ×3)

## Current active state — v0.7.7 [FACT]
- 49 active cases; 1 retired historical case (case042).
- **No live rerun has been performed after v0.7.7.** Any "active-set accuracy" number therefore
  does not yet exist as a measured value; it would require a new run over the 49 active cases.
- [INTERPRETATION] If the historical Phase-5A run were simply filtered to the 49 active cases,
  case042's 3 misses drop out, leaving case054 as the only stable-alternative miss. That is an
  *arithmetic projection*, not a fresh measurement, and is not recorded as an official metric.

## Interpretation of the 96% [INTERPRETATION]
96% is a **single strong model ceiling** figure, not a benchmark-validity figure. It shows the
library is internally consistent and that one strong model finds ~all cases unambiguous. It does
**not** demonstrate discrimination power (ability to separate strong from weak models). See
Section 3.

## Facts vs interpretations [FACT]
- Fact: 988 tests pass; 49 active / 1 retired; case042 retired without deletion or label flip.
- Fact: Phase-5A historical metrics as listed above.
- Interpretation: the library is "clean and stable for one model," not "validated."
- Open: case054 adjudication; taxonomy precedence rule.

---

# Section 5 — Open Decisions & Next Steps (prioritized)

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

*End of combined Fable 5 audit input. Compiled offline from the Phase 4.9 dossier at tag
v0.7.7-retire-case042; source documents are unchanged.*
