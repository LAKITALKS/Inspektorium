"""Durable single-variant and exact-content controls from the WP9.3 review."""

import json
from copy import deepcopy

import pytest

from agent_arena.phase9_review import case_key, position_from_result
from agent_arena.phase9_runtime import (
    OfflineReviewProvider, build_challenge, execute_review, replay_review,
    stability_variant, validate_variant,
)
from tests.test_phase9_budget import run_record


def paths(base, task):
    root = base / "phase9"
    identity = case_key(task)
    return root / f"{identity}.json", root / f"{identity}.ledger.json"


@pytest.mark.parametrize("invalid", [False, True])
def test_rejected_choice_survives_repeated_sidecar_loss_without_call_or_budget_renewal(tmp_path, invalid):
    record, raw = run_record(two_evidence=invalid)
    provider = OfflineReviewProvider(raw)
    first = execute_review(record, provider, base_dir=tmp_path, authorized=True, budget_calls=2)
    rejected = execute_review(first, provider, base_dir=tmp_path, authorized=True, budget_calls=2,
                              kind="stability", variant={"original_claim": "changed"} if invalid else None)
    receipt = deepcopy(rejected.metadata["phase9"]["attempts"][-1])
    assert receipt["status"] == "rejected"
    sidecar, ledger_path = paths(tmp_path, record.task)
    ledger = ledger_path.read_bytes()
    for index in range(2):
        sidecar.unlink()
        recovered = execute_review(first.model_copy(update={"run_id": f"reopened-{index}"}), provider,
                                   base_dir=tmp_path, authorized=True, budget_calls=2, kind="stability")
        assert recovered.metadata["phase9"]["attempts"][-1] == receipt
        assert recovered.metadata["phase9"]["route"] == "UNRESOLVED"
        assert recovered.metadata["phase9"]["positions"] == first.metadata["phase9"]["positions"]
        assert ledger_path.read_bytes() == ledger
        assert len(provider.requests) == 1
    replay = replay_review(record.task, base_dir=tmp_path)
    assert replay.metadata["phase9"]["attempts"] == recovered.metadata["phase9"]["attempts"]
    assert len(json.loads(ledger)["attempts"]) == 1
    assert len(provider.requests) == 1


def test_rejection_is_durable_before_sidecar_save_can_fail(tmp_path, monkeypatch):
    from agent_arena import phase9_runtime as runtime

    record, raw = run_record(two_evidence=True)
    provider = OfflineReviewProvider(raw)
    first = execute_review(record, provider, base_dir=tmp_path, authorized=True, budget_calls=2)
    original_save = runtime._save

    def interrupted_save(base, path, record):
        if record.metadata["phase9"]["attempts"][-1]["status"] == "rejected":
            raise RuntimeError("Synthetic interruption before sidecar checkpoint")
        original_save(base, path, record)

    monkeypatch.setattr(runtime, "_save", interrupted_save)
    with pytest.raises(RuntimeError, match="Synthetic interruption"):
        execute_review(first, provider, base_dir=tmp_path, authorized=True, budget_calls=2,
                       kind="stability", variant={})
    monkeypatch.setattr(runtime, "_save", original_save)
    recovered = execute_review(first, provider, base_dir=tmp_path, authorized=True,
                               budget_calls=2, kind="stability")
    assert recovered.metadata["phase9"]["attempts"][-1]["status"] == "rejected"
    assert len(provider.requests) == 1


def test_rejecting_variant_does_not_create_fresh_ledger_for_imported_execution(tmp_path):
    record, raw = run_record(two_evidence=True)
    provider = OfflineReviewProvider(raw)
    first = execute_review(record, provider, base_dir=tmp_path / "source", authorized=True, budget_calls=2)
    destination = tmp_path / "missing-ledger"
    result = execute_review(first, provider, base_dir=destination, authorized=True,
                            budget_calls=2, kind="stability", variant={})
    assert result.metadata["phase9"]["route"] == "UNRESOLVED"
    assert "Governance ledger missing" in result.metadata["phase9"]["attempts"][-1]["reason"]
    assert not paths(destination, record.task)[1].exists()
    assert len(provider.requests) == 1


def test_rejected_variant_before_counterreview_closes_only_variant_choice(tmp_path):
    record, raw = run_record(two_evidence=True)
    provider = OfflineReviewProvider(raw)
    rejected = execute_review(record, provider, base_dir=tmp_path, kind="stability", variant={})
    assert rejected.metadata["phase9"]["attempts"][-1]["status"] == "rejected"
    assert provider.requests == []
    first = execute_review(rejected, provider, base_dir=tmp_path, authorized=True, budget_calls=2)
    assert len(provider.requests) == 1
    paths(tmp_path, record.task)[0].unlink()
    # Even an older import cannot replace the rejected choice after later grant.
    result = execute_review(record, provider, base_dir=tmp_path, authorized=True,
                            budget_calls=2, kind="stability")
    assert result.metadata["phase9"]["attempts"][-1]["status"] == "rejected"
    assert len(provider.requests) == 1
    assert len(first.metadata["phase9"]["positions"]) == 2


