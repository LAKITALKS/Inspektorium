# Phase 5.1 — Eligibility Summary (aggregate; no case identities)

| metric | count |
|--------|-------|
| total known cases | 50 |
| active cases | 48 |
| retired cases | 2 |
| development-only cases | 1 |
| holdout-ineligible cases (retired ∪ development-only) | 3 |
| unresolved-review cases | 0 |

## Eligible counts by gold label (cases with a latest approved annotator-facing packet, active, not dev-only/retired)
| label | eligible | deduplicated eligible |
|-------|----------|-----------------------|
| solid | 5 | 5 |
| overclaim | 8 | 8 |
| correlation_vs_causation | 4 | 4 |
| mechanism_vs_evidence | 4 | 4 |

## Exclusion counts by reason (aggregate)
| reason | count |
|--------|-------|
| no_approved_annotator_facing_packet (cond 5; claim-isolation/source-voice/leakage unverified) | 26 |
| retired | 2 |
| development_only | 1 |

*(26 active non-blind cases lack an approved anonymized annotator-facing packet; they were never
curated for claim isolation / source voice / leakage and are therefore not certifiably eligible.)*
All four labels meet the required minimum of 4 eligible cases.
