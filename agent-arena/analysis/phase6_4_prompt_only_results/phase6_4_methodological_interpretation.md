# Phase 6.4 — Methodological Interpretation

### DEVELOPMENT PILOT — NOT HOLDOUT

This interpretation is bound by the frozen `interpretation_rules.md` and
`paired_comparison_protocol.md`. Every number below comes from the deterministic generator
`build_paired_comparison.py` over the two anonymized envelopes; nothing was re-tuned after
results, no case was excluded, and no threshold was optimized.

## What this pilot is (and is not)

- **Same 27 paired development cases**, the same opaque `DEV-0001…DEV-0027` identities.
- **One run per arm**; the **same exact model** `claude-haiku-4-5-20251001`.
- A **package-level contrast**: the Agent Arena forensic prompting/scaffolding package
  (system prompt + ~11-field response contract + truncation-repairing parser) vs a
  competent minimal prompt-only package (3-field contract + strict no-repair parser). Held
  fixed: provider, model, cases, user-visible case content, runtime parameters, replication
  count, and the evaluated targets (top label + confidence).
- **Descriptive, small-sample** characterization. **Not** a holdout, **not** statistical
  proof, **not** a universal-superiority claim, **not** production evidence. The 16-case
  holdout **remained sealed**. The 54 predictions are two paired outputs on 27 cases and are
  **never** pooled into a 54-case benchmark; no pooled score exists.
- The contrast is **not** the causal effect of one system-prompt string alone. The arms
  differ as whole packages.

## Headline observation (this pool only)

On this 27-case development pilot:

| metric | Agent Arena | prompt-only | difference (frozen sign) |
|---|---|---|---|
| accuracy (all 27) | **1.000** (27/27) | **0.889** (24/27) | AA − PO = **+0.111** |
| Brier top-label (VALID) — primary | **0.0093** | **0.0814** | PO − AA = **+0.0721** |
| ECE 5-bin (all 27) — secondary | 0.0896 | 0.0811 | — |
| mean reported confidence | 0.910 | 0.896 | — |
| parser completion | 27/27 | 27/27 | — |
| confidence-valid coverage | 100% | 100% | — |
| high-confidence errors (≥0.8) | 0 | 1 | PO − AA = **+1** |

**On this pilot, the Agent Arena arm was descriptively more accurate and had a
descriptively lower (better) top-label Brier than the prompt-only arm.** This is reported
as a **paired development observation for this 27-case pool only**. It does **not**
generalize beyond the pilot, is **not** production or holdout evidence, and is **not**
attributed solely to the system prompt (the arms differ as whole packages).

## No accuracy ceiling this time — but the signal is small and label-local

Phase 6.2 anticipated a possible ceiling (Haiku was 27/27 under the Agent Arena package).
Here the arms **did** separate on accuracy, so no ceiling applies to the accuracy endpoint.
However, the entire accuracy gap rests on **3 cases**, all in the **`overclaim` gold class**
(`overclaim` accuracy: AA 15/15 vs PO 12/15 = 0.80). The other three gold classes are tied
at 100% in both arms, and `correlation_vs_causation` and `mechanism_vs_evidence` are at
**n = 2** (`small_n` / `descriptive_only`, unsuitable for label-level calibration claims).
A three-case, single-class, single-run difference is a **fragile** signal and must not be
read as a stable or general effect.

## The gap is genuine label disagreement, not a parser-completion artifact

Parser completion is **27/27 in both arms** and confidence-valid coverage is **100% in both
arms**, so the accuracy difference is **not** an artifact of the baseline's stricter
no-repair parser or of any confidence-validity gap. The three prompt-only errors are
**genuine predicted-label disagreements** on cases where the Agent Arena arm predicted the
gold `overclaim` label and the prompt-only arm predicted a *more specific* label instead:

| dev_id | stratum | gold | Agent Arena | prompt-only | prompt-only conf |
|---|---|---|---|---|---|
| DEV-0011 | clear | overclaim | overclaim ✓ | correlation_vs_causation ✗ | 0.75 |
| DEV-0013 | development_only | overclaim | overclaim ✓ | mechanism_vs_evidence ✗ | 0.92 |
| DEV-0018 | clear | overclaim | overclaim ✓ | mechanism_vs_evidence ✗ | 0.72 |

