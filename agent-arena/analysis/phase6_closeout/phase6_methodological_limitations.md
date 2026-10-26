# Phase 6 — Methodological Limitations & Risk Summary

Consolidated from the per-phase risk registers and result limitations
(`phase6_2_calibration/phase6_2_risk_register.md`, `phase6_2_results/phase6_2_limitations.md`,
`phase6_4_prompt_only_pilot/phase6_4_risk_register.md`,
`phase6_4_prompt_only_results/phase6_4_limitations.md`). These bound what Phase 6 evidence may
support; none is resolved by the closeout.

## Sample size and structure

- **Development-only, small n = 27.** The 16-case holdout stayed **sealed**; no Phase 6 result
  is a validated guarantee.
- **corr / mech at n = 2** are `small_n` / `descriptive_only` — unusable for label-level
  calibration claims.
- **`development_only` n = 1, `borderline` n = 0** — reported separately, never folded into
  headline figures.
- Whole-phase framing: **DEVELOPMENT CALIBRATION / PILOT — NOT HOLDOUT**.

## Single replication

- Each model run and each pilot arm is **one** replication. `temperature = 0.0` and an
  unsupported seed reduce but do **not** eliminate run-to-run variation. Only the **analysis**
  is deterministic, not the **sampling**. Label stability and confidence variability are
  unmeasured (Phase 7 priority).

## Ceiling effects

- Haiku and Opus reached 27/27; accuracy could not discriminate at the top of the pool. The
  pool likely lacks discriminative difficulty for strong models — an **evaluation-coverage vs
  discriminative-difficulty** distinction Phase 7 must address without retiring easy cases.

## Metric caveats

- **Brier is primary; ECE is secondary and high-variance.** With confidences concentrated in
  the top bins, ECE is sparse-bin and can invert against accuracy (Sonnet: lowest ECE, most
  errors). No "well-calibrated" claim is drawn from ECE.
- In the paired pilot, **Brier is dominated by the accuracy gap** (a confidently-wrong
  prediction contributes a large squared error) and adds little independent calibration
  signal.
- **Abstention was not demonstrated beneficial** as a general rule; any benefit point is
  **development-selected**, never an operating guarantee. `select_operating_threshold()`
  remains prohibited in code.

## Package-level contrast (Phase 6.4)

- The pilot contrasts **whole packages** (system prompt **and** ~11-vs-3-field response
  contract **and** truncation-repair-vs-strict-no-repair parser). It does **not** isolate one
  system-prompt string.
- **Conservative response-burden asymmetry:** the baseline's lighter 3-field burden could
  favor it; the Agent Arena advantage ran against that direction (conservative).
- **Arm-specific no-repair parser:** disclosed; it did not drive the result (both arms
  27/27), but a future parse-completion gap must be read as a design choice, not model
  behavior.

## Interpretation risks carried forward

- **Overclaim → over-specific** error pattern is a **hypothesis**, not a proven taxonomy
  defect (`phase6_integrated_findings.md` Part C).
- Replication frequency must **not** be reinterpreted directly as calibrated correctness
  probability (Phase 7 aggregation must be defined before results).
- No cross-model or cross-package result may be **pooled**; the 81 and 54 predictions are
  paired, not independent.

## Governance / process risks (mitigated, monitored)

- Post-result methodology drift — mitigated by frozen prep/result checkpoints and hashed
  contracts; re-verified at closeout (no result artifact modified).
- Private-material leakage — mitigated by anonymized envelopes, opaque DEV ids, and repeated
  leakage scans; re-verified at closeout (`phase6_security_and_leakage_audit.md`).
- Documentation overhead — Phase 6 accreted many narrative artifacts; Phase 7 proposes a
  compact artifact set (`phase7_handoff.md` §6).

## Residual open questions for Phase 7

Multi-run label/confidence stability; discriminative difficulty at the overclaim boundary;
perturbation and adversarial robustness; whether the paired advantage persists under
replication and harder cases; and a defined, pre-registered human-validation objective. None
authorizes holdout access absent a separate curator decision.
