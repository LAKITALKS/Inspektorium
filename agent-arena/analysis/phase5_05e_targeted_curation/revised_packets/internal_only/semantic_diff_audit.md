# Phase 5.05e — Semantic Diff & Contamination Audit

Scope: the two revised annotator-facing packets (`BIAA-013_v2.md`, `BIAA-016_v2.md`) vs
their originals. BIAA-003/007 have no revised packet (internal rationale/designation only);
BIAA-019 has no revised packet (retirement recommended).

## Per-case semantic verification

### BIAA-013 (gold `correlation_vs_causation` — unchanged)
| dimension | original | v2 | verdict |
|---|---|---|---|
| public claim | study findings + media causal framing | identical | unchanged |
| evidence | study design/findings/limitations/funding + 3 headlines + 2 quotes | all present verbatim | unchanged |
| section structure | Task / Case material / **Study** / **Media Coverage** / Your annotation (5 `##`) | Task / Case material / Your annotation (3 `##`); Study & Media as inline **bold** | normalized |
| embedded instruction | "Analyze… Identify any overclaims… correlation-as-causation issues" (names all 4 labels) | **removed** | approved change |
| taxonomy terms visible to annotator | 4 label terms in the instruction line | none (only the paper's own "cannot prove causation" caveat remains — legitimate evidence) | improved |
| case-material words | 390 | 368 (only the instruction line removed; no evidence shortened) | acceptable |
| gold label | correlation_vs_causation | correlation_vs_causation | unchanged |
| approved action implemented | — | remove instruction + normalize structure | yes |
| unapproved change | — | none | none |

### BIAA-016 (gold `overclaim` — unchanged)
| dimension | original | v2 | verdict |
|---|---|---|---|
| public claim | company: app can "revolutionize mental health care and replace clinical therapies" | identical, quoted verbatim | unchanged |
| evidence | app + 15-student 2-week pilot + 30% self-reported stress decline + university caveats | all present verbatim | unchanged |
| claim isolation | company claim and university critique interleaved in one block | evidence context and the single evaluated claim explicitly separated; caveats flagged as context | isolated |
| source voice | company (implicit) | company (explicit) | clarified |
| section structure | Task / Case material / Your annotation | identical | unchanged |
| paraphrase strength | — | claim quoted verbatim; not strengthened or weakened; no evidence added/removed | preserved |
| gold label | overclaim | overclaim | unchanged |
| approved action implemented | — | isolate claim + borderline marking (YAML) | yes |
| unapproved change | — | none | none |

## Contamination scan (revised annotator-facing material)
Scanned `README_FOR_REVALIDATION.md`, `BIAA-013_v2.md`, `BIAA-016_v2.md` for: gold_label,
gold justification, real_case_id, blind_case_index, internal_only, curator decision,
majority vote, agreement result, kappa, Opus, Gemini, GLM, Anthropic, Rater 1–4, expected
label, correct answer, real case IDs (case009/037/043/public), real names (e.g. John
Gabrieli).

**Result: NONE — clean.** (An earlier draft README used the tokens "internal_only" and
"curator decision" as ordinary process references; these were reworded so the annotator-
facing material carries no such tokens.)

### Harmless ordinary-language occurrences (NOT leakage)
- BIAA-013_v2 retains the paper's own stated limitation "Observational design — cannot
  prove **causation**." This is legitimate evidence text quoted from the source, not a
  taxonomy cue; it was preserved deliberately.

## Structural consistency
- Both v2 packets now use the standard 3-heading structure (Task / Case material / Your
  annotation), matching the 19 well-formed original packets.
- Packet lengths were **not** forced equal: 013_v2 remains long (368 words) because its
  evidence is genuinely long; only the non-evidence instruction was removed.
- Embedded instructions: none remain in either v2 packet.
- Taxonomy-term occurrences visible to annotators: none introduced; the 013 instruction
  line that named all four labels was removed.

## Conclusion
Both revised packets implement exactly the approved actions, preserve claim, evidence,
evidence tier, and gold label, introduce no unapproved change, and pass the contamination
scan clean.
