"""Tests for the Phase 6.4 paired comparison generator (SYNTHETIC envelopes only).

These synthetic envelopes are illustrative fixtures built with the frozen 8/15/2/2 GOLD
aggregate and the tracked public manifest binding. They do NOT read, represent, simulate, or
imply the real private Phase 6.2 / 6.4B envelopes or real Agent Arena performance. The test
never touches any file in the private envelopes tree.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from agent_arena.calibration import load_public_manifest_binding

# --- load the generator module from its analysis/ path (not on the package path) ----
_GEN_PATH = (Path(__file__).resolve().parents[1]
             / "analysis" / "phase6_4_prompt_only_results" / "build_paired_comparison.py")
_spec = importlib.util.spec_from_file_location("build_paired_comparison", _GEN_PATH)
bpc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bpc)

MANIFEST_ID, COMMITMENT = load_public_manifest_binding(repo_root=Path(__file__).resolve().parents[1])

# Fixed 27-slot gold layout with the frozen 8/15/2/2 aggregate; DEV-0013 is development_only.
_GOLD_LAYOUT = (
    ["solid"] * 8
    + ["overclaim"] * 15
    + ["correlation_vs_causation"] * 2
    + ["mechanism_vs_evidence"] * 2
)
_DEV_ONLY = "DEV-0013"


def _dev(i: int) -> str:
    return f"DEV-{i:04d}"


def _arm_envelope(arm: str, *, wrong=None, conf=None):
    """Synthetic envelope for one arm. ``wrong`` maps dev_id -> a wrong predicted label;
    ``conf`` maps dev_id -> confidence (default 0.9)."""
    wrong = wrong or {}
    conf = conf or {}
    exp = bpc.EXPECTED_RUNS[arm]
    records = []
    for idx, gold in enumerate(_GOLD_LAYOUT, start=1):
        dev = _dev(idx)
        pred = wrong.get(dev, gold)
        records.append({
            "dev_id": dev,
            "model": exp["model"],
            "predicted_label": pred,
            "gold_label": gold,
            "stratum": "development_only" if dev == _DEV_ONLY else "clear",
            "confidence": conf.get(dev, 0.9),
        })
    return {
        "envelope_version": "6.2.0",
        "protocol_version": "6.1",
        "manifest_id": MANIFEST_ID,
        "public_commitment": COMMITMENT,
        "run_id": exp["run_id"],
        "model": exp["model"],
        "provider": "anthropic",
        "prompt_contract_version": exp["contract_id"],
        "generated_at": "2026-01-01T00:00:00+00:00",
        "expected_record_count": 27,
        "declared_gold_aggregate": {
            "solid": 8, "overclaim": 15, "correlation_vs_causation": 2,
            "mechanism_vs_evidence": 2, "total": 27},
        "records": records,
    }


# ---------------------------------------------------------------------------
# Small pure helpers
# ---------------------------------------------------------------------------

def test_leakage_scan_flags_forbidden_tokens():
    # SYNTHETIC placeholder ids only (9xx range) — never real canonical/BIAA/HLD ids; these
    # merely prove the detector fires, matching the tracked test convention.
    assert bpc.leakage_scan("nothing to see") == []
    assert bpc.leakage_scan("study-forensics-901 here")
    assert bpc.leakage_scan("BIAA-901 present")
    assert bpc.leakage_scan("HLD-901 present")
    assert bpc.leakage_scan('{"salt": "x"}')


def test_parse_completion_counts_failures():
    good = [{"dev_id": _dev(i), "predicted_label": "solid"} for i in range(1, 28)]
    pc = bpc.parse_completion(good)
    assert pc["parse_ok"] == 27 and pc["parse_failures"] == 0
    bad = good[:-1] + [{"dev_id": _dev(27), "predicted_label": "NOT_A_LABEL"}]
    pcb = bpc.parse_completion(bad)
    assert pcb["parse_ok"] == 26 and pcb["parse_failures"] == 1
    assert pcb["parse_failure_dev_ids"] == [_dev(27)]


def test_cross_arm_pairing_identical_and_mismatch():
    aa = bpc.validate_one("agent_arena", _arm_envelope("agent_arena"), MANIFEST_ID, COMMITMENT)
    po = bpc.validate_one("prompt_only", _arm_envelope("prompt_only"), MANIFEST_ID, COMMITMENT)
    pairing = bpc.cross_arm_pairing(aa, po)
    assert pairing["all_pass"] is True
    assert pairing["dev_id_set_identical_across_arms"] is True
    assert pairing["gold_label_identical_per_paired_dev"] is True
    assert pairing["stratum_identical_per_paired_dev"] is True

    # a gold-label mismatch on one paired DEV must be detected
    po_env = _arm_envelope("prompt_only")
    po_env["records"][0]["gold_label"] = "overclaim"  # DEV-0001 gold flipped -> breaks aggregate
    po_env["declared_gold_aggregate"] = {  # keep envelope self-consistent so validate_one still runs
        "solid": 7, "overclaim": 16, "correlation_vs_causation": 2,
        "mechanism_vs_evidence": 2, "total": 27}
    po_bad = bpc.validate_one("prompt_only", po_env, MANIFEST_ID, COMMITMENT)
    pairing_bad = bpc.cross_arm_pairing(aa, po_bad)
    assert pairing_bad["gold_label_identical_per_paired_dev"] is False
    assert _dev(1) in pairing_bad["gold_mismatch_dev_ids"]
    assert pairing_bad["all_pass"] is False


# ---------------------------------------------------------------------------
# Per-arm integrity
# ---------------------------------------------------------------------------

def test_validate_one_clean_envelope_passes():
    integ = bpc.validate_one("agent_arena", _arm_envelope("agent_arena"), MANIFEST_ID, COMMITMENT)
    assert integ["all_pass"] is True
    assert integ["confidence_counts"] == {"valid": 27, "missing": 0, "invalid": 0}
    assert integ["parser_completion"]["parse_ok"] == 27


def test_validate_one_detects_tampering():
    # wrong run id
    env = _arm_envelope("agent_arena")
    env["run_id"] = "AA-6.2-RUN-deadbeef"
    integ = bpc.validate_one("agent_arena", env, MANIFEST_ID, COMMITMENT)
    assert integ["all_pass"] is False
    assert any(c["check"] == "run_id_matches_expected" and not c["pass"] for c in integ["checks"])

    # unexpected record field
    env2 = _arm_envelope("agent_arena")
    env2["records"][0]["canonical_id"] = "study-forensics-901"  # SYNTHETIC placeholder
    integ2 = bpc.validate_one("agent_arena", env2, MANIFEST_ID, COMMITMENT)
    assert integ2["all_pass"] is False
    assert any(c["check"] == "records_no_unexpected_fields" and not c["pass"]
               for c in integ2["checks"])
    assert any(c["check"] == "no_identity_leakage" and not c["pass"] for c in integ2["checks"])

    # zero-confidence coercion artifact
    env3 = _arm_envelope("agent_arena", conf={_dev(1): 0.0})
    integ3 = bpc.validate_one("agent_arena", env3, MANIFEST_ID, COMMITMENT)
    assert any(c["check"] == "no_zero_coercion_artifact" and not c["pass"] for c in integ3["checks"])


# ---------------------------------------------------------------------------
# End-to-end paired comparison
# ---------------------------------------------------------------------------

def _build(aa_env, po_env):
    return bpc.build_all(aa_env, po_env, MANIFEST_ID, COMMITMENT)


def test_paired_comparison_asymmetric_correctness():
    # Agent Arena perfect; prompt-only wrong on DEV-0011 (low conf) and DEV-0013 (high conf).
    aa_env = _arm_envelope("agent_arena")
    po_env = _arm_envelope(
        "prompt_only",
        wrong={_dev(11): "solid", _dev(13): "solid"},
        conf={_dev(11): 0.7, _dev(13): 0.9},
    )
    built = _build(aa_env, po_env)
    cmp = built["paired"]

    assert cmp["accuracy"]["agent_arena_all27"] == 1
    assert cmp["accuracy"]["prompt_only_all27"] == pytest.approx(25 / 27)
    assert cmp["accuracy"]["difference_agent_arena_minus_prompt_only"] == pytest.approx(2 / 27)

    # frozen sign convention: Brier(PO) - Brier(AA) > 0 (AA lower is better)
    assert cmp["brier_top_label_valid"]["difference_prompt_only_minus_agent_arena"] > 0

    pt = cmp["paired_correctness_table"]
    assert pt["both_correct"] == 25
    assert pt["agent_arena_correct_prompt_only_incorrect"] == 2
    assert pt["agent_arena_incorrect_prompt_only_correct"] == 0
    assert pt["both_incorrect"] == 0
    assert pt["dev_ids"]["agent_arena_only"] == [_dev(11), _dev(13)]

    assert cmp["prediction_disagreements"]["n"] == 2
    dis_ids = {d["dev_id"] for d in cmp["prediction_disagreements"]["detail"]}
    assert dis_ids == {_dev(11), _dev(13)}

    # only DEV-0013 (conf 0.9) is a high-confidence error
    assert cmp["high_confidence_errors"]["prompt_only"]["n"] == 1
    assert cmp["high_confidence_errors"]["agent_arena"]["n"] == 0
    assert cmp["high_confidence_errors"]["difference_prompt_only_minus_agent_arena"] == 1

    assert cmp["accuracy_ceiling"] is False
    assert cmp["parser_completion"]["agent_arena"]["parse_ok"] == 27
    assert cmp["parser_completion"]["prompt_only"]["parse_ok"] == 27
    # never pooled
    assert cmp["prohibitions_upheld"]["no_54_case_pool"] is True


def test_paired_comparison_reports_accuracy_ceiling():
    aa_env = _arm_envelope("agent_arena")
    po_env = _arm_envelope("prompt_only")  # also perfect
    cmp = _build(aa_env, po_env)["paired"]
    assert cmp["accuracy"]["agent_arena_all27"] == 1
    assert cmp["accuracy"]["prompt_only_all27"] == 1
    assert cmp["accuracy_ceiling"] is True
    # even at a ceiling the arms are NOT called equivalent — Brier still reported per arm
    assert cmp["brier_top_label_valid"]["agent_arena"] is not None
    assert cmp["brier_top_label_valid"]["prompt_only"] is not None


def test_by_gold_label_keeps_all_four_labels_and_small_n_flags():
    cmp = _build(_arm_envelope("agent_arena"),
                 _arm_envelope("prompt_only", wrong={_dev(11): "solid"}))["paired"]
    for arm in ("agent_arena", "prompt_only"):
        g = cmp["by_gold_label_all27"][arm]
        assert set(g) == {"solid", "overclaim",
                          "correlation_vs_causation", "mechanism_vs_evidence"}
        assert g["correlation_vs_causation"]["small_n"] is True
        assert g["mechanism_vs_evidence"]["descriptive_only"] is True
        assert g["solid"]["small_n"] is False


def test_build_all_is_deterministic():
    aa_env = _arm_envelope("agent_arena")
    po_env = _arm_envelope("prompt_only", wrong={_dev(11): "solid", _dev(13): "solid"},
                           conf={_dev(11): 0.7, _dev(13): 0.9})
    one = _build(aa_env, po_env)["paired"]
    two = _build(aa_env, po_env)["paired"]
    assert json.dumps(one, sort_keys=True) == json.dumps(two, sort_keys=True)


def test_build_all_rejects_broken_binding():
    aa_env = _arm_envelope("agent_arena")
    aa_env["public_commitment"] = "0" * 64  # wrong commitment
    with pytest.raises(SystemExit):
        _build(aa_env, _arm_envelope("prompt_only"))
