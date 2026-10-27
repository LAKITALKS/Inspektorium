"""v1 closeout: operator-facing outcome wording and conflict wording (Stage P, Areas A2 and B).

Live doubles use the tests/integration/test_workflow_live.py helpers (throwaway authorizations in tmp_path, httpx
MockTransport); no test can reach a provider. Conflict fixtures are SYNTHETIC TEST FIXTURES built from
examples/audit; their materiality is computed by review.routing, never set by hand.
"""

from __future__ import annotations

import html
import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from inspektorium.audit.workflow import live
from inspektorium.audit.workflow.bundle import (
    inspect_bundle,
    release_candidate,
    review_candidate,
    run_audit,
)
from inspektorium.audit.cli import audit
from inspektorium.audit.workflow.models import AuditRecord
from inspektorium.audit.workflow.pipeline import (
    REGISTRY,
    automatic_outcome,
    digest,
    evaluate,
)
from inspektorium.audit.workflow.projection import projection
from inspektorium.audit.review.models import CONTRACT_VERSION as P9_CONTRACT
from inspektorium.audit.review.runtime import OfflineReviewProvider
from inspektorium.audit.providers.anthropic_live import PROFILES
from inspektorium.audit.schemas import RunRecord
from inspektorium.audit.execution.task_loader import load_task
from tests.integration.test_workflow_live import (
    HAIKU,
    HAIKU3,
    P8,
    Transport,
    _authorize,
    _closed_predecessor,
    _conflict_task,
    _pin,
    _session,
    _successor,
    _two_evidence_unknown,
    message,
)
from tests.acceptance.test_forensics_review_conflict import example

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "examples" / "audit"
OPEN = (
    "Automatic processing has ended. The result is not conclusively resolved and is not scientifically released. "
    "No human reviewer or review queue is assumed. This revision is immutable: only a recorded human decision "
    "(inspektorium audit review) or a new, explicitly commissioned run creates a new revision."
)
READY = (
    "Automatic processing has ended. No blocking cause is recorded; an explicit local release is still required. "
    "This is not a scientific validation."
)
RELEASED = (
    "Automatic processing has ended. This is an explicitly released local artifact; its controls are technical "
    "and do not establish scientific truth."
)
NOT_MATERIAL = (
    f"not material for the composite, a decisive output or the derived label; no review is required under "
    f"{P9_CONTRACT} (the Phase-8 conflict reason states the rule for material conflicts); "
)


@pytest.fixture(autouse=True)
def _isolated_live_history(monkeypatch):
    monkeypatch.setattr(live, "KNOWN_CLOSED_AUTHORIZATIONS", {})


def lines(path, name="report.md"):
    return html.unescape((Path(path) / name).read_text()).splitlines()


def row(path, field):
    return next(line for line in lines(path) if line.startswith(f"| {field} |"))


def phase9(path):
    return json.loads((Path(path) / "record.json").read_text())["run_record"][
        "metadata"
    ]["phase9"]


def projected(path):
    record = AuditRecord.model_validate_json((Path(path) / "record.json").read_bytes())
    _, controls, review, selected, assessment, forensic = evaluate(
        RunRecord.model_validate(record.run_record),
        digest(record.model_dump()),
        record.provenance,
    )
    return projection(record, controls, review, selected, assessment, forensic)


def host_texts(path):
    return [
        block["text"]
        for _, section in projected(path)
        for block in section["blocks"]
        if block["kind"] == "text"
    ]


# ---------------------------------------------------------------- A2 live doubles


def _successor_run(tmp_path, task, responses, *, ceiling=300_000):
    predecessor = _closed_predecessor(tmp_path, "pred")
    _pin(predecessor)
    directory = _successor(
        tmp_path,
        [task],
        [predecessor],
        budget=1_500_000,
        profiles=(HAIKU3,),
        ceiling=ceiling,
    )
    transport = Transport(*responses)
    with _session(directory, transport) as session:
        provider = live.LiveAuditProvider(
            session, HAIKU3, task.id, "primary", PROFILES[HAIKU3].prompt_versions[0]
        )
        result = run_audit(
            task,
            provider,
            output_root=tmp_path / "out",
            review_state=directory / "phase9-state",
        )
    return result, len(transport.requests)


