"""Phase-7A robustness pool (class B) — read-only loader, fingerprint, and structural checks.

This module supports the **Phase-7A robustness pools** (data class B) that live in
``tasks/study_forensics_robustness/``: the **Boundary** pool (7A.1, ``P7A-BND-*.yaml``) and the
**Adversarial** pool (7A.3, ``P7A-ADV-*.yaml``). The two share the class-B directory, the canonical
SHA-256 fingerprint, and the provenance/source-role vocabulary, but keep **distinct ID namespaces**
and distinct verify helpers (``verify_pool`` / ``verify_adversarial_pool``). It is deliberately
**minimal and read-only**:

* it does **not** touch ``run_library.discover_cases`` or the normal Case-Library glob
  (``tasks/study_forensics/*.yaml``), so class-A discovery / counts are unaffected;
* it performs **no** model calls and holds **no** model outputs;
* it only loads the frozen YAML records, computes the canonical case fingerprint (reusing the
  existing ``runtime_contract._sha256_hex`` SHA-256 primitive), and reports deterministic
  structural counts for validation.

The pool distinguishes **active** cases (``status: active``) from **retired** historical cases
(``status: retired`` + ``excluded_from_active_metrics: true``). Only the active set counts toward
the frozen 14 / 5-5-4 / 8-2-2-2 distributions; retired cases are kept for provenance/history and
are excluded from the active metrics (repair re-freeze, ``docs/case_intake_policy.md`` §Retirement).

Every **active** case must carry resolved *real public-claim provenance* (a real, identifiable
claim source + URL + a bounded exact quote) and declared source **roles** on both the claim and its
evidence (``analysis/phase7a_boundary/boundary_curator_gold_audit.md`` and the repair WP).

See ``analysis/phase7a_startup/phase7a_case_and_perturbation_contract.md`` (the frozen design)
and ``analysis/phase7a_boundary/`` (candidate log, source-intake log, curator review).
"""

from __future__ import annotations

import json
from collections import Counter
from copy import deepcopy
from pathlib import Path

import yaml

from .runtime_contract import _sha256_hex

# --- Class-B location (structurally separate from the class-A library) ------
ROBUSTNESS_DIR = Path("tasks/study_forensics_robustness")
BOUNDARY_GLOB = "P7A-BND-*.yaml"
# Phase-7A adversarial pool (7A.3) lives in the SAME class-B directory but a distinct ID namespace.
ADVERSARIAL_GLOB = "P7A-ADV-*.yaml"

# The four frozen analytical gold labels (metadata families are NOT gold labels).
GOLD_LABELS = ("solid", "overclaim", "correlation_vs_causation", "mechanism_vs_evidence")

# Frozen, pre-result expected counts (case/perturbation contract §3). These are the **active**
# counts after the repair re-freeze; retired historical cases do not count.
EXPECTED_N_CASES = 14
EXPECTED_FAMILY_COUNTS = {"B1": 5, "B2": 5, "B3": 4}
EXPECTED_GOLD_COUNTS = {
    "overclaim": 8,
    "correlation_vs_causation": 2,
    "mechanism_vs_evidence": 2,
    "solid": 2,
}

# --- Frozen adversarial (7A.3) pre-result expected counts -------------------
# 8 frozen adversarial families (A1-A8, robustness_design.md/case_and_perturbation_contract.md §4)
# x 2 independent cases = 16 active adversarial bases. Unlike Boundary, the gold distribution is NOT
# a cosmetic 4-label balance: it EMERGES from the frozen family gold-logic (case_and_perturbation
# contract §4) and is frozen here before any model output.
ADVERSARIAL_FAMILY_IDS = ("A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8")
EXPECTED_N_ADVERSARIAL = 16
EXPECTED_ADVERSARIAL_FAMILY_COUNTS = {fid: 2 for fid in ADVERSARIAL_FAMILY_IDS}
# Emergent frozen distribution: A1/A4/A5/A6/A8 -> overclaim (10); A3 -> correlation (2);
# A2/A7 -> mechanism_vs_evidence (4); solid (0). See adversarial_manifest.yaml.
EXPECTED_ADVERSARIAL_GOLD_COUNTS = {
    "overclaim": 10,
    "correlation_vs_causation": 2,
    "mechanism_vs_evidence": 4,
    "solid": 0,
}

