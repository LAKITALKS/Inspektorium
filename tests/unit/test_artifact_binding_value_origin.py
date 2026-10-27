"""Phase 7B slice 2 — derived / source-reported value provenance.

Core invariant: SYSTEM-DERIVED VALUE != SOURCE-REPORTED VALUE. A value Agent Arena
derives must never be represented downstream as a source-reported / literature fact.
Failing variants are derived by mutation from one generic synthetic fixture.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from inspektorium.audit.artifact_binding import (
    CLAIM_LABELS,
    QA_ARTIFACT_SOURCE_BINDING_DRIFT,
    QA_MODEL_OUTPUT_TO_LITERATURE_FACT,
    QA_SOURCE_REPORTED_TO_MODELLED_FACT,
    QA_SUMMARY_STRENGTH_ESCALATION,
    QA_UNRESOLVED_VALUE_ORIGIN,
    SYSTEM_QA_CODES,
    check_value_origin,
    final_binding_check,
    load_forensic_record,
)
from inspektorium.audit.schemas import QAEvidenceItem

FIXTURE = (Path(__file__).resolve().parents[1] / "fixtures" / "audit" / "pipeline_qa"
           / "qa_modelled_value_origin.json")
SLICE1_FIXTURE = (Path(__file__).resolve().parents[1] / "fixtures" / "audit" / "pipeline_qa"
                  / "qa_evidence_symmetry_mixed_outcomes.json")


def base_record():
    return load_forensic_record(FIXTURE)


def d1_claim(rec):
    """The client value claim about the derived value D1."""
    (vc,) = [c for c in rec.client_findings[0].value_claims if c.evidence_id == "D1"]
    return vc


def ev(rec, eid):
    (item,) = [e for e in rec.evidence if e.evidence_id == eid]
    return item


# --- Test 1 — valid system-derived representation passes ------------------------

def test_1_valid_system_derived_passes():
    rec = base_record()
    result = final_binding_check(rec)
    assert result.releasable is True
    assert result.findings == []
    assert check_value_origin(rec) == []


# --- Test 2 — derived becomes literature fact (core regression) ------------------

def test_2_derived_becomes_literature_fact_blocks():
    rec = base_record()
    d1_claim(rec).claimed_origin = "source_reported"   # was system_derived
    result = final_binding_check(rec)
    assert result.releasable is False
    assert QA_MODEL_OUTPUT_TO_LITERATURE_FACT in result.codes()


# --- Test 3 — source-reported remains source-reported ---------------------------

def test_3_source_reported_stays_source_reported_passes():
    rec = base_record()
    # E1/E2 are source_reported with resolvable source binding and matching claims.
    origin_findings = check_value_origin(rec)
    assert [f for f in origin_findings if "E1" in f.refs or "E2" in f.refs] == []
    assert final_binding_check(rec).releasable is True


# --- Test 4 — source-reported without source binding ----------------------------

def test_4_source_reported_without_binding_blocks():
    rec = base_record()
    ev(rec, "E1").source_id = ""        # a source-reported value with no source binding
    result = final_binding_check(rec)
    assert result.releasable is False
    drift = [f for f in result.findings if f.code == QA_ARTIFACT_SOURCE_BINDING_DRIFT]
    assert any(f.check == "VC" and "E1" in f.refs for f in drift)


# --- Test 5 — derived input evidence missing ------------------------------------

def test_5_derived_missing_input_blocks():
    rec = base_record()
    ev(rec, "D1").input_evidence_ids = ["E1", "E99"]
    result = final_binding_check(rec)
    assert result.releasable is False
    drift = [f for f in result.findings if f.code == QA_ARTIFACT_SOURCE_BINDING_DRIFT]
    assert any(f.check == "VD" and "E99" in f.refs for f in drift)


# --- Test 6 — invented client source attribution --------------------------------

def test_6_invented_source_attribution_blocks():
    rec = base_record()
    d1_claim(rec).claimed_source_ids = ["S3"]   # S3 is not in the derivation lineage
    result = final_binding_check(rec)
    assert result.releasable is False
    drift = [f for f in result.findings if f.code == QA_ARTIFACT_SOURCE_BINDING_DRIFT]
    assert any(f.check == "VE" and "S3" in f.refs for f in drift)


# --- Test 7 — origin axis is independent of strength axis -----------------------

def test_7_origin_independent_of_strength():
    rec = base_record()
    # strength stays within the allowed ceiling (no strength escalation) ...
    rec.client_findings[0].client_strength = "not_directly_established"
    # ... but origin is escalated derived -> source_reported.
    d1_claim(rec).claimed_origin = "source_reported"
    result = final_binding_check(rec)
    codes = result.codes()
    assert QA_MODEL_OUTPUT_TO_LITERATURE_FACT in codes      # origin failure fires
    assert QA_SUMMARY_STRENGTH_ESCALATION not in codes       # strength axis does not
    assert result.releasable is False


# --- Test 8 — cautious client representation passes -----------------------------

def test_8_cautious_unspecified_origin_passes():
    rec = base_record()
    d1_claim(rec).claimed_origin = "unspecified"
    result = final_binding_check(rec)
    assert QA_MODEL_OUTPUT_TO_LITERATURE_FACT not in result.codes()
    assert result.releasable is True


def test_8b_omitting_origin_claim_is_not_escalation():
    rec = base_record()
    rec.client_findings[0].value_claims = [
        c for c in rec.client_findings[0].value_claims if c.evidence_id != "D1"
    ]  # no explicit origin claim for the derived value
    result = final_binding_check(rec)
    assert QA_MODEL_OUTPUT_TO_LITERATURE_FACT not in result.codes()
    assert result.releasable is True


# --- Test 19 — parametrized invariant: derived may never be claimed source-reported

@pytest.mark.parametrize("claimed,should_pass", [
    ("system_derived", True),
    ("unspecified", True),
    ("source_reported", False),
])
def test_19_system_derived_may_never_be_source_reported(claimed, should_pass):
    rec = base_record()
    assert ev(rec, "D1").value_origin == "system_derived"
    d1_claim(rec).claimed_origin = claimed
    result = final_binding_check(rec)
    if should_pass:
        assert QA_MODEL_OUTPUT_TO_LITERATURE_FACT not in result.codes()
    else:
        assert QA_MODEL_OUTPUT_TO_LITERATURE_FACT in result.codes()
        assert result.releasable is False


# --- Slice invariant: QA code is not a claim label ------------------------------

def test_model_output_code_is_not_a_claim_label():
    assert QA_MODEL_OUTPUT_TO_LITERATURE_FACT not in CLAIM_LABELS
    assert QA_UNRESOLVED_VALUE_ORIGIN not in CLAIM_LABELS
    assert set(SYSTEM_QA_CODES).isdisjoint(set(CLAIM_LABELS))


# ===========================================================================
# Curator hardening patch — fail-closed value origin
# ===========================================================================

def test_default_value_origin_is_unresolved_not_source_reported():
    # The default must fail closed: a missing origin is None, never source_reported.
    item = QAEvidenceItem(evidence_id="X", source_id="src")
    assert item.value_origin is None
    assert item.value_origin != "source_reported"


# --- Hardening A — omitted origin does not become source-reported ----------------

def test_A_omitted_origin_with_source_claim_is_blocked():
    rec = base_record()
    ev(rec, "D1").value_origin = None            # origin omitted
    d1_claim(rec).claimed_origin = "source_reported"
    result = final_binding_check(rec)
    assert result.releasable is False
    assert QA_UNRESOLVED_VALUE_ORIGIN in result.codes()
    # it must NOT silently become a literature fact via a default origin
    assert QA_MODEL_OUTPUT_TO_LITERATURE_FACT not in result.codes()


# --- Hardening B — omitted origin with derivation metadata stays unresolved ------

def test_B_derivation_metadata_does_not_infer_origin():
    rec = base_record()
    d1 = ev(rec, "D1")
    d1.value_origin = None                        # omitted, despite derivation metadata
    assert d1.derivation_method and d1.input_evidence_ids  # metadata present
    result = final_binding_check(rec)
    assert result.releasable is False
    assert QA_UNRESOLVED_VALUE_ORIGIN in result.codes()
    # no heuristic inference of system_derived (or anything) from metadata
    assert QA_MODEL_OUTPUT_TO_LITERATURE_FACT not in result.codes()


# --- Hardening C/D/E — explicit origins behave as before -------------------------

def test_C_explicit_system_derived_passes():
    rec = base_record()
    assert ev(rec, "D1").value_origin == "system_derived"
    d1_claim(rec).claimed_origin = "system_derived"
    assert final_binding_check(rec).releasable is True


def test_D_explicit_derived_to_source_reported_blocked():
    rec = base_record()
    d1_claim(rec).claimed_origin = "source_reported"
    assert QA_MODEL_OUTPUT_TO_LITERATURE_FACT in final_binding_check(rec).codes()


def test_E_source_reported_with_full_binding_passes():
    rec = base_record()
    e1 = ev(rec, "E1")
    assert e1.value_origin == "source_reported" and e1.source_id and e1.exact_reference
    assert final_binding_check(rec).releasable is True


# --- Hardening F — source-reported without positive binding fails ----------------

def test_F_source_reported_without_locator_is_blocked():
    rec = base_record()
    ev(rec, "E1").exact_reference = None          # source_id present, but no locator/span
    result = final_binding_check(rec)
    assert result.releasable is False
    drift = [f for f in result.findings if f.code == QA_ARTIFACT_SOURCE_BINDING_DRIFT]
    assert any(f.check == "VC" and "E1" in f.refs for f in drift)


# --- Hardening G — Slice-1 records stay backward-compatible ----------------------

def test_G_slice1_record_without_value_claims_still_passes():
    # Slice-1 records carry no value_origin / value_claims; the fail-closed default
    # must not retroactively block them (their evidence is not client-visible values).
    rec = load_forensic_record(SLICE1_FIXTURE)
    assert all(e.value_origin is None for e in rec.evidence)
    result = final_binding_check(rec)
    assert result.releasable is True
    assert QA_UNRESOLVED_VALUE_ORIGIN not in result.codes()


# ===========================================================================
# Curator hardening II — categorical provenance (not a total order)
# ===========================================================================

def _set_origin(rec, eid, origin):
    """Set an evidence item's internal origin, keeping its bindings consistent."""
    item = ev(rec, eid)
    item.value_origin = origin
    if origin == "source_reported":
        item.source_id = item.source_id or "src-D"
        item.exact_reference = item.exact_reference or "Table 9"
        item.input_evidence_ids = []          # a source-reported value is not derived
    # keep the client's claim about this value pointing at it, no invented sources
    claim = d1_claim(rec) if eid == "D1" else None
    if claim is not None:
        claim.claimed_source_ids = []