def cap_denied(tmp_path):
    first, first_raw = _conflict_task("v1-cap-a")
    second, second_raw = _conflict_task("v1-cap-b")
    predecessor = _closed_predecessor(tmp_path, "pred")
    _pin(predecessor)
    directory = _successor(
        tmp_path, [first, second], [predecessor], budget=1_500_000, profiles=(HAIKU3,)
    )
    transport = Transport(message(first_raw), message(first_raw), message(second_raw))
    with _session(directory, transport) as session:
        for task in (first, second):
            provider = live.LiveAuditProvider(
                session, HAIKU3, task.id, "primary", PROFILES[HAIKU3].prompt_versions[0]
            )
            result = run_audit(
                task,
                provider,
                output_root=tmp_path / "out",
                review_state=directory / "phase9-state",
            )
    return result, len(transport.requests)


def reviews_completed(tmp_path):
    task, raw = _two_evidence_unknown()
    directory = _authorize(tmp_path / "auth", [task])
    transport = Transport(message(raw), message(raw), message(raw))
    with _session(directory, transport) as session:
        provider = live.LiveAuditProvider(session, HAIKU, task.id, "primary", P8)
        result = run_audit(
            task,
            provider,
            output_root=tmp_path / "out",
            review_state=directory / "phase9-state",
        )
    return result, len(transport.requests)


def conflict_review_completed(tmp_path):
    task, raw = _conflict_task("v1-reviewed")
    return _successor_run(tmp_path, task, [message(raw), message(raw)])


def span_offset(tmp_path):
    task, raw = _conflict_task("v1-span")
    data = json.loads(raw)
    for proposition in data["forensic_record"]["phase8"]["propositions"]:
        proposition["original_span"]["start"] += 1
        proposition["original_span"]["end"] += 1
    return _successor_run(tmp_path, task, [message(json.dumps(data))])


def review_sent_but_failed(tmp_path):
    task, raw = _conflict_task("v1-failed")
    return _successor_run(
        tmp_path, task, [message(raw), message("I cannot provide that analysis.")]
    )


def review_not_sent(tmp_path):
    from inspektorium.audit.providers.anthropic_live import (
        build_user_message,
        max_exposure_microusd,
    )
    from inspektorium.audit.execution.runner import resolve_study_forensics_prompt

    task, raw = _conflict_task("v1-unsent")
    prompt = PROFILES[HAIKU3].prompt_versions[0]
    ceiling, _ = max_exposure_microusd(
        PROFILES[HAIKU3],
        resolve_study_forensics_prompt(prompt),
        build_user_message(task),
    )
    return _successor_run(tmp_path, task, [message(raw)], ceiling=ceiling)


DOUBLES = {
    # name: (builder, requests, status, open cause prefix, conflict row)
    "cap_denied": (
        cap_denied,
        3,
        "REVIEW_REQUIRED",
        "mandatory review not executed: counterreview denied: Review cap for this model reached",
        "selected judgment: 2 open; mandatory review not executed, release blocked",
    ),
    "reviews_completed": (
        reviews_completed,
        3,
        "REVIEW_REQUIRED",
        "automatic reviews executed (counterreview completed; stability completed); "
        "the material conflict or UNKNOWN remains open",
        "none recorded",
    ),
    "conflict_review_completed": (
        conflict_review_completed,
        2,
        "REVIEW_REQUIRED",
        "automatic reviews executed (counterreview completed; stability rejected without "
        "a call: Rejected: evidence reversal is a no-op",
        "selected judgment: 2 open; mandatory review executed, conflict still open, "
        "release blocked; other positions: 2 (open; see review route)",
    ),
    "span_offset": (
        span_offset,
        1,
        "ANALYSIS_INCOMPLETE",
        "technically incomplete analysis; no conflict review was run: claim:p1: original span mismatch",
        "not evaluated (analysis technically incomplete)",
    ),
    "review_sent_but_failed": (
        review_sent_but_failed,
        2,
        "REVIEW_REQUIRED",
        "mandatory review executed but failed: ",
        "selected judgment: 2 open; mandatory review executed but failed, release blocked",
    ),
    "review_not_sent": (
        review_not_sent,
        1,
        "REVIEW_REQUIRED",
        "mandatory review not executed: counterreview not sent: ",
        "selected judgment: 2 open; mandatory review not executed, release blocked",
    ),
}