# --- Frozen neutral perturbation anchors (7A.2, contract §5) ----------------
# Four dedicated perturbation base cases (P7A-NEU-*), one per frozen gold label. These are
# independent bases (counted in the 34) and are auto-included as perturbation base clusters. They are
# NOT selected from Boundary/Adversarial performance.
NEUTRAL_GLOB = "P7A-NEU-*.yaml"
EXPECTED_N_NEUTRAL = 4
# Exactly one neutral anchor per frozen gold label (contract §5).
EXPECTED_NEUTRAL_GOLD_COUNTS = {lbl: 1 for lbl in GOLD_LABELS}

# --- Frozen perturbation variants (7A.2, contract §6/§7) --------------------
# 10 base clusters x 5 families (P1-P5) x 1 variant = 50 meaning-preserving variants. Variants are
# NOT independent cases; each inherits its base gold and nests under base_case_id. Stored as compact
# records in ``perturbation_variants.yaml`` (normalized references to the base evidence package, not
# 50 duplicated evidence packets — contract §17).
PERTURBATION_VARIANTS_FILE = "perturbation_variants.yaml"
PERTURBATION_FAMILY_IDS = ("P1", "P2", "P3", "P4", "P5")
PERTURBATION_FAMILY_NAMES = {
    "P1": "claim paraphrase",
    "P2": "hedging variation (neutral)",
    "P3": "order (claim/evidence context)",
    "P4": "distractor context",
    "P5": "formatting",
}
EXPECTED_N_PERTURBATION_BASES = 10
EXPECTED_N_PERTURBATION_VARIANTS = 50
EXPECTED_VARIANTS_PER_BASE = 5
EXPECTED_VARIANTS_PER_FAMILY = 10
# Frozen strata quotas for the 6 deterministically selected bases (contract §6 step 2).
PERTURBATION_BASE_STRATA_QUOTAS = {"B1": 1, "B2": 1, "B3": 1, "adversarial": 3}
# The field that holds the variant fingerprint itself — excluded from the hashed variant content.
_VARIANT_FINGERPRINT_KEY = "variant_fingerprint"

# --- Controlled source-role vocabulary (repair WP §6/§24) -------------------
# Source ROLE (function in the case) is NOT source QUALITY. The claim side is a
# ``public_claim_source``; each evidence item declares one of the evidence roles. A single source
# may be BOTH the public claim and evidence when that is genuinely the forensic object (§7).
CLAIM_SOURCE_ROLE = "public_claim_source"
EVIDENCE_SOURCE_ROLES = (
    "primary_research",
    "systematic_review",            # systematic review / meta-analysis
    "regulatory_assessment",        # regulatory / government / authoritative assessment or enforcement
    "trial_registration",
    "secondary_discovery",          # secondary/discovery source (news synthesis, provenance record)
    "other",
)
SOURCE_ROLES = (CLAIM_SOURCE_ROLE, *EVIDENCE_SOURCE_ROLES)

# Deterministic organisation → expected evidence-role guard (§24). Known non-primary bodies must
# not be mislabeled as primary research. Matched case-insensitively against evidence citations.
NON_PRIMARY_EVIDENCE_ORGS = {
    "cochrane": "systematic_review",
    "efsa": "regulatory_assessment",
    "european food safety authority": "regulatory_assessment",
    "uspstf": "regulatory_assessment",
    "preventive services task force": "regulatory_assessment",
    "iarc": "regulatory_assessment",
    "international agency for research on cancer": "regulatory_assessment",
    "ftc": "regulatory_assessment",
    "federal trade commission": "regulatory_assessment",
    "food and drug administration": "regulatory_assessment",
}

# The field that holds the fingerprint itself — excluded from the hashed content.
_FINGERPRINT_KEY = "case_fingerprint"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def boundary_dir(repo_root: str | Path | None = None) -> Path:
    root = Path(repo_root).resolve() if repo_root else _repo_root()
    return root / ROBUSTNESS_DIR


def load_boundary_cases(repo_root: str | Path | None = None) -> list[tuple[Path, dict]]:
    """Load every ``P7A-BND-*.yaml`` boundary record (active + retired) as a raw dict, by filename."""
    d = boundary_dir(repo_root)
    out: list[tuple[Path, dict]] = []
    for f in sorted(d.glob(BOUNDARY_GLOB)):
        out.append((f, yaml.safe_load(f.read_text(encoding="utf-8"))))
    return out


