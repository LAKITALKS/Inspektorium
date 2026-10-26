# Phase 6.2 — Limitations & Statistical Caveats

**DEVELOPMENT CALIBRATION — NOT HOLDOUT.** Every figure in this results set is
small-sample **characterization**, not a validated calibration or performance
guarantee. This document enumerates the limitations a curator must hold in mind when
reading the reports.

## 1. Sample size (the dominant limitation)

- **n = 27** per model, total. All calibration metrics inherit high variance.
- **Per-label**: `solid` n = 8, `overclaim` n = 15 (14 in the clear stratum),
  `correlation_vs_causation` **n = 2**, `mechanism_vs_evidence` **n = 2**.
- The two causal labels at **n = 2** are marked `small_n` / `descriptive_only`
  everywhere and are **excluded from macro summaries** (macro uses only `solid` and
  `overclaim`, the labels with n ≥ 5). **No label-level calibration claim** may be
  drawn for correlation/mechanism.
- Strata: `clear` n = 26, `development_only` **n = 1**, `borderline` **n = 0**. The
  single development-only case and the empty borderline stratum are reported separately
  and never pooled into the headline.

## 2. Confidence is confined to one reliability bin

- All observed confidences lie in **[0.80, 0.98]** → the entire sample falls in the top
  primary bin `[0.8, 1.0]`. The other four bins are **empty (n = 0)** for all models.
- Consequence: the reliability curve has **one populated point**. ECE degenerates to
  `|mean_confidence − accuracy|` and cannot see within-bin miscalibration (see the
  Sonnet ECE = 0.001-with-3-errors case in the interpretation). ECE here is
  **indicative only, not validated**, exactly as the frozen protocol states.
- The 10-bin table is a **sensitivity view only**; it splits the top bin into
  `[0.8,0.9)` and `[0.9,1.0]` and is even sparser. It is not a headline.

## 3. Single run per model; possible nondeterminism

- `replication_count = 1` per model. There is **no within-model variance estimate**;
  every metric is a point value from one execution.
- The runtime contracts pin `temperature = 0.0` but `seed = UNSUPPORTED`. **Model
  outputs may remain nondeterministic despite frozen request parameters** — a re-run
  could differ. No claim here should be read as reproducible model behavior; only the
  *analysis* of these fixed envelopes is byte-for-byte reproducible.

## 4. Errors concentrate at high confidence (Sonnet)

- Sonnet's 3 errors all carry confidence ≥ 0.92. Confidence-based abstention therefore
  cannot separate them from correct predictions; the risk–coverage curve shows
  **no beneficial operating point** (τ = 0.9 benefit = −0.010). "Abstention not
  demonstrated beneficial on development data" is the reportable outcome, not a defect
  to be tuned away.

## 5. No cross-model pooling; no ranking

- The three runs share the same 27 cases. They are **paired**, not independent. The 81
  predictions must **not** be pooled into an 81-case benchmark, and **no single pooled
  calibration score** is computed.
- No universal-superiority claim is made. Haiku and Opus being error-free on this pool,
  and Sonnet missing 3, is a description of **this development pool**, not evidence that
  one model is generally better.

## 6. Provenance nuance — Opus contract-id echo

- Haiku and Sonnet echo their runtime-contract id (`AA-RTC-6.2-HAIKU-001`,
  `AA-RTC-6.2-SONNET-001`) inside `prompt_contract_version`. **Opus** carries only the
  `system_prompt_sha256` (`f7704…8abfcfd5`) — the schema-permitted *hash* form of that
  field — and **not** the literal `AA-RTC-6.2-OPUS-001` token.
- The envelope binding is still satisfied: Opus's exact model id
  (`claude-opus-4-5-20251101`) maps uniquely to its contract, and the pinned
  `system_prompt_sha256` matches. This is a **provenance-completeness observation**
  surfaced for curator awareness, **not** an integrity failure — the anonymized result
  contract explicitly allows a version *or hash*. Note also that all three contracts
  share the same `system_prompt_sha256`, so the hash alone does not distinguish
  contracts; the distinguishing pin is the exact model id.

## 7. Gold composition is not a result

- The frozen 8/15/2/2 aggregate is the **gold-label** composition of the pool and is
  enforced on `gold_label` only. Predicted-label distributions differ from it (e.g.
  Sonnet clear: solid 8 / overclaim 12 / correlation 3 / mechanism 3) and are reported
  **descriptively**; they are never constrained and never read as a performance target.

## 8. Boundaries respected

- The 16-case **holdout stayed sealed**; no private mapping, salt, canonical/BIAA/HLD
  identity, retry ledger, or `internal_only/` material was accessed. All outputs use
  opaque `DEV-####` ids and class labels only.
- **No frozen methodology was changed** after seeing results — no bin, threshold,
  abstention cost, or metric definition was altered; no result-driven case exclusion;
  no threshold optimized on the evaluation set.

## Bottom line

These results usefully **characterize** the three models' behavior on the frozen
development pool and exercise the frozen tooling end-to-end. They are **not** a
validated calibration, **not** a model ranking, and **not** a basis for adopting an
abstention threshold. Any such claim requires separately authorized, pre-registered
evaluation on non-development data — not this pool, and not the sealed holdout.
