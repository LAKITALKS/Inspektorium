"""Verifier probe for P9-F1 with the REAL R1 (-003) captures, replayed from a scratch COPY.

Safety: real files are only read (sha256 before/after). The copy's authorization is re-pinned to the
scratch directory (canonical_directory) and the copied ledger's binding fingerprint is updated to the
copied authorization bytes; nothing points to the real repository. Replay mode only (no live
session, no claim_succession, no close_for_successor, no LiveBudgetLedger write). Network is
forbidden (httpx.Client.send patched to raise), transport = MockTransport that raises, api_key='test-key',
KNOWN_CLOSED_AUTHORIZATIONS = {}.
"""
import hashlib
import json
import shutil
import sys
from pathlib import Path

D = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new"
sys.path[:0] = [D + "/src"]
OUT = Path("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_p8_p10/P9/verify/r1copy")
REAL = Path("__LOCAL_HOME__/Documents/Projects/agent-arena/analysis/live_smoke_20261011")
assert str(OUT).startswith("/private/tmp/")

import httpx


def forbid(*_a, **_k):
    raise AssertionError("network access attempted")


httpx.Client.send = forbid

from agent_arena import phase10_live as live  # noqa: E402
live.KNOWN_CLOSED_AUTHORIZATIONS = {}
import agent_arena.phase10_bundle as B  # noqa: E402
from agent_arena.providers.anthropic_live import PROFILES  # noqa: E402
from agent_arena.task_loader import load_task  # noqa: E402


def tree_hash(root: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(root.rglob("*")):
        if p.is_file():
            h.update(str(p.relative_to(root)).encode())
            h.update(hashlib.sha256(p.read_bytes()).digest())
    return h.hexdigest()


before = {d: tree_hash(REAL / d) for d in ("live_run", "repair_r1")}

shutil.rmtree(OUT, ignore_errors=True)
auth_dir = OUT / "auth"
(auth_dir / "captures").mkdir(parents=True)
for f in (REAL / "repair_r1" / "captures").iterdir():
    shutil.copyfile(f, auth_dir / "captures" / f.name)
auth = json.loads((REAL / "repair_r1" / "authorization.json").read_bytes())
auth["canonical_directory"] = str(auth_dir.resolve())
raw_auth = json.dumps(auth, indent=2).encode()
(auth_dir / "authorization.json").write_bytes(raw_auth)
ledger = json.loads((REAL / "repair_r1" / "ledger.json").read_bytes())
ledger["binding"]["authorization_fingerprint"] = hashlib.sha256(raw_auth).hexdigest()
(auth_dir / "ledger.json").write_text(json.dumps(ledger, indent=2))
ledger_bytes = (auth_dir / "ledger.json").read_bytes()

tasks = {p.stem: load_task(p) for p in sorted((REAL / "live_run" / "tasks").glob("LS-*.json"))}
for name, t in tasks.items():
    assert auth["task_bindings"][t.id] == live.task_sha256(t), name

captured = {}
orig_cc = B.create_candidate


def cap(record, **kw):
    captured["r"] = record
    return orig_cc(record, **kw)


B.create_candidate = cap

transport = httpx.MockTransport(lambda request: (_ for _ in ()).throw(AssertionError("transport used")))
rows = []
for profile in ("claude-haiku-5-5@2", "claude-sonnet-5-5@2"):
    for name, task in tasks.items():
        captured.clear()
        with live.LiveSession(auth_dir, mode="replay", transport=transport, api_key="test-key") as session:
            prov = live.ReplayProvider(session, profile, task.id, "primary", PROFILES[profile].prompt_versions[0])
            res = B.run_audit(task, prov, output_root=OUT / "bundles", review_state=OUT / "rs" / profile / name)
        p9 = captured["r"].metadata.get("phase9", {}) if "r" in captured else {}
        primary_ev = captured["r"].results[0].agent_result.execution_evidence if "r" in captured else {}
        rows.append({
            "profile": profile, "case": name, "status": res.status,
            "errors": [e[:220] for e in res.errors][:2],
            "primary_replay_verified": (primary_ev or {}).get("replay_capture_verified"),
            "primary_request_identical": (primary_ev or {}).get("replay_request_identical"),
            "p9_route": p9.get("route"), "p9_exec": p9.get("execution_status"),
            "attempts": [(a["kind"], a["status"], a["reason"][:90]) for a in p9.get("attempts", [])],
            "mh_conflict_triggers": sorted({t["code"] for t in p9.get("triggers", []) if "model_host" in t["code"]}),
        })
for r in rows:
    print(json.dumps(r))
print("copied ledger unchanged:", (auth_dir / "ledger.json").read_bytes() == ledger_bytes)
after = {d: tree_hash(REAL / d) for d in ("live_run", "repair_r1")}
print("real directories unchanged:", before == after, {k: v[:12] for k, v in after.items()})
print("status counts:", {s: sum(r["status"] == s for r in rows) for s in sorted({r["status"] for r in rows})})
