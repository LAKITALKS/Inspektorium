"""Synthetic error-path tests for the explicitly invoked local historical verifier.

The real ignored ASA inputs are intentionally absent from these tests and from the default suite.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from agent_arena import local_historical_verification as hv


def _historical_paths(root: Path) -> tuple[Path, Path]:
    case_root = root / hv.CASE_ROOT
    case_root.mkdir(parents=True)
    return case_root / hv.FORENSIC_RECORD_FILE, case_root / hv.STORED_RELEASE_REPORT_FILE


def test_local_historical_verifier_requires_explicit_subcommand():
    with pytest.raises(SystemExit) as exc:
        hv.main([])
    assert exc.value.code != 0


def test_local_historical_verifier_missing_input_is_explicit_non_success(tmp_path, capsys):
    exit_code = hv.main(["verify-asa-phase7b", "--repo-root", str(tmp_path)])
    result = json.loads(capsys.readouterr().out)

    assert exit_code != 0
    assert result["verification_type"] == "LOCAL_HISTORICAL_VERIFICATION"
    assert result["suite_scope"] == "NOT_PART_OF_TRACKED_ONLY_FULL_SUITE"
    assert result["artifact_role"] == "NOT_AN_OFFICIAL_RELEASE"
    assert result["status"] == "HISTORICAL_INPUT_UNAVAILABLE"
    assert result["success"] is False
    assert result["official_release_write_count"] == 0


def test_local_historical_verifier_hash_mismatch_is_non_success(tmp_path, capsys):
    record, stored = _historical_paths(tmp_path)
    record.write_text("{}\n")
    stored.write_text("{}\n")

    exit_code = hv.main(["verify-asa-phase7b", "--repo-root", str(tmp_path)])
    result = json.loads(capsys.readouterr().out)

    assert exit_code != 0
    assert result["status"] == "HISTORICAL_INPUT_HASH_MISMATCH"
    assert result["success"] is False
    assert result["official_release_write_count"] == 0


def test_local_historical_verifier_malformed_hash_bound_input_is_non_success(
    tmp_path, monkeypatch, capsys
):
    record, stored = _historical_paths(tmp_path)
    record_bytes = b"{}\n"
    stored_bytes = b"{}\n"
    record.write_bytes(record_bytes)
    stored.write_bytes(stored_bytes)
    monkeypatch.setattr(
        hv, "EXPECTED_FORENSIC_RECORD_SHA256", hashlib.sha256(record_bytes).hexdigest()
    )
    monkeypatch.setattr(
        hv, "EXPECTED_STORED_REPORT_SHA256", hashlib.sha256(stored_bytes).hexdigest()
    )

    exit_code = hv.main(["verify-asa-phase7b", "--repo-root", str(tmp_path)])
    result = json.loads(capsys.readouterr().out)

    assert exit_code != 0
    assert result["status"] == "HISTORICAL_VERIFICATION_FAILED"
    assert result["success"] is False
    assert result["official_release_write_count"] == 0
    assert not (tmp_path / hv.OFFICIAL_RELEASE_NAMESPACE).exists()
