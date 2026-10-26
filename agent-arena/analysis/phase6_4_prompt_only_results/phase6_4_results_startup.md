# Phase 6.4C — Results Startup (written BEFORE any metric was calculated)

### DEVELOPMENT PILOT — NOT HOLDOUT

This startup report is committed to the workflow **before** any performance metric is
computed. It fixes the checkpoint, the authorized inputs, the frozen methodology, and the
integrity gates that must pass before paired analysis. It changes no frozen prompt, parser,
metric, bin, threshold, cost, or interpretation rule.

## Session purpose

Validate, analyze, document, and prepare for curator review the **paired
development-pilot comparison** between two completed, anonymized Haiku result envelopes:

1. the completed **Agent Arena** forensic-package Haiku arm (Phase 6.2 run, read-only);
2. the completed competent minimal **prompt-only** Haiku arm (Phase 6.4B run, read-only).

No re-run, no model/provider call, no modification of either completed envelope, no Phase 6
closeout.

## Authoritative checkpoint (verified)

- Repository: the tracked `agent-arena` working tree (path not embedded here).
- Expected HEAD: `b4ce7e2a65e158b4833b33ce769e3bce067be43c` — **verified**.
- Tracked working tree: **clean** before analysis.
- Frozen baseline contract: `AA-RTC-6.4-HAIKU-PROMPT-ONLY-001`.
- Shared model: `claude-haiku-4-5-20251001`.

## Authorized inputs (the only two files read)

Both envelopes live **outside** the repository (in the private envelopes tree) and are
**never copied into Git**; the generator receives their paths as runtime arguments, so no
private path is embedded in any tracked artifact.

| arm | envelope (private tree, outside the repo) | expected run_id | contract |
|---|---|---|---|
| Agent Arena | `phase6_2_envelopes/haiku_result_envelope.json` | `AA-6.2-RUN-6a3b93a24af7431e` | `AA-RTC-6.2-HAIKU-001` |
| prompt-only | `phase6_4_envelopes/haiku_prompt_only_result_envelope.json` | `AA-6.4B-HAIKU-PROMPTONLY-f44d734f00162c03` | `AA-RTC-6.4-HAIKU-PROMPT-ONLY-001` |

**Not accessed** (out of scope by design): raw responses, retry ledgers, execution
attestations, DEV→canonical mappings, private manifests/salt, completed Sonnet/Opus
envelopes, private annotations, `candidate_eligibility.csv`, `internal_only/`, holdout
maps/gold/results, HLD/BIAA mappings, unrelated private directories. Only opaque `DEV-####`
identifiers are used.

## Scientific contrast (frozen, accurate)

A **descriptive, package-level** contrast. Held fixed: provider, exact dated Haiku model,
the same 27 development cases, the same model-visible case content (`task.prompt`), runtime
parameters, replication count, and the evaluated targets (predicted top label + confidence).
The arms differ as **whole packages**:

- **Agent Arena arm** — richer forensic system prompt/scaffold, larger structured response
  burden (~11 fields), Agent Arena parser path (truncation repair + heuristic label).
- **prompt-only arm** — competent minimal prompt, 3-field contract
  (`predicted_label, confidence, brief_reason`), strict no-repair parser.

Both are normalized to the same evaluated outputs. This is **not** the causal effect of one
system-prompt string. Parser completion and classification quality are reported
**separately**. The baseline's lighter response burden is a documented **conservative
asymmetry**; its strict no-repair parser is an **arm-specific design choice**.

## Input-integrity gates (must all pass before paired analysis)

Run IDs · contract IDs · shared model ID · manifest ID `AA-DEVPOOL-6100` · public
commitment `679233c6…4332` · 27 records/arm · unique opaque DEV ids · identical DEV-ID set
across arms · identical gold label per paired DEV · identical stratum per paired DEV · gold
aggregate exactly 8/15/2/2 · parser-completion state preserved · confidence
VALID/MISSING/INVALID preserved · no missing→0.0 coercion · no canonical/salt/mapping/
private-path/BIAA/HLD tokens · no unexpected result fields · no synthetic fixture mislabeled
as a real run · leakage clean. **If any gate fails, stop before paired performance
analysis.**

## Per-arm analysis (each arm separately, before comparison)

Parser completion + failure count; confidence VALID/MISSING/INVALID; accuracy over all
eligible records; correct/incorrect counts; predicted-label distribution; mean reported
confidence; confidence-valid coverage; binary top-label Brier; frozen five-bin reliability
table; descriptive ECE; frozen ten-bin sensitivity (secondary only); fixed-threshold
selective accuracy/coverage; frozen abstention-cost; results by gold label; results by
stratum; high-confidence errors; low-confidence correct; exact denominators; empty bins;
small-n warnings. All four labels remain visible. `correlation_vs_causation` (n=2) and
`mechanism_vs_evidence` (n=2) retain `small_n` / `descriptive_only` and are not suitable for
label-level calibration claims. Parser failures are never silently removed; every
denominator is reported.

## Paired comparison (descriptive; frozen sign conventions)

Accuracy difference = `accuracy(Agent Arena) − accuracy(prompt-only)`; Brier difference =
`Brier(prompt-only) − Brier(Agent Arena)`; ECE per arm (secondary); mean confidence and
confidence-valid coverage per arm; parser completion per arm; predicted-label disagreement
count; paired correctness table (both correct / AA-only / prompt-only-only / both incorrect);
opaque DEV ids for disagreements and asymmetric correctness; high-confidence-error
difference; fixed-threshold selective behavior; abstention-cost difference; results by gold
label and stratum; exact denominators.

**Prohibited:** pooling into a 54-case dataset; treating 54 predictions as 54 independent
cases; any pooled accuracy/Brier/ECE; statistical-proof claims; universal-winner selection;
altering or excluding cases after seeing results.

## Frozen interpretation banner (every report)

DEVELOPMENT PILOT — NOT HOLDOUT · same 27 paired development cases · one run per arm · same
exact model · package-level contrast · descriptive small-sample analysis · no
universal-superiority inference · no threshold optimized after results · small-n label
limitations · holdout remained sealed · residual model nondeterminism · parser and
response-contract asymmetry · smaller baseline response burden may favor the baseline.

## Planned tracked artifacts

`analysis/phase6_4_prompt_only_results/`: this startup, `input_integrity_report.{md,json}`,
`agent_arena_haiku_arm_report.{md,json}`, `prompt_only_haiku_arm_report.{md,json}`,
`paired_comparison_report.{md,json}`, `phase6_4_methodological_interpretation.md`,
`phase6_4_limitations.md`, `phase6_4_acceptance_review.md`, `phase6_4_results_status.md`,
and the deterministic generator `build_paired_comparison.py`. Tracked artifacts carry only
aggregate metrics, public provenance, and opaque DEV references — no raw envelope, no
private mapping. Neither raw envelope is copied into Git.

## Commit behavior

No auto-commit. Stop for curator review after implementation and validation.
