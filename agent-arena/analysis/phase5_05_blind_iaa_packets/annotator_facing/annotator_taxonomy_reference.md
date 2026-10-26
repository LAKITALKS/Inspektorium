# Annotation Taxonomy Reference

*The label definitions and the precedence rule for this task. This is the only file
that names the labels — supply the label from here. Judge claim/evidence structure
only; never guess an "intended" answer.*

## The four labels

### `solid`
The claim is appropriately scoped for its evidence. Limitations may exist but are
honestly acknowledged; the reporting does not overstate. Weak evidence honestly
reported as weak is still `solid`.

### `overclaim` (generic / residual)
The conclusion exceeds the evidence — rhetorical inflation. The *framing* is the
problem. Includes: conclusions beyond the data; surrogate endpoints / biomarkers
framed as clinical outcomes; extrapolation to populations not studied; decorative
hedging (a qualifier that does not actually constrain the implied claim).

### `correlation_vs_causation` (specific)
**Trigger:** a causal claim drawn from a non-causal / uncontrolled / confounded
design — e.g. an uncontrolled before/after comparison, a cross-sectional or
observational association, or observational data used for a causal or policy
recommendation, with confounders unaddressed and no counterfactual / comparison arm.

### `mechanism_vs_evidence` (specific)
**Trigger:** a *described biological mechanism* (an animal or preclinical pathway)
is used to imply a human clinical benefit that has not been demonstrated. There must
be an actual mechanism narrative leaping to a human therapeutic claim.
**Not this label:** a bare surrogate/biomarker-to-clinical gap with no mechanism
narrative → that is `overclaim`.

## Precedence rule (choosing among applicable labels)
1. A specific label (`correlation_vs_causation`, `mechanism_vs_evidence`) takes
   precedence over generic `overclaim` **only if its trigger is genuinely present
   AND it captures the core error**.
2. If the specific trigger is absent, or fits only by stretching its definition,
   choose `overclaim` as primary and record the specific label as `secondary_label`.
3. If a genuine specific failure and rhetorical inflation are both present, make the
   one that captures the *core* error primary and record the other as secondary.

Do **not** stretch a specific label to fit. No described mechanism ⇒ do not use
`mechanism_vs_evidence`, however "biological" the topic sounds.

## Filling the fields
- `primary_label` — one of the four above.
- `secondary_label` — a second genuinely co-present failure mode, or "none".
- `confidence` — 0–1, your own judgement.
- `rationale` — 1–3 sentences grounding the label in claim vs evidence.
- `ambiguity_notes` — what made it hard/debatable, if anything.
- `source_voice_clear` — yes/no/uncertain: is the claim-maker unambiguous?
- `claim_isolated` — yes/no/uncertain: is the claim to judge isolated, not buried in
  surrounding analysis that already critiques it?
- `evidence_matches_claim_strength` — yes/no/uncertain.
- `missing_evidence_notes` — what evidence would be needed to justify the claim.
- `recommended_human_review` — yes/no.
- `freeform_notes` — anything else.

## Golden rule
Judge the claim/evidence structure only. Your independent reading is the
measurement — do not reverse-engineer what the task "wants".
