# Phase 5.05g — Semantic Diff BIAA-013_v2 → v3

| dimension | v2 | v3 | change class |
|---|---|---|---|
| identifier / version | BIAA-013, `packet_version: 2` | BIAA-013, `packet_version: 3` | identifier/version change |
| evaluated claim | **not designated** — study finding, 3 headlines, and 2 author quotes presented together under one "Case material" block | **exactly one**: the lead author's verbatim quotation, under an explicit `## Evaluated Claim` section | claim-isolation change |
| speaker / source attribution | lead author quote embedded as "Key quote from media coverage — Lead author [Author B] stated: …" | stated neutrally: "a statement attributed to the study's lead author ([Author B])" | source-attribution clarification |
| study finding | inside the combined Case material block | moved verbatim to `## Evidence Context`, labelled as context, "not itself the claim" | structural repositioning |
| evidence context (design/findings/limitations/funding) | present, verbatim | present, verbatim, under `## Evidence Context` | structural repositioning (no wording change) |
| additional headlines & co-author quote | inside the combined block | moved verbatim to `## Additional Context`, explicitly "not the claim under evaluation" | structural repositioning |
| section structure | Task / Case material / Your annotation | Task / **Evaluated Claim** / **Evidence Context** / **Additional Context** / Your annotation | structural repositioning |
| caveats | "Observational design — cannot prove causation" etc. | identical, preserved | none |
| evidence tier | observational cohort (accelerometer + questionnaire, ~7y) | identical | none |
| current gold label | correlation_vs_causation | correlation_vs_causation | no change |
| alternative reading | overclaim (secondary) | overclaim (secondary) | no change |

## Verified deterministically
- The evaluated claim is **byte-identical** in v2 and v3 (verbatim quotation; no paraphrase).
- Every evidence snippet (study title, design, key findings, all four stated limitations,
  funding, all three headlines, the co-author quote) is **present verbatim** in v3.
- **No evidence was added or removed.**
- The `## Evaluated Claim` section contains **exactly one** quoted statement.

## Result
- One explicit claim isolated ✔ · source voice clarified ✔ · surrounding material repositioned ✔
- No evidence added/removed ✔ · no gold-label change ✔ · no taxonomy change ✔
- **No material semantic change beyond specifying the evaluated object.** Packet approved for
  the audit trail (not yet revalidated).
