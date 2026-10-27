"""Record the observable behaviour of one installed Inspektorium CLI.

Usage: golden.py --cli PATH --inspect-examples DIR --audit-examples DIR --out DIR

Every step records argv, exit code, stdout, stderr and, for audit bundles, the
bytes of every bundle file. Absolute paths are replaced by stable tokens so two
recordings can be compared field by field.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

CASES = ("positive", "negative", "unknown", "long-hostile")
REVIEWER = "Offline test operator"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Recorder:
    def __init__(self, cli: Path, out: Path, tokens: dict[str, Path]):
        self.cli, self.out, self.tokens = cli, out, tokens
        self.steps: list[dict] = []
        self.env = {k: v for k, v in os.environ.items()
                    if k not in {"ANTHROPIC_API_KEY", "OPENAI_API_KEY", "PYTHONPATH", "PYTHONHOME"}}
        self.env.update(PYTHONNOUSERSITE="1", PIP_NO_INDEX="1", PYTHONHASHSEED="0")

    def tokenize(self, text: str) -> str:
        for name, path in sorted(self.tokens.items(), key=lambda kv: -len(str(kv[1]))):
            text = text.replace(str(path.resolve()), f"<{name}>").replace(str(path), f"<{name}>")
        return text

    def run(self, label: str, args: list[str], cwd: Path) -> dict:
        proc = subprocess.run([str(self.cli), *map(str, args)], cwd=cwd, env=self.env,
                              capture_output=True, check=False)
        stdout = proc.stdout.decode("utf-8", errors="replace")
        stderr = proc.stderr.decode("utf-8", errors="replace")
        row = {"label": label, "argv": [self.tokenize(str(a)) for a in args],
               "exit_code": proc.returncode, "stdout": self.tokenize(stdout),
               "stderr": self.tokenize(stderr), "stdout_sha256": sha(proc.stdout)}
        try:
            row["json"] = json.loads(self.tokenize(stdout))
        except ValueError:
            row["json"] = None
        self.steps.append(row)
        return row

    def bundle(self, label: str, path: str | None) -> None:
        if not path:
            return
        directory = Path(path)
        files = {}
        for item in sorted(directory.rglob("*")):
            if item.is_file():
                raw = item.read_bytes()
                entry = {"sha256": sha(raw), "bytes": len(raw)}
                text = raw.decode("utf-8", errors="replace")
                if item.suffix == ".json":
                    try:
                        entry["json"] = json.loads(self.tokenize(text))
                    except ValueError:
                        entry["text"] = self.tokenize(text)
                else:
                    entry["text"] = self.tokenize(text)
                files[item.relative_to(directory).as_posix()] = entry
        self.steps.append({"label": label + " [bundle files]", "bundle": self.tokenize(path), "files": files})


def path_of(row: dict) -> str | None:
    data = row.get("json") or {}
    value = data.get("path")
    if not value:
        return None
    for name, token_path in TOKENS.items():
        value = value.replace(f"<{name}>", str(token_path))
    return value


def first_position(bundle: str) -> str | None:
    record = json.loads((Path(bundle) / "record.json").read_text())
    positions = record["run_record"]["metadata"].get("phase9", {}).get("positions", [])
    return positions[0]["position_id"] if positions else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cli", type=Path, required=True)
    parser.add_argument("--inspect-examples", type=Path, required=True)
    parser.add_argument("--audit-examples", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    work = out / "work"
    work.mkdir()
    global TOKENS
    TOKENS = {"WORK": work, "AUDIT_EXAMPLES": args.audit_examples.resolve(),
              "INSPECT_EXAMPLES": args.inspect_examples.resolve()}
    rec = Recorder(args.cli, out, TOKENS)

    # (a) Reference checker examples: stdout and --output bytes, JSON and Markdown.
    for case in sorted(p for p in args.inspect_examples.iterdir() if (p / "input.json").is_file()):
        for fmt, suffix in (("json", "json"), ("markdown", "md")):
            target = work / f"inspect-{case.name}.{suffix}"
            base = ["inspect", "--input", case / "input.json", "--proposals", case / "proposals.json",
                    "--format", fmt]
            rec.run(f"inspect {case.name} {fmt} stdout", base, work)
            row = rec.run(f"inspect {case.name} {fmt} file", [*base, "--output", target], work)
            row["output_sha256"] = sha(target.read_bytes()) if target.is_file() else None
            row["output_text"] = target.read_text() if target.is_file() else None

    # (b) Audit workflow per case.
    bundles = work / "bundles"
    ex = args.audit_examples
    for case in CASES:
        task, recording = ex / f"{case}-task.json", ex / f"{case}-recording.json"
        rec.run(f"{case}: validate", ["audit", "validate", "--task", task], work)
        run = rec.run(f"{case}: run --offline", ["audit", "run", "--offline", "--task", task,
                                                 "--recording", recording, "--output-root", bundles], work)
        candidate = path_of(run)
        rec.bundle(f"{case}: candidate", candidate)
        if not candidate:
            continue
        rec.run(f"{case}: inspect candidate", ["audit", "inspect", "--bundle", candidate], work)
        position = first_position(candidate)
        review_args = ["audit", "review", "--bundle", candidate, "--state-dir", work / f"state-{case}",
                       "--output-root", bundles, "--select", position or "none", "--reviewer", REVIEWER,
                       "--reason", "Synthetic recorded review"]
        if case == "unknown":
            review_args += ["--correction", ex / "positive-recording.json"]
        review = rec.run(f"{case}: review", review_args, work)
        reviewed = path_of(review)
        rec.bundle(f"{case}: reviewed", reviewed)
        if reviewed:
            rec.run(f"{case}: inspect reviewed", ["audit", "inspect", "--bundle", reviewed], work)
        for label, bundle in ((f"{case}: release candidate", candidate),
                              (f"{case}: release reviewed", reviewed)):
            if not bundle:
                continue
            before = {p.name: sha(p.read_bytes()) for p in Path(bundle).iterdir() if p.is_file()}
            released = rec.run(label, ["audit", "release", "--bundle", bundle, "--output-root", bundles,
                                       "--reviewer", REVIEWER, "--reason", "Explicit synthetic release"], work)
            after = {p.name: sha(p.read_bytes()) for p in Path(bundle).iterdir() if p.is_file()}
            released["source_bundle_unchanged"] = before == after
            target = path_of(released)
            rec.bundle(label + " output", target)
            if target:
                rec.run(label + " inspect", ["audit", "inspect", "--bundle", target], work)

    # (c) Counter-checks.
    positive = next((path_of(s) for s in rec.steps if s.get("label") == "positive: run --offline"), None)
    if positive:
        tampered = work / "tampered"
        shutil.copytree(positive, tampered)
        with (tampered / "report.md").open("a", encoding="utf-8") as stream:
            stream.write("\nUnapproved report mutation.\n")
        rec.run("counter: tampered report rejected", ["audit", "inspect", "--bundle", tampered], work)
        tampered_record = work / "tampered-record"
        shutil.copytree(positive, tampered_record)
        data = json.loads((tampered_record / "record.json").read_text())
        data["run_record"]["run_id"] = data["run_record"]["run_id"] + "-forged"
        (tampered_record / "record.json").write_text(json.dumps(data))
        rec.run("counter: tampered record rejected", ["audit", "inspect", "--bundle", tampered_record], work)
    rec.run("counter: live without authorization", ["audit", "run", "--live", "--task", ex / "positive-task.json",
                                                    "--authorization-dir", work / "absent-authorization",
                                                    "--profile", "claude-haiku-5-5@3", "--output-root", bundles], work)
    rec.run("counter: missing mode", ["audit", "run", "--task", ex / "positive-task.json", "--output-root", bundles], work)
    rec.run("counter: conflicting modes", ["audit", "run", "--offline", "--live", "--task", ex / "positive-task.json",
                                           "--recording", ex / "positive-recording.json", "--output-root", bundles], work)
    source = args.inspect_examples / "01_supported"
    raw = (source / "input.json").read_text()
    dup_input = work / "duplicate-key-input.json"
    dup_input.write_text(raw.replace("{", '{"answer": null, ', 1))
    rec.run("counter: duplicate key in inspect input", ["inspect", "--input", dup_input, "--proposals",
                                                         source / "proposals.json", "--format", "json"], work)
    dup_proposals = work / "duplicate-key-proposals.json"
    dup_proposals.write_text((source / "proposals.json").read_text().replace("{", '{"findings": [], ', 1))
    rec.run("counter: duplicate key in inspect proposals", ["inspect", "--input", source / "input.json",
                                                             "--proposals", dup_proposals, "--format", "json"], work)
    task_raw = (ex / "positive-task.json").read_text()
    dup_task = work / "duplicate-key-task.json"
    dup_task.write_text(task_raw.replace("{", '{"id": "duplicate-first", ', 1))
    rec.run("counter: duplicate key in audit task", ["audit", "validate", "--task", dup_task], work)
    rec.run("counter: unknown command", ["frobnicate"], work)

    (out / "steps.json").write_text(json.dumps(rec.steps, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"steps": len(rec.steps), "out": str(out)}))
    return 0


TOKENS: dict[str, Path] = {}

if __name__ == "__main__":
    raise SystemExit(main())
