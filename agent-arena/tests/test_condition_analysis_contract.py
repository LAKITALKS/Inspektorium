"""Focused offline proof for Phase-5A aggregation, verdict, and retry accounting."""

from __future__ import annotations

import json
from pathlib import Path

import anthropic
import httpx
import pytest

from agent_arena import condition_analysis as ca
from agent_arena import condition_contract as cc
from agent_arena import condition_retry as cr
from agent_arena import phase7a_execution as p7
from agent_arena import resume_integrity as ri
from agent_arena.phase7a_real_run import _CaptureProvider, execute_model_records
from agent_arena.providers.anthropic import AnthropicProvider


REPO_ROOT = Path(__file__).resolve().parents[1]
MODEL_IDS = ["model-a", "model-b"]
PRIMARY_IDS = [f"PRIMARY-{index:02d}" for index in range(8)]
CONTROL_IDS = [f"CONTROL-{index:02d}" for index in range(11)]
UNIT_BINDINGS = [
    {"unit_id": unit_id, "gold_label": "solid"}
    for unit_id in PRIMARY_IDS + CONTROL_IDS
]
UNIT_STRATA = [
    {"stratum_id": "primary", "unit_ids": PRIMARY_IDS},
    {"stratum_id": "controls", "unit_ids": CONTROL_IDS},
]
ANALYSIS_CONTRACT = ca.build_analysis_contract(
    primary_stratum_ids=["primary"],
    control_stratum_ids=["controls"],
    expected_primary_units=8,
    expected_control_units=11,
    n_replications=3,
)


def _record(
    model: str,
    unit_id: str,
    run_index: int,
    label: str | None,
    *,
    confidence: object = 0.8,
    confidence_state: str = "VALID",
    parse_ok: bool = True,
    error: str | None = None,
    error_type: str | None = None,
) -> dict:
    return {
        "model": model,
        "unit_id": unit_id,
        "run_index": run_index,
        "gold_label": "solid",
        "label": label,
        "confidence": confidence,
        "confidence_state": confidence_state,
        "parse_ok": parse_ok,
        "finish_reason": "error" if error else "stop",
        "truncation_suspected": False,
        "error": error,
        "error_type": error_type,
    }


def _single_population_analysis(records: list[dict], *, units: int = 1) -> dict:
    unit_ids = [f"UNIT-{index:02d}" for index in range(units)]
    bindings = [{"unit_id": unit_id, "gold_label": "solid"} for unit_id in unit_ids]
    strata = [{"stratum_id": "primary", "unit_ids": unit_ids}]
    contract = ca.build_analysis_contract(
        primary_stratum_ids=["primary"],
        control_stratum_ids=[],
        expected_primary_units=units,
        expected_control_units=0,
        n_replications=3,
    )
    return ca.build_arm_model_analysis(
        records,
        ordered_unit_bindings=bindings,
        unit_strata=strata,
        analysis_contract=contract,
        model="model-a",
        arm_id="arm",
    )


def _analysis(
    model: str,
    arm: str,
    *,
    primary_correct: int,
    control_correct: int,
    unresolved_unit: str | None = None,
    invalid_confidence_unit: str | None = None,
    missing_third_unit: str | None = None,
) -> dict:
    records = []
    for position, unit_id in enumerate(PRIMARY_IDS + CONTROL_IDS):
        correct_limit = primary_correct if unit_id in PRIMARY_IDS else control_correct
        population_position = position if unit_id in PRIMARY_IDS else position - len(PRIMARY_IDS)
        labels = ["solid"] * 3 if population_position < correct_limit else ["overclaim"] * 3
        if unit_id == unresolved_unit:
            labels = ["solid", "overclaim", "mechanism_vs_evidence"]
        for run_index, label in enumerate(labels):
            if unit_id == missing_third_unit and run_index == 2:
                continue
            kwargs = {}
            if unit_id == invalid_confidence_unit and run_index == 0:
                kwargs = {"confidence": 2.0, "confidence_state": "INVALID"}
            records.append(_record(model, unit_id, run_index, label, **kwargs))
    return ca.build_arm_model_analysis(
        records,
        ordered_unit_bindings=UNIT_BINDINGS,
        unit_strata=UNIT_STRATA,
        analysis_contract=ANALYSIS_CONTRACT,
        model=model,
        arm_id=arm,
    )