@pytest.mark.parametrize("name", list(DOUBLES))
def test_A2_every_unresolved_live_double_states_that_automatic_processing_ended_and_why(
    tmp_path, name
):
    build, requests, status, cause, conflicts = DOUBLES[name]
    result, sent = build(tmp_path)
    assert sent == requests and result.status == status, result.errors
    assert inspect_bundle(Path(result.path)).valid
    for document in ("report.md", "report.html"):
        text = lines(result.path, document)
        if document == "report.md":
            # The status paragraph is unchanged; the ended sentence follows it directly.
            index = text.index(f"{status} — local artifact status")
            assert [line for line in text[index + 1 :] if line][0] == OPEN
        else:
            joined = "\n".join(text)
            assert (
                f'<p class="status">{status} — local artifact status</p><p class="notice">{OPEN}</p>'
                in joined
            )
    assert (
        row(result.path, "automatic processing") == "| automatic processing | ended |"
    )
    assert row(result.path, "open cause").startswith(f"| open cause | {cause}")
    assert (
        row(result.path, "model/host conflicts")
        == f"| model/host conflicts | {conflicts} |"
    )
    # OperationResult errors (what `inspektorium audit run` prints) name the open cause.
    review_error = next(
        e for e in result.errors if e.startswith("phase9_history_review: ")
    )
    assert (
        review_error
        == "phase9_history_review: Review open: "
        + row(result.path, "open cause")[len("| open cause | ") : -len(" |")]
    )
    decision = {
        c["control_id"]: c
        for c in json.loads((Path(result.path) / "decision.json").read_text())[
            "controls"
        ]
    }
    assert decision["phase9_history_review"]["reason"] == review_error.removeprefix(
        "phase9_history_review: "
    )


def test_A2_the_open_causes_of_the_doubles_differ_pairwise(tmp_path):
    causes = {}
    for name, (build, *_rest) in DOUBLES.items():
        live.KNOWN_CLOSED_AUTHORIZATIONS.clear()
        result, _ = build(tmp_path / name)
        causes[name] = row(result.path, "open cause")
    assert len(set(causes.values())) == len(causes), causes


def test_A2_incomplete_analysis_names_its_cause_in_every_failing_analysis_control(
    tmp_path,
):
    result, _ = span_offset(tmp_path)
    errors = dict(e.split(": ", 1) for e in result.errors)
    assert errors["analysis_source"].startswith(
        "Analysis incomplete: claim:p1: original span mismatch"
    )
    assert errors["phase8_semantics_taxonomy"].startswith(
        "Semantic or taxonomy analysis incomplete: claim:p1: original span mismatch"
    )
    assert errors["phase9_history_review"].startswith(
        "Review open: technically incomplete analysis; no conflict review was run: claim:p1: original span mismatch"
    )
    history = "\n".join(lines(result.path))
    assert (
        "Conflicts were not evaluated: the selected analysis is technically incomplete."
        in history
    )
    assert "contains no recorded conflicts" not in history


def test_A2_ready_released_and_offline_review_outcomes_through_the_canonical_cli(
    tmp_path,
):
    runner = CliRunner()
    recording = tmp_path / "conflict.json"
    recording.write_text(example("positive", "unsupported")[1])
    task_file = tmp_path / "task.json"
    task_file.write_text((EXAMPLES / "positive-task.json").read_text())
    blocked = runner.invoke(
        audit,
        [
            "run",
            "--offline",
            "--task",
            str(task_file),
            "--recording",
            str(recording),
            "--output-root",
            str(tmp_path / "cli"),
        ],
    )
    payload = json.loads(blocked.output)
    assert payload["status"] == "REVIEW_REQUIRED"
    assert (
        "phase9_history_review: Review open: mandatory review not executed: no automatic review was authorized "
        "or run in this execution"
    ) in payload["errors"]
    assert (
        row(payload["path"], "model/host conflicts")
        == "| model/host conflicts | selected judgment: 2 open; mandatory review not executed, release blocked |"
    )
    ready = runner.invoke(
        audit,
        [
            "run",
            "--offline",
            "--task",
            str(task_file),
            "--recording",
            str(EXAMPLES / "positive-recording.json"),
            "--output-root",
            str(tmp_path / "ok"),
        ],
    )
    candidate = json.loads(ready.output)
    assert candidate["status"] == "READY_FOR_RELEASE" and candidate["errors"] == []
    assert (
        READY in lines(candidate["path"])
        and row(candidate["path"], "open cause")
        == "| open cause | no blocking cause recorded |"
    )
    released = release_candidate(
        Path(candidate["path"]),
        output_root=tmp_path / "rel",
        reviewer="TEST ONLY",
        reason="v1 closeout wording",
    )
    assert released.status == "RELEASED" and inspect_bundle(Path(released.path)).valid
    assert RELEASED in lines(released.path) and OPEN not in lines(released.path)
    assert (
        row(released.path, "automatic processing") == "| automatic processing | ended |"
    )


