"""Deterministic analysis contract for the paired Phase-5A prompt conditions.

The implementation is deliberately narrow: three planned responses per unit,
two predeclared populations, fixed majority resolution, explicit missingness,
and a mutually exclusive directional verdict.  It reuses the existing Phase-1
classification/calibration predicates and the frozen calibration primitives.
"""

from __future__ import annotations

from collections import Counter
from math import comb

from agent_arena import calibration as cal
from agent_arena import phase7a_execution as p7


ANALYSIS_CONTRACT_SCHEMA_VERSION = "agent_arena.condition_analysis_contract/v1"
ANALYSIS_CONTRACT_ID = "AA-P5A-ANALYSIS-CONTRACT-001"
ARM_ANALYSIS_SCHEMA_VERSION = "agent_arena.condition_analysis/v2"
PAIRED_ANALYSIS_SCHEMA_VERSION = "agent_arena.condition_paired_analysis/v1"

INCONCLUSIVE_INCOMPLETE = "INCONCLUSIVE_INCOMPLETE"
ADVERSE = "ADVERSE"
SUPPORTIVE_DIRECTIONAL = "SUPPORTIVE_DIRECTIONAL"
INCONCLUSIVE = "INCONCLUSIVE"


class ConditionAnalysisError(ValueError):
    """The prospective analysis inputs or frozen contract are inconsistent."""


