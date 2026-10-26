"""Run the real ``inspektorium`` CLI of one installed product venv on every case.

For each case and each format (json, markdown) the tool pre-creates the output
file with known bytes, runs ``inspektorium inspect --input ... --proposals ...
--format <fmt> --output <file>`` as a subprocess with a credential-free
environment and the network guard log enabled, and records the exit code,
standard output/error, the output file state and the guard records that the
subprocess wrote. Nothing is inferred: every row is built from process output.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path
from typing import Any

from common import read_json, scrubbed_env, sha256_bytes, sha256_file

FORMATS = (("json", "report.json"), ("markdown", "report.md"))
PRESEED = "PRE-EXISTING OUTPUT FILE (evidence harness) {case} {fmt}\n"
TIMEOUT_SECONDS = 120


def _guard_records(log: Path, offset: int) -> tuple[list[dict[str, Any]], int]:
    if not log.exists():
        return [], offset
    with log.open("rb") as handle:
        handle.seek(offset)
        data = handle.read()
    records = [json.loads(line) for line in data.decode("utf-8").splitlines() if line]
    return records, offset + len(data)


def classify(row: dict[str, Any]) -> str:
    """CLI-level outcome for one invocation."""

    if row.get("timeout"):
        return "TIMEOUT"
    code = row["exit_code"]
    if code == 0:
        if row["output_written"] and not row["stdout"]:
            return "ACCEPTED"
        return "ACCEPTED_IRREGULAR"
    if "Traceback (most recent call last)" in row["stderr"]:
        return "CRASHED"
    clean = (
        code == 2
        and row["stderr"].startswith("inspektorium: error:")
        and row["stdout"] == ""
        and row["output_preserved"]
    )
    if clean:
        return "REJECTED_CLEAN"
    if not row["output_preserved"]:
        return "REJECTED_OUTPUT_DAMAGED"
    return "REJECTED_IRREGULAR"


def run_case(
    executable: Path,
    case_dir: Path,
    out_dir: Path,
    case_id: str,
    guard_log: Path,
    cwd: Path,
) -> list[dict[str, Any]]:
    rows = []
    out_dir.mkdir(parents=True, exist_ok=True)
    for fmt, name in FORMATS:
        target = out_dir / name
        preseed = PRESEED.format(case=case_id, fmt=fmt).encode("ascii")
        target.write_bytes(preseed)
        command = [
            str(executable),
            "inspect",
            "--input",
            str(case_dir / "input.json"),
            "--proposals",
            str(case_dir / "proposals.json"),
            "--format",
            fmt,
            "--output",
            str(target),
        ]
        offset = guard_log.stat().st_size if guard_log.exists() else 0
        env = scrubbed_env({"EVIDENCE_NETGUARD_LOG": str(guard_log)})
        started = time.monotonic()
        timeout = False
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                env=env,
                capture_output=True,
                timeout=TIMEOUT_SECONDS,
                check=False,
            )
            stdout = result.stdout.decode("utf-8", errors="backslashreplace")
            stderr = result.stderr.decode("utf-8", errors="backslashreplace")
            exit_code: int | None = result.returncode
        except subprocess.TimeoutExpired:
            stdout, stderr, exit_code, timeout = "", "", None, True
        duration = round(time.monotonic() - started, 3)
        records, _ = _guard_records(guard_log, offset)
        data = target.read_bytes() if target.exists() else b""
        row: dict[str, Any] = {
            "case": case_id,
            "format": fmt,
            "argv": ["inspektorium", *command[1:]],
            "exit_code": exit_code,
            "timeout": timeout,
            "duration_s": duration,
            "stdout": stdout,
            "stderr": stderr,
            "output_exists": target.exists(),
            "output_sha256": sha256_bytes(data) if target.exists() else None,
            "output_bytes": len(data),
            "output_preserved": data == preseed,
            "output_written": target.exists() and data != preseed and len(data) > 0,
            "guard_armed_records": sum(r.get("event") == "armed" for r in records),
            "guard_refused_records": sum(r.get("event") == "refused" for r in records),
            "guard_other_records": sum(
                r.get("event") not in ("armed", "refused") for r in records
            ),
        }
        row["cli_outcome"] = classify(row)
        rows.append(row)
    return rows


def run_all(
    venv: Path, cases_dir: Path, out_dir: Path, guard_log: Path
) -> list[dict[str, Any]]:
    executable = venv / "bin" / "inspektorium"
    if not executable.exists():
        raise SystemExit(f"missing console script: {executable}")
    manifest = read_json(cases_dir / "cases_manifest.json")
    cwd = out_dir / "_cwd"
    cwd.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for entry in manifest["cases"]:
        case_dir = cases_dir / entry["id"]
        if sha256_file(case_dir / "input.json") != entry["input_sha256"]:
            raise SystemExit(f"input hash mismatch for {entry['id']}")
        if sha256_file(case_dir / "proposals.json") != entry["proposals_sha256"]:
            raise SystemExit(f"proposals hash mismatch for {entry['id']}")
        rows.extend(
            run_case(
                executable, case_dir, out_dir / entry["id"], entry["id"], guard_log, cwd
            )
        )
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--venv", required=True)
    parser.add_argument("--cases", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--guard-log", required=True)
    args = parser.parse_args(argv)
    rows = run_all(
        Path(args.venv), Path(args.cases), Path(args.out), Path(args.guard_log)
    )
    for row in rows:
        print(row["case"], row["format"], row["exit_code"], row["cli_outcome"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
