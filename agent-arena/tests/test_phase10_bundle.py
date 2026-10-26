"""Development boundary regressions; separate from frozen Phase10 acceptance."""
import json
from html import unescape
from copy import deepcopy
from pathlib import Path

import pytest
from click.testing import CliRunner

from agent_arena import artifact_binding, phase10_render
from agent_arena.cli import cli
from agent_arena.evaluator import evaluate_run
from agent_arena.phase10_bundle import (
    create_candidate, inspect_bundle, release_candidate, review_candidate, run_audit,
)
from agent_arena.phase10_pipeline import canonical, digest
from agent_arena.phase9_runtime import OfflineReviewProvider, execute_review
from agent_arena.runner import run_agent
from tests.test_phase9_runtime import fixture


def recorded(state="supported"):
    task, raw = fixture(state)
    response = json.loads(raw)
    payload = response["forensic_record"]
    payload["phase8_taxonomy"] = {
        "core_error": "none" if state == "supported" else "unknown" if state == "unknown" else "overstatement",
        "causal_claim": True, "noncausal_result_used": False,
        "described_biological_mechanism": False, "implies_human_benefit": True,
        "proposition_ids": ["claim:p1"], "evidence_ids": ["e1"],
        "trigger_proposition_id": "claim:p1", "trigger_evidence_id": "e1",
        "trigger_quote": payload["evidence"][0]["text"], "reason": "Offline extracted taxonomy",
    }
    return task, json.dumps(response)


def candidate(tmp_path, state="supported"):
    task, raw = recorded(state)
    provider = OfflineReviewProvider(raw)
    result = run_audit(task, provider, output_root=tmp_path)
    assert result.path, result
    return task, raw, provider, result


def data(path, filename):
    return json.loads((Path(path) / filename).read_text())


def rewrite_hashes(path):
    directory = Path(path)
    manifest = data(path, "manifest.json")
    manifest["files"] = {name: digest((directory / name).read_bytes()) for name in manifest["files"]}
    manifest.pop("fingerprint")
    manifest["fingerprint"] = digest(manifest)
    (directory / "manifest.json").write_bytes(canonical(manifest))


@pytest.mark.parametrize("state", ["supported", "contradicted"])
def test_positive_and_bounded_negative_have_separate_immutable_release(tmp_path, state):
    _, _, provider, first = candidate(tmp_path, state)
    assert first.status == "READY_FOR_RELEASE", first
    original = {p.name: p.read_bytes() for p in Path(first.path).iterdir()}
    released = release_candidate(Path(first.path), output_root=tmp_path,
                                 reviewer="offline operator", reason="Local artifact review")
    assert released.status == "RELEASED", released
    assert first.path != released.path
    assert inspect_bundle(Path(released.path)).valid
    assert {p.name: p.read_bytes() for p in Path(first.path).iterdir()} == original
    envelope = data(released.path, "record.json")
    assert envelope["parent"]["manifest_fingerprint"] == data(first.path, "manifest.json")["fingerprint"]
    decision = data(released.path, "decision.json")
    manifest = data(released.path, "manifest.json")
    assert manifest["provenance"]["phase8_summary"]["composite_state"] == state
    assert manifest["provenance"]["phase9_summary"]["mandatory"] is False
    assert manifest["provenance"]["review_counts"]["positions"] == 1
    assert len(decision["controls"]) == 12
    assert all(c["execution"] == "executed" for c in decision["controls"])
    scope = next(c for c in decision["controls"] if c["control_id"] == "search_scope_binding")
    assert scope["outcome"] == "not_applicable" and scope["eligible"] == 0
    assert "RELEASED" in (Path(released.path) / "report.md").read_text()
    assert len(provider.requests) == 1