def build_analysis_contract(
    *,
    primary_stratum_ids: list[str],
    control_stratum_ids: list[str],
    expected_primary_units: int,
    expected_control_units: int,
    n_replications: int,
) -> dict:
    """Build the complete executable policy embedded in the registered plan."""
    return {
        "analysis_contract_schema_version": ANALYSIS_CONTRACT_SCHEMA_VERSION,
        "analysis_contract_id": ANALYSIS_CONTRACT_ID,
        "implementation": "agent_arena.condition_analysis",
        "classification_predicate": (
            "agent_arena.phase7a_execution.is_classification_valid"
        ),
        "calibration_predicate": "agent_arena.phase7a_execution.is_calibration_valid",
        "aggregation": {
            "planned_votes_per_unit": n_replications,
            "vote_eligibility": "classification-valid responses only",
            "resolved_label_requirement": "at least 2 matching valid labels",
            "two_matching_plus_missing_or_invalid": "RESOLVED",
            "three_different_valid_labels": "UNRESOLVED",
            "two_conflicting_valid_plus_missing_or_invalid": "UNRESOLVED",
            "one_or_zero_valid_responses": "UNRESOLVED",
            "invalid_confidence_effect_on_label_vote": "NONE",
            "gold_access_order": "after label aggregation, for scoring only",
            "tie_breakers": {
                "gold": "PROHIBITED",
                "confidence": "PROHIBITED",
                "response_order": "PROHIBITED",
                "model_preference": "PROHIBITED",
            },
            "retain_raw_labels_and_validity_states": True,
        },
        "populations": {
            "primary": {
                "stratum_ids": list(primary_stratum_ids),
                "expected_units_per_model_arm": expected_primary_units,
            },
            "controls": {
                "stratum_ids": list(control_stratum_ids),
                "expected_units_per_model_arm": expected_control_units,
            },
        },
        "population_accounting": {
            "required_fields": [
                "expected_units",
                "resolved_units",
                "correct_resolved_units",
                "incorrect_resolved_units",
                "unresolved_units",
                "classification_valid_response_slots",
                "calibration_valid_response_slots",
                "missing_invalid_error_slots",
            ],
            "unit_invariant": (
                "expected_units = correct_resolved_units + "
                "incorrect_resolved_units + unresolved_units"
            ),
        },
        "classification_metrics": {
            "coverage_adjusted_correct_unit_rate": {
                "numerator": "correct_resolved_units",
                "denominator": "fixed expected_units",
                "unresolved_treatment": "retained in denominator; not called incorrect",
            },
            "resolved_unit_accuracy": {
                "numerator": "correct_resolved_units",
                "denominator": "resolved_units",
            },
            "response_level_accuracy": {
                "eligibility": "is_classification_valid(response)",
                "numerator": "eligible responses whose label equals gold",
                "denominator": "classification_valid_response_slots",
            },
        },
        "calibration_metrics": {
            "confidence_eligibility": "is_calibration_valid(response)",
            "missing_or_invalid_confidence": "NONNUMERIC_AND_EXCLUDED",
            "invalid_confidence_effect_on_classification": "NONE",
            "brier_top_label": {
                "implementation": "agent_arena.calibration.brier_top_label",
                "formula": "mean((confidence - binary_top_label_correctness)^2)",
                "denominator": "calibration_valid_response_slots",
            },
            "ece_5bin": {
                "implementations": [
                    "agent_arena.calibration.reliability_table",
                    "agent_arena.calibration.ece_from_table",
                ],
                "fixed_bin_edges": list(cal.FIVE_BIN_EDGES),
                "bin_semantics": "left-closed/right-open; confidence 1.0 in final bin",
                "formula": "sum((bin_n / calibration_valid_response_slots) * abs_gap)",
                "denominator": "calibration_valid_response_slots",
                "empty_bins": "RETAINED",
            },
        },
        "directional_decision_order": [
            {
                "order": 1,
                "verdict": INCONCLUSIVE_INCOMPLETE,
                "condition": (
                    "any unresolved primary or control unit prevents the complete comparison"
                ),
            },
            {
                "order": 2,
                "verdict": ADVERSE,
                "condition": (
                    "either model loses primary correct units or loses more than one "
                    "control correct unit"
                ),
            },
            {
                "order": 3,
                "verdict": SUPPORTIVE_DIRECTIONAL,
                "condition": (
                    "both models gain primary correct units and neither loses more "
                    "than one control correct unit"
                ),
            },
            {"order": 4, "verdict": INCONCLUSIVE, "condition": "otherwise"},
        ],
        "supportive_directional_scope": (
            "descriptive direction only; no statistical significance, generalization, "
            "or proof that every harness repair improved accuracy"
        ),
        "paired_sign_test": {
            "unit_pair_eligibility": (
                "same model and unit with resolved labels in both prompt arms"
            ),
            "discordant_pair_eligibility": (
                "eligible pair where exactly one arm's resolved label is correct"
            ),
            "exclusions": [
                "unresolved label in either arm",
                "both arms correct",
                "both arms incorrect",
            ],
            "implementation": "exact two-sided binomial sign test with p=0.5",
            "significance_threshold": "NONE_PREDECLARED",
            "independent_unit": "unit, never an individual repetition",
        },
        "completeness": {
            "classification": "all expected unit labels resolved",
            "calibration": "all planned response slots calibration-valid",
            "transport_missingness": "no missing slots and no provider-error slots",
            "separate_reporting_required": True,
        },
        "stopping": {
            "prompt_tuning_after_results": "PROHIBITED",
            "case_replacement_after_results": "PROHIBITED",
            "additional_repetitions_after_results": "PROHIBITED",
            "semantic_retries": "PROHIBITED",
        },
    }


