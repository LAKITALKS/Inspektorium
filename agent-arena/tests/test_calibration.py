"""Tests for the Phase 6.2 calibration/abstention engine (SYNTHETIC records only).

These synthetic records are illustrative fixtures; they do not represent, simulate,
or imply real Agent Arena performance. Reports built here pass ``synthetic=True``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agent_arena.calibration import (
    EXPECTED_MANIFEST_ID,
    FIVE_BIN_EDGES,
    CalibrationError,
    ResultRecord,
    _bin_index,
    _subset_metrics,
    assert_reliability_bins_complete,
    brier_top_label,
    build_report,
    confidence_audit,
    ece_from_table,
    load_public_manifest_binding,
    reliability_table,
    render_report_text,
    risk_coverage_curve,
    select_operating_threshold,
    validate_result_envelope,
    validate_result_records,
)

GOLD_PLAN = [("solid", 8), ("overclaim", 15),
             ("correlation_vs_causation", 2), ("mechanism_vs_evidence", 2)]


def _rec(pred, gold, conf, stratum="clear", model="mA", dev="DEV-001"):
    return ResultRecord(dev_id=dev, model=model, predicted_label=pred, gold_label=gold,
                        stratum=stratum, confidence_raw=conf).finalize()


def _full_raw(model="mA", predict=None):
    """27 records for one model with the frozen 8/15/2/2 GOLD aggregate.

    ``predict(gold, i) -> label`` sets predicted labels; default is a perfect predictor.
    """
    raw = []
    n = 0
    for label, count in GOLD_PLAN:
        for _ in range(count):
            n += 1
            pred = predict(label, n) if predict else label
            raw.append({"dev_id": f"DEV-{n:03d}", "model": model,
                        "predicted_label": pred, "gold_label": label,
                        "stratum": "clear", "confidence": 0.8})
    return raw


def _envelope(records, manifest_id=EXPECTED_MANIFEST_ID, commitment="a" * 64, **over):
    env = {
        "envelope_version": "6.2.0", "protocol_version": "6.1",
        "manifest_id": manifest_id, "public_commitment": commitment,
        "run_id": "RUN-001", "model": "mA", "provider": "prov",
        "prompt_contract_version": "sf-v0.6.5", "generated_at": "2026-08-04T00:00:00Z",
        "expected_record_count": 27,
        "declared_gold_aggregate": {"solid": 8, "overclaim": 15,
                                    "correlation_vs_causation": 2, "mechanism_vs_evidence": 2, "total": 27},
        "records": records,
    }
    env.update(over)
    return env


# ========================= 1. gold vs predicted =========================

def test_valid_full_set_ok():
    assert validate_result_records(_full_raw()).ok


def test_predicted_distribution_may_differ_from_gold():
    # predict everything "solid": predicted dist 27/0/0/0, gold still 8/15/2/2 -> OK
    raw = _full_raw(predict=lambda gold, i: "solid")
    res = validate_result_records(raw)
    assert res.ok
    report = build_report(res.records, synthetic=True)
    dist = report["models"]["mA"]["micro_all"]["predicted_label_distribution"]
    assert dist == {"solid": 27, "overclaim": 0,
                    "correlation_vs_causation": 0, "mechanism_vs_evidence": 0}


def test_aggregate_enforced_on_gold_not_predicted():
    # gold aggregate wrong -> error even if predicted is well-formed
    raw = _full_raw()
    raw[-1]["gold_label"] = "solid"        # 9 solid / 1 mechanism (gold)
    assert any("gold" in e and "count" in e for e in validate_result_records(raw).errors)
    # predicted skew alone (gold intact) is fine
    assert validate_result_records(_full_raw(predict=lambda g, i: "overclaim")).ok


def test_supplied_correctness_inconsistent_rejected():
    raw = _full_raw()
    raw[0]["predicted_label"] = "overclaim"     # gold solid
    raw[0]["correct"] = 1
    assert any("inconsistent" in e for e in validate_result_records(raw).errors)


# ========================= 2. envelope binding =========================

def test_valid_envelope_accepted():
    res = validate_result_envelope(_envelope(_full_raw()), EXPECTED_MANIFEST_ID, "a" * 64)
    assert res.ok
    assert res.provenance["manifest_id"] == EXPECTED_MANIFEST_ID
    assert res.provenance["run_id"] == "RUN-001"


def test_envelope_wrong_manifest_id_rejected():
    env = _envelope(_full_raw(), manifest_id="AA-DEVPOOL-9999")
    assert any("manifest_id" in e for e in validate_result_envelope(env, EXPECTED_MANIFEST_ID, "a" * 64).errors)


def test_envelope_wrong_commitment_rejected():
    env = _envelope(_full_raw(), commitment="b" * 64)
    assert any("commitment does not match" in e
               for e in validate_result_envelope(env, EXPECTED_MANIFEST_ID, "a" * 64).errors)


def test_envelope_wrong_protocol_rejected():
    env = _envelope(_full_raw(), protocol_version="9.9")
    assert any("protocol_version" in e for e in validate_result_envelope(env, EXPECTED_MANIFEST_ID, "a" * 64).errors)


def test_envelope_wrong_record_count_rejected():
    env = _envelope(_full_raw()[:-1], expected_record_count=27)   # 26 records
    assert any("records" in e for e in validate_result_envelope(env, EXPECTED_MANIFEST_ID, "a" * 64).errors)


def test_envelope_wrong_declared_aggregate_rejected():
    env = _envelope(_full_raw(), declared_gold_aggregate={"solid": 9, "overclaim": 14,
                    "correlation_vs_causation": 2, "mechanism_vs_evidence": 2, "total": 27})
    assert any("declared_gold_aggregate" in e
               for e in validate_result_envelope(env, EXPECTED_MANIFEST_ID, "a" * 64).errors)


def test_envelope_canonical_id_rejected():
    env = _envelope(_full_raw(), leaked="study-forensics-901")
    assert any("canonical id present" in e
               for e in validate_result_envelope(env, EXPECTED_MANIFEST_ID, "a" * 64).errors)


def test_envelope_salt_rejected():
    env = _envelope(_full_raw(), salt="deadbeef")
    assert any("salt" in e for e in validate_result_envelope(env, EXPECTED_MANIFEST_ID, "a" * 64).errors)


def test_load_public_manifest_binding_real():
    mid, commitment = load_public_manifest_binding(repo_root=Path(__file__).resolve().parents[1])
    assert mid == EXPECTED_MANIFEST_ID
    assert isinstance(commitment, str) and len(commitment) == 64  # provisioned salted commitment


# ========================= 3. confidence denominators =========================

def test_ordinary_accuracy_uses_all_records_regardless_of_confidence():
    recs = validate_result_records(_full_raw()).records          # all correct, valid conf
    base = _subset_metrics(recs)
    assert base["accuracy"] == 1.0 and base["denominators"]["brier"] == 27
    # make one confidence MISSING: accuracy(all) unchanged; brier denominator drops
    recs2 = list(recs)
    recs2[0] = ResultRecord("DEV-001", "mA", recs2[0].predicted_label, recs2[0].gold_label,
                            "clear", None).finalize()
    m = _subset_metrics(recs2)
    assert m["accuracy"] == 1.0                                   # classification NOT erased
    assert m["denominators"]["accuracy"] == 27
    assert m["denominators"]["brier"] == 26                       # confidence denominator changed
    assert m["confidence_audit"]["n_missing"] == 1
    assert m["confidence_coverage_warning"] is True


def test_invalid_confidence_flagged_and_not_zero():
    recs = [_rec("solid", "solid", 0.8), _rec("solid", "solid", 1.5, dev="DEV-002")]
    # 1.5 is INVALID -> excluded from Brier (not coerced to 0.0 which would be VALID)
    assert brier_top_label(recs) == pytest.approx(0.04)
    audit = confidence_audit(recs)
    assert audit["n_invalid"] == 1 and audit["n_valid"] == 1


# ========================= 4. small-n label reporting =========================

def test_all_four_labels_present_even_with_n2():
    res = validate_result_records(_full_raw())
    report = build_report(res.records, synthetic=True)
    per_label = report["models"]["mA"]["per_label_clear"]
    assert set(per_label) == {"solid", "overclaim", "correlation_vs_causation", "mechanism_vs_evidence"}
    assert per_label["correlation_vs_causation"]["small_n"] is True
    assert per_label["mechanism_vs_evidence"]["descriptive_only"] is True
    text = render_report_text(report)
    for lbl in ("solid", "overclaim", "correlation_vs_causation", "mechanism_vs_evidence"):
        assert lbl in text


def test_macro_states_included_and_excluded_labels():
    res = validate_result_records(_full_raw())
    m = build_report(res.records, synthetic=True)["models"]["mA"]
    assert set(m["macro_included_labels"]) == {"solid", "overclaim"}       # n>=5
    assert m["macro_excluded_labels"]["correlation_vs_causation"] == "n<5"
    assert m["macro_excluded_labels"]["mechanism_vs_evidence"] == "n<5"


# ========================= 5. frozen bins / thresholds / costs =========================

@pytest.mark.parametrize("conf,expected_bin", [
    (0.0, 0), (0.2, 1), (0.4, 2), (0.6, 3), (0.8, 4), (1.0, 4),
    (0.19, 0), (0.99, 4),
])
def test_bin_boundaries(conf, expected_bin):
    assert _bin_index(conf, FIVE_BIN_EDGES) == expected_bin


def test_five_edges_are_frozen():
    assert FIVE_BIN_EDGES == (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)


def test_reliability_retains_all_five_bins_including_empty():
    recs = [_rec("solid", "solid", 0.85), _rec("solid", "overclaim", 0.05, dev="DEV-002")]
    table = reliability_table(recs, FIVE_BIN_EDGES)
    assert len(table) == 5 and table[2]["n"] == 0 and table[2]["accuracy"] is None
    assert assert_reliability_bins_complete(table) == []


def test_assert_reliability_bins_complete_detects_truncation():
    table = reliability_table([_rec("solid", "solid", 0.85)])[:3]
    assert any("retain all" in e for e in assert_reliability_bins_complete(table))


def test_ece_denominator_is_valid_count():
    recs = [_rec("solid", "solid", 0.9), _rec("solid", "overclaim", 0.9, dev="DEV-002")]
    table = reliability_table(recs)
    assert ece_from_table(table, n_valid=2) == pytest.approx(abs(0.5 - 0.9))


def test_brier_binary_top_label_exact():
    recs = [_rec("solid", "solid", 0.8), _rec("solid", "overclaim", 0.6, dev="DEV-002")]
    assert brier_top_label(recs) == pytest.approx(0.20)


def test_risk_coverage_costed_and_involuntary_counted():
    recs = [_rec("solid", "solid", 0.9), _rec("solid", "overclaim", 0.3, dev="DEV-002"),
            _rec("solid", "solid", None, dev="DEV-003")]
    curve = {round(p["tau"], 1): p for p in risk_coverage_curve(recs)}
    assert curve[0.0]["n_involuntary_abstained"] == 1
    assert curve[0.0]["coverage_all"] == pytest.approx(2 / 3)
    assert curve[0.5]["n_covered"] == 1
    assert curve[0.5]["coverage_lost_all"] == pytest.approx(1 - 1 / 3)


def test_threshold_optimization_prohibited():
    with pytest.raises(CalibrationError):
        select_operating_threshold()


# ========================= 6. report status / provenance =========================

def test_report_status_banner_and_provenance():
    res = validate_result_envelope(_envelope(_full_raw()), EXPECTED_MANIFEST_ID, "a" * 64)
    report = build_report(res.records, provenance=res.provenance, synthetic=True)
    st = report["status"]
    assert "DEVELOPMENT CALIBRATION — NOT HOLDOUT" in st["banner"]
    assert st["manifest_id"] == EXPECTED_MANIFEST_ID
    assert st["public_commitment"] == "a" * 64
    assert st["protocol_version"] == "6.1"
    assert st["synthetic_fixture"] is True
    assert report["params"]["abstention_cost_model"].startswith("coverage_lost_all")


def test_render_marks_not_holdout_and_synthetic():
    res = validate_result_envelope(_envelope(_full_raw()), EXPECTED_MANIFEST_ID, "a" * 64)
    text = render_report_text(build_report(res.records, provenance=res.provenance, synthetic=True))
    assert "DEVELOPMENT CALIBRATION — NOT HOLDOUT" in text
    assert "SYNTHETIC FIXTURE" in text
    assert "mA" in text


def test_build_report_is_deterministic():
    res = validate_result_records(_full_raw())
    assert build_report(res.records, synthetic=True) == build_report(res.records, synthetic=True)
