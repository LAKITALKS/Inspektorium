"""Deterministic historical-reference analysis for the Phase-5B Haiku replication."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median

from agent_arena import calibration as cal
from agent_arena import condition_contract as cc
from agent_arena import phase7a_execution as p7
from agent_arena import runtime_contract as rc


ANALYSIS_SCHEMA_VERSION = "agent_arena.full_replication_analysis/v1"
COMPARISON_SCHEMA_VERSION = "agent_arena.full_replication_comparison/v1"
TARGETED_19 = (
    "P7A-ADV-003", "P7A-ADV-004", "P7A-ADV-013", "P7A-ADV-017",
    "P7A-BND-009", "P7A-BND-010", "P7A-NEU-004", "P7A-ADV-009",
    "P7A-ADV-010", "P7A-BND-015", "P7A-BND-016", "P7A-ADV-001",
    "P7A-ADV-002", "P7A-NEU-002", "P7A-BND-001", "P7A-NEU-001",
    "P7A-BND-012", "P7A-NEU-003", "P7A-ADV-005",
)


class FullReplicationAnalysisError(ValueError):
    """The fixed-denominator deterministic analysis could not reproduce."""


def _rate(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def _quantile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = round((len(ordered) - 1) * fraction)
    return ordered[index]


def _unit_result(binding: dict, records: list[dict], repetitions: int) -> dict:
    by_index: dict[int, dict] = {}
    for record in records:
        try:
            run_index = int(record["run_index"])
        except (KeyError, TypeError, ValueError) as exc:
            raise FullReplicationAnalysisError("record run index is malformed") from exc
        if run_index < 0 or run_index >= repetitions or run_index in by_index:
            raise FullReplicationAnalysisError("record slot is duplicate or outside the plan")
        if record.get("gold_label") != binding["gold_label"]:
            raise FullReplicationAnalysisError("record gold differs from immutable unit binding")
        by_index[run_index] = record
    labels = [
        record["label"]
        for _, record in sorted(by_index.items())
        if p7.is_classification_valid(record)
    ]
    counts = Counter(labels)
    modal_label = None
    modal_support = 0
    tied_modal_labels: list[str] = []
    if counts:
        modal_support = max(counts.values())
        tied_modal_labels = sorted(
            label for label, count in counts.items() if count == modal_support
        )
        if len(tied_modal_labels) == 1:
            modal_label = tied_modal_labels[0]
    observed = len(by_index)
    terminal = sum(p7.is_terminal_attempt(record) for record in by_index.values())
    classification_valid = sum(
        p7.is_classification_valid(record) for record in by_index.values()
    )
    calibration_valid = sum(
        p7.is_calibration_valid(record) for record in by_index.values()
    )
    return {
        "unit_id": binding["unit_id"],
        "unit_type": binding["unit_type"],
        "family_id": binding.get("family_id"),
        "gold_label": binding["gold_label"],
        "vote_counts": {label: counts[label] for label in sorted(counts)},
        "modal_label": modal_label,
        "modal_support": modal_support,
        "modal_tie": len(tied_modal_labels) > 1,
        "tied_modal_labels": tied_modal_labels if len(tied_modal_labels) > 1 else [],
        "modal_correct": None if modal_label is None else modal_label == binding["gold_label"],
        "unanimous": modal_label is not None and modal_support == repetitions,
        "expected_response_slots": repetitions,
        "observed_response_slots": observed,
        "terminal_response_slots": terminal,
        "classification_valid_response_slots": classification_valid,
        "calibration_valid_response_slots": calibration_valid,
        "missing_response_slots": repetitions - observed,
        "provider_error_slots": observed - terminal,
        "classification_invalid_terminal_slots": terminal - classification_valid,
        "calibration_invalid_terminal_slots": terminal - calibration_valid,
        "labels_by_run_index": [
            by_index[index].get("label") if index in by_index else None
            for index in range(repetitions)
        ],
    }


def _population(
    name: str,
    unit_ids: set[str],
    unit_results: list[dict],
    records: list[dict],
    repetitions: int,
) -> dict:
    units = [unit for unit in unit_results if unit["unit_id"] in unit_ids]
    scoped_records = [record for record in records if record.get("unit_id") in unit_ids]
    expected_units = len(unit_ids)
    expected_slots = expected_units * repetitions
    correct_units = sum(unit["modal_correct"] is True for unit in units)
    incorrect_units = sum(unit["modal_correct"] is False for unit in units)
    unresolved_units = expected_units - correct_units - incorrect_units
    classification_valid = [
        record for record in scoped_records if p7.is_classification_valid(record)
    ]
    calibration_valid = [
        record for record in scoped_records if p7.is_calibration_valid(record)
    ]
    response_correct = sum(bool(record.get("label_correct")) for record in classification_valid)
    brier_values = [
        (float(record["confidence"]) - (1.0 if record.get("label_correct") else 0.0)) ** 2
        for record in calibration_valid
    ]
    return {
        "population": name,
        "expected_units": expected_units,
        "expected_response_slots": expected_slots,
        "observed_response_slots": len(scoped_records),
        "terminal_response_slots": sum(p7.is_terminal_attempt(record) for record in scoped_records),
        "classification_valid_response_slots": len(classification_valid),
        "calibration_valid_response_slots": len(calibration_valid),
        "missing_invalid_or_provider_error_slots": expected_slots - len(classification_valid),
        "correct_modal_units": correct_units,
        "incorrect_modal_units": incorrect_units,
        "unresolved_modal_units": unresolved_units,
        "unit_level_modal_accuracy": {
            "numerator": correct_units,
            "fixed_denominator": expected_units,
            "value": _rate(correct_units, expected_units),
        },
        "response_level_accuracy": {
            "numerator": response_correct,
            "classification_valid_denominator": len(classification_valid),
            "fixed_expected_slot_denominator": expected_slots,
            "value": _rate(response_correct, len(classification_valid)),
        },
        "brier": {
            "denominator": len(brier_values),
            "value": mean(brier_values) if brier_values else None,
        },
    }


def summarize_records(
    records: list[dict],
    *,
    ordered_unit_bindings: list[dict],
    model_id: str,
    repetitions: int,
    condition: str,
) -> dict:
    expected_ids = [binding["unit_id"] for binding in ordered_unit_bindings]
    if len(expected_ids) != len(set(expected_ids)):
        raise FullReplicationAnalysisError("ordered unit bindings contain duplicates")
    foreign = [record for record in records if record.get("unit_id") not in set(expected_ids)]
    if foreign:
        raise FullReplicationAnalysisError("records contain units outside the immutable universe")
    if any(record.get("model") != model_id for record in records):
        raise FullReplicationAnalysisError("records contain another model")
    by_unit: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        by_unit[str(record["unit_id"])].append(record)
    unit_results = [
        _unit_result(binding, by_unit[binding["unit_id"]], repetitions)
        for binding in ordered_unit_bindings
    ]
    expected_units = len(expected_ids)
    expected_slots = expected_units * repetitions
    terminal = [record for record in records if p7.is_terminal_attempt(record)]
    classification_valid = [record for record in records if p7.is_classification_valid(record)]
    calibration_valid = [record for record in records if p7.is_calibration_valid(record)]
    correct_modal = sum(unit["modal_correct"] is True for unit in unit_results)
    incorrect_modal = sum(unit["modal_correct"] is False for unit in unit_results)
    unresolved_modal = expected_units - correct_modal - incorrect_modal
    response_correct = sum(bool(record.get("label_correct")) for record in classification_valid)
    confidences = [float(record["confidence"]) for record in calibration_valid]
    brier_values = [
        (float(record["confidence"]) - (1.0 if record.get("label_correct") else 0.0)) ** 2
        for record in calibration_valid
    ]
    calibration_records = []
    for index, record in enumerate(calibration_valid):
        calibration_records.append(
            cal.ResultRecord(
                dev_id=f"P5B-{index + 1:04d}",
                model=model_id,
                predicted_label=str(record["label"]),
                gold_label=str(record["gold_label"]),
                stratum="clear",
                confidence_raw=record["confidence"],
            ).finalize()
        )
    reliability = cal.reliability_table(calibration_records, cal.FIVE_BIN_EDGES)
    ece = cal.ece_from_table(reliability, len(calibration_records))
    matrix: dict[str, Counter] = defaultdict(Counter)
    label_expected = Counter(binding["gold_label"] for binding in ordered_unit_bindings)
    label_correct = Counter()
    label_unresolved = Counter()
    for unit in unit_results:
        predicted = unit["modal_label"] if unit["modal_label"] is not None else "UNRESOLVED"
        matrix[unit["gold_label"]][predicted] += 1
        if unit["modal_correct"] is True:
            label_correct[unit["gold_label"]] += 1
        if unit["modal_label"] is None:
            label_unresolved[unit["gold_label"]] += 1
    per_label = {
        label: {
            "correct_modal_units": label_correct[label],
            "fixed_denominator_units": label_expected[label],
            "unresolved_units": label_unresolved[label],
            "accuracy": _rate(label_correct[label], label_expected[label]),
        }
        for label in sorted(label_expected)
    }
    targeted = set(TARGETED_19)
    remaining = set(expected_ids) - targeted
    if len(targeted & set(expected_ids)) != 19 or len(remaining) != 65:
        raise FullReplicationAnalysisError("targeted-19 / remaining-65 partition drift")
    summary = {
        "analysis_schema_version": ANALYSIS_SCHEMA_VERSION,
        "condition": condition,
        "model_id": model_id,
        "expected_units": expected_units,
        "repetitions": repetitions,
        "expected_response_slots": expected_slots,
        "observed_response_slots": len(records),
        "terminal_response_slots": len(terminal),
        "classification_valid_response_slots": len(classification_valid),
        "calibration_valid_response_slots": len(calibration_valid),
        "provider_error_response_slots": len(records) - len(terminal),
        "missing_response_slots": expected_slots - len(records),
        "classification_invalid_terminal_slots": len(terminal) - len(classification_valid),
        "calibration_invalid_terminal_slots": len(terminal) - len(calibration_valid),
        "unit_level_modal_accuracy": {
            "numerator": correct_modal,
            "fixed_denominator": expected_units,
            "incorrect_units": incorrect_modal,
            "unresolved_units": unresolved_modal,
            "value": _rate(correct_modal, expected_units),
        },
        "response_level_accuracy": {
            "numerator": response_correct,
            "classification_valid_denominator": len(classification_valid),
            "fixed_expected_slot_denominator": expected_slots,
            "value": _rate(response_correct, len(classification_valid)),
        },
        "calibration": {
            "brier": {"denominator": len(brier_values), "value": mean(brier_values) if brier_values else None},
            "ece_5bin": {
                "denominator": len(calibration_records),
                "fixed_bin_edges": list(cal.FIVE_BIN_EDGES),
                "value": ece,
                "reliability_table": reliability,
            },
            "confidence_distribution": {
                "denominator": len(confidences),
                "mean": mean(confidences) if confidences else None,
                "median": median(confidences) if confidences else None,
                "minimum": min(confidences) if confidences else None,
                "maximum": max(confidences) if confidences else None,
                "p05_nearest_rank": _quantile(confidences, 0.05),
                "p95_nearest_rank": _quantile(confidences, 0.95),
            },
        },
        "confusion_matrix": {
            gold: {predicted: counts[predicted] for predicted in sorted(counts)}
            for gold, counts in sorted(matrix.items())
        },
        "per_label_accuracy": per_label,
        "me_ov_confusions": {
            "mechanism_vs_evidence_to_overclaim": matrix["mechanism_vs_evidence"]["overclaim"],
            "overclaim_to_mechanism_vs_evidence": matrix["overclaim"]["mechanism_vs_evidence"],
        },
        "stability": {
            "unanimous_units": sum(unit["unanimous"] for unit in unit_results),
            "modal_support_counts": dict(sorted(Counter(unit["modal_support"] for unit in unit_results).items())),
            "modal_tie_units": [unit["unit_id"] for unit in unit_results if unit["modal_tie"]],
        },
        "populations": {
            "targeted_19": _population("targeted_19", targeted, unit_results, records, repetitions),
            "remaining_65": _population("remaining_65", remaining, unit_results, records, repetitions),
        },
        "unit_results": unit_results,
    }
    summary["analysis_fingerprint"] = cc._fp(summary)
    return summary


def build_comparison(
    historical_records: list[dict],
    prospective_records: list[dict],
    *,
    document: dict,
    historical_raw_path: str | Path,
    prospective_raw_path: str | Path,
) -> dict:
    specification = document["specification"]
    model_id = specification["model_ids"][0]
    bindings = specification["ordered_unit_bindings"]
    repetitions = specification["n_replications"]
    historical = summarize_records(
        historical_records,
        ordered_unit_bindings=bindings,
        model_id=model_id,
        repetitions=repetitions,
        condition="historical_old_prompt_reference",
    )
    prospective = summarize_records(
        prospective_records,
        ordered_unit_bindings=bindings,
        model_id=model_id,
        repetitions=repetitions,
        condition="prospective_taxonomy_aligned_prompt",
    )
    historical_units = {unit["unit_id"]: unit for unit in historical["unit_results"]}
    prospective_units = {unit["unit_id"]: unit for unit in prospective["unit_results"]}
    transitions = []
    matrix: dict[str, Counter] = defaultdict(Counter)
    for binding in bindings:
        unit_id = binding["unit_id"]
        old = historical_units[unit_id]
        new = prospective_units[unit_id]
        old_label = old["modal_label"] or "UNRESOLVED"
        new_label = new["modal_label"] or "UNRESOLVED"
        matrix[old_label][new_label] += 1
        transitions.append({
            "unit_id": unit_id,
            "population": "targeted_19" if unit_id in TARGETED_19 else "remaining_65",
            "gold_label": binding["gold_label"],
            "historical_modal_label": old["modal_label"],
            "prospective_modal_label": new["modal_label"],
            "historical_modal_support": old["modal_support"],
            "prospective_modal_support": new["modal_support"],
            "historical_correct": old["modal_correct"],
            "prospective_correct": new["modal_correct"],
            "historical_unanimous": old["unanimous"],
            "prospective_unanimous": new["unanimous"],
        })
    comparison = {
        "comparison_schema_version": COMPARISON_SCHEMA_VERSION,
        "plan_id": specification["plan_id"],
        "comparison_id": specification["comparison_id"],
        "specification_fingerprint": specification["specification_fingerprint"],
        "model_id": model_id,
        "design": "historical_reference_replication_not_simultaneous_randomized_ab",
        "interpretation": (
            "The prospective corrected-prompt run differs from the historical old-prompt "
            "reference; prompt condition, stochastic variation, and temporal provider/runtime "
            "effects are all potential contributors. Prompt-only causal attribution is prohibited."
        ),
        "historical_raw": {
            "path": str(historical_raw_path),
            "sha256": rc._sha256_hex(Path(historical_raw_path).read_bytes()),
            "reused_as_prospective_response": False,
        },
        "prospective_raw": {
            "path": str(prospective_raw_path),
            "sha256": rc._sha256_hex(Path(prospective_raw_path).read_bytes()),
        },
        "historical": historical,
        "prospective": prospective,
        "differences": {
            "unit_level_modal_accuracy": (
                prospective["unit_level_modal_accuracy"]["value"]
                - historical["unit_level_modal_accuracy"]["value"]
            ),
            "response_level_accuracy": (
                prospective["response_level_accuracy"]["value"]
                - historical["response_level_accuracy"]["value"]
                if prospective["response_level_accuracy"]["value"] is not None
                and historical["response_level_accuracy"]["value"] is not None
                else None
            ),
            "brier": (
                prospective["calibration"]["brier"]["value"]
                - historical["calibration"]["brier"]["value"]
                if prospective["calibration"]["brier"]["value"] is not None
                and historical["calibration"]["brier"]["value"] is not None
                else None
            ),
            "ece_5bin": (
                prospective["calibration"]["ece_5bin"]["value"]
                - historical["calibration"]["ece_5bin"]["value"]
                if prospective["calibration"]["ece_5bin"]["value"] is not None
                and historical["calibration"]["ece_5bin"]["value"] is not None
                else None
            ),
            "targeted_19_modal_accuracy": (
                prospective["populations"]["targeted_19"]["unit_level_modal_accuracy"]["value"]
                - historical["populations"]["targeted_19"]["unit_level_modal_accuracy"]["value"]
            ),
            "remaining_65_modal_accuracy": (
                prospective["populations"]["remaining_65"]["unit_level_modal_accuracy"]["value"]
                - historical["populations"]["remaining_65"]["unit_level_modal_accuracy"]["value"]
            ),
            "unanimous_units": prospective["stability"]["unanimous_units"] - historical["stability"]["unanimous_units"],
        },
        "modal_label_transition_matrix": {
            old: {new: counts[new] for new in sorted(counts)}
            for old, counts in sorted(matrix.items())
        },
        "unit_transitions": transitions,
    }
    comparison["comparison_fingerprint"] = cc._fp(comparison)
    return comparison


def build_usage_cost(records: list[dict], *, input_price: float, output_price: float) -> dict:
    input_tokens = output_tokens = http_attempts = transport_retries = 0
    usage_records = attempt_records = 0
    for record in records:
        usage = record.get("usage") or {}
        if isinstance(usage.get("input_tokens"), int):
            input_tokens += usage["input_tokens"]
            usage_records += 1
        if isinstance(usage.get("output_tokens"), int):
            output_tokens += usage["output_tokens"]
        if isinstance(usage.get("http_attempts"), int):
            http_attempts += usage["http_attempts"]
            transport_retries += int(usage.get("transport_retries") or 0)
            attempt_records += 1
    cost = input_tokens * input_price / 1_000_000 + output_tokens * output_price / 1_000_000
    value = {
        "usage_cost_schema_version": "agent_arena.full_replication_usage_cost/v1",
        "records": len(records),
        "records_with_token_usage": usage_records,
        "records_with_http_attempt_accounting": attempt_records,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "http_attempts": http_attempts,
        "transport_retries": transport_retries,
        "provider_failures": sum(not p7.is_terminal_attempt(record) for record in records),
        "pricing": {
            "currency": "USD",
            "input_usd_per_million_tokens": input_price,
            "output_usd_per_million_tokens": output_price,
            "cache_included": False,
            "batch_discount_included": False,
        },
        "calculated_cost_usd": cost,
    }
    value["usage_cost_fingerprint"] = cc._fp(value)
    return value


def render_comparison_markdown(comparison: dict) -> str:
    old = comparison["historical"]
    new = comparison["prospective"]
    lines = [
        "# Phase 5B Haiku Full Replication — Historical Reference Comparison",
        "",
        f"- Model: `{comparison['model_id']}`",
        f"- Design: `{comparison['design']}`",
        f"- Expected slots per condition: **{old['expected_response_slots']}**",
        f"- Historical terminal/classification/calibration: **{old['terminal_response_slots']} / {old['classification_valid_response_slots']} / {old['calibration_valid_response_slots']}**",
        f"- Prospective terminal/classification/calibration: **{new['terminal_response_slots']} / {new['classification_valid_response_slots']} / {new['calibration_valid_response_slots']}**",
        "",
        "## Metrics",
        "",
        "| Metric | Historical old prompt | Prospective corrected prompt | Difference |",
        "|---|---:|---:|---:|",
        f"| Unit-level modal accuracy | {old['unit_level_modal_accuracy']['value']} | {new['unit_level_modal_accuracy']['value']} | {comparison['differences']['unit_level_modal_accuracy']} |",
        f"| Response-level accuracy | {old['response_level_accuracy']['value']} | {new['response_level_accuracy']['value']} | {comparison['differences']['response_level_accuracy']} |",
        f"| Brier | {old['calibration']['brier']['value']} | {new['calibration']['brier']['value']} | {comparison['differences']['brier']} |",
        f"| ECE (5 bins) | {old['calibration']['ece_5bin']['value']} | {new['calibration']['ece_5bin']['value']} | {comparison['differences']['ece_5bin']} |",
        f"| Targeted-19 modal accuracy | {old['populations']['targeted_19']['unit_level_modal_accuracy']['value']} | {new['populations']['targeted_19']['unit_level_modal_accuracy']['value']} | {comparison['differences']['targeted_19_modal_accuracy']} |",
        f"| Remaining-65 modal accuracy | {old['populations']['remaining_65']['unit_level_modal_accuracy']['value']} | {new['populations']['remaining_65']['unit_level_modal_accuracy']['value']} | {comparison['differences']['remaining_65_modal_accuracy']} |",
        "",
        "## Interpretation boundary",
        "",
        comparison["interpretation"],
        "",
    ]
    return "\n".join(lines)
