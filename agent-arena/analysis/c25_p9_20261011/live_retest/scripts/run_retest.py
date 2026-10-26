"""Run the frozen live retest through the canonical CLI, one subprocess per primary slot, fixed order.

Usage (repository root; started detached; the key is loaded only into this child process and is
never printed or stored):
  zsh -c 'source ~/.zshrc >/dev/null 2>&1; exec .venv/bin/python analysis/c25_p9_20261011/live_retest/scripts/run_retest.py'
Applies the manifest's pre-checks, single-start rule, cap-aware reserve rule and stop rule (manifest
call_plan.rules). Bundle paths are logged relative to the retest directory.
"""
import fcntl
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

RETEST = Path("analysis/c25_p9_20261011/live_retest")
LOG = RETEST / "evidence" / "run_log.jsonl"
CLAIM = Path("analysis/live_smoke_20261011/repair_r1/successor_claim.json")
FROZEN = ("authorization.json", "manifest.json", "expectations.json", "tasks", "scripts")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def ledger():
    path = RETEST / "ledger.json"
    return json.loads(path.read_text()) if path.exists() else None


def log(record):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    say(json.dumps({k: record.get(k) for k in ("event", "profile", "case", "invoked", "status", "stop_reasons",
                                               "reason", "precheck_errors")}, ensure_ascii=False))


def say(text):
    # Console output is a convenience; a closed or broken output channel never interrupts the run.
    try:
        print(text, flush=True)
    except (OSError, ValueError):
        pass


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True)


def prechecks(manifest):
    """Refuse to run anything that differs from the frozen, committed manifest (manifest call_plan.rules)."""
    errors = []
    head = git("rev-parse", "HEAD").stdout.strip()
    tested = manifest["tested_code_commit"]
    if git("diff", "--quiet", tested, "HEAD", "--", "src").returncode != 0:
        errors.append(f"src at HEAD {head} differs from the tested commit {tested}")
    if git("status", "--porcelain", "--", "src").stdout.strip():
        errors.append("uncommitted or untracked changes under src")
    frozen = [str(RETEST / name) for name in FROZEN]
    if git("ls-files", "--error-unmatch", *frozen).returncode != 0:
        errors.append("the frozen retest files are not all committed")
    if git("diff", "--quiet", "HEAD", "--", *frozen).returncode != 0 or git("status", "--porcelain", "--",
                                                                            *frozen).stdout.strip():
        errors.append("the frozen retest files differ from HEAD or contain untracked files")
    if sha(RETEST / "authorization.json") != manifest["authorization_sha256"]:
        errors.append("authorization.json differs from the manifest")
    for case in manifest["cases"]:
        if sha(RETEST / case["task_file"]) != case["task_file_sha256"]:
            errors.append(f"task file {case['task_file']} differs from the manifest")
    if sha(RETEST / manifest["expectations_file"]) != manifest["expectations_sha256"]:
        errors.append("expectations.json differs from the manifest")
    for name, digest in manifest["scripts"].items():
        if sha(RETEST / name) != digest:
            errors.append(f"{name} differs from the manifest")
    if not os.environ.get("ANTHROPIC_API_KEY"):  # presence only; the value is never read into any output
        errors.append("provider key not present in the runner environment")
    if CLAIM.exists():
        claim = json.loads(CLAIM.read_text())
        if (claim.get("successor_authorization_id") != manifest["authorization_id"]
                or claim.get("successor_canonical_directory") != str(RETEST.resolve())
                or claim.get("successor_authorization_sha256") != manifest["authorization_sha256"]):
            errors.append("-003 carries a successor claim that is not this retest")
    state = ledger()
    if state is not None and (state["state"] != "ACTIVE" or state["attempts"] or state.get("review_cap_claims")):
        errors.append("single start: the -004 ledger already records attempts or review claims, or is not ACTIVE; "
                      "an executed run is never restarted or resumed")
    freeze = git("log", "-1", "--format=%H", "--", str(RETEST / "manifest.json")).stdout.strip() or None
    return head, freeze, errors


def stop_reasons_for(new, after, result, max_retries):
    reasons = [f"{a['attempt_id']} {a['slot_key'].split('|')[2]} FAILED_PERMANENT" for a in new
               if a["state"] == "FAILED_PERMANENT"]
    reasons += [f"{a['attempt_id']} unresolved reservation" for a in new if a["state"] == "RESERVED_POSSIBLY_BILLABLE"]
    reasons += [f"{a['attempt_id']} overrun {a['overrun_microusd']} microUSD" for a in new if a.get("overrun_microusd")]
    if after:
        used = sum(1 for a in after["attempts"] if a.get("retry_of"))
        for key in dict.fromkeys(a["slot_key"] for a in new):
            final = [a for a in after["attempts"] if a["slot_key"] == key][-1]
            if final["state"] == "FAILED_TRANSIENT" and (not final.get("retry_of") or used >= max_retries):
                reasons.append(f"{final['attempt_id']} {key.split('|')[2]} FAILED_TRANSIENT without a permitted "
                               f"retry left ({used} of {max_retries} order-wide retries used)")
        if after["state"] != "ACTIVE":
            reasons.append(f"ledger not ACTIVE: {after.get('revocation_reason')}")
    if result.get("status") in (None, "PREFLIGHT_BLOCKED", "RELEASE_BLOCKED") or not result.get("path"):
        reasons.append(f"no bundle (status {result.get('status')})")
    return reasons


