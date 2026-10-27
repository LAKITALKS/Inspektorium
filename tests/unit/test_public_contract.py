"""Regression tests for the deliberately narrow public contract."""

from __future__ import annotations

import json
from pathlib import Path

from inspektorium.core.models import InspectionReport
from inspektorium.core.relations import EvidenceRelation

ROOT = Path(__file__).resolve().parents[2]


def test_relationship_vocabulary_is_exactly_the_public_four() -> None:
    assert {relation.value for relation in EvidenceRelation} == {
        "supported",
        "contradicted",
        "not_established",
        "attribution_mismatch",
    }


def test_report_schema_contains_no_score_or_semantic_verification_field() -> None:
    schema = json.dumps(InspectionReport.model_json_schema(), sort_keys=True)

    for forbidden in (
        '"total_score"',
        '"trust_score"',
        '"quality_score"',
        '"weighted_score"',
        '"severity_score"',
        '"verified_relation"',
    ):
        assert forbidden not in schema


def test_exactly_one_real_provider_adapter_is_shipped() -> None:
    provider_files = {
        path.name for path in (ROOT / "src" / "inspektorium" / "providers").glob("*.py")
    }

    assert provider_files == {
        "__init__.py",
        "anthropic.py",
        "base.py",
        "parsing.py",
    }


def test_no_benchmark_or_agent_runtime_module_is_shipped() -> None:
    module_names = {path.stem for path in (ROOT / "src" / "inspektorium").rglob("*.py")}

    assert "benchmark" not in module_names
    assert "leaderboard" not in module_names
    assert "agent" not in module_names
