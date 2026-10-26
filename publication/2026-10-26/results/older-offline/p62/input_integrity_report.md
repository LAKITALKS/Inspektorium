# Phase 6.2 — Input Integrity Report

### DEVELOPMENT CALIBRATION — NOT HOLDOUT

Independent validation of the three anonymized result envelopes **before** any performance analysis. The holdout remained sealed; no private mapping, salt, or canonical identity was accessed.

## Tracked binding

- manifest_id: `AA-DEVPOOL-6100`
- public_commitment: `679233c6e8ccadf49045bd183c11e8f47d8dac3c6759eb99cc49b88026ae4332`

## DEV-ID set identical across all three models: **YES** (27 ids, DEV-0001…DEV-0027)

## Overall integrity: **PASS**

### haiku — claude-haiku-4-5-20251001
- run_id: `AA-6.2-RUN-6a3b93a24af7431e`  ·  expected contract: `AA-RTC-6.2-HAIKU-001`
- prompt_contract_version: `AA-RTC-6.2-HAIKU-001@sys_sha256=f7704fa50a7689ae56f8fc6d7a383205a5aca34d0c400be36335d6ad8abfcfd5`
- contract_id echoed in prompt_contract_version: **True**  ·  system_prompt_sha256 present: **True**
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
| run_id_matches_expected | ✓ | AA-6.2-RUN-6a3b93a24af7431e vs AA-6.2-RUN-6a3b93a24af7431e |
| model_matches_expected | ✓ | claude-haiku-4-5-20251001 vs claude-haiku-4-5-20251001 |
| contract_binding_satisfied | ✓ | contract_id_present=True sha_present=True |
| record_count_27 | ✓ | 27 |
| dev_ids_unique | ✓ | n_unique=27 |
| gold_aggregate_8_15_2_2 | ✓ | {"correlation_vs_causation": 2, "mechanism_vs_evidence": 2, "overclaim": 15, "solid": 8} |
| confidence_all_valid | ✓ | valid=27 missing=0 invalid=0 |
| no_zero_coercion_artifact | ✓ | zero_conf_dev_ids=[] |
| explicit_correct_consistent | ✓ | inconsistent=[] |
| no_identity_leakage | ✓ |  |
| engine_validate_result_envelope_clean | ✓ |  |

### sonnet — claude-sonnet-4-5-20250929
- run_id: `AA-P62-SONNET-23f5dcc25de6`  ·  expected contract: `AA-RTC-6.2-SONNET-001`
- prompt_contract_version: `AA-RTC-6.2-SONNET-001;system_prompt_sha256=f7704fa50a7689ae56f8fc6d7a383205a5aca34d0c400be36335d6ad8abfcfd5`
- contract_id echoed in prompt_contract_version: **True**  ·  system_prompt_sha256 present: **True**
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
| run_id_matches_expected | ✓ | AA-P62-SONNET-23f5dcc25de6 vs AA-P62-SONNET-23f5dcc25de6 |
| model_matches_expected | ✓ | claude-sonnet-4-5-20250929 vs claude-sonnet-4-5-20250929 |
| contract_binding_satisfied | ✓ | contract_id_present=True sha_present=True |
| record_count_27 | ✓ | 27 |
| dev_ids_unique | ✓ | n_unique=27 |
| gold_aggregate_8_15_2_2 | ✓ | {"correlation_vs_causation": 2, "mechanism_vs_evidence": 2, "overclaim": 15, "solid": 8} |
| confidence_all_valid | ✓ | valid=27 missing=0 invalid=0 |
| no_zero_coercion_artifact | ✓ | zero_conf_dev_ids=[] |
| explicit_correct_consistent | ✓ | inconsistent=[] |
| no_identity_leakage | ✓ |  |
| engine_validate_result_envelope_clean | ✓ |  |

### opus — claude-opus-4-5-20251101
- run_id: `opus-878636c64fc8`  ·  expected contract: `AA-RTC-6.2-OPUS-001`
- prompt_contract_version: `f7704fa50a7689ae56f8fc6d7a383205a5aca34d0c400be36335d6ad8abfcfd5`
- contract_id echoed in prompt_contract_version: **False**  ·  system_prompt_sha256 present: **True**
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
| run_id_matches_expected | ✓ | opus-878636c64fc8 vs opus-878636c64fc8 |
| model_matches_expected | ✓ | claude-opus-4-5-20251101 vs claude-opus-4-5-20251101 |
| contract_binding_satisfied | ✓ | contract_id_present=False sha_present=True |
| record_count_27 | ✓ | 27 |
| dev_ids_unique | ✓ | n_unique=27 |
| gold_aggregate_8_15_2_2 | ✓ | {"correlation_vs_causation": 2, "mechanism_vs_evidence": 2, "overclaim": 15, "solid": 8} |
| confidence_all_valid | ✓ | valid=27 missing=0 invalid=0 |
| no_zero_coercion_artifact | ✓ | zero_conf_dev_ids=[] |
| explicit_correct_consistent | ✓ | inconsistent=[] |
| no_identity_leakage | ✓ |  |
| engine_validate_result_envelope_clean | ✓ |  |