def _paired(
    scores: dict[str, tuple[int, int, int, int]],
    *,
    unresolved: tuple[str, str] | None = None,
    invalid_confidence: tuple[str, str] | None = None,
    missing_third: tuple[str, str] | None = None,
) -> dict:
    analyses = []
    for model in MODEL_IDS:
        old_primary, old_controls, new_primary, new_controls = scores[model]
        analyses.extend([
            _analysis(
                model,
                "old",
                primary_correct=old_primary,
                control_correct=old_controls,
            ),
            _analysis(
                model,
                "new",
                primary_correct=new_primary,
                control_correct=new_controls,
                unresolved_unit=(
                    unresolved[1] if unresolved and unresolved[0] == model else None
                ),
                invalid_confidence_unit=(
                    invalid_confidence[1]
                    if invalid_confidence and invalid_confidence[0] == model
                    else None
                ),
                missing_third_unit=(
                    missing_third[1]
                    if missing_third and missing_third[0] == model
                    else None
                ),
            ),
        ])
    return ca.build_paired_analysis(
        analyses,
        model_ids=MODEL_IDS,
        historical_arm_id="old",
        prospective_arm_id="new",
    )


def test_unanimous_and_two_matching_votes_resolve_while_missingness_remains_visible():
    records = [
        *[_record("model-a", "UNIT-00", index, "solid") for index in range(3)],
        _record("model-a", "UNIT-01", 0, "overclaim"),
        _record("model-a", "UNIT-01", 1, "overclaim"),
    ]
    report = _single_population_analysis(records, units=2)
    unanimous, majority = report["unit_results"]
    assert unanimous["resolution"] == "UNANIMOUS"
    assert unanimous["resolved_label"] == "solid"
    assert majority["resolution"] == "RESOLVED_MAJORITY"
    assert majority["resolved_label"] == "overclaim"
    assert majority["slot_accounting"]["missing_response_slots"] == 1
    assert report["classification_complete"] is True
    assert report["transport_missingness_complete"] is False


@pytest.mark.parametrize(
    "labels,expected_resolution",
    [
        (
            ["solid", "overclaim", "mechanism_vs_evidence"],
            "UNRESOLVED_THREE_WAY_TIE",
        ),
        (["solid", "overclaim", None], "UNRESOLVED_CONFLICTING_VALID_VOTES"),
        (["solid", None, None], "UNRESOLVED_INSUFFICIENT_VALID_VOTES"),
        ([None, None, None], "UNRESOLVED_INSUFFICIENT_VALID_VOTES"),
    ],
)
def test_unresolved_vote_states(labels, expected_resolution):
    records = [
        _record("model-a", "UNIT-00", index, label)
        for index, label in enumerate(labels)
        if label is not None
    ]
    result = _single_population_analysis(records)["unit_results"][0]
    assert result["resolved_label"] is None
    assert result["resolution"] == expected_resolution


def test_invalid_terminal_response_does_not_break_two_vote_resolution():
    records = [
        _record("model-a", "UNIT-00", 0, "solid"),
        _record("model-a", "UNIT-00", 1, "solid"),
        _record("model-a", "UNIT-00", 2, None, parse_ok=False),
    ]
    result = _single_population_analysis(records)["unit_results"][0]
    assert result["resolved_label"] == "solid"
    assert result["slot_accounting"]["classification_invalid_response_slots"] == 1


def test_invalid_confidence_preserves_label_vote_but_is_excluded_from_calibration():
    records = [
        _record(
            "model-a",
            "UNIT-00",
            0,
            "solid",
            confidence=2.0,
            confidence_state="INVALID",
        ),
        _record("model-a", "UNIT-00", 1, "solid"),
        _record("model-a", "UNIT-00", 2, "solid"),
    ]
    report = _single_population_analysis(records)
    population = report["populations"]["primary"]
    assert report["classification_complete"] is True
    assert report["calibration_complete"] is False
    assert population["classification_valid_response_slots"] == 3
    assert population["calibration_valid_response_slots"] == 2
    assert population["response_slot_accounting"][
        "invalid_or_missing_confidence_on_valid_classification_slots"
    ] == 1


