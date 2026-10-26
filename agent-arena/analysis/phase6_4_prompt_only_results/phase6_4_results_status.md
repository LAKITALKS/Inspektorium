# Phase 6.4 — Results Status (for curator review)

### DEVELOPMENT PILOT — NOT HOLDOUT

Validated, analyzed, and documented the paired Haiku package-level development comparison
from the two completed anonymized envelopes. **Nothing committed — stops for curator
review.** No re-run, no model/provider call, no holdout access, no completed Sonnet/Opus
result accessed, no methodology changed after results, neither completed envelope modified,
**Phase 6 closeout not begun.**

## Checkpoint

- HEAD `b4ce7e2a65e158b4833b33ce769e3bce067be43c` — verified; tracked tree clean before work.
- Frozen prompt/parser/metrics/thresholds/interpretation reused unchanged.

## Input-integrity status: **PASS** (both arms + cross-arm pairing)

All 22 gates passed for both envelopes: exact run IDs, contract IDs, shared model
`claude-haiku-4-5-20251001`, manifest `AA-DEVPOOL-6100`, public commitment `679233c6…4332`,
27 records/arm, unique opaque DEV ids, identical DEV-ID set across arms, identical gold label
and stratum per paired DEV, gold aggregate 8/15/2/2, parser-completion preserved, confidence
validity preserved, no missing→0.0 coercion, no unexpected fields, no synthetic-fixture
mislabel, and a clean leakage scan (no canonical/salt/mapping/private-path/BIAA/HLD token).

## Parser completion (reported SEPARATELY from accuracy)

- **Agent Arena:** 27/27 parsed, **0** parser failures.
- **prompt-only:** 27/27 parsed, **0** parser failures.
- Both arms: confidence VALID=27, MISSING=0, INVALID=0 (coverage 100%). The accuracy
  difference is therefore **not** a parser-completion or confidence-validity artifact.

## Headline result (descriptive; this 27-case pool only)

| metric | Agent Arena | prompt-only |
|---|---|---|
| accuracy (all 27) | **1.000** (27/27) | **0.889** (24/27) |
| Brier top-label (VALID) — primary | **0.0093** | **0.0814** |
| ECE 5-bin (all 27) — secondary | 0.0896 | 0.0811 |
| mean reported confidence | 0.910 | 0.896 |
| high-confidence errors (≥0.8) | 0 | 1 |

- **Accuracy difference** (AA − PO, frozen sign) = **+0.111** (3 of 27 cases).
- **Brier difference** (PO − AA, frozen sign) = **+0.0721** (Agent Arena lower/better).
- **No accuracy ceiling** this pilot (contrast: Phase 6.2 anticipated one). The gap rests
  entirely on **3 `overclaim` cases**; the other three gold classes tie at 100% (corr/mech at
  n=2 are `small_n`/`descriptive_only`).

## Paired correctness pattern (same 27 cases; never pooled into 54)

| quadrant | count | DEV ids |
|---|---|---|
| both correct | 24 | (all except below) |
| Agent Arena correct / prompt-only incorrect | **3** | DEV-0011, DEV-0013, DEV-0018 |
| Agent Arena incorrect / prompt-only correct | 0 | — |
| both incorrect | 0 | — |

- **Predicted-label disagreements: 3** — all gold `overclaim`, all cases where prompt-only
  chose a *more specific* label (correlation/mechanism) instead of `overclaim`. Hypothesis
  only: over-specification on borderline overclaim cases without the Agent Arena priority-rule
  scaffold.

## Confidence and abstention findings

- **High-confidence error:** exactly one, **prompt-only DEV-0013** (predicted
  `mechanism_vs_evidence` at conf **0.92**, gold `overclaim`), in the `development_only`
  stratum. Agent Arena: zero.
- **ECE inversion (read cautiously):** the secondary ECE is *lower* for prompt-only despite
  its errors — a sparse-bin, high-variance artifact at N=27, **not** a calibration-superiority
  claim.
- **Abstention (clear stratum, frozen τ grid, development-selected only):** Agent Arena gets
  **no benefit** from abstention (no errors to remove) and only loses coverage; prompt-only
  reaches selective accuracy 1.0 at **τ=0.8** (benefit 0.077) at a **cost** of declining
  3/26 ≈ 11.5% of cases — but its high-confidence DEV-0013 error is in `development_only` and
  is **not** caught by the clear-stratum curve. No threshold adopted or tuned.

## Methodological limitations (full list in `phase6_4_limitations.md`)

Small n (27; one run/arm); the whole accuracy signal is 3 single-class cases; corr/mech at
n=2 `descriptive_only`; `development_only` n=1, `borderline` n=0; package-level contrast (not
one prompt string) with a conservative response-burden asymmetry and an arm-specific no-repair
parser; Brier dominated by the accuracy gap; ECE high-variance; abstention points
development-selected; residual model nondeterminism; holdout sealed. No universal-superiority,
causal-attribution, calibration-superiority, or holdout/production claim is supported.

## Files created (nothing committed)

```
analysis/phase6_4_prompt_only_results/
  phase6_4_results_startup.md
  build_paired_comparison.py                 (deterministic generator)
  input_integrity_report.md / .json          (generated)
  agent_arena_haiku_arm_report.md / .json     (generated)
  prompt_only_haiku_arm_report.md / .json     (generated)
  paired_comparison_report.md / .json         (generated)
  phase6_4_methodological_interpretation.md
  phase6_4_limitations.md
  phase6_4_acceptance_review.md
  phase6_4_results_status.md                 (this file)
tests/test_phase6_4_paired_comparison.py     (new; 10 tests, synthetic envelopes only)
```

Neither raw envelope was copied into Git; tracked artifacts carry only aggregate metrics,
public provenance, and opaque DEV references.

## Validation

| gate | result |
|---|---|
| targeted paired-comparison tests | **10 passed** |
| targeted + 6.4A + calibration/confidence/output-contract | **195 passed** |
| full test suite | **1309 passed** (was 1299; +10) |
| ruff on generator + test | **clean** |
| deterministic regeneration (2 independent processes) | **byte-for-byte identical**; matches on-disk |
| leakage scan over tracked artifacts | **clean** — the only 64-hex values are the public commitment and the two public prompt hashes; no canonical/BIAA/HLD/salt/private-path/raw-response token; DEV-#### only as the opaque identity space; Sonnet/Opus only in "not accessed" boundary statements |

## Proposed commit paths (nothing staged)

```
analysis/phase6_4_prompt_only_results/
tests/test_phase6_4_paired_comparison.py
```

## Proposed commit message

```
Phase 6.4 results: paired Haiku package-level development comparison
```

**Phase 6 closeout not begun. No auto-commit; awaiting curator review.**
