# Migrating from 0.2.0 to 0.3.0

Inspektorium 0.3.0 is one distribution, `inspektorium`, with one command, `inspektorium`.
The second distribution `agent-arena` (package `agent_arena`, command `agent-arena`) no longer exists.
There is no compatibility shim. Evaluation behavior is unchanged; the [behavior comparison](#behavior-comparison-with-020) below shows the measured differences.

## Install

| 0.2.0 | 0.3.0 |
| --- | --- |
| `python -m pip install . ./agent-arena` | `python -m pip install .` |
| `inspektorium-0.2.0-py3-none-any.whl` and `agent_arena-1.0.2-py3-none-any.whl` | `inspektorium-0.3.0-py3-none-any.whl` |
| `agent-arena[providers]` | `inspektorium[providers]` (the extra `anthropic` stays as an alias) |

Uninstall the old runtime from an existing environment with `python -m pip uninstall agent-arena`.

## Commands

| 0.2.0 | 0.3.0 |
| --- | --- |
| `inspektorium audit …` or `agent-arena audit …` | `inspektorium audit …` (validate, run, inspect, review, release) |
| `inspektorium inspect …` | `inspektorium inspect …` (unchanged) |
| Other `agent-arena` commands (`run`, `report`, `client-report`, `forensic-report`, `official-release`, `audit-log`, study commands) | Removed; their code is in the [research record](../research/history.md#research-record) |

Options, exit codes and printed status values of `inspektorium audit` are unchanged.

## Python imports

The audit runtime is the subpackage `inspektorium.audit`, grouped by responsibility.
Modules that the audit command does not reach left the package with their tests.

| 0.2.0 module | 0.3.0 module |
| --- | --- |
| `inspektorium.audit` (launcher module `src/inspektorium/audit.py`) | `inspektorium.cli.run_audit` |
| `agent_arena.agent_loader` | `inspektorium.audit.execution.agent_loader` |
| `agent_arena.artifact_binding` | `inspektorium.audit.integrity.artifact_binding` |
| `agent_arena.audit_trail` | `inspektorium.audit.integrity.audit_trail` |
| `agent_arena.bounded_harness_mission`: `MissionError`, `read`, `atomic`, `BudgetLedger`, `MAX_ATTEMPT_MICROUSD`, `MAX_TOTAL_MICROUSD` | `inspektorium.audit.integrity.budget_ledger` (verbatim) |
| `agent_arena.claim_checker` | `inspektorium.audit.checks.claim_checker` |
| `agent_arena.confidence_validity` | `inspektorium.audit.checks.confidence_validity` |
| `agent_arena.consistency` | `inspektorium.audit.checks.consistency` |
| `agent_arena.evaluator` | `inspektorium.audit.execution.evaluator` |
| `agent_arena.forecast_checker` | `inspektorium.audit.checks.forecast_checker` |
| `agent_arena.forensic_report` | `inspektorium.audit.forensics.forensic_report` |
| `agent_arena.output_contract` | `inspektorium.audit.integrity.output_contract` |
| `agent_arena.phase10_bundle` | `inspektorium.audit.workflow.bundle` |
| `agent_arena.phase10_cli` | `inspektorium.audit.cli` |
| `agent_arena.phase10_live` | `inspektorium.audit.workflow.live` |
| `agent_arena.phase10_models` | `inspektorium.audit.workflow.models` |
| `agent_arena.phase10_pipeline` | `inspektorium.audit.workflow.pipeline` |
| `agent_arena.phase10_projection` | `inspektorium.audit.workflow.projection` |
| `agent_arena.phase10_render` | `inspektorium.audit.workflow.render` |
| `agent_arena.phase8_models` | `inspektorium.audit.forensics.models` |
| `agent_arena.phase8_pipeline` | `inspektorium.audit.forensics.pipeline` |
| `agent_arena.phase8_semantics` | `inspektorium.audit.forensics.semantics` |
| `agent_arena.phase8_taxonomy` | `inspektorium.audit.forensics.taxonomy` |
| `agent_arena.phase9_adjudication` | `inspektorium.audit.review.adjudication` |
| `agent_arena.phase9_models` | `inspektorium.audit.review.models` |
| `agent_arena.phase9_pipeline` | `inspektorium.audit.review.pipeline` |
| `agent_arena.phase9_review` | `inspektorium.audit.review.routing` |
| `agent_arena.phase9_runtime` | `inspektorium.audit.review.runtime` |
| `agent_arena.reasoning_graph` | `inspektorium.audit.checks.reasoning_graph` |
| `agent_arena.release_boundary` | `inspektorium.audit.integrity.release_boundary` |
| `agent_arena.reporter` | `inspektorium.audit.reports.reporter` |
| `agent_arena.reporting` | `inspektorium.audit.reports.reporting` |
| `agent_arena.run_library` | `inspektorium.audit.execution.run_library` |
| `agent_arena.runner` | `inspektorium.audit.execution.runner` |
| `agent_arena.step_checker` | `inspektorium.audit.checks.step_checker` |
| `agent_arena.study_forensics_checker` | `inspektorium.audit.checks.study_forensics_checker` |
| `agent_arena.task_loader` | `inspektorium.audit.execution.task_loader` |
| `agent_arena.schemas` | `inspektorium.audit.schemas` |
| `agent_arena.providers.*` | `inspektorium.audit.providers.*` |
| `agent_arena.bounded_harness_continuation` | research record (not shipped) |
| `agent_arena.bounded_harness_mission` (rest of the module) | research record (not shipped) |
| `agent_arena.calibrate` | research record (not shipped) |
| `agent_arena.calibration` | research record (not shipped) |
| `agent_arena.caseforge` | research record (not shipped) |
| `agent_arena.cli` | research record (not shipped) |
| `agent_arena.condition_analysis` | research record (not shipped) |
| `agent_arena.condition_contract` | research record (not shipped) |
| `agent_arena.condition_retry` | research record (not shipped) |
| `agent_arena.dev_manifest` | research record (not shipped) |
| `agent_arena.disagreement_lab` | research record (not shipped) |
| `agent_arena.full_replication_analysis` | research record (not shipped) |
| `agent_arena.full_replication_contract` | research record (not shipped) |
| `agent_arena.iaa_analysis` | research record (not shipped) |
| `agent_arena.insights` | research record (not shipped) |
| `agent_arena.journal` | research record (not shipped) |
| `agent_arena.judge` | research record (not shipped) |
| `agent_arena.local_historical_verification` | research record (not shipped) |
| `agent_arena.packet_integrity` | research record (not shipped) |
| `agent_arena.pattern_analyzer` | research record (not shipped) |
| `agent_arena.phase7a_execution` | research record (not shipped) |
| `agent_arena.phase7a_real_run` | research record (not shipped) |
| `agent_arena.pipeline` | research record (not shipped) |
| `agent_arena.postmortem` | research record (not shipped) |
| `agent_arena.preflight_integrity` | research record (not shipped) |
| `agent_arena.prompt_only_baseline` | research record (not shipped) |
| `agent_arena.provision_dev_manifest` | research record (not shipped) |
| `agent_arena.resume_integrity` | research record (not shipped) |
| `agent_arena.robustness_pool` | research record (not shipped) |
| `agent_arena.router` | research record (not shipped) |
| `agent_arena.runtime_contract` | research record (not shipped) |

## Names in outputs and identifiers

Generated reports, help texts and identifiers name Inspektorium. These string values changed:

| Where | 0.2.0 | 0.3.0 |
| --- | --- | --- |
| Bundle field `package_version` | version of `agent-arena` (1.0.2) | version of `inspektorium` (0.3.0) |
| Review notice in audit reports | `(agent-arena audit review)` | `(inspektorium audit review)` |
| Release-boundary schema identifiers | `agent_arena.release_source/v1`, `agent_arena.release_object/v1`, `agent_arena.official_release/v1`, `agent_arena.official_release_manifest/v1` and their `v2-condition-aware` variants | the same with prefix `inspektorium.audit.` |
| Release report and gate set | `agent_arena.phase7b_release_report/v2`, `agent_arena.phase7b.mandatory` | `inspektorium.audit.phase7b_release_report/v2`, `inspektorium.audit.phase7b.mandatory` |
| Official artifact role and namespace | `official_agent_arena_release`, `official-agent-arena-releases` | `official_inspektorium_release`, `official-inspektorium-releases` |
| Release staging directory prefix | `.agent-arena-release-staging-` | `.inspektorium-release-staging-` |
| Audit-trail default directory | `.agent_arena` | `.inspektorium` |
| Diagnostic report texts | `Agent Arena …` | `Inspektorium …` |
| Recorded-capture derivation schema (`scripts/extract_recorded_capture.py`) | `agent-arena-offline-capture-derivation/1.0` | `inspektorium-offline-capture-derivation/1.0` |
| Provider install hint | `pip install 'agent-arena[providers]'` | `pip install 'inspektorium[providers]'` |
| `run_library` program name | `agent_arena.run_library` | `inspektorium.audit.execution.run_library` |

These stay unchanged on purpose:

- control and data field names in bundles and records, such as `phase8`, `phase9`, `phase9_history_review` and `phase8_semantics_taxonomy`;
- status values, exit codes, gate versions, contract identifiers (`AA-P8/1.0`, `AA-P9/1.3`, `AA-P10/1.0`) and profile identifiers;
- prompt versions and prompt bytes. One model docstring in `inspektorium.audit.schemas` keeps the former product name. Its model's JSON schema is embedded in the frozen live prompt `study_forensics_prompt/v3-phase8`, and the live profiles bind that prompt's SHA-256;
- `src/inspektorium/core/` and `src/inspektorium/report/` (byte-identical), and the report schema 0.1 of `inspect`.

## Historical bundles and evidence

Audit bundles bind the module paths and bytes of the installation that produced them.
0.3.0 does not verify bundles produced by 0.2.0 or earlier.
Check them with the release that produced them; [history](../research/history.md) lists the releases and install commands.

## Tests

| Measurement at the source commit | Tests |
| --- | ---: |
| `d086973` (0.2.0 line): root suite plus audit-runtime suite | 3923 |
| 0.3.0: one suite under `tests/` | 2840 |
| Moved to the research record | 1083 |

Counts are collected tests (`pytest --collect-only`) at the two states.
The research record keeps every archived test with the module it tests.

Whole test files moved to the research record, with their subject:

| Test file (0.2.0) | Tests | Subject (archived) |
| --- | ---: | --- |
| `test_authorization_state_invariant.py` | 30 | authorization state of the study harness (`phase7a_real_run`) |
| `test_bounded_harness_continuation.py` | 4 | bounded study harness (`bounded_harness_continuation`) |
| `test_bounded_harness_mission.py` | 21 | bounded study harness (`bounded_harness_mission`) and its analysis script |
| `test_calibrate.py` | 40 | `calibrate` |
| `test_calibration.py` | 35 | `calibration` |
| `test_case_library.py` | 16 | consistency of the research case library and its document (research material) |
| `test_caseforge.py` | 43 | `caseforge` |
| `test_condition_analysis_contract.py` | 23 | study condition analysis (`condition_analysis`, `phase7a_real_run`) |
| `test_condition_contract.py` | 26 | `condition_contract`; one release-boundary test moved to `tests/unit/test_release_boundary.py` |
| `test_dev_manifest.py` | 17 | `dev_manifest` |
| `test_disagreement_lab.py` | 56 | `disagreement_lab` |
| `test_e2e_meta_stack.py` | 55 | chain of `calibrate`, `caseforge`, `disagreement_lab`, `insights`, `journal`, `router` |
| `test_full_replication_contract.py` | 12 | full-replication study contract (`full_replication_contract`) |
| `test_h1_s1_controlled_comparison.py` | 7 | study comparison (`condition_contract`, `full_replication_contract`, `phase7a_execution`, `runtime_contract`) |
| `test_iaa_analysis.py` | 20 | `iaa_analysis` |
| `test_insights.py` | 53 | `insights` |
| `test_journal.py` | 42 | `journal` |
| `test_judge.py` | 4 | `judge` |
| `test_judge_parser.py` | 10 | `judge` |
| `test_local_historical_verification.py` | 4 | `local_historical_verification` |
| `test_monorepo_plan_binding.py` | 6 | plan binding of `condition_contract` |
| `test_packet_integrity.py` | 19 | `packet_integrity` |
| `test_pattern_analyzer.py` | 24 | `pattern_analyzer` |
| `test_phase6_4_paired_comparison.py` | 10 | Phase 6.4 analysis script (research record) |
| `test_phase7a_adversarial_pool.py` | 22 | study pool (`robustness_pool`) |
| `test_phase7a_boundary_pool.py` | 21 | study pool (`robustness_pool`) |
| `test_phase7a_cli_exit.py` | 12 | study execution (`phase7a_execution`) |
| `test_phase7a_execution.py` | 53 | study execution (`phase7a_execution`, `preflight_integrity`, `robustness_pool`) |
| `test_phase7a_perturbation_pool.py` | 27 | study pool (`robustness_pool`) |
| `test_phase7a_real_run.py` | 28 | study execution (`phase7a_real_run`) |
| `test_pipeline.py` | 38 | `pipeline`, `journal` |
| `test_postmortem.py` | 21 | `postmortem` |
| `test_preflight_integrity.py` | 44 | `preflight_integrity` |
| `test_prompt_only_baseline.py` | 52 | `prompt_only_baseline` and its study protocol |
| `test_provision_dev_manifest.py` | 15 | `provision_dev_manifest`, `dev_manifest` |
| `test_reproduction_guard_counter.py` | 2 | clean-reproduction script (research record) |
| `test_resume_integrity.py` | 38 | `resume_integrity` |
| `test_router.py` | 36 | `router` |
| `test_runtime_contract.py` | 30 | `runtime_contract` and its study freeze |
| `test_sonnet_authorization_state_invariant.py` | 24 | replication authorization state (`phase7a_real_run`) |
| `test_sonnet_full_replication_registration.py` | 19 | replication registration through the legacy CLI (`cli`) |

| Test file (0.2.0) | Removed tests | 0.3.0 file | Removed subject |
| --- | ---: | --- | --- |
| `test_package_b_regressions.py` | 4 | `tests/unit/test_package_b_regressions.py` | four tests of `phase7a_execution`, `phase7a_real_run` and `full_replication_contract` (P1 frozen record, P5, BF6, BF8); P1 and BF4 stay without their `phase7a_execution` assertion |
| `test_release_boundary.py` | 6 | `tests/unit/test_release_boundary.py` | legacy CLI commands `client-report`, `report`, `forensic-report`; two tests keep their API part |
| `test_v1_entry_point.py` | 14 | `tests/integration/test_workflow_entry.py` | root help, command help and disabled commands of the legacy CLI |

Two kinds of tests were kept although their files changed:

- `test_P1_a_second_analysis_is_flagged_and_never_a_complete_phase8_analysis` (eight cases) and `test_BF4_the_library_harness_records_a_second_analysis` keep every assertion on retained code. That covers the parser, the Phase-8 assessment, reconstruction and `run_library`. Only the classification check of the archived study harness was dropped.
- `test_R_validation_artifact_role_is_not_a_supported_release_source` moved from the archived condition-contract tests to `tests/unit/test_release_boundary.py`.

No expectation on a status, exit code, rejection, lock or binding was changed.

## Name check exceptions

`git grep -n -i -E "agent[ _-]arena"` finds the former name in this page, in [history](../research/history.md), in historical `CHANGELOG.md` entries and in one `NOTICE` sentence.
It also finds it in files that are bound to earlier bytes or that compare with release 0.2.0:

| File | Why the name stays |
| --- | --- |
| `tests/fixtures/audit/historical/live_smoke_20261011/*/authorization.json` | Closed historical authorizations; their SHA-256 values are pinned in `inspektorium.audit.workflow.live` |
| `tests/fixtures/audit/historical/public_archive_bindings.json` | Verbatim extract of the research record's import index; its paths name the record's folders |
| `src/inspektorium/audit/schemas.py` (one docstring) | Embedded in the frozen live prompt `study_forensics_prompt/v3-phase8` |
| `evidence/v0.1.1/addendum-20261024-e1-layout/` (two lines) | The v0.1.1 evidence package stays unchanged |
| `evidence/v0.3.0-behavior/` (maps, environment record, logic diff and the comparison tools) | The package compares 0.3.0 with the 0.2.0 release, whose paths, wheel and identifiers carry the former name |

## Behavior comparison with 0.2.0

The published 0.2.0 wheels and the 0.3.0 candidate were recorded with the same 79-step script, twice each, offline and under the Python network guard.
The method, tools and results are in the evidence package [`v0.3.0-behavior`](../../evidence/v0.3.0-behavior/README.md).

| Check | Result |
| --- | --- |
| `inspect` output of the five examples, JSON and Markdown, standard output and `--output` | byte-identical (20 and 10 steps) |
| `audit` statuses and exit codes of validate, run, inspect, review and release for four cases | identical (35 steps) |
| Findings, review obligations, release ability and bundle contents, after masking | identical (all 79 projected steps) |
| Counter-checks: tampered report and record, live run without authorization, missing and conflicting mode, duplicate JSON keys, unknown command | identical outcomes |

Two kinds of differences remain before masking, and both are allowed:

- **Module-hash manifest.** Reports show the number of bound runtime modules: 74 in 0.2.0, 51 in 0.3.0. The module hashes themselves differ because files moved and were renamed.
- **Position order.** Reports list review positions sorted by a position ID that hashes the random run ID. Their order varies between runs of either release; the 0.2.0 baseline recordings happened to share one order.

Names and versions in outputs differ as listed under [names in outputs](#names-in-outputs-and-identifiers).
The audit-runtime logic is unchanged apart from those names: 27 of 42 modules have identical code without imports and docstrings, and the others differ only in the changes this page lists.
