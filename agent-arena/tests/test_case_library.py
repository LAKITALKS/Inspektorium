"""Phase 3 case-library validation tests.

Validates the curated study_forensics case library as a whole: total count,
unique filenames and internal IDs, no case-number collisions, schema
conformance of the Phase-3 additions (case043-063), representation of every
major pattern group, and that the library documentation covers all new cases.

No live API keys required — pure file/parse validation.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from agent_arena.task_loader import load_task

TASK_DIR = Path("tasks/study_forensics")
DOC = Path("STUDY_FORENSICS_CASE_LIBRARY_V0_1.md")

EXPECTED_TOTAL = 50
NEW_CASE_NUMBERS = list(range(43, 64))  # 043..063 inclusive (21 cases)
VALID_LABELS = {"solid", "overclaim", "mechanism_vs_evidence", "correlation_vs_causation"}

# Major pattern groups mapped to their case-number ranges (Phase 3).
PATTERN_GROUPS = {
    "biomedical": range(43, 53),          # 043-052
    "market_communication": range(53, 58),  # 053-057
    "ai_technology": range(58, 62),        # 058-061
    "environment_policy": range(62, 64),   # 062-063
}


def _all_yaml():
    return sorted(TASK_DIR.glob("*.yaml"))


def _case_number(path: Path) -> int | None:
    m = re.match(r"case(\d+)_", path.name)
    return int(m.group(1)) if m else None


# ---------------------------------------------------------------------------
# Library-wide invariants
# ---------------------------------------------------------------------------

class TestLibraryInvariants:
    def test_total_count(self):
        assert len(_all_yaml()) == EXPECTED_TOTAL

    def test_filenames_unique(self):
        names = [p.name for p in _all_yaml()]
        assert len(names) == len(set(names))

    def test_case_numbers_unique(self):
        nums = [n for p in _all_yaml() if (n := _case_number(p)) is not None]
        assert len(nums) == len(set(nums)), "duplicate case numbers"

    def test_internal_ids_unique(self):
        ids = [load_task(p).id for p in _all_yaml()]
        assert len(ids) == len(set(ids)), "duplicate internal IDs"

    def test_all_parse(self):
        for p in _all_yaml():
            load_task(p)  # must not raise

    def test_every_label_represented(self):
        labels = {load_task(p).gold_label for p in _all_yaml()}
        assert VALID_LABELS.issubset(labels), f"missing labels: {VALID_LABELS - labels}"


# ---------------------------------------------------------------------------
# Phase 3 additions (case043-063)
# ---------------------------------------------------------------------------

class TestNewCases:
    def _new_files(self):
        return [p for p in _all_yaml() if _case_number(p) in NEW_CASE_NUMBERS]

    def test_all_new_cases_present(self):
        present = {_case_number(p) for p in self._new_files()}
        assert set(NEW_CASE_NUMBERS) == present, f"missing: {set(NEW_CASE_NUMBERS) - present}"

    def test_new_cases_marked_synthetic(self):
        for p in self._new_files():
            assert load_task(p).origin == "synthetic_fixture", f"{p.name}: not marked synthetic"

    def test_new_cases_schema_conformant(self):
        for p in self._new_files():
            t = load_task(p)
            assert t.gold_label in VALID_LABELS
            assert t.expected_answer == t.gold_label
            assert t.task_family == t.gold_label
            assert t.gold_confidence in ("high", "medium", "low")
            assert t.gold_case_type in ("clear", "borderline")
            if t.gold_case_type == "clear":
                assert t.gold_confidence == "high", f"{p.name}: clear must be high"
            if t.gold_case_type == "borderline":
                assert t.gold_alternative_reading and len(t.gold_alternative_reading.strip()) > 10
            assert len(t.expected_findings) > 0
            assert len(t.gold_evidence_spans) > 0
            assert t.curator_notes and "SYNTHETIC FIXTURE" in t.curator_notes

    def test_new_cases_required_fields_via_raw_yaml(self):
        for p in self._new_files():
            data = yaml.safe_load(p.read_text())
            for field in ("id", "gold_label", "expected_findings", "gold_evidence_spans",
                          "difficulty", "origin"):
                assert field in data, f"{p.name}: missing {field}"

    def test_difficulty_values_valid(self):
        for p in self._new_files():
            assert load_task(p).difficulty.value in ("easy", "medium", "hard")


# ---------------------------------------------------------------------------
# Pattern-group coverage
# ---------------------------------------------------------------------------

class TestPatternCoverage:
    def test_each_group_has_at_least_one_case(self):
        present = {_case_number(p) for p in _all_yaml()}
        for group, rng in PATTERN_GROUPS.items():
            assert any(n in present for n in rng), f"no case for group {group}"

    def test_biomedical_group_has_solid_positive_controls(self):
        # cases 051 and 052 are the fair/solid positive controls
        solids = {_case_number(p) for p in _all_yaml()
                  if load_task(p).gold_label == "solid"}
        assert 51 in solids and 52 in solids


# ---------------------------------------------------------------------------
# Documentation coverage
# ---------------------------------------------------------------------------

class TestDocumentation:
    def test_doc_exists(self):
        assert DOC.exists(), "STUDY_FORENSICS_CASE_LIBRARY_V0_1.md missing"

    def test_doc_covers_all_new_cases(self):
        text = DOC.read_text()
        for n in NEW_CASE_NUMBERS:
            token = f"{n:03d}"
            assert token in text, f"doc missing case {token}"

    def test_doc_has_taxonomy_section(self):
        text = DOC.read_text().lower()
        assert "taxonomy" in text