def test_unknown_blocks_but_real_corrected_human_layer_is_selected(tmp_path):
    task, _, provider, first = candidate(tmp_path / "bundles", "unknown")
    assert first.status == "REVIEW_REQUIRED"
    assert inspect_bundle(Path(first.path)).valid
    assert release_candidate(Path(first.path), output_root=tmp_path, reviewer="x", reason="x").path is None
    before = data(first.path, "record.json")
    original = before["run_record"]["metadata"]["phase9"]["positions"][0]
    _, correction = recorded()
    revised = review_candidate(Path(first.path), output_root=tmp_path / "bundles",
                               state_dir=tmp_path / "review", selected_position_id=original["position_id"],
                               reviewer="human test operator", reason="Corrected supplied-source interpretation",
                               corrected_raw_output=correction)
    assert revised.status == "READY_FOR_RELEASE", revised
    after = data(revised.path, "record.json")
    history = after["run_record"]["metadata"]["phase9"]
    assert len(history["positions"]) == 2
    assert original in history["positions"]
    selected = next(p for p in history["positions"] if p["position_id"] == after["selected_position_id"])
    assert selected["origin"] == "human_correction"
    assert selected["phase8"]["composite_state"] == "supported"
    assert data(first.path, "record.json") == before
    assert len(provider.requests) == 1
    released = release_candidate(Path(revised.path), output_root=tmp_path / "bundles",
                                 reviewer="operator", reason="Release corrected revision")
    assert released.status == "RELEASED", released


@pytest.mark.parametrize("mutation", ["missing_source", "missing_taxonomy", "empty_findings", "truncated"])
def test_missing_required_analysis_cannot_be_released(tmp_path, mutation):
    task, raw = recorded()
    response = json.loads(raw)
    payload = response["forensic_record"]
    if mutation == "missing_source":
        payload["evidence"][0]["exact_reference"] = "unprovided source"
    elif mutation == "missing_taxonomy":
        del payload["phase8_taxonomy"]
    elif mutation == "empty_findings":
        payload["client_findings"] = []
    raw = json.dumps(response)
    if mutation == "truncated":
        raw = raw[:-20]
    outcome = run_audit(task, OfflineReviewProvider(raw), output_root=tmp_path)
    assert outcome.status == "ANALYSIS_INCOMPLETE", outcome
    assert inspect_bundle(Path(outcome.path)).valid
    assert not release_candidate(Path(outcome.path), output_root=tmp_path, reviewer="x", reason="x").path


def test_provider_error_is_not_analysis_success(tmp_path):
    task, _ = recorded()
    outcome = run_audit(task, OfflineReviewProvider(error="simulated failure"), output_root=tmp_path)
    assert outcome.status == "RUN_FAILED", outcome
    assert inspect_bundle(Path(outcome.path)).valid


@pytest.mark.parametrize("mutation", ["report", "case", "gate", "extra_file", "symlink", "code"])
def test_verifier_rejects_material_changes_even_with_new_outer_hashes(tmp_path, mutation, monkeypatch):
    _, _, _, first = candidate(tmp_path)
    directory = Path(first.path)
    if mutation == "report":
        (directory / "report.html").write_text("<html>truncated</html>")
    elif mutation == "case":
        record = data(first.path, "record.json")
        record["run_record"]["task"]["context"] = "different context"
        (directory / "record.json").write_bytes(canonical(record))
    elif mutation == "gate":
        decision = data(first.path, "decision.json")
        decision["controls"] = decision["controls"][:-1]
        (directory / "decision.json").write_bytes(canonical(decision))
    elif mutation == "extra_file":
        (directory / "report.pdf").write_bytes(b"fake PDF")
    elif mutation == "symlink":
        saved = directory.parent / "foreign.md"
        saved.write_bytes((directory / "report.md").read_bytes())
        (directory / "report.md").unlink()
        (directory / "report.md").symlink_to(saved)
    else:
        from agent_arena import phase10_pipeline
        original = phase10_pipeline.code_identity
        def changed():
            value = original()
            value["code_fingerprint"] = "changed code"
            return value
        monkeypatch.setattr(phase10_pipeline, "code_identity", changed)
    rewrite_hashes(first.path)
    checked = inspect_bundle(directory)
    assert not checked.valid, checked
    assert release_candidate(directory, output_root=tmp_path, reviewer="x", reason="x").path is None


def test_missing_gate_and_failed_renderer_do_not_promote(tmp_path, monkeypatch):
    task, raw = recorded()
    monkeypatch.setattr(artifact_binding, "MANDATORY_PHASE7B_GATE_SPECS",
                        artifact_binding.MANDATORY_PHASE7B_GATE_SPECS[:-1])
    blocked = run_audit(task, OfflineReviewProvider(raw), output_root=tmp_path / "missing")
    assert blocked.status not in {"READY_FOR_RELEASE", "RELEASED"}
    monkeypatch.undo()
    monkeypatch.setattr(phase10_render, "html_report", lambda projection: b"<html>truncated</html>")
    malformed = run_audit(task, OfflineReviewProvider(raw), output_root=tmp_path / "malformed")
    assert malformed.status == "RELEASE_BLOCKED" and malformed.path is None
    assert not list((tmp_path / "malformed").iterdir())


