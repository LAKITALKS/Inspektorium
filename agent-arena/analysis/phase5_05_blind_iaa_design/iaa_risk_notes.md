# IAA Risk Notes

*Threats to the validity of the blind-IAA result. IAA is a **credibility gate**,
not final proof of benchmark validity.*

## 1. Original curator has seen model outputs
- [RISK] Label A (gold) was set by a curator who has seen Phase-5A model behavior
  and adjudications. So A is not itself blind; IAA measures B-vs-A, not two blind
  labelers.
- [MITIGATION] Frame the result honestly as "reproducibility of gold by an
  independent annotator," not "two-way blind agreement." A fully-blind two-annotator
  round is a possible follow-up.

## 2. Annotator may infer the intended label from synthetic style
- [RISK] The library is mostly synthetic fixtures with recognizable patterns; a
  sharp annotator may guess the "designed" answer from phrasing, not structure.
- [MITIGATION] Anonymized IDs, stripped metadata, explicit instruction to ignore
  style and judge structure only. Consider light paraphrase of prompts in a future
  round (not done here — no prompt edits this phase).

## 3. Single-label taxonomy limitation
- [RISK] Cases with two genuine failure modes force an artificial single primary;
  disagreement may reflect the schema, not a real labeling error.
- [MITIGATION] The form captures a `secondary_label` and partial-agreement is
  scored (`adjudication_and_kappa_plan.md`), separating "ranking difference" from
  "different reading." Motivates Schema v2 consideration.

## 4. Class imbalance
- [RISK] Sample label mix is overclaim 9 / solid 6 / correlation 3 / mechanism 2.
  Thin specific classes make per-label agreement noisy and inflate the influence of
  the overclaim class on κ marginals.
- [MITIGATION] Report per-label agreement with explicit small-N caveats; do not
  headline a single κ without the per-label breakdown.

## 5. Sample too small for definitive validity
- [RISK] N=20 yields a wide κ confidence interval; it can flag a problem but cannot
  certify the full 49-case library.
- [MITIGATION] Treat κ as directional. Report a bootstrap CI. A weak result triggers
  action; a strong result licenses the *next* step, not a validity claim.

## 6. IAA is a credibility gate, not proof
- [RISK] Even strong human agreement does not establish discrimination power (that
  needs the Phase 5.1 model panel) or real-world generality.
- [MITIGATION] Keep the phase ladder explicit: IAA → holdout freeze → panel →
  (later) real-world intake. No public/customer claims off IAA alone.

## 7. Paraphrase robustness still needed later
- [RISK] Agreement on the exact fixture text does not prove the label is robust to
  rewording; models/annotators may key on surface cues.
- [MITIGATION] Plan a later paraphrase-robustness check (separate phase; requires
  controlled prompt variants, which are **not** created here).

## 8. Annotator selection / expertise
- [RISK] A single second annotator's domain expertise skews results either way;
  under-expertise inflates disagreement, shared training inflates agreement.
- [MITIGATION] Record annotator background; prefer someone not involved in curation.
  Consider ≥2 annotators in a later round for a true multi-rater κ.
