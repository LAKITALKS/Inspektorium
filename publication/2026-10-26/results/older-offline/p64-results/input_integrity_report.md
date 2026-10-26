# Phase 6.4 — Input Integrity Report

### DEVELOPMENT PILOT — NOT HOLDOUT

Independent validation of the two anonymized result envelopes **before** any paired performance analysis. The holdout remained sealed; no private mapping, salt, or canonical identity was accessed.

## Tracked binding

- manifest_id: `AA-DEVPOOL-6100`
- public_commitment: `679233c6e8ccadf49045bd183c11e8f47d8dac3c6759eb99cc49b88026ae4332`

## Overall integrity: **PASS**

## Cross-arm pairing

- DEV-ID set identical across arms: **YES** (27 common ids)
- gold label identical per paired DEV: **YES** (mismatches: none)
- stratum identical per paired DEV: **YES** (mismatches: none)

### Agent Arena (forensic package) — claude-haiku-4-5-20251001
- run_id: `AA-6.2-RUN-6a3b93a24af7431e`  ·  expected contract: `AA-RTC-6.2-HAIKU-001`
- prompt_contract_version: `AA-RTC-6.2-HAIKU-001@sys_sha256=f7704fa50a7689ae56f8fc6d7a383205a5aca34d0c400be36335d6ad8abfcfd5`
- contract_id echoed in prompt_contract_version: **True**  ·  system_prompt_sha256 present: **True**
- parser completion: **27/27** (failures: 0) — reported separately from accuracy
- confidence: valid=27 missing=0 invalid=0
- gold aggregate: {"correlation_vs_causation": 2, "mechanism_vs_evidence": 2, "overclaim": 15, "solid": 8}
- leakage: none
- per-envelope result: **PASS**

| check | pass | detail |
|---|---|---|
| envelope_no_unexpected_fields | ✓ | unexpected=[] |
| records_no_unexpected_fields | ✓ | unexpected=[] |
| envelope_version_6.2.0 | ✓ | 6.2.0 |
| protocol_version_6.1 | ✓ | 6.1 |
| manifest_id_matches_tracked | ✓ | AA-DEVPOOL-6100 vs AA-DEVPOOL-6100 |
| public_commitment_matches_tracked | ✓ | 679233c6e8ccadf49045bd183c11e8f47d8dac3c6759eb99cc49b88026ae4332 |
| provider_anthropic | ✓ | anthropic |
| expected_record_count_27 | ✓ | 27 |
| declared_gold_aggregate_8_15_2_2 | ✓ | {"correlation_vs_causation": 2, "mechanism_vs_evidence": 2, "overclaim": 15, "solid": 8, "total": 27} |
| run_id_matches_expected | ✓ | AA-6.2-RUN-6a3b93a24af7431e vs AA-6.2-RUN-6a3b93a24af7431e |
| model_matches_expected | ✓ | claude-haiku-4-5-20251001 vs claude-haiku-4-5-20251001 |
| model_is_shared_pilot_model | ✓ | claude-haiku-4-5-20251001 |
| contract_binding_satisfied | ✓ | contract_id_present=True sha_present=True |
| record_count_27 | ✓ | 27 |
| dev_ids_unique_opaque | ✓ | n_unique=27 |
| gold_aggregate_8_15_2_2 | ✓ | {"correlation_vs_causation": 2, "mechanism_vs_evidence": 2, "overclaim": 15, "solid": 8} |
| confidence_no_invalid | ✓ | valid=27 missing=0 invalid=0 |
| confidence_validity_preserved | ✓ | valid=27 missing=0 invalid=0 |
| no_zero_coercion_artifact | ✓ | zero_conf_dev_ids=[] |
| explicit_correct_consistent | ✓ | inconsistent=[] |
| parser_completion_state_preserved | ✓ | parse_ok=27/27 failures=0 |
| not_synthetic_fixture_mislabeled_as_real | ✓ | run_id=AA-6.2-RUN-6a3b93a24af7431e generated_at=2026-08-05T07:35:06.214022+00:00 |
| no_identity_leakage | ✓ |  |
| engine_validate_result_envelope_clean | ✓ |  |

### prompt-only (competent minimal package) — claude-haiku-4-5-20251001
- run_id: `AA-6.4B-HAIKU-PROMPTONLY-f44d734f00162c03`  ·  expected contract: `AA-RTC-6.4-HAIKU-PROMPT-ONLY-001`
- prompt_contract_version: `AA-RTC-6.4-HAIKU-PROMPT-ONLY-001`
- contract_id echoed in prompt_contract_version: **True**  ·  system_prompt_sha256 present: **False**
- parser completion: **27/27** (failures: 0) — reported separately from accuracy
- confidence: valid=27 missing=0 invalid=0
- gold aggregate: {"correlation_vs_causation": 2, "mechanism_vs_evidence": 2, "overclaim": 15, "solid": 8}
- leakage: none
- per-envelope result: **PASS**

| check | pass | detail |
|---|---|---|
| envelope_no_unexpected_fields | ✓ | unexpected=[] |
| records_no_unexpected_fields | ✓ | unexpected=[] |
| envelope_version_6.2.0 | ✓ | 6.2.0 |
| protocol_version_6.1 | ✓ | 6.1 |
| manifest_id_matches_tracked | ✓ | AA-DEVPOOL-6100 vs AA-DEVPOOL-6100 |
| public_commitment_matches_tracked | ✓ | 679233c6e8ccadf49045bd183c11e8f47d8dac3c6759eb99cc49b88026ae4332 |
| provider_anthropic | ✓ | anthropic |
| expected_record_count_27 | ✓ | 27 |
| declared_gold_aggregate_8_15_2_2 | ✓ | {"correlation_vs_causation": 2, "mechanism_vs_evidence": 2, "overclaim": 15, "solid": 8, "total": 27} |
| run_id_matches_expected | ✓ | AA-6.4B-HAIKU-PROMPTONLY-f44d734f00162c03 vs AA-6.4B-HAIKU-PROMPTONLY-f44d734f00162c03 |
| model_matches_expected | ✓ | claude-haiku-4-5-20251001 vs claude-haiku-4-5-20251001 |
| model_is_shared_pilot_model | ✓ | claude-haiku-4-5-20251001 |
| contract_binding_satisfied | ✓ | contract_id_present=True sha_present=False |
| record_count_27 | ✓ | 27 |
| dev_ids_unique_opaque | ✓ | n_unique=27 |
| gold_aggregate_8_15_2_2 | ✓ | {"correlation_vs_causation": 2, "mechanism_vs_evidence": 2, "overclaim": 15, "solid": 8} |
| confidence_no_invalid | ✓ | valid=27 missing=0 invalid=0 |
| confidence_validity_preserved | ✓ | valid=27 missing=0 invalid=0 |
| no_zero_coercion_artifact | ✓ | zero_conf_dev_ids=[] |
| explicit_correct_consistent | ✓ | inconsistent=[] |
| parser_completion_state_preserved | ✓ | parse_ok=27/27 failures=0 |
| not_synthetic_fixture_mislabeled_as_real | ✓ | run_id=AA-6.4B-HAIKU-PROMPTONLY-f44d734f00162c03 generated_at=2026-08-05T22:33:07.630125+00:00 |
| no_identity_leakage | ✓ |  |
| engine_validate_result_envelope_clean | ✓ |  |