def validate_analysis_contract(
    contract: dict,
    unit_strata: list[dict],
    n_replications: int,
) -> list[str]:
    """Reproduce the policy and verify that its populations partition the units."""
    errors: list[str] = []
    try:
        populations = contract["populations"]
        primary_ids = populations["primary"]["stratum_ids"]
        control_ids = populations["controls"]["stratum_ids"]
        expected_primary = populations["primary"]["expected_units_per_model_arm"]
        expected_control = populations["controls"]["expected_units_per_model_arm"]
    except (KeyError, TypeError):
        return ["analysis contract population definition is missing or malformed"]

    strata = {item.get("stratum_id"): item for item in unit_strata if isinstance(item, dict)}
    declared_ids = [item.get("stratum_id") for item in unit_strata if isinstance(item, dict)]
    if len(strata) != len(unit_strata) or None in strata:
        errors.append("unit strata contain missing or duplicate identities")
    if set(primary_ids) & set(control_ids):
        errors.append("analysis populations overlap")
    if set(primary_ids) | set(control_ids) != set(declared_ids):
        errors.append("analysis populations do not partition every declared stratum")
    actual_primary = sum(len(strata[item]["unit_ids"]) for item in primary_ids if item in strata)
    actual_control = sum(len(strata[item]["unit_ids"]) for item in control_ids if item in strata)
    if expected_primary != actual_primary:
        errors.append("primary expected-unit count differs from selected strata")
    if expected_control != actual_control:
        errors.append("control expected-unit count differs from selected strata")
    expected = build_analysis_contract(
        primary_stratum_ids=primary_ids,
        control_stratum_ids=control_ids,
        expected_primary_units=actual_primary,
        expected_control_units=actual_control,
        n_replications=n_replications,
    )
    if contract != expected:
        errors.append("analysis contract differs from executable deterministic policy")
    return errors


