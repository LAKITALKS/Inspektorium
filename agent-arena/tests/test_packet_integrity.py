"""Tests for the Phase 6.0 deterministic, offline packet-integrity tool.

Covers: the clean baseline over the real library, the model-facing reconstruction
contract, injected contamination (gold token / gold text / IAA id / case id /
evidence annotation), semantic breakage (empty claim / altered system prompt),
sealed-path refusal, and aggregate reporting over a temp directory.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from agent_arena.packet_integrity import (
    STUDY_FORENSICS_PROMPT,
    SealedPathError,
    ModelFacingPacket,
    assert_path_allowed,
    build_model_facing_packet,
    check_semantic_preservation,
    check_task,
    run_packet_integrity,
)
from agent_arena.schemas import GoldEvidenceSpan, Task
from agent_arena.task_loader import load_task

CASE = Path("tasks/study_forensics/case013_gut_microbes.yaml")


@pytest.fixture
def task() -> Task:
    return load_task(CASE)


def _codes(result) -> set[str]:
    return {f.code for f in result.findings}


# --------------------------------------------------------------------------
# Reconstruction contract + clean baseline
# --------------------------------------------------------------------------

def test_build_packet_mirrors_provider_contract(task: Task):
    """User content is exactly task.prompt; system is the canonical SF contract.

    Pins the runtime assumption the tool relies on: if a provider ever serializes
    more of the Task into the model message, this test must be updated in lockstep.
    """
    packet = build_model_facing_packet(task)
    assert packet.user == task.prompt
    assert packet.system == STUDY_FORENSICS_PROMPT
    assert packet.case_id == task.id


def test_clean_task_passes_both_checks(task: Task):
    report = check_task(task, case_file=CASE.name)
    assert report.semantic.passed
    assert report.contamination.passed
    assert report.ok


# --------------------------------------------------------------------------
# Contamination / leakage — each check reported separately from semantic
# --------------------------------------------------------------------------

def test_technical_label_token_in_claim_flagged(task: Task):
    leaked = task.model_copy(update={"prompt": task.prompt + " label: mechanism_vs_evidence"})
    report = check_task(leaked, case_file=CASE.name)
    # semantic still passes (claim == task.prompt); only contamination fails.
    assert report.semantic.passed
    assert not report.contamination.passed
    assert "label_token_in_claim" in _codes(report.contamination)


def test_gold_justification_copied_into_claim_flagged(task: Task):
    leaked = task.model_copy(update={"prompt": task.prompt + "\n\n" + (task.gold_justification or "")})
    report = check_task(leaked, case_file=CASE.name)
    assert "gold_text_in_claim" in _codes(report.contamination)


def test_iaa_identifier_flagged(task: Task):
    leaked = task.model_copy(update={"prompt": task.prompt + " (packet BIAA-013)"})
    report = check_task(leaked, case_file=CASE.name)
    assert "iaa_identifier_in_packet" in _codes(report.contamination)


def test_case_identifier_in_claim_flagged(task: Task):
    leaked = task.model_copy(update={"prompt": task.prompt + f" [{task.id}]"})
    report = check_task(leaked, case_file=CASE.name)
    assert "case_identifier_in_claim" in _codes(report.contamination)


def test_filename_stem_in_claim_flagged(task: Task):
    leaked = task.model_copy(update={"prompt": task.prompt + " see case013_gut_microbes"})
    report = check_task(leaked, case_file=CASE.name)
    assert "case_identifier_in_claim" in _codes(report.contamination)


def test_evidence_annotation_leak_flagged(task: Task):
    annotation = "This annotation reveals why the span matters for gold labeling."
    span = GoldEvidenceSpan(span="x", why_it_matters=annotation, supports_finding="f")
    leaked = task.model_copy(update={
        "prompt": task.prompt + "\n" + annotation,
        "gold_evidence_spans": [span],
    })
    report = check_task(leaked, case_file=CASE.name)
    assert "evidence_annotation_in_claim" in _codes(report.contamination)


def test_bare_word_solid_not_flagged(task: Task):
    """The generic English word 'solid' must not trip the label-token check."""
    benign = task.model_copy(update={"prompt": task.prompt + " The design rests on solid ground."})
    report = check_task(benign, case_file=CASE.name)
    assert report.contamination.passed


# --------------------------------------------------------------------------
# Semantic preservation
# --------------------------------------------------------------------------

def test_empty_claim_semantic_fail(task: Task):
    broken = task.model_copy(update={"prompt": ""})
    report = check_task(broken, case_file=CASE.name)
    assert not report.semantic.passed
    assert "empty_claim" in _codes(report.semantic)


def test_altered_system_prompt_semantic_fail(task: Task):
    tampered = ModelFacingPacket(
        case_id=task.id, task_type="study_forensics",
        system="You are a helpful assistant.", user=task.prompt,
    )
    result = check_semantic_preservation(task, tampered)
    assert not result.passed
    assert "system_prompt_modified" in _codes(result)


def test_claim_altered_semantic_fail(task: Task):
    packet = build_model_facing_packet(task)
    tampered = ModelFacingPacket(
        case_id=task.id, task_type="study_forensics",
        system=packet.system, user=task.prompt + " EXTRA",
    )
    result = check_semantic_preservation(task, tampered)
    assert "claim_altered" in _codes(result)


# --------------------------------------------------------------------------
# Isolation guard
# --------------------------------------------------------------------------

@pytest.mark.parametrize("sealed", [
    "/x/analysis/phase5_05_blind_iaa_packets/internal_only",
    "__LOCAL_HOME__/Documents/AgentArena_IAA_Private/phase5_1_holdout",
    "/repo/research/agent_arena_library_expansion_150/candidates",
])
def test_sealed_path_refused(sealed: str):
    with pytest.raises(SealedPathError):
        assert_path_allowed(sealed)


def test_run_refuses_sealed_dir():
    with pytest.raises(SealedPathError):
        run_packet_integrity(task_dir="/repo/analysis/x/internal_only")


def test_allowed_path_ok(tmp_path):
    assert assert_path_allowed(tmp_path) == tmp_path.resolve()


# --------------------------------------------------------------------------
# Aggregate reporting
# --------------------------------------------------------------------------

def test_run_packet_integrity_aggregates(tmp_path):
    raw = yaml.safe_load(CASE.read_text())
    # good copy
    (tmp_path / "good.yaml").write_text(yaml.safe_dump(raw))
    # contaminated copy
    bad = dict(raw)
    bad["id"] = "study-forensics-bad"
    bad["prompt"] = raw["prompt"] + " label: correlation_vs_causation"
    (tmp_path / "bad.yaml").write_text(yaml.safe_dump(bad))

    report = run_packet_integrity(task_dir=tmp_path)
    assert report.n_cases == 2
    assert report.n_contamination_fail == 1
    assert report.n_semantic_fail == 0
    assert not report.ok
    d = report.as_dict()
    # both checks remain separately represented in the machine-readable output
    for case in d["cases"]:
        assert "semantic_preservation" in case
        assert "contamination_leakage" in case


def test_real_library_passes():
    """Regression guard: every active canonical case has a clean model-facing packet."""
    report = run_packet_integrity()
    assert report.n_cases >= 40
    assert report.n_ok == report.n_cases
    assert report.ok
