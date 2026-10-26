"""A5/A6 scripted demo on SYNTHETIC authorizations in scratch only (counting httpx.MockTransport doubles).

SYNTHETIC TEST FIXTURE — not an empirical model response: every model answer here is built from
examples/phase10/positive-recording.json via the helpers in tests/test_phase10_live.py.

Isolation: KNOWN_CLOSED_AUTHORIZATIONS is cleared in-process only (as the autouse fixture of tests/test_phase10_live.py
does); LiveSession in live mode is refused for any directory outside BASE or any authorization naming the real
live_smoke_20261011 / c25_p9_20261011 trees. Real network is refused and counted by netguard.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import traceback
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
S = TOOLS.parent
REPO = Path("__LOCAL_HOME__/Documents/Projects/agent-arena")
sys.path.insert(0, str(TOOLS))
import netguard  # noqa: E402

netguard.allow_mock_transport(True)
sys.path.insert(0, str(REPO))
from agent_arena import phase10_live as live  # noqa: E402

live.KNOWN_CLOSED_AUTHORIZATIONS.clear()
from tests import test_phase10_live as T  # noqa: E402

live.KNOWN_CLOSED_AUTHORIZATIONS.clear()
import agent_arena  # noqa: E402
from agent_arena.phase10_bundle import inspect_bundle, run_audit  # noqa: E402
from agent_arena.phase9_review import case_key  # noqa: E402
from agent_arena.phase9_runtime import execute_review  # noqa: E402
from agent_arena.providers.anthropic_live import PROFILES  # noqa: E402
from agent_arena.schemas import RunRecord  # noqa: E402

BASE = (S / "a5a6").resolve()
if BASE.exists():
    shutil.rmtree(BASE)
BASE.mkdir(parents=True)
NOTICE = "SYNTHETIC TEST FIXTURE — not an empirical model response"
(BASE / "SYNTHETIC_TEST_FIXTURE.txt").write_text(NOTICE + ". Throwaway authorizations for A5/A6 only.\n")
_orig_init = live.LiveSession.__init__
LIVE_SESSIONS = []


def guarded(self, directory, *, mode, **kw):
    d = Path(directory).resolve()
    if mode == "live":
        assert str(d).startswith(str(BASE)), f"REFUSED: live session outside scratch: {d}"
        text = (d / "authorization.json").read_text()
        assert "live_smoke_20261011" not in text and "c25_p9_20261011" not in text, "REFUSED: real history"
        for p in json.loads(text).get("predecessors") or []:
            assert str(Path(p["directory"]).resolve()).startswith(str(BASE)), "REFUSED: real predecessor"
        LIVE_SESSIONS.append(str(d.relative_to(BASE)))
    return _orig_init(self, directory, mode=mode, **kw)


live.LiveSession.__init__ = guarded
HAIKU3 = T.HAIKU3
OUT = {"fixture_notice": NOTICE, "agent_arena_version": agent_arena.__version__,
       "agent_arena_path": os.path.dirname(agent_arena.__file__)}


def tree(path):
    return {str(p.relative_to(path)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(Path(path).rglob("*")) if p.is_file()}


def two_evidence_conflict(task_id):
    """Conflict case with two evidence items so the stability variant is a real reversal (Sonnet LR-03 shape)."""
    task, raw = T._conflict_task(task_id)
    extra = "A second randomized comparison in adults (human) reported a similar reduction of event Q."
    task = task.model_copy(update={"context": task.context + " " + extra})
    data = json.loads(raw)
    record = data["forensic_record"]
    record["evidence"].append(dict(record["evidence"][0], evidence_id="e2", exact_reference=extra, text=extra))
    for proposition in record["phase8"]["propositions"]:
        proposition["evidence_bindings"].append(dict(proposition["evidence_bindings"][0], binding_id="b2",
                                                     evidence_id="e2"))
    record["phase8"]["evidence_descriptions"].append(dict(record["phase8"]["evidence_descriptions"][0],
                                                          evidence_id="e2", study_id="synthetic-second-study"))
    for finding in record["findings"]:
        finding["supporting_evidence_ids"].append("e2")
    for finding in record["client_findings"]:
        finding["referenced_evidence_ids"].append("e2")
    return task, json.dumps(data)


def successor(directory, auth_id, tasks, predecessors, *, budget):
    d = T._authorize(directory, tasks, budget=budget, ceiling=300_000, attempts=12, retries=2, profiles=(HAIKU3,),
                     auth_id=auth_id)
    auth = json.loads((d / "authorization.json").read_text())
    auth.update(schema=live.AUTH_SCHEMA_SUCCESSOR, authorization_id=auth_id, predecessors=predecessors,
                review_caps={HAIKU3: {"counterreview": 1, "stability": 1}},
                work_order="SYNTHETIC TEST FIXTURE — evidence-A A5/A6 demo; not an empirical run")
    (d / "authorization.json").write_text(json.dumps(auth, indent=2))
    return d


def close(directory, auth_id, next_id):
    s = live.close_for_successor(directory, successor_id=next_id, reason="evidence-A synthetic demo")
    return {"authorization_id": auth_id, "directory": str(Path(directory).resolve()),
            "ledger_sha256": s["ledger_sha256"], "consumed_microusd": s["reserved_or_confirmed_microusd"],
            "attempts": s["attempts"], "technical_retries": s["technical_retries"]}


def live_run(directory, task, transport, *, out, state=None):
    with T._session(directory, transport) as session:
        provider = live.LiveAuditProvider(session, HAIKU3, task.id, "primary", PROFILES[HAIKU3].prompt_versions[0])
        result = run_audit(task, provider, output_root=out, review_state=state or (directory / "phase9-state"))
        return result, session.summary(), provider.network_attempts


def phase9(path):
    return json.loads((Path(path) / "record.json").read_text())["run_record"]["metadata"]["phase9"]


def ids(path):
    r = json.loads((Path(path) / "record.json").read_text())
    return {"revision_id": r["revision_id"], "run_id": r["run_record"]["run_id"], "case_id": r["provenance"]["case_id"],
            "authorization_ids": sorted({e.get("authorization_id") for e in r["provenance"]["execution_evidence"]})}


def many(raw, n=10):
    """A double that WOULD answer up to n requests; len(requests) counts what the code actually sent."""
    return T.Transport(*[T.message(raw, request_id=f"req_extra_{i}") for i in range(n)])


def cli(*args):
    env = {k: v for k, v in os.environ.items() if k not in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY")}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    p = subprocess.run([str(REPO / ".venv/bin/python"), str(TOOLS / "aa_cli.py"), *args], capture_output=True,
                       text=True, env=env, cwd=str(S))
    guard = [ln for ln in p.stderr.splitlines() if ln.startswith("[netguard]")]
    return {"argv": ["agent-arena", *[a.replace(str(S), "<scratch>") for a in args]], "exit": p.returncode,
            "stdout": json.loads(p.stdout) if p.stdout.strip().startswith("{") else p.stdout[-600:],
            "stderr_tail": [ln for ln in p.stderr.splitlines() if not ln.startswith("[")][-3:],
            "netguard": json.loads(guard[0][len("[netguard] "):]) if guard else None}


try:
    pred = T._closed_predecessor(BASE, "pred")  # closed throwaway predecessor (1 mock request inside)
    T._pin(pred)
    OUT["setup_predecessor"] = {"authorization_id": pred["authorization_id"], "attempts": pred["attempts"]}
    task_a, raw_a = two_evidence_conflict("evidence-a-synthetic-conflict")
    succ1 = successor(BASE / "succ1", "EVIDENCE-A-SYNTH-SUCC-1", [task_a], [pred], budget=1_000_000)

    # A5 step 1: first run until the conflict review completes.
    t1 = T.Transport(T.message(raw_a, request_id="req_p"), T.message(raw_a, request_id="req_c"),
                     T.message(raw_a, request_id="req_s"))
    r1, s1, n1 = live_run(succ1, task_a, t1, out=BASE / "succ1-out")
    p1 = phase9(r1.path)
    OUT["A5_first_run"] = {"status": r1.status, "errors": r1.errors, "requests_sent_to_double": len(t1.requests),
                           "provider_network_attempts": n1, "route": p1["route"],
                           "execution_status": p1.get("execution_status"),
                           "attempts": [[a["kind"], a["status"]] for a in p1["attempts"]],
                           "valid": inspect_bundle(Path(r1.path)).valid, "bundle": str(Path(r1.path).relative_to(BASE)),
                           **ids(r1.path)}
    ledger1 = json.loads((succ1 / "ledger.json").read_text())
    OUT["A5_ledger_after_first_run"] = {"terminal_keys": ledger1["terminal_keys"],
                                        "review_cap_claims": ledger1.get("review_cap_claims"),
                                        "attempts": len(ledger1["attempts"])}
    before = tree(succ1)
    out_before = sorted(p.name for p in (BASE / "succ1-out").iterdir())

    # A5 step 2: resume the same run: same authorization, task, profile and Phase-9 state, live mode.
    tr = many(raw_a)
    rr, sr, nr = live_run(succ1, task_a, tr, out=BASE / "succ1-out")
    OUT["A5_resume_same_run"] = {"status": rr.status, "errors": rr.errors, "path": rr.path,
                                 "requests_sent_to_double": len(tr.requests), "provider_network_attempts": nr,
                                 "authorization_dir_byte_identical": tree(succ1) == before,
                                 "no_new_bundle": sorted(p.name for p in (BASE / "succ1-out").iterdir()) == out_before}

    # A5 step 3: re-execute both reviews directly with the bound record and the same state.
    direct = {}
    record_a = RunRecord.model_validate(json.loads((Path(r1.path) / "record.json").read_text())["run_record"])
    for kind in ("counterreview", "stability"):
        tr = many(raw_a)
        with T._session(succ1, tr) as session:
            reviewer = live.LiveAuditProvider(session, HAIKU3, task_a.id, kind, PROFILES[HAIKU3].prompt_versions[1])
            try:
                res = execute_review(record_a, reviewer, base_dir=succ1 / "phase9-state" / HAIKU3, authorized=True,
                                     budget_calls=2, kind=kind)
                direct[kind] = {"requests_sent_to_double": len(tr.requests),
                                "provider_network_attempts": reviewer.network_attempts,
                                "returned_attempts": [[a["kind"], a["status"]] for a in res.metadata["phase9"]["attempts"]]}
            except Exception as exc:  # noqa: BLE001
                direct[kind] = {"requests_sent_to_double": len(tr.requests), "exception": repr(exc)[:300]}
    OUT["A5_direct_review_reexecution_same_state"] = direct
    OUT["A5_authorization_dir_byte_identical_after_reexecution"] = tree(succ1) == before

    # A5 step 4: inspect 3x (API and canonical CLI) and replay 3x from a copy (API and canonical CLI).
    OUT["A5_inspect_api_3x"] = [{"valid": v.valid, "status": v.status} for v in
                                (inspect_bundle(Path(r1.path)) for _ in range(3))]
    OUT["A5_inspect_cli_3x"] = [cli("audit", "inspect", "--bundle", str(r1.path)) for _ in range(3)]
    copy = BASE / "succ1-copy"
    shutil.copytree(succ1, copy)
    copy_before = tree(copy)
    rep = []
    for i in range(3):
        with live.LiveSession(copy, mode="replay") as session:
            provider = live.ReplayProvider(session, HAIKU3, task_a.id, "primary", PROFILES[HAIKU3].prompt_versions[0])
            res = run_audit(task_a, provider, output_root=BASE / f"replay-api-{i}",
                            review_state=BASE / f"replay-api-state-{i}")
            rep.append({"status": res.status, "valid": inspect_bundle(Path(res.path)).valid,
                        "provider_network_attempts": provider.network_attempts,
                        "attempts": [[a["kind"], a["status"]] for a in phase9(res.path)["attempts"]],
                        "raw_sha256_by_origin_equal_to_live": {p["origin"]: p["raw_sha256"] for p in phase9(res.path)["positions"]}
                        == {p["origin"]: p["raw_sha256"] for p in p1["positions"]}})
    OUT["A5_replay_api_3x_from_copy"] = rep
    task_file = BASE / "task_a.json"
    task_file.write_text(task_a.model_dump_json(indent=2))
    OUT["A5_replay_cli_3x_from_copy"] = [cli("audit", "run", "--replay", "--task", str(task_file),
                                             "--authorization-dir", str(copy), "--profile", HAIKU3,
                                             "--output-root", str(BASE / f"replay-cli-{i}")) for i in range(3)]
    OUT["A5_copy_byte_identical_after_replays"] = tree(copy) == copy_before
    OUT["A5_source_authorization_byte_identical"] = tree(succ1) == before
    OUT["A5_real_network_refused_so_far"] = netguard.total()

    # A6: a new, explicitly commissioned authorization in a NEW directory re-runs the same input.
    rec1 = close(succ1, "EVIDENCE-A-SYNTH-SUCC-1", "EVIDENCE-A-SYNTH-SUCC-2")
    succ2 = successor(BASE / "succ2", "EVIDENCE-A-SYNTH-SUCC-2", [task_a], [pred, rec1], budget=600_000)
    t2 = T.Transport(T.message(raw_a, request_id="req_p2"), T.message(raw_a, request_id="req_c2"),
                     T.message(raw_a, request_id="req_s2"))
    r2, s2, n2 = live_run(succ2, task_a, t2, out=BASE / "succ2-out")
    i1, i2 = ids(r1.path), ids(r2.path)
    OUT["A6_new_authorization_same_input"] = {
        "status": r2.status, "errors": r2.errors, "requests_sent_to_double": len(t2.requests),
        "provider_network_attempts": n2, "valid": inspect_bundle(Path(r2.path)).valid,
        "attempts": [[a["kind"], a["status"]] for a in phase9(r2.path)["attempts"]],
        "first": i1, "second": i2, "revision_id_differs": i1["revision_id"] != i2["revision_id"],
        "run_id_differs": i1["run_id"] != i2["run_id"],
        "same_case_key": i1["case_id"] == i2["case_id"] == case_key(task_a),
        "same_task_in_both_records": json.loads((Path(r1.path) / "record.json").read_text())["run_record"]["task"]
        == json.loads((Path(r2.path) / "record.json").read_text())["run_record"]["task"], "bundle": str(Path(r2.path).relative_to(BASE))}
    OUT["A6_successor_claims_written_in_scratch_only"] = sorted(str(p.relative_to(BASE)) for p in
                                                                BASE.rglob("successor_claim.json"))
except Exception:  # noqa: BLE001
    OUT["fatal"] = traceback.format_exc()

OUT["live_sessions_opened_in_live_mode"] = LIVE_SESSIONS
OUT["real_network_attempts_refused"] = netguard.total()
OUT["real_network_by_kind"] = netguard.COUNT
OUT["mock_transport_sends_in_process"] = netguard.MOCK["mock_sends"]
text = json.dumps(OUT, indent=1, default=str, ensure_ascii=False).replace(str(S), "<scratch>")
(S / "a5_a6_result.json").write_text(text + "\n")
print(text)
