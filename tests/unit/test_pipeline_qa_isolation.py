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

from inspektorium.audit.execution.run_library import discover_cases
from inspektorium.audit.schemas import Task, TaskType

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


def test_case_discovery_never_yields_a_qa_fixture():
    discovered = discover_cases(task_dir=CASE_DIR)
    qa_dir = QA_DIR.resolve()
    for path, _task in discovered:
        assert path.suffix == ".yaml"
        assert path.resolve().parent != qa_dir
        assert qa_dir not in path.resolve().parents


def test_qa_dir_contributes_zero_cases_to_enumeration():
    # Pointing case discovery straight at the QA dir yields nothing: no *.yaml there.
    assert discover_cases(task_dir=QA_DIR) == []
    # And the active case count equals the study_forensics yaml set — QA adds nothing.
    active = discover_cases(task_dir=CASE_DIR)
    assert len(active) >= 1  # sanity: the real library is present
    assert all(p.parent.name == "case_library" for p, _ in active)


def test_qa_fixture_is_not_a_loadable_case():
    import json
    for fx in QA_DIR.glob("*.json"):
        data = json.loads(fx.read_text())
        # A ForensicRecord lacks the required Task fields, so it cannot be a case.
        with pytest.raises(Exception):
            Task(**data)
        assert "task_type" not in data
        assert data.get("gold_label") is None


def test_discovered_cases_are_study_forensics_tasks():
    for _path, task in discover_cases(task_dir=CASE_DIR):
        assert task.task_type == TaskType.STUDY_FORENSICS


def test_value_origin_fixture_contributes_zero_cases():
    # Slice-2 fixture must be present and provably outside case discovery.
    fx = QA_DIR / "qa_modelled_value_origin.json"
    assert fx.exists()
    discovered_names = {p.name for p, _ in discover_cases(task_dir=CASE_DIR)}
    assert fx.name not in discovered_names
    # every pipeline-QA fixture (all slices) is a *.json outside the tasks tree
    assert len(list(QA_DIR.glob("*.json"))) >= 2
    assert discover_cases(task_dir=QA_DIR) == []


def test_search_scope_fixture_contributes_zero_cases():
    # Slice-3 fixture must be present and provably outside case discovery.
    fx = QA_DIR / "qa_search_scope_negative_language.json"
    assert fx.exists()
    discovered_names = {p.name for p, _ in discover_cases(task_dir=CASE_DIR)}
    assert fx.name not in discovered_names
    assert len(list(QA_DIR.glob("*.json"))) >= 3
    assert discover_cases(task_dir=QA_DIR) == []


def test_release_gate_fixture_contributes_zero_cases():
    # Consolidated release-gate fixture must be present and provably outside case discovery.
    fx = QA_DIR / "qa_release_gate_consolidated.json"
    assert fx.exists()
    discovered_names = {p.name for p, _ in discover_cases(task_dir=CASE_DIR)}
    assert fx.name not in discovered_names
    assert len(list(QA_DIR.glob("*.json"))) >= 4
    assert discover_cases(task_dir=QA_DIR) == []
