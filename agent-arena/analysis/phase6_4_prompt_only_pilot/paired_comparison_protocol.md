# Phase 6.4A — Paired Comparison Protocol (FROZEN BEFORE RESULTS)

This protocol is frozen **before any prompt-only result exists**. It reuses the frozen
Phase 6.1/6.2 bins, thresholds, abstention costs, and denominator rules
(`analysis/phase6_1_confidence_protocol/`, `analysis/phase6_2_calibration/metric_definitions.md`)
and the same calibration engine (`src/agent_arena/calibration.py`). No metric, bin,
threshold, or cost may be changed after results are seen.

## Comparison unit

The same **27 development cases** with the same opaque **`DEV-0001…DEV-0027`** identities,
compared **pairwise** across two arms:

- **arm A — Agent Arena**: the completed Phase 6.2 Haiku envelope (`AA-6.2-RUN-6a3b93a24af7431e`);
- **arm B — prompt-only baseline**: one new Haiku run under `AA-RTC-6.4-HAIKU-PROMPT-ONLY-001`.

The 54 predictions are **paired outputs on 27 cases, not 54 independent cases.** They are
**never** pooled into a 54-case benchmark; no single pooled score is computed.

## What is contrasted (package-level, not a single prompt string)

Held fixed: the model (dated snapshot), the 27 cases, the user-visible case content
(`task.prompt`), runtime parameters, replication count, and the **evaluation targets**
(predicted top label + confidence — both arms are normalized to these). The arms differ as
**whole packages**: the system prompt **and** the model-facing response contract (~11
structured forensic fields for arm A vs 3 for arm B: `predicted_label, confidence,
brief_reason`) **and** the parser (arm A `parse_structured_output` with truncation repair
and a heuristic `final_answer` label; arm B a stricter no-repair parser reading
`predicted_label` directly). The endpoints below therefore describe a **package-level**
contrast, **not** the causal effect of one system-prompt string.

- **Parser and confidence completion are reported SEPARATELY** (per arm:
  `parse_ok` rate, confidence VALID/MISSING/INVALID coverage) and are **never conflated
  with classification accuracy**.
- The baseline's **lighter 3-field response burden** may favor arm B — a documented
  **conservative asymmetry** (an Agent Arena advantage despite the heavier burden is
  conservative; a baseline advantage may be partly explained by it).
- Arm B's **stricter no-repair parser** is an **arm-specific design choice**; a
  parse-completion gap must be interpreted in that light, not as model behavior.

## Primary descriptive endpoints (per arm)

1. **classification accuracy over all 27 cases** (denominator = 27, all records);
2. **binary top-label Brier score** over **VALID-confidence records only**.

## Secondary descriptive endpoints (per arm)

- **ECE** using the frozen **five-bin** definition `[0,0.2) [0.2,0.4) [0.4,0.6) [0.6,0.8)
  [0.8,1.0]` (descriptive; high-variance at this n);
- **ten-bin sensitivity** view (secondary only);
- **mean reported confidence**; **confidence-valid coverage** (VALID/MISSING/INVALID);
- **predicted-label distribution** (descriptive; never constrained);
- **high-confidence error count** (incorrect with VALID confidence ≥ 0.8, the top bin);
- **fixed-threshold selective accuracy and coverage** over the frozen τ grid
  `{0.0, 0.1, …, 1.0}`;
- **frozen abstention-cost** results (`coverage_lost_all = 1 − coverage_all`; benefit **and**
  cost; involuntary abstentions from MISSING/INVALID counted);
- **results by gold label** (all four labels visible);
- **results by existing stratum** (clear / borderline / development_only, reported separately);
- **paired correctness table by opaque DEV ID** (per-case correct/incorrect for both arms).

## Paired arm-vs-arm contrasts (descriptive)

- **prediction-disagreement count** — DEV ids where arm A and arm B predict different labels;
- **Brier difference** = `Brier(baseline) − Brier(Agent Arena)` (VALID records);
- **accuracy difference** = `accuracy(Agent Arena) − accuracy(baseline)` (all 27).

Sign conventions are fixed here so they cannot be re-oriented after results.

## Denominators (frozen, reused)

- accuracy → all records (valid labels), regardless of confidence validity;
- Brier / reliability / ECE → VALID-confidence records only;
- MISSING / INVALID → counted, **never** coerced to 0.0; a MISSING/INVALID record still
  contributes its classification outcome to accuracy.

## Small-sample discipline (frozen)

- Whole exercise labelled **development small-sample characterization**, not a validated
  guarantee; the 16-case holdout stays sealed.
- All four labels remain visible. For **`correlation_vs_causation` (n = 2)** and
  **`mechanism_vs_evidence` (n = 2)**, results are marked **`small_n`**,
  **`descriptive_only`**, and **not suitable for label-level calibration claims** — and
  are excluded from any macro summary.
- Every metric prints its `n`; every reliability bin prints its `n`; empty bins stay
  visible.

## Prohibitions (frozen)

No threshold is chosen/tuned on the results and then reported as unbiased
(`select_operating_threshold` remains an error). No new metric/bin/threshold/cost is
introduced after results. No winner is declared solely from this pilot. The comparison
metrics are computed **only** in a later analysis step from the two anonymized envelopes;
the execution session computes no metrics.
