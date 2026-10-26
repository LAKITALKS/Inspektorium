"""Controlled canary for the network guards (no real request is sent).

Python guard: in each guarded venv, a child interpreter first checks that the
guard is armed (and stops without attempting anything if it is not), then
tries a DNS lookup of api.anthropic.com, socket.create_connection to
1.1.1.1:443, raw TCP connects to 1.1.1.1:443 and [2606:4700:4700::1111]:443
and a UDP send to 1.1.1.1:53. Each attempt must be
refused by the guard before the original socket function runs. A loopback
connection to a local listener is the positive control (must succeed).

Browser guard: a local page with a remote image and a remote stylesheet is
loaded with the same routing and host-resolver rules as the measurement; the
requests must be aborted by the route handler and counted.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from common import Sanitizer, scrubbed_env, write_json, write_jsonl

CHILD = r"""
import json, socket, sys
results = {}
try:
    import evidence_netguard as guard
    armed = guard.is_armed()
except Exception as exc:
    armed = False
results["armed"] = armed
if not armed:
    print(json.dumps(results)); sys.exit(3)

def attempt(name, func):
    try:
        func()
        results[name] = "NOT_REFUSED"
    except guard.NetworkRefusedError:
        results[name] = "refused_by_guard"
    except OSError as exc:
        results[name] = "other_oserror:" + type(exc).__name__

attempt("dns_api.anthropic.com", lambda: socket.getaddrinfo("api.anthropic.com", 443))
attempt("create_connection_1.1.1.1:443",
        lambda: socket.create_connection(("1.1.1.1", 443), 2))
def v4():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.settimeout(2); s.connect(("1.1.1.1", 443))
    finally:
        s.close()
attempt("connect_1.1.1.1:443", v4)
def v6():
    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    try:
        s.settimeout(2); s.connect(("2606:4700:4700::1111", 443))
    finally:
        s.close()
attempt("connect_[2606:4700:4700::1111]:443", v6)
def udp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.sendto(b"x", ("1.1.1.1", 53))
    finally:
        s.close()
attempt("udp_1.1.1.1:53", udp)
server = socket.socket(); server.bind(("127.0.0.1", 0)); server.listen(1)
port = server.getsockname()[1]
try:
    client = socket.create_connection(("127.0.0.1", port), 2); client.close()
    results["loopback_positive_control"] = "connected"
except OSError as exc:
    results["loopback_positive_control"] = "failed:" + type(exc).__name__
server.close()
print(json.dumps(results))
"""

PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>canary</title>
<link rel="stylesheet" href="https://api.anthropic.com/canary.css"></head>
<body><p>canary</p><img src="https://api.anthropic.com/canary.png"></body></html>
"""


def python_canary(venv: Path, log: Path) -> dict[str, Any]:
    before = log.stat().st_size if log.exists() else 0
    result = subprocess.run(
        [str(venv / "bin" / "python"), "-c", CHILD],
        capture_output=True,
        text=True,
        check=False,
        env=scrubbed_env({"EVIDENCE_NETGUARD_LOG": str(log)}),
        cwd=log.parent,
    )
    data = log.read_bytes()[before:].decode("utf-8") if log.exists() else ""
    records = [json.loads(line) for line in data.splitlines() if line.strip()]
    outcome = json.loads(result.stdout) if result.stdout.strip() else {}
    attempts = [k for k in outcome if k not in ("armed", "loopback_positive_control")]
    passed = (
        result.returncode == 0
        and outcome.get("armed") is True
        and all(outcome[k] == "refused_by_guard" for k in attempts)
        and len(attempts) == 5
        and outcome.get("loopback_positive_control") == "connected"
        and sum(r.get("event") == "refused" for r in records) == 5
    )
    return {
        "venv": str(venv),
        "exit_code": result.returncode,
        "results": outcome,
        "guard_records": records,
        "refused_records": sum(r.get("event") == "refused" for r in records),
        "passed": passed,
    }


def browser_canary(work: Path) -> dict[str, Any]:
    from browser_check import probe_pages

    page = work / "canary.html"
    page.write_text(PAGE, encoding="utf-8")
    job = {
        "case": "CANARY",
        "renderer": "none",
        "path": str(page),
        "tokens": [],
        "fields": [],
    }
    facts, network, info = probe_pages([job])
    blocked = [row for row in network if not row["own_page"]]
    return {
        "browser": info,
        "requests": network,
        "blocked_network_requests": sum(row["network"] for row in blocked),
        "probe_error": facts[0]["error"],
        "passed": len(blocked) >= 2
        and all(row["action"] == "abort" for row in blocked)
        and facts[0]["error"] is None,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--venv", action="append", required=True)
    parser.add_argument("--work", required=True)
    parser.add_argument("--results", required=True)
    args = parser.parse_args(argv)
    work = Path(args.work).resolve()
    work.mkdir(parents=True, exist_ok=True)
    log = work / "canary_netguard.jsonl"
    if log.exists():
        log.unlink()
    venvs = [Path(v).resolve() for v in args.venv]
    python_results = [python_canary(venv, log) for venv in venvs]
    browser = browser_canary(work)
    sanitizer = Sanitizer(
        {str(work): "<WORK>", **{str(v): f"<VENV:{v.name}>" for v in venvs}}
    )
    summary = {
        "python_guard": python_results,
        "browser_guard": browser,
        "passed": all(item["passed"] for item in python_results) and browser["passed"],
        "note": "A refused call never reaches the original socket function, so no "
        "packet is sent; the check aborts before any attempt if the guard is not "
        "armed. This verifies the Python hook and the browser routing only.",
    }
    results = Path(args.results)
    write_json(results / "canary.json", sanitizer.obj(summary))
    rows = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    write_jsonl(results / "canary_netguard.jsonl", sanitizer.obj(rows))
    print(json.dumps({"passed": summary["passed"]}))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
