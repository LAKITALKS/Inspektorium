"""Repair Phase 4 — authoritative release-boundary adversarial matrix A–Y.

All release candidates are generic synthetic QA records.  Every source manifest lives in an
isolated temporary Git repository, every output lives under ``tmp_path``, and no provider/model is
constructed.  Historical ASA replay (Z) is intentionally a separate read-only verification so the
tracked suite never depends on ignored real-case material.
"""

from __future__ import annotations

import importlib
import json
import subprocess
from dataclasses import replace
from pathlib import Path

import pytest
from click.testing import CliRunner

from inspektorium.audit import artifact_binding as ab
from inspektorium.audit import release_boundary as rb
from inspektorium.audit.artifact_binding import record_fingerprint
from inspektorium.audit.forensic_report import (
    build_forensic_report,
    render_forensic_report_markdown,
)
from inspektorium.audit.reporting import (
    generate_client_report,
    generate_html_report,
    generate_pdf_report,
)
from inspektorium.audit.reporter import generate_report
from inspektorium.audit.schemas import Difficulty, RunRecord, Task, TaskType


REPO_ROOT = Path(__file__).resolve().parents[2]
RECORD_FIXTURE = REPO_ROOT / "tests/fixtures/audit/pipeline_qa/qa_release_gate_consolidated.json"
REPORT_FIXTURE = REPO_ROOT / "tests/fixtures/audit/report_prototype/01_solid.json"


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


class MaterialFactory:
    def __init__(self, root: Path):
        self.root = root
        self.counter = 0

    def __call__(self, mutate=None):
        self.counter += 1
        record = ab.load_forensic_record(RECORD_FIXTURE).model_copy(deep=True)
        record.synthetic_fixture = True
        record.fixture_class = "release_boundary_qa"
        if mutate is not None:
            mutate(record)
        for provenance in record.provenance:
            provenance.content_fingerprint = ab.compute_content_fingerprint(
                provenance.exact_claim_text,
                provenance.provenance_state,
            )
        repo = self.root / f"source-{self.counter}"
        repo.mkdir()
        _git(repo, "init", "-q")
        _git(repo, "config", "user.name", "Agent Arena QA")
        _git(repo, "config", "user.email", "qa@example.invalid")
        source = repo / "release_source.json"
        source.write_text(json.dumps({
            "release_source_schema_version": rb.RELEASE_SOURCE_SCHEMA_VERSION,
            "data_role": "synthetic_release_qa",
            "execution_id": f"synthetic-execution-{self.counter}",
            "analysis_id": f"synthetic-analysis-{self.counter}",
            "package_fingerprint": "a" * 64,
            "runtime_contract_fingerprint": "b" * 64,
            "forensic_record_fingerprint": record_fingerprint(record),
        }, sort_keys=True) + "\n")
        _git(repo, "add", "release_source.json")
        _git(repo, "commit", "-qm", "freeze synthetic release source")
        candidate = rb.build_release_object(
            record,
            release_object_id=f"synthetic-release-{self.counter}",
            source_artifact_path="release_source.json",
            repo_root=repo,
        )
        output = self.root / f"output-{self.counter}"
        return candidate, repo, source, output


@pytest.fixture
def material(tmp_path):
    return MaterialFactory(tmp_path)


def _packages(output: Path) -> list[Path]:
    namespace = output / rb.OFFICIAL_RELEASE_NAMESPACE
    return sorted(path for path in namespace.iterdir() if path.is_dir()) if namespace.exists() else []


def _assert_no_write(result: rb.ReleaseResult, output: Path) -> None:
    assert result.released is False
    assert result.official_release_write_count == 0
    assert result.package_path is None
    assert _packages(output) == []


def test_A_valid_object_writes_exactly_one_verified_official_package(material):
    candidate, repo, _source, output = material()
    result = rb.release_official_artifact(candidate, output_root=output, repo_root=repo)
    assert result.status == "RELEASED"
    assert result.official_release_write_count == 1
    assert _packages(output) == [Path(result.package_path)]
    verified = rb.verify_official_release(result.package_path, release_object=candidate)
    assert verified.valid is True
    assert verified.artifact_role == rb.OFFICIAL_ARTIFACT_ROLE


