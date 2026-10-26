import sys, io, contextlib, runpy, json
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    g = runpy.run_path("scan_multi.py")
seen = g["seen"]
from agent_arena.output_contract import _strip_fence, ParseDiagnostics, _scan_outermost_object
dups = []
def hook(pairs):
    keys = [k for k, _ in pairs]
    if len(keys) != len(set(keys)):
        dups.append(sorted({k for k in keys if keys.count(k) > 1}))
    return dict(pairs)
n = 0
for h, (t, locs, ks) in seen.items():
    before = len(dups)
    text = _strip_fence(t.strip(), ParseDiagnostics())
    cand, _ = _scan_outermost_object(text)
    if cand is None: continue
    try:
        json.loads(cand, object_pairs_hook=hook); n += 1
    except Exception:
        pass
    if len(dups) > before: print("DUP", locs[:1], dups[before:][:3])
print("parsed", n, "outputs; outputs with duplicate keys (any depth):", sum(1 for _ in dups))