def is_active(case: dict) -> bool:
    """A case is active iff ``status == active`` and it is not excluded from active metrics."""
    return case.get("status") == "active" and not case.get("excluded_from_active_metrics", False)


def load_active_boundary_cases(repo_root: str | Path | None = None) -> list[tuple[Path, dict]]:
    """The frozen **active** Boundary pool (status: active) — the 14 that count toward metrics."""
    return [(f, c) for f, c in load_boundary_cases(repo_root) if is_active(c)]


def load_retired_boundary_cases(repo_root: str | Path | None = None) -> list[tuple[Path, dict]]:
    """Retired historical Boundary cases — kept for provenance/history, excluded from metrics."""
    return [(f, c) for f, c in load_boundary_cases(repo_root) if not is_active(c)]


# --- Adversarial (7A.3) loaders — additive, do NOT touch the Boundary path ---
def adversarial_dir(repo_root: str | Path | None = None) -> Path:
    """The adversarial pool shares the class-B directory; only the ID namespace/glob differs."""
    return boundary_dir(repo_root)


def load_adversarial_cases(repo_root: str | Path | None = None) -> list[tuple[Path, dict]]:
    """Load every ``P7A-ADV-*.yaml`` adversarial record as a raw dict, by filename."""
    d = adversarial_dir(repo_root)
    out: list[tuple[Path, dict]] = []
    for f in sorted(d.glob(ADVERSARIAL_GLOB)):
        out.append((f, yaml.safe_load(f.read_text(encoding="utf-8"))))
    return out


def load_active_adversarial_cases(repo_root: str | Path | None = None) -> list[tuple[Path, dict]]:
    """The frozen **active** adversarial pool (status: active) — the 16 that count toward metrics."""
    return [(f, c) for f, c in load_adversarial_cases(repo_root) if is_active(c)]


def load_retired_adversarial_cases(repo_root: str | Path | None = None) -> list[tuple[Path, dict]]:
    """Retired historical adversarial cases — kept for provenance/history, excluded from metrics."""
    return [(f, c) for f, c in load_adversarial_cases(repo_root) if not is_active(c)]