def test_B_nonreleasable_consolidated_decision_writes_nothing(material):
    def mutate(record):
        record.client_findings[0].client_strength = "disproven"

    candidate, repo, _source, output = material(mutate)
    result = rb.release_official_artifact(candidate, output_root=output, repo_root=repo)
    assert result.decision_status == "not_releasable"
    _assert_no_write(result, output)


def test_C_one_release_blocking_gate_finding_writes_nothing(material):
    def mutate(record):
        record.client_findings[0].referenced_evidence_ids = ["E1", "D1"]

    candidate, repo, _source, output = material(mutate)
    result = rb.release_official_artifact(candidate, output_root=output, repo_root=repo)
    assert result.status == "NOT_RELEASABLE"
    _assert_no_write(result, output)


def test_D_missing_mandatory_gate_report_is_rejected_before_promotion(
    material, monkeypatch
):
    candidate, repo, _source, output = material()

    def remove_gate(_candidate, report, _staging):
        report.checks_run.pop()

    monkeypatch.setattr(rb, "_before_promotion", remove_gate)
    result = rb.release_official_artifact(candidate, output_root=output, repo_root=repo)
    assert result.status == "REVALIDATION_FAILED"
    _assert_no_write(result, output)


@pytest.mark.parametrize("damage", ["unknown", "duplicate", "wrong_version"])
def test_E_unknown_duplicate_or_wrong_version_gate_report_is_rejected(
    material, monkeypatch, damage
):
    candidate, repo, _source, output = material()

    def damage_report(_candidate, report, _staging):
        if damage == "unknown":
            report.checks_run[0].name = "unknown_gate"
        elif damage == "duplicate":
            report.checks_run.append(report.checks_run[0].model_copy(deep=True))
        else:
            report.checks_run[0].gate_version = "999.0.0"

    monkeypatch.setattr(rb, "_before_promotion", damage_report)
    result = rb.release_official_artifact(candidate, output_root=output, repo_root=repo)
    assert result.status == "REVALIDATION_FAILED"
    _assert_no_write(result, output)


def test_F_caller_cannot_select_one_trivial_gate(material):
    candidate, repo, _source, output = material()
    with pytest.raises(TypeError):
        rb.release_official_artifact(
            candidate, output_root=output, repo_root=repo, mandatory_gates=("trivial",)
        )
    assert _packages(output) == []


@pytest.mark.parametrize("argument", ["release_report", "authorization", "releasable"])
def test_G_H_caller_or_stored_all_green_dictionary_cannot_authorize(
    material, argument
):
    candidate, repo, _source, output = material()
    with pytest.raises(TypeError):
        rb.release_official_artifact(
            candidate,
            output_root=output,
            repo_root=repo,
            **{argument: {"releasable": True}},
        )
    assert _packages(output) == []


def test_I_gate_execution_failure_is_controlled_no_go(material, monkeypatch):
    candidate, repo, _source, output = material()

    def cannot_execute(_record):
        raise RuntimeError("controlled gate unavailable")

    first = replace(ab.MANDATORY_PHASE7B_GATE_SPECS[0], check=cannot_execute)
    monkeypatch.setattr(
        ab, "MANDATORY_PHASE7B_GATE_SPECS", (first, *ab.MANDATORY_PHASE7B_GATE_SPECS[1:])
    )
    result = rb.release_official_artifact(candidate, output_root=output, repo_root=repo)
    assert result.status == "GATE_EXECUTION_ERROR"
    _assert_no_write(result, output)


def test_J_gate_internal_incomplete_state_is_no_go(material, monkeypatch):
    candidate, repo, _source, output = material()

    def malformed_result(_record):
        return None

    first = replace(ab.MANDATORY_PHASE7B_GATE_SPECS[0], check=malformed_result)
    monkeypatch.setattr(
        ab, "MANDATORY_PHASE7B_GATE_SPECS", (first, *ab.MANDATORY_PHASE7B_GATE_SPECS[1:])
    )
    result = rb.release_official_artifact(candidate, output_root=output, repo_root=repo)
    assert result.status == "GATE_EXECUTION_ERROR"
    _assert_no_write(result, output)


