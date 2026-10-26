"""Phase-7A Adversarial robustness pool (7A.3) — structural validation.

Deterministic, offline, **no model scoring**. Validates the class-B Adversarial pool in
``tasks/study_forensics_robustness/`` (``P7A-ADV-*.yaml``) — 16 ACTIVE frozen cases across the 8
frozen adversarial families (A1-A8, 2 each) — its real public-claim provenance / source-role
metadata, its adversarial-mechanism / gold / steelman / difficulty metadata, and its isolation from
the class-A Case Library and the Boundary pool. Covers WP-2 §36 checks A-Q.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from agent_arena import run_library
from agent_arena.robustness_pool import (
    ADVERSARIAL_FAMILY_IDS,
    EVIDENCE_SOURCE_ROLES,
    EXPECTED_ADVERSARIAL_FAMILY_COUNTS,
    EXPECTED_ADVERSARIAL_GOLD_COUNTS,
    EXPECTED_N_ADVERSARIAL,
    GOLD_LABELS,
    NON_PRIMARY_EVIDENCE_ORGS,
    SOURCE_ROLES,
    CLAIM_SOURCE_ROLE,
    adversarial_dir,
    case_fingerprint,
    claim_provenance_status,
    load_active_adversarial_cases,
    load_adversarial_cases,
    load_retired_adversarial_cases,
    load_active_boundary_cases,
    load_retired_boundary_cases,
    stored_fingerprint,
    verify_adversarial_pool,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

# Frozen WP-1 baseline (unchanged by WP-2): class-A active library discovery counts.
BASELINE_ACTIVE_LIBRARY = 48
BASELINE_LIBRARY_INCL_RETIRED = 50
# Boundary counts must remain untouched (WP-2 §36 Q).
BOUNDARY_ACTIVE = 14
BOUNDARY_RETIRED = 4

# Required frozen top-level fields on every adversarial case (case contract §8, WP-2 §19).
REQUIRED_TOP_FIELDS = (
    "id", "prompt", "context", "gold_label", "gold_confidence", "gold_case_type",
    "gold_justification", "gold_alternative_reading", "origin", "status", "gold_status",
)
# Required robustness fields (adversarial variant of the Boundary contract).
REQUIRED_ROBUSTNESS_FIELDS = (
    "robustness_case_id", "case_family", "adversarial_family_id", "adversarial_family",
    "adversarial_mechanism", "gold_status", "difficulty_tier", "difficulty_rationale",
    "precedence_rationale", "ambiguity_note", "steelman_challenge", "provenance",
    "hypothesis_map", "case_fingerprint",
)
# Real public-claim provenance fields required on every active case (WP-2 §10/§19).
REQUIRED_PROVENANCE_FIELDS = (
    "claim_source_title", "claim_source_url", "claim_source_publisher", "claim_source_role",
    "claim_source_type", "claim_context", "claim_exact_span",
)

FORBIDDEN_RESULT_KEYS = {
    "detected_label", "label_correct", "brier", "ece", "accuracy", "run_index",
    "raw_output", "model_output", "parsed", "library_run_id", "finish_reason",
    "latency_ms", "usage", "modal_label", "label_switch_count",
}
FORBIDDEN_HOLDOUT_TERMS = ("holdout", "salt", "envelope", "identity_map", "identity map")
FORBIDDEN_CLIENT_TERMS = ("lavita",)


@pytest.fixture(scope="module")
def all_cases():
    return load_adversarial_cases(REPO_ROOT)


@pytest.fixture(scope="module")
def active():
    return load_active_adversarial_cases(REPO_ROOT)


@pytest.fixture(scope="module")
def report():
    return verify_adversarial_pool(REPO_ROOT)


def _iter_keys(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from _iter_keys(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _iter_keys(v)


# --- TEST A: adversarial pool does not alter normal Case Library discovery ---
def test_A_class_a_discovery_unchanged():
    task_dir = REPO_ROOT / "tasks" / "study_forensics"
    active = run_library.discover_cases(task_dir=task_dir)
    incl = run_library.discover_cases(task_dir=task_dir, include_retired=True)
    assert len(active) == BASELINE_ACTIVE_LIBRARY
    assert len(incl) == BASELINE_LIBRARY_INCL_RETIRED
    assert run_library.TASK_DIR == Path("tasks/study_forensics")


# --- TEST B: exactly 16 ACTIVE adversarial cases ----------------------------
def test_B_exactly_16_active(active):
    assert len(active) == EXPECTED_N_ADVERSARIAL
    assert all(c["status"] == "active" for _, c in active)
    assert all(not c.get("excluded_from_active_metrics", False) for _, c in active)
    assert all(f.name.startswith("P7A-ADV-") for f, _ in active)


# --- TEST C: exactly 2 active cases per A1-A8 family ------------------------
def test_C_family_counts(report):
    assert report["family_counts"] == EXPECTED_ADVERSARIAL_FAMILY_COUNTS
    assert report["family_counts_match_expected"]
    assert set(report["family_counts"]) == set(ADVERSARIAL_FAMILY_IDS)


# --- TEST D: IDs unique and in the adversarial namespace --------------------
def test_D_ids_unique_namespace(active, report):
    assert report["unique_ids"]
    assert all(i.startswith("P7A-ADV-") for i in report["ids"])


# --- TEST E: fingerprints unique and reproducible ---------------------------
def test_E_fingerprints_unique_and_reproduce(all_cases, report):
    assert report["unique_fingerprints"]
    assert report["unique_fingerprints_incl_retired"]
    assert report["fingerprints_reproduce"]
    for _, c in all_cases:
        assert stored_fingerprint(c) == case_fingerprint(c)
        assert stored_fingerprint(c) != "PENDING"
        assert len(stored_fingerprint(c)) == 64  # sha256 hex


# --- TEST F: every active case has real claim provenance --------------------
def test_F_claim_provenance(active):
    for f, c in active:
        st = claim_provenance_status(c)
        assert st["passes"], f"{f.name} provenance FAIL: {st['reasons']}"
        prov = c["robustness"]["provenance"]
        for k in REQUIRED_PROVENANCE_FIELDS:
            assert str(prov.get(k) or "").strip(), f"{f.name} missing provenance.{k}"
        assert prov["claim_source_url"].startswith("http"), f"{f.name} claim_source_url not a URL"
        assert prov["claim_source_role"] == CLAIM_SOURCE_ROLE
        assert len(str(prov["claim_exact_span"]).strip()) > 10, f.name
        assert prov.get("access_date")


# --- TEST G: evidence provenance / source-role metadata present -------------
def test_G_evidence_provenance_and_roles(active):
    for f, c in active:
        ev = c["robustness"]["provenance"].get("evidence_sources") or []
        assert ev, f"{f.name} has no evidence source"
        for e in ev:
            assert e.get("source_role") in EVIDENCE_SOURCE_ROLES, (
                f"{f.name}: evidence source_role {e.get('source_role')!r} not in vocabulary"
            )
            assert e.get("url") and e.get("result") and e.get("design"), f.name
        for role in [e.get("source_role") for e in ev]:
            assert role in SOURCE_ROLES


# --- TEST §24: known non-primary bodies not mislabeled primary_research -----
def test_source_role_guard_non_primary_orgs(active):
    for f, c in active:
        for e in c["robustness"]["provenance"].get("evidence_sources") or []:
            cite = str(e.get("citation") or "").lower()
            for org, expected in NON_PRIMARY_EVIDENCE_ORGS.items():
                if org in cite:
                    assert e.get("source_role") != "primary_research", (
                        f"{f.name}: '{org}' evidence mislabeled primary_research (expected {expected})"
                    )


# --- TEST H: every active case has gold justification + mandatory fields ----
def test_H_gold_justification_and_fields(active):
    for f, c in active:
        for k in REQUIRED_TOP_FIELDS:
            assert c.get(k) not in (None, ""), f"{f.name} missing {k}"
        rob = c.get("robustness") or {}
        for k in REQUIRED_ROBUSTNESS_FIELDS:
            assert rob.get(k) not in (None, ""), f"{f.name} missing robustness.{k}"
        assert len(str(c["gold_justification"]).strip()) > 60, f.name
        assert c["gold_label"] in GOLD_LABELS
        assert c["task_family"] == c["gold_label"]  # class-A convention consistency
        assert c["gold_status"] == "frozen_pre_model"
        assert rob["case_family"] == "adversarial"
        assert rob["adversarial_family_id"] in ADVERSARIAL_FAMILY_IDS


# --- TEST I: every active case has a genuine strongest-alternative / steelman -
def test_I_alternative_and_steelman(active):
    for f, c in active:
        alt = c.get("gold_alternative_reading", "")
        assert isinstance(alt, str) and len(alt.strip()) > 30, f.name
        competing = c["robustness"]["hypothesis_map"]["most_plausible_competing_label"]
        assert competing in GOLD_LABELS
        assert competing != c["gold_label"], f"{f.name}: alternative equals gold"
        assert len(str(c["robustness"]["steelman_challenge"]).strip()) > 40, f.name


# --- TEST J: every active case has adversarial-mechanism metadata -----------
def test_J_adversarial_mechanism(active):
    for f, c in active:
        mech = c["robustness"]["adversarial_mechanism"]
        assert isinstance(mech, str) and len(mech.strip()) > 40, f.name
        # the mechanism field is NOT the gold label
        assert c["gold_label"] not in {mech.strip()}
        fam = c["robustness"]["adversarial_family"]
        assert isinstance(fam, str) and len(fam.strip()) > 10, f.name


# --- TEST K: every active case has pre-result difficulty metadata -----------
def test_K_difficulty_metadata(active):
    for f, c in active:
        tier = c["robustness"]["difficulty_tier"]
        assert tier in {"D1", "D2", "D3"}, f.name
        assert len(str(c["robustness"]["difficulty_rationale"]).strip()) > 30, f.name
    tiers = {c["robustness"]["difficulty_tier"] for _, c in active}
    assert len(tiers) >= 2  # not all forced to one tier


# --- TEST: frozen emergent gold distribution --------------------------------
def test_gold_distribution_frozen(report):
    observed = {lbl: report["gold_counts"].get(lbl, 0) for lbl in GOLD_LABELS}
    expected = {lbl: EXPECTED_ADVERSARIAL_GOLD_COUNTS.get(lbl, 0) for lbl in GOLD_LABELS}
    assert observed == expected
    assert sum(observed.values()) == EXPECTED_N_ADVERSARIAL


# --- TEST L: no adversarial case discoverable as normal Class-A case --------
def test_L_no_adversarial_in_class_a(all_cases):
    task_dir = REPO_ROOT / "tasks" / "study_forensics"
    class_a_ids = {t.id for _, t in run_library.discover_cases(task_dir=task_dir, include_retired=True)}
    adv_ids = {c["id"] for _, c in all_cases}
    assert class_a_ids.isdisjoint(adv_ids)
    for f, _ in all_cases:
        assert f.parent.name == "study_forensics_robustness"


# --- TEST M: no Phase-7B QA fixture counted / discoverable as adversarial ----
def test_M_no_phase7b_fixture(all_cases):
    for _, c in all_cases:
        assert c["id"].startswith("P7A-ADV-")
        assert not any(c["id"].startswith(f"R{n}") for n in range(1, 9))


# --- TEST N: no holdout references ------------------------------------------
def test_N_no_holdout_references(all_cases):
    for f, c in all_cases:
        text = yaml.safe_dump(c, allow_unicode=True).lower()
        for term in FORBIDDEN_HOLDOUT_TERMS:
            assert term not in text, f"{f.name} references '{term}'"


# --- TEST O: no model response / result artifacts ---------------------------
def test_O_no_model_results(all_cases):
    for f, c in all_cases:
        present = set(_iter_keys(c))
        leaked = present & FORBIDDEN_RESULT_KEYS
        assert not leaked, f"{f.name} contains result-like keys: {leaked}"
    for p in adversarial_dir(REPO_ROOT).glob("P7A-ADV-*.json"):
        raise AssertionError(f"unexpected json artifact: {p.name}")


# --- TEST P: no client / LaVita material ------------------------------------
def test_P_no_client_material(all_cases):
    for f, c in all_cases:
        text = yaml.safe_dump(c, allow_unicode=True).lower()
        for term in FORBIDDEN_CLIENT_TERMS:
            assert term not in text, f"{f.name} references client term '{term}'"


# --- TEST Q: Boundary active/retired counts unchanged -----------------------
def test_Q_boundary_counts_unchanged():
    assert len(load_active_boundary_cases(REPO_ROOT)) == BOUNDARY_ACTIVE
    assert len(load_retired_boundary_cases(REPO_ROOT)) == BOUNDARY_RETIRED


# --- TEST: adversarial cases and boundary cases have disjoint fingerprints ---
def test_disjoint_fingerprints_across_pools():
    all_adv = load_adversarial_cases(REPO_ROOT)
    active_adv = load_active_adversarial_cases(REPO_ROOT)
    adv_fps = {stored_fingerprint(c) for _, c in all_adv}
    bnd_active = {stored_fingerprint(c) for _, c in load_active_boundary_cases(REPO_ROOT)}
    bnd_retired = {stored_fingerprint(c) for _, c in load_retired_boundary_cases(REPO_ROOT)}
    assert adv_fps.isdisjoint(bnd_active)
    assert adv_fps.isdisjoint(bnd_retired)
    # 16 active + 1 retired = 17 unique fingerprints, none reused anywhere
    assert len({stored_fingerprint(c) for _, c in active_adv}) == EXPECTED_N_ADVERSARIAL
    assert len(adv_fps) == len(all_adv)


# --- TEST: retired adversarial case carries full retirement governance -------
def test_retired_adversarial_governance():
    retired = load_retired_adversarial_cases(REPO_ROOT)
    assert len(retired) == 1
    f, c = retired[0]
    assert c["id"] == "P7A-ADV-014"
    assert c["status"] == "retired"
    assert c["excluded_from_active_metrics"] is True
    assert c["superseded_by"] == "P7A-ADV-017"
    sh = c.get("suite_history") or []
    assert sh and sh[0]["label_flip"] is False
    assert sh[0].get("prior_case_fingerprint")
    assert sh[0].get("audit_reference")
    # the active replacement declares the supersession
    active_by_id = {c["id"]: c for _, c in load_active_adversarial_cases(REPO_ROOT)}
    assert "P7A-ADV-017" in active_by_id
    assert active_by_id["P7A-ADV-017"]["robustness"]["supersedes"] == "P7A-ADV-014"
    # retired fingerprint reproduces over its retirement-augmented content
    assert stored_fingerprint(c) == case_fingerprint(c)


# --- TEST: manifest matches the frozen pool ---------------------------------
def test_manifest_matches_pool(active):
    manifest = yaml.safe_load(
        (adversarial_dir(REPO_ROOT) / "adversarial_manifest.yaml").read_text(encoding="utf-8")
    )
    assert manifest["model_calls"] == 0
    assert manifest["holdout_touched"] is False
    assert manifest["track"] == "7A.3_adversarial"
    assert len(manifest["cases"]) == EXPECTED_N_ADVERSARIAL
    assert len(manifest["families"]) == len(ADVERSARIAL_FAMILY_IDS)

    fp_active = {c["id"]: stored_fingerprint(c) for _, c in active}
    fam_active = {c["id"]: c["robustness"]["adversarial_family_id"] for _, c in active}
    gold_active = {c["id"]: c["gold_label"] for _, c in active}
    for row in manifest["cases"]:
        assert row["status"] == "active"
        assert row["case_fingerprint"] == fp_active[row["id"]]
        assert row["family"] == fam_active[row["id"]]
        assert row["gold"] == gold_active[row["id"]]
    # retired section matches the retired pool
    retired = load_retired_adversarial_cases(REPO_ROOT)
    fp_retired = {c["id"]: stored_fingerprint(c) for _, c in retired}
    assert len(manifest.get("retired_cases", [])) == len(retired)
    for row in manifest["retired_cases"]:
        assert row["status"] == "retired"
        assert row["excluded_from_active_metrics"] is True
        assert row["case_fingerprint"] == fp_retired[row["id"]]
    assert manifest["verification"]["family_counts_match_expected"] is True
    assert manifest["verification"]["gold_counts_match_expected"] is True
    assert manifest["verification"]["n_active"] == EXPECTED_N_ADVERSARIAL
    assert manifest["verification"]["n_retired"] == len(retired)
    assert manifest["expected_counts"]["gold"] == EXPECTED_ADVERSARIAL_GOLD_COUNTS
