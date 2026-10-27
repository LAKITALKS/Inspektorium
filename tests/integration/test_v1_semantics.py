"""v1 closeout, Stage S: whole-claim summary semantics, contract versions, shared live review state,
exact recorded bytes and the package version.

SYNTHETIC TEST FIXTURES only, built from examples/phase10. Offline; live mode only through the
MockTransport helpers of tests/test_phase10_live.py with synthetic authorizations in tmp_path.
"""
from __future__ import annotations

import copy
import hashlib
import json
import tomllib
from pathlib import Path

import pytest
from click.testing import CliRunner

from inspektorium.audit.phase10_cli import audit
from inspektorium.audit.phase10_bundle import inspect_bundle, release_candidate, run_audit
from inspektorium.audit.phase9_runtime import OfflineReviewProvider
from inspektorium.audit.schemas import Task
from tests.integration.test_phase10_live import (  # noqa: F401  (autouse fixture isolates the pinned live history)
    HAIKU, P8, Transport, _authorize, _isolated_live_history, _recording, _session, _task, message,
)
from inspektorium.audit import phase10_live as live

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "examples" / "audit"


# ---------------------------------------------------------------- NEW-VB-1 fixtures

def _base():
    task = json.loads((EXAMPLES / "positive-task.json").read_text())
    task["id"] = "v1-semantics-synthetic"
    task["title"] = "SYNTHETIC TEST FIXTURE v1 semantics"
    data = json.loads((EXAMPLES / "optional-unknown-recording.json").read_text())
    data["forensic_record"]["record_id"] = "SYNTHETIC-TEST-FIXTURE-v1-semantics"
    return task, data


def _prop(led, pid):
    return next(p for p in led["propositions"] if p["proposition_id"] == pid)


def _bind(prop, observation, directness, bid):
    prop["evidence_bindings"] = [{"binding_id": bid, "proposition_id": prop["proposition_id"], "evidence_id": "e1",
                                  "directness": directness, "observation": observation,
                                  "reason": "SYNTHETIC binding"}]


def _client_summary(fr, led, pid, asserted, whole, cid="client-opt"):
    o = _prop(led, pid)
    if not any(f["finding_id"] == pid for f in fr["findings"]):
        fr["findings"].append({"finding_id": pid, "provenance_id": "origin", "proposition": o["proposition_text"],
                               "verdict_summary": "", "supporting_evidence_ids": ["e1"], "contrary_evidence_ids": [],
                               "allowed_summary_strength": "not_assessed", "confidence_status": "",
                               "predicted_label": None})
    fr["client_findings"].append({"client_finding_id": cid, "parent_finding_id": pid,
                                  "display_claim": o["proposition_text"], "client_explanation": "",
                                  "client_strength": "not_assessed", "referenced_evidence_ids": ["e1"],
                                  "provenance_id": "origin", "value_claims": [], "client_negative_assertions": []})
    t = copy.deepcopy(next(t for t in led["transformations"] if t["stage"] == "summary"))
    t.update(transformation_id="summary-" + cid, target_id=cid, from_proposition_ids=[pid],
             from_text=o["proposition_text"], to_text=o["proposition_text"],
             from_attributes=copy.deepcopy(o["attributes"]), to_attributes=copy.deepcopy(o["attributes"]),
             asserted_state=asserted, asserts_whole_claim=whole)
    led["transformations"].append(t)


def _or_disjunct(fr, led, operator):
    """Second REQUIRED proposition claim:p2 combined with claim:p1 by `operator`."""
    p2 = copy.deepcopy(_prop(led, "claim:p1"))
    p2["proposition_id"] = "claim:p2"
    _bind(p2, "inconclusive", "partial", "b-p2")
    p2["reported_verdict"] = "supported"
    led["propositions"].insert(1, p2)
    led["required_proposition_ids"] = ["claim:p1", "claim:p2"]
    led["logic"] = {"operator": operator, "children": [{"operator": "leaf", "proposition_id": "claim:p1"},
                                                       {"operator": "leaf", "proposition_id": "claim:p2"}]}
    f2 = copy.deepcopy(fr["findings"][0])
    f2["finding_id"] = "claim:p2"
    fr["findings"].append(f2)
    for stage in ("extraction", "search_question", "internal"):
        t = copy.deepcopy(next(t for t in led["transformations"] if t["stage"] == stage and t["target_id"] == "claim:p1"))
        t.update(transformation_id=stage + "-p2", target_id="claim:p2", from_proposition_ids=["claim:p2"])
        led["transformations"].append(t)


