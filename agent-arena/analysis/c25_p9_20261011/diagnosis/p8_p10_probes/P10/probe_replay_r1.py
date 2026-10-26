"""Probe: K1 (replay from a copy) and replay of the sealed R1 history under 93cd64d code.
Works only on scratch copies of the TRACKED checkout files; never opens the real directories."""
import sys, json, shutil, hashlib, collections
D = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new"
S = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_p8_p10/P10"
sys.path.insert(0, D + "/src")
from pathlib import Path
import httpx
def forbid(*a, **k): raise AssertionError("network attempted")
httpx.Client.send = forbid
from agent_arena import phase10_live as live
from agent_arena.phase10_bundle import run_audit, inspect_bundle
from agent_arena.providers.anthropic_live import PROFILES
from agent_arena.task_loader import load_task
src = Path(D) / "analysis/live_smoke_20261011" / sys.argv[1]
label = sys.argv[1]
work = Path(S) / f"replay_{label}"
if work.exists(): shutil.rmtree(work)
work.mkdir()
# 1. unchanged copy -> K1
plain = work / "copy_unchanged"
shutil.copytree(src, plain, ignore=shutil.ignore_patterns("evidence", "offline_simulation", "tasks", "diagnosis*", "expectations.json", "manifest.json"))
try:
    live.LiveSession(plain, mode="replay"); print("K1 unchanged copy: OPENED (unexpected)")
except Exception as e:
    print("K1 unchanged copy:", type(e).__name__, str(e)[:200])
# 2. rebound copy (simulates the same bytes living at the canonical directory)
reb = work / "copy_rebound"
shutil.copytree(plain, reb)
auth = json.loads((reb / "authorization.json").read_text())
auth["canonical_directory"] = str(reb.resolve())
raw = json.dumps(auth, indent=2).encode()
(reb / "authorization.json").write_bytes(raw)
led = json.loads((reb / "ledger.json").read_text())
led["binding"]["authorization_fingerprint"] = hashlib.sha256(raw).hexdigest()
(reb / "ledger.json").write_text(json.dumps(led, indent=2))
before = hashlib.sha256((reb / "ledger.json").read_bytes()).hexdigest()
tasks = {t.id: t for t in (load_task(p) for p in sorted((Path(D) / "analysis/live_smoke_20261011/live_run/tasks").glob("*.json")))}
counts = collections.Counter()
rows = []
with live.LiveSession(reb, mode="replay") as session:
    for slot in session.ledger.data["terminal_keys"]:
        tid, profile, kind = slot.split("|")
        if kind != "primary": continue
        task = tasks[tid]
        prov = live.ReplayProvider(session, profile, tid, "primary", PROFILES[profile].prompt_versions[0])
        try:
            res = run_audit(task, prov, output_root=work / "out", review_state=work / "state" / tid)
            route = None
            if res.path:
                rec = json.loads((Path(res.path) / "record.json").read_text())
                p9 = rec["run_record"]["metadata"].get("phase9", {})
                route = (p9.get("route"), [(a["kind"], a["status"], a.get("reason", "")[:80]) for a in p9.get("attempts", [])])
                v = inspect_bundle(Path(res.path)).valid
            else:
                v = None
            rows.append({"slot": slot, "status": res.status, "inspect_valid": v, "route": route, "errors": [e[:300] for e in res.errors][:2]})
        except Exception as e:
            rows.append({"slot": slot, "exception": f"{type(e).__name__}: {str(e)[:300]}"})
        counts[rows[-1].get("status", "EXC")] += 1
after = hashlib.sha256((reb / "ledger.json").read_bytes()).hexdigest()
for r in rows: print(json.dumps(r)[:900])
print("COUNTS", dict(counts), "ledger_unchanged", before == after)
(work / "rows.json").write_text(json.dumps(rows, indent=1))
