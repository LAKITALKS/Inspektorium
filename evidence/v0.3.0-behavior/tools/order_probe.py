"""Measure the order of review positions over repeated unknown-case reviews.

order_probe.py --cli PATH --examples DIR --out DIR --runs N > order.json

Each run creates an unknown-case candidate offline, records a human
correction with `audit review` and reads the reviewed revision. It counts the
order of positions in record.json and in report.md, and whether report.md
lists the positions sorted by position ID.
"""

from __future__ import annotations

import argparse
import collections
import html
import json
import re
import subprocess
from pathlib import Path

POSITION_ID = re.compile(r"^\| positions / (\d+) / position id \| ([^|]+) \|", re.M)


def audit(cli: str, *args: str) -> dict:
    process = subprocess.run([cli, "audit", *args], capture_output=True, text=True)
    return json.loads(process.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", required=True)
    parser.add_argument("--examples", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--runs", type=int, default=16)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    examples = args.examples
    record_order: collections.Counter[str] = collections.Counter()
    report_order: collections.Counter[str] = collections.Counter()
    sorted_by_id = 0
    for index in range(args.runs):
        work = args.out / f"run{index}"
        run = audit(
            args.cli,
            "run",
            "--offline",
            "--task",
            str(examples / "unknown-task.json"),
            "--recording",
            str(examples / "unknown-recording.json"),
            "--output-root",
            str(work),
        )
        record = json.loads((Path(run["path"]) / "record.json").read_text())
        first = record["run_record"]["metadata"]["phase9"]["positions"][0][
            "position_id"
        ]
        review = audit(
            args.cli,
            "review",
            "--bundle",
            run["path"],
            "--state-dir",
            str(work / "state"),
            "--output-root",
            str(work),
            "--select",
            first,
            "--reviewer",
            "probe",
            "--reason",
            "order probe",
            "--correction",
            str(examples / "positive-recording.json"),
        )
        reviewed = Path(review["path"])
        positions = json.loads((reviewed / "record.json").read_text())["run_record"][
            "metadata"
        ]["phase9"]["positions"]
        origin = {p["position_id"]: p["origin"] for p in positions}
        record_order[" > ".join(p["origin"] for p in positions)] += 1
        text = (reviewed / "report.md").read_text()
        ids = [html.unescape(value.strip()) for _, value in POSITION_ID.findall(text)]
        ids = list(dict.fromkeys(ids))
        sorted_by_id += ids == sorted(ids)
        report_order[" > ".join(origin[i] for i in ids)] += 1
    print(
        json.dumps(
            {
                "runs": args.runs,
                "record_order": dict(record_order),
                "report_order": dict(report_order),
                "report_sorted_by_position_id": sorted_by_id,
            },
            indent=1,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
