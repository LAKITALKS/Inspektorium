"""Phase-7A thin execution + reporting readiness (WP-4) — deterministic, offline, no model calls.

Validates the execution-universe resolution (84 evaluated units = 34 bases + 50 clustered variants),
the deterministic manifest / call plan (840 planned calls) + fingerprints, the fail-closed pre-run
gate, replication-level enrichment/aggregation + stability tiers, and the frozen Boundary /
Adversarial / Perturbation / Replication systematic-failure computations. Covers WP-4 §38 (A-J) and
§39 (A-V). The only "execution" is the in-process fake provider (§30) — 0 real analytical calls.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agent_arena import preflight_integrity as pi
from agent_arena.confidence_validity import INVALID, MISSING, VALID, classify_confidence
from agent_arena.phase7a_execution import (
    EXEC_TYPE_ADJUDICATION,
    EXEC_TYPE_DRY_RUN,
    EXEC_TYPE_REPRODUCTION,
    EXECUTION_TYPES,
    EXPECTED_EVALUATED_UNITS,
    EXPECTED_INDEPENDENT_BASES,
    EXPECTED_PERTURBATION_CLUSTERS,
    EXPECTED_PERTURBATION_VARIANTS,
    EXPECTED_PLANNED_CALLS,
    N_REPLICATIONS,
    PRIMARY_MODELS,
    TIER_FRAGILE,
    TIER_STABLE_MAJORITY,
    TIER_UNANIMOUS,
    UnitStability,
    adversarial_assessment,
    aggregate,
    boundary_assessment,
    build_call_plan,
    build_execution_manifest,
    build_phase7a_report,
    classify_qa,
    diagnostic_preflight,
    execute,
    execute_qa,
    is_calibration_valid,
    is_classification_valid,
    is_terminal_attempt,
    model_call_again_allowed,
    perturbation_assessment,
    real_run_preflight,
    replication_assessment,
    resolve_evaluated_units,
    run_metadata,
    unit_type_breakdown,
    verify_pre_run,
)
from agent_arena.run_library import FakeLibraryProvider

REPO_ROOT = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------------------
# Synthetic factories (never a model call)
# ---------------------------------------------------------------------------

def mk_record(model, unit_id, unit_type, family_id, gold, label, run_index,
              base_case_id=None, cluster_root_id=None, error=None, parse_ok=True, confidence=0.8,
              confidence_state=None, truncation_suspected=False):
    label_correct = None if label is None else (label == gold)
    rec = {
        "model": model, "unit_id": unit_id, "unit_type": unit_type,
        "base_case_id": base_case_id or unit_id, "cluster_root_id": cluster_root_id,
        "family_id": family_id, "gold_label": gold, "run_index": run_index,
        "error": error, "error_type": ("timeout" if error else None),
        "label": label, "label_correct": label_correct, "parse_ok": parse_ok,
        "truncation_suspected": truncation_suspected,
        "confidence": confidence,
        "confidence_state": confidence_state or classify_confidence(confidence),
        "dry_run": True,
    }
    rec["brier_contribution"] = (
        round((float(confidence) - (1.0 if label_correct else 0.0)) ** 2, 6)
        if label_correct is not None and is_calibration_valid(rec) else None
    )
    return rec


def unit_records(model, unit_id, unit_type, family_id, gold, labels,
                 cluster_root_id=None, base_case_id=None, errors=None):
    errors = errors or [None] * len(labels)
    return [mk_record(model, unit_id, unit_type, family_id, gold, lab, i,
                      base_case_id=base_case_id, cluster_root_id=cluster_root_id,
                      error=err, parse_ok=(err is None))
            for i, (lab, err) in enumerate(zip(labels, errors))]


def mk_stab(model, unit_id, unit_type, family_id, gold, modal_label, modal_support,
            n_provider_errors=0, cluster_root_id=None):
    modal_correct = None if modal_label is None else (modal_label == gold)
    from agent_arena.phase7a_execution import _tier
    return UnitStability(
        model=model, unit_id=unit_id, unit_type=unit_type,
        base_case_id=cluster_root_id or unit_id, cluster_root_id=cluster_root_id,
        family_id=family_id, gold_label=gold, n_runs=5, n_labelled=5 - n_provider_errors,
        n_provider_errors=n_provider_errors, n_parse_failures=0, modal_label=modal_label,
        modal_support=modal_support, modal_correct=modal_correct,
        unique_labels=[modal_label] if modal_label else [], label_switch_count=0,
        confidence_mean=0.8, confidence_spread=0.0, brier_mean=None,
        per_replication_correct=[bool(modal_correct)] * (5 - n_provider_errors),
        stability_tier=_tier(modal_support),
    )


# ===========================================================================
# §39 deterministic validation A-V
# ===========================================================================

@pytest.fixture(scope="module")
def units():
    return resolve_evaluated_units(REPO_ROOT)


@pytest.fixture(scope="module")
def gate():
    return verify_pre_run(REPO_ROOT)


def test_A_34_independent_bases(units):
    bases = [u for u in units if u.unit_type != "perturbation_variant"]
    assert len(bases) == EXPECTED_INDEPENDENT_BASES == 34


def test_B_84_evaluated_units(units, gate):
    assert len(units) == EXPECTED_EVALUATED_UNITS == 84
    assert gate["n_evaluated_units"] == 84


def test_C_50_derived_perturbations(units):
    assert sum(1 for u in units if u.unit_type == "perturbation_variant") == EXPECTED_PERTURBATION_VARIANTS == 50


def test_D_10_perturbation_clusters(units):
    clusters = {u.cluster_root_id for u in units if u.unit_type == "perturbation_variant"}
    assert len(clusters) == EXPECTED_PERTURBATION_CLUSTERS == 10


def test_E_two_exact_model_ids():
    assert list(PRIMARY_MODELS) == ["claude-haiku-4-5-20251001", "claude-sonnet-4-5-20250929"]


def test_F_n_is_5():
    assert N_REPLICATIONS == 5


def test_G_planned_calls_840(gate):
    assert gate["planned_analytical_calls"] == EXPECTED_PLANNED_CALLS == 840
    plan = build_call_plan(REPO_ROOT)
    assert plan["planned_analytical_calls"] == 840
    assert plan["max_transport_retries_per_call"] == 2  # retries are not replications


def test_H_no_retired_case_included(units):
    # retired ids: P7A-BND-003/006/007/008, P7A-ADV-014
    retired = {"P7A-BND-003", "P7A-BND-006", "P7A-BND-007", "P7A-BND-008", "P7A-ADV-014"}
    assert {u.unit_id for u in units}.isdisjoint(retired)


def test_I_no_class_a_case(units):
    from agent_arena import run_library
    class_a = {t.id for _, t in run_library.discover_cases(
        task_dir=REPO_ROOT / "tasks" / "study_forensics", include_retired=True)}
    assert {u.unit_id for u in units}.isdisjoint(class_a)


def test_J_no_phase7b_fixture(units):
    for u in units:
        assert not any(u.unit_id.startswith(f"R{n}") for n in range(1, 9))


def test_K_no_holdout(gate):
    # gate scans the execution universe for forbidden terms and fails closed
    assert gate["passes"], gate["errors"]


def test_L_no_client_lavita_stacy(units):
    from agent_arena.phase7a_execution import _canon
    blob = _canon([u.meta() for u in units]).lower()
    for term in ("lavita", "stacy", "inspektorium", "holdout", "salt", "envelope"):
        assert term not in blob


def test_M_scientific_fingerprints_reproduce(gate):
    assert gate["passes"]
    assert not any("fingerprint drift" in e for e in gate["errors"])


def test_N_variant_fingerprints_reproduce():
    from agent_arena.robustness_pool import (
        load_perturbation_variants, stored_variant_fingerprint, variant_fingerprint,
    )
    for v in load_perturbation_variants(REPO_ROOT):
        if v.get("status") == "active":
            assert stored_variant_fingerprint(v) == variant_fingerprint(v)


def test_O_runtime_fingerprints_reproduce():
    from agent_arena import runtime_contract as rc
    for k in ("haiku", "sonnet"):
        assert rc.is_executable(rc.build_contract(k, REPO_ROOT))


def test_P_model_specific_reporting_path():
    # two models, one triggers an adversarial blocker, the other does not
    recs = []
    for i in range(5):
        recs += [mk_record("claude-haiku-4-5-20251001", "P7A-ADV-001", "adversarial_base", "A1",
                           "overclaim", "solid", i)]  # haiku wrong
        recs += [mk_record("claude-haiku-4-5-20251001", "P7A-ADV-002", "adversarial_base", "A1",
                           "overclaim", "solid", i)]  # haiku wrong (2/2)
        recs += [mk_record("claude-sonnet-4-5-20250929", "P7A-ADV-001", "adversarial_base", "A1",
                           "overclaim", "overclaim", i)]  # sonnet correct
        recs += [mk_record("claude-sonnet-4-5-20250929", "P7A-ADV-002", "adversarial_base", "A1",
                           "overclaim", "overclaim", i)]
    rep = build_phase7a_report(recs, dry_run=True)
    assert rep["per_model"]["claude-haiku-4-5-20251001"]["adversarial_family_results"]["status"] == "BLOCK"
    assert rep["per_model"]["claude-sonnet-4-5-20250929"]["adversarial_family_results"]["status"] == "OK"


def test_Q_boundary_rule_computable():
    # same directional confusion on 2 independent B1 cases (overclaim -> correlation)
    stabs = [
        mk_stab("m", "P7A-BND-001", "boundary_base", "B1", "overclaim", "correlation_vs_causation", 4),
        mk_stab("m", "P7A-BND-002", "boundary_base", "B1", "overclaim", "correlation_vs_causation", 3),
    ]
    a = boundary_assessment(stabs)
    assert a["status"] == "BLOCK"
    assert "B1:overclaim->correlation_vs_causation" in a["blocking_directions"]
    # single wrong case = INVESTIGATE, not BLOCK
    one = boundary_assessment([stabs[0]])
    assert one["status"] == "INVESTIGATE"


def test_R_adversarial_rule_computable():
    def fam(model, ids, labels):
        return [mk_stab(model, i, "adversarial_base", "A5", "overclaim", lab, 4)
                for i, lab in zip(ids, labels)]
    # 2/2 wrong -> BLOCK
    assert adversarial_assessment(fam("m", ["a", "b"], ["solid", "solid"]))["families"]["A5"]["verdict"] == "BLOCK"
    # 1/2 -> INVESTIGATE
    assert adversarial_assessment(fam("m", ["a", "b"], ["solid", "overclaim"]))["families"]["A5"]["verdict"] == "INVESTIGATE"
    # 0/2 -> PASS
    assert adversarial_assessment(fam("m", ["a", "b"], ["overclaim", "overclaim"]))["families"]["A5"]["verdict"] == "PASS"


def test_S_perturbation_rule_computable():
    # roots (bases) modal correct; variants flip
    def cluster(root_id, root_gold, fam_flips):
        stabs = [mk_stab("m", root_id, "neutral_base", "solid", root_gold, root_gold, 5)]
        for fam, flip_to in fam_flips.items():
            stabs.append(mk_stab("m", f"{root_id}-{fam}", "perturbation_variant", fam, root_gold,
                                 flip_to, 4, cluster_root_id=root_id))
        return stabs
    # (G) same family flips in >=2 clusters
    g = cluster("R1", "solid", {"P1": "overclaim"}) + cluster("R2", "solid", {"P1": "overclaim"})
    ag = perturbation_assessment(g)
    assert ag["status"] == "BLOCK"
    assert "P1" in ag["family_multi_cluster_flips"]
    # (H) one cluster flips under >=2 families
    h = cluster("R3", "solid", {"P1": "overclaim", "P2": "overclaim"})
    ah = perturbation_assessment(h)
    assert ah["status"] == "BLOCK"
    assert "R3" in ah["cluster_multi_family_flips"]
    # no flips -> OK
    ok = cluster("R4", "solid", {"P1": "solid"})
    assert perturbation_assessment(ok)["status"] == "OK"


def test_T_replication_stability_computable():
    # >=2 same-family fragile-or-worse -> BLOCK
    stabs = [
        mk_stab("m", "P7A-BND-001", "boundary_base", "B1", "overclaim", "overclaim", 3),  # fragile
        mk_stab("m", "P7A-BND-002", "boundary_base", "B1", "overclaim", "overclaim", 2),  # unstable
    ]
    assert replication_assessment(stabs)["status"] == "BLOCK"
    # infra failures excluded (provider errors do not count as instability)
    infra = [mk_stab("m", "P7A-BND-001", "boundary_base", "B1", "overclaim", "overclaim", 2,
                     n_provider_errors=3)]
    assert replication_assessment(infra)["status"] == "OK"


def test_U_raw_records_are_replication_level():
    units = resolve_evaluated_units(REPO_ROOT)[:3]
    recs = execute(units, lambda mid: FakeLibraryProvider(model=mid), dry_run=True)
    # 3 units x 5 reps x 2 models = 30 records, each with a distinct run_index per (model, unit)
    assert len(recs) == 3 * 5 * 2
    by_key = {}
    for r in recs:
        by_key.setdefault((r["model"], r["unit_id"]), set()).add(r["run_index"])
    for key, idxs in by_key.items():
        assert idxs == {0, 1, 2, 3, 4}, key


def test_V_dry_run_clearly_separated():
    units = resolve_evaluated_units(REPO_ROOT)[:2]
    recs = execute(units, lambda mid: FakeLibraryProvider(model=mid), dry_run=True)
    assert all(r["dry_run"] is True for r in recs)
    rep = build_phase7a_report(recs, dry_run=True)
    assert rep["dry_run"] is True and rep["synthetic_non_analytical"] is True


# ===========================================================================
# §38 dry-run stability paths A-D (aggregate)
# ===========================================================================

def test_38A_all_correct_unanimous():
    recs = unit_records("m", "u", "boundary_base", "B1", "overclaim", ["overclaim"] * 5)
    s = aggregate(recs)[0]
    assert s.stability_tier == TIER_UNANIMOUS and s.modal_support == 5 and s.modal_correct is True


def test_38B_stable_majority_4of5():
    recs = unit_records("m", "u", "boundary_base", "B1", "overclaim",
                        ["overclaim", "overclaim", "overclaim", "overclaim", "solid"])
    s = aggregate(recs)[0]
    assert s.stability_tier == TIER_STABLE_MAJORITY and s.modal_support == 4


def test_38C_fragile_3of5():
    recs = unit_records("m", "u", "boundary_base", "B1", "overclaim",
                        ["overclaim", "overclaim", "overclaim", "solid", "solid"])
    s = aggregate(recs)[0]
    assert s.stability_tier == TIER_FRAGILE and s.modal_support == 3


def test_38D_provider_error_path():
    recs = unit_records("m", "u", "boundary_base", "B1", "overclaim",
                        ["overclaim", "overclaim", None, None, None],
                        errors=[None, None, "timeout", "timeout", "timeout"])
    s = aggregate(recs)[0]
    assert s.n_provider_errors == 3 and s.n_labelled == 2
    # a case that is only unstable because of infra failures is excluded from replication BLOCK
    assert replication_assessment([s])["status"] == "OK"


def test_38I_38J_model_specific_blockers():
    # Haiku-only boundary blocker; Sonnet clean
    recs = []
    for i in range(5):
        for uid in ("P7A-BND-001", "P7A-BND-002"):
            recs.append(mk_record("claude-haiku-4-5-20251001", uid, "boundary_base", "B1",
                                  "overclaim", "correlation_vs_causation", i))
            recs.append(mk_record("claude-sonnet-4-5-20250929", uid, "boundary_base", "B1",
                                  "overclaim", "overclaim", i))
    rep = build_phase7a_report(recs, dry_run=True)
    assert rep["per_model"]["claude-haiku-4-5-20251001"]["boundary_family_results"]["status"] == "BLOCK"
    assert rep["per_model"]["claude-sonnet-4-5-20250929"]["boundary_family_results"]["status"] == "OK"
    # symmetric: Sonnet-only
    recs2 = []
    for i in range(5):
        for uid in ("P7A-ADV-003", "P7A-ADV-004"):
            recs2.append(mk_record("claude-sonnet-4-5-20250929", uid, "adversarial_base", "A2",
                                   "mechanism_vs_evidence", "overclaim", i))
            recs2.append(mk_record("claude-haiku-4-5-20251001", uid, "adversarial_base", "A2",
                                   "mechanism_vs_evidence", "mechanism_vs_evidence", i))
    rep2 = build_phase7a_report(recs2, dry_run=True)
    assert rep2["per_model"]["claude-sonnet-4-5-20250929"]["adversarial_family_results"]["status"] == "BLOCK"
    assert rep2["per_model"]["claude-haiku-4-5-20251001"]["adversarial_family_results"]["status"] == "OK"


# ===========================================================================
# End-to-end dry run (fake provider) — full 84x5x2 mechanics
# ===========================================================================

def test_full_dry_run_mechanics():
    units = resolve_evaluated_units(REPO_ROOT)
    recs = execute(units, lambda mid: FakeLibraryProvider(model=mid), dry_run=True)
    assert len(recs) == EXPECTED_PLANNED_CALLS == 840
    report = build_phase7a_report(recs, dry_run=True)
    assert report["accounting"]["n_independent_bases"] == 34
    assert report["accounting"]["n_evaluated_units"] == 84
    assert report["accounting"]["n_perturbation_variants"] == 50
    assert report["accounting"]["n_perturbation_clusters"] == 10
    assert report["accounting"]["no_pooled_headline_score"] is True
    assert set(report["models"]) == set(PRIMARY_MODELS)
    # fake echoes gold -> all triggers OK (no fabricated failure)
    for m in PRIMARY_MODELS:
        trig = report["per_model"][m]["systematic_failure_triggers"]
        assert set(trig.values()) == {"OK"}
        assert report["per_model"][m]["model_summary"]["accuracy_all_units"] == 1.0


def test_manifest_and_plan_fingerprints_present():
    m = build_execution_manifest(REPO_ROOT)
    p = build_call_plan(REPO_ROOT)
    assert len(m["execution_manifest_fingerprint"]) == 64
    assert len(m["scientific_manifest_fingerprint"]) == 64
    assert len(p["call_plan_fingerprint"]) == 64
    assert p["package_fingerprint"] and len(p["package_fingerprint"]) == 64
    assert set(p["runtime_contract_fingerprints"]) == set(PRIMARY_MODELS)
    assert m["model_calls"] == 0 and p["model_calls"] == 0


def test_unit_type_breakdown(units):
    b = unit_type_breakdown(units)
    assert b == {"boundary_base": 14, "adversarial_base": 16, "neutral_base": 4,
                 "perturbation_variant": 50}


def test_resume_merge_never_overwrites_completed():
    from agent_arena.phase7a_execution import is_completed, merge_records, replication_key
    completed = mk_record("m", "u", "boundary_base", "B1", "overclaim", "overclaim", 0)
    errored = mk_record("m", "u", "boundary_base", "B1", "overclaim", None, 1, error="timeout",
                        parse_ok=False)
    assert is_completed(completed) and not is_completed(errored)
    assert replication_key(completed) == ("m", "u", 0)
    # a completed record is never overwritten by a re-run of the same key
    dup = mk_record("m", "u", "boundary_base", "B1", "overclaim", "solid", 0)  # different label, same key
    r1 = merge_records([completed], [dup])
    assert r1["skipped_completed"] == 1 and r1["n_total"] == 1
    assert r1["records"][0]["label"] == "overclaim"  # original completed preserved
    # an errored record IS replaced by a later completed retry for the same key
    retry = mk_record("m", "u", "boundary_base", "B1", "overclaim", "overclaim", 1)
    r2 = merge_records([errored], [retry])
    assert r2["replaced_error"] == 1 and r2["records"][0]["label"] == "overclaim"


# ===========================================================================
# Repair Phase 1 — terminal, classification, and calibration state separation
# ===========================================================================

@pytest.mark.parametrize(("case", "overrides", "expected"), [
    ("provider_error", {"error": "timeout", "parse_ok": False, "label": None,
                        "confidence": None, "confidence_state": MISSING},
     (False, False, False, True)),
    ("parser_failure", {"parse_ok": False, "label": None,
                        "confidence": None, "confidence_state": MISSING},
     (True, False, False, False)),
    ("truncated_malformed", {"parse_ok": False, "truncation_suspected": True,
                             "label": None, "confidence": None,
                             "confidence_state": MISSING},
     (True, False, False, False)),
    ("missing_label", {"parse_ok": True, "label": None},
     (True, False, False, False)),
    ("unexpected_label", {"parse_ok": True, "label": "unexpected"},
     (True, False, False, False)),
    ("invalid_confidence", {"parse_ok": True, "label": "overclaim",
                            "confidence": None, "confidence_state": INVALID},
     (True, True, False, False)),
    ("fully_valid", {"parse_ok": True, "label": "overclaim",
                     "confidence": 0.8, "confidence_state": VALID},
     (True, True, True, False)),
])
def test_analytical_state_completion_matrix(case, overrides, expected):
    values = {
        "error": None, "parse_ok": True, "label": "overclaim", "confidence": 0.8,
        "confidence_state": VALID, "truncation_suspected": False,
    }
    values.update(overrides)
    rec = mk_record(
        "m", "u", "boundary_base", "B1", "overclaim", values["label"], 0,
        error=values["error"], parse_ok=values["parse_ok"],
        confidence=values["confidence"], confidence_state=values["confidence_state"],
        truncation_suspected=values["truncation_suspected"],
    )
    actual = (
        is_terminal_attempt(rec), is_classification_valid(rec),
        is_calibration_valid(rec), model_call_again_allowed(rec),
    )
    assert actual == expected, case
    assert (rec["brier_contribution"] is not None) is expected[2]


@pytest.mark.parametrize("state", [MISSING, INVALID])
def test_invalid_or_missing_confidence_preserves_classification_but_excludes_calibration(state):
    rec = mk_record(
        "m", "u", "boundary_base", "B1", "overclaim", "overclaim", 0,
        confidence=None, confidence_state=state,
    )
    assert is_classification_valid(rec) is True
    assert is_calibration_valid(rec) is False
    assert rec["brier_contribution"] is None


def test_stored_valid_state_cannot_override_an_invalid_numeric_representation():
    rec = mk_record(
        "m", "u", "boundary_base", "B1", "overclaim", "overclaim", 0,
        confidence=None, confidence_state=VALID,
    )
    assert is_classification_valid(rec) is True
    assert is_calibration_valid(rec) is False
    assert rec["brier_contribution"] is None


def test_unknown_stored_confidence_state_fails_closed():
    rec = mk_record(
        "m", "u", "boundary_base", "B1", "overclaim", "overclaim", 0,
        confidence=0.8, confidence_state="BOGUS",
    )
    assert is_classification_valid(rec) is True
    assert is_calibration_valid(rec) is False
    assert rec["brier_contribution"] is None


# ===========================================================================
# WP-4.1 P0 — executable QA provenance + execution-type provenance
# ===========================================================================

def _write_test(dirpath: Path, body: str) -> None:
    (dirpath / "test_tmp.py").write_text(body)


def test_qa_real_execution_pass(tmp_path):
    _write_test(tmp_path, "def test_a():\n    assert 1 == 1\n\ndef test_b():\n    assert True\n")
    qa = execute_qa(repo_root=tmp_path)
    assert qa["qa_kind"] == "pytest_diagnostic_non_authorizing"
    assert qa["exit_code"] == 0
    assert qa["tests_collected"] == 2 and qa["tests_passed"] == 2 and qa["tests_failed"] == 0
    assert qa["produced_by"] == "agent_arena.preflight_integrity.execute_diagnostic_qa"
    assert classify_qa(qa) == pi.QA_NON_AUTHORIZING


def test_qa_real_execution_nonzero_fails_closed(tmp_path):
    # §13: pytest non-zero exit path (synthetic — never breaks the real suite)
    _write_test(tmp_path, "def test_a():\n    assert 1 == 2\n\ndef test_b():\n    assert True\n")
    qa = execute_qa(repo_root=tmp_path)
    assert qa["exit_code"] != 0 and qa["tests_failed"] == 1
    assert classify_qa(qa) == pi.QA_FAILED


def test_qa_no_tests_fails_closed(tmp_path):
    qa = execute_qa(repo_root=tmp_path)  # empty dir -> pytest exit 5, 0 collected
    assert qa["tests_collected"] == 0
    assert classify_qa(qa) == pi.QA_FAILED


def test_qa_tests_not_executed_is_fail_closed():
    # §4: no genuine execution -> TESTS_NOT_EXECUTED (never inferred PASS from a constant)
    assert classify_qa(None) == pi.QA_NOT_EXECUTED
    assert classify_qa({"tests_passed": 9999}) == pi.QA_NON_AUTHORIZING
    pf = diagnostic_preflight(REPO_ROOT, run_qa=False)
    assert pf["qa_status"] == pi.QA_NOT_EXECUTED
    assert pf["go"] is False
    assert pf["production_authorizing"] is False


def test_caller_supplied_green_qa_cannot_reach_production_preflight():
    pass_qa = {"qa_kind": "pytest_execution", "exit_code": 0, "tests_collected": 1516,
               "tests_passed": 1516, "tests_failed": 0, "tests_errors": 0,
               "qa_record_fingerprint": "x" * 64}
    with pytest.raises(TypeError):
        real_run_preflight(REPO_ROOT, qa_record=pass_qa)


def test_invalid_source_prevents_canonical_qa_launch():
    calls = 0

    def qa_executor(root, binding):
        nonlocal calls
        calls += 1
        raise AssertionError("QA must not launch")

    pf = __import__(
        "agent_arena.phase7a_execution", fromlist=["_production_preflight"]
    )._production_preflight(
        REPO_ROOT,
        qa_executor=qa_executor,
        source_inspector=lambda root: {"valid": False, "errors": ["dirty"]},
    )
    assert pf["go"] is False
    assert pf["qa_status"] == pi.QA_NOT_EXECUTED
    assert calls == 0


def test_no_hardcoded_pass_in_module():
    # §5: the module must not encode a fixed truth test count as a QA pass condition
    src = (REPO_ROOT / "src" / "agent_arena" / "phase7a_execution.py").read_text()
    assert "1516" not in src and "1484" not in src


def test_execution_type_recorded_dry_run():
    units = resolve_evaluated_units(REPO_ROOT)[:2]
    recs = execute(units, lambda mid: FakeLibraryProvider(model=mid), dry_run=True)
    assert all(r["execution_type"] == EXEC_TYPE_DRY_RUN for r in recs)


def test_execution_type_adjudication_vs_reproduction():
    units = resolve_evaluated_units(REPO_ROOT)[:2]
    adj = execute(units, lambda mid: FakeLibraryProvider(model=mid), dry_run=False,
                  execution_type=EXEC_TYPE_ADJUDICATION)
    rep = execute(units, lambda mid: FakeLibraryProvider(model=mid), dry_run=False,
                  execution_type=EXEC_TYPE_REPRODUCTION)
    assert all(r["execution_type"] == EXEC_TYPE_ADJUDICATION for r in adj)
    assert all(r["execution_type"] == EXEC_TYPE_REPRODUCTION for r in rep)
    assert EXEC_TYPE_ADJUDICATION != EXEC_TYPE_REPRODUCTION
    with pytest.raises(ValueError):
        execute(units, lambda mid: FakeLibraryProvider(model=mid), execution_type="bogus")


def test_run_metadata_three_layers():
    meta = run_metadata(EXEC_TYPE_ADJUDICATION, REPO_ROOT)
    assert meta["execution_type"] == EXEC_TYPE_ADJUDICATION
    assert meta["reproduction_of_frozen_records"] is False
    layers = meta["layers"]
    assert set(layers) == {"model_execution", "harness_execution", "report_render"}
    assert set(layers["model_execution"]["runtime_contract_fingerprints"]) == set(PRIMARY_MODELS)
    assert layers["harness_execution"]["package_fingerprint"]
    assert run_metadata(EXEC_TYPE_REPRODUCTION, REPO_ROOT)["reproduction_of_frozen_records"] is True
    assert set(EXECUTION_TYPES) == {EXEC_TYPE_ADJUDICATION, EXEC_TYPE_REPRODUCTION, EXEC_TYPE_DRY_RUN}


def test_frozen_artifacts_match_live_state():
    # committed manifest/plan must equal the freshly recomputed ones (drift gate)
    import json
    from agent_arena.phase7a_execution import (
        CALL_PLAN_FILE, EXECUTION_MANIFEST_FILE, _ARTIFACT_DIR,
    )
    mpath = REPO_ROOT / _ARTIFACT_DIR / EXECUTION_MANIFEST_FILE
    ppath = REPO_ROOT / _ARTIFACT_DIR / CALL_PLAN_FILE
    if not (mpath.exists() and ppath.exists()):
        pytest.skip("frozen artifacts not present")
    fm = json.loads(mpath.read_text())
    fp = json.loads(ppath.read_text())
    assert fm["execution_manifest_fingerprint"] == build_execution_manifest(REPO_ROOT)["execution_manifest_fingerprint"]
    assert fp["call_plan_fingerprint"] == build_call_plan(REPO_ROOT)["call_plan_fingerprint"]
