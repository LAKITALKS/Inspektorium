"""Phase-7A Perturbation robustness pool (7A.2) — structural validation.

Deterministic, offline, **no model scoring**. Validates the class-B perturbation track in
``tasks/study_forensics_robustness/``: the 4 neutral anchors (``P7A-NEU-*.yaml``), the deterministic
10-base selection (contract §6), and the 50 meaning-preserving variants
(``perturbation_variants.yaml``) = 10 clusters × 5 frozen families (P1–P5). Covers WP-3 §33 checks
A–V, gold inheritance, fingerprint binding, and class-A / Boundary / Adversarial isolation. **50
variants are nested in 10 independent bases — never 50 independent cases.**
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from agent_arena import run_library
from agent_arena.robustness_pool import (
    ADVERSARIAL_FAMILY_IDS,
    CLAIM_SOURCE_ROLE,
    EVIDENCE_SOURCE_ROLES,
    EXPECTED_N_NEUTRAL,
    EXPECTED_N_PERTURBATION_BASES,
    EXPECTED_N_PERTURBATION_VARIANTS,
    EXPECTED_NEUTRAL_GOLD_COUNTS,
    EXPECTED_VARIANTS_PER_BASE,
    EXPECTED_VARIANTS_PER_FAMILY,
    GOLD_LABELS,
    PERTURBATION_FAMILY_IDS,
    boundary_dir,
    case_fingerprint,
    claim_provenance_status,
    load_active_adversarial_cases,
    load_active_boundary_cases,
    load_active_neutral_cases,
    load_adversarial_cases,
    load_boundary_cases,
    load_neutral_cases,
    load_perturbation_variants,
    load_retired_adversarial_cases,
    load_retired_boundary_cases,
    select_perturbation_bases,
    stored_fingerprint,
    stored_variant_fingerprint,
    variant_fingerprint,
    verify_neutral_pool,
    verify_perturbation_pool,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

BASELINE_ACTIVE_LIBRARY = 48
BASELINE_LIBRARY_INCL_RETIRED = 50
BOUNDARY_ACTIVE, BOUNDARY_RETIRED = 14, 4
ADVERSARIAL_ACTIVE, ADVERSARIAL_RETIRED = 16, 1

REQUIRED_TOP_FIELDS = (
    "id", "prompt", "context", "gold_label", "gold_confidence", "gold_case_type",
    "gold_justification", "gold_alternative_reading", "origin", "status", "gold_status",
)
REQUIRED_NEUTRAL_ROBUSTNESS_FIELDS = (
    "robustness_case_id", "case_family", "neutral_anchor_label", "gold_status", "difficulty_tier",
    "difficulty_rationale", "precedence_rationale", "ambiguity_note", "steelman_challenge",
    "provenance", "hypothesis_map", "case_fingerprint",
)
REQUIRED_PROVENANCE_FIELDS = (
    "claim_source_title", "claim_source_url", "claim_source_publisher", "claim_source_role",
    "claim_source_type", "claim_context", "claim_exact_span",
)
REQUIRED_VARIANT_FIELDS = (
    "variant_id", "base_case_id", "base_case_fingerprint", "perturbation_family",
    "original_claim", "perturbed_claim", "gold_label", "meaning_preservation_attestation",
    "transformation_description", "forbidden_semantic_dimensions_checked", "variant_fingerprint",
    "status",
)

FORBIDDEN_RESULT_KEYS = {
    "detected_label", "label_correct", "brier", "ece", "accuracy", "run_index",
    "raw_output", "model_output", "parsed", "library_run_id", "finish_reason",
    "latency_ms", "usage", "modal_label", "label_switch_count",
}
FORBIDDEN_HOLDOUT_TERMS = ("holdout", "salt", "envelope", "identity_map", "identity map")
FORBIDDEN_CLIENT_TERMS = ("lavita",)


@pytest.fixture(scope="module")
def neutral():
    return load_active_neutral_cases(REPO_ROOT)


@pytest.fixture(scope="module")
def variants():
    return load_perturbation_variants(REPO_ROOT)


@pytest.fixture(scope="module")
def selected():
    return select_perturbation_bases(REPO_ROOT)


@pytest.fixture(scope="module")
def report():
    return verify_perturbation_pool(REPO_ROOT)


def _iter_keys(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from _iter_keys(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _iter_keys(v)


# --- §33 A: Boundary remains 14 active / 4 retired --------------------------
def test_A_boundary_counts_unchanged():
    assert len(load_active_boundary_cases(REPO_ROOT)) == BOUNDARY_ACTIVE
    assert len(load_retired_boundary_cases(REPO_ROOT)) == BOUNDARY_RETIRED


# --- §33 B: Adversarial remains 16 active / 1 retired -----------------------
def test_B_adversarial_counts_unchanged():
    assert len(load_active_adversarial_cases(REPO_ROOT)) == ADVERSARIAL_ACTIVE
    assert len(load_retired_adversarial_cases(REPO_ROOT)) == ADVERSARIAL_RETIRED


# --- §33 C: exactly 4 active neutral anchors --------------------------------
def test_C_four_active_neutral(neutral):
    assert len(neutral) == EXPECTED_N_NEUTRAL
    assert all(c["status"] == "active" for _, c in neutral)
    assert all(f.name.startswith("P7A-NEU-") for f, _ in neutral)
    assert all(c["robustness"]["case_family"] == "neutral_perturbation_anchor" for _, c in neutral)


# --- §33 D: neutral gold distribution exactly 1/1/1/1 -----------------------
def test_D_neutral_gold_distribution(neutral):
    rep = verify_neutral_pool(REPO_ROOT)
    assert rep["gold_counts"] == EXPECTED_NEUTRAL_GOLD_COUNTS
    assert rep["gold_counts_match_expected"]
    assert rep["anchor_labels_match_gold"]
    assert sum(rep["gold_counts"].values()) == EXPECTED_N_NEUTRAL


# --- neutral anchors: complete case + provenance ----------------------------
def test_neutral_case_and_provenance_complete(neutral):
    for f, c in neutral:
        for k in REQUIRED_TOP_FIELDS:
            assert c.get(k) not in (None, ""), f"{f.name} missing {k}"
        rob = c.get("robustness") or {}
        for k in REQUIRED_NEUTRAL_ROBUSTNESS_FIELDS:
            assert rob.get(k) not in (None, ""), f"{f.name} missing robustness.{k}"
        assert c["gold_label"] in GOLD_LABELS
        assert c["gold_label"] == rob["neutral_anchor_label"]
        assert c["task_family"] == c["gold_label"]
        assert c["gold_status"] == "frozen_pre_model"
        assert rob["difficulty_tier"] in {"D1", "D2", "D3"}
        st = claim_provenance_status(c)
        assert st["passes"], f"{f.name} provenance FAIL: {st['reasons']}"
        prov = rob["provenance"]
        for k in REQUIRED_PROVENANCE_FIELDS:
            assert str(prov.get(k) or "").strip(), f"{f.name} missing provenance.{k}"
        assert prov["claim_source_url"].startswith("http")
        assert prov["claim_source_role"] == CLAIM_SOURCE_ROLE
        ev = prov.get("evidence_sources") or []
        assert ev, f"{f.name} has no evidence source"
        for e in ev:
            assert e.get("source_role") in EVIDENCE_SOURCE_ROLES
            assert e.get("url") and e.get("result") and e.get("design")


# --- neutral anchors independent of every other pool (fingerprint-disjoint) --
def test_neutral_independence_fingerprints():
    neu = {stored_fingerprint(c) for _, c in load_neutral_cases(REPO_ROOT)}
    bnd = {stored_fingerprint(c) for _, c in load_boundary_cases(REPO_ROOT)}
    adv = {stored_fingerprint(c) for _, c in load_adversarial_cases(REPO_ROOT)}
    assert len(neu) == EXPECTED_N_NEUTRAL
    assert neu.isdisjoint(bnd)
    assert neu.isdisjoint(adv)
    for _, c in load_neutral_cases(REPO_ROOT):
        assert stored_fingerprint(c) == case_fingerprint(c)
        assert len(stored_fingerprint(c)) == 64


# --- §33 E: exactly 10 perturbation bases -----------------------------------
def test_E_ten_bases(selected):
    assert len(selected) == EXPECTED_N_PERTURBATION_BASES
    assert len({b["base_case_id"] for b in selected}) == EXPECTED_N_PERTURBATION_BASES


# --- §33 F: base strata exactly 4 neutral / 1 B1 / 1 B2 / 1 B3 / 3 adversarial
def test_F_base_strata(selected):
    origins = [b["origin"] for b in selected]
    assert origins.count("neutral_anchor") == 4
    assert origins.count("boundary") == 3
    assert origins.count("adversarial") == 3
    boundary_strata = sorted(b["stratum"] for b in selected if b["origin"] == "boundary")
    assert boundary_strata == ["B1", "B2", "B3"]


# --- §33 G: three adversarial bases come from distinct adversarial families --
def test_G_adversarial_distinct_families(selected):
    fams = [b["stratum"].split(":")[1] for b in selected if b["origin"] == "adversarial"]
    assert len(fams) == 3
    assert len(set(fams)) == 3
    assert all(f in ADVERSARIAL_FAMILY_IDS for f in fams)


# --- §33 H: deterministic fingerprint-order selection reproduces ------------
def test_H_selection_reproduces(selected):
    # re-run independently and compare
    again = select_perturbation_bases(REPO_ROOT)
    assert [b["base_case_id"] for b in selected] == [b["base_case_id"] for b in again]
    # boundary picks are the lexicographically smallest fingerprint in their stratum
    bnd = load_active_boundary_cases(REPO_ROOT)
    for stratum in ("B1", "B2", "B3"):
        members = sorted(stored_fingerprint(c) for _, c in bnd
                         if c["robustness"]["boundary_family_id"] == stratum)
        pick = next(b for b in selected if b["stratum"] == stratum)
        assert pick["case_fingerprint"] == members[0]
    # adversarial picks are the first distinct-family cases in fingerprint order
    adv_sorted = sorted(((stored_fingerprint(c), c["robustness"]["adversarial_family_id"])
                         for _, c in load_active_adversarial_cases(REPO_ROOT)))
    expected, seen = [], set()
    for fp, fam in adv_sorted:
        if fam not in seen:
            seen.add(fam)
            expected.append(fp)
        if len(expected) == 3:
            break
    got = [b["case_fingerprint"] for b in selected if b["origin"] == "adversarial"]
    assert got == expected


# --- §33 I: exactly 5 perturbation families ---------------------------------
def test_I_five_families(report):
    assert report["n_families"] == 5
    assert set(report["variants_per_family"]) == set(PERTURBATION_FAMILY_IDS)


# --- §33 J: exactly 50 active variants --------------------------------------
def test_J_fifty_active_variants(variants, report):
    active = [v for v in variants if v.get("status") == "active"]
    assert len(active) == EXPECTED_N_PERTURBATION_VARIANTS
    assert report["n_variants"] == EXPECTED_N_PERTURBATION_VARIANTS
    for v in active:
        for k in REQUIRED_VARIANT_FIELDS:
            assert v.get(k) not in (None, ""), f"{v.get('variant_id')} missing {k}"
        assert v["gold_status"] == "frozen_pre_model"


# --- §33 K: exactly 5 variants per base -------------------------------------
def test_K_five_variants_per_base(report):
    assert report["variants_per_base_all_5"]
    assert all(n == EXPECTED_VARIANTS_PER_BASE for n in report["variants_per_base"].values())
    assert len(report["variants_per_base"]) == EXPECTED_N_PERTURBATION_BASES


# --- §33 L: exactly 10 variants per family -----------------------------------
def test_L_ten_variants_per_family(report):
    assert report["variants_per_family_all_10"]
    for fam in PERTURBATION_FAMILY_IDS:
        assert report["variants_per_family"][fam] == EXPECTED_VARIANTS_PER_FAMILY


# --- §33 M: variant IDs unique + namespaced ---------------------------------
def test_M_variant_ids_unique(variants, report):
    ids = [v["variant_id"] for v in variants]
    assert report["unique_variant_ids"]
    assert len(set(ids)) == len(ids) == EXPECTED_N_PERTURBATION_VARIANTS
    assert all(i.startswith("P7A-PRT-") for i in ids)
    # cluster membership resolvable from the id (slot -> base)
    slot_by_base = {b["base_case_id"]: b["slot"] for b in select_perturbation_bases(REPO_ROOT)}
    for v in variants:
        assert v["variant_id"] == f"P7A-PRT-{slot_by_base[v['base_case_id']]:02d}-{v['perturbation_family']}"


# --- §33 N: variant fingerprints unique + reproducible ----------------------
def test_N_variant_fingerprints(variants, report):
    assert report["unique_variant_fingerprints"]
    assert report["variant_fingerprints_reproduce"]
    for v in variants:
        assert stored_variant_fingerprint(v) == variant_fingerprint(v)
        assert len(stored_variant_fingerprint(v)) == 64
        assert stored_variant_fingerprint(v) != "PENDING"


# --- §32: variant fingerprint BINDS base fp + family + perturbed claim + attestation
def test_variant_fingerprint_binds_contract(variants):
    v = deepcopy(variants[0])
    base_fp = variant_fingerprint(v)
    for mutate in (
        lambda x: x.__setitem__("perturbed_claim", x["perturbed_claim"] + " X"),
        lambda x: x.__setitem__("perturbation_family", "P9"),
        lambda x: x.__setitem__("base_case_fingerprint", "0" * 64),
        lambda x: x["meaning_preservation_attestation"].__setitem__("status", "FAIL"),
    ):
        m = deepcopy(v)
        mutate(m)
        assert variant_fingerprint(m) != base_fp


# --- §33 O: every variant resolves to a real base ---------------------------
def test_O_variants_resolve_to_base(report):
    assert report["all_resolve_to_base"]
    assert report["bases_match_selection"]


# --- §33 P: every variant gold equals base gold -----------------------------
def test_P_gold_inheritance(variants, report):
    assert report["all_gold_inherited"]
    assert report["all_base_fingerprints_match"]
    base_gold = {}
    for _, c in (load_neutral_cases(REPO_ROOT) + load_boundary_cases(REPO_ROOT)
                 + load_adversarial_cases(REPO_ROOT)):
        base_gold[c["id"]] = (c["gold_label"], stored_fingerprint(c))
    for v in variants:
        g, fp = base_gold[v["base_case_id"]]
        assert v["gold_label"] == g, f"{v['variant_id']} gold != base gold"
        assert v["base_case_fingerprint"] == fp


# --- §33 Q: every variant meaning-preservation status = PASS ----------------
def test_Q_meaning_preservation_pass(variants, report):
    assert report["all_meaning_preserved"]
    for v in variants:
        att = v["meaning_preservation_attestation"]
        assert att["status"] == "PASS", f"{v['variant_id']} not PASS"
        assert att.get("proposition_unchanged") is True
        assert len(str(att.get("rationale") or "").strip()) > 40
        assert v["counterfactual_gold_change"] is False
        dims = v["forbidden_semantic_dimensions_checked"]
        assert all(val == "preserved" for val in dims.values())


# --- original_claim is the verbatim base prompt -----------------------------
def test_original_claim_matches_base_prompt(variants):
    by_id = {c["id"]: c for _, c in (load_neutral_cases(REPO_ROOT)
             + load_boundary_cases(REPO_ROOT) + load_adversarial_cases(REPO_ROOT))}
    for v in variants:
        base = by_id[v["base_case_id"]]
        assert v["original_claim"].rstrip("\n") == base["prompt"].rstrip("\n")
        assert v["perturbed_claim"].strip() != v["original_claim"].strip()


# --- §33 R: independent-base count reported as 10, not 50 -------------------
def test_R_cluster_count_not_inflated(report):
    assert report["n_independent_bases"] == EXPECTED_N_PERTURBATION_BASES
    assert report["n_clusters"] == EXPECTED_N_PERTURBATION_BASES
    assert report["n_variants"] == EXPECTED_N_PERTURBATION_VARIANTS
    manifest = yaml.safe_load(
        (boundary_dir(REPO_ROOT) / "perturbation_manifest.yaml").read_text(encoding="utf-8")
    )
    cl = manifest["clustering"]
    assert cl["n_independent_perturbation_bases"] == 10
    assert cl["n_perturbation_variants"] == 50
    assert cl["variants_are_independent_cases"] is False


# --- §33 S: normal Class-A discovery unchanged ------------------------------
def test_S_class_a_discovery_unchanged():
    task_dir = REPO_ROOT / "tasks" / "study_forensics"
    active = run_library.discover_cases(task_dir=task_dir)
    incl = run_library.discover_cases(task_dir=task_dir, include_retired=True)
    assert len(active) == BASELINE_ACTIVE_LIBRARY
    assert len(incl) == BASELINE_LIBRARY_INCL_RETIRED
    assert run_library.TASK_DIR == Path("tasks/study_forensics")
    # neither neutral anchors nor variants leak into class-A discovery
    class_a_ids = {t.id for _, t in run_library.discover_cases(task_dir=task_dir, include_retired=True)}
    neu_ids = {c["id"] for _, c in load_neutral_cases(REPO_ROOT)}
    var_ids = {v["variant_id"] for v in load_perturbation_variants(REPO_ROOT)}
    assert class_a_ids.isdisjoint(neu_ids)
    assert class_a_ids.isdisjoint(var_ids)


# --- §33 T: Phase-7B fixture contribution = 0 -------------------------------
def test_T_no_phase7b_fixture(neutral, variants):
    for _, c in neutral:
        assert c["id"].startswith("P7A-NEU-")
        assert not any(c["id"].startswith(f"R{n}") for n in range(1, 9))
    for v in variants:
        assert v["variant_id"].startswith("P7A-PRT-")


# --- §33 U: no holdout / client / LaVita content ----------------------------
def test_U_no_holdout_or_client_material(neutral, variants):
    blobs = [yaml.safe_dump(c, allow_unicode=True) for _, c in load_neutral_cases(REPO_ROOT)]
    blobs.append(yaml.safe_dump(load_perturbation_variants(REPO_ROOT), allow_unicode=True))
    for text in blobs:
        low = text.lower()
        for term in FORBIDDEN_HOLDOUT_TERMS:
            assert term not in low, f"holdout term '{term}' present"
        for term in FORBIDDEN_CLIENT_TERMS:
            assert term not in low, f"client term '{term}' present"


# --- §33 V: no evaluation-model result artifacts ----------------------------
def test_V_no_model_result_artifacts(neutral, variants):
    for _, c in load_neutral_cases(REPO_ROOT):
        leaked = set(_iter_keys(c)) & FORBIDDEN_RESULT_KEYS
        assert not leaked, f"{c['id']} result-like keys: {leaked}"
    for v in variants:
        leaked = set(_iter_keys(v)) & FORBIDDEN_RESULT_KEYS
        assert not leaked, f"{v['variant_id']} result-like keys: {leaked}"
    for pat in ("P7A-NEU-*.json", "P7A-PRT-*.json"):
        for p in boundary_dir(REPO_ROOT).glob(pat):
            raise AssertionError(f"unexpected json artifact: {p.name}")
    # manifest + variants declare 0 model calls
    manifest = yaml.safe_load(
        (boundary_dir(REPO_ROOT) / "perturbation_manifest.yaml").read_text(encoding="utf-8")
    )
    vdoc = yaml.safe_load(
        (boundary_dir(REPO_ROOT) / "perturbation_variants.yaml").read_text(encoding="utf-8")
    )
    assert manifest["model_calls"] == 0 and manifest["holdout_touched"] is False
    assert vdoc["model_calls"] == 0 and vdoc["holdout_touched"] is False


# --- manifest matches the frozen pool ---------------------------------------
def test_manifest_matches_pool(selected, variants):
    manifest = yaml.safe_load(
        (boundary_dir(REPO_ROOT) / "perturbation_manifest.yaml").read_text(encoding="utf-8")
    )
    assert manifest["track"] == "7A.2_perturbation"
    assert len(manifest["five_perturbation_families"]) == 5
    assert len(manifest["base_selection"]) == EXPECTED_N_PERTURBATION_BASES
    assert len(manifest["neutral_anchors"]) == EXPECTED_N_NEUTRAL
    sel_by_id = {b["base_case_id"]: b for b in selected}
    total_variants = 0
    for row in manifest["base_selection"]:
        b = sel_by_id[row["base_case_id"]]
        assert row["base_case_fingerprint"] == b["case_fingerprint"]
        assert row["base_gold"] == b["gold"]
        assert row["stratum"] == b["stratum"]
        assert len(row["variants"]) == EXPECTED_VARIANTS_PER_BASE
        for vr in row["variants"]:
            assert vr["meaning_preservation"] == "PASS"
            total_variants += 1
    assert total_variants == EXPECTED_N_PERTURBATION_VARIANTS
    assert manifest["verification"]["all_gold_inherited"]
    assert manifest["verification"]["all_meaning_preserved"]
    assert manifest["verification"]["bases_match_selection"]