def canonical_material(case: dict) -> str:
    """Deterministic canonical serialization of the frozen analytical contract.

    Binds the entire frozen case record **except** the stored fingerprint itself, so any change
    to release-relevant analytical content (prompt, context, gold label/justification/alternative,
    precedence, family, difficulty, provenance/evidence, …) changes the fingerprint. Uses
    sorted-key, non-ASCII-preserving compact JSON so the hash is stable and reproducible.
    """
    c = deepcopy(case)
    rob = c.get("robustness")
    if isinstance(rob, dict):
        rob.pop(_FINGERPRINT_KEY, None)
    return json.dumps(c, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def case_fingerprint(case: dict) -> str:
    """SHA-256 (hex) over the canonical material contract — reuses runtime_contract._sha256_hex."""
    return _sha256_hex(canonical_material(case).encode("utf-8"))


def stored_fingerprint(case: dict) -> str | None:
    rob = case.get("robustness") or {}
    return rob.get(_FINGERPRINT_KEY)


def claim_provenance_status(case: dict) -> dict:
    """Structural (not semantic) completeness of a case's real public-claim provenance (§23).

    Verifies presence of: a real claim source identifier/URL, a bounded exact public claim quote,
    a declared claim source role, and a declared evidence source role on every evidence item.
    Scientific source *fidelity* remains curator-reviewed; this only checks structural completeness.
    """
    prov = (case.get("robustness") or {}).get("provenance") or {}
    reasons: list[str] = []

    if not str(prov.get("claim_source_url") or "").strip():
        reasons.append("missing claim_source_url")
    if not str(prov.get("claim_exact_span") or "").strip():
        reasons.append("missing claim_exact_span")
    role = prov.get("claim_source_role")
    if role not in SOURCE_ROLES:
        reasons.append(f"claim_source_role not in controlled vocabulary: {role!r}")

    ev = prov.get("evidence_sources") or []
    if not ev:
        reasons.append("no evidence_sources")
    for i, e in enumerate(ev):
        er = e.get("source_role")
        if er not in EVIDENCE_SOURCE_ROLES:
            reasons.append(f"evidence_sources[{i}].source_role not in controlled vocabulary: {er!r}")
        cite = str(e.get("citation") or "").lower()
        for org, expected in NON_PRIMARY_EVIDENCE_ORGS.items():
            if org in cite and er == "primary_research":
                reasons.append(
                    f"evidence_sources[{i}] cites '{org}' but is labeled primary_research "
                    f"(expected {expected})"
                )
    return {"passes": not reasons, "reasons": reasons}


def verify_pool(repo_root: str | Path | None = None) -> dict:
    """Return a deterministic structural report over the **active** boundary pool (no model calls).

    Counts are computed over active cases only; retired historical cases are reported separately and
    excluded from the active metrics.
    """
    all_cases = load_boundary_cases(repo_root)
    active = [(f, c) for f, c in all_cases if is_active(c)]
    retired = [(f, c) for f, c in all_cases if not is_active(c)]

    families = Counter(c["robustness"]["boundary_family_id"] for _, c in active)
    golds = Counter(c["gold_label"] for _, c in active)
    difficulties = Counter(c["robustness"]["difficulty_tier"] for _, c in active)
    ids = [c["id"] for _, c in active]
    fps = {c["id"]: stored_fingerprint(c) for _, c in active}
    fp_ok = {c["id"]: (stored_fingerprint(c) == case_fingerprint(c)) for _, c in all_cases}
    prov_ok = {c["id"]: claim_provenance_status(c)["passes"] for _, c in active}

    # global fingerprint uniqueness spans active + retired (no reuse anywhere)
    all_fps = [stored_fingerprint(c) for _, c in all_cases]

    return {
        "n_cases": len(active),
        "n_active": len(active),
        "n_retired": len(retired),
        "ids": ids,
        "active_ids": ids,
        "retired_ids": [c["id"] for _, c in retired],
        "unique_ids": len(set(ids)) == len(ids),
        "family_counts": dict(families),
        "gold_counts": dict(golds),
        "difficulty_counts": dict(difficulties),
        "fingerprints": fps,
        "unique_fingerprints": len(set(fps.values())) == len(fps) and None not in fps.values()
        and "PENDING" not in fps.values(),
        "unique_fingerprints_incl_retired": len(set(all_fps)) == len(all_fps)
        and None not in all_fps and "PENDING" not in all_fps,
        "fingerprints_reproduce": all(fp_ok.values()),
        "all_frozen_pre_model": all(c.get("gold_status") == "frozen_pre_model" for _, c in active),
        "claim_provenance": prov_ok,
        "claim_provenance_all_pass": all(prov_ok.values()),
    }


def verify_adversarial_pool(repo_root: str | Path | None = None) -> dict:
    """Deterministic structural report over the **active** adversarial pool (no model calls).

    Mirrors :func:`verify_pool` but keys on ``adversarial_family_id`` (A1-A8). The gold distribution
    is reported as-observed and compared to the frozen emergent distribution
    (``EXPECTED_ADVERSARIAL_GOLD_COUNTS``); it is not an imposed cosmetic balance.
    """
    all_cases = load_adversarial_cases(repo_root)
    active = [(f, c) for f, c in all_cases if is_active(c)]
    retired = [(f, c) for f, c in all_cases if not is_active(c)]

    families = Counter(c["robustness"]["adversarial_family_id"] for _, c in active)
    golds = Counter(c["gold_label"] for _, c in active)
    difficulties = Counter(c["robustness"]["difficulty_tier"] for _, c in active)
    ids = [c["id"] for _, c in active]
    fps = {c["id"]: stored_fingerprint(c) for _, c in active}
    fp_ok = {c["id"]: (stored_fingerprint(c) == case_fingerprint(c)) for _, c in all_cases}
    prov_ok = {c["id"]: claim_provenance_status(c)["passes"] for _, c in active}
    all_fps = [stored_fingerprint(c) for _, c in all_cases]

    return {
        "n_cases": len(active),
        "n_active": len(active),
        "n_retired": len(retired),
        "ids": ids,
        "active_ids": ids,
        "retired_ids": [c["id"] for _, c in retired],
        "unique_ids": len(set(ids)) == len(ids),
        "family_counts": dict(families),
        "family_counts_match_expected": dict(families) == EXPECTED_ADVERSARIAL_FAMILY_COUNTS,
        "gold_counts": dict(golds),
        "difficulty_counts": dict(difficulties),
        "fingerprints": fps,
        "unique_fingerprints": len(set(fps.values())) == len(fps) and None not in fps.values()
        and "PENDING" not in fps.values(),
        "unique_fingerprints_incl_retired": len(set(all_fps)) == len(all_fps)
        and None not in all_fps and "PENDING" not in all_fps,
        "fingerprints_reproduce": all(fp_ok.values()),
        "all_frozen_pre_model": all(c.get("gold_status") == "frozen_pre_model" for _, c in active),
        "claim_provenance": prov_ok,
        "claim_provenance_all_pass": all(prov_ok.values()),
    }


# --- Neutral perturbation anchors (7A.2) — additive, read-only --------------
def load_neutral_cases(repo_root: str | Path | None = None) -> list[tuple[Path, dict]]:
    """Load every ``P7A-NEU-*.yaml`` neutral perturbation-anchor record as a raw dict, by filename."""
    d = boundary_dir(repo_root)
    out: list[tuple[Path, dict]] = []
    for f in sorted(d.glob(NEUTRAL_GLOB)):
        out.append((f, yaml.safe_load(f.read_text(encoding="utf-8"))))
    return out


def load_active_neutral_cases(repo_root: str | Path | None = None) -> list[tuple[Path, dict]]:
    """The frozen **active** neutral anchors (status: active) — the 4 that count toward metrics."""
    return [(f, c) for f, c in load_neutral_cases(repo_root) if is_active(c)]


def verify_neutral_pool(repo_root: str | Path | None = None) -> dict:
    """Deterministic structural report over the **active** neutral anchor pool (no model calls)."""
    all_cases = load_neutral_cases(repo_root)
    active = [(f, c) for f, c in all_cases if is_active(c)]
    golds = Counter(c["gold_label"] for _, c in active)
    anchor_labels = Counter(c["robustness"]["neutral_anchor_label"] for _, c in active)
    ids = [c["id"] for _, c in active]
    fps = {c["id"]: stored_fingerprint(c) for _, c in active}
    fp_ok = {c["id"]: (stored_fingerprint(c) == case_fingerprint(c)) for _, c in all_cases}
    prov_ok = {c["id"]: claim_provenance_status(c)["passes"] for _, c in active}
    return {
        "n_active": len(active),
        "ids": ids,
        "unique_ids": len(set(ids)) == len(ids),
        "gold_counts": dict(golds),
        "gold_counts_match_expected": dict(golds) == EXPECTED_NEUTRAL_GOLD_COUNTS,
        "anchor_label_counts": dict(anchor_labels),
        "anchor_labels_match_gold": all(
            c["robustness"]["neutral_anchor_label"] == c["gold_label"] for _, c in active
        ),
        "fingerprints": fps,
        "unique_fingerprints": len(set(fps.values())) == len(fps) and None not in fps.values()
        and "PENDING" not in fps.values(),
        "fingerprints_reproduce": all(fp_ok.values()),
        "all_frozen_pre_model": all(c.get("gold_status") == "frozen_pre_model" for _, c in active),
        "claim_provenance_all_pass": all(prov_ok.values()),
    }


# --- Deterministic pre-result base selection (contract §6) ------------------
def select_perturbation_bases(repo_root: str | Path | None = None) -> list[dict]:
    """Reproduce the frozen, model-performance-free selection of the 10 perturbation base clusters.

    Contract §6: (1) the 4 neutral anchors are auto-included, one per frozen gold label; (2) six
    additional bases are selected from the frozen eligible pool (14 Boundary + 16 Adversarial) using
    stratified, ascending-``case_fingerprint`` (lexicographic sha256 hex) ordering with the frozen
    strata quotas B1=1, B2=1, B3=1, Adversarial=3 (three **distinct** adversarial families). Returns a
    slot-ordered list of dicts proving each pick is the one implied by the frozen fingerprints.
    """
    bases: list[dict] = []

    # (1) Four neutral anchors — auto-included, one per frozen gold label (fixed label order).
    neutral_by_label = {
        c["robustness"]["neutral_anchor_label"]: c for _, c in load_active_neutral_cases(repo_root)
    }
    for lbl in GOLD_LABELS:
        c = neutral_by_label[lbl]
        bases.append({
            "slot": len(bases) + 1,
            "base_case_id": c["id"],
            "origin": "neutral_anchor",
            "stratum": f"neutral:{lbl}",
            "gold": c["gold_label"],
            "case_fingerprint": stored_fingerprint(c),
            "selection_rule": f"neutral anchor for '{lbl}' (auto-included per contract §6 step 1)",
        })

    # (2a) Boundary strata B1/B2/B3 — lowest case_fingerprint in each stratum.
    bnd = load_active_boundary_cases(repo_root)
    for stratum in ("B1", "B2", "B3"):
        members = sorted(
            ((stored_fingerprint(c), c) for _, c in bnd
             if c["robustness"]["boundary_family_id"] == stratum),
            key=lambda t: t[0],
        )
        fp, c = members[0]
        bases.append({
            "slot": len(bases) + 1,
            "base_case_id": c["id"],
            "origin": "boundary",
            "stratum": stratum,
            "gold": c["gold_label"],
            "case_fingerprint": fp,
            "selection_rule": (
                f"rank 1 of {len(members)} by ascending case_fingerprint in stratum {stratum}"
            ),
        })

    # (2b) Adversarial — first fingerprint-ordered cases producing 3 distinct families.
    adv_sorted = sorted(
        ((stored_fingerprint(c), c) for _, c in load_active_adversarial_cases(repo_root)),
        key=lambda t: t[0],
    )
    chosen_families: set[str] = set()
    n_picked = 0
    for fp, c in adv_sorted:
        fam = c["robustness"]["adversarial_family_id"]
        if fam in chosen_families:
            continue
        chosen_families.add(fam)
        n_picked += 1
        bases.append({
            "slot": len(bases) + 1,
            "base_case_id": c["id"],
            "origin": "adversarial",
            "stratum": f"adversarial:{fam}",
            "gold": c["gold_label"],
            "case_fingerprint": fp,
            "selection_rule": (
                f"distinct-family pick #{n_picked}: first fingerprint-ordered case of new family {fam}"
            ),
        })
        if n_picked == PERTURBATION_BASE_STRATA_QUOTAS["adversarial"]:
            break
    return bases


# --- Perturbation variants (7A.2) — fingerprint + loader + verify -----------
def variant_canonical_material(variant: dict) -> str:
    """Deterministic canonical serialization of a variant record (excludes the stored fingerprint).

    Binds the whole variant record — including ``base_case_fingerprint``, ``perturbation_family``,
    ``perturbed_claim``, and the ``meaning_preservation_attestation`` — so any change to those changes
    the fingerprint (contract §32). Reuses the same sorted-key compact-JSON convention as
    :func:`canonical_material`.
    """
    v = deepcopy(variant)
    v.pop(_VARIANT_FINGERPRINT_KEY, None)
    return json.dumps(v, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def variant_fingerprint(variant: dict) -> str:
    """SHA-256 (hex) over the canonical variant material — reuses runtime_contract._sha256_hex."""
    return _sha256_hex(variant_canonical_material(variant).encode("utf-8"))


def stored_variant_fingerprint(variant: dict) -> str | None:
    return variant.get(_VARIANT_FINGERPRINT_KEY)


def load_perturbation_variants(repo_root: str | Path | None = None) -> list[dict]:
    """Load the 50 frozen perturbation variant records from ``perturbation_variants.yaml``."""
    d = boundary_dir(repo_root)
    doc = yaml.safe_load((d / PERTURBATION_VARIANTS_FILE).read_text(encoding="utf-8"))
    return list(doc.get("variants") or [])


def _resolve_base_case(base_case_id: str, repo_root: str | Path | None = None) -> dict | None:
    """Resolve a variant's base_case_id to its frozen case record (neutral/boundary/adversarial)."""
    for _, c in (
        load_neutral_cases(repo_root)
        + load_boundary_cases(repo_root)
        + load_adversarial_cases(repo_root)
    ):
        if c["id"] == base_case_id:
            return c
    return None


def verify_perturbation_pool(repo_root: str | Path | None = None) -> dict:
    """Deterministic structural report over the 50 perturbation variants (no model calls).

    Verifies cluster structure (10 bases x 5 families), gold inheritance (variant gold == base gold),
    meaning-preservation PASS on every variant, base-fingerprint resolution, and variant-fingerprint
    uniqueness/reproduction. Reports the pseudoreplication-guard counts (contract §24/§25): 50 variants
    nested in 10 independent bases — never 50 independent cases.
    """
    variants = load_perturbation_variants(repo_root)
    active = [v for v in variants if v.get("status") == "active"]
    selected = select_perturbation_bases(repo_root)
    selected_ids = [b["base_case_id"] for b in selected]
    base_fp_by_id = {b["base_case_id"]: b["case_fingerprint"] for b in selected}

    per_base = Counter(v["base_case_id"] for v in active)
    per_family = Counter(v["perturbation_family"] for v in active)
    ids = [v["variant_id"] for v in active]
    vfps = [stored_variant_fingerprint(v) for v in active]

    gold_ok, base_fp_ok, meaning_ok, family_ok, resolves_ok, vfp_reproduce = {}, {}, {}, {}, {}, {}
    for v in active:
        vid = v["variant_id"]
        base = _resolve_base_case(v["base_case_id"], repo_root)
        resolves_ok[vid] = base is not None
        gold_ok[vid] = base is not None and v["gold_label"] == base["gold_label"]
        base_fp_ok[vid] = (
            base is not None
            and v.get("base_case_fingerprint") == stored_fingerprint(base)
            and v.get("base_case_fingerprint") == base_fp_by_id.get(v["base_case_id"])
        )
        meaning_ok[vid] = (
            (v.get("meaning_preservation_attestation") or {}).get("status") == "PASS"
            and v.get("counterfactual_gold_change") is False
        )
        family_ok[vid] = v.get("perturbation_family") in PERTURBATION_FAMILY_IDS
        vfp_reproduce[vid] = stored_variant_fingerprint(v) == variant_fingerprint(v)

    return {
        "n_variants": len(active),
        "n_independent_bases": len(set(v["base_case_id"] for v in active)),
        "n_clusters": len(per_base),
        "n_families": len(per_family),
        "selected_base_ids": selected_ids,
        "variants_per_base": dict(per_base),
        "variants_per_family": dict(per_family),
        "variants_per_base_all_5": all(n == EXPECTED_VARIANTS_PER_BASE for n in per_base.values())
        and len(per_base) == EXPECTED_N_PERTURBATION_BASES,
        "variants_per_family_all_10": all(
            per_family.get(f, 0) == EXPECTED_VARIANTS_PER_FAMILY for f in PERTURBATION_FAMILY_IDS
        ) and set(per_family) == set(PERTURBATION_FAMILY_IDS),
        "bases_match_selection": set(per_base) == set(selected_ids),
        "unique_variant_ids": len(set(ids)) == len(ids),
        "unique_variant_fingerprints": len(set(vfps)) == len(vfps)
        and None not in vfps and "PENDING" not in vfps,
        "variant_fingerprints_reproduce": all(vfp_reproduce.values()),
        "all_resolve_to_base": all(resolves_ok.values()),
        "all_gold_inherited": all(gold_ok.values()),
        "all_base_fingerprints_match": all(base_fp_ok.values()),
        "all_meaning_preserved": all(meaning_ok.values()),
        "all_family_valid": all(family_ok.values()),
        "all_frozen_pre_model": all(v.get("gold_status") == "frozen_pre_model" for v in active),
    }


if __name__ == "__main__":  # pragma: no cover - manual inspection helper
    import pprint

    print("=== Boundary (7A.1) ===")
    pprint.pprint(verify_pool())
    print("=== Adversarial (7A.3) ===")
    pprint.pprint(verify_adversarial_pool())
    print("=== Neutral anchors (7A.2) ===")
    pprint.pprint(verify_neutral_pool())
    print("=== Deterministic base selection (7A.2 §6) ===")
    for b in select_perturbation_bases():
        print(f"  slot {b['slot']:>2} | {b['base_case_id']} | {b['origin']:<15} | "
              f"{b['stratum']:<22} | gold={b['gold']:<24} | {b['case_fingerprint'][:12]} | {b['selection_rule']}")
    print("=== Perturbation variants (7A.2) ===")
    pprint.pprint(verify_perturbation_pool())
