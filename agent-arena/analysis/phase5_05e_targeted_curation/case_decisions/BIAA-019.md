# BIAA-019 — Case Decision (source-voice resolution)

**Approved actions:** clarify source voice · determine whether revision is sufficient or
retirement is required · exclude from holdout until resolved.

## Who makes the evaluated claim? (attribution from source material only)
The material is written in an **editorial-narrator / reporting voice** and contains several
distinct, separately attributed statements:
- a preclinical fact (mouse mTOR lifespan extension, replicated) — attributed to research;
- an **implicit claim** that rapamycin slows human aging — attributed to "**enthusiasts**"
  who take it off-label;
- a human-trial result (safe; failed its primary abdominal-fat endpoint; modest lean-muscle
  gain) — attributed to "the first well-designed human trial";
- a caution that no clinical evidence shows rapamycin slows aging in people — attributed to
  "**experts**."

There is **no single claim-maker** for one evaluated claim. The gold label (`solid`) is the
result of judging the **overall balanced reporting**, which honestly scopes the evidence.

## Why unambiguous single-claim attribution is not available
The current gold (`solid`) was historically **relabeled from `mechanism_vs_evidence`**
(per the source YAML curator_notes) precisely because the honest, whole-report framing —
not the enthusiasts' implicit claim — is what should be evaluated. Isolating a single
claim therefore risks re-pointing the evaluated object:
- isolate the enthusiasts' implicit anti-aging claim ⇒ pushes toward
  `mechanism_vs_evidence` / `overclaim` (the historically rejected reading);
- isolate the reporting's overall summary ⇒ `solid`.
Any explicit single-claim framing added now would itself resolve the ambiguity in a
direction, biasing a blind revalidation. Making the voice "explicit" cannot be done without
choosing which claim is under evaluation — i.e., without adding framing not present as a
single attribution in the source.

## Proposed disposition: **B — RETIREMENT RECOMMENDED**
- Source voice remains **materially ambiguous** for a single evaluated claim.
- Do **not** manufacture a clarified packet (no `BIAA-019_v2.md` created).
- Recommend retirement from the blind case pool **subject to curator approval** — not
  executed here.
- **Curator alternative** (for the curator to weigh, not chosen here): retain the case as an
  explicit *whole-reporting `solid` exemplar* with a scope note stating that the reporting's
  overall characterization is the evaluated object. This would be a curator framing
  decision, not a mechanical revision.

**Not changed:** gold_label (`solid`), evidence, taxonomy, original packet.

## Curator decision and execution (Phase 5.05e finalization, v0.8.6)
- **Proposed:** retirement (this document, above).
- **Approved:** retirement (curator_approval.md, 2026-08-01).
- **Executed:** retirement applied to the authoritative case `case031_rapamycin_longevity.yaml`
  using the existing repository convention (`status: retired` +
  `excluded_from_active_metrics: true`), following the case042 precedent. Retirement
  reason recorded in the case `curator_notes`. Library counts moved from 49 active / 1
  retired to **48 active / 2 retired** (total 50 — not deleted).
- **Retirement is not deletion:** the case file, gold label (`solid`), public claim,
  evidence, prior rationale, and the original blind packet are all preserved unchanged;
  the case remains loadable with `--include-retired`.
- **Holdout eligibility:** ineligible (retired). **Targeted revalidation required:** no.