@pytest.mark.parametrize("drift", ["bool_offset", "float_offset", "tuple_propositions", "tuple_evidence"])
def test_only_typed_identical_reversal_may_cross_provider_boundary(tmp_path, drift):
    record, raw = run_record(two_evidence=True)
    provider = OfflineReviewProvider(raw)
    first = execute_review(record, provider, base_dir=tmp_path, authorized=True, budget_calls=2)
    original = position_from_result(record.task, record.results[0].agent_result, record.run_id)
    packet = build_challenge(record.task, original)
    variant = stability_variant(packet)
    if drift in {"bool_offset", "float_offset"}:
        variant["propositions"][0]["original_span"]["start"] = False if drift == "bool_offset" else 0.0
    elif drift == "tuple_propositions":
        variant["propositions"] = tuple(variant["propositions"])
    else:
        variant["evidence"] = tuple(variant["evidence"])
    assert validate_variant(packet, variant).startswith("Rejected:")
    result = execute_review(first, provider, base_dir=tmp_path, authorized=True,
                            budget_calls=2, kind="stability", variant=variant)
    assert result.metadata["phase9"]["attempts"][-1]["status"] == "rejected"
    assert len(provider.requests) == 1


def test_valid_reversal_still_executes_once_with_unchanged_typed_payload(tmp_path):
    record, raw = run_record(two_evidence=True)
    provider = OfflineReviewProvider(raw)
    first = execute_review(record, provider, base_dir=tmp_path, authorized=True, budget_calls=2)
    packet = build_challenge(record.task, position_from_result(
        record.task, record.results[0].agent_result, record.run_id))
    variant = stability_variant(packet)
    before = deepcopy(variant)
    assert validate_variant(packet, variant) is None
    result = execute_review(first, provider, base_dir=tmp_path, authorized=True,
                            budget_calls=2, kind="stability", variant=variant)
    assert result.metadata["phase9"]["attempts"][-1]["status"] == "completed"
    assert len(provider.requests) == 2
    sent = json.loads(provider.requests[-1]["task"]["context"].split("Bound evidence packet:\n")[1])
    assert sent == before
    assert type(sent["propositions"][0]["original_span"]["start"]) is int
    assert variant == before
    execute_review(first, provider, base_dir=tmp_path, authorized=True, budget_calls=2, kind="stability")
    assert len(provider.requests) == 2


@pytest.mark.parametrize("requested_kind", ["counterreview", "stability"])
@pytest.mark.parametrize("import_without_sidecar", [False, True])
def test_legacy_rejection_is_made_durable_before_any_early_return(tmp_path, requested_kind, import_without_sidecar):
    record, raw = run_record(two_evidence=True)
    provider = OfflineReviewProvider(raw)
    first = execute_review(record, provider, base_dir=tmp_path, authorized=True, budget_calls=2)
    rejected = execute_review(first, provider, base_dir=tmp_path, authorized=True,
                              budget_calls=2, kind="stability", variant={})
    sidecar, ledger_path = paths(tmp_path, record.task)
    receipt = deepcopy(rejected.metadata["phase9"]["attempts"][-1])
    # Persisted pre-fix format: outcome contains the rejected receipt, while the
    # existing governance ledger contains only the actual counterreview call.
    old_ledger = json.loads(ledger_path.read_text())
    old_ledger.pop("rejected_variants")
    ledger_path.write_text(json.dumps(old_ledger))
    if import_without_sidecar:
        sidecar.unlink()
    reopened = execute_review(rejected, provider, base_dir=tmp_path, authorized=True,
                               budget_calls=2, kind=requested_kind)
    durable = json.loads(ledger_path.read_text())
    assert durable["rejected_variants"]["stability"] == receipt
    assert durable["attempts"] == old_ledger["attempts"]
    assert reopened.metadata["phase9"]["attempts"] == rejected.metadata["phase9"]["attempts"]
    sidecar.unlink()
    attempted_replacement = execute_review(first, provider, base_dir=tmp_path, authorized=True,
                                           budget_calls=2, kind="stability")
    assert attempted_replacement.metadata["phase9"]["attempts"][-1] == receipt
    assert len(provider.requests) == 1


def test_existing_rejected_import_without_execution_ledger_is_rejected_without_new_allowance(tmp_path):
    record, raw = run_record(two_evidence=True)
    provider = OfflineReviewProvider(raw)
    first = execute_review(record, provider, base_dir=tmp_path / "source", authorized=True, budget_calls=2)
    rejected = execute_review(first, provider, base_dir=tmp_path / "source", authorized=True,
                              budget_calls=2, kind="stability", variant={})
    before = rejected.model_dump(mode="json")
    destination = tmp_path / "import"
    with pytest.raises(ValueError, match="Governance ledger missing"):
        execute_review(rejected, provider, base_dir=destination, authorized=True,
                       budget_calls=2, kind="stability")
    assert not paths(destination, record.task)[0].exists()
    assert not paths(destination, record.task)[1].exists()
    assert rejected.model_dump(mode="json") == before
    assert len(provider.requests) == 1


def test_legacy_uncalled_rejection_can_import_durably_without_inventing_calls(tmp_path):
    record, raw = run_record(two_evidence=True)
    rejected = execute_review(record, base_dir=tmp_path / "source", kind="stability", variant={})
    provider = OfflineReviewProvider(raw)
    destination = tmp_path / "import"
    imported = execute_review(rejected, provider, base_dir=destination, kind="stability")
    ledger = json.loads(paths(destination, record.task)[1].read_text())
    assert ledger["attempts"] == []
    assert ledger["rejected_variants"]["stability"] == imported.metadata["phase9"]["attempts"][-1]
    assert provider.requests == []
    execute_review(imported, provider, base_dir=destination, authorized=True, budget_calls=1)
    assert len(provider.requests) == 1
