"""Verify the public entry using installed wheels outside their source trees.

Install both built packages and the repository's Python network guard first.
This script uses recorded synthetic examples only; it installs nothing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def module_hashes(directory: Path) -> dict[str, str]:
    return {
        path.relative_to(directory).as_posix(): sha(path.read_bytes())
        for path in sorted(directory.rglob("*.py"))
    }


def verify(repo: Path, output: Path, result: dict) -> None:
    work = output / "work"
    work.mkdir()
    if work.is_relative_to(repo):
        raise ValueError("Verification output must be outside the source checkout")
    if sys.prefix == sys.base_prefix:
        raise ValueError("Use a fresh virtual environment with both wheels installed")

    env = dict(os.environ)
    for name in (
        "PYTHONPATH",
        "PYTHONHOME",
        "PYTHONSTARTUP",
        "PYTHONUSERBASE",
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "AZURE_OPENAI_API_KEY",
    ):
        env.pop(name, None)
    env.update(PYTHONNOUSERSITE="1", PIP_NO_INDEX="1")
    network_log = output / "offline-network.jsonl"
    env["EVIDENCE_NETGUARD_LOG"] = str(network_log)

    # Existing independently counterchecked monitor, not an assumed zero-call field.
    sys.path.insert(0, str(repo / "evidence/v0.1.1/tools"))
    from canary import python_canary

    canary = python_canary(Path(sys.prefix), output / "guard-canary.jsonl")
    result["network_guard_canary_passed"] = canary["passed"]
    result["network_guard_canary"] = {
        "exit_code": canary["exit_code"],
        "outcomes": canary["results"],
        "refused_records": canary["refused_records"],
    }
    if not canary["passed"]:
        raise AssertionError("The Python socket guard countercheck failed")

    def call(label: str, arguments: list[str], expected: int = 0, json_output=False):
        process = subprocess.run(
            arguments, cwd=work, env=env, text=True, capture_output=True, check=False
        )
        row = {"check": label, "exit_code": process.returncode}
        result["checks"].append(row)
        if process.returncode != expected:
            raise AssertionError(
                f"{label}: expected exit {expected}, got {process.returncode}; "
                f"{process.stderr[-1200:]} {process.stdout[-1200:]}"
            )
        if json_output:
            data = json.loads(process.stdout)
            for field in ("status", "valid", "input_valid"):
                if field in data:
                    row[field] = data[field]
            return data
        return process.stdout

    probe = """
import hashlib, importlib, importlib.metadata, json, pathlib, sys
result = {}
packages = [('inspektorium', 'inspektorium'), ('agent_arena', 'agent-arena')]
for name, distribution in packages:
    package = importlib.import_module(name)
    folder = pathlib.Path(package.__file__).resolve().parent
    result[name] = {
        'version': importlib.metadata.version(distribution),
        'inside_environment': folder.is_relative_to(pathlib.Path(sys.prefix).resolve()),
        'modules': {p.relative_to(folder).as_posix():
                    hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in sorted(folder.rglob('*.py'))}}
