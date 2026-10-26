# Phase 6.2 — Methodological Interpretation

**DEVELOPMENT CALIBRATION — NOT HOLDOUT.** Descriptive small-sample analysis. All three
models evaluated **the same 27 development cases**. No universal-superiority inference;
no threshold was optimized on these results; the holdout remained sealed. Model outputs
may remain nondeterministic despite frozen request parameters (`temperature = 0.0`,
`seed = UNSUPPORTED`).

This document separates three registers explicitly:
**[OBSERVED]** = numbers read off the frozen engine · **[INTERPRETATION]** =
methodological reading within the frozen protocol · **[SPECULATION]** = explicitly
unsupported, not a basis for any decision.

---

## 1. Headline results (observed)

Denominator note (important): the frozen engine reports two accuracy figures. The
per-model **headline is the CLEAR stratum** (26 records, protocol §11); the *all-27*
figure (`micro_all`) additionally includes the single `development_only` case. Both are
reported below; neither is pooled across strata into one headline.

| model | acc (all 27) | acc (clear, n=26) | Brier clear ↓ (primary) | Brier all-27 ↓ | ECE clear (secondary) | mean conf | errors |
|---|---|---|---|---|---|---|---|
| Haiku  | 27/27 = 1.000 | 26/26 = 1.000 | **0.0096** | 0.0093 | 0.0912 | 0.910 | 0 |
| Sonnet | 24/27 = 0.889 | 24/26 = 0.923 | **0.0747** | 0.1053 | 0.0012 | 0.923 | 3 |
| Opus   | 27/27 = 1.000 | 26/26 = 1.000 | **0.0098** | 0.0097 | 0.0927 | 0.908 | 0 |

**[OBSERVED]**
- Confidence coverage is 100% for every model: 27 VALID / 0 MISSING / 0 INVALID. No
  confidence was coerced; every classification outcome is retained in the accuracy
  denominator.
- All observed confidences lie in **[0.80, 0.98]**, i.e. entirely inside the top
  primary reliability bin `[0.8, 1.0]`. Bins `[0.0,0.2) … [0.6,0.8)` are **empty
  (n = 0)** for all three models and are shown as empty, never hidden.
- Haiku and Opus classified all 27 cases correctly. Sonnet made 3 errors.

## 2. Brier vs ECE — why Brier is primary (interpretation)

**[OBSERVED]** Sonnet — the only model with errors — has the **lowest** ECE (0.0012),
while error-free Haiku and Opus have ECE ≈ 0.09.

**[INTERPRETATION]** This is a textbook illustration of why the frozen protocol makes
**Brier primary and ECE secondary/descriptive**:

- With every confidence in a single bin, ECE collapses to `|mean_confidence −
  accuracy|`. Sonnet's mean confidence (0.922) happens to almost equal its clear
  accuracy (0.923), so its aggregate gap is ~0 — **even though three individually
  confident predictions are wrong**. ECE, at n = 27 in one bin, is blind to this.
- Brier is computed per prediction, so it correctly ranks Sonnet worst (0.075 clear /
  0.105 all-27) and Haiku/Opus best (~0.010). The primary metric orders the models the
  way the raw correctness does; the secondary metric inverts it. Per the frozen
  protocol, we read Brier and treat ECE as an underpowered, high-variance descriptor.
- Haiku/Opus ECE ≈ 0.09 reflects mild **under-confidence** (100% correct but ~0.91
  mean confidence), not miscalibration in the harmful direction.

## 3. Sonnet's errors (observed) and their shape (interpretation)

**[OBSERVED]** All three Sonnet errors have gold label `overclaim` and high confidence:

| dev_id | stratum | predicted | gold | confidence |
|---|---|---|---|---|
| DEV-0011 | clear | correlation_vs_causation | overclaim | 0.92 |
| DEV-0024 | clear | mechanism_vs_evidence | overclaim | 0.95 |
| DEV-0013 | development_only | mechanism_vs_evidence | overclaim | 0.95 |

Per-label (clear): Sonnet `overclaim` accuracy = 12/14 = 0.857 (Brier 0.128); `solid`
= 8/8; the two n = 2 labels are descriptive only.

**[INTERPRETATION]** On this development pool, Sonnet's misses are confident confusions
of `overclaim` cases for the two causal-reasoning categories
(`correlation_vs_causation`, `mechanism_vs_evidence`). This is a *directional* pattern
worth noting for curator attention, but it rests on **3 events**.

**[SPECULATION — not a basis for any decision]** Whether this reflects a stable
tendency of this Sonnet snapshot to over-attribute a specific failure mode to
`overclaim` items cannot be determined from 3 errors on a 27-case development pool. It
is a hypothesis to be examined only under separately authorized, pre-registered
evaluation — never confirmed here, and never on the sealed holdout.

## 4. Abstention (observed → interpretation)

**[OBSERVED]** Costed risk–coverage over the fixed τ grid `{0.0 … 1.0}`:

- Haiku, Opus: baseline selective risk is already **0** (all covered predictions
  correct); no τ can reduce risk below 0. Raising τ only sheds coverage
  (`benefit = 0`, `cost = coverage lost > 0`).
- Sonnet: baseline risk (τ = 0) = 0.077 on clear. The only non-trivial operating point,
  τ = 0.9, yields selective accuracy 0.913 (risk 0.087) at coverage 0.885 —
  **benefit = −0.010**. Because all three errors are among the *highest*-confidence
  predictions (≥ 0.92), thresholding drops correct low-confidence items first and the
  errors survive; selective risk **rises**.

**[INTERPRETATION]** Per `abstention_policy.md` §3, the honest conclusion is
**"abstention is not demonstrated beneficial on development data"** for any of the three
models: for Haiku/Opus there is nothing to gain; for Sonnet, confidence-thresholded
abstention would *increase* selective risk while also costing coverage. No operating
threshold is selected or recommended (that is prohibited on the evaluation set,
`calibration_protocol.md` §14).

## 5. Cross-model (observed → interpretation)

**[OBSERVED]** Same 27 cases, paired.
- Prediction disagreements: **3 of 27** DEV ids (DEV-0011, DEV-0013, DEV-0024) — every
  disagreement is Sonnet differing from an agreeing Haiku+Opus, and every one is a gold
  `overclaim` case.
- Paired correctness patterns (Haiku, Sonnet, Opus): `1,1,1` × 24; `1,0,1` × 3. Haiku
  and Opus are correctness-identical across all 27.

**[INTERPRETATION]** On this small development pool the three models agree on 24/27
cases and are separated only by Sonnet's 3 confident `overclaim` misses. This is a
descriptive, paired observation on identical items.

**[SPECULATION — explicitly rejected as a conclusion]** These data do **not** support
"Haiku/Opus are better than Sonnet" as a general claim. n = 27 (corr/mech at n = 2), a
single run per model, one development pool, and known small-sample variance make any
ranking a description of *this* pool, not a validated model comparison. No winner is
selected. The 81 predictions are **not** pooled into an 81-case benchmark and are not
treated as independent.

## 6. What would be needed to strengthen any of the above

**[INTERPRETATION]** Every statement above is development-set characterization. Turning
any of it into a validated claim (calibration guarantee, model ranking, adopted
abstention threshold, per-label calibration for corr/mech) would require separately
authorized, pre-registered evaluation on data that is **not** this development pool and
is **not** the sealed holdout — outside the scope Phase 6.2 authorizes.