def test_K_nonzero_evaluated_zero_findings_is_explicitly_clean(material):
    candidate, _repo, _source, _output = material()
    report = ab.evaluate_artifact_release(candidate.record)
    assert report.releasable is True
    assert all(check.eligible_count > 0 for check in report.checks_run)
    assert all(check.evaluated_count == check.eligible_count for check in report.checks_run)
    assert all(check.finding_count == 0 for check in report.checks_run)
    assert all(check.coverage_state == "evaluated_clean" for check in report.checks_run)


def test_L_zero_eligible_gate_is_explicit_and_fails_closed(material):
    def mutate(record):
        for client in record.client_findings:
            client.client_negative_assertions = []

    candidate, repo, _source, output = material(mutate)
    result = rb.release_official_artifact(candidate, output_root=output, repo_root=repo)
    report = ab.evaluate_artifact_release(candidate.record)
    search = next(check for check in report.checks_run if check.name == "search_scope_binding")
    assert search.eligible_count == search.evaluated_count == 0
    assert search.coverage_state == "zero_eligibility"
    assert result.status == "ZERO_ELIGIBILITY"
    _assert_no_write(result, output)


def test_M_empty_vacuous_record_is_invalid_before_gates(material):
    candidate, repo, _source, output = material()
    candidate.record.provenance = []
    candidate.record.evidence = []
    candidate.record.findings = []
    candidate.record.client_findings = []
    candidate.object_fingerprint = rb.canonical_release_object_fingerprint(candidate)
    result = rb.release_official_artifact(candidate, output_root=output, repo_root=repo)
    assert result.status == "INVALID_OBJECT"
    _assert_no_write(result, output)


def test_N_unknown_eligibility_is_no_go(material, monkeypatch):
    candidate, repo, _source, output = material()

    def unknown(_record):
        raise RuntimeError("eligibility unavailable")

    first = replace(ab.MANDATORY_PHASE7B_GATE_SPECS[0], eligible_count=unknown)
    monkeypatch.setattr(
        ab, "MANDATORY_PHASE7B_GATE_SPECS", (first, *ab.MANDATORY_PHASE7B_GATE_SPECS[1:])
    )
    result = rb.release_official_artifact(candidate, output_root=output, repo_root=repo)
    assert result.status == "GATE_EXECUTION_ERROR"
    _assert_no_write(result, output)


def test_O_partial_coverage_is_rejected(material, monkeypatch):
    candidate, repo, _source, output = material()

    def partial(_candidate, report, _staging):
        report.checks_run[0].evaluated_count -= 1
        report.checks_run[0].unevaluated_count += 1

    monkeypatch.setattr(rb, "_before_promotion", partial)
    result = rb.release_official_artifact(candidate, output_root=output, repo_root=repo)
    assert result.status == "REVALIDATION_FAILED"
    _assert_no_write(result, output)


@pytest.mark.parametrize("damage", ["evaluated_gt_eligible", "negative", "finding_count"])
def test_P_impossible_or_contradictory_counters_are_rejected(
    material, monkeypatch, damage
):
    candidate, repo, _source, output = material()

    def corrupt(_candidate, report, _staging):
        check = report.checks_run[0]
        if damage == "evaluated_gt_eligible":
            check.evaluated_count = check.eligible_count + 1
        elif damage == "negative":
            check.eligible_count = -1
        else:
            check.finding_count += 1

    monkeypatch.setattr(rb, "_before_promotion", corrupt)
    result = rb.release_official_artifact(candidate, output_root=output, repo_root=repo)
    assert result.status == "REVALIDATION_FAILED"
    _assert_no_write(result, output)


def test_Q_wrong_source_fingerprint_is_no_go(material):
    candidate, repo, _source, output = material()
    candidate.source_binding.source_artifact_sha256 = "0" * 64
    candidate.object_fingerprint = rb.canonical_release_object_fingerprint(candidate)
    result = rb.release_official_artifact(candidate, output_root=output, repo_root=repo)
    assert result.status == "INVALID_OBJECT"
    _assert_no_write(result, output)


