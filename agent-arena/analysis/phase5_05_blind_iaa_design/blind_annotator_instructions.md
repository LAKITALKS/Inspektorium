# Blind Annotator Instructions

*Read this fully before labelling. You are judging the **structure of a claim
against its evidence**, using a fixed 4-label taxonomy. You will not see the
"intended" answer, model outputs, or prior decisions — judge only what is in the
packet.*

## The four labels

### `solid`
The claim is appropriately scoped for its evidence. Limitations may exist but are
honestly acknowledged; the *reporting* does not overstate. Weak evidence honestly
reported as weak is still `solid`.

### `overclaim` (GENERIC / RESIDUAL)
The conclusion exceeds the evidence — **rhetorical inflation**. The *framing* is
the problem. Includes: conclusions beyond the data; **surrogate endpoints / biomarkers
framed as clinical outcomes**; extrapolation to unstudied populations; **decorative
hedging** (a qualifier that does not actually constrain the implied claim).

### `correlation_vs_causation` (SPECIFIC)
**Trigger:** a causal claim is drawn from a non-causal / uncontrolled / confounded
design — e.g. an uncontrolled before/after comparison, a cross-sectional
association, or an observational result used for a causal or policy recommendation,
with confounders unaddressed and no counterfactual / comparison arm.

### `mechanism_vs_evidence` (SPECIFIC)
**Trigger:** a **described biological mechanism** — an animal or preclinical
pathway — is used to imply a **human clinical benefit that has not been
demonstrated**. There must be an actual mechanism narrative (in mice/cells/pathway)
leaping to a human therapeutic claim.
**Not this label:** a bare surrogate/biomarker-to-clinical gap with no mechanism
narrative → that is `overclaim`.

## Precedence rule (how to choose among applicable labels)
1. A **specific** label (`correlation_vs_causation`, `mechanism_vs_evidence`) takes
   precedence over generic `overclaim` **only if its definitional trigger is
   genuinely present AND it captures the core error**.
2. If the specific trigger is absent, or fits only by stretching its definition,
   choose `overclaim` as primary. You may record the specific label as a
   `secondary_label`.
3. If both a genuine specific failure **and** rhetorical inflation are present,
   pick the one that captures the **core** error as primary and record the other as
   secondary.

**Do not stretch a specific label** to fit. If there is no described mechanism, do
not use `mechanism_vs_evidence` however "biological" the topic sounds.

## Handling ambiguity
- If two labels feel equally defensible, pick the primary that best captures the
  **core** error, set `confidence: low`, and use `secondary_label` +
  `ambiguity_notes` to record the tension. Low-confidence honest splits are
  valuable data, not failures.
- Do **not** try to guess the "intended" label from writing style, topic, or how
  synthetic the text feels. Judge only claim vs evidence.

## Recording a secondary label
Use `secondary_label` when a second failure mode is genuinely co-present (e.g. a
causal overreach that is *also* rhetorically inflated). Leave it "none" if only one
mode applies.

## Flagging structural problems
- `source_voice_clear = no` — if you cannot tell who is asserting the claim, or the
  claim is voiced by someone critiquing it.
- `claim_isolated = no` — if the claim to judge is buried inside surrounding
  analysis that already qualifies or critiques it (this makes the task
  interpretation, not claim forensics — flag it rather than forcing a label).
- `evidence_matches_claim_strength` — your core judgement: yes / partial / no.

## Golden rule
**Judge the claim/evidence structure only.** Ignore what you imagine the benchmark
"wants." Your independent reading is the measurement.
