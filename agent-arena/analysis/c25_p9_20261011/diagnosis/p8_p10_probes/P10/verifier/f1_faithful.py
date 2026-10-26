"""Verifier probe for F1: replay of the sealed history with UNCHANGED authorization and ledger bytes.

Works on scratch copies of the TRACKED checkout files only. The canonical_directory equality is bypassed
in-process by a json shim (only the parsed dict is rebound; raw bytes, fingerprint and ledger stay original).
Network is forbidden. Usage: f1_faithful.py <live_run|repair_r1> [fix]
"""
import collections
import hashlib
import json as _json
import shutil
import sys
from pathlib import Path

D = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new"
S = Path("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_p8_p10/P10/verifier")
sys.path.insert(0, D + "/src")
import httpx  # noqa: E402


def forbid(*a, **k):
    raise AssertionError("network attempted")


httpx.Client.send = forbid
from agent_arena import phase10_live as live  # noqa: E402
assert live.__file__.startswith(D), live.__file__
live.send_request = forbid
from agent_arena.phase10_bundle import inspect_bundle, run_audit  # noqa: E402
from agent_arena.providers.anthropic_live import PROFILES  # noqa: E402
from agent_arena.task_loader import load_task  # noqa: E402

label = sys.argv[1]
fix = len(sys.argv) > 2 and sys.argv[2] == "fix"
src = Path(D) / "analysis/live_smoke_20261011" / label
work = S / f"f1_{label}{'_fix' if fix else ''}"
if work.exists():
    shutil.rmtree(work)
work.mkdir(parents=True)
copy = work / "auth"
copy.mkdir()
for name in ("authorization.json", "ledger.json"):
    shutil.copy2(src / name, copy / name)
shutil.copytree(src / "captures", copy / "captures")
real_canonical = _json.loads((src / "authorization.json").read_bytes())["canonical_directory"]


class Shim:
    """json module stand-in: rebinds only the parsed canonical_directory of this authorization."""

    def __getattr__(self, name):
        return getattr(_json, name)

    def loads(self, raw, *a, **k):
        value = _json.loads(raw, *a, **k)
        if isinstance(value, dict) and value.get("canonical_directory") == real_canonical:
            value = dict(value, canonical_directory=str(copy.resolve()))
        return value


live.json = Shim()
if fix:
    orig = live.review_allowance

    def patched(session, slot, *, claim=False):
        if session.mode != "live" and not session.authorization.get("review_caps") \
                and slot.split("|")[2] != "primary" and slot not in session.ledger.data["terminal_keys"]:
            return "No live review was executed for this slot; the review stays open"
        return orig(session, slot, claim=claim)

    live.review_allowance = patched


def shas():
    return {p.relative_to(copy).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(copy.rglob("*")) if p.is_file()}


before = shas()
auth_sha = hashlib.sha256((copy / "authorization.json").read_bytes()).hexdigest()
print("authorization sha (unchanged bytes):", auth_sha, "pinned:",
      live.KNOWN_CLOSED_AUTHORIZATIONS[_json.loads((copy / "authorization.json").read_bytes())["authorization_id"]]["authorization_sha256"] == auth_sha)
tasks = {t.id: t for t in (load_task(p) for p in sorted((Path(D) / "analysis/live_smoke_20261011/live_run/tasks").glob("*.json")))}
counts = collections.Counter()
rows = []
with live.LiveSession(copy, mode="replay") as session:
    print("session fingerprint == original:", session.fingerprint == auth_sha)
    for slot in session.ledger.data["terminal_keys"]:
        tid, profile, kind = slot.split("|")
        if kind != "primary":
            continue
        prov = live.ReplayProvider(session, profile, tid, "primary", PROFILES[profile].prompt_versions[0])
        res = run_audit(tasks[tid], prov, output_root=work / "out", review_state=work / "state" / tid)
        row = {"slot": slot, "status": res.status, "path": res.path, "errors": [e[:240] for e in res.errors[:2]]}
        if res.path:
            rec = _json.loads((Path(res.path) / "record.json").read_text())
            p9 = rec["run_record"]["metadata"]["phase9"]
            row.update(route=p9.get("route"), mandatory=p9.get("mandatory"),
                       attempts=[(a["kind"], a["status"], a.get("reason", "")[:70]) for a in p9.get("attempts", [])],
                       mode=rec["execution_mode"], inspect=inspect_bundle(Path(res.path)).valid)
        rows.append(row)
        counts[res.status] += 1
after = shas()
for r in rows:
    print(_json.dumps(r)[:700])
print("COUNTS", dict(counts), "auth dir byte-identical:", before == after,
      "files written into auth dir:", sorted(set(after) - set(before)))
(work / "rows.json").write_text(_json.dumps(rows, indent=1))
