# Phase 6.2 — Results Status (for curator review)

**DEVELOPMENT CALIBRATION — NOT HOLDOUT.** Descriptive small-sample analysis; the same
27 development cases across all three models; no universal-superiority inference; no
threshold optimized on the results; small-n label limitations apply; the holdout
remained sealed; model outputs may remain nondeterministic despite frozen request
parameters. **Nothing is committed — this session stops here for curator review.**

## 1. Envelope integrity — PASS (all three)

- HEAD `dd53226…`; tracked tree clean before analysis.
- `manifest_id` = `AA-DEVPOOL-6100` and `public_commitment` = `679233c6…6ae4332` equal
  the tracked public manifest for every envelope.
- 27 records each; **DEV-ID set identical** across all three (`DEV-0001…DEV-0027`);
  gold aggregate **8 / 15 / 2 / 2** verified on gold labels per model.
- Confidence: **27 VALID / 0 MISSING / 0 INVALID** per model; no `0.0` coercion artifact.
- No unexpected envelope/record fields; leakage scan clean (no canonical/BIAA/HLD id,
  salt, or private path).
- Run/model/contract match expectations. **One provenance note:** Opus's
  `prompt_contract_version` carries only the `system_prompt_sha256` (schema-permitted
  hash form), not the literal `AA-RTC-6.2-OPUS-001`; binding satisfied via exact model
  id + matching pinned sha. Flagged for curator decision; **not** a failure.

## 2. Headline results (development, small-sample)

| model | acc all-27 | acc clear (n=26) | Brier clear ↓ (primary) | ECE clear (secondary) | mean conf | errors |
|---|---|---|---|---|---|---|
| Haiku  | 1.000 | 1.000 | 0.0096 | 0.0912 | 0.910 | 0 |
| Sonnet | 0.889 | 0.923 | 0.0747 | 0.0012 | 0.923 | 3 |
| Opus   | 1.000 | 1.000 | 0.0098 | 0.0927 | 0.908 | 0 |

- **Haiku, Opus:** all 27 correct; mildly **under-confident** (mean conf ≈ 0.91 vs 100%
  accuracy → the ~0.09 ECE).
- **Sonnet:** 3 high-confidence errors, **all gold `overclaim`** (DEV-0011 →
  correlation @0.92 clear; DEV-0024 → mechanism @0.95 clear; DEV-0013 → mechanism @0.95
  development_only). Brier ranks Sonnet worst; **ECE (0.001) is deceptively low** because
  all confidences sit in one bin and its mean confidence ≈ its accuracy — the documented
  reason ECE is secondary.

## 3. Abstention — not demonstrated beneficial (all three)

Costed risk–coverage over τ ∈ {0.0 … 1.0}. Haiku/Opus baseline risk already 0 (no
gain possible). Sonnet's only non-trivial point τ = 0.9 gives **benefit = −0.010**
(errors are the highest-confidence predictions, so thresholding raises selective risk
while costing coverage). No operating threshold selected.

## 4. Cross-model (secondary, descriptive; same 27 paired cases)

- Prediction disagreements: **3 of 27** DEV ids, all Sonnet-vs-(Haiku=Opus), all gold
  `overclaim`. Paired correctness pattern (H,S,O): `1,1,1` × 24, `1,0,1` × 3.
- **No pooling** into an 81-case benchmark; **no winner** selected. Haiku/Opus being
  error-free and Sonnet missing 3 describes *this* pool only.

## 5. Validation results

| gate | result |
|---|---|
| targeted calibration/confidence/manifest tests | **120 passed** |
| full test suite | **1162 passed** |
| ruff (generator; touched-relevant source) | **clean** |
| deterministic regeneration (2 independent processes) | **byte-for-byte identical**, and identical to the committed artifacts |
| leakage scan of data artifacts (.json/.md) | **clean** — only 64-hex present are the 2 public values (commitment, prompt-sha) |
| envelopes copied into repo? | **no** |
| src/ or tests/ modified? | **no** — no methodology change, no threshold optimization, no result-driven exclusion |
| all 27 records in every denominator where applicable | **yes** |

_Leakage-scan note:_ the generator source's `_SALTY_KEYS` tuple lists forbidden **key
names** (`salt`, `salt_hex`, …) as its own screening vocabulary — detector code, not a
private value.

## 6. Files created (all under `analysis/phase6_2_results/`, none committed)

`build_calibration_reports.py` · `input_integrity_report.{md,json}` ·
`haiku_calibration_report.{md,json}` · `sonnet_calibration_report.{md,json}` ·
`opus_calibration_report.{md,json}` · `cross_model_descriptive_comparison.{md,json}` ·
`phase6_2_results_startup.md` · `phase6_2_methodological_interpretation.md` ·
`phase6_2_limitations.md` · `phase6_2_acceptance_review.md` · this status file.

## 7. Boundaries

No private case mapping, raw response, retry ledger, private manifest, salt,
`candidate_eligibility.csv`, `internal_only/`, HLD/BIAA mapping, or holdout material was
accessed. No frozen methodology was modified. **Phase 6.3 / 6.4 not begun.** Awaiting
curator review before any commit.