def test_A2_outcome_helper_covers_every_status_from_recorded_fields_only():
    record = {
        "results": [
            {"agent_result": {"error": ""}},
            {"agent_result": {"error": "timeout " + "x" * 300}},
        ]
    }
    sentence, cause = automatic_outcome("RUN_FAILED", {}, {}, record=record)
    assert sentence == OPEN and cause == "run failed: " + ("timeout " + "x" * 300)[:200]
    assert (
        automatic_outcome("RUN_FAILED", {}, {}, record={"results": []})[1]
        == "run failed: no usable model output"
    )
    failing = [
        type("C", (), {"control_id": cid, "outcome": outcome})()
        for cid, outcome in (
            ("provenance", "fail"),
            ("analysis_source", "pass"),
            ("html_qa", "fail"),
        )
    ]
    assert (
        automatic_outcome(
            "RELEASE_BLOCKED", {}, {"technical_status": "completed"}, failing
        )[1]
        == "release controls failed: provenance, html_qa"
    )
    assert automatic_outcome("READY_FOR_RELEASE", {}, {}) == (
        READY,
        "no blocking cause recorded",
    )
    assert automatic_outcome("RELEASED", {}, {}) == (
        RELEASED,
        "no blocking cause recorded",
    )
    completed = {"technical_status": "completed"}
    assert (
        automatic_outcome(
            "REVIEW_REQUIRED",
            {"history_validation": "invalid", "reasons": ["Stored differs"]},
            completed,
        )[1]
        == "review history invalid: Stored differs"
    )
    assert (
        automatic_outcome(
            "REVIEW_REQUIRED",
            {"route": "HUMAN_REVIEW_REQUIRED", "reasons": ["Label conflict"]},
            completed,
        )[1]
        == "not automatically resolvable: Label conflict"
    )
    begun = {"attempts": [{"kind": "counterreview", "status": "begun"}]}
    assert automatic_outcome("REVIEW_REQUIRED", begun, completed)[1] == (
        "mandatory review interrupted: counterreview "
        "interrupted without a completed response "
        "(a request may have been sent)"
    )
    # The latest attempt per kind decides, as in phase9_runtime._rebuild.
    retried = {
        "attempts": [
            {"kind": "counterreview", "status": "denied", "reason": "cap"},
            {"kind": "counterreview", "status": "rejected", "reason": "no-op"},
        ]
    }
    assert (
        automatic_outcome("REVIEW_REQUIRED", retried, completed)[1]
        == "mandatory review not executed: counterreview rejected without a call: no-op"
    )
    incomplete = {"technical_status": "incomplete", "reasons": ["a" * 250, "b", "c"]}
    assert (
        automatic_outcome("ANALYSIS_INCOMPLETE", {}, incomplete)[1]
        == "technically incomplete analysis; no conflict review was run: "
        + "a" * 200
        + "; b"
    )


# ---------------------------------------------------------------- B conflict wording (SYNTHETIC TEST FIXTURES)


