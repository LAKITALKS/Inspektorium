"""Verifier: regenerate a generator into an out dir with sys.path=<src>, then cmp against committed files."""
import sys, runpy, filecmp, hashlib
from pathlib import Path
src, script, out, committed_dir = sys.argv[1:5]
names = sys.argv[5:]
sys.path.insert(0, src)
import agent_arena
print("agent_arena from", agent_arena.__file__)
sys.argv = [script, "--out-dir", out]
try:
    runpy.run_path(script, run_name="__main__")
except SystemExit as e:
    print("exit", e.code)
for n in names:
    a, b = Path(out) / n, Path(committed_dir) / n
    same = a.exists() and b.exists() and filecmp.cmp(a, b, shallow=False)
    print(f"{n}: {'SAME' if same else 'DIFF'} regen_sha={hashlib.sha256(a.read_bytes()).hexdigest()[:12] if a.exists() else None} committed_sha={hashlib.sha256(b.read_bytes()).hexdigest()[:12]}")
