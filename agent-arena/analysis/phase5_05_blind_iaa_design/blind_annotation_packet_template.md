# Blind Annotation Packet — Template

*One packet per case. The curator fills the `[[ ... ]]` slots from the case YAML,
**omitting every label-bearing field**. The annotator sees only what is below.
Do not include gold_label, expected_answer, task_family, gold_justification,
gold_alternative_reading, gold_case_type, gold_confidence, curator_notes,
trap_type, diagnostic_focus, model outputs, scores, or the real filename.*

---

## Packet `[[ANON_ID e.g. IAA-01]]`

> Anonymized ID only. The mapping ANON_ID → real case_id is kept in a **separate
> curator-only key file** that the annotator never sees.

### 1. Claim under evaluation
[[Verbatim claim / prompt text — the single isolated claim to be judged.]]

### 2. Evidence / source description
[[The context, study design, and data type as stated in the case — e.g. "pre/post
comparison, no control group", "in-vitro dissolution curves only", "RCT with
pre-registered endpoints". Include only what is needed to judge the claim.]]

### 3. Who is making the claim
[[The claim-maker / source voice as presented — e.g. "the study authors", "a
company brochure", "a program director". Needed for the source-voice question.]]

### 4. Taxonomy reference
See `blind_annotator_instructions.md` for full definitions and the precedence rule.
Labels: `solid`, `overclaim`, `correlation_vs_causation`, `mechanism_vs_evidence`.

---

### Annotation form (annotator completes)

| Field | Your answer |
|---|---|
| `primary_label` | [[ solid / overclaim / correlation_vs_causation / mechanism_vs_evidence ]] |
| `secondary_label` (optional) | [[ one label or "none" ]] |
| `confidence` | [[ low / medium / high ]] |
| `rationale` (1–3 sentences) | [[ ground the label in claim/evidence structure ]] |
| `ambiguity_notes` | [[ what made it hard / debatable, if anything ]] |
| `source_voice_clear` | [[ yes / no ]] |
| `claim_isolated` | [[ yes / no ]] |
| `evidence_matches_claim_strength` | [[ yes / no / partial ]] |

---

**Explicitly NOT in this packet (by design):** gold label, expected answer, model
prediction, Phase-5A result, prior adjudication, score, confidence-of-gold,
case-type, or any curator note. Their absence is intentional — do not request them.
