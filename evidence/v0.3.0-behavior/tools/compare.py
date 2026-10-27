"""Compare two golden recordings step by step.

compare.py A B [--ignore-file FILE] [--json-out FILE]
Prints every differing JSON path. With --ignore-file, paths matching the given
regular expressions (one per line) are reported separately as allowed.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def walk(a, b, path, out):
    if isinstance(a, dict) and isinstance(b, dict):
        for key in sorted(set(a) | set(b)):
            if key not in a or key not in b:
                out.append((f"{path}/{key}", a.get(key, "<missing>"), b.get(key, "<missing>")))
            else:
                walk(a[key], b[key], f"{path}/{key}", out)
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for index, (x, y) in enumerate(zip(a, b)):
            walk(x, y, f"{path}[{index}]", out)
    elif a != b:
        out.append((path, a, b))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("a", type=Path)
    parser.add_argument("b", type=Path)
    parser.add_argument("--ignore-file", type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    a = json.loads((args.a / "steps.json").read_text())
    b = json.loads((args.b / "steps.json").read_text())
    patterns = []
    if args.ignore_file:
        patterns = [re.compile(line.strip()) for line in args.ignore_file.read_text().splitlines()
                    if line.strip() and not line.startswith("#")]
    diffs = []
    if len(a) != len(b):
        diffs.append(("<steps>", len(a), len(b)))
    for x, y in zip(a, b):
        if x.get("label") != y.get("label"):
            diffs.append((f"<label {x.get('label')}>", x.get("label"), y.get("label")))
            continue
        walk(x, y, x["label"], diffs)
    allowed, unexpected = [], []
    for row in diffs:
        (allowed if any(p.search(row[0]) for p in patterns) else unexpected).append(row)
    for path, x, y in unexpected:
        print("DIFF", path, "|", str(x)[:150].replace("\n", "\\n"), "|", str(y)[:150].replace("\n", "\\n"))
    print(json.dumps({"differences": len(diffs), "allowed": len(allowed), "unexpected": len(unexpected)}))
    if args.json_out:
        args.json_out.write_text(json.dumps({"allowed": [r[0] for r in allowed],
                                             "unexpected": [[str(c) for c in r] for r in unexpected]}, indent=1))
    return 1 if unexpected else 0


if __name__ == "__main__":
    raise SystemExit(main())
