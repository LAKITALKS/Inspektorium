"""AA-P10-LIVE/1.0 acceptance matrix L1-L9 through the real audit entry point.

Network access is replaced by an httpx MockTransport double; no test can reach a provider.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
import pytest

from agent_arena import phase10_live as live
from agent_arena.bounded_harness_mission import MissionError
from agent_arena.phase10_bundle import create_candidate, inspect_bundle, release_candidate, run_audit
from agent_arena.phase10_pipeline import REGISTRY, LIVE_REGISTRY, registry_fingerprint
from agent_arena.phase10_projection import LIVE_NOTICE, NOTICE, REPLAY_NOTICE
from agent_arena.phase9_runtime import OfflineReviewProvider
from agent_arena.providers.anthropic_live import (
    PROFILES, build_user_message, cost_microusd, interpret_message, max_exposure_microusd,
)
from agent_arena.runner import (
    STUDY_FORENSICS_PROMPT_VERSION_PHASE8, STUDY_FORENSICS_PROMPT_VERSION_PHASE9,
    resolve_study_forensics_prompt,
)
from agent_arena.schemas import RunRecord
from agent_arena.task_loader import load_task

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples" / "phase10"
HAIKU = "claude-haiku-5-5@1"
SONNET = "claude-sonnet-5-5@1"
P8 = STUDY_FORENSICS_PROMPT_VERSION_PHASE8
# Captured at import, before the fixture below isolates each test from the pinned live history.
PINNED_HISTORY = dict(live.KNOWN_CLOSED_AUTHORIZATIONS)


@pytest.fixture(autouse=True)
def _isolated_live_history(monkeypatch):
    """Unit tests use their own throwaway authorizations; the pinned closed history has its own tests."""
    monkeypatch.setattr(live, "KNOWN_CLOSED_AUTHORIZATIONS", {})


def _task(name):
    return load_task(EXAMPLES / f"{name}-task.json")


def _recording(name):
    return (EXAMPLES / f"{name}-recording.json").read_text()


def _authorize(directory: Path, tasks, *, budget=2_000_000, ceiling=400_000, attempts=40, retries=4,
               expires=None, profiles=(HAIKU, SONNET), auth_id="TEST-LIVE-AUTH"):
    directory.mkdir(parents=True, exist_ok=True)
    auth = {
        "schema": live.AUTH_SCHEMA, "authorization_id": auth_id,
        "work_order": "unit test", "issued_at": "2026-10-11T00:00:00+00:00",
        "expires_at": (expires or datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "status": "ACTIVE", "canonical_directory": str(directory.resolve()),
        "endpoint": "https://api.anthropic.com",
        "total_budget_microusd": budget, "max_generation_attempts": attempts,
        "max_technical_retries": retries, "max_attempts_per_request": 2,
        "per_call_ceiling_microusd": ceiling,
        "allowed_profiles": {p: PROFILES[p].fingerprint() for p in profiles},
        "task_bindings": {t.id: live.task_sha256(t) for t in tasks},
        "slots": [live.slot_key(t.id, p, k) for t in tasks for p in profiles for k in live.KINDS],
        "supersedes": {"state": "CLOSED_NOT_EXECUTABLE"},
    }
    (directory / "authorization.json").write_text(json.dumps(auth, indent=2))
    return directory


class Transport:
    """Scripted Messages API double that records every request it would have sent."""

    def __init__(self, *responses):
        self.responses = list(responses)
        self.requests = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append({"url": str(request.url), "headers": dict(request.headers),
                              "body": json.loads(request.content)})
        item = self.responses.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item

    def mock(self):
        return httpx.MockTransport(self)


def message(text, *, model="claude-haiku-5-5", stop="end_turn", blocks=None, usage=None, request_id="req_t"):
    content = blocks if blocks is not None else [
        {"type": "thinking", "thinking": "", "signature": "sig"}, {"type": "text", "text": text}]
    body = {"id": "msg_t", "type": "message", "role": "assistant", "model": model, "content": content,
            "stop_reason": stop, "stop_sequence": None,
            "usage": usage or {"input_tokens": 9000, "output_tokens": 3000,
                               "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}}
    return httpx.Response(200, json=body, headers={"request-id": request_id})


def _session(directory, transport, mode="live"):
    return live.LiveSession(directory, mode=mode, transport=transport.mock() if transport else None,
                            api_key="test-key")


def _live_run(tmp_path, name, transport, *, profile=HAIKU, directory=None, tasks=None):
    task = _task(name)
    directory = directory or _authorize(tmp_path / "auth", tasks or [task])
    with _session(directory, transport) as session:
        provider = live.LiveAuditProvider(session, profile, task.id, "primary", P8)
        result = run_audit(task, provider, output_root=tmp_path / "out", review_state=directory / "phase9-state")
        return result, session.summary(), provider


def _record(path) -> dict:
    return json.loads((Path(path) / "record.json").read_text())


def _decision(path) -> dict:
    return json.loads((Path(path) / "decision.json").read_text())


# ---------------------------------------------------------------- L1 offline and replay


def test_L1_offline_run_and_inspect_send_nothing_and_keep_offline_contract(tmp_path, monkeypatch):
    def forbid(*_args, **_kwargs):
        raise AssertionError("network access attempted")
    monkeypatch.setattr(httpx.Client, "send", forbid)
    result = run_audit(_task("positive"), OfflineReviewProvider(_recording("positive")), output_root=tmp_path)
    assert result.status == "READY_FOR_RELEASE"
    record, decision = _record(result.path), _decision(result.path)
    assert record["execution_mode"] == "recorded_offline"
    assert record["provenance"]["config"] == "offline-recording-v1"
    assert "execution_evidence" not in record["provenance"]
    assert decision["registry_fingerprint"] == registry_fingerprint()
    assert {c["control_id"]: c["version"] for c in decision["controls"]} == REGISTRY
    assert NOTICE in (Path(result.path) / "report.md").read_text()
    assert inspect_bundle(Path(result.path)).valid


def test_L1_replay_reuses_capture_without_any_network_call(tmp_path, monkeypatch):
    result, _, _ = _live_run(tmp_path, "positive", Transport(message(_recording("positive"))))
    assert result.status == "READY_FOR_RELEASE"
    directory = tmp_path / "auth"

    def forbid(*_args, **_kwargs):
        raise AssertionError("network access attempted during replay")
    monkeypatch.setattr(httpx.Client, "send", forbid)
    task = _task("positive")
    with live.LiveSession(directory, mode="replay") as session:
        provider = live.ReplayProvider(session, HAIKU, task.id, "primary", P8)
        replay = run_audit(task, provider, output_root=tmp_path / "replay", review_state=tmp_path / "rs")
    assert replay.status == "READY_FOR_RELEASE"
    record = _record(replay.path)
    assert record["execution_mode"] == "offline_replay_of_live"
    evidence = record["run_record"]["results"][0]["agent_result"]["execution_evidence"]
    assert evidence["origin"] == "live_generation" and evidence["current_execution"] == "offline_replay"
    assert evidence["new_generation"] is False and evidence["replay_capture_verified"] is True
    assert REPLAY_NOTICE in (Path(replay.path) / "report.md").read_text()
    assert inspect_bundle(Path(replay.path)).valid


# ---------------------------------------------------------------- L2 live path


def test_L2_authorized_live_run_reaches_parser_p8_p9_p10_and_binds_evidence(tmp_path):
    transport = Transport(message(_recording("positive")))
    result, summary, provider = _live_run(tmp_path, "positive", transport)
    assert result.status == "READY_FOR_RELEASE", result.errors
    assert provider.network_attempts == 1 and len(transport.requests) == 1
    sent = transport.requests[0]
    assert sent["url"] == "https://api.anthropic.com/v1/messages"
    body = sent["body"]
    assert not {"temperature", "top_p", "top_k"} & set(body)
    assert body["thinking"] == {"type": "adaptive"} and body["output_config"] == {"effort": "medium"}
    assert body["model"] == "claude-haiku-5-5" and body["max_tokens"] == 16000
    task = _task("positive")
    assert body["messages"][0]["content"] == build_user_message(task)
    assert task.prompt in body["messages"][0]["content"] and task.context in body["messages"][0]["content"]
    assert body["system"] == resolve_study_forensics_prompt(P8)
    assert "x-api-key" in {k.lower() for k in sent["headers"]}
    record = _record(result.path)
    assert record["execution_mode"] == "live_generation"
    agent = record["run_record"]["results"][0]["agent_result"]
    assert agent["phase8"]["technical_status"] == "completed" and agent["phase9"]
    ev = agent["execution_evidence"]
    assert ev["requested_model"] == ev["returned_model"] == "claude-haiku-5-5"
    assert ev["request_id"] == "req_t" and ev["completion_state"] == "complete"
    assert ev["content_block_types"] == ["thinking", "text"] and ev["thinking_block_count"] == 1
    assert ev["confirmed_cost_microusd"] == cost_microusd(PROFILES[HAIKU], ev["usage"]) == 2400
    controls = {c["control_id"]: c for c in _decision(result.path)["controls"]}
    assert controls["provenance"]["version"] == "live-1.0" and controls["provenance"]["outcome"] == "pass"
    assert LIVE_NOTICE in (Path(result.path) / "report.md").read_text()
    assert LIVE_NOTICE in (Path(result.path) / "report.html").read_text()
    assert NOTICE not in (Path(result.path) / "report.md").read_text()
    assert summary["reserved_or_confirmed_microusd"] == 2400
    capture = tmp_path / "auth" / "captures" / f"{ev['final_attempt_id']}.json"
    assert json.loads(capture.read_text())["call"]["response_body"]["content"][1]["text"] == _recording("positive")
    assert "test-key" not in capture.read_text()
    assert inspect_bundle(Path(result.path)).valid
    released = release_candidate(Path(result.path), output_root=tmp_path / "out",
                                 reviewer="Unit test (synthetic)", reason="Test-only local release")
    assert released.status == "RELEASED" and inspect_bundle(Path(released.path)).valid


# ---------------------------------------------------------------- L3 stop before sending


def test_L3_missing_or_altered_authorization_blocks_before_sending(tmp_path):
    with pytest.raises(FileNotFoundError):
        live.LiveSession(tmp_path / "none", mode="live", api_key="k")
    task = _task("positive")
    expired = _authorize(tmp_path / "expired", [task], expires=datetime.now(timezone.utc) - timedelta(seconds=1))
    with pytest.raises(ValueError, match="expired"):
        live.LiveSession(expired, mode="live", api_key="k")
    directory = _authorize(tmp_path / "auth", [task])
    data = json.loads((directory / "authorization.json").read_text())
    data["allowed_profiles"][HAIKU] = "0" * 64
    (directory / "authorization.json").write_text(json.dumps(data))
    with pytest.raises(ValueError, match="configuration revision"):
        live.LiveSession(directory, mode="live", api_key="k")


def test_L3_foreign_provider_profile_or_task_is_refused_without_network(tmp_path):
    task = _task("positive")
    directory = _authorize(tmp_path / "auth", [task], profiles=(HAIKU,))
    transport = Transport()
    with _session(directory, transport) as session:
        with pytest.raises(ValueError, match="not allowed"):
            live.LiveAuditProvider(session, SONNET, task.id, "primary", P8)

        class LookAlike(live.LiveAuditProvider):
            pass
        result = run_audit(task, LookAlike(session, HAIKU, task.id, "primary", P8), output_root=tmp_path / "o",
                           review_state=tmp_path / "s")
        assert result.status == "PREFLIGHT_BLOCKED" and result.path is None
        altered = task.model_copy(update={"context": task.context + " Altered."})
        result = run_audit(altered, live.LiveAuditProvider(session, HAIKU, task.id, "primary", P8),
                           output_root=tmp_path / "o", review_state=tmp_path / "s")
        assert result.status == "PREFLIGHT_BLOCKED" and "authorized case binding" in result.errors[0]
    assert transport.requests == []


def test_L3_insufficient_budget_stops_before_sending(tmp_path):
    task = _task("positive")
    directory = _authorize(tmp_path / "auth", [task], budget=5_000, ceiling=5_000)
    transport = Transport(message(_recording("positive")))
    result, summary, _ = _live_run(tmp_path, "positive", transport, directory=directory)
    assert result.status == "PREFLIGHT_BLOCKED" and "Insufficient remaining budget" in result.errors[0]
    assert transport.requests == [] and summary["attempts"] == 0


# ---------------------------------------------------------------- L4 response shapes


def test_L4_content_blocks_refusal_truncation_and_missing_text():
    text_after = interpret_message({"model": "m", "stop_reason": "end_turn", "content": [
        {"type": "thinking", "thinking": "", "signature": "s"}, {"type": "text", "text": "{\"a\":"},
        {"type": "text", "text": "1}"}], "usage": {}})
    assert text_after["final_text"] == "{\"a\":1}" and text_after["completion_state"] == "complete"
    assert interpret_message({"stop_reason": "refusal", "content": []})["completion_state"] == "refusal"
    assert interpret_message({"stop_reason": "max_tokens", "content": [
        {"type": "text", "text": "{"}]})["completion_state"] == "truncated"
    assert interpret_message({"stop_reason": "end_turn", "content": [
        {"type": "thinking", "thinking": "only thinking", "signature": "s"}]})["completion_state"] == "no_final_text"
    assert interpret_message({"stop_reason": "pause_turn", "content": [
        {"type": "text", "text": "x"}]})["completion_state"] == "unexpected_stop_reason"


@pytest.mark.parametrize(("response", "state", "statuses"), [
    (message(_recording("positive")[:500], stop="max_tokens"), "truncated", {"ANALYSIS_INCOMPLETE", "RUN_FAILED"}),
    (message("", stop="refusal", blocks=[]), "refusal", {"RUN_FAILED"}),
    (message("", blocks=[{"type": "thinking", "thinking": "", "signature": "s"}]), "no_final_text", {"RUN_FAILED"}),
])
def test_L4_unusable_live_output_is_an_explicit_state_not_a_pass(tmp_path, response, state, statuses):
    result, _, _ = _live_run(tmp_path, "positive", Transport(response))
    assert result.status in statuses
    record = _record(result.path)
    ev = record["run_record"]["results"][0]["agent_result"]["execution_evidence"]
    assert ev["completion_state"] == state
    assert inspect_bundle(Path(result.path)).valid


# ---------------------------------------------------------------- L5 provenance manipulation


def test_L5_tampered_or_relabelled_live_provenance_is_detected(tmp_path):
    result, _, _ = _live_run(tmp_path, "positive", Transport(message(_recording("positive"))))
    path = Path(result.path)
    original = (path / "record.json").read_bytes()
    record = json.loads(original)
    record["run_record"]["results"][0]["agent_result"]["execution_evidence"]["returned_model"] = "claude-opus-5-5"
    (path / "record.json").write_text(json.dumps(record))
    assert not inspect_bundle(path).valid
    (path / "record.json").write_bytes(original)
    assert inspect_bundle(path).valid

    run = RunRecord.model_validate(json.loads(original)["run_record"])
    relabelled = run.model_copy(deep=True)
    agent = relabelled.results[0].agent_result
    agent.execution_evidence = None  # live output without its evidence
    blocked = create_candidate(relabelled, output_root=tmp_path / "relabel")
    assert blocked.status == "PREFLIGHT_BLOCKED" and "mixed, unknown or unbound" in blocked.errors[0]
    forged = relabelled.model_copy(deep=True)
    forged.results[0].agent_result.execution_evidence = dict(run.results[0].agent_result.execution_evidence,
                                                              request_id=None)
    blocked = create_candidate(forged, output_root=tmp_path / "forged")
    assert blocked.status == "PREFLIGHT_BLOCKED" and "request ID missing" in blocked.errors[0]


def test_L5_mixed_offline_and_live_carriers_are_never_unified(tmp_path):
    live_result, _, _ = _live_run(tmp_path, "positive", Transport(message(_recording("positive"))))
    offline = run_audit(_task("positive"), OfflineReviewProvider(_recording("positive")), output_root=tmp_path / "off")
    live_run = RunRecord.model_validate(_record(live_result.path)["run_record"])
    offline_run = RunRecord.model_validate(_record(offline.path)["run_record"])
    mixed = live_run.model_copy(update={"results": live_run.results + offline_run.results})
    blocked = create_candidate(mixed, output_root=tmp_path / "mixed")
    assert blocked.status == "PREFLIGHT_BLOCKED" and "mixed" in blocked.errors[0]


def test_L5_altered_authorization_or_capture_breaks_resume_and_replay(tmp_path):
    result, _, _ = _live_run(tmp_path, "positive", Transport(message(_recording("positive"))))
    directory = tmp_path / "auth"
    capture = next((directory / "captures").glob("*.json"))
    data = json.loads(capture.read_text())
    data["call"]["response_body"]["content"][1]["text"] += " "
    capture.write_text(json.dumps(data))
    task = _task("positive")
    with live.LiveSession(directory, mode="replay") as session:
        provider = live.ReplayProvider(session, HAIKU, task.id, "primary", P8)
        replay = run_audit(task, provider, output_root=tmp_path / "r", review_state=tmp_path / "rs")
    assert replay.status != "READY_FOR_RELEASE"
    auth = json.loads((directory / "authorization.json").read_text())
    auth["work_order"] = "changed after use"
    (directory / "authorization.json").write_text(json.dumps(auth))
    with pytest.raises(MissionError, match="binding mismatch"):
        live.LiveSession(directory, mode="live", api_key="k")


# ---------------------------------------------------------------- L6 mandatory controls


def test_L6_live_registry_is_complete_and_an_unbound_carrier_fails_provenance(tmp_path):
    assert set(LIVE_REGISTRY) == set(REGISTRY) and LIVE_REGISTRY["provenance"] == "live-1.0"
    assert registry_fingerprint("live_generation") != registry_fingerprint()
    result, _, _ = _live_run(tmp_path, "positive", Transport(message(_recording("positive"))))
    decision = _decision(result.path)
    assert len(decision["controls"]) == len(LIVE_REGISTRY)
    assert all(c["execution"] == "executed" for c in decision["controls"])
    path = Path(result.path)
    trimmed = dict(decision, controls=[c for c in decision["controls"] if c["control_id"] != "provenance"])
    (path / "decision.json").write_text(json.dumps(trimmed))
    assert not inspect_bundle(path).valid


# ---------------------------------------------------------------- L7 Phase9


def test_L7_counterreview_runs_live_on_trigger_and_noop_stability_generates_nothing(tmp_path):
    unknown = _recording("unknown")
    transport = Transport(message(unknown, request_id="req_p"), message(unknown, request_id="req_c"))
    result, summary, _ = _live_run(tmp_path, "unknown", transport)
    assert len(transport.requests) == 2
    assert result.status == "REVIEW_REQUIRED"
    phase9 = _record(result.path)["run_record"]["metadata"]["phase9"]
    kinds = {a["kind"]: a["status"] for a in phase9["attempts"]}
    # One evidence item: reversing it is a no-op, recorded and never sampled (AA-P9 rule 7).
    assert kinds == {"counterreview": "completed", "stability": "rejected"}
    assert sorted(p["origin"] for p in phase9["positions"]) == ["model_review", "original"]
    review = transport.requests[1]["body"]
    assert review["system"] == resolve_study_forensics_prompt(STUDY_FORENSICS_PROMPT_VERSION_PHASE9)
    assert "Bound evidence packet" in review["messages"][0]["content"]
    assert summary["attempts"] == 2
    assert inspect_bundle(Path(result.path)).valid
    controls = {c["control_id"]: c for c in _decision(result.path)["controls"]}
    assert controls["provenance"]["outcome"] == "pass"
    again = Transport(message(unknown))
    repeat, _, _ = _live_run(tmp_path, "unknown", again, directory=tmp_path / "auth")
    assert repeat.status == "PREFLIGHT_BLOCKED" and "never resent" in repeat.errors[0]
    assert again.requests == []


def _two_evidence_unknown():
    task = _task("unknown")
    extra = "A second randomized comparison in adults (human) reported a similar reduction of event Q."
    task = task.model_copy(update={"id": "phase10-live-two-evidence", "context": task.context + " " + extra})
    data = json.loads(_recording("unknown"))
    record = data["forensic_record"]
    record["evidence"].append(dict(record["evidence"][0], evidence_id="e2", exact_reference=extra, text=extra))
    for proposition in record["phase8"]["propositions"]:
        proposition["evidence_bindings"].append(dict(proposition["evidence_bindings"][0], binding_id="b2",
                                                     evidence_id="e2"))
    description = dict(record["phase8"]["evidence_descriptions"][0], evidence_id="e2",
                       study_id="synthetic-second-study")
    record["phase8"]["evidence_descriptions"].append(description)
    for finding in record["findings"]:
        finding["supporting_evidence_ids"].append("e2")
    for finding in record["client_findings"]:
        finding["referenced_evidence_ids"].append("e2")
    return task, json.dumps(data)


def test_L7_stability_variant_is_generated_live_when_the_reversal_is_real(tmp_path):
    task, raw = _two_evidence_unknown()
    directory = _authorize(tmp_path / "auth", [task])
    transport = Transport(message(raw, request_id="req_p"), message(raw, request_id="req_c"),
                          message(raw, request_id="req_s"))
    with _session(directory, transport) as session:
        provider = live.LiveAuditProvider(session, HAIKU, task.id, "primary", P8)
        result = run_audit(task, provider, output_root=tmp_path / "out", review_state=directory / "phase9-state")
        summary = session.summary()
    assert len(transport.requests) == 3 and summary["attempts"] == 3
    phase9 = _record(result.path)["run_record"]["metadata"]["phase9"]
    assert {a["kind"]: a["status"] for a in phase9["attempts"]} == {"counterreview": "completed",
                                                                     "stability": "completed"}
    assert sorted(p["origin"] for p in phase9["positions"]) == ["model_review", "original", "stability"]
    counter, stability = (json.loads(r["body"]["messages"][0]["content"].split("Bound evidence packet:\n", 1)[1]
                                     .rsplit("\n</task_context>", 1)[0]) for r in transport.requests[1:])
    assert stability["evidence"] == list(reversed(counter["evidence"]))
    assert result.status == "REVIEW_REQUIRED" and inspect_bundle(Path(result.path)).valid


def test_L7_auto_resolvable_case_uses_no_review_call(tmp_path):
    transport = Transport(message(_recording("negative")))
    result, summary, _ = _live_run(tmp_path, "negative", transport)
    assert len(transport.requests) == 1 and summary["attempts"] == 1
    assert result.status == "READY_FOR_RELEASE"
    phase9 = _record(result.path)["run_record"]["metadata"].get("phase9") or {}
    assert not phase9.get("attempts")


# ---------------------------------------------------------------- L8 errors, retries, crash


def test_L8_transient_failure_retries_once_with_a_separate_reservation(tmp_path):
    overloaded = httpx.Response(529, json={"type": "error", "error": {"type": "overloaded_error"}},
                                headers={"request-id": "req_fail"})
    transport = Transport(overloaded, message(_recording("positive")))
    result, summary, provider = _live_run(tmp_path, "positive", transport)
    assert result.status == "READY_FOR_RELEASE" and provider.network_attempts == 2
    ledger = json.loads((tmp_path / "auth" / "ledger.json").read_text())
    first, second = ledger["attempts"]
    assert first["state"] == "FAILED_TRANSIENT" and first["billing"] == "unknown_reservation_kept"
    assert first["bound_microusd"] == first["reserved_microusd"] > 0
    assert second["retry_of"] == first["attempt_id"] and second["state"] == "COMPLETED"
    assert summary["reserved_or_confirmed_microusd"] == first["reserved_microusd"] + 2400
    ev = _record(result.path)["run_record"]["results"][0]["agent_result"]["execution_evidence"]
    assert ev["attempt_ids"] == [first["attempt_id"], second["attempt_id"]]


def test_L8_timeout_keeps_reservation_and_second_failure_is_final(tmp_path):
    transport = Transport(httpx.ReadTimeout("timed out"), httpx.ReadTimeout("timed out"))
    result, summary, provider = _live_run(tmp_path, "positive", transport)
    assert provider.network_attempts == 2 and result.status == "RUN_FAILED"
    ledger = json.loads((tmp_path / "auth" / "ledger.json").read_text())
    assert all(a["billing"] == "unknown_reservation_kept" for a in ledger["attempts"])
    assert summary["reserved_or_confirmed_microusd"] == sum(a["reserved_microusd"] for a in ledger["attempts"])


def test_L8_retry_cap_parallel_lease_and_interrupted_reservation(tmp_path):
    task = _task("positive")
    directory = _authorize(tmp_path / "auth", [task], retries=0)
    overloaded = httpx.Response(529, json={"type": "error", "error": {"type": "overloaded_error"}})
    transport = Transport(overloaded)
    result, _, provider = _live_run(tmp_path, "positive", transport, directory=directory)
    assert provider.network_attempts == 1 and result.status == "RUN_FAILED"
    ev = _record(result.path)["run_record"]["results"][0]["agent_result"]["execution_evidence"]
    assert "retry cap" in ev["retry_denied"]

    second = _authorize(tmp_path / "auth2", [task])
    with _session(second, Transport()):
        with pytest.raises(ValueError, match="parallel execution refused"):
            live.LiveSession(second, mode="live", api_key="k")
    with _session(second, Transport()) as session:
        slot = live.slot_key(task.id, HAIKU, "primary")
        session.ledger.reserve(slot, "p", "w", microusd=10_000)  # crash before any capture
    with _session(second, Transport()) as session:
        assert session.unresolved == ["attempt-001"]
        provider = live.LiveAuditProvider(session, HAIKU, task.id, "primary", P8)
        assert "unresolved reservation" in provider.preflight(task)
        assert session.summary()["reserved_or_confirmed_microusd"] == 10_000


def test_L8_capture_persisted_before_crash_is_settled_on_resume(tmp_path):
    task = _task("positive")
    directory = _authorize(tmp_path / "auth", [task])
    with _session(directory, Transport()) as session:
        slot = live.slot_key(task.id, HAIKU, "primary")
        system = resolve_study_forensics_prompt(P8)
        exposure, basis = max_exposure_microusd(PROFILES[HAIKU], system, build_user_message(task))
        aid = session.ledger.reserve(slot, "p", "w", microusd=exposure)
        body = json.loads(message(_recording("positive")).content)
        call = {"request_sent": True, "http_status": 200, "request_id": "req_x", "response_body": body,
                "billing": "usage_reported", "request_sha256": "x"}
        from agent_arena.bounded_harness_mission import atomic
        atomic(session.capture_path(aid), {"profile_id": HAIKU, "call": call, "attempt_id": aid, "slot_key": slot,
                                           "authorization_id": "TEST-LIVE-AUTH"})
    with _session(directory, Transport()) as session:
        attempt = session.ledger.data["attempts"][0]
        assert attempt["state"] == "COMPLETED" and attempt["reconciled_after_interruption"] is True
        assert attempt["bound_microusd"] == 2400 and session.unresolved == []


def test_L8_ledger_never_exceeds_total_and_settlement_is_single(tmp_path):
    task = _task("positive")
    directory = _authorize(tmp_path / "auth", [task], budget=30_000, ceiling=20_000)
    with _session(directory, Transport()) as session:
        ledger = session.ledger
        primary = live.slot_key(task.id, HAIKU, "primary")
        review = live.slot_key(task.id, HAIKU, "counterreview")
        aid = ledger.reserve(primary, "p", "w", microusd=20_000)
        with pytest.raises(MissionError, match="dollar cap"):
            ledger.reserve(review, "p", "w", microusd=20_000)
        ledger.settle(aid, state="COMPLETED", confirmed_microusd=1_000)
        with pytest.raises(MissionError, match="already settled"):
            ledger.settle(aid, state="COMPLETED", confirmed_microusd=1_000)
        ledger.reserve(review, "p", "w", microusd=20_000)
        assert ledger.data["reserved_microusd"] == 21_000 <= 30_000


# ---------------------------------------------------------------- L9 reports


def test_L9_positive_and_negative_live_reports_pass_open_review_blocks(tmp_path):
    positive, _, _ = _live_run(tmp_path / "p", "positive", Transport(message(_recording("positive"))))
    negative, _, _ = _live_run(tmp_path / "n", "negative", Transport(message(_recording("negative"))))
    assert positive.status == negative.status == "READY_FOR_RELEASE"
    unknown = _recording("unknown")
    blocked, _, _ = _live_run(tmp_path / "u", "unknown", Transport(message(unknown), message(unknown)))
    assert blocked.status == "REVIEW_REQUIRED"
    refused = release_candidate(Path(blocked.path), output_root=tmp_path / "u",
                                reviewer="Unit test", reason="must not waive open review")
    assert refused.status == "RELEASE_BLOCKED"


def test_sonnet_profile_omits_sampling_and_prices_its_exposure(tmp_path):
    task = _task("positive")
    system = resolve_study_forensics_prompt(P8)
    sonnet, basis = max_exposure_microusd(PROFILES[SONNET], system, build_user_message(task))
    haiku, _ = max_exposure_microusd(PROFILES[HAIKU], system, build_user_message(task))
    assert sonnet > haiku > 0 and basis["cache_discount_assumed"] is False
    transport = Transport(message(_recording("positive"), model="claude-sonnet-5-5"))
    result, _, _ = _live_run(tmp_path, "positive", transport, profile=SONNET)
    assert result.status == "READY_FOR_RELEASE"
    body = transport.requests[0]["body"]
    assert body["model"] == "claude-sonnet-5-5" and not {"temperature", "top_p", "top_k"} & set(body)
    mismatch = Transport(message(_recording("positive"), model="claude-haiku-5-5"))
    other, _, _ = _live_run(tmp_path / "m", "positive", mismatch, profile=SONNET)
    assert other.status == "PREFLIGHT_BLOCKED" and "returned model differs" in other.errors[0]


# ---------------------------------------------------------------- critic round 1 corrections


def test_M1_review_carrier_from_another_case_cannot_pass_provenance(tmp_path):
    result, _, _ = _live_run(tmp_path, "unknown", Transport(message(_recording("unknown")),
                                                            message(_recording("unknown"))))
    record = _record(result.path)
    run = RunRecord.model_validate(record["run_record"])
    review = record["run_record"]["metadata"]["phase9"]
    assert live.execution_mode(run, review) == ("live_generation", [])
    foreign = json.loads(json.dumps(review))
    position = next(p for p in foreign["positions"] if p["origin"] == "model_review")
    evidence = position["agent_result"]["execution_evidence"]
    evidence["task_id"] = "another-case"
    evidence["slot_key"] = live.slot_key("another-case", HAIKU, "counterreview")
    mode, errors = live.execution_mode(run, foreign)
    assert mode is None and any("another case" in e for e in errors)
    evidence.update(task_id=run.task.id, slot_key=live.slot_key(run.task.id, SONNET, "counterreview"),
                    profile_id=SONNET)
    mode, errors = live.execution_mode(run, foreign)
    assert mode is None and any("mix model profiles" in e or "registered profile" in e for e in errors)


def test_M2_copied_authorization_lost_ledger_and_capture_overwrite_are_refused(tmp_path):
    task = _task("positive")
    directory = _authorize(tmp_path / "auth", [task])
    copy = tmp_path / "copy"
    copy.mkdir()
    (copy / "authorization.json").write_bytes((directory / "authorization.json").read_bytes())
    with pytest.raises(ValueError, match="bound to another directory"):
        live.LiveSession(copy, mode="live", api_key="k")
    _live_run(tmp_path, "positive", Transport(message(_recording("positive"))), directory=directory)
    (directory / "ledger.json").unlink()
    with pytest.raises(MissionError, match="fresh budget is never created"):
        live.LiveSession(directory, mode="live", api_key="k")


def test_M2_existing_capture_is_never_overwritten(tmp_path):
    task = _task("positive")
    directory = _authorize(tmp_path / "auth", [task])
    (directory / "captures").mkdir(parents=True)
    with _session(directory, Transport(message(_recording("positive")))) as session:
        (directory / "captures" / "attempt-001.json").write_text("{}")
        provider = live.LiveAuditProvider(session, HAIKU, task.id, "primary", P8)
        transport_used = provider.network_attempts
        with pytest.raises(MissionError, match="never overwritten"):
            provider.generate(task, resolve_study_forensics_prompt(P8))
        assert provider.network_attempts == transport_used == 0  # refused before sending
        assert session.ledger.data["attempts"][0]["state"] == "RESERVED_POSSIBLY_BILLABLE"
    assert (directory / "captures" / "attempt-001.json").read_text() == "{}"


def test_round2_foreign_capture_does_not_settle_and_interrupted_retry_resumes(tmp_path):
    task = _task("positive")
    directory = _authorize(tmp_path / "auth", [task])
    slot = live.slot_key(task.id, HAIKU, "primary")
    with _session(directory, Transport()) as session:
        aid = session.ledger.reserve(slot, "p", "w", microusd=10_000)
        from agent_arena.bounded_harness_mission import atomic
        atomic(session.capture_path(aid), {"profile_id": HAIKU, "attempt_id": aid, "slot_key": "other|slot|primary",
                                           "authorization_id": "TEST-LIVE-AUTH", "call": {"http_status": 200}})
    with _session(directory, Transport()) as session:
        assert session.unresolved == [aid]
        assert session.ledger.data["attempts"][0]["state"] == "RESERVED_POSSIBLY_BILLABLE"

    second = _authorize(tmp_path / "auth2", [task])
    with _session(second, Transport()) as session:
        first = session.ledger.reserve(slot, "p", "w", microusd=10_000)
        session.ledger.settle(first, state="FAILED_TRANSIENT")  # crash before the retry was reserved
    transport = Transport(message(_recording("positive")))
    result, summary, provider = _live_run(tmp_path, "positive", transport, directory=second)
    assert result.status == "READY_FOR_RELEASE" and provider.network_attempts == 1
    attempts = json.loads((second / "ledger.json").read_text())["attempts"]
    assert [a["retry_of"] for a in attempts] == [None, first] and summary["attempts"] == 2


def test_refusal_with_partial_text_is_a_clean_failure_with_valid_provenance(tmp_path):
    response = message("partial words", stop="refusal")
    result, _, _ = _live_run(tmp_path, "positive", Transport(response))
    assert result.status == "RUN_FAILED" and result.path
    ev = _record(result.path)["run_record"]["results"][0]["agent_result"]["execution_evidence"]
    assert ev["completion_state"] == "refusal"
    assert ev["capture_final_text_sha256"] != ev["final_text_sha256"]
    controls = {c["control_id"]: c for c in _decision(result.path)["controls"]}
    assert controls["provenance"]["outcome"] == "pass"


def test_missing_credential_reserves_and_sends_nothing(tmp_path, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    task = _task("positive")
    directory = _authorize(tmp_path / "auth", [task])
    transport = Transport(message(_recording("positive")))
    with live.LiveSession(directory, mode="live", transport=transport.mock()) as session:
        provider = live.LiveAuditProvider(session, HAIKU, task.id, "primary", P8)
        result = run_audit(task, provider, output_root=tmp_path / "o", review_state=directory / "s")
        assert result.status == "PREFLIGHT_BLOCKED" and "ANTHROPIC_API_KEY" in result.errors[0]
        assert session.ledger.data["attempts"] == []
    assert transport.requests == []


def test_environment_cannot_redirect_the_live_endpoint(tmp_path, monkeypatch):
    seen = {}
    original = httpx.Client.__init__

    def spy(self, *args, **kwargs):
        seen.update(kwargs)
        original(self, *args, **kwargs)
    monkeypatch.setattr(httpx.Client, "__init__", spy)
    monkeypatch.setenv("HTTPS_PROXY", "http://127.0.0.1:9")
    monkeypatch.setenv("ANTHROPIC_BASE_URL", "http://127.0.0.1:9")
    transport = Transport(message(_recording("positive")))
    result, _, _ = _live_run(tmp_path, "positive", transport)
    assert result.status == "READY_FOR_RELEASE"
    assert seen["trust_env"] is False and transport.requests[0]["url"] == "https://api.anthropic.com/v1/messages"


def test_crash_between_settlement_and_terminal_is_completed_on_resume(tmp_path):
    task = _task("positive")
    directory = _authorize(tmp_path / "auth", [task])
    _live_run(tmp_path, "positive", Transport(message(_recording("positive"))), directory=directory)
    ledger = json.loads((directory / "ledger.json").read_text())
    ledger["terminal_keys"] = []
    ledger.pop("terminal_record_hashes")
    (directory / "ledger.json").write_text(json.dumps(ledger, indent=2))
    with _session(directory, Transport()) as session:
        assert live.slot_key(task.id, HAIKU, "primary") in session.ledger.data["terminal_keys"]
        provider = live.LiveAuditProvider(session, HAIKU, task.id, "primary", P8)
        assert "never resent" in provider.preflight(task)


def test_cli_modes_and_replay_end_to_end(tmp_path, monkeypatch):
    from click.testing import CliRunner
    from agent_arena.phase10_cli import audit
    runner = CliRunner()
    task_file = str(EXAMPLES / "positive-task.json")
    both = runner.invoke(audit, ["run", "--offline", "--live", "--task", task_file, "--output-root", str(tmp_path)])
    assert both.exit_code == 2 and "exactly one" in both.output
    no_dir = runner.invoke(audit, ["run", "--live", "--task", task_file, "--output-root", str(tmp_path)])
    assert no_dir.exit_code == 2
    missing = runner.invoke(audit, ["run", "--live", "--task", task_file, "--authorization-dir",
                                    str(tmp_path / "nothing"), "--profile", HAIKU, "--output-root", str(tmp_path)])
    assert missing.exit_code == 2 and "PREFLIGHT_BLOCKED" in missing.output
    _live_run(tmp_path, "positive", Transport(message(_recording("positive"))))

    def forbid(*_args, **_kwargs):
        raise AssertionError("network access attempted during CLI replay")
    monkeypatch.setattr(httpx.Client, "send", forbid)
    replay = runner.invoke(audit, ["run", "--replay", "--task", task_file, "--authorization-dir",
                                   str(tmp_path / "auth"), "--profile", HAIKU, "--output-root",
                                   str(tmp_path / "cli-replay")])
    assert replay.exit_code == 0, replay.output
    payload = json.loads(replay.output)
    assert payload["status"] == "READY_FOR_RELEASE"
    assert _record(payload["path"])["execution_mode"] == "offline_replay_of_live"


# ---------------------------------------------------------------- R1 repair revision (P8 contract)

HAIKU2, SONNET2 = "claude-haiku-5-5@2", "claude-sonnet-5-5@2"
P9 = STUDY_FORENSICS_PROMPT_VERSION_PHASE9
R1 = "study_forensics_prompt/v3-phase8-contract-r1"
R1_REVIEW = "study_forensics_prompt/v3-phase8-contract-r1-review-p9-1"
FROZEN_PROMPT_SHA256 = {
    "study_forensics_prompt/v1-historical-phase7": "f7704fa50a7689ae56f8fc6d7a383205a5aca34d0c400be36335d6ad8abfcfd5",
    "study_forensics_prompt/v2-taxonomy-aligned-phase5a":
        "37d91b813bee2b4febb9dba5da66fa8e2bda1e091989785adf6ca5acc132b7ef",
    P8: "4399b8eb743e951ad4c38ec26d4125ecabc19da880b748d2949af04ec5bb2063",
    P9: "1335ee48ff21b5d5cd42db5663163526b6ec352214788990625357f669c494ca",
    R1: "8f4642eb278ee149cbffc4134ec0cc797a6135f2d91016724b46447115287fa0",
    R1_REVIEW: "afee61e6fea6e8bb9609724a8363503ecce29f555c9399a3483cfcb0e2d37eea",
}
FROZEN_PROFILE_FINGERPRINTS = {
    HAIKU: "22055d66faee28c9df55fbebb95a053d505aa2e8799b5f092790b0e8c370e82d",
    SONNET: "c0231e6c5148e2d4eaeec08e969623e6bfec68bee6a8939a16fc5167c89f26a7",
    HAIKU2: "14db974ae1cda492ac33fa9f63e2f9347382d2ecd01b5453a16f5ae6167f433e",
    SONNET2: "afda15e9afdb1e59281935e6b06ecfbefb81a5e4ce11e4157e913f0483641fcb",
}


def _appendix() -> str:
    return resolve_study_forensics_prompt(R1)[len(resolve_study_forensics_prompt(P8)) + 1:]


def test_R1_prompt_bytes_profile_fingerprints_and_bindings_are_frozen():
    import hashlib
    from dataclasses import fields
    from agent_arena.providers.anthropic_live import LiveProfile
    from agent_arena.runner import (
        STUDY_FORENSICS_PROMPT_VERSION_PHASE8_CONTRACT_R1, STUDY_FORENSICS_PROMPT_VERSION_PHASE9_CONTRACT_R1,
    )
    assert (STUDY_FORENSICS_PROMPT_VERSION_PHASE8_CONTRACT_R1, STUDY_FORENSICS_PROMPT_VERSION_PHASE9_CONTRACT_R1) \
        == (R1, R1_REVIEW)
    for version, digest in FROZEN_PROMPT_SHA256.items():
        assert hashlib.sha256(resolve_study_forensics_prompt(version).encode()).hexdigest() == digest, version
    assert {pid: PROFILES[pid].fingerprint() for pid in FROZEN_PROFILE_FINGERPRINTS} == FROZEN_PROFILE_FINGERPRINTS
    p8, p9, r1 = (resolve_study_forensics_prompt(v) for v in (P8, P9, R1))
    assert r1 == p8 + "\n" + _appendix()  # the historical bytes are an unchanged prefix
    assert resolve_study_forensics_prompt(R1_REVIEW) == r1 + p9[len(p8):]  # identical Phase9 suffix
    assert PROFILES[HAIKU].prompt_versions == PROFILES[SONNET].prompt_versions == (P8, P9)
    assert PROFILES[HAIKU2].prompt_versions == PROFILES[SONNET2].prompt_versions == (R1, R1_REVIEW)

    def changed(old, new):
        return {f.name for f in fields(LiveProfile) if getattr(PROFILES[old], f.name) != getattr(PROFILES[new], f.name)}
    assert changed(HAIKU, HAIKU2) == {"profile_id", "max_tokens", "prompt_binding", "rationale"}
    assert changed(SONNET, SONNET2) == {"profile_id", "prompt_binding", "rationale"}
    assert PROFILES[HAIKU2].max_tokens == 32000 and PROFILES[SONNET2].max_tokens == 16000


def test_R1_contract_states_every_validator_vocabulary_and_no_case_content():
    from typing import get_args
    from agent_arena.phase8_models import Directness, Observation, SemanticAttributes
    from agent_arena.phase8_semantics import CORE_DIMENSIONS, PRODUCT_DIMENSIONS, RELATIONS
    from agent_arena.phase8_taxonomy import CAUSAL_RELATIONS, CLINICAL_ENDPOINTS
    from agent_arena.schemas import ASSERTION_SCOPES, SUMMARY_STRENGTH_ORDER, VALUE_ORIGINS, EvidenceRole
    appendix = _appendix()
    vocabulary = [*SemanticAttributes.model_fields, *CORE_DIMENSIONS, *PRODUCT_DIMENSIONS, *RELATIONS,
                  *CAUSAL_RELATIONS, *CLINICAL_ENDPOINTS, *VALUE_ORIGINS, *ASSERTION_SCOPES,
                  *SUMMARY_STRENGTH_ORDER, *get_args(Directness), *get_args(Observation),
                  *(role.value for role in EvidenceRole)]
    assert [value for value in vocabulary if value not in appendix] == []
    # Every rule class that failed in the @1 live smoke is stated explicitly.
    for rule in ("from_proposition_ids", "negative_assertions", "identification_argument", "value_origin",
                 "material_dimensions", "not_applicable", "client_scope", "original_span.text",
                 "required_proposition_ids", "product_transfers", "premise_proposition_id", "trigger_quote",
                 "referenced_evidence_ids", "Do not put\nfinal_answer", "do not wrap it"):
        assert rule in appendix, rule
    # Disclosure only: no final labels, no case text, no expected answer.
    for label in ("solid", "overclaim", "correlation_vs_causation", "mechanism_vs_evidence"):
        assert label not in appendix
    for name in ("positive", "negative", "unknown"):
        task = _task(name)
        assert task.prompt not in appendix and task.context not in appendix


def _r1_run(tmp_path, name, transport, *, profile=HAIKU2, directory=None):
    task = _task(name)
    directory = directory or _authorize(tmp_path / "auth", [task], profiles=(profile,), ceiling=300_000)
    with _session(directory, transport) as session:
        provider = live.LiveAuditProvider(session, profile, task.id, "primary", PROFILES[profile].prompt_versions[0])
        result = run_audit(task, provider, output_root=tmp_path / "out", review_state=directory / "phase9-state")
        return result, session.summary()


def test_R1_profile_sends_its_bound_prompt_for_primary_and_live_review(tmp_path):
    unknown = _recording("unknown")
    transport = Transport(message(unknown, request_id="req_p"), message(unknown, request_id="req_c"))
    result, summary = _r1_run(tmp_path, "unknown", transport)
    assert len(transport.requests) == 2 and summary["attempts"] == 2
    primary, review = (request["body"] for request in transport.requests)
    assert primary["system"] == resolve_study_forensics_prompt(R1)
    assert primary["max_tokens"] == 32000 and primary["output_config"] == {"effort": "medium"}
    assert review["system"] == resolve_study_forensics_prompt(R1_REVIEW)
    record = _record(result.path)
    evidence = record["run_record"]["results"][0]["agent_result"]["execution_evidence"]
    assert (evidence["profile_id"], evidence["system_prompt_version"]) == (HAIKU2, R1)
    reviewed = [p for p in record["run_record"]["metadata"]["phase9"]["positions"] if p["origin"] == "model_review"]
    assert reviewed[0]["agent_result"]["execution_evidence"]["system_prompt_version"] == R1_REVIEW
    assert result.status == "REVIEW_REQUIRED" and inspect_bundle(Path(result.path)).valid
    controls = {c["control_id"]: c for c in _decision(result.path)["controls"]}
    assert controls["provenance"]["outcome"] == "pass"


def test_R1_prompt_and_profile_revisions_cannot_be_mixed(tmp_path):
    task = _task("positive")
    directory = _authorize(tmp_path / "auth", [task], profiles=(HAIKU, HAIKU2))
    with _session(directory, Transport()) as session:
        for profile, kind, version in ((HAIKU, "primary", R1), (HAIKU2, "primary", P8), (HAIKU2, "primary", R1_REVIEW),
                                       (HAIKU2, "counterreview", R1), (HAIKU, "counterreview", R1_REVIEW)):
            with pytest.raises(ValueError, match="bound to this profile revision"):
                live.LiveAuditProvider(session, profile, task.id, kind, version)


def test_R1_carrier_claiming_a_foreign_prompt_version_fails_provenance(tmp_path):
    result, _ = _r1_run(tmp_path, "positive", Transport(message(_recording("positive"))))
    assert result.status == "READY_FOR_RELEASE", result.errors
    record = RunRecord.model_validate(_record(result.path)["run_record"])
    assert live.execution_mode(record, {}) == ("live_generation", [])
    carrier = record.results[0].agent_result.model_dump(mode="json")
    forged = json.loads(json.dumps(carrier))
    forged["execution_evidence"].update(system_prompt_version=P8, system_prompt_sha256=FROZEN_PROMPT_SHA256[P8])
    assert "system prompt is not the version bound to this profile revision" in live.validate_live_carrier(
        forged, expected_kind="primary", task=record.task)
    forged_result = record.results[0].model_copy(update={"agent_result": record.results[0].agent_result.model_copy(
        update={"execution_evidence": forged["execution_evidence"]})})
    mode, errors = live.execution_mode(record.model_copy(update={"results": [forged_result]}), {})
    assert mode is None and any("system prompt" in error for error in errors)


def test_R1_replay_survives_authorization_expiry_while_live_is_refused(tmp_path):
    task = _task("positive")
    directory = _authorize(tmp_path / "auth", [task])
    _live_run(tmp_path, "positive", Transport(message(_recording("positive"))), directory=directory)
    later = datetime.now(timezone.utc) + timedelta(days=30)
    with pytest.raises(ValueError, match="expired"):
        live.LiveSession(directory, mode="live", now=later)
    ledger_bytes = (directory / "ledger.json").read_bytes()
    with live.LiveSession(directory, mode="replay", now=later) as session:
        provider = live.ReplayProvider(session, HAIKU, task.id, "primary", P8)
        replay = run_audit(task, provider, output_root=tmp_path / "replay", review_state=tmp_path / "rs")
    assert replay.status == "READY_FOR_RELEASE" and inspect_bundle(Path(replay.path)).valid
    assert (directory / "ledger.json").read_bytes() == ledger_bytes  # replay never writes the ledger


def test_R1_closing_an_authorization_for_its_successor_leaves_no_parallel_budget(tmp_path):
    task = _task("positive")
    directory = _authorize(tmp_path / "auth", [task])
    _live_run(tmp_path, "positive", Transport(message(_recording("positive"))), directory=directory)
    summary = live.close_for_successor(directory, successor_id="TEST-SUCCESSOR", reason="unit test")
    assert summary["ledger_state"] == "REVOKED" and summary["executable_remaining_microusd"] == 0
    assert summary["attempts"] == 1 and summary["technical_retries"] == 0
    assert summary["unknown_billing_attempts"] == [] and summary["reserved_or_confirmed_microusd"] > 0
    ledger = json.loads((directory / "ledger.json").read_text())
    assert ledger["revocation_reason"].startswith("CLOSED_SUPERSEDED by TEST-SUCCESSOR")
    transport = Transport(message(_recording("positive")))
    with _session(directory, transport) as session:
        provider = live.LiveAuditProvider(session, SONNET, task.id, "primary", P8)
        assert provider.preflight(task) == "Live ledger is not ACTIVE"
        assert provider.generate(task, resolve_study_forensics_prompt(P8)).error_type == "live_denied"
    assert transport.requests == []
    with pytest.raises(MissionError, match="not ACTIVE"):
        live.close_for_successor(directory, successor_id="AGAIN", reason="twice")
    with live.LiveSession(directory, mode="replay") as session:
        replay = run_audit(task, live.ReplayProvider(session, HAIKU, task.id, "primary", P8),
                           output_root=tmp_path / "replay", review_state=tmp_path / "rs")
    assert replay.status == "READY_FOR_RELEASE"


def test_R1_close_is_refused_while_a_reservation_is_unresolved(tmp_path):
    task = _task("positive")
    directory = _authorize(tmp_path / "auth", [task])
    with _session(directory, Transport()) as session:
        session.ledger.reserve(live.slot_key(task.id, HAIKU, "primary"), "a" * 64, "a" * 64, microusd=1000)
    with pytest.raises(MissionError, match="unresolved"):
        live.close_for_successor(directory, successor_id="TEST-SUCCESSOR", reason="unit test")
    assert json.loads((directory / "ledger.json").read_text())["state"] == "ACTIVE"


def test_R1_cli_uses_the_profile_prompt_and_refuses_unknown_profiles(tmp_path, monkeypatch):
    from click.testing import CliRunner
    from agent_arena.phase10_cli import audit
    runner = CliRunner()
    task_file = str(EXAMPLES / "positive-task.json")
    _r1_run(tmp_path, "positive", Transport(message(_recording("positive"))))
    unknown = runner.invoke(audit, ["run", "--replay", "--task", task_file, "--authorization-dir",
                                    str(tmp_path / "auth"), "--profile", "claude-haiku-5-5@9",
                                    "--output-root", str(tmp_path / "x")])
    assert unknown.exit_code == 2 and "Unknown live profile" in unknown.output

    def forbid(*_args, **_kwargs):
        raise AssertionError("network access attempted during CLI replay")
    monkeypatch.setattr(httpx.Client, "send", forbid)
    replay = runner.invoke(audit, ["run", "--replay", "--task", task_file, "--authorization-dir",
                                   str(tmp_path / "auth"), "--profile", HAIKU2, "--output-root",
                                   str(tmp_path / "cli-replay")])
    assert replay.exit_code == 0, replay.output
    payload = json.loads(replay.output)
    record = _record(payload["path"])
    evidence = record["run_record"]["results"][0]["agent_result"]["execution_evidence"]
    assert payload["status"] == "READY_FOR_RELEASE" and evidence["system_prompt_version"] == R1
    assert record["execution_mode"] == "offline_replay_of_live"


LS_TASKS = ROOT / "analysis" / "live_smoke_20261011" / "live_run" / "tasks"


def test_R1_contract_sentences_match_the_unchanged_validators():
    """C17, C19 and the binding-ID sentence, each checked against the validator it describes."""
    from agent_arena.artifact_binding import QA_ASYMMETRIC_EVIDENCE_SELECTION, check_evidence_symmetry, check_search_scope
    from agent_arena.phase8_models import PropositionLedger
    from agent_arena.phase8_semantics import validate_ledger
    from agent_arena.schemas import ForensicRecord

    def errors(data):
        return validate_ledger(ForensicRecord.model_validate(data), PropositionLedger.model_validate(data["phase8"]))
    appendix = _appendix()
    base = json.loads(_recording("positive"))["forensic_record"]
    assert errors(base) == []
    # C19: an empty client reference list fails when the parent has material evidence.
    empty = json.loads(json.dumps(base))
    empty["client_findings"][0]["referenced_evidence_ids"] = []
    assert any(f.code == QA_ASYMMETRIC_EVIDENCE_SELECTION
               for f in check_evidence_symmetry(ForensicRecord.model_validate(empty)))
    assert "so an empty list fails when the parent has material evidence" in appendix
    # C17: the negative-assertion trace is required only for required propositions ...
    optional = json.loads(json.dumps(base))
    first = optional["phase8"]["propositions"][0]
    extra = dict(json.loads(json.dumps(first)), proposition_id="claim:p2", materiality="optional")
    extra["evidence_bindings"] = [dict(first["evidence_bindings"][0], binding_id="b2", proposition_id="claim:p2",
                                       observation="no_evidence_found")]
    optional["phase8"]["propositions"].append(extra)
    assert errors(optional) == []
    assert "no_evidence_found on a required proposition" in appendix
    # ... and any negative assertion needs an existing finding.
    stray = json.loads(json.dumps(optional))
    stray["negative_assertions"] = [{"assertion_id": "n1", "finding_id": "claim:p2",
                                     "proposition": extra["proposition_text"], "search_scope_id": None}]
    assert any(f.check == "SA" for f in check_search_scope(ForensicRecord.model_validate(stray)))
    assert "A negative\nassertion always needs an existing finding" in appendix
    # Binding IDs are unique across all propositions, not per list.
    duplicate = json.loads(json.dumps(optional))
    duplicate["phase8"]["propositions"][1]["evidence_bindings"][0]["binding_id"] = "b1"
    assert "duplicate binding IDs" in errors(duplicate)
    assert "binding_id values are unique across all propositions" in appendix


def test_R1_unknown_values_and_clinical_endpoints_match_the_semantics():
    from types import SimpleNamespace
    from agent_arena.phase8_models import EvidenceDescription, SemanticAttributes
    from agent_arena.phase8_semantics import _capability, _unknown_value
    from agent_arena.phase8_taxonomy import CLINICAL_ENDPOINTS
    sets = [c for c in _unknown_value.__code__.co_consts if isinstance(c, frozenset)]
    listed = _appendix().split('Treated as unknown: null, "", ', 1)[1].split(".\n", 1)[0].split(", ")
    assert len(sets) == 1 and set(listed) | {""} == sets[0] and _unknown_value(None)
    claim = SimpleNamespace(attributes=SemanticAttributes(relation="therapeutic"))
    for endpoint in [*sorted(CLINICAL_ENDPOINTS), "surrogate", "biomarker", "educational"]:
        description = EvidenceDescription(
            evidence_id="e", source_role="trial", evidence_type="controlled_intervention", randomized=True,
            attributes=SemanticAttributes(comparison="between", species="human", endpoint_type=endpoint))
        state, _ = _capability(claim, description, {}, {})
        assert (state == "supported") == (endpoint in CLINICAL_ENDPOINTS), endpoint


def test_R1_frozen_smoke_cases_fit_the_ceiling_and_are_absent_from_the_contract():
    appendix, system = _appendix(), resolve_study_forensics_prompt(R1)
    paths = sorted(LS_TASKS.glob("LS-0*.json"))
    assert len(paths) == 6
    for path in paths:
        task = load_task(path)
        assert task.prompt not in appendix and task.context not in appendix
        for profile in (HAIKU2, SONNET2):
            exposure, _ = max_exposure_microusd(PROFILES[profile], system, build_user_message(task))
            assert exposure <= 300_000, (path.name, profile, exposure)


def test_R1_close_after_expiry_is_refused_and_the_ledger_stays_unchanged(tmp_path, monkeypatch):
    task = _task("positive")
    directory = _authorize(tmp_path / "auth", [task])
    _live_run(tmp_path, "positive", Transport(message(_recording("positive"))), directory=directory)
    before = (directory / "ledger.json").read_bytes()
    later = datetime.now(timezone.utc) + timedelta(days=30)

    class Later(datetime):
        @classmethod
        def now(cls, tz=None):
            return later
    monkeypatch.setattr(live, "datetime", Later)
    with pytest.raises(ValueError, match="expired"):
        live.close_for_successor(directory, successor_id="LATE", reason="after expiry")
    assert (directory / "ledger.json").read_bytes() == before


def test_R1_contract_C14_matches_raw_match():
    from types import SimpleNamespace
    from agent_arena.phase8_models import EvidenceDescription, SemanticAttributes
    from agent_arena.phase8_semantics import _raw_match

    def proposition(not_applicable=None, **attributes):
        return SimpleNamespace(attributes=SemanticAttributes(**attributes), material_dimensions=[],
                               not_applicable=not_applicable or {})

    def description(**attributes):
        return EvidenceDescription(evidence_id="e", source_role="trial", attributes=SemanticAttributes(**attributes))
    core = dict(species="human", population="adults", intervention="drug x", comparator="placebo", endpoint="ldl",
                endpoint_type="biomarker", follow_up="12 weeks", certainty="asserted", relation="causal")
    assert _raw_match(proposition(**core), description(**{k: v.upper() for k, v in core.items()})) == ([], [])
    reason = {"follow_up": "not stated in the claim"}
    # A null attribute with a not_applicable reason is skipped, whatever the description says.
    assert _raw_match(proposition(reason, **{**core, "follow_up": None}), description(**core)) == ([], [])
    # Only the C12 dimensions are compared: a null, non-core, non-material attribute is not.
    assert _raw_match(proposition(**core), description(**core, dose="10 mg")) == ([], [])
    # An unknown-like string is still compared and leaves the binding unresolved, even with a reason.
    assert _raw_match(proposition(reason, **{**core, "follow_up": "not_applicable"}), description(**core)) \
        == ([], ["follow_up"])
    # A null or unknown description value on a compared dimension is unresolved; a real difference mismatches.
    assert _raw_match(proposition(**core), description(**{**core, "population": None})) == ([], ["population"])
    assert _raw_match(proposition(**core), description(**{**core, "population": "children"})) == (["population"], [])
    # An effect_direction difference does not count for a contradiction binding (_binding_state).
    from agent_arena.phase8_models import EvidenceBinding
    from agent_arena.phase8_semantics import _binding_state
    claim = proposition(**{**core, "endpoint_type": "clinical", "effect_direction": "weight loss"})
    claim.proposition_id = "claim:p1"
    trial = EvidenceDescription(evidence_id="e", source_role="trial", evidence_type="controlled_intervention",
                                randomized=True, attributes=SemanticAttributes(
                                    **{**core, "endpoint_type": "clinical", "effect_direction": "no weight loss",
                                       "comparison": "between"}))
    ledger = SimpleNamespace(product_transfers=[], bridges=[])

    def state(observation):
        binding = EvidenceBinding(binding_id="b", proposition_id="claim:p1", evidence_id="e", directness="direct",
                                  observation=observation, reason="r")
        return _binding_state(claim, binding, ledger, {"e": trial}, {}, {}, [])[0]
    assert (state("contradiction"), state("support")) == ("contradicted", "unsupported")
    text = " ".join(_appendix().split())
    for sentence in ("An effect_direction difference does not count for a binding with observation contradiction",
                     "compared with its proposition on the C12 dimensions except relation and certainty",
                     "a proposition attribute that is null with a not_applicable reason is skipped",
                     "A null or unknown value on either side of a compared dimension leaves that binding unresolved",
                     "an unknown-like string such as not_applicable is still compared"):
        assert sentence in text, sentence


# ---------------------------------------------------------------- AA-P8/1.1 + AA-P9/1.1 live path (K11)

HAIKU3, SONNET3 = "claude-haiku-5-5@3", "claude-sonnet-5-5@3"


def _conflict_task(task_id="aa-p9-1-1-conflict", model="unsupported"):
    """The positive example (host derives supported) with a different, consistently stated model judgment."""
    from tests.test_phase8_9_conflict import set_model
    task = _task("positive").model_copy(update={"id": task_id})
    data = json.loads(_recording("positive"))
    set_model(data["forensic_record"], model)
    return task, json.dumps(data)


def test_K11_live_conflict_reaches_mandatory_counterreview_with_both_positions(tmp_path):
    task, raw = _conflict_task()
    directory = _authorize(tmp_path / "auth", [task], profiles=(HAIKU3,), ceiling=300_000)
    transport = Transport(message(raw, request_id="req_p"), message(raw, request_id="req_c"))
    with _session(directory, transport) as session:
        provider = live.LiveAuditProvider(session, HAIKU3, task.id, "primary", PROFILES[HAIKU3].prompt_versions[0])
        result = run_audit(task, provider, output_root=tmp_path / "out", review_state=directory / "phase9-state")
    assert len(transport.requests) == 2, "primary plus one mandatory counterreview"
    primary, review = (r["body"] for r in transport.requests)
    assert primary["system"] == resolve_study_forensics_prompt("study_forensics_prompt/v3-phase8-contract-r2")
    assert review["system"] == resolve_study_forensics_prompt("study_forensics_prompt/v3-phase8-contract-r2-review-p9-2")
    packet = json.loads(review["messages"][0]["content"].split("Bound evidence packet:\n", 1)[1].rsplit("\n</task_context>", 1)[0])
    conflict = next(c for c in packet["model_host_conflicts"] if c["scope"] == "proposition")
    assert (conflict["model_position"]["state"], conflict["host_position"]["state"]) == ("unsupported", "supported")
    record = _record(result.path)
    phase9 = record["run_record"]["metadata"]["phase9"]
    assert {a["kind"]: a["status"] for a in phase9["attempts"]} == {"counterreview": "completed", "stability": "rejected"}
    # One evidence item: the reversal is a recorded no-op (AA-P9 rule 7), so the mandatory case
    # stays UNRESOLVED; the completed counterreview never closes the conflict.
    assert phase9["route"] == "UNRESOLVED" and phase9["mandatory"] is True
    assert result.status == "REVIEW_REQUIRED" and inspect_bundle(Path(result.path)).valid
    blocked = release_candidate(Path(result.path), output_root=tmp_path / "rel", reviewer="TEST ONLY", reason="K11")
    assert blocked.status == "RELEASE_BLOCKED"


def _successor(tmp_path, tasks, predecessors, *, budget, attempts=12, retries=2, caps=None, profiles=(HAIKU3, SONNET3),
               ceiling=300_000):
    directory = _authorize(tmp_path / "succ", tasks, budget=budget, ceiling=ceiling, attempts=attempts,
                           retries=retries, profiles=profiles)
    auth = json.loads((directory / "authorization.json").read_text())
    auth["schema"] = live.AUTH_SCHEMA_SUCCESSOR
    auth["authorization_id"] = "TEST-SUCCESSOR-AUTH"
    auth["predecessors"] = predecessors
    auth["review_caps"] = caps or {p: {"counterreview": 1, "stability": 1} for p in profiles}
    (directory / "authorization.json").write_text(json.dumps(auth, indent=2))
    return directory


def _closed_predecessor(tmp_path, name, run=True, auth_id="TEST-LIVE-AUTH", earlier=None):
    """A closed throwaway authorization; ``earlier`` records the predecessor it superseded."""
    task = _task("positive")
    directory = _authorize(tmp_path / name, [task], auth_id=auth_id)
    if earlier is not None:
        auth = json.loads((directory / "authorization.json").read_text())
        auth["supersedes"] = {"prior_authorization_id": earlier["authorization_id"], "state": "CLOSED_SUPERSEDED",
                              "prior_ledger_sha256_after_closure": earlier["ledger_sha256"]}
        (directory / "authorization.json").write_text(json.dumps(auth, indent=2))
    if run:
        _live_run(tmp_path / f"{name}-out", "positive", Transport(message(_recording("positive"))), directory=directory)
    summary = live.close_for_successor(directory, successor_id="TEST-SUCC", reason="unit test")
    return {"authorization_id": auth_id, "directory": str(directory.resolve()),
            "ledger_sha256": summary["ledger_sha256"], "consumed_microusd": summary["reserved_or_confirmed_microusd"],
            "attempts": summary["attempts"], "technical_retries": summary["technical_retries"]}


def _pin(*records):
    """Pin throwaway closed authorizations the way -002/-003 are pinned (per-test history dict)."""
    for record in records:
        raw = (Path(record["directory"]) / "authorization.json").read_bytes()
        live.KNOWN_CLOSED_AUTHORIZATIONS[record["authorization_id"]] = {
            "ledger_sha256": record["ledger_sha256"], "authorization_sha256": live._sha_bytes(raw)}


def test_successor_authorization_binds_the_full_cost_history(tmp_path):
    task, _ = _conflict_task()
    predecessor = _closed_predecessor(tmp_path, "pred")
    open_task = _task("positive")
    open_directory = _authorize(tmp_path / "open", [open_task])
    _live_run(tmp_path / "open-out", "positive", Transport(message(_recording("positive"))), directory=open_directory)
    _pin(predecessor)
    rest = 2_000_000 - predecessor["consumed_microusd"]
    directory = _successor(tmp_path, [task], [predecessor], budget=rest)
    auth, _ = live.load_authorization(directory)
    assert auth["schema"] == live.AUTH_SCHEMA_SUCCESSOR
    too_much = _successor(tmp_path / "x", [task], [predecessor], budget=rest + 1)
    with pytest.raises(ValueError, match="exceeds the total ceiling"):
        live.load_authorization(too_much)
    many = _successor(tmp_path / "y", [task], [predecessor], budget=rest, attempts=40)
    with pytest.raises(ValueError, match="attempts exceed"):
        live.load_authorization(many)
    changed = dict(predecessor, ledger_sha256="0" * 64)
    with pytest.raises(ValueError, match="ledger changed since closure"):
        live.load_authorization(_successor(tmp_path / "z", [task], [changed], budget=rest))
    raw = (open_directory / "ledger.json").read_bytes()
    still_open = dict(predecessor, directory=str(open_directory.resolve()), ledger_sha256=live._sha_bytes(raw),
                      consumed_microusd=json.loads(raw)["reserved_microusd"])
    with pytest.raises(ValueError, match="still executable"):
        live.load_authorization(_successor(tmp_path / "w", [task], [still_open], budget=1_000_000))
    no_caps = _successor(tmp_path / "v", [task], [predecessor], budget=rest, caps={HAIKU3: {"counterreview": 1}})
    with pytest.raises(ValueError, match="review caps"):
        live.load_authorization(no_caps)


def test_review_cap_per_model_denies_a_second_counterreview_without_a_request(tmp_path):
    first, first_raw = _conflict_task("aa-p9-cap-a")
    second, second_raw = _conflict_task("aa-p9-cap-b")
    predecessor = _closed_predecessor(tmp_path, "pred")
    _pin(predecessor)
    directory = _successor(tmp_path, [first, second], [predecessor], budget=1_500_000, profiles=(HAIKU3,))
    transport = Transport(message(first_raw, request_id="req_a"), message(first_raw, request_id="req_ar"),
                          message(second_raw, request_id="req_b"))
    with _session(directory, transport) as session:
        for task in (first, second):
            provider = live.LiveAuditProvider(session, HAIKU3, task.id, "primary", PROFILES[HAIKU3].prompt_versions[0])
            result = run_audit(task, provider, output_root=tmp_path / "out", review_state=directory / "phase9-state")
        summary = session.summary()
    assert len(transport.requests) == 3 and summary["attempts"] == 3
    phase9 = _record(result.path)["run_record"]["metadata"]["phase9"]
    assert phase9["attempts"][0]["status"] == "denied" and phase9["route"] == "UNRESOLVED"
    assert phase9["attempts"][0]["reason"].startswith("Review cap for this model reached")
    assert result.status == "REVIEW_REQUIRED"


R2 = "study_forensics_prompt/v3-phase8-contract-r2"
R2_REVIEW = "study_forensics_prompt/v3-phase8-contract-r2-review-p9-2"
R2_PROMPT_SHA256 = {
    R2: "e92bba734f72c8526f5d922839a282fdb290e3d8b4db45d9e9e15e00a61a131f",
    R2_REVIEW: "725f35b00a758daa6a4ee5d7d8822e3db2b3787553fb6955ae4cc9a47e88fd9e",
}
R2_PROFILE_FINGERPRINTS = {
    HAIKU3: "074068522bba56971670c34b634073b64e9193529fe50553e3f4245e5013d1f2",
    SONNET3: "537510e9db6bf7564f9840998ed2987cb4b3691a9c48ed0a0853f629ce775af5",
}


def test_r2_prompt_bytes_and_at3_profiles_are_frozen_and_leave_history_unchanged():
    import hashlib
    from dataclasses import fields
    from agent_arena.phase8_pipeline import _R2_REPLACEMENTS, build_phase8_contract_r1, build_phase8_contract_r2
    from agent_arena.providers.anthropic_live import LiveProfile
    from agent_arena.runner import (
        STUDY_FORENSICS_PROMPT_VERSION_PHASE8_CONTRACT_R2, STUDY_FORENSICS_PROMPT_VERSION_PHASE9_CONTRACT_R2,
    )
    assert (STUDY_FORENSICS_PROMPT_VERSION_PHASE8_CONTRACT_R2, STUDY_FORENSICS_PROMPT_VERSION_PHASE9_CONTRACT_R2) \
        == (R2, R2_REVIEW)
    for version, digest in {**FROZEN_PROMPT_SHA256, **R2_PROMPT_SHA256}.items():
        assert hashlib.sha256(resolve_study_forensics_prompt(version).encode()).hexdigest() == digest, version
    assert {pid: PROFILES[pid].fingerprint() for pid in {**FROZEN_PROFILE_FINGERPRINTS, **R2_PROFILE_FINGERPRINTS}} \
        == {**FROZEN_PROFILE_FINGERPRINTS, **R2_PROFILE_FINGERPRINTS}
    p8, r2, review = (resolve_study_forensics_prompt(v) for v in (P8, R2, R2_REVIEW))
    assert r2 == p8 + "\n" + build_phase8_contract_r2()  # the historical v3 bytes are an unchanged prefix
    assert review.startswith(r2) and "repeating a position is not a resolution" in review[len(r2):]
    # r2 differs from R1 by exactly the listed replacements, each applied once.
    r1_text = build_phase8_contract_r1()
    for old, new in _R2_REPLACEMENTS:
        assert r1_text.count(old) == 1 and new in build_phase8_contract_r2(), old[:60]
    assert PROFILES[HAIKU3].prompt_versions == PROFILES[SONNET3].prompt_versions == (R2, R2_REVIEW)

    def changed(old, new):
        return {f.name for f in fields(LiveProfile) if getattr(PROFILES[old], f.name) != getattr(PROFILES[new], f.name)}
    assert changed(HAIKU2, HAIKU3) == {"profile_id", "max_tokens", "prompt_binding", "rationale"}
    assert changed(SONNET2, SONNET3) == {"profile_id", "prompt_binding", "rationale"}
    assert PROFILES[HAIKU3].max_tokens == 48000 and PROFILES[SONNET3].max_tokens == 16000


# ---------------------------------------------------------------- Package A rounds 1-2 (A-C1 to A-C5, A-C9, A-R1 to A-R3)

def test_successor_must_list_the_whole_genuine_chain_read_from_canonical_directories(tmp_path):
    import shutil
    task, _ = _conflict_task()
    first = _closed_predecessor(tmp_path, "a", auth_id="TEST-A")
    second = _closed_predecessor(tmp_path, "b", run=False, auth_id="TEST-B", earlier=first)
    unrelated = _closed_predecessor(tmp_path, "c", run=False, auth_id="TEST-C")
    hand_written = _closed_predecessor(tmp_path, "x", run=False, auth_id="TEST-X", earlier=second)
    _pin(first, second)
    rest = 2_000_000 - first["consumed_microusd"] - second["consumed_microusd"]
    auth, _ = live.load_authorization(_successor(tmp_path / "ok", [task], [first, second], budget=rest))
    assert [p["authorization_id"] for p in auth["predecessors"]] == ["TEST-A", "TEST-B"]
    # A-C1: omitting an earlier link would hide its spending from the cumulative ceiling.
    with pytest.raises(ValueError, match="supersedes TEST-A, which the successor omits"):
        live.load_authorization(_successor(tmp_path / "omit", [task], [second], budget=rest))
    # A-C1: an unchanged copy of a predecessor directory binds nothing.
    copy = tmp_path / "copy-of-a"
    shutil.copytree(first["directory"], copy)
    with pytest.raises(ValueError, match="not read from its canonical directory"):
        live.load_authorization(_successor(tmp_path / "copy", [task], [dict(first, directory=str(copy.resolve())),
                                                                         second], budget=rest))
    # A-R2 vector 1: byte-identical ledger, authorization rewritten to point at the copy.
    moved = tmp_path / "moved-b"
    shutil.copytree(second["directory"], moved)
    rewritten = json.loads((moved / "authorization.json").read_text())
    rewritten["canonical_directory"] = str(moved.resolve())
    (moved / "authorization.json").write_text(json.dumps(rewritten, indent=2))
    with pytest.raises(ValueError, match="authorization differs from the pinned closed authorization"):
        live.load_authorization(_successor(tmp_path / "moved", [task], [first, dict(second, directory=str(moved.resolve()))],
                                           budget=rest))
    # A-R2 vector 2: a hand-written closed "predecessor" that supersedes the pinned head.
    with pytest.raises(ValueError, match="TEST-X is neither pinned closed history nor a schema-1.1 successor"):
        live.load_authorization(_successor(tmp_path / "fake-head", [task], [first, second, hand_written], budget=rest))
    _pin(unrelated)
    with pytest.raises(ValueError, match="one chain with a single latest authorization"):
        live.load_authorization(_successor(tmp_path / "two-heads", [task], [first, second, unrelated], budget=rest))


def test_a_chain_continues_only_through_the_recorded_successor(tmp_path):
    import shutil
    task, _ = _conflict_task()
    root = _closed_predecessor(tmp_path, "root", auth_id="TEST-ROOT")
    _pin(root)
    rest = 2_000_000 - root["consumed_microusd"]
    first = _successor(tmp_path / "s1", [task], [root], budget=rest - 100_000, attempts=10)
    summary = live.close_for_successor(first, successor_id="TEST-NEXT", reason="unit test")  # opens, claims, closes
    link = {"authorization_id": "TEST-SUCCESSOR-AUTH", "directory": str(first.resolve()),
            "ledger_sha256": summary["ledger_sha256"], "consumed_microusd": summary["reserved_or_confirmed_microusd"],
            "attempts": summary["attempts"], "technical_retries": summary["technical_retries"]}

    def successor_of(name, links):
        directory = _successor(tmp_path / name, [task], [root, *links], budget=100_000, attempts=4, ceiling=100_000)
        auth = json.loads((directory / "authorization.json").read_text())
        auth["authorization_id"] = f"TEST-{name.upper()}"
        (directory / "authorization.json").write_text(json.dumps(auth, indent=2))
        return directory
    live.load_authorization(successor_of("next", [link]))  # genuine: the root's claim names the link
    # A-R2: a self-consistent forged copy of the link (rebound ledger) was never the recorded successor.
    forged = tmp_path / "forged-link"
    shutil.copytree(first, forged)
    auth = json.loads((forged / "authorization.json").read_text())
    auth["canonical_directory"] = str(forged.resolve())
    (forged / "authorization.json").write_text(json.dumps(auth, indent=2))
    ledger = json.loads((forged / "ledger.json").read_text())
    ledger["binding"]["authorization_fingerprint"] = live._sha_bytes((forged / "authorization.json").read_bytes())
    (forged / "ledger.json").write_text(json.dumps(ledger, indent=2))
    fake = dict(link, directory=str(forged.resolve()), ledger_sha256=live._sha_bytes((forged / "ledger.json").read_bytes()))
    with pytest.raises(ValueError, match="not the successor recorded by its own predecessor"):
        live.load_authorization(successor_of("via-forged", [fake]))
    # Skipping the link leaves the root's claim naming another successor.
    with pytest.raises(ValueError, match="already carries another successor"):
        live.load_authorization(_successor(tmp_path / "skip", [task], [root], budget=100_000, attempts=4,
                                           ceiling=100_000))


def test_pinned_closed_history_binds_every_new_live_budget(tmp_path):
    import hashlib
    # The pins are the closed ledgers and authorization files of -002 and -003 as stored in the repository.
    base = ROOT / "analysis/live_smoke_20261011"
    for directory, auth_id in (("live_run", "AA-P10-LIVE-SMOKE-20261011-002"),
                               ("repair_r1", "AA-P10-LIVE-SMOKE-20261011-003")):
        raw = (base / directory / "ledger.json").read_bytes()
        auth_raw = (base / directory / "authorization.json").read_bytes()
        ledger = json.loads(raw)
        assert PINNED_HISTORY[auth_id] == {"ledger_sha256": hashlib.sha256(raw).hexdigest(),
                                           "authorization_sha256": hashlib.sha256(auth_raw).hexdigest()}
        assert ledger["binding"]["authorization_fingerprint"] == hashlib.sha256(auth_raw).hexdigest()
        assert ledger["state"] == "REVOKED" and ledger["executable_remaining_microusd"] == 0
    assert set(PINNED_HISTORY) == {"AA-P10-LIVE-SMOKE-20261011-002", "AA-P10-LIVE-SMOKE-20261011-003"}
    task, _ = _conflict_task()
    pinned = _closed_predecessor(tmp_path, "pinned", auth_id="TEST-PINNED")
    other = _closed_predecessor(tmp_path, "other", run=False, auth_id="TEST-OTHER")
    _pin(pinned)
    # A-C3: a fresh schema-1.0 budget would sit outside the cumulative ceilings; replay stays possible.
    fresh = _authorize(tmp_path / "fresh", [task], auth_id="TEST-FRESH")
    with pytest.raises(ValueError, match="must be a schema-1.1 successor"):
        live.load_authorization(fresh)
    assert live.load_authorization(fresh, mode="replay")[0]["authorization_id"] == "TEST-FRESH"
    # A-R1: reusing a pinned id never opens a fresh ledger; the pinned authorization opens only as itself.
    reuse = _authorize(tmp_path / "reuse", [task], auth_id="TEST-PINNED")
    with pytest.raises(ValueError, match="opens only with its unchanged file and closed ledger"):
        _session(reuse, None)
    assert not (reuse / "ledger.json").exists()
    with _session(Path(pinned["directory"]), None) as session:
        assert session.ledger.data["state"] == "REVOKED"
    with pytest.raises(ValueError, match="TEST-PINNED is missing from the predecessor history"):
        live.load_authorization(_successor(tmp_path / "missing", [task], [other], budget=1_000_000))
    rest = 2_000_000 - pinned["consumed_microusd"]
    live.load_authorization(_successor(tmp_path / "bound", [task], [pinned], budget=rest))
    live.KNOWN_CLOSED_AUTHORIZATIONS["TEST-PINNED"] = dict(live.KNOWN_CLOSED_AUTHORIZATIONS["TEST-PINNED"],
                                                           ledger_sha256="0" * 64)
    with pytest.raises(ValueError, match="does not match its pinned closed ledger"):
        live.load_authorization(_successor(tmp_path / "repinned", [task], [pinned], budget=rest))


def test_a_predecessor_carries_one_successor_so_no_parallel_budget_exists(tmp_path):
    task, _ = _conflict_task()
    predecessor = _closed_predecessor(tmp_path, "pred")
    _pin(predecessor)
    ledger_before = (Path(predecessor["directory"]) / "ledger.json").read_bytes()
    rest = 2_000_000 - predecessor["consumed_microusd"]
    first = _successor(tmp_path / "s1", [task], [predecessor], budget=rest)
    second = _successor(tmp_path / "s2", [task], [predecessor], budget=rest)
    with _session(first, None):
        pass  # opening the fresh ledger records the succession once
    claim = json.loads((Path(predecessor["directory"]) / live.SUCCESSOR_CLAIM).read_text())
    assert claim["successor_authorization_id"] == "TEST-SUCCESSOR-AUTH"
    assert claim["successor_canonical_directory"] == str(first.resolve())
    # A-C2: the second successor of the same predecessor is refused before any ledger exists.
    with pytest.raises(ValueError, match="already carries another successor"):
        live.load_authorization(second)
    with pytest.raises(ValueError, match="already carries another successor"):
        _session(second, None)
    assert not (second / "ledger.json").exists()
    with _session(first, None) as session:  # the claimed successor resumes
        assert session.ledger.data["state"] == "ACTIVE"
    assert (Path(predecessor["directory"]) / "ledger.json").read_bytes() == ledger_before


def test_successor_review_caps_are_zero_or_one_and_only_r2_profiles_are_allowed(tmp_path):
    task, _ = _conflict_task()
    predecessor = _closed_predecessor(tmp_path, "pred")
    _pin(predecessor)
    rest = 2_000_000 - predecessor["consumed_microusd"]
    many = {p: {"counterreview": 7, "stability": 9} for p in (HAIKU3, SONNET3)}
    with pytest.raises(ValueError, match="limits of 0 or 1"):  # A-C4
        live.load_authorization(_successor(tmp_path / "caps", [task], [predecessor], budget=rest, caps=many))
    with pytest.raises(ValueError, match="does not bind the AA-P8/1.1 prompts"):  # A-C9
        live.load_authorization(_successor(tmp_path / "r1", [task], [predecessor], budget=rest, profiles=(HAIKU2,)))


def _replay_rows(directory, tasks, tmp_path):
    rows = {}
    for task in tasks:
        with live.LiveSession(directory, mode="replay") as session:
            provider = live.ReplayProvider(session, HAIKU3, task.id, "primary", R2)
            result = run_audit(task, provider, output_root=tmp_path / "replay", review_state=tmp_path / "rs" / task.id)
        phase9 = _record(result.path)["run_record"]["metadata"]["phase9"]
        rows[task.id] = (result.status, phase9["route"], [(a["kind"], a["status"]) for a in phase9["attempts"]],
                         [a["reason"] for a in phase9["attempts"]])
    return rows


def test_review_cap_decision_is_recorded_before_the_request_and_replayed_exactly(tmp_path):
    from agent_arena.providers.anthropic_live import build_user_message, max_exposure_microusd
    first, first_raw = _conflict_task("aa-p9-edge-a")
    second, second_raw = _conflict_task("aa-p9-edge-b")
    predecessor = _closed_predecessor(tmp_path, "pred")
    _pin(predecessor)
    # The per-call ceiling admits the primary request but not the longer counterreview request.
    ceiling, _ = max_exposure_microusd(PROFILES[HAIKU3], resolve_study_forensics_prompt(R2), build_user_message(first))
    directory = _successor(tmp_path, [first, second], [predecessor], budget=1_500_000, profiles=(HAIKU3,),
                           ceiling=ceiling)
    transport = Transport(message(first_raw, request_id="req_a"), message(second_raw, request_id="req_b"))
    live_rows = {}
    with _session(directory, transport) as session:
        for task in (first, second):
            provider = live.LiveAuditProvider(session, HAIKU3, task.id, "primary", R2)
            result = run_audit(task, provider, output_root=tmp_path / "out", review_state=directory / "phase9-state")
            phase9 = _record(result.path)["run_record"]["metadata"]["phase9"]
            live_rows[task.id] = (result.status, phase9["route"], [(a["kind"], a["status"]) for a in phase9["attempts"]])
        claims = session.ledger.data["review_cap_claims"]
    assert len(transport.requests) == 2, "two primaries; no review request left the process"
    # A's review used the single allowance (then failed at the per-call ceiling); B's was capped.
    assert claims == [live.slot_key(first.id, HAIKU3, "counterreview")]
    assert live_rows[first.id][2] == [("counterreview", "failed")]
    assert live_rows[second.id][2] == [("counterreview", "denied")]
    replay = _replay_rows(directory, (first, second), tmp_path)
    assert {k: v[:3] for k, v in replay.items()} == live_rows
    assert replay[second.id][3][0].startswith("Review cap for this model reached")


def test_review_after_a_cost_overrun_is_denied_with_its_true_reason_and_the_bundle_is_written(tmp_path):
    from agent_arena.providers.anthropic_live import build_user_message, max_exposure_microusd
    task, raw = _conflict_task("aa-p9-overrun")
    predecessor = _closed_predecessor(tmp_path, "pred")
    _pin(predecessor)
    exposure, _ = max_exposure_microusd(PROFILES[HAIKU3], resolve_study_forensics_prompt(R2), build_user_message(task))
    directory = _successor(tmp_path, [task], [predecessor], budget=exposure, profiles=(HAIKU3,), ceiling=exposure)
    overrun = {"input_tokens": 9000, "output_tokens": 4_000_000, "cache_creation_input_tokens": 0,
               "cache_read_input_tokens": 0}
    transport = Transport(message(raw, request_id="req_o", usage=overrun))
    with _session(directory, transport) as session:
        provider = live.LiveAuditProvider(session, HAIKU3, task.id, "primary", R2)
        result = run_audit(task, provider, output_root=tmp_path / "out", review_state=directory / "phase9-state")
        assert session.ledger.data["state"] == "REVOKED"
    # A-R3: the run ends with a bundle; the mandatory review stays open with the true reason.
    assert result.status == "REVIEW_REQUIRED" and inspect_bundle(Path(result.path)).valid
    phase9 = _record(result.path)["run_record"]["metadata"]["phase9"]
    assert [(a["kind"], a["status"]) for a in phase9["attempts"]] == [("counterreview", "denied")]
    assert phase9["attempts"][0]["reason"] == "Live ledger is not ACTIVE; the review stays open"
    replay = _replay_rows(directory, (task,), tmp_path)[task.id]
    assert replay[:3] == (result.status, phase9["route"], [("counterreview", "denied")])
    assert replay[3] == ["No live review allowance was recorded for this slot; the review stays open"]


# ---------------------------------------------------------------- Package B (P10-F1/G1, P9-F1/A1, P9-F2, K1)

def test_replay_from_a_copy_keeps_a_never_executed_mandatory_review_open(tmp_path, monkeypatch):
    """P10-F1/P9-F1 and K1: the sealed R1 (-003) history replays from any unchanged copy (AA-P9/1.2)."""
    import shutil
    monkeypatch.setattr(live, "KNOWN_CLOSED_AUTHORIZATIONS", dict(PINNED_HISTORY))  # the real pins apply
    source = ROOT / "analysis/live_smoke_20261011/repair_r1"
    copy = tmp_path / "r1-copy"
    copy.mkdir()
    for name in ("authorization.json", "ledger.json"):
        (copy / name).write_bytes((source / name).read_bytes())
    shutil.copytree(source / "captures", copy / "captures")
    rows = {}
    for case in ("LS-01", "LS-02"):
        task = load_task(ROOT / f"analysis/live_smoke_20261011/live_run/tasks/{case}.json")
        with live.LiveSession(copy, mode="replay") as session:
            provider = live.ReplayProvider(session, HAIKU2, task.id, "primary", R1)
            result = run_audit(task, provider, output_root=tmp_path / "out", review_state=tmp_path / "rs" / case)
        assert result.path and inspect_bundle(Path(result.path)).valid, result.errors
        carrier = _record(result.path)["run_record"]["results"][0]["agent_result"]["execution_evidence"]
        # BF3: the replayed ledger bytes are recorded, so a replay is traceable to the sealed ledger.
        assert carrier["replay_ledger_sha256"] == PINNED_HISTORY["AA-P10-LIVE-SMOKE-20261011-003"]["ledger_sha256"]
        phase9 = _record(result.path)["run_record"]["metadata"]["phase9"]
        attempts = phase9.get("attempts", [])
        rows[case] = (result.status, [(a["kind"], a["status"]) for a in attempts], [a["reason"] for a in attempts])
    assert rows["LS-01"][:2] == ("READY_FOR_RELEASE", [])
    assert rows["LS-02"][:2] == ("REVIEW_REQUIRED", [("counterreview", "denied")])
    assert rows["LS-02"][2][0].startswith("No live review was executed for this slot under AA-P10-LIVE-SMOKE-20261011-003")
    for name in ("authorization.json", "ledger.json"):
        assert (copy / name).read_bytes() == (source / name).read_bytes()  # replay never writes
    # BF3: replay is location-free, so a pinned history replays only from its unchanged bytes.
    edited = tmp_path / "r1-edited"
    shutil.copytree(copy, edited)
    ledger = json.loads((edited / "ledger.json").read_text())
    ledger["attempts"][0]["confirmed_token_cost_microusd"] = 1
    (edited / "ledger.json").write_text(json.dumps(ledger, indent=2))
    with pytest.raises(ValueError, match="replays only from its unchanged file and closed ledger"):
        live.load_authorization(edited, mode="replay")


class _Kill(BaseException):
    """A hard interruption (crash, kill, Ctrl-C) while a request is in flight."""


def test_an_interrupted_live_review_replays_as_an_open_review_with_a_bundle(tmp_path):
    """G1/P9-A1: a review request killed in flight stays unresolved; replay still yields a bundle."""
    task, raw = _conflict_task("aa-p9-killed")
    predecessor = _closed_predecessor(tmp_path, "pred")
    _pin(predecessor)
    directory = _successor(tmp_path, [task], [predecessor], budget=1_500_000, profiles=(HAIKU3,))
    transport = Transport(message(raw, request_id="req_p"), _Kill())
    with pytest.raises(_Kill):
        with _session(directory, transport) as session:
            provider = live.LiveAuditProvider(session, HAIKU3, task.id, "primary", R2)
            run_audit(task, provider, output_root=tmp_path / "out", review_state=directory / "phase9-state")
    ledger = json.loads((directory / "ledger.json").read_text())
    assert [(a["slot_key"].split("|")[2], a["state"]) for a in ledger["attempts"]] == \
        [("primary", "COMPLETED"), ("counterreview", "RESERVED_POSSIBLY_BILLABLE")]
    before = (directory / "ledger.json").read_bytes()
    with live.LiveSession(directory, mode="replay") as session:
        provider = live.ReplayProvider(session, HAIKU3, task.id, "primary", R2)
        result = run_audit(task, provider, output_root=tmp_path / "replay", review_state=tmp_path / "rs")
    assert result.status == "REVIEW_REQUIRED" and inspect_bundle(Path(result.path)).valid
    phase9 = _record(result.path)["run_record"]["metadata"]["phase9"]
    assert [(a["kind"], a["status"]) for a in phase9["attempts"]] == [("counterreview", "denied")]
    assert "interrupted or is unresolved" in phase9["attempts"][0]["reason"]
    assert phase9["route"] == "UNRESOLVED" and (directory / "ledger.json").read_bytes() == before


def test_a_live_review_adjudication_states_its_true_provenance(tmp_path):
    """P9-F2: the model adjudication of a live conflict review names the live run and the disclosed positions."""
    task, raw = _conflict_task("aa-p9-provenance")
    directory = _authorize(tmp_path / "auth", [task], profiles=(HAIKU3,), ceiling=300_000)
    transport = Transport(message(raw, request_id="req_p"), message(raw, request_id="req_c"))
    with _session(directory, transport) as session:
        provider = live.LiveAuditProvider(session, HAIKU3, task.id, "primary", R2)
        result = run_audit(task, provider, output_root=tmp_path / "out", review_state=directory / "phase9-state")
    decisions = _record(result.path)["run_record"]["metadata"]["phase9"]["adjudications"]
    model = next(d for d in decisions if d["reviewer_type"] == "model")
    assert model["reviewer_provenance"].startswith("Live model review under AA-P10-LIVE/1.0 (anthropic-live/")
    assert model["independence"].startswith(
        "Host comparison of a live model review: model and host positions of the open conflicts supplied")
    assert "Built-in offline recording" not in json.dumps(decisions)
    with live.LiveSession(directory, mode="replay") as session:
        provider = live.ReplayProvider(session, HAIKU3, task.id, "primary", R2)
        replay = run_audit(task, provider, output_root=tmp_path / "replay", review_state=tmp_path / "rs")
    replayed = next(d for d in _record(replay.path)["run_record"]["metadata"]["phase9"]["adjudications"]
                    if d["reviewer_type"] == "model")
    assert replayed["reviewer_provenance"].startswith("Offline replay of a recorded live model review under AA-P10-LIVE/1.0")
    assert replayed["independence"].startswith("Host comparison of a replayed live model review: model and host positions")


def test_a_refused_live_review_is_adjudicated_as_not_sent_live_and_in_replay(tmp_path):
    """BF1: a review refused before sending states that no request was sent and nothing was supplied."""
    from agent_arena.providers.anthropic_live import build_user_message, max_exposure_microusd
    task, raw = _conflict_task("aa-p9-refused")
    predecessor = _closed_predecessor(tmp_path, "pred")
    _pin(predecessor)
    ceiling, _ = max_exposure_microusd(PROFILES[HAIKU3], resolve_study_forensics_prompt(R2), build_user_message(task))
    directory = _successor(tmp_path, [task], [predecessor], budget=1_500_000, profiles=(HAIKU3,), ceiling=ceiling)
    transport = Transport(message(raw, request_id="req_p"))
    with _session(directory, transport) as session:
        provider = live.LiveAuditProvider(session, HAIKU3, task.id, "primary", R2)
        result = run_audit(task, provider, output_root=tmp_path / "out", review_state=directory / "phase9-state")
    assert len(transport.requests) == 1 and result.status == "REVIEW_REQUIRED"

    def model_decision(path):
        decisions = _record(path)["run_record"]["metadata"]["phase9"]["adjudications"]
        return next(d for d in decisions if d["reviewer_type"] == "model")
    decision = model_decision(result.path)
    assert decision["reviewer_provenance"].startswith("Live review request not sent under AA-P10-LIVE/1.0")
    assert decision["independence"].startswith("No model review output") and decision["outcome"] == "failed"
    attempt = _record(result.path)["run_record"]["metadata"]["phase9"]["attempts"][0]
    assert attempt["independence"].startswith("No review request sent (")  # RF2: the receipt says the same
    assert "No review request sent (" in (Path(result.path) / "report.md").read_text()
    with live.LiveSession(directory, mode="replay") as session:
        provider = live.ReplayProvider(session, HAIKU3, task.id, "primary", R2)
        replay = run_audit(task, provider, output_root=tmp_path / "replay", review_state=tmp_path / "rs")
    assert replay.status == "REVIEW_REQUIRED"
    replayed = model_decision(replay.path)
    assert replayed["reviewer_provenance"].startswith("Offline replay of a live review request that was never sent")
    assert replayed["independence"].startswith("No model review output")
    receipt = _record(replay.path)["run_record"]["metadata"]["phase9"]["attempts"][0]
    assert receipt["independence"].startswith("No review request sent (") and "Offline replay" in receipt["independence"]


def test_cli_replay_keeps_its_review_state_out_of_the_authorization_directory(tmp_path, monkeypatch):
    """P10-F4/BE14: a CLI replay that reaches a review writes nothing into the (sealed) evidence directory."""
    import hashlib
    import shutil
    from click.testing import CliRunner
    from agent_arena.phase10_cli import audit
    monkeypatch.setattr(live, "KNOWN_CLOSED_AUTHORIZATIONS", dict(PINNED_HISTORY))
    monkeypatch.setattr(httpx.Client, "send", lambda *a, **k: (_ for _ in ()).throw(AssertionError("network")))
    source = ROOT / "analysis/live_smoke_20261011/repair_r1"
    copy = tmp_path / "r1-copy"
    copy.mkdir()
    for name in ("authorization.json", "ledger.json"):
        (copy / name).write_bytes((source / name).read_bytes())
    shutil.copytree(source / "captures", copy / "captures")

    def tree(path):
        return {str(p.relative_to(path)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(path.rglob("*")) if p.is_file()}
    before = tree(copy)
    out = tmp_path / "out"
    result = CliRunner().invoke(audit, ["run", "--replay", "--task",
                                        str(ROOT / "analysis/live_smoke_20261011/live_run/tasks/LS-02.json"),
                                        "--authorization-dir", str(copy), "--profile", HAIKU2,
                                        "--output-root", str(out)])
    assert result.exit_code == 2 and json.loads(result.output)["status"] == "REVIEW_REQUIRED", result.output
    assert tree(copy) == before  # nothing written into the authorization directory
    assert list((out / "replay-state").rglob("phase9/*.json"))  # the Phase-9 state sits next to the output