def test_offline_rejects_subclasses_callbacks_and_preflight_before_any_call(tmp_path):
    task, raw = recorded()
    class Subclass(OfflineReviewProvider):
        pass
    for provider in (Subclass(raw), OfflineReviewProvider(raw)):
        if type(provider) is OfflineReviewProvider:
            provider.send_prompt = lambda *_: pytest.fail("callback must not run")
        assert run_audit(task, provider, output_root=tmp_path).status == "PREFLIGHT_BLOCKED"
        assert not provider.requests
    provider = OfflineReviewProvider(raw)
    empty = task.model_copy(update={"prompt": " "})
    assert run_audit(empty, provider, output_root=tmp_path).status == "PREFLIGHT_BLOCKED"
    assert not provider.requests


def test_divergent_history_carriers_remain_visible_and_block(tmp_path):
    task, raw = recorded("unknown")
    original = evaluate_run(task, "first", [run_agent(OfflineReviewProvider(raw), task)])
    _, counter = recorded("contradicted")
    # A mandatory UNKNOWN receives a source-bound contradictory comparison.
    changed = execute_review(original, OfflineReviewProvider(counter), base_dir=tmp_path / "review",
                             authorized=True, budget_calls=2)
    assert len(changed.metadata["phase9"]["positions"]) == 2
    stale = changed.model_copy(deep=True)
    stale.metadata["phase9"] = deepcopy(original.metadata["phase9"])
    outcome = create_candidate(stale, output_root=tmp_path / "bundles")
    assert outcome.status == "REVIEW_REQUIRED", outcome
    bound = data(outcome.path, "record.json")["run_record"]
    assert len(bound["results"][0]["agent_result"]["phase9"]["positions"]) == 2
    assert inspect_bundle(Path(outcome.path)).valid


def test_cli_offline_pipeline_inspect_release_and_no_name_resolution(tmp_path, monkeypatch):
    import agent_arena.cli as legacy
    monkeypatch.setattr(legacy, "get_provider", lambda *_: pytest.fail("No named provider in offline path"))
    task, raw = recorded()
    task_path, recording = tmp_path / "task.json", tmp_path / "recording.json"
    task_path.write_text(task.model_dump_json())
    recording.write_text(raw)
    runner = CliRunner()
    assert runner.invoke(cli, ["audit", "validate", "--task", str(task_path)]).exit_code == 0
    run = runner.invoke(cli, ["audit", "run", "--offline", "--task", str(task_path), "--recording",
                              str(recording), "--output-root", str(tmp_path / "bundles")])
    assert run.exit_code == 0, run.output
    path = json.loads(run.output)["path"]
    assert runner.invoke(cli, ["audit", "inspect", "--bundle", path]).exit_code == 0
    release = runner.invoke(cli, ["audit", "release", "--bundle", path, "--output-root",
                                 str(tmp_path / "bundles"), "--reviewer", "test", "--reason", "local test"])
    assert release.exit_code == 0, release.output
    assert json.loads(release.output)["status"] == "RELEASED"
    assert "Not the canonical Phase10 path" in runner.invoke(cli, ["official-release", "--help"]).output


def test_human_correction_of_failed_original_uses_new_analysis_without_erasing_failure(tmp_path):
    task, correction = recorded()
    first = run_audit(task, OfflineReviewProvider('{"forensic_record":'), output_root=tmp_path / "bundles")
    assert first.status == "ANALYSIS_INCOMPLETE"
    before = data(first.path, "record.json")
    old = before["run_record"]["metadata"]["phase9"]["positions"][0]
    fixed = review_candidate(Path(first.path), output_root=tmp_path / "bundles", state_dir=tmp_path / "state",
                             selected_position_id=old["position_id"], reviewer="host operator",
                             reason="Provide a complete source-bound interpretation", corrected_raw_output=correction)
    assert fixed.status == "READY_FOR_RELEASE", fixed
    revised = data(fixed.path, "record.json")
    assert old in revised["run_record"]["metadata"]["phase9"]["positions"]
    assert revised["selected_position_id"] != old["position_id"]
    assert inspect_bundle(Path(fixed.path)).valid