def _children(prop):
    """Population mismatch: e1 is about adults, so the host derivation is 'unsupported'."""
    prop["proposition_text"] = "intervention X reduces event Q in children."
    prop["attributes"]["population"] = "children"


def variant(name):
    task, data = _base()
    fr = data["forensic_record"]
    led = fr["phase8"]
    o = _prop(led, "claim:optional")
    if name == "C0_no_conflict":
        pass
    elif name == "N1_optional_inconclusive_model_supported":
        _bind(o, "inconclusive", "partial", "b-opt")
        o["reported_verdict"] = "supported"
    elif name == "N4_required_or_disjunct_conflict":
        _or_disjunct(fr, led, "or")
    elif name in ("M4b_whole_claim_summary_divergent_optional", "M4c_partial_summary_divergent_optional"):
        _children(o)
        _bind(o, "support", "direct", "b-opt")
        o["reported_verdict"] = "supported"
        _client_summary(fr, led, "claim:optional", "supported", name.startswith("M4b"))
    elif name == "M4d_whole_claim_summary_agreed_unsupported_optional":
        _children(o)
        _bind(o, "support", "direct", "b-opt")
        o["reported_verdict"] = "unsupported"  # the model agrees with the host
        _client_summary(fr, led, "claim:optional", "supported", True)
    elif name == "M4e_whole_claim_summary_from_unsupported_or_disjunct":
        _or_disjunct(fr, led, "or")
        p2 = _prop(led, "claim:p2")
        _children(p2)
        _bind(p2, "support", "direct", "b-p2")
        p2["reported_verdict"] = "unsupported"  # the model agrees with the host
        for f in fr["findings"]:
            if f["finding_id"] == "claim:p2":
                f["proposition"] = p2["proposition_text"]
        for t in led["transformations"]:
            if t["target_id"] != "claim:p2":
                continue
            if t["stage"] == "extraction":
                t["to_text"] = p2["proposition_text"]
                t["to_attributes"] = copy.deepcopy(p2["attributes"])
                t["from_attributes"] = copy.deepcopy(p2["attributes"])
            else:
                t["from_text"] = p2["proposition_text"]
                t["from_attributes"] = copy.deepcopy(p2["attributes"])
                t["to_attributes"] = copy.deepcopy(p2["attributes"])
                if t["stage"] == "internal":
                    t["to_text"] = p2["proposition_text"]
                if t["stage"] == "search_question":
                    t["to_text"] = p2["search_question"]
        _client_summary(fr, led, "claim:p2", "supported", True, cid="client-p2")
    else:
        raise KeyError(name)
    return Task.model_validate(task), json.dumps(data)


def _audit(tmp_path, name):
    task, raw = variant(name)
    return run_audit(task, OfflineReviewProvider(raw), output_root=tmp_path / "c")


def _run_record(result):
    return json.loads((Path(result.path) / "record.json").read_text())["run_record"]


# ---------------------------------------------------------------- NEW-VB-1

def test_M4b_conflict_on_the_source_of_a_whole_claim_summary_is_material(tmp_path):
    result = _audit(tmp_path, "M4b_whole_claim_summary_divergent_optional")
    assert result.status == "REVIEW_REQUIRED", result.status
    triggers = _run_record(result)["metadata"]["phase9"]["triggers"]
    assert ("model_host_conflict", True) in {(t["code"], t["mandatory"]) for t in triggers}
    assert not any(t["code"] == "bounded_model_host_conflict" for t in triggers)
    assert release_candidate(Path(result.path), output_root=tmp_path / "r", reviewer="T",
                             reason="x").status == "RELEASE_BLOCKED"


def test_M4c_the_partial_summary_counterpart_stays_material(tmp_path):
    assert _audit(tmp_path, "M4c_partial_summary_divergent_optional").status == "REVIEW_REQUIRED"


@pytest.mark.parametrize("name", ["M4d_whole_claim_summary_agreed_unsupported_optional",
                                  "M4e_whole_claim_summary_from_unsupported_or_disjunct"])
