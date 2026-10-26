# Adjudication & Kappa Plan

*How agreement between the original gold and the blind annotator is measured, and
how disagreements are handled. **No label is changed solely to match the second
annotator.***

## Units
- N = 20 active sample cases (case042 excluded; never in the stats).
- Two labelers: **A** = original gold (from YAML), **B** = blind annotator.
- Compare on **primary_label** first; secondary labels handled separately below.

## Metrics

### 1. Raw agreement
`raw_agreement = (# cases where A.primary == B.primary) / N`. Report overall and
separately for the **clear** (11) and **borderline** (9) strata.

### 2. Cohen's kappa (κ)
Chance-corrected agreement on the 4-label primary decision:
`κ = (p_o − p_e) / (1 − p_e)`, where `p_o` = raw agreement and `p_e` = expected
agreement from each labeler's marginal label frequencies. Report κ with a caveat
that N=20 gives a **wide confidence interval** (bootstrap 95% CI if feasible).

Interpretation bands (Landis–Koch, used as a rough guide, not a hard gate):
- κ ≥ 0.80 strong · 0.60–0.79 moderate–substantial · 0.40–0.59 fair–moderate ·
  < 0.40 weak.

### 3. Per-label agreement
For each of the four labels, report precision/recall-style agreement of B against A
(and note the thin classes: mechanism 2, correlation 3 — estimates are noisy).

### 4. Disagreement matrix
A 4×4 A-primary × B-primary confusion matrix over the 20 cases, so the **direction**
of disagreement is visible (e.g. overclaim↔mechanism, overclaim↔solid).

### 5. Primary vs secondary partial agreement
Beyond exact primary match, credit **partial agreement**:
- `partial_hit` = A.primary appears in {B.primary, B.secondary} OR B.primary
  appears in {A.primary, A.gold_alternative_reading label}.
Report `partial_agreement_rate` alongside strict agreement. This distinguishes
"totally different reading" from "same two modes, different ranking".

## What counts as serious disagreement
- **Serious:** A.primary and B.primary differ **and** B.primary is not A's
  documented alternative reading — i.e. a genuinely different failure mode (e.g.
  gold `solid` vs blind `correlation_vs_causation`).
- **Soft:** A.primary vs B.primary differ but B lands on A's **documented
  alternative** (e.g. case054 gold overclaim, blind mechanism_vs_evidence). These
  are expected on borderline cases and are informative, not alarming.
- **Structural flag:** any case where B marks `source_voice_clear = no` or
  `claim_isolated = no` — routed to intake review regardless of label agreement
  (this is the case042 failure signature).

## Curator-review queue
Every disagreement (serious or soft) and every structural flag is logged to a
documented review queue with: case_id, A.primary, B.primary/secondary, B.rationale,
disagreement class, and a curator disposition. Dispositions:
- `label_confirmed` — gold stands; rationale recorded (blind reading noted as
  alternative if apt).
- `taxonomy_clarified` — definitions/precedence doc updated; no case label changed.
- `case_flagged_for_rewrite_or_retire` — structural (source-voice/isolation) issue;
  follow the intake policy (new case_id / retirement), never a silent relabel.
- `label_revised` — **only** with an independent taxonomy justification (as in the
  case040 precedent), and logged with before/after + reason. Model or annotator
  agreement is corroboration, never the sole cause.

## Anti-drift rule
Do **not** flip a gold label just because the blind annotator disagrees. A single
second annotator is another data point, not ground truth. Changes require an
independent taxonomy argument and a logged rationale, exactly as for model
disagreement. Preserve every disagreement in the audit trail.
