"""Phase 7B first vertical slice — artifact binding gate tests.

Tests A–G exercise the CLAIM → PROVENANCE → EVIDENCE → INTERNAL FINDING →
CLIENT FINDING → SYMMETRY → FINAL BINDING chain on one synthetic, generic
pipeline-QA fixture (no LaVita identity). Failing variants are derived by mutation.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from inspektorium.audit.integrity.artifact_binding import (
    CLAIM_LABELS,
    QA_ARTIFACT_SOURCE_BINDING_DRIFT,
    QA_ASYMMETRIC_EVIDENCE_SELECTION,
    QA_SUMMARY_STRENGTH_ESCALATION,
    SYSTEM_QA_CODES,
    check_evidence_symmetry,
    compute_content_fingerprint,
    final_binding_check,
    load_forensic_record,
)
from inspektorium.audit.schemas import ClaimProvenance

FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "audit"
    / "pipeline_qa"
    / "qa_evidence_symmetry_mixed_outcomes.json"
)


def base_record():
    """Fresh, unmutated record for every test."""
    return load_forensic_record(FIXTURE)


# --- Test A — complete representation passes -------------------------------------


def test_a_complete_representation_passes():
    rec = base_record()
    result = final_binding_check(rec)
    assert result.releasable is True
    assert result.findings == []
    assert result.blocker_count == 0 and result.major_count == 0
    # the symmetry primitive alone is also clean
    assert check_evidence_symmetry(rec) == []


# --- Test B — favorable / qualifying evidence omitted ---------------------------


def test_b_favorable_evidence_omitted_flags_asymmetry():
    rec = base_record()
    rec.client_findings[0].referenced_evidence_ids = ["E1"]  # drop E2 (favorable)
    result = final_binding_check(rec)
    assert result.releasable is False
    assert QA_ASYMMETRIC_EVIDENCE_SELECTION in result.codes()
    sym = check_evidence_symmetry(rec)
    assert [f.code for f in sym] == [QA_ASYMMETRIC_EVIDENCE_SELECTION]
    assert "E2" in sym[0].refs


# --- Test C — opposite-side evidence omitted (direction-neutral) -----------------


def test_c_opposite_side_evidence_omitted_flags_asymmetry():
    rec = base_record()
    rec.client_findings[0].referenced_evidence_ids = ["E2"]  # drop E1 (null biomarker)
    result = final_binding_check(rec)
    assert result.releasable is False
    assert QA_ASYMMETRIC_EVIDENCE_SELECTION in result.codes()
    # the gate is neutral about which side benefits: dropping either direction fails
    assert "E1" in check_evidence_symmetry(rec)[0].refs


# --- Test D — unknown evidence id -----------------------------------------------


def test_d_unknown_evidence_id_flags_binding_drift():
    rec = base_record()
    rec.client_findings[0].referenced_evidence_ids = ["E1", "E2", "E-does-not-exist"]
    result = final_binding_check(rec)
    assert result.releasable is False
    drift = [f for f in result.findings if f.code == QA_ARTIFACT_SOURCE_BINDING_DRIFT]
    assert any(f.check == "B" and "E-does-not-exist" in f.refs for f in drift)


# --- Test E — wrong parent finding id -------------------------------------------


def test_e_wrong_parent_finding_flags_binding_drift():
    rec = base_record()
    rec.client_findings[0].parent_finding_id = "F-wrong"
    result = final_binding_check(rec)
    assert result.releasable is False
    drift = [f for f in result.findings if f.code == QA_ARTIFACT_SOURCE_BINDING_DRIFT]
    assert any(f.check == "A" and "F-wrong" in f.refs for f in drift)


# --- Test F — provenance mismatch -----------------------------------------------


def test_f_provenance_mismatch_flags_binding_drift():
    rec = base_record()
    # A second frozen provenance exists; the client resolves against the wrong one.
    rec.provenance.append(
        ClaimProvenance(
            provenance_id="prov-2",
            exact_claim_text="An unrelated frozen claim.",
            source_id="src-other",
            provenance_state="published_literature",
        )
    )
    rec.client_findings[0].provenance_id = "prov-2"  # parent finding froze prov-1
    result = final_binding_check(rec)
    assert result.releasable is False
    drift = [f for f in result.findings if f.code == QA_ARTIFACT_SOURCE_BINDING_DRIFT]
    assert any(f.check == "F" for f in drift)


def test_f_unknown_provenance_also_flags_binding_drift():
    rec = base_record()
    rec.client_findings[0].provenance_id = "prov-nonexistent"
    result = final_binding_check(rec)
    assert result.releasable is False
    assert any(
        f.check == "F"
        for f in result.findings
        if f.code == QA_ARTIFACT_SOURCE_BINDING_DRIFT
    )


# --- Test G — strength escalation (semantic monotonicity, minimal) --------------


def test_g_strength_escalation_flags_monotonicity():
    rec = base_record()
    # parent allows "not_directly_established"; client claims a stronger negative status
    rec.client_findings[0].client_strength = "not_supported"
    result = final_binding_check(rec)
    assert result.releasable is False
    assert QA_SUMMARY_STRENGTH_ESCALATION in result.codes()


def test_g_equal_or_weaker_strength_passes():
    rec = base_record()
    rec.client_findings[0].client_strength = "mixed"  # weaker than parent ceiling
    result = final_binding_check(rec)
    assert QA_SUMMARY_STRENGTH_ESCALATION not in result.codes()


# --- Slice invariants -----------------------------------------------------------


def test_qa_codes_are_disjoint_from_claim_taxonomy():
    assert set(SYSTEM_QA_CODES).isdisjoint(set(CLAIM_LABELS))


def test_content_fingerprint_recomputes():
    rec = base_record()
    prov = rec.provenance[0]
    assert prov.content_fingerprint == compute_content_fingerprint(
        prov.exact_claim_text, prov.provenance_state
    )


def test_modelled_vs_literature_fingerprints_differ():
    text = "42% of the body's cells renew within roughly 75 days."
    assert compute_content_fingerprint(text, "modelled") != compute_content_fingerprint(
        text, "published_literature"
    )


def test_loader_rejects_private_path_leakage(tmp_path):
    data = json.loads(FIXTURE.read_text())
    # Synthetic private-path counterexample; no real account or home directory.
    data["provenance"][0]["canonical_url"] = "/" + "Users/fixture-user/private/notes.md"
    bad = tmp_path / "leaky.json"
    bad.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="private identity/path"):
        load_forensic_record(bad)