def conflict_fixture(link=None):
    """SYNTHETIC TEST FIXTURE: optional proposition, model 'supported' vs host 'unknown' (inconclusive binding).

    ``link`` adds exactly one structural link that makes the same conflict material.
    """
    task = load_task(EXAMPLES / "positive-task.json")
    data = json.loads((EXAMPLES / "optional-unknown-recording.json").read_text())
    record = data["forensic_record"]
    record["record_id"] = "SYNTHETIC-TEST-FIXTURE-v1-closeout"
    ledger = record["phase8"]
    optional = next(
        p for p in ledger["propositions"] if p["proposition_id"] == "claim:optional"
    )
    optional["evidence_bindings"] = [
        {
            "binding_id": "b-opt",
            "proposition_id": "claim:optional",
            "evidence_id": "e1",
            "directness": "partial",
            "observation": "inconclusive",
            "reason": "SYNTHETIC TEST FIXTURE binding",
        }
    ]
    optional["reported_verdict"] = "supported"
    if link == "premise":
        ledger["propositions"][0]["premise_proposition_ids"] = ["claim:optional"]
    elif link == "label":
        record["phase8_taxonomy"]["proposition_ids"] = ["claim:p1", "claim:optional"]
    elif link == "summary":
        record["findings"].append(
            {
                "finding_id": "claim:optional",
                "provenance_id": "origin",
                "proposition": optional["proposition_text"],
                "verdict_summary": "",
                "supporting_evidence_ids": ["e1"],
                "contrary_evidence_ids": [],
                "allowed_summary_strength": "not_assessed",
                "confidence_status": "",
                "predicted_label": None,
            }
        )
        record["client_findings"].append(
            {
                "client_finding_id": "client2",
                "parent_finding_id": "claim:optional",
                "display_claim": optional["proposition_text"],
                "client_explanation": "",
                "client_strength": "not_assessed",
                "referenced_evidence_ids": ["e1"],
                "provenance_id": "origin",
                "value_claims": [],
                "client_negative_assertions": [],
            }
        )
        summary = json.loads(
            json.dumps(
                next(t for t in ledger["transformations"] if t["stage"] == "summary")
            )
        )
        summary.update(
            transformation_id="summary-optional",
            target_id="client2",
            from_proposition_ids=["claim:optional"],
            asserted_state="supported",
            asserts_whole_claim=False,
        )
        ledger["transformations"].append(summary)
    elif (
        link == "mixed"
    ):  # the required proposition also disagrees: material and bounded conflicts together
        ledger["propositions"][0]["reported_verdict"] = "unsupported"
        for transformation in ledger["transformations"]:
            if transformation.get("asserted_state") is not None:
                transformation["asserted_state"] = "unsupported"
    return task, json.dumps(data)


def test_B_bounded_conflict_is_open_not_reviewed_and_releasable_with_matching_record_md_html(
    tmp_path,
):
    task, raw = conflict_fixture()
    result = run_audit(task, OfflineReviewProvider(raw), output_root=tmp_path / "c")
    assert result.status == "READY_FOR_RELEASE" and result.errors == []
    data = phase9(result.path)
    trigger = next(t for t in data["triggers"] if "model_host" in t["code"])
    assert (trigger["code"], trigger["mandatory"], trigger["proposition_ids"]) == (
        "bounded_model_host_conflict",
        False,
        ["claim:optional"],
    )
    assert (
        data["route"],
        data["mandatory"],
        data.get("attempts", []),
        data["conflicts"],
    ) == ("AUTO_RESOLVABLE", False, [], [])
    expected = "selected judgment: 1 open; " + NOT_MATERIAL + "not reviewed"
    assert (
        row(result.path, "model/host conflicts")
        == f"| model/host conflicts | {expected} |"
    )
    assert f"<td>model/host conflicts</td><td>{expected}</td>" in "".join(
        lines(result.path, "report.html")
    )
    assert (
        row(result.path, "open cause") == "| open cause | no blocking cause recorded |"
    )
    assert READY in lines(result.path)
    for document in ("report.md", "report.html"):
        text = "\n".join(lines(result.path, document))
        assert "contains no recorded conflicts" not in text
        assert (
            "No disagreement between positions is recorded. Model/host conflicts are listed under Execution and "
            "release." in text
        )
        assert "counterreview" not in text
    # No projection-owned sentence claims a review that did not happen.
    assert not any(
        "mandatory review" in sentence or "counterreview" in sentence
        for sentence in host_texts(result.path)
    )
    released = release_candidate(
        Path(result.path), output_root=tmp_path / "r", reviewer="TEST ONLY", reason="B"
    )
    assert released.status == "RELEASED" and inspect_bundle(Path(released.path)).valid
    assert (
        row(released.path, "model/host conflicts")
        == f"| model/host conflicts | {expected} |"
    )


