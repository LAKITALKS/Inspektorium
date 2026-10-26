# Taxonomy Precedence Rule — study_forensics gold labels

*Companion to `study_forensics_taxonomy.md`. Defines how a single primary
`gold_label` is chosen when more than one taxonomy category could apply. The rule
is model-independent: it is applied on claim/evidence structure, never on model
predictions.*

## Category roles

- **`overclaim` is the GENERIC / RESIDUAL category.** Its core signal is
  *rhetorical inflation* — the framing of results exceeds the evidence. This
  includes decorative hedging, surrogate endpoints framed as clinical outcomes,
  and extrapolation to unstudied populations (see `study_forensics_taxonomy.md`,
  `overclaim` section).
- **`correlation_vs_causation` and `mechanism_vs_evidence` are SPECIFIC
  structural failure-mode categories.** Each has an explicit definitional trigger:
  - `correlation_vs_causation`: a causal claim is drawn from a non-causal,
    uncontrolled, or confounded design (missing counterfactual / comparison arm).
  - `mechanism_vs_evidence`: a **described biological mechanism** (animal or
    preclinical pathway) is used to imply human clinical benefit that has not been
    demonstrated. Note: the taxonomy explicitly **excludes** the biomarker/
    surrogate-to-clinical gap ("Shape B") from this category and routes surrogate
    endpoints framed as clinical outcomes to `overclaim`.

## Precedence rule

1. A specific label takes precedence over generic `overclaim` **only if its
   documented definitional trigger is genuinely present AND it captures the core
   error of the claim.**
2. If the specific trigger is absent — or the specific label only fits by
   stretching its documented scope — the primary label stays `overclaim`. The
   specific label may be recorded as `gold_alternative_reading`, not as primary.
3. `overclaim` may remain a documented **secondary** reading when rhetorical
   overstatement co-exists with a genuine specific failure (e.g. case040).

## Governance constraints

- **Do not stretch a specific label** beyond its documented scope just because a
  model selects it. Silently widening a category to match model output is
  benchmark co-evolution / overfitting.
- **Stable model disagreement is a review trigger, not a label-change reason.** A
  strong model reading a documented alternative flags the case for human review;
  it does not by itself change the gold label.
- **A flip requires an independent taxonomy justification** (this rule), never
  "the model said so."
- **Historical metrics stay frozen.** Phase-5A reports reflect the case set at the
  time they were produced and are never silently recalculated. Any label change
  generates a **new** active-set artifact.

## Worked precedents

### case040 — specific trigger PRESENT → flip justified
An uncontrolled pre/post vocational-training design attributes a 27-point
employment gain causally to the program. The `correlation_vs_causation` trigger
(causal claim from an uncontrolled, confounded design) is directly present and
captures the core error. Primary label flipped `overclaim → correlation_vs_causation`
on taxonomy grounds; `overclaim` retained as the secondary reading. Model
agreement (3/3, 0.92) was corroboration, not the cause of the flip.

### case054 — model-preferred specific label REJECTED → no flip
A generic-drug brochure pairs a lone "may be comparable" hedge with
interchangeable framing and a switch recommendation, backed only by in-vitro
dissolution curves. A strong model **stably** read this as `mechanism_vs_evidence`
(3/3 in Phase-5A). The precedence rule **rejects** that reading as primary:

- No biological mechanism / animal-preclinical pathway is described — the
  `mechanism_vs_evidence` definitional trigger is **absent**.
- In-vitro dissolution is a **surrogate endpoint**; the taxonomy already routes
  "surrogate endpoints framed as clinical outcomes" to `overclaim` and excludes
  the surrogate-to-clinical gap ("Shape B") from `mechanism_vs_evidence`.
- The core designed error is a **decorative hedge** implying unproven equivalence
  — rhetorical inflation = `overclaim`.

Flipping to `mechanism_vs_evidence` would require stretching or silently expanding
the category; that larger taxonomy change is **not** made here. Primary label
stays `overclaim`; `mechanism_vs_evidence` is recorded as a documented but
**rejected** alternative.

**Anti-co-evolution note:** This adjudication is deliberately decided *against* a
stable 3/3 model reading. It is the reference example that the taxonomy rule — not
model behavior — controls gold labels.