def main():
    manifest = json.loads((RETEST / "manifest.json").read_text())
    authorization = json.loads((RETEST / "authorization.json").read_text())
    total, max_retries = authorization["total_budget_microusd"], authorization["max_technical_retries"]
    budget = manifest["budget"]
    earlier = sum(1 for line in LOG.read_text().splitlines() if json.loads(line).get("event") == "start") \
        if LOG.exists() else 0
    head, freeze, errors = prechecks(manifest)
    log({"event": "start", "at": now(), "head": head, "freeze_commit": freeze, "restart": earlier > 0,
         "accepted": not errors, "precheck_errors": errors})
    if errors:
        say("pre-checks failed; nothing was run")
        return 2
    order = manifest["call_plan"]["order"]
    for index, entry in enumerate(order):
        profile, case = entry.split()
        state = ledger()
        if state and state["state"] != "ACTIVE":
            stop = f"ledger not ACTIVE before {entry}: {state.get('revocation_reason')}"
            for rest in order[index:]:
                p, c = rest.split()
                log({"profile": p, "case": c, "invoked": False, "at": now(), "reason": "not run: " + stop})
            break
        spent = state["reserved_microusd"] if state else 0
        claims = state.get("review_cap_claims", []) if state else []
        review_open = not any(k.split("|")[1:] == [profile, "counterreview"] for k in claims)
        primary = budget["max_primary_exposure_microusd"][f"{profile}|{case}"]
        reserve = budget["counterreview_reserve_microusd"][f"{profile}|{case}"] if review_open else 0
        check = {"remaining_microusd": total - spent, "primary_exposure_microusd": primary,
                 "counterreview_reserve_microusd": reserve, "counterreview_allowance_claimed": not review_open,
                 "required_microusd": primary + reserve}
        if total - spent < primary + reserve:
            log({"profile": profile, "case": case, "invoked": False, "at": now(), "reserve_check": check,
                 "reason": (f"reserve rule: remaining {total - spent} < required {primary + reserve} microUSD "
                            f"(counterreview reserve {'included' if review_open else 'not needed: allowance claimed'})")})
            continue
        n0 = len(state["attempts"]) if state else 0
        cmd = [".venv/bin/agent-arena", "audit", "run", "--live", "--task", str(RETEST / "tasks" / f"{case}.json"),
               "--authorization-dir", str(RETEST), "--profile", profile,
               "--output-root", str(RETEST / "bundles" / profile)]
        started_at, started = now(), time.time()
        proc = subprocess.run(cmd, capture_output=True, text=True)
        try:
            result = json.loads(proc.stdout)
        except ValueError:
            result = {"unparsed_stdout_tail": proc.stdout[-2000:]}
        after = ledger()
        new = after["attempts"][n0:] if after else []
        stop_reasons = stop_reasons_for(new, after, result, max_retries)
        path = result.get("path")
        bundle = os.path.relpath(path, RETEST.resolve()) if path else None
        log({"profile": profile, "case": case, "invoked": True, "started_at": started_at, "ended_at": now(),
             "wall_seconds": round(time.time() - started, 1), "exit_code": proc.returncode, "reserve_check": check,
             "status": result.get("status"), "bundle": bundle, "errors": result.get("errors"),
             "result": {k: v for k, v in result.items() if k != "path"},
             "new_attempts": [{k: a.get(k) for k in ("attempt_id", "slot_key", "state", "billing", "retry_of",
                                                     "overrun_microusd")} for a in new],
             "ledger_after": {"attempts": len(after["attempts"]), "reserved_or_confirmed_microusd":
                              after["reserved_microusd"], "state": after["state"],
                              "review_cap_claims": after.get("review_cap_claims", [])} if after else None,
             "stop_reasons": stop_reasons, "stderr_tail": proc.stderr[-800:]})
        if stop_reasons:
            for rest in order[index + 1:]:
                p, c = rest.split()
                log({"profile": p, "case": c, "invoked": False, "at": now(),
                     "reason": f"not run: stop rule after {entry}: {'; '.join(stop_reasons)}"})
            break
    log({"event": "end", "at": now()})
    return 0


if __name__ == "__main__":
    if not (Path.cwd() / ".git").exists() or not RETEST.exists():
        sys.exit("run from the repository root after the freeze")
    (RETEST / "evidence").mkdir(exist_ok=True)
    lock = (RETEST / "evidence" / ".runner-lock").open("a+")
    try:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        sys.exit("another runner holds the runner lock; nothing was run")
    sys.exit(main())
