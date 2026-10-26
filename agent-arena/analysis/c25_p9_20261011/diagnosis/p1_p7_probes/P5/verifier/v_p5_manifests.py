"""Phase-5.x immutability probe: do the recorded sha256 values in the 5.05e/5.05g change manifests and the
5.1 holdout freeze still match the files at HEAD (closeout: 'Historical Phase 5 artifacts remain immutable')."""
import json, hashlib, subprocess
from pathlib import Path
B = Path("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base")
h = lambda p: hashlib.sha256((B / p).read_bytes()).hexdigest() if (B / p).is_file() else None


def walk(obj, out, prefix=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdef" for c in v) and ("/" in k or k.endswith((".md", ".json", ".csv", ".yaml"))):
                out.append((k, v))
            walk(v, out, prefix + "/" + str(k))


g = json.loads((B / "analysis/phase5_05g_biaa013_final_remediation/source_change_manifest.json").read_text())
pairs = []
walk({"c": g["created_files"]}, pairs)
mods = g.get("modified_tracked_files") or {}
for k, v in (mods.items() if isinstance(mods, dict) else []):
    if isinstance(v, dict) and "sha_after" in v:
        pairs.append((v.get("file", k), v["sha_after"]))
res = [(p, h(p) == s) for p, s in pairs]
print("5.05g recorded files:", len(res), "match HEAD:", sum(ok for _, ok in res), "| mismatches:", [p for p, ok in res if not ok][:8])
e = json.loads((B / "analysis/phase5_05e_targeted_curation/source_change_manifest.json").read_text())
res = [(v["file"], h(v["file"]) == v["sha_after"]) for v in e["changed_tracked_files"].values() if isinstance(v, dict) and "sha_after" in v]
print("5.05e changed task files:", len(res), "match HEAD:", sum(ok for _, ok in res), "| differ:", [p for p, ok in res if not ok])
for p, ok in res:
    if not ok:
        log = subprocess.run(["git", "-C", str(B), "log", "--format=%h %cs %s", "--", p], capture_output=True, text=True).stdout.splitlines()
        print("   ", p, "later commits:", log[:3])
