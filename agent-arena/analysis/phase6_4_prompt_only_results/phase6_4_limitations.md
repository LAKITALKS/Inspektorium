# Phase 6.4 — Limitations

### DEVELOPMENT PILOT — NOT HOLDOUT

Every limitation the frozen protocol requires be stated wherever the corresponding numbers
appear. None of these are resolved by the pilot; they bound what the numbers may support.

## Sample size and structure

- **n = 27**, one run per arm. This is a **development small-sample characterization**, not
  a validated guarantee. The 16-case holdout **remained sealed**.
- The entire accuracy difference rests on **3 cases**, all in the **`overclaim`** gold class
  (n = 15). It is a fragile, single-class, single-run signal.
- **`correlation_vs_causation` (n = 2)** and **`mechanism_vs_evidence` (n = 2)** are
  **`small_n`** and **`descriptive_only`** — **not suitable for label-level calibration
  claims** and excluded from any macro summary. Both arms tie at 100% on these two labels, so
  they carry no discriminating information here regardless.
- The `development_only` stratum has **n = 1** (DEV-0013) and the `borderline` stratum is
  **empty (n = 0)**; each is reported separately and never folded into the clear-stratum
  headline. DEV-0013 is also the prompt-only arm's only high-confidence error.
- Reliability bins are sparse: only `[0.6,0.8)` and `[0.8,1.0]` are ever occupied; the three
  lower bins are empty (shown with n = 0). Any occupied bin with n < 5 is flagged
  `underpowered` and is not interpreted.

## Package-level contrast (not a single prompt string)

- The arms differ as **whole packages** — system prompt **and** model-facing response
  contract (~11 vs 3 fields) **and** parser (truncation-repair vs strict no-repair). The
  pilot **does not isolate the causal effect of one system-prompt string**.
- **Response-burden asymmetry (disclosed):** the baseline's lighter 3-field burden may favor
  it. Here the Agent Arena arm led *despite* its heavier burden, so the observed advantage is
  the **conservative** direction — but the asymmetry remains a confound for any attempt to
  attribute the gap to a single package component.
- **No-repair parser (arm-specific design choice, disclosed):** the baseline rejects
  repaired/truncated output while the Agent Arena arm accepts it. It did **not** drive this
  result (both arms completed 27/27), but a future parse-completion gap must be read as a
  design choice, not model behavior.

## Metric-specific caveats

- **Brier (primary)** is dominated here by the accuracy difference (a confidently-wrong
  prediction contributes a large squared error); it adds little independent calibration
  signal on this pool.
- **ECE (secondary)** is a **high-variance, low-precision** descriptor at N = 27 with two
  occupied bins. It is **lower for the prompt-only arm** — the opposite direction to accuracy
  — which is a sparse-bin arithmetic artifact, **not** evidence of better calibration. No
  "well-calibrated" claim is made from ECE.
- **Ten-bin reliability** is a **sensitivity view only** (secondary), never a headline.
- **Selective accuracy / abstention** points that show benefit are **development-selected**
  and are **not** unbiased operating guarantees; no threshold is adopted or tuned
  (`select_operating_threshold` remains prohibited). The prompt-only arm's only
  high-confidence error (DEV-0013) lies in the `development_only` stratum and is **not**
  captured by the clear-stratum risk–coverage curve.

## Determinism and reproducibility boundaries

- **Residual model nondeterminism:** `temperature = 0.0` and an unsupported seed reduce but
  do **not** eliminate run-to-run variation. Only the **analysis** is fully deterministic;
  the **sampling** is not. Each arm is a **single** replication.
- The analysis pipeline is byte-for-byte reproducible from the two envelopes and the frozen
  engine; the underlying model outputs are not guaranteed to reproduce.

## Scope boundaries (what was deliberately not touched)

- No raw responses, retry ledgers, execution attestations, DEV→canonical mappings, private
  manifests/salt, private annotations, `candidate_eligibility.csv`, `internal_only/`, holdout
  maps/gold/results, or HLD/BIAA mappings were accessed. Only opaque `DEV-####` identifiers
  are used.
- **No completed Sonnet or Opus result was accessed**; this pilot is Haiku-only by design and
  makes no cross-model claim.
- No frozen prompt, parser, metric, bin, threshold, cost, or interpretation rule was changed
  after seeing results. No case was excluded or altered. Neither completed envelope was
  modified. Phase 6 closeout was not begun.

## Bottom line

The pilot supports a **narrow, descriptive, paired observation on 27 development cases**: the
Agent Arena package classified all 27 correctly and the prompt-only package missed three
`overclaim` cases, with a correspondingly lower Agent Arena Brier and no Agent Arena
high-confidence error. It supports **no** claim of universal superiority, causal attribution
to any single package component, calibration superiority, or holdout/production performance.
