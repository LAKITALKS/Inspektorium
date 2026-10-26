"""Tests for the Phase 6.1 provisioning workflow (SYNTHETIC fixtures only).

Verifies deterministic derivation (active minus eligible, retired excluded), frozen
aggregate enforcement, salted public commitment, the narrow approved-path guards
(private output root outside repo; public path == the one approved tracked path),
and that no canonical / eligible / dev id or salt ever reaches stdout, stderr, return
values, exception messages, or the public artifact.
"""

from __future__ import annotations

import json

import pytest

from agent_arena.dev_manifest import (
    FROZEN_AGGREGATE,
    PENDING_SENTINEL,
    assert_public_clean,
    validate_manifest,
    verify_public_against_private,
)
from agent_arena.provision_dev_manifest import (
    APPROVED_PUBLIC_MANIFEST_RELPATH,
    CaseRec,
    ProvisioningError,
    derive_development_pool,
    run_provisioning,
)

SALT = b"\x00" * 32


def _synthetic_library():
    """50 synthetic records: 27 dev + 21 eligible (active) + 2 retired.

    Per-label active split matches reality (solid 13 / overclaim 23 / corr 6 / mech 6)
    so that active-minus-eligible yields the frozen 8/15/2/2 = 27.
    """
    recs = []
    cid = 900
    eligible = []

    def add(label, gct, retired):
        nonlocal cid
        cid += 1
        recs.append(CaseRec(f"study-forensics-{cid}", label, gct, retired))
        return f"study-forensics-{cid}"

    for _ in range(5):
        eligible.append(add("solid", "clear", False))
    for _ in range(8):
        eligible.append(add("overclaim", "clear", False))
    for _ in range(4):
        eligible.append(add("correlation_vs_causation", "clear", False))
    for _ in range(4):
        eligible.append(add("mechanism_vs_evidence", "clear", False))
    for _ in range(8):
        add("solid", "clear", False)
    for _ in range(15):
        add("overclaim", "clear", False)
    for _ in range(2):
        add("correlation_vs_causation", "clear", False)
    for _ in range(2):
        add("mechanism_vs_evidence", "clear", False)
    add("solid", "clear", True)
    add("overclaim", "borderline", True)
    return recs, eligible


def _setup(tmp_path):
    """A synthetic repo root + an external private output root (sibling of the repo)."""
    repo = tmp_path / "repo"
    (repo / "analysis" / "phase6_1_confidence_protocol").mkdir(parents=True)
    private_root = tmp_path / "private_store"
    private_root.mkdir()
    approved_public = repo / APPROVED_PUBLIC_MANIFEST_RELPATH
    return repo, private_root, approved_public


# --------------------------- derivation ---------------------------

def test_derive_pool_matches_frozen_aggregate():
    recs, eligible = _synthetic_library()
    cases = derive_development_pool(recs, eligible)
    assert len(cases) == 27
    counts = {}
    for c in cases:
        counts[c["gold_label"]] = counts.get(c["gold_label"], 0) + 1
    assert counts == {"solid": 8, "overclaim": 15,
                      "correlation_vs_causation": 2, "mechanism_vs_evidence": 2}


def test_retired_and_eligible_excluded():
    recs, eligible = _synthetic_library()
    cases = derive_development_pool(recs, eligible)
    canon = {c["canonical_id"] for c in cases}
    assert canon.isdisjoint(set(eligible))
    retired = {r.canonical_id for r in recs if r.is_retired}
    assert canon.isdisjoint(retired)


def test_wrong_eligible_count_raises_id_free():
    recs, eligible = _synthetic_library()
    with pytest.raises(ProvisioningError) as exc:
        derive_development_pool(recs, eligible[:-1])
    assert "study-forensics" not in str(exc.value)


def test_development_only_stratum_assignment():
    recs, eligible = _synthetic_library()
    dev_only = [r.canonical_id for r in recs
                if r.canonical_id not in eligible and not r.is_retired][:1]
    cases = derive_development_pool(recs, eligible, development_only_ids=dev_only)
    assert sum(1 for c in cases if c["stratum"] == "development_only") == 1


# --------------------------- successful provisioning ---------------------------

def test_run_provisioning_writes_valid_private_and_clean_public(tmp_path):
    recs, eligible = _synthetic_library()
    repo, priv_root, pub = _setup(tmp_path)
    summary = run_provisioning(recs, eligible, priv_root, pub, salt=SALT, repo_root=repo)

    assert summary.aggregate == FROZEN_AGGREGATE
    assert summary.commitment != PENDING_SENTINEL

    private = json.loads((priv_root / "private_manifest.json").read_text())
    assert validate_manifest(private) == []
    assert (priv_root / "salt.hex").read_text() == SALT.hex()

    public = json.loads(pub.read_text())
    assert assert_public_clean(public) == []
    assert verify_public_against_private(public, private, SALT) == []


