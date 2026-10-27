"""Counter-test of projection version 2: injected faults must be reported.

projection_countertest.py --recording RUN_DIR --out DIR

Copies one golden recording, changes one review-position value in the report
of the reviewed unknown case and one source-binding text in the report of the
positive candidate, then projects both recordings with project2.py and
compares them with compare.py. The check passes only if compare.py reports
differences for both altered steps.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
POSITION = "| positions / 1 / value / 1 / evidence type | "
BINDING = "<td>code / source binding</td><td>installed bytes only"


def project(recording: Path, target: Path) -> None:
    target.mkdir(parents=True)
    output = subprocess.run(
        [sys.executable, "-I", str(TOOLS / "project2.py"), str(recording)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    (target / "steps.json").write_text(output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recording", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    steps = json.loads((args.recording / "steps.json").read_text())
    reviewed = next(
        s for s in steps if s.get("label") == "unknown: reviewed [bundle files]"
    )
    report = reviewed["files"]["report.md"]["text"]
    start = report.index(POSITION) + len(POSITION)
    end = report.index(" |", start)
    value = report[start:end]
    replacement = "unknown" if value != "unknown" else "controlled&#95;intervention"
    reviewed["files"]["report.md"]["text"] = report[:start] + replacement + report[end:]
    positive = next(
        s for s in steps if s.get("label") == "positive: candidate [bundle files]"
    )
    page = positive["files"]["report.html"]["text"]
    if BINDING not in page:
        raise SystemExit("source-binding row not found; the counter-test cannot run")
    positive["files"]["report.html"]["text"] = page.replace(
        BINDING, "<td>code / source binding</td><td>verified Git source bytes", 1
    )
    altered = args.out / "altered-recording"
    altered.mkdir()
    (altered / "steps.json").write_text(json.dumps(steps))
    project(args.recording, args.out / "original")
    project(altered, args.out / "altered")
    compared = subprocess.run(
        [
            sys.executable,
            "-I",
            str(TOOLS / "compare.py"),
            str(args.out / "original"),
            str(args.out / "altered"),
        ],
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    differing = {
        line.split("/files/")[0][5:] for line in compared if line.startswith("DIFF")
    }
    expected = {
        "unknown: reviewed [bundle files]",
        "positive: candidate [bundle files]",
    }
    summary = json.loads(compared[-1])
    result = {
        "altered_position_value": f"{value} -> {replacement}",
        "differences": summary["differences"],
        "steps_with_differences": sorted(differing),
        "passed": expected <= differing,
    }
    print(json.dumps(result, indent=1))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
