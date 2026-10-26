import sys, runpy, io, contextlib
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    g = runpy.run_path("scan_multi.py")
seen = g["seen"]
from agent_arena.output_contract import parse_structured_output
tot = sum(len(v[1]) for v in seen.values())
print("total occurrences:", tot)
import collections
by_dir = collections.Counter()
for h,(t,locs,ks) in seen.items():
    for l in locs: by_dir[l.split('/')[0] + '/' + l.split('/')[1] if '/' in l else l] += 1
print(by_dir.most_common(30))
for h,(t,locs,ks) in seen.items():
    p,d = parse_structured_output(t)
    if not d.ok: print("FAIL", locs[:2], ks, d.error, repr(t[:120]))