This shows up in the predicted-label distributions: the prompt-only arm **under-used**
`overclaim` (12 vs the gold 15) and **over-used** the two specific labels
(`correlation_vs_causation` 3 vs 2; `mechanism_vs_evidence` 4 vs 2). A **hypothesis only**
(not a conclusion): the minimal prompt's instruction to "choose the single most specific
label" may, without the Agent Arena priority-rule scaffold, pull borderline `overclaim`
cases toward an over-specific label. This is a candidate for later, separately authorized
investigation; it cannot be established from three cases in one run.

## Conservative-asymmetry framing (the advantage is on the harder side of the asymmetry)

Two frozen asymmetries were pre-declared:

1. **Response-burden asymmetry (conservative here).** The baseline carries a *lighter*
   3-field response burden that could *favor* it. The Agent Arena arm nonetheless showed the
   accuracy/Brier advantage **despite** its heavier ~11-field burden — i.e. the advantage
   runs **against** the direction this asymmetry would predict, so it is the *conservative*
   outcome, not one explained by the burden difference.
2. **No-repair parser (arm-specific design choice).** The baseline rejects
   repaired/truncated output. Because both arms completed 27/27, this choice did **not**
   drive the result here; it is noted so a future parse-completion gap would be read as a
   design choice, not model behavior.

## Confidence, Brier, and the ECE inversion (read cautiously)

The Agent Arena arm's much lower Brier (0.0093 vs 0.0814) is **primarily a consequence of
its perfect accuracy** on this pool — a wrong prediction made with high confidence (e.g.
DEV-0013 at 0.92) contributes a large squared error. Brier here therefore mostly re-expresses
the accuracy difference rather than adding an independent calibration finding.

The **secondary** 5-bin ECE is **slightly lower for the prompt-only arm** (0.0811 vs
0.0896) — i.e. it moves in the *opposite* direction to accuracy and Brier. This is **not**
evidence that the prompt-only arm is "better calibrated." ECE at N = 27 with only two
occupied bins is a **high-variance, low-precision** descriptor: the prompt-only arm happened
to place three predictions in the `[0.6,0.8)` bin (mean conf 0.73, accuracy 0.33), and the
arithmetic of that sparse bin structure lowered its ECE even though it made three errors. No
"well-calibrated" claim is drawn from ECE (per the frozen protocol). This inversion is a
useful reminder that ECE and accuracy can disagree at this n.

## High-confidence error (one, in the development-only stratum)

The prompt-only arm produced exactly **one high-confidence error** (VALID confidence ≥ 0.8):
**DEV-0013**, predicted `mechanism_vs_evidence` at confidence **0.92** against gold
`overclaim`. This case sits in the **`development_only` stratum** (reported separately,
excluded from the clear-stratum headline). The Agent Arena arm had **zero** high-confidence
errors. A confidently-wrong prediction is the most costly calibration failure mode, so this
single instance is worth flagging — while recognizing it is one case in one run.

## Fixed-threshold selective behavior (development-selected; not an operating guarantee)

On the **clear stratum** and the frozen τ grid:

- **Agent Arena** — selective accuracy is 1.0 at every τ; abstention yields **no benefit**
  (there are no errors to remove) and only **costs** coverage as τ rises (e.g. cost 0.308 at
  τ = 0.9). Abstention is **not demonstrated beneficial** for this arm on this pool.
- **prompt-only** — the two clear-stratum errors (DEV-0011 @ 0.75, DEV-0018 @ 0.72) sit
  below 0.8, so raising τ to **0.8** lifts selective accuracy to 1.0 (benefit 0.077) at a
  **cost** of declining 3/26 ≈ 11.5% of cases (the two errors **and** one correct case,
  DEV-0007 @ 0.72). The high-confidence DEV-0013 error is in the `development_only` stratum
  and so is **not** captured by this clear-stratum curve — abstention would **not** catch it.

Any such point is **development-selected** and explicitly **not** an unbiased operating
guarantee; no threshold is adopted (`select_operating_threshold` remains prohibited).

## What may and may not be concluded

**May (descriptive, this pool only):** on these 27 paired cases the Agent Arena package
classified all 27 correctly while the prompt-only package missed three `overclaim` cases;
its top-label Brier was lower; it had no high-confidence error. The difference is a paired
per-case observation.

**May not:** that Agent Arena is universally superior; that the system prompt alone caused
the gap; that the result predicts holdout or production behavior; that the prompt-only arm is
"worse calibrated" (the ECE moved the other way); that three overclaim cases in one run
establish a stable class-level effect; or that 27 cases (corr/mech at n = 2) support any
statistical claim.
