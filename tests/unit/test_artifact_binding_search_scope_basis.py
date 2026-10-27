"""Phase 7B slice 3 — curator hardening: narrower scope requires a resolvable basis.

The initial search-scope gate correctly prevented *broadening* a bounded negative
assertion, but allowed a client to *narrow* its scope on scope-containment alone. That
is unsafe: a narrower scope label makes a MORE specific provenance claim ("the cited
source", "the reviewed sources") whose evidence basis must actually resolve. This module
freezes the hardened invariant:

    SCOPE MAY NARROW ONLY IF THE NARROWER EVIDENCE BASIS RESOLVES.

    NARROWER SCOPE WITHOUT NARROWER BASIS = INVENTED PROVENANCE.

All variants are derived by mutation from the one generic synthetic slice-3 fixture (no
new fixture, no LaVita / commercial identity). Confidence and evidence strength are never
consulted by the gate; tests N and O prove they cannot compensate for a missing basis.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from inspektorium.audit.integrity.artifact_binding import (
    QA_ARTIFACT_SOURCE_BINDING_DRIFT,
    QA_SEARCH_SCOPE_TO_WORLD_GENERALIZATION,
    QA_UNRESOLVED_SEARCH_SCOPE,
    check_evidence_symmetry,
    check_search_scope,
    check_value_origin,
    final_binding_check,
    load_forensic_record,
)
from inspektorium.audit.schemas import Task

FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "audit"
    / "pipeline_qa"
    / "qa_search_scope_negative_language.json"
)


def rec():
    return load_forensic_record(FIXTURE)


def na(r):
    (a,) = [a for a in r.negative_assertions if a.assertion_id == "NA1"]
    return a


def ss(r):
    (s,) = [s for s in r.search_scopes if s.search_scope_id == "SS1"]
    return s


def cna(r):
    return r.client_findings[0].client_negative_assertions[0]


def ev(r, eid):
    (e,) = [e for e in r.evidence if e.evidence_id == eid]
    return e


# --- Test A — documented_search -> documented_search (kept) ---------------------


def test_A_documented_search_kept_passes():
    r = rec()
    cna(r).client_scope = "documented_search"
    result = final_binding_check(r)
    assert result.releasable is True
    assert check_search_scope(r) == []


# --- Test B — documented_search -> reviewed_set WITH a reviewed set -------------


def test_B_documented_search_to_reviewed_set_with_set_passes():
    r = rec()  # SS1 documented_search carries reviewed_source_ids = [src-1, src-2]
    assert ss(r).reviewed_source_ids  # precondition: a real reviewed set is represented
    cna(r).client_scope = "reviewed_set"
    result = final_binding_check(r)
    assert result.releasable is True
    assert check_search_scope(r) == []


# --- Test C — documented_search -> reviewed_set WITHOUT a reviewed set ----------
# Key curator regression: containment holds, but the reviewed set does not resolve.


def test_C_documented_search_to_reviewed_set_without_set_blocked():
    r = rec()
    ss(r).reviewed_source_ids = []  # search still substantiated by resources/queries
    cna(r).client_scope = "reviewed_set"
    result = final_binding_check(r)
    assert result.releasable is False
    assert QA_ARTIFACT_SOURCE_BINDING_DRIFT in result.codes()
    # NOT a broadening and NOT a fully-unresolved scope: a basis DID resolve.
    assert QA_SEARCH_SCOPE_TO_WORLD_GENERALIZATION not in result.codes()
    assert QA_UNRESOLVED_SEARCH_SCOPE not in result.codes()


# --- Test D — documented_search -> source_local WITH a concrete basis -----------


def test_D_documented_search_to_source_local_with_basis_passes():
    r = rec()
    na(r).source_local_evidence_ids = [
        "E1"
    ]  # concrete source-local evidence, resolves to src-1
    cna(r).client_scope = "source_local"
    result = final_binding_check(r)
    assert result.releasable is True
    assert check_search_scope(r) == []


# --- Test E — documented_search -> source_local WITHOUT a concrete basis --------


def test_E_documented_search_to_source_local_without_basis_blocked():
    r = rec()  # source_local_evidence_ids = [] in the base
    cna(r).client_scope = "source_local"
    result = final_binding_check(r)
    assert result.releasable is False
    assert QA_ARTIFACT_SOURCE_BINDING_DRIFT in result.codes()


# --- Test F — reviewed_set -> reviewed_set --------------------------------------


def test_F_reviewed_set_to_reviewed_set_passes():
    r = rec()
    ss(r).scope_type = "reviewed_set"  # reviewed_source_ids still present
    cna(r).client_scope = "reviewed_set"
    assert final_binding_check(r).releasable is True


# --- Test G — reviewed_set -> source_local WITH a concrete basis ----------------


def test_G_reviewed_set_to_source_local_with_basis_passes():
    r = rec()
    ss(r).scope_type = "reviewed_set"
    na(r).source_local_evidence_ids = ["E1"]
    cna(r).client_scope = "source_local"
    assert final_binding_check(r).releasable is True


# --- Test H — reviewed_set -> source_local WITHOUT a concrete basis -------------


def test_H_reviewed_set_to_source_local_without_basis_blocked():
    r = rec()
    ss(r).scope_type = "reviewed_set"  # source_local_evidence_ids stays []
    cna(r).client_scope = "source_local"
    result = final_binding_check(r)
    assert result.releasable is False
    assert QA_ARTIFACT_SOURCE_BINDING_DRIFT in result.codes()


# --- Test I — source_local -> source_local (concrete basis resolves) ------------


def test_I_source_local_with_basis_passes():
    r = rec()
    na(r).search_scope_id = None
    na(r).source_local_evidence_ids = ["E1"]
    cna(r).client_scope = "source_local"
    assert final_binding_check(r).releasable is True


# --- Test J — source_local with a missing source/evidence binding --------------


def test_J_source_local_missing_source_binding_blocked():
    r = rec()
    na(r).search_scope_id = None
    na(r).source_local_evidence_ids = ["E1"]
    ev(r, "E1").source_id = ""  # evidence exists but binds to no source
    cna(r).client_scope = "source_local"
    result = final_binding_check(r)
    assert result.releasable is False
    assert QA_ARTIFACT_SOURCE_BINDING_DRIFT in result.codes()


# --- Test K — any bounded scope -> global_nonexistence --------------------------


def test_K_bounded_to_global_blocked():
    r = rec()
    cna(r).client_scope = "global_nonexistence"
    result = final_binding_check(r)
    assert result.releasable is False
    assert QA_SEARCH_SCOPE_TO_WORLD_GENERALIZATION in result.codes()


# --- Test L — unresolved search scope ------------------------------------------


def test_L_unresolved_search_scope_blocked():
    r = rec()
    na(r).search_scope_id = None
    na(r).source_local_evidence_ids = []  # no basis of any kind
    cna(r).client_scope = "documented_search"  # search-dependent claim
    result = final_binding_check(r)
    assert result.releasable is False
    assert QA_UNRESOLVED_SEARCH_SCOPE in result.codes()


# --- Test M — a narrower label does not create provenance -----------------------
# The general invariant: a substantiated basis DOES resolve (so it is not an
# unresolved-scope failure), yet the narrower reviewed-set provenance is fabricated.


def test_M_narrower_label_does_not_create_provenance():
    r = rec()
    ss(r).reviewed_source_ids = []  # documented_search still substantiated
    # sanity: the (broad) basis itself is not unresolved — only the narrower one is absent
    cna(r).client_scope = "documented_search"
    assert final_binding_check(r).releasable is True
    # now narrow the label without providing the narrower basis
    cna(r).client_scope = "reviewed_set"
    result = final_binding_check(r)
    assert result.releasable is False
    assert QA_ARTIFACT_SOURCE_BINDING_DRIFT in result.codes()
    assert QA_UNRESOLVED_SEARCH_SCOPE not in result.codes()


# --- Test N — scope compatibility is independent of confidence ------------------


def test_N_missing_basis_not_saved_by_confidence():
    r = rec()
    ss(r).reviewed_source_ids = []
    r.findings[0].confidence_status = "VALID"  # maximal evaluator confidence
    cna(r).client_scope = "reviewed_set"
    result = final_binding_check(r)
    assert result.releasable is False
    assert QA_ARTIFACT_SOURCE_BINDING_DRIFT in result.codes()


# --- Test O — scope compatibility is independent of evidence strength -----------


def test_O_missing_basis_not_saved_by_evidence_strength():
    r = rec()
    ss(r).reviewed_source_ids = []
    r.findings[
        0
    ].allowed_summary_strength = "not_supported"  # strong underlying strength
    r.client_findings[0].client_strength = "not_supported"
    cna(r).client_scope = "reviewed_set"
    result = final_binding_check(r)
    assert result.releasable is False
    assert QA_ARTIFACT_SOURCE_BINDING_DRIFT in result.codes()


# --- Test P — the base search-scope path is intact (no over-blocking) -----------


def test_P_base_search_scope_record_is_clean():
    r = rec()
    result = final_binding_check(r)
    assert result.releasable is True
    assert result.findings == []


# --- Test Q — value-origin primitive unaffected by this patch -------------------


def test_Q_value_origin_primitive_clean_on_base():
    assert check_value_origin(rec()) == []


# --- Test R — evidence-symmetry primitive unaffected by this patch --------------


def test_R_evidence_symmetry_primitive_clean_on_base():
    assert check_evidence_symmetry(rec()) == []


# --- Test S — the slice-3 fixture stays a pipeline-QA (class C) artifact --------


def test_S_fixture_is_isolated_pipeline_qa():
    r = rec()
    assert r.synthetic_fixture is True
    assert r.fixture_class == "pipeline_qa"
    # A ForensicRecord is structurally not a loadable Task (cannot enter the case library).
    import json

    data = json.loads(FIXTURE.read_text())
    with pytest.raises(Exception):
        Task(**data)
    assert "task_type" not in data
    assert data.get("gold_label") is None
