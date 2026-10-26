# Phase 6.1 — Confidence Semantics (frozen preparation spec)

**Governance:** Level 2 (methodology). Frozen **before** any calibration result is
viewed. No model calls, no holdout, no results-driven choices.

---

## 1. Operational meaning of confidence

Confidence is **the model's stated degree of belief that its own primary
classification is correct**, under the frozen four-label study-forensics task
(`solid` · `overclaim` · `correlation_vs_causation` · `mechanism_vs_evidence`).

- It is a property of a single `(case, model, run)` prediction: the model's
  self-assessed probability that its emitted `final_answer` equals the gold label.
- It is **not** a system/heuristic score, **not** the checker's finding-confidence
  label (`HIGH/MEDIUM/HEURISTIC`), and **not** a calibrated probability yet.
  Calibration (Phase 6.2) is the empirical mapping from this stated value to
  observed accuracy; this document only fixes what the raw value *means* and when
  it is *usable*.

## 2. Scale and range (frozen)

- Confidence is a real number on the closed interval **[0.0, 1.0]** (the value the
  study-forensics output contract elicits, e.g. `"confidence": 0.85`).
- `1.0` = maximal stated belief the primary classification is correct; `0.0` =
  minimal stated belief. No rescaling, bucketing, or transformation is applied at
  ingestion; binning happens only in the calibration protocol.

## 3. Confidence validity rules (frozen)

Each raw confidence value is classified into exactly one validity state:

| state | definition | calibration use |
|-------|------------|-----------------|
| **VALID** | a real numeric value (`int`/`float`, not boolean, not NaN/Inf) with `0.0 ≤ v ≤ 1.0` | included |
| **MISSING** | absent / `null` / empty | excluded + counted |
| **INVALID** | present but non-numeric, boolean, NaN/Inf, or out of `[0.0, 1.0]` | excluded + counted |

Only **VALID** confidences enter calibration. **MISSING** and **INVALID** are
**never** imputed, defaulted, clipped, or coerced into a usable number — they are
recorded and reported as explicit exclusions with counts and reasons.

## 4. Mandatory non-silent handling (critical — risk R-2)

The current output parser (`output_contract.parse_structured_output`) coerces a
missing/non-numeric confidence to `0.0`. A coerced `0.0` is indistinguishable from
a genuine minimal-confidence report and would silently corrupt every reliability
curve.

**Rule:** calibration must operate on the **raw** confidence (pre-coercion), or on
a preserved validity flag — never on the coerced `0.0`. Concretely:

1. The Phase 6.2 runner must record, per prediction, either the raw confidence
   token or a `confidence_validity ∈ {VALID, MISSING, INVALID}` flag (and the raw
   value when VALID). The coerced `0.0` from the legacy parser must not be treated
   as a datum.
2. `confidence_validity.classify_confidence()` (this phase's deterministic tool) is
   the single source of truth for the classification; it is tested to keep
   MISSING/INVALID strictly separate from a true `0.0`.
3. A prediction whose confidence is MISSING/INVALID is excluded from calibration
   metrics and reported in an explicit "excluded-for-invalid-confidence" tally.

This is a **semantics decision**, not a code change to existing behavior: the
legacy parser is unchanged; Phase 6.2 consumes raw/flagged confidence instead of
the coerced field.

## 5. Correctness pairing (used by calibration)

For a prediction with a VALID confidence, **correctness** is binary:
`correct = (detected_label == gold_label)` under the frozen 4-label task
(see `calibration_protocol.md §correctness`). Confidence is always paired with this
correctness outcome; calibration asks whether stated confidence tracks empirical
correctness.

## 6. Reporting strata (confidence is reported within, never across, these)

- **clear** vs **borderline** cases are separate strata (borderline excluded from
  standard accuracy; reported as a divergence stratum).
- the **development-only** case(s) are their own explicitly labelled stratum.
- **retired** cases are excluded entirely.
- per-label reporting is mandatory given class imbalance (see protocol).

## 7. Out of scope for this document

The empirical calibration mapping, binning, scoring, abstention thresholds, and
risk–coverage all live in `calibration_protocol.md` / `abstention_policy.md`. This
document fixes only the meaning, scale, validity, and non-silent handling of the
raw confidence value.

For consistency (small-sample regime, N = 27): the **Brier score is the primary
probabilistic scoring metric** and **ECE is secondary/descriptive**; the primary
reliability presentation uses **five fixed equal-width bins** (`[0,0.2), [0.2,0.4),
[0.4,0.6), [0.6,0.8), [0.8,1.0]`), with a ten-bin view reported only as a sensitivity
check. All results are small-sample **characterization**, not validated calibration
guarantees.
