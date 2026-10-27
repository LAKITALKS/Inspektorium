"""Summarize decision projections step by step.

summarize.py LABEL=PROJECTION_DIR ... > summary.json

For each projection (the steps.json written by project2.py) this records, per
step, the exit code, the status fields and the SHA-256 of the step's canonical
projected JSON. Two runs are decision-identical when every step hash matches.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def canonical(value) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()


def main() -> int:
    runs = {}
    for argument in sys.argv[1:]:
        label, _, directory = argument.partition("=")
        steps = json.loads((Path(directory) / "steps.json").read_text())
        rows = []
        for step in steps:
            data = step.get("json") if isinstance(step.get("json"), dict) else {}
            rows.append(
                {
                    "label": step["label"],
                    "exit_code": step.get("exit_code"),
                    "status": data.get("status"),
                    "valid": data.get("valid"),
                    "projection_sha256": hashlib.sha256(canonical(step)).hexdigest(),
                }
            )
        runs[label] = rows
    labels = list(runs)
    reference = runs[labels[0]]
    comparison = {}
    for label in labels[1:]:
        other = runs[label]
        same = [
            a["label"] == b["label"]
            and a["projection_sha256"] == b["projection_sha256"]
            for a, b in zip(reference, other, strict=False)
        ]
        comparison[f"{labels[0]} vs {label}"] = {
            "steps": len(reference),
            "identical_steps": sum(same) if len(reference) == len(other) else 0,
            "different_steps": [
                a["label"] for a, ok in zip(reference, same, strict=False) if not ok
            ],
        }
    print(json.dumps({"comparison": comparison, "runs": runs}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