@pytest.mark.parametrize("internal,claimed,ok,code", [
    ("source_reported", "source_reported", True, None),                              # A
    ("source_reported", "unspecified", True, None),                                  # B
    ("source_reported", "system_derived", False, QA_SOURCE_REPORTED_TO_MODELLED_FACT),  # C
    ("system_derived", "system_derived", True, None),                                # D
    ("system_derived", "unspecified", True, None),                                   # E
    ("system_derived", "source_reported", False, QA_MODEL_OUTPUT_TO_LITERATURE_FACT),   # F
])
def test_categorical_origin_compatibility(internal, claimed, ok, code):
    rec = base_record()
    _set_origin(rec, "D1", internal)
    d1_claim(rec).claimed_origin = claimed
    result = final_binding_check(rec)
    if ok:
        assert QA_MODEL_OUTPUT_TO_LITERATURE_FACT not in result.codes()
        assert QA_SOURCE_REPORTED_TO_MODELLED_FACT not in result.codes()
    else:
        assert code in result.codes()
        assert result.releasable is False


def test_no_total_order_source_reported_may_not_become_derived():
    # The old total order (unspecified < system_derived < source_reported) would have
    # ALLOWED this as a "more cautious" move. Categorical semantics block it.
    rec = base_record()
    _set_origin(rec, "D1", "source_reported")
    d1_claim(rec).claimed_origin = "system_derived"
    result = final_binding_check(rec)
    assert QA_SOURCE_REPORTED_TO_MODELLED_FACT in result.codes()
    assert result.releasable is False


def test_H_origin_compatibility_independent_of_strength():
    # A provenance-category falsification fires even when summary strength stays legal,
    # proving the origin axis is independent of the evidence-strength axis.
    rec = base_record()
    _set_origin(rec, "D1", "source_reported")
    d1_claim(rec).claimed_origin = "system_derived"
    rec.client_findings[0].client_strength = "not_directly_established"  # within allowed
    result = final_binding_check(rec)
    assert QA_SOURCE_REPORTED_TO_MODELLED_FACT in result.codes()
    assert QA_SUMMARY_STRENGTH_ESCALATION not in result.codes()
    assert result.releasable is False


def test_reverse_falsification_code_is_not_a_claim_label():
    assert QA_SOURCE_REPORTED_TO_MODELLED_FACT not in CLAIM_LABELS
    assert QA_SOURCE_REPORTED_TO_MODELLED_FACT in SYSTEM_QA_CODES
