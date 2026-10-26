"""Tests for the Phase 6.3 claim-forensics report prototype (agent_arena.forensic_report).

All fixtures are SYNTHETIC (loaded from analysis/phase6_3_report_prototype/fixtures).
The tests exercise the frozen taxonomy, the biological mechanism_vs_evidence scope,
Phase 6.1 confidence semantics (no 0.0 coercion), missing/invalid preservation, the
parser-failure failure report, the no-invented-facts guards, determinism, and leakage
rejection.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent_arena import forensic_report as fr
from agent_arena.forensic_report import (
    FORENSIC_LABELS,
    REPORT_SCHEMA_VERSION,
    VERDICT_TITLES,
    ForensicReportError,
    build_forensic_report,
    canonical_report_bytes,
    render_executive_summary,
    render_forensic_report_markdown,
    report_digest,
    validate_forensic_report,
    validate_forensic_report_input,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "analysis" / "phase6_3_report_prototype" / "fixtures"


def load(name: str) -> dict:
    return json.loads((FIXTURES_DIR / f"{name}.json").read_text())


def all_fixture_names() -> list[str]:
    return sorted(p.stem for p in FIXTURES_DIR.glob("*.json"))


def base_input(**over) -> dict:
    inp = {
        "meta": {"synthetic_fixture": True, "generated_at": "2026-08-05T12:00:00+00:00",
                 "report_id": "FR-TEST"},
        "claim": {"claim_text": "Drug Q reduced a marker by 30% in one small trial."},
        "verdict": {"predicted_label": "overclaim", "confidence": 0.7},
    }
    for k, v in over.items():
        inp[k] = v
    return inp


# ---------------------------------------------------------------------------
# All fixtures build and validate
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name", all_fixture_names())
def test_every_fixture_builds_and_validates(name):
    report = build_forensic_report(load(name))
    ok, errs = validate_forensic_report(report)
    assert ok, f"{name}: {errs}"
    assert report["report_schema_version"] == REPORT_SCHEMA_VERSION
    assert report["synthetic_fixture"] is True


# ---------------------------------------------------------------------------
# All four frozen labels + label/title consistency
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name,label", [
    ("01_solid", "solid"),
    ("02_overclaim", "overclaim"),
    ("03_correlation_vs_causation", "correlation_vs_causation"),
    ("04_mechanism_vs_evidence", "mechanism_vs_evidence"),
])
def test_four_labels_present_and_titled(name, label):
    report = build_forensic_report(load(name))
    assert report["verdict"]["predicted_label"] == label
    assert report["verdict"]["verdict_title"] == VERDICT_TITLES[label]


def test_all_four_labels_have_titles():
    assert set(VERDICT_TITLES) == set(FORENSIC_LABELS)


def test_mechanism_vs_evidence_is_biologically_scoped():
    title = VERDICT_TITLES["mechanism_vs_evidence"].lower()
    # scope must reference biological/preclinical → human clinical, not a generic mechanism
    assert "human clinical" in title
    assert "preclinical" in title or "biological" in title
    report = build_forensic_report(load("04_mechanism_vs_evidence"))
    md = render_forensic_report_markdown(report)
    assert "human clinical benefit" in md


# ---------------------------------------------------------------------------
# Unknown label rejected
# ---------------------------------------------------------------------------

def test_unknown_label_rejected():
    with pytest.raises(ForensicReportError):
        build_forensic_report(base_input(verdict={"predicted_label": "made_up_label"}))
    ok, errs = validate_forensic_report_input(base_input(verdict={"predicted_label": "made_up_label"}))
    assert not ok
    assert any("frozen label" in e for e in errs)


# ---------------------------------------------------------------------------
# Confidence semantics — VALID / MISSING / INVALID, no 0.0 coercion
# ---------------------------------------------------------------------------

def test_missing_confidence_not_coerced_to_zero():
    report = build_forensic_report(base_input(verdict={"predicted_label": "overclaim"}))
    assert report["verdict"]["confidence_status"] == "MISSING"
    assert report["verdict"]["confidence_value"] is None


def test_explicit_null_confidence_is_missing():
    report = build_forensic_report(base_input(verdict={"predicted_label": "overclaim", "confidence": None}))
    assert report["verdict"]["confidence_status"] == "MISSING"
    assert report["verdict"]["confidence_value"] is None


def test_bool_confidence_rejected_as_invalid():
    report = build_forensic_report(base_input(verdict={"predicted_label": "overclaim", "confidence": True}))
    assert report["verdict"]["confidence_status"] == "INVALID"
    assert report["verdict"]["confidence_value"] is None
    # and a report whose confidence_value is a bool must fail output validation
    report["verdict"]["confidence_value"] = True
    ok, errs = validate_forensic_report(report)
    assert not ok
    assert any("boolean" in e for e in errs)


def test_out_of_range_confidence_is_invalid():
    for bad in (1.5, -0.1):
        report = build_forensic_report(base_input(verdict={"predicted_label": "overclaim", "confidence": bad}))
        assert report["verdict"]["confidence_status"] == "INVALID"
        assert report["verdict"]["confidence_value"] is None


def test_zero_confidence_is_valid_not_missing():
    report = build_forensic_report(base_input(verdict={"predicted_label": "overclaim", "confidence": 0.0}))
    assert report["verdict"]["confidence_status"] == "VALID"
    assert report["verdict"]["confidence_value"] == 0.0


def test_invalid_confidence_preserved_from_fixture():
    report = build_forensic_report(load("06_invalid_confidence"))
    assert report["verdict"]["confidence_status"] == "INVALID"
    assert report["verdict"]["confidence_value"] is None


# ---------------------------------------------------------------------------
# Parser failure produces a failure report, not a verdict
# ---------------------------------------------------------------------------

def test_parser_failure_status_and_no_verdict():
    report = build_forensic_report(load("08_parser_failure"))
    assert report["analysis_status"] == "parser_failure"
    assert report["verdict"]["predicted_label"] is None
    assert "parser failure" in report["verdict"]["verdict_title"].lower()
    assert report["provenance"]["parser_status"] == "failed"


def test_parser_failure_cannot_masquerade_as_complete():
    # parse_ok False overrides an over-optimistic analysis_status=complete
    raw = {
        "meta": {"synthetic_fixture": True, "analysis_status": "complete"},
        "parser": {"parse_ok": False, "error": "broken"},
        "claim": {"claim_text": "A synthetic claim."},
        "verdict": {"predicted_label": "solid", "confidence": 0.99},
    }
    report = build_forensic_report(raw)
    assert report["analysis_status"] == "parser_failure"
    assert report["verdict"]["predicted_label"] is None


def test_insufficient_input_when_no_label():
    raw = {"meta": {"synthetic_fixture": True}, "claim": {"claim_text": "A synthetic claim."}}
    report = build_forensic_report(raw)
    assert report["analysis_status"] == "insufficient_input"
    assert report["verdict"]["predicted_label"] is None


# ---------------------------------------------------------------------------
# Missing data stays explicit; nothing invented
# ---------------------------------------------------------------------------

def test_empty_evidence_list_preserved_and_visible():
    report = build_forensic_report(load("12_empty_evidence"))
    assert report["evidence"]["evidence_items"] == []
    assert any("empty" in w for w in report["provenance"]["warnings"])
    md = render_forensic_report_markdown(report)
    assert "No evidence items supplied" in md


def test_missing_source_not_invented():
    report = build_forensic_report(load("07_missing_evidence"))
    assert report["claim"]["claim_source_reference"] is None
    for it in report["evidence"]["evidence_items"]:
        assert it["source_reference"] is None or isinstance(it["source_reference"], str)


def test_missing_reader_impact_is_unknown():
    report = build_forensic_report(load("12_empty_evidence"))
    assert report["reader_impact"]["risk_level"] == "unknown"


# ---------------------------------------------------------------------------
# Rewrite guard — no unsupported new facts
# ---------------------------------------------------------------------------

def test_rewrite_with_new_number_is_blocked():
    report = build_forensic_report(load("10_no_safe_rewrite"))
    rev = report["recommended_revision"]
    assert rev["rewrite_guard"]["status"] == "blocked"
    assert rev["defensible_rewrite"] is None
    assert rev["rewrite_available"] is False
    assert rev["rewrite_verification"] == "blocked_unsupported_new_facts"
    assert rev["rewrite_guard"]["unsupported_new_facts"]


def test_rewrite_without_new_facts_is_clean_but_unverified():
    raw = base_input(recommended_revision={
        "defensible_rewrite": "In one small trial, drug Q reduced a marker by 30%."})
    report = build_forensic_report(raw)
    rev = report["recommended_revision"]
    assert rev["rewrite_guard"]["status"] == "clean"
    assert rev["rewrite_available"] is True
    # passing the numeric guard is NOT verification
    assert rev["rewrite_verification"] == "unverified_proposal"
    assert "UNVERIFIED" in rev["rewrite_verification_note"]


# --- Curator rewrite-safety gate: six required conditions -----------------------

def test_no_rewrite_supplied():
    report = build_forensic_report(base_input())  # no recommended_revision block
    rev = report["recommended_revision"]
    assert rev["defensible_rewrite"] is None
    assert rev["rewrite_available"] is False
    assert rev["rewrite_verification"] == "no_rewrite_supplied"


def test_no_safe_rewrite_available_is_stated():
    report = build_forensic_report(load("10_no_safe_rewrite"))
    full = render_forensic_report_markdown(report)
    execmd = render_executive_summary(report)
    assert "No safe rewrite available" in full
    assert "none available" in execmd


def test_supplied_rewrite_marked_unverified_not_verified():
    raw = base_input(recommended_revision={
        "defensible_rewrite": "In one small trial, drug Q reduced a marker by 30%.",
        "rewrite_rationale": "Bounds the claim to the trial."})
    report = build_forensic_report(raw)
    assert report["recommended_revision"]["rewrite_verification"] == "unverified_proposal"
    full = render_forensic_report_markdown(report)
    execmd = render_executive_summary(report)
    # the unverified-proposal limitation is preserved in BOTH views
    assert "Unverified proposal" in full
    assert "unverified proposal" in execmd.lower()
    # never labelled as evidence/factually verified
    for bad in ("evidence-verified", "factually verified", "verified as accurate", "confirmed accurate"):
        assert bad not in full.lower()
        assert bad not in execmd.lower()


def test_builder_and_renderers_never_invent_rewrite_text():
    # a distinctive rewrite string must appear verbatim and nothing is synthesized when absent
    marker = "ZZ-DISTINCT-REWRITE-STRING"
    raw = base_input(recommended_revision={
        "defensible_rewrite": f"In one small trial, drug Q reduced a marker by 30%. {marker}"})
    report = build_forensic_report(raw)
    assert marker in report["recommended_revision"]["defensible_rewrite"]
    # when no rewrite is supplied, defensible_rewrite is null (never fabricated)
    report2 = build_forensic_report(base_input())
    assert report2["recommended_revision"]["defensible_rewrite"] is None
    full2 = render_forensic_report_markdown(report2)
    assert "No safe rewrite available" in full2


def test_report_validator_rejects_present_rewrite_not_marked_unverified():
    raw = base_input(recommended_revision={
        "defensible_rewrite": "In one small trial, drug Q reduced a marker by 30%."})
    report = build_forensic_report(raw)
    # tamper: a present rewrite mislabeled as no_rewrite_supplied must fail validation
    report["recommended_revision"]["rewrite_verification"] = "no_rewrite_supplied"
    ok, errs = validate_forensic_report(report)
    assert not ok
    assert any("unverified_proposal" in e for e in errs)


def test_failure_mode_requires_rationale():
    raw = base_input(failure_modes={"detected": [{"mode": "conclusion_exceeds_results", "rationale": ""}]})
    ok, errs = validate_forensic_report_input(raw)
    assert not ok
    assert any("rationale" in e for e in errs)


def test_unknown_failure_mode_rejected():
    raw = base_input(failure_modes={"detected": [{"mode": "not_a_mode", "rationale": "x"}]})
    ok, errs = validate_forensic_report_input(raw)
    assert not ok
    assert any("failure mode" in e for e in errs)


# ---------------------------------------------------------------------------
# Classification is not proof of falsity
# ---------------------------------------------------------------------------

def test_classification_not_presented_as_falsity():
    report = build_forensic_report(load("02_overclaim"))
    assert "not, by itself, proof that the claim is factually false" in report["verdict"]["classification_note"]
    md = render_forensic_report_markdown(report)
    assert "factually false" in md


# ---------------------------------------------------------------------------
# Risk vocabulary
# ---------------------------------------------------------------------------

def test_invalid_risk_level_rejected():
    raw = base_input(reader_impact={"risk_level": "catastrophic"})
    ok, errs = validate_forensic_report_input(raw)
    assert not ok
    assert any("risk_level" in e for e in errs)


@pytest.mark.parametrize("level", ["low", "moderate", "high", "critical", "unknown"])
def test_valid_risk_levels_accepted(level):
    report = build_forensic_report(base_input(reader_impact={"risk_level": level}))
    assert report["reader_impact"]["risk_level"] == level


# ---------------------------------------------------------------------------
# Executive summary and full report share the same verdict
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name", ["01_solid", "02_overclaim", "04_mechanism_vs_evidence",
                                  "06_invalid_confidence", "09_high_reader_impact"])
def test_exec_and_full_share_verdict(name):
    report = build_forensic_report(load(name))
    full = render_forensic_report_markdown(report)
    execmd = render_executive_summary(report)
    title = report["verdict"]["verdict_title"]
    assert title in full and title in execmd
    status = report["verdict"]["confidence_status"]
    assert status in full and status in execmd
    assert report["reader_impact"]["risk_level"] in execmd


def test_exec_summary_preserves_material_uncertainty_and_warnings():
    report = build_forensic_report(load("06_invalid_confidence"))  # INVALID confidence → material
    execmd = render_executive_summary(report)
    assert "INVALID" in execmd
    # warnings must be visible in exec summary
    for w in report["provenance"]["warnings"]:
        # at least the confidence warning should surface
        if "INVALID" in w:
            assert "Warnings" in execmd


def test_markdown_includes_all_material_warnings():
    report = build_forensic_report(load("10_no_safe_rewrite"))
    md = render_forensic_report_markdown(report)
    assert report["provenance"]["warnings"]  # there are warnings
    for w in report["provenance"]["warnings"]:
        assert w in md


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name", all_fixture_names())
def test_deterministic_json_and_markdown(name):
    raw = load(name)
    r1 = build_forensic_report(raw)
    r2 = build_forensic_report(raw)
    assert canonical_report_bytes(r1) == canonical_report_bytes(r2)
    assert render_forensic_report_markdown(r1) == render_forensic_report_markdown(r2)
    assert render_executive_summary(r1) == render_executive_summary(r2)
    # digest recomputable
    assert report_digest(r1) == r1["provenance"]["report_generation_digest_sha256"]


def test_one_char_input_change_changes_digest():
    raw = load("02_overclaim")
    r1 = build_forensic_report(raw)
    raw2 = json.loads(json.dumps(raw))
    raw2["claim"]["claim_text"] = raw2["claim"]["claim_text"] + "."
    r2 = build_forensic_report(raw2)
    assert (r1["provenance"]["report_generation_digest_sha256"]
            != r2["provenance"]["report_generation_digest_sha256"])
    assert (r1["provenance"]["input_digest_sha256"]
            != r2["provenance"]["input_digest_sha256"])


# ---------------------------------------------------------------------------
# Leakage / private material rejection
# ---------------------------------------------------------------------------

# Forbidden tokens are ASSEMBLED AT RUNTIME from fragments so that no literal
# canonical/BIAA/HLD/DEV id or private path appears in this tracked test file.
_LEAK_TOKENS = [
    "study-" + "forensics-" + "12",
    "BIAA" + "-7",
    "HLD" + "-3",
    "DEV" + "-0001",
    "/Us" + "ers/someone/secret",
    "AgentArena_" + "IAA_Private",
    "internal_" + "only/map",
]


@pytest.mark.parametrize("leak", _LEAK_TOKENS)
def test_private_identifiers_and_paths_rejected(leak):
    raw = base_input()
    raw["claim"]["claim_text"] = f"A claim referencing {leak} somehow."
    ok, errs = validate_forensic_report_input(raw)
    assert not ok
    assert any("private" in e for e in errs)
    with pytest.raises(ForensicReportError):
        build_forensic_report(raw)


# ---------------------------------------------------------------------------
# Unexpected fields rejected where frozen
# ---------------------------------------------------------------------------

def test_unexpected_top_level_field_rejected():
    raw = base_input()
    raw["surprise"] = 1
    ok, errs = validate_forensic_report_input(raw)
    assert not ok
    assert any("unexpected" in e for e in errs)


def test_unexpected_evidence_item_field_rejected():
    raw = base_input(evidence={"evidence_items": [{"text": "x", "tier": "animal", "bogus": 1}]})
    ok, errs = validate_forensic_report_input(raw)
    assert not ok
    assert any("unexpected" in e for e in errs)


# ---------------------------------------------------------------------------
# Visibility of status/version/synthetic flag
# ---------------------------------------------------------------------------

def test_schema_version_and_synthetic_flag_visible():
    report = build_forensic_report(base_input())
    assert report["report_schema_version"] == REPORT_SCHEMA_VERSION
    assert "synthetic_fixture" in report
    md = render_forensic_report_markdown(report)
    assert REPORT_SCHEMA_VERSION in md


def test_synthetic_defaults_true_when_absent():
    raw = base_input(meta={"generated_at": "2026-08-05T12:00:00+00:00"})
    report = build_forensic_report(raw)
    assert report["synthetic_fixture"] is True
    assert any("synthetic_fixture" in w for w in report["provenance"]["warnings"])


# ---------------------------------------------------------------------------
# No hidden threshold / model-selection logic
# ---------------------------------------------------------------------------

def test_no_threshold_or_model_selection_logic():
    src = Path(fr.__file__).read_text()
    for forbidden in ("select_operating_threshold", "argmax", "def select_", "optimize_threshold"):
        assert forbidden not in src, f"forbidden construct present: {forbidden}"
    # no public function chooses a winner / threshold
    public = [n for n in dir(fr) if not n.startswith("_")]
    assert not any(n.startswith(("select", "choose", "optimize", "rank_best")) for n in public)
