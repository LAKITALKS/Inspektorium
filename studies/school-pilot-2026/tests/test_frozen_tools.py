"""The tools under test stay frozen until the held-out cases are evaluated.

The held-out file can be rebuilt from public inputs, so its secrecy protects
nothing. These two fixed hashes protect the test instead.
"""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pytest

FROZEN_SRC_TREE = "0afbc0115f904d6408b1b8196af4e019678d3c56"
FROZEN_CHECKER_BLOB = "2a3368683da37db01ae6487dc75cf552c6bfa9e0"


def git_blob_id(content: bytes) -> str:
    """Compute the id Git gives a file with this content."""

    header = f"blob {len(content)}\0".encode()
    return hashlib.sha1(header + content, usedforsecurity=False).hexdigest()


def test_the_blob_id_matches_git_for_a_known_value() -> None:
    assert git_blob_id(b"") == "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"


def test_a_changed_byte_changes_the_blob_id(study_root: Path) -> None:
    content = (study_root / "scripts/check_quotes.py").read_bytes()
    assert git_blob_id(content + b"\n") != FROZEN_CHECKER_BLOB


def test_the_quote_checker_is_frozen(study_root: Path) -> None:
    content = (study_root / "scripts/check_quotes.py").read_bytes()
    assert git_blob_id(content) == FROZEN_CHECKER_BLOB


def test_the_source_tree_is_frozen(study_root: Path) -> None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD:src"],
        cwd=study_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        pytest.skip("not a Git checkout")
    assert result.stdout.strip() == FROZEN_SRC_TREE
