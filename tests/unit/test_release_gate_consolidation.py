"""Phase 7B — consolidated release-gate integration matrix (Tests A–T).

Proves that the single authoritative entrypoint :func:`evaluate_artifact_release` wires
every mandatory representation-QA control into one deterministic release decision, that it
collects ALL findings without early exit (one failure never masks another), that its
severity roll-up and release policy are deterministic, and that its report binds to the
exact input by fingerprint. These are integration tests over the real orchestration — no
primitive is mocked away.

All variants are derived by mutation from ONE generic synthetic consolidated fixture (no
real company / LaVita / client content, no case-library gold label).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from inspektorium.audit.artifact_binding import (
    MANDATORY_PHASE7B_CHECKS,
    QA_ARTIFACT_SOURCE_BINDING_DRIFT,
    QA_ASYMMETRIC_EVIDENCE_SELECTION,
    QA_MODEL_OUTPUT_TO_LITERATURE_FACT,
    QA_SOURCE_REPORTED_TO_MODELLED_FACT,
    QA_SUMMARY_STRENGTH_ESCALATION,
    QA_SEARCH_SCOPE_TO_WORLD_GENERALIZATION,
    QA_UNRESOLVED_VALUE_ORIGIN,
    BindingFinding,
    _severity_rollup,
    evaluate_artifact_release,
    load_forensic_record,
)
from inspektorium.audit.run_library import discover_cases
from inspektorium.audit.schemas import FailureSeverity, Task

FIXTURE = (Path(__file__).resolve().parents[1] / "fixtures" / "audit" / "pipeline_qa"
           / "qa_release_gate_consolidated.json")
CASE_DIR = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "audit" / "case_library"


def rec():
    return load_forensic_record(FIXTURE)


def cf(r):
    return r.client_findings[0]


def na_client(r):
    return r.client_findings[0].client_negative_assertions[0]


def ss(r):
    return r.search_scopes[0]


def finding(r):
    return r.findings[0]


def ev(r, eid):
    (e,) = [e for e in r.evidence if e.evidence_id == eid]
    return e


def vc(r, eid):
    (v,) = [v for v in r.client_findings[0].value_claims if v.evidence_id == eid]
    return v


def synthetic(sev: str, code: str = "synthetic_rollup_code") -> BindingFinding:
    return BindingFinding(code=code, severity=sev, check="T", detail="roll-up unit finding")


# --- Test A — a fully clean artifact releases -----------------------------------

def test_A_clean_artifact_releases():
    report = evaluate_artifact_release(rec())
    assert report.severity_counts["critical"] == 0
    assert report.severity_counts["major"] == 0
    assert report.releasable is True
    assert report.findings == []
    assert report.blocking_codes == []


# --- Test B — a single critical failure blocks ----------------------------------

def test_B_single_critical_blocks():
    r = rec()
    na_client(r).client_scope = "global_nonexistence"
    report = evaluate_artifact_release(r)
    assert report.releasable is False
    assert QA_SEARCH_SCOPE_TO_WORLD_GENERALIZATION in report.codes()
    assert report.severity_counts["critical"] >= 1


# --- Test C — a single major failure blocks (roll-up policy) --------------------
# No current Phase-7B QA code maps to `major` (all map to `critical`); the major
# roll-up branch is therefore exercised directly with a typed synthetic finding.

def test_C_single_major_blocks_rollup():
    counts, releasable, blocking = _severity_rollup([synthetic(FailureSeverity.MAJOR.value)])
    assert counts["major"] == 1
    assert releasable is False
    assert "synthetic_rollup_code" in blocking


# --- Test D — moderate/minor/stylistic findings do not block --------------------

def test_D_sub_major_findings_do_not_block():
    findings = [
        synthetic(FailureSeverity.MODERATE.value, "m"),
        synthetic(FailureSeverity.MINOR.value, "n"),
        synthetic(FailureSeverity.STYLISTIC.value, "s"),
    ]
    counts, releasable, blocking = _severity_rollup(findings)
    assert releasable is True
    assert blocking == []
    assert counts["moderate"] == 1 and counts["minor"] == 1 and counts["stylistic"] == 1


# --- Test E — multiple independent failures are all reported (no early exit) -----

def test_E_multiple_failures_all_reported():
    r = rec()
    cf(r).referenced_evidence_ids = ["E1", "D1"]        # (1) drops opposing E2 -> asymmetry
    vc(r, "D1").claimed_origin = "source_reported"       # (2) derived -> literature fact
    na_client(r).client_scope = "global_nonexistence"    # (3) search-scope overreach
    report = evaluate_artifact_release(r)
    assert report.releasable is False
    codes = report.codes()
    assert QA_ASYMMETRIC_EVIDENCE_SELECTION in codes
    assert QA_MODEL_OUTPUT_TO_LITERATURE_FACT in codes
    assert QA_SEARCH_SCOPE_TO_WORLD_GENERALIZATION in codes


# --- Test F — a binding failure does not mask another resolvable failure ---------

def test_F_binding_failure_does_not_mask_others():
    r = rec()
    cf(r).referenced_evidence_ids = ["E1", "E2", "D1", "E99"]   # E99 unknown -> binding drift
    na_client(r).client_scope = "global_nonexistence"           # independent search-scope defect
    report = evaluate_artifact_release(r)
    assert report.releasable is False
    codes = report.codes()
    assert QA_ARTIFACT_SOURCE_BINDING_DRIFT in codes
    assert QA_SEARCH_SCOPE_TO_WORLD_GENERALIZATION in codes


# --- Test G — an unresolvable dependency does not produce a false pass -----------

def test_G_unresolvable_dependency_no_false_pass():
    r = rec()
    cf(r).parent_finding_id = "F-NOPE"       # parent cannot resolve
    report = evaluate_artifact_release(r)
    # The missing parent surfaces as a finding and blocks — it is never a silent pass.
    assert report.releasable is False
    assert QA_ARTIFACT_SOURCE_BINDING_DRIFT in report.codes()
    # Strength cannot be assessed without the parent: it abstains, it does NOT fabricate
    # a pass or a spurious escalation.
    assert QA_SUMMARY_STRENGTH_ESCALATION not in report.codes()
    by_name = {c.name: c for c in report.checks_run}
    assert by_name["summary_strength_monotonicity"].finding_count == 0
    # Every mandatory control still ran (no top-level skip).
    assert len(report.checks_run) == len(MANDATORY_PHASE7B_CHECKS)


# --- Test H — evidence-symmetry integration -------------------------------------

def test_H_evidence_symmetry_blocks():
    r = rec()
    cf(r).referenced_evidence_ids = ["E1", "D1"]   # drops the opposing/qualifying E2
    report = evaluate_artifact_release(r)
    assert report.releasable is False
    assert QA_ASYMMETRIC_EVIDENCE_SELECTION in report.codes()


# --- Test I — value-origin integration (derived -> source-reported) --------------

def test_I_value_origin_derived_to_source_blocks():
    r = rec()
    vc(r, "D1").claimed_origin = "source_reported"
    report = evaluate_artifact_release(r)
    assert report.releasable is False
    assert QA_MODEL_OUTPUT_TO_LITERATURE_FACT in report.codes()


# --- Test J — reverse value-origin integration (source-reported -> derived) ------

def test_J_value_origin_source_to_derived_blocks():
    r = rec()
    vc(r, "E1").claimed_origin = "system_derived"
    report = evaluate_artifact_release(r)
    assert report.releasable is False
    assert QA_SOURCE_REPORTED_TO_MODELLED_FACT in report.codes()


# --- Test K — unresolved value origin -------------------------------------------

def test_K_unresolved_value_origin_blocks():
    r = rec()
    ev(r, "E1").value_origin = None            # client-visible value, origin unresolved
    report = evaluate_artifact_release(r)
    assert report.releasable is False
    assert QA_UNRESOLVED_VALUE_ORIGIN in report.codes()


# --- Test L — search-scope globalization ----------------------------------------

def test_L_search_scope_globalization_blocks():
    r = rec()
    na_client(r).client_scope = "global_nonexistence"
    report = evaluate_artifact_release(r)
    assert report.releasable is False
    assert QA_SEARCH_SCOPE_TO_WORLD_GENERALIZATION in report.codes()


# --- Test M — narrowed search scope without a resolvable basis -------------------

def test_M_narrowed_scope_without_basis_blocks():
    r = rec()
    ss(r).reviewed_source_ids = []              # documented search still substantiated
    na_client(r).client_scope = "reviewed_set"  # narrows without a represented reviewed set
    report = evaluate_artifact_release(r)
    assert report.releasable is False
    assert QA_ARTIFACT_SOURCE_BINDING_DRIFT in report.codes()


# --- Test N — summary-strength escalation ----------------------------------------

def test_N_summary_strength_escalation_blocks():
    r = rec()
    cf(r).client_strength = "disproven"         # far stronger than parent's ceiling
    report = evaluate_artifact_release(r)
    assert report.releasable is False
    assert QA_SUMMARY_STRENGTH_ESCALATION in report.codes()


# --- Test O — a clean mixed-evidence artifact still releases ---------------------
# Mixed evidence represented symmetrically and cautiously is NOT a QA defect.

def test_O_clean_mixed_evidence_releases():
    report = evaluate_artifact_release(rec())
    assert report.releasable is True
    assert QA_ASYMMETRIC_EVIDENCE_SELECTION not in report.codes()


# --- Test P — the input fingerprint changes when the record changes --------------

def test_P_fingerprint_tracks_input():
    base = evaluate_artifact_release(rec())
    same = evaluate_artifact_release(rec())
    assert base.record_fingerprint == same.record_fingerprint      # stable for same input
    r = rec()
    cf(r).display_claim = cf(r).display_claim + " (edited)"          # release-relevant change
    changed = evaluate_artifact_release(r)
    assert changed.record_fingerprint != base.record_fingerprint


# --- Test Q — report determinism -------------------------------------------------

def test_Q_report_is_deterministic():
    a = evaluate_artifact_release(rec())
    b = evaluate_artifact_release(rec())
    assert a.model_dump() == b.model_dump()     # no timestamp; fully canonical


# --- Test R — finding order is stable under irrelevant input reordering ----------

def _three_failures(r):
    cf(r).referenced_evidence_ids = ["E1", "D1"]
    vc(r, "D1").claimed_origin = "source_reported"
    na_client(r).client_scope = "global_nonexistence"


def test_R_finding_order_is_canonical():
    r1 = rec()
    _three_failures(r1)
    report1 = evaluate_artifact_release(r1)

    r2 = rec()
    _three_failures(r2)
    r2.evidence = list(reversed(r2.evidence))   # irrelevant collection reordering
    report2 = evaluate_artifact_release(r2)

    assert [f.model_dump() for f in report1.findings] == [f.model_dump() for f in report2.findings]
    assert len(report1.findings) >= 3


# --- Test S — the entrypoint invokes every mandatory control --------------------

def test_S_mandatory_check_coverage():
    report = evaluate_artifact_release(rec())
    run_names = [c.name for c in report.checks_run]
    assert run_names == [name for name, _ in MANDATORY_PHASE7B_CHECKS]
    # Freeze the known mandatory set — removing a registered control fails this test.
    expected = {
        "finding_artifact_binding",
        "summary_strength_monotonicity",
        "evidence_symmetry",
        "value_origin_provenance",
        "search_scope_binding",
    }
    assert expected <= set(run_names)
    assert len(run_names) == len(MANDATORY_PHASE7B_CHECKS)


# --- Test T — pipeline-QA isolation (the consolidated fixture is class C) --------

def test_T_fixture_is_isolated_pipeline_qa():
    r = rec()
    assert r.synthetic_fixture is True
    assert r.fixture_class == "pipeline_qa"
    discovered_names = {p.name for p, _ in discover_cases(task_dir=CASE_DIR)}
    assert FIXTURE.name not in discovered_names
    import json
    data = json.loads(FIXTURE.read_text())
    with pytest.raises(Exception):
        Task(**data)
    assert "task_type" not in data
    assert data.get("gold_label") is None
