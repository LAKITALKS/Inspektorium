"""Verifier: case-content drift since the P4 tag (read-only git show; no checkout)."""
import subprocess
import sys

import yaml

B = sys.argv[1]


def show(rev, path):
    r = subprocess.run(["git", "-C", B, "show", f"{rev}:{path}"], capture_output=True, text=True)
    return yaml.safe_load(r.stdout) if r.returncode == 0 else None


files = [f for f in subprocess.run(["git", "-C", B, "ls-tree", "--name-only", "v0.7.1-run-harness",
                                    "tasks/study_forensics/"], capture_output=True, text=True).stdout.split()
         if f.endswith(".yaml")]
diff = {"prompt": [], "context": [], "gold_label": []}
for f in files:
    a, b = show("v0.7.1-run-harness", f), show("c4c2a4c", f)
    for k in diff:
        if a and b and a.get(k) != b.get(k):
            diff[k].append(f.rsplit("/", 1)[-1][:7])
print("cases at v0.7.1:", len(files), "| changed since v0.7.1 ->", diff)
