# Phase 5.05c — Multi-Annotator Proxy-IAA Analysis Plan

**analysis_plan_version:** 1.0
**run_id:** iaa_20260801_162800
**written_at (UTC):** 2026-08-01T16:28:00Z
**repository_commit:** d99d6f649ae93333ac6af451453912547518287b
**repository_tag:** v0.8.4-iaa-analysis-prep
**study_type:** strongly_anonymized_model_assisted_proxy_iaa

> This plan is written and frozen **before** the blind-to-gold mapping is resolved
> or any metric is calculated. The internal gold mapping may only be used *after*
> this file exists. No annotator may be removed after results are observed.

## Annotators (original identities preserved in all reports)
| ID | model_family | model_variant |
|----|--------------|---------------|
| A  | Anthropic    | Opus 4.8      |
| B  | Anthropic    | Opus 5        |
| C  | Gemini       | Flash 3.5     |
| D  | GLM          | GLM 5.2       |

## PRIMARY CROSS-FAMILY PROXY IAA
- Annotator A (Opus 4.8), Annotator C (Gemini Flash 3.5), Annotator D (GLM 5.2)
- Prioritizes cross-family model independence.

## SENSITIVITY TRIAD
- Annotator B (Opus 5), Annotator C (Gemini Flash 3.5), Annotator D (GLM 5.2)
- Pre-specified sensitivity: swap Opus 4.8 -> Opus 5 in the triad.

## WITHIN-FAMILY ANALYSIS
- Annotator A vs Annotator B (within-Anthropic generation comparison).
- This is a model-generation sensitivity analysis, NOT an independent multi-family IAA.

## FOUR-RATER DESCRIPTIVE ANALYSIS
- A, B, C, D.
- All six pairwise raw-agreement and Cohen's kappa.
- Each annotator vs gold.
- Four-rater Fleiss' kappa **only if** the committed `fleiss_kappa` is mathematically
  generic for four complete raters (it accepts n raters/item with n>=2 and complete
  data; verified generic -> will be computed).

## Rationale
- Primary analysis prioritizes cross-family independence (A/C/D).
- B is retained as a pre-specified sensitivity annotator (not removable post-hoc).
- A and B enable a within-Anthropic generation comparison.
- Disposition uses multiple signals, never one statistic alone, and is labelled
  PROVISIONAL — CURATOR REVIEW REQUIRED. No automatic Holdout Freeze.

## Independence description
- model independence: strong for A/C/D; partial for A/B (same family/vendor)
- context independence: preserved
- response independence: preserved
- source-material isolation: preserved
- retrieval independence: not applicable (web retrieval prohibited)
- human IAA: no — this is a model-assisted PROXY IAA, explicitly NOT a human IAA

## Metric implementation
- Uses the committed, tested `agent_arena.iaa_analysis` functions
  (metric_version iaa_analysis/1.0): raw_agreement, cohen_kappa, fleiss_kappa,
  per_label_agreement, disagreement_matrix, classify_disagreements,
  confidence_ambiguity_analysis, propose_disposition. No new statistical
  implementation is introduced in this run.
- Confidence values are uncalibrated self-reports throughout.
- per_label metrics use the committed names (gold_reproduction_rate /
  annotator_label_purity) and are NOT public benchmark accuracy claims.
