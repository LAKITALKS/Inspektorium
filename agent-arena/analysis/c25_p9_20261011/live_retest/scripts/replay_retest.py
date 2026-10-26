"""Replay one new live capture of the retest offline with an installed (wheel) package; no model call.

Usage (repository root; INSTALLED_PYTHON is the clean-reproduction wheel venv of the tested commit):
  INSTALLED_PYTHON analysis/c25_p9_20261011/live_retest/scripts/replay_retest.py SCRATCH_DIR
The target follows the manifest's replay_target rule and is chosen from the ledger: the first slot in the
fixed order with a sent live review request, else the first slot with a terminal primary capture.
SCRATCH_DIR must lie outside the repository; the Phase-9 state and the replay bundle go there. Network
access is blocked (httpx sends and socket connects are refused and counted). The whole retest directory
is hashed before and after the replay; the result is compared with the live bundle and then written to
evidence/replay_check.json (the only write into the retest directory, made after the comparison; a
later repetition is appended to evidence/replay_checks_later.jsonl). A failed replay is recorded too.
"""
import hashlib
import json
import os
import socket
import sys
import traceback
import uuid
from pathlib import Path

import httpx

ATTEMPTS = []


def forbid(*_args, **_kwargs):
    ATTEMPTS.append("network")
    raise AssertionError("network access attempted during replay")


httpx.Client.send = forbid
socket.socket.connect = forbid
socket.socket.connect_ex = forbid
import agent_arena  # noqa: E402
from agent_arena import phase10_live as live  # noqa: E402
from agent_arena.phase10_bundle import inspect_bundle, run_audit  # noqa: E402
from agent_arena.providers.anthropic_live import PROFILES  # noqa: E402
from agent_arena.task_loader import load_task  # noqa: E402

REPO = Path.cwd().resolve()
RETEST = (REPO / "analysis/c25_p9_20261011/live_retest").resolve()
EVIDENCE = RETEST / "evidence"


def tree():
    return {str(p.relative_to(RETEST)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(RETEST.rglob("*")) if p.is_file()}


def facts(path):
    record = json.loads((Path(path) / "record.json").read_text())
    phase8 = record["run_record"]["results"][0]["agent_result"].get("phase8") or {}
    phase9 = record["run_record"]["metadata"].get("phase9") or {}
    return {"model": phase8.get("model_composite_state"), "host": phase8.get("host_composite_state"),
            "effective": phase8.get("composite_state"), "route": phase9.get("route"),
            "attempts": [[a["kind"], a["status"]] for a in phase9.get("attempts", [])]}, record


def choose_target(manifest, ledger):
    order = [tuple(item.split()) for item in manifest["call_plan"]["order"]]
    for profile, case in order:
        prefix = f"aa-p10-live-retest-{case}|{profile}|"
        for attempt in ledger["attempts"]:
            path = RETEST / "captures" / f"{attempt['attempt_id']}.json"
            if attempt["slot_key"] in (prefix + "counterreview", prefix + "stability") and path.exists() and \
                    (json.loads(path.read_text()).get("call") or {}).get("request_sent"):
                return profile, case, "first slot with a sent live review request"
    for profile, case in order:
        if f"aa-p10-live-retest-{case}|{profile}|primary" in ledger["terminal_keys"]:
            return profile, case, "no sent live review request; first slot with a terminal primary capture"
    return None, None, "no slot with a terminal primary capture; nothing to replay"


def live_record(profile, case):
    path = EVIDENCE / "run_log.jsonl"
    found = None
    for line in path.read_text().splitlines() if path.exists() else []:
        entry = json.loads(line)
        if entry.get("event") == "start" and entry.get("accepted"):
            found = None  # only records after the last accepted start belong to the evaluated run
        elif entry.get("profile") == profile and entry.get("case") == case and entry.get("invoked"):
            found = entry
    return found


def replay(scratch):
    manifest = json.loads((RETEST / "manifest.json").read_text())
    ledger = json.loads((RETEST / "ledger.json").read_text())
    profile, case, why = choose_target(manifest, ledger)
    out = {"installation": str(Path(agent_arena.__file__).resolve().parent),
           "installation_inside_repository": REPO in Path(agent_arena.__file__).resolve().parents,
           "target": {"profile": profile, "case": case, "rule": manifest["replay_target"], "chosen_because": why}}
    if profile is None:
        return out
    entry = live_record(profile, case)
    task = load_task(RETEST / "tasks" / f"{case}.json")
    with live.LiveSession(RETEST, mode="replay") as session:
        provider = live.ReplayProvider(session, profile, task.id, "primary", PROFILES[profile].prompt_versions[0])
        result = run_audit(task, provider, output_root=scratch / "bundle", review_state=scratch / "state" / str(uuid.uuid4()))
    replay_facts, record = facts(result.path) if result.path else ({}, {})
    live_bundle = RETEST / entry["bundle"] if entry and entry.get("bundle") else None
    live_facts = facts(live_bundle)[0] if live_bundle and (live_bundle / "record.json").exists() else None
    evidence = ((record.get("run_record", {}).get("results") or [{}])[0].get("agent_result", {})
                .get("execution_evidence", {}))
    out.update({"status": result.status, "live_status": entry.get("status") if entry else None,
                "live_bundle": entry.get("bundle") if entry else None, "errors": result.errors[:3],
                "bundle_valid": inspect_bundle(Path(result.path)).valid if result.path else None,
                "execution_mode": record.get("execution_mode"), "current_execution": evidence.get("current_execution"),
                "new_generation": evidence.get("new_generation"),
                "capture_verified": evidence.get("replay_capture_verified"),
                "request_identical": evidence.get("replay_request_identical"),
                "replay_ledger_sha256": evidence.get("replay_ledger_sha256"),
                "original_request_id": evidence.get("request_id"),
                "replay_facts": replay_facts, "live_facts": live_facts,
                "same_as_live": live_facts is not None and live_facts == replay_facts
                and entry.get("status") == result.status,
                "provider_network_attempts": provider.network_attempts})
    return out


def main(scratch):
    scratch = Path(scratch).resolve()
    if scratch == REPO or REPO in scratch.parents:
        sys.exit("SCRATCH_DIR must lie outside the repository")
    before = tree()
    try:
        out = replay(scratch)
    except Exception as exc:  # recorded, never hidden
        out = {"failed": True, "error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()[-3000:]}
    out["retest_directory_unchanged"] = tree() == before
    out["blocked_network_attempts"] = len(ATTEMPTS)
    out["network_measurement"] = ("httpx.Client.send, socket.connect and socket.connect_ex are replaced by a refusing "
                                  "counter before the package is imported")
    text = json.dumps(out, indent=2, ensure_ascii=False) + "\n"
    EVIDENCE.mkdir(exist_ok=True)
    try:
        fd = os.open(EVIDENCE / "replay_check.json", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        with os.fdopen(fd, "w") as handle:
            handle.write(text)
    except FileExistsError:
        with (EVIDENCE / "replay_checks_later.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(out, ensure_ascii=False) + "\n")
    print(text)
    return 0 if not out.get("failed") else 1


if __name__ == "__main__":
    if not (REPO / ".git").exists() or not RETEST.exists():
        sys.exit("run from the repository root after the run")
    if len(sys.argv) != 2:
        sys.exit("usage: replay_retest.py SCRATCH_DIR")
    sys.exit(main(sys.argv[1]))
