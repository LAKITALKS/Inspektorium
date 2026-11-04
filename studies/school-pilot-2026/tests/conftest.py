"""Make the study scripts importable and locate the optional corpus."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

STUDY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STUDY_ROOT / "scripts"))


@pytest.fixture(scope="session")
def study_root() -> Path:
    return STUDY_ROOT


@pytest.fixture(scope="session")
def annotations_dir(study_root: Path) -> Path:
    """The unpacked corpus. It is not committed, so these tests can skip."""

    path = study_root / "data" / "external" / "genius" / "annotations"
    if not path.is_dir():
        pytest.skip("corpus not fetched; run scripts/fetch_genius.py")
    return path
