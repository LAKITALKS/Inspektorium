"""Tests for Phase 6.1 private development-manifest tooling (salted commitment).

Uses SYNTHETIC placeholder ids only (study-forensics-9xx) — never real canonical
cases. Verifies schema/aggregate validation, salted-commitment determinism and
membership-hiding, and that the public projection carries no case identities or salt.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from agent_arena.dev_manifest import (
    COMMITMENT_ALGORITHM,
    FROZEN_AGGREGATE,
    PENDING_SENTINEL,
    assert_public_clean,
    commitment,
    generate_salt,
    public_projection,
    validate_manifest,
    validate_public_manifest_state,
    verify_commitment,
    verify_public_against_private,
)

PUBLIC_MANIFEST = Path("analysis/phase6_1_confidence_protocol/development_pool_public_manifest.json")

SALT_A = b"\x00" * 32
SALT_B = b"\x11" * 32


def _synthetic_manifest() -> dict:
    """A schema-valid manifest with fake ids (8 solid / 15 overclaim / 2 corr / 2 mech)."""
    plan = [("solid", 8), ("overclaim", 15),
            ("correlation_vs_causation", 2), ("mechanism_vs_evidence", 2)]
    cases = []
    n = 0
    for label, count in plan:
        for _ in range(count):
            n += 1
            cases.append({
                "dev_id": f"DEV-{n:03d}",
                "canonical_id": f"study-forensics-{900 + n}",
                "gold_label": label,
                "gold_case_type": "clear",
                "stratum": "clear",
            })
    cases[0]["stratum"] = "development_only"
    cases[1]["stratum"] = "borderline"
    cases[1]["gold_case_type"] = "borderline"
    return {
        "schema_version": "6.1.0",
        "manifest_id": "AA-DEVPOOL-6100",
        "exclusion_rule_id": "active_and_not_holdout_eligible",
        "aggregate": dict(FROZEN_AGGREGATE),
        "cases": cases,
    }


# --------------------------- validation ---------------------------

def test_synthetic_manifest_validates():
    assert validate_manifest(_synthetic_manifest()) == []


def test_wrong_total_rejected():
    m = _synthetic_manifest()
    m["cases"] = m["cases"][:-1]
    assert any("27" in e for e in validate_manifest(m))


def test_label_count_mismatch_rejected():
    m = _synthetic_manifest()
    m["cases"][-1]["gold_label"] = "solid"
    assert any("label count mismatch" in e for e in validate_manifest(m))


def test_duplicate_dev_id_rejected():
    m = _synthetic_manifest()
    m["cases"][1]["dev_id"] = m["cases"][0]["dev_id"]
    assert any("duplicate" in e for e in validate_manifest(m))


def test_wrong_aggregate_rejected():
    m = _synthetic_manifest()
    m["aggregate"] = {**FROZEN_AGGREGATE, "total": 26}
    assert any("aggregate" in e for e in validate_manifest(m))


def test_validation_errors_are_id_free():
    m = _synthetic_manifest()
    m["cases"][0]["canonical_id"] = "study-forensics-913"  # duplicate of case index 13
    for e in validate_manifest(m):
        assert "study-forensics" not in e


# --------------------------- salted commitment ---------------------------

def test_commitment_deterministic_for_same_manifest_and_salt():
    m = _synthetic_manifest()
    assert commitment(m, SALT_A) == commitment(m, SALT_A)


def test_commitment_order_independent():
    m = _synthetic_manifest()
    reordered = dict(reversed(list(m.items())))
    assert commitment(reordered, SALT_A) == commitment(m, SALT_A)


def test_different_salt_changes_commitment():
    m = _synthetic_manifest()
    assert commitment(m, SALT_A) != commitment(m, SALT_B)


def test_manifest_change_changes_commitment():
    m = _synthetic_manifest()
    c0 = commitment(m, SALT_A)
    m["manifest_id"] = "AA-DEVPOOL-6101"
    assert commitment(m, SALT_A) != c0


def test_verify_commitment_detects_manifest_or_salt_change():
    m = _synthetic_manifest()
    c = commitment(m, SALT_A)
    assert verify_commitment(m, SALT_A, c)
    assert not verify_commitment(m, SALT_B, c)          # salt changed
    m2 = _synthetic_manifest()
    m2["cases"][0]["gold_case_type"] = "clear"
    m2["cases"][0]["stratum"] = "clear"                 # manifest changed
    assert not verify_commitment(m2, SALT_A, c)


def test_generate_salt_is_random_and_min_length():
    s1, s2 = generate_salt(), generate_salt()
    assert len(s1) >= 32 and len(s2) >= 32
    assert s1 != s2


# --------------------------- public projection / leakage ---------------------------

def test_public_projection_has_no_identities_or_salt():
    pub = public_projection(_synthetic_manifest())
    assert "cases" not in pub
    assert "salt" not in pub and "salt_hex" not in pub
    assert pub["commitment"] == PENDING_SENTINEL
    assert pub["commitment_algorithm"] == COMMITMENT_ALGORITHM
    assert assert_public_clean(pub) == []


def test_assert_public_clean_detects_leaks():
    pub = public_projection(_synthetic_manifest())
    pub["oops"] = "study-forensics-913"
    assert any("canonical id leaked" in e for e in assert_public_clean(pub))
    pub2 = public_projection(_synthetic_manifest())
    pub2["salt"] = "deadbeef"
    assert any("salt" in e for e in assert_public_clean(pub2))
    pub3 = public_projection(_synthetic_manifest())
    pub3["cases"] = []
    assert any("cases" in e for e in assert_public_clean(pub3))


def test_verify_public_against_private_pending_matched_and_wrong():
    priv = _synthetic_manifest()
    pub_pending = public_projection(priv)
    assert any("PENDING" in e for e in verify_public_against_private(pub_pending, priv, SALT_A))
    c = commitment(priv, SALT_A)
    pub_ok = public_projection(priv, commitment_value=c)
    assert verify_public_against_private(pub_ok, priv, SALT_A) == []
    # right commitment value but wrong salt supplied to verification
    assert any("does not match" in e for e in verify_public_against_private(pub_ok, priv, SALT_B))


def test_committed_public_manifest_is_clean_and_wellformed():
    # Valid in BOTH states: pre-provisioning (commitment == sentinel) and after the
    # curator provisioning gate is closed (commitment == salted-sha256 hex digest).
    # The public side must never carry the salt or any identity in either state.
    data = json.loads(PUBLIC_MANIFEST.read_text())
    assert data["aggregate"] == FROZEN_AGGREGATE
    assert data["commitment_algorithm"] == COMMITMENT_ALGORITHM
    cv = data["commitment"]
    assert cv == PENDING_SENTINEL or re.fullmatch(r"[0-9a-f]{64}", cv)
    assert assert_public_clean(data) == []
    # enforce ONLY the valid paired states (PENDING↔pending, 64-hex↔provisioned)
    assert validate_public_manifest_state(data) == []


def test_validate_public_manifest_state_pairing():
    # valid pairs
    assert validate_public_manifest_state(
        {"commitment": PENDING_SENTINEL, "status": "aggregate_frozen; identity_pending_provisioning"}) == []
    assert validate_public_manifest_state(
        {"commitment": "a" * 64, "status": "aggregate_frozen; identity_provisioned"}) == []
    # mismatched pairs
    assert validate_public_manifest_state(
        {"commitment": PENDING_SENTINEL, "status": "aggregate_frozen; identity_provisioned"}) != []
    assert validate_public_manifest_state(
        {"commitment": "a" * 64, "status": "aggregate_frozen; identity_pending_provisioning"}) != []
    # malformed commitment
    assert validate_public_manifest_state({"commitment": "not-hex", "status": "provisioned"}) != []
