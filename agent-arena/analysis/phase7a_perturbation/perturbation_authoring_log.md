# Phase 7A — Perturbation Authoring Log (7A.2, WP-3)

Compact record of the meaning-preservation discipline applied while authoring the 50 variants and the
material transformation drafts **rejected** because they would have changed the proper gold (§13/§16).
Not a wording-draft archive — only material rejections and the standing rules that produced them.
**Repo agent (Claude Opus) authored all transformations; 0 model/evaluation calls; no external
semantic-judge model (§20).**

## Standing rules applied to every family (from §12–§13, §16, §23)

- **P1 (paraphrase):** reword the claim only; reuse the evidence paragraph verbatim. Every decisive
  term (population, comparator, endpoint, magnitude, causal/mechanistic/clinical-benefit force,
  certainty, temporal scope, superiority, evidence tier) must survive the rewording unchanged.
- **P2 (hedging, neutral):** use **attributional / discourse** framing only ("as the campaign puts
  it", "reporting the result as it stands"). Epistemic softeners that weaken the claim ("may", "might",
  "preliminary") are **forbidden** — for an overclaim/causal/mechanism base they would *repair the
  defect* and flip the gold (§13). For the two `solid` bases the hedge must likewise not downgrade
  certainty.
- **P3 (order):** pure paragraph-order swap (evidence before claim); **no** word added/removed, so
  content is provably identical.
- **P4 (distractor):** append exactly one irrelevant sentence about packaging/format/logistics/media
  reach; it must **not** add evidence, a comparator, an endpoint, or bear on the forensic judgment
  (§23).
- **P5 (formatting):** re-render the same content as a labelled/bulleted layout; every claim and
  evidence item preserved, format only.

## Material rejections (representative, by failure mode)

| base / family | rejected draft (paraphrase) | material reason rejected | fix used |
|---|---|---|---|
| P7A-NEU-002 (Sensa) / P2 | "…marketers *claim* it *may* help you lose weight" | **hedge changed claim strength** — "may help" softens a proven-efficacy overclaim into a tentative claim, repairing the defect (would move gold overclaim→solid-ish) | attributional frame only ("with an upbeat sales pitch"); "clinically studied / average 30 lb" force intact |
| P7A-ADV-001 (Airborne) / P2 | "…the ad *loosely suggests* Airborne *might* help prevent colds" | **removed wording responsible for the defect** — dropping "clinically proven" guts the decorative-citation overclaim | keep "clinically proven … double-blind, placebo-controlled study"; add only "in the brand's own confident words" |
| P7A-NEU-003 (coffee) / P1 | "coffee *is associated with* higher cancer rates" | **causal→associational** — changing "causes/raises risk" to "is associated with" removes the correlation-as-cause error (gold correlation_vs_causation would no longer hold) | keep the explicit causal verb ("must raise your cancer risk"); only rephrase the association wording |
| P7A-ADV-011 (Nexium) / P1 | "Nexium heals reflux; some patients prefer it" | **superiority removed** — dropping "better than Prilosec" deletes the A6 unsupported-superiority structure | keep the explicit comparator superiority ("does a better job than Prilosec") |
| P7A-BND-017 (Delhi) / P1 | "Delhi's air *may be roughly comparable to* heavy smoking" | **magnitude/literal-equivalence softened** — hedged comparison removes the literal per-day "44 cigarettes" overreach | keep "the equivalent of smoking 44 cigarettes … literally" |
| P7A-ADV-010 (soap) / P4 | distractor: "independent labs confirmed it cuts flu transmission" | **added new evidence + fixed the surrogate→clinical gap** — a distractor may not add evidence bearing on the claim (§23) | neutral distractor about scent/pump bottle only |
| P7A-BND-011 (Shingrix) / P2 | "…the summary *optimistically* reports a 97.2% reduction" | **certainty/faithfulness change** — "optimistically" imputes inflation to a faithful `solid` report, nudging toward overclaim | neutral attributional frame ("reporting the trial result as it stands") |
| P7A-BND-009 (senolytics) / P1 | "senolytics *have been shown in people* to reverse aging" | **evidence tier / species change** — asserting human proof removes the mouse→human gap that makes it mechanism_vs_evidence | keep the mouse-evidence framing; reword the marketing claim only |

Every retained variant was re-checked against §12 (no change to population, comparator, endpoint,
magnitude, causal/mechanistic/clinical-benefit force, certainty, temporal scope, superiority, evidence
tier, scientific meaning) and the §22 counterfactual test (a competent forensic reviewer has **no**
scientific reason to change the base gold). All 50 retained variants pass; none introduce a new
scientific proposition. See `perturbation_curator_review.md` Part D/§K for the per-variant surface and
the (empty) FAIL list.
