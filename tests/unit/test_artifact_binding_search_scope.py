"""Phase 7B slice 3 — search-scope binding for negative evidence claims.

Core invariant: NOT FOUND != DOES NOT EXIST. A client negative assertion may keep or
narrow its documented basis scope, never broaden it; global non-existence is supported
by no basis by default. Failing variants are derived by mutation from one generic
synthetic fixture (no LaVita / commercial identity).
"""

from __future__ import annotations

from pathlib import Path

from inspektorium.audit.artifact_binding import (
    CLAIM_LABELS,
    QA_SEARCH_SCOPE_TO_WORLD_GENERALIZATION,
    QA_UNRESOLVED_SEARCH_SCOPE,
    SYSTEM_QA_CODES,
    check_search_scope,
    final_binding_check,
    load_forensic_record,
)

FIXTURE = (Path(__file__).resolve().parents[1] / "fixtures" / "audit" / "pipeline_qa"
           / "qa_search_scope_negative_language.json")


def base_record():
    return load_forensic_record(FIXTURE)


def na(rec):
    (a,) = [a for a in rec.negative_assertions if a.assertion_id == "NA1"]
    return a


def ss(rec):
    (s,) = [s for s in rec.search_scopes if s.search_scope_id == "SS1"]
    return s


def cna(rec):
    return rec.client_findings[0].client_negative_assertions[0]


def _make_source_local(rec):
    a = na(rec)
    a.assertion_scope = "source_local"
    a.search_scope_id = None
    a.source_local_evidence_ids = ["E1"]


# --- Test A — source-local safe -------------------------------------------------

def test_A_source_local_safe_passes():
    rec = base_record()
    _make_source_local(rec)
    cna(rec).client_scope = "source_local"
    result = final_binding_check(rec)
    assert result.releasable is True
    assert check_search_scope(rec) == []


# --- Test B — source-local -> world claim ---------------------------------------

def test_B_source_local_to_world_blocked():
    rec = base_record()
    _make_source_local(rec)
    cna(rec).client_scope = "global_nonexistence"
    result = final_binding_check(rec)
    assert result.releasable is False
    assert QA_SEARCH_SCOPE_TO_WORLD_GENERALIZATION in result.codes()


# --- Test C — reviewed-set safe -------------------------------------------------

def test_C_reviewed_set_safe_passes():
    rec = base_record()
    ss(rec).scope_type = "reviewed_set"
    na(rec).assertion_scope = "reviewed_set"
    cna(rec).client_scope = "reviewed_set"
    assert final_binding_check(rec).releasable is True


# --- Test D — reviewed-set -> structured-search claim ---------------------------

def test_D_reviewed_set_to_structured_blocked():
    rec = base_record()
    ss(rec).scope_type = "reviewed_set"
    cna(rec).client_scope = "documented_search"
    result = final_binding_check(rec)
    assert result.releasable is False
    assert QA_SEARCH_SCOPE_TO_WORLD_GENERALIZATION in result.codes()


# --- Test E — documented structured search safe (base) --------------------------

def test_E_documented_search_safe_passes():
    rec = base_record()
    assert cna(rec).client_scope == "documented_search"
    result = final_binding_check(rec)
    assert result.releasable is True
    assert result.findings == []


# --- Test F — documented search -> global non-existence (core regression) --------

def test_F_documented_search_to_global_blocked():
    rec = base_record()
    cna(rec).client_scope = "global_nonexistence"
    result = final_binding_check(rec)
    assert result.releasable is False
    assert QA_SEARCH_SCOPE_TO_WORLD_GENERALIZATION in result.codes()


# --- Test G — missing search scope ----------------------------------------------

def test_G_missing_search_scope_blocked():
    rec = base_record()
    na(rec).search_scope_id = None
    na(rec).source_local_evidence_ids = []     # no basis of any kind
    cna(rec).client_scope = "reviewed_set"      # search-dependent claim
    result = final_binding_check(rec)
    assert result.releasable is False
    assert QA_UNRESOLVED_SEARCH_SCOPE in result.codes()


# --- Test H — source-local needs no fabricated search ---------------------------

def test_H_source_local_needs_no_search_metadata():
    rec = base_record()
    _make_source_local(rec)
    cna(rec).client_scope = "source_local"
    assert na(rec).search_scope_id is None      # no SearchScope invented
    assert final_binding_check(rec).releasable is True


# --- Test I — client may narrow scope -------------------------------------------

def test_I_client_may_narrow_scope():
    rec = base_record()                          # documented_search basis
    cna(rec).client_scope = "reviewed_set"       # narrower
    assert final_binding_check(rec).releasable is True


# --- Test J — client may not broaden scope --------------------------------------

def test_J_client_may_not_broaden_scope():
    rec = base_record()
    ss(rec).scope_type = "reviewed_set"
    cna(rec).client_scope = "global_nonexistence"
    result = final_binding_check(rec)
    assert result.releasable is False
    assert QA_SEARCH_SCOPE_TO_WORLD_GENERALIZATION in result.codes()


# --- Test K — scope independent of confidence -----------------------------------

def test_K_scope_independent_of_confidence():
    rec = base_record()
    ss(rec).scope_type = "reviewed_set"
    rec.findings[0].confidence_status = "VALID"          # high evaluator confidence
    cna(rec).client_scope = "global_nonexistence"
    result = final_binding_check(rec)
    assert result.releasable is False
    assert QA_SEARCH_SCOPE_TO_WORLD_GENERALIZATION in result.codes()


# --- Test L — scope independent of evidence strength ----------------------------

def test_L_scope_independent_of_evidence_strength():
    rec = base_record()
    ss(rec).scope_type = "reviewed_set"
    rec.findings[0].allowed_summary_strength = "not_supported"   # strong underlying strength
    rec.client_findings[0].client_strength = "not_supported"
    cna(rec).client_scope = "reviewed_set"       # scope stays within basis
    assert QA_SEARCH_SCOPE_TO_WORLD_GENERALIZATION not in final_binding_check(rec).codes()


# --- Section 18 — a documented search needs a machine-readable record ------------

def test_documented_search_without_record_is_unresolved():
    rec = base_record()
    s = ss(rec)
    s.reviewed_source_ids = []
    s.resources = []
    s.query_terms = []
    s.date_cutoff = None                          # documented_search with no search record
    result = final_binding_check(rec)
    assert result.releasable is False
    assert QA_UNRESOLVED_SEARCH_SCOPE in result.codes()


# --- Slice invariant: scope codes are not claim labels --------------------------

def test_scope_codes_are_not_claim_labels():
    assert QA_SEARCH_SCOPE_TO_WORLD_GENERALIZATION not in CLAIM_LABELS
    assert QA_UNRESOLVED_SEARCH_SCOPE not in CLAIM_LABELS
    assert {QA_SEARCH_SCOPE_TO_WORLD_GENERALIZATION, QA_UNRESOLVED_SEARCH_SCOPE} <= set(SYSTEM_QA_CODES)
