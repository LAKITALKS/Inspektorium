# Phase 6.2 — Results Analysis Startup

**DEVELOPMENT CALIBRATION — NOT HOLDOUT.** Descriptive, small-sample analysis of the
frozen 27-case development pool. The 16-case holdout **remained sealed** and was never
accessed.

## Scope of this session

A fresh normal analysis session to **validate, analyze, document, and prepare** the
Phase 6.2 three-model calibration results for curator review. This session did **not**:

- access private case mappings, raw model responses, retry ledgers, private manifests,
  the salt, `candidate_eligibility.csv`, `internal_only/`, HLD/BIAA mappings, or the
  holdout (gold, maps, or results);
- modify any frozen methodology (metric definitions, bins, thresholds, abstention
  costs) — before **or** after seeing results;
- begin Phase 6.3 or Phase 6.4;
- commit anything (stops for curator review).

## Checkpoint verified

| item | expected | observed |
|---|---|---|
| repository HEAD | `dd53226b7a3b25b477794941f12a2bafca4c53af` | matches |
| tracked working tree | clean before analysis | clean |
| manifest_id | `AA-DEVPOOL-6100` | matches (tracked public manifest) |
| public commitment | `679233c6…6ae4332` | matches (tracked public manifest) |
| frozen gold aggregate | solid 8 / overclaim 15 / correlation 2 / mechanism 2 (= 27) | matches, per model |

## Authorized inputs (only these)

Three anonymized result envelopes, read from a private location **outside** the
repository and never copied into it:

| model | run_id | contract | records |
|---|---|---|---|
| Haiku (`claude-haiku-4-5-20251001`) | `AA-6.2-RUN-6a3b93a24af7431e` | `AA-RTC-6.2-HAIKU-001` | 27 |
| Sonnet (`claude-sonnet-4-5-20250929`) | `AA-P62-SONNET-23f5dcc25de6` | `AA-RTC-6.2-SONNET-001` | 27 |
| Opus (`claude-opus-4-5-20251101`) | `opus-878636c64fc8` | `AA-RTC-6.2-OPUS-001` | 27 |

Only opaque `DEV-####` identifiers and class labels were used.

## Frozen protocol honored (read first, unchanged)

`analysis/phase6_1_confidence_protocol/` (confidence semantics, calibration protocol,
abstention policy) and `analysis/phase6_2_calibration/` (anonymized result contract,
metric definitions, reporting template, acceptance criteria, risk register), realized
by `src/agent_arena/calibration.py`. Primary score = **binary top-label Brier**;
**five** fixed reliability bins primary, ten-bin only as a sensitivity view; **ECE
secondary/descriptive**; confidence VALID/MISSING/INVALID with **no coercion to 0.0**;
abstention **costed**; `n < 5` flagged; correlation/mechanism (n = 2) descriptive only.

## Artifacts produced (this directory)

`build_calibration_reports.py` (deterministic generator) · `input_integrity_report.{md,json}` ·
`{haiku,sonnet,opus}_calibration_report.{md,json}` ·
`cross_model_descriptive_comparison.{md,json}` ·
`phase6_2_methodological_interpretation.md` · `phase6_2_limitations.md` ·
`phase6_2_acceptance_review.md` · `phase6_2_results_status.md`.

All reports carry aggregated metrics and opaque `DEV` references only.