@pytest.mark.parametrize("link", ["premise", "label", "summary"])
def test_B_the_same_conflict_made_material_by_one_link_blocks_release(tmp_path, link):
    task, raw = conflict_fixture(link)
    result = run_audit(task, OfflineReviewProvider(raw), output_root=tmp_path / "c")
    assert result.status == "REVIEW_REQUIRED", result.errors
    data = phase9(result.path)
    assert any(
        t["code"] == "model_host_conflict"
        and t["mandatory"]
        and t["proposition_ids"] == ["claim:optional"]
        for t in data["triggers"]
    )
    assert not any(t["code"] == "bounded_model_host_conflict" for t in data["triggers"])
    assert (
        row(result.path, "model/host conflicts")
        == "| model/host conflicts | selected judgment: 1 open; mandatory review not executed, release blocked |"
    )
    assert row(result.path, "open cause") == (
        "| open cause | mandatory review not executed: no automatic review "
        "was authorized or run in this execution |"
    )
    assert (
        release_candidate(
            Path(result.path),
            output_root=tmp_path / "r",
            reviewer="TEST ONLY",
            reason="B",
        ).status
        == "RELEASE_BLOCKED"
    )


def test_B_material_and_bounded_conflicts_are_counted_separately(tmp_path):
    task, raw = conflict_fixture("mixed")
    result = run_audit(task, OfflineReviewProvider(raw), output_root=tmp_path / "c")
    assert result.status == "REVIEW_REQUIRED"
    assert row(result.path, "model/host conflicts") == (
        "| model/host conflicts | selected judgment: 3 open "
        "(2 material, 1 not material); mandatory review not executed, "
        "release blocked |"
    )


def test_B_human_adjudication_over_a_bounded_conflict_does_not_claim_not_reviewed_or_closed(
    tmp_path,
):
    task, raw = conflict_fixture()
    result = run_audit(task, OfflineReviewProvider(raw), output_root=tmp_path / "c")
    original = phase9(result.path)["positions"][0]["position_id"]
    revision = review_candidate(
        Path(result.path),
        output_root=tmp_path / "h",
        state_dir=tmp_path / "s",
        selected_position_id=original,
        reviewer="TEST human",
        reason="select the original",
    )
    assert revision.status == "READY_FOR_RELEASE", revision.errors
    assert phase9(revision.path)["review_state"] == "adjudicated"
    assert row(revision.path, "model/host conflicts") == (
        "| model/host conflicts | selected judgment: 1 open; "
        + NOT_MATERIAL
        + "case adjudicated, conflict not closed by the adjudication |"
    )


def test_P4_registry_versions_of_the_v1_closeout_report_controls():
    assert {
        k: REGISTRY[k]
        for k in ("analysis_source", "phase9_history_review", "markdown_qa", "html_qa")
    } == {
        "analysis_source": "1.1",
        "phase9_history_review": "1.3",
        "markdown_qa": "1.1",
        "html_qa": "1.1",
    }


def test_review_causes_name_the_recorded_reason_not_the_routing_sentence():
    # Critic VC-4: the constant routing sentence of phase9_review is never presented as the cause.
    ROUTING_REASON = "Routing preserves separate scientific/taxonomy layers; no majority or provider call executed"
    completed = {"technical_status": "completed"}
    invalid = {
        "history_validation": "invalid",
        "reasons": [ROUTING_REASON],
        "uncertainty": [
            "p9position:a/claim:p1: scientific UNKNOWN",
            "Invalid Phase9 history: stored differs",
        ],
    }
    assert (
        automatic_outcome("REVIEW_REQUIRED", invalid, completed)[1]
        == "review history invalid: Invalid Phase9 history: stored differs"
    )
    positions = {
        "route": "HUMAN_REVIEW_REQUIRED",
        "reasons": [ROUTING_REASON],
        "conflicts": [{"material": True}, {"material": False}],
    }
    assert (
        automatic_outcome("REVIEW_REQUIRED", positions, completed)[1]
        == "1 material conflict(s) between positions; not automatically resolvable"
    )
    assert (
        ROUTING_REASON
        not in automatic_outcome(
            "REVIEW_REQUIRED", {"reasons": [ROUTING_REASON]}, completed
        )[1]
    )


def test_an_interrupted_mandatory_review_is_not_reported_as_not_executed():
    from inspektorium.audit.workflow.projection import _conflict_status

    review = {
        "attempts": [{"kind": "counterreview", "status": "begun"}],
        "triggers": [{"code": "model_host_conflict", "position_ids": ["p1"]}],
    }
    assessment = {
        "technical_status": "completed",
        "propositions": [{"proposition_id": "claim:p1"}],
        "model_host_conflicts": [{"scope": "composite"}],
    }
    assert (
        _conflict_status(assessment, review, "p1")
        == "selected judgment: 1 open; mandatory review interrupted, "
        "release blocked"
    )
