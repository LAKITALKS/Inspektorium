# Phase 6.1 — Abstention Policy (frozen preparation spec)

**Governance:** Level 2. Frozen before results. Abstention is **evaluated, never
assumed beneficial** (risk R-5). Development material only.

---

## 1. Abstention rule (frozen)

A prediction **abstains** when its **VALID** confidence is below an operating
threshold `τ`:

```
answer(prediction) = detected_label   if confidence ≥ τ   (covered)
                     ABSTAIN          if confidence < τ    (abstained)
```

- `τ` ranges over the pre-declared grid `{0.0, 0.1, …, 1.0}` for curve reporting.
- A prediction with **MISSING/INVALID** confidence cannot be thresholded; it is an
  **involuntary abstention** (coverage failure) and is counted in the coverage
  denominator, never silently dropped.
- Abstention is defined only on the frozen four-label task; abstaining means "no
  label emitted at this operating point," not a fifth label.

## 2. Cost model (frozen)

Every abstention operating point reports **both sides of the trade**:

| quantity | definition |
|----------|------------|
| **coverage(τ)** | covered / (covered + abstained) over VALID-with-label predictions |
| **selective accuracy(τ)** | accuracy among covered |
| **selective risk(τ)** | 1 − selective accuracy(τ) |
| **benefit** | error reduction on covered vs the no-abstention baseline (τ = 0) |
| **cost** | coverage lost = 1 − coverage(τ); i.e. cases the system declines to answer |

- **No single scalar is used to declare abstention "good."** The risk–coverage
  curve is reported in full; any chosen point is described by its (coverage, risk)
  pair and both benefit and cost explicitly.
- An optional explicit cost ratio may be *reported* (e.g. "each avoided error costs
  k declined answers"), but is **not** optimized to a target in Phase 6 (see
  `calibration_protocol.md §14`).

## 3. Acceptance criterion for adopting abstention (frozen, conditional)

Abstention is **not** adopted by default. It may be described as *beneficial at a
point* only if, on development data:

1. selective risk strictly decreases relative to the τ = 0 baseline **and**
2. the coverage retained at that point is explicitly stated **and**
3. the point is disclosed as **development-selected** (not an unbiased estimate).

If no point satisfies (1) with acceptable coverage, the honest reported conclusion
is **"abstention not demonstrated beneficial on development data."** Absence of
benefit is a valid, reportable outcome.

## 4. Small-sample caveat (frozen)

With `n_calibration` small and correlation/mechanism at n = 2, risk–coverage
estimates are high-variance. Every abstention figure carries the `n` it rests on
and the "indicative, not validated" flag. No abstention threshold derived here may
be presented as a validated operating guarantee, and none may be tuned against the
sealed holdout. Consistent with `calibration_protocol.md` (Brier primary, ECE
secondary, five primary reliability bins), the correlation/mechanism strata (n = 2)
are **descriptive only** — no label-level abstention claim is drawn from them.

## 5. Stratified reporting (frozen)

Risk–coverage is reported per model and, where `n ≥ 5`, per clear-label stratum;
borderline and development-only strata are reported separately and never pooled
into the headline abstention figure.