def test_whole_claim_supported_summary_cannot_exceed_its_source_judgment(tmp_path, name):
    result = _audit(tmp_path, name)
    assert result.status == "ANALYSIS_INCOMPLETE", result.status
    p8 = _run_record(result)["results"][0]["agent_result"]["phase8"]
    assert p8["technical_status"] == "incomplete"
    assert any(f.endswith(": partial-to-whole promotion") for f in p8["transformation_findings"])
    assert release_candidate(Path(result.path), output_root=tmp_path / "r", reviewer="T",
                             reason="x").status == "RELEASE_BLOCKED"


@pytest.mark.parametrize("name, bounded", [("C0_no_conflict", False),
                                           ("N1_optional_inconclusive_model_supported", True),
                                           ("N4_required_or_disjunct_conflict", True)])
def test_controls_without_a_decisive_output_are_unchanged(tmp_path, name, bounded):
    result = _audit(tmp_path, name)
    assert result.status == "READY_FOR_RELEASE", (result.status, result.errors)
    record = _run_record(result)
    assert not record["results"][0]["agent_result"]["phase8"]["transformation_findings"]
    codes = {(t["code"], t["mandatory"]) for t in record["metadata"]["phase9"]["triggers"] if "model_host" in t["code"]}
    assert codes == ({("bounded_model_host_conflict", False)} if bounded else set())
    assert release_candidate(Path(result.path), output_root=tmp_path / "r", reviewer="T",
                             reason="x").status == "RELEASED"


# ---------------------------------------------------------------- contract versions

def test_contract_versions_of_the_v1_closeout():
    from inspektorium.audit.phase10_pipeline import LIVE_REGISTRY, REGISTRY
    from inspektorium.audit.phase8_models import HOST_RULE_VERSION, Phase8Assessment, PropositionLedger
    from inspektorium.audit.phase8_pipeline import unavailable
    from inspektorium.audit.phase8_semantics import evaluate_phase8
    from inspektorium.audit.phase9_adjudication import AdjudicationRecord
    from inspektorium.audit.phase9_models import CONTRACT_VERSION
    from inspektorium.audit.schemas import ForensicRecord
    assert Phase8Assessment(technical_status="completed").contract_version == "AA-P8/1.3"
    assert unavailable("failed", "x")["contract_version"] == "AA-P8/1.3"
    assert HOST_RULE_VERSION == "AA-P8-HOST/1.1"
    assert PropositionLedger.model_fields["contract_version"].default == "AA-P8/1.0"  # model output format
    assert CONTRACT_VERSION == "AA-P9/1.3"
    assert AdjudicationRecord.model_fields["contract_version"].default == "AA-P9/1.3"
    record = ForensicRecord.model_validate(json.loads(_recording("positive"))["forensic_record"])
    assessment = evaluate_phase8(record)
    assert assessment.technical_status == "completed" and assessment.contract_version == "AA-P8/1.3"
    assert assessment.reasons[0].startswith("Ledger, evidence constraints and transformations evaluated "
                                            "under AA-P8/1.3 (AA-P8-HOST/1.1)")
    assert REGISTRY["phase8_semantics_taxonomy"] == LIVE_REGISTRY["phase8_semantics_taxonomy"] == "1.3"


def test_package_version_is_0_3_0():
    import inspektorium
    from inspektorium.audit.schemas import FORENSIC_RECORD_SCHEMA_VERSION
    assert inspektorium.__version__ == "0.3.0"
    assert tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"] == "0.3.0"
    assert FORENSIC_RECORD_SCHEMA_VERSION == "0.1.0"  # schema versions are not the package version


# ---------------------------------------------------------------- A-D8 shared live review state

