"""Tests for the Phase 6.2 runtime-contract tooling and the three frozen contracts.

Offline, deterministic, no model calls, no private material.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from agent_arena import runtime_contract as rc

FREEZE_DIR = Path("analysis/phase6_2_runtime_freeze")
CONTRACT_FILES = {
    "haiku": FREEZE_DIR / "phase6_2_runtime_contract_haiku.json",
    "sonnet": FREEZE_DIR / "phase6_2_runtime_contract_sonnet.json",
    "opus": FREEZE_DIR / "phase6_2_runtime_contract_opus.json",
}


def _load(key):
    return json.loads(CONTRACT_FILES[key].read_text())


def _all_committed():
    return [_load(k) for k in CONTRACT_FILES]


# ------------------- committed contracts are valid -------------------

@pytest.mark.parametrize("key", list(CONTRACT_FILES))
def test_committed_contract_validates(key):
    assert rc.validate_contract(_load(key)) == []


def test_committed_matches_generator():
    for key in CONTRACT_FILES:
        assert _load(key) == rc.build_contract(key)


# ------------------- no alias / exact dated snapshots -------------------

@pytest.mark.parametrize("key", list(CONTRACT_FILES))
def test_exact_model_id_is_dated_snapshot(key):
    c = _load(key)
    mid = c["exact_model_id"]
    assert rc._DATED_MODEL_RE.match(mid)
    assert mid[-8:].isdigit() and mid.count("-") >= 4
    # the referenced agent config carries the same exact dated id (no override)
    assert c["agent_config_model"] == mid


@pytest.mark.parametrize("key", list(CONTRACT_FILES))
def test_config_on_disk_carries_dated_snapshot(key):
    c = _load(key)
    on_disk = rc.agent_config_model(c["agent_config_path"])
    assert on_disk == c["exact_model_id"]
    assert rc._DATED_MODEL_RE.match(on_disk)  # not a moving alias


def test_contract_config_model_mismatch_rejected():
    c = _load("sonnet")
    c["agent_config_model"] = "claude-sonnet-4-5-20250101"  # different dated id
    assert any("mismatch" in e for e in rc.validate_contract(c))


def test_moving_alias_rejected():
    c = _load("opus")
    c["agent_config_model"] = "claude-opus-4-5"  # moving alias
    errs = rc.validate_contract(c)
    assert any("moving alias" in e for e in errs)


def test_provider_timeout_enforcement_mismatch_rejected():
    c = _load("haiku")
    c["request_timeout_seconds"] = 600  # SDK default, not the enforced 120
    assert any("request_timeout_seconds" in e for e in rc.validate_contract(c))


def test_provider_retry_enforcement_mismatch_rejected():
    c = _load("haiku")
    c["max_transport_retries_after_initial_request"] = 5
    assert any("max_transport_retries" in e for e in rc.validate_contract(c))


def test_no_alias_remains_across_contracts():
    for c in _all_committed():
        assert rc._DATED_MODEL_RE.match(c["exact_model_id"]), c["exact_model_id"]


def test_three_distinct_models_per_model_mode():
    ids = {c["exact_model_id"] for c in _all_committed()}
    assert ids == {"claude-haiku-4-5-20251001", "claude-sonnet-4-5-20250929",
                   "claude-opus-4-5-20251101"}
    for c in _all_committed():
        assert c["calibration_mode"] == "THREE_MODEL_PER_MODEL_CALIBRATION"


# ------------------- all non-model values identical -------------------

def test_non_model_values_identical():
    assert rc.assert_non_model_values_identical(_all_committed()) == []


# ------------------- hashes reproduce; one-char change invalidates -------------------

def test_prompt_and_config_hashes_reproduce():
    c = _load("haiku")
    assert c["system_prompt_sha256"] == rc.system_prompt_sha256()
    assert c["task_packet_construction_sha256"] == rc.task_packet_construction_sha256()
    assert c["parser_contract_sha256"] == rc.parser_contract_sha256()
    assert c["agent_config_sha256"] == rc.agent_config_sha256(c["agent_config_path"])


def test_one_character_prompt_change_changes_hash():
    from agent_arena.runner import STUDY_FORENSICS_PROMPT
    base = hashlib.sha256(STUDY_FORENSICS_PROMPT.encode()).hexdigest()
    changed = hashlib.sha256((STUDY_FORENSICS_PROMPT + "x").encode()).hexdigest()
    assert base != changed
    assert base == rc.system_prompt_sha256()


def test_config_change_changes_config_hash(tmp_path):
    f = tmp_path / "cfg.yaml"
    f.write_text("model: x\n")
    h1 = hashlib.sha256(f.read_bytes()).hexdigest()
    f.write_text("model: x\n\n")  # one-byte change
    h2 = hashlib.sha256(f.read_bytes()).hexdigest()
    assert h1 != h2


def test_tampered_hash_fails_validation():
    c = _load("haiku")
    c["system_prompt_sha256"] = "0" * 64
    assert any("system_prompt_sha256" in e for e in rc.validate_contract(c))


# ------------------- rejects missing / ambiguous / placeholder -------------------

def test_missing_field_rejected():
    c = _load("sonnet")
    del c["request_timeout_seconds"]
    assert any("request_timeout_seconds" in e for e in rc.validate_contract(c))


def test_placeholder_rejected_and_not_executable():
    c = _load("opus")
    c["endpoint"] = "TODO"
    errs = rc.validate_contract(c)
    assert any("placeholder" in e for e in errs)
    assert rc.is_executable(c) is False


def test_explicit_markers_are_not_placeholders():
    # UNSUPPORTED / OMITTED_FROM_REQUEST / PROHIBITED must pass
    assert rc.validate_contract(_load("haiku")) == []


# ------------------- unsupported params require explicit markers -------------------

def test_top_p_must_be_omitted_marker():
    c = _load("haiku")
    c["top_p"] = 1.0
    assert any("top_p" in e for e in rc.validate_contract(c))


def test_seed_must_be_unsupported_marker():
    c = _load("haiku")
    c["seed"] = None
    assert any("seed" in e for e in rc.validate_contract(c))


# ------------------- semantic retries forbidden; replication frozen -------------------

def test_semantic_retries_prohibited():
    c = _load("sonnet")
    c["semantic_or_quality_retries"] = "allowed"
    assert any("semantic_or_quality_retries" in e for e in rc.validate_contract(c))


def test_replication_count_exactly_one():
    c = _load("opus")
    c["replication_count"] = 2
    assert any("replication_count" in e for e in rc.validate_contract(c))


# ------------------- executable gate -------------------

def test_executable_only_when_clean():
    assert rc.is_executable(_load("haiku")) is True
    bad = _load("haiku")
    bad["max_output_tokens"] = 4096
    bad["retry_backoff"] = ""   # placeholder
    assert rc.is_executable(bad) is False


def test_deterministic_build():
    assert rc.build_contract("opus") == rc.build_contract("opus")
