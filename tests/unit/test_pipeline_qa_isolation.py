"""Phase 7B — pipeline-QA fixture isolation (Test H, enforceable invariant).

Governance: LaVita / pipeline-QA fixtures are data class C. They must never enter
the case library, development pool, or any evaluation / benchmark / holdout count.
Isolation here is STRUCTURAL, not by naming convention:

  * case discovery globs ``tasks/study_forensics/*.yaml`` for STUDY_FORENSICS Tasks;
  * pipeline-QA fixtures are ``*.json`` ForensicRecords under
    ``tests/fixtures/pipeline_qa/`` — a different directory, a different extension,
    and a different schema (not a Task).

Any one of those three facts already prevents ingestion; the tests assert all three.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from inspektorium.audit.schemas import Task

ROOT = Path(__file__).resolve().parents[2]
CASE_DIR = ROOT / "tests" / "fixtures" / "audit" / "case_library"
QA_DIR = ROOT / "tests" / "fixtures" / "audit" / "pipeline_qa"


def test_qa_fixtures_exist_and_are_json_only():
    fixtures = list(QA_DIR.glob("*.json"))
    assert fixtures, "expected at least one pipeline-QA fixture"
    # No YAML case can live in the QA dir (the case-discovery glob only matches *.yaml).
    assert list(QA_DIR.glob("*.yaml")) == []
    assert list(QA_DIR.glob("*.yml")) == []


def test_qa_fixtures_live_outside_tasks_tree():
    tasks_root = CASE_DIR.resolve()
    for fx in QA_DIR.glob("*.json"):
        assert tasks_root not in fx.resolve().parents


def test_qa_fixture_is_not_a_loadable_case():
    import json

    for fx in QA_DIR.glob("*.json"):
        data = json.loads(fx.read_text())
        # A ForensicRecord lacks the required Task fields, so it cannot be a case.
        with pytest.raises(Exception):
            Task(**data)
        assert "task_type" not in data
        assert data.get("gold_label") is None