print(json.dumps(result))
"""
    installed = call(
        "installed package identities",
        [sys.executable, "-I", "-c", probe],
        json_output=True,
    )
    sources = {
        "inspektorium": repo / "src/inspektorium",
        "agent_arena": repo / "agent-arena/src/agent_arena",
    }
    result["packages"] = installed
    for name, source in sources.items():
        if not installed[name]["inside_environment"]:
            raise AssertionError(
                f"{name} was not imported from the installed environment"
            )
        if installed[name]["modules"] != module_hashes(source):
            raise AssertionError(
                f"{name} installed modules differ from the supplied source"
            )

    public = str(Path(sys.executable).parent / "inspektorium")
    legacy = str(Path(sys.executable).parent / "agent-arena")
    examples = repo / "agent-arena/examples/phase10"
    bundles = output / "bundles"

    def audit(label, args, expected=0, legacy_entry=False):
        return call(
            label,
            [legacy if legacy_entry else public, "audit", *map(str, args)],
            expected,
            json_output=True,
        )

    root_help = call("public root help", [public, "--help"])
    assert "audit" in root_help and "reference checker" in root_help
    for command in ([], ["run"]):
        help_text = call(
            "audit help " + " ".join(command), [public, "audit", *command, "--help"]
        )
        assert "Usage: inspektorium audit" in help_text
    call("invalid option stays a usage error", [public, "audit", "run", "--invalid"], 2)
    mode_args = [
        "--task",
        str(examples / "positive-task.json"),
        "--output-root",
        str(bundles),
    ]
    call("missing mode is blocked", [public, "audit", "run", *mode_args], 2)
    call(
        "conflicting modes are blocked",
        [public, "audit", "run", "--offline", "--live", *mode_args],
        2,
    )
    absent_auth = audit(
        "live without authorization is blocked",
        [
            "run",
            "--live",
            *mode_args,
            "--authorization-dir",
            output / "absent-authorization",
            "--profile",
            "claude-haiku-5-5@3",
        ],
        2,
    )
    assert absent_auth["status"] == "PREFLIGHT_BLOCKED"

    created = {}
    for case in ("positive", "negative", "unknown"):
        task = examples / f"{case}-task.json"
        recording = examples / f"{case}-recording.json"
        valid = audit(f"{case}: validate", ["validate", "--task", task])
        assert valid["input_valid"] is True
        run = audit(
            f"{case}: run",
            [
                "run",
                "--offline",
                "--task",
                task,
                "--recording",
                recording,
                "--output-root",
                bundles,
            ],
            2 if case == "unknown" else 0,
        )
        wanted = "REVIEW_REQUIRED" if case == "unknown" else "READY_FOR_RELEASE"
        assert run["status"] == wanted
        created[case] = Path(run["path"])
        for legacy_entry in (False, True):
            inspected = audit(
                f"{case}: inspect {'legacy' if legacy_entry else 'public'}",
                ["inspect", "--bundle", run["path"]],
                legacy_entry=legacy_entry,
            )
            assert inspected["valid"] is True and inspected["status"] == wanted

    unknown = created["unknown"]
    before = {p.name: sha(p.read_bytes()) for p in unknown.iterdir()}
    blocked = audit(
        "UNKNOWN cannot be released",
        [
            "release",
            "--bundle",
            unknown,
            "--output-root",
            bundles,
            "--reviewer",
            "Offline test operator",
            "--reason",
            "Synthetic control",
        ],
        2,
    )
    assert blocked["path"] is None
    assert before == {p.name: sha(p.read_bytes()) for p in unknown.iterdir()}
    unknown_record = json.loads((unknown / "record.json").read_text())
    position = unknown_record["run_record"]["metadata"]["phase9"]["positions"][0][
        "position_id"
    ]
    reviewed = audit(
        "explicit recorded correction",
        [
            "review",
            "--bundle",
            unknown,
            "--state-dir",
            output / "review-state",
            "--output-root",
            bundles,
            "--select",
            position,
            "--reviewer",
            "Offline test operator",
            "--reason",
            "Synthetic supplied-source correction",
            "--correction",
            examples / "positive-recording.json",
        ],
    )
    assert reviewed["status"] == "READY_FOR_RELEASE"
    assert before == {p.name: sha(p.read_bytes()) for p in unknown.iterdir()}

    for label, candidate in (
        ("positive", created["positive"]),
        ("reviewed", reviewed["path"]),
    ):
        released = audit(
            f"{label}: explicit release",
            [
                "release",
                "--bundle",
                candidate,
                "--output-root",
                bundles,
                "--reviewer",
                "Offline test operator",
                "--reason",
                "Explicit synthetic artifact release",
            ],
        )
        assert released["status"] == "RELEASED"
        inspected = audit(
            f"{label}: legacy inspection of public release",
            ["inspect", "--bundle", released["path"]],
            legacy_entry=True,
        )
        assert inspected["valid"] is True and inspected["status"] == "RELEASED"

    old_run = audit(
        "compatibility entry creates candidate",
        [
            "run",
            "--offline",
            "--task",
            examples / "positive-task.json",
            "--recording",
            examples / "positive-recording.json",
            "--output-root",
            bundles,
        ],
        legacy_entry=True,
    )
    new_inspection = audit(
        "public entry inspects compatibility candidate",
        ["inspect", "--bundle", old_run["path"]],
    )
    assert new_inspection["valid"] is True

    tampered = output / "tampered-bundle"
    shutil.copytree(created["positive"], tampered)
    with (tampered / "report.md").open("a", encoding="utf-8") as stream:
        stream.write("\nUnapproved report mutation.\n")
    rejected = audit(
        "tampered report is rejected", ["inspect", "--bundle", tampered], 2
    )
    assert rejected["valid"] is False

    for case in sorted((repo / "examples").iterdir()):
        if not (case / "input.json").is_file():
            continue
        for format_name, suffix in (("json", "json"), ("markdown", "md")):
            rendered = work / f"{case.name}.{suffix}"
            call(
                f"reference {case.name}: {format_name}",
                [
                    public,
                    "inspect",
                    "--input",
                    str(case / "input.json"),
                    "--proposals",
                    str(case / "proposals.json"),
                    "--format",
                    format_name,
                    "--output",
                    str(rendered),
                ],
            )
            assert (
                rendered.read_bytes()
                == (case / f"expected_report.{suffix}").read_bytes()
            )

    call("installed dependency consistency", [sys.executable, "-m", "pip", "check"])
    events = [json.loads(line) for line in network_log.read_text().splitlines()]
    result["network_monitor"] = {
        "scope": "Python socket hooks only; not native or OS-wide traffic",
        "armed_records": sum(e["event"] == "armed" for e in events),
        "refused_operations": sum(e["event"] == "refused" for e in events),
    }
    assert result["network_monitor"]["armed_records"] > 0
    assert result["network_monitor"]["refused_operations"] == 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo, output = args.repo.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    result = {
        "status": "running",
        "python": sys.version.split()[0],
        "started_at_utc": datetime.now(UTC).isoformat(),
        "checks": [],
    }
    try:
        verify(repo, output, result)
        result["status"] = "passed"
        return_code = 0
    except Exception as exc:
        message = str(exc)
        for path, label in (
            (repo, "<checkout>"),
            (output, "<verification>"),
            (Path(sys.prefix), "<environment>"),
        ):
            message = message.replace(str(path), label)
        result.update(status="failed", error=f"{type(exc).__name__}: {message}")
        return_code = 1
    result["finished_at_utc"] = datetime.now(UTC).isoformat()
    (output / "results.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": result["status"],
                "checks_completed": len(result["checks"]),
                "error": result.get("error"),
            }
        )
    )
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
