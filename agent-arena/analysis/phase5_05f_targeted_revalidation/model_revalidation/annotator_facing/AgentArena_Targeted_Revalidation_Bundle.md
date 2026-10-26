---
SOURCE FILE: README_FOR_REVALIDATOR.md
---
# Read Me — Independent Revalidator

You are an **independent revalidator** for a claim-forensics taxonomy task. Evaluate
**exactly two packets** (`RVAL-001` and `RVAL-002`) and record your answers on your assigned
response sheet.

## How to work
- Apply **only** the supplied four-label taxonomy in `annotator_taxonomy_reference.md`.
- Make an **independent** judgment from the packet content and the taxonomy alone.
- **Do not use the web.**
- **Do not** try to identify the original source, study, product, or case.
- **Do not** search for or reuse any previous Agent Arena material.
- **Do not** consult another model, and do not reuse or look for any earlier answers.
- **Complete every field** on your response sheet, using **only the permitted values**.
- **Preserve the `RVAL-###` identifiers** exactly; one row per packet.
- **Do not alter the packet text.**
- Return a **valid CSV** file matching the provided header.
- **Do not** provide benchmark scores, comparisons, or an overall verdict.

## What to record per packet
- `primary_label` (one of the four taxonomy labels), optional `secondary_label`
  (a different label or `none`), `confidence` (0–1), and a short `rationale`.
- Packet-quality fields: `source_voice_clear`, `claim_isolated`,
  `evidence_context_understandable`, `multiple_competing_claims_present`,
  `material_packet_defect` (+ notes if yes), `recommended_human_review`, `ambiguity_notes`,
  and any `freeform_notes`.

Your independent reading is the measurement. There is no answer key to request, and no
"expected" label. Judge only the claim/evidence structure in front of you.
---
SOURCE FILE: annotator_taxonomy_reference.md
---
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
---
SOURCE FILE: RVAL-001.md
---
# Blind Annotation Packet — RVAL-001

`packet_version: 2`

> Independent blind annotation. Classify this item using the taxonomy in
> `annotator_taxonomy_reference.md`, and record your answers in your assigned
> response sheet on the row for **RVAL-001**. Judge the claim/evidence structure only;
> do not try to infer an "intended" answer from wording, formatting, topic, or
> named placeholders.

## Task
The material below presents a scientific or commercial claim together with the
evidence available for it. Some proper names have been replaced with neutral
placeholders (e.g. [Researcher A], [Journal A]); treat placeholders as opaque.
Decide which single failure mode (if any) best characterizes the relationship
between the claim and its evidence, note any second failure mode, and flag any
structural problems.

## Case material (claim + available evidence)

**Study summary**

Title: "Volume vs intensity of physical activity and risk of cardiovascular and non-cardiovascular chronic diseases"

Published: [Journal A]
Authors: [Author A], [Author B], et al. ([University Lab A], [University Lab B], [University Lab C])

Design: Prospective observational cohort study using [National Biobank Cohort A] data. Two cohorts: ~96,000 participants with wrist-worn accelerometer data (7 days of wear), and ~376,000 with self-reported physical activity questionnaires. Median follow-up approximately 7 years.

Key findings:
- Participants with >4% of physical activity classified as vigorous had 29-63% lower risk of 8 major chronic diseases compared to those with no vigorous activity
- The 8 diseases: cardiovascular disease, dementia, type 2 diabetes, chronic kidney disease, chronic liver disease, respiratory disease, immune-mediated inflammatory diseases, and depression
- Strongest associations were for inflammatory conditions (63% lower risk) and dementia (61% lower risk)
- Even 15-20 minutes per week of vigorous activity (~4 minutes/day) was associated with meaningful risk reduction
- Vigorous activity intensity showed stronger associations per minute than moderate activity for most outcomes

Stated limitations (from paper):
- Observational design — cannot prove causation
- [National Biobank Cohort A] participants may not represent the general population
- Accelerometer data captured only 7 days — may not reflect habitual activity levels
- Residual confounding possible despite statistical adjustments

Funding: [National Science Funder A], others. No pharmaceutical industry funding reported.

**Media coverage**

Headline 1 ([News Outlet A] / [Professional Society A] press release): "Just a few minutes of effort could lower your risk of 8 major diseases"

Headline 2 ([News Outlet B]): "Just a Few Breathless Minutes a Day Could Slash Your Risk of 8 Major Diseases"

Headline 3 ([News Outlet C]): "Just A Few Minutes of Hard Exercise May Slash Your Risk for These Serious Health Conditions, Study Says"

Key quote from media coverage — Lead author [Author B] stated: "Our findings suggest that making some of your physical activity vigorous can provide substantial health benefits. This doesn't require going to the gym. Adding short bursts of activity that make you slightly breathless into daily life can make a real difference."

Co-author [Author D] stated: "Four and a half minutes are associated with approximately 35 to 50% lower risk for incident cardiovascular disease."

## Your annotation (record on your response sheet, row RVAL-001)
- primary_label
- secondary_label (optional)
- confidence (0-1)
- rationale
- ambiguity_notes
- source_voice_clear (yes/no/uncertain)
- claim_isolated (yes/no/uncertain)
- evidence_matches_claim_strength (yes/no/uncertain)
- missing_evidence_notes
- recommended_human_review (yes/no)
- freeform_notes
---
SOURCE FILE: RVAL-002.md
---
# Blind Annotation Packet — RVAL-002

`packet_version: 2`

> Independent blind annotation. Classify this item using the taxonomy in
> `annotator_taxonomy_reference.md`, and record your answers in your assigned
> response sheet on the row for **RVAL-002**. Judge the claim/evidence structure only;
> do not try to infer an "intended" answer from wording, formatting, topic, or
> named placeholders.

## Task
The material below presents a scientific or commercial claim together with the
evidence available for it. Some proper names have been replaced with neutral
placeholders (e.g. [Researcher A], [Journal A]); treat placeholders as opaque.
Decide which single failure mode (if any) best characterizes the relationship
between the claim and its evidence, note any second failure mode, and flag any
structural problems.

## Case material (claim + available evidence)

**Evidence context.** A startup developed a chat-based mindfulness app that offers users brief daily breathing and meditation exercises. In a two-week pilot project with 15 university students, daily questionnaire data were collected. Participants reported an average 30 percent decline in their subjective stress levels. The accompanying university research group notes that there was no control group, that the sample size was very small, and that long-term effects have not yet been studied.

**Claim to evaluate (the company's public statement).** The company declared that the app "has the potential to revolutionize mental health care and replace clinical therapies."

Evaluate only the company's claim above against the available evidence. The university research group's caveats are provided as evidence context, not as the claim under evaluation.

## Your annotation (record on your response sheet, row RVAL-002)
- primary_label
- secondary_label (optional)
- confidence (0-1)
- rationale
- ambiguity_notes
- source_voice_clear (yes/no/uncertain)
- claim_isolated (yes/no/uncertain)
- evidence_matches_claim_strength (yes/no/uncertain)
- missing_evidence_notes
- recommended_human_review (yes/no)
- freeform_notes