def test_R_object_change_after_gates_is_rejected(material, monkeypatch):
    candidate, repo, _source, output = material()

    def mutate_object(release_object, _report, _staging):
        release_object.record.client_findings[0].display_claim += " changed"

    monkeypatch.setattr(rb, "_before_promotion", mutate_object)
    result = rb.release_official_artifact(candidate, output_root=output, repo_root=repo)
    assert result.status == "REVALIDATION_FAILED"
    _assert_no_write(result, output)


def test_S_report_or_decision_change_after_execution_is_rejected(material, monkeypatch):
    candidate, repo, _source, output = material()

    def mutate_report(_candidate, report, _staging):
        report.releasable = False
        report.decision_status = "not_releasable"

    monkeypatch.setattr(rb, "_before_promotion", mutate_report)
    result = rb.release_official_artifact(candidate, output_root=output, repo_root=repo)
    assert result.status == "REVALIDATION_FAILED"
    _assert_no_write(result, output)


def test_T_rendered_artifact_change_is_detected_before_promotion(material, monkeypatch):
    candidate, repo, _source, output = material()

    def mutate_artifact(_candidate, _report, staging):
        with (staging / "artifact.json").open("ab") as handle:
            handle.write(b"changed")

    monkeypatch.setattr(rb, "_before_promotion", mutate_artifact)
    result = rb.release_official_artifact(candidate, output_root=output, repo_root=repo)
    assert result.status == "REVALIDATION_FAILED"
    _assert_no_write(result, output)


@pytest.mark.parametrize("failure", ["renderer", "write"])
def test_U_renderer_or_output_io_failure_leaves_no_partial_official_package(
    material, monkeypatch, failure
):
    candidate, repo, _source, output = material()
    if failure == "renderer":
        monkeypatch.setattr(
            rb, "_render_official_artifact",
            lambda *_args: (_ for _ in ()).throw(OSError("controlled renderer failure")),
        )
    else:
        original = rb.Path.write_bytes

        def fail_write(path, data):
            if path.name == "artifact.json":
                raise OSError("controlled output failure")
            return original(path, data)

        monkeypatch.setattr(rb.Path, "write_bytes", fail_write)
    result = rb.release_official_artifact(candidate, output_root=output, repo_root=repo)
    assert result.status == "WRITE_FAILED"
    _assert_no_write(result, output)
    assert list(output.glob(".agent-arena-release-staging-*")) == []


def test_V_preexisting_target_is_not_overwritten_or_reported_as_new(material):
    candidate, repo, _source, output = material()
    first = rb.release_official_artifact(candidate, output_root=output, repo_root=repo)
    assert first.released is True
    manifest = Path(first.package_path) / "manifest.json"
    before = manifest.read_bytes()
    second = rb.release_official_artifact(candidate, output_root=output, repo_root=repo)
    assert second.status == "TARGET_COLLISION"
    assert second.official_release_write_count == 0
    assert second.package_path is None
    assert manifest.read_bytes() == before


def test_V_broken_symlink_target_is_an_occupied_collision(material):
    candidate, repo, _source, output = material()
    report = ab.evaluate_artifact_release(candidate.record)
    target = output / rb.OFFICIAL_RELEASE_NAMESPACE / rb._release_id(candidate, report)
    target.parent.mkdir(parents=True)
    target.symlink_to(output / "missing-prior-target", target_is_directory=True)
    result = rb.release_official_artifact(candidate, output_root=output, repo_root=repo)
    assert result.status == "TARGET_COLLISION"
    assert result.official_release_write_count == 0
    assert target.is_symlink()


def test_V_symlinked_official_namespace_is_rejected(material):
    candidate, repo, _source, output = material()
    output.mkdir()
    external = output.parent / "external-namespace"
    external.mkdir()
    (output / rb.OFFICIAL_RELEASE_NAMESPACE).symlink_to(external, target_is_directory=True)
    result = rb.release_official_artifact(candidate, output_root=output, repo_root=repo)
    assert result.status == "INVALID_OUTPUT_NAMESPACE"
    assert result.official_release_write_count == 0
    assert list(external.iterdir()) == []