def test_unverifiable_tracked_source_claim_is_not_accepted(tmp_path):
    from agent_arena.phase10_pipeline import evaluate
    from agent_arena.schemas import RunRecord
    _, _, _, result = candidate(tmp_path)
    audit = data(result.path, "record.json")
    provenance = deepcopy(audit["provenance"])
    provenance["code"]["verified_source_commit"] = "0" * 40
    provenance["code"]["source_binding"] = "verified Git source bytes"
    status, controls, *_ = evaluate(RunRecord.model_validate(audit["run_record"]), "subject", provenance)
    assert status == "RELEASE_BLOCKED"
    assert next(c for c in controls if c.control_id == "provenance").outcome == "fail"


def test_final_release_bytes_are_checked_before_atomic_promotion(tmp_path, monkeypatch):
    _, _, _, first = candidate(tmp_path)
    before = {p.name: p.read_bytes() for p in Path(first.path).iterdir()}
    original_html = phase10_render.html_report
    def corrupt_only_release(projected):
        if projected[0][1]["status"] == "RELEASED":
            return b"<html>unverified final status bytes</html>"
        return original_html(projected)
    monkeypatch.setattr(phase10_render, "html_report", corrupt_only_release)
    outcome = release_candidate(Path(first.path), output_root=tmp_path, reviewer="test", reason="local test")
    assert outcome.status == "RELEASE_BLOCKED" and outcome.path is None
    assert list(tmp_path.iterdir()) == [Path(first.path)]
    assert {p.name: p.read_bytes() for p in Path(first.path).iterdir()} == before
    assert inspect_bundle(Path(first.path)).valid


@pytest.mark.parametrize("field,replacement", [
    ("reviewer", "replacement host"),
    ("reason", "replacement release decision"),
    ("scope", "scientific_truth"),
])
def test_replacing_decision_intent_cannot_reuse_checked_revision(tmp_path, field, replacement):
    _, _, _, first = candidate(tmp_path)
    released = release_candidate(Path(first.path), output_root=tmp_path,
                                 reviewer="original host", reason="original local release")
    assert released.status == "RELEASED"
    path = Path(released.path)
    before = {name: (path / name).read_bytes() for name in ("record.json", "report.md", "report.html")}
    decision = data(path, "decision.json")
    subject = decision["subject"]
    decision["release_intent"][field] = replacement
    (path / "decision.json").write_bytes(canonical(decision))
    rewrite_hashes(path)
    assert data(path, "decision.json")["subject"] == subject
    assert before == {name: (path / name).read_bytes() for name in before}
    assert not inspect_bundle(path).valid


def test_host_release_intent_is_bound_and_visible_and_changes_create_new_revision(tmp_path):
    _, _, provider, first = candidate(tmp_path)
    assert data(first.path, "record.json")["release_intent"] is None
    released = release_candidate(Path(first.path), output_root=tmp_path,
                                 reviewer="first operator", reason="first local review")
    assert released.status == "RELEASED"
    path = Path(released.path)
    original_bytes = {p.name: p.read_bytes() for p in path.iterdir()}
    intent = {"reviewer": "first operator", "reason": "first local review", "scope": "local_artifact_only"}
    for filename in ("record.json", "decision.json", "manifest.json"):
        assert data(path, filename)["release_intent"] == intent
    assert data(path, "decision.json")["subject"] == digest(data(path, "record.json"))
    for filename in ("report.md", "report.html"):
        rendered = unescape((path / filename).read_text())
        assert all(value in rendered for value in intent.values())
    second = release_candidate(Path(first.path), output_root=tmp_path,
                               reviewer="second operator", reason="new local review")
    assert second.status == "RELEASED" and second.path != released.path
    assert data(second.path, "record.json")["revision_id"] != data(path, "record.json")["revision_id"]
    assert data(second.path, "decision.json")["subject"] != data(path, "decision.json")["subject"]
    assert original_bytes == {p.name: p.read_bytes() for p in path.iterdir()}
    assert inspect_bundle(path).valid and inspect_bundle(Path(second.path)).valid
    assert len(provider.requests) == 1
