# Sensitivity Triad — B / C / D

**Study:** strongly_anonymized_model_assisted_proxy_iaa — model-assisted PROXY IAA, not human IAA.  
**Annotators:** B (Anthropic Opus 5), C (Gemini Flash 3.5), D (GLM GLM 5.2)

**Fleiss' kappa:** 0.8568 · **All-rater exact agreement:** 0.8500

## Pairwise Cohen's kappa
- B_vs_C: 0.7902 (raw 0.8500)
- B_vs_D: 1.0000 (raw 1.0000)
- C_vs_D: 0.7902 (raw 0.8500)

## Annotator vs gold
- B: kappa 1.0000, raw 1.0000
- C: kappa 0.7902, raw 0.8500
- D: kappa 1.0000, raw 1.0000

## Disagreements
- soft: 3 · serious: 0

**Proposed disposition (framework signal):** STRONG  
> consider multi-rater + pairwise kappas + raw agreement + serious disagreement count + per-label/borderline concentration together; this is a proxy-IAA gate, not a benchmark-validity claim

*Confidence values are uncalibrated self-reports. No gold label is changed.*