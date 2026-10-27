# Audit runtime test fixtures

Synthetic fixtures for the audit runtime tests live here, together with copies of research
material that the product tests read. The research material was copied from source commit
`d086973936d893e204dce426d23b35328d2a6c2c`. The
[research record](https://github.com/LAKITALKS/inspektorium-research-record/tree/record-2026-10-27)
keeps the originals in its runtime folder (see [history](../../../docs/research/history.md)); the
source paths below are relative to that folder. Copies are byte-identical unless noted.

- `historical/` holds byte-bound public archive files. Tests compare their SHA-256 with
  pinned values, so they are never edited and keep their original wording.
- `live_capture_attempt_010_final_text.json` keeps only `interpretation.final_text` of the
  source capture. The value is byte-identical; the echoed request prompt is omitted.
- `case_library/`, `robustness_cases/`, `report_prototype/` and `agents/` are research inputs
  that the tests use as realistic data.

| Fixture | Source path in the record's runtime folder | SHA-256 of the fixture |
| --- | --- | --- |
| `agents/claude_opus.yaml` | `agents/claude_opus.yaml` | `36a7d3b92b77157a254015ce762b54f20f53b440a357821bf28baf8d04e4d6ca` |
| `case_library/case001_social_media.yaml` | `tasks/study_forensics/case001_social_media.yaml` | `b0be7f9bb18de920cae2fb5f73ada759c9ae75991a8012a08928681c0a3d1e4f` |
| `case_library/case004_multivitamin.yaml` | `tasks/study_forensics/case004_multivitamin.yaml` | `5de0dea4e6294c3e527b252ed43f6199b9f001febf49cbeea2a0ead4ab5241ac` |
| `case_library/case007_vitamin_d_covid.yaml` | `tasks/study_forensics/case007_vitamin_d_covid.yaml` | `340dca8bcb4ebd60b45580d7935a90af6dbd12bd3b42c69456953aa7905620bb` |
| `case_library/case009_mindfulness_autism.yaml` | `tasks/study_forensics/case009_mindfulness_autism.yaml` | `7124abfed709c0373e225c8c00eb5a1949619ea9788e3cafb614602295b6ac6a` |
| `case_library/case013_gut_microbes.yaml` | `tasks/study_forensics/case013_gut_microbes.yaml` | `4202b09701fd91e2ae37a9992a9d64967d25e275fa152e04ed9970dd69ed368b` |
| `case_library/case019_houseplants.yaml` | `tasks/study_forensics/case019_houseplants.yaml` | `c045752a9d2906ccc8e0c2c257d442f52bf9c6a308064b59dc9c6aa8900b4b6a` |
| `case_library/case021_virtual_tutoring.yaml` | `tasks/study_forensics/case021_virtual_tutoring.yaml` | `5a6c7b14c465b91f402065bec28a75fbb84b6f43d72a0a8cf1dbff664fb9e22e` |
| `case_library/case022_four_day_workweek.yaml` | `tasks/study_forensics/case022_four_day_workweek.yaml` | `9b8c7abe223e32ce60bce886376aba0830a8550ba9371343a32a17a23393672a` |
| `case_library/case023_green_space_mental_health.yaml` | `tasks/study_forensics/case023_green_space_mental_health.yaml` | `20f733d6f8873822d97cc80f2e6e5c27542fec14ddeaea2656eb2c9a259905d0` |
| `case_library/case024_klotho_gene_therapy.yaml` | `tasks/study_forensics/case024_klotho_gene_therapy.yaml` | `e3189793dcff8d07fb6f048dacaea1dd6f7e4c16b4ea360f6569971218ebea63` |
| `case_library/case025_ai_instruction_overclaim.yaml` | `tasks/study_forensics/case025_ai_instruction_overclaim.yaml` | `aee61cb985b41cc4b401c93433f9f1ff9362f9a74706000c695e7c65d1497d82` |
| `case_library/case026_air_sensor_validation.yaml` | `tasks/study_forensics/case026_air_sensor_validation.yaml` | `37ca6a8ae7db70911fdada42c5ac59233ab12d6e43690b33ac00b59f76949828` |
| `case_library/case027_ai_coding_productivity.yaml` | `tasks/study_forensics/case027_ai_coding_productivity.yaml` | `dd0ad866b546573ba8f9e36ea6194b1aa88648a454d027f6c3db0bf09b77a550` |
| `case_library/case028_nad_alzheimers_mice.yaml` | `tasks/study_forensics/case028_nad_alzheimers_mice.yaml` | `fcd270733404df27f16f608972c332eb5cd34988efb0458dcbb5fa15e8653df3` |
| `case_library/case029_amyloid_antibody_biomarkers.yaml` | `tasks/study_forensics/case029_amyloid_antibody_biomarkers.yaml` | `fa89c5aed455d856ad2b9302de6d3352b113eca8c2656316d5dbe25a12b7969f` |
| `case_library/case030_apj_exercise_mimetic.yaml` | `tasks/study_forensics/case030_apj_exercise_mimetic.yaml` | `32f61704168fad9547f5ecf072dc5203f0e0fdacdb5e0f2c527a6c72ba69f2a9` |
| `case_library/case031_rapamycin_longevity.yaml` | `tasks/study_forensics/case031_rapamycin_longevity.yaml` | `73c1c204628a59e42f2107ebe467db46bd9dfb293265347291c68cfcad743889` |
| `case_library/case032_cholesterol_drug_biomarker.yaml` | `tasks/study_forensics/case032_cholesterol_drug_biomarker.yaml` | `12a328f73e1dbbee20660f03d406a65cf26061176d4deb4e3e8fe4e581da88c6` |
| `case_library/case033_literacy_rct.yaml` | `tasks/study_forensics/case033_literacy_rct.yaml` | `a7a3b086830fdc29b048dbf3d8dd3a45629f05bb931f05aa9464b1b720bb91c4` |
| `case_library/case034_gas_stoves_asthma.yaml` | `tasks/study_forensics/case034_gas_stoves_asthma.yaml` | `0f0e6f3588e125a3dfdfe7689c71ab618a8a33e226cb38903791c492faef077c` |
| `case_library/case035_ai_tutoring.yaml` | `tasks/study_forensics/case035_ai_tutoring.yaml` | `be2685b8b833955c0608e48b03d1e6832a5d1b7378b7dd179770bb69abbbd4a2` |
| `case_library/case036_antioxidant_mice_memory.yaml` | `tasks/study_forensics/case036_antioxidant_mice_memory.yaml` | `ab2b5a657a82f0dc580bffe6a609ef37d6e7ba30addffc7c8863fb989eb785af` |
| `case_library/case037_mindfulness_app.yaml` | `tasks/study_forensics/case037_mindfulness_app.yaml` | `f2686eb227a9a06697b5fe9e99843726200c27d5c2e7736b3680ddd58f3daa4e` |
| `case_library/case038_mediterranean_diet.yaml` | `tasks/study_forensics/case038_mediterranean_diet.yaml` | `f5b50289db0ee9dff9bab03c86fcd559745f1e0d890cf502504a8b3e845d1584` |
| `case_library/case039_nlp_benchmark.yaml` | `tasks/study_forensics/case039_nlp_benchmark.yaml` | `1747c32ff47c6a725be3c2c8e95a42f1119d7d39e1ed6a65a625f0a989ef76eb` |
| `case_library/case040_vocational_training.yaml` | `tasks/study_forensics/case040_vocational_training.yaml` | `48e9612037de2a4a85ddaaf2b7eb17ea977b8577276f93a15e562acf70dae6ff` |
| `case_library/case041_glp1_aleniglipron.yaml` | `tasks/study_forensics/case041_glp1_aleniglipron.yaml` | `91c71b1b1aa53304329b2fb0be8e5ecdaa6bf05a8cf7190a12f76272b5d66bba` |
| `case_library/case042_edge_ai_energy_blind_spot.yaml` | `tasks/study_forensics/case042_edge_ai_energy_blind_spot.yaml` | `b060b9b3463b71ccd5ae2c07b38bb6b1f68b0a27b70b565e6d7256693d80063b` |
| `case_library/case043_cell_study_cancer_cure.yaml` | `tasks/study_forensics/case043_cell_study_cancer_cure.yaml` | `1d6562c039aabd520882cedb743aadc1d773161d0d6563584c77e8d03b752a98` |
| `case_library/case044_mice_memory_dementia.yaml` | `tasks/study_forensics/case044_mice_memory_dementia.yaml` | `9ef3fd280f068c7bc4a801a4c6ac98d055c5d76ceba244bd9b53bf3f8a084139` |
| `case_library/case045_inflammation_marker_heart.yaml` | `tasks/study_forensics/case045_inflammation_marker_heart.yaml` | `09c4ecaa838bd49afbaceda9f14a362fc976f2e206a2c7c26dd68c6bdaecb0db` |
| `case_library/case046_coffee_longevity_correlation.yaml` | `tasks/study_forensics/case046_coffee_longevity_correlation.yaml` | `922cf35b9146bb51b67572a91f6978c9f158c621dbf4e2cc3320c236bdb0be6a` |
| `case_library/case047_pilot_trial_broad_recommendation.yaml` | `tasks/study_forensics/case047_pilot_trial_broad_recommendation.yaml` | `d2f0d1003f3037348b8305943e18e72743a40a14a3e69b2a5d88de0ec3cc1ff6` |
| `case_library/case048_tumor_shrinkage_survival.yaml` | `tasks/study_forensics/case048_tumor_shrinkage_survival.yaml` | `7e56b3e119d77756ce4d8f5173f636464aac172bf3bdf865d5daf707256d2bc7` |
| `case_library/case049_no_adverse_events_safe.yaml` | `tasks/study_forensics/case049_no_adverse_events_safe.yaml` | `5bab835d423dc1e9997102b8d79f3e45ad03075f0ee0e25f72162d30601421ac` |
| `case_library/case050_clinically_proven_supplement.yaml` | `tasks/study_forensics/case050_clinically_proven_supplement.yaml` | `84f04276bc84ce4cd7e72b9dd28e38f292b262e4c865d9d96ab566bfd6edef3c` |
| `case_library/case051_fair_cautious_observational.yaml` | `tasks/study_forensics/case051_fair_cautious_observational.yaml` | `fecf16210bdbd9b7d1dd2c200d10f59bb8ecafd000e9dfc3385bd6d2577c0a15` |
| `case_library/case052_strong_rct_fair.yaml` | `tasks/study_forensics/case052_strong_rct_fair.yaml` | `496d0f04be49f2321258207748a5294d8b424e3fe59f4086b3c696d0f60312ab` |
| `case_library/case053_best_in_class_no_h2h.yaml` | `tasks/study_forensics/case053_best_in_class_no_h2h.yaml` | `040f424a240f9e58f035497e4fe7ccd5887905332a6bbed2f3422de753b77f97` |
| `case_library/case054_decorative_hedging_equivalence.yaml` | `tasks/study_forensics/case054_decorative_hedging_equivalence.yaml` | `608158152a646f7f5b226d104f2e669854d351849869827e0a51bbea59095cf0` |
| `case_library/case055_short_followup_long_term.yaml` | `tasks/study_forensics/case055_short_followup_long_term.yaml` | `7251264b5463ba66ce3a5a91a100e0e006e322be21c8f9a9baf6e1d093a6f764` |
| `case_library/case056_subgroup_works_for_everyone.yaml` | `tasks/study_forensics/case056_subgroup_works_for_everyone.yaml` | `91453b096778ecaaaa5f4612477d9407ec7515c529af194bcfa63af182a58979` |
| `case_library/case057_relative_vs_absolute_risk.yaml` | `tasks/study_forensics/case057_relative_vs_absolute_risk.yaml` | `3f26caf280ed4ca67c96c2e7cc5940437b5acf6327a2f0309053369704a39cbb` |
| `case_library/case058_ai_beats_doctors_benchmark.yaml` | `tasks/study_forensics/case058_ai_beats_doctors_benchmark.yaml` | `bedb8b5e0aec25752fc4e3edc2104a81577c4b6d34b2e66fcf1ca00d940dfcfc` |
| `case_library/case059_ai_saves_energy_rebound.yaml` | `tasks/study_forensics/case059_ai_saves_energy_rebound.yaml` | `6e246a32a8cfbc90388566aca1a8e3bc69f6cbd43788f54e60ec30d95623d6bd` |
| `case_library/case060_synthetic_benchmark_real_world.yaml` | `tasks/study_forensics/case060_synthetic_benchmark_real_world.yaml` | `d41b32f38d453c8c9625c5f95d9ee7cd2409e63775ed48a56bd1a65df09eb0f1` |
| `case_library/case061_fully_autonomous_scripted.yaml` | `tasks/study_forensics/case061_fully_autonomous_scripted.yaml` | `a73a1fac20cb7446fc5e9fa11baff3b6b7c7865d611402b3eb0c2a63bec3f74c` |
| `case_library/case062_green_product_lifecycle.yaml` | `tasks/study_forensics/case062_green_product_lifecycle.yaml` | `ffcaf0042aa0c1dc904aebeceb47bb9e9b279cc1e1df46e7673ef87a4944b8f8` |
| `case_library/case063_policy_caused_improvement.yaml` | `tasks/study_forensics/case063_policy_caused_improvement.yaml` | `96b1735e78dd2fa5b165efb751483689b2e8401391caabdafa5d176894461caa` |
| `case_library/case_public_001_exercise_intensity.yaml` | `tasks/study_forensics/case_public_001_exercise_intensity.yaml` | `3478f17ef1843dc60fa767219a67ac077680da123c354e2d73e19111ff72ce9a` |
| `historical/live_smoke_20261011/live_run/authorization.json` | `analysis/live_smoke_20261011/live_run/authorization.json` | `49f8ba584f0e7ebef021a9d5c0d7f112d2434ed99f324e28d49e8169724e3b44` |
| `historical/live_smoke_20261011/live_run/ledger.json` | `analysis/live_smoke_20261011/live_run/ledger.json` | `e6ef0f5aff3b6bdd3c841fc0a5982449a83eecac004f73e42f9a19a66b0c64b5` |
| `historical/live_smoke_20261011/live_run/tasks/LS-01.json` | `analysis/live_smoke_20261011/live_run/tasks/LS-01.json` | `56a4d8315f60702b7813a607c3c29873b7a2d7e6932717a9ec8d5402a6dfb381` |
| `historical/live_smoke_20261011/live_run/tasks/LS-02.json` | `analysis/live_smoke_20261011/live_run/tasks/LS-02.json` | `fb2de29d129f2a1aad158f6bb30da160e2a0cb388e1924ef2b56389b3dbc8e37` |
| `historical/live_smoke_20261011/live_run/tasks/LS-03.json` | `analysis/live_smoke_20261011/live_run/tasks/LS-03.json` | `4521346818a0912f4152a80648b848e96c8afa5ff1f02dac48cbcbad29721bc2` |
| `historical/live_smoke_20261011/live_run/tasks/LS-04.json` | `analysis/live_smoke_20261011/live_run/tasks/LS-04.json` | `d128c28701ee978f897a875997e123160644c45d344350e04630dfcfab15e356` |
| `historical/live_smoke_20261011/live_run/tasks/LS-05.json` | `analysis/live_smoke_20261011/live_run/tasks/LS-05.json` | `26129e4700ee6da2cd45c98195180f462172d94dee7d4b51595e138c57e02d6d` |
| `historical/live_smoke_20261011/live_run/tasks/LS-06.json` | `analysis/live_smoke_20261011/live_run/tasks/LS-06.json` | `5b700333253f32f36961dcd5239514943aec825d2732b4acd9ed7d9573f217f4` |
| `historical/live_smoke_20261011/repair_r1/authorization.json` | `analysis/live_smoke_20261011/repair_r1/authorization.json` | `a8b5c90107c0e4e983eabdd903fdc7eafb5bad5bcb2314c35c66f3c9fd0293d3` |
| `historical/live_smoke_20261011/repair_r1/ledger.json` | `analysis/live_smoke_20261011/repair_r1/ledger.json` | `124ffab09ad94b9c751b50fe2888e48a2e585d41f16a6e21d2062d99e69497da` |
| `live_capture_attempt_010_final_text.json` | `analysis/live_smoke_20261011/repair_r1/captures/attempt-010.json` | `bb738ffe64796841a32ff77476f8cd42a34b6bb61cdf9ef35db82d971c43af0b` |
| `report_prototype/01_solid.json` | `analysis/phase6_3_report_prototype/fixtures/01_solid.json` | `a3ed16669da365189274479312cc9cb59cc1fa374603efe74b5157f2924c97c5` |
| `report_prototype/02_overclaim.json` | `analysis/phase6_3_report_prototype/fixtures/02_overclaim.json` | `0d46d90546143846447a17668a5efde8ddc4e221d849005772224553b1142b65` |
| `report_prototype/03_correlation_vs_causation.json` | `analysis/phase6_3_report_prototype/fixtures/03_correlation_vs_causation.json` | `1226ef27ce9322544adc82274a8779fc54e2a5b443dc6f0fcec5e9625fd81622` |
| `report_prototype/04_mechanism_vs_evidence.json` | `analysis/phase6_3_report_prototype/fixtures/04_mechanism_vs_evidence.json` | `8b1cbb8b546c2688c33ec9b6050ed7f4d2dff93abbf8de0185adf7651c9f59b7` |
| `report_prototype/05_missing_confidence.json` | `analysis/phase6_3_report_prototype/fixtures/05_missing_confidence.json` | `ade8f7c8b31ac08b316b9ef6cf6de6a8332bfb37c54ae4c961dbf0711c37287c` |
| `report_prototype/06_invalid_confidence.json` | `analysis/phase6_3_report_prototype/fixtures/06_invalid_confidence.json` | `c0516d8dc3e25d12bad8cf4f1aa42064aa8ae7ecd463b1d7beb0173259141e58` |
| `report_prototype/07_missing_evidence.json` | `analysis/phase6_3_report_prototype/fixtures/07_missing_evidence.json` | `9012639bd7a4fe55f86ed12438de47263fe1760040d79cd550499f26e52dd00e` |
| `report_prototype/08_parser_failure.json` | `analysis/phase6_3_report_prototype/fixtures/08_parser_failure.json` | `9f9e71a6e832407dad4f362cfe785f846740aa67ccb9b5df1e75ad3118aca42e` |
| `report_prototype/09_high_reader_impact.json` | `analysis/phase6_3_report_prototype/fixtures/09_high_reader_impact.json` | `3bf115960a76829e2e98707a44c8fa913212cafb9c3714f2a9916e46f667dd43` |
| `report_prototype/10_no_safe_rewrite.json` | `analysis/phase6_3_report_prototype/fixtures/10_no_safe_rewrite.json` | `e761242d38e1d6cb2c40ddb60082f2e2b743077bb3e9efbb8146d4b26974e024` |
| `report_prototype/11_multiple_failure_modes.json` | `analysis/phase6_3_report_prototype/fixtures/11_multiple_failure_modes.json` | `a82b0706f8c462c504a7b5e0568a2cdba692e88d0072a3345f1448769d610ddc` |
| `report_prototype/12_empty_evidence.json` | `analysis/phase6_3_report_prototype/fixtures/12_empty_evidence.json` | `a59bf0041ce5cd3786dd7f239038ca357de598f1526ed0497e6a6842ff4ff821` |
| `report_prototype/13_unsupported_superiority.json` | `analysis/phase6_3_report_prototype/fixtures/13_unsupported_superiority.json` | `9cf0407cb8e5ae738330a72ea1957f0997dc8c656a7ef3f498a13b53603cab91` |
| `report_prototype/14_missing_comparison_group.json` | `analysis/phase6_3_report_prototype/fixtures/14_missing_comparison_group.json` | `c3f09ec0188a0d0652a2ce39bde6e8ff242ef287d9edc09b53e7794e8a85b2c3` |
| `report_prototype/15_missing_causal_chain.json` | `analysis/phase6_3_report_prototype/fixtures/15_missing_causal_chain.json` | `e6c831692809edca31ab190d640ce98b848da38fad8872ff73374f9bbfcca704` |
| `robustness_cases/P7A-ADV-001.yaml` | `tasks/study_forensics_robustness/P7A-ADV-001.yaml` | `477ea9b71e55b17eabb8235c9247ebeaccfea6c788618cffb828c8b01bf60064` |
| `robustness_cases/P7A-ADV-002.yaml` | `tasks/study_forensics_robustness/P7A-ADV-002.yaml` | `ee427c1019940f97496be5d467c9f3587555b14eb6f4050844f69809d14975ec` |
| `robustness_cases/P7A-ADV-003.yaml` | `tasks/study_forensics_robustness/P7A-ADV-003.yaml` | `440be265bd47c6ed56617ffde31fecc39e103a1cf577f10c366b0963e6bb4ed6` |
| `robustness_cases/P7A-ADV-004.yaml` | `tasks/study_forensics_robustness/P7A-ADV-004.yaml` | `cf098bffe7cb8f280eb1c43f9229cf3bfcd7b7a1478a26c05697e8d39725e515` |
| `robustness_cases/P7A-ADV-005.yaml` | `tasks/study_forensics_robustness/P7A-ADV-005.yaml` | `1c3e77778d39f0f1b06d384805923baee3dcf7df9e155b35d3ce64f464f2da77` |
| `robustness_cases/P7A-ADV-006.yaml` | `tasks/study_forensics_robustness/P7A-ADV-006.yaml` | `e43f1b2d09757aa9b5ec4b485bd4620aba6a6e5de178b613324b220936eeacf6` |
| `robustness_cases/P7A-ADV-007.yaml` | `tasks/study_forensics_robustness/P7A-ADV-007.yaml` | `72e57f1818564e4f78cb33bfc930964acdfa20fd1d05cdd4b878018b5bf1d532` |
| `robustness_cases/P7A-ADV-008.yaml` | `tasks/study_forensics_robustness/P7A-ADV-008.yaml` | `71a9ffff0c34d2a54b1d35bca29f4999c29fd2d4fe892f8505362420ab266041` |
| `robustness_cases/P7A-ADV-009.yaml` | `tasks/study_forensics_robustness/P7A-ADV-009.yaml` | `02997b889bb711c9ea49f4abfcd2acb29aceca19a4e64a849f61e4469e22ec21` |
| `robustness_cases/P7A-ADV-010.yaml` | `tasks/study_forensics_robustness/P7A-ADV-010.yaml` | `bde86ff444c23735f777bc6d4c0c0a0bea2326d60d2450cf0e285d2e435353a9` |
| `robustness_cases/P7A-ADV-011.yaml` | `tasks/study_forensics_robustness/P7A-ADV-011.yaml` | `c6270a00ae0035ec4121e9b63004d85ac4ae814367f0e449a607937de7a73538` |
| `robustness_cases/P7A-ADV-012.yaml` | `tasks/study_forensics_robustness/P7A-ADV-012.yaml` | `b001d69833dd2e956ff0adba9718dc34da73ca5edf931b5d839d151630bc4b92` |
| `robustness_cases/P7A-ADV-013.yaml` | `tasks/study_forensics_robustness/P7A-ADV-013.yaml` | `13a4621d0a6e19394ac8ba17644075998fb2c268090f30d996bb9f5531ac752f` |
| `robustness_cases/P7A-ADV-014.yaml` | `tasks/study_forensics_robustness/P7A-ADV-014.yaml` | `823f0d25bed543523ae7a38b011e77e868e825f772e7a3fce17730ec8c18e96f` |
| `robustness_cases/P7A-ADV-015.yaml` | `tasks/study_forensics_robustness/P7A-ADV-015.yaml` | `225c6d0fa2af574a61a0ed3d2310eaf969f40aff9c3bfc353844afec44c9ce35` |
| `robustness_cases/P7A-ADV-016.yaml` | `tasks/study_forensics_robustness/P7A-ADV-016.yaml` | `fdc80b83599ace2d8e68d5eee03bf3c9136245fee2b1dc1362ef4201d08cef4f` |
| `robustness_cases/P7A-ADV-017.yaml` | `tasks/study_forensics_robustness/P7A-ADV-017.yaml` | `167e7f3af5b666b585e0e0c8f28d6d341ace800b6612255c1e8bb58b6ed89e11` |
| `robustness_cases/P7A-BND-001.yaml` | `tasks/study_forensics_robustness/P7A-BND-001.yaml` | `65f1503f6b72db9d15712a36fe77d853b87d85dfc653e7b6460215f1e047405f` |
| `robustness_cases/P7A-BND-002.yaml` | `tasks/study_forensics_robustness/P7A-BND-002.yaml` | `218a1a8ed9bb0e2542e960af62bd904c407d82d99830430b61dec90752230ca5` |
| `robustness_cases/P7A-BND-003.yaml` | `tasks/study_forensics_robustness/P7A-BND-003.yaml` | `2554bb905a185972ea9261ebae54b4b367ae0bcfa5eccfef716c4f7f64ebb0e4` |
| `robustness_cases/P7A-BND-004.yaml` | `tasks/study_forensics_robustness/P7A-BND-004.yaml` | `d2f28ad4ba437e5428ceff5ee6fb72015bc5fc5e8a3fc04b13406654adf277ec` |
| `robustness_cases/P7A-BND-005.yaml` | `tasks/study_forensics_robustness/P7A-BND-005.yaml` | `9a6f064ef6c805cb4238629245de7ed12714b6106816867fc643a838633c8b53` |
| `robustness_cases/P7A-BND-006.yaml` | `tasks/study_forensics_robustness/P7A-BND-006.yaml` | `1e7a85974d7fee1a48481ca70713cfee91ba8883856232992e258528712ba381` |
| `robustness_cases/P7A-BND-007.yaml` | `tasks/study_forensics_robustness/P7A-BND-007.yaml` | `b306c015286a553825a0d4d8375ebef1b36c1a0c372999d3cd5b26ac6d69d1a2` |
| `robustness_cases/P7A-BND-008.yaml` | `tasks/study_forensics_robustness/P7A-BND-008.yaml` | `78a68b830093dc3b7e06df1cfc71e8f81823ac806cba5aaa07ec173ca0599b53` |
| `robustness_cases/P7A-BND-009.yaml` | `tasks/study_forensics_robustness/P7A-BND-009.yaml` | `4551f7c839d8b2324a0dd01d070d165c952170b12a465ac14c319dcbe887cfde` |
| `robustness_cases/P7A-BND-010.yaml` | `tasks/study_forensics_robustness/P7A-BND-010.yaml` | `ad5a0dbf9780bad0a60399a1526bd0820fc341a8fc82f754578c5e673653f6ae` |
| `robustness_cases/P7A-BND-011.yaml` | `tasks/study_forensics_robustness/P7A-BND-011.yaml` | `2a00d690030ba8ad129b6092981210a550d657b2b477b969201c56d924131eb4` |
| `robustness_cases/P7A-BND-012.yaml` | `tasks/study_forensics_robustness/P7A-BND-012.yaml` | `562d0e4881c64788caa990eb74ecac8b9d11e94572aaf0fe817ac828031ac64f` |
| `robustness_cases/P7A-BND-013.yaml` | `tasks/study_forensics_robustness/P7A-BND-013.yaml` | `015ca67a41dce99cf5c04f040ed83fa6e05f0f682b8869f31e71d77374cc1440` |
| `robustness_cases/P7A-BND-014.yaml` | `tasks/study_forensics_robustness/P7A-BND-014.yaml` | `7e21f91886e38e58c91c95474ff837ee81383c5c31eb76735f7f040694151d1c` |
| `robustness_cases/P7A-BND-015.yaml` | `tasks/study_forensics_robustness/P7A-BND-015.yaml` | `63a6c88f565ece123581d596850c11c2baccaf853d6ad7d23b98176a8791580c` |
| `robustness_cases/P7A-BND-016.yaml` | `tasks/study_forensics_robustness/P7A-BND-016.yaml` | `0bbb47716685ca9bb477ac21a88b04ef4730f8f5ab801e5c0e27ef0cb3a5beea` |
| `robustness_cases/P7A-BND-017.yaml` | `tasks/study_forensics_robustness/P7A-BND-017.yaml` | `17c2b21bc0aafcc62975fe84b9e483c1686946729b7c69705791d224c58faf22` |
| `robustness_cases/P7A-BND-018.yaml` | `tasks/study_forensics_robustness/P7A-BND-018.yaml` | `db59866778ee2ce8f1939e2c58f72a975675608d153700665d3edb2cd61dc81e` |
| `robustness_cases/P7A-NEU-001.yaml` | `tasks/study_forensics_robustness/P7A-NEU-001.yaml` | `ebb33c4a771a07a12ce02bf25aca6158a19dd258d14025190bd2a303a079781a` |
| `robustness_cases/P7A-NEU-002.yaml` | `tasks/study_forensics_robustness/P7A-NEU-002.yaml` | `315cb13e37b00a82ee27f3d1c7345f250bf582d3b1f67a98a9da79fca80f93f4` |
| `robustness_cases/P7A-NEU-003.yaml` | `tasks/study_forensics_robustness/P7A-NEU-003.yaml` | `a2de65ebb7289a7564afbda1d39681856604cd2bf230a3d49ece692a0291aa58` |
| `robustness_cases/P7A-NEU-004.yaml` | `tasks/study_forensics_robustness/P7A-NEU-004.yaml` | `8da3f25a8f28d35e680016706db2c6d231e47100ded057b10be8d372a9755556` |

The remaining files (`workflow/`, `review/`, `pipeline_qa/` and
`synthetic_study_forensics_pilot_responses.json`) were moved unchanged from the runtime's own
test fixtures.
