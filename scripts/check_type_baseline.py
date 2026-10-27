"""Check the audit runtime against its recorded mypy baseline.

The audit runtime is type-checked in mypy's default mode (see the override in
pyproject.toml). Its known errors are recorded per file in type_baseline.json.
The check fails when any file has more errors than recorded or a new file has
errors. Fewer errors pass and are reported; refresh the baseline with --write.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = Path(__file__).with_name("type_baseline.json")
TARGET = "src/inspektorium/audit"
ERROR = re.compile(
    r"^(?P<file>[^:\n]+\.py):\d+(?::\d+)?: error: .*\[(?P<code>[a-z-]+)\]$"
)
SUMMARY = re.compile(
    r"^(?:Found (?P<count>\d+) errors? in \d+ files?|Success: no issues found)"
)


def measure() -> tuple[str, Counter[str], Counter[str]]:
    version = subprocess.run(
        [sys.executable, "-m", "mypy", "--version"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()[1]
    process = subprocess.run(
        [sys.executable, "-m", "mypy", TARGET],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if process.returncode not in (0, 1):
        message = process.stderr.strip() or process.stdout.strip()
        sys.exit(f"mypy did not run: {message}")
    files: Counter[str] = Counter()
    codes: Counter[str] = Counter()
    summary = None
    for line in process.stdout.splitlines():
        match = ERROR.match(line.strip())
        if match:
            files[match["file"]] += 1
            codes[match["code"]] += 1
        elif SUMMARY.match(line.strip()):
            summary = SUMMARY.match(line.strip())
    # A changed output format must fail the check, never pass it silently.
    if summary is None:
        sys.exit("mypy output has no summary line; cannot compare with the baseline")
    reported = int(summary["count"] or 0)
    if reported != sum(files.values()):
        sys.exit(f"parsed {sum(files.values())} errors, mypy reported {reported}")
    return version, files, codes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="record current errors")
    args = parser.parse_args()
    version, files, codes = measure()
    total = sum(files.values())
    if args.write:
        BASELINE.write_text(
            json.dumps(
                {
                    "mypy": version,
                    "target": TARGET,
                    "total": total,
                    "codes": dict(sorted(codes.items())),
                    "files": dict(sorted(files.items())),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"recorded {total} errors in {len(files)} files with mypy {version}")
        return 0
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    if version != baseline["mypy"]:
        print(f"note: baseline from mypy {baseline['mypy']}, running {version}")
    recorded = baseline["files"]
    worse = {f: n for f, n in files.items() if n > recorded.get(f, 0)}
    better = {f: n for f, n in recorded.items() if files.get(f, 0) < n}
    for name, count in sorted(worse.items()):
        print(f"more errors than recorded: {name}: {count} > {recorded.get(name, 0)}")
    for name, count in sorted(better.items()):
        print(f"fewer errors than recorded: {name}: {files.get(name, 0)} < {count}")
    print(f"mypy {version}: {total} errors in {len(files)} files")
    print(f"baseline: {baseline['total']} errors")
    return 1 if worse else 0


if __name__ == "__main__":
    raise SystemExit(main())
