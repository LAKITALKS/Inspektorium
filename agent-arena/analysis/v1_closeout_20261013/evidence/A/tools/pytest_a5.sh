#!/bin/bash
# A5: existing tests proving zero additional generation on resume/replay (synthetic authorizations in tmp, MockTransport).
cd __LOCAL_HOME__/Documents/Projects/agent-arena
set -x
env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/v1/evidence-A/tools .venv/bin/python -m pytest -p no:cacheprovider -p pytest_netguard_plugin --basetemp __LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/v1/evidence-A/pytest-a5 -v \
  tests/test_phase10_live.py::test_L7_counterreview_runs_live_on_trigger_and_noop_stability_generates_nothing \
  tests/test_phase10_live.py::test_L7_stability_variant_is_generated_live_when_the_reversal_is_real \
  tests/test_phase10_live.py::test_L7_auto_resolvable_case_uses_no_review_call \
  tests/test_phase10_live.py::test_L8_capture_persisted_before_crash_is_settled_on_resume \
  tests/test_phase10_live.py::test_crash_between_settlement_and_terminal_is_completed_on_resume \
  tests/test_phase10_live.py::test_round2_foreign_capture_does_not_settle_and_interrupted_retry_resumes \
  tests/test_phase10_live.py::test_M2_existing_capture_is_never_overwritten \
  tests/test_phase10_live.py::test_L1_replay_reuses_capture_without_any_network_call \
  tests/test_phase10_live.py::test_L1_offline_run_and_inspect_send_nothing_and_keep_offline_contract \
  tests/test_phase10_live.py::test_review_cap_decision_is_recorded_before_the_request_and_replayed_exactly \
  tests/test_phase10_live.py::test_replay_from_a_copy_keeps_a_never_executed_mandatory_review_open \
  tests/test_phase10_live.py::test_an_interrupted_live_review_replays_as_an_open_review_with_a_bundle \
  tests/test_v1_semantics.py::test_a_second_authorization_with_a_shared_review_state_is_refused_before_any_request
