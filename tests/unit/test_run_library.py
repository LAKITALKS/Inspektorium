"""Tests for the Phase 4 case-library run harness (run_library.py).

All tests use deterministic in-process fake providers — no live API calls.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from inspektorium.audit import run_library as run_library_module
from inspektorium.audit.confidence_validity import INVALID, MISSING, VALID
from inspektorium.audit.providers import BaseProvider, ModelResponse
from inspektorium.audit.run_library import (
    FakeLibraryProvider,
    _case_stability,
    discover_cases,
    render_summary_md,
    run_library,
    HIGH_SCORE_VARIANCE_THRESHOLD,
)

# The case library is a test fixture; the harness default path is relative to the working directory.
CASE_LIBRARY = Path(__file__).resolve().parents[1] / "fixtures" / "audit" / "case_library"


@pytest.fixture(autouse=True)
def _case_library_fixture(monkeypatch):
    monkeypatch.setattr(run_library_module, "TASK_DIR", CASE_LIBRARY)


REQUIRED_FIELDS = {
    "library_run_id", "case_id", "case_file", "gold_label", "run_index",
    "provider", "model", "label", "label_correct", "score", "confidence",
    "confidence_state",
    "parse_ok", "finish_reason", "truncation_suspected", "error", "error_type",
    "latency_ms", "usage", "timestamp", "raw_result_ref",
}


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------

class FakeMalformed(BaseProvider):
    name = "fake_malformed"

    def __init__(self):
        self.model = "fm"
        self.label = "FM"

    def send_prompt(self, task, system_prompt) -> str:
        return "here is my analysis {not valid json"


class FakeLength(BaseProvider):
    name = "fake_length"

    def __init__(self):
        self.model = "fl"
        self.label = "FL"

    def generate(self, task, system_prompt) -> ModelResponse:
        payload = json.dumps({"final_answer": task.gold_label, "confidence": 0.7})
        return ModelResponse(text=payload, provider=self.name, model=self.model,
                             finish_reason="length", latency_ms=1)

    def send_prompt(self, task, system_prompt) -> str:
        return self.generate(task, system_prompt).text


class FakeError(BaseProvider):
    name = "fake_error"

    def __init__(self):
        self.model = "fe"
        self.label = "FE"

    def generate(self, task, system_prompt) -> ModelResponse:
        return ModelResponse(text="", provider=self.name, model=self.model,
                             finish_reason="error", error="429 too many requests",
                             error_type="rate_limit_error", latency_ms=1)

    def send_prompt(self, task, system_prompt) -> str:
        raise RuntimeError("429 too many requests")


class FakeUnstable(BaseProvider):
    """Alternates the detected label across runs of the same case."""
    name = "fake_unstable"

    def __init__(self):
        self.model = "fu"
        self.label = "FU"
        self._n = 0

    def send_prompt(self, task, system_prompt) -> str:
        label = "overclaim" if self._n % 2 == 0 else "solid"
        self._n += 1
        return json.dumps({"final_answer": label, "confidence": 0.6})


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

class TestDiscovery:
    def test_active_default_excludes_retired(self):
        # 50 files exist, but retired cases are excluded from active discovery.
        # Retired: study-forensics-042 (Phase 5 intake audit) and study-forensics-031
        # (Phase 5.05e curator-approved retirement) -> 48 active.
        cases = discover_cases()
        assert len(cases) == 48
        assert all(t.id != "study-forensics-042" for _, t in cases)
        assert all(t.id != "study-forensics-031" for _, t in cases)

    def test_include_retired_returns_all(self):
        cases = discover_cases(include_retired=True)
        assert len(cases) == 50
        assert any(t.id == "study-forensics-042" for _, t in cases)

    def test_case_id_filter(self):
        cases = discover_cases(case_id="study-forensics-043")
        assert len(cases) == 1
        assert cases[0][1].id == "study-forensics-043"

    def test_limit(self):
        assert len(discover_cases(limit=5)) == 5

    def test_synthetic_only_subset(self):
        syn = discover_cases(synthetic_only=True)
        # the 21 Phase-3 fixtures are synthetic; there may be more later
        assert len(syn) >= 21
        assert all(t.origin == "synthetic_fixture" for _, t in syn)

    def test_label_filter(self):
        solids = discover_cases(label="solid")
        assert len(solids) >= 2
        assert all(t.gold_label == "solid" for _, t in solids)


# ---------------------------------------------------------------------------
# Batch execution
# ---------------------------------------------------------------------------

class TestBatchRun:
    def test_small_subset_fake(self):
        cases = discover_cases(limit=3)
        summary = run_library(FakeLibraryProvider(), cases, runs_per_case=1,
                              write_artifacts=False)
        assert summary.total_cases == 3
        assert summary.total_runs == 3
        assert all(not r["error"] for r in summary.records)

    def test_runs_per_case_creates_n_results(self):
        cases = discover_cases(limit=4)
        summary = run_library(FakeLibraryProvider(), cases, runs_per_case=3,
                              write_artifacts=False)
        assert summary.total_runs == 12
        for c in summary.case_stability:
            assert c.n_runs == 3

    def test_result_records_have_required_fields(self):
        cases = discover_cases(limit=2)
        summary = run_library(FakeLibraryProvider(), cases, runs_per_case=1,
                              write_artifacts=False)
        for r in summary.records:
            assert REQUIRED_FIELDS.issubset(r.keys())
            assert "api_key" not in r and "ANTHROPIC_API_KEY" not in json.dumps(r)

    def test_fake_provider_is_label_correct(self):
        cases = discover_cases(limit=5)
        summary = run_library(FakeLibraryProvider(), cases, runs_per_case=1,
                              write_artifacts=False)
        # fake echoes gold_label, so detected label should match gold
        for r in summary.records:
            assert r["label"] == r["gold_label"]


# ---------------------------------------------------------------------------
# Stability metrics & flags
# ---------------------------------------------------------------------------

class TestStability:
    def test_label_consistency_stable(self):
        cases = discover_cases(limit=2)
        summary = run_library(FakeLibraryProvider(), cases, runs_per_case=3,
                              write_artifacts=False)
        for c in summary.case_stability:
            assert c.label_consistency_rate == 1.0
            assert c.flags["stable_label"] is True
            assert c.flags["unstable_label"] is False

    def test_unstable_label_flagged(self):
        cases = discover_cases(limit=1)
        summary = run_library(FakeUnstable(), cases, runs_per_case=4,
                              write_artifacts=False)
        c = summary.case_stability[0]
        assert c.flags["unstable_label"] is True
        assert len(c.unique_labels) == 2
        assert c.label_consistency_rate < 1.0

    def test_parse_failure_flagged(self):
        cases = discover_cases(limit=1)
        summary = run_library(FakeMalformed(), cases, runs_per_case=2,
                              write_artifacts=False)
        c = summary.case_stability[0]
        assert c.parse_failures == 2
        assert c.flags["parse_fragile"] is True

    def test_truncation_risk_flagged(self):
        cases = discover_cases(limit=1)
        summary = run_library(FakeLength(), cases, runs_per_case=2,
                              write_artifacts=False)
        c = summary.case_stability[0]
        assert c.truncation_count >= 1
        assert c.flags["truncation_risk"] is True
        for r in summary.records:
            assert r["finish_reason"] == "length"

    def test_provider_error_flagged(self):
        cases = discover_cases(limit=1)
        summary = run_library(FakeError(), cases, runs_per_case=2,
                              write_artifacts=False)
        c = summary.case_stability[0]
        assert c.flags["provider_error_seen"] is True
        assert c.failed_runs == 2
        assert "rate_limit_error" in c.error_types
        # a failed call must not look like a successful empty response
        for r in summary.records:
            assert r["error"] is not None
            assert r["parse_ok"] is False

    def test_summary_dict_aggregates(self):
        cases = discover_cases(limit=3)
        summary = run_library(FakeLibraryProvider(), cases, runs_per_case=2,
                              write_artifacts=False)
        s = summary.summary_dict()
        assert s["total_runs"] == 6
        assert s["successful_runs"] == 6
        assert s["thresholds"]["high_score_variance"] == HIGH_SCORE_VARIANCE_THRESHOLD

    def test_confidence_mean_requires_valid_state_and_reports_denominator(self):
        records = []
        for confidence, state in ((0.9, VALID), (None, MISSING), (0.8, INVALID)):
            records.append({
                "error": None,
                "parse_ok": True,
                "truncation_suspected": False,
                "label": "solid",
                "score": 80.0,
                "confidence": confidence,
                "confidence_state": state,
                "error_type": None,
                "case_file": "case.yaml",
                "gold_label": "solid",
            })

        stability = _case_stability("case", records)

        assert stability.confidence_mean == 0.9
        assert stability.n_confidence_observations == 3
        assert stability.n_confidence_eligible == 1
        assert stability.n_confidence_ineligible == 2


# ---------------------------------------------------------------------------
# Artifacts
# ---------------------------------------------------------------------------

class TestArtifacts:
    def test_artifacts_written(self, tmp_path):
        cases = discover_cases(limit=2)
        out = tmp_path / "librun"
        run_library(FakeLibraryProvider(), cases, runs_per_case=2,
                    out_dir=out, write_artifacts=True)
        assert (out / "manifest.json").exists()
        assert (out / "results.jsonl").exists()
        assert (out / "summary.json").exists()
        assert (out / "summary.md").exists()

        lines = (out / "results.jsonl").read_text().strip().splitlines()
        assert len(lines) == 4  # 2 cases x 2 runs
        rec = json.loads(lines[0])
        assert REQUIRED_FIELDS.issubset(rec.keys())

        manifest = json.loads((out / "manifest.json").read_text())
        assert manifest["total_runs"] == 4
        assert manifest["runs_per_case"] == 2

    def test_summary_md_content(self):
        cases = discover_cases(limit=2)
        summary = run_library(FakeLibraryProvider(), cases, runs_per_case=1,
                              write_artifacts=False)
        md = render_summary_md(summary)
        assert "Case Library Run Summary" in md
        assert "Per-case stability" in md
        assert "Label distribution" in md


# ---------------------------------------------------------------------------
# Case retirement (docs/case_intake_policy.md)
# ---------------------------------------------------------------------------

class TestRetirement:
    RETIRED_ID = "study-forensics-042"

    def _load_042(self):
        from inspektorium.audit.task_loader import load_task
        return load_task("tests/fixtures/audit/case_library/case042_edge_ai_energy_blind_spot.yaml")

    def test_retired_case_still_loads(self):
        # 1. case042 still loads and is not hard-deleted.
        t = self._load_042()
        assert t.id == self.RETIRED_ID
        assert t.status == "retired"
        assert t.excluded_from_active_metrics is True
        assert t.origin == "demo_derived"

    def test_is_retired_helper(self):
        from inspektorium.audit.run_library import is_retired
        assert is_retired(self._load_042()) is True

    def test_retired_skipped_by_default(self):
        # 2. retired case is skipped by default discovery.
        ids = {t.id for _, t in discover_cases()}
        assert self.RETIRED_ID not in ids

    def test_active_count_is_48(self):
        # 4. active case count is 48 under default discovery: 50 files minus two
        # retired cases (study-forensics-042 and study-forensics-031).
        assert len(discover_cases()) == 48

    def test_include_retired_includes_it(self):
        # 3. include-retired behavior includes it.
        ids = {t.id for _, t in discover_cases(include_retired=True)}
        assert self.RETIRED_ID in ids
        assert len(discover_cases(include_retired=True)) == 50

    def test_retired_discoverable_by_explicit_case_id(self):
        # remains discoverable for audit if explicitly requested.
        cases = discover_cases(case_id=self.RETIRED_ID)
        assert len(cases) == 1 and cases[0][1].id == self.RETIRED_ID

    def test_label_and_prompt_unchanged(self):
        # 5. no label / prompt changes from retirement.
        t = self._load_042()
        assert t.gold_label == "overclaim"
        assert t.expected_answer == "overclaim"
        assert t.task_family == "overclaim"
        # prompt still contains the evaluated central claim + all four subclaims
        assert "Evaluate the following central claim" in t.prompt
        for sub in ('A. "Edge-AI hardware can support', 'B. "Energy efficiency',
                    'C. "Enterprise readiness', 'D. "Lack of process-level'):
            assert sub in t.prompt
