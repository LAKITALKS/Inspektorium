# Case Review — RVAL-001 (internal target BIAA-013_v2)

**Existing gold label:** `correlation_vs_causation` · **packet_version:** 2 · **provisional status:** **CURATOR_REVIEW_REQUIRED**

## Frozen acceptance criteria (5.05f/1.0)
1. ≥2/3 assign gold as primary · 2. no majority assigns a different primary · 3. ≥2/3 mark source_voice_clear/claim_isolated/evidence_context_understandable = yes · 4. no majority material_packet_defect = yes · 5. no individual material-defect report remains unresolved after curator inspection · 6. no serious disagreement reveals a new taxonomy-boundary problem · 7. remaining disagreements documented & curator-reviewed.

## All three responses
| field | X (Opus 5) | Y (GLM 5.2) | Z (Gemini 3.5 Flash, Extra Thinking) |
|---|---|---|---|
| primary_label | correlation_vs_causation | correlation_vs_causation | correlation_vs_causation |
| secondary_label | overclaim | overclaim | overclaim |
| confidence | 0.6 | 0.9 | 0.9 |
| source_voice_clear | **uncertain** | yes | yes |
| claim_isolated | **no** | yes | yes |
| evidence_context_understandable | yes | yes | yes |
| multiple_competing_claims_present | **yes** | no | no |
| material_packet_defect | **uncertain** | no | no |
| recommended_human_review | **yes** | no | no |
| ambiguity_notes | target-selection ambiguity (study reporting honest/hedged; headlines + lead-author quote causal) | headlines hedge (could/may) vs author quotes causal; overall causal framing clear | none |
| freeform_notes | (see material-defect note) | none | none |

**X material_packet_defect note (verbatim):** "The packet does not designate which single statement is the claim under evaluation. It supplies at least five candidate claims (three media headlines, the lead author's quote, a co-author's quote) alongside the study's own honestly hedged reporting including explicit \"cannot prove causation\" limitations. The label is reading-dependent: judging the paper itself yields solid, judging the headlines or the lead author's quote yields correlation_vs_causation. RVAL-002 contains an explicit isolation instruction while RVAL-001 does not, so the omission looks structural rather than intentional. Labelled uncertain rather than yes because the framing \"claim together with the evidence available for it\" plus the inclusion of a media-coverage section makes the disseminated claims the plausible intended target."

## Vote counts
- Primary: correlation_vs_causation ×3 → **gold-primary 3/3, unanimous**. No alternate majority.
- Clarity yes-counts: source_voice 2/3 · claim_isolated 2/3 · evidence_context 3/3.
- material_packet_defect: yes 0 · uncertain 1 · no 2. recommended_human_review: yes 1 / no 2.
- Disagreement (label): soft 0, serious 0 (all primaries equal gold).

## Criterion-by-criterion
| # | criterion | result |
|---|-----------|--------|
| 1 | ≥2/3 gold primary | **PASS** (3/3) |
| 2 | no alternate majority | **PASS** |
| 3 | ≥2/3 clarity (each field) | **PASS** (2/2/3) |
| 4 | no material-defect majority | **PASS** (0 yes) |
| 5 | no unresolved individual material-defect report | **NEEDS CURATOR** (X = uncertain, claim_isolated = no) |
| 6 | no serious taxonomy-boundary disagreement | PASS on label; the flag is packet-quality, not a taxonomy split |
| 7 | remaining disagreements documented | done (this review) |

## Provisional status & unresolved curator question
**CURATOR_REVIEW_REQUIRED.** Numerical criteria 1–4 pass and all three revalidators reproduce the gold
label, but one revalidator's `uncertain` material-defect + `no` claim-isolation report is unresolved
(criterion 5) and must not be treated as `no`.

**Unresolved curator question:** Should BIAA-013_v2 receive the same explicit "Claim to evaluate"
isolation instruction that BIAA-016_v2 received (the target is currently reading-dependent), and then be
re-revalidated, before any holdout eligibility? This is a packet-remediation-quality decision, not a
taxonomy disagreement. **No label is changed and no holdout action is taken here.**
