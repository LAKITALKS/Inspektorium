"""Holdout sealing probe: does any blob in the whole Git history match a sealed holdout commitment?"""
import json, subprocess, sys
B = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
m = json.load(open(B + "/analysis/phase5_1_holdout_freeze/holdout_public_manifest.json"))
c = json.load(open(B + "/analysis/phase5_1_holdout_freeze/private_material_commitment.json"))
targets = {v["sha256"]: f"packet {k}" for k, v in m["generated_packets"].items()}
targets[m["bundle"]["sha256"]] = "bundle"
targets[m["blank_response_sheet"]["sha256"]] = "blank_response_sheet"
for k, v in c.items():
    if isinstance(v, dict) and "sha256" in v:
        targets[v["sha256"]] = f"private {k}"
sizes = {}
for k, v in list(m["generated_packets"].items()) + [("bundle", m["bundle"]), ("blank", m["blank_response_sheet"])] + [(k, v) for k, v in c.items() if isinstance(v, dict)]:
    sizes.setdefault(v["bytes"], []).append(k)
# every blob reachable from any ref/commit in the repository object store, filtered by committed byte sizes
objs = subprocess.run(["git", "-C", B, "rev-list", "--all", "--objects"], capture_output=True, text=True, check=True).stdout.splitlines()
batch = subprocess.run(["git", "-C", B, "cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)"],
                       input="\n".join(o.split()[0] for o in objs), capture_output=True, text=True, check=True).stdout.splitlines()
paths = {o.split()[0]: (o.split(maxsplit=1)[1] if len(o.split()) > 1 else "") for o in objs}
cands = [(oid, int(sz)) for oid, typ, sz in (l.split() for l in batch) if typ == "blob" and int(sz) in sizes]
import hashlib
hits = []
for oid, sz in cands:
    data = subprocess.run(["git", "-C", B, "cat-file", "blob", oid], capture_output=True, check=True).stdout
    h = hashlib.sha256(data).hexdigest()
    if h in targets:
        hits.append((targets[h], paths.get(oid)))
print("commitments:", len(targets), "| blobs in history:", sum(1 for l in batch if ' blob ' in l), "| size-matched candidates:", len(cands), "| sha256 hits:", hits)