def test_fixed_population_denominators_and_unresolved_accounting_are_explicit():
    report = _analysis(
        "model-a",
        "old",
        primary_correct=4,
        control_correct=9,
        unresolved_unit=PRIMARY_IDS[-1],
    )
    primary = report["populations"]["primary"]
    controls = report["populations"]["controls"]
    assert primary["expected_units"] == 8
    assert controls["expected_units"] == 11
    assert primary["expected_units"] == (
        primary["correct_resolved_units"]
        + primary["incorrect_resolved_units"]
        + primary["unresolved_units"]
    )
    assert primary["unresolved_units"] == 1
    assert primary["classification_metrics"]["coverage_adjusted_correct_unit_rate"] == {
        "numerator": 4,
        "denominator": 8,
        "value": 0.5,
        "unresolved_units_are_scientifically_incorrect": False,
    }
    assert primary["classification_metrics"]["resolved_unit_accuracy"]["denominator"] == 7


def test_response_accuracy_brier_and_fixed_bin_ece_use_exact_eligible_denominators():
    records = [
        _record("model-a", "UNIT-00", 0, "solid", confidence=0.1),
        _record("model-a", "UNIT-00", 1, "overclaim", confidence=0.9),
        _record("model-a", "UNIT-00", 2, "solid", confidence=0.5),
    ]
    population = _single_population_analysis(records)["populations"]["primary"]
    accuracy = population["classification_metrics"]["response_level_accuracy"]
    brier = population["calibration_metrics"]["brier_top_label"]
    ece = population["calibration_metrics"]["ece_5bin"]
    assert accuracy["numerator"] == 2 and accuracy["denominator"] == 3
    assert brier["denominator"] == 3
    assert brier["value"] == pytest.approx((0.9**2 + 0.9**2 + 0.5**2) / 3)
    assert ece["fixed_bin_edges"] == [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    assert ece["denominator"] == 3
    assert ece["value"] == pytest.approx((0.9 + 0.9 + 0.5) / 3)


def test_paired_transitions_exclude_unresolved_and_nondiscordant_units_from_sign_test():
    old = _analysis("model-a", "old", primary_correct=4, control_correct=11)
    new = _analysis(
        "model-a",
        "new",
        primary_correct=5,
        control_correct=11,
        unresolved_unit=PRIMARY_IDS[-1],
    )
    paired = ca._paired_population(old, new, "primary")
    reasons = {row["sign_test_exclusion_reason"] for row in paired["transitions"]}
    assert "unresolved label in one or both prompt arms" in reasons
    assert "both arms correct" in reasons
    assert "both arms incorrect" in reasons
    assert paired["sign_test"]["discordant_pairs"] == 1
    assert paired["sign_test"]["exact_two_sided_p_value"] == 1.0


@pytest.mark.parametrize(
    "scores,expected",
    [
        (
            {"model-a": (4, 11, 5, 10), "model-b": (3, 10, 4, 10)},
            ca.SUPPORTIVE_DIRECTIONAL,
        ),
        (
            {"model-a": (4, 11, 3, 11), "model-b": (3, 10, 4, 10)},
            ca.ADVERSE,
        ),
        (
            {"model-a": (4, 11, 5, 11), "model-b": (4, 11, 3, 11)},
            ca.ADVERSE,
        ),
        (
            {"model-a": (4, 11, 5, 9), "model-b": (3, 10, 4, 10)},
            ca.ADVERSE,
        ),
        (
            {"model-a": (4, 11, 5, 10), "model-b": (3, 10, 3, 10)},
            ca.INCONCLUSIVE,
        ),
    ],
)
def test_directional_verdicts_are_mutually_exclusive(scores, expected):
    result = _paired(scores)
    assert result["directional_verdict"] == expected
    for model in MODEL_IDS:
        rate = result["model_results"][model][
            "primary_coverage_adjusted_correct_unit_rate"
        ]
        assert rate["denominator"] == 8
        assert rate["difference"] == pytest.approx(
            result["model_results"][model]["primary_correct_unit_delta"] / 8
        )


def test_incomplete_classification_precedes_directional_rules():
    scores = {"model-a": (4, 11, 5, 11), "model-b": (3, 10, 4, 10)}
    result = _paired(scores, unresolved=("model-a", PRIMARY_IDS[-1]))
    assert result["directional_verdict"] == ca.INCONCLUSIVE_INCOMPLETE
    assert result["classification_complete"] is False


def test_incomplete_calibration_does_not_erase_complete_classification_verdict():
    scores = {"model-a": (4, 11, 5, 11), "model-b": (3, 10, 4, 10)}
    result = _paired(scores, invalid_confidence=("model-a", PRIMARY_IDS[0]))
    assert result["directional_verdict"] == ca.SUPPORTIVE_DIRECTIONAL
    assert result["classification_complete"] is True
    assert result["calibration_complete"] is False


def test_resolved_two_vote_result_reports_transport_missingness_separately():
    scores = {"model-a": (4, 11, 5, 11), "model-b": (3, 10, 4, 10)}
    result = _paired(scores, missing_third=("model-a", PRIMARY_IDS[0]))
    assert result["directional_verdict"] == ca.SUPPORTIVE_DIRECTIONAL
    assert result["classification_complete"] is True
    assert result["transport_missingness_complete"] is False


def test_retry_contract_separates_228_slots_684_provider_calls_and_2052_http_attempts():
    contract = cr.build_retry_contract(
        analytical_slots=228,
        guarded_batch_invocations=4,
        slots_per_batch=57,
    )
    schedule = contract["schedule"]
    assert schedule["provider_method_invocations_per_batch_max"] == 171
    assert schedule["provider_method_invocations_schedule_max"] == 684
    assert schedule["http_attempts_per_batch_max"] == 513
    assert schedule["http_attempts_schedule_max"] == 2052
    assert contract["persistent_cross_invocation_spending_cap_enforced"] is False
    assert contract["availability_probe_http_attempts_in_guarded_path"] == 0


def _source_binding() -> dict:
    return {
        "repository_identity": "repository-id",
        "commit": "a" * 40,
        "tree": "b" * 40,
        "tracked_source_fingerprint": "c" * 64,
        "tracked_config_fingerprint": "d" * 64,
        "python_environment_fingerprint": "e" * 64,
        "source_state_fingerprint": "f" * 64,
    }


def _retry_context(tmp_path):
    artifact = json.loads(
        (
            REPO_ROOT
            / "analysis/phase5a_scientific_contract/paired_prompt_validation_plan.json"
        ).read_text()
    )
    document = cc.build_plan_document(artifact["definition"], REPO_ROOT)
    arm = cc.resolve_arm(document, cc.PROSPECTIVE_ARM_ID)
    units = cc.units_for_plan(document, REPO_ROOT)[:1]
    contract = ri.build_condition_resume_contract(
        document,
        arm,
        "haiku",
        units,
        REPO_ROOT,
        execution_type=p7.EXEC_TYPE_DRY_RUN,
        dry_run=True,
        source_binding=_source_binding(),
        checkpoint_root=tmp_path,
    )
    return document, arm, units, contract


def _valid_message(text: str) -> dict:
    return {
        "id": "msg_test",
        "type": "message",
        "role": "assistant",
        "model": cc.rc.MODELS["haiku"]["exact_model_id"],
        "content": [{"type": "text", "text": text}],
        "stop_reason": "end_turn",
        "stop_sequence": None,
        "usage": {"input_tokens": 1, "output_tokens": 1},
    }


def _install_sdk_transport(monkeypatch, *, mode: str) -> dict:
    original_client = anthropic.Anthropic
    counter = {"provider_method_invocations": 0, "http_attempts": 0}
    valid_text = json.dumps({
        "final_answer": "solid",
        "evidence_tier": "clinical_human",
        "conclusion_tier": "same as evidence",
        "bridge_supported": True,
        "assumptions": [],
        "steps": ["offline synthetic response"],
        "alternative_hypotheses": [],
        "uncertainties": [],
        "key_claims": [],
        "self_check": [],
        "confidence": 0.8,
    })

    def factory(*, timeout, max_retries, http_client):
        # Production (AnthropicProvider.generate) constructs its own instrumented
        # httpx client and passes it explicitly. The synthetic factory mirrors that
        # signature and carries the production request hooks onto the mock-transport
        # client so the transport-attempt accounting under test stays production's.
        assert isinstance(http_client, httpx.Client)
        assert http_client.event_hooks["request"]
        counter["provider_method_invocations"] += 1
        request_attempt = 0

        def handler(request):
            nonlocal request_attempt
            request_attempt += 1
            counter["http_attempts"] += 1
            if mode == "exhaust" or (mode == "retry_then_success" and request_attempt < 3):
                return httpx.Response(
                    500,
                    request=request,
                    headers={"content-type": "application/json", "retry-after": "0"},
                    json={"type": "error", "error": {"type": "api_error", "message": "down"}},
                )
            text = "not-json" if mode == "semantic_failure" else valid_text
            return httpx.Response(
                200,
                request=request,
                headers={"content-type": "application/json"},
                json=_valid_message(text),
            )

        return original_client(
            api_key="offline-test-key",
            timeout=timeout,
            max_retries=max_retries,
            http_client=httpx.Client(
                transport=httpx.MockTransport(handler),
                event_hooks=http_client.event_hooks,
            ),
        )

    monkeypatch.setattr(anthropic, "Anthropic", factory)
    monkeypatch.setattr("anthropic._base_client.time.sleep", lambda _seconds: None)
    return counter


def _execute_one(arm, units, contract, *, existing=None):
    provider = _CaptureProvider(
        AnthropicProvider(model=cc.rc.MODELS["haiku"]["exact_model_id"])
    )
    records = execute_model_records(
        "haiku",
        units,
        provider,
        repo_root=REPO_ROOT,
        existing=existing,
        execution_type=p7.EXEC_TYPE_DRY_RUN,
        dry_run=True,
        max_passes=cr.PROVIDER_ERROR_PASSES_PER_GUARDED_INVOCATION,
        resume_contract=contract,
        condition_arm=arm,
        n_replications=1,
    )
    return records, provider


def test_real_sdk_transport_retry_then_success_uses_three_http_attempts_once(
    monkeypatch, tmp_path
):
    counter = _install_sdk_transport(monkeypatch, mode="retry_then_success")
    _document, arm, units, contract = _retry_context(tmp_path)
    records, provider = _execute_one(arm, units, contract)
    assert p7.is_classification_valid(records[0])
    assert len(provider.captures) == 1
    assert counter == {"provider_method_invocations": 1, "http_attempts": 3}


def test_sdk_exhaustion_exercises_three_outer_passes_and_nine_http_attempts(
    monkeypatch, tmp_path
):
    counter = _install_sdk_transport(monkeypatch, mode="exhaust")
    _document, arm, units, contract = _retry_context(tmp_path)
    records, provider = _execute_one(arm, units, contract)
    assert not p7.is_terminal_attempt(records[0])
    assert len(provider.captures) == 3
    assert counter == {"provider_method_invocations": 3, "http_attempts": 9}


def test_terminal_semantic_failure_receives_no_sdk_or_outer_semantic_retry(
    monkeypatch, tmp_path
):
    counter = _install_sdk_transport(monkeypatch, mode="semantic_failure")
    _document, arm, units, contract = _retry_context(tmp_path)
    records, provider = _execute_one(arm, units, contract)
    assert p7.is_terminal_attempt(records[0])
    assert not p7.is_classification_valid(records[0])
    assert len(provider.captures) == 1
    assert counter == {"provider_method_invocations": 1, "http_attempts": 1}


def test_later_guarded_invocation_resets_outer_pass_counter_for_nonterminal_checkpoint(
    monkeypatch, tmp_path
):
    counter = _install_sdk_transport(monkeypatch, mode="exhaust")
    _document, arm, units, contract = _retry_context(tmp_path)
    first, provider_one = _execute_one(arm, units, contract)
    second, provider_two = _execute_one(arm, units, contract, existing=first)
    assert not p7.is_terminal_attempt(second[0])
    assert len(provider_one.captures) == len(provider_two.captures) == 3
    assert counter == {"provider_method_invocations": 6, "http_attempts": 18}
