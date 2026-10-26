# Phase 6.3 — Reader-Impact Risk Vocabulary (frozen)

Reader-impact risk answers one question: **how badly could a non-specialist reader be
misled by this claim, and how consequential is acting on that misunderstanding?** It is
a qualitative editorial category. It is **not** a computed medical, legal, or financial
harm probability, and the report says so on every rendering
(`not_a_harm_probability_note`).

## Frozen levels

| level | meaning | illustrative (synthetic) |
|---|---|---|
| `low` | Misreading is unlikely or low-consequence; claim is appropriately scoped. | A well-hedged, modest human-outcome claim. |
| `moderate` | A plausible misreading could influence a non-critical decision. | A causal lifestyle claim from an observational association. |
| `high` | A likely misreading could drive a consequential health/operational/financial decision. | Preclinical result framed as human prevention; "beats all doctors, replace staff now". |
| `critical` | A misreading could lead to serious, hard-to-reverse harm (e.g. abandoning necessary treatment). | "Skip your medication; this cures stage-4 cancer." |
| `unknown` | Insufficient information to assign a level. **Explicit** — never silently `low`. | Reader-impact not supplied by the analysis. |

## Rules

- The four graded levels (`low · moderate · high · critical`) are the only rankable
  values. `unknown` is an explicit insufficient-evidence state, not a rank.
- When the analysis supplies no `risk_level`, the report records `unknown` **and** emits
  a warning; it does not guess.
- The level is **not** derived from confidence, the label, or any numeric formula — it is
  an editorial judgement supplied by the analysis and echoed with its rationale. The
  prototype computes no harm probability and applies no threshold.
- `risk_rationale`, `likely_reader_misunderstanding`, `affected_decision_type`, and
  `risk_uncertainty` accompany the level where supplied; absent ones render as
  `_not supplied_`.

## Why not reuse `FailureSeverity`?

The engine's `FailureSeverity` (`critical · major · moderate · minor · stylistic`)
grades an **internal evaluation finding's** severity. Reader-impact risk grades
**external reader consequence** and follows the Phase 6.3 brief's
`low · moderate · high · critical` scale. Keeping them distinct avoids conflating "how
severe is the analytical flaw" with "how badly could a reader be harmed by the claim".
