"""Phase 5.05c IAA analyzer tests — synthetic fixtures only.

No real annotator answers exist; every fixture here is fabricated for structural
testing. Covers parsing/validation, agreement metrics (raw / Cohen / Fleiss),
soft-vs-serious disagreement, refusal on incomplete data, no gold mutation, and the
internal-vs-annotator-facing path guard.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

import pytest

from agent_arena import iaa_analysis as iaa
from agent_arena.iaa_analysis import (
    ResponseRow, cohen_kappa, fleiss_kappa, raw_agreement, classify_disagreements,
)

COLS = iaa.RESPONSE_COLUMNS
EXPECTED = {"BIAA-001", "BIAA-002", "BIAA-003"}


def _write_sheet(path: Path, rows: list[dict]) -> Path:
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in COLS})
    return path


def _row(bid, primary="", secondary="", confidence="", **kw):
    base = {"blind_case_id": bid, "primary_label": primary, "secondary_label": secondary,
            "confidence": confidence, "rationale": kw.get("rationale", "because"),
            "source_voice_clear": kw.get("svc", "yes"), "claim_isolated": kw.get("ci", "yes"),
            "evidence_matches_claim_strength": kw.get("emc", "no"),
            "recommended_human_review": kw.get("rhr", "no")}
    return base


def _completed_rows():
    return [
        _row("BIAA-001", "solid", confidence="0.9"),
        _row("BIAA-002", "overclaim", confidence="0.8"),
        _row("BIAA-003", "mechanism_vs_evidence", confidence="0.7"),
    ]


def _index(tmp: Path, mapping):
    p = tmp / "blind_case_index.csv"
    with p.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["blind_case_id", "real_case_id", "filename", "included_in_iaa_stats",
                    "packet_path", "sample_reason", "internal_notes"])
        for bid, (rid, fn) in mapping.items():
            w.writerow([bid, rid, fn, "yes", "", "", ""])
    return p


def _tasks(tmp: Path, gold):
    d = tmp / "tasks"
    d.mkdir()
    for fn, label in gold.items():
        (d / fn).write_text(f"id: {fn}\ngold_label: {label}\nprompt: x\n")
    return d


# --------------------------------------------------------------------------- parsing/validation
def test_valid_completed_sheet(tmp_path):
    p = _write_sheet(tmp_path / "a.csv", _completed_rows())
    v = iaa.validate_sheet(p, EXPECTED, "A")
    assert v.ok and v.completed and not v.is_blank_template
    assert v.n_completed == 3


def test_blank_template_detection(tmp_path):
    rows = [_row(b) for b in ["BIAA-001", "BIAA-002", "BIAA-003"]]
    p = _write_sheet(tmp_path / "blank.csv", rows)
    v = iaa.validate_sheet(p, EXPECTED, "A")
    assert v.is_blank_template and not v.completed
    assert v.ok  # a recognized template is not an error


def test_missing_row(tmp_path):
    p = _write_sheet(tmp_path / "a.csv", _completed_rows()[:2])
    v = iaa.validate_sheet(p, EXPECTED, "A")
    assert not v.ok
    assert any("missing expected blind_case_id" in e for e in v.errors)


def test_duplicate_blind_case_id(tmp_path):
    rows = _completed_rows() + [_row("BIAA-001", "solid", confidence="0.5")]
    p = _write_sheet(tmp_path / "a.csv", rows)
    v = iaa.validate_sheet(p, EXPECTED, "A")
    assert any("duplicate blind_case_id" in e for e in v.errors)


def test_unknown_blind_case_id(tmp_path):
    rows = _completed_rows() + [_row("BIAA-999", "solid", confidence="0.5")]
    # expected set must still include the 3, so treat BIAA-999 as unknown
    p = _write_sheet(tmp_path / "a.csv", rows)
    v = iaa.validate_sheet(p, EXPECTED, "A")
    assert any("unknown blind_case_id" in e for e in v.errors)


def test_invalid_label(tmp_path):
    rows = _completed_rows()
    rows[0]["primary_label"] = "not_a_label"
    p = _write_sheet(tmp_path / "a.csv", rows)
    v = iaa.validate_sheet(p, EXPECTED, "A")
    assert any("invalid primary_label" in e for e in v.errors)


def test_invalid_confidence(tmp_path):
    rows = _completed_rows()
    rows[0]["confidence"] = "1.7"
    rows[1]["confidence"] = "abc"
    p = _write_sheet(tmp_path / "a.csv", rows)
    v = iaa.validate_sheet(p, EXPECTED, "A")
    assert any("confidence out of range" in e for e in v.errors)
    assert any("non-numeric confidence" in e for e in v.errors)


def test_invalid_categorical_field(tmp_path):
    rows = _completed_rows()
    rows[0]["source_voice_clear"] = "maybe"
    p = _write_sheet(tmp_path / "a.csv", rows)
    v = iaa.validate_sheet(p, EXPECTED, "A")
    assert any("source_voice_clear='maybe'" in e for e in v.errors)


def test_primary_equals_secondary(tmp_path):
    rows = _completed_rows()
    rows[0]["secondary_label"] = "solid"  # same as primary
    p = _write_sheet(tmp_path / "a.csv", rows)
    v = iaa.validate_sheet(p, EXPECTED, "A")
    assert any("primary_label equals secondary_label" in e for e in v.errors)


def test_missing_rationale_is_warning_not_error(tmp_path):
    rows = _completed_rows()
    rows[0]["rationale"] = ""
    p = _write_sheet(tmp_path / "a.csv", rows)
    v = iaa.validate_sheet(p, EXPECTED, "A")
    assert v.ok
    assert any("rationale missing" in w for w in v.warnings)


# --------------------------------------------------------------------------- metrics
def test_raw_agreement():
    assert raw_agreement(["solid", "overclaim", "solid"], ["solid", "solid", "solid"]) == pytest.approx(2 / 3)


def test_cohen_kappa_known_example():
    a = ["solid", "solid", "overclaim", "overclaim"]
    b = ["solid", "overclaim", "overclaim", "overclaim"]
    assert cohen_kappa(a, b, ["solid", "overclaim"]) == pytest.approx(0.5)


def test_fleiss_kappa_perfect_and_intermediate():
    perfect = [["solid", "solid", "solid"], ["overclaim", "overclaim", "overclaim"]]
    assert fleiss_kappa(perfect, ["solid", "overclaim"]) == pytest.approx(1.0)
    inter = [["solid", "solid", "overclaim"], ["solid", "overclaim", "overclaim"]]
    assert fleiss_kappa(inter, ["solid", "overclaim"]) == pytest.approx(-1 / 3, abs=1e-6)


def test_soft_disagreement_detection():
    gold_map = {"BIAA-001": {"gold_label": "overclaim"}}
    rows = [ResponseRow("BIAA-001", primary_label="mechanism_vs_evidence",
                        secondary_label="overclaim", confidence=0.6)]
    res = classify_disagreements(rows, gold_map)
    assert len(res["soft"]) == 1 and not res["serious"]


def test_serious_disagreement_detection():
    gold_map = {"BIAA-001": {"gold_label": "overclaim"}}
    rows = [ResponseRow("BIAA-001", primary_label="solid",
                        secondary_label="", confidence=0.6)]
    res = classify_disagreements(rows, gold_map)
    assert len(res["serious"]) == 1 and not res["soft"]


def test_no_gold_label_mutation():
    gold_map = {"BIAA-001": {"gold_label": "overclaim"}}
    snapshot = dict(gold_map["BIAA-001"])
    rows = [ResponseRow("BIAA-001", primary_label="solid", confidence=0.6)]
    classify_disagreements(rows, gold_map)
    assert gold_map["BIAA-001"] == snapshot  # unchanged


# --------------------------------------------------------------------------- orchestration guards
def test_refusal_on_incomplete_data(tmp_path):
    idx = _index(tmp_path, {"BIAA-001": ("c1", "c1.yaml"), "BIAA-002": ("c2", "c2.yaml"),
                            "BIAA-003": ("c3", "c3.yaml")})
    tasks = _tasks(tmp_path, {"c1.yaml": "solid", "c2.yaml": "overclaim", "c3.yaml": "mechanism_vs_evidence"})
    blank = _write_sheet(tmp_path / "blank.csv", [_row(b) for b in EXPECTED])
    out = tmp_path / "results"
    res = iaa.analyze({"A": str(blank)}, idx, tasks, out, allow_partial=False)
    assert res["status"] == "REFUSED"
    assert not out.exists()  # no artifacts created from blank data


def test_internal_mapping_never_written_to_annotator_facing(tmp_path):
    idx = _index(tmp_path, {"BIAA-001": ("c1", "c1.yaml")})
    tasks = _tasks(tmp_path, {"c1.yaml": "solid"})
    bad = tmp_path / "annotator_facing" / "results"
    with pytest.raises(ValueError):
        iaa.analyze({"A": "x.csv"}, idx, tasks, bad)


def test_full_analysis_end_to_end(tmp_path):
    idx = _index(tmp_path, {"BIAA-001": ("c1", "c1.yaml"), "BIAA-002": ("c2", "c2.yaml"),
                            "BIAA-003": ("c3", "c3.yaml")})
    tasks = _tasks(tmp_path, {"c1.yaml": "solid", "c2.yaml": "overclaim", "c3.yaml": "mechanism_vs_evidence"})
    # three completed sheets that all match gold -> perfect agreement
    sheets = {}
    for aid in ("A", "B", "C"):
        sheets[aid] = str(_write_sheet(tmp_path / f"{aid}.csv", _completed_rows()))
    out = tmp_path / "run1"
    res = iaa.analyze(sheets, idx, tasks, out)
    assert res["status"] == "COMPLETE"
    m = res["metrics"]
    assert m["multi_rater"]["fleiss_kappa"] == pytest.approx(1.0)
    assert m["serious_disagreement_count"] == 0
    assert m["disposition"]["level"] == "STRONG"
    assert (out / "iaa_summary.json").exists() and (out / "input_manifest.json").exists()
    # gold YAML untouched
    assert "gold_label: solid" in (tasks / "c1.yaml").read_text()


def test_structure_validation_only_banner(tmp_path):
    idx = _index(tmp_path, {"BIAA-001": ("c1", "c1.yaml"), "BIAA-002": ("c2", "c2.yaml"),
                            "BIAA-003": ("c3", "c3.yaml")})
    tasks = _tasks(tmp_path, {"c1.yaml": "solid", "c2.yaml": "overclaim", "c3.yaml": "mechanism_vs_evidence"})
    blank = _write_sheet(tmp_path / "blank.csv", [_row(b) for b in EXPECTED])
    out = tmp_path / "partial"
    res = iaa.analyze({"A": str(blank)}, idx, tasks, out, allow_partial=True)
    assert res["status"] == "STRUCTURE_VALIDATION_ONLY"
    report = (out / "response_validation_report.md").read_text()
    assert "STRUCTURE VALIDATION ONLY — NO ANNOTATOR RESULTS." in report
    manifest = (out / "input_manifest.json").read_text()
    assert iaa.STUDY_TYPE in manifest