def test_a_second_authorization_with_a_shared_review_state_is_refused_before_any_request(tmp_path):
    task, unknown = _task("unknown"), _recording("unknown")
    shared = tmp_path / "shared-state"
    first_dir = _authorize(tmp_path / "auth1", [task], auth_id="TEST-LIVE-AUTH-1")
    first = Transport(message(unknown, request_id="req_p1"), message(unknown, request_id="req_c1"))
    with _session(first_dir, first) as session:
        provider = live.LiveAuditProvider(session, HAIKU, task.id, "primary", P8)
        result = run_audit(task, provider, output_root=tmp_path / "out1", review_state=shared)
    assert result.status == "REVIEW_REQUIRED" and len(first.requests) == 2
    from inspektorium.audit.phase9_review import case_key
    assert (shared / HAIKU / "phase9" / f"{case_key(task)}.json").exists()

    second_dir = _authorize(tmp_path / "auth2", [task], auth_id="TEST-LIVE-AUTH-2")
    second = Transport(message(unknown, request_id="req_p2"), message(unknown, request_id="req_c2"))
    with _session(second_dir, second) as session:
        provider = live.LiveAuditProvider(session, HAIKU, task.id, "primary", P8)
        refused = run_audit(task, provider, output_root=tmp_path / "out2", review_state=shared)
        summary = session.summary()
    assert refused.status == "PREFLIGHT_BLOCKED" and refused.path is None
    assert refused.errors == ["Review state already holds this case from another run; "
                              "use a fresh review state per authorization."]
    assert second.requests == [] and summary["attempts"] == 0
    assert not (tmp_path / "out2").exists()

    # The same authorization resuming over its own state keeps the existing preflight.
    again = Transport(message(unknown))
    with _session(first_dir, again) as session:
        provider = live.LiveAuditProvider(session, HAIKU, task.id, "primary", P8)
        repeat = run_audit(task, provider, output_root=tmp_path / "out1", review_state=shared)
    assert repeat.status == "PREFLIGHT_BLOCKED" and "never resent" in repeat.errors[0]
    assert again.requests == []

    # A fresh review state for the second authorization runs normally.
    fresh = Transport(message(unknown, request_id="req_p3"), message(unknown, request_id="req_c3"))
    with _session(second_dir, fresh) as session:
        provider = live.LiveAuditProvider(session, HAIKU, task.id, "primary", P8)
        ok = run_audit(task, provider, output_root=tmp_path / "out3", review_state=tmp_path / "fresh-state")
    assert ok.status == "REVIEW_REQUIRED" and len(fresh.requests) == 2
    assert inspect_bundle(Path(ok.path)).valid


# ---------------------------------------------------------------- D7 exact recorded bytes

def _crlf_file(path, text):
    data = text.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8")
    assert b"\r\n" in data
    path.write_bytes(data)
    return data


def test_offline_cli_stores_the_recording_bytes_exactly(tmp_path):
    task_path = tmp_path / "task.json"
    task_path.write_text(_task("positive").model_dump_json())
    data = _crlf_file(tmp_path / "recording.json", json.dumps(json.loads(_recording("positive")), indent=2))
    run = CliRunner().invoke(audit, ["run", "--offline", "--task", str(task_path), "--recording",
                                   str(tmp_path / "recording.json"), "--output-root", str(tmp_path / "b")])
    assert run.exit_code == 0, run.output
    path = Path(json.loads(run.output)["path"])
    record = json.loads((path / "record.json").read_text())["run_record"]
    assert record["results"][0]["agent_result"]["raw_output"].encode("utf-8") == data
    digest = hashlib.sha256(data).hexdigest()
    assert digest in {p["raw_sha256"] for p in record["metadata"]["phase9"]["positions"]}
    assert inspect_bundle(path).valid


def test_review_cli_stores_the_correction_bytes_exactly(tmp_path):
    task = _task("positive")
    first = run_audit(task, OfflineReviewProvider('{"forensic_record":'), output_root=tmp_path / "b")
    assert first.status == "ANALYSIS_INCOMPLETE"
    original = json.loads((Path(first.path) / "record.json").read_text())["run_record"]["metadata"]["phase9"]
    data = _crlf_file(tmp_path / "correction.json", json.dumps(json.loads(_recording("positive")), indent=2))
    review = CliRunner().invoke(audit, ["review", "--bundle", first.path, "--state-dir", str(tmp_path / "s"),
                                      "--output-root", str(tmp_path / "b"),
                                      "--select", original["positions"][0]["position_id"],
                                      "--reviewer", "TEST human", "--reason", "complete correction",
                                      "--correction", str(tmp_path / "correction.json")])
    assert review.exit_code == 0, review.output
    path = Path(json.loads(review.output)["path"])
    phase9 = json.loads((path / "record.json").read_text())["run_record"]["metadata"]["phase9"]
    digest = hashlib.sha256(data).hexdigest()
    assert digest in {p["raw_sha256"] for p in phase9["positions"] if p["origin"] == "human_correction"}
    assert inspect_bundle(path).valid
