# Phase 5.05c — IAA Executive Summary (PROVISIONAL — CURATOR REVIEW REQUIRED)

**run:** iaa_20260801_162800 · **commit:** d99d6f649ae9 · **tag:** v0.8.4-iaa-analysis-prep
**study_type:** strongly_anonymized_model_assisted_proxy_iaa — model-assisted PROXY IAA, **not** a human IAA.

Annotators: A=Opus 4.8, B=Opus 5, C=Gemini Flash 3.5, D=GLM 5.2. n=20 blind cases.

## Primary cross-family A/C/D
- Fleiss' kappa: **0.8568** · all-three exact agreement: 0.8500
- Pairwise kappa: A_vs_C 0.7902, A_vs_D 1.0000, C_vs_D 0.7902
- vs gold kappa: A 1.0000, C 0.7902, D 1.0000
- soft 3 · serious 0 (serious on clear cases: 0)

## Sensitivity B/C/D (swap Opus 4.8 -> Opus 5)
- Fleiss' kappa: **0.8568** · all-three exact: 0.8500
- soft 3 · serious 0
- consensus changes vs primary: 0 []

## Within-Anthropic A vs B (generation sensitivity, not multi-family IAA)
- raw 1.0000 · Cohen's kappa 1.0000 · disagreements 0

## Four-rater A/B/C/D (descriptive)
- Fleiss' kappa: **0.8918** · unanimous 17 · 3-of-4 3 · 2v2 0 []

## Provisional disposition
**PROVISIONAL — CURATOR REVIEW REQUIRED · level: STRONG**
Multi-signal (Fleiss + pairwise + raw + serious count + clear/borderline concentration + sensitivity stability);
never one statistic alone. Holdout Freeze **NOT** triggered. Primary and sensitivity provisional level agree: True.

*All confidence values are uncalibrated self-reports. No gold label changed; no annotation altered.*
