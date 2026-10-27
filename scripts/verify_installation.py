"""Verify an installed Inspektorium wheel outside its source tree.

Run this with the Python of a fresh virtual environment into which the built
wheel was installed. The installed-package checks use the committed synthetic
examples and recordings only and make no provider call; a Python socket guard
(evidence/v0.1.1/tools/netguard.py) records that no network operation is
attempted. With --readme, the script also runs the README quickstart commands
in a new working directory; see --local-release for running them before the
release URLs exist.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

RELEASE_URL = "https://github.com/LAKITALKS/Inspektorium/releases/download/v0.3.0/"
RAW_URL = "https://raw.githubusercontent.com/LAKITALKS/Inspektorium/v0.3.0/"
QUICKSTART = re.compile(r"<!-- quickstart:start -->(.*?)<!-- quickstart:end -->", re.S)
FENCE = re.compile(r"```(?:bash|sh)\n(.*?)```", re.S)
SECRETS = (
    "PYTHONPATH",
    "PYTHONHOME",
    "PYTHONSTARTUP",
    "PYTHONUSERBASE",
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY",
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "AZURE_OPENAI_API_KEY",
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def module_hashes(directory: Path) -> dict[str, str]:
    return {
        path.relative_to(directory).as_posix(): sha(path.read_bytes())
        for path in sorted(directory.rglob("*.py"))
    }


def clean_env() -> dict[str, str]:
    env = dict(os.environ)
    for name in SECRETS:
        env.pop(name, None)
    env["PYTHONNOUSERSITE"] = "1"
    return env


def quickstart_script(readme: Path) -> str:
    match = QUICKSTART.search(readme.read_text(encoding="utf-8"))
    if match is None:
        raise ValueError("README has no quickstart markers")
    blocks = FENCE.findall(match.group(1))
    if not blocks:
        raise ValueError("README quickstart has no shell blocks")
    return "\n".join(blocks)


def verify_installed(repo: Path, output: Path, result: dict) -> None:
    work = output / "work"
    work.mkdir()
    env = clean_env()
    env["PIP_NO_INDEX"] = "1"
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
package = importlib.import_module('inspektorium')
folder = pathlib.Path(package.__file__).resolve().parent
print(json.dumps({
    'version': importlib.metadata.version('inspektorium'),
    'package_version': package.__version__,
    'inside_environment': folder.is_relative_to(pathlib.Path(sys.prefix).resolve()),
    'top_level': sorted({f.parts[0] for f in importlib.metadata.distribution('inspektorium').files
                         if not f.parts[0].endswith('.dist-info') and f.parts[0] != '..'}),
    'console_scripts': sorted(e.name for e in importlib.metadata.distribution('inspektorium').entry_points
                              if e.group == 'console_scripts'),
    'modules': {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(folder.rglob('*.py'))}}))
"""
    installed = call(
        "installed package identity",
        [sys.executable, "-I", "-c", probe],
        json_output=True,
    )
    result["package"] = {k: v for k, v in installed.items() if k != "modules"}
    result["package"]["module_count"] = len(installed["modules"])
    if not installed["inside_environment"]:
        raise AssertionError(
            "inspektorium was not imported from the installed environment"
        )
    if installed["modules"] != module_hashes(repo / "src/inspektorium"):
        raise AssertionError("installed modules differ from the supplied source")
    # One distribution, one package, one command: nothing else ships, so no shim exists.
    if installed["top_level"] != ["inspektorium"]:
        raise AssertionError(
            f"the wheel ships more than one top-level package: {installed['top_level']}"
        )
    if installed["console_scripts"] != ["inspektorium"]:
        raise AssertionError(
            f"the wheel installs other commands: {installed['console_scripts']}"
        )
    bin_dir = Path(sys.executable).parent

    public = str(bin_dir / "inspektorium")
    examples = repo / "examples/audit"
    bundles = output / "bundles"

    def audit(label, args, expected=0):
        return call(
            label, [public, "audit", *map(str, args)], expected, json_output=True
        )

    root_help = call("root help", [public, "--help"])
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
        inspected = audit(f"{case}: inspect", ["inspect", "--bundle", run["path"]])
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
            f"{label}: inspection of release", ["inspect", "--bundle", released["path"]]
        )
        assert inspected["valid"] is True and inspected["status"] == "RELEASED"

    tampered = output / "tampered-bundle"
    shutil.copytree(created["positive"], tampered)
    with (tampered / "report.md").open("a", encoding="utf-8") as stream:
        stream.write("\nUnapproved report mutation.\n")
    rejected = audit(
        "tampered report is rejected", ["inspect", "--bundle", tampered], 2
    )
    assert rejected["valid"] is False

    for case in sorted((repo / "examples/inspect").iterdir()):
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


def verify_readme(
    repo: Path, output: Path, result: dict, local_release: Path | None
) -> None:
    """Run the README quickstart blocks in one shell, in a new directory."""
    script = quickstart_script(repo / "README.md")
    substitutions = []
    if local_release is not None:
        # Before publication the release URLs do not exist yet: only these two URL
        # prefixes are mapped to the local build and checkout; every command is kept.
        substitutions = [
            (RELEASE_URL, local_release.as_uri() + "/"),
            (RAW_URL, repo.as_uri() + "/"),
        ]
        for old, new in substitutions:
            if old not in script:
                raise ValueError(f"README quickstart does not use {old}")
            script = script.replace(old, new)
    quickstart = output / "quickstart"
    quickstart.mkdir()
    (output / "quickstart.sh").write_text(script, encoding="utf-8")
    process = subprocess.run(
        ["bash", "-euo", "pipefail", "-c", script],
        cwd=quickstart,
        env=clean_env(),
        text=True,
        capture_output=True,
        check=False,
    )
    (output / "quickstart.log").write_text(
        process.stdout + process.stderr, encoding="utf-8"
    )
    result["readme_quickstart"] = {
        "exit_code": process.returncode,
        "url_substitutions": [old for old, _ in substitutions],
    }
    if process.returncode != 0:
        raise AssertionError(f"README quickstart failed: {process.stderr[-1500:]}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True, help="source checkout")
    parser.add_argument(
        "--output", type=Path, required=True, help="new directory outside the checkout"
    )
    parser.add_argument(
        "--readme", action="store_true", help="also run the README quickstart"
    )
    parser.add_argument(
        "--local-release",
        type=Path,
        help="directory with the built wheel; maps the release and raw URLs to local files",
    )
    args = parser.parse_args()
    repo, output = args.repo.resolve(), args.output.resolve()
    if output.is_relative_to(repo):
        raise SystemExit("Verification output must be outside the source checkout")
    if sys.prefix == sys.base_prefix:
        raise SystemExit("Use a fresh virtual environment with the wheel installed")
    output.mkdir(parents=True, exist_ok=False)
    result = {
        "status": "running",
        "python": sys.version.split()[0],
        "started_at_utc": datetime.now(UTC).isoformat(),
        "checks": [],
    }
    try:
        verify_installed(repo, output, result)
        if args.readme:
            local = args.local_release.resolve() if args.local_release else None
            verify_readme(repo, output, result, local)
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
                "readme_quickstart": result.get("readme_quickstart"),
                "error": result.get("error"),
            }
        )
    )
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