def _rate(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def _resolve_unit(
    unit: dict,
    records: list[dict],
    *,
    planned_votes: int,
    population: str,
) -> dict:
    """Resolve one unit without consulting gold until after vote aggregation."""
    by_index: dict[int, dict] = {}
    for record in records:
        if record.get("unit_id") != unit["unit_id"]:
            raise ConditionAnalysisError("unit aggregation received a foreign record")
        try:
            run_index = int(record["run_index"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ConditionAnalysisError("record run_index is missing or malformed") from exc
        if run_index < 0 or run_index >= planned_votes:
            raise ConditionAnalysisError("record run_index is outside the planned vote universe")
        if run_index in by_index:
            raise ConditionAnalysisError("duplicate response slot in unit aggregation")
        if record.get("gold_label") != unit["gold_label"]:
            raise ConditionAnalysisError("record gold binding differs from selected unit")
        by_index[run_index] = record

    responses = []
    valid_labels: list[str] = []
    for run_index in range(planned_votes):
        record = by_index.get(run_index)
        if record is None:
            responses.append({
                "run_index": run_index,
                "observed": False,
                "label": None,
                "classification_valid": False,
                "calibration_valid": False,
                "confidence_state": "MISSING",
                "provider_error": False,
                "error_type": None,
            })
            continue
        classification_valid = p7.is_classification_valid(record)
        calibration_valid = p7.is_calibration_valid(record)
        if classification_valid:
            valid_labels.append(record["label"])
        responses.append({
            "run_index": run_index,
            "observed": True,
            "label": record.get("label"),
            "classification_valid": classification_valid,
            "calibration_valid": calibration_valid,
            "confidence_state": p7.record_confidence_state(record),
            "provider_error": not p7.is_terminal_attempt(record),
            "error_type": record.get("error_type"),
        })

    counts = Counter(valid_labels)
    resolved_label = None
    support = 0
    qualifying = sorted(label for label, count in counts.items() if count >= 2)
    if len(qualifying) == 1:
        resolved_label = qualifying[0]
        support = counts[resolved_label]

    if resolved_label is not None:
        resolution = "UNANIMOUS" if support == planned_votes else "RESOLVED_MAJORITY"
    elif len(valid_labels) == 3 and len(counts) == 3:
        resolution = "UNRESOLVED_THREE_WAY_TIE"
    elif len(valid_labels) == 2 and len(counts) == 2:
        resolution = "UNRESOLVED_CONFLICTING_VALID_VOTES"
    else:
        resolution = "UNRESOLVED_INSUFFICIENT_VALID_VOTES"

    # Gold is deliberately consulted only after the response-only vote is fixed.
    resolved_correct = None if resolved_label is None else resolved_label == unit["gold_label"]
    missing = sum(not response["observed"] for response in responses)
    provider_errors = sum(response["provider_error"] for response in responses)
    classification_invalid = sum(
        response["observed"]
        and not response["provider_error"]
        and not response["classification_valid"]
        for response in responses
    )
    invalid_confidence = sum(
        response["classification_valid"] and not response["calibration_valid"]
        for response in responses
    )
    return {
        "unit_id": unit["unit_id"],
        "population": population,
        "gold_label": unit["gold_label"],
        "resolved_label": resolved_label,
        "resolved_correct": resolved_correct,
        "resolution": resolution,
        "valid_vote_count": len(valid_labels),
        "resolved_vote_support": support,
        "vote_counts": {label: counts[label] for label in sorted(counts)},
        "raw_response_labels_and_validity": responses,
        "slot_accounting": {
            "planned_response_slots": planned_votes,
            "observed_response_slots": len(by_index),
            "classification_valid_response_slots": len(valid_labels),
            "calibration_valid_response_slots": sum(
                response["calibration_valid"] for response in responses
            ),
            "missing_response_slots": missing,
            "classification_invalid_response_slots": classification_invalid,
            "provider_error_slots": provider_errors,
            "invalid_or_missing_confidence_on_valid_classification_slots": invalid_confidence,
            "missing_invalid_error_slots": missing + classification_invalid + provider_errors,
        },
    }


def _calibration_records(records: list[dict], gold_by_unit: dict[str, str]) -> list[cal.ResultRecord]:
    eligible = []
    for index, record in enumerate(records):
        if not p7.is_calibration_valid(record):
            continue
        result = cal.ResultRecord(
            dev_id=f"DEV-{index + 1:04d}",
            model=str(record["model"]),
            predicted_label=str(record["label"]),
            gold_label=gold_by_unit[str(record["unit_id"])],
            stratum="clear",
            confidence_raw=record["confidence"],
        ).finalize()
        eligible.append(result)
    return eligible


def _population_summary(
    name: str,
    unit_results: list[dict],
    records: list[dict],
    gold_by_unit: dict[str, str],
    *,
    planned_votes: int,
) -> dict:
    ids = {unit["unit_id"] for unit in unit_results}
    population_records = [record for record in records if record.get("unit_id") in ids]
    expected_units = len(unit_results)
    resolved = [unit for unit in unit_results if unit["resolved_label"] is not None]
    correct = sum(unit["resolved_correct"] is True for unit in resolved)
    incorrect = sum(unit["resolved_correct"] is False for unit in resolved)
    unresolved = expected_units - len(resolved)
    classification_valid = [
        record for record in population_records if p7.is_classification_valid(record)
    ]
    calibration_valid = [
        record for record in population_records if p7.is_calibration_valid(record)
    ]
    response_correct = sum(
        record["label"] == gold_by_unit[str(record["unit_id"])]
        for record in classification_valid
    )
    calibration_records = _calibration_records(population_records, gold_by_unit)
    brier_sum = sum((record.confidence - record.correct) ** 2 for record in calibration_records)
    brier = cal.brier_top_label(calibration_records)
    reliability = cal.reliability_table(calibration_records, cal.FIVE_BIN_EDGES)
    ece_numerator = sum(
        bucket["n"] * bucket["abs_gap"] for bucket in reliability if bucket["n"] > 0
    )
    ece = cal.ece_from_table(reliability, len(calibration_records))
    expected_response_slots = expected_units * planned_votes
    missing = sum(unit["slot_accounting"]["missing_response_slots"] for unit in unit_results)
    invalid = sum(
        unit["slot_accounting"]["classification_invalid_response_slots"]
        for unit in unit_results
    )
    provider_errors = sum(unit["slot_accounting"]["provider_error_slots"] for unit in unit_results)
    invalid_confidence = sum(
        unit["slot_accounting"][
            "invalid_or_missing_confidence_on_valid_classification_slots"
        ]
        for unit in unit_results
    )
    if expected_units != correct + incorrect + unresolved:
        raise ConditionAnalysisError("population unit accounting invariant failed")
    return {
        "population": name,
        "expected_units": expected_units,
        "resolved_units": len(resolved),
        "correct_resolved_units": correct,
        "incorrect_resolved_units": incorrect,
        "unresolved_units": unresolved,
        "classification_valid_response_slots": len(classification_valid),
        "calibration_valid_response_slots": len(calibration_valid),
        "missing_invalid_error_slots": missing + invalid + provider_errors,
        "response_slot_accounting": {
            "expected_response_slots": expected_response_slots,
            "observed_response_slots": len(population_records),
            "missing_response_slots": missing,
            "classification_invalid_response_slots": invalid,
            "provider_error_slots": provider_errors,
            "invalid_or_missing_confidence_on_valid_classification_slots": invalid_confidence,
            "calibration_ineligible_response_slots": expected_response_slots - len(calibration_valid),
        },
        "classification_metrics": {
            "coverage_adjusted_correct_unit_rate": {
                "numerator": correct,
                "denominator": expected_units,
                "value": _rate(correct, expected_units),
                "unresolved_units_are_scientifically_incorrect": False,
            },
            "resolved_unit_accuracy": {
                "numerator": correct,
                "denominator": len(resolved),
                "value": _rate(correct, len(resolved)),
            },
            "response_level_accuracy": {
                "eligibility_predicate": (
                    "agent_arena.phase7a_execution.is_classification_valid"
                ),
                "numerator": response_correct,
                "denominator": len(classification_valid),
                "value": _rate(response_correct, len(classification_valid)),
            },
        },
        "calibration_metrics": {
            "eligibility_predicate": "agent_arena.phase7a_execution.is_calibration_valid",
            "brier_top_label": {
                "sum_squared_error": brier_sum,
                "denominator": len(calibration_records),
                "value": brier,
            },
            "ece_5bin": {
                "weighted_gap_numerator": ece_numerator,
                "denominator": len(calibration_records),
                "value": ece,
                "fixed_bin_edges": list(cal.FIVE_BIN_EDGES),
                "reliability_table": reliability,
            },
        },
        "classification_complete": unresolved == 0,
        "calibration_complete": len(calibration_valid) == expected_response_slots,
        "transport_missingness_complete": missing == 0 and provider_errors == 0,
    }


def build_arm_model_analysis(
    records: list[dict],
    *,
    ordered_unit_bindings: list[dict],
    unit_strata: list[dict],
    analysis_contract: dict,
    model: str,
    arm_id: str,
) -> dict:
    """Build one model/arm result with fixed primary and control denominators."""
    errors = validate_analysis_contract(
        analysis_contract,
        unit_strata,
        analysis_contract["aggregation"]["planned_votes_per_unit"],
    )
    if errors:
        raise ConditionAnalysisError("; ".join(errors))
    planned_votes = analysis_contract["aggregation"]["planned_votes_per_unit"]
    unit_by_id = {unit["unit_id"]: unit for unit in ordered_unit_bindings}
    if len(unit_by_id) != len(ordered_unit_bindings):
        raise ConditionAnalysisError("ordered unit bindings contain duplicate identities")
    if any(record.get("model") != model for record in records):
        raise ConditionAnalysisError("arm analysis records contain another model")
    records_by_unit: dict[str, list[dict]] = {unit_id: [] for unit_id in unit_by_id}
    for record in records:
        unit_id = record.get("unit_id")
        if unit_id not in records_by_unit:
            raise ConditionAnalysisError("arm analysis contains an unexpected unit")
        records_by_unit[unit_id].append(record)

    stratum_map = {stratum["stratum_id"]: stratum["unit_ids"] for stratum in unit_strata}
    population_by_unit: dict[str, str] = {}
    for population, definition in analysis_contract["populations"].items():
        for stratum_id in definition["stratum_ids"]:
            for unit_id in stratum_map[stratum_id]:
                population_by_unit[unit_id] = population
    if set(population_by_unit) != set(unit_by_id):
        raise ConditionAnalysisError("analysis populations do not cover the ordered unit universe")

    unit_results = [
        _resolve_unit(
            unit,
            records_by_unit[unit["unit_id"]],
            planned_votes=planned_votes,
            population=population_by_unit[unit["unit_id"]],
        )
        for unit in ordered_unit_bindings
    ]
    gold_by_unit = {unit["unit_id"]: unit["gold_label"] for unit in ordered_unit_bindings}
    populations = {
        name: _population_summary(
            name,
            [unit for unit in unit_results if unit["population"] == name],
            records,
            gold_by_unit,
            planned_votes=planned_votes,
        )
        for name in ("primary", "controls")
    }
    return {
        "model": model,
        "arm_id": arm_id,
        "planned_votes_per_unit": planned_votes,
        "unit_results": unit_results,
        "populations": populations,
        "classification_complete": all(
            population["classification_complete"] for population in populations.values()
        ),
        "calibration_complete": all(
            population["calibration_complete"] for population in populations.values()
        ),
        "transport_missingness_complete": all(
            population["transport_missingness_complete"] for population in populations.values()
        ),
    }


def _exact_two_sided_sign_test(revised_wins: int, historical_wins: int) -> float | None:
    n = revised_wins + historical_wins
    if n == 0:
        return None
    tail = sum(comb(n, index) for index in range(min(revised_wins, historical_wins) + 1))
    return min(1.0, 2 * tail / (2 ** n))


def _paired_population(
    historical: dict,
    prospective: dict,
    population: str,
) -> dict:
    historical_units = {
        unit["unit_id"]: unit
        for unit in historical["unit_results"]
        if unit["population"] == population
    }
    prospective_units = {
        unit["unit_id"]: unit
        for unit in prospective["unit_results"]
        if unit["population"] == population
    }
    if set(historical_units) != set(prospective_units):
        raise ConditionAnalysisError("paired arms have different unit populations")
    transitions = []
    revised_wins = historical_wins = 0
    for unit_id in sorted(historical_units):
        old = historical_units[unit_id]
        new = prospective_units[unit_id]
        eligible = old["resolved_label"] is not None and new["resolved_label"] is not None
        discordant = bool(
            eligible and old["resolved_correct"] != new["resolved_correct"]
        )
        if discordant and new["resolved_correct"]:
            revised_wins += 1
        elif discordant and old["resolved_correct"]:
            historical_wins += 1
        if not eligible:
            sign_test_exclusion = "unresolved label in one or both prompt arms"
        elif old["resolved_correct"] and new["resolved_correct"]:
            sign_test_exclusion = "both arms correct"
        elif not old["resolved_correct"] and not new["resolved_correct"]:
            sign_test_exclusion = "both arms incorrect"
        else:
            sign_test_exclusion = None
        transitions.append({
            "unit_id": unit_id,
            "historical_resolved_label": old["resolved_label"],
            "prospective_resolved_label": new["resolved_label"],
            "historical_correct": old["resolved_correct"],
            "prospective_correct": new["resolved_correct"],
            "paired_transition_eligible": eligible,
            "discordant_sign_test_eligible": discordant,
            "sign_test_exclusion_reason": sign_test_exclusion,
        })
    return {
        "population": population,
        "transitions": transitions,
        "sign_test": {
            "revised_wins": revised_wins,
            "historical_wins": historical_wins,
            "discordant_pairs": revised_wins + historical_wins,
            "exact_two_sided_p_value": _exact_two_sided_sign_test(
                revised_wins, historical_wins
            ),
            "significance_threshold": None,
        },
    }


def build_paired_analysis(
    analyses: list[dict],
    *,
    model_ids: list[str],
    historical_arm_id: str,
    prospective_arm_id: str,
) -> dict:
    """Apply the mutually exclusive decision order across all four batches."""
    by_key = {(analysis["model"], analysis["arm_id"]): analysis for analysis in analyses}
    expected_keys = {
        (model, arm)
        for model in model_ids
        for arm in (historical_arm_id, prospective_arm_id)
    }
    if set(by_key) != expected_keys:
        raise ConditionAnalysisError("paired analysis requires exactly four model/arm analyses")

    model_results = {}
    any_incomplete = False
    adverse = False
    supportive = True
    calibration_complete = True
    transport_complete = True
    for model in model_ids:
        old = by_key[(model, historical_arm_id)]
        new = by_key[(model, prospective_arm_id)]
        primary_delta = (
            new["populations"]["primary"]["correct_resolved_units"]
            - old["populations"]["primary"]["correct_resolved_units"]
        )
        control_delta = (
            new["populations"]["controls"]["correct_resolved_units"]
            - old["populations"]["controls"]["correct_resolved_units"]
        )
        primary_denominator = old["populations"]["primary"]["expected_units"]
        if primary_denominator != new["populations"]["primary"]["expected_units"]:
            raise ConditionAnalysisError(
                "paired primary populations have different fixed denominators"
            )
        control_denominator = old["populations"]["controls"]["expected_units"]
        if control_denominator != new["populations"]["controls"]["expected_units"]:
            raise ConditionAnalysisError(
                "paired control populations have different fixed denominators"
            )
        incomplete = not old["classification_complete"] or not new["classification_complete"]
        any_incomplete = any_incomplete or incomplete
        adverse = adverse or primary_delta < 0 or control_delta < -1
        supportive = supportive and primary_delta > 0 and control_delta >= -1
        calibration_complete = (
            calibration_complete and old["calibration_complete"] and new["calibration_complete"]
        )
        transport_complete = (
            transport_complete
            and old["transport_missingness_complete"]
            and new["transport_missingness_complete"]
        )
        model_results[model] = {
            "primary_correct_unit_delta": primary_delta,
            "primary_coverage_adjusted_correct_unit_rate": {
                "denominator": primary_denominator,
                "historical_numerator": old["populations"]["primary"][
                    "correct_resolved_units"
                ],
                "historical_value": _rate(
                    old["populations"]["primary"]["correct_resolved_units"],
                    primary_denominator,
                ),
                "prospective_numerator": new["populations"]["primary"][
                    "correct_resolved_units"
                ],
                "prospective_value": _rate(
                    new["populations"]["primary"]["correct_resolved_units"],
                    primary_denominator,
                ),
                "difference": _rate(primary_delta, primary_denominator),
                "unresolved_units_are_scientifically_incorrect": False,
            },
            "control_correct_unit_delta": control_delta,
            "control_fixed_denominator": control_denominator,
            "primary_direction": (
                "IMPROVED" if primary_delta > 0 else "WORSENED" if primary_delta < 0 else "UNCHANGED"
            ),
            "classification_complete": not incomplete,
            "paired_populations": {
                population: _paired_population(old, new, population)
                for population in ("primary", "controls")
            },
        }

    if any_incomplete:
        verdict = INCONCLUSIVE_INCOMPLETE
        trigger = "unresolved unit labels prevent the complete primary/control comparison"
    elif adverse:
        verdict = ADVERSE
        trigger = "at least one model crossed a predeclared adverse delta threshold"
    elif supportive:
        verdict = SUPPORTIVE_DIRECTIONAL
        trigger = "both models improved primary correct units without excessive control loss"
    else:
        verdict = INCONCLUSIVE
        trigger = "complete comparison did not meet supportive or adverse criteria"
    return {
        "paired_analysis_schema_version": PAIRED_ANALYSIS_SCHEMA_VERSION,
        "directional_verdict": verdict,
        "directional_verdict_trigger": trigger,
        "classification_complete": not any_incomplete,
        "calibration_complete": calibration_complete,
        "transport_missingness_complete": transport_complete,
        "model_results": model_results,
        "interpretation": (
            "SUPPORTIVE_DIRECTIONAL is descriptive only; no significance threshold, "
            "generalization claim, or proof of universal harness improvement is applied."
        ),
    }