def test_W_direct_forensic_renderer_is_diagnostic_and_verifier_rejects_it(tmp_path):
    report = build_forensic_report(json.loads(REPORT_FIXTURE.read_text()))
    rendered = render_forensic_report_markdown(report)
    assert "DIAGNOSTIC / NON-RELEASE ARTIFACT" in rendered
    assert "official_release_authorized=false" in rendered
    package = tmp_path / "diagnostic"
    package.mkdir()
    (package / "preview.md").write_text(rendered)
    assert rb.verify_official_release(package).valid is False


def test_public_client_renderers_return_diagnostic_only_content():
    record = RunRecord(
        run_id="diagnostic-renderer-test",
        task=Task(
            id="diagnostic-renderer-task",
            title="Diagnostic renderer task",
            domain="synthetic",
            difficulty=Difficulty.EASY,
            task_type=TaskType.CLOSED_WITH_REASONING,
            prompt="Synthetic diagnostic input.",
        ),
        results=[],
        timestamp="2026-08-27T00:00:00+00:00",
    )
    for content in (
        generate_report(record), generate_client_report(record), generate_html_report(record),
    ):
        assert "DIAGNOSTIC / NON-RELEASE ARTIFACT" in content
        assert "official_release_authorized=false" in content
        assert '"official_release_authorized":true' not in content.replace(" ", "").lower()


def test_direct_pdf_renderer_cannot_write_into_official_namespace(tmp_path):
    record = RunRecord(
        run_id="diagnostic-pdf-test",
        task=Task(
            id="diagnostic-pdf-task",
            title="Diagnostic PDF task",
            domain="synthetic",
            difficulty=Difficulty.EASY,
            task_type=TaskType.CLOSED_WITH_REASONING,
            prompt="Synthetic diagnostic input.",
        ),
        results=[],
        timestamp="2026-08-27T00:00:00+00:00",
    )
    forbidden = tmp_path / rb.OFFICIAL_RELEASE_NAMESPACE / "preview.pdf"
    with pytest.raises(ValueError, match="official release namespace"):
        generate_pdf_report(record, forbidden)
    assert not forbidden.exists()


def test_Y_valid_package_cross_verifies_exact_object_report_and_hashes(material):
    candidate, repo, _source, output = material()
    result = rb.release_official_artifact(candidate, output_root=output, repo_root=repo)
    verification = rb.verify_official_release(result.package_path, release_object=candidate)
    assert verification.valid is True
    other = candidate.model_copy(deep=True)
    other.release_object_id = "different-object"
    other.object_fingerprint = rb.canonical_release_object_fingerprint(other)
    mismatch = rb.verify_official_release(result.package_path, release_object=other)
    assert mismatch.valid is False
    assert "different release object" in "; ".join(mismatch.errors)


def test_official_release_api_still_releases(material, tmp_path):
    candidate, repo, _source, output = material()
    assert _packages(output) == []
    # The historical API stays available for verification of earlier packages.
    released = rb.release_official_artifact(candidate, output_root=output, repo_root=repo)
    assert released.released is True and released.status == "RELEASED"
    assert len(_packages(output)) == 1


def test_official_release_api_denial_writes_nothing(material, tmp_path):
    def mutate(record):
        record.client_findings[0].client_strength = "disproven"

    candidate, repo, _source, output = material(mutate)
    assert _packages(output) == []
    denied = rb.release_official_artifact(candidate, output_root=output, repo_root=repo)
    assert denied.released is False and denied.status == "NOT_RELEASABLE"
    assert _packages(output) == []


def test_wrong_release_object_schema_and_pipeline_qa_role_fail_closed(material):
    candidate, repo, _source, output = material()
    raw = candidate.model_dump(mode="json")
    raw["release_object_schema_version"] = "unknown/v999"
    with pytest.raises(Exception):
        rb.CanonicalReleaseObject.model_validate(raw)
    candidate.record.fixture_class = "pipeline_qa"
    candidate.object_fingerprint = rb.canonical_release_object_fingerprint(candidate)
    result = rb.release_official_artifact(candidate, output_root=output, repo_root=repo)
    assert result.status == "INVALID_OBJECT"
    _assert_no_write(result, output)