def test_approved_external_private_root_accepted(tmp_path):
    recs, eligible = _synthetic_library()
    repo, priv_root, pub = _setup(tmp_path)
    # Should not raise; writes into the external approved root.
    run_provisioning(recs, eligible, priv_root, pub, salt=SALT, repo_root=repo)
    assert (priv_root / "private_manifest.json").exists()


# --------------------------- private-root path guard ---------------------------

def test_relative_private_root_rejected(tmp_path):
    recs, eligible = _synthetic_library()
    repo, _priv, pub = _setup(tmp_path)
    with pytest.raises(ProvisioningError) as exc:
        run_provisioning(recs, eligible, "relative/private", pub, salt=SALT, repo_root=repo)
    assert "absolute" in str(exc.value)


def test_private_root_inside_repository_rejected(tmp_path):
    recs, eligible = _synthetic_library()
    repo, _priv, pub = _setup(tmp_path)
    inside = repo / "inside_private"
    inside.mkdir()
    with pytest.raises(ProvisioningError) as exc:
        run_provisioning(recs, eligible, inside, pub, salt=SALT, repo_root=repo)
    assert "outside the repository" in str(exc.value)


def test_unapproved_external_root_rejected_ancestor(tmp_path):
    recs, eligible = _synthetic_library()
    repo, _priv, pub = _setup(tmp_path)
    with pytest.raises(ProvisioningError) as exc:
        run_provisioning(recs, eligible, tmp_path, pub, salt=SALT, repo_root=repo)  # ancestor of repo
    assert "ancestor" in str(exc.value)


def test_nonexistent_private_root_rejected(tmp_path):
    recs, eligible = _synthetic_library()
    repo, _priv, pub = _setup(tmp_path)
    missing = tmp_path / "does_not_exist"
    with pytest.raises(ProvisioningError) as exc:
        run_provisioning(recs, eligible, missing, pub, salt=SALT, repo_root=repo)
    assert "existing" in str(exc.value)


# --------------------------- public-path guard ---------------------------

def test_wrong_public_path_rejected(tmp_path):
    recs, eligible = _synthetic_library()
    repo, priv_root, _pub = _setup(tmp_path)
    wrong = repo / "analysis" / "phase6_1_confidence_protocol" / "not_the_manifest.json"
    with pytest.raises(ProvisioningError) as exc:
        run_provisioning(recs, eligible, priv_root, wrong, salt=SALT, repo_root=repo)
    assert "approved tracked public-manifest path" in str(exc.value)


def test_public_path_outside_repository_rejected(tmp_path):
    recs, eligible = _synthetic_library()
    repo, priv_root, _pub = _setup(tmp_path)
    outside = tmp_path / "public_out.json"
    with pytest.raises(ProvisioningError) as exc:
        run_provisioning(recs, eligible, priv_root, outside, salt=SALT, repo_root=repo)
    assert "approved tracked public-manifest path" in str(exc.value)


# --------------------------- identity / salt safety ---------------------------

def test_error_messages_are_id_free_inside_run(tmp_path):
    recs, eligible = _synthetic_library()
    repo, priv_root, pub = _setup(tmp_path)
    with pytest.raises(ProvisioningError) as exc:
        run_provisioning(recs, eligible[:-1], priv_root, pub, salt=SALT, repo_root=repo)
    assert "study-forensics" not in str(exc.value)


def test_no_id_or_salt_output_on_success(capsys, tmp_path):
    recs, eligible = _synthetic_library()
    repo, priv_root, pub = _setup(tmp_path)
    summary = run_provisioning(recs, eligible, priv_root, pub, salt=SALT, repo_root=repo)
    out = capsys.readouterr()
    # nothing printed to stdout/stderr, and certainly no ids or salt
    for stream in (out.out, out.err):
        assert "study-forensics" not in stream
        assert SALT.hex() not in stream
    # id-free, salt-free summary and public artifact
    blob = json.dumps(summary.as_dict()) + pub.read_text()
    assert "study-forensics" not in blob
    assert SALT.hex() not in blob


def test_existing_provisioning_validation_intact(tmp_path):
    """The frozen aggregate is still enforced end-to-end through run_provisioning."""
    recs, eligible = _synthetic_library()
    repo, priv_root, pub = _setup(tmp_path)
    # drop one eligible so the derived pool becomes 28 -> aggregate check must fail
    with pytest.raises(ProvisioningError):
        run_provisioning(recs, eligible[:-1], priv_root, pub, salt=SALT, repo_root=repo)
    # and a correct run still succeeds
    run_provisioning(recs, eligible, priv_root, pub, salt=SALT, repo_root=repo)
    assert json.loads(pub.read_text())["aggregate"] == FROZEN_AGGREGATE
