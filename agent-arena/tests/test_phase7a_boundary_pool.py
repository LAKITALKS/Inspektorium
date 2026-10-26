"""Phase-7A Boundary robustness pool — structural validation (post-audit REPAIR re-freeze).

Deterministic, offline, **no model scoring**. Validates the repaired class-B Boundary pool in
``tasks/study_forensics_robustness/`` — 14 ACTIVE re-frozen cases + 3 RETIRED historical cases —
its real public-claim provenance / source-role metadata, and its isolation from the class-A Case
Library. Covers repair-WP §38 checks A-Q.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from agent_arena import run_library
from agent_arena.robustness_pool import (
    CLAIM_SOURCE_ROLE,
    EVIDENCE_SOURCE_ROLES,
    EXPECTED_FAMILY_COUNTS,
    EXPECTED_GOLD_COUNTS,
    EXPECTED_N_CASES,
    GOLD_LABELS,
    NON_PRIMARY_EVIDENCE_ORGS,
    ROBUSTNESS_DIR,
    SOURCE_ROLES,
    boundary_dir,
    case_fingerprint,
    claim_provenance_status,
    load_active_boundary_cases,
    load_boundary_cases,
    load_retired_boundary_cases,
    stored_fingerprint,
    verify_pool,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

# Frozen WP-1 baseline (see analysis/phase7a_startup/phase7a_reconstruction.md §A / F).
BASELINE_ACTIVE_LIBRARY = 48
BASELINE_LIBRARY_INCL_RETIRED = 50

# Required frozen fields on every boundary case (case/perturbation contract §8, WP-1 §19).
REQUIRED_TOP_FIELDS = (
    "id", "prompt", "context", "gold_label", "gold_confidence", "gold_case_type",
    "gold_justification", "gold_alternative_reading", "origin", "status", "gold_status",
)
REQUIRED_ROBUSTNESS_FIELDS = (
    "robustness_case_id", "case_family", "boundary_family_id", "boundary", "gold_status",
    "difficulty_tier", "difficulty_rationale", "precedence_rationale", "ambiguity_note",
    "steelman_challenge", "provenance", "hypothesis_map", "case_fingerprint",
)
# Real public-claim provenance fields required on every ACTIVE case (repair WP §5/§23).
REQUIRED_PROVENANCE_FIELDS = (
    "claim_source_title", "claim_source_url", "claim_source_publisher", "claim_source_role",
    "claim_source_type", "claim_context", "claim_exact_span",
)

# Keys that would indicate a model output / run result leaked into a frozen case (§44 TEST L).
FORBIDDEN_RESULT_KEYS = {
    "detected_label", "label_correct", "brier", "ece", "accuracy", "run_index",
    "raw_output", "model_output", "parsed", "library_run_id", "finish_reason",
    "latency_ms", "usage", "modal_label", "label_switch_count",
}
# Holdout / private-mapping terms that must never appear in a class-B case (§44 TEST M).
FORBIDDEN_HOLDOUT_TERMS = ("holdout", "salt", "envelope", "identity_map", "identity map")
# Client / LaVita material must never appear in a class-B case (§38 Q).
FORBIDDEN_CLIENT_TERMS = ("lavita",)


@pytest.fixture(scope="module")
def all_cases():
    return load_boundary_cases(REPO_ROOT)


@pytest.fixture(scope="module")
def active():
    return load_active_boundary_cases(REPO_ROOT)


@pytest.fixture(scope="module")
def retired():
    return load_retired_boundary_cases(REPO_ROOT)


@pytest.fixture(scope="module")
def report():
    return verify_pool(REPO_ROOT)


def _iter_keys(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from _iter_keys(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _iter_keys(v)


# --- TEST A: robustness dir does not alter normal Case Library discovery -----
def test_A_class_a_discovery_unchanged():
    task_dir = REPO_ROOT / "tasks" / "study_forensics"
    active = run_library.discover_cases(task_dir=task_dir)
    incl = run_library.discover_cases(task_dir=task_dir, include_retired=True)
    assert len(active) == BASELINE_ACTIVE_LIBRARY
    assert len(incl) == BASELINE_LIBRARY_INCL_RETIRED
    assert run_library.TASK_DIR == Path("tasks/study_forensics")
    assert ROBUSTNESS_DIR == Path("tasks/study_forensics_robustness")
    assert ROBUSTNESS_DIR != run_library.TASK_DIR
    assert not str(ROBUSTNESS_DIR).startswith(str(run_library.TASK_DIR) + "/")


# --- TEST B: exactly 14 ACTIVE boundary cases ------------------------------
def test_B_exactly_14_active(active):
    assert len(active) == EXPECTED_N_CASES
    assert all(c["status"] == "active" for _, c in active)
    assert all(not c.get("excluded_from_active_metrics", False) for _, c in active)


# --- TEST C: family counts 5/5/4 (active) -----------------------------------
def test_C_family_counts(report):
    assert report["family_counts"] == EXPECTED_FAMILY_COUNTS


# --- TEST D: gold counts 8/2/2/2 (active) -----------------------------------
def test_D_gold_counts(report):
    assert report["gold_counts"] == EXPECTED_GOLD_COUNTS


# --- TEST E: IDs unique; every active case has real claim provenance ---------
def test_E_active_ids_and_provenance(active, report):
    assert report["unique_ids"]
    assert all(i.startswith("P7A-BND-") for i in report["ids"])
    for f, c in active:
        st = claim_provenance_status(c)
        assert st["passes"], f"{f.name} provenance FAIL: {st['reasons']}"
        prov = c["robustness"]["provenance"]
        for k in REQUIRED_PROVENANCE_FIELDS:
            assert str(prov.get(k) or "").strip(), f"{f.name} missing provenance.{k}"
        assert prov["claim_source_url"].startswith("http"), f"{f.name} claim_source_url not a URL"
        assert prov["claim_source_role"] == CLAIM_SOURCE_ROLE


# --- TEST F: fingerprints unique and reproducible (active + retired) ---------
def test_F_fingerprints_unique_and_reproduce(all_cases, report):
    assert report["unique_fingerprints"]
    assert report["unique_fingerprints_incl_retired"]
    assert report["fingerprints_reproduce"]
    for _, c in all_cases:
        assert stored_fingerprint(c) == case_fingerprint(c)
        assert stored_fingerprint(c) != "PENDING"
        assert len(stored_fingerprint(c)) == 64  # sha256 hex


# --- TEST G: all mandatory gold/preference fields present (active) ----------
def test_G_mandatory_fields_present(active):
    for f, c in active:
        for k in REQUIRED_TOP_FIELDS:
            assert c.get(k) not in (None, ""), f"{f.name} missing {k}"
        rob = c.get("robustness") or {}
        for k in REQUIRED_ROBUSTNESS_FIELDS:
            assert rob.get(k) not in (None, ""), f"{f.name} missing robustness.{k}"
        assert c["gold_label"] in GOLD_LABELS
        assert c["task_family"] == c["gold_label"]  # class-A convention consistency
        assert c["gold_status"] == "frozen_pre_model"


# --- TEST H: every active case has a plausible alternative reading ----------
def test_H_alternative_reading(active):
    for f, c in active:
        alt = c.get("gold_alternative_reading", "")
        assert isinstance(alt, str) and len(alt.strip()) > 30, f.name
        competing = c["robustness"]["hypothesis_map"]["most_plausible_competing_label"]
        assert competing in GOLD_LABELS
        assert competing != c["gold_label"], f"{f.name}: alternative equals gold"


# --- TEST I: every active case has difficulty metadata ----------------------
def test_I_difficulty_metadata(active):
    for f, c in active:
        tier = c["robustness"]["difficulty_tier"]
        assert tier in {"D1", "D2", "D3"}, f.name
        assert len(c["robustness"]["difficulty_rationale"].strip()) > 30, f.name
    tiers = {c["robustness"]["difficulty_tier"] for _, c in active}
    assert len(tiers) >= 2


# --- TEST F/§23: source roles use the controlled vocabulary -----------------
def test_source_roles_controlled_vocabulary(active):
    for f, c in active:
        prov = c["robustness"]["provenance"]
        assert prov["claim_source_role"] in SOURCE_ROLES, f.name
        ev = prov.get("evidence_sources") or []
        assert ev, f"{f.name} has no evidence source"
        for e in ev:
            assert e.get("source_role") in EVIDENCE_SOURCE_ROLES, (
                f"{f.name}: evidence source_role {e.get('source_role')!r} not in vocabulary"
            )


# --- TEST §24: known non-primary bodies are not mislabeled primary_research -
def test_source_role_guard_non_primary_orgs(active):
    for f, c in active:
        for e in c["robustness"]["provenance"].get("evidence_sources") or []:
            cite = str(e.get("citation") or "").lower()
            for org, expected in NON_PRIMARY_EVIDENCE_ORGS.items():
                if org in cite:
                    assert e.get("source_role") != "primary_research", (
                        f"{f.name}: '{org}' evidence mislabeled primary_research (expected {expected})"
                    )


# --- TEST §17/H: no active archetype-only claim without a public source ------
def test_active_claim_bound_to_public_source(active):
    for f, c in active:
        prov = c["robustness"]["provenance"]
        # a resolvable public claim: URL + a bounded exact span the source can be checked against
        assert prov["claim_source_url"].startswith("http"), f.name
        assert len(str(prov["claim_exact_span"]).strip()) > 10, f.name
        # evidence basis separate and resolvable
        for e in prov.get("evidence_sources") or []:
            assert e.get("url") and e.get("result") and e.get("design"), f.name
        assert prov.get("access_date")


# --- TEST I/§18: retired cases carry full retirement governance --------------
def test_retired_governance(retired):
    assert len(retired) == 4
    expected_supersede = {
        "P7A-BND-003": "P7A-BND-017",
        "P7A-BND-006": "P7A-BND-018",
        "P7A-BND-007": "P7A-BND-015",
        "P7A-BND-008": "P7A-BND-016",
    }
    for f, c in retired:
        assert c["status"] == "retired", f.name
        assert c["excluded_from_active_metrics"] is True, f.name
        assert c["superseded_by"] == expected_supersede[c["id"]], f.name
        sh = c.get("suite_history") or []
        assert sh and sh[0]["label_flip"] is False, f.name
        assert sh[0].get("prior_case_fingerprint"), f.name
        assert sh[0].get("audit_reference"), f.name


# --- TEST J: replacement IDs do not collide and supersede retired -----------
def test_J_replacement_ids(all_cases, active):
    ids = [c["id"] for _, c in all_cases]
    assert len(ids) == len(set(ids))  # no collisions across active + retired
    by_id = {c["id"]: c for _, c in active}
    for new_id, retired_id in (("P7A-BND-015", "P7A-BND-007"),
                               ("P7A-BND-016", "P7A-BND-008"),
                               ("P7A-BND-017", "P7A-BND-003"),
                               ("P7A-BND-018", "P7A-BND-006")):
        assert new_id in by_id, f"{new_id} not active"
        assert by_id[new_id]["supersedes"] == retired_id


# --- TEST M/§38 J: no Phase-7B QA fixture discoverable as Phase-7A ----------
def test_M_no_phase7b_fixture_in_pool(all_cases):
    for _, c in all_cases:
        assert c["id"].startswith("P7A-BND-")
        assert not any(c["id"].startswith(f"R{n}") for n in range(1, 9))
    names = {p.name for p in boundary_dir(REPO_ROOT).iterdir()}
    assert not any(n.lower().startswith(("r1", "r2", "r3", "r4", "r5", "r6", "r7", "r8"))
                   for n in names)


# --- TEST N: no Boundary case discoverable as normal Case Library case ------
def test_N_no_boundary_in_class_a(all_cases):
    task_dir = REPO_ROOT / "tasks" / "study_forensics"
    class_a_ids = {t.id for _, t in run_library.discover_cases(task_dir=task_dir, include_retired=True)}
    boundary_ids = {c["id"] for _, c in all_cases}
    assert class_a_ids.isdisjoint(boundary_ids)
    for f, _ in all_cases:
        assert f.parent.name == "study_forensics_robustness"


# --- TEST O: no model response / result artifacts in the pool ---------------
def test_O_no_model_results(all_cases):
    for f, c in all_cases:
        present = set(_iter_keys(c))
        leaked = present & FORBIDDEN_RESULT_KEYS
        assert not leaked, f"{f.name} contains result-like keys: {leaked}"
    for p in boundary_dir(REPO_ROOT).iterdir():
        assert not (p.suffix == ".json"), f"unexpected json artifact: {p.name}"


# --- TEST P: no holdout references ------------------------------------------
def test_P_no_holdout_references(all_cases):
    for f, c in all_cases:
        text = yaml.safe_dump(c, allow_unicode=True).lower()
        for term in FORBIDDEN_HOLDOUT_TERMS:
            assert term not in text, f"{f.name} references '{term}'"


# --- TEST Q: no client / LaVita material ------------------------------------
def test_Q_no_client_material(all_cases):
    for f, c in all_cases:
        text = yaml.safe_dump(c, allow_unicode=True).lower()
        for term in FORBIDDEN_CLIENT_TERMS:
            assert term not in text, f"{f.name} references client term '{term}'"


# --- extra: steelman challenge present (§24) --------------------------------
def test_steelman_present(active):
    for f, c in active:
        assert len(c["robustness"]["steelman_challenge"].strip()) > 40, f.name


# --- TEST L: manifest matches the active pool + retired section -------------
def test_L_manifest_matches_pool(active, retired):
    manifest = yaml.safe_load(
        (boundary_dir(REPO_ROOT) / "boundary_manifest.yaml").read_text(encoding="utf-8")
    )
    assert manifest["model_calls"] == 0
    assert manifest["holdout_touched"] is False
    assert manifest["repair"] == "post_audit_refreeze"
    assert len(manifest["cases"]) == EXPECTED_N_CASES
    assert len(manifest["retired_cases"]) == 4

    fp_active = {c["id"]: stored_fingerprint(c) for _, c in active}
    for row in manifest["cases"]:
        assert row["status"] == "active"
        assert row["case_fingerprint"] == fp_active[row["id"]]
    fp_retired = {c["id"]: stored_fingerprint(c) for _, c in retired}
    for row in manifest["retired_cases"]:
        assert row["status"] == "retired"
        assert row["excluded_from_active_metrics"] is True
        assert row["case_fingerprint"] == fp_retired[row["id"]]
    assert manifest["verification"]["family_counts_match_expected"] is True
    assert manifest["verification"]["gold_counts_match_expected"] is True
    assert manifest["verification"]["claim_provenance_all_pass"] is True
    assert manifest["verification"]["n_active"] == 14
    assert manifest["verification"]["n_retired"] == 4
