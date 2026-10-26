# Phase-5B Haiku Full Replication — H0->H1 Contract Difference Preregistration

**Frozen before Call 1. Do not edit after the first generation.**

- Plan: `AA-P5B-HAIKU-FULL-REPLICATION-001`  ·  Comparison: `AA-P5B-HAIKU-HISTORICAL-REFERENCE-001`
- Specification fingerprint: `d5de45995627efe97ea5042a8ae932f148ded456d9b939af678220de70cc5841`
- Preregistration content fingerprint: `53330eeeca015e45ec1003607807174d0fce30b5069772919405329e5347ccdd`
- Exact model (both conditions): `claude-haiku-4-5-20251001`

## Experiment identity
- **H0** = historical Phase-7 Haiku condition (frozen, reference-only, prompt v1-historical-phase7)
- **H1** = current repaired Agent Arena Haiku condition (prospective, prompt v2-taxonomy-aligned-phase5a)

## Scientific universe (identical H0/H1)
- 84 units = 34 bases (14 boundary + 16 adversarial + 4 neutral) + 50 perturbation variants in 10 clusters; N=5 -> 420 slots.
- Gold: solid 13, overclaim 44, correlation_vs_causation 10, mechanism_vs_evidence 17.
- Scientific manifest fingerprint: `55217a9de2b159388a13fca2038d284e3289f5d5e835b39cea3d980f1467f45c`

## Prompt identity (the primary intended difference)
- H0 prompt: `study_forensics_prompt/v1-historical-phase7` (condition `study_forensics.historical.v1`, sha `f7704fa50a7689ae...`, 4622 chars)
- H1 prompt: `study_forensics_prompt/v2-taxonomy-aligned-phase5a` (condition `study_forensics.taxonomy_aligned.v2`, sha `37d91b813bee2b4f...`, 5171 chars)
- Delta: H1 == H0 with exactly two rule blocks replaced (KEY RULE + PRIORITY RULE); +549 chars.

## Runtime parameters — IDENTICAL
- temperature 0.0, top_p OMITTED_FROM_REQUEST, seed UNSUPPORTED, max_output_tokens 4096, timeout 120s, transport retries <= 2, semantic retries PROHIBITED.

## Difference register — 32 components (6 can affect model output)

| # | Component | Can affect output? | Accounting-only? | Intentional? |
|---|---|---|---|---|
| 1 | `scientific_prompt_text_and_version` | YES | no | yes |
| 2 | `taxonomy_prompt_precedence` | YES | no | yes |
| 3 | `mechanism_vs_evidence_vs_overclaim_handling` | YES | no | yes |
| 4 | `scientific_decision_label_space` | no | yes | no |
| 5 | `confidence_parsing_and_validation_semantics` | no | yes | yes |
| 6 | `missing_confidence_handling` | no | yes | no |
| 7 | `invalid_confidence_handling` | no | yes | no |
| 8 | `boolean_string_nan_inf_out_of_range_confidence` | no | yes | yes |
| 9 | `terminal_attempt_semantics` | no | yes | no |
| 10 | `classification_valid_semantics` | no | yes | no |
| 11 | `calibration_valid_semantics` | no | yes | no |
| 12 | `analytical_complete_semantics` | no | yes | no |
| 13 | `denominator_handling` | no | yes | no |
| 14 | `parser_failure_semantics` | no | yes | no |
| 15 | `semantic_failure_persistence` | no | yes | no |
| 16 | `resume_checkpoint_authentication` | no | yes | yes |
| 17 | `unit_runtime_package_binding` | no | yes | yes |
| 18 | `execution_source_binding` | no | yes | yes |
| 19 | `environment_interpreter_binding` | no | yes | yes |
| 20 | `provider_construction_gate` | no | yes | yes |
| 21 | `canonical_qa_preflight` | no | yes | yes |
| 22 | `execution_authorization_contract` | no | yes | yes |
| 23 | `consumed_revoked_authorization_semantics` | no | yes | yes |
| 24 | `provenance_requirements` | no | yes | yes |
| 25 | `fail_closed_behavior` | no | yes | yes |
| 26 | `raw_freeze_procedure` | no | yes | yes |
| 27 | `prompt_packaging` | YES | no | yes |
| 28 | `runtime_sampling_parameters` | no | yes | no |
| 29 | `request_construction` | YES | no | yes |
| 30 | `runtime_contract_representation` | no | yes | yes |
| 31 | `temporal_provider_runtime_drift` | YES | no | no |
| 32 | `execution_ordering` | no | yes | no |

### Components that can affect model output

- **scientific_prompt_text_and_version** — PRIMARY confound. The prospective prompt is the historical prompt with exactly two rule blocks replaced (KEY RULE, PRIORITY RULE). All other prompt bytes identical.
- **taxonomy_prompt_precedence** — Changes how the model resolves overclaim vs specific structural labels; can move CvC/ME/overclaim modal outcomes.
- **mechanism_vs_evidence_vs_overclaim_handling** — H0 scored ME 0/17 and CvC 4/10 historically; the narrowed ME trigger is expected to move ME/overclaim boundary units. This is the central hypothesis.
- **prompt_packaging** — Follows from the prompt change.
- **request_construction** — Only the system prompt bytes differ; the 84 unit user payloads are byte-identical.
- **temporal_provider_runtime_drift** — UNCONTROLLED confound: identical model snapshot, but provider-side nondeterminism/temporal effects differ between the two runs. Not separable from the prompt effect in this design.

## Confounding statement

H0->H1 is a WHOLE-SYSTEM comparison. The only intended generation-time difference is the system prompt (v1->v2: KEY RULE + PRIORITY RULE). An uncontrolled temporal/provider confound also exists (same model snapshot, different wall-clock). All accounting/validity/authorization/QA differences are applied uniformly at analysis time or are non-generative execution controls. This design does NOT identify the causal contribution of any individual repair. No improvement or degradation may be attributed to a specific repair without a controlled ablation.

